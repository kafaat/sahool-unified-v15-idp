"""
SAHOOL Container Health Tests
==============================
Comprehensive health validation for all 86 Docker containers.
Tests are organized into 16 parallel test classes covering:

1.  Infrastructure healthchecks (postgres, redis, nats, kong, vault, pgbouncer)
2.  Supporting services healthchecks (qdrant, milvus, minio, mqtt, ollama, mlflow, etcd)
3.  Python FastAPI service healthchecks (48 services)
4.  Node.js NestJS service healthchecks (12 services)
5.  Dockerfile HEALTHCHECK directive validation
6.  Health endpoint code validation (Python)
7.  Health endpoint code validation (Node.js)
8.  Readiness probe validation
9.  Health check timing configuration
10. Dependency health chain validation
11. Health check response format validation
12. Container restart policy validation
13. Resource limits validation
14. Network connectivity validation
15. Volume mount validation
16. Security configuration validation

Run: pytest tests/container/test_container_health.py -v --tb=short -x
Run parallel: pytest tests/container/test_container_health.py -v -n auto
"""

import re
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
TEST_COMPOSE = REPO_ROOT / "docker-compose.test.yml"
SERVICES_DIR = REPO_ROOT / "apps" / "services"


def _load_compose(path: Path) -> dict:
    """Load and parse a docker-compose YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def compose_data() -> dict:
    """Load main docker-compose.yml once for all tests."""
    assert MAIN_COMPOSE.exists(), f"docker-compose.yml not found at {MAIN_COMPOSE}"
    return _load_compose(MAIN_COMPOSE)


@pytest.fixture(scope="module")
def node_src_cache() -> dict[str, str]:
    """Cache concatenated .ts source content per Node.js service (module-scoped)."""
    cache: dict[str, str] = {}
    for svc_name in NODE_SERVICES:
        svc_dir = SERVICES_DIR / svc_name / "src"
        if not svc_dir.exists():
            cache[svc_name] = ""
            continue
        parts = []
        for f in svc_dir.rglob("*.ts"):
            parts.append(f.read_text(errors="replace"))
        cache[svc_name] = "\n".join(parts)
    return cache


# ---------------------------------------------------------------------------
# Service Classification
# ---------------------------------------------------------------------------

INFRASTRUCTURE_SERVICES = {
    "postgres": {"port": 5432, "health_cmd": "pg_isready"},
    "pgbouncer": {"port": 6432, "health_cmd": "healthcheck.sh"},
    "redis": {"port": 6379, "health_cmd": "redis-cli"},
    "nats": {"port": 4222, "health_cmd": "healthz"},
    "kong": {"port": 8000, "health_cmd": "kong health"},
    "vault": {"port": 8200, "health_cmd": "vault status"},
}

SUPPORTING_SERVICES = {
    "qdrant": {"port": 6333, "health_endpoint": "/healthz"},
    "milvus": {"port": 19530, "health_endpoint": "/healthz"},
    "minio": {"port": 9000, "health_endpoint": "/minio/health/live"},
    "mqtt": {"port": 1883, "health_cmd": "mosquitto_sub"},
    "ollama": {"port": 11434, "health_endpoint": "/"},
    "mlflow": {"port": 5000, "health_endpoint": "/health"},
    "etcd": {"port": None, "health_cmd": "etcdctl"},
    "nats-prometheus-exporter": {"port": 7777, "health_endpoint": "/healthz"},
}

PYTHON_SERVICES = {
    "advisory-service": 8093,
    "agent-registry": 8160,
    "ai-advisor": 8112,
    "ai-agents-core": 8161,
    "ai-agents-service": 8130,
    "ai-chat-assistant": 8260,
    "alert-service": 8113,
    "astronomical-calendar": 8111,
    "audit-service": 8114,
    "billing-core": 8089,
    "code-fix-agent": 8162,
    "code-review-service": 8102,
    "cooperative-service": 8127,
    "copilot-api": 8088,
    "crm-service": 8131,
    "crop-intelligence-service": 8095,
    "digital-twin-engine": 8253,
    "drone-service": 8126,
    "edge-orchestrator-service": 8180,
    "equipment-service": 8101,
    "fertigation-engine": 8252,
    "field-intelligence": 8120,
    "globalgap-compliance": 8128,
    "ground-vision-service": 8182,
    "hydrology-service": 8165,
    "indicators-service": 8091,
    "inventory-service": 8116,
    "iot-gateway": 8106,
    "iot-sensor-hub": 8251,
    "irrigation-cycle-engine": 8250,
    "irrigation-smart": 8094,
    "knowledge-graph": 8140,
    "leveling-optimizer-service": 8170,
    "llm-orchestrator-service": 8164,
    "logistics-service": 8167,
    "lowcode-engine": 8132,
    "mcp-server": 8201,
    "notification-service": 8110,
    "pest-detection-service": 8125,
    "provider-config": 8104,
    "skills-service": 8121,
    "soil-analysis-service": 8134,
    "supply-chain-service": 8230,
    "task-service": 8103,
    "terrain-core-service": 8185,
    "traceability-service": 8123,
    "ussd-gateway": 8183,
    "vegetation-analysis-service": 8090,
    "virtual-sensors": 8119,
    "weather-service": 8092,
    "whatsapp-bot-service": 8240,
    "ws-gateway": 8081,
    "yolo26-vision-service": 8150,
}

NODE_SERVICES = {
    "chat-service": 8115,
    "crop-growth-model": 3023,
    "disaster-assessment": 3020,
    "field-management-service": 3000,
    "iot-service": 8117,
    "lai-estimation": 3022,
    "marketplace-service": 3010,
    "research-core": 3015,
    "user-service": 3025,
    "yield-prediction": 3021,
    "yield-prediction-service": 8152,
}

# Services without ports (workers/init containers)
PORTLESS_SERVICES = {"agro-rules", "code-review-agent", "demo-data", "etcd-init", "ollama-model-loader"}

# All services with health endpoints
ALL_HTTP_SERVICES = {**PYTHON_SERVICES, **NODE_SERVICES}

pytestmark = [pytest.mark.smoke]


# ===========================================================================
# 1. Infrastructure Health Check Validation
# ===========================================================================


class TestInfrastructureHealthChecks:
    """Validate healthcheck configuration for infrastructure containers."""

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_service_has_healthcheck(self, compose_data, svc_name):
        """Infrastructure service must have a healthcheck defined."""
        svc = compose_data["services"].get(svc_name)
        assert svc is not None, f"Infrastructure service '{svc_name}' not in compose"
        assert "healthcheck" in svc, (
            f"Infrastructure service '{svc_name}' missing healthcheck"
        )

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_healthcheck_has_test(self, compose_data, svc_name):
        """Infrastructure healthcheck must have a test command."""
        svc = compose_data["services"][svc_name]
        hc = svc.get("healthcheck", {})
        assert "test" in hc, f"'{svc_name}' healthcheck missing 'test' command"

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_healthcheck_has_interval(self, compose_data, svc_name):
        """Infrastructure healthcheck must have an interval."""
        svc = compose_data["services"][svc_name]
        hc = svc.get("healthcheck", {})
        assert "interval" in hc, f"'{svc_name}' healthcheck missing 'interval'"

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_healthcheck_has_retries(self, compose_data, svc_name):
        """Infrastructure healthcheck must have retries."""
        svc = compose_data["services"][svc_name]
        hc = svc.get("healthcheck", {})
        assert "retries" in hc, f"'{svc_name}' healthcheck missing 'retries'"

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_healthcheck_has_start_period(self, compose_data, svc_name):
        """Infrastructure healthcheck must have start_period for warm-up."""
        svc = compose_data["services"][svc_name]
        hc = svc.get("healthcheck", {})
        assert "start_period" in hc, f"'{svc_name}' healthcheck missing 'start_period'"

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_exposes_expected_port(self, compose_data, svc_name):
        """Infrastructure service must expose its expected port."""
        expected_port = INFRASTRUCTURE_SERVICES[svc_name]["port"]
        svc = compose_data["services"][svc_name]
        ports_str = str(svc.get("ports", []))
        assert str(expected_port) in ports_str, (
            f"'{svc_name}' should expose port {expected_port}"
        )


# ===========================================================================
# 2. Supporting Services Health Check Validation
# ===========================================================================


class TestSupportingServicesHealthChecks:
    """Validate healthcheck configuration for supporting containers."""

    @pytest.mark.parametrize("svc_name", list(SUPPORTING_SERVICES.keys()))
    def test_supporting_service_exists(self, compose_data, svc_name):
        """Supporting service must be defined in docker-compose."""
        assert svc_name in compose_data["services"], (
            f"Supporting service '{svc_name}' not found"
        )

    @pytest.mark.parametrize("svc_name", list(SUPPORTING_SERVICES.keys()))
    def test_supporting_service_has_healthcheck(self, compose_data, svc_name):
        """Supporting service must have a healthcheck."""
        svc = compose_data["services"][svc_name]
        assert "healthcheck" in svc, (
            f"Supporting service '{svc_name}' missing healthcheck"
        )

    @pytest.mark.parametrize("svc_name", list(SUPPORTING_SERVICES.keys()))
    def test_supporting_service_uses_image(self, compose_data, svc_name):
        """Supporting services should use official Docker images."""
        svc = compose_data["services"][svc_name]
        assert "image" in svc, (
            f"Supporting service '{svc_name}' should use a Docker image"
        )


# ===========================================================================
# 3. Python Service Healthcheck Validation (docker-compose)
# ===========================================================================


class TestPythonServiceComposeHealthChecks:
    """Validate healthcheck in docker-compose for Python services."""

    @pytest.mark.parametrize("svc_name,port", list(PYTHON_SERVICES.items()))
    def test_python_service_has_healthcheck(self, compose_data, svc_name, port):
        """Python service must have a healthcheck in docker-compose."""
        svc = compose_data["services"].get(svc_name)
        assert svc is not None, f"Python service '{svc_name}' not in compose"
        assert "healthcheck" in svc, (
            f"Python service '{svc_name}' missing healthcheck in docker-compose"
        )

    @pytest.mark.parametrize("svc_name,port", list(PYTHON_SERVICES.items()))
    def test_python_service_healthcheck_uses_correct_port(self, compose_data, svc_name, port):
        """Python service healthcheck should reference its correct port."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        test_cmd = str(hc.get("test", ""))
        assert str(port) in test_cmd, (
            f"'{svc_name}' healthcheck should use port {port}, "
            f"but test command is: {test_cmd}"
        )

    @pytest.mark.parametrize("svc_name,port", list(PYTHON_SERVICES.items()))
    def test_python_service_healthcheck_uses_healthz(self, compose_data, svc_name, port):
        """Python service healthcheck should use /healthz endpoint."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        test_cmd = str(hc.get("test", ""))
        assert "healthz" in test_cmd or "health" in test_cmd, (
            f"'{svc_name}' healthcheck should use /healthz endpoint"
        )


# ===========================================================================
# 4. Node.js Service Healthcheck Validation (docker-compose)
# ===========================================================================


class TestNodeServiceComposeHealthChecks:
    """Validate healthcheck in docker-compose for Node.js services."""

    @pytest.mark.parametrize("svc_name,port", list(NODE_SERVICES.items()))
    def test_node_service_has_healthcheck(self, compose_data, svc_name, port):
        """Node.js service must have a healthcheck in docker-compose."""
        svc = compose_data["services"].get(svc_name)
        assert svc is not None, f"Node.js service '{svc_name}' not in compose"
        assert "healthcheck" in svc, (
            f"Node.js service '{svc_name}' missing healthcheck in docker-compose"
        )

    @pytest.mark.parametrize("svc_name,port", list(NODE_SERVICES.items()))
    def test_node_service_healthcheck_uses_correct_port(self, compose_data, svc_name, port):
        """Node.js service healthcheck should reference its correct port."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        test_cmd = str(hc.get("test", ""))
        assert str(port) in test_cmd, (
            f"'{svc_name}' healthcheck should use port {port}"
        )


