"""
CrisisSignal AI — Export Service
Phase 3: CSV export for audit logs and alert summaries.

Generates a streaming CSV response — no temp files, no heavy PDF deps.
Use reportlab/weasyprint in Phase 4 if PDF is needed.
"""

import csv
import io
from datetime import datetime
from flask import Response


class ExportService:
    """Generates CSV exports for admin dashboards."""

    @staticmethod
    def export_alerts_csv(alerts, community_name="Community"):
        """
        Export a list of Alert objects as a downloadable CSV.

        Args:
            alerts: list of Alert model instances
            community_name: str — used in filename

        Returns:
            Flask Response with Content-Disposition: attachment
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Alert ID", "Type", "Severity", "Status", "Confidence",
            "Location", "Reporter", "Assigned To", "Contact Phone",
            "Is Emergency", "Evidence Photo", "Votes (Confirm/Reject)",
            "Evidence Score", "Urgency", "Submitted At", "Resolved At",
            "Resolution Note", "Message"
        ])

        for a in alerts:
            writer.writerow([
                a.id,
                (a.type or "general").upper(),
                a.severity or 0,
                (a.status or "new").upper(),
                f"{(a.confidence or 0):.2%}",
                a.location or "Unknown",
                a.reporter.name if a.reporter else "Unknown",
                a.responder.name if getattr(a, "responder", None) else "Unassigned",
                getattr(a, "contact_phone", "") or "",
                "YES" if getattr(a, "is_emergency", False) else "no",
                "YES" if getattr(a, "photo_path", None) else "no",
                f"{a.confirmations_count or 0}/{a.rejections_count or 0}",
                a.evidence_score or 0,
                (a.urgency_level or "none").upper(),
                a.timestamp.strftime("%Y-%m-%d %H:%M") if a.timestamp else "",
                a.resolved_at.strftime("%Y-%m-%d %H:%M") if a.resolved_at else "",
                a.resolution_note or "",
                (a.message or "")[:200],  # Truncate for CSV readability
            ])

        output.seek(0)
        filename = (
            f"crisissignal_alerts_{community_name.replace(' ', '_')}"
            f"_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
        )
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    @staticmethod
    def export_audit_csv(logs, community_name="Community"):
        """
        Export audit log entries as a downloadable CSV.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Log ID", "Alert ID", "Actor", "Action",
            "Previous Value", "New Value", "Detail", "Logged At"
        ])

        for log in logs:
            writer.writerow([
                log.id,
                log.alert_id,
                log.actor.name if log.actor else "System",
                log.action or "",
                log.previous_value or "",
                log.new_value or "",
                (log.detail or "")[:300],
                log.logged_at.strftime("%Y-%m-%d %H:%M:%S") if log.logged_at else "",
            ])

        output.seek(0)
        filename = (
            f"crisissignal_audit_{community_name.replace(' ', '_')}"
            f"_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
        )
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
