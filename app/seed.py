"""
CrisisSignal AI — Database Seed
Pre-populate demo users with preset reliability scores.
Run with: flask seed

Phase 0 fix: Passwords are hashed at seed time using werkzeug.
Plain-text passwords are never stored. Change DEMO_PASSWORDS in
your .env to override defaults before running in any shared environment.
"""

import os
from werkzeug.security import generate_password_hash
from .extensions import db
from .models import User, Community


# ── Demo User Definitions ─────────────────────────────────────
# Passwords are read from environment variables with safe defaults.
# In any shared/public environment: set these env vars before seeding.
DEMO_USERS = [
    {
        "name": "Campus Admin",
        "email": "admin@crisis.ai",
        "role": "admin",
        "reliability": 0.95,
        "password_env": "SEED_ADMIN_PASSWORD",
        "password_default": "Change-Me-Admin-2026!",
    },
    {
        "name": "Security Chief",
        "email": "security@crisis.ai",
        "role": "security",
        "reliability": 0.90,
        "password_env": "SEED_SECURITY_PASSWORD",
        "password_default": "Change-Me-Security-2026!",
    },
    {
        "name": "Patrol Guard",
        "email": "guard@crisis.ai",
        "role": "security",
        "reliability": 0.82,
        "password_env": "SEED_GUARD_PASSWORD",
        "password_default": "Change-Me-Guard-2026!",
    },
    {
        "name": "Hostel Warden",
        "email": "warden@crisis.ai",
        "role": "admin",
        "reliability": 0.88,
        "password_env": "SEED_WARDEN_PASSWORD",
        "password_default": "Change-Me-Warden-2026!",
    },
    {
        "name": "Student Alpha",
        "email": "alpha@student.edu",
        "role": "user",
        "reliability": 0.70,
        "password_env": "SEED_STUDENT_PASSWORD",
        "password_default": "Change-Me-Student-2026!",
    },
    {
        "name": "Student Beta",
        "email": "beta@student.edu",
        "role": "user",
        "reliability": 0.55,
        "password_env": "SEED_STUDENT_PASSWORD",
        "password_default": "Change-Me-Student-2026!",
    },
    {
        "name": "Student Gamma",
        "email": "gamma@student.edu",
        "role": "user",
        "reliability": 0.65,
        "password_env": "SEED_STUDENT_PASSWORD",
        "password_default": "Change-Me-Student-2026!",
    },
    {
        "name": "Known Prankster",
        "email": "prank@student.edu",
        "role": "user",
        "reliability": 0.25,
        "password_env": "SEED_STUDENT_PASSWORD",
        "password_default": "Change-Me-Student-2026!",
    },
    {
        "name": "New Student",
        "email": "new@student.edu",
        "role": "user",
        "reliability": 0.50,
        "password_env": "SEED_STUDENT_PASSWORD",
        "password_default": "Change-Me-Student-2026!",
    },
    {
        "name": "Campus Nurse",
        "email": "nurse@crisis.ai",
        "role": "user",
        "reliability": 0.85,
        "password_env": "SEED_NURSE_PASSWORD",
        "password_default": "Change-Me-Nurse-2026!",
    },
]


def _get_password(user_data):
    """Resolve password from environment variable or use default.
    Always returns a secure hashed value — never plain text."""
    plain = os.getenv(user_data["password_env"], user_data["password_default"])
    return generate_password_hash(plain)


def seed_database():
    """Seed the database with demo users (passwords hashed at seed time)."""
    # ── Create Default Community ──────────────────────────────
    default_comm = Community.query.filter_by(name="Global Campus").first()
    if not default_comm:
        default_comm = Community(
            name="Global Campus",
            city="Demo City",
            type="university",
            tier="advanced",
            join_code="DEMO12"
        )
        db.session.add(default_comm)
        db.session.commit()

    created = 0
    for user_data in DEMO_USERS:
        existing = User.query.filter_by(email=user_data["email"]).first()
        if existing:
            continue

        user = User(
            name=user_data["name"],
            email=user_data["email"],
            role=user_data["role"],
            reliability_score=user_data["reliability"],
            community_id=default_comm.id,
            # Phase 0: hash is generated here — no plain text stored
            password_hash=_get_password(user_data),
        )
        db.session.add(user)
        created += 1

    db.session.commit()
    return created


def register_seed_command(app):
    """Register the 'flask seed' and 'flask reset-db' CLI commands."""
    import click

    @app.cli.command("seed")
    def seed_cmd():
        """Seed the database with demo users."""
        count = seed_database()
        click.echo(f"✅ Seeded {count} demo users. Total: {User.query.count()}")
        click.echo("⚠️  Remember to set SEED_*_PASSWORD env vars before any public demo.")

    @app.cli.command("reset-db")
    def reset_db_cmd():
        """Drop all tables and recreate with seed data."""
        from .models import Alert, CrowdVote, AuditLog
        click.echo("Dropping all tables...")
        db.drop_all()
        db.create_all()
        count = seed_database()
        click.echo(f"Database reset. Seeded {count} demo users.")

    @app.cli.command("train-classifier")
    def train_classifier_cmd():
        """Phase 2.1: Train and save the TF-IDF + LinearSVC alert classifier."""
        click.echo("Training TF-IDF + LinearSVC classifier on built-in examples...")
        try:
            from .ml.classifier import CrisisClassifier
            _, _, accuracy = CrisisClassifier.train(save=True)
            click.echo(f"Training complete. Cross-validated accuracy: {accuracy:.1%}")
            click.echo("Model saved to app/ml/model.pkl and app/ml/vectorizer.pkl")
        except Exception as e:
            click.echo(f"Training failed: {e}")
