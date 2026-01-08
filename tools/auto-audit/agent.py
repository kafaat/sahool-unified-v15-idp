#!/usr/bin/env python3
"""
SAHOOL Audit Agent - وكيل التدقيق الذكي
A2A Protocol-compliant audit agent with self-healing capabilities

This agent integrates the Auto Audit Tools suite with the SAHOOL AI agent ecosystem,
providing automated security monitoring, compliance validation, and self-healing.

يدمج هذا الوكيل مجموعة أدوات التدقيق التلقائي مع نظام وكلاء SAHOOL،
مما يوفر مراقبة أمنية آلية وتحقق من الامتثال وإصلاح ذاتي.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog

# Import Auto Audit Tools
from tools.auto_audit.analyzer import AuditLogAnalyzer
from tools.auto_audit.anomaly_detector import AuditAnomalyDetector
from tools.auto_audit.compliance_reporter import ComplianceFramework, ComplianceReporter
from tools.auto_audit.exporter import AuditDataExporter, ExportConfig, ExportFormat
from tools.auto_audit.hashchain_validator import HashChainValidator

# Import A2A Protocol components
from shared.a2a.agent import A2AAgent, AgentCapability
from shared.a2a.protocol import TaskMessage

logger = structlog.get_logger()


class AuditAgent(A2AAgent):
    """
    Intelligent Audit Agent - وكيل التدقيق الذكي

    Provides automated audit analysis, threat detection, compliance monitoring,
    and self-healing recommendations for the SAHOOL platform.

    يوفر تحليل تدقيق آلي وكشف تهديدات ومراقبة امتثال
    وتوصيات إصلاح ذاتي لمنصة سهول.

    Capabilities:
    - analyze_audit_logs: Comprehensive audit log analysis
    - validate_integrity: Hash chain validation for tamper detection
    - assess_compliance: Multi-framework compliance assessment
    - detect_anomalies: ML-based threat and anomaly detection
    - recommend_fixes: Self-healing recommendations
    - export_audit_data: Export to SIEM systems
    - run_full_audit: Complete audit suite execution
    """

    def __init__(
        self,
        task_endpoint: str = "https://api.sahool.app/agents/audit-agent/invoke",
        websocket_endpoint: str | None = None,
    ):
        """Initialize Audit Agent"""
        super().__init__(
            agent_id="audit-agent",
            name="Audit Agent",
            version="1.0.0",
            description="Intelligent audit analysis, compliance monitoring, and self-healing agent",
            provider="SAHOOL",
            task_endpoint=task_endpoint,
            websocket_endpoint=websocket_endpoint,
        )

        # Initialize audit tools
        self._analyzer = AuditLogAnalyzer()
        self._validator = HashChainValidator()
        self._compliance_reporter = ComplianceReporter()
        self._anomaly_detector = AuditAnomalyDetector()
        self._exporter = AuditDataExporter()

        # Cached audit data
        self._audit_cache: dict[str, list[dict]] = {}

        # Register task handlers
        self._register_handlers()

        logger.info(
            "audit_agent_initialized",
            agent_id=self.agent_id,
            capabilities=len(self.get_capabilities()),
        )

    def _register_handlers(self) -> None:
        """Register all task handlers"""
        self.register_task_handler("analyze_audit_logs", self._handle_analyze)
        self.register_task_handler("validate_integrity", self._handle_validate)
        self.register_task_handler("assess_compliance", self._handle_compliance)
        self.register_task_handler("detect_anomalies", self._handle_detect)
        self.register_task_handler("recommend_fixes", self._handle_recommend_fixes)
        self.register_task_handler("export_audit_data", self._handle_export)
        self.register_task_handler("run_full_audit", self._handle_full_audit)
        self.register_task_handler("get_threat_score", self._handle_threat_score)

    def get_capabilities(self) -> list[AgentCapability]:
        """Define agent capabilities for A2A discovery"""
        return [
            AgentCapability(
                capability_id="analyze_audit_logs",
                name="Analyze Audit Logs",
                description="Comprehensive audit log analysis with pattern detection and risk indicators",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id"],
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"},
                        "audit_data": {"type": "array", "description": "Audit log entries"},
                        "start_date": {"type": "string", "format": "date-time"},
                        "end_date": {"type": "string", "format": "date-time"},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "total_events": {"type": "integer"},
                        "unique_actors": {"type": "integer"},
                        "risk_indicators": {"type": "array"},
                        "anomalies": {"type": "array"},
                        "top_actors": {"type": "array"},
                        "top_actions": {"type": "array"},
                    },
                },
                tags=["audit", "analysis", "security"],
            ),
            AgentCapability(
                capability_id="validate_integrity",
                name="Validate Hash Chain Integrity",
                description="Verify audit trail integrity using cryptographic hash chain validation",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "audit_data": {"type": "array"},
                        "generate_recovery": {"type": "boolean", "default": True},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "is_valid": {"type": "boolean"},
                        "chain_integrity": {"type": "number"},
                        "chain_breaks": {"type": "integer"},
                        "tamper_indicators": {"type": "integer"},
                        "recovery_suggestions": {"type": "array"},
                    },
                },
                tags=["audit", "integrity", "security", "hash-chain"],
            ),
            AgentCapability(
                capability_id="assess_compliance",
                name="Assess Compliance",
                description="Multi-framework compliance assessment (GDPR, SOC2, ISO27001)",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id", "framework"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "framework": {
                            "type": "string",
                            "enum": ["gdpr", "soc2", "iso27001", "all"],
                        },
                        "audit_data": {"type": "array"},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "overall_score": {"type": "number"},
                        "risk_level": {"type": "string"},
                        "compliant_controls": {"type": "integer"},
                        "non_compliant_controls": {"type": "integer"},
                        "critical_findings": {"type": "array"},
                        "recommendations": {"type": "array"},
                    },
                },
                tags=["compliance", "gdpr", "soc2", "iso27001"],
            ),
            AgentCapability(
                capability_id="detect_anomalies",
                name="Detect Anomalies",
                description="ML-based anomaly and threat detection with behavioral analysis",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "audit_data": {"type": "array"},
                        "window_hours": {"type": "integer", "default": 24},
                        "build_baselines": {"type": "boolean", "default": True},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "threat_score": {"type": "number"},
                        "threat_level": {"type": "string"},
                        "anomalies_detected": {"type": "integer"},
                        "critical_anomalies": {"type": "integer"},
                        "anomalies": {"type": "array"},
                        "top_threats": {"type": "array"},
                    },
                },
                tags=["anomaly", "threat", "security", "ml"],
            ),
            AgentCapability(
                capability_id="recommend_fixes",
                name="Recommend Fixes",
                description="Generate self-healing recommendations based on detected issues",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id", "issues"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "issues": {"type": "array"},
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "all"],
                        },
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendations": {"type": "array"},
                        "auto_fixable": {"type": "array"},
                        "manual_required": {"type": "array"},
                        "priority_order": {"type": "array"},
                    },
                },
                tags=["self-healing", "remediation", "automation"],
            ),
            AgentCapability(
                capability_id="run_full_audit",
                name="Run Full Audit",
                description="Execute complete audit analysis suite",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "audit_data": {"type": "array"},
                        "compliance_framework": {"type": "string", "default": "all"},
                        "output_format": {"type": "string", "default": "json"},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "analysis_report": {"type": "object"},
                        "integrity_report": {"type": "object"},
                        "compliance_report": {"type": "object"},
                        "anomaly_report": {"type": "object"},
                        "overall_health": {"type": "string"},
                        "recommendations": {"type": "array"},
                    },
                },
                tags=["audit", "comprehensive", "security"],
            ),
            AgentCapability(
                capability_id="export_audit_data",
                name="Export Audit Data",
                description="Export audit data in various SIEM formats",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id", "format"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "format": {
                            "type": "string",
                            "enum": ["json", "csv", "splunk", "elk", "cef", "syslog"],
                        },
                        "redact_pii": {"type": "boolean", "default": True},
                        "compress": {"type": "boolean", "default": False},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "entries_exported": {"type": "integer"},
                        "format": {"type": "string"},
                        "data": {"type": "string"},
                    },
                },
                tags=["export", "siem", "integration"],
            ),
            AgentCapability(
                capability_id="get_threat_score",
                name="Get Threat Score",
                description="Get current security threat score for tenant",
                input_schema={
                    "type": "object",
                    "required": ["tenant_id"],
                    "properties": {
                        "tenant_id": {"type": "string"},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "threat_score": {"type": "number"},
                        "threat_level": {"type": "string"},
                        "last_updated": {"type": "string"},
                    },
                },
                tags=["threat", "security", "monitoring"],
            ),
        ]

    def _load_audit_data(self, task: TaskMessage) -> list[dict]:
        """Load audit data from task input or cache"""
        audit_data = task.input_data.get("audit_data")
        if audit_data:
            return audit_data

        # Try to load from file if path provided
        file_path = task.input_data.get("audit_file_path")
        if file_path:
            with open(file_path) as f:
                return json.load(f)

        # Return cached data for tenant if available
        tenant_id = task.input_data.get("tenant_id")
        return self._audit_cache.get(tenant_id, [])

    async def _handle_analyze(self, task: TaskMessage) -> dict[str, Any]:
        """Handle audit log analysis task"""
        tenant_id = task.input_data.get("tenant_id")
        audit_data = self._load_audit_data(task)

        self._analyzer.entries = audit_data
        report = self._analyzer.analyze(tenant_id=tenant_id)

        return {
            "tenant_id": tenant_id,
            "total_events": report.total_events,
            "unique_actors": report.unique_actors,
            "unique_resources": report.unique_resources,
            "unique_actions": report.unique_actions,
            "action_distribution": dict(list(report.action_distribution.items())[:10]),
            "risk_indicators": report.risk_indicators[:20],
            "anomalies": report.anomalies[:20],
            "top_actors": report.top_actors[:10],
            "top_actions": report.top_actions[:10],
            "actor_profiles": dict(list(report.actor_profiles.items())[:5]),
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_validate(self, task: TaskMessage) -> dict[str, Any]:
        """Handle hash chain validation task"""
        tenant_id = task.input_data.get("tenant_id")
        audit_data = self._load_audit_data(task)
        generate_recovery = task.input_data.get("generate_recovery", True)

        self._validator.entries = audit_data
        report = self._validator.validate(tenant_id=tenant_id)

        result = {
            "tenant_id": tenant_id,
            "is_valid": report.is_valid,
            "chain_integrity": report.chain_integrity,
            "total_entries": report.total_entries,
            "validated_entries": report.validated_entries,
            "chain_breaks": report.chain_breaks_detected,
            "tamper_indicators": report.tamper_indicators,
            "errors": [
                {
                    "index": e.entry_index,
                    "type": e.error_type,
                    "severity": e.severity,
                    "description": e.description,
                }
                for e in report.errors[:20]
            ],
            "suspicious_entries": report.suspicious_entries[:10],
            "timeline_gaps": report.timeline_gaps[:10],
            "validation_timestamp": datetime.now(UTC).isoformat(),
        }

        if generate_recovery and not report.is_valid:
            result["recovery_suggestions"] = self._generate_recovery_suggestions(report)

        return result

    def _generate_recovery_suggestions(self, report) -> list[dict]:
        """Generate recovery suggestions for integrity issues"""
        suggestions = []

        for error in report.errors[:10]:
            if error.error_type == "hash_mismatch":
                suggestions.append(
                    {
                        "issue": f"Hash mismatch at entry {error.entry_index}",
                        "severity": "critical",
                        "action": "Compare with backup data",
                        "auto_fixable": False,
                        "steps": [
                            "Retrieve backup of affected entries",
                            "Compare current values with backup",
                            "Identify modified fields",
                            "Restore from backup if tampering confirmed",
                        ],
                    }
                )
            elif error.error_type == "chain_break":
                suggestions.append(
                    {
                        "issue": f"Chain break at entry {error.entry_index}",
                        "severity": "high",
                        "action": "Investigate missing entries",
                        "auto_fixable": False,
                        "steps": [
                            "Check for deleted entries",
                            "Verify database replication",
                            "Look for timestamp gaps",
                        ],
                    }
                )

        return suggestions

    async def _handle_compliance(self, task: TaskMessage) -> dict[str, Any]:
        """Handle compliance assessment task"""
        tenant_id = task.input_data.get("tenant_id")
        framework_str = task.input_data.get("framework", "all")
        audit_data = self._load_audit_data(task)

        framework_map = {
            "gdpr": ComplianceFramework.GDPR,
            "soc2": ComplianceFramework.SOC2,
            "iso27001": ComplianceFramework.ISO27001,
            "all": ComplianceFramework.ALL,
        }

        self._compliance_reporter.entries = audit_data
        self._compliance_reporter._build_action_cache()

        report = self._compliance_reporter.generate_report(
            framework=framework_map.get(framework_str, ComplianceFramework.ALL),
            tenant_id=tenant_id,
        )

        return {
            "tenant_id": tenant_id,
            "framework": report.framework,
            "overall_score": report.overall_score,
            "risk_level": report.risk_level,
            "total_controls": report.total_controls,
            "compliant_controls": report.compliant_controls,
            "partial_controls": report.partial_controls,
            "non_compliant_controls": report.non_compliant_controls,
            "categories": [
                {
                    "name": cat.name,
                    "score": cat.compliance_score,
                    "controls_count": len(cat.controls),
                }
                for cat in report.categories
            ],
            "critical_findings": report.critical_findings[:20],
            "recommendations": report.recommendations[:20],
            "executive_summary": report.executive_summary,
            "assessment_timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_detect(self, task: TaskMessage) -> dict[str, Any]:
        """Handle anomaly detection task"""
        tenant_id = task.input_data.get("tenant_id")
        window_hours = task.input_data.get("window_hours", 24)
        build_baselines = task.input_data.get("build_baselines", True)
        audit_data = self._load_audit_data(task)

        self._anomaly_detector.entries = audit_data

        if build_baselines:
            self._anomaly_detector.build_baselines(tenant_id)

        report = self._anomaly_detector.detect(
            tenant_id=tenant_id,
            window_hours=window_hours,
        )

        return {
            "tenant_id": tenant_id,
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
                    "actor_id": a.actor_id,
                    "recommendations": a.recommendations,
                }
                for a in report.anomalies[:30]
            ],
            "detection_timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_recommend_fixes(self, task: TaskMessage) -> dict[str, Any]:
        """Handle self-healing recommendations task"""
        tenant_id = task.input_data.get("tenant_id")
        issues = task.input_data.get("issues", [])
        priority = task.input_data.get("priority", "all")

        recommendations = []
        auto_fixable = []
        manual_required = []

        for issue in issues:
            issue_type = issue.get("type", "unknown")
            severity = issue.get("severity", "medium")

            if priority != "all" and severity != priority:
                continue

            rec = self._generate_fix_recommendation(issue)
            recommendations.append(rec)

            if rec.get("auto_fixable"):
                auto_fixable.append(rec)
            else:
                manual_required.append(rec)

        # Sort by priority
        priority_order = ["critical", "high", "medium", "low"]
        recommendations.sort(key=lambda x: priority_order.index(x.get("severity", "medium")))

        return {
            "tenant_id": tenant_id,
            "total_issues": len(issues),
            "recommendations": recommendations,
            "auto_fixable": auto_fixable,
            "manual_required": manual_required,
            "priority_order": [r["issue_id"] for r in recommendations],
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def _generate_fix_recommendation(self, issue: dict) -> dict:
        """Generate fix recommendation for an issue"""
        issue_type = issue.get("type", "unknown")
        issue_id = issue.get("id", str(uuid4())[:8])

        # Define fix strategies for common issue types
        fix_strategies = {
            "volume_spike": {
                "action": "Investigate and implement rate limiting",
                "auto_fixable": True,
                "auto_fix_command": "apply_rate_limit",
                "steps": [
                    "Identify source of high volume",
                    "Apply rate limiting rules",
                    "Monitor for continued spikes",
                ],
            },
            "brute_force": {
                "action": "Block source and strengthen authentication",
                "auto_fixable": True,
                "auto_fix_command": "block_ip_and_lockout",
                "steps": [
                    "Block source IP address",
                    "Enable account lockout",
                    "Implement CAPTCHA",
                    "Notify security team",
                ],
            },
            "privilege_escalation": {
                "action": "Review and revoke unauthorized privileges",
                "auto_fixable": False,
                "steps": [
                    "Audit privilege change",
                    "Verify authorization",
                    "Revoke if unauthorized",
                    "Review access policies",
                ],
            },
            "data_exfiltration": {
                "action": "Investigate and suspend access",
                "auto_fixable": True,
                "auto_fix_command": "suspend_account",
                "steps": [
                    "Suspend user account immediately",
                    "Audit exported data",
                    "Notify data protection officer",
                    "Initiate incident response",
                ],
            },
            "hash_mismatch": {
                "action": "Restore from backup and investigate",
                "auto_fixable": False,
                "steps": [
                    "Preserve current state for forensics",
                    "Restore from verified backup",
                    "Investigate root cause",
                    "Strengthen access controls",
                ],
            },
            "unusual_time": {
                "action": "Verify legitimate access",
                "auto_fixable": False,
                "steps": [
                    "Contact user to verify",
                    "Review access patterns",
                    "Consider implementing time-based access",
                ],
            },
        }

        strategy = fix_strategies.get(
            issue_type,
            {
                "action": "Manual investigation required",
                "auto_fixable": False,
                "steps": ["Review issue details", "Consult security team"],
            },
        )

        return {
            "issue_id": issue_id,
            "issue_type": issue_type,
            "severity": issue.get("severity", "medium"),
            "description": issue.get("description", ""),
            "action": strategy["action"],
            "auto_fixable": strategy["auto_fixable"],
            "auto_fix_command": strategy.get("auto_fix_command"),
            "steps": strategy["steps"],
            "estimated_time": "5-15 minutes" if strategy["auto_fixable"] else "30-60 minutes",
        }

    async def _handle_export(self, task: TaskMessage) -> dict[str, Any]:
        """Handle audit data export task"""
        tenant_id = task.input_data.get("tenant_id")
        format_str = task.input_data.get("format", "json")
        redact_pii = task.input_data.get("redact_pii", True)
        audit_data = self._load_audit_data(task)

        format_map = {
            "json": ExportFormat.JSON,
            "jsonl": ExportFormat.JSONL,
            "csv": ExportFormat.CSV,
            "splunk": ExportFormat.SPLUNK,
            "elk": ExportFormat.ELK,
            "cef": ExportFormat.CEF,
            "syslog": ExportFormat.SYSLOG,
        }

        from tools.auto_audit.exporter import RedactionLevel

        config = ExportConfig(
            format=format_map.get(format_str, ExportFormat.JSON),
            redaction_level=RedactionLevel.STANDARD if redact_pii else RedactionLevel.NONE,
        )

        self._exporter.entries = audit_data

        # Export to string (in-memory)
        entries = self._exporter._filter_entries(tenant_id, None, None)
        if redact_pii:
            entries = [self._exporter._redact_entry(e, config.redaction_level) for e in entries]

        if format_str == "json":
            data = self._exporter._export_json(entries)
        elif format_str == "jsonl":
            data = self._exporter._export_jsonl(entries)
        elif format_str == "csv":
            data = self._exporter._export_csv(entries)
        elif format_str == "splunk":
            data = self._exporter._export_splunk(entries)
        elif format_str == "elk":
            data = self._exporter._export_elk(entries)
        elif format_str == "cef":
            data = self._exporter._export_cef(entries)
        elif format_str == "syslog":
            data = self._exporter._export_syslog(entries)
        else:
            data = self._exporter._export_json(entries)

        return {
            "success": True,
            "tenant_id": tenant_id,
            "format": format_str,
            "entries_exported": len(entries),
            "pii_redacted": redact_pii,
            "data": data[:100000],  # Limit size for response
            "truncated": len(data) > 100000,
            "export_timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_full_audit(self, task: TaskMessage) -> dict[str, Any]:
        """Handle full audit suite execution"""
        tenant_id = task.input_data.get("tenant_id")
        framework = task.input_data.get("compliance_framework", "all")
        audit_data = self._load_audit_data(task)

        # Run all analysis tools
        analysis = await self._handle_analyze(task)
        validation = await self._handle_validate(task)
        compliance = await self._handle_compliance(task)
        detection = await self._handle_detect(task)

        # Calculate overall health
        health_factors = [
            validation.get("is_valid", False),
            compliance.get("overall_score", 0) >= 70,
            detection.get("threat_score", 100) < 50,
            detection.get("critical_anomalies", 0) == 0,
        ]
        health_score = sum(health_factors) / len(health_factors) * 100

        if health_score >= 90:
            overall_health = "healthy"
        elif health_score >= 70:
            overall_health = "warning"
        elif health_score >= 50:
            overall_health = "degraded"
        else:
            overall_health = "critical"

        # Collect all recommendations
        all_recommendations = []
        if validation.get("recovery_suggestions"):
            all_recommendations.extend(validation["recovery_suggestions"])
        if compliance.get("recommendations"):
            all_recommendations.extend([{"action": r} for r in compliance["recommendations"][:10]])
        if detection.get("anomalies"):
            for anomaly in detection["anomalies"][:5]:
                if anomaly.get("recommendations"):
                    all_recommendations.extend([{"action": r} for r in anomaly["recommendations"]])

        return {
            "tenant_id": tenant_id,
            "overall_health": overall_health,
            "health_score": health_score,
            "analysis_report": {
                "total_events": analysis.get("total_events"),
                "unique_actors": analysis.get("unique_actors"),
                "risk_indicators_count": len(analysis.get("risk_indicators", [])),
            },
            "integrity_report": {
                "is_valid": validation.get("is_valid"),
                "chain_integrity": validation.get("chain_integrity"),
                "issues_found": validation.get("chain_breaks", 0)
                + validation.get("tamper_indicators", 0),
            },
            "compliance_report": {
                "framework": compliance.get("framework"),
                "overall_score": compliance.get("overall_score"),
                "risk_level": compliance.get("risk_level"),
            },
            "anomaly_report": {
                "threat_score": detection.get("threat_score"),
                "threat_level": detection.get("threat_level"),
                "anomalies_detected": detection.get("anomalies_detected"),
                "critical_anomalies": detection.get("critical_anomalies"),
            },
            "recommendations": all_recommendations[:20],
            "audit_timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_threat_score(self, task: TaskMessage) -> dict[str, Any]:
        """Handle threat score request"""
        tenant_id = task.input_data.get("tenant_id")
        audit_data = self._load_audit_data(task)

        if not audit_data:
            return {
                "tenant_id": tenant_id,
                "threat_score": 0,
                "threat_level": "unknown",
                "message": "No audit data available",
                "last_updated": datetime.now(UTC).isoformat(),
            }

        self._anomaly_detector.entries = audit_data
        report = self._anomaly_detector.detect(tenant_id=tenant_id, window_hours=24)

        return {
            "tenant_id": tenant_id,
            "threat_score": report.threat_score,
            "threat_level": report.threat_level,
            "critical_count": report.critical_anomalies,
            "high_count": report.high_anomalies,
            "last_updated": datetime.now(UTC).isoformat(),
        }

    # =========================================================================
    # Integration with Other Agents
    # =========================================================================

    async def collaborate_with_agent(
        self,
        target_agent: str,
        capability: str,
        input_data: dict,
    ) -> dict[str, Any]:
        """
        Collaborate with other SAHOOL agents

        Args:
            target_agent: Target agent ID (e.g., "field-analyst-agent")
            capability: Capability to invoke
            input_data: Input data for the capability

        Returns:
            Response from target agent
        """
        logger.info(
            "agent_collaboration_initiated",
            source_agent=self.agent_id,
            target_agent=target_agent,
            capability=capability,
        )

        # In production, this would make HTTP call to target agent
        # For now, return structure for integration
        return {
            "collaboration_id": str(uuid4()),
            "source_agent": self.agent_id,
            "target_agent": target_agent,
            "capability": capability,
            "status": "pending",
            "message": f"Collaboration request sent to {target_agent}",
        }

    async def notify_security_team(self, alert: dict) -> None:
        """Send security alert notification"""
        logger.warning(
            "security_alert",
            alert_type=alert.get("type"),
            severity=alert.get("severity"),
            description=alert.get("description"),
        )
        # In production, integrate with notification service

    async def trigger_auto_remediation(self, issue: dict, fix_command: str) -> dict:
        """Trigger automatic remediation for an issue"""
        logger.info(
            "auto_remediation_triggered",
            issue_type=issue.get("type"),
            fix_command=fix_command,
        )

        # In production, execute actual remediation
        return {
            "success": True,
            "issue_id": issue.get("id"),
            "action_taken": fix_command,
            "timestamp": datetime.now(UTC).isoformat(),
        }


# Factory function for creating agent instance
def create_audit_agent(
    task_endpoint: str | None = None,
    websocket_endpoint: str | None = None,
) -> AuditAgent:
    """
    Create and configure an Audit Agent instance

    Args:
        task_endpoint: Custom task endpoint URL
        websocket_endpoint: Optional WebSocket endpoint

    Returns:
        Configured AuditAgent instance
    """
    return AuditAgent(
        task_endpoint=task_endpoint or "https://api.sahool.app/agents/audit-agent/invoke",
        websocket_endpoint=websocket_endpoint,
    )
