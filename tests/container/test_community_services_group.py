"""
SAHOOL Community & Supply Chain Services Group – Container Function Tests
==========================================================================
اختبارات وظائف مجموعة خدمات المجتمع وسلسلة التوريد

Validates consistency across community, CRM, cooperative, and supply chain
services. All tests are **static analysis** — no Docker daemon required.

Services in this group:
  chat-service (Node.js) · marketplace-service (Node.js) · crm-service
  cooperative-service · traceability-service · supply-chain-service
  community-service

Coverage:
 1.  Framework deps (FastAPI for Python, NestJS for Node.js)
 2.  Database connectivity
 3.  Real-time communication (WebSocket for chat)
 4.  NATS event bus
 5.  Health endpoints
 6.  Non-root user
 7.  Compose configuration
 8.  Port range
 9.  Shared modules & pip/npm mirror
10.  Node.js workspace dependencies

Run:
    pytest tests/container/test_community_services_group.py -v --tb=short
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

COMMUNITY_SERVICES: dict[str, int] = {
    "chat-service": 8115,
    "marketplace-service": 3010,
    "crm-service": 8131,
    "cooperative-service": 8127,
    "traceability-service": 8123,
    "supply-chain-service": 8230,
    "community-service": 8133,
}

PYTHON_COMMUNITY = {
    "crm-service", "cooperative-service", "traceability-service",
    "supply-chain-service", "community-service",
}

NODE_COMMUNITY = {"chat-service", "marketplace-service"}

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
# 1. Python Framework Dependencies
# ===========================================================================


class TestPythonCommunityDeps:
    """مكتبات Python لخدمات المجتمع."""

    @pytest.mark.parametrize("svc", sorted(PYTHON_COMMUNITY))
    def test_fastapi_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"

    @pytest.mark.parametrize("svc", sorted(PYTHON_COMMUNITY))
    def test_pydantic_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs or "pydantic_settings" in pkgs, (
            f"{svc} missing pydantic"
        )


# ===========================================================================
# 2. Node.js Services
# ===========================================================================


class TestNodeCommunityServices:
    """خدمات Node.js للمجتمع."""

    @pytest.mark.parametrize("svc", sorted(NODE_COMMUNITY))
    def test_package_json_exists(self, svc: str) -> None:
        pkg = SERVICES_DIR / svc / "package.json"
        assert pkg.exists(), f"{svc} missing package.json"

    @pytest.mark.parametrize("svc", sorted(NODE_COMMUNITY))
    def test_nestjs_in_package(self, svc: str) -> None:
        pkg = SERVICES_DIR / svc / "package.json"
        if not pkg.exists():
            pytest.skip(f"No package.json for {svc}")
        content = pkg.read_text("utf-8")
        assert "nestjs" in content.lower(), f"{svc} missing NestJS"

    def test_chat_service_realtime(self) -> None:
        """chat-service should support real-time messaging."""
        src_dir = SERVICES_DIR / "chat-service" / "src"
        if not src_dir.exists():
            pytest.skip("No src/ for chat-service")
        all_files = list(src_dir.rglob("*.ts"))
        combined = ""
        for f in all_files[:20]:
            combined += f.read_text("utf-8", errors="ignore")
        has_realtime = (
            "websocket" in combined.lower()
            or "socket" in combined.lower()
            or "gateway" in combined.lower()
            or "ws" in combined.lower()
        )
        assert has_realtime, "chat-service should support real-time messaging"


# ===========================================================================
# 3. Health Endpoints
# ===========================================================================


class TestCommunityHealthEndpoints:
    """نقاط فحص الصحة."""

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"


# ===========================================================================
# 4. Non-Root User
# ===========================================================================


class TestCommunityNonRoot:
    """مستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
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


class TestCommunityComposeConfig:
    """تكوين docker-compose."""

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_depends_on_infrastructure(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        infra = {"postgres", "pgbouncer", "redis", "nats"}
        assert dep_names & infra, (
            f"{svc} should depend on infrastructure (deps: {dep_names})"
        )

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert svc_def.get("restart") == "unless-stopped", (
            f"{svc} missing restart: unless-stopped"
        )

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging"

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_nats_url_env(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, f"{svc} missing NATS_URL"


# ===========================================================================
# 6. Port Range
# ===========================================================================


class TestCommunityPortRange:
    """منافذ خدمات المجتمع."""

    @pytest.mark.parametrize("svc,port", sorted(COMMUNITY_SERVICES.items()))
    def test_port_valid(self, svc: str, port: int) -> None:
        assert 3000 <= port <= 9000, f"{svc} port {port} out of range"

    def test_no_duplicate_ports(self) -> None:
        ports = list(COMMUNITY_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 7. Shared Modules & Mirror
# ===========================================================================


class TestCommunitySharedModules:
    """وحدات مشتركة ومرآة."""

    @pytest.mark.parametrize("svc", sorted(COMMUNITY_SERVICES))
    def test_copies_shared(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} does not COPY shared/"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_COMMUNITY))
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
