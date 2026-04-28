"""
CrisisSignal AI — Analytics Service
Institutional intelligence: aggregate analytics, trends, and response metrics.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, case, extract
from ..extensions import db
from ..models import Alert, User, CrowdVote, AuditLog


class AnalyticsService:
    """Generates aggregate analytics for the institutional intelligence dashboard."""

    @staticmethod
    def get_dashboard_analytics(community_id=None):
        """Returns comprehensive analytics for the analytics dashboard."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        return {
            "overview": AnalyticsService._get_overview_stats(community_id),
            "alerts_by_type": AnalyticsService._get_alerts_by_type(community_id),
            "alerts_by_status": AnalyticsService._get_alerts_by_status(community_id),
            "hourly_distribution": AnalyticsService._get_hourly_distribution(community_id),
            "response_metrics": AnalyticsService._get_response_metrics(community_id),
            "reliability_leaderboard": AnalyticsService._get_reliability_leaderboard(community_id=community_id),
            "recent_trend": AnalyticsService._get_recent_trend(community_id),
            "system_health": AnalyticsService._get_system_health(community_id),
        }

    @staticmethod
    def _get_overview_stats(community_id=None):
        """High-level system statistics."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        query_alert = Alert.query
        query_user = User.query
        query_vote = CrowdVote.query
        if community_id:
            query_alert = query_alert.filter_by(community_id=community_id)
            query_user = query_user.filter_by(community_id=community_id)
            
        total_alerts = query_alert.count()
        active_alerts = query_alert.filter(
            Alert.status.notin_(["resolved", "rejected"])
        ).count()
        resolved_alerts = query_alert.filter_by(status="resolved").count()
        total_votes = query_vote.count() # Not filtering votes strictly for now
        total_users = query_user.count()
        alerts_24h = query_alert.filter(Alert.timestamp >= last_24h).count()
        alerts_7d = query_alert.filter(Alert.timestamp >= last_7d).count()

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "total_votes": total_votes,
            "total_users": total_users,
            "alerts_24h": alerts_24h,
            "alerts_7d": alerts_7d,
        }

    @staticmethod
    def _get_alerts_by_type(community_id=None):
        """Count alerts by incident type."""
        q = db.session.query(Alert.type, func.count(Alert.id))
        if community_id:
            q = q.filter(Alert.community_id == community_id)
        results = q.group_by(Alert.type).all()

        return {row[0]: row[1] for row in results}

    @staticmethod
    def _get_alerts_by_status(community_id=None):
        """Count alerts by current status."""
        q = db.session.query(Alert.status, func.count(Alert.id))
        if community_id:
            q = q.filter(Alert.community_id == community_id)
        results = q.group_by(Alert.status).all()

        return {row[0]: row[1] for row in results}

    @staticmethod
    def _get_hourly_distribution(community_id=None):
        """Alert count by hour of day (0-23) for peak hour analysis."""
        q = db.session.query(
            extract("hour", Alert.timestamp).label("hour"),
            func.count(Alert.id),
        )
        if community_id:
            q = q.filter(Alert.community_id == community_id)
        results = q.group_by("hour").all()

        # Fill all 24 hours
        distribution = {h: 0 for h in range(24)}
        for row in results:
            hour_val = int(row[0]) if row[0] is not None else 0
            distribution[hour_val] = row[1]

        return distribution

    @staticmethod
    def _get_response_metrics(community_id=None):
        """Calculate average response times from report to verified/critical/resolved."""
        query = Alert.query.filter(
            Alert.resolved_at.isnot(None),
            Alert.status == "resolved",
        )
        if community_id:
            query = query.filter_by(community_id=community_id)
        resolved = query.all()

        if not resolved:
            return {
                "avg_resolution_minutes": 0,
                "fastest_resolution_minutes": 0,
                "total_resolved": 0,
                "verification_rate": 0,
            }

        resolution_times = []
        for alert in resolved:
            if alert.timestamp and alert.resolved_at:
                delta = (alert.resolved_at - alert.timestamp).total_seconds() / 60
                resolution_times.append(delta)

        total_alerts = Alert.query
        if community_id:
            total_alerts = total_alerts.filter_by(community_id=community_id)
        
        tc = total_alerts.count()
        
        v_query = Alert.query.filter(
            Alert.status.in_(["verified", "critical", "resolved"])
        )
        if community_id:
            v_query = v_query.filter_by(community_id=community_id)
        verified_count = v_query.count()

        return {
            "avg_resolution_minutes": round(
                sum(resolution_times) / len(resolution_times), 1
            ) if resolution_times else 0,
            "fastest_resolution_minutes": round(
                min(resolution_times), 1
            ) if resolution_times else 0,
            "total_resolved": len(resolved),
            "verification_rate": round(
                (verified_count / tc * 100), 1
            ) if tc > 0 else 0,
        }

    @staticmethod
    def _get_reliability_leaderboard(limit=10, community_id=None):
        """Top users by reliability score."""
        q = User.query.filter(
            User.role == "user",
            User.total_reports > 0,
        )
        if community_id:
            q = q.filter_by(community_id=community_id)
        users = q.order_by(User.reliability_score.desc()).limit(limit).all()

        return [
            {
                "id": u.id,
                "name": u.name,
                "reliability_score": u.reliability_score,
                "total_reports": u.total_reports,
                "confirmed_reports": u.confirmed_reports,
                "accuracy": round(
                    (u.confirmed_reports / u.total_reports * 100), 1
                ) if u.total_reports > 0 else 0,
            }
            for u in users
        ]

    @staticmethod
    def _get_recent_trend(community_id=None):
        """Alert counts for the last 7 days for trend line."""
        now = datetime.utcnow()
        trend = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            q = Alert.query.filter(
                Alert.timestamp >= day_start,
                Alert.timestamp < day_end,
            )
            if community_id:
                q = q.filter_by(community_id=community_id)
            count = q.count()
            trend.append({
                "date": day_start.strftime("%b %d"),
                "count": count,
            })

        return trend

    @staticmethod
    def _get_system_health(community_id=None):
        """Overall system health indicators."""
        q = Alert.query
        if community_id:
            q = q.filter_by(community_id=community_id)
        total = q.count()
        if total == 0:
            return {
                "avg_confidence": 0,
                "crowd_participation_rate": 0,
                "false_alarm_rate": 0,
                "health_score": 100,
            }

        # Average confidence of verified/critical alerts
        v_query = Alert.query.filter(
            Alert.status.in_(["verified", "critical"])
        )
        if community_id:
            v_query = v_query.filter_by(community_id=community_id)
        verified = v_query.all()
        avg_conf = (
            sum(a.confidence for a in verified) / len(verified)
            if verified else 0
        )

        # Crowd participation: alerts with at least 1 vote
        c_query = Alert.query.filter(
            (Alert.confirmations_count + Alert.rejections_count) > 0
        )
        if community_id:
            c_query = c_query.filter_by(community_id=community_id)
        alerts_with_votes = c_query.count()
        participation = alerts_with_votes / total * 100 if total > 0 else 0

        # False alarm rate
        r_query = Alert.query.filter_by(status="rejected")
        if community_id:
            r_query = r_query.filter_by(community_id=community_id)
        rejected = r_query.count()
        false_alarm = rejected / total * 100 if total > 0 else 0

        # Composite health score
        health = min(100, int(
            (avg_conf * 40)
            + (min(participation, 100) * 0.3)
            + ((100 - false_alarm) * 0.3)
        ))

        return {
            "avg_confidence": round(avg_conf, 2),
            "crowd_participation_rate": round(participation, 1),
            "false_alarm_rate": round(false_alarm, 1),
            "health_score": health,
        }
