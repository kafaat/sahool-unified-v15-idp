"""
SAHOOL IoT/Edge Services Group – Container Function Tests
==========================================================
اختبارات وظائف مجموعة خدمات إنترنت الأشياء والحافة

Validates that IoT and edge-computing services share consistent patterns
for device communication, sensor data ingestion, and edge orchestration.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  iot-service (Node.js) · iot-gateway · iot-sensor-hub · edge-orchestrator-service
  virtual-sensors · drone-service

Coverage:
 1.  IoT protocol dependencies (MQTT, WebSocket)
 2.  NATS connectivity for sensor event bridging
 3.  Init system usage (tini) for signal handling
 4.  Node.js vs Python consistency within sub-clusters
 5.  Edge storage provisioning (models, data, logs)
 6.  Health endpoint patterns
 7.  Non-root user
 8.  Compose dependency chain (infrastructure)
 9.  Port range consistency
10.  Real-time communication dependencies

Run:
    pytest tests/container/test_iot_edge_services_group.py -v --tb=short
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

IOT_EDGE_SERVICES: dict[str, int] = {
    "iot-service": 8117,         # Node.js NestJS
    "iot-gateway": 8106,         # Python – MQTT bridge
    "iot-sensor-hub": 8251,      # Python – sensor aggregation
    "edge-orchestrator-service": 8180,  # Python – Jetson Orin edge
    "virtual-sensors": 8119,     # Python – virtual sensor computation
    "drone-service": 8126,       # Python – drone fleet & VRA
}

PYTHON_IOT = {
    "iot-gateway",
    "iot-sensor-hub",
    "edge-orchestrator-service",
    "virtual-sensors",
    "drone-service",
}

NODE_IOT = {"iot-service"}

# Services that bridge external protocols to NATS
PROTOCOL_BRIDGE_SERVICES = {"iot-gateway", "iot-service"}

# Edge services that manage local device model/data storage
EDGE_STORAGE_SERVICES = {"edge-orchestrator-service"}

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
# 1. IoT Protocol Dependencies
# ===========================================================================


class TestIoTProtocolDeps:
    """خدمات IoT يجب أن تدعم بروتوكولات الاتصال بالأجهزة."""

    def test_iot_gateway_mqtt_dependency(self) -> None:
        """iot-gateway declares MQTT client library."""
        pkgs = _req_packages("iot-gateway")
        has_mqtt = any("mqtt" in p for p in pkgs)
        assert has_mqtt, "iot-gateway missing MQTT dependency (aiomqtt/paho-mqtt)"

    @pytest.mark.parametrize("svc", sorted(PYTHON_IOT))
    def test_python_iot_has_nats(self, svc: str) -> None:
        """Python IoT service declares nats-py or accesses NATS via shared/."""
        pkgs = _req_packages(svc)
        has_nats = any("nats" in p for p in pkgs)
        if not has_nats:
            # Check if NATS is accessed through shared/ module copy
            content = _read_dockerfile(svc)
            has_nats = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_nats, f"{svc} missing nats-py dependency or shared/ NATS module"

    @pytest.mark.parametrize("svc", sorted(PYTHON_IOT))
    def test_python_iot_has_fastapi(self, svc: str) -> None:
        """Python IoT service declares fastapi."""
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi dependency"

    def test_iot_service_nestjs(self) -> None:
        """iot-service (Node.js) has package.json with NestJS."""
        pkg_json = SERVICES_DIR / "iot-service" / "package.json"
        if not pkg_json.exists():
            pytest.skip("No package.json for iot-service")
        content = pkg_json.read_text("utf-8")
        assert "nestjs" in content.lower(), "iot-service missing NestJS in package.json"


# ===========================================================================
# 2. Init System (tini) for Signal Handling
# ===========================================================================


class TestInitSystem:
    """خدمات IoT/Edge يجب أن تستخدم نظام تهيئة لمعالجة الإشارات."""

    # iot-gateway uses uvicorn's built-in signal handling (no tini needed)
    TINI_CANDIDATES = sorted({"edge-orchestrator-service", "iot-service"})

    @pytest.mark.parametrize("svc", TINI_CANDIDATES)
    def test_tini_installed_or_init(self, svc: str) -> None:
        """Long-lived IoT service uses tini or --init for proper signal handling."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_tini = "tini" in content.lower()
        has_init = "--init" in content.lower()
        has_entrypoint_tini = bool(
            re.search(r'ENTRYPOINT.*tini', content, re.IGNORECASE)
        )
        assert has_tini or has_init or has_entrypoint_tini, (
            f"{svc} should use tini or --init for signal handling in IoT workloads"
        )


