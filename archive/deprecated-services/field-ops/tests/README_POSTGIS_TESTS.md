# PostGIS Validation Test Suite for SAHOOL

# مجموعة اختبارات التحقق من PostGIS لنظام سهول

## Overview | نظرة عامة

Comprehensive test suite for validating PostGIS spatial operations in the SAHOOL agricultural platform. This suite ensures that all geospatial operations meet quality, performance, and accuracy requirements.

مجموعة اختبارات شاملة للتحقق من صحة العمليات المكانية لـ PostGIS في منصة سهول الزراعية. تضمن هذه المجموعة أن جميع العمليات الجغرافية المكانية تلبي متطلبات الجودة والأداء والدقة.

## Test Coverage | التغطية الاختبارية

### 1. Geometry Validation | التحقق من صحة الأشكال الهندسية

**File:** `test_postgis_validation.py::TestGeometryValidation`

- ✅ `test_valid_polygon_geometry` - Validates correct polygon structure
- ✅ `test_invalid_self_intersecting_polygon` - Detects self-intersecting polygons
- ✅ `test_polygon_winding_order` - Verifies counterclockwise winding
- ✅ `test_multipolygon_support` - Tests MultiPolygon geometries

**PostGIS Functions Tested:**

- `ST_IsValid()`
- `ST_MakeValid()`
- `ST_IsSimple()`
- Polygon ring validation

### 2. Spatial Operations | العمليات المكانية

**File:** `test_postgis_validation.py::TestSpatialOperations`

- ✅ `test_point_in_polygon` - Point containment checks (ST_Contains)
- ✅ `test_polygon_intersection` - Polygon intersection operations
- ✅ `test_buffer_calculation` - Buffer/erosion operations
- ✅ `test_centroid_calculation` - Centroid calculation accuracy
- ✅ `test_area_calculation_hectares` - Area calculation in hectares

**PostGIS Functions Tested:**

- `ST_Contains()`
- `ST_Intersection()`
- `ST_Buffer()`
- `ST_Centroid()`
- `ST_Area(geography)`

### 3. Coordinate Reference Systems | أنظمة الإحداثيات المرجعية

**File:** `test_postgis_validation.py::TestCoordinateReferenceSystems`

- ✅ `test_srid_4326_wgs84` - WGS84 coordinate validation
- ✅ `test_coordinate_transformation` - CRS transformations (EPSG:4326 ↔ EPSG:32638)
- ✅ `test_yemen_bounds_validation` - Yemen geographic bounds (12.0-19.0°N, 42.0-54.0°E)

**Coordinate Systems:**

- EPSG:4326 (WGS84) - GPS coordinates
- EPSG:32638 (UTM Zone 38N) - Yemen projected coordinates
- Geographic bounds validation

### 4. Field Boundary Validation | التحقق من صحة حدود الحقول

**File:** `test_postgis_validation.py::TestFieldBoundaryValidation`

- ✅ `test_field_minimum_area` - Minimum area constraint (0.1 hectares)
- ✅ `test_field_maximum_area` - Maximum area constraint (1000 hectares)
- ✅ `test_overlapping_fields_detection` - Overlap detection between fields
- ✅ `test_field_simplification` - Polygon simplification (ST_Simplify)

**Business Rules:**

- Minimum field area: 0.1 hectares (1,000 m²)
- Maximum field area: 1,000 hectares (10,000,000 m²)
- Overlap detection and percentage calculation
- Douglas-Peucker simplification

### 5. Index Performance | أداء الفهارس

**File:** `test_postgis_validation.py::TestIndexPerformance`

- ✅ `test_spatial_index_exists` - Verifies GIST indexes exist
- ✅ `test_query_performance_with_index` - Validates index usage and performance

**Indexes Validated:**

- `idx_fields_boundary` - GIST index on field boundaries
- `idx_fields_centroid` - GIST index on field centroids
- `idx_farms_location` - GIST index on farm locations
- `idx_farms_boundary` - GIST index on farm boundaries

### 6. Additional Test Classes | فئات اختبار إضافية

**Integration Tests** (`TestPostGISIntegration`):

- Complete field creation workflow
- GeoJSON conversion and validation

**Utility Functions** (`TestUtilityFunctions`):

- Yemen coordinate validation
- Haversine distance calculation
- Geographic utility functions

**Performance Benchmarks** (`TestPerformanceBenchmarks`):

- Bulk geometry validation (1000+ polygons)
- Throughput measurements

**Error Handling** (`TestErrorHandling`):

- Empty polygon handling
- Invalid coordinate detection
- Insufficient points validation

## Installation | التثبيت

### 1. Install Dependencies | تثبيت التبعيات

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-ops
pip install -r requirements.txt
```

**Required packages:**

- `pytest==8.3.4` - Testing framework
- `pytest-asyncio==0.24.0` - Async test support
- `pytest-cov==4.1.0` - Code coverage
- `shapely==2.0.6` - Geometry operations
- `geojson==3.1.0` - GeoJSON support
- `pyproj==3.7.0` - Coordinate transformations
- `asyncpg==0.30.0` - PostgreSQL async driver

### 2. PostgreSQL + PostGIS Setup | إعداد PostgreSQL + PostGIS

Ensure PostGIS extension is enabled in your database:

```sql
-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify installation
SELECT PostGIS_Version();
```

### 3. Create Spatial Indexes | إنشاء الفهارس المكانية

```sql
-- Fields table indexes
CREATE INDEX IF NOT EXISTS idx_fields_boundary
ON fields USING GIST(boundary);

