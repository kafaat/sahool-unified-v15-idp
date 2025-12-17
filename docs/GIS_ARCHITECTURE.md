# SAHOOL GIS Architecture

> Sprint 7 - Spatial Data Enhancement

## Overview

SAHOOL implements a hierarchical GIS structure for precision agriculture:

```
Farm → Field → Zone → SubZone
```

Each level supports PostGIS geometry for spatial queries.

## Hierarchy

### Farm
- Top-level container
- Has location (lat/lon)
- Contains multiple Fields

### Field
- Agricultural parcel
- Polygon geometry (PostGIS)
- Contains multiple Zones
- Properties: soil_type, irrigation_type, crop

### Zone
- Management unit within Field
- Types: irrigation, soil_type, ndvi_cluster, yield_zone, management, custom
- Contains multiple SubZones
- Properties stored as JSONB

### SubZone
- Finest granularity
- Used for Variable Rate Application (VRA)
- Sensor placement areas
- Targeted interventions

## PostGIS Integration

### Geometry Columns

Each spatial table has:
- `geometry_wkt`: WKT string for compatibility
- `geom`: Native PostGIS geometry(Polygon, 4326)

A trigger automatically syncs `geometry_wkt` → `geom` on INSERT/UPDATE.

### Spatial Indexes

GIST indexes are created for efficient spatial queries:
- `ix_fields_geom`
- `ix_zones_geom`
- `ix_subzones_geom`

### Common Queries

```python
from field_suite.spatial import fields_in_bbox, find_containing_field

# Find fields in bounding box
fields = fields_in_bbox(
    db,
    tenant_id=tenant_id,
    xmin=30.0, ymin=30.0,
    xmax=32.0, ymax=32.0,
)

# Find field containing a point
field = find_containing_field(
    db,
    tenant_id=tenant_id,
    latitude=30.5,
    longitude=31.5,
)
```

## Geometry Validation

The validation job detects and fixes invalid geometries:

```python
from field_suite.spatial import validate_and_fix_geometries

report = validate_and_fix_geometries(db)
print(f"Fixed: {report.total_fixed} geometries")
```

Fixes applied:
- `ST_MakeValid`: Repairs invalid geometry
- `ST_Force2D`: Ensures 2D (removes Z/M)
- `ST_CollectionExtract(..., 3)`: Extracts polygons

## Zone Types

| Type | Use Case |
|------|----------|
| `irrigation` | Irrigation management zones |
| `soil_type` | Soil classification zones |
| `ndvi_cluster` | NDVI-based clustering |
| `yield_zone` | Historical yield zones |
| `management` | General management zones |
| `custom` | User-defined zones |

## Migration

Run PostGIS migration:
```bash
make gis-migrate
```

Or directly:
```bash
alembic -c field_suite/migrations/alembic.ini upgrade head
```

## Makefile Commands

```bash
make gis-migrate    # Run PostGIS migrations
make gis-validate   # Validate/fix geometries
make gis-test       # Run GIS tests
make gis-status     # Check GIS infrastructure
```

## Files Structure

```
field_suite/
├── zones/
│   ├── __init__.py
│   └── models.py          # Zone, SubZone domain models
├── spatial/
│   ├── __init__.py
│   ├── orm_models.py      # SQLAlchemy ORM with PostGIS
│   ├── queries.py         # Spatial query utilities
│   └── validation.py      # Geometry validation job
└── migrations/
    └── versions/
        └── s7_0001_postgis_hierarchy.py
```

## Best Practices

1. **Always use GIST indexes** for spatial queries
2. **Validate geometries** before bulk imports
3. **Use WKT for imports**, geom column for queries
4. **Tenant isolation** on all spatial queries
5. **Area calculations** use geography type for accuracy
