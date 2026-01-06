"""
Weather Tool
أداة الطقس

Tool for calling the weather-service.
أداة لاستدعاء خدمة الطقس.
"""

from typing import Any

import httpx
import structlog

from ..config import settings

logger = structlog.get_logger()


class WeatherTool:
    """
    Tool to interact with weather-service
    أداة للتفاعل مع خدمة الطقس
    """

    def __init__(self):
        self.base_url = settings.weather_core_url
        self.timeout = 30.0

    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Get current weather conditions
        الحصول على ظروف الطقس الحالية

        Args:
            latitude: Location latitude | خط العرض
            longitude: Location longitude | خط الطول

        Returns:
            Current weather data | بيانات الطقس الحالية
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/weather/current",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "current_weather_retrieved", latitude=latitude, longitude=longitude
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "current_weather_failed",
                error=str(e),
                latitude=latitude,
                longitude=longitude,
            )
            return {"error": str(e), "status": "failed"}

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> dict[str, Any]:
        """
        Get weather forecast
        الحصول على توقعات الطقس

        Args:
            latitude: Location latitude | خط العرض
            longitude: Location longitude | خط الطول
            days: Number of days to forecast | عدد أيام التوقع

        Returns:
            Weather forecast data | بيانات توقعات الطقس
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/weather/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "days": days,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "weather_forecast_retrieved",
                    latitude=latitude,
                    longitude=longitude,
                    days=days,
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "weather_forecast_failed",
                error=str(e),
                latitude=latitude,
                longitude=longitude,
            )
            return {"error": str(e), "status": "failed"}

    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """
        Get historical weather data
        الحصول على بيانات الطقس التاريخية

        Args:
            latitude: Location latitude | خط العرض
            longitude: Location longitude | خط الطول
            start_date: Start date (YYYY-MM-DD) | تاريخ البداية
            end_date: End date (YYYY-MM-DD) | تاريخ النهاية

        Returns:
            Historical weather data | بيانات الطقس التاريخية
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/weather/historical",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "historical_weather_retrieved",
                    latitude=latitude,
                    longitude=longitude,
                    period=f"{start_date} to {end_date}",
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "historical_weather_failed",
                error=str(e),
                latitude=latitude,
                longitude=longitude,
            )
            return {"error": str(e), "status": "failed"}

    async def get_et0(
        self,
        latitude: float,
        longitude: float,
        date: str | None = None,
    ) -> dict[str, Any]:
        """
        Get reference evapotranspiration (ET0)
        الحصول على التبخر النتح المرجعي

        Args:
            latitude: Location latitude | خط العرض
            longitude: Location longitude | خط الطول
            date: Date (YYYY-MM-DD), defaults to today | التاريخ

        Returns:
            ET0 data | بيانات التبخر النتح المرجعي
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                }
                if date:
                    params["date"] = date

                response = await client.get(
                    f"{self.base_url}/api/v1/weather/et0", params=params
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "et0_retrieved",
                    latitude=latitude,
                    longitude=longitude,
                    date=date or "today",
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "et0_retrieval_failed",
                error=str(e),
                latitude=latitude,
                longitude=longitude,
            )
            return {"error": str(e), "status": "failed"}

    async def get_alerts(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Get weather alerts and warnings
        الحصول على تنبيهات وتحذيرات الطقس

        Args:
            latitude: Location latitude | خط العرض
            longitude: Location longitude | خط الطول

        Returns:
            Weather alerts | تنبيهات الطقس
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/weather/alerts",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "weather_alerts_retrieved",
                    latitude=latitude,
                    longitude=longitude,
                    alert_count=len(result.get("alerts", [])),
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "weather_alerts_failed",
                error=str(e),
                latitude=latitude,
                longitude=longitude,
            )
            return {"error": str(e), "status": "failed"}