CREATE INDEX IF NOT EXISTS idx_fields_centroid
ON fields USING GIST(centroid);

-- Farms table indexes
CREATE INDEX IF NOT EXISTS idx_farms_location
ON farms USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_farms_boundary
ON farms USING GIST(boundary);
```

## Running Tests | تشغيل الاختبارات

### Run All PostGIS Tests | تشغيل جميع اختبارات PostGIS

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-ops
pytest tests/test_postgis_validation.py -v
```

### Run Specific Test Class | تشغيل فئة اختبار محددة

```bash
# Geometry validation tests only
pytest tests/test_postgis_validation.py::TestGeometryValidation -v

# Spatial operations tests only
pytest tests/test_postgis_validation.py::TestSpatialOperations -v

# CRS tests only
pytest tests/test_postgis_validation.py::TestCoordinateReferenceSystems -v

# Field boundary validation
pytest tests/test_postgis_validation.py::TestFieldBoundaryValidation -v

# Performance tests
pytest tests/test_postgis_validation.py::TestIndexPerformance -v
```

### Run Single Test | تشغيل اختبار واحد

```bash
pytest tests/test_postgis_validation.py::TestGeometryValidation::test_valid_polygon_geometry -v
```

### Run with Coverage | تشغيل مع تغطية الكود

```bash
pytest tests/test_postgis_validation.py --cov=src --cov-report=html --cov-report=term
```

### Run Async Tests | تشغيل الاختبارات غير المتزامنة

```bash
pytest tests/test_postgis_validation.py -v --asyncio-mode=auto
```

## Test Statistics | إحصائيات الاختبارات

- **Total Test Functions:** 26
- **Test Classes:** 8
- **Lines of Code:** 1,063
- **File Size:** 39 KB
- **Fixtures:** 8

### Test Distribution | توزيع الاختبارات

| Category            | Test Count | Arabic Name                |
| ------------------- | ---------- | -------------------------- |
| Geometry Validation | 4          | التحقق من الأشكال الهندسية |
| Spatial Operations  | 5          | العمليات المكانية          |
| Coordinate Systems  | 3          | أنظمة الإحداثيات           |
| Field Boundaries    | 4          | حدود الحقول                |
| Index Performance   | 2          | أداء الفهارس               |
| Integration         | 2          | التكامل                    |
| Utilities           | 2          | الأدوات المساعدة           |
| Benchmarks          | 1          | قياس الأداء                |
| Error Handling      | 3          | معالجة الأخطاء             |

## Yemen Geographic Reference | المرجع الجغرافي لليمن

### Coordinate Bounds | حدود الإحداثيات

```python
YEMEN_MIN_LAT = 12.0  # Southern boundary
YEMEN_MAX_LAT = 19.0  # Northern boundary
YEMEN_MIN_LON = 42.0  # Western boundary
YEMEN_MAX_LON = 54.0  # Eastern boundary
```

### Major Cities Coordinates | إحداثيات المدن الرئيسية

| City    | Arabic | Latitude | Longitude |
| ------- | ------ | -------- | --------- |
| Sana'a  | صنعاء  | 15.3547  | 44.2075   |
| Aden    | عدن    | 12.7855  | 45.0328   |
| Mukalla | المكلا | 14.5519  | 48.7837   |
| Sa'dah  | صعدة   | 15.6949  | 43.7461   |

### UTM Zones for Yemen | مناطق UTM لليمن

- **UTM Zone 38N** (EPSG:32638) - Western Yemen
- **UTM Zone 39N** (EPSG:32639) - Eastern Yemen

## Field Size Constraints | قيود حجم الحقل

### Minimum Area | الحد الأدنى للمساحة

- **0.1 hectares** (1,000 m²)
- Equivalent to 0.001 km²
- Approximately 100m × 100m plot

### Maximum Area | الحد الأقصى للمساحة

- **1,000 hectares** (10,000,000 m²)
- Equivalent to 10 km²
- Approximately 3.16 km × 3.16 km

### Typical Field Sizes | أحجام الحقول النموذجية

| Field Type  | Size (hectares) | Arabic       |
| ----------- | --------------- | ------------ |
| Small farm  | 0.5 - 5         | مزرعة صغيرة  |
| Medium farm | 5 - 50          | مزرعة متوسطة |
| Large farm  | 50 - 500        | مزرعة كبيرة  |
| Estate      | 500 - 1000      | عقار كبير    |

## Performance Benchmarks | معايير الأداء

### Expected Performance | الأداء المتوقع

