# shared/field_boundaries

Geospatial field boundary management for the SAHOOL platform. Provides Pydantic
data models, pure-Python geodesic geometry calculations, GPS-track-to-polygon
conversion, boundary sharing workflows, and conflict detection — all with
bilingual (Arabic/English) support and PostGIS integration helpers.

## File Structure

```
shared/field_boundaries/
├── __init__.py    # Module entry point; exports all public symbols
├── models.py      # Pydantic data models (FieldBoundary, BoundaryConflict, etc.)
├── geometry.py    # Geodesic math: area, perimeter, centroid, overlap, simplification
├── mapping.py     # GPS track recording and conversion to boundary polygons
└── sharing.py     # Boundary sharing requests, permissions, conflict detection
```

## Key Components

### models.py

Complete GeoJSON-compatible Pydantic model hierarchy:

| Model | Purpose |
|-------|---------|
| `Point` | GeoJSON Point with coordinate range validation |
| `Polygon` | GeoJSON Polygon with ring closure and minimum-point enforcement |
| `MultiPolygon` | GeoJSON MultiPolygon |
| `BoundaryPoint` | GPS point with `accuracy_m`, `accuracy_level`, `altitude_m`, and `device_id` |
| `FieldBoundary` | Full boundary record: type, status, versioning, sharing list, timestamps |
| `BoundaryConflict` | Detected conflict between two boundaries with `overlap_area_sqm` / `gap_distance_m` |
| `BoundaryShareRequest` | Share request with permission level and expiry |
| `GPSTrack` | Ordered collection of `BoundaryPoint` records with `close_track()` helper |

Enums: `BoundaryStatus` (draft / pending_approval / approved / disputed / archived),
`BoundaryType` (field / plot / farm / irrigation_zone / exclusion_zone),
`CoordinateAccuracy` (high < 1 m / medium 1-5 m / low > 5 m / unknown),
`ConflictType` (overlap / gap / encroachment / disputed_line).

`FieldBoundary.to_geojson_feature()` serializes to a standard GeoJSON Feature dict.
`FieldBoundary.to_postgis_insert()` generates a parameterized SQL INSERT using `ST_SetSRID`.

### geometry.py

Pure-Python geodesic calculations (no external GIS library required):

| Function | Description |
|----------|-------------|
| `haversine_distance(lon1, lat1, lon2, lat2)` | Great-circle distance in metres |
| `calculate_polygon_area(coordinates)` | Shoelace formula, returns m² |
| `calculate_perimeter(coordinates)` | Sum of haversine segment distances |
| `calculate_centroid(coordinates)` | Geometric centroid of exterior ring |
| `calculate_geometry_metrics(coordinates)` | Returns `GeometryMetrics` with m², ha, dunams, acres, perimeter, centroid, bounding box |
| `simplify_polygon(coordinates, tolerance_m)` | Douglas-Peucker simplification |
| `polygons_overlap(coords_a, coords_b)` | Boolean overlap check using bounding-box pre-filter |
| `calculate_overlap_area(coords_a, coords_b)` | Approximate overlap area in m² |

`GeometryMetrics` dataclass: `area_sqm`, `area_hectares`, `area_dunams`, `area_acres`,
`perimeter_m`, `centroid_lon`, `centroid_lat`, `bounding_box`, `is_valid`, `validation_errors`.

Conversion constants: `HECTARES_PER_SQM = 0.0001`, `DUNAMS_PER_SQM = 0.001`, `ACRES_PER_SQM = 0.000247105`.

### mapping.py

Converts real-world GPS walks into clean boundary polygons:

- **`MappingMode`** enum: `WALKING`, `DRIVING`, `POINT_CAPTURE`, `AUTO_TRACE`
- **`FilterMethod`** enum: statistical outlier removal methods
- **`GPSTrackProcessor`**: filters noisy GPS points (accuracy threshold, speed-based outlier removal), smooths with moving average, closes the ring, and calls `calculate_geometry_metrics` on the result
- Returns a ready-to-store `FieldBoundary` with `boundary_points` populated from the raw track

### sharing.py

Manages the full lifecycle of boundary sharing and neighbor approval:

- **`PermissionLevel`** enum: `VIEW`, `COMMENT`, `EDIT`, `APPROVE`, `ADMIN`
- **`ShareStatus`** enum: `PENDING`, `ACCEPTED`, `REJECTED`
- **`BoundarySharingService`**: creates share requests, validates expiry, checks permissions, generates `BoundaryConflict` records using `polygons_overlap` and `calculate_overlap_area`
- Conflict descriptions are bilingual (`get_description(language="en"|"ar")`)

## Usage Example

```python
from shared.field_boundaries.models import (
    FieldBoundary, BoundaryType, BoundaryStatus, Polygon, BoundaryPoint
)
from shared.field_boundaries.geometry import calculate_geometry_metrics
from shared.field_boundaries.mapping import MappingMode
from shared.field_boundaries.sharing import PermissionLevel

# Define a field boundary polygon
polygon = Polygon(coordinates=[[
    (46.70, 24.70), (46.80, 24.70),
    (46.80, 24.80), (46.70, 24.80),
    (46.70, 24.70),   # closed ring
]])

# Calculate area and perimeter
metrics = calculate_geometry_metrics(polygon.coordinates[0])
print(f"Area: {metrics.area_hectares:.2f} ha")       # e.g. 118.55 ha
print(f"Perimeter: {metrics.perimeter_m:.0f} m")     # e.g. 43928 m
print(f"Centroid: {metrics.centroid_lon:.4f}, {metrics.centroid_lat:.4f}")

# Create a FieldBoundary record
boundary = FieldBoundary(
    field_id="FIELD-003",
    tenant_id="tenant-uuid",
    owner_id="farmer-uuid",
    name="North Wheat Field",
    name_ar="حقل القمح الشمالي",
    boundary_type=BoundaryType.FIELD,
    status=BoundaryStatus.APPROVED,
    geometry=polygon,
    area_hectares=metrics.area_hectares,
    perimeter_meters=metrics.perimeter_m,
)

# Export to GeoJSON
feature = boundary.to_geojson_feature()

# Export PostGIS INSERT (use with parameterized queries in production)
sql = boundary.to_postgis_insert(table_name="field_boundaries")

# Check conflict between two boundaries
from shared.field_boundaries.geometry import polygons_overlap, calculate_overlap_area

coords_a = polygon.coordinates[0]
coords_b = [...]  # neighbour's boundary ring
if polygons_overlap(coords_a, coords_b):
    overlap_sqm = calculate_overlap_area(coords_a, coords_b)
    print(f"Overlap: {overlap_sqm:.1f} m²")
```

## PostGIS Schema (Reference)

The generated SQL targets this table structure:

```sql
CREATE TABLE field_boundaries (
    id            UUID PRIMARY KEY,
    field_id      TEXT NOT NULL,
    tenant_id     UUID NOT NULL,
    owner_id      UUID NOT NULL,
    name          TEXT,
    name_ar       TEXT,
    boundary_type TEXT,
    status        TEXT,
    geometry      GEOMETRY(GEOMETRY, 4326) NOT NULL,
    area_hectares FLOAT,
    perimeter_meters FLOAT,
    version       INT DEFAULT 1,
    created_at    TIMESTAMPTZ,
    updated_at    TIMESTAMPTZ
);
CREATE INDEX idx_field_boundaries_geometry ON field_boundaries USING GIST (geometry);
```
