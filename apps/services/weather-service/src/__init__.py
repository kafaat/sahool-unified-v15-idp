"""SAHOOL Weather Core Service"""

__version__ = "15.3.3"

# Export main modules
from .config import WeatherServiceConfig, get_config
from .forecast_integration import (
    AgriculturalAlert,
    AgriculturalIndices,
    WeatherForecastService,
    calculate_agricultural_indices,
    calculate_chill_hours,
    calculate_evapotranspiration,
    calculate_gdd,
    detect_drought_conditions,
    detect_frost_risk,
    detect_heat_wave,
    detect_heavy_rain,
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