| Operation        | Target    | Description                         |
| ---------------- | --------- | ----------------------------------- |
| Validation       | >1000/sec | Geometry validation throughput      |
| Point-in-polygon | <1ms      | Single point containment check      |
| Intersection     | <5ms      | Polygon intersection operation      |
| Buffer           | <10ms     | Buffer generation                   |
| Spatial query    | <100ms    | Indexed spatial query (10K records) |

### Index Performance | أداء الفهارس

With GIST indexes:

- Radius query (10km): **<10ms** for 10,000 fields
- Bounding box query: **<5ms** for 10,000 fields
- Distance calculation: **<1ms** between two fields

## Fixtures | التركيبات الاختبارية

### Database Fixtures | تركيبات قاعدة البيانات

```python
@pytest.fixture
async def mock_db_pool():
    """Mock database connection pool for PostGIS operations"""
    # Returns mocked pool and connection
```

### Geometry Fixtures | تركيبات الأشكال الهندسية

```python
@pytest.fixture
def valid_polygon_coords():
    """Valid polygon coordinates for Yemen region"""

@pytest.fixture
def self_intersecting_polygon_coords():
    """Self-intersecting polygon (invalid geometry)"""

@pytest.fixture
def yemen_test_polygon():
    """Test polygon within Yemen boundaries"""

@pytest.fixture
def multipolygon_geometry():
    """MultiPolygon geometry for testing"""
```

## Common Test Patterns | أنماط الاختبار الشائعة

### 1. Geometry Validation Pattern

```python
def test_geometry_validation():
    polygon = Polygon(coordinates)
    assert polygon.is_valid, f"Invalid: {explain_validity(polygon)}"
    assert polygon.is_simple, "Polygon should be simple"
    assert not polygon.is_empty, "Polygon should not be empty"
```

### 2. Area Calculation Pattern

```python
def test_area_calculation():
    from pyproj import Geod
    geod = Geod(ellps="WGS84")

    coords = list(polygon.exterior.coords)
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    area_m2, _ = geod.polygon_area_perimeter(lons, lats)
    area_hectares = abs(area_m2) / 10000

    assert MIN_AREA <= area_hectares <= MAX_AREA
```

### 3. Database Query Pattern

```python
@pytest.mark.asyncio
async def test_spatial_query(mock_db_pool):
    pool, connection = mock_db_pool

    # Mock response
    connection.fetch = AsyncMock(return_value=[...])

    # Execute query
    async with pool.acquire() as conn:
        results = await conn.fetch(query, *params)

    # Validate results
    assert len(results) > 0
```

## Troubleshooting | استكشاف الأخطاء وإصلاحها

### Common Issues | المشاكل الشائعة

**Issue:** `ModuleNotFoundError: No module named 'shapely'`
**Solution:**

```bash
pip install shapely==2.0.6
```

**Issue:** `ModuleNotFoundError: No module named 'pyproj'`
**Solution:**

```bash
pip install pyproj==3.7.0
```

**Issue:** `pytest: command not found`
**Solution:**

```bash
pip install pytest pytest-asyncio
```

**Issue:** Tests fail with async warnings
**Solution:**

```bash
pytest --asyncio-mode=auto
```

**Issue:** PostGIS functions not available
**Solution:**

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

## Integration with CI/CD | التكامل مع CI/CD

### GitHub Actions Example

```yaml
- name: Run PostGIS Tests
  run: |
    cd apps/services/field-ops
    pytest tests/test_postgis_validation.py -v --cov=src
```

### Docker Test Environment

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev \
    libproj-dev proj-data proj-bin \
    libgeos-dev
COPY requirements.txt .
RUN pip install -r requirements.txt
```

## References | المراجع

### Documentation

- [PostGIS Documentation](https://postgis.net/docs/)
- [Shapely Documentation](https://shapely.readthedocs.io/)
- [PyProj Documentation](https://pyproj4.github.io/pyproj/)
- [GeoJSON Specification](https://geojson.org/)

### SAHOOL Documentation

- [Field Core Geospatial Setup](/apps/services/field-core/GEOSPATIAL_SETUP_SUMMARY.md)
- [PostGIS Optimization](/docs/infrastructure/POSTGIS_OPTIMIZATION.md)
- [GIS Architecture](/docs/GIS_ARCHITECTURE.md)

### Related Files

- `/packages/field_suite/spatial/validation.py` - Geometry validation utilities
- `/apps/services/field-service/src/geo.py` - Geospatial service layer
- `/packages/field-shared/src/geo/geo-service.ts` - TypeScript geo service

## Contributing | المساهمة

### Adding New Tests

1. Follow the existing test class structure
2. Include Arabic descriptions in docstrings
3. Use appropriate fixtures
4. Add test to relevant test class
5. Update this README

### Test Naming Convention

```python
def test_{operation}_{condition}():
    """
    Test description in English
    الوصف بالعربية
    """
```

## License

Copyright © 2025 SAHOOL Agricultural Platform
All rights reserved.

---

**Created:** 2026-01-02
**Version:** 1.0.0
**Maintainer:** SAHOOL Development Team
**File:** `test_postgis_validation.py`
**Lines:** 1,063
**Tests:** 26
