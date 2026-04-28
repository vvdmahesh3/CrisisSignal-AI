"""
CrisisSignal AI — REST API Routes
Pure JSON API endpoints for frontend consumption.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Alert, User
from ..services.alert_service import AlertService

api_bp = Blueprint("api", __name__)


@api_bp.route("/alerts", methods=["GET"])
@login_required
def get_alerts():
    """Get all active alerts, sorted by priority (severity × confidence)."""
    status_filter = request.args.get("status")
    type_filter = request.args.get("type")
    limit = request.args.get("limit", 50, type=int)

    query = Alert.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(type=type_filter)

    alerts = query.order_by(
        (Alert.severity * Alert.confidence).desc(),
        Alert.timestamp.desc()
    ).limit(limit).all()

    return jsonify([a.to_dict() for a in alerts])


@api_bp.route("/alerts", methods=["POST"])
@login_required
def create_alert():
    """Submit a new alert for AI processing."""
    data = request.get_json()
    message = data.get("message", "").strip()
    location = data.get("location", "Unknown").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400
    if len(message) > 500:
        return jsonify({"error": "Message must be under 500 characters"}), 400

    alert = AlertService.create_alert(
        message=message,
        location=location,
        user_id=current_user.id,
    )

    return jsonify(alert.to_dict()), 201


@api_bp.route("/alerts/<int:alert_id>", methods=["GET"])
@login_required
def get_alert(alert_id):
    """Get full alert details including votes and timeline."""
    alert = db.session.get(Alert, alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    result = alert.to_dict()

    # Include votes
    result["votes"] = [v.to_dict() for v in alert.votes.all()]

    # Include audit trail
    result["timeline"] = [
        log.to_dict() for log in alert.audit_entries
        .order_by(db.text("logged_at ASC")).all()
    ]

    return jsonify(result)


@api_bp.route("/alerts/preview", methods=["POST"])
@login_required
def preview_alert():
    """Live AI preview — classify text without saving to database."""
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    from ..ai_engine import process_alert
    result = process_alert(message, "Preview")

    return jsonify(result)


@api_bp.route("/users/me", methods=["GET"])
@login_required
def get_current_user():
    """Get the current user's profile and reliability score."""
    return jsonify(current_user.to_dict())


@api_bp.route("/users/<int:user_id>/reliability", methods=["GET"])
@login_required
def get_user_reliability(user_id):
    """Get a user's reliability score and history."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.id,
        "name": user.name,
        "reliability_score": user.reliability_score,
        "total_reports": user.total_reports,
        "confirmed_reports": user.confirmed_reports,
        "rejected_reports": user.rejected_reports,
        "is_flagged": user.is_flagged,
    })


@api_bp.route("/dashboard/stats", methods=["GET"])
@login_required
def dashboard_stats():
    """Aggregate dashboard statistics."""
    stats = {
        "total_active": Alert.query.filter(Alert.status != "resolved").count(),
        "critical": Alert.query.filter_by(status="critical").count(),
        "verified": Alert.query.filter_by(status="verified").count(),
        "verifying": Alert.query.filter_by(status="verifying").count(),
        "awaiting_review": Alert.query.filter_by(status="awaiting_review").count(),
        "rejected": Alert.query.filter_by(status="rejected").count(),
        "total_users": User.query.count(),
    }
    return jsonify(stats)


@api_bp.route("/reset", methods=["POST"])
@login_required
def reset_system():
    """Reset all alerts for demo mode. Admin only."""
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403

    from ..models import CrowdVote, AuditLog
    CrowdVote.query.delete()
    AuditLog.query.delete()
    Alert.query.delete()
    db.session.commit()

    return jsonify({"status": "reset", "message": "System cleared for demo"})
