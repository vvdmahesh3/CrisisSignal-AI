"""
CrisisSignal AI — Alert Service
Core business logic: alert creation, AI pipeline, duplicate detection,
state machine transitions, and resolution.
"""

from datetime import datetime, timedelta
from ..extensions import db
from ..models import Alert, AuditLog
from ..ai_engine import process_alert
from .audit_service import AuditService


# ── Valid State Transitions ───────────────────────────────────
VALID_TRANSITIONS = {
    "new": ["verifying", "awaiting_review", "rejected", "resolved"],
    "awaiting_review": ["verifying", "verified", "rejected", "resolved"],
    "verifying": ["verified", "rejected", "critical", "resolved"],
    "verified": ["critical", "resolved"],
    "critical": ["resolved"],
    "rejected": ["resolved"],
    # "resolved" is terminal
}


class AlertService:
    """Service layer for alert lifecycle management."""

    @staticmethod
    def create_alert(message, location, user_id, community_id=None):
        """
        Full alert creation pipeline:
        1. Run AI engine
        2. Check for duplicates
        3. Create alert record
        4. Log audit event
        """
        # ── Step 1: AI Processing ─────────────────────────────
        ai_result = process_alert(message, location)

        # ── Step 2: Duplicate Detection ───────────────────────
        parent = AlertService._detect_duplicate(message, location, community_id=community_id)
        if parent:
            parent.confirmations_count += 1
            parent.weighted_confirms += 0.5  # Neutral weight for duplicate reporter
            AuditService.log_event(
                alert_id=parent.id,
                actor_id=user_id,
                action="DUPLICATE_MERGED",
                new_value=f"confirmations={parent.confirmations_count}",
                detail=f"Duplicate report merged. New confirmation count: {parent.confirmations_count}",
            )
            db.session.commit()
            return parent

        # ── Step 3: Create Alert Record ───────────────────────
        alert = Alert(
            message=message,
            location=location,
            type=ai_result["type"],
            severity=ai_result["severity"],
            confidence=ai_result["confidence"],
            initial_confidence=ai_result["confidence"],
            evidence_score=ai_result["evidence_score"],
            evidence_strength=ai_result["evidence_strength"],
            explanation=ai_result["explanation"],
            keywords_found=",".join(ai_result.get("keywords_found", [])),
            urgency_level=ai_result.get("urgency_level", "none"),
            suspicion_flags=",".join(ai_result.get("suspicion_flags", [])),
            status="awaiting_review",
            reported_by=user_id,
            community_id=community_id,
        )
        db.session.add(alert)
        db.session.flush()  # Get alert.id before commit

        # ── Step 4: Update Reporter Stats ─────────────────────
        from ..models import User
        reporter = db.session.get(User, user_id)
        if reporter:
            reporter.total_reports += 1

        # ── Step 5: Audit Log ─────────────────────────────────
        AuditService.log_event(
            alert_id=alert.id,
            actor_id=user_id,
            action="ALERT_CREATED",
            new_value=f"type={alert.type}, severity={alert.severity}, confidence={alert.confidence:.2f}",
            detail=alert.explanation,
        )

        db.session.commit()
        return alert

    @staticmethod
    def _detect_duplicate(message, location, time_window_minutes=None, community_id=None):
        """
        Check for duplicate alerts using text overlap + location match within the community.
        Returns the parent alert if a duplicate is found, else None.

        Phase 1.7: Window is now per-type configurable. Fire and medical emergencies
        often generate second waves of reports 30–90 minutes later which should
        still merge into the same parent, not create a separate alert.
        """
        # Per-type duplicate windows (minutes)
        TYPE_DEDUP_WINDOWS = {
            "fire":     120,  # 2 hours — evacuations trigger delayed re-reports
            "medical":  120,  # 2 hours — second-responder reports
            "violence":  60,  # 1 hour
            "infra":     90,  # 90 minutes — power cuts, leaks re-reported
            "theft":     45,
            "general":   30,
        }

        # If no explicit window, detect the type first to pick the right window
        if time_window_minutes is None:
            from ..ai_engine import classify_text
            detected_type, _, _, _, _ = classify_text(message)
            time_window_minutes = TYPE_DEDUP_WINDOWS.get(detected_type, 30)

        cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        query = Alert.query.filter(
            Alert.status.notin_(["rejected", "resolved"]),
            Alert.timestamp >= cutoff,
        )
        if community_id:
            query = query.filter_by(community_id=community_id)

        recent_alerts = query.all()

        new_tokens = set(message.lower().split())

        for alert in recent_alerts:
            # Location proximity check (same location string)
            if alert.location and location:
                if alert.location.lower() != location.lower():
                    continue

            existing_tokens = set(alert.message.lower().split())
            if not existing_tokens or not new_tokens:
                continue

            intersection = new_tokens & existing_tokens
            union = new_tokens | existing_tokens
            similarity = len(intersection) / len(union)

            if similarity > 0.60:
                return alert

        return None

    @staticmethod
    def resolve_alert(alert, admin_id, resolution_note=""):
        """Resolve an alert and update reporter reliability."""
        old_status = alert.status

        # Update reliability from pre-resolution outcome (verified/critical/rejected).
        from .reliability_service import ReliabilityService
        ReliabilityService.update_on_resolution(alert, outcome_status=old_status)

        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        alert.resolution_note = resolution_note

        AuditService.log_event(
            alert_id=alert.id,
            actor_id=admin_id,
            action="ALERT_RESOLVED",
            previous_value=old_status,
            new_value="resolved",
            detail=f"Resolution: {resolution_note}",
        )

        db.session.commit()

    @staticmethod
    def escalate_alert(alert, admin_id):
        """Manually escalate an alert to critical."""
        old_status = alert.status
        if "critical" not in VALID_TRANSITIONS.get(old_status, []):
            # Force escalation for admin (override state machine)
            pass

        alert.status = "critical"
        if alert.severity < 8:
            alert.severity = 8  # Minimum severity for critical

        AuditService.log_event(
            alert_id=alert.id,
            actor_id=admin_id,
            action="ADMIN_ESCALATE",
            previous_value=old_status,
            new_value="critical",
            detail=f"Manually escalated to CRITICAL by admin",
        )
        db.session.commit()

    @staticmethod
    def transition_status(alert, new_status, actor_id=None, reason=""):
        """
        Transition alert to a new status with validation.
        Raises ValueError if transition is invalid.
        """
        if new_status not in VALID_TRANSITIONS.get(alert.status, []):
            raise ValueError(
                f"Invalid transition: {alert.status} → {new_status}"
            )

        old_status = alert.status
        alert.status = new_status

        AuditService.log_event(
            alert_id=alert.id,
            actor_id=actor_id,
            action="STATUS_CHANGE",
            previous_value=old_status,
            new_value=new_status,
            detail=reason or f"Transitioned from {old_status} to {new_status}",
        )
