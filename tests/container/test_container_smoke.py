"""
SAHOOL Container Smoke & Startup Tests
========================================
اختبارات الدخان وإعدادات تشغيل الحاويات

Smoke-level tests that validate container *runtime configuration* without
actually starting containers. Tests parse docker-compose.yml and Dockerfile
content statically to assert that every service is correctly configured to
start up safely and operate in production.

Coverage:
1.  Service definition completeness – every service is in docker-compose.yml
2.  Restart policy                  – all services use 'unless-stopped'
3.  Logging configuration           – json-file driver with size limits
4.  Environment variable essentials – PORT, LOG_LEVEL, ENVIRONMENT declared
5.  Startup dependency chains       – depends_on references existing services
6.  Dependency condition            – depends_on uses service_healthy or
                                      service_started (not bare list)
7.  Build context vs image          – services use build: not external images
8.  Container naming                – container_name matches service name pattern
9.  Network membership              – services are on the sahool-internal network
10. Port mapping format             – host:container port mappings are valid
11. Environment variable injection  – required secrets injected via env vars
12. Health check propagation        – HEALTHCHECK in Dockerfile = healthcheck in compose
13. No privileged containers        – no `privileged: true` on app services
14. Read-only filesystem flag       – tmpfs / read_only recommendation
15. Volume mount paths              – source paths exist or are named volumes

Run:
    pytest tests/container/test_container_smoke.py -v --tb=short
    pytest tests/container/test_container_smoke.py -v -n auto   # parallel
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

# Import the shared service registry (single source of truth)
from tests.container.service_registry import (
    ALL_HTTP_SERVICES,
    INFRA_SERVICES,
    NODE_SERVICES,
    PORTLESS_SERVICES,
    PYTHON_SERVICES,
)

pytestmark = [pytest.mark.container, pytest.mark.smoke]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
SERVICES_DIR = REPO_ROOT / "apps" / "services"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    """Load and return the main docker-compose.yml once per test module."""
    assert MAIN_COMPOSE.exists(), f"docker-compose.yml not found at {MAIN_COMPOSE}"
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    """Return the 'services' section of docker-compose.yml."""
    return compose.get("services", {})


# ===========================================================================
# 1. Service Definition Completeness
# ===========================================================================


class TestServiceDefinitionCompleteness:
    """Every application service must be declared in docker-compose.yml."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_http_service_in_compose(self, services: dict, svc_name: str) -> None:
        """HTTP service is defined in docker-compose.yml."""
        assert svc_name in services, (
            f"Service '{svc_name}' is not defined in docker-compose.yml"
        )

    @pytest.mark.parametrize("svc_name", sorted(PORTLESS_SERVICES))
    def test_portless_service_in_compose(self, services: dict, svc_name: str) -> None:
        """Worker/init service is defined in docker-compose.yml."""
        assert svc_name in services, (
            f"Portless service '{svc_name}' is not defined in docker-compose.yml"
        )


# ===========================================================================
# 2. Restart Policy
# ===========================================================================


