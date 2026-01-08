#!/usr/bin/env python3
"""
SAHOOL Compliance Report Generator
Advanced compliance reporting for GDPR, SOC2, ISO27001, and HIPAA

Features:
- Multi-framework compliance assessment
- Evidence collection from audit logs
- Gap analysis and remediation tracking
- Automated compliance scoring
- Executive summary generation
- Audit-ready documentation

Usage:
    python -m tools.auto-audit.compliance_reporter --framework gdpr [options]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ALL = "all"


class ControlStatus(str, Enum):
    """Status of a compliance control"""

    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    NEEDS_REVIEW = "needs_review"


@dataclass
class ComplianceControl:
    """Individual compliance control assessment"""

    control_id: str
    framework: str
    title: str
    description: str
    status: ControlStatus
    evidence: list[dict] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    audit_logs_analyzed: int = 0
    last_assessed: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ComplianceCategory:
    """Category grouping related controls"""

    name: str
    description: str
    controls: list[ComplianceControl] = field(default_factory=list)
    compliance_score: float = 0.0


@dataclass
class ComplianceReport:
    """Complete compliance assessment report"""

    framework: str
    tenant_id: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assessment_period: tuple[datetime, datetime] | None = None

    # Overall scores
    overall_score: float = 0.0
    risk_level: str = "unknown"  # low, medium, high, critical

    # Categories and controls
    categories: list[ComplianceCategory] = field(default_factory=list)

    # Summary statistics
    total_controls: int = 0
    compliant_controls: int = 0
    partial_controls: int = 0
    non_compliant_controls: int = 0

    # Key findings
    critical_findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Evidence summary
    total_audit_logs: int = 0
    evidence_items: int = 0

    # Executive summary
    executive_summary: str = ""


class ComplianceReporter:
    """
    Comprehensive compliance assessment and reporting engine.

    Supports multiple frameworks: GDPR, SOC2, ISO27001, HIPAA, PCI-DSS
    """

    # GDPR Article mappings to audit actions
    GDPR_MAPPINGS = {
        "article_5": {
            "title": "Principles of Processing",
            "actions": ["data.process", "data.collect", "consent.*"],
            "requirements": [
                "Lawfulness of processing",
                "Purpose limitation",
                "Data minimization",
            ],
        },
        "article_6": {
            "title": "Lawfulness of Processing",
            "actions": ["consent.grant", "consent.withdraw", "legal_basis.*"],
            "requirements": ["Documented legal basis for processing"],
        },
        "article_15": {
            "title": "Right of Access",
            "actions": ["data.export", "data.access_request", "subject_access.*"],
            "requirements": ["Subject access request handling", "Data export capability"],
        },
        "article_17": {
            "title": "Right to Erasure",
            "actions": ["data.delete", "data.erasure", "user.delete"],
            "requirements": ["Data deletion capability", "Erasure request handling"],
        },
        "article_20": {
            "title": "Right to Data Portability",
            "actions": ["data.export", "data.portability"],
            "requirements": ["Machine-readable export format"],
        },
        "article_25": {
            "title": "Data Protection by Design",
            "actions": ["config.privacy.*", "encryption.*"],
            "requirements": ["Privacy by default settings"],
        },
        "article_30": {
            "title": "Records of Processing",
            "actions": ["audit.*", "processing_record.*"],
            "requirements": ["Processing activity records", "Audit trail maintenance"],
        },
        "article_32": {
            "title": "Security of Processing",
            "actions": ["security.*", "access_control.*", "encryption.*"],
            "requirements": ["Appropriate security measures"],
        },
        "article_33": {
            "title": "Breach Notification",
            "actions": ["breach.*", "incident.*", "notification.*"],
            "requirements": ["72-hour breach notification capability"],
        },
    }

    # SOC2 Trust Service Criteria mappings
    SOC2_MAPPINGS = {
        "CC1": {
            "title": "Control Environment",
            "subcriteria": {
                "CC1.1": "Management oversight",
                "CC1.2": "Board independence",
                "CC1.3": "Authority and responsibility",
                "CC1.4": "HR policies",
            },
        },
        "CC2": {
            "title": "Communication and Information",
            "subcriteria": {
                "CC2.1": "Internal communication",
                "CC2.2": "External communication",
            },
        },
        "CC3": {
            "title": "Risk Assessment",
            "subcriteria": {
                "CC3.1": "Risk identification",
                "CC3.2": "Risk analysis",
                "CC3.3": "Fraud risk",
            },
        },
        "CC5": {
            "title": "Control Activities",
            "subcriteria": {
                "CC5.1": "Selection of controls",
                "CC5.2": "Technology controls",
            },
        },
        "CC6": {
            "title": "Logical and Physical Access Controls",
            "subcriteria": {
                "CC6.1": "Logical access security",
                "CC6.2": "Access provisioning/deprovisioning",
                "CC6.3": "Role-based access",
                "CC6.6": "Encryption",
                "CC6.7": "Physical access",
            },
            "actions": ["user.login", "user.logout", "permission.*", "role.*", "access.*"],
        },
        "CC7": {
            "title": "System Operations",
            "subcriteria": {
                "CC7.1": "Configuration management",
                "CC7.2": "Change management",
                "CC7.3": "Incident management",
            },
            "actions": ["config.*", "change.*", "incident.*", "deploy.*"],
        },
        "CC8": {
            "title": "Change Management",
            "subcriteria": {
                "CC8.1": "Infrastructure changes",
            },
            "actions": ["deploy.*", "migration.*", "upgrade.*"],
        },
        "CC9": {
            "title": "Risk Mitigation",
            "subcriteria": {
                "CC9.1": "Business continuity",
                "CC9.2": "Vendor management",
            },
        },
    }

    # ISO 27001 Annex A controls
    ISO27001_MAPPINGS = {
        "A.5": {
            "title": "Information Security Policies",
            "controls": ["A.5.1.1", "A.5.1.2"],
        },
        "A.6": {
            "title": "Organization of Information Security",
            "controls": ["A.6.1.1", "A.6.1.2", "A.6.2.1", "A.6.2.2"],
        },
        "A.9": {
            "title": "Access Control",
            "controls": ["A.9.1.1", "A.9.2.1", "A.9.2.2", "A.9.2.3", "A.9.4.1"],
            "actions": ["user.*", "permission.*", "role.*", "access.*"],
        },
        "A.10": {
            "title": "Cryptography",
            "controls": ["A.10.1.1", "A.10.1.2"],
            "actions": ["encryption.*", "key.*", "certificate.*"],
        },
        "A.12": {
            "title": "Operations Security",
            "controls": ["A.12.1.1", "A.12.4.1", "A.12.4.2", "A.12.4.3"],
            "actions": ["audit.*", "log.*", "monitor.*", "backup.*"],
        },
        "A.16": {
            "title": "Information Security Incident Management",
            "controls": ["A.16.1.1", "A.16.1.2", "A.16.1.4", "A.16.1.5"],
            "actions": ["incident.*", "breach.*", "alert.*"],
        },
        "A.18": {
            "title": "Compliance",
            "controls": ["A.18.1.1", "A.18.1.3", "A.18.2.1"],
        },
    }

    def __init__(self, entries: list[dict] | None = None):
        """
        Initialize compliance reporter.

        Args:
            entries: List of audit log entries for evidence collection
        """
        self.entries = entries or []
        self._action_cache: dict[str, list[dict]] = {}
        self._build_action_cache()

    def _build_action_cache(self) -> None:
        """Build cache of entries by action prefix"""
        self._action_cache.clear()
        for entry in self.entries:
            action = entry.get("action", "")
            prefix = action.split(".")[0] if "." in action else action
            if prefix not in self._action_cache:
                self._action_cache[prefix] = []
            self._action_cache[prefix].append(entry)

    def load_from_file(self, file_path: Path) -> None:
        """Load audit entries from JSON file"""
        with open(file_path) as f:
            self.entries = json.load(f)
        self._build_action_cache()

    def generate_report(
        self,
        framework: ComplianceFramework,
        tenant_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> ComplianceReport:
        """
        Generate compliance report for specified framework.

        Args:
            framework: Compliance framework to assess
            tenant_id: Tenant identifier
            start_date: Start of assessment period
            end_date: End of assessment period

        Returns:
            Complete ComplianceReport
        """
        # Filter entries by period
        entries = self._filter_entries(tenant_id, start_date, end_date)

        report = ComplianceReport(
            framework=framework.value,
            tenant_id=tenant_id,
            assessment_period=(
                start_date or datetime.now(UTC) - timedelta(days=90),
                end_date or datetime.now(UTC),
            ),
            total_audit_logs=len(entries),
        )

        # Generate framework-specific assessment
        if framework == ComplianceFramework.GDPR:
            self._assess_gdpr(report, entries)
        elif framework == ComplianceFramework.SOC2:
            self._assess_soc2(report, entries)
        elif framework == ComplianceFramework.ISO27001:
            self._assess_iso27001(report, entries)
        elif framework == ComplianceFramework.ALL:
            self._assess_gdpr(report, entries)
            self._assess_soc2(report, entries)
            self._assess_iso27001(report, entries)

        # Calculate overall statistics
        self._calculate_statistics(report)

        # Generate executive summary
        report.executive_summary = self._generate_executive_summary(report)

        return report

    def _filter_entries(
        self,
        tenant_id: str,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[dict]:
        """Filter entries by tenant and date range"""
        entries = [e for e in self.entries if e.get("tenant_id") == tenant_id]

        if start_date or end_date:
            filtered = []
            for entry in entries:
                ts_str = entry.get("created_at", "")
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if start_date and ts < start_date:
                            continue
                        if end_date and ts > end_date:
                            continue
                        filtered.append(entry)
                    except ValueError:
                        pass
            entries = filtered

        return entries

    def _find_evidence(self, entries: list[dict], action_patterns: list[str]) -> list[dict]:
        """Find audit entries matching action patterns"""
        evidence = []

        for entry in entries:
            action = entry.get("action", "")
            for pattern in action_patterns:
                if pattern.endswith("*"):
                    prefix = pattern[:-1]
                    if action.startswith(prefix):
                        evidence.append(
                            {
                                "action": action,
                                "actor": entry.get("actor_id"),
                                "resource": f"{entry.get('resource_type')}/{entry.get('resource_id')}",
                                "timestamp": entry.get("created_at"),
                            }
                        )
                        break
                elif action == pattern:
                    evidence.append(
                        {
                            "action": action,
                            "actor": entry.get("actor_id"),
                            "resource": f"{entry.get('resource_type')}/{entry.get('resource_id')}",
                            "timestamp": entry.get("created_at"),
                        }
                    )
                    break

        return evidence

    def _assess_gdpr(self, report: ComplianceReport, entries: list[dict]) -> None:
        """Assess GDPR compliance"""
        category = ComplianceCategory(
            name="GDPR - General Data Protection Regulation",
            description="EU data protection and privacy regulation",
        )

        for article_id, mapping in self.GDPR_MAPPINGS.items():
            actions = mapping.get("actions", [])
            evidence = self._find_evidence(entries, actions)

            # Determine compliance status
            if evidence:
                if len(evidence) >= 5:
                    status = ControlStatus.COMPLIANT
                else:
                    status = ControlStatus.PARTIAL
            else:
                # Check if we have any related infrastructure
                status = ControlStatus.NEEDS_REVIEW

            control = ComplianceControl(
                control_id=article_id.upper().replace("_", " "),
                framework="GDPR",
                title=mapping["title"],
                description=", ".join(mapping.get("requirements", [])),
                status=status,
                evidence=evidence[:10],  # Limit evidence items
                audit_logs_analyzed=len(evidence),
            )

            # Add findings and recommendations
            if status == ControlStatus.NON_COMPLIANT:
                control.findings.append(f"No evidence found for {mapping['title']}")
                control.recommendations.append(
                    f"Implement {mapping['title']} controls and ensure audit logging"
                )
            elif status == ControlStatus.PARTIAL:
                control.findings.append(f"Limited evidence for {mapping['title']}")
                control.recommendations.append(
                    f"Enhance {mapping['title']} implementation and audit coverage"
                )

            category.controls.append(control)

        report.categories.append(category)

    def _assess_soc2(self, report: ComplianceReport, entries: list[dict]) -> None:
        """Assess SOC 2 compliance"""
        category = ComplianceCategory(
            name="SOC 2 Type II",
            description="Service Organization Control 2 - Trust Service Criteria",
        )

        for criteria_id, mapping in self.SOC2_MAPPINGS.items():
            actions = mapping.get("actions", [])
            evidence = self._find_evidence(entries, actions) if actions else []

            # For SOC2, we need more evidence
            if len(evidence) >= 20:
                status = ControlStatus.COMPLIANT
            elif len(evidence) >= 5:
                status = ControlStatus.PARTIAL
            elif actions:
                status = ControlStatus.NON_COMPLIANT
            else:
                status = ControlStatus.NEEDS_REVIEW

            control = ComplianceControl(
                control_id=criteria_id,
                framework="SOC2",
                title=mapping["title"],
                description=", ".join(mapping.get("subcriteria", {}).values()),
                status=status,
                evidence=evidence[:10],
                audit_logs_analyzed=len(evidence),
            )

            if status != ControlStatus.COMPLIANT:
                control.recommendations.append(
                    f"Review {criteria_id} - {mapping['title']} implementation"
                )

            category.controls.append(control)

        report.categories.append(category)

    def _assess_iso27001(self, report: ComplianceReport, entries: list[dict]) -> None:
        """Assess ISO 27001 compliance"""
        category = ComplianceCategory(
            name="ISO 27001:2022",
            description="Information Security Management System (ISMS)",
        )

        for annex_id, mapping in self.ISO27001_MAPPINGS.items():
            actions = mapping.get("actions", [])
            evidence = self._find_evidence(entries, actions) if actions else []

            if len(evidence) >= 10:
                status = ControlStatus.COMPLIANT
            elif len(evidence) >= 3:
                status = ControlStatus.PARTIAL
            elif actions:
                status = ControlStatus.NON_COMPLIANT
            else:
                status = ControlStatus.NEEDS_REVIEW

            controls_list = mapping.get("controls", [])
            control = ComplianceControl(
                control_id=annex_id,
                framework="ISO27001",
                title=mapping["title"],
                description=f"Controls: {', '.join(controls_list)}" if controls_list else "",
                status=status,
                evidence=evidence[:10],
                audit_logs_analyzed=len(evidence),
            )

            if status != ControlStatus.COMPLIANT:
                control.recommendations.append(
                    f"Implement {annex_id} - {mapping['title']} controls"
                )

            category.controls.append(control)

        report.categories.append(category)

    def _calculate_statistics(self, report: ComplianceReport) -> None:
        """Calculate overall compliance statistics"""
        all_controls = []
        for category in report.categories:
            all_controls.extend(category.controls)
            # Calculate category score
            compliant = sum(1 for c in category.controls if c.status == ControlStatus.COMPLIANT)
            partial = sum(1 for c in category.controls if c.status == ControlStatus.PARTIAL)
            total = len([c for c in category.controls if c.status != ControlStatus.NOT_APPLICABLE])
            if total > 0:
                category.compliance_score = round((compliant + partial * 0.5) / total * 100, 1)

        report.total_controls = len(all_controls)
        report.compliant_controls = sum(
            1 for c in all_controls if c.status == ControlStatus.COMPLIANT
        )
        report.partial_controls = sum(1 for c in all_controls if c.status == ControlStatus.PARTIAL)
        report.non_compliant_controls = sum(
            1 for c in all_controls if c.status == ControlStatus.NON_COMPLIANT
        )

        # Calculate overall score
        applicable = [c for c in all_controls if c.status != ControlStatus.NOT_APPLICABLE]
        if applicable:
            score = (
                (report.compliant_controls + report.partial_controls * 0.5) / len(applicable) * 100
            )
            report.overall_score = round(score, 1)

        # Determine risk level
        if report.overall_score >= 90:
            report.risk_level = "low"
        elif report.overall_score >= 70:
            report.risk_level = "medium"
        elif report.overall_score >= 50:
            report.risk_level = "high"
        else:
            report.risk_level = "critical"

        # Collect evidence count
        report.evidence_items = sum(len(c.evidence) for c in all_controls)

        # Collect critical findings
        for control in all_controls:
            if control.status == ControlStatus.NON_COMPLIANT:
                for finding in control.findings:
                    report.critical_findings.append(f"[{control.control_id}] {finding}")
            report.recommendations.extend(control.recommendations)

    def _generate_executive_summary(self, report: ComplianceReport) -> str:
        """Generate executive summary"""
        summary_parts = [
            f"This compliance assessment evaluated {report.total_controls} controls "
            f"under the {report.framework.upper()} framework.",
            "",
            f"Overall Compliance Score: {report.overall_score}% ({report.risk_level.upper()} risk)",
            "",
            f"- Compliant: {report.compliant_controls} controls",
            f"- Partially Compliant: {report.partial_controls} controls",
            f"- Non-Compliant: {report.non_compliant_controls} controls",
            "",
            f"Assessment based on {report.total_audit_logs:,} audit log entries "
            f"with {report.evidence_items} evidence items collected.",
        ]

        if report.critical_findings:
            summary_parts.extend(
                [
                    "",
                    f"Critical Findings: {len(report.critical_findings)} items require immediate attention.",
                ]
            )

        return "\n".join(summary_parts)


def generate_markdown_report(report: ComplianceReport) -> str:
    """Generate markdown compliance report"""
    risk_icons = {
        "low": "LOW",
        "medium": "MEDIUM",
        "high": "HIGH",
        "critical": "CRITICAL",
    }

    lines = [
        f"# {report.framework.upper()} Compliance Report",
        "",
        f"> Generated: {report.generated_at.isoformat()}",
        f"> Tenant: {report.tenant_id}",
        f"> Assessment Period: {report.assessment_period[0].strftime('%Y-%m-%d')} to "
        f"{report.assessment_period[1].strftime('%Y-%m-%d')}"
        if report.assessment_period
        else "",
        "",
        "## Executive Summary",
        "",
        report.executive_summary,
        "",
        "## Compliance Score",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Overall Score | **{report.overall_score}%** |",
        f"| Risk Level | {risk_icons.get(report.risk_level, report.risk_level)} |",
        f"| Total Controls | {report.total_controls} |",
        f"| Compliant | {report.compliant_controls} |",
        f"| Partial | {report.partial_controls} |",
        f"| Non-Compliant | {report.non_compliant_controls} |",
        "",
    ]

    # Category details
    for category in report.categories:
        lines.extend(
            [
                f"## {category.name}",
                "",
                f"*{category.description}*",
                "",
                f"**Category Score: {category.compliance_score}%**",
                "",
                "| Control | Status | Evidence | Findings |",
                "|---------|--------|----------|----------|",
            ]
        )

        status_icons = {
            ControlStatus.COMPLIANT: "PASS",
            ControlStatus.PARTIAL: "PARTIAL",
            ControlStatus.NON_COMPLIANT: "FAIL",
            ControlStatus.NEEDS_REVIEW: "REVIEW",
            ControlStatus.NOT_APPLICABLE: "N/A",
        }

        for control in category.controls:
            status = status_icons.get(control.status, "?")
            findings = "; ".join(control.findings[:2]) if control.findings else "-"
            lines.append(
                f"| {control.control_id}: {control.title} | {status} | "
                f"{control.audit_logs_analyzed} | {findings} |"
            )

        lines.append("")

    # Critical Findings
    if report.critical_findings:
        lines.extend(
            [
                "## Critical Findings",
                "",
            ]
        )
        for finding in report.critical_findings[:20]:
            lines.append(f"- {finding}")
        lines.append("")

    # Recommendations
    if report.recommendations:
        lines.extend(
            [
                "## Recommendations",
                "",
            ]
        )
        seen = set()
        for rec in report.recommendations[:30]:
            if rec not in seen:
                lines.append(f"- {rec}")
                seen.add(rec)
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "*Report generated by SAHOOL Auto Audit Tools*",
            "",
            "**Disclaimer**: This automated assessment provides guidance based on "
            "audit log analysis. A formal compliance audit by qualified auditors "
            "is recommended for certification purposes.",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate compliance reports")
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
        help="Tenant ID to assess",
    )
    parser.add_argument(
        "--framework",
        "-f",
        choices=["gdpr", "soc2", "iso27001", "all"],
        default="all",
        help="Compliance framework to assess",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="compliance_report.md",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()

    # Load and assess
    reporter = ComplianceReporter()
    reporter.load_from_file(Path(args.input))

    framework_map = {
        "gdpr": ComplianceFramework.GDPR,
        "soc2": ComplianceFramework.SOC2,
        "iso27001": ComplianceFramework.ISO27001,
        "all": ComplianceFramework.ALL,
    }

    report = reporter.generate_report(
        framework=framework_map[args.framework],
        tenant_id=args.tenant_id,
    )

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "framework": report.framework,
                "tenant_id": report.tenant_id,
                "generated_at": report.generated_at.isoformat(),
                "overall_score": report.overall_score,
                "risk_level": report.risk_level,
                "total_controls": report.total_controls,
                "compliant": report.compliant_controls,
                "partial": report.partial_controls,
                "non_compliant": report.non_compliant_controls,
                "categories": [
                    {
                        "name": cat.name,
                        "score": cat.compliance_score,
                        "controls": [
                            {
                                "id": c.control_id,
                                "title": c.title,
                                "status": c.status.value,
                                "evidence_count": c.audit_logs_analyzed,
                            }
                            for c in cat.controls
                        ],
                    }
                    for cat in report.categories
                ],
                "critical_findings": report.critical_findings,
                "recommendations": report.recommendations[:30],
            },
            indent=2,
        )
    else:
        output = generate_markdown_report(report)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(output)

    print(f"Compliance Report: {report.framework.upper()}")
    print(f"  Overall Score: {report.overall_score}%")
    print(f"  Risk Level: {report.risk_level.upper()}")
    print(f"  Controls: {report.compliant_controls}/{report.total_controls} compliant")
    print(f"  Report: {output_path}")


if __name__ == "__main__":
    main()
