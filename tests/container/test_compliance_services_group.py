"""
SAHOOL Compliance & Specialty Services Group – Container Function Tests
========================================================================
اختبارات وظائف مجموعة خدمات الامتثال والخدمات المتخصصة

Validates consistency across compliance, messaging bots, low-code automation,
and specialty services. All tests are **static analysis**.

Services in this group:
  globalgap-compliance · whatsapp-bot-service · lowcode-engine
  astronomical-calendar · logistics-service · digital-twin-engine

Coverage:
 1.  Core framework dependencies
 2.  Domain-specific patterns (compliance, bot, simulation)
 3.  Health endpoints
 4.  Non-root user
 5.  Compose configuration
 6.  Port range
 7.  Shared modules & pip mirror
 8.  Base image

Run:
    pytest tests/container/test_compliance_services_group.py -v --tb=short
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

COMPLIANCE_SERVICES: dict[str, int] = {
    "globalgap-compliance": 8128,
    "whatsapp-bot-service": 8240,
    "lowcode-engine": 8132,
    "astronomical-calendar": 8111,
    "logistics-service": 8167,
    "digital-twin-engine": 8253,
}

# Sub-clusters
COMPLIANCE_STRICT = {"globalgap-compliance"}
BOT_SERVICES = {"whatsapp-bot-service"}
SIMULATION_SERVICES = {"digital-twin-engine"}

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


class TestComplianceFrameworkDeps:
    """المكتبات الأساسية."""

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_fastapi_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_pydantic_declared(self, svc: str) -> None:
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs or "pydantic_settings" in pkgs, (
            f"{svc} missing pydantic"
        )


# ===========================================================================
# 2. Domain-Specific Patterns
# ===========================================================================


class TestDomainSpecific:
    """أنماط خاصة بالمجال."""

    def test_globalgap_compliance_references(self) -> None:
        """globalgap-compliance references compliance/audit logic."""
        src_dir = SERVICES_DIR / "globalgap-compliance" / "src"
        if not src_dir.exists():
            pytest.skip("No src/")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_compliance = (
            "compliance" in combined.lower()
            or "globalgap" in combined.lower()
            or "checklist" in combined.lower()
            or "audit" in combined.lower()
        )
        assert has_compliance, "globalgap-compliance should reference compliance logic"

    def test_digital_twin_simulation(self) -> None:
        """digital-twin-engine references simulation/model logic."""
        src_dir = SERVICES_DIR / "digital-twin-engine" / "src"
        if not src_dir.exists():
            pytest.skip("No src/")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_sim = (
            "twin" in combined.lower()
            or "simulation" in combined.lower()
            or "model" in combined.lower()
        )
        assert has_sim, "digital-twin-engine should reference simulation logic"

    def test_whatsapp_bot_messaging(self) -> None:
        """whatsapp-bot-service references messaging."""
        src_dir = SERVICES_DIR / "whatsapp-bot-service" / "src"
        if not src_dir.exists():
            pytest.skip("No src/")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_msg = (
            "whatsapp" in combined.lower()
            or "message" in combined.lower()
            or "bot" in combined.lower()
            or "webhook" in combined.lower()
        )
        assert has_msg, "whatsapp-bot-service should reference messaging"

    def test_astronomical_calendar_references(self) -> None:
        """astronomical-calendar references calendar/timing logic."""
        src_dir = SERVICES_DIR / "astronomical-calendar" / "src"
        if not src_dir.exists():
            pytest.skip("No src/")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:15]:
            combined += f.read_text("utf-8", errors="ignore")
        has_cal = (
            "calendar" in combined.lower()
            or "astronomical" in combined.lower()
            or "hijri" in combined.lower()
            or "prayer" in combined.lower()
            or "moon" in combined.lower()
        )
        assert has_cal, "astronomical-calendar should reference calendar logic"


# ===========================================================================
# 3. Health Endpoints
# ===========================================================================


class TestComplianceHealthEndpoints:
    """نقاط فحص الصحة."""

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
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


class TestComplianceNonRoot:
    """مستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
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


class TestComplianceComposeConfig:
    """تكوين docker-compose."""

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert svc_def.get("restart") == "unless-stopped", (
            f"{svc} missing restart: unless-stopped"
        )

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging"

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    # Services that require NATS (astronomical-calendar uses HTTP only)
    NATS_REQUIRED = sorted(set(COMPLIANCE_SERVICES) - {"astronomical-calendar"})

    @pytest.mark.parametrize("svc", NATS_REQUIRED)
    def test_nats_url_env(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, f"{svc} missing NATS_URL"


# ===========================================================================
# 6. Port Range
# ===========================================================================


class TestCompliancePortRange:
    """منافذ الخدمات."""

    @pytest.mark.parametrize("svc,port", sorted(COMPLIANCE_SERVICES.items()))
    def test_port_in_8xxx_range(self, svc: str, port: int) -> None:
        assert 8000 <= port <= 8999, f"{svc} port {port} outside range"

    def test_no_duplicate_ports(self) -> None:
        ports = list(COMPLIANCE_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 7. Shared Modules & Mirror
# ===========================================================================


class TestComplianceSharedModules:
    """وحدات مشتركة ومرآة."""

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_copies_shared(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} does not COPY shared/"
        )

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
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

    @pytest.mark.parametrize("svc", sorted(COMPLIANCE_SERVICES))
    def test_python_base(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+python:", content, re.IGNORECASE), (
            f"{svc} does not use Python base image"
        )
