"""
CrisisSignal AI — Database Models
SQLAlchemy models for Users, Alerts, Crowd Votes, and Audit Log.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db
import json

class Community(db.Model):
    """Multi-tenant isolation for different apartments, lodges, or cities."""

    __tablename__ = "communities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False, default="apartment")  # apartment, lodge, gated_community
    tier = db.Column(db.String(20), nullable=False, default="standard")   # simple, standard, advanced
    join_code = db.Column(db.String(20), unique=True, nullable=False)
    settings = db.Column(db.Text, nullable=True)  # Store JSON as text for SQLite compatibility
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────
    users = db.relationship("User", backref="community", lazy="dynamic")
    alerts = db.relationship("Alert", backref="community", lazy="dynamic")
    audit_logs = db.relationship("AuditLog", backref="community", lazy="dynamic")
    
    @property
    def settings_dict(self):
        return json.loads(self.settings) if self.settings else {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "type": self.type,
            "tier": self.tier,
            "join_code": self.join_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Community {self.name} | {self.city} | tier={self.tier}>"


class User(UserMixin, db.Model):
    """User model with self-learning reliability metrics."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    reliability_score = db.Column(db.Float, nullable=False, default=0.5)
    total_reports = db.Column(db.Integer, nullable=False, default=0)
    confirmed_reports = db.Column(db.Integer, nullable=False, default=0)
    rejected_reports = db.Column(db.Integer, nullable=False, default=0)
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Multi-Tenancy Key
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=True)

    # ── Relationships ─────────────────────────────────────────
    alerts = db.relationship(
        "Alert", backref="reporter", lazy="dynamic",
        foreign_keys="Alert.reported_by"
    )
    votes = db.relationship("CrowdVote", backref="voter", lazy="dynamic")

    # ── Password Handling ─────────────────────────────────────
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ── Reliability Score Management ──────────────────────────
    def adjust_reliability(self, delta):
        """Adjust reliability score with clamping to [0.0, 1.0]."""
        self.reliability_score = max(0.0, min(1.0, self.reliability_score + delta))

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_security(self):
        return self.role == "security"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "reliability_score": self.reliability_score,
            "total_reports": self.total_reports,
            "confirmed_reports": self.confirmed_reports,
            "rejected_reports": self.rejected_reports,
            "is_flagged": self.is_flagged,
            "community_id": self.community_id,
            "community_name": self.community.name if self.community else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.name} | {self.role} | reliability={self.reliability_score:.2f}>"


