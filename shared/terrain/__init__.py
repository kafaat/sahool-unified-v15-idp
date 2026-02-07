"""
SAHOOL Terrain Shared Module
============================
Shared utilities for terrain analysis services.

مودول التضاريس المشترك

Includes:
- Validators for GeoJSON, coordinates, elevations, grades
- GeoJSON utilities for parsing, creation, and manipulation
- Common terrain data structures
- Caching utilities for terrain calculations

Usage:
    from shared.terrain import validators, geojson_utils
    from shared.terrain.validators import validate_geojson_polygon
    from shared.terrain.geojson_utils import create_feature_collection

Author: SAHOOL Platform
Version: 16.0.0
"""

from . import validators
from . import geojson_utils

__all__ = ["validators", "geojson_utils"]
__version__ = "16.0.0"
