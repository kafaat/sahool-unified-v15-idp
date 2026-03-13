"""
SAHOOL Docker Container Function Tests
=======================================
Comprehensive tests validating Docker container definitions, Dockerfiles,
service completeness, and the categorization documented in
docker-container-function.md.

Tests cover:
1. Container structure validation (docker-compose.yml integrity)
2. Service functionality verification (not just pass-through stubs)
3. Dockerfile best practices (security, healthchecks, non-root)
4. Docker-compose cross-file consistency
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
SERVICES_DIR = REPO_ROOT / "apps" / "services"

# Backbone infrastructure containers (image-based, not built from source)
BACKBONE_CONTAINERS = {
    "postgres": {"image_pattern": "postgis/postgis", "required_port": 5432},
    "pgbouncer": {"image_pattern": "pgbouncer", "required_port": 6432},
    "redis": {"image_pattern": "redis", "required_port": 6379},
    "nats": {"image_pattern": "nats", "required_port": 4222},
    "kong": {"image_pattern": "kong", "required_port": 8000},
    "vault": {"image_pattern": "vault", "required_port": 8200},
}

# Supporting containers that serve other containers
SUPPORTING_CONTAINERS = {
    "qdrant": {"image_pattern": "qdrant"},
    "milvus": {"image_pattern": "milvus"},
    "minio": {"image_pattern": "minio"},
    "mqtt": {"image_pattern": "mosquitto"},
    "ollama": {"image_pattern": "ollama"},
    "mlflow": {"image_pattern": "mlflow"},
    "etcd": {"image_pattern": "etcd"},
    "nats-prometheus-exporter": {"image_pattern": "nats"},
    "mongo": {"image_pattern": "mongo"},
    "mongo-init-replica": {"image_pattern": "mongo"},
    "rocketchat": {"image_pattern": "rocket.chat"},
}

# All Python/FastAPI service containers expected to be fully functional
PYTHON_SERVICES = [
    "advisory-service",
    "agent-registry",
    "ai-advisor",
    "ai-agents-core",
    "ai-agents-service",
    "ai-chat-assistant",
    "alert-service",
    "astronomical-calendar",
    "audit-service",
    "billing-core",
    "code-fix-agent",
    "code-review-service",
    "community-service",
    "cooperative-service",
    "copilot-api",
    "crm-service",
    "crop-intelligence-service",
    "digital-twin-engine",
    "drone-service",
    "edge-orchestrator-service",
    "equipment-service",
    "fertigation-engine",
    "field-intelligence",
    "globalgap-compliance",
    "ground-vision-service",
    "hydrology-service",
    "indicators-service",
    "inventory-service",
    "iot-gateway",
    "iot-sensor-hub",
    "irrigation-cycle-engine",
    "irrigation-smart",
    "knowledge-graph",
    "leveling-optimizer-service",
    "llm-orchestrator-service",
    "logistics-service",
    "lowcode-engine",
    "mcp-server",
    "ndvi-processor",
    "notification-service",
    "pest-detection-service",
    "provider-config",
    "skills-service",
    "soil-analysis-service",
    "supply-chain-service",
    "task-service",
    "terrain-core-service",
    "traceability-service",
    "ussd-gateway",
    "vegetation-analysis-service",
    "virtual-sensors",
    "weather-service",
    "wechat-service",
    "whatsapp-bot-service",
    "ws-gateway",
    "yolo26-vision-service",
]

# Node.js/NestJS service containers
NODE_SERVICES = [
    "chat-service",
    "code-review-agent",
    "crop-growth-model",
    "disaster-assessment",
    "field-management-service",
    "iot-service",
    "lai-estimation",
    "marketplace-service",
    "research-core",
    "user-service",
    "yield-prediction",
    "yield-prediction-service",
]

# Services with known incomplete implementations (documented in analysis)
KNOWN_INCOMPLETE_SERVICES: set[str] = set()  # All services now have complete implementations

# Services that MUST have Dockerfiles
ALL_BUILDABLE_SERVICES = PYTHON_SERVICES + NODE_SERVICES

# Minimum lines threshold - services below this are likely stubs
MIN_MAIN_LINES_THRESHOLD = 50

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_compose(path: Path) -> dict:
    """Load and parse a docker-compose YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _find_main_file(service_dir: Path) -> Path | None:
    """Find the main entry point file for a service."""
    candidates = [
        service_dir / "src" / "main.py",
        service_dir / "src" / "main.ts",
        service_dir / "src" / "index.ts",
        service_dir / "main.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _find_dockerfile(service_dir: Path) -> Path | None:
    """Find the Dockerfile for a service."""
    candidates = [
        service_dir / "Dockerfile",
        service_dir / "dockerfile",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _count_route_decorators(content: str, lang: str = "python") -> int:
    """Count API route/endpoint decorators in source code."""
    if lang == "python":
        patterns = [
            r"@(?:app|router)\.(get|post|put|delete|patch)\(",
            r"app\.include_router\(",
        ]
    else:
        patterns = [
            r"@(?:Get|Post|Put|Delete|Patch)\(",
            r"@Controller\(",
        ]
    total = 0
    for p in patterns:
        total += len(re.findall(p, content))
    return total


def _has_health_endpoint(content: str, lang: str = "python") -> bool:
    """Check if the service defines a health endpoint."""
    if lang == "python":
        return bool(re.search(r'["\']/(healthz?|readyz?|health)["\']', content))
    return bool(re.search(r"health|healthz|readyz", content, re.IGNORECASE))


def _has_real_logic_beyond_health(content: str, lang: str = "python") -> bool:
    """Detect if a service has logic beyond just health endpoints."""
    if lang == "python":
        # Look for real business patterns
        patterns = [
            r"await\s+\w+\.(execute|fetch|publish|put|get|set)",
            r"app\.state\.\w+",
            r"Depends\(",
            r"include_router\(",
            r"async\s+def\s+(?!health|readyz|readiness|liveness)",
            r"BaseModel\)",
            r"pydantic",
        ]
    else:
        patterns = [
            r"@Injectable",
            r"@Controller",
            r"PrismaService",
            r"async\s+\w+\(",
            r"this\.\w+Service",
        ]
    matches = 0
    for p in patterns:
        if re.search(p, content):
            matches += 1
    return matches >= 2


# ===========================================================================
# TEST SUITE 1: Docker-Compose Structure Validation
# ===========================================================================

pytestmark = [pytest.mark.smoke]


class TestDockerComposeStructure:
    """Validate the main docker-compose.yml structure and integrity."""

    @pytest.fixture(scope="class")
    def compose_data(self) -> dict:
        assert MAIN_COMPOSE.exists(), f"docker-compose.yml not found at {MAIN_COMPOSE}"
        return _load_compose(MAIN_COMPOSE)

    def test_compose_file_exists(self):
        """docker-compose.yml must exist at repo root."""
        assert MAIN_COMPOSE.exists()

    def test_compose_has_services_section(self, compose_data):
        """docker-compose.yml must define a 'services' key."""
        assert "services" in compose_data
        assert len(compose_data["services"]) > 0

    def test_compose_has_minimum_service_count(self, compose_data):
        """Platform must have at least 70 services defined."""
        count = len(compose_data["services"])
        assert count >= 70, f"Expected >= 70 services, found {count}"

    def test_compose_has_volumes_section(self, compose_data):
        """docker-compose.yml must define named volumes."""
        assert "volumes" in compose_data
        assert len(compose_data["volumes"]) >= 5

    def test_compose_has_network(self, compose_data):
        """docker-compose.yml should define a network."""
        assert "networks" in compose_data

    def test_no_duplicate_ports(self, compose_data):
        """No two active services should expose the same host port.
        يجب ألا تستخدم خدمتان نشطتان نفس منفذ المضيف."""
        deprecated_profiles = {"deprecated", "legacy"}
        host_ports = {}
        conflicts = []
        for svc_name, svc_def in compose_data["services"].items():
            # Skip deprecated/profiled services that don't run by default
            svc_profiles = set(svc_def.get("profiles", []))
            if svc_profiles & deprecated_profiles:
                continue
            for port_mapping in svc_def.get("ports", []):
                port_str = str(port_mapping)
                # Extract host port: "127.0.0.1:8093:8093" -> 8093
                parts = port_str.split(":")
                if len(parts) == 3:
                    host_port = parts[1]
                elif len(parts) == 2:
                    host_port = parts[0]
                else:
                    continue
                if host_port in host_ports:
                    conflicts.append(f"Port {host_port} used by both '{host_ports[host_port]}' and '{svc_name}'")
                host_ports[host_port] = svc_name
        assert not conflicts, f"Port conflicts detected: {conflicts}"


class TestBackboneContainers:
    """Validate backbone infrastructure containers."""

    @pytest.fixture(scope="class")
    def compose_data(self) -> dict:
        return _load_compose(MAIN_COMPOSE)

    @pytest.mark.parametrize("container_name", list(BACKBONE_CONTAINERS.keys()))
    def test_backbone_container_defined(self, compose_data, container_name):
        """Each backbone container must be defined in docker-compose.yml."""
        assert container_name in compose_data["services"], (
            f"Backbone container '{container_name}' missing from docker-compose.yml"
        )

    @pytest.mark.parametrize("container_name", list(BACKBONE_CONTAINERS.keys()))
    def test_backbone_has_image(self, compose_data, container_name):
        """Backbone containers must use official images (not build from source)."""
        svc = compose_data["services"][container_name]
        assert "image" in svc, f"'{container_name}' should use an image, not build"
        expected_pattern = BACKBONE_CONTAINERS[container_name]["image_pattern"]
        assert expected_pattern in svc["image"], (
            f"'{container_name}' image should contain '{expected_pattern}', got '{svc['image']}'"
        )

    @pytest.mark.parametrize("container_name", list(BACKBONE_CONTAINERS.keys()))
    def test_backbone_has_port(self, compose_data, container_name):
        """Backbone containers must expose their expected ports."""
        svc = compose_data["services"][container_name]
        expected_port = BACKBONE_CONTAINERS[container_name]["required_port"]
        ports_str = str(svc.get("ports", []))
        assert str(expected_port) in ports_str, f"'{container_name}' should expose port {expected_port}"

    @pytest.mark.parametrize("container_name", list(BACKBONE_CONTAINERS.keys()))
    def test_backbone_has_volumes(self, compose_data, container_name):
        """Backbone containers must have persistent storage."""
        # vault may not always have volumes in dev config
        if container_name == "vault":
            pytest.skip("Vault volume is optional in development")
        svc = compose_data["services"][container_name]
        assert svc.get("volumes"), f"'{container_name}' should have volumes for data persistence"


class TestSupportingContainers:
    """Validate containers that serve other containers."""

    @pytest.fixture(scope="class")
    def compose_data(self) -> dict:
        return _load_compose(MAIN_COMPOSE)

    @pytest.mark.parametrize("container_name", list(SUPPORTING_CONTAINERS.keys()))
    def test_supporting_container_defined(self, compose_data, container_name):
        """Each supporting container must be defined in docker-compose.yml."""
        assert container_name in compose_data["services"], f"Supporting container '{container_name}' missing"

    @pytest.mark.parametrize("container_name", list(SUPPORTING_CONTAINERS.keys()))
    def test_supporting_has_image(self, compose_data, container_name):
        """Supporting containers should use official images."""
        svc = compose_data["services"][container_name]
        assert "image" in svc, f"'{container_name}' should use an image"


# ===========================================================================
# TEST SUITE 2: Service Functionality Verification
# ===========================================================================


class TestPythonServiceDirectories:
    """Verify Python service directory structure."""

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_service_directory_exists(self, service_name):
        """Each Python service must have a directory in apps/services/."""
        svc_dir = SERVICES_DIR / service_name
        assert svc_dir.exists(), f"Service directory missing: {svc_dir}"

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_service_has_main_file(self, service_name):
        """Each Python service must have a main.py entry point."""
        if service_name in KNOWN_INCOMPLETE_SERVICES:
            pytest.skip(f"'{service_name}' is a known incomplete service")
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        main_file = _find_main_file(svc_dir)
        assert main_file is not None, f"No main.py or src/main.py found in {svc_dir}"

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_service_has_requirements(self, service_name):
        """Each Python service should have a requirements.txt."""
        if service_name in KNOWN_INCOMPLETE_SERVICES:
            pytest.skip(f"'{service_name}' is a known incomplete service")
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        req = svc_dir / "requirements.txt"
        assert req.exists(), f"requirements.txt missing in {svc_dir}"


class TestNodeServiceDirectories:
    """Verify Node.js service directory structure."""

    @pytest.mark.parametrize("service_name", NODE_SERVICES)
    def test_service_directory_exists(self, service_name):
        """Each Node.js service must have a directory in apps/services/."""
        svc_dir = SERVICES_DIR / service_name
        assert svc_dir.exists(), f"Service directory missing: {svc_dir}"

    @pytest.mark.parametrize("service_name", NODE_SERVICES)
    def test_service_has_package_json(self, service_name):
        """Each Node.js service must have a package.json."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        pkg = svc_dir / "package.json"
        assert pkg.exists(), f"package.json missing in {svc_dir}"

    @pytest.mark.parametrize("service_name", NODE_SERVICES)
    def test_service_has_entry_point(self, service_name):
        """Each Node.js service must have an entry point (src/index.ts or src/main.ts)."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        has_entry = (svc_dir / "src" / "index.ts").exists() or (svc_dir / "src" / "main.ts").exists()
        assert has_entry, f"No src/index.ts or src/main.ts in {svc_dir}"


class TestServiceNotPassThrough:
    """
    Verify services have REAL business logic and are not just pass-through stubs.
    This is the core test matching the analysis in docker-container-function.md.
    """

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_python_service_has_health_endpoint(self, service_name):
        """Every Python service must define health endpoints."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        main_file = _find_main_file(svc_dir)
        if main_file is None:
            pytest.skip(f"No main file found for {service_name}")
        content = main_file.read_text(errors="replace")
        assert _has_health_endpoint(content), f"'{service_name}' is missing /healthz or /readyz endpoints"

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_python_service_not_trivially_small(self, service_name):
        """Service main file should exceed minimum line threshold (not a stub)."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        main_file = _find_main_file(svc_dir)
        if main_file is None:
            pytest.skip(f"No main file found for {service_name}")
        lines = len(main_file.read_text(errors="replace").splitlines())
        assert lines >= MIN_MAIN_LINES_THRESHOLD, (
            f"'{service_name}' main file has only {lines} lines (threshold: {MIN_MAIN_LINES_THRESHOLD}). Likely a stub."
        )

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_python_service_has_real_logic(self, service_name):
        """Service must have real business logic, not just health endpoints."""
        # Background workers without HTTP API are exceptions
        if service_name in ("agro-rules", "demo-data"):
            pytest.skip(f"'{service_name}' is a worker/CLI, not HTTP API")
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        main_file = _find_main_file(svc_dir)
        if main_file is None:
            pytest.skip(f"No main file found for {service_name}")
        content = main_file.read_text(errors="replace")
        assert _has_real_logic_beyond_health(content, "python"), (
            f"'{service_name}' appears to be a pass-through stub with no real logic"
        )

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_python_service_has_routes_or_workers(self, service_name):
        """Service must define API routes or worker handlers."""
        if service_name in ("agro-rules", "demo-data"):
            pytest.skip(f"'{service_name}' is a worker/CLI")
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        main_file = _find_main_file(svc_dir)
        if main_file is None:
            pytest.skip(f"No main file found for {service_name}")
        content = main_file.read_text(errors="replace")
        route_count = _count_route_decorators(content, "python")
        # Also check for included routers in separate files
        api_dir = svc_dir / "src" / "api"
        if api_dir.exists():
            for py_file in api_dir.rglob("*.py"):
                route_count += _count_route_decorators(py_file.read_text(errors="replace"), "python")
        assert route_count >= 1, (
            f"'{service_name}' has no API routes defined. Expected at least 1 route decorator or include_router call."
        )


# ===========================================================================
# TEST SUITE 3: Dockerfile Validation
# ===========================================================================


class TestDockerfileBestPractices:
    """Validate Dockerfiles follow SAHOOL platform conventions."""

    @pytest.mark.parametrize("service_name", ALL_BUILDABLE_SERVICES)
    def test_dockerfile_exists(self, service_name):
        """Each buildable service must have a Dockerfile."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        dockerfile = _find_dockerfile(svc_dir)
        assert dockerfile is not None, f"Dockerfile missing for service '{service_name}'"

    @pytest.mark.parametrize("service_name", ALL_BUILDABLE_SERVICES)
    def test_dockerfile_has_healthcheck(self, service_name):
        """Dockerfiles should define a HEALTHCHECK instruction."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        dockerfile = _find_dockerfile(svc_dir)
        if dockerfile is None:
            pytest.skip(f"No Dockerfile for {service_name}")
        content = dockerfile.read_text(errors="replace")
        assert "HEALTHCHECK" in content, f"Dockerfile for '{service_name}' is missing HEALTHCHECK instruction"

    @pytest.mark.parametrize("service_name", ALL_BUILDABLE_SERVICES)
    def test_dockerfile_uses_non_root_user(self, service_name):
        """Dockerfiles must create and use a non-root user."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        dockerfile = _find_dockerfile(svc_dir)
        if dockerfile is None:
            pytest.skip(f"No Dockerfile for {service_name}")
        content = dockerfile.read_text(errors="replace")
        has_user = bool(re.search(r"USER\s+(sahool|appuser|app|agent|node|\d+)", content))
        assert has_user, f"Dockerfile for '{service_name}' does not switch to a non-root user"

    @pytest.mark.parametrize("service_name", PYTHON_SERVICES)
    def test_python_dockerfile_has_pip_no_cache(self, service_name):
        """Python Dockerfiles should use --no-cache-dir for pip install."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        dockerfile = _find_dockerfile(svc_dir)
        if dockerfile is None:
            pytest.skip(f"No Dockerfile for {service_name}")
        content = dockerfile.read_text(errors="replace")
        if "pip install" in content:
            has_no_cache = "--no-cache-dir" in content or "PIP_NO_CACHE_DIR" in content
            assert has_no_cache, (
                f"Dockerfile for '{service_name}' uses pip install without --no-cache-dir (increases image size)"
            )

    @pytest.mark.parametrize("service_name", ALL_BUILDABLE_SERVICES)
    def test_dockerfile_has_workdir(self, service_name):
        """Dockerfiles should set a WORKDIR."""
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        dockerfile = _find_dockerfile(svc_dir)
        if dockerfile is None:
            pytest.skip(f"No Dockerfile for {service_name}")
        content = dockerfile.read_text(errors="replace")
        assert "WORKDIR" in content, f"Dockerfile for '{service_name}' is missing WORKDIR instruction"

    @pytest.mark.parametrize("service_name", ALL_BUILDABLE_SERVICES)
    def test_dockerfile_exposes_port(self, service_name):
        """Dockerfiles should EXPOSE their service port."""
        # Workers and CLI tools may not expose ports
        if service_name in ("agro-rules", "demo-data", "code-review-agent"):
            pytest.skip(f"'{service_name}' is a worker/CLI, no port expected")
        svc_dir = SERVICES_DIR / service_name
        if not svc_dir.exists():
            pytest.skip(f"Service directory not found: {service_name}")
        dockerfile = _find_dockerfile(svc_dir)
        if dockerfile is None:
            pytest.skip(f"No Dockerfile for {service_name}")
        content = dockerfile.read_text(errors="replace")
        assert "EXPOSE" in content, f"Dockerfile for '{service_name}' is missing EXPOSE instruction"


# ===========================================================================
# TEST SUITE 4: Docker-Compose Cross-File Consistency
# ===========================================================================


class TestComposeFileConsistency:
    """Validate consistency across multiple docker-compose files."""

    COMPOSE_FILES = [
        REPO_ROOT / "docker-compose.yml",
        REPO_ROOT / "docker-compose.test.yml",
        REPO_ROOT / "docker-compose.prod.yml",
        REPO_ROOT / "docker-compose.ha.yml",
        REPO_ROOT / "docker-compose.telemetry.yml",
    ]

    def test_all_compose_files_exist(self):
        """All expected docker-compose files must exist."""
        for cf in self.COMPOSE_FILES:
            assert cf.exists(), f"Missing compose file: {cf.name}"

    def test_all_compose_files_valid_yaml(self):
        """All docker-compose files must be valid YAML."""
        for cf in self.COMPOSE_FILES:
            if not cf.exists():
                continue
            try:
                data = _load_compose(cf)
                assert data is not None, f"{cf.name} parsed as empty"
            except yaml.YAMLError as e:
                pytest.fail(f"{cf.name} is invalid YAML: {e}")

    def test_event_layer_compose_files_exist(self):
        """4-layer event architecture compose files must exist."""
        layer_files = [
            REPO_ROOT / "docker" / "compose" / "compose.acquisition.yml",
            REPO_ROOT / "docker" / "compose" / "compose.intelligence.yml",
            REPO_ROOT / "docker" / "compose" / "compose.decision.yml",
            REPO_ROOT / "docker" / "compose" / "compose.business.yml",
        ]
        for lf in layer_files:
            assert lf.exists(), f"Event layer compose file missing: {lf.name}"

    def test_infra_compose_exists(self):
        """Infrastructure-only compose file must exist."""
        infra = REPO_ROOT / "docker" / "docker-compose.infra.yml"
        assert infra.exists()

    def test_infra_compose_has_core_services(self):
        """Infrastructure compose must include core backbone services."""
        infra = REPO_ROOT / "docker" / "docker-compose.infra.yml"
        if not infra.exists():
            pytest.skip("infra compose not found")
        data = _load_compose(infra)
        services = data.get("services", {})
        for core in ["postgres", "redis", "nats"]:
            assert core in services, f"Infrastructure compose missing '{core}'"


class TestComposeServiceDependencies:
    """Validate that service dependencies are properly declared."""

    @pytest.fixture(scope="class")
    def compose_data(self) -> dict:
        return _load_compose(MAIN_COMPOSE)

    def test_services_with_db_depend_on_pgbouncer(self, compose_data):
        """Services using database should depend on pgbouncer."""
        db_dependent_services = [
            "advisory-service",
            "alert-service",
            "audit-service",
            "field-management-service",
            "user-service",
            "vegetation-analysis-service",
            "weather-service",
            "crm-service",
        ]
        for svc_name in db_dependent_services:
            svc = compose_data["services"].get(svc_name)
            if svc is None:
                continue
            depends = svc.get("depends_on", {})
            if isinstance(depends, list):
                dep_names = depends
            elif isinstance(depends, dict):
                dep_names = list(depends.keys())
            else:
                dep_names = []
            has_db_dep = "pgbouncer" in dep_names or "postgres" in dep_names
            assert has_db_dep, f"'{svc_name}' uses database but doesn't depend on pgbouncer or postgres"

    def test_services_with_events_depend_on_nats(self, compose_data):
        """Services publishing events should depend on nats."""
        event_services = [
            "vegetation-analysis-service",
            "alert-service",
            "field-management-service",
            "weather-service",
        ]
        for svc_name in event_services:
            svc = compose_data["services"].get(svc_name)
            if svc is None:
                continue
            depends = svc.get("depends_on", {})
            if isinstance(depends, list):
                dep_names = depends
            elif isinstance(depends, dict):
                dep_names = list(depends.keys())
            else:
                dep_names = []
            assert "nats" in dep_names, f"'{svc_name}' publishes events but doesn't depend on nats"


# ===========================================================================
# TEST SUITE 5: Container Categorization Validation
# ===========================================================================


class TestContainerCategorization:
    """
    Validate the 4-category classification from docker-container-function.md.
    Ensures every service in docker-compose.yml is accounted for.
    """

    @pytest.fixture(scope="class")
    def compose_data(self) -> dict:
        return _load_compose(MAIN_COMPOSE)

    @pytest.fixture(scope="class")
    def all_services(self, compose_data) -> set:
        return set(compose_data["services"].keys())

    def _categorized_services(self) -> set:
        """Return all services that are categorized."""
        backbone = set(BACKBONE_CONTAINERS.keys())
        supporting = set(SUPPORTING_CONTAINERS.keys())
        service_centric = set(PYTHON_SERVICES) | set(NODE_SERVICES)
        isolated = {"demo-data", "agro-rules", "ollama-model-loader", "etcd-init", "vllm-deepseek"}
        return backbone | supporting | service_centric | isolated

    def test_backbone_count(self):
        """There should be exactly 6 backbone containers."""
        assert len(BACKBONE_CONTAINERS) == 6

    def test_all_services_are_categorized(self, all_services):
        """Every service in docker-compose.yml must belong to a category."""
        categorized = self._categorized_services()
        uncategorized = all_services - categorized
        # Allow some tolerance for special containers
        allowed_uncategorized = {"ussd-gateway", "whatsapp-bot-service"}
        truly_uncategorized = uncategorized - allowed_uncategorized
        # Filter out containers already in our lists
        truly_uncategorized = {s for s in truly_uncategorized if s not in categorized}
        assert len(truly_uncategorized) == 0, f"Uncategorized services: {truly_uncategorized}"

    def test_no_service_in_multiple_categories(self):
        """A service should not appear in more than one category."""
        backbone = set(BACKBONE_CONTAINERS.keys())
        supporting = set(SUPPORTING_CONTAINERS.keys())
        service_centric = set(PYTHON_SERVICES) | set(NODE_SERVICES)

        overlap_bs = backbone & supporting
        overlap_bsc = backbone & service_centric
        overlap_ssc = supporting & service_centric

        assert not overlap_bs, f"Backbone/Supporting overlap: {overlap_bs}"
        assert not overlap_bsc, f"Backbone/Service overlap: {overlap_bsc}"
        assert not overlap_ssc, f"Supporting/Service overlap: {overlap_ssc}"


# ===========================================================================
# TEST SUITE 6: Port Consistency
# ===========================================================================


class TestPortConsistency:
    """Validate port assignments match the service-ports contract."""

    EXPECTED_PORTS = {
        "field-management-service": 3000,
        "user-service": 3025,
        "marketplace-service": 3010,
        "research-core": 3015,
        "disaster-assessment": 3020,
        "yield-prediction": 3021,
        "lai-estimation": 3022,
        "crop-growth-model": 3023,
        "advisory-service": 8093,
        "vegetation-analysis-service": 8090,
        "weather-service": 8092,
        "irrigation-smart": 8094,
        "crop-intelligence-service": 8095,
        "notification-service": 8110,
        "billing-core": 8089,
        "task-service": 8103,
        "equipment-service": 8101,
        "alert-service": 8113,
        "audit-service": 8114,
        "yolo26-vision-service": 8150,
        "terrain-core-service": 8185,
        "hydrology-service": 8165,
        "leveling-optimizer-service": 8170,
        "edge-orchestrator-service": 8180,
    }

    @pytest.fixture(scope="class")
    def compose_data(self) -> dict:
        return _load_compose(MAIN_COMPOSE)

    @pytest.mark.parametrize(
        "service_name,expected_port",
        list(EXPECTED_PORTS.items()),
    )
    def test_service_port_matches(self, compose_data, service_name, expected_port):
        """Service port in docker-compose must match expected assignment."""
        svc = compose_data["services"].get(service_name)
        if svc is None:
            pytest.skip(f"Service '{service_name}' not in compose")
        ports_str = str(svc.get("ports", []))
        assert str(expected_port) in ports_str, (
            f"'{service_name}' should use port {expected_port}, but ports are: {svc.get('ports')}"
        )


# ===========================================================================
# TEST SUITE 7: Configuration Files Existence
# ===========================================================================


class TestConfigurationFiles:
    """Validate that required configuration files exist for infrastructure."""

    def test_kong_declarative_config_exists(self):
        """Kong declarative config must exist."""
        paths = [
            REPO_ROOT / "config" / "kong" / "kong.yml",
            REPO_ROOT / "infrastructure" / "gateway" / "kong" / "kong.yml",
        ]
        found = any(p.exists() for p in paths)
        assert found, "Kong declarative configuration file not found"

    def test_nats_config_exists(self):
        """NATS configuration file must exist."""
        paths = [
            REPO_ROOT / "config" / "nats" / "nats-server.conf",
            REPO_ROOT / "config" / "nats" / "nats.conf",
        ]
        found = any(p.exists() for p in paths)
        assert found, "NATS configuration file not found"

    def test_prometheus_config_exists(self):
        """Prometheus configuration must exist."""
        path = REPO_ROOT / "infrastructure" / "monitoring" / "prometheus" / "prometheus.yml"
        assert path.exists(), "Prometheus configuration not found"

    def test_prometheus_alert_rules_exist(self):
        """Prometheus alert rules directory must exist and contain rules."""
        rules_dir = REPO_ROOT / "infrastructure" / "monitoring" / "prometheus" / "rules"
        assert rules_dir.exists(), "Prometheus rules directory not found"
        rule_files = list(rules_dir.glob("*.yml"))
        assert len(rule_files) >= 1, "No alert rule files found"

    def test_grafana_dashboards_exist(self):
        """Grafana dashboards must exist."""
        dash_dir = REPO_ROOT / "infrastructure" / "monitoring" / "grafana" / "dashboards"
        assert dash_dir.exists(), "Grafana dashboards directory not found"
        dashboards = list(dash_dir.glob("*.json"))
        assert len(dashboards) >= 1, "No Grafana dashboard files found"

    def test_otel_collector_config_exists(self):
        """OpenTelemetry collector config must exist."""
        paths = [
            REPO_ROOT / "shared" / "telemetry" / "otel-collector-config.yaml",
            REPO_ROOT / "infrastructure" / "monitoring" / "otel-collector-config.yaml",
        ]
        found = any(p.exists() for p in paths)
        assert found, "OpenTelemetry collector config not found"


# ===========================================================================
# TEST SUITE 8: Documentation Validation
# ===========================================================================


class TestDockerDocumentation:
    """Validate the docker-container-function.md documentation file."""

    DOC_FILE = REPO_ROOT / "docker-container-function.md"

    def test_documentation_file_exists(self):
        """docker-container-function.md must exist."""
        assert self.DOC_FILE.exists()

    def test_documentation_has_four_sections(self):
        """Documentation must have all 4 required categories."""
        content = self.DOC_FILE.read_text()
        required_sections = [
            "Backbone Containers",
            "Service-Centric Containers",
            "Containers Serve Other Containers",
            "Isolated Containers",
        ]
        for section in required_sections:
            assert section in content, f"Documentation missing section: '{section}'"

    def test_documentation_has_functionality_analysis(self):
        """Documentation must include functionality completeness analysis."""
        content = self.DOC_FILE.read_text()
        assert "FULLY FUNCTIONAL" in content
        assert "PARTIAL" in content or "Partially" in content

    def test_documentation_has_summary_statistics(self):
        """Documentation must include summary statistics."""
        content = self.DOC_FILE.read_text()
        assert "Summary" in content or "Statistics" in content

    def test_documentation_not_empty(self):
        """Documentation must have substantial content."""
        content = self.DOC_FILE.read_text()
        line_count = len(content.splitlines())
        assert line_count >= 100, f"Documentation has only {line_count} lines - too short"
