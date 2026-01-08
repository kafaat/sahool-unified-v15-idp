"""
Geo/NDVI Rules - SAHOOL-specific geospatial and vegetation index checks
"""

import re
from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all geo/NDVI-related checks"""
    findings = []

    findings.extend(check_postgis_usage(repo_root))
    findings.extend(check_srid_configuration(repo_root))
    findings.extend(check_ndvi_async_processing(repo_root))
    findings.extend(check_tenant_field_isolation(repo_root))
    findings.extend(check_sentinel_integration(repo_root))

    return findings


def check_postgis_usage(repo_root: Path) -> list:
    """Check PostGIS is properly enabled and used"""
    findings = []

    # Check SQL migrations for PostGIS
    sql_files = list(repo_root.rglob("*.sql"))
    has_postgis = False

    for sql_file in sql_files:
        try:
            content = sql_file.read_text().lower()
            if "postgis" in content or "create extension" in content:
                has_postgis = True
                break
        except Exception:
            continue

    if not has_postgis and sql_files:
        findings.append(
            {
                "severity": "CRITICAL",
                "component": "Geo-Core",
                "issue": "PostGIS extension not detected in migrations",
                "impact": "Geospatial queries (field boundaries, NDVI) will fail",
                "fix": "Add 'CREATE EXTENSION IF NOT EXISTS postgis;' to migrations",
                "file": "database/migrations/",
            }
        )

    # Check Python code uses geometry types
    geo_patterns = ["geometry", "ST_", "Point", "Polygon", "geoalchemy"]
    has_geo_code = False

    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue
        try:
            content = py_file.read_text()
            if any(pattern in content for pattern in geo_patterns):
                has_geo_code = True
                break
        except Exception:
            continue

    if not has_geo_code:
        findings.append(
            {
                "severity": "HIGH",
                "component": "Geo-Core",
                "issue": "No geospatial code patterns detected",
                "impact": "Field boundaries and spatial queries may not work",
                "fix": "Implement geospatial models using PostGIS/GeoAlchemy2",
                "file": "packages/field_suite/spatial/",
            }
        )

    return findings


def check_srid_configuration(repo_root: Path) -> list:
    """Check SRID (Spatial Reference ID) is properly configured"""
    findings = []

    # Common SRIDs: 4326 (WGS84), 3857 (Web Mercator)
    srid_pattern = r"SRID[=:\s]+(\d+)"

    found_srids = set()

    for py_file in repo_root.rglob("*.py"):
        try:
            content = py_file.read_text()
            matches = re.findall(srid_pattern, content, re.IGNORECASE)
            found_srids.update(matches)
        except Exception:
            continue

    for sql_file in repo_root.rglob("*.sql"):
        try:
            content = sql_file.read_text()
            matches = re.findall(srid_pattern, content, re.IGNORECASE)
            found_srids.update(matches)
        except Exception:
            continue

    # Check for SRID inconsistency
    if len(found_srids) > 2:  # Allow 4326 and 3857
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "Geo-Core",
                "issue": f"Multiple SRIDs detected: {found_srids}",
                "impact": "Coordinate system mismatches may cause incorrect calculations",
                "fix": "Standardize on SRID 4326 (WGS84) for storage, transform as needed",
                "file": "Global",
            }
        )

    return findings


def check_ndvi_async_processing(repo_root: Path) -> list:
    """Check NDVI calculations are done asynchronously"""
    findings = []

    ndvi_files = []
    for pattern in ["*ndvi*", "*vegetation*", "*satellite*"]:
        ndvi_files.extend(repo_root.rglob(f"**/{pattern}.py"))

    for ndvi_file in ndvi_files:
        if "test" in str(ndvi_file).lower():
            continue

        try:
            content = ndvi_file.read_text()
        except Exception:
            continue

        # Check for async patterns
        has_async = "async def" in content or "asyncio" in content
        has_background = (
            "BackgroundTasks" in content
            or "celery" in content.lower()
            or "nats" in content.lower()
            or "queue" in content.lower()
        )

        # Check for heavy computation in sync context
        has_heavy_sync = (
            "def calculate_ndvi" in content
            or "def compute_ndvi" in content
            or "def process_ndvi" in content
        ) and "async def" not in content

        if has_heavy_sync and not has_background:
            findings.append(
                {
                    "severity": "HIGH",
                    "component": "NDVI-Engine",
                    "issue": f"Synchronous NDVI processing in {ndvi_file.name}",
                    "impact": "API will timeout during heavy NDVI calculations",
                    "fix": "Move NDVI processing to background worker with async/queue",
                    "file": str(ndvi_file.relative_to(repo_root)),
                }
            )

    return findings


def check_tenant_field_isolation(repo_root: Path) -> list:
    """Check tenant isolation for field/geo data"""
    findings = []

    # Check models have tenant_id
    model_files = list(repo_root.rglob("**/models*.py")) + list(
        repo_root.rglob("**/models/*.py")
    )

    for model_file in model_files:
        if "test" in str(model_file).lower():
            continue

        try:
            content = model_file.read_text()
        except Exception:
            continue

        # Check if it's a field/geo model
        is_geo_model = any(
            pattern in content.lower()
            for pattern in ["field", "polygon", "geometry", "ndvi", "zone"]
        )

        if is_geo_model:
            has_tenant = "tenant_id" in content or "tenant" in content.lower()
            if not has_tenant:
                findings.append(
                    {
                        "severity": "CRITICAL",
                        "component": "Security",
                        "issue": f"Missing tenant isolation in {model_file.name}",
                        "impact": "Data leakage between tenants possible",
                        "fix": "Add tenant_id field and enforce in all queries",
                        "file": str(model_file.relative_to(repo_root)),
                    }
                )

    return findings


def check_sentinel_integration(repo_root: Path) -> list:
    """Check Sentinel Hub / satellite data integration"""
    findings = []

    # Look for satellite data integration
    satellite_patterns = ["sentinel", "copernicus", "landsat", "satellite"]

    has_satellite = False
    for py_file in repo_root.rglob("*.py"):
        try:
            content = py_file.read_text().lower()
            if any(pattern in content for pattern in satellite_patterns):
                has_satellite = True
                break
        except Exception:
            continue

    if not has_satellite:
        findings.append(
            {
                "severity": "MEDIUM",
                "component": "NDVI-Engine",
                "issue": "No satellite data integration detected",
                "impact": "NDVI calculations may rely on mock/sample data only",
                "fix": "Integrate with Sentinel Hub or Copernicus for real satellite imagery",
                "file": "packages/sahool-eo/",
            }
        )

    return findings
