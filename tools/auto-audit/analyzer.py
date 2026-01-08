#!/usr/bin/env python3
"""
SAHOOL Audit Log Analyzer
Comprehensive analysis tool for audit logs with pattern detection and reporting

Features:
- Statistical analysis of audit events
- Pattern detection and trend analysis
- Actor activity profiling
- Resource access analysis
- Time-based reporting
- Risk scoring

Usage:
    python -m tools.auto-audit.analyzer --tenant-id <uuid> [options]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID


@dataclass
class ActivityMetrics:
    """Metrics for actor or resource activity"""

    total_events: int = 0
    unique_actions: set = field(default_factory=set)
    unique_resources: set = field(default_factory=set)
    first_activity: datetime | None = None
    last_activity: datetime | None = None
    peak_hour: int | None = None
    action_counts: Counter = field(default_factory=Counter)
    hourly_distribution: Counter = field(default_factory=Counter)


@dataclass
class AnalysisReport:
    """Complete audit analysis report"""

    tenant_id: str
    analysis_period: tuple[datetime, datetime]
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Summary metrics
    total_events: int = 0
    unique_actors: int = 0
    unique_resources: int = 0
    unique_actions: int = 0

    # Distribution data
    action_distribution: dict = field(default_factory=dict)
    resource_type_distribution: dict = field(default_factory=dict)
    actor_type_distribution: dict = field(default_factory=dict)
    hourly_distribution: dict = field(default_factory=dict)
    daily_distribution: dict = field(default_factory=dict)

    # Top items
    top_actors: list = field(default_factory=list)
    top_resources: list = field(default_factory=list)
    top_actions: list = field(default_factory=list)

    # Risk indicators
    risk_indicators: list = field(default_factory=list)
    anomalies: list = field(default_factory=list)

    # Actor profiles
    actor_profiles: dict = field(default_factory=dict)


class AuditLogAnalyzer:
    """
    Comprehensive audit log analyzer for security analysis and reporting.

    Analyzes audit logs to detect patterns, anomalies, and generate
    compliance reports.
    """

    # Risk thresholds
    HIGH_ACTIVITY_THRESHOLD = 100  # Events per hour
    SUSPICIOUS_HOURS = {0, 1, 2, 3, 4, 5}  # Midnight to 6 AM
    SENSITIVE_ACTIONS = {
        "user.delete",
        "user.role.assign",
        "permission.grant",
        "data.export",
        "data.bulk_delete",
        "config.change",
        "api_key.create",
        "api_key.delete",
    }
    SENSITIVE_RESOURCES = {"user", "permission", "role", "api_key", "config", "secret"}

    def __init__(self, entries: list[dict] | None = None):
        """
        Initialize analyzer with audit log entries.

        Args:
            entries: List of audit log entries as dictionaries
        """
        self.entries = entries or []
        self._actor_metrics: dict[str, ActivityMetrics] = defaultdict(ActivityMetrics)
        self._resource_metrics: dict[str, ActivityMetrics] = defaultdict(ActivityMetrics)

    def load_from_file(self, file_path: Path) -> None:
        """Load audit entries from JSON file"""
        with open(file_path) as f:
            self.entries = json.load(f)

    def load_from_database(
        self,
        db_session: Any,
        tenant_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> None:
        """
        Load audit entries from database.

        Args:
            db_session: SQLAlchemy session
            tenant_id: Tenant UUID to filter by
            start_date: Start of analysis period
            end_date: End of analysis period
        """
        # Import here to avoid circular dependencies
        from shared.libs.audit import query_audit_logs

        self.entries = [
            entry.to_dict()
            for entry in query_audit_logs(
                db_session,
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                limit=100000,
            )
        ]

    def analyze(self, tenant_id: str | None = None) -> AnalysisReport:
        """
        Perform comprehensive analysis of audit logs.

        Args:
            tenant_id: Optional tenant ID filter

        Returns:
            Complete AnalysisReport with all metrics
        """
        if tenant_id:
            entries = [e for e in self.entries if e.get("tenant_id") == tenant_id]
        else:
            entries = self.entries

        if not entries:
            return AnalysisReport(
                tenant_id=tenant_id or "all",
                analysis_period=(datetime.now(UTC), datetime.now(UTC)),
            )

        # Parse timestamps
        for entry in entries:
            if isinstance(entry.get("created_at"), str):
                entry["_timestamp"] = datetime.fromisoformat(
                    entry["created_at"].replace("Z", "+00:00")
                )
            else:
                entry["_timestamp"] = entry.get("created_at", datetime.now(UTC))

        # Determine analysis period
        timestamps = [e["_timestamp"] for e in entries]
        start_date = min(timestamps)
        end_date = max(timestamps)

        report = AnalysisReport(
            tenant_id=tenant_id or "all",
            analysis_period=(start_date, end_date),
            total_events=len(entries),
        )

        # Collect metrics
        action_counter = Counter()
        resource_type_counter = Counter()
        actor_type_counter = Counter()
        hourly_counter = Counter()
        daily_counter = Counter()
        actor_counter = Counter()
        resource_counter = Counter()

        unique_actors = set()
        unique_resources = set()
        unique_actions = set()

        for entry in entries:
            action = entry.get("action", "unknown")
            resource_type = entry.get("resource_type", "unknown")
            resource_id = entry.get("resource_id", "unknown")
            actor_id = entry.get("actor_id")
            actor_type = entry.get("actor_type", "unknown")
            timestamp = entry["_timestamp"]

            # Count distributions
            action_counter[action] += 1
            resource_type_counter[resource_type] += 1
            actor_type_counter[actor_type] += 1
            hourly_counter[timestamp.hour] += 1
            daily_counter[timestamp.strftime("%Y-%m-%d")] += 1

            if actor_id:
                actor_counter[actor_id] += 1
                unique_actors.add(actor_id)

            resource_key = f"{resource_type}/{resource_id}"
            resource_counter[resource_key] += 1
            unique_resources.add(resource_key)
            unique_actions.add(action)

            # Update actor metrics
            if actor_id:
                metrics = self._actor_metrics[actor_id]
                metrics.total_events += 1
                metrics.unique_actions.add(action)
                metrics.unique_resources.add(resource_key)
                metrics.action_counts[action] += 1
                metrics.hourly_distribution[timestamp.hour] += 1
                if metrics.first_activity is None or timestamp < metrics.first_activity:
                    metrics.first_activity = timestamp
                if metrics.last_activity is None or timestamp > metrics.last_activity:
                    metrics.last_activity = timestamp

        # Populate report
        report.unique_actors = len(unique_actors)
        report.unique_resources = len(unique_resources)
        report.unique_actions = len(unique_actions)

        report.action_distribution = dict(action_counter.most_common())
        report.resource_type_distribution = dict(resource_type_counter.most_common())
        report.actor_type_distribution = dict(actor_type_counter.most_common())
        report.hourly_distribution = {str(h): c for h, c in sorted(hourly_counter.items())}
        report.daily_distribution = dict(sorted(daily_counter.items()))

        report.top_actors = actor_counter.most_common(20)
        report.top_resources = resource_counter.most_common(20)
        report.top_actions = action_counter.most_common(20)

        # Detect risk indicators
        report.risk_indicators = self._detect_risk_indicators(entries)
        report.anomalies = self._detect_anomalies(entries)

        # Generate actor profiles
        report.actor_profiles = self._generate_actor_profiles()

        return report

    def _detect_risk_indicators(self, entries: list[dict]) -> list[dict]:
        """Detect potential security risk indicators"""
        risks = []

        # Check for high-frequency activity
        hourly_activity = Counter()
        for entry in entries:
            hour_key = entry["_timestamp"].strftime("%Y-%m-%d %H")
            hourly_activity[hour_key] += 1

        for hour, count in hourly_activity.items():
            if count > self.HIGH_ACTIVITY_THRESHOLD:
                risks.append(
                    {
                        "type": "high_activity",
                        "severity": "medium",
                        "description": f"High activity detected: {count} events in hour {hour}",
                        "timestamp": hour,
                        "count": count,
                    }
                )

        # Check for off-hours activity
        off_hours_entries = [e for e in entries if e["_timestamp"].hour in self.SUSPICIOUS_HOURS]
        if off_hours_entries:
            off_hours_actors = Counter(
                e.get("actor_id") for e in off_hours_entries if e.get("actor_id")
            )
            for actor, count in off_hours_actors.most_common(10):
                if count > 5:
                    risks.append(
                        {
                            "type": "off_hours_activity",
                            "severity": "low",
                            "description": f"Off-hours activity: {count} events by actor {actor}",
                            "actor_id": actor,
                            "count": count,
                        }
                    )

        # Check for sensitive actions
        sensitive_entries = [e for e in entries if e.get("action") in self.SENSITIVE_ACTIONS]
        for entry in sensitive_entries:
            risks.append(
                {
                    "type": "sensitive_action",
                    "severity": "high",
                    "description": f"Sensitive action: {entry.get('action')}",
                    "action": entry.get("action"),
                    "actor_id": entry.get("actor_id"),
                    "resource": f"{entry.get('resource_type')}/{entry.get('resource_id')}",
                    "timestamp": entry["_timestamp"].isoformat(),
                }
            )

        # Check for failed actions
        failed_entries = [e for e in entries if e.get("success") is False]
        if len(failed_entries) > 10:
            failed_by_actor = Counter(
                e.get("actor_id") for e in failed_entries if e.get("actor_id")
            )
            for actor, count in failed_by_actor.most_common(5):
                if count > 5:
                    risks.append(
                        {
                            "type": "failed_actions",
                            "severity": "medium",
                            "description": f"Multiple failed actions: {count} failures by actor {actor}",
                            "actor_id": actor,
                            "count": count,
                        }
                    )

        return sorted(risks, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])

    def _detect_anomalies(self, entries: list[dict]) -> list[dict]:
        """Detect anomalous patterns in audit logs"""
        anomalies = []

        # Group entries by actor
        actor_entries = defaultdict(list)
        for entry in entries:
            actor_id = entry.get("actor_id")
            if actor_id:
                actor_entries[actor_id].append(entry)

        for actor_id, actor_logs in actor_entries.items():
            # Check for sudden activity spikes
            daily_counts = Counter(e["_timestamp"].strftime("%Y-%m-%d") for e in actor_logs)
            if len(daily_counts) >= 3:
                counts = list(daily_counts.values())
                avg = sum(counts[:-1]) / len(counts[:-1])
                if avg > 0 and counts[-1] > avg * 3:
                    anomalies.append(
                        {
                            "type": "activity_spike",
                            "actor_id": actor_id,
                            "description": f"Activity spike: {counts[-1]} vs avg {avg:.1f}",
                            "current": counts[-1],
                            "average": avg,
                        }
                    )

            # Check for new resource access
            if len(actor_logs) >= 10:
                early_resources = set(
                    f"{e.get('resource_type')}/{e.get('resource_id')}"
                    for e in actor_logs[: len(actor_logs) // 2]
                )
                late_resources = set(
                    f"{e.get('resource_type')}/{e.get('resource_id')}"
                    for e in actor_logs[len(actor_logs) // 2 :]
                )
                new_resources = late_resources - early_resources
                if len(new_resources) > 5:
                    anomalies.append(
                        {
                            "type": "new_resource_access",
                            "actor_id": actor_id,
                            "description": f"Accessing {len(new_resources)} new resources",
                            "count": len(new_resources),
                        }
                    )

        return anomalies

    def _generate_actor_profiles(self) -> dict[str, dict]:
        """Generate behavioral profiles for actors"""
        profiles = {}

        for actor_id, metrics in self._actor_metrics.items():
            if metrics.total_events < 3:
                continue

            # Find peak hour
            if metrics.hourly_distribution:
                peak_hour = metrics.hourly_distribution.most_common(1)[0][0]
            else:
                peak_hour = None

            # Determine activity level
            if metrics.total_events > 500:
                activity_level = "very_high"
            elif metrics.total_events > 100:
                activity_level = "high"
            elif metrics.total_events > 20:
                activity_level = "moderate"
            else:
                activity_level = "low"

            # Calculate diversity score (how diverse are the actions)
            diversity_score = (
                len(metrics.unique_actions) / metrics.total_events
                if metrics.total_events > 0
                else 0
            )

            profiles[actor_id] = {
                "total_events": metrics.total_events,
                "unique_actions": len(metrics.unique_actions),
                "unique_resources": len(metrics.unique_resources),
                "activity_level": activity_level,
                "diversity_score": round(diversity_score, 3),
                "peak_hour": peak_hour,
                "first_activity": (
                    metrics.first_activity.isoformat() if metrics.first_activity else None
                ),
                "last_activity": (
                    metrics.last_activity.isoformat() if metrics.last_activity else None
                ),
                "top_actions": metrics.action_counts.most_common(5),
            }

        return profiles

    def get_activity_timeline(
        self,
        interval: str = "hour",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict[str, int]:
        """
        Get activity counts grouped by time interval.

        Args:
            interval: 'hour', 'day', or 'week'
            start: Start of period
            end: End of period

        Returns:
            Dictionary of timestamp -> count
        """
        entries = self.entries
        if start:
            entries = [e for e in entries if e["_timestamp"] >= start]
        if end:
            entries = [e for e in entries if e["_timestamp"] <= end]

        counter = Counter()
        for entry in entries:
            ts = entry["_timestamp"]
            if interval == "hour":
                key = ts.strftime("%Y-%m-%d %H:00")
            elif interval == "day":
                key = ts.strftime("%Y-%m-%d")
            elif interval == "week":
                key = ts.strftime("%Y-W%W")
            else:
                key = ts.strftime("%Y-%m-%d")
            counter[key] += 1

        return dict(sorted(counter.items()))

    def search_events(
        self,
        action: str | None = None,
        actor_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[dict]:
        """
        Search audit events with filters.

        Args:
            action: Filter by action (supports wildcards with *)
            actor_id: Filter by actor
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            ip: Filter by IP address
            start: Start date
            end: End date

        Returns:
            List of matching events
        """
        results = []

        for entry in self.entries:
            # Apply filters
            if action:
                entry_action = entry.get("action", "")
                if "*" in action:
                    pattern = action.replace("*", "")
                    if pattern not in entry_action:
                        continue
                elif entry_action != action:
                    continue

            if actor_id and entry.get("actor_id") != actor_id:
                continue

            if resource_type and entry.get("resource_type") != resource_type:
                continue

            if resource_id and entry.get("resource_id") != resource_id:
                continue

            if ip and entry.get("ip") != ip:
                continue

            if start and entry.get("_timestamp", datetime.min) < start:
                continue

            if end and entry.get("_timestamp", datetime.max) > end:
                continue

            results.append(entry)

        return results


def generate_markdown_report(report: AnalysisReport) -> str:
    """Generate markdown report from analysis"""
    lines = [
        "# SAHOOL Audit Log Analysis Report",
        "",
        f"> Generated: {report.generated_at.isoformat()}",
        f"> Tenant: {report.tenant_id}",
        f"> Period: {report.analysis_period[0].isoformat()} to {report.analysis_period[1].isoformat()}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Events | {report.total_events:,} |",
        f"| Unique Actors | {report.unique_actors:,} |",
        f"| Unique Resources | {report.unique_resources:,} |",
        f"| Unique Actions | {report.unique_actions:,} |",
        "",
    ]

    # Risk Indicators
    if report.risk_indicators:
        lines.extend(
            [
                "## Risk Indicators",
                "",
            ]
        )
        high_risks = [r for r in report.risk_indicators if r["severity"] == "high"]
        medium_risks = [r for r in report.risk_indicators if r["severity"] == "medium"]
        low_risks = [r for r in report.risk_indicators if r["severity"] == "low"]

        if high_risks:
            lines.append("### High Severity")
            lines.append("")
            for risk in high_risks[:10]:
                lines.append(f"- **{risk['type']}**: {risk['description']}")
            lines.append("")

        if medium_risks:
            lines.append("### Medium Severity")
            lines.append("")
            for risk in medium_risks[:10]:
                lines.append(f"- **{risk['type']}**: {risk['description']}")
            lines.append("")

        if low_risks:
            lines.append("### Low Severity")
            lines.append("")
            for risk in low_risks[:10]:
                lines.append(f"- {risk['type']}: {risk['description']}")
            lines.append("")

    # Top Actors
    if report.top_actors:
        lines.extend(
            [
                "## Top Actors",
                "",
                "| Actor ID | Events |",
                "|----------|--------|",
            ]
        )
        for actor, count in report.top_actors[:10]:
            lines.append(f"| {actor} | {count:,} |")
        lines.append("")

    # Top Actions
    if report.top_actions:
        lines.extend(
            [
                "## Top Actions",
                "",
                "| Action | Count |",
                "|--------|-------|",
            ]
        )
        for action, count in report.top_actions[:15]:
            lines.append(f"| {action} | {count:,} |")
        lines.append("")

    # Resource Type Distribution
    if report.resource_type_distribution:
        lines.extend(
            [
                "## Resource Types",
                "",
                "| Resource Type | Count |",
                "|---------------|-------|",
            ]
        )
        for resource_type, count in list(report.resource_type_distribution.items())[:15]:
            lines.append(f"| {resource_type} | {count:,} |")
        lines.append("")

    # Hourly Distribution
    if report.hourly_distribution:
        lines.extend(
            [
                "## Hourly Activity Distribution",
                "",
                "| Hour | Events |",
                "|------|--------|",
            ]
        )
        for hour, count in report.hourly_distribution.items():
            lines.append(f"| {hour}:00 | {count:,} |")
        lines.append("")

    # Anomalies
    if report.anomalies:
        lines.extend(
            [
                "## Detected Anomalies",
                "",
            ]
        )
        for anomaly in report.anomalies[:10]:
            lines.append(f"- **{anomaly['type']}**: {anomaly['description']}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "*Report generated by SAHOOL Auto Audit Tools*",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze SAHOOL audit logs")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input JSON file with audit logs",
    )
    parser.add_argument(
        "--tenant-id",
        "-t",
        help="Filter by tenant ID",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="audit_analysis_report.md",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()

    # Load and analyze
    analyzer = AuditLogAnalyzer()
    analyzer.load_from_file(Path(args.input))
    report = analyzer.analyze(tenant_id=args.tenant_id)

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "tenant_id": report.tenant_id,
                "generated_at": report.generated_at.isoformat(),
                "analysis_period": [
                    report.analysis_period[0].isoformat(),
                    report.analysis_period[1].isoformat(),
                ],
                "total_events": report.total_events,
                "unique_actors": report.unique_actors,
                "unique_resources": report.unique_resources,
                "unique_actions": report.unique_actions,
                "action_distribution": report.action_distribution,
                "resource_type_distribution": report.resource_type_distribution,
                "top_actors": report.top_actors,
                "top_actions": report.top_actions,
                "risk_indicators": report.risk_indicators,
                "anomalies": report.anomalies,
            },
            indent=2,
            default=str,
        )
    else:
        output = generate_markdown_report(report)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(output)
    print(f"Analysis report generated: {output_path}")
    print(f"  Total events: {report.total_events:,}")
    print(f"  Risk indicators: {len(report.risk_indicators)}")
    print(f"  Anomalies: {len(report.anomalies)}")


if __name__ == "__main__":
    main()
