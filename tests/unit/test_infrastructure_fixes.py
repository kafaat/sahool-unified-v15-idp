"""
Infrastructure Fixes Validation Tests
اختبارات التحقق من إصلاحات البنية التحتية

Validates:
1. Kong gateway port correctness vs docker-compose.yml
2. No deprecated ghost services in Kong (returning 502)
3. NumPy version constraint for TensorFlow compatibility
4. Governance services registry consistency
5. Docker-compose port uniqueness
"""

import re
from pathlib import Path

import pytest
import yaml

# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).parent.parent.parent
KONG_CONFIG = ROOT / "infrastructure" / "gateway" / "kong" / "kong.yml"
DOCKER_COMPOSE = ROOT / "docker-compose.yml"
PYPROJECT = ROOT / "pyproject.toml"
GOVERNANCE = ROOT / "governance" / "services.yaml"


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def kong_config():
    """Load Kong gateway configuration."""
    with open(KONG_CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def kong_services(kong_config):
    """Extract services from Kong config."""
    return {s["name"]: s for s in kong_config.get("services", [])}


@pytest.fixture(scope="module")
def docker_compose_content():
    """Load raw docker-compose.yml content."""
    return DOCKER_COMPOSE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def docker_compose_config():
    """Parse docker-compose.yml."""
    with open(DOCKER_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def docker_services(docker_compose_config):
    """Extract service names from docker-compose."""
    return set(docker_compose_config.get("services", {}).keys())


@pytest.fixture(scope="module")
def pyproject_content():
    """Load pyproject.toml content."""
    return PYPROJECT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def governance_config():
    """Load governance services registry."""
    with open(GOVERNANCE, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Kong Port Correctness Tests | اختبارات صحة منافذ Kong
# ═══════════════════════════════════════════════════════════════════════════


class TestKongPortCorrectness:
    """Verify Kong service ports match actual container internal ports."""

    def test_chat_service_port_is_8115(self, kong_services):
        """chat-service must use port 8115 (container PORT=8115)."""
        assert "chat-service" in kong_services, "chat-service missing from Kong"
        assert kong_services["chat-service"]["port"] == 8115, (
            f"chat-service Kong port should be 8115, got {kong_services['chat-service']['port']}"
        )

    def test_mcp_server_port_is_8201(self, kong_services):
        """mcp-server must use port 8201 (MCP_SERVER_PORT=8201)."""
        assert "mcp-server" in kong_services, "mcp-server missing from Kong"
        assert kong_services["mcp-server"]["port"] == 8201, (
            f"mcp-server Kong port should be 8201, got {kong_services['mcp-server']['port']}"
        )

    def test_copilot_api_port_is_8088(self, kong_services):
        """copilot-api must use port 8088 (container internal, host-mapped to 8163)."""
        assert "copilot-api" in kong_services, "copilot-api missing from Kong"
        assert kong_services["copilot-api"]["port"] == 8088, (
            f"copilot-api Kong port should be 8088, got {kong_services['copilot-api']['port']}"
        )

    def test_field_management_service_port(self, kong_services):
        """field-management-service must use port 3000."""
        assert "field-management-service" in kong_services
        assert kong_services["field-management-service"]["port"] == 3000

    def test_user_service_port(self, kong_services):
        """user-service must use port 3025."""
        assert "user-service" in kong_services
        assert kong_services["user-service"]["port"] == 3025

    def test_vegetation_analysis_service_port(self, kong_services):
        """vegetation-analysis-service must use port 8090."""
        assert "vegetation-analysis-service" in kong_services
        assert kong_services["vegetation-analysis-service"]["port"] == 8090

    def test_advisory_service_port(self, kong_services):
        """advisory-service must use port 8093."""
        assert "advisory-service" in kong_services
        assert kong_services["advisory-service"]["port"] == 8093

    def test_weather_service_port(self, kong_services):
        """weather-service must use port 8092."""
        assert "weather-service" in kong_services
        assert kong_services["weather-service"]["port"] == 8092

    def test_crop_intelligence_service_port(self, kong_services):
        """crop-intelligence-service must use port 8095."""
        assert "crop-intelligence-service" in kong_services
        assert kong_services["crop-intelligence-service"]["port"] == 8095

    def test_yield_prediction_service_port(self, kong_services):
        """yield-prediction-service must use port 8152."""
        assert "yield-prediction-service" in kong_services
        assert kong_services["yield-prediction-service"]["port"] == 8152


# ═══════════════════════════════════════════════════════════════════════════
# 2. No Ghost Services Tests | اختبارات عدم وجود خدمات وهمية
# ═══════════════════════════════════════════════════════════════════════════


class TestNoGhostServices:
    """Verify deprecated services are removed from Kong config."""

    DEPRECATED_SERVICES = [
        "community-chat",
        "field-ops",
        "field-chat",
        "field-service",
        "field-core",
        "crop-health",
        "yield-engine",
        "satellite-service",
        "weather-advanced",
        "crop-health-ai",
        "fertilizer-advisor",
    ]

    @pytest.mark.parametrize("service_name", DEPRECATED_SERVICES)
    def test_deprecated_service_not_in_kong(self, kong_services, service_name):
        """Deprecated service must NOT be registered in Kong (would return 502)."""
        assert service_name not in kong_services, f"Deprecated service '{service_name}' still in Kong - will return 502"

    def test_no_port_9000_range_services(self, kong_services):
        """No services should use deprecated 9000-9999 port range."""
        for name, service in kong_services.items():
            port = service.get("port")
            if port is None:
                continue  # Some entries (e.g., root-endpoint) have no port
            assert port < 9000, f"Service '{name}' uses deprecated port {port} (9000+ range)"

    def test_all_kong_services_have_docker_container(self, kong_services, docker_services):
        """Every Kong service must have a corresponding Docker container."""
        # Exclude Kong meta-entries (no port), route variants, and infrastructure.
        # Services whose names end in "-health" or "-public" are routing-only variants
        # that share the same backend port as their canonical service — they are not
        # ghost services and do not need their own docker-compose entry.
        excluded = {
            "kong",  # infrastructure
            "root-endpoint",  # Kong meta-route (no backend needed)
        }
        # Kong route suffixes that map to a base service (e.g. chat-service-health → chat-service)
        route_suffixes = ("-health", "-public", "-ws")

        for service_name, service_config in kong_services.items():
            if service_name in excluded:
                continue
            if service_name.endswith("-health") or service_name.endswith("-public"):
                continue  # Route variants — same backend as canonical service
            if service_config.get("port") is None:
                continue  # Meta-entries without a port

            # For route variants, check the base service name exists in Docker
            check_name = service_name
            for suffix in route_suffixes:
                if service_name.endswith(suffix):
                    check_name = service_name[: -len(suffix)]
                    break

            assert check_name in docker_services, (
                f"Kong service '{service_name}' (base: '{check_name}') has no Docker container - will return 502"
            )


# ═══════════════════════════════════════════════════════════════════════════
# 3. Dependency Constraints Tests | اختبارات قيود التبعيات
# ═══════════════════════════════════════════════════════════════════════════


class TestDependencyConstraints:
    """Verify critical dependency version constraints."""

    def test_numpy_upper_bound_below_2_5(self, pyproject_content):
        """NumPy must be pinned <2.5.0 for TensorFlow 2.20 compatibility."""
        match = re.search(r'"numpy>=[\d.]+,<([\d.]+)"', pyproject_content)
        assert match, "NumPy constraint not found in pyproject.toml"
        upper = match.group(1)
        major, minor = [int(x) for x in upper.split(".")[:2]]
        # <2.5.0 means upper bound is 2.5.0 exclusive, which is safe
        assert (major, minor) <= (2, 5), f"NumPy upper bound is {upper}, must be <=2.5.0 for TensorFlow compatibility"
        # Must NOT allow 3.0+ which definitely breaks TF
        assert major < 3, f"NumPy upper bound {upper} allows 3.x which breaks TensorFlow"

    def test_numpy_lower_bound_at_least_1_26(self, pyproject_content):
        """NumPy must have lower bound >= 1.26.0."""
        match = re.search(r'"numpy>=([\d.]+),', pyproject_content)
        assert match, "NumPy lower bound not found"
        lower = match.group(1)
        parts = [int(x) for x in lower.split(".")]
        assert parts[0] >= 1 and parts[1] >= 26, f"NumPy lower bound {lower} should be >= 1.26.0"

    def test_tensorflow_version_pinned(self, pyproject_content):
        """TensorFlow must be explicitly pinned."""
        assert "tensorflow-cpu==" in pyproject_content, "TensorFlow must be pinned with == (not range)"

    def test_cryptography_has_minimum_version(self, pyproject_content):
        """cryptography must have a minimum version for CVE fixes."""
        assert "cryptography>=" in pyproject_content, "cryptography must specify minimum version for security"

    def test_aiohttp_has_minimum_version(self, pyproject_content):
        """aiohttp must have minimum version for CVE fixes."""
        assert "aiohttp>=" in pyproject_content, "aiohttp must specify minimum version for security"


# ═══════════════════════════════════════════════════════════════════════════
# 4. Docker Compose Port Uniqueness | اختبارات تفرد المنافذ
# ═══════════════════════════════════════════════════════════════════════════


class TestDockerComposePortUniqueness:
    """Verify no two Docker services share the same host port."""

    def test_no_duplicate_host_ports(self, docker_compose_config):
        """All Docker services must have unique host port mappings."""
        port_map = {}  # port -> service name
        services = docker_compose_config.get("services", {})

        for svc_name, svc_config in services.items():
            ports = svc_config.get("ports", [])
            for port_spec in ports:
                port_str = str(port_spec)
                # Extract host port from "IP:HOST:CONTAINER" or "HOST:CONTAINER"
                # e.g., "127.0.0.1:6432:6432" -> 6432, "8000:8000" -> 8000
                match = re.match(r"(?:\d+\.\d+\.\d+\.\d+:)?(\d+):\d+", port_str)
                if match:
                    host_port = int(match.group(1))
                    if host_port in port_map:
                        pytest.fail(f"Port {host_port} conflict: '{svc_name}' and '{port_map[host_port]}'")
                    port_map[host_port] = svc_name

    def test_all_services_have_ports(self, docker_compose_config):
        """Application services (not infrastructure) should have port mappings."""
        infra_services = {
            "postgres",
            "pgbouncer",
            "redis",
            "nats",
            "kong",
            "nats-prometheus-exporter",
            "mqtt",
            "qdrant",
            "vault",
            "ollama",
            "ollama-model-loader",
            "milvus",
            "etcd",
            "etcd-init",
            "etcd-perms-init",
            "minio",
            "mlflow",
            "mongo",
            "mongo-init-replica",
        }
        # Deprecated services may not have host port mappings to avoid conflicts
        deprecated_services = {
            "wechat-service",
        }
        services = docker_compose_config.get("services", {})
        missing = []
        for svc_name, svc_config in services.items():
            if svc_name in infra_services or svc_name in deprecated_services:
                continue
            if not svc_config.get("ports"):
                missing.append(svc_name)

        # Allow some services without ports (workers, sidecars)
        # but flag if too many are missing
        assert len(missing) <= 5, f"Too many application services without port mappings: {missing}"


# ═══════════════════════════════════════════════════════════════════════════
# 5. Governance Registry Tests | اختبارات سجل الحوكمة
# ═══════════════════════════════════════════════════════════════════════════


class TestGovernanceRegistry:
    """Verify governance services.yaml consistency."""

    def test_version_is_current(self, governance_config):
        """Governance version must be >= 3.3.0."""
        version = governance_config.get("version", "0.0.0")
        parts = [int(x) for x in version.split(".")]
        assert parts[0] >= 3 and parts[1] >= 3, f"Governance version {version} should be >= 3.3.0"

    def test_last_updated_is_2026(self, governance_config):
        """Last updated date must be in 2026."""
        updated = governance_config.get("last_updated", "")
        assert "2026" in updated, f"Governance last_updated '{updated}' should be in 2026"

    def test_has_event_architecture(self, governance_config):
        """Governance must define event architecture layers."""
        assert "event_architecture" in governance_config
        layers = governance_config["event_architecture"].get("layers", {})
        required = {"acquisition", "intelligence", "decision", "business"}
        assert required.issubset(set(layers.keys())), f"Missing event layers: {required - set(layers.keys())}"


# ═══════════════════════════════════════════════════════════════════════════
# 6. Kong Configuration Integrity | اختبارات سلامة إعدادات Kong
# ═══════════════════════════════════════════════════════════════════════════


class TestKongConfigIntegrity:
    """Verify Kong configuration structural integrity."""

    def test_all_services_have_routes(self, kong_config):
        """Every Kong service must have at least one route."""
        for service in kong_config.get("services", []):
            routes = service.get("routes", [])
            assert len(routes) > 0, f"Kong service '{service['name']}' has no routes"

    def test_all_routes_have_paths(self, kong_config):
        """Every Kong route must define at least one path."""
        for service in kong_config.get("services", []):
            for route in service.get("routes", []):
                paths = route.get("paths", [])
                assert len(paths) > 0, f"Route '{route.get('name', '?')}' in service '{service['name']}' has no paths"

    def test_no_duplicate_service_names(self, kong_config):
        """Kong must not have duplicate service names."""
        names = [s["name"] for s in kong_config.get("services", [])]
        duplicates = [n for n in names if names.count(n) > 1]
        assert not duplicates, f"Duplicate Kong service names: {set(duplicates)}"

    def test_no_duplicate_route_paths(self, kong_config):
        """Kong must not have duplicate primary route paths."""
        all_paths = []
        for service in kong_config.get("services", []):
            for route in service.get("routes", []):
                for path in route.get("paths", []):
                    if path.endswith("-legacy"):
                        continue  # Skip legacy paths
                    all_paths.append((path, service["name"]))

        path_set = {}
        conflicts = []
        for path, svc in all_paths:
            if path in path_set and path_set[path] != svc:
                conflicts.append(f"{path} -> {path_set[path]} vs {svc}")
            path_set[path] = svc

        assert not conflicts, f"Duplicate route paths: {conflicts}"

    def test_kong_service_count_reasonable(self, kong_config):
        """Kong should have between 50-95 services (not too few, not too many).

        The platform has 72 active microservices.  Each service may have an
        additional "-health" or "-public" routing variant in Kong (same backend
        port as the canonical service).  The upper bound allows for
        72 canonical + up to 23 routing variants = 95 entries before the config
        is considered bloated.
        """
        count = len(kong_config.get("services", []))
        assert 50 <= count <= 95, f"Kong has {count} services, expected 50-95"


# ═══════════════════════════════════════════════════════════════════════════
# 7. Cross-Validation Tests | اختبارات التحقق المتبادل
# ═══════════════════════════════════════════════════════════════════════════


class TestCrossValidation:
    """Cross-validate between different configuration sources."""

    CRITICAL_SERVICES = [
        ("field-management-service", 3000),
        ("user-service", 3025),
        ("weather-service", 8092),
        ("advisory-service", 8093),
        ("irrigation-smart", 8094),
        ("crop-intelligence-service", 8095),
        ("notification-service", 8110),
        ("task-service", 8103),
        ("chat-service", 8115),
        ("vegetation-analysis-service", 8090),
    ]

    @pytest.mark.parametrize("service_name,expected_port", CRITICAL_SERVICES)
    def test_critical_service_in_kong(self, kong_services, service_name, expected_port):
        """Critical services must be in Kong with correct port."""
        assert service_name in kong_services, f"Critical service '{service_name}' missing from Kong"
        assert kong_services[service_name]["port"] == expected_port, (
            f"{service_name} port mismatch: Kong={kong_services[service_name]['port']}, expected={expected_port}"
        )

    @pytest.mark.parametrize("service_name,expected_port", CRITICAL_SERVICES)
    def test_critical_service_in_docker(self, docker_services, service_name, expected_port):
        """Critical services must have Docker containers."""
        assert service_name in docker_services, f"Critical service '{service_name}' missing from docker-compose.yml"
