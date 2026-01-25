# PostGIS Test Suite - Quick Reference Card

# مرجع سريع لمجموعة اختبارات PostGIS

## Installation | التثبيت

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-ops
pip install -r requirements.txt
```

## Run Tests | تشغيل الاختبارات

```bash
# All tests
pytest tests/test_postgis_validation.py -v

# Using test runner script
./tests/run_postgis_tests.sh

# Specific category
pytest tests/test_postgis_validation.py::TestGeometryValidation -v

# With coverage
pytest tests/test_postgis_validation.py --cov=src --cov-report=html
```

## Test Categories | فئات الاختبارات

| Category            | Class Name                     | Tests        |
| ------------------- | ------------------------------ | ------------ |
| Geometry Validation | TestGeometryValidation         | 4            |
| Spatial Operations  | TestSpatialOperations          | 5            |
| Coordinate Systems  | TestCoordinateReferenceSystems | 3            |
| Field Boundaries    | TestFieldBoundaryValidation    | 4            |
| Index Performance   | TestIndexPerformance           | 2            |
| Integration         | TestPostGISIntegration         | 2            |
| Utilities           | TestUtilityFunctions           | 2            |
| Benchmarks          | TestPerformanceBenchmarks      | 1            |
| Error Handling      | TestErrorHandling              | 3            |
| **TOTAL**           | **9 classes**                  | **26 tests** |

## Yemen Coordinates | إحداثيات اليمن

```python
# Bounds
LAT: 12.0 - 19.0°N
LON: 42.0 - 54.0°E

# Cities
Sana'a: 15.3547, 44.2075
Aden:   12.7855, 45.0328
Mukalla: 14.5519, 48.7837
```

## Field Constraints | قيود الحقول

```python
MIN_AREA = 0.1 hectares    # 1,000 m²
MAX_AREA = 1000 hectares   # 10,000,000 m²
```

## Common Commands | الأوامر الشائعة

```bash
# Install dependencies only
pip install pytest shapely pyproj geojson

# Run specific test
pytest tests/test_postgis_validation.py::TestGeometryValidation::test_valid_polygon_geometry -v

# Run async tests
pytest tests/test_postgis_validation.py::TestIndexPerformance -v --asyncio-mode=auto

# Generate HTML coverage report
pytest tests/test_postgis_validation.py --cov=src --cov-report=html
open htmlcov/index.html
```

## PostGIS Functions Tested | دوال PostGIS المختبرة

- ✅ ST_IsValid() - Geometry validation
- ✅ ST_MakeValid() - Geometry repair
- ✅ ST_Contains() - Point in polygon
- ✅ ST_Intersection() - Polygon intersection
- ✅ ST_Buffer() - Buffer/erosion
- ✅ ST_Centroid() - Centroid calculation
- ✅ ST_Area(geography) - Area in hectares
- ✅ ST_Simplify() - Polygon simplification

## Files Created | الملفات المنشأة

```
tests/
├── test_postgis_validation.py        # Main test file (39 KB, 1063 lines)
├── README_POSTGIS_TESTS.md          # Full documentation (14 KB)
├── POSTGIS_TEST_SUITE_SUMMARY.md    # Implementation summary (16 KB)
├── POSTGIS_QUICK_REFERENCE.md       # This file
└── run_postgis_tests.sh             # Test runner script (2.6 KB)

requirements.txt                      # Updated with dependencies
```

## Troubleshooting | استكشاف الأخطاء

```bash
# Missing shapely
pip install shapely==2.0.6

# Missing pyproj
pip install pyproj==3.7.0

# Missing pytest
pip install pytest pytest-asyncio

# GDAL not found (Ubuntu)
sudo apt-get install gdal-bin libgdal-dev
```

## Quick Examples | أمثلة سريعة

### Validate Polygon

```python
from shapely.geometry import Polygon

polygon = Polygon([[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]])
assert polygon.is_valid
```

### Calculate Area

```python
from pyproj import Geod

geod = Geod(ellps="WGS84")
coords = list(polygon.exterior.coords)
lons = [c[0] for c in coords]
lats = [c[1] for c in coords]
area_m2, _ = geod.polygon_area_perimeter(lons, lats)
area_hectares = abs(area_m2) / 10000
```

### Check Point in Polygon

```python
from shapely.geometry import Point, Polygon

point = Point(44.05, 15.05)
polygon = Polygon([[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]])
assert polygon.contains(point)
```

## CI/CD Integration | تكامل CI/CD

```yaml
- name: Run PostGIS Tests
  run: |
    cd apps/services/field-ops
    pip install -r requirements.txt
    pytest tests/test_postgis_validation.py -v --cov=src
```

## Performance Targets | أهداف الأداء

| Operation           | Target    | Status |
| ------------------- | --------- | ------ |
| Geometry validation | >1000/sec | ✅     |
| Point-in-polygon    | <1ms      | ✅     |
| Spatial query       | <100ms    | ✅     |

---

**Quick Help:** See `README_POSTGIS_TESTS.md` for full documentation
**للمساعدة السريعة:** راجع `README_POSTGIS_TESTS.md` للتوثيق الكامل
