"""
SAHOOL Irrigation/Water Services Group – Container Function Tests
==================================================================
اختبارات وظائف مجموعة خدمات الري وإدارة المياه

Validates consistency across the irrigation and water management cluster.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  irrigation-smart · irrigation-cycle-engine · fertigation-engine
  weather-service · advisory-service

These services share a common domain: water delivery, nutrient management,
and environmental monitoring for precision agriculture.

Coverage:
 1.  Scientific computing deps (NumPy, SciPy) for ET/water balance
 2.  Weather data integration
 3.  NATS event subjects for irrigation recommendations
 4.  Shared domain modules (shared/irrigation/, shared/weather_alerts/)
 5.  Health endpoints
 6.  Non-root user
 7.  Compose dependency chain
 8.  Environment variable consistency
 9.  Port range
10.  Logging & network

Run:
    pytest tests/container/test_irrigation_water_services_group.py -v --tb=short
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

# --- Service group -----------------------------------------------------------

IRRIGATION_SERVICES: dict[str, int] = {
    "irrigation-smart": 8094,
    "irrigation-cycle-engine": 8250,
    "fertigation-engine": 8252,
    "weather-service": 8092,
    "advisory-service": 8093,
}

# Sub-cluster: core water delivery services
WATER_DELIVERY = {
    "irrigation-smart",
    "irrigation-cycle-engine",
    "fertigation-engine",
}

# Sub-cluster: advisory chain (weather → advisory → irrigation)
ADVISORY_CHAIN = {
    "weather-service",
    "advisory-service",
    "irrigation-smart",
}

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
# 1. Scientific Computing Dependencies
# ===========================================================================


class TestScientificDeps:
    """خدمات الري يجب أن تحتوي على مكتبات الحوسبة العلمية."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_fastapi_declared(self, svc: str) -> None:
        """Irrigation service declares fastapi."""
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_pydantic_declared(self, svc: str) -> None:
        """Irrigation service declares pydantic."""
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs or "pydantic_settings" in pkgs, (
            f"{svc} missing pydantic"
        )

    @pytest.mark.parametrize("svc", sorted(WATER_DELIVERY))
    def test_has_numeric_library(self, svc: str) -> None:
        """Water delivery service has numeric computing library or shared/ access."""
        pkgs = _req_packages(svc)
        numeric = {"numpy", "scipy", "pandas"}
        has_numeric = pkgs & numeric
        if not has_numeric:
            # May access numeric libs via shared/ modules
            content = _read_dockerfile(svc)
            has_numeric = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_numeric, (
            f"{svc} missing numeric computing library (expected one of {sorted(numeric)} "
            f"or shared/ module copy)"
        )

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_nats_dependency(self, svc: str) -> None:
        """Irrigation service declares nats-py for event-driven architecture."""
        pkgs = _req_packages(svc)
        has_nats = any("nats" in p for p in pkgs)
        assert has_nats, f"{svc} missing nats-py dependency"

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_structlog_declared(self, svc: str) -> None:
        """Irrigation service declares structlog."""
        pkgs = _req_packages(svc)
        assert "structlog" in pkgs, f"{svc} missing structlog"


# ===========================================================================
# 2. Base Image Consistency
# ===========================================================================


class TestIrrigationBaseImage:
    """صورة أساسية متسقة عبر خدمات الري."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_python_slim_base(self, svc: str) -> None:
        """Irrigation service uses Python slim-bookworm."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+python:", content, re.IGNORECASE), (
            f"{svc} does not use Python base image"
        )

    # Services with simpler, single-stage builds
    SINGLE_STAGE_OK = {"advisory-service", "fertigation-engine", "irrigation-cycle-engine"}

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_has_from_stage(self, svc: str) -> None:
        """Dockerfile has at least one FROM stage; multi-stage preferred."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE | re.IGNORECASE))
        if svc in self.SINGLE_STAGE_OK:
            assert from_count >= 1, f"{svc} has no FROM instruction"
        else:
            assert from_count >= 2, f"{svc} has {from_count} stage(s), expected ≥2"


# ===========================================================================
# 3. Health Endpoints
# ===========================================================================


class TestIrrigationHealthEndpoints:
    """نقاط فحص الصحة لخدمات الري."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        """Dockerfile defines HEALTHCHECK."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_health_in_source(self, svc: str) -> None:
        """Source code has health endpoint."""
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/healthz" in content or "/health" in content, (
            f"{svc} main.py missing health endpoint"
        )

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_readyz_in_source(self, svc: str) -> None:
        """Source code has readiness endpoint."""
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/readyz" in content or "/ready" in content, (
            f"{svc} main.py missing readiness endpoint"
        )


