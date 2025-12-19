"""
SAHOOL Spatial Module
PostGIS-enabled ORM models and spatial utilities

This module provides:
- SQLAlchemy ORM models with PostGIS geometry columns
- Spatial query utilities (bbox, intersects, within)
- Geometry validation and repair
- GIST index management
"""

from .orm_models import (
    Base,
    FarmORM,
    FieldORM,
    ZoneORM,
    SubZoneORM,
)
from .queries import (
    fields_in_bbox,
    zones_in_field,
    subzones_in_zone,
    find_containing_field,
    calculate_area_hectares,
)
from .validation import (
    validate_and_fix_geometries,
    GeometryValidationReport,
)

__all__ = [
    # ORM Models
    "Base",
    "FarmORM",
    "FieldORM",
    "ZoneORM",
    "SubZoneORM",
    # Queries
    "fields_in_bbox",
    "zones_in_field",
    "subzones_in_zone",
    "find_containing_field",
    "calculate_area_hectares",
    # Validation
    "validate_and_fix_geometries",
    "GeometryValidationReport",
]
