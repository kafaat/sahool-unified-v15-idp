# shared/terrain

Shared utilities for terrain analysis services in the SAHOOL platform.
Consumed by `terrain-core-service`, `hydrology-service`, and `leveling-optimizer-service`.
All components support bilingual (Arabic/English) error messages.

## File Structure

```
shared/terrain/
├── __init__.py         # Module exports
├── validators.py       # GeoJSON, coordinate, elevation, and grade validation
├── geojson_utils.py    # GeoJSON parsing, creation, and manipulation helpers
├── cache.py            # LRU in-memory cache with optional Redis backend
├── responses.py        # Standardised API response formatting
└── batch.py            # Async batch processing with concurrency control
```

## Key Components

### validators.py

Validates terrain-specific inputs against regional and physical constraints.

| Validator | Purpose |
|-----------|---------|
| `validate_geojson_polygon` | GeoJSON Polygon structure, ring closure, coordinate bounds |
| `validate_geojson_point` | GeoJSON Point with coordinate range check |
| `validate_geojson_linestring` | GeoJSON LineString with minimum point count |
| `validate_elevation` | Elevation in metres within [-415, 3500] m range |
| `validate_elevation_point` | Combined (x, y, z) point validation |
| `validate_grade_percentage` | Slope grade within [-15%, 15%] (recommended: 0.05–2%) |
| `validate_slope_degrees` | Slope in degrees within [0, 90] |
| `validate_field_id` | SAHOOL field ID formats (FIELD-*, UUID, alphanumeric) |
| `validate_resolution` | DEM/raster resolution in metres [0.1, 1000] |
| `validate_batch_size` | Batch size within [1, 1000] |

Regional bounds constants: `SAUDI_ARABIA_BOUNDS`, `MENA_BOUNDS`, `GLOBAL_BOUNDS`.

Pydantic base models: `TerrainValidatedModel`, `CoordinateModel`, `ElevationPointModel`, `GradeModel`, `BoundingBoxModel`.

### cache.py

Two-level caching: Redis (primary) with in-memory LRU fallback.

| Class / Function | Purpose |
|-----------------|---------|
| `LRUCache` | Thread-safe ordered-dict LRU with TTL and hit/miss stats |
| `RedisCache` | Async Redis wrapper, JSON serialisation, auto-reconnect |
| `TerrainCache` | Unified cache; writes to both layers, reads Redis first |
| `generate_cache_key` | Deterministic key: `{field_id}:{operation}:{params_hash}` |
| `cache_result` | Async decorator to transparently cache function results |
| `cache_result_sync` | Synchronous version of the decorator |
| `get_terrain_cache` | Singleton accessor |

Default TTL: 3600 s. Default max in-memory items: 1000.

### batch.py

Concurrent async batch processing with priority ordering and partial-failure tracking.

| Class / Function | Purpose |
|-----------------|---------|
| `BatchProcessor` | Semaphore-controlled concurrent processor |
| `BatchRequest` | Single item with ID, priority, and metadata |
| `BatchResult` | Aggregated result with success/error counts and timing |
| `process_batch` | Convenience wrapper for homogeneous item lists |
| `process_batch_with_priority` | Accepts `(item, priority)` tuples |
| `format_batch_result` | Serialises result to API-ready dict |

Limits: `DEFAULT_MAX_CONCURRENT = 5`, `MAX_BATCH_SIZE = 1000`, `DEFAULT_TIMEOUT_SECONDS = 300`.

### geojson_utils.py

GeoJSON lifecycle utilities: parse, create, calculate, and convert.

| Function | Description |
|----------|-------------|
| `parse_geojson_geometry` | Parses raw dict into `GeoJSONGeometry` with `area_sqm`, `perimeter_m`, `centroid` |
| `create_point / create_linestring / create_polygon` | Type-safe GeoJSON constructors |
| `create_feature_collection` | Wraps features into a `FeatureCollection` |
| `haversine_distance` | Great-circle distance in metres between two coordinates |
| `calculate_polygon_area_geodesic` | Shoelace formula on WGS84 ellipsoid |
| `calculate_polygon_centroid` | Arithmetic centroid of exterior ring |
| `simplify_coordinates` | Douglas-Peucker simplification with tolerance in metres |
| `geometry_to_wkt / wkt_to_geometry` | WKT round-trip conversion |

### responses.py

Standardised FastAPI response helpers with bilingual message support and processing metadata.

| Function | Description |
|----------|-------------|
| `success_response(data, message)` | Wraps payload in `{status, data, request_id, processing_time_ms}` |
| `error_response(code, message)` | Returns `{status, error_code, message, message_ar}` |
| `paginated_response(items, total, page, size)` | Adds `pagination` block to response |
| `TerrainResponse` | Pydantic model for typed response validation |

## Usage Example

```python
from shared.terrain.validators import validate_geojson_polygon, SAUDI_ARABIA_BOUNDS
from shared.terrain.geojson_utils import parse_geojson_geometry
from shared.terrain.cache import TerrainCache, generate_cache_key, cache_result
from shared.terrain.batch import process_batch, format_batch_result

# Validate incoming polygon against Saudi Arabia bounds
polygon = {
    "type": "Polygon",
    "coordinates": [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]]
}
validate_geojson_polygon(polygon, bounds=SAUDI_ARABIA_BOUNDS)

# Parse geometry and get computed metrics
geom = parse_geojson_geometry(polygon)
print(f"Area: {geom.area_sqm:.0f} m²")
print(f"Centroid: {geom.centroid}")

# Cache terrain results using the decorator
cache = TerrainCache(namespace="terrain")

@cache_result(cache, operation="slope", ttl=3600, key_params=["field_id"])
async def calculate_slope(field_id: str, resolution: float) -> dict:
    # ... heavy computation (DEM processing, etc.) ...
    return {"slope_degrees": 1.2}

result = await calculate_slope(field_id="FIELD-001", resolution=10.0)

# Invalidate all cached entries for a specific field
await cache.invalidate_field("FIELD-001")

# Batch process multiple fields
async def analyse_field(field_id: str) -> dict:
    return {"field_id": field_id, "status": "ok"}

batch_result = await process_batch(
    items=["FIELD-001", "FIELD-002", "FIELD-003"],
    handler=analyse_field,
    max_concurrent=5,
)
print(f"Success: {batch_result.success_count}, Errors: {batch_result.error_count}")

# Format for API response
response = format_batch_result(batch_result, include_all_results=True)
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `REDIS_URL` | `""` | Redis connection URL for cache backend |
| `TERRAIN_CACHE_ENABLED` | `"true"` | Enable or disable the caching layer |