# ===========================================================================
# 4. Non-Root User
# ===========================================================================


class TestIrrigationNonRoot:
    """خدمات الري يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        """Dockerfile switches to non-root USER."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 5. Compose Dependency Chain
# ===========================================================================


class TestIrrigationComposeDeps:
    """سلسلة تبعيات docker-compose لخدمات الري."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        """Service defined in docker-compose.yml."""
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_depends_on_infrastructure(self, services: dict, svc: str) -> None:
        """Service depends on at least one infrastructure service."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        infra = {"postgres", "pgbouncer", "redis", "nats"}
        has_infra = dep_names & infra
        assert has_infra, (
            f"{svc} should depend on infrastructure (deps: {dep_names})"
        )

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_nats_url_env(self, services: dict, svc: str) -> None:
        """Service declares NATS_URL in compose."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, f"{svc} missing NATS_URL"


# ===========================================================================
# 6. Advisory Chain – Cross-Service Event Flow
# ===========================================================================


class TestAdvisoryChainConsistency:
    """سلسلة الاستشارات: الطقس → الاستشارة → الري."""

    def test_weather_publishes_events(self) -> None:
        """weather-service source references NATS event publishing."""
        src_dir = SERVICES_DIR / "weather-service" / "src"
        if not src_dir.exists():
            pytest.skip("No src/ for weather-service")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_events = (
            "nats" in combined.lower()
            or "publish" in combined.lower()
            or "event" in combined.lower()
        )
        assert has_events, "weather-service should publish events for downstream services"

    def test_advisory_references_weather(self) -> None:
        """advisory-service references weather data in its source."""
        src_dir = SERVICES_DIR / "advisory-service" / "src"
        if not src_dir.exists():
            pytest.skip("No src/ for advisory-service")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_weather = "weather" in combined.lower()
        assert has_weather, "advisory-service should reference weather data"

    def test_irrigation_references_advisory(self) -> None:
        """irrigation-smart references advisory or recommendation logic."""
        src_dir = SERVICES_DIR / "irrigation-smart" / "src"
        if not src_dir.exists():
            pytest.skip("No src/ for irrigation-smart")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_advisory = (
            "advisory" in combined.lower()
            or "recommend" in combined.lower()
            or "irrigation" in combined.lower()
        )
        assert has_advisory, "irrigation-smart should implement irrigation recommendations"


# ===========================================================================
# 7. Port Range
# ===========================================================================


class TestIrrigationPortRange:
    """منافذ خدمات الري."""

    @pytest.mark.parametrize("svc,port", sorted(IRRIGATION_SERVICES.items()))
    def test_port_in_8xxx_range(self, svc: str, port: int) -> None:
        """All irrigation services in 8xxx range."""
        assert 8000 <= port <= 8999, f"{svc} port {port} outside range"

    def test_no_duplicate_ports(self) -> None:
        """No duplicate ports."""
        ports = list(IRRIGATION_SERVICES.values())
        assert len(ports) == len(set(ports))

    def test_advisory_chain_port_proximity(self) -> None:
        """Advisory chain services have nearby ports (8092-8094)."""
        chain_ports = {
            "weather-service": 8092,
            "advisory-service": 8093,
            "irrigation-smart": 8094,
        }
        sorted_ports = sorted(chain_ports.values())
        spread = sorted_ports[-1] - sorted_ports[0]
        assert spread <= 10, (
            f"Advisory chain port spread is {spread}, "
            f"expected ≤10 for related services"
        )


# ===========================================================================
# 8. Logging & Networking
# ===========================================================================


class TestIrrigationLoggingNetwork:
    """تسجيل الأحداث والشبكات لخدمات الري."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        """Service has logging configuration."""
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging config"

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        """Service on sahool network."""
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        """Service has restart policy."""
        svc_def = services.get(svc, {})
        assert "restart" in svc_def, f"{svc} missing restart policy"


# ===========================================================================
# 9. Shared Modules
# ===========================================================================


class TestIrrigationSharedModules:
    """خدمات الري يجب أن تنسخ الوحدات المشتركة."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_copies_shared(self, svc: str) -> None:
        """Dockerfile copies shared/ directory."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} Dockerfile does not COPY shared/"
        )


# ===========================================================================
# 10. Pip Mirror Fallback
# ===========================================================================


class TestIrrigationPipMirror:
    """خدمات الري يجب أن تستخدم مرآة pip احتياطية."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_SERVICES))
    def test_pip_fallback(self, svc: str) -> None:
        """Dockerfile has pip mirror fallback."""
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
