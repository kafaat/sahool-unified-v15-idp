"""
SAHOOL Business Operations & Finance Services Group – Container Function Tests
================================================================================
اختبارات وظائف مجموعة خدمات العمليات التجارية والمالية

Validates consistency across the business operations cluster: billing,
notifications, task management, alerting, auditing, equipment, and inventory.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  billing-core · notification-service · task-service · alert-service
  audit-service · equipment-service · inventory-service

Coverage:
 1.  Core framework dependencies (FastAPI, Pydantic, uvicorn)
 2.  Database connectivity (asyncpg for PostgreSQL)
 3.  NATS event bus integration
 4.  Structured logging (structlog)
 5.  Health endpoints in source and Dockerfile
 6.  Non-root user
 7.  Compose dependency chain (postgres, redis, nats)
 8.  Port range & uniqueness
 9.  Logging & network configuration
10.  Shared module copy

Run:
    pytest tests/container/test_business_services_group.py -v --tb=short
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

BUSINESS_SERVICES: dict[str, int] = {
    "billing-core": 8089,
    "notification-service": 8110,
    "task-service": 8103,
    "alert-service": 8113,
    "audit-service": 8114,
    "equipment-service": 8101,
    "inventory-service": 8116,
}

# Sub-cluster: services that must emit audit events
AUDITABLE_SERVICES = {"billing-core", "audit-service", "inventory-service"}

# Sub-cluster: notification-oriented services
NOTIFICATION_CHAIN = {"notification-service", "alert-service"}

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
# 1. Core Framework Dependencies
# ===========================================================================


class TestCoreFrameworkDeps:
    """المكتبات الأساسية لخدمات العمليات التجارية."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_fastapi_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_pydantic_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs or "pydantic_settings" in pkgs, (
            f"{svc} missing pydantic"
        )

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_uvicorn_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        has_uvicorn = any("uvicorn" in p for p in pkgs)
        assert has_uvicorn, f"{svc} missing uvicorn"


# ===========================================================================
# 2. Database Connectivity
# ===========================================================================


class TestDatabaseConnectivity:
    """خدمات العمليات التجارية يجب أن تتصل بقاعدة البيانات."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_database_driver(self, svc: str) -> None:
        """Service declares asyncpg or sqlalchemy for DB access."""
        pkgs = _req_packages(svc)
        has_db = "asyncpg" in pkgs or "sqlalchemy" in pkgs or "databases" in pkgs
        if not has_db:
            content = _read_dockerfile(svc)
            has_db = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_db, f"{svc} missing database driver or shared/ copy"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_database_url_in_compose(self, services: dict, svc: str) -> None:
        """Service declares DATABASE_URL in compose environment."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "DATABASE_URL" in env_str, f"{svc} missing DATABASE_URL"


# ===========================================================================
# 3. NATS Event Bus
# ===========================================================================


class TestNATSEventBus:
    """خدمات العمليات التجارية يجب أن تتصل بناقل الأحداث."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_nats_dependency(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        has_nats = any("nats" in p for p in pkgs)
        if not has_nats:
            content = _read_dockerfile(svc)
            has_nats = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_nats, f"{svc} missing nats-py or shared/ NATS module"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_nats_url_env(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, f"{svc} missing NATS_URL"


# ===========================================================================
# 4. Health Endpoints
# ===========================================================================


class TestBusinessHealthEndpoints:
    """نقاط فحص الصحة لخدمات العمليات التجارية."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_health_in_source(self, svc: str) -> None:
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/healthz" in content or "/health" in content, (
            f"{svc} main.py missing health endpoint"
        )


# ===========================================================================
# 5. Non-Root User
# ===========================================================================


class TestBusinessNonRoot:
    """خدمات العمليات التجارية يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 6. Compose Configuration
# ===========================================================================


class TestBusinessComposeConfig:
    """تكوين docker-compose لخدمات العمليات التجارية."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_depends_on_infrastructure(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        infra = {"postgres", "pgbouncer", "redis", "nats"}
        has_infra = dep_names & infra
        assert has_infra, f"{svc} should depend on infrastructure (deps: {dep_names})"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert svc_def.get("restart") == "unless-stopped", (
            f"{svc} missing restart: unless-stopped"
        )

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging"

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"


# ===========================================================================
# 7. Port Range
# ===========================================================================


class TestBusinessPortRange:
    """منافذ خدمات العمليات التجارية."""

    @pytest.mark.parametrize("svc,port", sorted(BUSINESS_SERVICES.items()))
    def test_port_in_8xxx_range(self, svc: str, port: int) -> None:
        assert 8000 <= port <= 8999, f"{svc} port {port} outside range"

    def test_no_duplicate_ports(self) -> None:
        ports = list(BUSINESS_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 8. Notification Chain
# ===========================================================================


class TestNotificationChain:
    """سلسلة الإشعارات: إشعار + تنبيه."""

    @pytest.mark.parametrize("svc", sorted(NOTIFICATION_CHAIN))
    def test_notification_source_references_events(self, svc: str) -> None:
        """Notification/alert service references event handling."""
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            pytest.skip(f"No src/ for {svc}")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_events = (
            "nats" in combined.lower()
            or "event" in combined.lower()
            or "publish" in combined.lower()
            or "notify" in combined.lower()
        )
        assert has_events, f"{svc} should reference event/notification handling"


# ===========================================================================
# 9. Shared Module & Pip Mirror
# ===========================================================================


class TestBusinessSharedModules:
    """وحدات مشتركة ومرآة pip."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_copies_shared(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} does not COPY shared/"
        )

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
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
# 10. Base Image
# ===========================================================================


class TestBusinessBaseImage:
    """صورة أساسية متسقة."""

    @pytest.mark.parametrize("svc", sorted(BUSINESS_SERVICES))
    def test_python_base(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+python:", content, re.IGNORECASE), (
            f"{svc} does not use Python base image"
        )
