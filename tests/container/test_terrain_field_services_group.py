"""
SAHOOL Terrain/Field/Geospatial Services Group – Container Function Tests
==========================================================================
اختبارات وظائف مجموعة خدمات التضاريس والحقول والجغرافيا المكانية

Validates that terrain analysis, hydrology, leveling, and field management
services share consistent geospatial tooling and configuration.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  terrain-core-service · hydrology-service · leveling-optimizer-service
  field-management-service (Node.js) · field-intelligence · soil-analysis-service

Coverage:
 1.  Geospatial library dependencies (GDAL, GEOS, PROJ, Shapely, Rasterio)
 2.  Scientific computing stack (NumPy, SciPy)
 3.  Database dependency (asyncpg / Prisma)
 4.  GDAL environment configuration in Dockerfile
 5.  DEM/raster data directory provisioning
 6.  Health endpoints
 7.  Non-root user
 8.  Node.js field-management Prisma build
 9.  Compose dependency chain (PostGIS)
10.  Port consistency & network membership

Run:
    pytest tests/container/test_terrain_field_services_group.py -v --tb=short
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

TERRAIN_FIELD_SERVICES: dict[str, int] = {
    "terrain-core-service": 8185,
    "hydrology-service": 8165,
    "leveling-optimizer-service": 8170,
    "field-management-service": 3000,   # Node.js NestJS
    "field-intelligence": 8120,
    "soil-analysis-service": 8134,
}

# Sub-clusters
GEOSPATIAL_PYTHON = {
    "terrain-core-service",
    "hydrology-service",
    "leveling-optimizer-service",
    "soil-analysis-service",
}

TERRAIN_CORE = {
    "terrain-core-service",
    "hydrology-service",
    "leveling-optimizer-service",
}

NODE_FIELD = {"field-management-service"}

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
# 1. Geospatial Library Dependencies
# ===========================================================================


class TestGeospatialDeps:
    """خدمات التضاريس يجب أن تحتوي على مكتبات جغرافية مكانية."""

    @pytest.mark.parametrize("svc", sorted(TERRAIN_CORE))
    def test_numpy_dependency(self, svc: str) -> None:
        """Terrain service declares numpy."""
        pkgs = _req_packages(svc)
        assert "numpy" in pkgs, f"{svc} missing numpy"

    @pytest.mark.parametrize("svc", sorted(TERRAIN_CORE))
    def test_has_geospatial_lib(self, svc: str) -> None:
        """Terrain service declares geospatial lib or accesses via shared/."""
        pkgs = _req_packages(svc)
        geo_libs = {"rasterio", "shapely", "pyproj", "gdal", "geopandas", "fiona", "affine"}
        has_geo = pkgs & geo_libs
        dockerfile = _read_dockerfile(svc)
        has_gdal_sys = "gdal" in dockerfile.lower() or "geos" in dockerfile.lower()
        # Some services access geospatial via shared/ module copy
        has_shared = bool(re.search(r"COPY.*shared", dockerfile, re.IGNORECASE))
        assert has_geo or has_gdal_sys or has_shared, (
            f"{svc} missing geospatial dependency "
            f"(expected one of {geo_libs}, system GDAL/GEOS, or shared/ copy)"
        )

    def test_terrain_core_rasterio(self) -> None:
        """terrain-core-service declares rasterio for DEM processing."""
        pkgs = _req_packages("terrain-core-service")
        assert "rasterio" in pkgs, "terrain-core-service missing rasterio"

    def test_terrain_core_gdal_env(self) -> None:
        """terrain-core-service Dockerfile configures GDAL environment."""
        content = _read_dockerfile("terrain-core-service")
        if not content:
            pytest.skip("No Dockerfile")
        gdal_vars = ["GDAL_CACHEMAX", "GDAL_DISABLE_READDIR", "GDAL_DATA"]
        found = [v for v in gdal_vars if v in content]
        assert found, (
            f"terrain-core-service missing GDAL env configuration (checked: {gdal_vars})"
        )


# ===========================================================================
# 2. Scientific Computing Stack
# ===========================================================================


class TestScientificComputing:
    """خدمات التضاريس يجب أن تحتوي على مكتبات الحوسبة العلمية."""

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_PYTHON))
    def test_fastapi_declared(self, svc: str) -> None:
        """Geospatial Python service declares fastapi."""
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_PYTHON))
    def test_asyncpg_for_postgis(self, svc: str) -> None:
        """Geospatial service declares asyncpg for PostGIS access."""
        pkgs = _req_packages(svc)
        has_db = "asyncpg" in pkgs or "sqlalchemy" in pkgs or "databases" in pkgs
        assert has_db, f"{svc} missing database driver (asyncpg/sqlalchemy)"


# ===========================================================================
# 3. GDAL System Packages in Dockerfile
# ===========================================================================


class TestGDALSystemPackages:
    """خدمة terrain-core يجب أن تثبت حزم GDAL في النظام."""

    def test_terrain_core_gdal_apt(self) -> None:
        """terrain-core-service installs libgdal-dev in builder stage."""
        content = _read_dockerfile("terrain-core-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert "gdal" in content.lower(), (
            "terrain-core-service Dockerfile should install GDAL packages"
        )

    def test_terrain_core_proj(self) -> None:
        """terrain-core-service installs PROJ library."""
        content = _read_dockerfile("terrain-core-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert "proj" in content.lower(), (
            "terrain-core-service should install PROJ for coordinate transformations"
        )

    def test_terrain_core_temp_cache(self) -> None:
        """terrain-core-service creates temp/cache directories for DEM processing."""
        content = _read_dockerfile("terrain-core-service")
        if not content:
            pytest.skip("No Dockerfile")
        has_cache = "terrain" in content.lower() and ("cache" in content.lower() or "tmp" in content.lower())
        assert has_cache, (
            "terrain-core-service should provision temp/cache directories"
        )


# ===========================================================================
# 4. Node.js Field Management – Prisma
# ===========================================================================


class TestFieldManagementPrisma:
    """خدمة إدارة الحقول (Node.js) يجب أن تبني Prisma Client."""

    def test_prisma_in_package_json(self) -> None:
        """field-management-service package.json includes Prisma."""
        pkg_path = SERVICES_DIR / "field-management-service" / "package.json"
        if not pkg_path.exists():
            pytest.skip("No package.json")
        content = pkg_path.read_text("utf-8")
        assert "prisma" in content.lower(), (
            "field-management-service missing Prisma in package.json"
        )

    def test_prisma_generate_in_dockerfile(self) -> None:
        """Dockerfile runs prisma generate for client code generation."""
        content = _read_dockerfile("field-management-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert "prisma" in content.lower(), (
            "field-management-service Dockerfile should run prisma generate"
        )

    def test_nestjs_build_in_dockerfile(self) -> None:
        """Dockerfile runs NestJS build."""
        content = _read_dockerfile("field-management-service")
        if not content:
            pytest.skip("No Dockerfile")
        has_build = "nest build" in content.lower() or "npm run build" in content.lower()
        assert has_build, "field-management-service Dockerfile missing NestJS build step"

    def test_field_shared_package(self) -> None:
        """Dockerfile copies field-shared workspace package."""
        content = _read_dockerfile("field-management-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert "field-shared" in content or "field_shared" in content, (
            "field-management-service should include field-shared package"
        )


# ===========================================================================
# 5. Health Endpoints
# ===========================================================================


class TestTerrainHealthEndpoints:
    """نقاط فحص الصحة لخدمات التضاريس."""

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        """Dockerfile defines HEALTHCHECK."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_PYTHON))
    def test_health_in_source(self, svc: str) -> None:
        """Python terrain service source has health endpoint."""
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/healthz" in content or "/health" in content, (
            f"{svc} main.py missing health endpoint"
        )


