#!/usr/bin/env python3
"""
SAHOOL Platform - Dependency Drift Detection
كشف انحراف الاعتماديات لمنصة سهول

Compares dependency versions across:
  - pyproject.toml (root optional-dependencies)
  - constraints.txt (central pinning)
  - Individual service requirements.txt files
  - package.json (Node.js root + workspaces)

Usage:
  python3 scripts/check-dependency-drift.py [--fix] [--json]

Exit codes:
  0 - No drift detected
  1 - Drift detected (versions mismatch)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────────

def parse_constraints(path: Path) -> dict[str, str]:
    """Parse constraints.txt into {package: version_spec}."""
    deps: dict[str, str] = {}
    if not path.exists():
        return deps
    for line in path.read_text().splitlines():
        # Strip inline comments first
        line = re.sub(r"\s*#.*$", "", line).strip()
        if not line or line.startswith("#"):
            continue
        # Match: package==1.0.0 or package>=1.0.0,<2.0.0
        m = re.match(r"^([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,-]+\])?)\s*([>=<!=~].+)$", line)
        if m:
            pkg = re.sub(r"\[.*\]", "", m.group(1)).lower().replace("-", "_")
            deps[pkg] = m.group(2).strip()
    return deps


def parse_pyproject_deps(path: Path) -> dict[str, dict[str, str]]:
    """Parse pyproject.toml optional-dependencies into {group: {package: version_spec}}."""
    groups: dict[str, dict[str, str]] = {}
    if not path.exists():
        return groups
    content = path.read_text()
    current_group = None
    in_deps = False
    for line in content.splitlines():
        # Match group header: base = [
        gm = re.match(r"^(\w+)\s*=\s*\[", line)
        if gm and "[project.optional-dependencies]" not in line:
            if in_deps or "[project.optional-dependencies]" in "\n".join(content.splitlines()[:content.splitlines().index(line)]):
                current_group = gm.group(1)
                groups[current_group] = {}
                in_deps = True
                continue
        if in_deps and line.strip() == "]":
            in_deps = False
            current_group = None
            continue
        if in_deps and current_group:
            # Match: "package==1.0.0",  or "package>=1.0.0,<2.0.0",
            dm = re.match(r'^\s*"([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,-]+\])?)\s*([>=<!=~][^"]*)"', line)
            if dm:
                pkg = re.sub(r"\[.*\]", "", dm.group(1)).lower().replace("-", "_")
                groups[current_group][pkg] = dm.group(2).strip()
    return groups


def parse_requirements(path: Path) -> dict[str, str]:
    """Parse a requirements.txt into {package: version_spec}."""
    deps: dict[str, str] = {}
    if not path.exists():
        return deps
    for line in path.read_text().splitlines():
        line = re.sub(r"\s*#.*$", "", line).strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,-]+\])?)\s*([>=<!=~].+?)(?:\s*#.*)?$", line)
        if m:
            pkg = re.sub(r"\[.*\]", "", m.group(1)).lower().replace("-", "_")
            deps[pkg] = m.group(2).strip()
        else:
            # Unpinned dependency
            m2 = re.match(r"^([a-zA-Z0-9_-]+)\s*$", line)
            if m2:
                pkg = m2.group(1).lower().replace("-", "_")
                deps[pkg] = "*"
    return deps


def parse_package_json_deps(path: Path) -> dict[str, str]:
    """Parse package.json dependencies."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    deps: dict[str, str] = {}
    for section in ("dependencies", "devDependencies"):
        for pkg, ver in data.get(section, {}).items():
            deps[pkg] = ver
    return deps


# ─────────────────────────────────────────────────────────────────────────────
# Version comparison
# ─────────────────────────────────────────────────────────────────────────────

def extract_exact_version(spec: str) -> str | None:
    """Extract exact version from ==X.Y.Z spec."""
    m = re.match(r"^==(.+)$", spec)
    return m.group(1) if m else None


def specs_compatible(spec_a: str, spec_b: str) -> bool:
    """Check if two version specs are obviously compatible."""
    if spec_a == spec_b:
        return True
    # Both exact
    va = extract_exact_version(spec_a)
    vb = extract_exact_version(spec_b)
    if va and vb:
        return va == vb
    # If one is exact and other is range, check if exact is in range start
    if va and spec_b.startswith(">="):
        return True  # Can't fully resolve without pip, assume OK
    if vb and spec_a.startswith(">="):
        return True
    # Range vs range - too complex without resolver
    return spec_a == spec_b