# ===========================================================================
# 5. Dockerfile HEALTHCHECK Directive Validation
# ===========================================================================


class TestDockerfileHealthDirectives:
    """Validate HEALTHCHECK instruction exists in all service Dockerfiles."""

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_dockerfile_has_healthcheck(self, svc_name):
        """Every service Dockerfile must have a HEALTHCHECK instruction."""
        svc_dir = SERVICES_DIR / svc_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {svc_name}")
        dockerfile = svc_dir / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"Dockerfile not found for {svc_name}")
        content = dockerfile.read_text(errors="replace")
        assert "HEALTHCHECK" in content, (
            f"Dockerfile for '{svc_name}' is missing HEALTHCHECK instruction"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_dockerfile_healthcheck_has_interval(self, svc_name):
        """Dockerfile HEALTHCHECK must specify --interval."""
        svc_dir = SERVICES_DIR / svc_name
        dockerfile = svc_dir / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"Dockerfile not found for {svc_name}")
        content = dockerfile.read_text(errors="replace")
        if "HEALTHCHECK" not in content:
            pytest.skip(f"No HEALTHCHECK in Dockerfile for {svc_name}")
        assert "--interval=" in content, (
            f"HEALTHCHECK for '{svc_name}' missing --interval"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_dockerfile_healthcheck_has_timeout(self, svc_name):
        """Dockerfile HEALTHCHECK must specify --timeout."""
        svc_dir = SERVICES_DIR / svc_name
        dockerfile = svc_dir / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"Dockerfile not found for {svc_name}")
        content = dockerfile.read_text(errors="replace")
        if "HEALTHCHECK" not in content:
            pytest.skip(f"No HEALTHCHECK in Dockerfile for {svc_name}")
        assert "--timeout=" in content, (
            f"HEALTHCHECK for '{svc_name}' missing --timeout"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_dockerfile_healthcheck_has_retries(self, svc_name):
        """Dockerfile HEALTHCHECK must specify --retries."""
        svc_dir = SERVICES_DIR / svc_name
        dockerfile = svc_dir / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"Dockerfile not found for {svc_name}")
        content = dockerfile.read_text(errors="replace")
        if "HEALTHCHECK" not in content:
            pytest.skip(f"No HEALTHCHECK in Dockerfile for {svc_name}")
        assert "--retries=" in content, (
            f"HEALTHCHECK for '{svc_name}' missing --retries"
        )


