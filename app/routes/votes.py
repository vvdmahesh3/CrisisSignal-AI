"""
CrisisSignal AI — Voting Routes
Crowd verification: confirm/reject votes on alerts.
Now with full WebSocket integration for real-time updates.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..extensions import db, limiter
from ..models import Alert, CrowdVote
from ..services.confidence_service import ConfidenceService
from ..services.audit_service import AuditService
from ..services.notification_service import NotificationService
from datetime import datetime, timedelta

BURST_WINDOW_SECONDS = 30   # Window to count votes
BURST_THRESHOLD = 6         # Votes within window = burst

votes_bp = Blueprint("votes", __name__)


@votes_bp.route("/api/alerts/<int:alert_id>/vote", methods=["POST"])
@login_required
@limiter.limit("15 per minute", error_message="Voting too fast. Please slow down.")
def cast_vote(alert_id):
    """Cast a crowd verification vote (confirm or reject) on an alert."""
    alert = db.session.get(Alert, alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    # ── Prevent self-voting ───────────────────────────────────
    if alert.reported_by == current_user.id:
        return jsonify({"error": "You cannot vote on your own alert"}), 403

    # ── Check for existing vote ───────────────────────────────
    existing_vote = CrowdVote.query.filter_by(
        alert_id=alert_id, user_id=current_user.id
    ).first()
    if existing_vote:
        return jsonify({"error": "You have already voted on this alert"}), 409

    # ── Check alert is in voteable state ──────────────────────
    if alert.status in ("resolved", "rejected"):
        return jsonify({"error": "This alert is no longer accepting votes"}), 400

    # ── Phase 2.7: Vote Burst Detection ─────────────────────
    # If too many votes arrive in a short window, the alert is flagged
    # for review instead of auto-updating status.
    cutoff = datetime.utcnow() - timedelta(seconds=BURST_WINDOW_SECONDS)
    recent_vote_count = CrowdVote.query.filter(
        CrowdVote.alert_id == alert_id,
        CrowdVote.voted_at >= cutoff,
    ).count()

    burst_detected = recent_vote_count >= BURST_THRESHOLD
    if burst_detected:
        AuditService.log_event(
            alert_id=alert_id,
            actor_id=current_user.id,
            action="BURST_DETECTED",
            detail=f"{recent_vote_count} votes in {BURST_WINDOW_SECONDS}s — status frozen for review",
        )

    # ── Parse vote data ───────────────────────────────────────
    data = request.get_json()
    vote_type = data.get("vote", "confirm")
    if vote_type not in ("confirm", "reject"):
        return jsonify({"error": "Vote must be 'confirm' or 'reject'"}), 400

    # ── Record the vote ───────────────────────────────────────
    vote = CrowdVote(
        alert_id=alert_id,
        user_id=current_user.id,
        vote=vote_type,
        vote_weight=current_user.reliability_score,
    )
    db.session.add(vote)

    # ── Update alert vote counts ──────────────────────────────
    old_confidence = alert.confidence

    if vote_type == "confirm":
        alert.confirmations_count += 1
        alert.weighted_confirms += current_user.reliability_score
    else:
        alert.rejections_count += 1
        alert.weighted_rejects += current_user.reliability_score

    # ── Recalculate confidence and status ─────────────────────
    reporter = alert.reporter
    reporter_reliability = reporter.reliability_score if reporter else 0.5

    new_confidence = ConfidenceService.recalculate(
        initial_confidence=alert.initial_confidence,
        weighted_confirms=alert.weighted_confirms,
        weighted_rejects=alert.weighted_rejects,
        reporter_reliability=reporter_reliability,
    )
    old_status = alert.status
    new_status = ConfidenceService.determine_status(
        confidence=new_confidence,
        severity=alert.severity,
        weighted_confirms=alert.weighted_confirms,
        weighted_rejects=alert.weighted_rejects,
        total_votes=alert.total_votes,
    )

    alert.confidence = new_confidence
    # Phase 2.7: During a vote burst, freeze status — don't auto-transition.
    # An admin must review the alert manually before it can escalate.
    if not burst_detected:
        alert.status = new_status
    else:
        new_status = alert.status  # Keep existing status

    # ── Audit logging ─────────────────────────────────────────
    AuditService.log_event(
        alert_id=alert_id,
        actor_id=current_user.id,
        action=f"VOTE_{vote_type.upper()}",
        previous_value=f"confidence={old_confidence:.2f}",
        new_value=f"confidence={new_confidence:.2f}",
        detail=f"{current_user.name} voted {vote_type} (weight: {current_user.reliability_score:.2f})",
    )

    if old_status != new_status:
        AuditService.log_event(
            alert_id=alert_id,
            actor_id=None,  # System action
            action="STATUS_CHANGE",
            previous_value=old_status,
            new_value=new_status,
            detail=f"Status changed due to confidence update: {new_confidence:.2f}",
        )

    db.session.commit()

    # ── WebSocket: Push real-time updates ─────────────────────
    # 1. Vote update → updates vote counters
    NotificationService.push_vote_update(alert, vote.to_dict())

    # 2. Confidence update → animates confidence bar
    NotificationService.push_confidence_update(
        alert, old_confidence, new_confidence
    )

    # 3. Status change → updates status badge
    if old_status != new_status:
        NotificationService.push_status_change(alert, old_status, new_status)

        # 4. Critical broadcast → full-screen alert overlay
        if new_status == "critical":
            NotificationService.push_critical_alert(alert)

    return jsonify({
        "success": True,
        "alert": alert.to_dict(),
        "vote": vote.to_dict(),
        "status_changed": old_status != new_status,
        "old_status": old_status,
        "new_status": new_status,
    })
