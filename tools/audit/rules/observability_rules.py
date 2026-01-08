"""
Observability Rules - Check logging, metrics, and monitoring
"""

from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all observability-related checks"""
    findings = []

    findings.extend(check_structured_logging(repo_root))
    findings.extend(check_health_endpoints(repo_root))
    findings.extend(check_metrics_endpoint(repo_root))
    findings.extend(check_correlation_id(repo_root))
    findings.extend(check_error_handling(repo_root))

    return findings


def check_structured_logging(repo_root: Path) -> list:
    """Check for structured (JSON) logging"""
    findings = []

    logging_libs = ["structlog", "json_logging", "python-json-logger"]

    has_structured_logging = False

    # Check requirements files
    for req_file in repo_root.rglob("requirements*.txt"):
        try:
            content = req_file.read_text(encoding='utf-8').lower()
            if any(lib in content for lib in logging_libs):
                has_structured_logging = True
                break
        except Exception:
            continue

    # Also check pyproject.toml
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding='utf-8').lower()
            if any(lib in content for lib in logging_libs):
                has_structured_logging = True
        except Exception:
            pass

    if not has_structured_logging:
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "Observability",
                "issue": "No structured logging library detected",
                "impact": "Logs may be difficult to parse and analyze",
                "fix": "Add structlog or python-json-logger for structured logs",
                "file": "pyproject.toml",
            }
        )

    return findings


def check_health_endpoints(repo_root: Path) -> list:
    """Check all services have health endpoints"""
    findings = []

    services_path = repo_root / "apps" / "services"
    if not services_path.exists():
        return findings

    health_patterns = ["/healthz", "/health", "/ready", "/readyz", "/live", "/livez"]

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

        has_health = any(pattern in content for pattern in health_patterns)

        if not has_health:
            findings.append(
                {
                    "severity": "HIGH",
                    "component": service_dir.name,
                    "issue": "No health check endpoint detected",
                    "impact": "Container orchestrators cannot verify service health",
                    "fix": "Add /healthz and /readyz endpoints",
                    "file": str(main_py.relative_to(repo_root)),
                }
            )

    return findings


def check_metrics_endpoint(repo_root: Path) -> list:
    """Check for Prometheus metrics endpoint"""
    findings = []

    metrics_patterns = ["prometheus", "/metrics", "prometheus_client"]

    has_metrics = False

    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue
        try:
            content = py_file.read_text(encoding='utf-8').lower()
            if any(pattern in content for pattern in metrics_patterns):
                has_metrics = True
                break
        except Exception:
            continue

    if not has_metrics:
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "Observability",
                "issue": "No Prometheus metrics endpoint detected",
                "impact": "Cannot monitor service performance metrics",
                "fix": "Add prometheus_client and expose /metrics endpoint",
                "file": "shared/observability/metrics.py",
            }
        )

    return findings


def check_correlation_id(repo_root: Path) -> list:
    """Check for request correlation/trace ID implementation"""
    findings = []

    correlation_patterns = [
        "correlation_id",
        "trace_id",
        "request_id",
        "x-request-id",
        "x-correlation-id",
    ]

    has_correlation = False

    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue
        try:
            content = py_file.read_text(encoding='utf-8').lower()
            if any(pattern in content for pattern in correlation_patterns):
                has_correlation = True
                break
        except Exception:
            continue

    if not has_correlation:
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "Observability",
                "issue": "No request correlation ID detected",
                "impact": "Difficult to trace requests across services",
                "fix": "Add correlation ID middleware to propagate trace context",
                "file": "shared/middleware/",
            }
        )

    return findings


def check_error_handling(repo_root: Path) -> list:
    """Check for proper error handling and logging"""
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

        # Check for exception handler
        has_exception_handler = (
            "exception_handler" in content
            or "@app.exception" in content
            or "HTTPException" in content
        )

        if not has_exception_handler:
            findings.append(
                {
                    "severity": "LOW",
                    "component": service_dir.name,
                    "issue": "No global exception handler detected",
                    "impact": "Unhandled errors may leak internal details",
                    "fix": "Add global exception handler with proper error responses",
                    "file": str(main_py.relative_to(repo_root)),
                }
            )

    return findings
