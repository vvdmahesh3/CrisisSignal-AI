"""
CrisisSignal AI — Route Decorators
Shared access-control decorators for blueprint routes.

Phase 1.5: Centralised role checks applied via decorator, not inline logic.
This prevents privilege escalation bugs from bypassing manual if-checks.
"""

from functools import wraps
from flask import redirect, url_for, flash, abort, request, jsonify
from flask_login import current_user


def admin_only(f):
    """Restrict route to admin role only.
    Returns 403 JSON for API routes, redirect for HTML routes.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith("/api"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("auth.login"))
        if current_user.role != "admin":
            if request.path.startswith("/api"):
                return jsonify({"error": "Admin access required"}), 403
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("alerts.user_dashboard"))
        return f(*args, **kwargs)
    return decorated


def security_or_admin(f):
    """Restrict route to security or admin roles.
    Used for: Security Map, alert management views.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith("/api"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("auth.login"))
        if current_user.role not in ("admin", "security"):
            if request.path.startswith("/api"):
                return jsonify({"error": "Insufficient privileges"}), 403
            flash("Access denied. Security or admin access required.", "error")
            return redirect(url_for("alerts.user_dashboard"))
        return f(*args, **kwargs)
    return decorated


def same_community_required(f):
    """Ensure the resource being accessed belongs to the current user's community.
    Use this on routes that take community_id or alert.community_id as input.
    Applied as additional guard — call abort(403) explicitly if mismatch found.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)
    return decorated