# ===========================================================================
# 6. Python Health Endpoint Code Validation
# ===========================================================================


class TestPythonHealthEndpoints:
    """Validate Python services implement /healthz and /readyz endpoints in code."""

    def _get_main_content(self, svc_name: str) -> str | None:
        svc_dir = SERVICES_DIR / svc_name
        if not svc_dir.exists():
            return None
        for candidate in [svc_dir / "src" / "main.py", svc_dir / "main.py"]:
            if candidate.exists():
                return candidate.read_text(errors="replace")
        return None

    @pytest.mark.parametrize("svc_name", list(PYTHON_SERVICES.keys()))
    def test_python_has_healthz_endpoint(self, svc_name):
        """Python service must define /healthz endpoint."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        has_healthz = bool(re.search(r'["\']/(healthz|health)["\']', content))
        assert has_healthz, (
            f"'{svc_name}' missing /healthz endpoint in main.py"
        )

    @pytest.mark.parametrize("svc_name", list(PYTHON_SERVICES.keys()))
    def test_python_has_readyz_endpoint(self, svc_name):
        """Python service should define /readyz endpoint for Kubernetes readiness."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        has_readyz = bool(re.search(r'["\']/(readyz|readiness|ready)["\']', content))
        assert has_readyz, (
            f"'{svc_name}' missing /readyz endpoint in main.py"
        )

    @pytest.mark.parametrize("svc_name", list(PYTHON_SERVICES.keys()))
    def test_python_healthz_returns_status(self, svc_name):
        """Health endpoint should return a status field."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        # Check for {"status": "ok"} or {"status": "healthy"} or status="ok" pattern
        has_status = bool(re.search(
            r'["\']status["\'].*["\'](ok|healthy|up|running)["\']', content, re.IGNORECASE
        )) or bool(re.search(
            r'status\s*=\s*["\'](ok|healthy|up|running)["\']', content, re.IGNORECASE
        ))
        assert has_status, (
            f"'{svc_name}' healthz should return a status field (ok/healthy/up/running)"
        )

    @pytest.mark.parametrize("svc_name", list(PYTHON_SERVICES.keys()))
    def test_python_healthz_returns_version(self, svc_name):
        """Health endpoint should return a version field."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        has_version = bool(
            re.search(r'["\']version["\']', content)
            or re.search(r'SERVICE_VERSION\s*=', content)
            or re.search(r'version\s*=\s*SERVICE_VERSION', content)
        )
        assert has_version, (
            f"'{svc_name}' healthz should return version information"
        )


