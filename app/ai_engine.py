"""
CrisisSignal AI Engine — Phase 2 Upgrade
- Phase 2.1: TF-IDF + LinearSVC ML classifier (keyword fallback retained)
- Phase 2.2: Negation detection ("no fire" != "fire")
- Phase 2.3: Hindi/Hinglish transliterated keyword support
- Phase 1.6: Safety floor for general/unclassified dangerous reports
- Classification → Urgency → Severity → Confidence → Evidence → Explanation
"""

import re
from datetime import datetime

# ── Category Keywords (English) ────────────────────────────────
CATEGORY_KEYWORDS = {
    "fire":     ["fire", "smoke", "burning", "flame", "blaze", "ash", "sparks", "inferno", "combustion"],
    "medical":  ["fainted", "unconscious", "bleeding", "hurt", "ambulance", "heart", "breathing", "seizure", "injury", "collapsed"],
    "theft":    ["stolen", "theft", "robbed", "pickpocket", "missing", "snatched", "burglar", "looted"],
    "violence": ["fight", "attack", "weapon", "assault", "threat", "hitting", "beating", "knife", "gun", "stabbing"],
    "infra":    ["leak", "short circuit", "flood", "power cut", "broken", "gas", "elevator stuck", "collapse", "crack"],
}

# ── Phase 2.3: Hindi / Hinglish Transliterated Keywords ────────
# Common transliterated words used in Indian campus/apartment reports
HINDI_KEYWORDS = {
    "fire":     ["aag", "aag lagi", "dhuan", "jal raha", "jal rahi", "aag lag gayi", "smoke aa raha"],
    "medical":  ["behosh", "girpada", "khoon", "ambulance chahiye", "doctor bulao", "bimaar", "chot lagi"],
    "theft":    ["chori", "chor", "churaya", "bag gaya", "phone gaya", "loot gaya", "daka"],
    "violence": ["maar pit", "ladai", "hathiyaar", "dhakka", "dhamki", "pit raha", "hath utha"],
    "infra":    ["paani tapak", "bijli gayi", "lift band", "gas nikal raha", "chhat toot", "daraar"],
}

# ── Urgency Amplifiers ─────────────────────────────────────────
URGENCY_PHRASES = {
    "high":   ["immediately", "right now", "urgent", "emergency", "call police", "help", "dying", "hurry",
               "jaldi", "abhi", "turant", "bachao"],
    "medium": ["quickly", "asap", "need help", "please come", "serious"],
    "low":    ["might be", "i think", "maybe", "not sure", "possibly", "shayad"],
}

# ── Negation Words (Phase 2.2) ─────────────────────────────────
NEGATION_WORDS = ["no", "not", "none", "without", "never", "false", "fake",
                  "nahi", "nahi hai", "nahin", "bilkul nahi"]

# ── Suspicion Indicators ───────────────────────────────────────
SUSPICION_WORDS = ["fake", "joke", "prank", "just kidding", "hoax", "lol", "haha", "testing", "drill"]

# ── Harm & Location Indicators ────────────────────────────────
HARM_INDICATORS = ["bleeding", "unconscious", "trapped", "cannot breathe", "injury", "dying", "collapsed", "critical condition"]
LOCATION_MULTIPLIERS = ["main gate", "children", "crowded", "parking", "hostel", "lab", "library", "auditorium", "canteen"]

# ── Base Severity per Category ─────────────────────────────────
CATEGORY_BASE_SEVERITY = {
    "fire": 7, "violence": 7, "medical": 6,
    "theft": 4, "infra": 4, "general": 1
}


# ── Phase 2.2: Negation Detection ──────────────────────────────

def _is_negated(keyword, tokens, window=3):
    """
    Return True if `keyword` is preceded by a negation word within `window` tokens.

    Example: "there is NO fire here" → fire is negated.
    Example: "there is fire, not water" → fire is NOT negated (negation comes after).
    """
    kw_index = -1
    keyword_tokens = keyword.lower().split()

    # Find start index of keyword in token list
    for i in range(len(tokens) - len(keyword_tokens) + 1):
        if tokens[i:i + len(keyword_tokens)] == keyword_tokens:
            kw_index = i
            break

    if kw_index == -1:
        return False

    # Check window before the keyword
    context_before = tokens[max(0, kw_index - window):kw_index]
    return any(neg in context_before for neg in NEGATION_WORDS)


