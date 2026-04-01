"""
CrisisSignal AI — Flask Application
Main backend with all endpoints
"""

from flask import Flask, render_template, request, jsonify
from ai_engine import process_alert, update_confidence_with_crowd, determine_status, DEMO_SCENARIOS
import uuid
import time

app = Flask(__name__)

# ── In-Memory Store (for demo) ────────────────────────────────
alerts_store = {}
votes_store = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/alerts", methods=["POST"])
def create_alert():
    """Submit a new alert — AI processes it immediately"""
    data = request.json
    message = data.get("message", "").strip()
    location = data.get("location", "Unknown")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # AI Processing
    result = process_alert(message, location)

    alert_id = str(uuid.uuid4())[:8]
    alert = {
        "id": alert_id,
        "message": message,
        "location": location,
        "type": result["type"],
        "severity": result["severity"],
        "confidence": result["confidence"],
        "initial_confidence": result["confidence"],
        "evidence_score": result["evidence_score"],
        "evidence_strength": result["evidence_strength"],
        "evidence_detail": result["evidence_detail"],
        "keywords_found": result["keywords_found"],
        "urgency_level": result["urgency_level"],
        "suspicion_flags": result["suspicion_flags"],
        "explanation": result["explanation"],
        "status": "new",
        "confirmations": 0,
        "rejections": 0,
        "weighted_confirms": 0.0,
        "weighted_rejects": 0.0,
        "total_votes": 0,
        "votes": [],
        "created_at": time.time(),
        "timeline": [
            {
                "event": "Alert Created",
                "detail": f"AI classified as {result['type'].upper()} | Severity {result['severity']}/10",
                "time": time.time()
            }
        ]
    }

    # FIX 2: Fallback mode — starts as awaiting_review until votes come
    alert["status"] = "awaiting_review"
    alert["timeline"].append({
        "event": "Awaiting Verification",
        "detail": "No crowd votes yet — Admin review recommended",
        "time": time.time()
    })

    alerts_store[alert_id] = alert
    votes_store[alert_id] = []

    return jsonify(alert), 201


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Get all alerts sorted by priority"""
    alerts = list(alerts_store.values())
    # Sort by severity * confidence descending
    alerts.sort(key=lambda a: a["severity"] * a["confidence"], reverse=True)
    return jsonify(alerts)


@app.route("/api/alerts/<alert_id>", methods=["GET"])
def get_alert(alert_id):
    """Get a single alert with full details"""
    alert = alerts_store.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    return jsonify(alert)


@app.route("/api/alerts/<alert_id>/vote", methods=["POST"])
def vote_alert(alert_id):
    """Cast a crowd verification vote on an alert"""
    alert = alerts_store.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    data = request.json
    vote_type = data.get("vote", "confirm")  # confirm or reject
    voter_name = data.get("voter_name", "Anonymous")
    voter_reliability = float(data.get("reliability", 0.5))

    # Record vote
    vote_record = {
        "voter": voter_name,
        "vote": vote_type,
        "reliability": voter_reliability,
        "weight": voter_reliability,
        "time": time.time()
    }
    alert["votes"].append(vote_record)

    # Update counts
    if vote_type == "confirm":
        alert["confirmations"] += 1
        alert["weighted_confirms"] += voter_reliability
    else:
        alert["rejections"] += 1
        alert["weighted_rejects"] += voter_reliability

    alert["total_votes"] += 1

    # Recalculate confidence
    new_confidence = update_confidence_with_crowd(
        alert["initial_confidence"],
        alert["weighted_confirms"],
        alert["weighted_rejects"],
        0.5  # reporter reliability placeholder
    )
    alert["confidence"] = new_confidence

    # Determine new status
    new_status = determine_status(
        new_confidence,
        alert["severity"],
        alert["weighted_confirms"],
        alert["weighted_rejects"],
        alert["total_votes"]
    )

    old_status = alert["status"]
    alert["status"] = new_status

    # Timeline event
    alert["timeline"].append({
        "event": f"Vote: {'✅ Confirm' if vote_type == 'confirm' else '❌ Reject'}",
        "detail": f"{voter_name} (reliability: {voter_reliability:.2f}) — Confidence now {new_confidence:.2f}",
        "time": time.time()
    })

    if old_status != new_status:
        alert["timeline"].append({
            "event": f"Status → {new_status.upper()}",
            "detail": f"Transitioned from {old_status} to {new_status}",
            "time": time.time()
        })

    return jsonify(alert)


@app.route("/api/alerts/<alert_id>/resolve", methods=["POST"])
def resolve_alert(alert_id):
    """Admin resolves an alert"""
    alert = alerts_store.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    alert["status"] = "resolved"
    alert["timeline"].append({
        "event": "Alert Resolved",
        "detail": "Marked as resolved by admin",
        "time": time.time()
    })
    return jsonify(alert)


@app.route("/api/demo-scenarios", methods=["GET"])
def get_demo_scenarios():
    """FIX 4: Get available demo scenarios"""
    return jsonify(DEMO_SCENARIOS)


@app.route("/api/reset", methods=["POST"])
def reset_system():
    """Reset all alerts for demo"""
    alerts_store.clear()
    votes_store.clear()
    return jsonify({"status": "reset", "message": "System cleared"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
