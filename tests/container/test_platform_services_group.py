"""
SAHOOL Platform Infrastructure & Gateway Services Group – Container Function Tests
====================================================================================
اختبارات وظائف مجموعة خدمات البنية التحتية والبوابات

Validates consistency across platform infrastructure services: gateways,
configuration, code review, agent registry, and developer tools.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  ws-gateway · mcp-server · ussd-gateway · provider-config
  code-review-service · agent-registry · skills-service

Coverage:
 1.  Core framework (FastAPI, Pydantic)
 2.  Gateway-specific patterns (WebSocket, USSD)
 3.  NATS connectivity
 4.  Health endpoints
 5.  Non-root user
 6.  Compose configuration
 7.  Port range
 8.  Shared modules & pip mirror
 9.  Base image
10.  MCP server specifics

Run:
    pytest tests/container/test_platform_services_group.py -v --tb=short
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

PLATFORM_SERVICES: dict[str, int] = {
    "ws-gateway": 8081,
    "mcp-server": 8201,
    "ussd-gateway": 8183,
    "provider-config": 8104,
    "code-review-service": 8102,
    "agent-registry": 8160,
    "skills-service": 8121,
}

GATEWAY_SERVICES = {"ws-gateway", "ussd-gateway", "mcp-server"}
REGISTRY_SERVICES = {"agent-registry", "provider-config", "skills-service"}

# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def _read_requirements(svc: str) -> str:
    if svc not in _requirements_cache:
        path = SERVICES_DIR / svc / "requirements.txt"
        _requirements_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _requirements_cache[svc]


def _req_packages(svc: str) -> set[str]:
    text = _read_requirements(svc)
    pkgs: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[>=<!\[;]", line)[0].strip().lower().replace("-", "_")
        if name:
            pkgs.add(name)
    return pkgs


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Core Framework
# ===========================================================================


class TestPlatformFrameworkDeps:
    """مكتبات الإطار الأساسي."""

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_fastapi_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_pydantic_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs or "pydantic_settings" in pkgs, (
            f"{svc} missing pydantic"
        )


# ===========================================================================
# 2. Gateway-Specific Patterns
# ===========================================================================


class TestGatewayPatterns:
    """أنماط خاصة بالبوابات."""

    def test_ws_gateway_websocket_support(self) -> None:
        """ws-gateway references WebSocket."""
        pkgs = _req_packages("ws-gateway")
        dockerfile = _read_dockerfile("ws-gateway")
        has_ws = (
            any("websocket" in p for p in pkgs)
            or "websocket" in dockerfile.lower()
            or any("ws" in p for p in pkgs)
        )
        # Also check source
        main_path = SERVICES_DIR / "ws-gateway" / "src" / "main.py"
        if main_path.exists():
            content = main_path.read_text("utf-8")
            has_ws = has_ws or "websocket" in content.lower() or "ws" in content.lower()
        assert has_ws, "ws-gateway should support WebSocket connections"

    def test_mcp_server_references_mcp(self) -> None:
        """mcp-server references Model Context Protocol."""
        src_dir = SERVICES_DIR / "mcp-server" / "src"
        if not src_dir.exists():
            pytest.skip("No src/ for mcp-server")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_mcp = "mcp" in combined.lower() or "context" in combined.lower()
        assert has_mcp, "mcp-server should reference MCP protocol"


# ===========================================================================
# 3. Health Endpoints
# ===========================================================================


class TestPlatformHealthEndpoints:
    """نقاط فحص الصحة."""

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_health_in_source(self, svc: str) -> None:
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/healthz" in content or "/health" in content, (
            f"{svc} main.py missing health endpoint"
        )


# ===========================================================================
# 4. Non-Root User
# ===========================================================================


class TestPlatformNonRoot:
    """مستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 5. Compose Configuration
# ===========================================================================


class TestPlatformComposeConfig:
    """تكوين docker-compose."""

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert svc_def.get("restart") == "unless-stopped", (
            f"{svc} missing restart: unless-stopped"
        )

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging"

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    # Services that require NATS event bus
    NATS_REQUIRED = sorted(set(PLATFORM_SERVICES) - {"mcp-server", "code-review-service", "skills-service"})

    @pytest.mark.parametrize("svc", NATS_REQUIRED)
    def test_nats_url_env(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, f"{svc} missing NATS_URL"


# ===========================================================================
# 6. Port Range
# ===========================================================================


class TestPlatformPortRange:
    """منافذ الخدمات."""

    @pytest.mark.parametrize("svc,port", sorted(PLATFORM_SERVICES.items()))
    def test_port_in_8xxx_range(self, svc: str, port: int) -> None:
        assert 8000 <= port <= 8999, f"{svc} port {port} outside 8xxx range"

    def test_no_duplicate_ports(self) -> None:
        ports = list(PLATFORM_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 7. Shared Modules & Mirror
# ===========================================================================


class TestPlatformSharedModules:
    """وحدات مشتركة ومرآة."""

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_copies_shared(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} does not COPY shared/"
        )

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_pip_fallback(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_fallback = (
            "aliyun" in content.lower()
            or "tencent" in content.lower()
            or "tsinghua" in content.lower()
            or "pip.conf" in content.lower()
            or "pip-install.sh" in content.lower()
        )
        assert has_fallback, f"{svc} missing pip mirror fallback"

    @pytest.mark.parametrize("svc", sorted(PLATFORM_SERVICES))
    def test_python_base(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+python:", content, re.IGNORECASE), (
            f"{svc} does not use Python base image"
        )
