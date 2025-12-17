"""
SAHOOL Field Suite Domain
Agricultural field management: Farms, Fields, Crops, Operations
"""

from .farms import Farm, FarmService
from .fields import Field, FieldService
from .crops import Crop, CropService

__version__ = "16.0.0"

__all__ = [
    "Farm",
    "FarmService",
    "Field",
    "FieldService",
    "Crop",
    "CropService",
]
