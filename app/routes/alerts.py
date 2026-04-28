"""
CrisisSignal AI — Alert Routes
Report submission, alert listing, detail views, user dashboard, and landing page.

Phase 3: Photo evidence upload, emergency flag, contact phone on report form.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from urllib.parse import quote
from ..extensions import db, limiter
from ..models import Alert, CrowdVote
from ..services.alert_service import AlertService
from ..services.notification_service import NotificationService
from ..services.evidence_service import EvidenceService

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/")
def index():
    """Landing page — show marketing page or redirect to dashboard."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("alerts.user_dashboard"))
    return render_template("landing.html")


@alerts_bp.route("/report", methods=["GET", "POST"])
@login_required
@limiter.limit("5 per 10 minutes", error_message="Too many reports. Please wait before submitting again.")
def report():
    """Structured incident report form — Phase 3: photo, emergency flag, contact."""
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        location = request.form.get("location", "Unknown").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        is_emergency = request.form.get("is_emergency") == "on"

        if location == "Other":
            location = request.form.get("custom_location", "Unknown").strip()

        if not message:
            flash("Please describe the incident.", "error")
            return render_template("alerts/report.html")

        if len(message) > 500:
            flash("Message must be under 500 characters.", "error")
            return render_template("alerts/report.html")

        # Create alert through service layer
        alert = AlertService.create_alert(
            message=message,
            location=location,
            user_id=current_user.id,
            community_id=current_user.community_id
        )

        # Phase 3: emergency flag and contact phone
        alert.is_emergency = is_emergency
        alert.contact_phone = contact_phone if contact_phone else None

        # Phase 3: If severity escalated due to emergency flag
        if is_emergency and alert.severity < 7:
            alert.severity = max(alert.severity, 7)

        # Phase 3: Photo evidence upload
        photo_file = request.files.get("photo_evidence")
        if photo_file and photo_file.filename:
            try:
                relative_path = EvidenceService.save_photo(photo_file, alert.id)
                alert.photo_path = relative_path
            except ValueError as e:
                flash(f"Photo upload skipped: {e}", "warning")

        db.session.commit()

        # WebSocket: push new alert to dashboard
        NotificationService.push_new_alert(alert)

        # Phase 3: Smart notification — emergency alerts broadcast immediately
        if is_emergency:
            NotificationService.push_critical_alert(alert)

        flash("Alert submitted successfully! AI analysis complete.", "success")
        return redirect(url_for("alerts.detail", alert_id=alert.id))

    return render_template("alerts/report.html")


@alerts_bp.route("/alert/<int:alert_id>")
@login_required
def detail(alert_id):
    """Alert detail view with timeline, X-Logic, voting, and evidence photo."""
    alert = db.session.get(Alert, alert_id)
    # Community check: both None means global/no-community, treat as same community
    user_community = current_user.community_id
    alert_community = alert.community_id if alert else None
    if not alert or (user_community is not None and alert_community != user_community):
        flash("Alert not found.", "error")
        return redirect(url_for("alerts.user_dashboard"))

    from ..models import AuditLog
    from ..models import User

    timeline = AuditLog.query.filter_by(alert_id=alert_id)\
        .order_by(AuditLog.logged_at.asc()).all()

    votes = CrowdVote.query.filter_by(alert_id=alert_id)\
        .order_by(CrowdVote.voted_at.asc()).all()

    user_vote = CrowdVote.query.filter_by(
        alert_id=alert_id, user_id=current_user.id
    ).first()

    # Phase 3: effective confidence (time-decayed for display)
    from ..services.confidence_service import ConfidenceService
    effective_confidence = ConfidenceService.get_effective_confidence(alert)

    share_text = (
        f"ALERT: {alert.type.upper()} at {alert.location or 'Unknown location'} "
        f"| Status: {alert.status.upper()} | Confidence: {int((alert.confidence or 0) * 100)}% "
        f"| {alert.confirmations_count} confirmations"
    )
    encoded_share_text = quote(share_text)
    share_links = {
        "whatsapp": f"https://wa.me/?text={encoded_share_text}",
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_share_text}",
        "email": (
            f"mailto:?subject={quote('CrisisSignal AI Emergency Alert')}"
            f"&body={encoded_share_text}"
        ),
    }

    return render_template(
        "alerts/detail.html",
        alert=alert,
        timeline=timeline,
        votes=votes,
        user_vote=user_vote,
        share_text=share_text,
        share_links=share_links,
        effective_confidence=effective_confidence,
    )


@alerts_bp.route("/dashboard")
@login_required
def user_dashboard():
    """User/reporter dashboard — own alerts + nearby alerts to verify."""
    from ..services.reliability_service import ReliabilityService

    # Handle NULL community_id correctly (SQL NULL == NULL is FALSE)
    if current_user.community_id is None:
        my_alerts = Alert.query.filter(
            Alert.reported_by == current_user.id,
            Alert.community_id.is_(None)
        ).order_by(Alert.timestamp.desc()).all()

        verifiable_alerts = Alert.query.filter(
            Alert.community_id.is_(None),
            Alert.reported_by != current_user.id,
            Alert.status.in_(["new", "awaiting_review", "verifying"])
        ).order_by(Alert.timestamp.desc()).limit(20).all()
    else:
        my_alerts = Alert.query.filter_by(
            reported_by=current_user.id,
            community_id=current_user.community_id
        ).order_by(Alert.timestamp.desc()).all()

        verifiable_alerts = Alert.query.filter(
            Alert.community_id == current_user.community_id,
            Alert.reported_by != current_user.id,
            Alert.status.in_(["new", "awaiting_review", "verifying"])
        ).order_by(Alert.timestamp.desc()).limit(20).all()

    # Check which alerts the user has already voted on
    voted_alert_ids = set()
    if verifiable_alerts:
        voted = CrowdVote.query.filter(
            CrowdVote.user_id == current_user.id,
            CrowdVote.alert_id.in_([a.id for a in verifiable_alerts])
        ).all()
        voted_alert_ids = {v.alert_id for v in voted}

    # Phase 3: reputation badge
    badge_tier, badge_label = ReliabilityService.get_badge(current_user.reliability_score)

    return render_template(
        "dashboard/user.html",
        my_alerts=my_alerts,
        verifiable_alerts=verifiable_alerts,
        voted_alert_ids=voted_alert_ids,
        badge_tier=badge_tier,
        badge_label=badge_label,
    )
