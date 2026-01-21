"""
Agricultural Research Agent
===========================
وكيل البحث الزراعي

Autonomous agent for conducting agricultural research and analysis.
Inspired by Dexter's financial research agent pattern.

Features:
- Task decomposition for agricultural queries
- Multi-source data gathering (satellite, weather, sensors)
- Self-validation of analysis results
- Bilingual output (Arabic/English)

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

from .base import (
    AgentMode,
    AgentStep,
    AgentTool,
    BaseAutonomousAgent,
    ToolResult,
)
from ..llm_provider import LLMProviderManager

logger = structlog.get_logger()


@dataclass
class ResearchQuery:
    """Agricultural research query."""
    query: str
    query_ar: str | None = None
    field_id: str | None = None
    crop_type: str | None = None
    date_range: tuple[datetime, datetime] | None = None
    data_sources: list[str] = field(default_factory=list)


class AgriculturalResearchAgent(BaseAutonomousAgent):
    """
    Autonomous Agricultural Research Agent.
    وكيل البحث الزراعي المستقل

    Like Dexter for finance, but for agriculture:
    - Decomposes research questions into data gathering steps
    - Fetches data from multiple sources (satellite, weather, IoT)
    - Validates findings before generating recommendations
    - Provides bilingual output for farmers

    Example:
        agent = AgriculturalResearchAgent()

        result = await agent.run(
            task="ما هي حالة محصول القمح في الحقل F003؟ وما التوصيات؟",
            context={"field_id": "F003", "crop_type": "wheat"}
        )

        print(result["summary"])
    """

    # Research-specific constants
    CONFIDENCE_THRESHOLD = 0.7
    MIN_DATA_SOURCES = 2

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        mode: AgentMode = AgentMode.EXECUTE,
    ):
        super().__init__(
            agent_id="agri-research-agent",
            name="Agricultural Research Agent",
            name_ar="وكيل البحث الزراعي",
            description="Autonomous agent for agricultural research and crop analysis",
            description_ar="وكيل مستقل للبحث الزراعي وتحليل المحاصيل",
            mode=mode,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
        )

        # Research state
        self.current_research: ResearchQuery | None = None
        self.gathered_data: dict[str, Any] = {}
        self.analysis_results: dict[str, Any] = {}

    def _register_default_tools(self) -> None:
        """Register agricultural research tools."""

        # Tool 1: Fetch Satellite Data (NDVI, LAI)
        self.register_tool(AgentTool(
            name="fetch_satellite_data",
            name_ar="جلب بيانات الأقمار الصناعية",
            description="Fetch satellite imagery and vegetation indices (NDVI, LAI) for a field",
            description_ar="جلب صور الأقمار الصناعية ومؤشرات الغطاء النباتي للحقل",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string", "description": "Field identifier"},
                    "indices": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["NDVI", "LAI", "NDWI", "EVI"]},
                        "description": "Vegetation indices to calculate"
                    },
                    "date_from": {"type": "string", "format": "date"},
                    "date_to": {"type": "string", "format": "date"},
                },
                "required": ["field_id", "indices"]
            },
            handler=self._fetch_satellite_data,
            tags=["satellite", "ndvi", "remote-sensing"],
        ))

        # Tool 2: Fetch Weather Data
        self.register_tool(AgentTool(
            name="fetch_weather_data",
            name_ar="جلب بيانات الطقس",
            description="Fetch historical and forecast weather data for a location",
            description_ar="جلب بيانات الطقس التاريخية والمتوقعة للموقع",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "include_forecast": {"type": "boolean", "default": True},
                    "days_history": {"type": "integer", "default": 30},
                },
                "required": ["field_id"]
            },
            handler=self._fetch_weather_data,
            tags=["weather", "forecast"],
        ))

        # Tool 3: Fetch IoT Sensor Data
        self.register_tool(AgentTool(
            name="fetch_sensor_data",
            name_ar="جلب بيانات المستشعرات",
            description="Fetch IoT sensor data (soil moisture, temperature, etc.)",
            description_ar="جلب بيانات مستشعرات إنترنت الأشياء (رطوبة التربة، درجة الحرارة، إلخ)",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "sensor_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Types: soil_moisture, soil_temp, air_temp, humidity"
                    },
                    "hours": {"type": "integer", "default": 24},
                },
                "required": ["field_id"]
            },
            handler=self._fetch_sensor_data,
            tags=["iot", "sensors"],
        ))

        # Tool 4: Analyze Crop Health
        self.register_tool(AgentTool(
            name="analyze_crop_health",
            name_ar="تحليل صحة المحصول",
            description="Analyze crop health based on gathered data",
            description_ar="تحليل صحة المحصول بناءً على البيانات المجمعة",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "crop_type": {"type": "string"},
                    "ndvi_data": {"type": "object"},
                    "weather_data": {"type": "object"},
                    "sensor_data": {"type": "object"},
                },
                "required": ["field_id", "crop_type"]
            },
            handler=self._analyze_crop_health,
            tags=["analysis", "health"],
        ))

        # Tool 5: Generate Recommendations
        self.register_tool(AgentTool(
            name="generate_recommendations",
            name_ar="توليد التوصيات",
            description="Generate actionable recommendations based on analysis",
            description_ar="توليد توصيات قابلة للتنفيذ بناءً على التحليل",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "crop_type": {"type": "string"},
                    "health_analysis": {"type": "object"},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                },
                "required": ["field_id", "health_analysis"]
            },
            handler=self._generate_recommendations,
            tags=["advisory", "recommendations"],
        ))

        # Tool 6: Search Agricultural Knowledge Base
        self.register_tool(AgentTool(
            name="search_knowledge_base",
            name_ar="البحث في قاعدة المعرفة",
            description="Search agricultural knowledge base for best practices",
            description_ar="البحث في قاعدة المعرفة الزراعية عن أفضل الممارسات",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "crop_type": {"type": "string"},
                    "topic": {
                        "type": "string",
                        "enum": ["irrigation", "fertilizer", "pest_control", "disease", "harvest"]
                    },
                },
                "required": ["query"]
            },
            handler=self._search_knowledge_base,
            tags=["knowledge", "search"],
        ))

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """
        Decompose research task into structured steps.
        تقسيم مهمة البحث إلى خطوات منظمة

        Uses LLM to understand the task and create a research plan.
        """
        field_id = context.get("field_id")
        crop_type = context.get("crop_type", "unknown")

        # Use LLM to analyze the task and determine required steps
        system_prompt = """أنت وكيل بحث زراعي متخصص. قم بتحليل السؤال وحدد خطوات البحث المطلوبة.

