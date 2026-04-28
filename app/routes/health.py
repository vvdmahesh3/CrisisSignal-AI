"""
CrisisSignal AI — Health Check Route
Phase 4: /health endpoint for load balancers, Docker HEALTHCHECK,
Kubernetes liveness/readiness probes.

Returns JSON — no login required.
"""

from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health_check():
    """
    Liveness probe — confirms the app process is up and the DB is reachable.

    Returns:
        200 OK  — app is healthy
        503     — DB unreachable (app is alive but not ready to serve traffic)
    """
    status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "CrisisSignal AI",
    }

    # Database connectivity check
    try:
        from ..extensions import db
        db.session.execute(db.text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        status["status"] = "degraded"
        status["database"] = "unreachable"
        status["db_error"] = str(e)
        return jsonify(status), 503

    # ML classifier check (non-critical — doesn't affect readiness)
    try:
        from ..ml.classifier import CrisisClassifier
        status["ml_classifier"] = "loaded" if CrisisClassifier.is_available() else "fallback"
    except Exception:
        status["ml_classifier"] = "unavailable"

    return jsonify(status), 200


@health_bp.route("/health/ready")
def readiness_check():
    """
    Readiness probe — stricter check used before routing traffic.
    Checks DB + that at least one community exists (seeded).
    """
    try:
        from ..extensions import db
        from ..models import Community
        db.session.execute(db.text("SELECT 1"))
        community_count = Community.query.count()
    except Exception as e:
        return jsonify({"status": "not_ready", "reason": str(e)}), 503

    if community_count == 0:
        return jsonify({"status": "not_ready", "reason": "Database not seeded"}), 503

    return jsonify({
        "status": "ready",
        "communities": community_count,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }), 200
