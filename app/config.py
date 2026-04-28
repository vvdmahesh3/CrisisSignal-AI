"""
CrisisSignal AI — Configuration
Environment-specific settings for Development, Testing, and Production.
"""

import os
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# ── Ensure instance directory exists ──────────────────────────
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "crisissignal-dev-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Application Settings ──────────────────────────────────
    APP_NAME = "CrisisSignal AI"
    APP_VERSION = "1.0.0"

    # ── AI Engine Settings ────────────────────────────────────
    AI_PROCESSING_TIMEOUT_MS = 200  # Target: < 200ms per alert
    MAX_MESSAGE_LENGTH = 500
    DUPLICATE_TIME_WINDOW_MINUTES = 30
    DUPLICATE_SIMILARITY_THRESHOLD = 0.60

    # ── Confidence Thresholds ─────────────────────────────────
    CONFIDENCE_VERIFIED_THRESHOLD = 0.70
    CONFIDENCE_CRITICAL_THRESHOLD = 0.85
    SEVERITY_CRITICAL_MINIMUM = 8

    # ── Reliability Score Settings ────────────────────────────
    RELIABILITY_DEFAULT = 0.50
    RELIABILITY_MAX = 1.0
    RELIABILITY_MIN = 0.0
    RELIABILITY_CONFIRM_BONUS = 0.05
    RELIABILITY_CRITICAL_BONUS = 0.15
    RELIABILITY_REJECT_PENALTY = -0.10
    RELIABILITY_ADMIN_REJECT_PENALTY = -0.15
    RELIABILITY_FLAG_THRESHOLD = 3  # rejections within 30 days

    # ── Session & Security ────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours


class DevelopmentConfig(BaseConfig):
    """Development configuration — SQLite, debug mode on."""

    DEBUG = True
    # Use raw absolute path to prevent SQLAlchemy from misparsing '#' as URL fragment
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(INSTANCE_DIR, "crisissignal_dev.db")
    )

    # ── Development-Specific ──────────────────────────────────
    DEMO_MODE_ENABLED = True
    TEMPLATES_AUTO_RELOAD = True


class TestingConfig(BaseConfig):
    """Testing configuration — in-memory SQLite, no CSRF."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    DEMO_MODE_ENABLED = True


class ProductionConfig(BaseConfig):
    """Production configuration — PostgreSQL, secure settings."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")

    # ── Production Security ───────────────────────────────────
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    DEMO_MODE_ENABLED = False

    @classmethod
    def init_app(cls, app):
        """Production-specific initialization."""
        assert cls.SECRET_KEY != "crisissignal-dev-key-change-in-production", \
            "Production SECRET_KEY must be set via environment variable!"
        assert cls.SQLALCHEMY_DATABASE_URI, \
            "Production DATABASE_URL must be set!"


# ── Configuration Map ─────────────────────────────────────────
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
