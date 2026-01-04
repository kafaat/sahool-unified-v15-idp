"""Weather Providers - مزودي بيانات الطقس"""

from .multi_provider import (
    DailyForecast as MultiDailyForecast,
)
from .multi_provider import (
    HourlyForecast as MultiHourlyForecast,
)
from .multi_provider import (
    MultiWeatherService,
    OpenWeatherMapProvider,
    WeatherAPIProvider,
    WeatherProvider,
    WeatherResult,
)
from .multi_provider import (
    OpenMeteoProvider as MultiOpenMeteoProvider,
)
from .multi_provider import (
    WeatherData as MultiWeatherData,
)
from .open_meteo import (
    DailyForecast,
    HourlyForecast,
    MockWeatherProvider,
    OpenMeteoProvider,
    WeatherData,
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
