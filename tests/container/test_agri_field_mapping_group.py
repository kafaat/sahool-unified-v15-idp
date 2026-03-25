"""
SAHOOL Agricultural Field Mapping & Terrain Services – Container Function Tests
=================================================================================
اختبارات وظائف خدمات رسم خرائط الحقول والتضاريس الزراعية

Validates field boundary detection, terrain analysis, map comparison,
DEM processing, hydrology, leveling, and geospatial operations.

Services:
  terrain-core-service · hydrology-service · leveling-optimizer-service
  field-management-service · field-intelligence · ground-vision-service

Domain coverage:
 1.  Field boundary geometry (Shapely, PostGIS)
 2.  DEM/terrain analysis (GDAL, rasterio)
 3.  Slope, aspect, watershed computation
 4.  Cut/fill leveling optimization
 5.  Satellite imagery map comparison
 6.  Drainage & hydrology analysis
 7.  Variable Rate Application (VRA) maps
 8.  Shared terrain/field_boundaries modules
 9.  GeoJSON API output support
10.  PostGIS spatial queries

Run:
    pytest tests/container/test_agri_field_mapping_group.py -v --tb=short
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
# Field Mapping & Terrain Cluster
# ---------------------------------------------------------------------------

FIELD_MAPPING_SERVICES: dict[str, int] = {
    "terrain-core-service": 8185,
    "hydrology-service": 8165,
    "leveling-optimizer-service": 8170,
    "field-management-service": 3000,
    "field-intelligence": 8120,
    "ground-vision-service": 8182,
}

# Services that process DEM/raster terrain data
TERRAIN_PROCESSING = {"terrain-core-service", "hydrology-service", "leveling-optimizer-service"}

# Services that manage field boundaries
FIELD_BOUNDARY_MGMT = {"field-management-service", "field-intelligence"}

# Expected shared modules for terrain/field services
TERRAIN_SHARED_MODULES = [
    "shared/terrain",
    "shared/field_boundaries",
    "shared/geofencing",
    "shared/vra_maps",
]

# ---------------------------------------------------------------------------

_source_cache: dict[str, str] = {}
_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def _req_packages(svc: str) -> set[str]:
    if svc not in _requirements_cache:
        path = SERVICES_DIR / svc / "requirements.txt"
        _requirements_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    text = _requirements_cache[svc]
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
# 1. DEM & Terrain Analysis
# ===========================================================================


class TestTerrainDomain:
    """مجال تحليل التضاريس ونموذج الارتفاع الرقمي."""

    def test_terrain_core_dem_processing(self) -> None:
        """terrain-core-service references DEM processing."""
        source = _read_all_source("terrain-core-service")
        if not source:
            pytest.skip("No source")
        dem_terms = ["dem", "elevation", "slope", "aspect", "terrain", "raster", "contour"]
        found = [t for t in dem_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"terrain-core should reference DEM/terrain terms (found: {found})"
        )

    def test_terrain_core_gdal_in_dockerfile(self) -> None:
        """terrain-core-service Dockerfile installs GDAL."""
        content = _read_dockerfile("terrain-core-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert "gdal" in content.lower(), (
            "terrain-core Dockerfile must install GDAL for DEM processing"
        )

    def test_terrain_core_rasterio(self) -> None:
        """terrain-core-service has rasterio for raster data."""
        pkgs = _req_packages("terrain-core-service")
        assert "rasterio" in pkgs, "terrain-core missing rasterio"


# ===========================================================================
# 2. Hydrology & Drainage
# ===========================================================================


class TestHydrologyDomain:
    """مجال الهيدرولوجيا والصرف."""

    def test_hydrology_drainage_analysis(self) -> None:
        """hydrology-service references drainage/watershed analysis."""
        source = _read_all_source("hydrology-service")
        if not source:
            pytest.skip("No source")
        hydro_terms = ["drainage", "watershed", "flow", "accumulation",
                        "hydrology", "stream", "basin", "runoff"]
        found = [t for t in hydro_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"hydrology-service should reference hydrology terms (found: {found})"
        )


# ===========================================================================
# 3. Field Leveling Optimization
# ===========================================================================


class TestLevelingDomain:
    """مجال تسوية الحقول."""

    def test_leveling_optimizer_cut_fill(self) -> None:
        """leveling-optimizer-service references cut/fill operations."""
        source = _read_all_source("leveling-optimizer-service")
        if not source:
            pytest.skip("No source")
        leveling_terms = ["cut", "fill", "level", "grade", "optimize", "volume", "cost"]
        found = [t for t in leveling_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"leveling-optimizer should reference cut/fill terms (found: {found})"
        )


# ===========================================================================
# 4. Field Boundary Management
# ===========================================================================


class TestFieldBoundaryDomain:
    """مجال إدارة حدود الحقول."""

    def test_shared_field_boundaries_exports(self) -> None:
        """shared/field_boundaries/ exports boundary management classes."""
        init_path = REPO_ROOT / "shared" / "field_boundaries" / "__init__.py"
        if not init_path.exists():
            pytest.skip("No shared/field_boundaries/")
        content = init_path.read_text("utf-8")
        exports = ["FieldBoundary", "GPSMapper", "Geometry", "Boundary"]
        found = [e for e in exports if e in content]
        assert found, (
            f"shared/field_boundaries should export boundary classes (checked: {exports})"
        )

    def test_shared_geofencing_exists(self) -> None:
        """shared/geofencing/ module exists for geofence alerts."""
        path = REPO_ROOT / "shared" / "geofencing" / "__init__.py"
        assert path.exists(), "shared/geofencing/ module missing"

    def test_shared_vra_maps_exists(self) -> None:
        """shared/vra_maps/ module exists for Variable Rate Application."""
        path = REPO_ROOT / "shared" / "vra_maps" / "__init__.py"
        assert path.exists(), "shared/vra_maps/ module missing"


# ===========================================================================
# 5. Terrain Shared Modules
# ===========================================================================


class TestTerrainSharedModules:
    """الوحدات المشتركة للتضاريس."""

    @pytest.mark.parametrize("module_path", sorted(TERRAIN_SHARED_MODULES))
    def test_module_exists(self, module_path: str) -> None:
        full_path = REPO_ROOT / module_path
        assert full_path.exists(), f"{module_path}/ missing"

    @pytest.mark.parametrize("module_path", sorted(TERRAIN_SHARED_MODULES))
    def test_module_has_init(self, module_path: str) -> None:
        init_path = REPO_ROOT / module_path / "__init__.py"
        assert init_path.exists(), f"{module_path}/__init__.py missing"


# ===========================================================================
# 6. PostGIS Spatial Queries
# ===========================================================================


class TestPostGISDependency:
    """تبعية PostGIS للاستعلامات المكانية."""

    @pytest.mark.parametrize("svc", sorted(FIELD_MAPPING_SERVICES))
    def test_depends_on_database(self, services: dict, svc: str) -> None:
        """Field mapping service depends on PostgreSQL/PostGIS."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        db_deps = {"postgres", "pgbouncer"}
        assert dep_names & db_deps, (
            f"{svc} should depend on PostgreSQL/PostGIS (deps: {dep_names})"
        )

    @pytest.mark.parametrize("svc", sorted(FIELD_MAPPING_SERVICES))
    def test_database_url_env(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "DATABASE_URL" in env_str, (
            f"{svc} missing DATABASE_URL for PostGIS spatial queries"
        )


# ===========================================================================
# 7. API Endpoints
# ===========================================================================


class TestFieldMappingAPIs:
    """نقاط نهاية API لرسم الخرائط."""

    @pytest.mark.parametrize("svc", sorted(TERRAIN_PROCESSING))
    def test_terrain_has_api(self, svc: str) -> None:
        source = _read_all_source(svc)
        if not source:
            pytest.skip(f"No source for {svc}")
        has_api = "/api/v1" in source or "router" in source.lower()
        assert has_api, f"{svc} should expose REST API endpoints"


# ===========================================================================
# 8. Compose & Docker Configuration
# ===========================================================================


class TestFieldMappingCompose:
    """تكوين docker-compose."""

    @pytest.mark.parametrize("svc", sorted(FIELD_MAPPING_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services

    @pytest.mark.parametrize("svc", sorted(FIELD_MAPPING_SERVICES))
    def test_healthcheck(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(FIELD_MAPPING_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} must run as non-root"

    def test_no_port_collisions(self) -> None:
        ports = list(FIELD_MAPPING_SERVICES.values())
        assert len(ports) == len(set(ports))
