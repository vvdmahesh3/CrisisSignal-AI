"""
CrisisSignal AI — Gemini AI Service
Phase 5: Google Gemini integration for intelligent alert classification.

Uses Gemini 1.5 Flash (fastest, free tier) to classify incident reports
with human-level language understanding.

Falls back gracefully to the keyword engine if:
- API key is not set
- Gemini API is unavailable (network error, quota exceeded)
- Response cannot be parsed

This ensures the system NEVER crashes due to AI failures.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# ── Gemini Classification Prompt ──────────────────────────────
_PROMPT_TEMPLATE = """You are the AI brain of CrisisSignal — an emergency response system for campuses and apartment buildings.

Your job: Analyze this incident report and classify it so emergency responders know exactly how serious it is.

INCIDENT REPORT:
Message: "{message}"
Location: "{location}"

Respond with ONLY a valid JSON object (no markdown, no explanation outside JSON):

{{
  "type": "fire|medical|theft|violence|infra|general",
  "severity": <integer 1-10>,
  "confidence": <float 0.0-1.0>,
  "urgency_level": "high|medium|low|none",
  "keywords_found": ["word1", "word2"],
  "suspicion_flags": [],
  "explanation": "A clear 1-2 sentence explanation of why you classified it this way",
  "evidence_strength": "Strong|Medium|Weak",
  "evidence_score": <integer 0-100>
}}

SEVERITY GUIDE:
- 9-10: Life-threatening RIGHT NOW (fire with people trapped, person unconscious, active weapon)
- 7-8: Serious emergency needing immediate response
- 5-6: Significant incident, response needed soon
- 3-4: Minor incident, low urgency
- 1-2: Informational, no immediate danger

CONFIDENCE GUIDE:
- 0.80-1.0: Message is very clear about a real emergency
- 0.60-0.79: Likely real but some uncertainty
- 0.40-0.59: Could be real, needs verification
- 0.10-0.39: Vague, possibly false alarm or prank

SUSPICION FLAGS (add if applicable): "vague_language", "prank_indicators", "uncertain_language", "anonymous_tip"

TYPE GUIDE:
- fire: smoke, fire, flames, burning, explosion
- medical: injury, unconscious, fainted, bleeding, heart attack, ambulance needed
- theft: stolen, robbery, pickpocket, missing valuables
- violence: fight, assault, weapon, threat, attack
- infra: power cut, water leak, elevator stuck, structural damage, flood
- general: anything else that doesn't fit above categories
"""


def classify_with_gemini(message: str, location: str = None) -> dict | None:
    """
    Classify an incident report using Google Gemini AI.

    Returns a result dict (same format as process_alert) on success,
    or None if Gemini is unavailable (triggers keyword engine fallback).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.debug("[Gemini] GEMINI_API_KEY not set — skipping Gemini, using keyword engine")
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = _PROMPT_TEMPLATE.format(
            message=message,
            location=location or "Location not specified",
        )

        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 512},
        )

        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps in ```json ... ```
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

        result = json.loads(raw)

        # ── Validate & Normalise ──────────────────────────────
        valid_types = {"fire", "medical", "theft", "violence", "infra", "general"}
        result["type"] = str(result.get("type", "general")).lower()
        if result["type"] not in valid_types:
            result["type"] = "general"

        result["severity"] = max(1, min(10, int(result.get("severity", 5))))
        result["confidence"] = round(max(0.0, min(1.0, float(result.get("confidence", 0.5)))), 4)
        result["urgency_level"] = result.get("urgency_level", "none")
        result["keywords_found"] = result.get("keywords_found", [])
        result["suspicion_flags"] = result.get("suspicion_flags", [])
        result["evidence_score"] = max(0, min(100, int(result.get("evidence_score", 50))))
        result["evidence_strength"] = result.get("evidence_strength", "Medium")
        result["explanation"] = result.get("explanation", "Classified by Gemini AI.")
        result["urgency_phrases"] = []   # Gemini doesn't use phrases list
        result["evidence_detail"] = {}   # Compatibility with keyword engine output
        result["location"] = location
        result["ml_used"] = True
        result["gemini_used"] = True     # Flag so templates can show "Powered by Gemini"

        logger.info(
            f"[Gemini] Classified as {result['type'].upper()} "
            f"| severity={result['severity']} | confidence={result['confidence']}"
        )
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"[Gemini] JSON parse failed: {e} — raw: {raw[:200]}")
        return None
    except Exception as e:
        logger.warning(f"[Gemini] API call failed: {type(e).__name__}: {e}")
        return None