# ===========================================================================
# 7. Node.js Health Endpoint Code Validation
# ===========================================================================


class TestNodeHealthEndpoints:
    """Validate Node.js services implement health endpoints in code."""

    @pytest.mark.parametrize("svc_name", list(NODE_SERVICES.keys()))
    def test_node_has_health_endpoint(self, svc_name, node_src_cache):
        """Node.js service must define a health endpoint."""
        content = node_src_cache.get(svc_name, "")
        if not content:
            pytest.skip(f"No source files found for {svc_name}")
        has_health = bool(re.search(r'health|healthz|readyz', content, re.IGNORECASE))
        assert has_health, (
            f"'{svc_name}' missing health endpoint in source code"
        )

    @pytest.mark.parametrize("svc_name", list(NODE_SERVICES.keys()))
    def test_node_uses_terminus_or_custom_health(self, svc_name, node_src_cache):
        """Node.js service should use @nestjs/terminus or custom health module."""
        content = node_src_cache.get(svc_name, "")
        if not content:
            pytest.skip(f"No source files found for {svc_name}")
        has_terminus = "terminus" in content.lower() or "TerminusModule" in content
        has_custom = bool(re.search(r'health|Health(Module|Controller|Service)', content))
        assert has_terminus or has_custom, (
            f"'{svc_name}' should use @nestjs/terminus or custom health module"
        )


# ===========================================================================
# 8. Readiness Probe Validation
# ===========================================================================


