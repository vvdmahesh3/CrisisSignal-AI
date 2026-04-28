"""
CrisisSignal AI — Reliability Service
Self-learning user reputation system.

Phase 2.6: Bayesian scoring prevents score volatility on small sample sizes.
A user with 1 confirmed report no longer has reliability = 0.55 immediately.
"""

from ..extensions import db
from ..models import User


# Bayesian prior weight — equivalent to N "neutral" prior reports.
# Higher = slower to change (more conservative). 5 is a reasonable start.
_BAYESIAN_PRIOR = 5


def bayesian_reliability(confirmed_reports, total_reports):
    """
    Phase 2.6 — Bayesian reliability scoring.

    Calculates a smoothed reliability score that resists extreme swings
    when a user has few data points.

    Formula:
        score = (confirmed + prior × 0.5) / (total + prior)

    With prior=5:
        - New user (0/0)   → 0.50 (neutral, as expected)
        - 1 confirmed/1    → (1 + 2.5) / (1 + 5) = 0.583
        - 5 confirmed/5    → (5 + 2.5) / (5 + 5) = 0.75
        - 10 confirmed/10  → (10 + 2.5) / (10 + 5) = 0.833
        - 0 confirmed/5    → (0 + 2.5) / (5 + 5) = 0.25 (5 rejections drag down)

    Returns float in [0.0, 1.0]
    """
    numerator = confirmed_reports + _BAYESIAN_PRIOR * 0.5
    denominator = total_reports + _BAYESIAN_PRIOR
    return round(max(0.0, min(1.0, numerator / denominator)), 4)


class ReliabilityService:
    """Manages user reliability score evolution."""

    # ── Score Adjustments ──────────────────────────────────────
    CONFIRM_BONUS = 0.05
    CRITICAL_BONUS = 0.15
    REJECT_PENALTY = -0.10
    ADMIN_REJECT_PENALTY = -0.15
    FLAG_THRESHOLD = 3

    @staticmethod
    def update_on_resolution(alert, outcome_status=None):
        """
        Update reliability scores for the reporter and all voters
        after an alert reaches a terminal state.

        Phase 2.6: After each update, recalculate using Bayesian formula
        and use the weighted average with the delta-adjusted score.
        """
        final_outcome = outcome_status or alert.status
        reporter = alert.reporter
        if not reporter:
            return

        # ── Reporter Score Update ─────────────────────────────
        if final_outcome == "critical":
            reporter.confirmed_reports += 1
            reporter.adjust_reliability(ReliabilityService.CRITICAL_BONUS)
        elif final_outcome == "verified":
            reporter.confirmed_reports += 1
            reporter.adjust_reliability(ReliabilityService.CONFIRM_BONUS)
        elif final_outcome == "rejected":
            reporter.rejected_reports += 1
            reporter.adjust_reliability(ReliabilityService.REJECT_PENALTY)

            if reporter.rejected_reports >= ReliabilityService.FLAG_THRESHOLD:
                reporter.is_flagged = True

        # Phase 2.6: Blend delta-adjusted score with Bayesian score (50/50)
        if reporter.total_reports > 0:
            bayesian = bayesian_reliability(reporter.confirmed_reports, reporter.total_reports)
            blended = (reporter.reliability_score + bayesian) / 2
            reporter.reliability_score = round(max(0.0, min(1.0, blended)), 4)

        # ── Voter Score Updates ───────────────────────────────
        for vote in alert.votes.all():
            voter = vote.voter
            if not voter:
                continue

            if final_outcome in ("verified", "critical") and vote.vote == "confirm":
                voter.adjust_reliability(0.02)
            elif final_outcome == "rejected" and vote.vote == "reject":
                voter.adjust_reliability(0.02)
            elif final_outcome in ("verified", "critical") and vote.vote == "reject":
                voter.adjust_reliability(-0.03)
            elif final_outcome == "rejected" and vote.vote == "confirm":
                voter.adjust_reliability(-0.03)

    @staticmethod
    def apply_admin_reject(alert):
        """Apply immediate reporter penalty for manual admin rejection."""
        reporter = alert.reporter
        if not reporter:
            return

        reporter.adjust_reliability(ReliabilityService.ADMIN_REJECT_PENALTY)
        reporter.rejected_reports += 1
        if reporter.rejected_reports >= ReliabilityService.FLAG_THRESHOLD:
            reporter.is_flagged = True

        # Phase 2.6: Apply Bayesian correction after penalty
        if reporter.total_reports > 0:
            bayesian = bayesian_reliability(reporter.confirmed_reports, reporter.total_reports)
            blended = (reporter.reliability_score + bayesian) / 2
            reporter.reliability_score = round(max(0.0, min(1.0, blended)), 4)

    @staticmethod
    def get_badge(reliability_score):
        """
        Phase 3 preview: Return reputation badge label and emoji for a score.
        """
        if reliability_score >= 0.85:
            return "gold", "Trusted Reporter"
        elif reliability_score >= 0.70:
            return "silver", "Reliable Reporter"
        elif reliability_score >= 0.50:
            return "bronze", "Active Member"
        elif reliability_score >= 0.25:
            return "warning", "Needs Improvement"
        else:
            return "danger", "Flagged Account"
