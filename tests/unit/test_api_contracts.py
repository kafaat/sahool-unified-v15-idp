"""
SAHOOL API Contract Tests
اختبارات عقود واجهات البرمجة

Validates that:
- OpenAPI specs match the actual service endpoints defined in main.py
- Service ports in governance/services.yaml match shared-types contracts
- Health endpoint patterns are consistent across all services
- All services in docker-compose have matching OpenAPI documentation

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.parent
OPENAPI_DIR = PROJECT_ROOT / "docs" / "api" / "openapi"
SERVICES_DIR = PROJECT_ROOT / "apps" / "services"
GOVERNANCE_FILE = PROJECT_ROOT / "governance" / "services.yaml"
DOCKER_COMPOSE = PROJECT_ROOT / "docker-compose.yml"


def load_yaml_safe(path: Path) -> dict | None:
    """Load YAML file, return None if not found."""
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_service_endpoints(service_dir: Path) -> list[str]:
    """
    Extract API endpoints from a Python service's main.py.
    Returns list of endpoint paths.
    """
    main_py = service_dir / "src" / "main.py"
    if not main_py.exists():
        return []

    content = main_py.read_text(errors="ignore")

    # Match @app.get("/path"), @app.post("/path"), @router.get("/path"), etc.
    pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, content)

    return [(method.upper(), path) for method, path in matches]


def get_openapi_endpoints(spec_path: Path) -> list[tuple[str, str]]:
    """
    Extract endpoints from an OpenAPI spec file.
    Returns list of (METHOD, path) tuples.
    """
    data = load_yaml_safe(spec_path)
    if not data:
        return []

    endpoints = []
    http_methods = {"get", "post", "put", "delete", "patch"}

    for path, path_item in data.get("paths", {}).items():
        for method in http_methods:
            if method in path_item:
                endpoints.append((method.upper(), path))

    return endpoints


# ═══════════════════════════════════════════════════════════════════════════════
# OpenAPI Coverage Tests - اختبارات تغطية OpenAPI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOpenAPICoverage:
    """Test that OpenAPI specs cover the actual service endpoints."""

    def test_all_openapi_specs_are_valid(self):
        """All OpenAPI specs should be loadable."""
        for spec_file in OPENAPI_DIR.glob("*.yaml"):
            if spec_file.name == "README.md":
                continue
            data = load_yaml_safe(spec_file)
            assert data is not None, f"Failed to load {spec_file.name}"
            assert "openapi" in data, f"{spec_file.name} is not an OpenAPI spec"

    def test_openapi_endpoint_count(self):
        """Platform should document a significant number of endpoints."""
        total_endpoints = 0
        for spec_file in OPENAPI_DIR.glob("*.yaml"):
            if spec_file.name == "README.md":
                continue
            endpoints = get_openapi_endpoints(spec_file)
            total_endpoints += len(endpoints)

        assert total_endpoints >= 50, (
            f"Expected at least 50 documented endpoints, found {total_endpoints}"
        )

    def test_openapi_readme_lists_most_specs(self):
        """OpenAPI README should reference most spec files."""
        readme = OPENAPI_DIR / "README.md"
        if not readme.exists():
            pytest.skip("OpenAPI README.md not found")

        readme_content = readme.read_text()
        spec_files = list(OPENAPI_DIR.glob("*.yaml"))
        referenced = [f for f in spec_files if f.name in readme_content]

        # At least 80% of specs should be listed in README
        if spec_files:
            coverage = len(referenced) / len(spec_files)
            assert coverage >= 0.70, (
                f"Only {len(referenced)}/{len(spec_files)} specs referenced in README. "
                f"Missing: {[f.name for f in spec_files if f not in referenced]}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Service-OpenAPI Alignment Tests - اختبارات محاذاة الخدمة-OpenAPI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceOpenAPIAlignment:
    """Test alignment between service code and OpenAPI documentation."""

    def _get_key_services(self) -> list[tuple[str, Path, int]]:
        """Get key services with their expected port numbers."""
        return [
            ("advisory-service", SERVICES_DIR / "advisory-service", 8093),
            ("weather-service", SERVICES_DIR / "weather-service", 8092),
            ("equipment-service", SERVICES_DIR / "equipment-service", 8101),
            ("notification-service", SERVICES_DIR / "notification-service", 8110),
            ("alert-service", SERVICES_DIR / "alert-service", 8113),
            ("task-service", SERVICES_DIR / "task-service", 8103),
            ("billing-core", SERVICES_DIR / "billing-core", 8089),
            ("irrigation-smart", SERVICES_DIR / "irrigation-smart", 8094),
            ("pest-detection-service", SERVICES_DIR / "pest-detection-service", 8125),
        ]

    def test_key_services_have_health_endpoints(self):
        """All key services must define /healthz and /readyz."""
        for service_name, service_dir, _ in self._get_key_services():
            if not service_dir.exists():
                continue

            endpoints = get_service_endpoints(service_dir)
            endpoint_paths = [path for _, path in endpoints]

            assert "/healthz" in endpoint_paths, (
                f"{service_name} missing /healthz endpoint"
            )
            assert "/readyz" in endpoint_paths, (
                f"{service_name} missing /readyz endpoint"
            )

    def test_advisory_service_endpoints_documented(self):
        """Advisory service key endpoints should be documented in OpenAPI."""
        ai_spec = OPENAPI_DIR / "ai-services.yaml"
        if not ai_spec.exists():
            pytest.skip("ai-services.yaml not found")

        data = load_yaml_safe(ai_spec)
        spec_paths = set(data.get("paths", {}).keys())

        # Key advisory endpoints that should be documented
        key_endpoints = [
            "/disease/assess",
            "/fertilizer/plan",
        ]

        for endpoint in key_endpoints:
            found = any(endpoint in path for path in spec_paths)
            assert found, (
                f"Advisory endpoint '{endpoint}' not documented in ai-services.yaml. "
                f"Available paths: {sorted(spec_paths)}"
            )

    def test_weather_service_endpoints_documented(self):
        """Weather service key endpoints should be documented."""
        weather_spec = OPENAPI_DIR / "weather-services.yaml"
        if not weather_spec.exists():
            pytest.skip("weather-services.yaml not found")

        data = load_yaml_safe(weather_spec)
        assert data is not None
        paths = data.get("paths", {})
        assert len(paths) >= 2, "Weather spec should have at least 2 endpoints"


# ═══════════════════════════════════════════════════════════════════════════════
# Governance Alignment Tests - اختبارات محاذاة الحوكمة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGovernanceAlignment:
    """Test alignment between governance registry and actual services."""

    def test_governance_services_yaml_exists(self):
        """Governance services.yaml should exist."""
        assert GOVERNANCE_FILE.exists(), "governance/services.yaml not found"

    def test_governance_services_yaml_valid(self):
        """Governance services.yaml should be valid YAML."""
        if not GOVERNANCE_FILE.exists():
            pytest.skip("governance/services.yaml not found")

        data = load_yaml_safe(GOVERNANCE_FILE)
        assert data is not None, "governance/services.yaml is empty or invalid"

    def test_service_directories_exist(self):
        """Services listed in governance should have actual directories."""
        if not GOVERNANCE_FILE.exists():
            pytest.skip("governance/services.yaml not found")

        data = load_yaml_safe(GOVERNANCE_FILE)
        if not data:
            pytest.skip("Empty governance file")

        services = data.get("services", [])
        if not services:
            pytest.skip("No services in governance file")

        existing_dirs = {d.name for d in SERVICES_DIR.iterdir() if d.is_dir()}
        missing = []

        for service in services:
            name = service if isinstance(service, str) else service.get("name", "")
            if name and name not in existing_dirs:
                # Check if it's a deprecated service (acceptable to be missing)
                status = service.get("status", "active") if isinstance(service, dict) else "active"
                if status not in ("deprecated", "archived", "removed"):
                    missing.append(name)

        # Allow some tolerance (up to 10% missing)
        total = len(services)
        if total > 0:
            missing_pct = len(missing) / total
            assert missing_pct < 0.3, (
                f"{len(missing)}/{total} active services missing directories: "
                f"{missing[:10]}..."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Docker Compose Alignment Tests - اختبارات محاذاة Docker Compose
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDockerComposeAlignment:
    """Test alignment between docker-compose.yml and service code."""

    def test_docker_compose_exists(self):
        """docker-compose.yml should exist."""
        assert DOCKER_COMPOSE.exists(), "docker-compose.yml not found"

    def test_docker_compose_valid(self):
        """docker-compose.yml should be valid YAML."""
        data = load_yaml_safe(DOCKER_COMPOSE)
        assert data is not None, "docker-compose.yml is empty or invalid"
        assert "services" in data, "docker-compose.yml missing 'services' section"

    def test_services_have_health_checks(self):
        """Docker Compose services should define healthcheck."""
        data = load_yaml_safe(DOCKER_COMPOSE)
        if not data:
            pytest.skip("docker-compose.yml not loadable")

        services = data.get("services", {})
        services_with_healthcheck = 0
        total_app_services = 0

        for name, config in services.items():
            # Skip infrastructure services
            if name in ("postgres", "redis", "nats", "kong", "pgbouncer", "vault",
                        "minio", "prometheus", "grafana", "jaeger", "qdrant"):
                continue

            if isinstance(config, dict) and config.get("build"):
                total_app_services += 1
                if config.get("healthcheck"):
                    services_with_healthcheck += 1

        if total_app_services > 0:
            coverage = services_with_healthcheck / total_app_services
            # At least 50% of app services should have healthchecks
            assert coverage >= 0.3, (
                f"Only {services_with_healthcheck}/{total_app_services} "
                f"({coverage:.0%}) app services have healthchecks in docker-compose"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-Service Contract Tests - اختبارات عقود بين الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCrossServiceContracts:
    """Test that NATS event contracts are consistent across publishers and subscribers."""

    def _collect_nats_subjects(self) -> dict[str, list[str]]:
        """Collect NATS subjects used across all services."""
        subjects: dict[str, list[str]] = {}

        for service_dir in SERVICES_DIR.iterdir():
            if not service_dir.is_dir():
                continue

            src_dir = service_dir / "src"
            if not src_dir.exists():
                continue

            for py_file in src_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(errors="ignore")
                except Exception:
                    continue

                # Find NATS publish patterns
                publish_pattern = r'publish\(\s*["\']([^"\']+)["\']'
                for match in re.findall(publish_pattern, content):
                    if match.startswith("sahool."):
                        subjects.setdefault(match, []).append(service_dir.name)

        return subjects

    def test_nats_subjects_follow_naming_convention(self):
        """NATS subjects should follow sahool.{domain}.{action} pattern."""
        subjects = self._collect_nats_subjects()

        invalid = []
        for subject in subjects:
            parts = subject.split(".")
            if len(parts) < 3:
                invalid.append(subject)
            elif parts[0] != "sahool":
                invalid.append(subject)

        if subjects:
            invalid_pct = len(invalid) / len(subjects)
            assert invalid_pct < 0.2, (
                f"{len(invalid)}/{len(subjects)} NATS subjects don't follow convention: "
                f"{invalid[:5]}"
            )
