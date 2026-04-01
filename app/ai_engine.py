"""
CrisisSignal AI Engine
- Classification (keyword + pattern)
- Severity scoring
- Confidence calculation with Evidence Score
- X-Logic explanation generator
- Evidence Strength rating (FIX 1)
"""

import re
from datetime import datetime

# ── Category Keywords ──────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "fire":     ["fire", "smoke", "burning", "flame", "blaze", "ash", "sparks", "inferno", "combustion"],
    "medical":  ["fainted", "unconscious", "bleeding", "hurt", "ambulance", "heart", "breathing", "seizure", "injury", "collapsed"],
    "theft":    ["stolen", "theft", "robbed", "pickpocket", "missing", "snatched", "burglar", "looted"],
    "violence": ["fight", "attack", "weapon", "assault", "threat", "hitting", "beating", "knife", "gun", "stabbing"],
    "infra":    ["leak", "short circuit", "flood", "power cut", "broken", "gas", "elevator stuck", "collapse", "crack"],
}

# ── Urgency Amplifiers ────────────────────────────────────────
URGENCY_PHRASES = {
    "high":   ["immediately", "right now", "urgent", "emergency", "call police", "help", "dying", "hurry"],
    "medium": ["quickly", "asap", "need help", "please come", "serious"],
    "low":    ["might be", "i think", "maybe", "not sure", "possibly"],
}

# ── Suspicion Indicators ──────────────────────────────────────
SUSPICION_WORDS = ["fake", "joke", "prank", "just kidding", "hoax", "lol", "haha", "testing", "drill"]

# ── Harm & Location Indicators ────────────────────────────────
HARM_INDICATORS = ["bleeding", "unconscious", "trapped", "cannot breathe", "injury", "dying", "collapsed", "critical condition"]
LOCATION_MULTIPLIERS = ["main gate", "children", "crowded", "parking", "hostel", "lab", "library", "auditorium", "canteen"]

# ── Base Severity per Category ────────────────────────────────
CATEGORY_BASE_SEVERITY = {
    "fire": 7, "violence": 7, "medical": 6,
    "theft": 4, "infra": 4, "general": 1
}


def classify_text(text):
    """Stage 1: Keyword classification — returns (category, match_count, matched_keywords)"""
    text_lower = text.lower()
    scores = {}
    matched = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in text_lower]
        scores[category] = len(matches)
        matched[category] = matches

    top_category = max(scores, key=scores.get)
    if scores[top_category] == 0:
        return "general", 0, []
    return top_category, scores[top_category], matched[top_category]


def get_urgency_info(text):
    """Stage 2: Urgency detection — returns (weight, level, matched_phrases)"""
    text_lower = text.lower()
    for level, phrases in URGENCY_PHRASES.items():
        found = [p for p in phrases if p in text_lower]
        if found:
            weight = {"high": 3, "medium": 1, "low": -1}[level]
            return weight, level, found
    return 0, "none", []


def get_suspicion_info(text):
    """Detect suspicion/prank indicators"""
    text_lower = text.lower()
    found = [w for w in SUSPICION_WORDS if w in text_lower]
    return found


def calculate_severity(category, text, urgency_weight):
    """Stage 3: Severity scoring (1-10)"""
    base = CATEGORY_BASE_SEVERITY.get(category, 1)
    text_lower = text.lower()

    harm_bonus = sum(2 for h in HARM_INDICATORS if h in text_lower)
    location_bonus = sum(1 for loc in LOCATION_MULTIPLIERS if loc in text_lower)

    severity = base + urgency_weight + harm_bonus + location_bonus
    return max(1, min(10, severity))


def calculate_initial_confidence(keyword_match_count, suspicion_flags):
    """Stage 4: Initial confidence — penalized by suspicion"""
    if keyword_match_count == 0:
        base = 0.25
    elif keyword_match_count == 1:
        base = 0.50
    elif keyword_match_count >= 3:
        base = 0.75
    else:
        base = 0.65

    # Suspicion penalty
    if suspicion_flags:
        base *= 0.6  # 40% penalty

    return round(min(1.0, max(0.0, base)), 4)