You are an agricultural research agent. Analyze the question and determine required research steps.

Available tools:
1. fetch_satellite_data - Get NDVI, LAI data
2. fetch_weather_data - Get weather history and forecast
3. fetch_sensor_data - Get IoT sensor readings
4. analyze_crop_health - Analyze based on gathered data
5. generate_recommendations - Create actionable advice
6. search_knowledge_base - Search best practices

Return a JSON array of steps with: description, description_ar, tool_name, tool_input"""

        prompt = f"""Task: {task}
Field ID: {field_id}
Crop Type: {crop_type}

Analyze this agricultural research question and create a step-by-step research plan.
Output valid JSON array only."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )

            # Parse LLM response (simplified - should use JSON parsing)
            steps = self._parse_research_plan(response.text, field_id, crop_type)

            if not steps:
                # Fallback to default research workflow
                steps = self._create_default_research_steps(field_id, crop_type)

            return steps

        except Exception as e:
            logger.warning("llm_decomposition_failed", error=str(e))
            return self._create_default_research_steps(field_id, crop_type)

    def _parse_research_plan(
        self,
        llm_response: str,
        field_id: str | None,
        crop_type: str,
    ) -> list[AgentStep]:
        """Parse LLM response into steps."""
        import json

        try:
            # Try to extract JSON from response
            start = llm_response.find("[")
            end = llm_response.rfind("]") + 1

            if start >= 0 and end > start:
                json_str = llm_response[start:end]
                plan_data = json.loads(json_str)

                steps = []
                for i, item in enumerate(plan_data):
                    steps.append(AgentStep(
                        step_id=str(uuid.uuid4()),
                        step_number=i + 1,
                        description=item.get("description", f"Step {i+1}"),
                        description_ar=item.get("description_ar", f"الخطوة {i+1}"),
                        tool_name=item.get("tool_name"),
                        tool_input=item.get("tool_input", {}),
                    ))

                return steps

        except json.JSONDecodeError:
            pass

        return []

    def _create_default_research_steps(
        self,
        field_id: str | None,
        crop_type: str,
    ) -> list[AgentStep]:
        """Create default research workflow steps."""
        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Fetch satellite imagery and NDVI data",
                description_ar="جلب صور الأقمار الصناعية وبيانات NDVI",
                tool_name="fetch_satellite_data",
                tool_input={
                    "field_id": field_id,
                    "indices": ["NDVI", "LAI"],
                },
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Fetch weather data and forecast",
                description_ar="جلب بيانات الطقس والتوقعات",
                tool_name="fetch_weather_data",
                tool_input={
                    "field_id": field_id,
                    "include_forecast": True,
                    "days_history": 14,
                },
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=3,
                description="Fetch IoT sensor data",
                description_ar="جلب بيانات مستشعرات إنترنت الأشياء",
                tool_name="fetch_sensor_data",
                tool_input={
                    "field_id": field_id,
                    "sensor_types": ["soil_moisture", "soil_temp"],
                    "hours": 72,
                },
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=4,
                description="Analyze crop health based on gathered data",
                description_ar="تحليل صحة المحصول بناءً على البيانات المجمعة",
                tool_name="analyze_crop_health",
                tool_input={
                    "field_id": field_id,
                    "crop_type": crop_type,
                },
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=5,
                description="Generate actionable recommendations",
                description_ar="توليد توصيات قابلة للتنفيذ",
                tool_name="generate_recommendations",
                tool_input={
                    "field_id": field_id,
                    "crop_type": crop_type,
                },
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """
        Validate step result (self-assessment).
        التحقق من نتيجة الخطوة (التقييم الذاتي)

        Inspired by Dexter's self-validation pattern.
        """
        if not result.success:
            return False, "Tool execution failed"

        tool_name = step.tool_name

        # Validation rules per tool type
        if tool_name == "fetch_satellite_data":
            # Check if we got valid NDVI data
            data = result.result or {}
            ndvi_values = data.get("ndvi_values", [])

            if not ndvi_values:
                return False, "No NDVI data returned"

            # Check for reasonable NDVI range (-1 to 1)
            if any(v < -1 or v > 1 for v in ndvi_values if v is not None):
                return False, "NDVI values out of valid range"

            # Store for later analysis
            self.gathered_data["satellite"] = data
            return True, None

        elif tool_name == "fetch_weather_data":
            data = result.result or {}

            if not data.get("temperature") and not data.get("forecast"):
                return False, "No weather data returned"

            self.gathered_data["weather"] = data
            return True, None

        elif tool_name == "fetch_sensor_data":
            data = result.result or {}

            # Sensors may be offline - that's OK but note it
            if not data.get("readings"):
                return True, "No active sensors found - using alternative data"

            self.gathered_data["sensors"] = data
            return True, None

        elif tool_name == "analyze_crop_health":
            analysis = result.result or {}

            # Check confidence threshold
            confidence = analysis.get("confidence", 0)
            if confidence < self.CONFIDENCE_THRESHOLD:
                return False, f"Analysis confidence too low: {confidence:.0%}"

            self.analysis_results["health"] = analysis
            return True, None

        elif tool_name == "generate_recommendations":
            recommendations = result.result or {}

            if not recommendations.get("actions"):
                return False, "No recommendations generated"

            return True, None

        return True, None

    # Tool handlers (to be connected to actual services)
    async def _fetch_satellite_data(
        self,
        field_id: str,
        indices: list[str],
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Fetch satellite data from vegetation-analysis-service."""
        # This would call the actual service in production
        # For now, return simulated data

        logger.info(
            "fetching_satellite_data",
            field_id=field_id,
            indices=indices,
        )

        # Simulated response (connect to vegetation-analysis-service)
        return {
            "field_id": field_id,
            "timestamp": datetime.utcnow().isoformat(),
            "ndvi_values": [0.68, 0.71, 0.72, 0.69, 0.70],
            "ndvi_mean": 0.70,
            "ndvi_trend": "stable",
            "lai_values": [2.8, 2.9, 3.0, 2.9, 2.9],
            "lai_mean": 2.9,
            "cloud_cover_pct": 15,
            "data_quality": "good",
        }

    async def _fetch_weather_data(
        self,
        field_id: str,
        latitude: float | None = None,
        longitude: float | None = None,
        include_forecast: bool = True,
        days_history: int = 30,
    ) -> dict[str, Any]:
        """Fetch weather data from weather-service."""
        logger.info("fetching_weather_data", field_id=field_id)

        return {
            "field_id": field_id,
            "temperature": {"min": 8, "max": 22, "avg": 15},
            "humidity": {"min": 45, "max": 75, "avg": 60},
            "precipitation_mm": 12,
            "wind_speed_kmh": 15,
            "forecast": [
                {"date": "2026-01-22", "temp_max": 20, "rain_prob": 10},
                {"date": "2026-01-23", "temp_max": 18, "rain_prob": 30},
                {"date": "2026-01-24", "temp_max": 16, "rain_prob": 60},
            ],
            "growing_degree_days": 120,
        }

    async def _fetch_sensor_data(
        self,
        field_id: str,
        sensor_types: list[str] | None = None,
        hours: int = 24,
    ) -> dict[str, Any]:
        """Fetch IoT sensor data from iot-service."""
        logger.info("fetching_sensor_data", field_id=field_id)

        return {
            "field_id": field_id,
            "timestamp": datetime.utcnow().isoformat(),
            "readings": {
                "soil_moisture": {
                    "value": 38,
                    "unit": "%",
                    "status": "adequate",
                    "threshold_low": 30,
                    "threshold_high": 60,
                },
                "soil_temperature": {
                    "value": 14,
                    "unit": "°C",
                    "status": "optimal",
                },
                "ec": {
                    "value": 1.8,
                    "unit": "dS/m",
                    "status": "normal",
                },
            },
            "sensor_health": "all_online",
        }

    async def _analyze_crop_health(
        self,
        field_id: str,
        crop_type: str,
        ndvi_data: dict[str, Any] | None = None,
        weather_data: dict[str, Any] | None = None,
        sensor_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze crop health using gathered data."""
        logger.info("analyzing_crop_health", field_id=field_id, crop_type=crop_type)

        # Use gathered data if not provided
        ndvi_data = ndvi_data or self.gathered_data.get("satellite", {})
        weather_data = weather_data or self.gathered_data.get("weather", {})
        sensor_data = sensor_data or self.gathered_data.get("sensors", {})

        # Calculate health score (simplified)
        ndvi_score = min(100, (ndvi_data.get("ndvi_mean", 0.5) / 0.8) * 100)
        moisture_reading = sensor_data.get("readings", {}).get("soil_moisture", {})
        moisture_score = 100 if moisture_reading.get("status") == "adequate" else 70

        health_score = (ndvi_score * 0.6 + moisture_score * 0.4)

        # Determine status
        if health_score >= 80:
            status = "healthy"
            status_ar = "صحي"
        elif health_score >= 60:
            status = "moderate"
            status_ar = "متوسط"
        else:
            status = "stressed"
            status_ar = "مجهد"

        return {
            "field_id": field_id,
            "crop_type": crop_type,
            "health_score": round(health_score, 1),
            "status": status,
            "status_ar": status_ar,
            "confidence": 0.85,
            "indicators": {
                "vegetation": {
                    "ndvi": ndvi_data.get("ndvi_mean"),
                    "trend": ndvi_data.get("ndvi_trend"),
                    "score": round(ndvi_score, 1),
                },
                "water": {
                    "soil_moisture": moisture_reading.get("value"),
                    "status": moisture_reading.get("status"),
                    "score": moisture_score,
                },
            },
            "issues_detected": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _generate_recommendations(
        self,
        field_id: str,
        crop_type: str | None = None,
        health_analysis: dict[str, Any] | None = None,
        priority: str = "medium",
    ) -> dict[str, Any]:
        """Generate recommendations based on analysis."""
        logger.info("generating_recommendations", field_id=field_id)

        health_analysis = health_analysis or self.analysis_results.get("health", {})
        health_score = health_analysis.get("health_score", 70)

        actions = []

        # Generate recommendations based on health indicators
        if health_score < 70:
            actions.append({
                "type": "irrigation",
                "priority": "high",
                "action": "Increase irrigation frequency",
                "action_ar": "زيادة تكرار الري",
                "details": "Apply 25mm of water within 48 hours",
                "details_ar": "قم بتطبيق 25 ملم من الماء خلال 48 ساعة",
            })

        # Weather-based recommendations
        weather = self.gathered_data.get("weather", {})
        forecast = weather.get("forecast", [])

        for day in forecast:
            if day.get("rain_prob", 0) > 50:
                actions.append({
                    "type": "irrigation",
                    "priority": "low",
                    "action": "Delay irrigation due to expected rain",
                    "action_ar": "تأجيل الري بسبب توقع هطول الأمطار",
                    "details": f"Rain expected on {day.get('date')}",
                    "details_ar": f"متوقع هطول أمطار في {day.get('date')}",
                })
                break

        return {
            "field_id": field_id,
            "crop_type": crop_type,
            "generated_at": datetime.utcnow().isoformat(),
            "actions": actions,
            "summary": f"Field health score: {health_score}%. {len(actions)} recommendations generated.",
            "summary_ar": f"درجة صحة الحقل: {health_score}%. تم توليد {len(actions)} توصيات.",
        }

    async def _search_knowledge_base(
        self,
        query: str,
        crop_type: str | None = None,
        topic: str | None = None,
    ) -> dict[str, Any]:
        """Search agricultural knowledge base."""
        logger.info("searching_knowledge_base", query=query[:50])

        # This would use embeddings and vector search in production
        return {
            "query": query,
            "results": [
                {
                    "title": "Wheat Irrigation Best Practices",
                    "title_ar": "أفضل ممارسات ري القمح",
                    "content": "Wheat requires 450-650mm of water throughout the growing season...",
                    "relevance_score": 0.92,
                },
            ],
            "total_results": 1,
        }

    def _generate_summary(self, outputs: list[dict[str, Any]]) -> str:
        """Generate research summary."""
        health = self.analysis_results.get("health", {})
        health_score = health.get("health_score", "N/A")
        status = health.get("status", "unknown")
        status_ar = health.get("status_ar", "غير معروف")

        return f"""
## Research Summary | ملخص البحث

**Field Health Score | درجة صحة الحقل:** {health_score}%
**Status | الحالة:** {status} | {status_ar}

**Data Sources Used | مصادر البيانات المستخدمة:**
- Satellite imagery (NDVI) | صور الأقمار الصناعية
- Weather data | بيانات الطقس
- IoT sensors | مستشعرات إنترنت الأشياء

**Steps Completed | الخطوات المكتملة:** {len(outputs)}
"""
