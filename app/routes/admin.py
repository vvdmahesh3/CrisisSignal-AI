"""
CrisisSignal AI — Admin Routes
Admin dashboard, alert management, analytics, user management.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Alert, User, AuditLog
from ..services.alert_service import AlertService
from ..services.audit_service import AuditService
from ..services.reliability_service import ReliabilityService
from ..services.notification_service import NotificationService
from ..services.export_service import ExportService
from ..utils.decorators import admin_only, security_or_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_only
def dashboard():
    """Admin priority dashboard — all alerts sorted by severity × confidence."""
    alerts = Alert.query.filter(
        Alert.community_id == current_user.community_id,
        Alert.status != "resolved"
    ).order_by(
        (Alert.severity * Alert.confidence).desc(),
        Alert.timestamp.desc()
    ).all()

    resolved = Alert.query.filter_by(status="resolved", community_id=current_user.community_id)\
        .order_by(Alert.resolved_at.desc()).limit(10).all()

    # Stats
    stats = {
        "total_active": Alert.query.filter(Alert.status != "resolved", Alert.community_id == current_user.community_id).count(),
        "critical": Alert.query.filter_by(status="critical", community_id=current_user.community_id).count(),
        "verified": Alert.query.filter_by(status="verified", community_id=current_user.community_id).count(),
        "verifying": Alert.query.filter_by(status="verifying", community_id=current_user.community_id).count(),
        "rejected": Alert.query.filter_by(status="rejected", community_id=current_user.community_id).count(),
        "awaiting_review": Alert.query.filter_by(status="awaiting_review", community_id=current_user.community_id).count(),
        "total_users": User.query.filter_by(community_id=current_user.community_id).count(),
        "flagged_users": User.query.filter_by(is_flagged=True, community_id=current_user.community_id).count(),
    }

    return render_template(
        "dashboard/admin.html",
        alerts=alerts,
        resolved=resolved,
        stats=stats,
    )


@admin_bp.route("/admin/analytics")
@login_required
@admin_only
def analytics():
    """Institutional intelligence analytics dashboard."""
    from ..services.analytics_service import AnalyticsService
    data = AnalyticsService.get_dashboard_analytics(current_user.community_id)
    return render_template("dashboard/analytics.html", analytics=data)


@admin_bp.route("/api/analytics", methods=["GET"])
@login_required
@admin_only
def api_analytics():
    """JSON analytics data for Chart.js."""
    from ..services.analytics_service import AnalyticsService
    return jsonify(AnalyticsService.get_dashboard_analytics(current_user.community_id))


@admin_bp.route("/admin/alert/<int:alert_id>/resolve", methods=["POST"])
@login_required
@admin_only
def resolve_alert(alert_id):
    """Admin resolves an alert with a resolution note."""
    alert = db.session.get(Alert, alert_id)
    if not alert or alert.community_id != current_user.community_id:
        flash("Alert not found.", "error")
        return redirect(url_for("admin.dashboard"))

    resolution_note = request.form.get("resolution_note", "Resolved by admin")
    old_status = alert.status
    AlertService.resolve_alert(alert, current_user.id, resolution_note)

    # WebSocket: notify dashboard of resolution
    NotificationService.push_status_change(alert, old_status, "resolved")

    flash(f"Alert #{alert_id} resolved.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/alert/<int:alert_id>/escalate", methods=["POST"])
@login_required
@admin_only
def escalate_alert(alert_id):
    """Admin manually escalates an alert to critical."""
    alert = db.session.get(Alert, alert_id)
    if not alert or alert.community_id != current_user.community_id:
        flash("Alert not found.", "error")
        return redirect(url_for("admin.dashboard"))

    old_status = alert.status
    AlertService.escalate_alert(alert, current_user.id)

    # WebSocket: critical broadcast
    NotificationService.push_status_change(alert, old_status, "critical")
    NotificationService.push_critical_alert(alert)

    flash(f"Alert #{alert_id} escalated to CRITICAL.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/alert/<int:alert_id>/reject", methods=["POST"])
@login_required
@admin_only
def reject_alert(alert_id):
    """Admin manually rejects an alert."""
    alert = db.session.get(Alert, alert_id)
    if not alert or alert.community_id != current_user.community_id:
        flash("Alert not found.", "error")
        return redirect(url_for("admin.dashboard"))

    old_status = alert.status
    alert.status = "rejected"
    ReliabilityService.apply_admin_reject(alert)

    AuditService.log_event(
        alert_id=alert_id,
        actor_id=current_user.id,
        action="ADMIN_REJECT",
        previous_value=old_status,
        new_value="rejected",
        detail=f"Manually rejected by {current_user.name}",
    )
    db.session.commit()

    # WebSocket: notify dashboard
    NotificationService.push_status_change(alert, old_status, "rejected")

    flash(f"Alert #{alert_id} rejected.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/users")
@login_required
@admin_only
def manage_users():
    """User management page — view reliability scores, flag users."""
    users = User.query.filter_by(community_id=current_user.community_id).order_by(User.reliability_score.desc()).all()
    return render_template("dashboard/users.html", users=users)


@admin_bp.route("/admin/audit")
@login_required
@admin_only
def audit_log():
    """View full audit trail."""
    logs = AuditLog.query.filter_by(community_id=current_user.community_id).order_by(AuditLog.logged_at.desc()).limit(200).all()
    return render_template("dashboard/audit.html", logs=logs)


@admin_bp.route("/security")
@login_required
@security_or_admin
def security_view():
    """Security/responder view — map + critical alerts."""
    critical_alerts = Alert.query.filter(
        Alert.community_id == current_user.community_id,
        Alert.status.in_(["critical", "verified"])
    ).order_by(Alert.severity.desc()).all()

    all_active = Alert.query.filter(
        Alert.community_id == current_user.community_id,
        Alert.status.notin_(["resolved", "rejected"])
    ).order_by(Alert.timestamp.desc()).all()

    # Phase 3: security personnel available for assignment
    security_users = User.query.filter_by(
        community_id=current_user.community_id,
        role="security"
    ).order_by(User.name).all()

    return render_template(
        "dashboard/security.html",
        alerts=critical_alerts,
        all_active=all_active,
        security_users=security_users,
    )


# ── Phase 3: Responder Assignment ────────────────────────────────

@admin_bp.route("/admin/alert/<int:alert_id>/assign", methods=["POST"])
@login_required
@security_or_admin
def assign_responder(alert_id):
    """Phase 3: Assign a security responder to an alert."""
    alert = db.session.get(Alert, alert_id)
    if not alert or alert.community_id != current_user.community_id:
        flash("Alert not found.", "error")
        return redirect(url_for("admin.dashboard"))

    responder_id = request.form.get("responder_id", type=int)
    if responder_id:
        responder = db.session.get(User, responder_id)
        if not responder or responder.community_id != current_user.community_id:
            flash("Invalid responder selected.", "error")
            return redirect(url_for("admin.dashboard"))

        old_responder = alert.assigned_to
        alert.assigned_to = responder_id

        AuditService.log_event(
            alert_id=alert_id,
            actor_id=current_user.id,
            action="RESPONDER_ASSIGNED",
            previous_value=str(old_responder) if old_responder else "None",
            new_value=str(responder_id),
            detail=f"{responder.name} assigned as responder by {current_user.name}",
        )
        db.session.commit()

        # Push WebSocket notification to community room
        NotificationService.push_status_change(alert, alert.status, alert.status)
        flash(f"{responder.name} assigned as responder for Alert #{alert_id}.", "success")
    else:
        # Unassign
        alert.assigned_to = None
        AuditService.log_event(
            alert_id=alert_id,
            actor_id=current_user.id,
            action="RESPONDER_UNASSIGNED",
            detail=f"Responder removed by {current_user.name}",
        )
        db.session.commit()
        flash(f"Responder removed from Alert #{alert_id}.", "info")

    return redirect(request.referrer or url_for("admin.dashboard"))


# ── Phase 3: CSV Export Routes ────────────────────────────────────

@admin_bp.route("/admin/export/alerts")
@login_required
@admin_only
def export_alerts():
    """Phase 3: Download all community alerts as CSV."""
    alerts = Alert.query.filter_by(
        community_id=current_user.community_id
    ).order_by(Alert.timestamp.desc()).all()

    community_name = current_user.community.name if current_user.community else "Community"
    return ExportService.export_alerts_csv(alerts, community_name)


@admin_bp.route("/admin/export/audit")
@login_required
@admin_only
def export_audit():
    """Phase 3: Download full audit trail as CSV."""
    logs = AuditLog.query.filter_by(
        community_id=current_user.community_id
    ).order_by(AuditLog.logged_at.desc()).all()

    community_name = current_user.community.name if current_user.community else "Community"
    return ExportService.export_audit_csv(logs, community_name)


@admin_bp.route("/admin/users/<int:user_id>/flag", methods=["POST"])
@login_required
@admin_only
def flag_user(user_id):
    """Phase 3: Manually flag or unflag a user."""
    user = db.session.get(User, user_id)
    if not user or user.community_id != current_user.community_id:
        flash("User not found.", "error")
        return redirect(url_for("admin.manage_users"))

    user.is_flagged = not user.is_flagged
    action = "flagged" if user.is_flagged else "unflagged"
    AuditService.log_event(
        alert_id=None,
        actor_id=current_user.id,
        action=f"USER_{action.upper()}",
        detail=f"{user.name} manually {action} by {current_user.name}",
    )
    db.session.commit()
    flash(f"{user.name} has been {action}.", "info")
    return redirect(url_for("admin.manage_users"))
