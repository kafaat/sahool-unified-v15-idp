"""
OpenMultiAgent Agricultural Tools
==================================
الأدوات الزراعية لـ OpenMultiAgent

Provides 8 agricultural-specific tools for AI agents that interface
with SAHOOL platform microservices for NDVI analysis, weather forecasts,
soil testing, irrigation planning, crop advisory, pest detection,
market pricing, and terrain analysis.

يوفر 8 أدوات زراعية متخصصة لوكلاء الذكاء الاصطناعي تتصل بالخدمات
المصغرة لمنصة سهول لتحليل NDVI وتوقعات الطقس واختبار التربة وتخطيط
الري والاستشارات الزراعية واكتشاف الآفات وأسعار السوق وتحليل التضاريس.

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx
import structlog

from .builtin import ToolDefinition

logger = structlog.get_logger(__name__)

# Default service ports (aligned with SERVICE_PORTS in shared-types contracts)
_SERVICE_PORTS = {
    "vegetation_analysis": 8090,
    "weather": 8092,
    "soil_analysis": 8134,
    "irrigation_smart": 8094,
    "advisory": 8093,
    "pest_detection": 8125,
    "marketplace": 3010,
    "terrain_core": 8185,
}

_DEFAULT_TIMEOUT = 20


class AgriculturalTools:
    """
    Agricultural domain tools for OpenMultiAgent agents.
    أدوات المجال الزراعي لوكلاء OpenMultiAgent.

    Provides 8 tools that call internal SAHOOL microservices:
        - ndvi_analysis: Get NDVI data for a field
        - weather_forecast: Get weather forecast for coordinates
        - soil_analysis: Get soil test data for a field
        - irrigation_calculator: Calculate irrigation requirements
        - crop_advisor: Get crop management advice
        - pest_detection: Identify pests from an image
        - market_price: Get agricultural market prices
        - terrain_analysis: Get terrain/DEM data for a field
    """

    def __init__(
        self,
        *,
        base_url: str = "http://localhost",
        service_ports: dict[str, int] | None = None,
        auth_token: str | None = None,
        tenant_id: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._ports = {**_SERVICE_PORTS, **(service_ports or {})}
        self._auth_token = auth_token
        self._tenant_id = tenant_id
        self._timeout = timeout
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            headers: dict[str, str] = {"Content-Type": "application/json"}
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"
            if self._tenant_id:
                headers["X-Tenant-ID"] = self._tenant_id
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                headers=headers,
                follow_redirects=True,
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client resources."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    def _service_url(self, service: str, path: str) -> str:
        port = self._ports.get(service, 8080)
        return f"{self._base_url}:{port}{path}"

    async def _call_service(
        self,
        service: str,
        path: str,
        *,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call an internal microservice with standard error handling."""
        url = self._service_url(service, path)
        client = await self._get_client()
        try:
            response = await client.request(
                method=method,
                url=url,
                json=body,
                params=params,
            )
            try:
                data = response.json()
            except Exception:
                data = {"raw": response.text[:4096]}

            if 200 <= response.status_code < 400:
                return {"success": True, "data": data, "status_code": response.status_code}
            return {
                "success": False,
                "error": f"Service returned {response.status_code}",
                "error_ar": f"الخدمة أعادت {response.status_code}",
                "data": data,
                "status_code": response.status_code,
            }
        except httpx.TimeoutException:
            msg = f"Service timeout: {service} | انتهت مهلة الخدمة: {service}"
            logger.warning("service_timeout", service=service, url=url)
            return {"success": False, "error": msg}
        except httpx.ConnectError:
            msg = f"Cannot connect to {service} | لا يمكن الاتصال بـ {service}"
            logger.warning("service_connect_error", service=service, url=url)
            return {"success": False, "error": msg}
        except Exception as exc:
            logger.error("service_call_failed", service=service, error=str(exc))
            return {"success": False, "error": f"Service call failed: {exc}"}

    # -------------------------------------------------------------------------
    # Tool listing
    # -------------------------------------------------------------------------

    def get_tools(self) -> list[ToolDefinition]:
        """Return all agricultural tool definitions."""
        return [
            self._ndvi_analysis_tool(),
            self._weather_forecast_tool(),
            self._soil_analysis_tool(),
            self._irrigation_calculator_tool(),
            self._crop_advisor_tool(),
            self._pest_detection_tool(),
            self._market_price_tool(),
            self._terrain_analysis_tool(),
        ]

    # -------------------------------------------------------------------------
    # 1. NDVI Analysis
    # -------------------------------------------------------------------------

    def _ndvi_analysis_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="ndvi_analysis",
            description="Get NDVI vegetation index analysis for a field",
            description_ar="الحصول على تحليل مؤشر الغطاء النباتي NDVI للحقل",
            parameters={
                "type": "object",
                "properties": {
                    "field_id": {
                        "type": "string",
                        "description": "Field identifier | معرف الحقل",
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Start date (ISO 8601) | تاريخ البداية",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date (ISO 8601) | تاريخ النهاية",
                    },
                },
                "required": ["field_id"],
            },
            execute=self._execute_ndvi_analysis,
        )

    async def _execute_ndvi_analysis(self, **kwargs: Any) -> dict[str, Any]:
        field_id: str = kwargs["field_id"]
        params: dict[str, Any] = {"field_id": field_id}
        if "date_from" in kwargs:
            params["date_from"] = kwargs["date_from"]
        if "date_to" in kwargs:
            params["date_to"] = kwargs["date_to"]

        result = await self._call_service(
            "vegetation_analysis",
            "/api/v1/ndvi/analysis",
            params=params,
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "ndvi_analysis",
                "tool_ar": "تحليل NDVI",
                "field_id": field_id,
            }
        return result

    # -------------------------------------------------------------------------
    # 2. Weather Forecast
    # -------------------------------------------------------------------------

    def _weather_forecast_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="weather_forecast",
            description="Get weather forecast for a location",
            description_ar="الحصول على توقعات الطقس لموقع محدد",
            parameters={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate | خط العرض",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate | خط الطول",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Forecast days (1-14, default 7) | أيام التوقع",
                        "default": 7,
                    },
                },
                "required": ["latitude", "longitude"],
            },
            execute=self._execute_weather_forecast,
        )

    async def _execute_weather_forecast(self, **kwargs: Any) -> dict[str, Any]:
        result = await self._call_service(
            "weather",
            "/api/v1/weather/forecast",
            params={
                "lat": kwargs["latitude"],
                "lon": kwargs["longitude"],
                "days": kwargs.get("days", 7),
            },
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "weather_forecast",
                "tool_ar": "توقعات الطقس",
                "coordinates": [kwargs["latitude"], kwargs["longitude"]],
            }
        return result

    # -------------------------------------------------------------------------
    # 3. Soil Analysis
    # -------------------------------------------------------------------------

    def _soil_analysis_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="soil_analysis",
            description="Get soil analysis data and recommendations for a field",
            description_ar="الحصول على بيانات تحليل التربة والتوصيات للحقل",
            parameters={
                "type": "object",
                "properties": {
                    "field_id": {
                        "type": "string",
                        "description": "Field identifier | معرف الحقل",
                    },
                    "test_type": {
                        "type": "string",
                        "enum": ["basic", "full", "nutrient", "salinity"],
                        "description": "Type of soil test | نوع اختبار التربة",
                        "default": "basic",
                    },
                },
                "required": ["field_id"],
            },
            execute=self._execute_soil_analysis,
        )

    async def _execute_soil_analysis(self, **kwargs: Any) -> dict[str, Any]:
        field_id: str = kwargs["field_id"]
        result = await self._call_service(
            "soil_analysis",
            f"/api/v1/soil/analysis/{field_id}",
            params={"test_type": kwargs.get("test_type", "basic")},
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "soil_analysis",
                "tool_ar": "تحليل التربة",
                "field_id": field_id,
            }
        return result

    # -------------------------------------------------------------------------
    # 4. Irrigation Calculator
    # -------------------------------------------------------------------------

    def _irrigation_calculator_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="irrigation_calculator",
            description="Calculate irrigation water requirements for a field and crop",
            description_ar="حساب متطلبات مياه الري للحقل والمحصول",
            parameters={
                "type": "object",
                "properties": {
                    "field_id": {
                        "type": "string",
                        "description": "Field identifier | معرف الحقل",
                    },
                    "crop_type": {
                        "type": "string",
                        "description": "Crop type (e.g. wheat, barley, date_palm) | نوع المحصول",
                    },
                    "crop_stage": {
                        "type": "string",
                        "description": "Growth stage (e.g. tillering, heading) | مرحلة النمو",
                    },
                    "soil_moisture": {
                        "type": "number",
                        "description": "Current soil moisture percentage | نسبة رطوبة التربة الحالية",
                    },
                },
                "required": ["field_id", "crop_type"],
            },
            execute=self._execute_irrigation_calculator,
        )

    async def _execute_irrigation_calculator(self, **kwargs: Any) -> dict[str, Any]:
        body: dict[str, Any] = {
            "field_id": kwargs["field_id"],
            "crop_type": kwargs["crop_type"],
        }
        if "crop_stage" in kwargs:
            body["crop_stage"] = kwargs["crop_stage"]
        if "soil_moisture" in kwargs:
            body["soil_moisture"] = kwargs["soil_moisture"]

        result = await self._call_service(
            "irrigation_smart",
            "/api/v1/irrigation/calculate",
            method="POST",
            body=body,
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "irrigation_calculator",
                "tool_ar": "حاسبة الري",
                "field_id": kwargs["field_id"],
                "crop_type": kwargs["crop_type"],
            }
        return result

    # -------------------------------------------------------------------------
    # 5. Crop Advisor
    # -------------------------------------------------------------------------

    def _crop_advisor_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="crop_advisor",
            description="Get crop management advice and recommendations",
            description_ar="الحصول على نصائح وتوصيات إدارة المحاصيل",
            parameters={
                "type": "object",
                "properties": {
                    "crop_type": {
                        "type": "string",
                        "description": "Crop type | نوع المحصول",
                    },
                    "query": {
                        "type": "string",
                        "description": "Advisory question or issue description | سؤال أو وصف المشكلة",
                    },
                    "field_id": {
                        "type": "string",
                        "description": "Field identifier for context | معرف الحقل للسياق",
                    },
                    "language": {
                        "type": "string",
                        "enum": ["en", "ar"],
                        "description": "Response language | لغة الاستجابة",
                        "default": "en",
                    },
                },
                "required": ["crop_type", "query"],
            },
            execute=self._execute_crop_advisor,
        )

    async def _execute_crop_advisor(self, **kwargs: Any) -> dict[str, Any]:
        body: dict[str, Any] = {
            "crop_type": kwargs["crop_type"],
            "query": kwargs["query"],
            "language": kwargs.get("language", "en"),
        }
        if "field_id" in kwargs:
            body["field_id"] = kwargs["field_id"]

        result = await self._call_service(
            "advisory",
            "/api/v1/advisory/recommend",
            method="POST",
            body=body,
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "crop_advisor",
                "tool_ar": "مستشار المحاصيل",
                "crop_type": kwargs["crop_type"],
            }
        return result

    # -------------------------------------------------------------------------
    # 6. Pest Detection
    # -------------------------------------------------------------------------

    def _pest_detection_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="pest_detection",
            description="Identify pests from an image using AI vision",
            description_ar="تحديد الآفات من صورة باستخدام الرؤية الحاسوبية",
            parameters={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file | مسار ملف الصورة",
                    },
                    "image_base64": {
                        "type": "string",
                        "description": "Base64-encoded image (alternative to path) | صورة مشفرة بـ Base64",
                    },
                    "crop_type": {
                        "type": "string",
                        "description": "Crop type for context | نوع المحصول للسياق",
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Min confidence score (0.0-1.0, default 0.25) | الحد الأدنى للثقة",
                        "default": 0.25,
                    },
                },
                "required": [],
            },
            execute=self._execute_pest_detection,
        )

    async def _execute_pest_detection(self, **kwargs: Any) -> dict[str, Any]:
        image_b64: str | None = kwargs.get("image_base64")
        image_path: str | None = kwargs.get("image_path")

        if not image_b64 and not image_path:
            return {
                "success": False,
                "error": "Either image_path or image_base64 is required | يجب توفير مسار الصورة أو صورة Base64",
            }

        # Read from file if path provided
        if image_path and not image_b64:
            p = Path(image_path)
            if not p.exists():
                return {"success": False, "error": f"Image not found: {image_path} | الصورة غير موجودة"}
            try:
                image_b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            except Exception as exc:
                return {"success": False, "error": f"Failed to read image: {exc}"}

        body: dict[str, Any] = {
            "image": image_b64,
            "confidence_threshold": kwargs.get("confidence_threshold", 0.25),
        }
        if "crop_type" in kwargs:
            body["crop_type"] = kwargs["crop_type"]

        result = await self._call_service(
            "pest_detection",
            "/api/v1/detect/pest",
            method="POST",
            body=body,
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "pest_detection",
                "tool_ar": "كشف الآفات",
                "crop_type": kwargs.get("crop_type"),
            }
        return result

    # -------------------------------------------------------------------------
    # 7. Market Price
    # -------------------------------------------------------------------------

    def _market_price_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="market_price",
            description="Get current agricultural market prices for crops",
            description_ar="الحصول على أسعار السوق الزراعية الحالية للمحاصيل",
            parameters={
                "type": "object",
                "properties": {
                    "crop_type": {
                        "type": "string",
                        "description": "Crop type to query | نوع المحصول للاستعلام",
                    },
                    "region": {
                        "type": "string",
                        "description": "Market region | منطقة السوق",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (default SAR) | رمز العملة",
                        "default": "SAR",
                    },
                },
                "required": ["crop_type"],
            },
            execute=self._execute_market_price,
        )

    async def _execute_market_price(self, **kwargs: Any) -> dict[str, Any]:
        params: dict[str, Any] = {
            "crop_type": kwargs["crop_type"],
            "currency": kwargs.get("currency", "SAR"),
        }
        if "region" in kwargs:
            params["region"] = kwargs["region"]

        result = await self._call_service(
            "marketplace",
            "/api/v1/marketplace/prices",
            params=params,
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "market_price",
                "tool_ar": "أسعار السوق",
                "crop_type": kwargs["crop_type"],
            }
        return result

    # -------------------------------------------------------------------------
    # 8. Terrain Analysis
    # -------------------------------------------------------------------------

    def _terrain_analysis_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="terrain_analysis",
            description="Get terrain and DEM analysis data for a field",
            description_ar="الحصول على بيانات تحليل التضاريس ونموذج الارتفاع الرقمي للحقل",
            parameters={
                "type": "object",
                "properties": {
                    "field_id": {
                        "type": "string",
                        "description": "Field identifier | معرف الحقل",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["elevation", "slope", "aspect", "full"],
                        "description": "Type of terrain analysis | نوع تحليل التضاريس",
                        "default": "full",
                    },
                    "resolution": {
                        "type": "number",
                        "description": "DEM resolution in meters | دقة نموذج الارتفاع بالأمتار",
                        "default": 30.0,
                    },
                },
                "required": ["field_id"],
            },
            execute=self._execute_terrain_analysis,
        )

    async def _execute_terrain_analysis(self, **kwargs: Any) -> dict[str, Any]:
        field_id: str = kwargs["field_id"]
        result = await self._call_service(
            "terrain_core",
            f"/api/v1/terrain/analysis/{field_id}",
            params={
                "analysis_type": kwargs.get("analysis_type", "full"),
                "resolution": kwargs.get("resolution", 30.0),
            },
        )
        if result["success"]:
            result["metadata"] = {
                "tool": "terrain_analysis",
                "tool_ar": "تحليل التضاريس",
                "field_id": field_id,
                "analysis_type": kwargs.get("analysis_type", "full"),
            }
        return result
