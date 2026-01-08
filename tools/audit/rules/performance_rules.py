"""
Performance Rules - Check for performance optimizations
"""

import re
from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all performance-related checks"""
    findings = []

    findings.extend(check_database_indexes(repo_root))
    findings.extend(check_pagination(repo_root))
    findings.extend(check_caching(repo_root))
    findings.extend(check_async_patterns(repo_root))
    findings.extend(check_n_plus_one(repo_root))

    return findings


def check_database_indexes(repo_root: Path) -> list:
    """Check for database indexes on common query columns"""
    findings = []

    # Critical columns that should be indexed
    index_columns = ["tenant_id", "field_id", "user_id", "created_at", "updated_at"]

    # Check migrations for indexes
    migration_files = list(repo_root.rglob("**/migrations/**/*.py")) + list(
        repo_root.rglob("**/migrations/**/*.sql")
    )

    found_indexes = set()

    for migration in migration_files:
        try:
            content = migration.read_text(encoding='utf-8').lower()
            for col in index_columns:
                if f"index" in content and col in content:
                    found_indexes.add(col)
        except Exception:
            continue

    missing_indexes = set(index_columns) - found_indexes

    if missing_indexes:
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "Database",
                "issue": f"Missing indexes on: {', '.join(missing_indexes)}",
                "impact": "Slow queries on large datasets",
                "fix": "Add database indexes for frequently queried columns",
                "file": "database/migrations/",
            }
        )

    return findings


def check_pagination(repo_root: Path) -> list:
    """Check list endpoints have pagination"""
    findings = []

    pagination_patterns = ["limit", "offset", "page", "per_page", "skip", "take"]

    services_path = repo_root / "apps" / "services"
    if not services_path.exists():
        return findings

    for service_dir in services_path.iterdir():
        if not service_dir.is_dir():
            continue

        for py_file in service_dir.rglob("*.py"):
            if "test" in str(py_file).lower():
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
            except Exception:
                continue

            # Check for list endpoints
            list_patterns = [
                r'@\w+\.get\s*\(\s*["\'][^"\']*list',
                r'@\w+\.get\s*\(\s*["\'][^"\']*all',
                r'def\s+list_\w+',
                r'def\s+get_all',
            ]

            has_list_endpoint = any(
                re.search(p, content, re.IGNORECASE) for p in list_patterns
            )

            if has_list_endpoint:
                has_pagination = any(p in content.lower() for p in pagination_patterns)

                if not has_pagination:
                    findings.append(
                        {
                            "severity": "MEDIUM",
                            "component": service_dir.name,
                            "issue": "List endpoint without pagination",
                            "impact": "Large datasets will cause memory/timeout issues",
                            "fix": "Add limit/offset or page/per_page parameters",
                            "file": str(py_file.relative_to(repo_root)),
                        }
                    )
                    break  # One finding per service

    return findings


def check_caching(repo_root: Path) -> list:
    """Check for caching implementation"""
    findings = []

    cache_patterns = ["redis", "cache", "memcache", "@cached", "lru_cache"]

    has_caching = False

    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue
        try:
            content = py_file.read_text(encoding='utf-8').lower()
            if any(pattern in content for pattern in cache_patterns):
                has_caching = True
                break
        except Exception:
            continue

    if not has_caching:
        findings.append(
            {
                "severity": "LOW",
                "component": "Performance",
                "issue": "No caching implementation detected",
                "impact": "Repeated expensive operations not cached",
                "fix": "Implement Redis caching for frequently accessed data",
                "file": "shared/cache/",
            }
        )

    return findings


def check_async_patterns(repo_root: Path) -> list:
    """Check for proper async/await usage"""
    findings = []

    services_path = repo_root / "apps" / "services"
    if not services_path.exists():
        return findings

    for service_dir in services_path.iterdir():
        if not service_dir.is_dir():
            continue

        main_py = service_dir / "src" / "main.py"
        if not main_py.exists():
            continue

        try:
            content = main_py.read_text(encoding='utf-8')
        except Exception:
            continue

        # Check if using FastAPI (which should use async)
        if "FastAPI" not in content:
            continue

        # Count sync vs async endpoints
        sync_endpoints = len(re.findall(r"def\s+\w+\s*\([^)]*\)\s*:", content))
        async_endpoints = len(re.findall(r"async\s+def\s+\w+\s*\([^)]*\)\s*:", content))

        # If mostly sync endpoints, flag it
        if sync_endpoints > async_endpoints and sync_endpoints > 3:
            findings.append(
                {
                    "severity": "LOW",
                    "component": service_dir.name,
                    "issue": f"Many sync endpoints ({sync_endpoints}) vs async ({async_endpoints})",
                    "impact": "May block event loop under load",
                    "fix": "Convert I/O-bound endpoints to async def",
                    "file": str(main_py.relative_to(repo_root)),
                }
            )

    return findings


def check_n_plus_one(repo_root: Path) -> list:
    """Check for potential N+1 query patterns"""
    findings = []

    # Patterns that might indicate N+1
    n_plus_one_patterns = [
        r"for\s+\w+\s+in\s+\w+:\s*\n\s+.*\.query",
        r"for\s+\w+\s+in\s+\w+:\s*\n\s+.*await.*get",
        r"for\s+\w+\s+in\s+\w+:\s*\n\s+.*fetch",
    ]

    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue

        try:
            content = py_file.read_text(encoding='utf-8')
        except Exception:
            continue

        for pattern in n_plus_one_patterns:
            if re.search(pattern, content):
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "component": py_file.parent.name,
                        "issue": "Potential N+1 query pattern detected",
                        "impact": "Performance degradation with large datasets",
                        "fix": "Use eager loading or batch queries",
                        "file": str(py_file.relative_to(repo_root)),
                    }
                )
                break

    return findings
