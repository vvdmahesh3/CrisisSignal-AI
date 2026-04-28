"""
CrisisSignal AI — Demo Scenario Engine
Complete demo scenario runner with timed auto-voting and WebSocket narration.

Fixed: removed broadcast=True (Flask-SocketIO v5 removed it).
       All socketio.emit() calls now use namespace='/' which broadcasts by default.
"""

import threading
import time
import traceback
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..extensions import db, socketio
from ..models import Alert, User, CrowdVote, AuditLog
from ..ai_engine import process_alert, DEMO_SCENARIOS
from ..services.alert_service import AlertService
from ..services.confidence_service import ConfidenceService
from ..services.audit_service import AuditService

demo_bp = Blueprint("demo", __name__)


def _emit(event, data):
    """Safe socketio emit — no broadcast=True (removed in Flask-SocketIO v5)."""
    try:
        socketio.emit(event, data)
    except Exception as e:
        print(f"[Demo] emit '{event}' failed: {e}")


@demo_bp.route("/")
@login_required
def scenarios():
    """Demo scenario selection page."""
    return render_template("demo/scenarios.html", scenarios=DEMO_SCENARIOS)


@demo_bp.route("/run/<scenario_id>", methods=["POST"])
@login_required
def run_scenario(scenario_id):
    """
    Execute a demo scenario with timed auto-voting.
    Returns JSON always — never HTML — so the frontend can parse it cleanly.
    """
    try:
        if scenario_id not in DEMO_SCENARIOS:
            return jsonify({"error": "Unknown scenario"}), 404

        scenario = DEMO_SCENARIOS[scenario_id]
        auto_reset = False
        if request.is_json:
            try:
                auto_reset = request.get_json(silent=True).get("reset", False)
            except Exception:
                pass

        # ── Step 1: Optional reset ────────────────────────────────
        if auto_reset:
            try:
                CrowdVote.query.delete()
                AuditLog.query.delete()
                Alert.query.delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"[Demo] Reset failed: {e}")

        # ── Step 2: Create the alert ──────────────────────────────
        alert = AlertService.create_alert(
            message=scenario["message"],
            location=scenario["location"],
            user_id=current_user.id,
        )

        # ── Step 3: Emit scenario start ───────────────────────────
        _emit("scenario_start", {
            "scenario_id": scenario_id,
            "scenario_name": scenario["name"],
            "alert": alert.to_dict(),
            "total_steps": len(scenario["simulated_votes"]),
        })

        # ── Step 4: Spawn background auto-voter thread ────────────
        from flask import current_app
        app = current_app._get_current_object()

        thread = threading.Thread(
            target=_run_simulated_votes,
            args=(app, alert.id, scenario["simulated_votes"], scenario_id),
            daemon=True,
        )
        thread.start()

        return jsonify({
            "success": True,
            "alert": alert.to_dict(),
            "scenario": scenario_id,
            "steps": len(scenario["simulated_votes"]),
            "message": f"▶ '{scenario['name']}' started! Watch the confidence bar rise...",
        })

    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@demo_bp.route("/reset", methods=["POST"])
@login_required
def reset_system():
    """Reset all data for a clean demo."""
    try:
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        CrowdVote.query.delete()
        AuditLog.query.delete()
        Alert.query.delete()
        db.session.commit()

        _emit("system_reset", {"message": "System has been reset for demo"})

        return jsonify({"success": True, "message": "System cleared for demo"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def _run_simulated_votes(app, alert_id, votes_config, scenario_id):
    """
    Background thread: simulate crowd votes at timed intervals.
    Each vote triggers real confidence recalculation and WebSocket events.
    """
    with app.app_context():
        try:
            for step_index, vote_config in enumerate(votes_config):
                delay_seconds = vote_config.get("delay", 2000) / 1000
                time.sleep(delay_seconds)

                alert = db.session.get(Alert, alert_id)
                if not alert or alert.status in ("resolved", "rejected"):
                    break

                voter_name = vote_config["user"]
                vote_type  = vote_config["vote"]
                reliability = vote_config["reliability"]

                old_confidence = alert.confidence

                if vote_type == "confirm":
                    alert.confirmations_count += 1
                    alert.weighted_confirms += reliability
                else:
                    alert.rejections_count += 1
                    alert.weighted_rejects += reliability

                reporter = alert.reporter
                reporter_reliability = reporter.reliability_score if reporter else 0.5

                new_confidence = ConfidenceService.recalculate(
                    initial_confidence=alert.initial_confidence,
                    weighted_confirms=alert.weighted_confirms,
                    weighted_rejects=alert.weighted_rejects,
                    reporter_reliability=reporter_reliability,
                )

                old_status = alert.status
                new_status = ConfidenceService.determine_status(
                    confidence=new_confidence,
                    severity=alert.severity,
                    weighted_confirms=alert.weighted_confirms,
                    weighted_rejects=alert.weighted_rejects,
                    total_votes=alert.total_votes,
                )

                alert.confidence = new_confidence
                alert.status = new_status

                AuditService.log_event(
                    alert_id=alert_id,
                    actor_id=None,
                    action=f"DEMO_VOTE_{vote_type.upper()}",
                    previous_value=f"confidence={old_confidence:.2f}",
                    new_value=f"confidence={new_confidence:.2f}",
                    detail=f"[Demo] {voter_name} voted {vote_type} (reliability: {reliability:.2f})",
                )

                if old_status != new_status:
                    AuditService.log_event(
                        alert_id=alert_id,
                        actor_id=None,
                        action="STATUS_CHANGE",
                        previous_value=old_status,
                        new_value=new_status,
                        detail="Status changed due to demo crowd verification",
                    )

                db.session.commit()

                # ── WebSocket events ──────────────────────────────
                _emit("scenario_step", {
                    "scenario_id": scenario_id,
                    "step": step_index + 1,
                    "total_steps": len(votes_config),
                    "voter": voter_name,
                    "vote": vote_type,
                    "reliability": reliability,
                    "alert": alert.to_dict(),
                    "old_confidence": old_confidence,
                    "new_confidence": new_confidence,
                    "old_status": old_status,
                    "new_status": new_status,
                    "status_changed": old_status != new_status,
                })

                _emit("confidence_update", {
                    "alert_id": alert.id,
                    "old_confidence": old_confidence,
                    "new_confidence": new_confidence,
                    "status": new_status,
                })

                _emit("vote_update", {
                    "alert_id": alert.id,
                    "voter": voter_name,
                    "vote": vote_type,
                    "reliability": reliability,
                    "confirmations": alert.confirmations_count,
                    "rejections": alert.rejections_count,
                })

                if old_status != new_status:
                    _emit("status_change", {
                        "alert_id": alert.id,
                        "old_status": old_status,
                        "new_status": new_status,
                        "confidence": new_confidence,
                        "severity": alert.severity,
                    })
                    if new_status == "critical":
                        _emit("critical_alert", alert.to_dict())

            # ── Scenario complete ─────────────────────────────────
            _emit("scenario_complete", {
                "scenario_id": scenario_id,
                "alert_id": alert_id,
                "message": "Demo scenario completed successfully!",
            })

        except Exception as e:
            traceback.print_exc()
            _emit("scenario_error", {
                "scenario_id": scenario_id,
                "error": str(e),
            })
