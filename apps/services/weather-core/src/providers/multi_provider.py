"""
SAHOOL Weather Providers - Multi-Provider Weather Service
خدمة الطقس متعددة المزودين

Supported Providers:
- Open-Meteo (Free - No API key required)
- OpenWeatherMap (Requires API key)
- WeatherAPI (Requires API key)
- Visual Crossing (Requires API key)
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import httpx

# ═══════════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class WeatherData:
    """Current weather data - بيانات الطقس الحالية"""

    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    wind_direction_deg: int
    wind_direction: str
    precipitation_mm: float
    cloud_cover_pct: float
    pressure_hpa: float
    uv_index: float
    condition: str
    condition_ar: str
    icon: str
    timestamp: str
    provider: str


@dataclass
class DailyForecast:
    """Daily weather forecast - توقعات الطقس اليومية"""

    date: str
    temp_max_c: float
    temp_min_c: float
    precipitation_mm: float
    precipitation_probability_pct: float
    wind_speed_max_kmh: float
    uv_index_max: float
    condition: str
    condition_ar: str
    icon: str
    sunrise: str | None = None
    sunset: str | None = None


@dataclass
class HourlyForecast:
    """Hourly weather forecast - توقعات الطقس الساعية"""

    datetime: str
    temperature_c: float
    humidity_pct: float
    precipitation_mm: float
    precipitation_probability_pct: float
    wind_speed_kmh: float
    cloud_cover_pct: float
    condition: str
    condition_ar: str


@dataclass
class WeatherResult:
    """Weather service result with fallback info"""

    data: Any
    provider: str
    failed_providers: list[str] = field(default_factory=list)
    is_cached: bool = False
    error: str | None = None
    error_ar: str | None = None

    @property
    def success(self) -> bool:
        return self.data is not None and self.error is None


class WeatherProviderType(Enum):
    OPEN_METEO = "open_meteo"
    OPENWEATHERMAP = "openweathermap"
    WEATHERAPI = "weatherapi"
    VISUAL_CROSSING = "visual_crossing"


# ═══════════════════════════════════════════════════════════════════════════════
# Base Provider Interface
# ═══════════════════════════════════════════════════════════════════════════════


class WeatherProvider(ABC):
    """Base class for weather providers"""

    def __init__(self, name: str, api_key: str | None = None):
        self.name = name
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        return True  # Override in providers that require API key

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def get_current(self, lat: float, lon: float) -> WeatherData:
        pass

    @abstractmethod
    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> list[DailyForecast]:
        pass

    @abstractmethod
    async def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> list[HourlyForecast]:
        pass

    # Helper functions
    @staticmethod
    def degree_to_direction(degree: float) -> str:
        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        index = int((degree + 11.25) / 22.5) % 16
        return directions[index]


# ═══════════════════════════════════════════════════════════════════════════════
# Open-Meteo Provider (FREE - No API Key)
# ═══════════════════════════════════════════════════════════════════════════════


class OpenMeteoProvider(WeatherProvider):
    """
    Open-Meteo API - Free weather data
    مجاني - لا يحتاج مفتاح API
    https://open-meteo.com/
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        super().__init__("Open-Meteo")

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        client = await self._get_client()

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
                "wind_speed_10m",
                "wind_direction_10m",
                "uv_index",
                "weather_code",
            ],
            "timezone": "auto",
        }

        response = await client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        weather_code = current.get("weather_code", 0)
        wind_deg = current.get("wind_direction_10m", 0)

        return WeatherData(
            temperature_c=current.get("temperature_2m", 0),
            humidity_pct=current.get("relative_humidity_2m", 0),
            wind_speed_kmh=current.get("wind_speed_10m", 0),
            wind_direction_deg=wind_deg,
            wind_direction=self.degree_to_direction(wind_deg),
            precipitation_mm=current.get("precipitation", 0),
            cloud_cover_pct=current.get("cloud_cover", 0),
            pressure_hpa=current.get("pressure_msl", 1013),
            uv_index=current.get("uv_index", 0),
            condition=self._wmo_to_condition(weather_code),
            condition_ar=self._wmo_to_condition_ar(weather_code),
            icon=self._wmo_to_icon(weather_code),
            timestamp=current.get("time", datetime.utcnow().isoformat()),
            provider=self.name,
        )

    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> list[DailyForecast]:
        client = await self._get_client()

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "uv_index_max",
                "weather_code",
                "sunrise",
                "sunset",
            ],
            "timezone": "auto",
            "forecast_days": min(days, 16),
        }

        response = await client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        daily = data.get("daily", {})

        forecasts = []
        dates = daily.get("time", [])

        for i, d in enumerate(dates):
            weather_code = daily.get("weather_code", [0])[i]
            forecasts.append(
                DailyForecast(
                    date=d,
                    temp_max_c=daily.get("temperature_2m_max", [0])[i],
                    temp_min_c=daily.get("temperature_2m_min", [0])[i],
                    precipitation_mm=daily.get("precipitation_sum", [0])[i] or 0,
                    precipitation_probability_pct=daily.get(
                        "precipitation_probability_max", [0]
                    )[i]
                    or 0,
                    wind_speed_max_kmh=daily.get("wind_speed_10m_max", [0])[i],
                    uv_index_max=daily.get("uv_index_max", [0])[i] or 0,
                    condition=self._wmo_to_condition(weather_code),
                    condition_ar=self._wmo_to_condition_ar(weather_code),
                    icon=self._wmo_to_icon(weather_code),
                    sunrise=daily.get("sunrise", [""])[i],
                    sunset=daily.get("sunset", [""])[i],
                )
            )

        return forecasts

    async def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> list[HourlyForecast]:
        client = await self._get_client()

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "precipitation_probability",
                "wind_speed_10m",
                "cloud_cover",
                "weather_code",
            ],
            "timezone": "auto",
            "forecast_hours": min(hours, 168),
        }

        response = await client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        hourly = data.get("hourly", {})

        forecasts = []
        times = hourly.get("time", [])[:hours]

        for i, t in enumerate(times):
            weather_code = hourly.get("weather_code", [0])[i]
            forecasts.append(
                HourlyForecast(
                    datetime=t,
                    temperature_c=hourly.get("temperature_2m", [0])[i],
                    humidity_pct=hourly.get("relative_humidity_2m", [0])[i],
                    precipitation_mm=hourly.get("precipitation", [0])[i] or 0,
                    precipitation_probability_pct=hourly.get(
                        "precipitation_probability", [0]
                    )[i]
                    or 0,
                    wind_speed_kmh=hourly.get("wind_speed_10m", [0])[i],
                    cloud_cover_pct=hourly.get("cloud_cover", [0])[i],
                    condition=self._wmo_to_condition(weather_code),
                    condition_ar=self._wmo_to_condition_ar(weather_code),
                )
            )

        return forecasts

    @staticmethod
    def _wmo_to_condition(code: int) -> str:
        if code == 0:
            return "Clear"
        if code <= 3:
            return "Partly Cloudy"
        if code <= 49:
            return "Foggy"
        if code <= 59:
            return "Drizzle"
        if code <= 69:
            return "Rain"
        if code <= 79:
            return "Snow"
        if code <= 84:
            return "Rain Showers"
        if code <= 94:
            return "Snow Showers"
        return "Thunderstorm"

    @staticmethod
    def _wmo_to_condition_ar(code: int) -> str:
        if code == 0:
            return "صافي"
        if code <= 3:
            return "غائم جزئياً"
        if code <= 49:
            return "ضبابي"
        if code <= 59:
            return "رذاذ"
        if code <= 69:
            return "مطر"
        if code <= 79:
            return "ثلج"
        if code <= 84:
            return "زخات مطر"
        if code <= 94:
            return "زخات ثلجية"
        return "عاصفة رعدية"

    @staticmethod
    def _wmo_to_icon(code: int) -> str:
        if code == 0:
            return "clear"
        if code <= 3:
            return "partly_cloudy"
        if code <= 49:
            return "fog"
        if code <= 59:
            return "drizzle"
        if code <= 69:
            return "rain"
        if code <= 79:
            return "snow"
        if code <= 84:
            return "rain_showers"
        if code <= 94:
            return "snow_showers"
        return "thunderstorm"


