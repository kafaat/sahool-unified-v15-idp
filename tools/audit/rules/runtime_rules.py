"""
Runtime Rules - Verify services can start and run correctly
"""

import re
from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all runtime-related checks"""
    findings = []

    findings.extend(check_healthchecks_defined(repo_root))
    findings.extend(check_startup_order(repo_root))
    findings.extend(check_port_conflicts(repo_root))
    findings.extend(check_entrypoints(repo_root))

    return findings


def check_healthchecks_defined(repo_root: Path) -> list:
    """Check all services have healthchecks in docker-compose"""
    findings = []

    compose_file = repo_root / "docker-compose.yml"
    if not compose_file.exists():
        return findings

    content = compose_file.read_text(encoding='utf-8')

    # Find services without healthchecks
    # Simple regex to find service blocks
    service_pattern = r"^\s{2}(\w[\w-]*):\s*$"
    healthcheck_pattern = r"healthcheck:"

    lines = content.split("\n")
    current_service = None
    service_has_healthcheck = {}
    indent_level = 0

    for i, line in enumerate(lines):
        # Check for service definition (2 spaces indent)
        service_match = re.match(service_pattern, line)
        if service_match and not line.strip().startswith("#"):
            current_service = service_match.group(1)
            service_has_healthcheck[current_service] = False
            indent_level = 2

        # Check for healthcheck in current service
        if current_service and "healthcheck:" in line:
            service_has_healthcheck[current_service] = True

    # Skip infrastructure services and one-shot containers
    # One-shot containers run once and exit (like model loaders, migrations)
    infra_services = {
        "postgres",
        "redis",
        "nats",
        "mqtt",
        "qdrant",
        "minio",
        "pgbouncer",
        "kong",
        "prometheus",
        "grafana",
        "networks",
        "volumes",
        # One-shot containers that run and exit
        "ollama-model-loader",
        "milvus-etcd",
        "milvus-minio",
        "milvus-standalone",
        "etcd",
        # YAML section markers (not services)
        "services",
        "x-logging",
        "x-healthcheck",
    }

    for service, has_healthcheck in service_has_healthcheck.items():
        if not has_healthcheck and service.lower() not in infra_services:
            findings.append(
                {
                    "severity": "HIGH",
                    "component": service,
                    "issue": f"Missing healthcheck for service: {service}",
                    "impact": "Docker cannot determine if service is healthy",
                    "fix": f"Add healthcheck configuration to {service} in docker-compose.yml",
                    "file": str(compose_file),
                }
            )

    return findings


def check_startup_order(repo_root: Path) -> list:
    """Check services have proper depends_on configuration"""
    findings = []

    compose_file = repo_root / "docker-compose.yml"
    if not compose_file.exists():
        return findings

    content = compose_file.read_text(encoding='utf-8')

    # Services that typically need database
    db_dependent_keywords = ["DATABASE_URL", "POSTGRES", "asyncpg", "sqlalchemy"]

    # Check if services using database have depends_on postgres
    services_path = repo_root / "apps" / "services"
    if services_path.exists():
        for service_dir in services_path.iterdir():
            if not service_dir.is_dir():
                continue

            service_name = service_dir.name

            # Check if service uses database
            uses_db = False
            for py_file in service_dir.rglob("*.py"):
                try:
                    py_content = py_file.read_text(encoding='utf-8')
                    if any(kw in py_content for kw in db_dependent_keywords):
                        uses_db = True
                        break
                except Exception:
                    continue

            if uses_db:
                # Check if service has depends_on postgres in compose
                service_block_pattern = rf"{service_name}:.*?(?=^\s{{2}}\w|\Z)"
                service_match = re.search(
                    service_block_pattern, content, re.MULTILINE | re.DOTALL
                )

                if service_match:
                    service_block = service_match.group(0)
                    if "depends_on" not in service_block or (
                        "postgres" not in service_block and "pgbouncer" not in service_block
                    ):
                        findings.append(
                            {
                                "severity": "MEDIUM",
                                "component": service_name,
                                "issue": f"{service_name} uses database but may not wait for it",
                                "impact": "Service may crash on startup before DB is ready",
                                "fix": f"Add depends_on: postgres with condition: service_healthy",
                                "file": str(compose_file),
                            }
                        )

    return findings


def check_port_conflicts(repo_root: Path) -> list:
    """Check for port conflicts in docker-compose"""
    findings = []

    compose_file = repo_root / "docker-compose.yml"
    if not compose_file.exists():
        return findings

    content = compose_file.read_text(encoding='utf-8')

    # Extract port mappings
    port_pattern = r'"(\d+):(\d+)"'
    ports = re.findall(port_pattern, content)

    host_ports = {}
    for host_port, container_port in ports:
        if host_port in host_ports:
            findings.append(
                {
                    "severity": "CRITICAL",
                    "component": "Infrastructure",
                    "issue": f"Port conflict: {host_port} is mapped multiple times",
                    "impact": "Only one service will be able to bind to this port",
                    "fix": f"Change one of the services to use a different host port",
                    "file": str(compose_file),
                }
            )
        host_ports[host_port] = True

    return findings


def check_entrypoints(repo_root: Path) -> list:
    """Check services have proper entrypoints"""
    findings = []

    services_path = repo_root / "apps" / "services"
    if not services_path.exists():
        return findings

    for service_dir in services_path.iterdir():
        if not service_dir.is_dir():
            continue

        dockerfile = service_dir / "Dockerfile"
        if not dockerfile.exists():
            continue

        content = dockerfile.read_text(encoding='utf-8')

        # Check for CMD or ENTRYPOINT
        has_cmd = "CMD " in content or "CMD[" in content
        has_entrypoint = "ENTRYPOINT " in content or "ENTRYPOINT[" in content

        if not has_cmd and not has_entrypoint:
            findings.append(
                {
                    "severity": "HIGH",
                    "component": service_dir.name,
                    "issue": f"Missing CMD or ENTRYPOINT in Dockerfile",
                    "impact": "Container will not know how to start",
                    "fix": "Add CMD or ENTRYPOINT instruction to Dockerfile",
                    "file": str(dockerfile),
                }
            )

    return findings