def classify_text(text):
    """
    Stage 1: Classification — tries ML classifier first, falls back to keywords.

    Phase 2.1: Uses TF-IDF + LinearSVC if trained model is available.
    Phase 2.2: Negation detection removes false keyword matches.
    Phase 2.3: Hindi/Hinglish keywords included.

    Returns: (category, match_count, matched_keywords, ml_used, ml_confidence)
    """
    text_lower = text.lower()
    tokens = text_lower.split()

    # ── Step A: Try ML classifier ─────────────────────────────
    ml_category, ml_confidence = "general", 0.25
    ml_used = False

    try:
        from .ml.classifier import CrisisClassifier
        if CrisisClassifier.is_available():
            ml_category, ml_confidence = CrisisClassifier.predict(text)
            ml_used = True
    except Exception:
        pass

    # ── Step B: Keyword matching with negation filter ─────────
    scores = {}
    matched = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        valid_matches = [
            kw for kw in keywords
            if kw in text_lower and not _is_negated(kw, tokens)
        ]
        scores[category] = len(valid_matches)
        matched[category] = valid_matches

    # ── Step C: Hindi/Hinglish keywords ───────────────────────
    for category, hindi_kws in HINDI_KEYWORDS.items():
        extra = [kw for kw in hindi_kws if kw in text_lower]
        scores[category] = scores.get(category, 0) + len(extra)
        matched[category] = matched.get(category, []) + extra

    top_keyword_category = max(scores, key=scores.get)
    top_keyword_count = scores[top_keyword_category]
    top_matched = matched[top_keyword_category]

    # ── Step D: Combine ML + keywords ────────────────────────
    if ml_used and top_keyword_count == 0:
        # ML only — no keyword evidence
        return ml_category, 0, [], True, ml_confidence
    elif ml_used and top_keyword_count > 0:
        # Both agree → high confidence
        if ml_category == top_keyword_category:
            return ml_category, top_keyword_count, top_matched, True, ml_confidence
        # Disagree → trust keywords more (they matched concrete words)
        return top_keyword_category, top_keyword_count, top_matched, True, ml_confidence * 0.8
    else:
        # Keyword-only fallback
        if top_keyword_count == 0:
            return "general", 0, [], False, 0.25
        return top_keyword_category, top_keyword_count, top_matched, False, 0.25


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
    """Stage 3: Severity scoring (1-10).

    Phase 1.6 — Safety floor: If urgency is high AND harm/location evidence
    is present, severity is floored at 5 regardless of category. This prevents
    dangerous unclassified reports (e.g. 'someone is hurt at the gate') from
    falling through with severity=1 just because they hit no keywords.
    """
    base = CATEGORY_BASE_SEVERITY.get(category, 1)
    text_lower = text.lower()

    harm_bonus = sum(2 for h in HARM_INDICATORS if h in text_lower)
    location_bonus = sum(1 for loc in LOCATION_MULTIPLIERS if loc in text_lower)

    severity = base + urgency_weight + harm_bonus + location_bonus

    # Safety floor: dangerous-but-unclassified reports must not be ignored
    if urgency_weight >= 3 and (harm_bonus > 0 or location_bonus > 0):
        severity = max(severity, 5)

    return max(1, min(10, severity))


def calculate_initial_confidence(keyword_match_count, suspicion_flags, ml_confidence=None, ml_used=False):
    """Stage 4: Initial confidence — blends keyword score with ML confidence.

    Phase 2.1: When ML model is available, confidence is a weighted blend.
    """
    # Keyword-based base
    if keyword_match_count == 0:
        keyword_base = 0.25
    elif keyword_match_count == 1:
        keyword_base = 0.50
    elif keyword_match_count >= 3:
        keyword_base = 0.75
    else:
        keyword_base = 0.65

    if ml_used and ml_confidence is not None:
        # Blend: 60% ML + 40% keyword base
        base = (ml_confidence * 0.60) + (keyword_base * 0.40)
    else:
        base = keyword_base

    # Suspicion penalty
    if suspicion_flags:
        base *= 0.6  # 40% penalty

    return round(min(1.0, max(0.0, base)), 4)


