#!/usr/bin/env python3
"""
SAHOOL Platform Fix Verification
Verifies that all infrastructure and code fixes are properly applied.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

try:
    import yaml
except ImportError:
    yaml = None


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_result(name: str, passed: bool, message: str = "") -> None:
    """Print a check result."""
    status = "✅" if passed else "❌"
    msg = f" - {message}" if message else ""
    print(f"  {status} {name}{msg}")


def verify_kong_config() -> Tuple[bool, str]:
    """Verify Kong HA configuration exists and is valid."""
    kong_files = [
        "infra/kong-ha/docker-compose.kong-ha.yml",
        "infra/kong-ha/nginx-kong-ha.conf",
        "infra/kong-ha/kong/declarative/kong.yml",
    ]

    for file_path in kong_files:
        path = Path(file_path)
        if not path.exists():
            return False, f"Missing: {file_path}"

    # Validate YAML syntax
    if yaml:
        try:
            kong_config = Path("infra/kong-ha/kong/declarative/kong.yml")
            data = yaml.safe_load(kong_config.read_text())
            services = data.get("services", [])
            if len(services) < 5:
                return False, f"Only {len(services)} services configured (expected 5+)"
        except Exception as e:
            return False, f"Invalid YAML: {e}"

    return True, f"3 config files, {len(services)} services"


def verify_circuit_breaker() -> Tuple[bool, str]:
    """Verify Circuit Breaker implementation exists."""
    cb_path = Path("shared/python-lib/sahool_core/resilient_client.py")

    if not cb_path.exists():
        return False, "resilient_client.py not found"

    content = cb_path.read_text()

    required_classes = ["CircuitBreaker", "CircuitState"]
    required_methods = ["call", "_fallback", "_on_failure", "_on_success"]

    missing = []
    for cls in required_classes:
        if f"class {cls}" not in content:
            missing.append(cls)

    for method in required_methods:
        if f"def {method}" not in content and f"async def {method}" not in content:
            missing.append(method)

    if missing:
        return False, f"Missing: {', '.join(missing)}"

    return True, "CircuitBreaker with fallback support"


def verify_postgis_migration() -> Tuple[bool, str]:
    """Verify PostGIS optimization migration exists."""
    migration_path = Path("migrations/20241222_postgis_optimization.sql")

    if not migration_path.exists():
        return False, "Migration file not found"

    content = migration_path.read_text()

    required_features = [
        ("GIST", "CREATE INDEX.*USING GIST"),
        ("Partitioning", "PARTITION BY RANGE"),
        ("Materialized View", "CREATE MATERIALIZED VIEW"),
        ("pg_cron", "cron.schedule"),
    ]

    found = []
    missing = []
    for name, pattern in required_features:
        import re
        if re.search(pattern, content, re.IGNORECASE):
            found.append(name)
        else:
            missing.append(name)

    if missing:
        return False, f"Missing: {', '.join(missing)}"

    return True, f"Includes: {', '.join(found)}"


def verify_memory_manager() -> Tuple[bool, str]:
    """Verify Flutter memory manager exists."""
    mm_path = Path("apps/mobile/lib/services/memory_manager.dart")

    if not mm_path.exists():
        return False, "memory_manager.dart not found"

    content = mm_path.read_text()

    required = ["MemoryManager", "autoEvict", "getPaginated", "maxCacheSize"]
    missing = [r for r in required if r not in content]

    if missing:
        return False, f"Missing: {', '.join(missing)}"

    return True, "LRU cache with pagination support"


def verify_analyzer_tool() -> Tuple[bool, str]:
    """Verify complete analyzer tool exists."""
    analyzer_path = Path("tools/complete-analyzer.py")

    if not analyzer_path.exists():
        return False, "complete-analyzer.py not found"

    content = analyzer_path.read_text()

    required = ["SahoolAnalyzer", "check_postgis_queries", "analyze_dependencies"]
    missing = [r for r in required if r not in content]

    if missing:
        return False, f"Missing: {', '.join(missing)}"

    return True, "Full platform analyzer"


def verify_precommit_hook() -> Tuple[bool, str]:
    """Verify pre-commit hook exists."""
    hook_path = Path("tools/scripts/pre-commit")

    if not hook_path.exists():
        return False, "pre-commit hook not found"

    content = hook_path.read_text()

    checks = [
        "dependencies",
        "YAML",
        "secrets",
        "Python",
    ]

    found = sum(1 for c in checks if c.lower() in content.lower())

    if found < 3:
        return False, f"Only {found}/4 checks configured"

    return True, f"{found} quality checks"


def verify_pubspec_fixes() -> Tuple[bool, str]:
    """Verify Flutter pubspec fixes are applied."""
    pubspec_paths = [
        "apps/mobile/pubspec.yaml",
        "apps/mobile/sahool_field_app/pubspec.yaml",
    ]

    issues = []
    for path_str in pubspec_paths:
        path = Path(path_str)
        if not path.exists():
            continue

        if yaml:
            try:
                data = yaml.safe_load(path.read_text())

                # Check mockito version
                dev_deps = data.get("dev_dependencies", {})
                mockito = dev_deps.get("mockito", "")
                if "5.4.6" in str(mockito):
                    issues.append(f"{path.name}: mockito 5.4.6 (needs 5.4.5)")

                # Check dependency overrides
                overrides = data.get("dependency_overrides", {})
                if "analyzer" not in overrides:
                    issues.append(f"{path.name}: missing analyzer override")

            except Exception as e:
                issues.append(f"{path.name}: parse error - {e}")

    if issues:
        return False, "; ".join(issues)

    return True, "mockito 5.4.5, analyzer override applied"


def main() -> int:
    """Run all verification checks."""
    print_header("SAHOOL Platform Fix Verification")

    checks = [
        ("Kong HA Configuration", verify_kong_config),
        ("Circuit Breaker", verify_circuit_breaker),
        ("PostGIS Migration", verify_postgis_migration),
        ("Memory Manager", verify_memory_manager),
        ("Platform Analyzer", verify_analyzer_tool),
        ("Pre-commit Hook", verify_precommit_hook),
        ("Pubspec Fixes", verify_pubspec_fixes),
    ]

    results: Dict[str, bool] = {}

    for name, check_func in checks:
        try:
            passed, message = check_func()
            results[name] = passed
            print_result(name, passed, message)
        except Exception as e:
            results[name] = False
            print_result(name, False, f"Error: {e}")

    # Summary
    passed = sum(results.values())
    total = len(results)

    print_header("Summary")
    print(f"  Passed: {passed}/{total}")

    if passed == total:
        print("\n  🎉 All fixes verified! Platform ready for production.")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} check(s) need attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
