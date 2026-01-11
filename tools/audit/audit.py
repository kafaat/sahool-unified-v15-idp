#!/usr/bin/env python3
"""
SAHOOL Audit Engine
====================
Comprehensive audit framework for SAHOOL agricultural platform.

Usage:
    python tools/audit/audit.py --repo . --format markdown
    python tools/audit/audit.py --repo . --format json --output report.json
"""

import argparse
import io
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

# Fix encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rules import (
    build_rules,
    connectivity_rules,
    geo_ndvi_rules,
    observability_rules,
    performance_rules,
    runtime_rules,
    security_rules,
)
from reporters import json_report, markdown_report


def load_config(config_path: Path) -> dict:
    """Load audit configuration"""
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_audit(repo_root: Path, config: dict) -> dict:
    """Run all audit rules and collect findings"""
    findings = []
    stats = {
        "total_checks": 0,
        "passed": 0,
        "failed": 0,
        "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "by_category": {},
    }

    # Define rule modules
    rule_modules = {
        "build": build_rules,
        "runtime": runtime_rules,
        "connectivity": connectivity_rules,
        "geo_ndvi": geo_ndvi_rules,
        "security": security_rules,
        "observability": observability_rules,
        "performance": performance_rules,
    }

    categories = config.get("categories", list(rule_modules.keys()))

    for category in categories:
        if category not in rule_modules:
            continue

        module = rule_modules[category]
        category_findings = module.run_checks(repo_root, config)

        stats["by_category"][category] = {
            "total": len(category_findings),
            "passed": 0,
            "failed": len(category_findings),
        }

        for finding in category_findings:
            finding["category"] = category
            findings.append(finding)
            stats["total_checks"] += 1
            stats["failed"] += 1
            severity = finding.get("severity", "MEDIUM")
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1

    # Calculate health score
    severity_weights = config.get(
        "severity_weights", {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1}
    )

    total_penalty = sum(
        stats["by_severity"].get(sev, 0) * weight
        for sev, weight in severity_weights.items()
    )

    # Base score of 10, reduced by penalties (min 0)
    max_penalty = 100  # Normalize to this scale
    health_score = max(0, 10 - (total_penalty / max_penalty * 10))

    return {
        "project": config.get("project", {}),
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "health_score": round(health_score, 1),
        "stats": stats,
        "findings": sorted(
            findings,
            key=lambda x: severity_weights.get(x.get("severity", "MEDIUM"), 0),
            reverse=True,
        ),
        "thresholds": config.get("thresholds", {}),
    }


def main():
    parser = argparse.ArgumentParser(description="SAHOOL Audit Engine")
    parser.add_argument(
        "--repo", type=str, default=".", help="Path to repository root"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file (default: tools/audit/config.yaml)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        default=None,
        help="Specific categories to run",
    )

    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()

    # Load config
    if args.config:
        config_path = Path(args.config)
    else:
        config_path = Path(__file__).parent / "config.yaml"

    if config_path.exists():
        config = load_config(config_path)
    else:
        config = {"project": {"name": "Unknown"}, "categories": []}

    # Override categories if specified
    if args.categories:
        config["categories"] = args.categories

    # Run audit
    print(f"🔍 Running SAHOOL Audit on: {repo_root}")
    print(f"📋 Categories: {', '.join(config.get('categories', ['all']))}")
    print("-" * 50)

    results = run_audit(repo_root, config)

    # Generate report
    if args.format in ("markdown", "both"):
        md_output = markdown_report.generate(results)
        if args.output and args.format == "markdown":
            Path(args.output).write_text(md_output, encoding='utf-8')
            print(f"📄 Report saved to: {args.output}")
        else:
            print(md_output)

    if args.format in ("json", "both"):
        json_output = json_report.generate(results)
        output_path = args.output or "audit_report.json"
        if args.format == "json" or args.format == "both":
            Path(output_path).write_text(json_output, encoding='utf-8')
            print(f"📄 JSON report saved to: {output_path}")

    # Exit with appropriate code
    thresholds = results.get("thresholds", {})
    if results["health_score"] < thresholds.get("development_ready", 4.0):
        sys.exit(2)  # Critical issues
    elif results["health_score"] < thresholds.get("staging_ready", 6.0):
        sys.exit(1)  # Needs attention

    sys.exit(0)


if __name__ == "__main__":
    main()