def calculate_evidence_score(keyword_count, urgency_level, harm_count, location_count, suspicion_count):
    """
    FIX 1: Evidence Score — aggregates signal count and quality
    Returns (score 0-100, strength label, detail breakdown)
    """
    # Number of signals
    signal_count = keyword_count + (1 if urgency_level != "none" else 0) + harm_count + location_count

    # Urgency strength multiplier
    urgency_multiplier = {"high": 1.5, "medium": 1.2, "low": 0.8, "none": 1.0}[urgency_level]

    # Base evidence from signals
    base = min(signal_count * 15, 60)  # Max 60 from signal count

    # Urgency boost
    urgency_bonus = 20 if urgency_level == "high" else (10 if urgency_level == "medium" else 0)

    # Context richness
    context_bonus = min((harm_count + location_count) * 10, 20)

    # Suspicion penalty
    suspicion_penalty = suspicion_count * 15

    score = min(100, max(0, int((base + urgency_bonus + context_bonus - suspicion_penalty) * urgency_multiplier)))

    # Determine strength label
    if score >= 70:
        strength = "Strong"
    elif score >= 40:
        strength = "Medium"
    else:
        strength = "Weak"

    detail = {
        "signal_count": signal_count,
        "urgency_strength": urgency_level,
        "context_indicators": harm_count + location_count,
        "suspicion_flags": suspicion_count,
        "raw_score": score,
    }

    return score, strength, detail


def generate_explanation(alert_type, keywords_found, severity, urgency_level, urgency_phrases,
                         confidence, suspicion_flags, evidence_strength, evidence_score):
    """Stage 5: X-Logic explanation generator"""
    parts = []

    if keywords_found:
        kw_str = ", ".join([f"'{kw}'" for kw in keywords_found])
        parts.append(f"Detected keywords: {kw_str} ({alert_type} indicators)")

    if urgency_phrases:
        parts.append(f"Urgency phrases detected: {', '.join(urgency_phrases)} (level: {urgency_level})")

    if suspicion_flags:
        parts.append(f"⚠ Suspicion detected: {', '.join(suspicion_flags)} — confidence penalized, needs verification")

    parts.append(f"Evidence Strength: {evidence_strength} (score: {evidence_score}/100)")
    parts.append(f"Initial severity: {severity}/10, confidence: {confidence:.2f}")

    return ". ".join(parts) + "."


def process_alert(text, location="Unknown"):
    """
    Full AI pipeline — processes raw text and returns complete analysis.
    """
    # Stage 1: Classification
    alert_type, keyword_count, keywords_found = classify_text(text)

    # Stage 2: Urgency
    urgency_weight, urgency_level, urgency_phrases = get_urgency_info(text)

    # Suspicion check
    suspicion_flags = get_suspicion_info(text)

    # Stage 3: Severity
    severity = calculate_severity(alert_type, text, urgency_weight)

    # Stage 4: Confidence
    confidence = calculate_initial_confidence(keyword_count, suspicion_flags)

    # FIX 1: Evidence Score
    text_lower = text.lower()
    harm_count = sum(1 for h in HARM_INDICATORS if h in text_lower)
    location_count = sum(1 for loc in LOCATION_MULTIPLIERS if loc in text_lower)

    evidence_score, evidence_strength, evidence_detail = calculate_evidence_score(
        keyword_count, urgency_level, harm_count, location_count, len(suspicion_flags)
    )

    # Stage 5: Explanation
    explanation = generate_explanation(
        alert_type, keywords_found, severity, urgency_level, urgency_phrases,
        confidence, suspicion_flags, evidence_strength, evidence_score
    )

    return {
        "type": alert_type,
        "severity": severity,
        "confidence": confidence,
        "evidence_score": evidence_score,
        "evidence_strength": evidence_strength,
        "evidence_detail": evidence_detail,
        "keywords_found": keywords_found,
        "urgency_level": urgency_level,
        "urgency_phrases": urgency_phrases,
        "suspicion_flags": suspicion_flags,
        "explanation": explanation,
        "location": location,
    }


