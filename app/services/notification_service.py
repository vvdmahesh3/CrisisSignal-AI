"""
CrisisSignal AI — Notification Service
WebSocket push events and notification dispatch.

Phase 1.3: All room names now scoped by community_id to prevent
cross-community data leakage in multi-tenant deployments.
"""

from ..extensions import socketio


class NotificationService:
    """Handles real-time push notifications via WebSocket."""

    @staticmethod
    def push_new_alert(alert):
        """Push a new alert to the community-scoped dashboard room."""
        try:
            data = alert.to_dict() if hasattr(alert, 'to_dict') else {}
            room = f"dashboard_{alert.community_id}" if alert.community_id else "dashboard_public"
            socketio.emit("new_alert", data, room=room)
        except Exception as e:
            print(f"[NotificationService] push_new_alert error: {e}")

    @staticmethod
    def push_vote_update(alert, vote_data):
        """Push a vote update to alert-specific room AND community dashboard."""
        try:
            alert_data = alert.to_dict() if hasattr(alert, 'to_dict') else {}
            payload = {"alert": alert_data, "vote": vote_data}
            room = f"dashboard_{alert.community_id}" if alert.community_id else "dashboard_public"
            # Emit to alert detail page viewers
            socketio.emit("vote_update", payload, room=f"alert_{alert.id}")
            # Emit to community dashboard for live counter updates
            socketio.emit("vote_update", payload, room=room)
        except Exception as e:
            print(f"[NotificationService] push_vote_update error: {e}")

    @staticmethod
    def push_status_change(alert, old_status, new_status):
        """Push a status change event to the community dashboard and alert room."""
        try:
            payload = {
                "alert_id": alert.id,
                "old_status": old_status or "unknown",
                "new_status": new_status or "unknown",
                "confidence": getattr(alert, 'confidence', 0) or 0,
                "severity": getattr(alert, 'severity', 0) or 0,
            }
            room = f"dashboard_{alert.community_id}" if alert.community_id else "dashboard_public"
            socketio.emit("status_change", payload, room=room)
            socketio.emit("status_change", payload, room=f"alert_{alert.id}")
        except Exception as e:
            print(f"[NotificationService] push_status_change error: {e}")

    @staticmethod
    def push_confidence_update(alert, old_confidence, new_confidence):
        """Push live confidence update for animated bar."""
        try:
            payload = {
                "alert_id": alert.id,
                "old_confidence": old_confidence or 0,
                "new_confidence": new_confidence or 0,
                "status": getattr(alert, 'status', 'unknown') or 'unknown',
            }
            room = f"dashboard_{alert.community_id}" if alert.community_id else "dashboard_public"
            socketio.emit("confidence_update", payload, room=f"alert_{alert.id}")
            socketio.emit("confidence_update", payload, room=room)
        except Exception as e:
            print(f"[NotificationService] push_confidence_update error: {e}")

    @staticmethod
    def push_critical_alert(alert):
        """Broadcast critical alert to ALL connected clients (community-wide)."""
        try:
            data = alert.to_dict() if hasattr(alert, 'to_dict') else {}
            # Critical alerts broadcast to entire community room
            room = f"dashboard_{alert.community_id}" if alert.community_id else "dashboard_public"
            socketio.emit("critical_alert", data, room=room)
        except Exception as e:
            print(f"[NotificationService] push_critical_alert error: {e}")

    @staticmethod
    def push_system_reset(community_id=None):
        """Broadcast system reset event to community clients."""
        try:
            room = f"dashboard_{community_id}" if community_id else "dashboard_public"
            socketio.emit("system_reset", {"message": "System has been reset"}, room=room)
        except Exception as e:
            print(f"[NotificationService] push_system_reset error: {e}")
