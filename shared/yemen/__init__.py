"""
SAHOOL Yemen Field Data Adapters.

Provides Yemen-specific crop parameters, climate data, soil profiles,
and regional adaptations for the SAHOOL platform.

Data sources:
- UNDP SIERY project (Hadhramaut, 2023-2024)
- FAO Yemen IWRM (Sana'a basin, 2023)
- MDPI Agricultural Water Deficit Yemen (2023)
- Sana'a University research papers
- Yemen Ministry of Agriculture crop bulletins
"""

from shared.yemen.climate import (
    YEMEN_CLIMATE_ZONES,
    YemenClimateData,
    YemenClimateZone,
    get_climate_zone,
    get_et0_range,
)
from shared.yemen.crops import (
    YEMEN_CROPS,
    YemenCropParameters,
    get_yemen_crop,
    list_yemen_crops,
)
from shared.yemen.soils import (
    YEMEN_SOIL_PROFILES,
    YemenSoilProfile,
    get_soil_profile,
    list_soil_profiles,
)

__all__ = [
    "YemenCropParameters",
    "get_yemen_crop",
    "list_yemen_crops",
    "YEMEN_CROPS",
    "YemenClimateZone",
    "YemenClimateData",
    "get_climate_zone",
    "get_et0_range",
    "YEMEN_CLIMATE_ZONES",
    "YemenSoilProfile",
    "get_soil_profile",
    "list_soil_profiles",
    "YEMEN_SOIL_PROFILES",
]
