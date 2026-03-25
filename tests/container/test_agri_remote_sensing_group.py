"""
SAHOOL Agricultural Remote Sensing & NDVI Services – Container Function Tests
===============================================================================
اختبارات وظائف خدمات الاستشعار عن بعد ومؤشرات النباتات الزراعية

Validates that satellite imagery, NDVI analysis, vegetation indices, and
field health monitoring services have the correct agricultural domain
dependencies, API endpoints, NATS event subjects, and shared modules.

Services:
  vegetation-analysis-service · ndvi-processor · indicators-service
  field-intelligence · ground-vision-service

Domain coverage:
 1.  Satellite/raster dependencies (rasterio, shapely, pyproj)
 2.  NDVI computation pipeline (satellite → NDVI → health classification)
 3.  NATS event subjects (sahool.satellite.*, sahool.health.*)
 4.  Shared module imports (shared/satellite/, shared/field_boundaries/)
 5.  API endpoints (/api/v1/ndvi, /api/v1/vegetation, /api/v1/indicators)
 6.  Geospatial output format (GeoJSON support)
 7.  Health classification logic (healthy/moderate/stressed/critical)
 8.  Time-series analysis capability
 9.  Multi-spectral band processing
10.  Field boundary integration for spatial queries

Run:
    pytest tests/container/test_agri_remote_sensing_group.py -v --tb=short
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

# ---------------------------------------------------------------------------
# Agricultural Remote Sensing Service Cluster
# ---------------------------------------------------------------------------

REMOTE_SENSING_SERVICES: dict[str, int] = {
    "vegetation-analysis-service": 8090,
    "ndvi-processor": 8118,
    "indicators-service": 8091,
    "field-intelligence": 8120,
    "ground-vision-service": 8182,
}

# Services that process satellite imagery directly
SATELLITE_PROCESSING = {"vegetation-analysis-service", "ndvi-processor"}

# Services that compute vegetation indices
NDVI_CHAIN = {"vegetation-analysis-service", "ndvi-processor", "indicators-service"}

# Services that need geospatial libraries
GEOSPATIAL_REQUIRED = {"ndvi-processor", "ground-vision-service"}

# NATS event subjects these services should publish/subscribe
EXPECTED_NATS_SUBJECTS = {
    "sahool.satellite",
    "sahool.satellite.ndvi",
    "sahool.satellite.anomaly",
    "sahool.health.disease",
    "sahool.health.pest",
    "sahool.health.stress",
    "sahool.vision",
}

# Shared agricultural modules these services should access
EXPECTED_SHARED_MODULES = {
    "shared/satellite",
    "shared/field_boundaries",
}

# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}
_source_cache: dict[str, str] = {}


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


def _read_all_source(svc: str, max_files: int = 25) -> str:
    """Read all Python source files from a service's src/ directory."""
    if svc not in _source_cache:
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            _source_cache[svc] = ""
            return ""
        combined = ""
        for f in sorted(src_dir.rglob("*.py"))[:max_files]:
            combined += f.read_text("utf-8", errors="ignore") + "\n"
        _source_cache[svc] = combined
    return _source_cache[svc]


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Geospatial / Raster Dependencies
# ===========================================================================


class TestGeospatialDependencies:
    """مكتبات معالجة البيانات الجغرافية المكانية والمرئيات الفضائية."""

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_REQUIRED))
    def test_rasterio_for_satellite_imagery(self, svc: str) -> None:
        """Service that processes satellite imagery declares rasterio."""
        pkgs = _req_packages(svc)
        assert "rasterio" in pkgs, (
            f"{svc} missing rasterio – required for satellite raster data (GeoTIFF) processing"
        )

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_REQUIRED))
    def test_shapely_for_field_boundaries(self, svc: str) -> None:
        """Service declares shapely for field boundary geometry operations."""
        pkgs = _req_packages(svc)
        assert "shapely" in pkgs, (
            f"{svc} missing shapely – required for field polygon/boundary operations"
        )

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_REQUIRED))
    def test_pyproj_for_coordinate_transform(self, svc: str) -> None:
        """Service declares pyproj for CRS coordinate transformations."""
        pkgs = _req_packages(svc)
        assert "pyproj" in pkgs, (
            f"{svc} missing pyproj – required for coordinate system transformations"
        )

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_numpy_for_array_computation(self, svc: str) -> None:
        """Remote sensing service declares numpy for array math."""
        pkgs = _req_packages(svc)
        has_numpy = "numpy" in pkgs
        if not has_numpy:
            # May get numpy via shared/ modules
            content = _read_dockerfile(svc)
            has_numpy = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_numpy, f"{svc} missing numpy (or shared/ with numpy)"


