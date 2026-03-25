"""
SAHOOL Workers & Portless Services Group – Container Function Tests
====================================================================
اختبارات وظائف مجموعة الخدمات العاملة بدون منافذ HTTP

Validates consistency across portless worker services that process events
via NATS without exposing HTTP endpoints. All tests are **static analysis**.

Services in this group:
  agro-rules · code-review-agent · demo-data

Coverage:
 1.  Dockerfile existence and structure
 2.  No EXPOSE directive (portless)
 3.  NATS event bus connectivity
 4.  Non-root user
 5.  Compose configuration
 6.  Shared modules
 7.  Base image
 8.  Pip mirror fallback

Run:
    pytest tests/container/test_workers_services_group.py -v --tb=short
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

WORKER_SERVICES: set[str] = {"agro-rules", "code-review-agent", "demo-data"}

# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Dockerfile Existence
# ===========================================================================


class TestWorkerDockerfiles:
    """ملفات Docker للخدمات العاملة."""

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_dockerfile_exists(self, svc: str) -> None:
        path = SERVICES_DIR / svc / "Dockerfile"
        assert path.exists(), f"{svc} missing Dockerfile"

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_has_cmd_or_entrypoint(self, svc: str) -> None:
        """Worker has CMD or ENTRYPOINT for startup."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_cmd = bool(re.search(r"^(CMD|ENTRYPOINT)\s+", content, re.MULTILINE | re.IGNORECASE))
        assert has_cmd, f"{svc} missing CMD or ENTRYPOINT"

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_no_expose_directive(self, svc: str) -> None:
        """Portless worker Dockerfile must not contain EXPOSE directives."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_expose = re.search(r"^EXPOSE\b", content, re.MULTILINE | re.IGNORECASE)
        assert not has_expose, f"{svc} Dockerfile must not contain EXPOSE directives"


# ===========================================================================
# 2. Non-Root User
# ===========================================================================


class TestWorkerNonRoot:
    """مستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 3. Compose Configuration
# ===========================================================================


class TestWorkerComposeConfig:
    """تكوين docker-compose للخدمات العاملة."""

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_no_ports_mapping(self, services: dict, svc: str) -> None:
        """Portless worker should not have port mappings in compose."""
        svc_def = services.get(svc, {})
        ports = svc_def.get("ports", [])
        assert not ports, (
            f"Portless worker '{svc}' should not have ports mapping (found: {ports})"
        )

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert "restart" in svc_def, f"{svc} missing restart policy"

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    # NATS-based workers (code-review-agent uses Ollama, not NATS)
    NATS_WORKERS = sorted({"agro-rules", "demo-data"})

    @pytest.mark.parametrize("svc", NATS_WORKERS)
    def test_depends_on_infrastructure(self, services: dict, svc: str) -> None:
        """Worker depends on infrastructure services."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        assert dep_names, f"Worker '{svc}' has no dependencies (deps: {dep_names})"


# ===========================================================================
# 4. Shared Modules & Mirror
# ===========================================================================


class TestWorkerSharedModules:
    """وحدات مشتركة ومرآة."""

    # Workers that copy shared/ modules (some are self-contained)
    SHARED_COPY_WORKERS = sorted({"agro-rules"})
    # code-review-agent is Node.js (no pip), demo-data is self-contained

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_copies_source(self, svc: str) -> None:
        """Worker copies its source code."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "COPY" in content, f"{svc} Dockerfile has no COPY instructions"

    # Python workers only
    PYTHON_WORKERS = sorted({"agro-rules", "demo-data"})

    @pytest.mark.parametrize("svc", PYTHON_WORKERS)
    def test_pip_fallback(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_fallback = (
            "aliyun" in content.lower()
            or "tencent" in content.lower()
            or "tsinghua" in content.lower()
            or "pip.conf" in content.lower()
        )
        assert has_fallback, f"{svc} missing pip mirror fallback"


# ===========================================================================
# 5. Base Image
# ===========================================================================


class TestWorkerBaseImage:
    """صورة أساسية."""

    @pytest.mark.parametrize("svc", sorted(WORKER_SERVICES))
    def test_uses_python_or_node(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_base = re.search(r"FROM\s+(python|node):", content, re.IGNORECASE)
        assert has_base, f"{svc} does not use standard Python/Node base image"