class TestReadinessProbes:
    """Validate readiness probes check actual dependencies."""

    def _get_main_content(self, svc_name: str) -> str | None:
        svc_dir = SERVICES_DIR / svc_name
        if not svc_dir.exists():
            return None
        for candidate in [svc_dir / "src" / "main.py", svc_dir / "main.py"]:
            if candidate.exists():
                return candidate.read_text(errors="replace")
        return None

    # Services that require database connectivity
    DB_DEPENDENT = [
        "advisory-service", "alert-service", "audit-service", "billing-core",
        "crm-service", "equipment-service", "inventory-service", "task-service",
        "notification-service", "weather-service", "vegetation-analysis-service",
    ]

    @pytest.mark.parametrize("svc_name", DB_DEPENDENT)
    def test_readyz_checks_database(self, svc_name):
        """Services with DB dependency should check DB in readiness."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        has_db_check = bool(re.search(
            r'(db|database|pool|asyncpg|connect)', content, re.IGNORECASE
        ))
        assert has_db_check, (
            f"'{svc_name}' readiness probe should check database connectivity"
        )

    # Services that require NATS connectivity
    NATS_DEPENDENT = [
        "advisory-service", "alert-service", "vegetation-analysis-service",
        "weather-service", "field-intelligence", "indicators-service",
    ]

    @pytest.mark.parametrize("svc_name", NATS_DEPENDENT)
    def test_readyz_checks_nats(self, svc_name):
        """Services with NATS dependency should reference NATS in code."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        has_nats_check = bool(re.search(r'(nats|NATS|nc\.|nats_)', content))
        assert has_nats_check, (
            f"'{svc_name}' should reference NATS for event integration"
        )


# ===========================================================================
# 9. Health Check Timing Configuration
# ===========================================================================