def calculate_evidence_score(keyword_count, urgency_level, harm_count, location_count, suspicion_count):
    """
    Evidence Score — aggregates signal count and quality.
    Returns (score 0-100, strength label, detail breakdown)
    """
    signal_count = keyword_count + (1 if urgency_level != "none" else 0) + harm_count + location_count
    urgency_multiplier = {"high": 1.5, "medium": 1.2, "low": 0.8, "none": 1.0}[urgency_level]
    base = min(signal_count * 15, 60)
    urgency_bonus = 20 if urgency_level == "high" else (10 if urgency_level == "medium" else 0)
    context_bonus = min((harm_count + location_count) * 10, 20)
    suspicion_penalty = suspicion_count * 15

    score = min(100, max(0, int((base + urgency_bonus + context_bonus - suspicion_penalty) * urgency_multiplier)))

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
                         confidence, suspicion_flags, evidence_strength, evidence_score,
                         ml_used=False, negation_filtered=False):
    """Stage 5: X-Logic explanation generator — Phase 2 upgrade."""
    parts = []

    if ml_used:
        parts.append("AI classification: ML model (TF-IDF + LinearSVC)")

    if keywords_found:
        kw_str = ", ".join([f"'{kw}'" for kw in keywords_found])
        parts.append(f"Detected keywords: {kw_str} ({alert_type} indicators)")

    if negation_filtered:
        parts.append("Note: Some keywords were filtered due to negation context")

    if urgency_phrases:
        parts.append(f"Urgency phrases detected: {', '.join(urgency_phrases)} (level: {urgency_level})")

    if suspicion_flags:
        parts.append(f"Suspicion detected: {', '.join(suspicion_flags)} — confidence penalized")

    parts.append(f"Evidence Strength: {evidence_strength} (score: {evidence_score}/100)")
    parts.append(f"Initial severity: {severity}/10, confidence: {confidence:.2f}")

    return ". ".join(parts) + "."


def process_alert(text, location="Unknown"):
    """
    Full AI pipeline — Phase 2 upgraded version.
    Runs ML + keyword classification, negation detection, Hindi support.
    """
    # Stage 1: Classification (ML + keywords + Hindi + negation)
    alert_type, keyword_count, keywords_found, ml_used, ml_confidence = classify_text(text)

    # Stage 2: Urgency
    urgency_weight, urgency_level, urgency_phrases = get_urgency_info(text)

    # Suspicion check
    suspicion_flags = get_suspicion_info(text)

    # Stage 3: Severity
    severity = calculate_severity(alert_type, text, urgency_weight)

    # Stage 4: Confidence (blends ML + keyword)
    confidence = calculate_initial_confidence(keyword_count, suspicion_flags, ml_confidence, ml_used)

    # Evidence Score
    text_lower = text.lower()
    harm_count = sum(1 for h in HARM_INDICATORS if h in text_lower)
    location_count = sum(1 for loc in LOCATION_MULTIPLIERS if loc in text_lower)

    evidence_score, evidence_strength, evidence_detail = calculate_evidence_score(
        keyword_count, urgency_level, harm_count, location_count, len(suspicion_flags)
    )

    # Stage 5: Explanation
    explanation = generate_explanation(
        alert_type, keywords_found, severity, urgency_level, urgency_phrases,
        confidence, suspicion_flags, evidence_strength, evidence_score,
        ml_used=ml_used,
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
        "ml_used": ml_used,
    }


def update_confidence_with_crowd(initial_confidence, weighted_confirms, weighted_rejects, reporter_reliability):
    """Recalculate confidence after crowd votes"""
    total = weighted_confirms + weighted_rejects + 0.001
    crowd_score = weighted_confirms / total
    reliability_bonus = 0.10 if reporter_reliability > 0.75 else 0.0
    new_confidence = (initial_confidence * 0.40) + (crowd_score * 0.40) + (reliability_bonus * 0.20)
    return round(max(0.0, min(1.0, new_confidence)), 4)


