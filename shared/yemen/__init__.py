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

from shared.yemen.crops import (
    YemenCropParameters,
    get_yemen_crop,
    list_yemen_crops,
    YEMEN_CROPS,
)
from shared.yemen.climate import (
    YemenClimateZone,
    YemenClimateData,
    get_climate_zone,
    get_et0_range,
    YEMEN_CLIMATE_ZONES,
)
from shared.yemen.soils import (
    YemenSoilProfile,
    get_soil_profile,
    list_soil_profiles,
    YEMEN_SOIL_PROFILES,
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
