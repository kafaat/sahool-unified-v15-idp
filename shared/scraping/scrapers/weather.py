"""Weather data scraper for agricultural applications.

This module provides the WeatherScraper class for collecting weather data
from public weather sources, extracting temperature, humidity, wind,
and rain forecast information.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..browser import BrowserManager
from ..config import ScrapingConfig
from ..utils import (
    clean_text,
    extract_first_number,
    normalize_location,
    parse_date,
    parse_percentage,
    parse_temperature,
)
from .base import BaseScraper, ScrapingResult, ScrapingStatus

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Current weather data."""

    temperature_c: float | None = None
    feels_like_c: float | None = None
    humidity_percent: float | None = None
    wind_speed_kmh: float | None = None
    wind_direction: str | None = None
    pressure_hpa: float | None = None
    visibility_km: float | None = None
    uv_index: float | None = None
    condition: str | None = None
    condition_ar: str | None = None
    observation_time: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "temperature_c": self.temperature_c,
            "feels_like_c": self.feels_like_c,
            "humidity_percent": self.humidity_percent,
            "wind_speed_kmh": self.wind_speed_kmh,
            "wind_direction": self.wind_direction,
            "pressure_hpa": self.pressure_hpa,
            "visibility_km": self.visibility_km,
            "uv_index": self.uv_index,
            "condition": self.condition,
            "condition_ar": self.condition_ar,
            "observation_time": (self.observation_time.isoformat() if self.observation_time else None),
        }


@dataclass
class DailyForecast:
    """Daily weather forecast."""

    date: datetime | None = None
    high_temp_c: float | None = None
    low_temp_c: float | None = None
    humidity_percent: float | None = None
    rain_probability_percent: float | None = None
    rain_amount_mm: float | None = None
    wind_speed_kmh: float | None = None
    condition: str | None = None
    condition_ar: str | None = None
    sunrise: str | None = None
    sunset: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat() if self.date else None,
            "high_temp_c": self.high_temp_c,
            "low_temp_c": self.low_temp_c,
            "humidity_percent": self.humidity_percent,
            "rain_probability_percent": self.rain_probability_percent,
            "rain_amount_mm": self.rain_amount_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "condition": self.condition,
            "condition_ar": self.condition_ar,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
        }


@dataclass
class WeatherForecast:
    """Complete weather forecast including current and future."""

    location: str
    location_ar: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    current: WeatherData | None = None
    daily_forecast: list[DailyForecast] = field(default_factory=list)
    source: str | None = None
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "location": self.location,
            "location_ar": self.location_ar,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": self.current.to_dict() if self.current else None,
            "daily_forecast": [f.to_dict() for f in self.daily_forecast],
            "source": self.source,
            "fetched_at": self.fetched_at.isoformat(),
        }


# Weather condition translations
WEATHER_CONDITIONS: dict[str, str] = {
    "clear": "صافي",
    "sunny": "مشمس",
    "partly cloudy": "غائم جزئياً",
    "cloudy": "غائم",
    "overcast": "ملبد بالغيوم",
    "rain": "ممطر",
    "light rain": "أمطار خفيفة",
    "heavy rain": "أمطار غزيرة",
    "thunderstorm": "عاصفة رعدية",
    "snow": "ثلج",
    "fog": "ضباب",
    "mist": "ضباب خفيف",
    "haze": "غبار",
    "dust": "غبار",
    "sandstorm": "عاصفة رملية",
    "windy": "عاصف",
    "hot": "حار",
    "cold": "بارد",
}


