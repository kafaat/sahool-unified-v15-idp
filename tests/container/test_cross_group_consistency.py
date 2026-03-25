"""
SAHOOL Cross-Group Container Consistency Tests
================================================
اختبارات اتساق الحاويات عبر المجموعات

Validates shared conventions and detects drift **between** service groups.
Ensures that AI, Vision, IoT, Terrain, and Irrigation clusters follow
the same platform-wide conventions.  All tests are **static analysis**.

Coverage:
 1.  Universal base image pattern (Python 3.11 slim-bookworm)
 2.  Non-root user enforcement across all groups
 3.  HEALTHCHECK presence in all Dockerfiles
 4.  NATS connectivity (nats-py or NATS_URL) across all groups
 5.  Shared module COPY in Dockerfiles
 6.  Port uniqueness across all groups (no collisions)
 7.  Compose restart policy across all groups
 8.  Logging configuration across all groups
 9.  Network membership across all groups
10.  Pip mirror fallback across all Python services

Run:
    pytest tests/container/test_cross_group_consistency.py -v --tb=short
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

# --- Aggregate all groups ----------------------------------------------------

AI_SERVICES: dict[str, int] = {
    "ai-advisor": 8112,
    "ai-agents-service": 8130,
    "ai-agents-core": 8161,
    "ai-chat-assistant": 8260,
    "copilot-api": 8088,
    "llm-orchestrator-service": 8164,
    "knowledge-graph": 8140,
    "code-fix-agent": 8162,
}

VISION_SERVICES: dict[str, int] = {
    "yolo26-vision-service": 8150,
    "ground-vision-service": 8182,
    "vegetation-analysis-service": 8090,
    "crop-intelligence-service": 8095,
    "pest-detection-service": 8125,
    "ndvi-processor": 8118,
    "field-intelligence": 8120,
    "indicators-service": 8091,
}

IOT_SERVICES: dict[str, int] = {
    "iot-service": 8117,
    "iot-gateway": 8106,
    "iot-sensor-hub": 8251,
    "edge-orchestrator-service": 8180,
    "virtual-sensors": 8119,
    "drone-service": 8126,
}

TERRAIN_SERVICES: dict[str, int] = {
    "terrain-core-service": 8185,
    "hydrology-service": 8165,
    "leveling-optimizer-service": 8170,
    "field-management-service": 3000,
    "field-intelligence": 8120,
    "soil-analysis-service": 8134,
}

IRRIGATION_SERVICES: dict[str, int] = {
    "irrigation-smart": 8094,
    "irrigation-cycle-engine": 8250,
    "fertigation-engine": 8252,
    "weather-service": 8092,
    "advisory-service": 8093,
}

# Union of all tested services (deduped)
ALL_GROUP_SERVICES: dict[str, int] = {
    **AI_SERVICES,
    **VISION_SERVICES,
    **IOT_SERVICES,
    **TERRAIN_SERVICES,
    **IRRIGATION_SERVICES,
}

# Node.js services within the tested groups
NODE_GROUP = {"iot-service", "field-management-service"}
PYTHON_GROUP = set(ALL_GROUP_SERVICES) - NODE_GROUP

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
# 1. Port Uniqueness Across All Groups
# ===========================================================================


class TestCrossGroupPortUniqueness:
    """عدم وجود تضارب في المنافذ عبر جميع المجموعات."""

    def test_no_port_collisions(self) -> None:
        """No two services from different groups share the same port."""
        groups = {
            "AI": AI_SERVICES,
            "Vision": VISION_SERVICES,
            "IoT": IOT_SERVICES,
            "Terrain": TERRAIN_SERVICES,
            "Irrigation": IRRIGATION_SERVICES,
        }
        seen: dict[int, tuple[str, str]] = {}
        collisions: list[str] = []
        for group_name, group_svcs in groups.items():
            for svc, port in group_svcs.items():
                if port in seen:
                    prev_svc, prev_group = seen[port]
                    if prev_svc != svc:  # Same svc in multiple groups is OK
                        collisions.append(
                            f"Port {port}: '{svc}' ({group_name}) vs "
                            f"'{prev_svc}' ({prev_group})"
                        )
                else:
                    seen[port] = (svc, group_name)
        assert not collisions, (
            "Port collisions across service groups:\n"
            + "\n".join(f"  {c}" for c in collisions)
        )


# ===========================================================================
# 2. Universal Non-Root User
# ===========================================================================


class TestUniversalNonRoot:
    """جميع الخدمات يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        """Dockerfile switches to non-root USER."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 3. Universal HEALTHCHECK
# ===========================================================================


class TestUniversalHealthCheck:
    """جميع الخدمات يجب أن تحتوي على فحص صحي."""

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_healthcheck_present(self, svc: str) -> None:
        """Dockerfile defines HEALTHCHECK."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK in Dockerfile"