class Alert(db.Model):
    """Alert model — core lifecycle container for crisis events."""

    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default="general")
    severity = db.Column(db.Integer, nullable=False, default=1)
    location = db.Column(db.String(100))
    confidence = db.Column(db.Float, nullable=False, default=0.5)
    initial_confidence = db.Column(db.Float, nullable=False, default=0.5)
    confirmations_count = db.Column(db.Integer, nullable=False, default=0)
    rejections_count = db.Column(db.Integer, nullable=False, default=0)
    weighted_confirms = db.Column(db.Float, nullable=False, default=0.0)
    weighted_rejects = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default="new")
    evidence_score = db.Column(db.Integer, default=0)
    evidence_strength = db.Column(db.String(20), default="Weak")
    explanation = db.Column(db.Text)
    keywords_found = db.Column(db.Text, default="")  # Comma-separated
    urgency_level = db.Column(db.String(20), default="none")
    suspicion_flags = db.Column(db.Text, default="")  # Comma-separated
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolution_note = db.Column(db.Text)
    parent_alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"))
    reported_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ── Phase 3: New Feature Fields ───────────────────────────
    photo_path   = db.Column(db.String(255), nullable=True)   # Relative path to uploaded evidence photo
    assigned_to  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Responder assignment
    contact_phone = db.Column(db.String(20), nullable=True)   # Reporter emergency contact
    is_emergency = db.Column(db.Boolean, nullable=False, default=False)  # True = one-tap emergency

    # Multi-Tenancy Key
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=True)

    # ── Relationships ─────────────────────────────────────────
    votes = db.relationship(
        "CrowdVote", backref="alert", lazy="dynamic",
        cascade="all, delete-orphan"
    )
    children = db.relationship(
        "Alert", backref=db.backref("parent", remote_side=[id])
    )
    audit_entries = db.relationship(
        "AuditLog", backref="alert", lazy="dynamic"
    )
    # Phase 3: assigned responder relationship
    responder = db.relationship(
        "User", foreign_keys=[assigned_to], backref="assigned_alerts"
    )

    @property
    def priority_score(self):
        """Priority = severity × confidence. Used for dashboard sorting."""
        return (self.severity or 0) * (self.confidence or 0)

    @property
    def total_votes(self):
        return (self.confirmations_count or 0) + (self.rejections_count or 0)

    def to_dict(self):
        """Serialize alert to a JSON-safe dictionary with null-safe fallbacks."""
        return {
            "id": self.id,
            "message": self.message or "",
            "type": self.type or "general",
            "severity": self.severity or 0,
            "location": self.location or "Unknown",
            "confidence": self.confidence or 0,
            "initial_confidence": self.initial_confidence or 0,
            "confirmations_count": self.confirmations_count or 0,
            "rejections_count": self.rejections_count or 0,
            "weighted_confirms": self.weighted_confirms or 0,
            "weighted_rejects": self.weighted_rejects or 0,
            "status": self.status or "new",
            "evidence_score": self.evidence_score or 0,
            "evidence_strength": self.evidence_strength or "Weak",
            "explanation": self.explanation or "",
            "keywords_found": self.keywords_found.split(",") if self.keywords_found else [],
            "urgency_level": self.urgency_level or "standard",
            "suspicion_flags": self.suspicion_flags.split(",") if self.suspicion_flags else [],
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_note": self.resolution_note or "",
            "parent_alert_id": self.parent_alert_id,
            "reported_by": self.reported_by,
            "community_id": self.community_id,
            "reporter_name": self.reporter.name if self.reporter else "Unknown",
            "total_votes": self.total_votes,
            "priority_score": round(self.priority_score, 2),
            # Phase 3 fields
            "photo_path": self.photo_path,
            "assigned_to": self.assigned_to,
            "responder_name": self.responder.name if self.responder else None,
            "contact_phone": self.contact_phone or "",
            "is_emergency": self.is_emergency or False,
        }

    def __repr__(self):
        return f"<Alert #{self.id} | {self.type} | sev={self.severity} | conf={self.confidence:.2f} | {self.status}>"


class CrowdVote(db.Model):
    """Community verification evidence stream."""

    __tablename__ = "crowd_votes"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(
        db.Integer, db.ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vote = db.Column(db.String(10), nullable=False)  # 'confirm' or 'reject'
    vote_weight = db.Column(db.Float, nullable=False)
    voted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "alert_id", "user_id",
            name="one_vote_per_user_per_alert"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "voter_name": self.voter.name if self.voter else "Unknown",
            "vote": self.vote,
            "vote_weight": self.vote_weight,
            "voted_at": self.voted_at.isoformat() if self.voted_at else None,
        }

    def __repr__(self):
        return f"<Vote #{self.id} | alert={self.alert_id} | {self.vote} | weight={self.vote_weight:.2f}>"


class AuditLog(db.Model):
    """Immutable record of all system state changes."""

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=True)  # Nullable for user-level events
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # NULL for system
    action = db.Column(db.String(50), nullable=False)
    previous_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    detail = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Multi-Tenancy Key
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=True)

    # ── Relationship ──────────────────────────────────────────
    actor = db.relationship("User", backref="audit_actions", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "actor_id": self.actor_id,
            "actor_name": self.actor.name if self.actor else "System",
            "action": self.action,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "detail": self.detail,
            "community_id": self.community_id,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
        }

    def __repr__(self):
        return f"<AuditLog #{self.id} | alert={self.alert_id} | {self.action}>"
