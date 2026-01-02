"""SAHOOL Weather Core Service"""

__version__ = "15.3.3"

# Export main modules
from .config import get_config, WeatherServiceConfig
from .forecast_integration import (
    WeatherForecastService,
    AgriculturalAlert,
    AgriculturalIndices,
    detect_frost_risk,
    detect_heat_wave,
    detect_heavy_rain,
    detect_drought_conditions,
    calculate_gdd,
    calculate_chill_hours,
    calculate_evapotranspiration,
    calculate_agricultural_indices,
)

__all__ = [
    # Configuration
    "get_config",
    "WeatherServiceConfig",
    # Forecast service
    "WeatherForecastService",
    # Data models
    "AgriculturalAlert",
    "AgriculturalIndices",
    # Alert detection functions
    "detect_frost_risk",
    "detect_heat_wave",
    "detect_heavy_rain",
    "detect_drought_conditions",
    # Agricultural indices functions
    "calculate_gdd",
    "calculate_chill_hours",
    "calculate_evapotranspiration",
    "calculate_agricultural_indices",
]
