# SAHOOL Field Suite Package

> Spatial and domain models for agricultural field management

## Modules

| Module        | Description                                     |
| ------------- | ----------------------------------------------- |
| `fields/`     | Field domain models and services                |
| `farms/`      | Farm management models                          |
| `crops/`      | Crop types and configurations                   |
| `spatial/`    | PostGIS ORM models, spatial queries, validation |
| `zones/`      | Management zone definitions                     |
| `migrations/` | Alembic migrations for PostGIS                  |

## Usage

```python
from packages.field_suite.spatial import SpatialQueries
from packages.field_suite.fields import FieldService
```

## Dependencies

- `geoalchemy2` for PostGIS
- `shapely` for geometry
- `sqlalchemy` for ORM

## Consumers

- `kernel/services/field_core/`
- `kernel/services/field_ops/`
- `kernel-services-v15.3/crop-growth-model/`
