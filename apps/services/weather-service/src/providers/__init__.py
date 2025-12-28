"""Weather Providers - مزودي بيانات الطقس"""

from .open_meteo import (
    DailyForecast,
    HourlyForecast,
    MockWeatherProvider,
    OpenMeteoProvider,
    WeatherData,
)

from .multi_provider import (
    MultiWeatherService,
    WeatherProvider,
    WeatherResult,
    OpenMeteoProvider as MultiOpenMeteoProvider,
    OpenWeatherMapProvider,
    WeatherAPIProvider,
    WeatherData as MultiWeatherData,
    DailyForecast as MultiDailyForecast,
    HourlyForecast as MultiHourlyForecast,
)

__all__ = [
    # Legacy single providers
    "OpenMeteoProvider",
    "MockWeatherProvider",
    "WeatherData",
    "DailyForecast",
    "HourlyForecast",
    # Multi-provider service
    "MultiWeatherService",
    "WeatherProvider",
    "WeatherResult",
    "OpenWeatherMapProvider",
    "WeatherAPIProvider",
]
