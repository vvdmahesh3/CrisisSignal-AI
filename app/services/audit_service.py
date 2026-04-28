"""
CrisisSignal AI — Audit Service
Immutable event logging for all system state changes.
"""

from ..extensions import db
from ..models import AuditLog


class AuditService:
    """Records every lifecycle event for accountability and audit trail."""

    @staticmethod
    def log_event(alert_id, actor_id, action, previous_value=None,
                  new_value=None, detail=None):
        """
        Write an immutable audit log entry.

        Args:
            alert_id: The alert this event relates to
            actor_id: User who performed the action (None for system actions)
            action: Action type (e.g., ALERT_CREATED, STATUS_CHANGE, VOTE_CONFIRM)
            previous_value: State before the action
            new_value: State after the action
            detail: Human-readable description
        """
        # alert_id can be None for user-level administrative events
        entry = AuditLog(
            alert_id=alert_id,
            actor_id=actor_id,
            action=action,
            previous_value=previous_value,
            new_value=new_value,
            detail=detail,
        )
        db.session.add(entry)
        # Note: caller is responsible for db.session.commit()

    @staticmethod
    def get_alert_timeline(alert_id):
        """Get the full audit timeline for an alert, ordered chronologically."""
        return AuditLog.query.filter_by(alert_id=alert_id)\
            .order_by(AuditLog.logged_at.asc()).all()

    @staticmethod
    def get_recent_events(limit=50):
        """Get the most recent audit events across all alerts."""
        return AuditLog.query.order_by(AuditLog.logged_at.desc())\
            .limit(limit).all()
