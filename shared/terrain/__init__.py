"""
SAHOOL Terrain Shared Module
============================
Shared utilities for terrain analysis services.

مودول التضاريس المشترك

Includes:
- Validators for GeoJSON, coordinates, elevations, grades
- GeoJSON utilities for parsing, creation, and manipulation
- Caching utilities for terrain calculations
- Standardized API response formatting
- Batch processing utilities
- Common terrain data structures

Usage:
    from shared.terrain import validators, geojson_utils, cache, responses, batch
    from shared.terrain.validators import validate_geojson_polygon
    from shared.terrain.geojson_utils import create_feature_collection
    from shared.terrain.cache import TerrainCache, cache_result
    from shared.terrain.responses import success_response, error_response
    from shared.terrain.batch import BatchProcessor, process_batch

Author: SAHOOL Platform
Version: 16.0.0
"""

from . import validators
from . import geojson_utils
from . import cache
from . import responses
from . import batch

__all__ = ["validators", "geojson_utils", "cache", "responses", "batch"]
__version__ = "16.0.0"