class WeatherScraper(BaseScraper):
    """Scraper for weather data from public sources.

    This scraper collects weather data including current conditions
    and forecasts from various public weather websites.

    Example:
        >>> async with BrowserManager() as browser:
        ...     scraper = WeatherScraper(browser)
        ...     result = await scraper.scrape_forecast(lat=24.7, lon=46.7)
        ...     if result.status == ScrapingStatus.SUCCESS:
        ...         print(f"Temperature: {result.data.current.temperature_c}°C")
    """

    # Weather source URLs
    SOURCES = {
        "timeanddate": "https://www.timeanddate.com/weather/{location}",
        "weather_com": "https://weather.com/weather/today/l/{lat},{lon}",
        "accuweather": "https://www.accuweather.com/en/search-locations?query={location}",
    }

    def __init__(
        self,
        browser: BrowserManager,
        config: ScrapingConfig | None = None,
        default_source: str = "timeanddate",
    ) -> None:
        """Initialize the weather scraper.

        Args:
            browser: Browser manager instance.
            config: Scraping configuration.
            default_source: Default weather source.
        """
        super().__init__(browser, config)
        self._default_source = default_source

    def _translate_condition(self, condition: str) -> str:
        """Translate weather condition to Arabic.

        Args:
            condition: English weather condition.

        Returns:
            Arabic translation or original if not found.
        """
        condition_lower = condition.lower().strip()
        for eng, ar in WEATHER_CONDITIONS.items():
            if eng in condition_lower:
                return ar
        return condition

    async def scrape_forecast(
        self,
        lat: float | None = None,
        lon: float | None = None,
        location: str | None = None,
        days: int = 7,
        source: str | None = None,
    ) -> ScrapingResult[WeatherForecast]:
        """Scrape weather forecast for a location.

        Args:
            lat: Latitude coordinate.
            lon: Longitude coordinate.
            location: Location name (if coordinates not provided).
            days: Number of forecast days (1-14).
            source: Weather source to use.

        Returns:
            ScrapingResult containing WeatherForecast.
        """
        import time

        start_time = time.time()

        # Validate input
        if not lat and not lon and not location:
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                error="Either coordinates (lat, lon) or location name required",
            )

        # Normalize location
        location_str = location or f"{lat},{lon}"
        location_normalized = normalize_location(location_str)

        # Check cache
        cache_key = f"weather_{location_normalized}_{days}"
        cached = self.get_cached(cache_key)
        if cached:
            return ScrapingResult(
                status=ScrapingStatus.CACHED,
                data=cached,
                cached=True,
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Select source and scrape
        source = source or self._default_source

        try:
            if source == "timeanddate":
                forecast = await self._scrape_timeanddate(location_normalized, lat, lon, days)
            else:
                # Default fallback
                forecast = await self._scrape_timeanddate(location_normalized, lat, lon, days)

            # Cache result
            self.set_cached(
                cache_key,
                forecast,
                ttl=self._config.cache.weather_ttl,
            )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Weather data scraped for {location_normalized} in {duration_ms:.0f}ms")

            return ScrapingResult(
                status=ScrapingStatus.SUCCESS,
                data=forecast,
                url=self._page.url if self._page else None,
                duration_ms=duration_ms,
            )

        except Exception as e:
            logger.error(f"Weather scraping failed: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def _scrape_timeanddate(
        self,
        location: str,
        lat: float | None,
        lon: float | None,
        days: int,
    ) -> WeatherForecast:
        """Scrape weather from timeanddate.com.

        Args:
            location: Location name.
            lat: Latitude.
            lon: Longitude.
            days: Number of forecast days.

        Returns:
            WeatherForecast data.
        """
        # Format location for URL
        url_location = location.lower().replace(" ", "-").replace(",", "/")
        url = f"https://www.timeanddate.com/weather/saudi-arabia/{url_location}"

        await self.with_retry(
            "Navigate to weather page",
            self.navigate,
            url,
            wait_until="networkidle",
        )

        # Extract current weather
        current = WeatherData()

        # Temperature
        temp_text = await self.extract_text("#qlook .h2")
        current.temperature_c = parse_temperature(temp_text)

        # Condition
        condition_text = await self.extract_text("#qlook .mtt")
        current.condition = clean_text(condition_text)
        current.condition_ar = self._translate_condition(current.condition or "")

        # Details table
        details = await self.extract_table("#wt-ext")
        for row in details:
            if len(row) >= 2:
                label = row[0].lower()
                value = row[1]

                if "humidity" in label or "رطوبة" in label:
                    current.humidity_percent = parse_percentage(value)
                elif "wind" in label or "رياح" in label:
                    current.wind_speed_kmh = extract_first_number(value)
                elif "pressure" in label or "ضغط" in label:
                    current.pressure_hpa = extract_first_number(value)
                elif "visibility" in label or "رؤية" in label:
                    current.visibility_km = extract_first_number(value)

        current.observation_time = datetime.now()

        # Extract daily forecast
        daily_forecast: list[DailyForecast] = []

        forecast_rows = await self.extract_table("#wt-ext-7d")
        for row in forecast_rows[:days]:
            if len(row) >= 3:
                daily = DailyForecast()

                # Date
                daily.date = parse_date(row[0])

                # Temperature (high/low)
                temps = row[1] if len(row) > 1 else ""
                temp_parts = temps.split("/")
                if len(temp_parts) >= 2:
                    daily.high_temp_c = parse_temperature(temp_parts[0])
                    daily.low_temp_c = parse_temperature(temp_parts[1])
                elif temp_parts:
                    daily.high_temp_c = parse_temperature(temp_parts[0])

                # Condition
                if len(row) > 2:
                    daily.condition = clean_text(row[2])
                    daily.condition_ar = self._translate_condition(daily.condition or "")

                daily_forecast.append(daily)

        return WeatherForecast(
            location=location,
            location_ar=normalize_location(location),
            latitude=lat,
            longitude=lon,
            current=current,
            daily_forecast=daily_forecast,
            source="timeanddate.com",
        )

    async def scrape(self, **kwargs: Any) -> ScrapingResult[WeatherForecast]:
        """Perform weather scraping.

        Args:
            **kwargs: Scraping parameters (lat, lon, location, days, source).

        Returns:
            ScrapingResult with WeatherForecast.
        """
        return await self.scrape_forecast(**kwargs)

    async def get_agricultural_weather(
        self,
        lat: float,
        lon: float,
        crop_type: str | None = None,
    ) -> dict[str, Any]:
        """Get weather data with agricultural context.

        Args:
            lat: Latitude coordinate.
            lon: Longitude coordinate.
            crop_type: Optional crop type for specific recommendations.

        Returns:
            Dictionary with weather data and agricultural insights.
        """
        result = await self.scrape_forecast(lat=lat, lon=lon, days=7)

        if result.status != ScrapingStatus.SUCCESS or not result.data:
            return {"error": result.error, "status": result.status.value}

        forecast = result.data
        current = forecast.current

        # Calculate agricultural metrics
        insights = {
            "weather": forecast.to_dict(),
            "agricultural_insights": {
                "irrigation_needed": False,
                "frost_risk": False,
                "heat_stress_risk": False,
                "spray_conditions": "unknown",
                "field_work_conditions": "unknown",
            },
        }

        if current:
            temp = current.temperature_c
            humidity = current.humidity_percent
            wind = current.wind_speed_kmh

            # Frost risk
            if temp is not None and temp < 5:
                insights["agricultural_insights"]["frost_risk"] = True

            # Heat stress
            if temp is not None and temp > 35:
                insights["agricultural_insights"]["heat_stress_risk"] = True

            # Spray conditions (optimal: low wind, moderate temp, no rain)
            if wind is not None and temp is not None:
                if wind < 15 and 10 < temp < 30:
                    insights["agricultural_insights"]["spray_conditions"] = "optimal"
                elif wind < 25:
                    insights["agricultural_insights"]["spray_conditions"] = "acceptable"
                else:
                    insights["agricultural_insights"]["spray_conditions"] = "poor"

            # Field work conditions
            if humidity is not None and wind is not None:
                if humidity < 80 and wind < 30:
                    insights["agricultural_insights"]["field_work_conditions"] = "good"
                elif humidity < 90 and wind < 40:
                    insights["agricultural_insights"]["field_work_conditions"] = "fair"
                else:
                    insights["agricultural_insights"]["field_work_conditions"] = "poor"

        # Check forecast for rain
        rain_expected = False
        for daily in forecast.daily_forecast[:3]:
            if daily.rain_probability_percent and daily.rain_probability_percent > 30:
                rain_expected = True
                break

        insights["agricultural_insights"]["irrigation_needed"] = not rain_expected

        return insights
