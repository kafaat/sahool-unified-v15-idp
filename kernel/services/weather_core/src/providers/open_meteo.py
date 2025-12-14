"""
Open-Meteo Weather Provider - SAHOOL Weather Core
Free weather API integration for Yemen
"""

import httpx
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class WeatherData:
    """Current weather data"""
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    wind_direction_deg: int
    precipitation_mm: float
    cloud_cover_pct: float
    pressure_hpa: float
    uv_index: float
    timestamp: str


@dataclass
class DailyForecast:
    """Daily weather forecast"""
    date: str
    temp_max_c: float
    temp_min_c: float
    precipitation_mm: float
    precipitation_probability_pct: float
    wind_speed_max_kmh: float
    uv_index_max: float
    sunrise: str
    sunset: str


@dataclass
class HourlyForecast:
    """Hourly weather forecast"""
    datetime: str
    temperature_c: float
    humidity_pct: float
    precipitation_mm: float
    precipitation_probability_pct: float
    wind_speed_kmh: float
    cloud_cover_pct: float


class OpenMeteoProvider:
    """
    Open-Meteo API client for weather data

    Free API, no key required
    https://open-meteo.com/
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        """
        Get current weather conditions

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            WeatherData with current conditions
        """
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
            ],
            "timezone": "auto",
        }

        try:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})

            return WeatherData(
                temperature_c=current.get("temperature_2m", 0),
                humidity_pct=current.get("relative_humidity_2m", 0),
                wind_speed_kmh=current.get("wind_speed_10m", 0),
                wind_direction_deg=current.get("wind_direction_10m", 0),
                precipitation_mm=current.get("precipitation", 0),
                cloud_cover_pct=current.get("cloud_cover", 0),
                pressure_hpa=current.get("pressure_msl", 0),
                uv_index=current.get("uv_index", 0),
                timestamp=current.get("time", datetime.utcnow().isoformat()),
            )

        except Exception as e:
            print(f"❌ Open-Meteo API error: {e}")
            raise

    async def get_daily_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 7,
    ) -> list[DailyForecast]:
        """
        Get daily weather forecast

        Args:
            lat: Latitude
            lon: Longitude
            days: Number of forecast days (1-16)

        Returns:
            List of DailyForecast
        """
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
                "sunrise",
                "sunset",
            ],
            "timezone": "auto",
            "forecast_days": min(days, 16),
        }

        try:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            forecasts = []

            dates = daily.get("time", [])
            for i, d in enumerate(dates):
                forecasts.append(
                    DailyForecast(
                        date=d,
                        temp_max_c=daily.get("temperature_2m_max", [0])[i],
                        temp_min_c=daily.get("temperature_2m_min", [0])[i],
                        precipitation_mm=daily.get("precipitation_sum", [0])[i],
                        precipitation_probability_pct=daily.get("precipitation_probability_max", [0])[i],
                        wind_speed_max_kmh=daily.get("wind_speed_10m_max", [0])[i],
                        uv_index_max=daily.get("uv_index_max", [0])[i],
                        sunrise=daily.get("sunrise", [""])[i],
                        sunset=daily.get("sunset", [""])[i],
                    )
                )

            return forecasts

        except Exception as e:
            print(f"❌ Open-Meteo forecast error: {e}")
            raise

    async def get_hourly_forecast(
        self,
        lat: float,
        lon: float,
        hours: int = 24,
    ) -> list[HourlyForecast]:
        """
        Get hourly weather forecast

        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours (up to 168)

        Returns:
            List of HourlyForecast
        """
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
            ],
            "timezone": "auto",
            "forecast_hours": min(hours, 168),
        }

        try:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            hourly = data.get("hourly", {})
            forecasts = []

            times = hourly.get("time", [])[:hours]
            for i, t in enumerate(times):
                forecasts.append(
                    HourlyForecast(
                        datetime=t,
                        temperature_c=hourly.get("temperature_2m", [0])[i],
                        humidity_pct=hourly.get("relative_humidity_2m", [0])[i],
                        precipitation_mm=hourly.get("precipitation", [0])[i],
                        precipitation_probability_pct=hourly.get("precipitation_probability", [0])[i],
                        wind_speed_kmh=hourly.get("wind_speed_10m", [0])[i],
                        cloud_cover_pct=hourly.get("cloud_cover", [0])[i],
                    )
                )

            return forecasts

        except Exception as e:
            print(f"❌ Open-Meteo hourly error: {e}")
            raise


# Mock provider for testing
class MockWeatherProvider:
    """Mock weather provider for testing"""

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        return WeatherData(
            temperature_c=32.5,
            humidity_pct=45,
            wind_speed_kmh=12,
            wind_direction_deg=180,
            precipitation_mm=0,
            cloud_cover_pct=20,
            pressure_hpa=1013,
            uv_index=8,
            timestamp=datetime.utcnow().isoformat(),
        )

    async def get_daily_forecast(self, lat: float, lon: float, days: int = 7) -> list[DailyForecast]:
        from datetime import timedelta
        forecasts = []
        today = date.today()

        for i in range(days):
            d = today + timedelta(days=i)
            forecasts.append(
                DailyForecast(
                    date=d.isoformat(),
                    temp_max_c=35 + (i % 3),
                    temp_min_c=22 + (i % 2),
                    precipitation_mm=0 if i % 3 != 0 else 5,
                    precipitation_probability_pct=10 if i % 3 != 0 else 40,
                    wind_speed_max_kmh=15 + (i * 2),
                    uv_index_max=9,
                    sunrise="06:00",
                    sunset="18:30",
                )
            )

        return forecasts

    async def close(self):
        pass