# ===========================================================================
# 3. Edge Storage Provisioning
# ===========================================================================


class TestEdgeStorage:
    """خدمات الحافة يجب أن توفر أدلة التخزين."""

    @pytest.mark.parametrize("svc", sorted(EDGE_STORAGE_SERVICES))
    def test_data_directories_created(self, svc: str) -> None:
        """Edge service Dockerfile creates data directories."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_mkdir = "mkdir" in content.lower()
        has_data = any(
            d in content.lower()
            for d in ["/data", "/app/data", "/app/models", "/app/uploads"]
        )
        assert has_mkdir or has_data, (
            f"{svc} Dockerfile should provision data/model directories for edge storage"
        )


# ===========================================================================
# 4. Health Endpoints
# ===========================================================================


class TestIoTHealthEndpoints:
    """نقاط فحص الصحة لخدمات IoT."""

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        """Dockerfile defines HEALTHCHECK."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK in Dockerfile"

    @pytest.mark.parametrize("svc", sorted(PYTHON_IOT))
    def test_health_in_source(self, svc: str) -> None:
        """Python IoT service source has health endpoint."""
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


class TestIoTNonRoot:
    """خدمات IoT يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        """Dockerfile switches to non-root USER."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 6. Compose Dependency Chain
# ===========================================================================


class TestIoTComposeDeps:
    """سلسلة تبعيات docker-compose لخدمات IoT."""

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        """IoT service defined in docker-compose.yml."""
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_depends_on_nats(self, services: dict, svc: str) -> None:
        """IoT service depends on NATS (event bus)."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        assert "nats" in dep_names, (
            f"{svc} should depend on nats for sensor event delivery "
            f"(deps: {dep_names})"
        )

    @pytest.mark.parametrize("svc", sorted(PROTOCOL_BRIDGE_SERVICES))
    def test_bridge_depends_on_mqtt(self, services: dict, svc: str) -> None:
        """Protocol bridge service depends on MQTT broker."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        # Accept mqtt or mosquitto
        has_mqtt = any("mqtt" in d or "mosquitto" in d for d in dep_names)
        assert has_mqtt, (
            f"{svc} (protocol bridge) should depend on MQTT broker (deps: {dep_names})"
        )


# ===========================================================================
# 7. Environment Variables
# ===========================================================================


class TestIoTEnvVars:
    """متغيرات البيئة لخدمات IoT."""

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_nats_url_env(self, services: dict, svc: str) -> None:
        """IoT service declares NATS_URL environment variable."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, f"{svc} missing NATS_URL env var"

    def test_iot_gateway_mqtt_env(self, services: dict) -> None:
        """iot-gateway declares MQTT environment variables."""
        svc_def = services.get("iot-gateway", {})
        env_str = str(svc_def.get("environment", {}))
        mqtt_vars = ["MQTT_BROKER", "MQTT_PORT", "MQTT_URL"]
        has_mqtt_env = any(v in env_str for v in mqtt_vars)
        assert has_mqtt_env, "iot-gateway missing MQTT_* env vars"


# ===========================================================================
# 8. Port Range
# ===========================================================================


class TestIoTPortRange:
    """منافذ خدمات IoT."""

    @pytest.mark.parametrize("svc,port", sorted(IOT_EDGE_SERVICES.items()))
    def test_port_in_valid_range(self, svc: str, port: int) -> None:
        """IoT service port in valid range."""
        assert 3000 <= port <= 9000, f"{svc} port {port} out of range"

    def test_no_duplicate_ports(self) -> None:
        """No duplicate ports in IoT group."""
        ports = list(IOT_EDGE_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 9. Logging & Networking
# ===========================================================================


class TestIoTLoggingNetwork:
    """تسجيل الأحداث والشبكات لخدمات IoT."""

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        """IoT service has logging configuration in compose."""
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging configuration"

    @pytest.mark.parametrize("svc", sorted(IOT_EDGE_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        """IoT service on sahool network."""
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), (
            f"{svc} not on sahool network"
        )


# ===========================================================================
# 10. Pip Mirror Fallback (Python services)
# ===========================================================================


class TestIoTPipMirror:
    """خدمات IoT بلغة Python يجب أن تستخدم مرآة pip احتياطية."""

    @pytest.mark.parametrize("svc", sorted(PYTHON_IOT))
    def test_pip_fallback(self, svc: str) -> None:
        """Python IoT service Dockerfile has pip mirror fallback."""
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