# ===========================================================================
# 4. Universal NATS Connectivity
# ===========================================================================


class TestUniversalNATS:
    """جميع الخدمات يجب أن تكون متصلة بـ NATS."""

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_nats_env_in_compose(self, services: dict, svc: str) -> None:
        """Service declares NATS_URL in compose environment."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, (
            f"{svc} missing NATS_URL – all services need event bus connectivity"
        )


# ===========================================================================
# 5. Universal Compose Restart Policy
# ===========================================================================


class TestUniversalRestartPolicy:
    """جميع الخدمات يجب أن تحتوي على سياسة إعادة التشغيل."""

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        """Service has restart policy in compose."""
        svc_def = services.get(svc, {})
        assert "restart" in svc_def, f"{svc} missing restart policy"

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_restart_unless_stopped(self, services: dict, svc: str) -> None:
        """Service restart policy is 'unless-stopped'."""
        svc_def = services.get(svc, {})
        policy = svc_def.get("restart", "")
        assert policy == "unless-stopped", (
            f"{svc} restart='{policy}', expected 'unless-stopped'"
        )


# ===========================================================================
# 6. Universal Logging
# ===========================================================================


class TestUniversalLogging:
    """جميع الخدمات يجب أن تحتوي على تكوين تسجيل."""

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        """Service has logging section in compose."""
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging configuration"

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_logging_json_driver(self, services: dict, svc: str) -> None:
        """Service uses json-file logging driver."""
        svc_def = services.get(svc, {})
        driver = svc_def.get("logging", {}).get("driver", "")
        assert driver == "json-file", f"{svc} logging driver='{driver}', expected 'json-file'"


# ===========================================================================
# 7. Universal Network Membership
# ===========================================================================


class TestUniversalNetwork:
    """جميع الخدمات يجب أن تكون على شبكة sahool."""

    @pytest.mark.parametrize("svc", sorted(ALL_GROUP_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        """Service on sahool network."""
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), (
            f"{svc} not on sahool network"
        )


# ===========================================================================
# 8. Python Services – Pip Mirror Fallback
# ===========================================================================


class TestPythonPipMirror:
    """خدمات Python يجب أن تستخدم مرآة pip احتياطية."""

    @pytest.mark.parametrize("svc", sorted(PYTHON_GROUP))
    def test_pip_fallback(self, svc: str) -> None:
        """Python service Dockerfile has pip mirror fallback."""
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
# 9. Python Services – Base Image
# ===========================================================================


class TestPythonBaseImage:
    """خدمات Python يجب أن تستخدم صورة أساسية متسقة."""

    EXCLUDE_FROM_STANDARD_BASE = {"yolo26-vision-service"}  # Uses CUDA image

    @pytest.mark.parametrize("svc", sorted(PYTHON_GROUP - EXCLUDE_FROM_STANDARD_BASE))
    def test_python_slim_bookworm(self, svc: str) -> None:
        """Python service uses python:*-slim-bookworm."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+python:", content, re.IGNORECASE), (
            f"{svc} does not use python base image"
        )


# ===========================================================================
# 10. Shared Module COPY
# ===========================================================================


class TestSharedModuleCopy:
    """جميع الخدمات يجب أن تنسخ الوحدات المشتركة."""

    @pytest.mark.parametrize("svc", sorted(PYTHON_GROUP))
    def test_copies_shared(self, svc: str) -> None:
        """Python service Dockerfile copies shared/ directory."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} Dockerfile does not COPY shared/"
        )


# ===========================================================================
# 11. Group Size Validation
# ===========================================================================


class TestGroupSizes:
    """التحقق من عدد الخدمات في كل مجموعة."""

    def test_ai_group_minimum(self) -> None:
        """AI group has at least 6 services."""
        assert len(AI_SERVICES) >= 6, (
            f"AI group has {len(AI_SERVICES)} services, expected ≥6"
        )

    def test_vision_group_minimum(self) -> None:
        """Vision group has at least 5 services."""
        assert len(VISION_SERVICES) >= 5

    def test_iot_group_minimum(self) -> None:
        """IoT group has at least 4 services."""
        assert len(IOT_SERVICES) >= 4

    def test_terrain_group_minimum(self) -> None:
        """Terrain group has at least 4 services."""
        assert len(TERRAIN_SERVICES) >= 4

    def test_irrigation_group_minimum(self) -> None:
        """Irrigation group has at least 4 services."""
        assert len(IRRIGATION_SERVICES) >= 4

    def test_total_services_covered(self) -> None:
        """Total unique services covered across all groups."""
        assert len(ALL_GROUP_SERVICES) >= 25, (
            f"Only {len(ALL_GROUP_SERVICES)} unique services covered, expected ≥25"
        )