def update_confidence_with_crowd(initial_confidence, weighted_confirms, weighted_rejects, reporter_reliability):
    """Recalculate confidence after crowd votes"""
    total = weighted_confirms + weighted_rejects + 0.001
    crowd_score = weighted_confirms / total
    reliability_bonus = 0.10 if reporter_reliability > 0.75 else 0.0

    new_confidence = (initial_confidence * 0.40) + (crowd_score * 0.40) + (reliability_bonus * 0.20)
    return round(max(0.0, min(1.0, new_confidence)), 4)


def determine_status(confidence, severity, weighted_confirms, weighted_rejects, total_votes):
    """
    Determine alert status from confidence/severity/votes
    FIX 2: Fallback mode — if no votes, recommend admin review
    """
    if total_votes == 0:
        return "awaiting_review"  # FIX 2: Fallback Mode

    if weighted_rejects > weighted_confirms * 2:
        return "rejected"
    elif confidence >= 0.85 and severity >= 8:
        return "critical"
    elif confidence >= 0.70:
        return "verified"
    elif confidence >= 0.30:
        return "verifying"
    else:
        return "new"


# ── Demo Scenarios (FIX 4) ────────────────────────────────────
DEMO_SCENARIOS = {
    "fire": {
        "name": "🔥 Fire Emergency",
        "message": "There is heavy smoke coming from the 3rd floor hostel staircase, burning smell is very strong. People are running, someone said they saw flames. Help immediately!",
        "location": "Block C, Floor 3 — Hostel Staircase",
        "simulated_votes": [
            {"user": "Campus Guard (0.82)", "vote": "confirm", "reliability": 0.82, "delay": 2000},
            {"user": "Resident Student (0.71)", "vote": "confirm", "reliability": 0.71, "delay": 3500},
            {"user": "Hostel Warden (0.90)", "vote": "confirm", "reliability": 0.90, "delay": 5000},
            {"user": "Nearby Student (0.55)", "vote": "confirm", "reliability": 0.55, "delay": 6500},
            {"user": "Passerby (0.45)", "vote": "confirm", "reliability": 0.45, "delay": 8000},
        ]
    },
    "medical": {
        "name": "🏥 Medical Emergency",
        "message": "Someone has collapsed near the library entrance, they are unconscious and not breathing properly. There's bleeding from the head. Need ambulance immediately!",
        "location": "Main Library — Ground Floor Entrance",
        "simulated_votes": [
            {"user": "Library Staff (0.85)", "vote": "confirm", "reliability": 0.85, "delay": 1500},
            {"user": "Student Witness (0.60)", "vote": "confirm", "reliability": 0.60, "delay": 3000},
            {"user": "Security Guard (0.78)", "vote": "confirm", "reliability": 0.78, "delay": 4500},
            {"user": "Curious Onlooker (0.40)", "vote": "reject", "reliability": 0.40, "delay": 6000},
            {"user": "Campus Nurse (0.92)", "vote": "confirm", "reliability": 0.92, "delay": 7500},
        ]
    },
    "fake": {
        "name": "🎭 Fake Alert Test",
        "message": "OMG there might be like a bomb or something lol not sure maybe its a joke haha but people are acting weird",
        "location": "Campus Ground — Open Area",
        "simulated_votes": [
            {"user": "Known Prankster (0.25)", "vote": "confirm", "reliability": 0.25, "delay": 2000},
            {"user": "Security Officer (0.88)", "vote": "reject", "reliability": 0.88, "delay": 3500},
            {"user": "Senior Admin (0.91)", "vote": "reject", "reliability": 0.91, "delay": 5000},
            {"user": "Student Rep (0.70)", "vote": "reject", "reliability": 0.70, "delay": 6500},
            {"user": "Random User (0.50)", "vote": "reject", "reliability": 0.50, "delay": 8000},
        ]
    }
}
