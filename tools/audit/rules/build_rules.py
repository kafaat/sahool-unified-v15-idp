"""
Build Rules - Verify project can be built successfully
"""

from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all build-related checks"""
    findings = []

    findings.extend(check_dockerfile_exists(repo_root))
    findings.extend(check_docker_compose(repo_root))
    findings.extend(check_requirements(repo_root))
    findings.extend(check_package_json(repo_root))
    findings.extend(check_env_example(repo_root))

    return findings


def check_dockerfile_exists(repo_root: Path) -> list:
    """Check that all services have Dockerfiles"""
    findings = []
    services_path = repo_root / "apps" / "services"

    if not services_path.exists():
        return findings

    for service_dir in services_path.iterdir():
        if not service_dir.is_dir():
            continue

        dockerfile = service_dir / "Dockerfile"
        if not dockerfile.exists():
            findings.append(
                {
                    "severity": "HIGH",
                    "component": service_dir.name,
                    "issue": f"Missing Dockerfile in {service_dir.name}",
                    "impact": "Service cannot be containerized",
                    "fix": f"Add Dockerfile to apps/services/{service_dir.name}/",
                    "file": str(service_dir),
                }
            )

    return findings


def check_docker_compose(repo_root: Path) -> list:
    """Check docker-compose.yml exists and is valid"""
    findings = []

    compose_file = repo_root / "docker-compose.yml"
    if not compose_file.exists():
        findings.append(
            {
                "severity": "CRITICAL",
                "component": "Infrastructure",
                "issue": "Missing docker-compose.yml",
                "impact": "Cannot orchestrate services locally",
                "fix": "Add docker-compose.yml with all service definitions",
                "file": str(compose_file),
            }
        )
        return findings

    content = compose_file.read_text()

    # Check for common issues
    if "version:" not in content and "services:" not in content:
        findings.append(
            {
                "severity": "HIGH",
                "component": "Infrastructure",
                "issue": "Invalid docker-compose.yml structure",
                "impact": "Docker compose will fail to parse",
                "fix": "Ensure docker-compose.yml has valid structure",
                "file": str(compose_file),
            }
        )

    return findings


def check_requirements(repo_root: Path) -> list:
    """Check Python services have requirements.txt"""
    findings = []
    services_path = repo_root / "apps" / "services"

    if not services_path.exists():
        return findings

    for service_dir in services_path.iterdir():
        if not service_dir.is_dir():
            continue

        # Check if it's a Python service
        has_python = (
            (service_dir / "src").exists()
            and list((service_dir / "src").glob("*.py"))
        ) or list(service_dir.glob("*.py"))

        if has_python:
            req_file = service_dir / "requirements.txt"
            if not req_file.exists():
                findings.append(
                    {
                        "severity": "HIGH",
                        "component": service_dir.name,
                        "issue": f"Missing requirements.txt in {service_dir.name}",
                        "impact": "Dependencies cannot be installed",
                        "fix": f"Add requirements.txt to apps/services/{service_dir.name}/",
                        "file": str(service_dir),
                    }
                )

    return findings


def check_package_json(repo_root: Path) -> list:
    """Check Node.js services/apps have package.json"""
    findings = []

    # Check web apps
    for app_type in ["web", "admin", "mobile"]:
        app_path = repo_root / "apps" / app_type
        if app_path.exists():
            for app_dir in app_path.iterdir():
                if not app_dir.is_dir():
                    continue

                # Check for TS/JS files
                has_node = list(app_dir.rglob("*.ts")) or list(app_dir.rglob("*.tsx"))
                if has_node:
                    pkg_file = app_dir / "package.json"
                    if not pkg_file.exists():
                        findings.append(
                            {
                                "severity": "HIGH",
                                "component": app_dir.name,
                                "issue": f"Missing package.json in {app_dir.name}",
                                "impact": "Node dependencies cannot be installed",
                                "fix": f"Add package.json to {app_dir.relative_to(repo_root)}",
                                "file": str(app_dir),
                            }
                        )

    return findings


def check_env_example(repo_root: Path) -> list:
    """Check .env.example exists"""
    findings = []

    env_example = repo_root / ".env.example"
    if not env_example.exists():
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "Configuration",
                "issue": "Missing .env.example file",
                "impact": "Developers cannot know required environment variables",
                "fix": "Create .env.example with all required variables (without secrets)",
                "file": str(env_example),
            }
        )

    return findings
