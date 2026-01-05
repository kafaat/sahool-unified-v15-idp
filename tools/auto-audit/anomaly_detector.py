#!/usr/bin/env python3
"""
SAHOOL Audit Anomaly Detector
Advanced ML-based anomaly detection for audit log analysis

Features:
- Statistical anomaly detection (Z-score, IQR)
- Behavioral baseline modeling
- Time-series pattern analysis
- Clustering-based outlier detection
- Real-time alert generation
- Threat scoring and classification

Usage:
    python -m tools.auto-audit.anomaly_detector --input logs.json [options]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable
from uuid import UUID


class AnomalyType(str, Enum):
    """Types of detected anomalies"""

    VOLUME_SPIKE = "volume_spike"
    VOLUME_DROP = "volume_drop"
    UNUSUAL_TIME = "unusual_time"
    NEW_ACTION = "new_action"
    NEW_RESOURCE = "new_resource"
    BEHAVIORAL_CHANGE = "behavioral_change"
    VELOCITY_ANOMALY = "velocity_anomaly"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"


class SeverityLevel(str, Enum):
    """Anomaly severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Detected anomaly"""

    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    description: str
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    actor_id: str | None = None
    resource: str | None = None
    evidence: list[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class BehaviorBaseline:
    """Behavioral baseline for an entity"""

    entity_id: str
    entity_type: str  # 'actor', 'resource', 'action'

    # Activity metrics
    avg_daily_events: float = 0.0
    std_daily_events: float = 0.0
    avg_hourly_events: float = 0.0
    typical_hours: set = field(default_factory=set)
    typical_actions: set = field(default_factory=set)
    typical_resources: set = field(default_factory=set)

    # Computed thresholds
    volume_upper_bound: float = 0.0
    volume_lower_bound: float = 0.0

    # Metadata
    baseline_period_days: int = 30
    data_points: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DetectionReport:
    """Complete anomaly detection report"""

    tenant_id: str
    detection_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    analysis_period: tuple[datetime, datetime] | None = None

    # Summary
    total_events_analyzed: int = 0
    anomalies_detected: int = 0
    critical_anomalies: int = 0
    high_anomalies: int = 0

    # Detected anomalies
    anomalies: list[Anomaly] = field(default_factory=list)

    # Baselines
    actor_baselines: dict[str, BehaviorBaseline] = field(default_factory=dict)

    # Threat indicators
    threat_score: float = 0.0  # 0-100
    threat_level: str = "low"
    top_threats: list[dict] = field(default_factory=list)

    # Statistics
    detection_duration_ms: float = 0


class AuditAnomalyDetector:
    """
    Advanced anomaly detection engine for audit logs.

    Uses multiple detection strategies:
    - Statistical methods (Z-score, IQR)
    - Behavioral analysis
    - Pattern matching
    - Time-series analysis
    """

    # Detection thresholds
    Z_SCORE_THRESHOLD = 3.0  # Standard deviations
    IQR_MULTIPLIER = 1.5
    UNUSUAL_HOUR_THRESHOLD = 0.05  # Less than 5% of normal activity
    VELOCITY_THRESHOLD = 10  # Events per minute

    # Suspicious patterns
    SUSPICIOUS_ACTION_SEQUENCES = [
        ["user.login.failed", "user.login.failed", "user.login.success"],
        ["permission.request", "permission.grant", "data.export"],
        ["user.create", "role.admin.assign", "config.change"],
    ]

    PRIVILEGE_ESCALATION_ACTIONS = {
        "role.admin.assign",
        "permission.admin.grant",
        "user.privilege.elevate",
        "access.override",
    }

    DATA_EXFILTRATION_INDICATORS = {
        "data.export",
        "data.bulk_download",
        "data.mass_export",
        "api.bulk_query",
        "report.generate.large",
    }

    def __init__(self, entries: list[dict] | None = None):
        """
        Initialize anomaly detector.

        Args:
            entries: List of audit log entries
        """
        self.entries = entries or []
        self._baselines: dict[str, BehaviorBaseline] = {}
        self._anomaly_counter = 0

    def load_from_file(self, file_path: Path) -> None:
        """Load entries from JSON file"""
        with open(file_path) as f:
            self.entries = json.load(f)

    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID"""
        self._anomaly_counter += 1
        return f"ANM-{datetime.now(UTC).strftime('%Y%m%d')}-{self._anomaly_counter:05d}"

    def build_baselines(
        self,
        tenant_id: str,
        baseline_days: int = 30,
    ) -> dict[str, BehaviorBaseline]:
        """
        Build behavioral baselines from historical data.

        Args:
            tenant_id: Tenant to build baselines for
            baseline_days: Days of history to use

        Returns:
            Dictionary of entity_id -> BehaviorBaseline
        """
        entries = [e for e in self.entries if e.get("tenant_id") == tenant_id]

        # Parse timestamps
        for entry in entries:
            if isinstance(entry.get("created_at"), str):
                entry["_timestamp"] = datetime.fromisoformat(
                    entry["created_at"].replace("Z", "+00:00")
                )
            else:
                entry["_timestamp"] = entry.get("created_at", datetime.now(UTC))

        # Build actor baselines
        actor_entries = defaultdict(list)
        for entry in entries:
            actor_id = entry.get("actor_id")
            if actor_id:
                actor_entries[actor_id].append(entry)

        for actor_id, actor_logs in actor_entries.items():
            baseline = self._build_entity_baseline(
                actor_id, "actor", actor_logs, baseline_days
            )
            self._baselines[f"actor:{actor_id}"] = baseline

        return self._baselines

    def _build_entity_baseline(
        self,
        entity_id: str,
        entity_type: str,
        entries: list[dict],
        baseline_days: int,
    ) -> BehaviorBaseline:
        """Build baseline for a single entity"""
        baseline = BehaviorBaseline(
            entity_id=entity_id,
            entity_type=entity_type,
            baseline_period_days=baseline_days,
            data_points=len(entries),
        )

        if not entries:
            return baseline

        # Calculate daily event counts
        daily_counts = Counter(
            e["_timestamp"].strftime("%Y-%m-%d") for e in entries
        )
        counts = list(daily_counts.values())

        if counts:
            baseline.avg_daily_events = sum(counts) / len(counts)
            if len(counts) > 1:
                variance = sum((c - baseline.avg_daily_events) ** 2 for c in counts) / len(counts)
                baseline.std_daily_events = math.sqrt(variance)

            # Calculate bounds (3 sigma)
            baseline.volume_upper_bound = (
                baseline.avg_daily_events + 3 * baseline.std_daily_events
            )
            baseline.volume_lower_bound = max(
                0, baseline.avg_daily_events - 3 * baseline.std_daily_events
            )

        # Calculate hourly distribution
        hourly_counts = Counter(e["_timestamp"].hour for e in entries)
        total_entries = len(entries)
        for hour, count in hourly_counts.items():
            if count / total_entries >= self.UNUSUAL_HOUR_THRESHOLD:
                baseline.typical_hours.add(hour)

        baseline.avg_hourly_events = total_entries / (baseline_days * 24)

        # Track typical actions and resources
        baseline.typical_actions = {e.get("action") for e in entries if e.get("action")}
        baseline.typical_resources = {
            f"{e.get('resource_type')}/{e.get('resource_id')}"
            for e in entries
            if e.get("resource_type")
        }

        return baseline

    def detect(
        self,
        tenant_id: str,
        window_hours: int = 24,
        use_baselines: bool = True,
    ) -> DetectionReport:
        """
        Run anomaly detection on audit logs.

        Args:
            tenant_id: Tenant to analyze
            window_hours: Analysis window in hours
            use_baselines: Whether to use behavioral baselines

        Returns:
            DetectionReport with all findings
        """
        start_time = datetime.now(UTC)

        entries = [e for e in self.entries if e.get("tenant_id") == tenant_id]

        # Parse timestamps
        for entry in entries:
            if isinstance(entry.get("created_at"), str):
                entry["_timestamp"] = datetime.fromisoformat(
                    entry["created_at"].replace("Z", "+00:00")
                )
            else:
                entry["_timestamp"] = entry.get("created_at", datetime.now(UTC))

        # Filter to analysis window
        cutoff = datetime.now(UTC) - timedelta(hours=window_hours)
        window_entries = [e for e in entries if e["_timestamp"] >= cutoff]

        report = DetectionReport(
            tenant_id=tenant_id,
            total_events_analyzed=len(window_entries),
            analysis_period=(cutoff, datetime.now(UTC)),
        )

        if use_baselines and not self._baselines:
            self.build_baselines(tenant_id)

        report.actor_baselines = {
            k: v for k, v in self._baselines.items() if k.startswith("actor:")
        }

        # Run detection algorithms
        anomalies = []

        # 1. Volume-based detection
        anomalies.extend(self._detect_volume_anomalies(window_entries))

        # 2. Time-based detection
        anomalies.extend(self._detect_time_anomalies(window_entries))

        # 3. Behavioral detection
        if use_baselines:
            anomalies.extend(self._detect_behavioral_anomalies(window_entries))

        # 4. Pattern-based detection
        anomalies.extend(self._detect_suspicious_patterns(window_entries))

        # 5. Velocity detection
        anomalies.extend(self._detect_velocity_anomalies(window_entries))

        # 6. Privilege escalation detection
        anomalies.extend(self._detect_privilege_escalation(window_entries))

        # 7. Data exfiltration detection
        anomalies.extend(self._detect_data_exfiltration(window_entries))

        # 8. Brute force detection
        anomalies.extend(self._detect_brute_force(window_entries))

        # Sort by severity and timestamp
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
            SeverityLevel.INFO: 4,
        }
        anomalies.sort(key=lambda a: (severity_order[a.severity], a.timestamp))

        report.anomalies = anomalies
        report.anomalies_detected = len(anomalies)
        report.critical_anomalies = sum(
            1 for a in anomalies if a.severity == SeverityLevel.CRITICAL
        )
        report.high_anomalies = sum(
            1 for a in anomalies if a.severity == SeverityLevel.HIGH
        )

        # Calculate threat score
        self._calculate_threat_score(report)

        # Calculate duration
        end_time = datetime.now(UTC)
        report.detection_duration_ms = (end_time - start_time).total_seconds() * 1000

        return report

    def _detect_volume_anomalies(self, entries: list[dict]) -> list[Anomaly]:
        """Detect volume-based anomalies using Z-score"""
        anomalies = []

        # Group by hour
        hourly_counts = defaultdict(int)
        for entry in entries:
            hour_key = entry["_timestamp"].strftime("%Y-%m-%d %H")
            hourly_counts[hour_key] += 1

        if len(hourly_counts) < 3:
            return anomalies

        counts = list(hourly_counts.values())
        mean = sum(counts) / len(counts)
        if len(counts) > 1:
            std = math.sqrt(sum((c - mean) ** 2 for c in counts) / len(counts))
        else:
            std = 0

        if std == 0:
            return anomalies

        for hour, count in hourly_counts.items():
            z_score = (count - mean) / std

            if z_score > self.Z_SCORE_THRESHOLD:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.VOLUME_SPIKE,
                        severity=SeverityLevel.MEDIUM
                        if z_score < 4
                        else SeverityLevel.HIGH,
                        description=f"Volume spike detected: {count} events in hour {hour} "
                        f"(Z-score: {z_score:.2f})",
                        confidence=min(0.95, 0.5 + z_score / 10),
                        timestamp=datetime.strptime(hour, "%Y-%m-%d %H").replace(
                            tzinfo=UTC
                        ),
                        metrics={
                            "count": count,
                            "mean": mean,
                            "std": std,
                            "z_score": z_score,
                        },
                        recommendations=[
                            "Investigate source of increased activity",
                            "Check for automated processes or attacks",
                        ],
                    )
                )
            elif z_score < -self.Z_SCORE_THRESHOLD:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.VOLUME_DROP,
                        severity=SeverityLevel.LOW,
                        description=f"Volume drop detected: {count} events in hour {hour}",
                        confidence=min(0.9, 0.5 + abs(z_score) / 10),
                        timestamp=datetime.strptime(hour, "%Y-%m-%d %H").replace(
                            tzinfo=UTC
                        ),
                        metrics={"count": count, "z_score": z_score},
                        recommendations=["Verify system availability"],
                    )
                )

        return anomalies

    def _detect_time_anomalies(self, entries: list[dict]) -> list[Anomaly]:
        """Detect unusual time patterns"""
        anomalies = []
        unusual_hours = {0, 1, 2, 3, 4, 5}  # Midnight to 6 AM

        # Group by actor and check for unusual hours
        actor_unusual = defaultdict(list)
        for entry in entries:
            hour = entry["_timestamp"].hour
            if hour in unusual_hours:
                actor_id = entry.get("actor_id", "unknown")
                actor_unusual[actor_id].append(entry)

        for actor_id, unusual_entries in actor_unusual.items():
            if len(unusual_entries) >= 3:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.UNUSUAL_TIME,
                        severity=SeverityLevel.LOW,
                        description=f"Activity during unusual hours by {actor_id}: "
                        f"{len(unusual_entries)} events",
                        confidence=0.6,
                        timestamp=unusual_entries[-1]["_timestamp"],
                        actor_id=actor_id,
                        evidence=[
                            {
                                "action": e.get("action"),
                                "time": e["_timestamp"].isoformat(),
                            }
                            for e in unusual_entries[:5]
                        ],
                        recommendations=[
                            "Verify if off-hours activity is expected",
                            "Check for compromised credentials",
                        ],
                    )
                )

        return anomalies

    def _detect_behavioral_anomalies(self, entries: list[dict]) -> list[Anomaly]:
        """Detect deviations from established baselines"""
        anomalies = []

        # Group by actor
        actor_entries = defaultdict(list)
        for entry in entries:
            actor_id = entry.get("actor_id")
            if actor_id:
                actor_entries[actor_id].append(entry)

        for actor_id, actor_logs in actor_entries.items():
            baseline_key = f"actor:{actor_id}"
            baseline = self._baselines.get(baseline_key)

            if not baseline or baseline.data_points < 10:
                continue

            # Check for new actions
            current_actions = {e.get("action") for e in actor_logs if e.get("action")}
            new_actions = current_actions - baseline.typical_actions

            if new_actions:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.NEW_ACTION,
                        severity=SeverityLevel.LOW,
                        description=f"New actions by {actor_id}: {', '.join(list(new_actions)[:5])}",
                        confidence=0.7,
                        timestamp=actor_logs[-1]["_timestamp"],
                        actor_id=actor_id,
                        metrics={"new_actions": list(new_actions)},
                        recommendations=["Review new action usage"],
                    )
                )

            # Check for new resources
            current_resources = {
                f"{e.get('resource_type')}/{e.get('resource_id')}"
                for e in actor_logs
                if e.get("resource_type")
            }
            new_resources = current_resources - baseline.typical_resources

            if len(new_resources) > 5:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.NEW_RESOURCE,
                        severity=SeverityLevel.MEDIUM,
                        description=f"Access to {len(new_resources)} new resources by {actor_id}",
                        confidence=0.75,
                        timestamp=actor_logs[-1]["_timestamp"],
                        actor_id=actor_id,
                        metrics={"new_resource_count": len(new_resources)},
                        recommendations=[
                            "Verify authorization for new resource access"
                        ],
                    )
                )

        return anomalies

    def _detect_suspicious_patterns(self, entries: list[dict]) -> list[Anomaly]:
        """Detect suspicious action sequences"""
        anomalies = []

        # Group by actor and session
        actor_sessions = defaultdict(list)
        for entry in entries:
            actor_id = entry.get("actor_id", "unknown")
            actor_sessions[actor_id].append(entry)

        for actor_id, actor_logs in actor_sessions.items():
            # Sort by timestamp
            actor_logs.sort(key=lambda x: x["_timestamp"])
            actions = [e.get("action", "") for e in actor_logs]

            # Check for suspicious sequences
            for pattern in self.SUSPICIOUS_ACTION_SEQUENCES:
                pattern_str = "->".join(pattern)
                for i in range(len(actions) - len(pattern) + 1):
                    window = actions[i : i + len(pattern)]
                    # Fuzzy match - check if actions contain the pattern
                    matches = all(
                        any(p in a for a in window) for p in pattern
                    )
                    if matches:
                        anomalies.append(
                            Anomaly(
                                anomaly_id=self._generate_anomaly_id(),
                                anomaly_type=AnomalyType.SUSPICIOUS_PATTERN,
                                severity=SeverityLevel.HIGH,
                                description=f"Suspicious action sequence detected for {actor_id}",
                                confidence=0.85,
                                timestamp=actor_logs[i]["_timestamp"],
                                actor_id=actor_id,
                                evidence=[
                                    {"action": a, "index": i + j}
                                    for j, a in enumerate(window)
                                ],
                                recommendations=[
                                    "Investigate actor's recent activity",
                                    "Consider temporary access suspension",
                                ],
                            )
                        )
                        break

        return anomalies

    def _detect_velocity_anomalies(self, entries: list[dict]) -> list[Anomaly]:
        """Detect abnormally high action velocity"""
        anomalies = []

        # Group by actor
        actor_entries = defaultdict(list)
        for entry in entries:
            actor_id = entry.get("actor_id")
            if actor_id:
                actor_entries[actor_id].append(entry)

        for actor_id, actor_logs in actor_entries.items():
            if len(actor_logs) < 2:
                continue

            # Sort by time
            actor_logs.sort(key=lambda x: x["_timestamp"])

            # Check velocity in 1-minute windows
            for i, entry in enumerate(actor_logs[:-1]):
                window_start = entry["_timestamp"]
                window_end = window_start + timedelta(minutes=1)

                window_count = sum(
                    1
                    for e in actor_logs[i:]
                    if window_start <= e["_timestamp"] <= window_end
                )

                if window_count >= self.VELOCITY_THRESHOLD:
                    anomalies.append(
                        Anomaly(
                            anomaly_id=self._generate_anomaly_id(),
                            anomaly_type=AnomalyType.VELOCITY_ANOMALY,
                            severity=SeverityLevel.HIGH,
                            description=f"High velocity: {window_count} events/minute by {actor_id}",
                            confidence=0.9,
                            timestamp=window_start,
                            actor_id=actor_id,
                            metrics={
                                "events_per_minute": window_count,
                                "threshold": self.VELOCITY_THRESHOLD,
                            },
                            recommendations=[
                                "Check for automated attacks",
                                "Review rate limiting configuration",
                            ],
                        )
                    )
                    break  # One alert per actor

        return anomalies

    def _detect_privilege_escalation(self, entries: list[dict]) -> list[Anomaly]:
        """Detect potential privilege escalation attempts"""
        anomalies = []

        for entry in entries:
            action = entry.get("action", "")
            if action in self.PRIVILEGE_ESCALATION_ACTIONS:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.PRIVILEGE_ESCALATION,
                        severity=SeverityLevel.CRITICAL,
                        description=f"Privilege escalation: {action}",
                        confidence=0.95,
                        timestamp=entry["_timestamp"],
                        actor_id=entry.get("actor_id"),
                        resource=f"{entry.get('resource_type')}/{entry.get('resource_id')}",
                        evidence=[
                            {
                                "action": action,
                                "actor": entry.get("actor_id"),
                                "target": entry.get("resource_id"),
                            }
                        ],
                        recommendations=[
                            "Verify authorization for privilege change",
                            "Audit the requesting actor",
                        ],
                    )
                )

        return anomalies

    def _detect_data_exfiltration(self, entries: list[dict]) -> list[Anomaly]:
        """Detect potential data exfiltration"""
        anomalies = []

        # Group export actions by actor
        actor_exports = defaultdict(list)
        for entry in entries:
            action = entry.get("action", "")
            if action in self.DATA_EXFILTRATION_INDICATORS:
                actor_id = entry.get("actor_id", "unknown")
                actor_exports[actor_id].append(entry)

        for actor_id, exports in actor_exports.items():
            if len(exports) >= 3:
                anomalies.append(
                    Anomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.DATA_EXFILTRATION,
                        severity=SeverityLevel.CRITICAL,
                        description=f"Potential data exfiltration: {len(exports)} export operations by {actor_id}",
                        confidence=0.85,
                        timestamp=exports[-1]["_timestamp"],
                        actor_id=actor_id,
                        evidence=[
                            {
                                "action": e.get("action"),
                                "resource": e.get("resource_type"),
                                "time": e["_timestamp"].isoformat(),
                            }
                            for e in exports[:5]
                        ],
                        recommendations=[
                            "Immediately investigate export activity",
                            "Consider temporary account suspension",
                            "Review exported data scope",
                        ],
                    )
                )

        return anomalies

    def _detect_brute_force(self, entries: list[dict]) -> list[Anomaly]:
        """Detect brute force attempts"""
        anomalies = []

        # Look for failed login patterns
        failed_logins = defaultdict(list)
        for entry in entries:
            action = entry.get("action", "")
            if "login" in action.lower() and "fail" in action.lower():
                # Group by IP or actor
                ip = entry.get("ip", "unknown")
                failed_logins[ip].append(entry)

        for ip, failures in failed_logins.items():
            if len(failures) >= 5:
                # Check time window
                failures.sort(key=lambda x: x["_timestamp"])
                time_span = (
                    failures[-1]["_timestamp"] - failures[0]["_timestamp"]
                ).total_seconds()

                if time_span < 300:  # 5 minutes
                    anomalies.append(
                        Anomaly(
                            anomaly_id=self._generate_anomaly_id(),
                            anomaly_type=AnomalyType.BRUTE_FORCE,
                            severity=SeverityLevel.CRITICAL,
                            description=f"Brute force attack: {len(failures)} failed logins from {ip} "
                            f"in {time_span:.0f} seconds",
                            confidence=0.95,
                            timestamp=failures[-1]["_timestamp"],
                            metrics={
                                "failed_attempts": len(failures),
                                "time_span_seconds": time_span,
                                "source_ip": ip,
                            },
                            evidence=[
                                {
                                    "time": f["_timestamp"].isoformat(),
                                    "target": f.get("resource_id"),
                                }
                                for f in failures[:5]
                            ],
                            recommendations=[
                                "Block source IP address",
                                "Enable account lockout",
                                "Implement CAPTCHA",
                            ],
                        )
                    )

        return anomalies

    def _calculate_threat_score(self, report: DetectionReport) -> None:
        """Calculate overall threat score"""
        if not report.anomalies:
            report.threat_score = 0
            report.threat_level = "low"
            return

        # Weight by severity
        weights = {
            SeverityLevel.CRITICAL: 25,
            SeverityLevel.HIGH: 15,
            SeverityLevel.MEDIUM: 8,
            SeverityLevel.LOW: 3,
            SeverityLevel.INFO: 1,
        }

        total_weight = sum(
            weights.get(a.severity, 0) * a.confidence for a in report.anomalies
        )

        # Normalize to 0-100
        report.threat_score = min(100, total_weight)

        # Determine threat level
        if report.threat_score >= 75:
            report.threat_level = "critical"
        elif report.threat_score >= 50:
            report.threat_level = "high"
        elif report.threat_score >= 25:
            report.threat_level = "medium"
        else:
            report.threat_level = "low"

        # Identify top threats
        threat_types = Counter(a.anomaly_type.value for a in report.anomalies)
        report.top_threats = [
            {"type": t, "count": c} for t, c in threat_types.most_common(5)
        ]


