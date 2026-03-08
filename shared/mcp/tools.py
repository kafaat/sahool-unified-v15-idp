"""
SAHOOL MCP Tools - Agricultural Intelligence Tools
===================================================

Implements MCP tool specifications for SAHOOL agricultural platform.
Each tool follows the Model Context Protocol specification for tool invocation.

Tool Categories:
- Agricultural Tools: Field data, crop health, weather, irrigation, fertilizer
- Farmer CRM Tools: Farmer info, interaction logging, recommendations history
- AI Agent Tools: Agent spawning, querying, and status management

All tools include bilingual descriptions (English/Arabic).

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel

from .config import (
    AgentType,
    Language,
    MCPConfig,
    ToolDescriptions,
    get_config,
)


class ToolResult(BaseModel):
    """Standard result format for tool execution"""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    error_ar: str | None = None  # Arabic error message
    metadata: dict[str, Any] | None = None


class AgentInstance(BaseModel):
    """Represents a spawned AI agent instance"""

    agent_id: str
    agent_type: AgentType
    created_at: datetime
    last_active: datetime
    status: str  # 'active', 'idle', 'terminated'
    context: dict[str, Any] | None = None
    query_count: int = 0


class SAHOOLTools:
    """
    SAHOOL Agricultural Tools for MCP Integration

    Provides agricultural intelligence tools that can be invoked by AI assistants
    through the Model Context Protocol.

    Tool Categories:
    1. Agricultural Tools - Field, crop health, weather, irrigation, fertilizer
    2. Farmer CRM Tools - Farmer management and interaction tracking
    3. AI Agent Tools - Specialized agent spawning and management
    """

    def __init__(self, base_url: str | None = None, config: MCPConfig | None = None):
        """
        Initialize SAHOOL Tools

        Args:
            base_url: Base URL for SAHOOL API (default: from env or localhost)
            config: MCP configuration (default: from environment)
        """
        self.config = config or get_config()
        self.base_url = base_url or self.config.api.base_url
        self.client = httpx.AsyncClient(timeout=self.config.api.default_timeout)

        # Agent pool for managing spawned agents
        self._agents: dict[str, AgentInstance] = {}
        self._agent_lock = asyncio.Lock()

    async def close(self):
        """Close HTTP client and cleanup agents"""
        await self.client.aclose()
        # Cleanup all agents
        async with self._agent_lock:
            self._agents.clear()

    # ==================== Tool Definitions ====================

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Get MCP tool definitions for all SAHOOL tools

        Returns:
            List of tool definitions following MCP specification
        """
        return [
            # ==================== Agricultural Tools ====================
            {
                "name": "fetch_field_data",
                "description": ToolDescriptions.get("fetch_field_data", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the field | معرف الحقل الفريد",
                        },
                        "include_history": {
                            "type": "boolean",
                            "description": "Include historical data and activities | تضمين البيانات التاريخية والأنشطة",
                            "default": False,
                        },
                        "include_sensors": {
                            "type": "boolean",
                            "description": "Include IoT sensor data | تضمين بيانات مستشعرات إنترنت الأشياء",
                            "default": False,
                        },
                        "language": {
                            "type": "string",
                            "description": "Response language (en, ar, both)",
                            "enum": ["en", "ar", "both"],
                            "default": "both",
                        },
                    },
                    "required": ["field_id"],
                },
            },
            {
                "name": "analyze_crop_health",
                "description": ToolDescriptions.get("analyze_crop_health", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the agricultural field | معرف الحقل الزراعي الفريد",
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform | نوع التحليل المطلوب",
                            "enum": ["ndvi", "ndwi", "lai", "full"],
                            "default": "ndvi",
                        },
                        "date": {
                            "type": "string",
                            "description": "Date for analysis in YYYY-MM-DD format (default: latest) | تاريخ التحليل",
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "description": "Include action recommendations | تضمين توصيات العمل",
                            "default": True,
                        },
                    },
                    "required": ["field_id"],
                },
            },
            {
                "name": "get_weather_forecast",
                "description": ToolDescriptions.get("get_weather_forecast", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude of the location | خط العرض",
                            "minimum": -90,
                            "maximum": 90,
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude of the location | خط الطول",
                            "minimum": -180,
                            "maximum": 180,
                        },
                        "field_id": {
                            "type": "string",
                            "description": "Field ID (alternative to lat/lon) | معرف الحقل (بديل للإحداثيات)",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to forecast (1-14) | عدد أيام التوقع",
                            "default": 7,
                            "minimum": 1,
                            "maximum": 14,
                        },
                        "include_advisories": {
                            "type": "boolean",
                            "description": "Include agricultural advisories | تضمين الإرشادات الزراعية",
                            "default": True,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "irrigation_recommendation",
                "description": ToolDescriptions.get("irrigation_recommendation", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the field | معرف الحقل الفريد",
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (e.g., wheat, tomatoes) | نوع المحصول (مثل القمح، الطماطم)",
                        },
                        "soil_moisture": {
                            "type": "number",
                            "description": "Current soil moisture percentage (0-100) | نسبة رطوبة التربة الحالية",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "growth_stage": {
                            "type": "string",
                            "description": "Current growth stage | مرحلة النمو الحالية",
                            "enum": [
                                "germination",
                                "vegetative",
                                "tillering",
                                "flowering",
                                "fruiting",
                                "maturation",
                            ],
                        },
                        "irrigation_system": {
                            "type": "string",
                            "description": "Type of irrigation system | نوع نظام الري",
                            "enum": ["drip", "sprinkler", "flood", "pivot"],
                            "default": "drip",
                        },
                    },
                    "required": ["field_id", "crop_type"],
                },
            },
            {
                "name": "fertilizer_recommendation",
                "description": ToolDescriptions.get("fertilizer_recommendation", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the field | معرف الحقل الفريد",
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop being grown | نوع المحصول المزروع",
                        },
                        "soil_test": {
                            "type": "object",
                            "description": "Soil test results | نتائج تحليل التربة",
                            "properties": {
                                "nitrogen_ppm": {
                                    "type": "number",
                                    "description": "النيتروجين (ppm)",
                                },
                                "phosphorus_ppm": {
                                    "type": "number",
                                    "description": "الفوسفور (ppm)",
                                },
                                "potassium_ppm": {
                                    "type": "number",
                                    "description": "البوتاسيوم (ppm)",
                                },
                                "ph": {"type": "number", "description": "درجة الحموضة"},
                                "organic_matter_pct": {
                                    "type": "number",
                                    "description": "نسبة المادة العضوية",
                                },
                            },
                        },
                        "target_yield": {
                            "type": "number",
                            "description": "Target yield in tons per hectare | الإنتاج المستهدف (طن/هكتار)",
                        },
                        "growth_stage": {
                            "type": "string",
                            "description": "Current growth stage | مرحلة النمو الحالية",
                        },
                    },
                    "required": ["field_id", "crop_type"],
                },
            },
            # ==================== Farmer CRM Tools ====================
            {
                "name": "get_farmer_info",
                "description": ToolDescriptions.get("get_farmer_info", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "farmer_id": {
                            "type": "string",
                            "description": "Unique identifier for the farmer | معرف المزارع الفريد",
                        },
                        "include_farms": {
                            "type": "boolean",
                            "description": "Include list of farms | تضمين قائمة المزارع",
                            "default": True,
                        },
                        "include_preferences": {
                            "type": "boolean",
                            "description": "Include farmer preferences | تضمين تفضيلات المزارع",
                            "default": True,
                        },
                        "include_interaction_history": {
                            "type": "boolean",
                            "description": "Include recent interactions | تضمين التفاعلات الأخيرة",
                            "default": False,
                        },
                    },
                    "required": ["farmer_id"],
                },
            },
            {
                "name": "log_interaction",
                "description": ToolDescriptions.get("log_interaction", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "farmer_id": {
                            "type": "string",
                            "description": "Farmer identifier | معرف المزارع",
                        },
                        "interaction_type": {
                            "type": "string",
                            "description": "Type of interaction | نوع التفاعل",
                            "enum": [
                                "advisory",
                                "query",
                                "complaint",
                                "feedback",
                                "follow_up",
                                "training",
                            ],
                        },
                        "channel": {
                            "type": "string",
                            "description": "Communication channel | قناة الاتصال",
                            "enum": ["app", "phone", "sms", "whatsapp", "field_visit", "ai_chat"],
                            "default": "ai_chat",
                        },
                        "summary": {
                            "type": "string",
                            "description": "Brief summary of the interaction | ملخص موجز للتفاعل",
                        },
                        "summary_ar": {
                            "type": "string",
                            "description": "Arabic summary | الملخص بالعربية",
                        },
                        "advisory_given": {
                            "type": "string",
                            "description": "Advisory or recommendation provided | الاستشارة أو التوصية المقدمة",
                        },
                        "farmer_response": {
                            "type": "string",
                            "description": "Farmer's response or feedback | رد أو تعليق المزارع",
                        },
                        "follow_up_required": {
                            "type": "boolean",
                            "description": "Whether follow-up is needed | هل المتابعة مطلوبة",
                            "default": False,
                        },
                        "follow_up_date": {
                            "type": "string",
                            "description": "Follow-up date (YYYY-MM-DD) | تاريخ المتابعة",
                        },
                        "field_id": {
                            "type": "string",
                            "description": "Related field ID (if applicable) | معرف الحقل المرتبط",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorization | وسوم للتصنيف",
                        },
                    },
                    "required": ["farmer_id", "interaction_type", "summary"],
                },
            },
            {
                "name": "get_recommendations_history",
                "description": ToolDescriptions.get("get_recommendations_history", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "farmer_id": {
                            "type": "string",
                            "description": "Farmer identifier | معرف المزارع",
                        },
                        "field_id": {
                            "type": "string",
                            "description": "Filter by field ID | التصفية حسب معرف الحقل",
                        },
                        "recommendation_type": {
                            "type": "string",
                            "description": "Filter by recommendation type | التصفية حسب نوع التوصية",
                            "enum": [
                                "irrigation",
                                "fertilizer",
                                "pest_control",
                                "disease_treatment",
                                "planting",
                                "harvest",
                                "general",
                            ],
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look back | عدد الأيام للعودة",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 365,
                        },
                        "include_outcomes": {
                            "type": "boolean",
                            "description": "Include outcome feedback | تضمين نتائج التطبيق",
                            "default": True,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records | الحد الأقصى للسجلات",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100,
                        },
                    },
                    "required": ["farmer_id"],
                },
            },
            # ==================== AI Agent Tools ====================
            {
                "name": "spawn_agent",
                "description": ToolDescriptions.get("spawn_agent", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_type": {
                            "type": "string",
                            "description": "Type of specialized agent | نوع الوكيل المتخصص",
                            "enum": [
                                "crop_advisor",
                                "irrigation_specialist",
                                "pest_management",
                                "soil_analyst",
                                "weather_analyst",
                                "farm_planner",
                                "general_assistant",
                            ],
                        },
                        "context": {
                            "type": "object",
                            "description": "Initial context for the agent | السياق الأولي للوكيل",
                            "properties": {
                                "field_id": {"type": "string"},
                                "farmer_id": {"type": "string"},
                                "crop_type": {"type": "string"},
                                "custom_instructions": {"type": "string"},
                                "language_preference": {
                                    "type": "string",
                                    "enum": ["en", "ar", "both"],
                                },
                            },
                        },
                        "model": {
                            "type": "string",
                            "description": "AI model to use | نموذج الذكاء الاصطناعي",
                            "default": "claude-3-sonnet",
                        },
                        "timeout_seconds": {
                            "type": "integer",
                            "description": "Agent timeout in seconds | مهلة الوكيل بالثواني",
                            "default": 300,
                            "minimum": 60,
                            "maximum": 3600,
                        },
                    },
                    "required": ["agent_type"],
                },
            },
            {
                "name": "query_agent",
                "description": ToolDescriptions.get("query_agent", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the spawned agent | معرف الوكيل المُنشأ",
                        },
                        "query": {
                            "type": "string",
                            "description": "Question or task for the agent | السؤال أو المهمة للوكيل",
                        },
                        "additional_context": {
                            "type": "object",
                            "description": "Additional context for this query | سياق إضافي لهذا الاستفسار",
                        },
                        "include_sources": {
                            "type": "boolean",
                            "description": "Include data sources in response | تضمين مصادر البيانات في الرد",
                            "default": True,
                        },
                        "response_format": {
                            "type": "string",
                            "description": "Preferred response format | تنسيق الرد المفضل",
                            "enum": ["text", "structured", "actionable"],
                            "default": "text",
                        },
                    },
                    "required": ["agent_id", "query"],
                },
            },
            {
                "name": "get_agent_status",
                "description": ToolDescriptions.get("get_agent_status", Language.BOTH),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the agent to check | معرف الوكيل للتحقق",
                        },
                        "include_metrics": {
                            "type": "boolean",
                            "description": "Include usage metrics | تضمين مقاييس الاستخدام",
                            "default": True,
                        },
                    },
                    "required": ["agent_id"],
                },
            },
        ]

    # ==================== Agricultural Tool Implementations ====================

    async def fetch_field_data(
        self,
        field_id: str,
        include_history: bool = False,
        include_sensors: bool = False,
        language: str = "both",
    ) -> ToolResult:
        """
        Retrieve comprehensive field data

        Args:
            field_id: Unique identifier for the field
            include_history: Include historical data
            include_sensors: Include IoT sensor data
            language: Response language preference

        Returns:
            ToolResult with field data
        """
        try:
            params = {
                "include_history": include_history,
                "include_sensors": include_sensors,
            }

            response = await self.client.get(f"{self.base_url}/api/fields/{field_id}", params=params)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "name": data.get("name"),
                    "name_ar": data.get("name_ar", data.get("name")),
                    "area_hectares": data.get("area_hectares"),
                    "boundaries": data.get("boundaries", {}),
                    "soil_properties": data.get("soil_properties", {}),
                    "current_crop": data.get("current_crop", {}),
                    "history": data.get("history", []) if include_history else None,
                    "sensors": data.get("sensors", []) if include_sensors else None,
                    "location": data.get("location", {}),
                    "irrigation_type": data.get("irrigation_type"),
                },
                metadata={
                    "last_updated": data.get("updated_at"),
                    "owner": data.get("owner"),
                    "language": language,
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Field data API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة بيانات الحقل: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    async def analyze_crop_health(
        self,
        field_id: str,
        analysis_type: str = "ndvi",
        date: str | None = None,
        include_recommendations: bool = True,
    ) -> ToolResult:
        """
        Analyze crop health using satellite imagery

        Args:
            field_id: Unique identifier for the field
            analysis_type: Type of analysis (ndvi, ndwi, lai, full)
            date: Date for analysis (YYYY-MM-DD)
            include_recommendations: Include action recommendations

        Returns:
            ToolResult with crop health analysis
        """
        try:
            params = {"field_id": field_id, "analysis_type": analysis_type}
            if date:
                params["date"] = date
            params["include_recommendations"] = include_recommendations

            response = await self.client.get(f"{self.base_url}/api/crop-health/analyze", params=params)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "analysis_type": analysis_type,
                    "ndvi_average": data.get("ndvi_average"),
                    "ndvi_min": data.get("ndvi_min"),
                    "ndvi_max": data.get("ndvi_max"),
                    "health_status": data.get("health_status"),
                    "health_status_ar": data.get("health_status_ar", data.get("health_status")),
                    "stress_areas": data.get("stress_areas", []),
                    "disease_risk": data.get("disease_risk", {}),
                    "recommendations": data.get("recommendations", []),
                    "recommendations_ar": data.get("recommendations_ar", []),
                },
                metadata={
                    "analysis_date": data.get("analysis_date"),
                    "satellite_source": data.get("satellite_source", "Sentinel-2"),
                    "cloud_coverage": data.get("cloud_coverage"),
                    "confidence_score": data.get("confidence_score"),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Crop health API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة صحة المحصول: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    async def get_weather_forecast(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        field_id: str | None = None,
        days: int = 7,
        include_advisories: bool = True,
    ) -> ToolResult:
        """
        Get weather forecast for a location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            field_id: Field ID (alternative to coordinates)
            days: Number of days to forecast
            include_advisories: Include agricultural advisories

        Returns:
            ToolResult with weather forecast data
        """
        try:
            params = {"days": days, "include_advisories": include_advisories}

            if field_id:
                params["field_id"] = field_id
            elif latitude is not None and longitude is not None:
                params["latitude"] = latitude
                params["longitude"] = longitude
            else:
                return ToolResult(
                    success=False,
                    error="Either field_id or latitude/longitude required",
                    error_ar="مطلوب إما معرف الحقل أو خط العرض/الطول",
                )

            response = await self.client.get(f"{self.base_url}/api/weather/forecast", params=params)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "location": data.get("location", {}),
                    "forecast": data.get("forecast", []),
                    "advisories": data.get("advisories", []),
                    "advisories_ar": data.get("advisories_ar", []),
                    "summary": data.get("summary", ""),
                    "summary_ar": data.get("summary_ar", ""),
                    "alerts": data.get("alerts", []),
                },
                metadata={
                    "provider": data.get("provider", "SAHOOL Weather"),
                    "updated_at": datetime.now(UTC).isoformat(),
                    "units": data.get("units", "metric"),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Weather API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة الطقس: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    async def irrigation_recommendation(
        self,
        field_id: str,
        crop_type: str,
        soil_moisture: float | None = None,
        growth_stage: str | None = None,
        irrigation_system: str = "drip",
    ) -> ToolResult:
        """
        Calculate optimal irrigation requirements

        Args:
            field_id: Unique identifier for the field
            crop_type: Type of crop
            soil_moisture: Current soil moisture percentage
            growth_stage: Current growth stage
            irrigation_system: Type of irrigation system

        Returns:
            ToolResult with irrigation recommendations
        """
        try:
            payload = {
                "field_id": field_id,
                "crop_type": crop_type,
                "irrigation_system": irrigation_system,
            }
            if soil_moisture is not None:
                payload["soil_moisture"] = soil_moisture
            if growth_stage:
                payload["growth_stage"] = growth_stage

            response = await self.client.post(f"{self.base_url}/api/irrigation/calculate", json=payload)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "recommendation": data.get("recommendation"),
                    "recommendation_ar": data.get("recommendation_ar"),
                    "water_amount_mm": data.get("water_amount_mm"),
                    "water_volume_m3": data.get("water_volume_m3"),
                    "duration_minutes": data.get("duration_minutes"),
                    "optimal_time": data.get("optimal_time"),
                    "next_irrigation_date": data.get("next_irrigation_date"),
                    "soil_moisture_target": data.get("soil_moisture_target"),
                    "adjustment_factors": data.get("adjustment_factors", {}),
                    "cost_estimate": data.get("cost_estimate"),
                },
                metadata={
                    "calculation_method": data.get("calculation_method"),
                    "confidence": data.get("confidence"),
                    "based_on_weather": data.get("based_on_weather", False),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Irrigation API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة الري: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    async def fertilizer_recommendation(
        self,
        field_id: str,
        crop_type: str,
        soil_test: dict[str, float] | None = None,
        target_yield: float | None = None,
        growth_stage: str | None = None,
    ) -> ToolResult:
        """
        Get fertilizer recommendations

        Args:
            field_id: Unique identifier for the field
            crop_type: Type of crop
            soil_test: Soil test results
            target_yield: Target yield in tons/ha
            growth_stage: Current growth stage

        Returns:
            ToolResult with fertilizer recommendations
        """
        try:
            payload = {
                "field_id": field_id,
                "crop_type": crop_type,
            }
            if soil_test:
                payload["soil_test"] = soil_test
            if target_yield:
                payload["target_yield"] = target_yield
            if growth_stage:
                payload["growth_stage"] = growth_stage

            response = await self.client.post(f"{self.base_url}/api/fertilizer/recommend", json=payload)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "crop_type": crop_type,
                    "npk_recommendation": data.get("npk_recommendation", {}),
                    "product_recommendations": data.get("product_recommendations", []),
                    "application_schedule": data.get("application_schedule", []),
                    "application_method": data.get("application_method"),
                    "application_method_ar": data.get("application_method_ar"),
                    "total_cost_estimate": data.get("total_cost_estimate"),
                    "organic_alternatives": data.get("organic_alternatives", []),
                    "warnings": data.get("warnings", []),
                    "warnings_ar": data.get("warnings_ar", []),
                },
                metadata={
                    "recommendation_basis": data.get("recommendation_basis"),
                    "confidence_score": data.get("confidence_score"),
                    "generated_at": datetime.now(UTC).isoformat(),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Fertilizer API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة الأسمدة: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    # ==================== Farmer CRM Tool Implementations ====================

    async def get_farmer_info(
        self,
        farmer_id: str,
        include_farms: bool = True,
        include_preferences: bool = True,
        include_interaction_history: bool = False,
    ) -> ToolResult:
        """
        Retrieve farmer profile information

        Args:
            farmer_id: Unique identifier for the farmer
            include_farms: Include list of farms
            include_preferences: Include farmer preferences
            include_interaction_history: Include recent interactions

        Returns:
            ToolResult with farmer information
        """
        try:
            params = {
                "include_farms": include_farms,
                "include_preferences": include_preferences,
                "include_interaction_history": include_interaction_history,
            }

            response = await self.client.get(f"{self.base_url}/api/farmers/{farmer_id}", params=params)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "farmer_id": farmer_id,
                    "name": data.get("name"),
                    "name_ar": data.get("name_ar"),
                    "phone": data.get("phone"),
                    "email": data.get("email"),
                    "location": data.get("location", {}),
                    "language_preference": data.get("language_preference", "ar"),
                    "farms": data.get("farms", []) if include_farms else None,
                    "total_area_hectares": data.get("total_area_hectares"),
                    "preferences": data.get("preferences", {}) if include_preferences else None,
                    "subscription_tier": data.get("subscription_tier"),
                    "member_since": data.get("member_since"),
                    "interaction_history": data.get("interaction_history", []) if include_interaction_history else None,
                    "last_interaction_date": data.get("last_interaction_date"),
                    "active_recommendations": data.get("active_recommendations", 0),
                },
                metadata={
                    "retrieved_at": datetime.now(UTC).isoformat(),
                    "data_completeness": data.get("data_completeness"),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Farmer API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة المزارع: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    async def log_interaction(
        self,
        farmer_id: str,
        interaction_type: str,
        summary: str,
        channel: str = "ai_chat",
        summary_ar: str | None = None,
        advisory_given: str | None = None,
        farmer_response: str | None = None,
        follow_up_required: bool = False,
        follow_up_date: str | None = None,
        field_id: str | None = None,
        tags: list[str] | None = None,
    ) -> ToolResult:
        """
        Log an interaction with a farmer

        Args:
            farmer_id: Farmer identifier
            interaction_type: Type of interaction
            summary: Brief summary of the interaction
            channel: Communication channel
            summary_ar: Arabic summary
            advisory_given: Advisory provided
            farmer_response: Farmer's response
            follow_up_required: Whether follow-up is needed
            follow_up_date: Follow-up date
            field_id: Related field ID
            tags: Tags for categorization

        Returns:
            ToolResult with interaction log confirmation
        """
        try:
            payload = {
                "farmer_id": farmer_id,
                "interaction_type": interaction_type,
                "summary": summary,
                "channel": channel,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            if summary_ar:
                payload["summary_ar"] = summary_ar
            if advisory_given:
                payload["advisory_given"] = advisory_given
            if farmer_response:
                payload["farmer_response"] = farmer_response
            if follow_up_required:
                payload["follow_up_required"] = follow_up_required
                if follow_up_date:
                    payload["follow_up_date"] = follow_up_date
            if field_id:
                payload["field_id"] = field_id
            if tags:
                payload["tags"] = tags

            response = await self.client.post(f"{self.base_url}/api/farmers/{farmer_id}/interactions", json=payload)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "interaction_id": data.get("interaction_id"),
                    "farmer_id": farmer_id,
                    "logged_at": data.get("logged_at"),
                    "message": "Interaction logged successfully",
                    "message_ar": "تم تسجيل التفاعل بنجاح",
                    "follow_up_scheduled": follow_up_required,
                },
                metadata={
                    "interaction_type": interaction_type,
                    "channel": channel,
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Interaction logging API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة تسجيل التفاعل: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    async def get_recommendations_history(
        self,
        farmer_id: str,
        field_id: str | None = None,
        recommendation_type: str | None = None,
        days: int = 30,
        include_outcomes: bool = True,
        limit: int = 20,
    ) -> ToolResult:
        """
        Get history of recommendations given to a farmer

        Args:
            farmer_id: Farmer identifier
            field_id: Filter by field ID
            recommendation_type: Filter by type
            days: Number of days to look back
            include_outcomes: Include outcome feedback
            limit: Maximum number of records

        Returns:
            ToolResult with recommendations history
        """
        try:
            params = {
                "days": days,
                "include_outcomes": include_outcomes,
                "limit": limit,
            }
            if field_id:
                params["field_id"] = field_id
            if recommendation_type:
                params["recommendation_type"] = recommendation_type

            response = await self.client.get(f"{self.base_url}/api/farmers/{farmer_id}/recommendations", params=params)
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "farmer_id": farmer_id,
                    "total_count": data.get("total_count", 0),
                    "recommendations": data.get("recommendations", []),
                    "summary_stats": {
                        "total_given": data.get("total_given", 0),
                        "implemented": data.get("implemented", 0),
                        "success_rate": data.get("success_rate"),
                        "average_rating": data.get("average_rating"),
                        "by_type": data.get("by_type", {}),
                    },
                    "recent_outcomes": data.get("recent_outcomes", []) if include_outcomes else None,
                },
                metadata={
                    "query_period_days": days,
                    "retrieved_at": datetime.now(UTC).isoformat(),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"Recommendations history API error: {str(e)}",
                error_ar=f"خطأ في واجهة برمجة سجل التوصيات: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_ar=f"خطأ غير متوقع: {str(e)}",
            )

    # ==================== AI Agent Tool Implementations ====================

    async def spawn_agent(
        self,
        agent_type: str,
        context: dict[str, Any] | None = None,
        model: str | None = None,
        timeout_seconds: int = 300,
    ) -> ToolResult:
        """
        Create a specialized AI agent for agricultural tasks

        Args:
            agent_type: Type of specialized agent
            context: Initial context for the agent
            model: AI model to use
            timeout_seconds: Agent timeout

        Returns:
            ToolResult with agent information
        """
        try:
            # Validate agent type
            try:
                agent_type_enum = AgentType(agent_type)
            except ValueError:
                return ToolResult(
                    success=False,
                    error=f"Invalid agent type: {agent_type}",
                    error_ar=f"نوع وكيل غير صالح: {agent_type}",
                )

            # Check agent limit
            async with self._agent_lock:
                if len(self._agents) >= self.config.agent.max_agents:
                    return ToolResult(
                        success=False,
                        error=f"Maximum agent limit reached ({self.config.agent.max_agents})",
                        error_ar=f"تم الوصول إلى الحد الأقصى للوكلاء ({self.config.agent.max_agents})",
                    )

                # Create agent instance
                agent_id = f"agent-{uuid.uuid4().hex[:12]}"
                now = datetime.now(UTC)

                agent = AgentInstance(
                    agent_id=agent_id,
                    agent_type=agent_type_enum,
                    created_at=now,
                    last_active=now,
                    status="active",
                    context=context,
                    query_count=0,
                )

                self._agents[agent_id] = agent

            # Get agent type descriptions
            agent_descriptions = {
                AgentType.CROP_ADVISOR: ("Crop Advisor", "مستشار المحاصيل"),
                AgentType.IRRIGATION_SPECIALIST: ("Irrigation Specialist", "أخصائي الري"),
                AgentType.PEST_MANAGEMENT: ("Pest Management Expert", "خبير إدارة الآفات"),
                AgentType.SOIL_ANALYST: ("Soil Analyst", "محلل التربة"),
                AgentType.WEATHER_ANALYST: ("Weather Analyst", "محلل الطقس"),
                AgentType.FARM_PLANNER: ("Farm Planner", "مخطط المزرعة"),
                AgentType.GENERAL_ASSISTANT: ("General Assistant", "مساعد عام"),
            }

            name_en, name_ar = agent_descriptions.get(agent_type_enum, ("Agent", "وكيل"))

            return ToolResult(
                success=True,
                data={
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "agent_name": name_en,
                    "agent_name_ar": name_ar,
                    "status": "active",
                    "status_ar": "نشط",
                    "model": model or self.config.agent.default_model,
                    "timeout_seconds": timeout_seconds,
                    "context_provided": context is not None,
                    "message": f"{name_en} agent spawned successfully",
                    "message_ar": f"تم إنشاء وكيل {name_ar} بنجاح",
                },
                metadata={
                    "created_at": now.isoformat(),
                    "expires_at": (now + timedelta(seconds=timeout_seconds)).isoformat() if timeout_seconds else None,
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Agent spawn error: {str(e)}",
                error_ar=f"خطأ في إنشاء الوكيل: {str(e)}",
            )

    async def query_agent(
        self,
        agent_id: str,
        query: str,
        additional_context: dict[str, Any] | None = None,
        include_sources: bool = True,
        response_format: str = "text",
    ) -> ToolResult:
        """
        Send a query to a spawned AI agent

        Args:
            agent_id: ID of the spawned agent
            query: Question or task for the agent
            additional_context: Additional context for this query
            include_sources: Include data sources in response
            response_format: Preferred response format

        Returns:
            ToolResult with agent response
        """
        try:
            # Get agent
            async with self._agent_lock:
                agent = self._agents.get(agent_id)
                if not agent:
                    return ToolResult(
                        success=False,
                        error=f"Agent not found: {agent_id}",
                        error_ar=f"لم يتم العثور على الوكيل: {agent_id}",
                    )

                if agent.status != "active":
                    return ToolResult(
                        success=False,
                        error=f"Agent is not active: {agent.status}",
                        error_ar=f"الوكيل غير نشط: {agent.status}",
                    )

                # Update agent activity
                agent.last_active = datetime.now(UTC)
                agent.query_count += 1

            # Build context for the query
            full_context = {
                "agent_type": agent.agent_type.value,
                "original_context": agent.context,
                "additional_context": additional_context,
                "query": query,
                "response_format": response_format,
            }

            # Call the AI service
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/agents/query",
                    json={
                        "agent_id": agent_id,
                        "agent_type": agent.agent_type.value,
                        "query": query,
                        "context": full_context,
                        "include_sources": include_sources,
                    },
                    timeout=self.config.api.long_timeout,
                )
                response.raise_for_status()
                data = response.json()

                return ToolResult(
                    success=True,
                    data={
                        "agent_id": agent_id,
                        "response": data.get("response"),
                        "response_ar": data.get("response_ar"),
                        "sources": data.get("sources", []) if include_sources else None,
                        "confidence_score": data.get("confidence_score"),
                        "follow_up_questions": data.get("follow_up_questions", []),
                        "action_items": data.get("action_items", []),
                    },
                    metadata={
                        "query_count": agent.query_count,
                        "response_time_ms": data.get("response_time_ms"),
                        "model_used": data.get("model_used"),
                    },
                )
            except httpx.HTTPError:
                # Return simulated response if API not available
                return ToolResult(
                    success=True,
                    data={
                        "agent_id": agent_id,
                        "response": f"[{agent.agent_type.value}] Processing query: {query}",
                        "response_ar": f"[{agent.agent_type.value}] معالجة الاستفسار: {query}",
                        "sources": [],
                        "confidence_score": 0.0,
                        "follow_up_questions": [],
                        "action_items": [],
                        "note": "Agent service not available - simulated response",
                    },
                    metadata={
                        "query_count": agent.query_count,
                        "simulated": True,
                    },
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Agent query error: {str(e)}",
                error_ar=f"خطأ في استعلام الوكيل: {str(e)}",
            )

    async def get_agent_status(
        self,
        agent_id: str,
        include_metrics: bool = True,
    ) -> ToolResult:
        """
        Check the status of a spawned AI agent

        Args:
            agent_id: ID of the agent to check
            include_metrics: Include usage metrics

        Returns:
            ToolResult with agent status
        """
        try:
            async with self._agent_lock:
                agent = self._agents.get(agent_id)
                if not agent:
                    return ToolResult(
                        success=False,
                        error=f"Agent not found: {agent_id}",
                        error_ar=f"لم يتم العثور على الوكيل: {agent_id}",
                    )

                # Calculate uptime
                uptime_seconds = (datetime.now(UTC) - agent.created_at).total_seconds()
                idle_seconds = (datetime.now(UTC) - agent.last_active).total_seconds()

                status_translations = {
                    "active": "نشط",
                    "idle": "خامل",
                    "terminated": "منتهي",
                }

                data = {
                    "agent_id": agent_id,
                    "agent_type": agent.agent_type.value,
                    "status": agent.status,
                    "status_ar": status_translations.get(agent.status, agent.status),
                    "created_at": agent.created_at.isoformat(),
                    "last_active": agent.last_active.isoformat(),
                    "has_context": agent.context is not None,
                }

                if include_metrics:
                    data["metrics"] = {
                        "query_count": agent.query_count,
                        "uptime_seconds": uptime_seconds,
                        "idle_seconds": idle_seconds,
                        "queries_per_minute": (agent.query_count / (uptime_seconds / 60) if uptime_seconds > 0 else 0),
                    }

                return ToolResult(
                    success=True,
                    data=data,
                    metadata={
                        "retrieved_at": datetime.now(UTC).isoformat(),
                    },
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Agent status error: {str(e)}",
                error_ar=f"خطأ في حالة الوكيل: {str(e)}",
            )

    async def terminate_agent(self, agent_id: str) -> ToolResult:
        """
        Terminate a spawned AI agent

        Args:
            agent_id: ID of the agent to terminate

        Returns:
            ToolResult confirming termination
        """
        try:
            async with self._agent_lock:
                agent = self._agents.get(agent_id)
                if not agent:
                    return ToolResult(
                        success=False,
                        error=f"Agent not found: {agent_id}",
                        error_ar=f"لم يتم العثور على الوكيل: {agent_id}",
                    )

                # Mark as terminated and remove
                agent.status = "terminated"
                del self._agents[agent_id]

            return ToolResult(
                success=True,
                data={
                    "agent_id": agent_id,
                    "message": "Agent terminated successfully",
                    "message_ar": "تم إنهاء الوكيل بنجاح",
                    "final_query_count": agent.query_count,
                },
                metadata={
                    "terminated_at": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Agent termination error: {str(e)}",
                error_ar=f"خطأ في إنهاء الوكيل: {str(e)}",
            )

    # ==================== Tool Invocation ====================

    async def invoke_tool(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """
        Invoke a tool by name with arguments

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments

        Returns:
            ToolResult from tool execution
        """
        tool_map = {
            # Agricultural tools
            "fetch_field_data": self.fetch_field_data,
            "get_field_data": self.fetch_field_data,  # Alias
            "analyze_crop_health": self.analyze_crop_health,
            "get_weather_forecast": self.get_weather_forecast,
            "irrigation_recommendation": self.irrigation_recommendation,
            "calculate_irrigation": self.irrigation_recommendation,  # Alias
            "fertilizer_recommendation": self.fertilizer_recommendation,
            "get_fertilizer_recommendation": self.fertilizer_recommendation,  # Alias
            # Farmer CRM tools
            "get_farmer_info": self.get_farmer_info,
            "log_interaction": self.log_interaction,
            "get_recommendations_history": self.get_recommendations_history,
            # AI Agent tools
            "spawn_agent": self.spawn_agent,
            "query_agent": self.query_agent,
            "get_agent_status": self.get_agent_status,
            "terminate_agent": self.terminate_agent,
        }

        if tool_name not in tool_map:
            return ToolResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
                error_ar=f"أداة غير معروفة: {tool_name}",
            )

        try:
            return await tool_map[tool_name](**arguments)
        except TypeError as e:
            return ToolResult(
                success=False,
                error=f"Invalid arguments for {tool_name}: {str(e)}",
                error_ar=f"معاملات غير صالحة لـ {tool_name}: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution error: {str(e)}",
                error_ar=f"خطأ في تنفيذ الأداة: {str(e)}",
            )

    def list_active_agents(self) -> list[dict[str, Any]]:
        """List all active agents"""
        return [
            {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type.value,
                "status": agent.status,
                "created_at": agent.created_at.isoformat(),
                "query_count": agent.query_count,
            }
            for agent in self._agents.values()
        ]
