#!/usr/bin/env python3
"""
SAHOOL Platform - Tenant Isolation Enforcement
فحص عزل المستأجرين لمنصة سهول

Scans service code for patterns that bypass the tenant isolation layer
(shared/platform.py). Services MUST use TenantDB, TenantRedis,
TenantStorage, and TenantNATSPublisher instead of raw clients.

Usage:
  python3 scripts/ci/enforce-tenant-isolation.py [--json] [--verbose]

Exit codes:
  0 - No violations found
  1 - Violations detected
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# ANSI colours (disabled when piped)
# ─────────────────────────────────────────────────────────────────────────────
NO_COLOR = not sys.stdout.isatty()
RED = "" if NO_COLOR else "\033[91m"
GREEN = "" if NO_COLOR else "\033[92m"
YELLOW = "" if NO_COLOR else "\033[93m"
BLUE = "" if NO_COLOR else "\033[94m"
RESET = "" if NO_COLOR else "\033[0m"

# ─────────────────────────────────────────────────────────────────────────────
# Forbidden patterns — each bypasses the tenant isolation layer
# ─────────────────────────────────────────────────────────────────────────────
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    (r"asyncpg\.connect\(", "Direct asyncpg.connect() — use TenantDB"),
    (r"psycopg2\.connect\(", "Direct psycopg2.connect() — use TenantDB"),
    (r"create_engine\(", "Direct SQLAlchemy create_engine() — use TenantDB"),
    (r"new\s+PrismaClient\(\)", "Direct PrismaClient() — use TenantDB"),
    (r"redis\.(get|set|delete)\s*\(", "Direct Redis call — use TenantRedis"),
    (r"boto3\.client\s*\(\s*['\"]s3", "Direct S3 client — use TenantStorage"),
    (r"WHERE\s+tenant_id\s*=", "Manual tenant_id in query — rely on RLS"),
    (r"tenant_id\s*=\s*\?", "Manual tenant_id parameter — rely on RLS"),
    (r"nc\.publish\s*\([^,]+,\s*[^,]+\s*\)(?!.*headers)", "NATS publish without headers — use TenantNATSPublisher"),
]


def check_file(filepath: Path, verbose: bool = False) -> list[dict[str, str]]:
    """Scan a single file for forbidden patterns.

    Returns a list of violation dicts with keys: file, line, pattern, message.
    """
    violations: list[dict[str, str]] = []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return violations

    for line_no, line_text in enumerate(lines, start=1):
        # Skip comment-only lines
        stripped = line_text.lstrip()
        if stripped.startswith("#"):
            continue

        for pattern, message in FORBIDDEN_PATTERNS:
            if re.search(pattern, line_text):
                violations.append(
                    {
                        "file": str(filepath.relative_to(PROJECT_ROOT)),
                        "line": str(line_no),
                        "pattern": pattern,
                        "message": message,
                    }
                )
                if verbose:
                    print(f"  {YELLOW}⚠ {filepath.relative_to(PROJECT_ROOT)}:{line_no}{RESET}  {message}")

    return violations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enforce tenant isolation — detect direct DB/Redis/S3/NATS usage",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON (for CI)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print each violation as found")
    args = parser.parse_args()

    services_dir = PROJECT_ROOT / "apps" / "services"

    if not services_dir.is_dir():
        print(f"{RED}❌ apps/services/ directory not found{RESET}", file=sys.stderr)
        sys.exit(1)

    all_violations: list[dict[str, str]] = []

    for py_file in sorted(services_dir.rglob("*.py")):
        # Skip test files and shared modules — they are allowed to use raw clients
        rel = str(py_file.relative_to(PROJECT_ROOT))
        if "test" in rel or "shared" in rel:
            continue
        all_violations.extend(check_file(py_file, verbose=args.verbose))

    # ── Output ────────────────────────────────────────────────────────────
    if args.json:
        result = {
            "tool": "enforce-tenant-isolation",
            "total_violations": len(all_violations),
            "violations": all_violations,
        }
        print(json.dumps(result, indent=2))
    else:
        if all_violations:
            print(f"\n{RED}❌ TENANT ISOLATION VIOLATIONS:{RESET}")
            for v in all_violations:
                print(f"  {v['file']}:{v['line']} — {v['message']}")
            print(f"\n{RED}Total: {len(all_violations)} violation(s){RESET}")
        else:
            print(f"{GREEN}✅ All services comply with tenant isolation{RESET}")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