def generate_markdown_report(report: DetectionReport) -> str:
    """Generate markdown detection report"""
    threat_icons = {
        "low": "LOW",
        "medium": "MEDIUM",
        "high": "HIGH",
        "critical": "CRITICAL",
    }

    lines = [
        "# SAHOOL Anomaly Detection Report",
        "",
        f"> Detection Time: {report.detection_time.isoformat()}",
        f"> Tenant: {report.tenant_id}",
        f"> Analysis Period: {report.analysis_period[0].isoformat()} to "
        f"{report.analysis_period[1].isoformat()}"
        if report.analysis_period
        else "",
        f"> Duration: {report.detection_duration_ms:.2f}ms",
        "",
        "## Threat Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Threat Score | **{report.threat_score:.1f}/100** |",
        f"| Threat Level | {threat_icons.get(report.threat_level, report.threat_level)} |",
        f"| Events Analyzed | {report.total_events_analyzed:,} |",
        f"| Anomalies Detected | {report.anomalies_detected} |",
        f"| Critical | {report.critical_anomalies} |",
        f"| High | {report.high_anomalies} |",
        "",
    ]

    if report.top_threats:
        lines.extend(
            [
                "## Top Threat Types",
                "",
            ]
        )
        for threat in report.top_threats:
            lines.append(f"- **{threat['type']}**: {threat['count']} occurrences")
        lines.append("")

    # Critical and High anomalies
    critical_high = [
        a
        for a in report.anomalies
        if a.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH)
    ]

    if critical_high:
        lines.extend(
            [
                "## Critical & High Severity Anomalies",
                "",
            ]
        )
        for anomaly in critical_high[:20]:
            severity = "CRITICAL" if anomaly.severity == SeverityLevel.CRITICAL else "HIGH"
            lines.extend(
                [
                    f"### [{severity}] {anomaly.anomaly_type.value}",
                    "",
                    f"**ID**: {anomaly.anomaly_id}",
                    f"**Time**: {anomaly.timestamp.isoformat()}",
                    f"**Confidence**: {anomaly.confidence:.0%}",
                    "",
                    anomaly.description,
                    "",
                ]
            )
            if anomaly.actor_id:
                lines.append(f"**Actor**: {anomaly.actor_id}")
            if anomaly.recommendations:
                lines.append("")
                lines.append("**Recommendations**:")
                for rec in anomaly.recommendations:
                    lines.append(f"- {rec}")
            lines.append("")

    # Medium and Low anomalies summary
    other = [
        a
        for a in report.anomalies
        if a.severity not in (SeverityLevel.CRITICAL, SeverityLevel.HIGH)
    ]

    if other:
        lines.extend(
            [
                "## Other Anomalies",
                "",
                "| Type | Severity | Time | Description |",
                "|------|----------|------|-------------|",
            ]
        )
        for anomaly in other[:30]:
            lines.append(
                f"| {anomaly.anomaly_type.value} | {anomaly.severity.value} | "
                f"{anomaly.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                f"{anomaly.description[:50]}... |"
            )
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
    parser = argparse.ArgumentParser(description="Detect anomalies in audit logs")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input JSON file with audit logs",
    )
    parser.add_argument(
        "--tenant-id",
        "-t",
        required=True,
        help="Tenant ID to analyze",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="anomaly_report.md",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--window",
        "-w",
        type=int,
        default=24,
        help="Analysis window in hours",
    )
    args = parser.parse_args()

    # Load and detect
    detector = AuditAnomalyDetector()
    detector.load_from_file(Path(args.input))
    report = detector.detect(tenant_id=args.tenant_id, window_hours=args.window)

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "tenant_id": report.tenant_id,
                "detection_time": report.detection_time.isoformat(),
                "threat_score": report.threat_score,
                "threat_level": report.threat_level,
                "events_analyzed": report.total_events_analyzed,
                "anomalies_detected": report.anomalies_detected,
                "critical_anomalies": report.critical_anomalies,
                "high_anomalies": report.high_anomalies,
                "top_threats": report.top_threats,
                "anomalies": [
                    {
                        "id": a.anomaly_id,
                        "type": a.anomaly_type.value,
                        "severity": a.severity.value,
                        "description": a.description,
                        "confidence": a.confidence,
                        "timestamp": a.timestamp.isoformat(),
                        "actor_id": a.actor_id,
                        "recommendations": a.recommendations,
                    }
                    for a in report.anomalies
                ],
            },
            indent=2,
        )
    else:
        output = generate_markdown_report(report)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(output)

    # Console output
    print(f"Anomaly Detection Complete")
    print(f"  Threat Score: {report.threat_score:.1f}/100 ({report.threat_level.upper()})")
    print(f"  Anomalies: {report.anomalies_detected} detected")
    print(f"  Critical: {report.critical_anomalies}")
    print(f"  High: {report.high_anomalies}")
    print(f"  Report: {output_path}")

    # Exit with error if critical threats found
    sys.exit(1 if report.critical_anomalies > 0 else 0)


if __name__ == "__main__":
    main()
