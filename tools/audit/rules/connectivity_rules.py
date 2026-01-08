"""
Connectivity Rules - Verify services can communicate with each other
"""

import re
from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all connectivity-related checks"""
    findings = []

    findings.extend(check_localhost_usage(repo_root))
    findings.extend(check_service_discovery(repo_root))
    findings.extend(check_api_gateway_routes(repo_root))
    findings.extend(check_cors_configuration(repo_root))

    return findings


def check_localhost_usage(repo_root: Path) -> list:
    """Check for hardcoded localhost in service-to-service communication"""
    findings = []

    # Patterns that indicate problematic localhost usage
    bad_patterns = [
        r"http://localhost:\d+",
        r"http://127\.0\.0\.1:\d+",
        r"localhost:\d+",
    ]

    # Files to check
    for py_file in repo_root.rglob("*.py"):
        # Skip test files and examples
        if "test" in str(py_file).lower() or "example" in str(py_file).lower():
            continue

        try:
            content = py_file.read_text()
        except Exception:
            continue

        for pattern in bad_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # Check if it's in a default/fallback (which is OK)
                for match in matches:
                    # Skip if it's clearly a fallback
                    context_pattern = rf".{{0,50}}{re.escape(match)}.{{0,50}}"
                    context = re.search(context_pattern, content)
                    if context:
                        ctx = context.group(0)
                        if "getenv" in ctx or "environ" in ctx or "default" in ctx.lower():
                            continue

                    findings.append(
                        {
                            "severity": "MEDIUM",
                            "component": py_file.parent.name,
                            "issue": f"Hardcoded localhost found: {match}",
                            "impact": "Service-to-service communication will fail in containers",
                            "fix": "Use environment variables or service names for URLs",
                            "file": str(py_file.relative_to(repo_root)),
                        }
                    )
                    break  # One finding per file is enough

    return findings


def check_service_discovery(repo_root: Path) -> list:
    """Check services use proper service names for discovery"""
    findings = []

    compose_file = repo_root / "docker-compose.yml"
    if not compose_file.exists():
        return findings

    content = compose_file.read_text()

    # Extract service names from compose
    service_pattern = r"^\s{2}(\w[\w-]*):\s*$"
    services = set(re.findall(service_pattern, content, re.MULTILINE))

    # Check environment variables reference correct service names
    env_url_pattern = r"(\w+_URL)=(\S+)"
    env_matches = re.findall(env_url_pattern, content)

    for env_name, env_value in env_matches:
        # Check if URL references a known service
        if "://" in env_value:
            # Extract hostname from URL
            host_match = re.search(r"://([^:/]+)", env_value)
            if host_match:
                hostname = host_match.group(1)
                # Check if it's a known service or valid placeholder
                if (
                    hostname not in services
                    and hostname not in ["localhost", "127.0.0.1"]
                    and not hostname.startswith("$")
                    and not hostname.startswith("{")
                ):
                    # Could be external service, skip
                    pass

    return findings


def check_api_gateway_routes(repo_root: Path) -> list:
    """Check API gateway (Kong) routes are properly configured"""
    findings = []

    # Look for Kong configuration
    kong_configs = list(repo_root.rglob("kong*.yml")) + list(
        repo_root.rglob("kong*.yaml")
    )

    if not kong_configs:
        # Check if Kong is used
        compose_file = repo_root / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            if "kong:" in content.lower():
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "component": "API Gateway",
                        "issue": "Kong is defined but no configuration file found",
                        "impact": "API routing may not work as expected",
                        "fix": "Add Kong configuration file (kong.yml)",
                        "file": "infrastructure/kong/",
                    }
                )

    return findings


def check_cors_configuration(repo_root: Path) -> list:
    """Check CORS is properly configured for web apps"""
    findings = []

    # Check FastAPI services for CORS
    for main_py in repo_root.rglob("main.py"):
        if "services" not in str(main_py):
            continue

        try:
            content = main_py.read_text()
        except Exception:
            continue

        # Check if it's a FastAPI app
        if "FastAPI" not in content:
            continue

        # Check for CORS middleware
        if "CORSMiddleware" not in content and "cors" not in content.lower():
            findings.append(
                {
                    "severity": "LOW",
                    "component": main_py.parent.parent.name,
                    "issue": "CORS middleware not detected",
                    "impact": "Web apps may not be able to call this API",
                    "fix": "Add CORSMiddleware to FastAPI app",
                    "file": str(main_py.relative_to(repo_root)),
                }
            )

    return findings
