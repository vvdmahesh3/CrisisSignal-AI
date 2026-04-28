"""
CrisisSignal AI — Extensions
Centralized extension instances. Initialized in create_app().

Phase 0: Added Flask-Limiter for rate limiting.
Phase 1: Added Flask-WTF CSRF protection.
"""

import sys

# ── Block eventlet import on Python 3.13+ (incompatible) ──────
if sys.version_info >= (3, 13):
    import unittest.mock
    sys.modules['eventlet'] = unittest.mock.MagicMock()
    sys.modules['eventlet.wsgi'] = unittest.mock.MagicMock()
    sys.modules['eventlet.greenthread'] = unittest.mock.MagicMock()
    sys.modules['eventlet.green'] = unittest.mock.MagicMock()
    sys.modules['eventlet.green.threading'] = unittest.mock.MagicMock()

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# ── Database ──────────────────────────────────────────────────
db = SQLAlchemy()

# ── Authentication ────────────────────────────────────────────
login_manager = LoginManager()

# ── Real-Time WebSocket (threading mode — no eventlet needed) ─
socketio = SocketIO(async_mode='threading')

# ── Database Migrations ───────────────────────────────────────
migrate = Migrate()

# ── Rate Limiter (Phase 0) ────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://",  # Use "redis://localhost:6379" in production
)

# ── CSRF Protection (Phase 1) ─────────────────────────────────
# Protects all state-changing POST/PUT/DELETE routes automatically.
# API JSON endpoints are exempted via csrf.exempt() in their blueprints.
csrf = CSRFProtect()