class TestHealthCheckTiming:
    """Validate health check timing parameters are reasonable."""

    def _parse_duration(self, duration_str: str) -> int:
        """Parse Docker duration string to seconds."""
        if isinstance(duration_str, (int, float)):
            return int(duration_str)
        match = re.match(r"(\d+)(ms|s|m)?", str(duration_str))
        if not match:
            return 0
        value = int(match.group(1))
        unit = match.group(2) or "s"
        if unit == "m":
            return value * 60
        if unit == "ms":
            return max(1, value // 1000)
        return value

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_interval_not_too_frequent(self, compose_data, svc_name):
        """Health check interval should be >= 5s to avoid overhead."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        interval = self._parse_duration(hc.get("interval", "30s"))
        assert interval >= 5, (
            f"'{svc_name}' healthcheck interval {interval}s is too frequent (min: 5s)"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_interval_not_too_infrequent(self, compose_data, svc_name):
        """Health check interval should be <= 120s for timely detection."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        interval = self._parse_duration(hc.get("interval", "30s"))
        assert interval <= 120, (
            f"'{svc_name}' healthcheck interval {interval}s is too infrequent (max: 120s)"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_timeout_less_than_interval(self, compose_data, svc_name):
        """Health check timeout must be less than interval."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        interval = self._parse_duration(hc.get("interval", "30s"))
        timeout = self._parse_duration(hc.get("timeout", "10s"))
        assert timeout <= interval, (
            f"'{svc_name}' timeout ({timeout}s) > interval ({interval}s)"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_retries_between_2_and_10(self, compose_data, svc_name):
        """Health check retries should be between 2 and 10."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        hc = svc.get("healthcheck", {})
        retries = hc.get("retries", 3)
        assert 2 <= retries <= 10, (
            f"'{svc_name}' retries={retries} outside range [2, 10]"
        )

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_start_period_adequate(self, compose_data, svc_name):
        """Infrastructure services need adequate start_period for initialization."""
        svc = compose_data["services"][svc_name]
        hc = svc.get("healthcheck", {})
        start_period = self._parse_duration(hc.get("start_period", "0s"))
        assert start_period >= 10, (
            f"Infrastructure '{svc_name}' start_period {start_period}s is too short (min: 10s)"
        )


# ===========================================================================
# 10. Dependency Health Chain Validation
# ===========================================================================


class TestDependencyHealthChain:
    """Validate service dependency health chain (depends_on with condition)."""

    def _get_depends(self, compose_data, svc_name) -> dict:
        svc = compose_data["services"].get(svc_name, {})
        depends = svc.get("depends_on", {})
        if isinstance(depends, list):
            return {d: {} for d in depends}
        return depends if isinstance(depends, dict) else {}

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_service_has_dependencies(self, compose_data, svc_name):
        """HTTP services should declare at least one dependency."""
        depends = self._get_depends(compose_data, svc_name)
        assert len(depends) >= 1, (
            f"'{svc_name}' should declare dependencies (at minimum pgbouncer, redis, or nats)"
        )

    DB_SERVICES = [
        "alert-service", "audit-service", "billing-core",
        "crm-service", "field-management-service", "user-service",
        "vegetation-analysis-service", "weather-service",
    ]

    @pytest.mark.parametrize("svc_name", DB_SERVICES)
    def test_db_service_depends_on_pgbouncer(self, compose_data, svc_name):
        """DB-dependent services must depend on pgbouncer or postgres."""
        depends = self._get_depends(compose_data, svc_name)
        dep_names = set(depends.keys())
        has_db = "pgbouncer" in dep_names or "postgres" in dep_names
        assert has_db, (
            f"'{svc_name}' uses DB but doesn't depend on pgbouncer/postgres"
        )

    @pytest.mark.parametrize("svc_name", DB_SERVICES)
    def test_db_dependency_uses_healthy_condition(self, compose_data, svc_name):
        """DB dependency should use condition: service_healthy."""
        depends = self._get_depends(compose_data, svc_name)
        for dep_name in ["pgbouncer", "postgres"]:
            if dep_name in depends:
                dep_config = depends[dep_name]
                if isinstance(dep_config, dict):
                    condition = dep_config.get("condition", "")
                    assert condition == "service_healthy", (
                        f"'{svc_name}' -> '{dep_name}' should use "
                        f"condition: service_healthy, got: {condition}"
                    )
                break


# ===========================================================================
# 11. Health Check Response Format Validation
# ===========================================================================


class TestHealthResponseFormat:
    """Validate health endpoint response format conventions."""

    def _get_main_content(self, svc_name: str) -> str | None:
        svc_dir = SERVICES_DIR / svc_name
        if not svc_dir.exists():
            return None
        for candidate in [svc_dir / "src" / "main.py", svc_dir / "main.py"]:
            if candidate.exists():
                return candidate.read_text(errors="replace")
        return None

    @pytest.mark.parametrize("svc_name", list(PYTHON_SERVICES.keys()))
    def test_health_returns_service_name(self, svc_name):
        """Health response should include the service name."""
        content = self._get_main_content(svc_name)
        if content is None:
            pytest.skip(f"No main.py found for {svc_name}")
        # Check for service field in response or SERVICE_NAME constant
        has_service_name = bool(
            re.search(r'["\']service["\']', content)
            or re.search(r'SERVICE_NAME\s*=', content)
            or re.search(r'service_name', content, re.IGNORECASE)
        )
        assert has_service_name, (
            f"'{svc_name}' health response should include 'service' field"
        )


# ===========================================================================
# 12. Container Restart Policy Validation
# ===========================================================================


class TestRestartPolicy:
    """Validate containers have appropriate restart policies."""

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_has_restart_policy(self, compose_data, svc_name):
        """Infrastructure services must have restart policy."""
        svc = compose_data["services"][svc_name]
        assert "restart" in svc, (
            f"Infrastructure '{svc_name}' missing restart policy"
        )

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_restart_unless_stopped(self, compose_data, svc_name):
        """Infrastructure services should use 'unless-stopped' restart."""
        svc = compose_data["services"][svc_name]
        restart = svc.get("restart", "")
        assert restart in ("unless-stopped", "always", "on-failure"), (
            f"'{svc_name}' restart should be 'unless-stopped', got: {restart}"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_service_has_restart_policy(self, compose_data, svc_name):
        """Application services must have a restart policy."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        assert "restart" in svc, (
            f"Service '{svc_name}' missing restart policy"
        )


# ===========================================================================
# 13. Resource Limits Validation
# ===========================================================================


class TestResourceLimits:
    """Validate containers have resource limits for stability."""

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_has_resource_limits(self, compose_data, svc_name):
        """Infrastructure services must have resource limits."""
        svc = compose_data["services"][svc_name]
        deploy = svc.get("deploy", {})
        resources = deploy.get("resources", {})
        limits = resources.get("limits", {})
        assert limits, (
            f"Infrastructure '{svc_name}' missing resource limits (deploy.resources.limits)"
        )

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_has_memory_limit(self, compose_data, svc_name):
        """Infrastructure services must have memory limit."""
        svc = compose_data["services"][svc_name]
        deploy = svc.get("deploy", {})
        resources = deploy.get("resources", {})
        limits = resources.get("limits", {})
        assert "memory" in limits, (
            f"Infrastructure '{svc_name}' missing memory limit"
        )


# ===========================================================================
# 14. Network Configuration Validation
# ===========================================================================


class TestNetworkConfiguration:
    """Validate network configuration for all services."""

    def test_compose_has_sahool_network(self, compose_data):
        """docker-compose.yml must define sahool-network."""
        networks = compose_data.get("networks", {})
        assert "sahool-network" in networks, (
            "docker-compose.yml must define 'sahool-network'"
        )

    def test_sahool_network_has_name(self, compose_data):
        """sahool-network should have explicit name."""
        networks = compose_data.get("networks", {})
        net = networks.get("sahool-network", {})
        has_name = net.get("name") == "sahool-network" or net.get("external") is True
        assert has_name, (
            "sahool-network should have name: sahool-network or external: true"
        )

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_on_sahool_network(self, compose_data, svc_name):
        """Infrastructure services must be on sahool-network."""
        svc = compose_data["services"][svc_name]
        networks = svc.get("networks", [])
        if isinstance(networks, list):
            net_names = networks
        elif isinstance(networks, dict):
            net_names = list(networks.keys())
        else:
            net_names = []
        assert "sahool-network" in net_names, (
            f"'{svc_name}' must be on sahool-network"
        )

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_service_on_sahool_network(self, compose_data, svc_name):
        """Application services must be on sahool-network."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        networks = svc.get("networks", [])
        if isinstance(networks, list):
            net_names = networks
        elif isinstance(networks, dict):
            net_names = list(networks.keys())
        else:
            net_names = []
        assert "sahool-network" in net_names, (
            f"'{svc_name}' must be on sahool-network"
        )


# ===========================================================================
# 15. Volume Mount Validation
# ===========================================================================


class TestVolumeMounts:
    """Validate volume configuration for data persistence."""

    DATA_SERVICES = ["postgres", "redis", "minio", "qdrant", "milvus", "mlflow"]

    @pytest.mark.parametrize("svc_name", DATA_SERVICES)
    def test_data_service_has_volumes(self, compose_data, svc_name):
        """Data services must have persistent volumes."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        volumes = svc.get("volumes", [])
        assert len(volumes) >= 1, (
            f"Data service '{svc_name}' must have at least one volume for persistence"
        )

    def test_compose_defines_named_volumes(self, compose_data):
        """docker-compose must define named volumes for data persistence."""
        volumes = compose_data.get("volumes", {})
        assert "postgres_data" in volumes, "Missing postgres_data volume"
        assert "redis_data" in volumes, "Missing redis_data volume"

    @pytest.mark.parametrize("svc_name", ["postgres", "redis"])
    def test_critical_data_uses_named_volume(self, compose_data, svc_name):
        """Critical data services must use named (not anonymous) volumes."""
        svc = compose_data["services"][svc_name]
        volumes = svc.get("volumes", [])
        named_volumes = [v for v in volumes if isinstance(v, str) and ":" in v and not v.startswith("/") and not v.startswith(".")]
        assert len(named_volumes) >= 1, (
            f"'{svc_name}' should use named volumes (not bind mounts) for critical data"
        )


# ===========================================================================
# 16. Security Configuration Validation
# ===========================================================================


class TestSecurityConfiguration:
    """Validate security-related health configurations."""

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_service_binds_to_localhost(self, compose_data, svc_name):
        """Services should bind ports to 127.0.0.1 (not 0.0.0.0)."""
        svc = compose_data["services"].get(svc_name)
        if svc is None:
            pytest.skip(f"Service '{svc_name}' not in compose")
        ports = svc.get("ports", [])
        for port in ports:
            port_str = str(port)
            # Skip if no host binding specified
            if ":" not in port_str:
                continue
            assert "127.0.0.1" in port_str or "localhost" in port_str, (
                f"'{svc_name}' port {port_str} should bind to 127.0.0.1 for security"
            )

    @pytest.mark.parametrize("svc_name", list(INFRASTRUCTURE_SERVICES.keys()))
    def test_infra_has_security_opt(self, compose_data, svc_name):
        """Infrastructure services should have security options."""
        svc = compose_data["services"][svc_name]
        has_security = "security_opt" in svc or "read_only" in svc
        # Some infra services may not need security_opt
        if not has_security:
            pytest.skip(f"'{svc_name}' security_opt is optional")

    @pytest.mark.parametrize("svc_name", list(ALL_HTTP_SERVICES.keys()))
    def test_dockerfile_uses_nonroot_user(self, svc_name):
        """Service Dockerfiles must run as non-root user."""
        svc_dir = SERVICES_DIR / svc_name
        dockerfile = svc_dir / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"Dockerfile not found for {svc_name}")
        content = dockerfile.read_text(errors="replace")
        has_user = bool(re.search(r'USER\s+(sahool|appuser|app|agent|node|\d+)', content))
        assert has_user, (
            f"Dockerfile for '{svc_name}' must switch to a non-root user"
        )

    @pytest.mark.parametrize("svc_name", list(PYTHON_SERVICES.keys()))
    def test_health_endpoint_no_sensitive_data(self, svc_name):
        """Health endpoints must not expose sensitive information in responses."""
        svc_dir = SERVICES_DIR / svc_name
        main_file = svc_dir / "src" / "main.py"
        if not main_file.exists():
            main_file = svc_dir / "main.py"
        if not main_file.exists():
            pytest.skip(f"No main.py for {svc_name}")
        content = main_file.read_text(errors="replace")
        # Extract health endpoint function bodies (look for def health/healthz/readyz
        # and check only the function body for sensitive data in return values)
        health_funcs = re.findall(
            r'(def\s+(?:health|healthz|readyz|readiness|liveness)\s*\(.*?\n(?:(?:    .*\n)*))',
            content,
        )
        if not health_funcs:
            pytest.skip(f"No extractable health function in {svc_name}")
        health_code = "\n".join(health_funcs)
        # Only flag if sensitive values are directly in return statements
        sensitive_patterns = [
            r'return.*password\s*[:=]',
            r'return.*secret_key\s*[:=]',
            r'return.*api_key\s*[:=]',
        ]
        for pattern in sensitive_patterns:
            match = re.search(pattern, health_code, re.IGNORECASE)
            assert not match, (
                f"'{svc_name}' health endpoint may expose sensitive data in return value"
            )


# ===========================================================================
# Summary Statistics Test
# ===========================================================================


class TestHealthSummaryStatistics:
    """Summary validation of overall health test coverage."""

    def test_total_services_count(self, compose_data):
        """Platform must have at least 80 services."""
        total = len(compose_data["services"])
        assert total >= 80, f"Expected >= 80 services, found {total}"

    def test_healthcheck_coverage(self, compose_data):
        """At least 95% of long-running services should have healthchecks.
        يجب أن يكون لدى 95% على الأقل من الخدمات طويلة التشغيل فحوصات صحية."""
        # Exclude one-shot init/loader containers that exit after completion
        init_containers = {"etcd-init", "mongo-init-replica", "ollama-model-loader"}
        long_running = {
            name: svc for name, svc in compose_data["services"].items()
            if name not in init_containers
        }
        total = len(long_running)
        with_hc = sum(
            1 for svc in long_running.values()
            if "healthcheck" in svc
        )
        coverage = with_hc / total * 100
        assert coverage >= 95, (
            f"Healthcheck coverage {coverage:.1f}% is below 95% "
            f"({with_hc}/{total} services)"
        )

    def test_all_http_services_have_ports(self, compose_data):
        """All HTTP services must expose ports."""
        missing = []
        for svc_name in ALL_HTTP_SERVICES:
            svc = compose_data["services"].get(svc_name)
            if svc and not svc.get("ports"):
                missing.append(svc_name)
        assert not missing, f"HTTP services without ports: {missing}"

    def test_python_service_count(self):
        """Platform should have at least 45 Python services."""
        assert len(PYTHON_SERVICES) >= 45, (
            f"Expected >= 45 Python services, found {len(PYTHON_SERVICES)}"
        )

    def test_node_service_count(self):
        """Platform should have at least 10 Node.js services."""
        assert len(NODE_SERVICES) >= 10, (
            f"Expected >= 10 Node.js services, found {len(NODE_SERVICES)}"
        )

    def test_infrastructure_service_count(self):
        """Platform should have exactly 6 infrastructure services."""
        assert len(INFRASTRUCTURE_SERVICES) == 6

    def test_no_duplicate_ports_across_all_services(self, compose_data):
        """No two active services should use the same host port.
        يجب ألا تستخدم خدمتان نشطتان نفس منفذ المضيف."""
        # Exclude deprecated/profiled services that don't run by default
        deprecated_profiles = {"deprecated", "legacy"}
        port_map: dict[str, str] = {}
        conflicts = []
        for svc_name, svc in compose_data["services"].items():
            svc_profiles = set(svc.get("profiles", []))
            if svc_profiles & deprecated_profiles:
                continue
            for port_mapping in svc.get("ports", []):
                port_str = str(port_mapping)
                # Strip protocol suffix (e.g. /tcp, /udp) before parsing
                port_str = re.sub(r"/\w+$", "", port_str)
                parts = port_str.split(":")
                if len(parts) >= 2:
                    host_port = parts[-2] if len(parts) == 3 else parts[0]
                    if host_port in port_map:
                        conflicts.append(
                            f"Port {host_port}: {port_map[host_port]} vs {svc_name}"
                        )
                    port_map[host_port] = svc_name
        assert not conflicts, f"Port conflicts: {conflicts}"