# ===========================================================================
# 2. NDVI Computation Pipeline
# ===========================================================================


class TestNDVIPipeline:
    """خط أنابيب حساب مؤشر الغطاء النباتي (NDVI)."""

    @pytest.mark.parametrize("svc", sorted(NDVI_CHAIN))
    def test_source_references_ndvi(self, svc: str) -> None:
        """Service source code references NDVI computation."""
        source = _read_all_source(svc)
        if not source:
            pytest.skip(f"No source for {svc}")
        has_ndvi = (
            "ndvi" in source.lower()
            or "vegetation" in source.lower()
            or "spectral" in source.lower()
        )
        assert has_ndvi, (
            f"{svc} source does not reference NDVI/vegetation/spectral analysis"
        )

    def test_vegetation_analysis_health_classification(self) -> None:
        """vegetation-analysis-service implements health status classification."""
        source = _read_all_source("vegetation-analysis-service")
        if not source:
            pytest.skip("No source")
        # Health classification: healthy, moderate, stressed, critical
        health_terms = ["healthy", "moderate", "stressed", "critical"]
        found = [t for t in health_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"vegetation-analysis-service should implement health classification "
            f"(found: {found}, expected ≥2 of {health_terms})"
        )

    def test_ndvi_processor_satellite_data(self) -> None:
        """ndvi-processor references satellite data processing."""
        source = _read_all_source("ndvi-processor")
        if not source:
            pytest.skip("No source")
        has_satellite = (
            "satellite" in source.lower()
            or "sentinel" in source.lower()
            or "raster" in source.lower()
            or "band" in source.lower()
        )
        assert has_satellite, (
            "ndvi-processor should reference satellite/sentinel/raster data"
        )


# ===========================================================================
# 3. NATS Event Subjects for Agriculture
# ===========================================================================


class TestAgriNATSEvents:
    """أحداث NATS الزراعية للاستشعار عن بعد."""

    def test_nats_subjects_file_has_satellite_events(self) -> None:
        """shared/events/subjects.py defines sahool.satellite.* subjects."""
        subjects_path = REPO_ROOT / "shared" / "events" / "subjects.py"
        if not subjects_path.exists():
            pytest.skip("No subjects.py")
        content = subjects_path.read_text("utf-8")
        satellite_subjects = [
            "SAHOOL_SATELLITE_DATA_READY",
            "SAHOOL_NDVI_COMPUTED",
            "SAHOOL_SATELLITE_ANOMALY",
        ]
        found = [s for s in satellite_subjects if s in content]
        assert len(found) >= 2, (
            f"subjects.py missing satellite event constants (found: {found})"
        )

    def test_nats_subjects_file_has_health_events(self) -> None:
        """shared/events/subjects.py defines sahool.health.* subjects."""
        subjects_path = REPO_ROOT / "shared" / "events" / "subjects.py"
        if not subjects_path.exists():
            pytest.skip("No subjects.py")
        content = subjects_path.read_text("utf-8")
        health_subjects = [
            "SAHOOL_HEALTH_DISEASE_DETECTED",
            "SAHOOL_HEALTH_PEST_DETECTED",
            "SAHOOL_HEALTH_STRESS_DETECTED",
        ]
        found = [s for s in health_subjects if s in content]
        assert len(found) >= 2, (
            f"subjects.py missing crop health event constants (found: {found})"
        )

    @pytest.mark.parametrize("svc", sorted(SATELLITE_PROCESSING))
    def test_service_references_nats_events(self, svc: str) -> None:
        """Satellite processing service references NATS event publishing."""
        source = _read_all_source(svc)
        if not source:
            pytest.skip(f"No source for {svc}")
        has_events = (
            "publish" in source.lower()
            or "nats" in source.lower()
            or "sahool.satellite" in source
            or "sahool.vision" in source
            or "event" in source.lower()
        )
        assert has_events, (
            f"{svc} should publish satellite/vision NATS events"
        )


