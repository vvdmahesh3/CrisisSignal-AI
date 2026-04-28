"""
CrisisSignal AI — Confidence Service
Triangulated dynamic confidence calculation and status determination.

Phase 2.5: Added time-decay — older alerts lose confidence weight gradually.
"""

import math
from datetime import datetime


class ConfidenceService:
    """Handles all confidence score calculations."""

    @staticmethod
    def recalculate(initial_confidence, weighted_confirms, weighted_rejects,
                    reporter_reliability):
        """
        Triangulated Trust Model:
        Confidence = (AI_Base_Score × 0.40) + (Crowd_Consensus × 0.40) + (Reliability_Bonus × 0.20)

        Where:
          AI_Base_Score     = Initial confidence from classification engine
          Crowd_Consensus   = weighted_confirms / (weighted_confirms + weighted_rejects)
          Reliability_Bonus = flat +0.10 bonus (not a multiplier) if reporter reliability > 0.75
        """
        initial_confidence = initial_confidence or 0
        weighted_confirms = weighted_confirms or 0
        weighted_rejects = weighted_rejects or 0
        reporter_reliability = reporter_reliability or 0

        total = weighted_confirms + weighted_rejects + 0.001  # Avoid division by zero
        crowd_score = weighted_confirms / total
        reliability_bonus = 0.10 if reporter_reliability > 0.75 else 0.0

        new_confidence = (
            (initial_confidence * 0.40)
            + (crowd_score * 0.40)
            + (reliability_bonus * 0.20)
        )

        return round(max(0.0, min(1.0, new_confidence)), 4)

    @staticmethod
    def apply_time_decay(confidence, alert_timestamp):
        """
        Phase 2.5 — Time Decay: Reduce confidence for stale alerts.

        Old alerts with no recent votes should not display as still-confident.
        Decay curve: confidence × e^(-0.05 × hours_elapsed)

        | Elapsed | Effective confidence |
        | 0h      | 100%                 |
        | 1h      | ~95%                 |
        | 6h      | ~74%                 |
        | 24h     | ~30% → auto-archive  |

        Returns decayed confidence value clamped to [0.0, 1.0].
        """
        if not alert_timestamp:
            return confidence

        hours_elapsed = (datetime.utcnow() - alert_timestamp).total_seconds() / 3600
        decay_factor = math.exp(-0.05 * hours_elapsed)
        decayed = confidence * decay_factor
        return round(max(0.0, min(1.0, decayed)), 4)

    @staticmethod
    def get_effective_confidence(alert):
        """
        Return the time-decayed effective confidence for display.
        Use this for dashboard rendering — NOT for state transitions
        (those use the raw stored confidence).
        """
        raw = alert.confidence or 0.0
        ts = getattr(alert, 'timestamp', None)
        if ts and alert.status not in ("resolved", "rejected", "critical"):
            return ConfidenceService.apply_time_decay(raw, ts)
        return raw

    @staticmethod
    def determine_status(confidence, severity, weighted_confirms,
                         weighted_rejects, total_votes):
        """
        Determine alert status based on confidence, severity, and vote data.

        Status thresholds:
          - 0.00–0.29  → NEW (insufficient data)
          - 0.30–0.69  → VERIFYING
          - 0.70–0.84  → VERIFIED
          - 0.85–1.00  → CRITICAL (auto-escalate if severity >= 8)

        Rejection path:
          If weighted_rejects > weighted_confirms × 2 → REJECTED
        """
        confidence = confidence or 0
        severity = severity or 0
        weighted_confirms = weighted_confirms or 0
        weighted_rejects = weighted_rejects or 0
        total_votes = total_votes or 0

        if total_votes == 0:
            return "awaiting_review"

        if weighted_rejects > weighted_confirms * 2:
            return "rejected"

        if confidence >= 0.85 and severity >= 8:
            return "critical"
        elif confidence >= 0.70:
            return "verified"
        elif confidence >= 0.30:
            return "verifying"
        else:
            return "new"
