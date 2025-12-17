"""
SAHOOL Legacy Field Compatibility
Re-exports from field_suite

DEPRECATED: Use field_suite instead
"""

import warnings

warnings.warn(
    "legacy.field is deprecated. Use field_suite instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from field_suite import (
    Farm,
    FarmService,
    Field,
    FieldService,
    Crop,
    CropService,
)

__all__ = [
    "Farm",
    "FarmService",
    "Field",
    "FieldService",
    "Crop",
    "CropService",
]