# ═══════════════════════════════════════════════════════════════════════════════
# OpenWeatherMap Provider
# ═══════════════════════════════════════════════════════════════════════════════


class OpenWeatherMapProvider(WeatherProvider):
    """
    OpenWeatherMap API
    يحتاج مفتاح API
    https://openweathermap.org/
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str | None = None):
        super().__init__(
            "OpenWeatherMap", api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        if not self.is_configured:
            raise ValueError("OpenWeatherMap API key not configured")

        client = await self._get_client()
        url = f"{self.BASE_URL}/weather"

        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        wind_deg = data.get("wind", {}).get("deg", 0)
        condition = data.get("weather", [{}])[0].get("main", "Unknown")

        return WeatherData(
            temperature_c=data.get("main", {}).get("temp", 0),
            humidity_pct=data.get("main", {}).get("humidity", 0),
            wind_speed_kmh=data.get("wind", {}).get("speed", 0) * 3.6,  # m/s to km/h
            wind_direction_deg=wind_deg,
            wind_direction=self.degree_to_direction(wind_deg),
            precipitation_mm=data.get("rain", {}).get("1h", 0),
            cloud_cover_pct=data.get("clouds", {}).get("all", 0),
            pressure_hpa=data.get("main", {}).get("pressure", 1013),
            uv_index=0,  # Not available in basic API
            condition=condition,
            condition_ar=self._condition_to_ar(condition),
            icon=data.get("weather", [{}])[0].get("icon", "01d"),
            timestamp=datetime.utcnow().isoformat(),
            provider=self.name,
        )

    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> list[DailyForecast]:
        if not self.is_configured:
            raise ValueError("OpenWeatherMap API key not configured")

        client = await self._get_client()
        url = f"{self.BASE_URL}/forecast"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8,  # 3-hour intervals
        }

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Group by day
        daily_data: dict[str, list[Any]] = {}
        for item in data.get("list", []):
            day = item["dt_txt"].split(" ")[0]
            daily_data.setdefault(day, []).append(item)

        forecasts = []
        for day, items in list(daily_data.items())[:days]:
            temps = [i["main"]["temp"] for i in items]
            precips = [i.get("rain", {}).get("3h", 0) for i in items]
            condition = items[0]["weather"][0]["main"]

            forecasts.append(
                DailyForecast(
                    date=day,
                    temp_max_c=max(temps),
                    temp_min_c=min(temps),
                    precipitation_mm=sum(precips),
                    precipitation_probability_pct=int(
                        (items[0].get("pop", 0) or 0) * 100
                    ),
                    wind_speed_max_kmh=items[0]["wind"]["speed"] * 3.6,
                    uv_index_max=0,
                    condition=condition,
                    condition_ar=self._condition_to_ar(condition),
                    icon=items[0]["weather"][0]["icon"],
                )
            )

        return forecasts

    async def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> list[HourlyForecast]:
        if not self.is_configured:
            raise ValueError("OpenWeatherMap API key not configured")

        client = await self._get_client()
        url = f"{self.BASE_URL}/forecast"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "cnt": min(hours // 3, 40),  # 3-hour intervals, max 5 days
        }

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for item in data.get("list", [])[: hours // 3]:
            condition = item["weather"][0]["main"]
            forecasts.append(
                HourlyForecast(
                    datetime=item["dt_txt"],
                    temperature_c=item["main"]["temp"],
                    humidity_pct=item["main"]["humidity"],
                    precipitation_mm=item.get("rain", {}).get("3h", 0),
                    precipitation_probability_pct=int((item.get("pop", 0) or 0) * 100),
                    wind_speed_kmh=item["wind"]["speed"] * 3.6,
                    cloud_cover_pct=item["clouds"]["all"],
                    condition=condition,
                    condition_ar=self._condition_to_ar(condition),
                )
            )

        return forecasts

    @staticmethod
    def _condition_to_ar(condition: str) -> str:
        translations = {
            "Clear": "صافي",
            "Clouds": "غائم",
            "Rain": "مطر",
            "Drizzle": "رذاذ",
            "Thunderstorm": "عاصفة رعدية",
            "Snow": "ثلج",
            "Mist": "ضباب خفيف",
            "Fog": "ضباب",
            "Haze": "ضباب دخاني",
        }
        return translations.get(condition, condition)


# ═══════════════════════════════════════════════════════════════════════════════
# WeatherAPI Provider
# ═══════════════════════════════════════════════════════════════════════════════


class WeatherAPIProvider(WeatherProvider):
    """
    WeatherAPI.com
    يحتاج مفتاح API
    https://www.weatherapi.com/
    """

    BASE_URL = "https://api.weatherapi.com/v1"

    def __init__(self, api_key: str | None = None):
        super().__init__("WeatherAPI", api_key or os.getenv("WEATHERAPI_KEY"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        if not self.is_configured:
            raise ValueError("WeatherAPI key not configured")

        client = await self._get_client()
        url = f"{self.BASE_URL}/current.json"

        params = {"key": self.api_key, "q": f"{lat},{lon}", "aqi": "no"}

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        return WeatherData(
            temperature_c=current.get("temp_c", 0),
            humidity_pct=current.get("humidity", 0),
            wind_speed_kmh=current.get("wind_kph", 0),
            wind_direction_deg=current.get("wind_degree", 0),
            wind_direction=current.get("wind_dir", "N"),
            precipitation_mm=current.get("precip_mm", 0),
            cloud_cover_pct=current.get("cloud", 0),
            pressure_hpa=current.get("pressure_mb", 1013),
            uv_index=current.get("uv", 0),
            condition=current.get("condition", {}).get("text", "Unknown"),
            condition_ar=current.get("condition", {}).get("text", "غير معروف"),
            icon=current.get("condition", {}).get("icon", ""),
            timestamp=datetime.utcnow().isoformat(),
            provider=self.name,
        )

    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> list[DailyForecast]:
        if not self.is_configured:
            raise ValueError("WeatherAPI key not configured")

        client = await self._get_client()
        url = f"{self.BASE_URL}/forecast.json"

        params = {
            "key": self.api_key,
            "q": f"{lat},{lon}",
            "days": min(days, 14),
            "aqi": "no",
        }

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for day in data.get("forecast", {}).get("forecastday", []):
            day_data = day.get("day", {})
            forecasts.append(
                DailyForecast(
                    date=day.get("date"),
                    temp_max_c=day_data.get("maxtemp_c", 0),
                    temp_min_c=day_data.get("mintemp_c", 0),
                    precipitation_mm=day_data.get("totalprecip_mm", 0),
                    precipitation_probability_pct=day_data.get(
                        "daily_chance_of_rain", 0
                    ),
                    wind_speed_max_kmh=day_data.get("maxwind_kph", 0),
                    uv_index_max=day_data.get("uv", 0),
                    condition=day_data.get("condition", {}).get("text", "Unknown"),
                    condition_ar=day_data.get("condition", {}).get("text", "غير معروف"),
                    icon=day_data.get("condition", {}).get("icon", ""),
                    sunrise=day.get("astro", {}).get("sunrise"),
                    sunset=day.get("astro", {}).get("sunset"),
                )
            )

        return forecasts

    async def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> list[HourlyForecast]:
        if not self.is_configured:
            raise ValueError("WeatherAPI key not configured")

        client = await self._get_client()
        url = f"{self.BASE_URL}/forecast.json"

        params = {"key": self.api_key, "q": f"{lat},{lon}", "days": 2, "aqi": "no"}

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for day in data.get("forecast", {}).get("forecastday", []):
            for hour in day.get("hour", []):
                if len(forecasts) >= hours:
                    break
                forecasts.append(
                    HourlyForecast(
                        datetime=hour.get("time"),
                        temperature_c=hour.get("temp_c", 0),
                        humidity_pct=hour.get("humidity", 0),
                        precipitation_mm=hour.get("precip_mm", 0),
                        precipitation_probability_pct=hour.get("chance_of_rain", 0),
                        wind_speed_kmh=hour.get("wind_kph", 0),
                        cloud_cover_pct=hour.get("cloud", 0),
                        condition=hour.get("condition", {}).get("text", "Unknown"),
                        condition_ar=hour.get("condition", {}).get("text", "غير معروف"),
                    )
                )

        return forecasts


# ═══════════════════════════════════════════════════════════════════════════════
# Multi-Provider Weather Service
# ═══════════════════════════════════════════════════════════════════════════════


class MultiWeatherService:
    """
    Multi-provider weather service with automatic fallback
    خدمة الطقس متعددة المزودين مع التبديل التلقائي

    Priority:
    1. Open-Meteo (Free - always available)
    2. OpenWeatherMap (if configured)
    3. WeatherAPI (if configured)
    """

    def __init__(self):
        self.providers: list[WeatherProvider] = [
            OpenMeteoProvider(),  # Free - always first
        ]

        # Add configured providers
        if os.getenv("OPENWEATHERMAP_API_KEY"):
            self.providers.append(OpenWeatherMapProvider())

        if os.getenv("WEATHERAPI_KEY"):
            self.providers.append(WeatherAPIProvider())

        # Simple in-memory cache
        self._cache: dict[str, tuple] = {}
        self._cache_duration = timedelta(minutes=10)

    async def close(self):
        """Close all provider connections"""
        for provider in self.providers:
            await provider.close()

    def _get_cached(self, key: str):
        """Get cached result if still valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.utcnow() - timestamp < self._cache_duration:
                return data
            del self._cache[key]
        return None

    def _set_cached(self, key: str, data: Any):
        """Cache a result"""
        self._cache[key] = (data, datetime.utcnow())

    async def get_current(self, lat: float, lon: float) -> WeatherResult:
        """Get current weather with automatic fallback"""
        cache_key = f"current_{lat:.2f}_{lon:.2f}"

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return WeatherResult(data=cached, provider="cache", is_cached=True)

        failed_providers = []

        for provider in self.providers:
            if not provider.is_configured:
                continue

            try:
                data = await provider.get_current(lat, lon)
                self._set_cached(cache_key, data)
                return WeatherResult(
                    data=data, provider=provider.name, failed_providers=failed_providers
                )
            except Exception as e:
                failed_providers.append(f"{provider.name}: {str(e)}")

        return WeatherResult(
            data=None,
            provider="none",
            failed_providers=failed_providers,
            error="All weather providers failed",
            error_ar="فشل جميع مزودي الطقس",
        )

    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> WeatherResult:
        """Get daily forecast with automatic fallback"""
        cache_key = f"daily_{lat:.2f}_{lon:.2f}_{days}"

        cached = self._get_cached(cache_key)
        if cached:
            return WeatherResult(data=cached, provider="cache", is_cached=True)

        failed_providers = []

        for provider in self.providers:
            if not provider.is_configured:
                continue

            try:
                data = await provider.get_daily_forecast(lat, lon, days)
                if data:
                    self._set_cached(cache_key, data)
                    return WeatherResult(
                        data=data,
                        provider=provider.name,
                        failed_providers=failed_providers,
                    )
            except Exception as e:
                failed_providers.append(f"{provider.name}: {str(e)}")

        return WeatherResult(
            data=None,
            provider="none",
            failed_providers=failed_providers,
            error="All forecast providers failed",
            error_ar="فشل جميع مزودي التوقعات",
        )

    async def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> WeatherResult:
        """Get hourly forecast with automatic fallback"""
        cache_key = f"hourly_{lat:.2f}_{lon:.2f}_{hours}"

        cached = self._get_cached(cache_key)
        if cached:
            return WeatherResult(data=cached, provider="cache", is_cached=True)

        failed_providers = []

        for provider in self.providers:
            if not provider.is_configured:
                continue

            try:
                data = await provider.get_hourly_forecast(lat, lon, hours)
                if data:
                    self._set_cached(cache_key, data)
                    return WeatherResult(
                        data=data,
                        provider=provider.name,
                        failed_providers=failed_providers,
                    )
            except Exception as e:
                failed_providers.append(f"{provider.name}: {str(e)}")

        return WeatherResult(
            data=None,
            provider="none",
            failed_providers=failed_providers,
            error="All hourly forecast providers failed",
            error_ar="فشل جميع مزودي التوقعات الساعية",
        )

    def get_available_providers(self) -> list[dict[str, Any]]:
        """Get list of available providers"""
        return [
            {
                "name": p.name,
                "configured": p.is_configured,
                "type": p.__class__.__name__,
            }
            for p in self.providers
        ]
