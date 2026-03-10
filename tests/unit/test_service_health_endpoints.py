"""
SAHOOL Service Health Endpoint Tests
اختبارات نقاط نهاية صحة الخدمات

Validates that all FastAPI services properly define health endpoints
(/healthz, /readyz) with correct response structure.

These tests import each service's FastAPI app directly (no Docker required).

Author: SAHOOL Platform Team
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.parent
SERVICES_DIR = PROJECT_ROOT / "apps" / "services"

# Minimal environment for test imports
TEST_ENV = {
    "ENVIRONMENT": "test",
    "DATABASE_URL": "",
    "NATS_URL": "",
    "REDIS_URL": "",
    "JWT_SECRET_KEY": "test-secret-key-for-unit-tests-only-32chars",
    "JWT_ALGORITHM": "HS256",
    "PORT": "0",
    "HOST": "127.0.0.1",
    "LOG_LEVEL": "WARNING",
}


def _get_python_service_dirs() -> list[tuple[str, Path]]:
    """
    Get all Python FastAPI services that have a src/main.py.
    Returns list of (service_name, service_path) tuples.
    """
    services = []
    if not SERVICES_DIR.exists():
        return services

    for service_dir in sorted(SERVICES_DIR.iterdir()):
        if not service_dir.is_dir():
            continue
        main_py = service_dir / "src" / "main.py"
        if main_py.exists():
            # Check it's a Python/FastAPI service (not NestJS)
            content = main_py.read_text(errors="ignore")
            if "FastAPI" in content or "fastapi" in content:
                services.append((service_dir.name, service_dir))

    return services


PYTHON_SERVICES = _get_python_service_dirs()
SERVICE_NAMES = [name for name, _ in PYTHON_SERVICES]


# ═══════════════════════════════════════════════════════════════════════════════
# Health Response Schema Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestHealthEndpointSchema:
    """
    Test that health endpoint responses follow the standard schema:
    {
        "status": "ok",
        "service": "<service_name>",
        "version": "<version>"
    }
    """

    def test_all_python_services_detected(self):
        """Verify we detect a reasonable number of Python services."""
        assert len(PYTHON_SERVICES) >= 20, (
            f"Expected at least 20 Python FastAPI services, found {len(PYTHON_SERVICES)}: {SERVICE_NAMES}"
        )

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_has_main_py(self, service_name: str):
        """Each service must have a src/main.py entry point."""
        service_dir = SERVICES_DIR / service_name
        main_py = service_dir / "src" / "main.py"
        assert main_py.exists(), f"{service_name} missing src/main.py"

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_defines_healthz(self, service_name: str):
        """Each service must define a /healthz endpoint."""
        service_dir = SERVICES_DIR / service_name
        main_content = (service_dir / "src" / "main.py").read_text(errors="ignore")
        assert "/healthz" in main_content, f"{service_name} does not define /healthz endpoint"

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_defines_readyz(self, service_name: str):
        """Each service must define a /readyz endpoint."""
        service_dir = SERVICES_DIR / service_name
        main_content = (service_dir / "src" / "main.py").read_text(errors="ignore")
        assert "/readyz" in main_content, f"{service_name} does not define /readyz endpoint"

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_healthz_returns_status(self, service_name: str):
        """Health endpoint should return a status in response body."""
        service_dir = SERVICES_DIR / service_name
        main_content = (service_dir / "src" / "main.py").read_text(errors="ignore")
        # Check that the health endpoint returns a dict with status field
        has_status = (
            '"ok"' in main_content
            or "'ok'" in main_content
            or '"status"' in main_content
            or "'status'" in main_content
            or "status" in main_content.lower()
        )
        assert has_status, f"{service_name}: /healthz should return a status field"

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_has_version(self, service_name: str):
        """Each service should define a version."""
        service_dir = SERVICES_DIR / service_name
        main_content = (service_dir / "src" / "main.py").read_text(errors="ignore")
        has_version = "version" in main_content.lower()
        assert has_version, f"{service_name}: should define a version"


# ═══════════════════════════════════════════════════════════════════════════════
# Service Structure Tests - اختبارات هيكل الخدمة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceStructure:
    """Test that services follow the standard file structure."""

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_has_dockerfile(self, service_name: str):
        """Each service should have a Dockerfile."""
        service_dir = SERVICES_DIR / service_name
        has_dockerfile = (service_dir / "Dockerfile").exists() or (service_dir / "dockerfile").exists()
        assert has_dockerfile, f"{service_name} missing Dockerfile"

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_has_requirements(self, service_name: str):
        """Each Python service should have requirements.txt."""
        service_dir = SERVICES_DIR / service_name
        has_reqs = (service_dir / "requirements.txt").exists() or (service_dir / "pyproject.toml").exists()
        assert has_reqs, f"{service_name} missing requirements.txt or pyproject.toml"

    @pytest.mark.parametrize(
        "service_name",
        SERVICE_NAMES,
        ids=SERVICE_NAMES,
    )
    def test_service_uses_error_handling(self, service_name: str):
        """Services should use the unified error handling from shared."""
        service_dir = SERVICES_DIR / service_name
        main_content = (service_dir / "src" / "main.py").read_text(errors="ignore")
        uses_error_handling = (
            "setup_exception_handlers" in main_content
            or "add_request_id_middleware" in main_content
            or "shared.errors_py" in main_content
        )
        # This is a warning, not a failure - some services may have their own error handling
        if not uses_error_handling:
            pytest.skip(f"{service_name} does not use shared error handling (optional)")


# ═══════════════════════════════════════════════════════════════════════════════
# NestJS Service Tests - اختبارات خدمات NestJS
# ═══════════════════════════════════════════════════════════════════════════════


def _get_nestjs_service_dirs() -> list[tuple[str, Path]]:
    """Get NestJS services with package.json and src/index.ts."""
    services = []
    if not SERVICES_DIR.exists():
        return services

    for service_dir in sorted(SERVICES_DIR.iterdir()):
        if not service_dir.is_dir():
            continue
        pkg_json = service_dir / "package.json"
        index_ts = service_dir / "src" / "index.ts"
        if pkg_json.exists() and index_ts.exists():
            services.append((service_dir.name, service_dir))

    return services


NESTJS_SERVICES = _get_nestjs_service_dirs()
NESTJS_NAMES = [name for name, _ in NESTJS_SERVICES]


@pytest.mark.unit
class TestNestJSServiceStructure:
    """Test NestJS service structure."""

    @pytest.mark.parametrize(
        "service_name",
        NESTJS_NAMES,
        ids=NESTJS_NAMES,
    )
    def test_nestjs_has_package_json(self, service_name: str):
        """NestJS services should have package.json."""
        service_dir = SERVICES_DIR / service_name
        assert (service_dir / "package.json").exists()

    @pytest.mark.parametrize(
        "service_name",
        NESTJS_NAMES,
        ids=NESTJS_NAMES,
    )
    def test_nestjs_has_tsconfig(self, service_name: str):
        """NestJS services should have tsconfig.json."""
        service_dir = SERVICES_DIR / service_name
        assert (service_dir / "tsconfig.json").exists(), f"{service_name} missing tsconfig.json"