# ─────────────────────────────────────────────────────────────────────────────
# Main drift detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_drift(project_root: Path) -> list[dict[str, Any]]:
    """Detect version drift across all dependency sources."""
    issues: list[dict[str, Any]] = []

    constraints = parse_constraints(project_root / "constraints.txt")
    pyproject_groups = parse_pyproject_deps(project_root / "pyproject.toml")

    # 1. Check pyproject.toml vs constraints.txt
    for group, deps in pyproject_groups.items():
        for pkg, spec in deps.items():
            if pkg in constraints:
                con_spec = constraints[pkg]
                if not specs_compatible(spec, con_spec):
                    issues.append({
                        "type": "pyproject_vs_constraints",
                        "severity": "error",
                        "package": pkg,
                        "source": f"pyproject.toml [{group}]",
                        "source_version": spec,
                        "constraint_version": con_spec,
                        "message": f"{pkg}: pyproject.toml has {spec}, constraints.txt has {con_spec}",
                    })

    # 2. Check each service requirements.txt vs constraints.txt
    services_dir = project_root / "apps" / "services"
    if services_dir.exists():
        for req_file in sorted(services_dir.glob("*/requirements.txt")):
            svc_name = req_file.parent.name
            svc_deps = parse_requirements(req_file)
            for pkg, spec in svc_deps.items():
                if spec == "*":
                    issues.append({
                        "type": "unpinned",
                        "severity": "warning",
                        "package": pkg,
                        "source": f"apps/services/{svc_name}/requirements.txt",
                        "source_version": "unpinned",
                        "constraint_version": constraints.get(pkg, "N/A"),
                        "message": f"{pkg} is unpinned in {svc_name}",
                    })
                    continue
                if pkg in constraints:
                    con_spec = constraints[pkg]
                    svc_exact = extract_exact_version(spec)
                    con_exact = extract_exact_version(con_spec)
                    if svc_exact and con_exact and svc_exact != con_exact:
                        issues.append({
                            "type": "service_vs_constraints",
                            "severity": "error",
                            "package": pkg,
                            "source": f"apps/services/{svc_name}/requirements.txt",
                            "source_version": spec,
                            "constraint_version": con_spec,
                            "message": f"{pkg}: {svc_name} has {spec}, constraints.txt has {con_spec}",
                        })

    # 3. Check Node.js workspace version consistency
    root_pkg = project_root / "package.json"
    if root_pkg.exists():
        root_data = json.loads(root_pkg.read_text())
        root_overrides = root_data.get("overrides", {})
        workspaces = root_data.get("workspaces", [])

        # Collect all workspace package.json files
        workspace_deps: dict[str, list[tuple[str, str]]] = {}  # pkg -> [(workspace, version)]
        for pattern in workspaces:
            for pkg_json in sorted(project_root.glob(f"{pattern}/package.json")):
                ws_name = pkg_json.parent.relative_to(project_root)
                deps = parse_package_json_deps(pkg_json)
                for pkg, ver in deps.items():
                    if pkg not in workspace_deps:
                        workspace_deps[pkg] = []
                    workspace_deps[pkg].append((str(ws_name), ver))

        # Check for version divergence across workspaces
        for pkg, locations in workspace_deps.items():
            versions = set(ver for _, ver in locations)
            if len(versions) > 1 and pkg not in root_overrides:
                # Only flag important packages
                if any(k in pkg for k in ["typescript", "react", "next", "prisma", "vitest", "@nestjs"]):
                    locs_str = "; ".join(f"{ws}={ver}" for ws, ver in locations[:5])
                    issues.append({
                        "type": "npm_workspace_divergence",
                        "severity": "warning",
                        "package": pkg,
                        "source": "npm workspaces",
                        "source_version": ", ".join(sorted(versions)),
                        "constraint_version": root_overrides.get(pkg, "no override"),
                        "message": f"{pkg} has {len(versions)} versions across workspaces: {locs_str}",
                    })

    return issues


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BLUE = "\033[34m"
BOLD = "\033[1m"


def print_report(issues: list[dict[str, Any]], as_json: bool = False) -> None:
    if as_json:
        print(json.dumps({"issues": issues, "total": len(issues)}, indent=2))
        return

    print(f"\n{BLUE}{'═' * 65}{RESET}")
    print(f"{BLUE}  SAHOOL - Dependency Drift Report{RESET}")
    print(f"{BLUE}  كشف انحراف الاعتماديات{RESET}")
    print(f"{BLUE}{'═' * 65}{RESET}\n")

    if not issues:
        print(f"{GREEN}{BOLD}No drift detected - all dependencies are consistent!{RESET}")
        print(f"{GREEN}لم يتم اكتشاف أي انحراف - جميع الاعتماديات متسقة{RESET}\n")
        return

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    if errors:
        print(f"{RED}{BOLD}Errors ({len(errors)}):{RESET}")
        for i in errors:
            print(f"  {RED}✗{RESET} {i['message']}")
            print(f"    Source: {i['source']} = {i['source_version']}")
            print(f"    Constraint: {i['constraint_version']}")
        print()

    if warnings:
        print(f"{YELLOW}{BOLD}Warnings ({len(warnings)}):{RESET}")
        for i in warnings:
            print(f"  {YELLOW}⚠{RESET} {i['message']}")
        print()

    print(f"\n{BOLD}Summary:{RESET} {RED}{len(errors)} errors{RESET}, {YELLOW}{len(warnings)} warnings{RESET}")
    if errors:
        print(f"\n{YELLOW}Fix errors by syncing versions between pyproject.toml, constraints.txt, and service requirements.txt{RESET}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SAHOOL Dependency Drift Detection")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fix", action="store_true", help="Generate fix suggestions (dry-run)")
    args = parser.parse_args()

    issues = detect_drift(PROJECT_ROOT)
    print_report(issues, as_json=args.json)

    if args.fix and issues:
        errors = [i for i in issues if i["severity"] == "error"]
        if errors:
            print(f"\n{BLUE}{BOLD}Fix suggestions:{RESET}")
            for i in errors:
                if i["type"] == "service_vs_constraints":
                    print(f"  In {i['source']}: change {i['package']}{i['source_version']} -> {i['package']}{i['constraint_version']}")
                elif i["type"] == "pyproject_vs_constraints":
                    print(f"  In {i['source']}: change {i['package']}{i['source_version']} -> {i['package']}{i['constraint_version']}")

    # Exit 1 if errors found
    return 1 if any(i["severity"] == "error" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