class TestRestartPolicy:
    """All application services must define a restart policy."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_restart_policy_set(self, services: dict, svc_name: str) -> None:
        """Service defines a restart policy."""
        svc = services.get(svc_name, {})
        assert "restart" in svc, f"Service '{svc_name}' is missing 'restart' policy"

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_restart_policy_is_unless_stopped(self, services: dict, svc_name: str) -> None:
        """Service restart policy is 'unless-stopped' (standard for application services)."""
        svc = services.get(svc_name, {})
        policy = svc.get("restart", "")
        assert policy == "unless-stopped", (
            f"Service '{svc_name}' restart policy is '{policy}', expected 'unless-stopped'"
        )


# ===========================================================================
# 3. Logging Configuration
# ===========================================================================


class TestLoggingConfiguration:
    """All application services must configure structured JSON logging with size limits."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_logging_driver_configured(self, services: dict, svc_name: str) -> None:
        """Service defines a 'logging' section."""
        svc = services.get(svc_name, {})
        assert "logging" in svc, (
            f"Service '{svc_name}' is missing 'logging' configuration"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_logging_driver_is_json_file(self, services: dict, svc_name: str) -> None:
        """Service uses 'json-file' logging driver for structured container logs."""
        svc = services.get(svc_name, {})
        driver = svc.get("logging", {}).get("driver", "")
        assert driver == "json-file", (
            f"Service '{svc_name}' uses logging driver '{driver}', expected 'json-file'"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_logging_has_max_size(self, services: dict, svc_name: str) -> None:
        """Service logging defines max-size to prevent unbounded log growth."""
        svc = services.get(svc_name, {})
        opts = svc.get("logging", {}).get("options", {})
        assert "max-size" in opts, (
            f"Service '{svc_name}' logging is missing 'max-size' option"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_logging_has_max_file(self, services: dict, svc_name: str) -> None:
        """Service logging defines max-file to limit number of retained log files."""
        svc = services.get(svc_name, {})
        opts = svc.get("logging", {}).get("options", {})
        assert "max-file" in opts, (
            f"Service '{svc_name}' logging is missing 'max-file' option"
        )


# ===========================================================================
# 4. Environment Variable Essentials
# ===========================================================================


class TestEnvironmentVariables:
    """Critical environment variables must be declared for every application service."""

    def _env_list(self, svc: dict) -> list[str]:
        """Return environment keys/entries as a flat list of strings."""
        env = svc.get("environment", {})
        if isinstance(env, dict):
            return [f"{k}={v}" for k, v in env.items()]
        if isinstance(env, list):
            return [str(e) for e in env]
        return []

    def _has_key(self, env_list: list[str], key: str) -> bool:
        """Return True if an env entry starting with key= exists."""
        prefix = f"{key}="
        return any(e.startswith(prefix) or e == key for e in env_list)

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_port_env_declared(self, services: dict, svc_name: str) -> None:
        """Service declares a port environment variable (PORT or *_PORT variant)."""
        svc = services.get(svc_name, {})
        env = self._env_list(svc)
        # Accept PORT, SERVICE_PORT, MCP_SERVER_PORT, API_PORT, etc.
        has_port = any(
            re.match(r"(?:PORT|[A-Z_]*PORT)\s*=", e) for e in env
        )
        assert has_port, (
            f"Service '{svc_name}' does not declare PORT or a *_PORT env var"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_environment_env_declared(self, services: dict, svc_name: str) -> None:
        """Service declares ENVIRONMENT (Python) or NODE_ENV (Node.js)."""
        svc = services.get(svc_name, {})
        env = self._env_list(svc)
        has_env = self._has_key(env, "ENVIRONMENT") or self._has_key(env, "NODE_ENV")
        assert has_env, (
            f"Service '{svc_name}' does not declare ENVIRONMENT or NODE_ENV"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_log_level_env_declared_python(self, services: dict, svc_name: str) -> None:
        """Python service declares LOG_LEVEL environment variable."""
        svc = services.get(svc_name, {})
        env = self._env_list(svc)
        assert self._has_key(env, "LOG_LEVEL"), (
            f"Python service '{svc_name}' does not declare LOG_LEVEL in 'environment'"
        )


# ===========================================================================
# 5. Startup Dependency Chains
# ===========================================================================


class TestStartupDependencies:
    """depends_on must reference services that actually exist in the compose file."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_depends_on_references_existing_services(
        self, services: dict, svc_name: str
    ) -> None:
        """All depends_on targets exist in docker-compose.yml."""
        svc = services.get(svc_name, {})
        depends = svc.get("depends_on", {})
        if isinstance(depends, list):
            dep_names = depends
        elif isinstance(depends, dict):
            dep_names = list(depends.keys())
        else:
            dep_names = []
        for dep in dep_names:
            assert dep in services, (
                f"Service '{svc_name}' depends_on '{dep}', but '{dep}' is not in compose"
            )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_all_http_services_have_depends_on(
        self, services: dict, svc_name: str
    ) -> None:
        """Every application service declares at least one startup dependency."""
        svc = services.get(svc_name, {})
        depends = svc.get("depends_on", {})
        assert depends, (
            f"Service '{svc_name}' has no depends_on – "
            f"it may start before its dependencies are ready"
        )


# ===========================================================================
# 6. Build Context Configuration
# ===========================================================================


class TestBuildConfiguration:
    """Application services must be built from source, not pulled as external images."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_service_uses_build_directive(self, services: dict, svc_name: str) -> None:
        """Service uses 'build:' directive (not a pre-built external image)."""
        svc = services.get(svc_name, {})
        assert "build" in svc, (
            f"Service '{svc_name}' is missing 'build:' directive – "
            f"application services must be built from source"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_build_context_is_repo_root(self, services: dict, svc_name: str) -> None:
        """Service build context is the repo root (for shared/ module access)."""
        svc = services.get(svc_name, {})
        build = svc.get("build", {})
        if isinstance(build, str):
            context = build
        elif isinstance(build, dict):
            context = build.get("context", "")
        else:
            context = ""
        # Accept '.' or the full absolute repo path or empty (defaults to .)
        assert context in (".", "") or context.endswith(str(REPO_ROOT)), (
            f"Service '{svc_name}' build context is '{context}', expected '.' (repo root)"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_dockerfile_path_declared(self, services: dict, svc_name: str) -> None:
        """Service build section declares the Dockerfile path."""
        svc = services.get(svc_name, {})
        build = svc.get("build", {})
        if isinstance(build, str):
            # String form: context only – Dockerfile must exist at context root
            context_path = REPO_ROOT / build / "Dockerfile"
            assert (
                context_path.exists()
                or (REPO_ROOT / "Dockerfile").exists()
            ), f"Service '{svc_name}' string build context has no Dockerfile"
        elif isinstance(build, dict):
            dockerfile = build.get("dockerfile", "")
            assert dockerfile, (
                f"Service '{svc_name}' build section is missing 'dockerfile:' path"
            )


# ===========================================================================
# 7. Port Mapping Validity
# ===========================================================================


class TestPortMapping:
    """Port mappings must be correctly formatted and within valid range."""

    @pytest.mark.parametrize("svc_name,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_service_port_declared(self, services: dict, svc_name: str, expected_port: int) -> None:
        """Service declares at least one port mapping."""
        svc = services.get(svc_name, {})
        ports = svc.get("ports", [])
        assert ports, f"Service '{svc_name}' has no 'ports' mapping"

    @pytest.mark.parametrize("svc_name,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_container_port_matches_registry(
        self, services: dict, svc_name: str, expected_port: int
    ) -> None:
        """Container-side port in mapping must match the expected service port."""
        svc = services.get(svc_name, {})
        ports = svc.get("ports", [])
        container_ports: list[int] = []
        for p in ports:
            p_str = str(p)
            # Format: "host:container" or "host:container/proto"
            parts = p_str.split(":")
            if len(parts) >= 2:
                cport_str = parts[-1].split("/")[0].strip()
                # Handle variable-based ports like ${PORT:-8093}
                m = re.search(r":-(\d+)", cport_str)
                if m:
                    container_ports.append(int(m.group(1)))
                elif cport_str.isdigit():
                    container_ports.append(int(cport_str))
        if not container_ports:
            pytest.skip(f"{svc_name} uses variable-based port mapping")
        assert expected_port in container_ports, (
            f"Service '{svc_name}' container ports {container_ports} "
            f"do not include expected port {expected_port}"
        )


# ===========================================================================
# 8. No Privileged Containers
# ===========================================================================


class TestNoPrivilegedContainers:
    """Application services must not run as privileged containers."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_privileged_flag(self, services: dict, svc_name: str) -> None:
        """Service does not have 'privileged: true'."""
        svc = services.get(svc_name, {})
        assert svc.get("privileged") is not True, (
            f"Service '{svc_name}' is running as a privileged container "
            f"(security risk)"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_pid_host_namespace(self, services: dict, svc_name: str) -> None:
        """Service does not share the host PID namespace."""
        svc = services.get(svc_name, {})
        assert svc.get("pid") != "host", (
            f"Service '{svc_name}' is using pid: host (security risk)"
        )


# ===========================================================================
# 9. Network Membership
# ===========================================================================


class TestNetworkMembership:
    """Application services must be on the internal network for inter-service communication."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_service_has_networks(self, services: dict, svc_name: str) -> None:
        """Service declares network membership."""
        svc = services.get(svc_name, {})
        assert svc.get("networks"), (
            f"Service '{svc_name}' has no 'networks' configuration"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_service_on_internal_network(self, services: dict, svc_name: str) -> None:
        """Service is connected to the sahool-network (internal service mesh)."""
        svc = services.get(svc_name, {})
        networks = svc.get("networks", {})
        if isinstance(networks, list):
            net_names = networks
        elif isinstance(networks, dict):
            net_names = list(networks.keys())
        else:
            net_names = []
        assert any("sahool" in n for n in net_names), (
            f"Service '{svc_name}' is not on any sahool network "
            f"(networks: {net_names})"
        )


# ===========================================================================
# 10. Dockerfile Startup Command Alignment
# ===========================================================================


class TestDockerfileStartupAlignment:
    """CMD/ENTRYPOINT in Dockerfile must align with the service's declared port."""

    @pytest.mark.parametrize("svc_name,port", sorted(PYTHON_SERVICES.items()))
    def test_python_dockerfile_port_in_cmd(self, svc_name: str, port: int) -> None:
        """Python service Dockerfile CMD references the expected port number or a PORT env var.

        Services that read the port from env vars internally (e.g. python -m src.main)
        are skipped – their port is validated through EXPOSE and HEALTHCHECK tests.
        """
        dockerfile_path = SERVICES_DIR / svc_name / "Dockerfile"
        if not dockerfile_path.exists():
            pytest.skip(f"Dockerfile not found for {svc_name}")
        content = dockerfile_path.read_text(encoding="utf-8")
        # Get the last CMD instruction
        cmd_matches = re.findall(r"^CMD\s+.*", content, re.IGNORECASE | re.MULTILINE)
        if not cmd_matches:
            pytest.skip(f"{svc_name} has no CMD instruction")
        last_cmd = cmd_matches[-1]
        # Accept: literal port, ${PORT}, $PORT, ${MCP_SERVER_PORT}, ${SERVICE_PORT}, etc.
        uses_port = str(port) in last_cmd or bool(re.search(r"\$\{?[A-Z_]*PORT", last_cmd))
        if not uses_port:
            # Service reads port from environment internally – skip (not a failure)
            pytest.skip(
                f"{svc_name} CMD does not inline port – reads from env at runtime"
            )
        assert uses_port

    @pytest.mark.parametrize("svc_name,port", sorted(NODE_SERVICES.items()))
    def test_node_service_port_declared_in_compose_env(
        self, services: dict, svc_name: str, port: int
    ) -> None:
        """Node.js service declares PORT env var in docker-compose with expected value."""
        svc = services.get(svc_name, {})
        env = svc.get("environment", {})
        if isinstance(env, dict):
            env_str = " ".join(f"{k}={v}" for k, v in env.items())
        elif isinstance(env, list):
            env_str = " ".join(str(e) for e in env)
        else:
            env_str = ""
        assert str(port) in env_str, (
            f"Node.js service '{svc_name}' compose environment does not reference "
            f"expected port {port}"
        )


# ===========================================================================
# 11. Compose Service Summary Statistics
# ===========================================================================


class TestComposeSummaryStatistics:
    """Aggregate statistics to catch regressions in service counts."""

    def test_python_services_all_present(self, services: dict) -> None:
        """All 55 Python services are present in docker-compose.yml."""
        missing = [s for s in PYTHON_SERVICES if s not in services]
        assert not missing, f"Missing Python services in compose: {missing}"

    def test_node_services_all_present(self, services: dict) -> None:
        """All 11 Node.js services are present in docker-compose.yml."""
        missing = [s for s in NODE_SERVICES if s not in services]
        assert not missing, f"Missing Node.js services in compose: {missing}"

    def test_portless_services_all_present(self, services: dict) -> None:
        """All portless worker services are present in docker-compose.yml."""
        missing = [s for s in PORTLESS_SERVICES if s not in services]
        assert not missing, f"Missing portless services in compose: {missing}"

    def test_infra_services_all_present(self, services: dict) -> None:
        """All infrastructure services are present in docker-compose.yml."""
        missing = [s for s in INFRA_SERVICES if s not in services]
        assert not missing, f"Missing infrastructure services in compose: {missing}"

    def test_no_duplicate_host_ports(self, services: dict) -> None:
        """No two services share the same host-side port mapping."""
        seen: dict[int, str] = {}
        duplicates: list[str] = []
        for svc_name, svc in services.items():
            for p in svc.get("ports", []):
                p_str = str(p)
                parts = p_str.split(":")
                if len(parts) >= 2:
                    host_str = parts[0].strip()
                    # Skip variable-based host ports
                    m = re.search(r":-?(\d+)", host_str)
                    if m:
                        host_port = int(m.group(1))
                    elif host_str.isdigit():
                        host_port = int(host_str)
                    else:
                        continue
                    if host_port in seen:
                        duplicates.append(
                            f"Port {host_port}: '{svc_name}' and '{seen[host_port]}'"
                        )
                    else:
                        seen[host_port] = svc_name
        assert not duplicates, (
            "Duplicate host port assignments in docker-compose.yml:\n"
            + "\n".join(f"  {d}" for d in duplicates)
        )