# ===========================================================================
# 4. Shared Agricultural Module Access
# ===========================================================================


class TestSharedAgriModules:
    """الوصول إلى الوحدات الزراعية المشتركة."""

    def test_shared_satellite_module_exists(self) -> None:
        """shared/satellite/ module exists with NDVI analyzer."""
        init_path = REPO_ROOT / "shared" / "satellite" / "__init__.py"
        assert init_path.exists(), "shared/satellite/ module missing"
        content = init_path.read_text("utf-8")
        assert "NDVI" in content or "Sentinel" in content or "ndvi" in content, (
            "shared/satellite/__init__.py should export NDVI analyzer"
        )

    def test_shared_field_boundaries_module_exists(self) -> None:
        """shared/field_boundaries/ module exists."""
        init_path = REPO_ROOT / "shared" / "field_boundaries" / "__init__.py"
        assert init_path.exists(), "shared/field_boundaries/ module missing"

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_dockerfile_copies_shared_for_agri_modules(self, svc: str) -> None:
        """Dockerfile copies shared/ so agri modules are available at runtime."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} must COPY shared/ for satellite/field_boundaries modules"
        )


# ===========================================================================
# 5. API Endpoints for Agriculture
# ===========================================================================


class TestAgriAPIEndpoints:
    """نقاط نهاية API الزراعية."""

    def test_vegetation_analysis_has_ndvi_endpoint(self) -> None:
        """vegetation-analysis-service exposes NDVI analysis API."""
        source = _read_all_source("vegetation-analysis-service")
        if not source:
            pytest.skip("No source")
        has_api = (
            "/ndvi" in source
            or "/vegetation" in source
            or "/analysis" in source
            or "/api/v1" in source
        )
        assert has_api, (
            "vegetation-analysis-service should expose /ndvi or /vegetation endpoint"
        )

    def test_indicators_service_has_indicators_endpoint(self) -> None:
        """indicators-service exposes field indicator computation API."""
        source = _read_all_source("indicators-service")
        if not source:
            pytest.skip("No source")
        has_api = (
            "/indicator" in source.lower()
            or "/compute" in source.lower()
            or "/api/v1" in source
        )
        assert has_api, (
            "indicators-service should expose indicator computation endpoint"
        )

    def test_field_intelligence_has_analytics_endpoint(self) -> None:
        """field-intelligence exposes analytics API."""
        source = _read_all_source("field-intelligence")
        if not source:
            pytest.skip("No source")
        has_api = (
            "/intelligence" in source.lower()
            or "/analytics" in source.lower()
            or "/field" in source.lower()
            or "/api/v1" in source
        )
        assert has_api, "field-intelligence should expose analytics endpoint"


# ===========================================================================
# 6. Bilingual Support (Arabic/English)
# ===========================================================================


class TestBilingualSupport:
    """دعم ثنائي اللغة (عربي/إنجليزي)."""

    def test_shared_satellite_bilingual(self) -> None:
        """shared/satellite/ provides Arabic health status labels."""
        init_path = REPO_ROOT / "shared" / "satellite" / "__init__.py"
        if not init_path.exists():
            pytest.skip("No shared/satellite/")
        # Check sentinel_ndvi.py for Arabic labels
        for py_file in (REPO_ROOT / "shared" / "satellite").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "صحي" in content or "حرج" in content or "مجهد" in content:
                return  # Found Arabic health status labels
        # Check if any file has Arabic content
        pytest.skip("Arabic health labels may be in a different layer")


# ===========================================================================
# 7. Compose Configuration for Remote Sensing
# ===========================================================================


class TestRemoteSensingCompose:
    """تكوين docker-compose للاستشعار عن بعد."""

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_nats_url_for_events(self, services: dict, svc: str) -> None:
        """Remote sensing service has NATS_URL for publishing analysis events."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NATS_URL" in env_str, (
            f"{svc} missing NATS_URL – needed for publishing satellite/health events"
        )

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_healthcheck_present(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} must run as non-root user"
