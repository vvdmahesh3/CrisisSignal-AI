"""
CrisisSignal AI — Application Factory
Creates and configures the Flask application instance.
"""

import os
import logging
from flask import Flask
from .config import config_map
from .extensions import db, login_manager, socketio, migrate, limiter, csrf
from .logger import configure_logging, get_logger

logger = get_logger(__name__)


def create_app(config_name=None):
    """
    Application Factory Pattern.
    Creates a fully configured Flask app instance.

    Args:
        config_name: One of 'development', 'production', 'testing'
                     Defaults to FLASK_ENV env var, falls back to 'development'.

    Returns:
        Configured Flask application
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # ── Load Configuration ─────────────────────────────────────
    cfg = config_map.get(config_name, config_map["default"])
    app.config.from_object(cfg)

    # Phase 4: Production init checks (asserts SECRET_KEY, DATABASE_URL set)
    if hasattr(cfg, "init_app"):
        cfg.init_app(app)

    # ── Phase 4: Structured Logging ────────────────────────────
    configure_logging(app)

    # ── Phase 4: Sentry Error Tracking ─────────────────────────
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration(), SqlalchemyIntegration()],
                traces_sample_rate=0.1,   # 10% perf tracing
                send_default_pii=False,   # GDPR: no PII in error reports
                environment=config_name,
            )
            logger.info("Sentry error tracking enabled")
        except ImportError:
            logger.warning("sentry-sdk not installed — skipping error tracking")

    # ── Phase 4: HTTPS / ProxyFix (behind Nginx) ───────────────
    if config_name == "production":
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
        logger.info("ProxyFix middleware enabled")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    limiter.init_app(app)   # Phase 0: rate limiting
    csrf.init_app(app)      # Phase 1: CSRF protection

    # ── Configure Login Manager ────────────────────────────────
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # ── Register Blueprints ────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.alerts import alerts_bp
    from .routes.votes import votes_bp
    from .routes.admin import admin_bp
    from .routes.api import api_bp
    from .routes.demo import demo_bp
    from .routes.health import health_bp  # Phase 4

    app.register_blueprint(auth_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(votes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(demo_bp, url_prefix="/demo")
    app.register_blueprint(health_bp)  # Phase 4: /health, /health/ready

    # ── User Loader for Flask-Login ────────────────────────────
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Create Database Tables ─────────────────────────────────
    with app.app_context():
        from . import models  # noqa: F401 — ensure models are imported
        db.create_all()

        # Auto-seed demo users if the database is empty
        from .seed import seed_database
        from .models import User
        if User.query.count() == 0:
            count = seed_database()
            print(f"  => Auto-seeded {count} demo users")

    # ── Register Error Handlers ────────────────────────────────
    _register_error_handlers(app)

    # ── Register WebSocket Handlers ────────────────────────────
    _register_socketio_handlers(app)

    # ── Shell Context ──────────────────────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Alert, CrowdVote, AuditLog
        return {
            "db": db, "User": User, "Alert": Alert,
            "CrowdVote": CrowdVote, "AuditLog": AuditLog,
        }

    # ── Register CLI Commands ──────────────────────────────────
    from .seed import register_seed_command
    register_seed_command(app)

    # ── Template Context Processors ────────────────────────────
    @app.context_processor
    def inject_app_info():
        return {
            "app_name": app.config.get("APP_NAME", "CrisisSignal AI"),
            "app_version": app.config.get("APP_VERSION", "2.0.0"),
        }

    return app


def _register_error_handlers(app):
    """Register custom error handlers for JSON API and HTML pages."""
    from flask import jsonify, render_template, request

    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith("/api"):
            return jsonify({"error": "Bad request", "message": str(error)}), 400
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith("/api"):
            return jsonify({"error": "Forbidden", "message": str(error)}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api"):
            return jsonify({"error": "Not found", "message": str(error)}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith("/api"):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("errors/500.html"), 500


def _register_socketio_handlers(app):
    """Register WebSocket event handlers for real-time features.

    Phase 1.3: Rooms are scoped by community_id to prevent cross-community
    data leakage in multi-tenant deployments.
    """
    from flask_socketio import join_room, leave_room
    from flask_login import current_user

    @socketio.on("connect")
    def handle_connect():
        """Client connected — join community-scoped dashboard room."""
        if current_user.is_authenticated and current_user.community_id:
            join_room(f"dashboard_{current_user.community_id}")
        else:
            join_room("dashboard_public")

    @socketio.on("disconnect")
    def handle_disconnect():
        """Client disconnected."""
        if current_user.is_authenticated and current_user.community_id:
            leave_room(f"dashboard_{current_user.community_id}")

    @socketio.on("join_alert")
    def handle_join_alert(data):
        """Join an alert-specific room for targeted updates."""
        alert_id = data.get("alert_id")
        if alert_id:
            join_room(f"alert_{alert_id}")

    @socketio.on("leave_alert")
    def handle_leave_alert(data):
        """Leave an alert-specific room."""
        alert_id = data.get("alert_id")
        if alert_id:
            leave_room(f"alert_{alert_id}")