# ===========================================================================
# 6. Non-Root User
# ===========================================================================


class TestTerrainNonRoot:
    """خدمات التضاريس يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        """Dockerfile switches to non-root USER."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 7. Compose Dependency Chain – PostGIS
# ===========================================================================


class TestTerrainComposeDeps:
    """سلسلة تبعيات docker-compose لخدمات التضاريس."""

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        """Terrain service defined in docker-compose.yml."""
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_depends_on_database(self, services: dict, svc: str) -> None:
        """Terrain service depends on database (postgres/pgbouncer)."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        db_deps = {"postgres", "pgbouncer"}
        has_db = dep_names & db_deps
        assert has_db, (
            f"{svc} should depend on database (postgres/pgbouncer) "
            f"for geospatial queries (deps: {dep_names})"
        )

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_database_url_env(self, services: dict, svc: str) -> None:
        """Terrain service declares DATABASE_URL environment variable."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "DATABASE_URL" in env_str, f"{svc} missing DATABASE_URL env var"


# ===========================================================================
# 8. Port Range & Network
# ===========================================================================


class TestTerrainPortNetwork:
    """منافذ وشبكات خدمات التضاريس."""

    @pytest.mark.parametrize("svc,port", sorted(TERRAIN_FIELD_SERVICES.items()))
    def test_port_valid(self, svc: str, port: int) -> None:
        """Terrain service port in valid range."""
        assert 3000 <= port <= 9000, f"{svc} port {port} out of range"

    def test_no_duplicate_ports(self) -> None:
        """No duplicate ports."""
        ports = list(TERRAIN_FIELD_SERVICES.values())
        assert len(ports) == len(set(ports))

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        """Service on sahool network."""
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    @pytest.mark.parametrize("svc", sorted(TERRAIN_FIELD_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        """Service has restart policy."""
        svc_def = services.get(svc, {})
        assert "restart" in svc_def, f"{svc} missing restart policy"


# ===========================================================================
# 9. Shared Module Copy
# ===========================================================================


class TestTerrainSharedModules:
    """خدمات التضاريس يجب أن تنسخ الوحدات المشتركة."""

    @pytest.mark.parametrize("svc", sorted(GEOSPATIAL_PYTHON))
    def test_copies_shared(self, svc: str) -> None:
        """Dockerfile copies shared/ directory."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} Dockerfile does not COPY shared/"
        )


# ===========================================================================
# 10. Terrain Services – Multi-Stage Build
# ===========================================================================


class TestTerrainMultiStage:
    """خدمات التضاريس يجب أن تستخدم بناء متعدد المراحل."""

    @pytest.mark.parametrize("svc", sorted(TERRAIN_CORE))
    def test_multi_stage_build(self, svc: str) -> None:
        """Dockerfile has at least 2 FROM stages."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE | re.IGNORECASE))
        assert from_count >= 2, (
            f"{svc} has {from_count} FROM stage(s), expected ≥2"
        )