def determine_status(confidence, severity, weighted_confirms, weighted_rejects, total_votes):
    """Determine alert status from confidence/severity/votes"""
    if total_votes == 0:
        return "awaiting_review"
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


# ── Demo Scenarios ────────────────────────────────────────────
DEMO_SCENARIOS = {
    "fire": {
        "name": "🔥 Fire in the Hostel",
        "tagline": "Watch a real emergency escalate from NEW → CRITICAL in real time",
        "message": (
            "URGENT! Heavy smoke is pouring out of the 3rd floor staircase in Block C. "
            "Burning smell is very strong — smells like electrical fire. People are running "
            "down the stairs and shouting. Someone said they saw actual flames near the fuse box. "
            "Please send help immediately, there are students still inside!"
        ),
        "location": "Block C, Floor 3 — Hostel Staircase",
        "simulated_votes": [
            {"user": "Ravi (Security Guard, Trust: 82%)",   "vote": "confirm", "reliability": 0.82, "delay": 2000},
            {"user": "Priya (Floor 3 Resident, Trust: 71%)", "vote": "confirm", "reliability": 0.71, "delay": 4000},
            {"user": "Mr. Sharma (Warden, Trust: 90%)",      "vote": "confirm", "reliability": 0.90, "delay": 6000},
            {"user": "Ankit (Nearby Room, Trust: 55%)",      "vote": "confirm", "reliability": 0.55, "delay": 8000},
            {"user": "Deepa (Ground Floor, Trust: 68%)",     "vote": "confirm", "reliability": 0.68, "delay": 10000},
        ]
    },
    "medical": {
        "name": "🚑 Student Collapsed at Library",
        "tagline": "See how trusted votes outweigh doubt — a real nurse's word matters more",
        "message": (
            "A student has collapsed near the library entrance! He is unconscious and not responding. "
            "There is bleeding from the head — looks like he hit the marble step when he fell. "
            "Someone is doing CPR but we need an ambulance RIGHT NOW. His name is Kiran, "
            "B.Tech 2nd year. Please someone call emergency services!"
        ),
        "location": "Main Library — Ground Floor Entrance",
        "simulated_votes": [
            {"user": "Meena (Library Staff, Trust: 85%)",      "vote": "confirm", "reliability": 0.85, "delay": 1500},
            {"user": "Rahul (Eyewitness Student, Trust: 60%)", "vote": "confirm", "reliability": 0.60, "delay": 3500},
            {"user": "Guard Suresh (Trust: 78%)",              "vote": "confirm", "reliability": 0.78, "delay": 5000},
            {"user": "Suspicious User (Trust: 35%)",          "vote": "reject",  "reliability": 0.35, "delay": 6500},
            {"user": "Nurse Kavitha (Trust: 94%)",            "vote": "confirm", "reliability": 0.94, "delay": 8500},
        ]
    },
    "fake": {
        "name": "🚨 Fake Bomb Rumour Test",
        "tagline": "Watch the system REJECT a false alarm — reliability scores protect the community",
        "message": (
            "omg omg guys someone said there might be a bomb somewhere near the canteen?? "
            "idk lol it might be a prank but people are acting weird haha. "
            "not sure if real or not just spreading the word lmao"
        ),
        "location": "Campus Canteen — Open Ground Area",
        "simulated_votes": [
            {"user": "Troll Account (Trust: 20%)",          "vote": "confirm", "reliability": 0.20, "delay": 2000},
            {"user": "Officer Rajan (Trust: 91%)",          "vote": "reject",  "reliability": 0.91, "delay": 3500},
            {"user": "Dr. Nair, Admin (Trust: 88%)",        "vote": "reject",  "reliability": 0.88, "delay": 5500},
            {"user": "Student Leader Sana (Trust: 72%)",   "vote": "reject",  "reliability": 0.72, "delay": 7000},
            {"user": "Canteen Staff Ram (Trust: 65%)",     "vote": "reject",  "reliability": 0.65, "delay": 9000},
        ]
    },
}
