#!/usr/bin/env python3
"""
SAHOOL Auto Audit Tools - Main CLI Entry Point
Unified command-line interface for all audit tools

Usage:
    python -m tools.auto-audit <command> [options]

Commands:
    analyze     - Analyze audit logs for patterns and statistics
    validate    - Verify hash chain integrity
    compliance  - Generate compliance reports (GDPR, SOC2, ISO27001)
    detect      - Detect anomalies and threats
    export      - Export audit data in various formats
    dashboard   - Interactive audit dashboard
    full-audit  - Run complete audit analysis suite

Examples:
    python -m tools.auto-audit analyze -i logs.json -t tenant-123
    python -m tools.auto-audit validate -i logs.json --recovery
    python -m tools.auto-audit compliance -i logs.json -f gdpr
    python -m tools.auto-audit detect -i logs.json -t tenant-123
    python -m tools.auto-audit export -i logs.json -f csv -o audit.csv
    python -m tools.auto-audit full-audit -i logs.json -t tenant-123 -o reports/
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def print_banner():
    """Print tool banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║           SAHOOL Auto Audit Tools v1.0.0                      ║
║     Comprehensive Audit Log Analysis & Compliance Suite       ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_analyze(args: argparse.Namespace) -> int:
    """Run audit log analyzer"""
    from .analyzer import AuditLogAnalyzer, generate_markdown_report

    print(f"Loading audit logs from: {args.input}")
    analyzer = AuditLogAnalyzer()
    analyzer.load_from_file(Path(args.input))

    print(f"Analyzing {len(analyzer.entries):,} entries...")
    report = analyzer.analyze(tenant_id=args.tenant_id)

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "tenant_id": report.tenant_id,
                "generated_at": report.generated_at.isoformat(),
                "total_events": report.total_events,
                "unique_actors": report.unique_actors,
                "unique_resources": report.unique_resources,
                "unique_actions": report.unique_actions,
                "action_distribution": report.action_distribution,
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)

    print(f"\n Analysis Complete")
    print(f"  Total events: {report.total_events:,}")
    print(f"  Unique actors: {report.unique_actors:,}")
    print(f"  Risk indicators: {len(report.risk_indicators)}")
    print(f"  Anomalies: {len(report.anomalies)}")
    print(f"  Report: {output_path}")

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Run hash chain validator"""
    from .hashchain_validator import (
        HashChainValidator,
        generate_markdown_report,
    )

    print(f"Loading audit logs from: {args.input}")
    validator = HashChainValidator()
    validator.load_from_file(Path(args.input))

    print(f"Validating hash chain for {len(validator.entries):,} entries...")
    report = validator.validate(tenant_id=args.tenant_id)

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "tenant_id": report.tenant_id,
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
                    for e in report.errors
                ],
            },
            indent=2,
        )
    else:
        output = generate_markdown_report(report)
        if args.recovery and not report.is_valid:
            output += "\n\n" + validator.generate_recovery_report(report)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)

    status = "VALID" if report.is_valid else "INTEGRITY ISSUES"
    print(f"\n Hash Chain Validation: {status}")
    print(f"  Integrity: {report.chain_integrity}%")
    print(f"  Entries validated: {report.validated_entries:,}")
    print(f"  Errors: {len(report.errors)}")
    print(f"  Report: {output_path}")

    return 0 if report.is_valid else 1


def cmd_compliance(args: argparse.Namespace) -> int:
    """Run compliance reporter"""
    from .compliance_reporter import (
        ComplianceFramework,
        ComplianceReporter,
        generate_markdown_report,
    )

    print(f"Loading audit logs from: {args.input}")
    reporter = ComplianceReporter()
    reporter.load_from_file(Path(args.input))

    framework_map = {
        "gdpr": ComplianceFramework.GDPR,
        "soc2": ComplianceFramework.SOC2,
        "iso27001": ComplianceFramework.ISO27001,
        "all": ComplianceFramework.ALL,
    }

    print(f"Generating {args.framework.upper()} compliance report...")
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
                "overall_score": report.overall_score,
                "risk_level": report.risk_level,
                "total_controls": report.total_controls,
                "compliant": report.compliant_controls,
                "partial": report.partial_controls,
                "non_compliant": report.non_compliant_controls,
                "critical_findings": report.critical_findings,
                "recommendations": report.recommendations[:30],
            },
            indent=2,
        )
    else:
        output = generate_markdown_report(report)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)

    print(f"\n Compliance Report: {report.framework.upper()}")
    print(f"  Overall Score: {report.overall_score}%")
    print(f"  Risk Level: {report.risk_level.upper()}")
    print(f"  Controls: {report.compliant_controls}/{report.total_controls} compliant")
    print(f"  Report: {output_path}")

    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    """Run anomaly detector"""
    from .anomaly_detector import AuditAnomalyDetector, generate_markdown_report

    print(f"Loading audit logs from: {args.input}")
    detector = AuditAnomalyDetector()
    detector.load_from_file(Path(args.input))

    print(f"Building baselines and detecting anomalies...")
    report = detector.detect(
        tenant_id=args.tenant_id,
        window_hours=args.window,
    )

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "tenant_id": report.tenant_id,
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)

    print(f"\n Anomaly Detection Complete")
    print(f"  Threat Score: {report.threat_score:.1f}/100 ({report.threat_level.upper()})")
    print(f"  Anomalies: {report.anomalies_detected}")
    print(f"  Critical: {report.critical_anomalies}")
    print(f"  High: {report.high_anomalies}")
    print(f"  Report: {output_path}")

    return 1 if report.critical_anomalies > 0 else 0


def cmd_export(args: argparse.Namespace) -> int:
    """Run audit data exporter"""
    from .exporter import (
        AuditDataExporter,
        ExportConfig,
        ExportFormat,
        RedactionLevel,
    )

    format_map = {
        "json": ExportFormat.JSON,
        "jsonl": ExportFormat.JSONL,
        "csv": ExportFormat.CSV,
        "splunk": ExportFormat.SPLUNK,
        "elk": ExportFormat.ELK,
        "cef": ExportFormat.CEF,
        "syslog": ExportFormat.SYSLOG,
    }

    redact_map = {
        "none": RedactionLevel.NONE,
        "basic": RedactionLevel.BASIC,
        "standard": RedactionLevel.STANDARD,
        "strict": RedactionLevel.STRICT,
    }

    config = ExportConfig(
        format=format_map[args.format],
        redaction_level=redact_map[args.redact],
        compress=args.compress,
        flatten_json=args.flatten,
        include_hash_chain=not args.no_hash_chain,
    )

    print(f"Loading audit logs from: {args.input}")
    exporter = AuditDataExporter()
    exporter.load_from_file(Path(args.input))

    print(f"Exporting {len(exporter.entries):,} entries to {args.format.upper()}...")
    result = exporter.export(
        output_path=Path(args.output),
        config=config,
        tenant_id=args.tenant_id,
    )

    if result.success:
        print(f"\n Export Complete: {result.format.upper()}")
        print(f"  Entries: {result.entries_exported:,}")
        print(f"  Size: {result.file_size_bytes:,} bytes")
        print(f"  Compressed: {result.compressed}")
        print(f"  Duration: {result.duration_ms:.2f}ms")
        print(f"  Output: {result.output_path}")
        return 0
    else:
        print(f" Export Failed: {', '.join(result.errors)}")
        return 1


def cmd_full_audit(args: argparse.Namespace) -> int:
    """Run complete audit analysis suite"""
    from .analyzer import AuditLogAnalyzer, generate_markdown_report as analyze_md
    from .anomaly_detector import (
        AuditAnomalyDetector,
        generate_markdown_report as detect_md,
    )
    from .compliance_reporter import (
        ComplianceFramework,
        ComplianceReporter,
        generate_markdown_report as compliance_md,
    )
    from .hashchain_validator import (
        HashChainValidator,
        generate_markdown_report as validate_md,
    )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading audit logs from: {args.input}")

    # Load entries once
    with open(args.input) as f:
        entries = json.load(f)

    print(f"Running full audit suite on {len(entries):,} entries...\n")

    results = []
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # 1. Hash Chain Validation
    print("1/4 Validating hash chain integrity...")
    validator = HashChainValidator(entries)
    validate_report = validator.validate(tenant_id=args.tenant_id)
    validate_output = output_dir / f"01_hashchain_validation_{timestamp}.md"
    validate_output.write_text(validate_md(validate_report))
    results.append(
        {
            "tool": "Hash Chain Validator",
            "status": "PASSED" if validate_report.is_valid else "FAILED",
            "details": f"Integrity: {validate_report.chain_integrity}%",
        }
    )
    print(
        f"   {'VALID' if validate_report.is_valid else 'ISSUES'} - "
        f"Integrity: {validate_report.chain_integrity}%"
    )

    # 2. Audit Log Analysis
    print("2/4 Analyzing audit logs...")
    analyzer = AuditLogAnalyzer(entries)
    analyze_report = analyzer.analyze(tenant_id=args.tenant_id)
    analyze_output = output_dir / f"02_analysis_report_{timestamp}.md"
    analyze_output.write_text(analyze_md(analyze_report))
    results.append(
        {
            "tool": "Audit Log Analyzer",
            "status": "COMPLETED",
            "details": f"Events: {analyze_report.total_events:,}, "
            f"Risks: {len(analyze_report.risk_indicators)}",
        }
    )
    print(
        f"   Events: {analyze_report.total_events:,}, "
        f"Risk indicators: {len(analyze_report.risk_indicators)}"
    )

    # 3. Compliance Assessment
    print("3/4 Generating compliance reports...")
    reporter = ComplianceReporter(entries)
    compliance_report = reporter.generate_report(
        framework=ComplianceFramework.ALL,
        tenant_id=args.tenant_id,
    )
    compliance_output = output_dir / f"03_compliance_report_{timestamp}.md"
    compliance_output.write_text(compliance_md(compliance_report))
    results.append(
        {
            "tool": "Compliance Reporter",
            "status": compliance_report.risk_level.upper(),
            "details": f"Score: {compliance_report.overall_score}%",
        }
    )
    print(
        f"   Score: {compliance_report.overall_score}% "
        f"({compliance_report.risk_level.upper()})"
    )

    # 4. Anomaly Detection
    print("4/4 Detecting anomalies...")
    detector = AuditAnomalyDetector(entries)
    detect_report = detector.detect(tenant_id=args.tenant_id)
    detect_output = output_dir / f"04_anomaly_report_{timestamp}.md"
    detect_output.write_text(detect_md(detect_report))
    results.append(
        {
            "tool": "Anomaly Detector",
            "status": detect_report.threat_level.upper(),
            "details": f"Score: {detect_report.threat_score:.1f}/100, "
            f"Anomalies: {detect_report.anomalies_detected}",
        }
    )
    print(
        f"   Threat: {detect_report.threat_score:.1f}/100 "
        f"({detect_report.threat_level.upper()}), "
        f"Anomalies: {detect_report.anomalies_detected}"
    )

    # Generate summary report
    summary_lines = [
        "# SAHOOL Full Audit Report",
        "",
        f"> Generated: {datetime.now(UTC).isoformat()}",
        f"> Tenant: {args.tenant_id}",
        f"> Entries Analyzed: {len(entries):,}",
        "",
        "## Executive Summary",
        "",
        "| Component | Status | Details |",
        "|-----------|--------|---------|",
    ]

    for result in results:
        summary_lines.append(
            f"| {result['tool']} | {result['status']} | {result['details']} |"
        )

    summary_lines.extend(
        [
            "",
            "## Overall Assessment",
            "",
            f"- **Chain Integrity**: {validate_report.chain_integrity}%",
            f"- **Compliance Score**: {compliance_report.overall_score}%",
            f"- **Threat Score**: {detect_report.threat_score:.1f}/100",
            f"- **Risk Indicators**: {len(analyze_report.risk_indicators)}",
            f"- **Critical Anomalies**: {detect_report.critical_anomalies}",
            "",
            "## Generated Reports",
            "",
            f"1. {validate_output.name}",
            f"2. {analyze_output.name}",
            f"3. {compliance_output.name}",
            f"4. {detect_output.name}",
            "",
            "---",
            "",
            "*Full audit completed by SAHOOL Auto Audit Tools*",
        ]
    )

    summary_output = output_dir / f"00_audit_summary_{timestamp}.md"
    summary_output.write_text("\n".join(summary_lines))

    print(f"\n Full Audit Complete")
    print(f"  Reports generated: 5")
    print(f"  Output directory: {output_dir}")
    print(f"  Summary: {summary_output.name}")

    # Return non-zero if critical issues found
    if detect_report.critical_anomalies > 0 or not validate_report.is_valid:
        return 1
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="sahool-audit",
        description="SAHOOL Auto Audit Tools - Comprehensive Audit Analysis Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze -i logs.json -t tenant-123
  %(prog)s validate -i logs.json --recovery
  %(prog)s compliance -i logs.json -f gdpr -t tenant-123
  %(prog)s detect -i logs.json -t tenant-123 -w 48
  %(prog)s export -i logs.json -f csv -o audit.csv
  %(prog)s full-audit -i logs.json -t tenant-123 -o reports/
        """,
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="SAHOOL Auto Audit Tools v1.0.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze audit logs for patterns and statistics"
    )
    analyze_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file"
    )
    analyze_parser.add_argument("--tenant-id", "-t", help="Filter by tenant ID")
    analyze_parser.add_argument(
        "--output", "-o", default="audit_analysis.md", help="Output file"
    )
    analyze_parser.add_argument(
        "--format", "-f", choices=["markdown", "json"], default="markdown"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Verify hash chain integrity"
    )
    validate_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file"
    )
    validate_parser.add_argument("--tenant-id", "-t", help="Filter by tenant ID")
    validate_parser.add_argument(
        "--output", "-o", default="hashchain_validation.md", help="Output file"
    )
    validate_parser.add_argument(
        "--format", "-f", choices=["markdown", "json"], default="markdown"
    )
    validate_parser.add_argument(
        "--recovery", "-r", action="store_true", help="Generate recovery report"
    )

    # Compliance command
    compliance_parser = subparsers.add_parser(
        "compliance", help="Generate compliance reports"
    )
    compliance_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file"
    )
    compliance_parser.add_argument(
        "--tenant-id", "-t", required=True, help="Tenant ID"
    )
    compliance_parser.add_argument(
        "--framework",
        "-f",
        choices=["gdpr", "soc2", "iso27001", "all"],
        default="all",
        help="Compliance framework",
    )
    compliance_parser.add_argument(
        "--output", "-o", default="compliance_report.md", help="Output file"
    )
    compliance_parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )

    # Detect command
    detect_parser = subparsers.add_parser(
        "detect", help="Detect anomalies and threats"
    )
    detect_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file"
    )
    detect_parser.add_argument(
        "--tenant-id", "-t", required=True, help="Tenant ID"
    )
    detect_parser.add_argument(
        "--output", "-o", default="anomaly_report.md", help="Output file"
    )
    detect_parser.add_argument(
        "--format", "-f", choices=["markdown", "json"], default="markdown"
    )
    detect_parser.add_argument(
        "--window", "-w", type=int, default=24, help="Analysis window (hours)"
    )

    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export audit data in various formats"
    )
    export_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file"
    )
    export_parser.add_argument(
        "--output", "-o", required=True, help="Output file"
    )
    export_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "jsonl", "csv", "splunk", "elk", "cef", "syslog"],
        default="json",
        help="Export format",
    )
    export_parser.add_argument("--tenant-id", "-t", help="Filter by tenant ID")
    export_parser.add_argument(
        "--redact",
        "-r",
        choices=["none", "basic", "standard", "strict"],
        default="standard",
        help="PII redaction level",
    )
    export_parser.add_argument(
        "--compress", "-c", action="store_true", help="Compress output"
    )
    export_parser.add_argument(
        "--flatten", action="store_true", help="Flatten nested JSON"
    )
    export_parser.add_argument(
        "--no-hash-chain", action="store_true", help="Exclude hash chain"
    )

    # Full audit command
    full_parser = subparsers.add_parser(
        "full-audit", help="Run complete audit analysis suite"
    )
    full_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file"
    )
    full_parser.add_argument(
        "--tenant-id", "-t", required=True, help="Tenant ID"
    )
    full_parser.add_argument(
        "--output", "-o", default="audit_reports", help="Output directory"
    )

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    print_banner()

    # Route to command handler
    handlers = {
        "analyze": cmd_analyze,
        "validate": cmd_validate,
        "compliance": cmd_compliance,
        "detect": cmd_detect,
        "export": cmd_export,
        "full-audit": cmd_full_audit,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
