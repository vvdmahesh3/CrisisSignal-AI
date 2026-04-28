"""
CrisisSignal AI — Authentication Routes
Login, Register, Logout with Flask-Login.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db, limiter
from ..models import User, Community
import string
import random

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"], error_message="Too many login attempts. Please wait.")
def login():
    """User login page and handler."""
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_security:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("alerts.user_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get("next")
            flash("Welcome back!", "success")

            # Redirect based on role
            if user.is_admin:
                return redirect(next_page or url_for("admin.dashboard"))
            elif user.is_security:
                return redirect(next_page or url_for("admin.security_view"))
            else:
                return redirect(next_page or url_for("alerts.user_dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page and handler."""
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_security:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("alerts.user_dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # ── Community Validation ──────────────────────────────
        errors = []
        community_action = request.form.get("community_action", "join")
        community = None
        
        if community_action == "join":
            join_code = request.form.get("join_code", "").strip().upper()
            if not join_code:
                errors.append("Please provide a join code to connect to your community.")
            else:
                community = Community.query.filter_by(join_code=join_code).first()
                if not community:
                    errors.append("Invalid join code. No community found.")
        elif community_action == "create":
            comm_name = request.form.get("community_name", "").strip()
            comm_city = request.form.get("community_city", "").strip()
            comm_type = request.form.get("community_type", "apartment")
            if not comm_name or not comm_city:
                errors.append("Community Name and City are required to create a new organization.")

        # ── Basic Validation ──────────────────────────────────────
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters.")
        if not email or "@" not in email:
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("auth/register.html")

        # ── Create Community (If Applicable) ──────────────────
        if community_action == "create":
            join_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            community = Community(
                name=request.form.get("community_name", "").strip(),
                city=request.form.get("community_city", "").strip(),
                type=request.form.get("community_type", "apartment"),
                join_code=join_code,
                tier="standard"
            )
            db.session.add(community)
            db.session.flush()  # To get the community.id

        # ── Create User ───────────────────────────────────────
        role = "admin" if community_action == "create" else "user"
        user = User(name=name, email=email, role=role, community_id=community.id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        if community_action == "create":
            flash(f"Community created successfully! Your Join Code is {community.join_code}", "success")
        else:
            flash(f"Successfully joined {community.name}! Welcome to CrisisSignal AI.", "success")
            
        return redirect(url_for("alerts.user_dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
