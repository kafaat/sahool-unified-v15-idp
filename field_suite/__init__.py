"""
SAHOOL Field Suite Domain
Agricultural field management: Farms, Fields, Crops, Zones, Operations

Hierarchy: Farm → Field → Zone → SubZone
"""

from .farms import Farm, FarmService
from .fields import Field, FieldService
from .crops import Crop, CropService
from .zones import Zone, SubZone, ZoneBoundary, ZoneType

__version__ = "16.0.0"

__all__ = [
    # Farms
    "Farm",
    "FarmService",
    # Fields
    "Field",
    "FieldService",
    # Crops
    "Crop",
    "CropService",
    # Zones (Sprint 7)
    "Zone",
    "SubZone",
    "ZoneBoundary",
    "ZoneType",
]
