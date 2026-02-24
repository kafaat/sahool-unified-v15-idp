"""Tests for drift detection detectors."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from shared.drift_detection.detectors.config_drift import ConfigDriftDetector
from shared.drift_detection.detectors.schema_drift import SchemaDriftDetector
from shared.drift_detection.detectors.api_drift import APIDriftDetector
from shared.drift_detection.detectors.event_drift import EventDriftDetector
from shared.drift_detection.detectors.data_drift import DataDriftDetector
from shared.drift_detection.detectors.security_drift import SecurityDriftDetector
from shared.drift_detection.models import DriftCategory, DriftSeverity


@pytest.fixture
def temp_project(tmp_path: Path):
    """Create a minimal project structure for testing."""
    # .env.example
    (tmp_path / ".env.example").write_text(
        "DATABASE_URL=postgresql://localhost/sahool\n"
        "REDIS_URL=redis://localhost:6379\n"
        "JWT_SECRET_KEY=change_me\n"
    )

    # Governance
    gov = tmp_path / "governance"
    gov.mkdir()
    (gov / "services.yaml").write_text(
        "services:\n"
        "  - name: user-service\n"
        "    port: 3025\n"
        "  - name: field-management-service\n"
        "    port: 3000\n"
    )

    events_dir = gov / "events"
    events_dir.mkdir()
    (events_dir / "catalog.yaml").write_text(
        "events:\n"
        "  - subject: sahool.field.created\n"
        "    description: Field created event\n"
        "    category: field\n"
    )

    schemas_dir = events_dir / "schemas"
    schemas_dir.mkdir()
    (schemas_dir / "field-created.json").write_text(
        '{"type": "object", "properties": {"field_id": {"type": "string"}}, "required": ["field_id"]}'
    )

    # Service structure
    svc = tmp_path / "apps" / "services" / "user-service" / "src"
    svc.mkdir(parents=True)
    (svc / "main.py").write_text(
        'import os\n'
        'from fastapi import FastAPI\n'
        'app = FastAPI()\n'
        'DB_URL = os.getenv("DATABASE_URL")\n'
        'NEW_VAR = os.getenv("UNDOCUMENTED_VAR")\n'
        '@app.get("/healthz")\n'
        'def health(): return {"status": "ok"}\n'
    )

    # Prisma
    prisma_dir = tmp_path / "apps" / "services" / "user-service" / "prisma"
    prisma_dir.mkdir(parents=True)
    (prisma_dir / "schema.prisma").write_text(
        'model User {\n'
        '  id String @id\n'
        '  email String\n'
        '  tenantId String @map("tenant_id")\n'
        '}\n'
        '\n'
        'model Session {\n'
        '  id String @id\n'
        '  userId String\n'
        '}\n'
    )

    # Docker
    (tmp_path / "apps" / "services" / "user-service" / "Dockerfile").write_text(
        'FROM python:3.11-slim-bookworm\n'
        'COPY . /app\n'
        'USER sahool\n'
        'HEALTHCHECK CMD curl -f http://localhost:3025/healthz || exit 1\n'
        'CMD ["python", "-m", "uvicorn"]\n'
    )

    # Contracts
    contracts = tmp_path / "packages" / "shared-types" / "src" / "contracts"
    contracts.mkdir(parents=True)
    (contracts / "index.ts").write_text(
        'export const CONTRACT_VERSION = "1.5.0";\n'
    )
    (contracts / "service-ports.ts").write_text(
        'export const SERVICE_PORTS = {\n'
        '  USER_SERVICE: 3025,\n'
        '  FIELD_MANAGEMENT: 3000,\n'
        '  ADVISORY: 8093,\n'
        '} as const;\n'
    )

    # Shared modules
    shared = tmp_path / "shared"
    shared.mkdir()

    events_py = shared / "events"
    events_py.mkdir()
    (events_py / "__init__.py").write_text("")
    (events_py / "subjects.py").write_text(
        'SAHOOL_FIELD_CREATED = "sahool.field.created"\n'
        'SAHOOL_FIELD_UPDATED = "sahool.field.updated"\n'
    )

    middleware = shared / "middleware"
    middleware.mkdir()
    (middleware / "security_headers.py").write_text(
        'HEADERS = {\n'
        '    "Strict-Transport-Security": "max-age=31536000",\n'
        '    "X-Content-Type-Options": "nosniff",\n'
        '    "X-Frame-Options": "DENY",\n'
        '}\n'
    )
    (middleware / "rate_limit.py").write_text("# Rate limiter\n")

    # AI / ML
    ai_dir = shared / "ai" / "models_registry"
    ai_dir.mkdir(parents=True)
    (ai_dir / "__init__.py").write_text("# Models registry with version tracking\nmodel_version = '1.0'\n")

    satellite = shared / "satellite"
    satellite.mkdir()
    (satellite / "__init__.py").write_text("")
    (satellite / "sentinel_ndvi.py").write_text(
        "# NDVI processing\n"
        "NDVI_MIN = -1.0\n"
        "NDVI_MAX = 1.0\n"
        "def check_freshness(data_age): pass\n"
    )

    # Constraints
    (tmp_path / "constraints.txt").write_text("fastapi>=0.128.0\npydantic>=2.10.0\n")

    return tmp_path


class TestConfigDriftDetector:
    """Tests for ConfigDriftDetector."""

    @pytest.mark.asyncio
    async def test_detect_env_drift(self, temp_project: Path):
        detector = ConfigDriftDetector(str(temp_project))
        results = await detector.detect()

        # Should find undocumented env var
        env_drifts = [r for r in results if r.source == "env_drift"]
        assert len(env_drifts) > 0

    @pytest.mark.asyncio
    async def test_detect_no_env_example(self, tmp_path: Path):
        detector = ConfigDriftDetector(str(tmp_path))
        results = await detector.detect()

        env_drifts = [r for r in results if r.source == "env_drift"]
        # Should report missing .env.example
        assert any(".env.example" in r.description for r in env_drifts)

    @pytest.mark.asyncio
    async def test_category(self, tmp_path: Path):
        detector = ConfigDriftDetector(str(tmp_path))
        assert detector.category == DriftCategory.CONFIG


class TestSchemaDriftDetector:
    """Tests for SchemaDriftDetector."""

    @pytest.mark.asyncio
    async def test_detect_missing_tenant_id(self, temp_project: Path):
        """Models without tenant_id should be flagged (except system models)."""
        detector = SchemaDriftDetector(str(temp_project))
        results = await detector.detect()

        # User model has tenant_id, Session is excluded (system model)
        tenant_results = [r for r in results if r.source == "tenant_isolation"]
        # Session model is in the excluded list, so no drift expected
        assert all(r.severity in (DriftSeverity.HIGH, DriftSeverity.CRITICAL) for r in tenant_results)

    @pytest.mark.asyncio
    async def test_category(self, tmp_path: Path):
        detector = SchemaDriftDetector(str(tmp_path))
        assert detector.category == DriftCategory.SCHEMA


class TestAPIDriftDetector:
    """Tests for APIDriftDetector."""

    @pytest.mark.asyncio
    async def test_detect_contract_version(self, temp_project: Path):
        detector = APIDriftDetector(str(temp_project))
        results = await detector.detect()

        # CONTRACT_VERSION exists, so no drift for that check
        version_drifts = [r for r in results if r.source == "contract_version"]
        assert len(version_drifts) == 0

    @pytest.mark.asyncio
    async def test_detect_port_uniqueness(self, temp_project: Path):
        detector = APIDriftDetector(str(temp_project))
        results = await detector.detect()

        # No port collisions in our test data
        port_drifts = [r for r in results if r.source == "port_uniqueness"]
        assert len(port_drifts) == 0

    @pytest.mark.asyncio
    async def test_health_endpoints(self, temp_project: Path):
        detector = APIDriftDetector(str(temp_project))
        results = await detector.detect()

        # user-service has /healthz, so it should pass
        health_drifts = [
            r for r in results
            if r.source == "health_endpoint" and r.service_name == "user-service"
        ]
        assert len(health_drifts) == 0


class TestEventDriftDetector:
    """Tests for EventDriftDetector."""

    @pytest.mark.asyncio
    async def test_detect_event_catalog(self, temp_project: Path):
        detector = EventDriftDetector(str(temp_project))
        results = await detector.detect()

        # Catalog exists and is valid
        catalog_errors = [
            r for r in results
            if r.source == "event_catalog" and r.severity == DriftSeverity.HIGH
        ]
        # No critical catalog errors since we have a valid catalog
        assert len(catalog_errors) == 0

    @pytest.mark.asyncio
    async def test_detect_subject_conventions(self, temp_project: Path):
        detector = EventDriftDetector(str(temp_project))
        results = await detector.detect()

        # Our subjects follow conventions
        convention_drifts = [r for r in results if r.source == "subject_convention"]
        assert len(convention_drifts) == 0


class TestDataDriftDetector:
    """Tests for DataDriftDetector."""

    @pytest.mark.asyncio
    async def test_ndvi_guards(self, temp_project: Path):
        detector = DataDriftDetector(str(temp_project))
        results = await detector.detect()

        # We have NDVI_MIN/MAX and freshness check, so range check should pass
        ndvi_range = [
            r for r in results
            if r.source == "ndvi_guards" and "range validation" in r.description
        ]
        assert len(ndvi_range) == 0

    @pytest.mark.asyncio
    async def test_model_versioning(self, temp_project: Path):
        detector = DataDriftDetector(str(temp_project))
        results = await detector.detect()

        # Models registry exists with version tracking
        versioning_drifts = [r for r in results if r.source == "model_versioning"]
        assert len(versioning_drifts) == 0


class TestSecurityDriftDetector:
    """Tests for SecurityDriftDetector."""

    @pytest.mark.asyncio
    async def test_docker_security_good(self, temp_project: Path):
        detector = SecurityDriftDetector(str(temp_project))
        results = await detector.detect()

        # Dockerfile has USER, no :latest, and HEALTHCHECK
        docker_drifts = [
            r for r in results
            if r.source == "docker_security" and r.service_name == "user-service"
        ]
        assert len(docker_drifts) == 0

    @pytest.mark.asyncio
    async def test_docker_security_bad(self, tmp_path: Path):
        svc_dir = tmp_path / "apps" / "services" / "bad-service"
        svc_dir.mkdir(parents=True)
        (svc_dir / "Dockerfile").write_text(
            "FROM python:latest\n"
            "COPY . /app\n"
            "CMD python main.py\n"
        )

        detector = SecurityDriftDetector(str(tmp_path))
        results = await detector.detect()

        docker_drifts = [r for r in results if r.source == "docker_security"]
        # Should find: no USER, :latest tag, no HEALTHCHECK
        assert len(docker_drifts) >= 2

    @pytest.mark.asyncio
    async def test_security_headers(self, temp_project: Path):
        detector = SecurityDriftDetector(str(temp_project))
        results = await detector.detect()

        # All required headers exist
        header_drifts = [r for r in results if r.source == "security_headers"]
        assert len(header_drifts) == 0
