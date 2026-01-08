"""
Markdown Report Generator
"""

from datetime import datetime


def generate(results: dict) -> str:
    """Generate markdown report from audit results"""
    lines = []

    # Header
    project = results.get("project", {})
    lines.append(f"# 🔍 SAHOOL Audit Report")
    lines.append("")
    lines.append(f"**Project:** {project.get('name', 'Unknown')}")
    lines.append(f"**Version:** {project.get('version', 'N/A')}")
    lines.append(f"**Generated:** {results.get('timestamp', datetime.utcnow().isoformat())}")
    lines.append("")

    # Executive Summary
    lines.append("## 📊 Executive Summary")
    lines.append("")

    score = results.get("health_score", 0)
    score_emoji = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"

    lines.append(f"### Overall Health Score: {score_emoji} {score}/10")
    lines.append("")

    # Readiness assessment
    thresholds = results.get("thresholds", {})
    lines.append("| Readiness Level | Threshold | Status |")
    lines.append("|-----------------|-----------|--------|")

    for level, threshold in [
        ("Production", thresholds.get("production_ready", 8.0)),
        ("Staging", thresholds.get("staging_ready", 6.0)),
        ("Development", thresholds.get("development_ready", 4.0)),
    ]:
        status = "✅ Ready" if score >= threshold else "❌ Not Ready"
        lines.append(f"| {level} | {threshold} | {status} |")

    lines.append("")

    # Statistics
    stats = results.get("stats", {})
    lines.append("### Findings by Severity")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")

    severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = stats.get("by_severity", {}).get(severity, 0)
        emoji = severity_emoji.get(severity, "")
        lines.append(f"| {emoji} {severity} | {count} |")

    lines.append("")

    # Findings by Category
    if stats.get("by_category"):
        lines.append("### Findings by Category")
        lines.append("")
        lines.append("| Category | Issues |")
        lines.append("|----------|--------|")

        for category, cat_stats in stats.get("by_category", {}).items():
            count = cat_stats.get("failed", 0)
            lines.append(f"| {category.replace('_', ' ').title()} | {count} |")

        lines.append("")

    # Top Blockers (Critical and High)
    findings = results.get("findings", [])
    blockers = [f for f in findings if f.get("severity") in ["CRITICAL", "HIGH"]]

    if blockers:
        lines.append("## 🚨 Top Blockers")
        lines.append("")
        lines.append("| # | Severity | Component | Issue |")
        lines.append("|---|----------|-----------|-------|")

        for i, finding in enumerate(blockers[:10], 1):
            severity = finding.get("severity", "")
            emoji = severity_emoji.get(severity, "")
            component = finding.get("component", "")
            issue = finding.get("issue", "")[:60]
            lines.append(f"| {i} | {emoji} {severity} | {component} | {issue} |")

        lines.append("")

    # Detailed Findings
    lines.append("## 📋 Detailed Findings")
    lines.append("")

    # Group by category
    by_category = {}
    for finding in findings:
        cat = finding.get("category", "other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(finding)

    for category, cat_findings in by_category.items():
        lines.append(f"### {category.replace('_', ' ').title()}")
        lines.append("")

        for finding in cat_findings:
            severity = finding.get("severity", "")
            emoji = severity_emoji.get(severity, "")
            lines.append(f"#### {emoji} [{severity}] {finding.get('issue', '')}")
            lines.append("")
            lines.append(f"- **Component:** {finding.get('component', 'N/A')}")
            lines.append(f"- **File:** `{finding.get('file', 'N/A')}`")
            lines.append(f"- **Impact:** {finding.get('impact', 'N/A')}")
            lines.append(f"- **Fix:** {finding.get('fix', 'N/A')}")
            lines.append("")

    # Recommendations
    lines.append("## 🛠️ Fix Roadmap")
    lines.append("")

    critical_count = stats.get("by_severity", {}).get("CRITICAL", 0)
    high_count = stats.get("by_severity", {}).get("HIGH", 0)

    if critical_count > 0:
        lines.append("### Phase 0: Critical Fixes (Immediate)")
        lines.append("")
        lines.append("- Fix all CRITICAL issues before deployment")
        lines.append("- These prevent the system from functioning correctly")
        lines.append("")

    if high_count > 0:
        lines.append("### Phase 1: High Priority")
        lines.append("")
        lines.append("- Address HIGH severity issues")
        lines.append("- Required for staging/production readiness")
        lines.append("")

    lines.append("### Phase 2: Continuous Improvement")
    lines.append("")
    lines.append("- Address MEDIUM and LOW issues")
    lines.append("- Improve observability and performance")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by SAHOOL Audit Engine*")

    return "\n".join(lines)
