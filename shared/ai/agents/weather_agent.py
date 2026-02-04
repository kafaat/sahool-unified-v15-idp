"""
Weather Sub-Agent
==================
وكيل فرعي للطقس

Specialized sub-agent for weather-based agricultural decisions.
Provides weather forecasting, climate risk assessment, and
weather-dependent recommendations.

Features:
- Weather forecast integration
- Climate risk assessment
- Frost/heat alerts
- Rain probability analysis
- Optimal timing for field operations
- Weather-dependent irrigation adjustments

Author: SAHOOL Platform Team
Created: January 2026
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC, timezone
from typing import Any

import structlog

from .base import (
    AgentMode,
    AgentStep,
    AgentTool,
    AgentCapability,
    BaseAutonomousAgent,
    CollaborationRole,
    ToolResult,
)
from ..llm_provider import LLMProviderManager

logger = structlog.get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class WeatherCondition:
    """
    Current or forecasted weather condition.
    حالة الطقس الحالية أو المتوقعة
    """
    timestamp: datetime
    temperature_c: float
    temperature_min_c: float
    temperature_max_c: float
    humidity_percent: float
    wind_speed_kmh: float
    wind_direction: str
    precipitation_mm: float
    cloud_cover_percent: float
    uv_index: float
    condition: str  # sunny, cloudy, rainy, etc.
    condition_ar: str


@dataclass
class WeatherAlert:
    """
    Weather alert/warning.
    تحذير/إنذار طقس
    """
    alert_id: str
    alert_type: str  # frost, heat, storm, rain, wind
    severity: str  # low, medium, high, critical
    severity_ar: str
    title: str
    title_ar: str
    description: str
    description_ar: str
    start_time: datetime
    end_time: datetime
    affected_operations: list[str]
    recommendations: list[str]
    recommendations_ar: list[str]


@dataclass
class WeatherForecast:
    """
    Multi-day weather forecast.
    توقعات الطقس لعدة أيام
    """
    location: str
    location_ar: str
    generated_at: datetime
    daily_forecasts: list[WeatherCondition]
    alerts: list[WeatherAlert]
    confidence: float
    source: str


@dataclass
class ClimateRiskAssessment:
    """
    Climate risk assessment for agricultural planning.
    تقييم مخاطر المناخ للتخطيط الزراعي
    """
    assessment_id: str
    period: str  # weekly, monthly, seasonal
    frost_risk: float  # 0-1
    heat_stress_risk: float
    drought_risk: float
    flood_risk: float
    storm_risk: float
    overall_risk: str  # low, medium, high
    overall_risk_ar: str
    recommendations: list[dict[str, str]]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ============================================================================
# WEATHER SUB-AGENT
# ============================================================================


class WeatherSubAgent(BaseAutonomousAgent):
    """
    Specialized sub-agent for weather-based agricultural decisions.
    وكيل فرعي متخصص للقرارات الزراعية المبنية على الطقس

    Provides:
    - Weather forecasting and analysis
    - Climate risk assessment
    - Optimal timing for field operations
    - Weather alerts and warnings
    - Integration with irrigation/spray scheduling

    Example:
        weather_agent = WeatherSubAgent(tenant_id="farm_001")

        # Get weather forecast
        forecast = await weather_agent.get_forecast(
            location={"lat": 24.7136, "lon": 46.6753},
            days=7
        )

        # Assess climate risks
        risks = await weather_agent.assess_climate_risks(
            location={"lat": 24.7136, "lon": 46.6753},
            period="weekly"
        )

        # Get optimal spray window
        window = await weather_agent.get_optimal_spray_window(
            field_id="F003",
            pesticide="fungicide"
        )
    """

    # Weather thresholds for agricultural operations
    FROST_THRESHOLD_C = 4.0
    HEAT_STRESS_THRESHOLD_C = 35.0
    SPRAY_WIND_MAX_KMH = 15.0
    SPRAY_RAIN_THRESHOLD_MM = 2.0
    IRRIGATION_RAIN_THRESHOLD_MM = 10.0

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        parent_agent: BaseAutonomousAgent | None = None,
        weather_api_url: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize Weather Sub-Agent.
        تهيئة وكيل الطقس الفرعي

        Args:
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager
            parent_agent: Parent agent for coordination
            weather_api_url: External weather API URL (optional)
        """
        super().__init__(
            agent_id=kwargs.get("agent_id", "weather-sub-agent"),
            name=kwargs.get("name", "Weather Specialist"),
            name_ar=kwargs.get("name_ar", "متخصص الطقس"),
            description="Specialized agent for weather-based agricultural decisions",
            description_ar="وكيل متخصص للقرارات الزراعية المبنية على الطقس",
            mode=AgentMode.EXECUTE,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            parent_agent=parent_agent,
            collaboration_role=CollaborationRole.SPECIALIST,
        )

        self.weather_api_url = weather_api_url
        self._forecast_cache: dict[str, WeatherForecast] = {}

    def _register_default_tools(self) -> None:
        """Register weather-specific tools."""

        # Tool 1: Get Weather Forecast
        self.register_tool(AgentTool(
            name="get_weather_forecast",
            name_ar="الحصول على توقعات الطقس",
            description="Get weather forecast for a location",
            description_ar="الحصول على توقعات الطقس لموقع معين",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"},
                        },
                    },
                    "days": {"type": "integer", "default": 7},
                },
                "required": ["location"]
            },
            handler=self._get_weather_forecast,
            tags=["weather", "forecast"],
        ))

        # Tool 2: Assess Climate Risks
        self.register_tool(AgentTool(
            name="assess_climate_risks",
            name_ar="تقييم مخاطر المناخ",
            description="Assess climate risks for agricultural planning",
            description_ar="تقييم مخاطر المناخ للتخطيط الزراعي",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "object"},
                    "period": {
                        "type": "string",
                        "enum": ["weekly", "monthly", "seasonal"],
                    },
                    "crop_type": {"type": "string"},
                },
                "required": ["location"]
            },
            handler=self._assess_climate_risks,
            tags=["weather", "risk"],
        ))

        # Tool 3: Get Optimal Spray Window
        self.register_tool(AgentTool(
            name="get_optimal_spray_window",
            name_ar="الحصول على نافذة الرش المثلى",
            description="Find optimal time window for pesticide/herbicide application",
            description_ar="إيجاد النافذة الزمنية المثلى لتطبيق المبيدات",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "application_type": {
                        "type": "string",
                        "enum": ["pesticide", "herbicide", "fungicide", "foliar"],
                    },
                    "days_ahead": {"type": "integer", "default": 5},
                },
                "required": ["field_id"]
            },
            handler=self._get_optimal_spray_window,
            tags=["weather", "spray", "timing"],
        ))

        # Tool 4: Check Frost Risk
        self.register_tool(AgentTool(
            name="check_frost_risk",
            name_ar="فحص خطر الصقيع",
            description="Check frost risk for upcoming days",
            description_ar="فحص خطر الصقيع للأيام القادمة",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "object"},
                    "days_ahead": {"type": "integer", "default": 3},
                },
                "required": ["location"]
            },
            handler=self._check_frost_risk,
            tags=["weather", "frost", "alert"],
        ))

        # Tool 5: Get Irrigation Weather Adjustment
        self.register_tool(AgentTool(
            name="get_irrigation_weather_adjustment",
            name_ar="الحصول على تعديل الري حسب الطقس",
            description="Calculate irrigation adjustment based on weather forecast",
            description_ar="حساب تعديل الري بناءً على توقعات الطقس",
            input_schema={
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "planned_amount_mm": {"type": "number"},
                    "planned_date": {"type": "string"},
                },
                "required": ["field_id", "planned_amount_mm"]
            },
            handler=self._get_irrigation_weather_adjustment,
            tags=["weather", "irrigation"],
        ))

        # Tool 6: Get Heat Stress Alert
        self.register_tool(AgentTool(
            name="get_heat_stress_alert",
            name_ar="الحصول على إنذار الإجهاد الحراري",
            description="Check for heat stress conditions affecting crops",
            description_ar="فحص ظروف الإجهاد الحراري المؤثرة على المحاصيل",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "object"},
                    "crop_type": {"type": "string"},
                },
                "required": ["location"]
            },
            handler=self._get_heat_stress_alert,
            tags=["weather", "heat", "alert"],
        ))

    def _register_default_capabilities(self) -> None:
        """Register weather capabilities."""
        self.register_capability(AgentCapability(
            name="weather_forecasting",
            name_ar="توقعات الطقس",
            description="Provide weather forecasts and analysis",
            description_ar="تقديم توقعات وتحليلات الطقس",
            domains=["weather", "climate", "forecasting"],
            skill_level=0.9,
        ))

        self.register_capability(AgentCapability(
            name="climate_risk_assessment",
            name_ar="تقييم مخاطر المناخ",
            description="Assess climate-related agricultural risks",
            description_ar="تقييم المخاطر الزراعية المتعلقة بالمناخ",
            domains=["weather", "risk", "planning"],
            skill_level=0.85,
        ))

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """Decompose weather-related task."""
        location = context.get("location", {"lat": 24.7136, "lon": 46.6753})
        field_id = context.get("field_id")

        task_lower = task.lower()

        # Detect task type
        if any(w in task_lower for w in ["forecast", "توقعات", "weather", "طقس"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Get weather forecast",
                    description_ar="الحصول على توقعات الطقس",
                    tool_name="get_weather_forecast",
                    tool_input={"location": location, "days": 7},
                ),
            ]

        elif any(w in task_lower for w in ["risk", "مخاطر", "climate", "مناخ"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Assess climate risks",
                    description_ar="تقييم مخاطر المناخ",
                    tool_name="assess_climate_risks",
                    tool_input={"location": location, "period": "weekly"},
                ),
            ]

        elif any(w in task_lower for w in ["spray", "رش", "pesticide", "مبيد"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Get optimal spray window",
                    description_ar="الحصول على نافذة الرش المثلى",
                    tool_name="get_optimal_spray_window",
                    tool_input={"field_id": field_id or "default"},
                ),
            ]

        elif any(w in task_lower for w in ["frost", "صقيع", "freeze", "تجمد"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Check frost risk",
                    description_ar="فحص خطر الصقيع",
                    tool_name="check_frost_risk",
                    tool_input={"location": location},
                ),
            ]

        # Default: comprehensive weather analysis
        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Get weather forecast",
                description_ar="الحصول على توقعات الطقس",
                tool_name="get_weather_forecast",
                tool_input={"location": location, "days": 7},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Assess climate risks",
                description_ar="تقييم مخاطر المناخ",
                tool_name="assess_climate_risks",
                tool_input={"location": location, "period": "weekly"},
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate weather step result."""
        if not result.success:
            return False, f"Tool failed: {result.error}"

        data = result.result or {}

        # Validate forecast has required data
        if step.tool_name == "get_weather_forecast":
            if not data.get("daily_forecasts"):
                return False, "No forecast data received"

        return True, None

    # ========================================================================
    # TOOL HANDLERS
    # ========================================================================

    async def _get_weather_forecast(
        self,
        location: dict[str, float],
        days: int = 7,
    ) -> dict[str, Any]:
        """Get weather forecast for location."""
        logger.info("getting_weather_forecast", location=location, days=days)

        # Simulated forecast data (in production, would call external API)
        lat = location.get("lat", 24.7136)
        lon = location.get("lon", 46.6753)

        # Generate mock forecast
        daily_forecasts = []
        base_temp = 18 if 1 <= datetime.now().month <= 3 else 32

        for i in range(days):
            daily_forecasts.append({
                "day": i + 1,
                "date": (datetime.now(UTC)).isoformat(),
                "temperature_c": base_temp + (i % 3) - 1,
                "temperature_min_c": base_temp - 5,
                "temperature_max_c": base_temp + 5,
                "humidity_percent": 55 + (i % 20),
                "wind_speed_kmh": 8 + (i % 10),
                "wind_direction": ["N", "NE", "E", "SE"][i % 4],
                "precipitation_mm": 0 if i % 5 != 0 else 5,
                "rain_probability_percent": 10 if i % 5 != 0 else 40,
                "cloud_cover_percent": 20 + (i % 30),
                "uv_index": 6 + (i % 4),
                "condition": "sunny" if i % 3 != 2 else "partly_cloudy",
                "condition_ar": "مشمس" if i % 3 != 2 else "غائم جزئياً",
            })

        alerts = []
        if base_temp > 30:
            alerts.append({
                "alert_type": "heat",
                "severity": "medium",
                "title": "Heat Advisory",
                "title_ar": "تحذير من الحرارة",
                "description": f"High temperatures expected ({base_temp}°C+)",
                "description_ar": f"متوقع درجات حرارة مرتفعة ({base_temp}°م+)",
            })

        return {
            "location": {"lat": lat, "lon": lon},
            "location_name": "Riyadh Region",
            "location_name_ar": "منطقة الرياض",
            "generated_at": datetime.now(UTC).isoformat(),
            "daily_forecasts": daily_forecasts,
            "alerts": alerts,
            "confidence": 0.85,
            "source": "SAHOOL Weather Service",
        }

    async def _assess_climate_risks(
        self,
        location: dict[str, float],
        period: str = "weekly",
        crop_type: str | None = None,
    ) -> dict[str, Any]:
        """Assess climate risks for agricultural planning."""
        logger.info("assessing_climate_risks", location=location, period=period)

        # Get current month for seasonal adjustment
        month = datetime.now().month

        # Calculate risk levels based on season
        frost_risk = 0.3 if month in [12, 1, 2] else 0.05
        heat_risk = 0.6 if month in [6, 7, 8] else 0.2
        drought_risk = 0.4 if month in [5, 6, 7, 8, 9] else 0.15

        # Overall risk
        max_risk = max(frost_risk, heat_risk, drought_risk)
        overall_risk = "low" if max_risk < 0.3 else "medium" if max_risk < 0.6 else "high"
        overall_risk_ar = "منخفض" if max_risk < 0.3 else "متوسط" if max_risk < 0.6 else "مرتفع"

        recommendations = []

        if frost_risk > 0.2:
            recommendations.append({
                "risk": "frost",
                "action": "Consider frost protection for sensitive crops",
                "action_ar": "النظر في حماية المحاصيل الحساسة من الصقيع",
            })

        if heat_risk > 0.4:
            recommendations.append({
                "risk": "heat_stress",
                "action": "Increase irrigation frequency, apply mulch",
                "action_ar": "زيادة تكرار الري، تطبيق التغطية",
            })

        if drought_risk > 0.3:
            recommendations.append({
                "risk": "drought",
                "action": "Ensure water reserves, optimize irrigation efficiency",
                "action_ar": "ضمان احتياطيات المياه، تحسين كفاءة الري",
            })

        return {
            "assessment_id": str(uuid.uuid4()),
            "location": location,
            "period": period,
            "crop_type": crop_type,
            "risks": {
                "frost": {"level": frost_risk, "status": "low" if frost_risk < 0.3 else "elevated"},
                "heat_stress": {"level": heat_risk, "status": "elevated" if heat_risk > 0.4 else "low"},
                "drought": {"level": drought_risk, "status": "moderate" if drought_risk > 0.3 else "low"},
                "flood": {"level": 0.1, "status": "low"},
                "storm": {"level": 0.15, "status": "low"},
            },
            "overall_risk": overall_risk,
            "overall_risk_ar": overall_risk_ar,
            "recommendations": recommendations,
            "created_at": datetime.now(UTC).isoformat(),
        }

    async def _get_optimal_spray_window(
        self,
        field_id: str,
        application_type: str = "pesticide",
        days_ahead: int = 5,
    ) -> dict[str, Any]:
        """Find optimal spray window based on weather."""
        logger.info("finding_spray_window", field_id=field_id, type=application_type)

        # Get forecast first
        forecast = await self._get_weather_forecast(
            location={"lat": 24.7136, "lon": 46.6753},
            days=days_ahead
        )

        suitable_windows = []

        for day_forecast in forecast.get("daily_forecasts", []):
            wind = day_forecast.get("wind_speed_kmh", 0)
            rain = day_forecast.get("precipitation_mm", 0)
            rain_prob = day_forecast.get("rain_probability_percent", 0)

            # Check if conditions are suitable
            if wind <= self.SPRAY_WIND_MAX_KMH and rain < self.SPRAY_RAIN_THRESHOLD_MM and rain_prob < 30:
                suitable_windows.append({
                    "day": day_forecast.get("day"),
                    "date": day_forecast.get("date"),
                    "suitability": "excellent" if wind < 10 and rain_prob < 20 else "good",
                    "suitability_ar": "ممتاز" if wind < 10 and rain_prob < 20 else "جيد",
                    "optimal_time": "06:00-09:00",
                    "optimal_time_ar": "06:00-09:00 صباحاً",
                    "wind_speed_kmh": wind,
                    "rain_probability": rain_prob,
                })

        return {
            "field_id": field_id,
            "application_type": application_type,
            "suitable_windows": suitable_windows,
            "best_window": suitable_windows[0] if suitable_windows else None,
            "recommendation": "Apply early morning when wind is calm and no rain expected" if suitable_windows else "No suitable window found, consider postponing",
            "recommendation_ar": "الرش في الصباح الباكر عندما يكون الهواء هادئاً ولا يتوقع مطر" if suitable_windows else "لم يتم العثور على نافذة مناسبة، يُنصح بالتأجيل",
        }

    async def _check_frost_risk(
        self,
        location: dict[str, float],
        days_ahead: int = 3,
    ) -> dict[str, Any]:
        """Check frost risk for upcoming days."""
        logger.info("checking_frost_risk", location=location)

        forecast = await self._get_weather_forecast(location, days=days_ahead)

        frost_nights = []
        for day in forecast.get("daily_forecasts", []):
            min_temp = day.get("temperature_min_c", 10)
            if min_temp <= self.FROST_THRESHOLD_C:
                frost_nights.append({
                    "day": day.get("day"),
                    "date": day.get("date"),
                    "min_temperature_c": min_temp,
                    "severity": "critical" if min_temp <= 0 else "warning",
                    "severity_ar": "حرج" if min_temp <= 0 else "تحذير",
                })

        has_frost_risk = len(frost_nights) > 0

        return {
            "location": location,
            "days_checked": days_ahead,
            "frost_risk": has_frost_risk,
            "frost_risk_level": "high" if len(frost_nights) >= 2 else "medium" if frost_nights else "low",
            "frost_risk_level_ar": "مرتفع" if len(frost_nights) >= 2 else "متوسط" if frost_nights else "منخفض",
            "frost_nights": frost_nights,
            "protective_measures": [
                {"action": "Cover sensitive crops", "action_ar": "تغطية المحاصيل الحساسة"},
                {"action": "Apply irrigation before frost", "action_ar": "الري قبل الصقيع"},
                {"action": "Use wind machines if available", "action_ar": "استخدام مراوح الهواء إن وجدت"},
            ] if has_frost_risk else [],
        }

    async def _get_irrigation_weather_adjustment(
        self,
        field_id: str,
        planned_amount_mm: float,
        planned_date: str | None = None,
    ) -> dict[str, Any]:
        """Calculate irrigation adjustment based on weather."""
        logger.info("calculating_irrigation_adjustment", field_id=field_id)

        forecast = await self._get_weather_forecast(
            location={"lat": 24.7136, "lon": 46.6753},
            days=3
        )

        # Calculate expected rainfall
        total_expected_rain = sum(
            day.get("precipitation_mm", 0)
            for day in forecast.get("daily_forecasts", [])
        )

        # Calculate adjustment
        adjustment = 0
        if total_expected_rain >= self.IRRIGATION_RAIN_THRESHOLD_MM:
            # Significant rain expected - reduce or skip
            adjustment = -min(planned_amount_mm, total_expected_rain * 0.8)
        elif total_expected_rain > 0:
            # Some rain expected - partial reduction
            adjustment = -total_expected_rain * 0.5

        adjusted_amount = max(0, planned_amount_mm + adjustment)

        return {
            "field_id": field_id,
            "planned_amount_mm": planned_amount_mm,
            "expected_rainfall_mm": total_expected_rain,
            "adjustment_mm": adjustment,
            "adjusted_amount_mm": adjusted_amount,
            "recommendation": "Proceed as planned" if adjustment == 0 else f"Reduce irrigation by {abs(adjustment):.1f}mm due to expected rainfall",
            "recommendation_ar": "المتابعة كما هو مخطط" if adjustment == 0 else f"تقليل الري بمقدار {abs(adjustment):.1f} ملم بسبب الأمطار المتوقعة",
            "skip_irrigation": adjusted_amount < 5,
        }

    async def _get_heat_stress_alert(
        self,
        location: dict[str, float],
        crop_type: str | None = None,
    ) -> dict[str, Any]:
        """Check for heat stress conditions."""
        logger.info("checking_heat_stress", location=location)

        forecast = await self._get_weather_forecast(location, days=3)

        heat_days = []
        for day in forecast.get("daily_forecasts", []):
            max_temp = day.get("temperature_max_c", 25)
            if max_temp >= self.HEAT_STRESS_THRESHOLD_C:
                heat_days.append({
                    "day": day.get("day"),
                    "date": day.get("date"),
                    "max_temperature_c": max_temp,
                    "severity": "critical" if max_temp >= 40 else "warning",
                    "severity_ar": "حرج" if max_temp >= 40 else "تحذير",
                })

        has_heat_risk = len(heat_days) > 0

        # Crop-specific recommendations
        crop_advice = {
            "wheat": "Increase irrigation frequency during grain filling",
            "tomato": "Apply shade cloth, increase irrigation",
            "date_palm": "Monitor for fruit drop, ensure adequate irrigation",
        }
        crop_advice_ar = {
            "wheat": "زيادة تكرار الري خلال مرحلة امتلاء الحبوب",
            "tomato": "تطبيق قماش التظليل، زيادة الري",
            "date_palm": "مراقبة تساقط الثمار، ضمان الري الكافي",
        }

        return {
            "location": location,
            "crop_type": crop_type,
            "heat_stress_risk": has_heat_risk,
            "risk_level": "high" if len(heat_days) >= 2 else "medium" if heat_days else "low",
            "risk_level_ar": "مرتفع" if len(heat_days) >= 2 else "متوسط" if heat_days else "منخفض",
            "heat_days": heat_days,
            "general_measures": [
                {"action": "Increase irrigation frequency", "action_ar": "زيادة تكرار الري"},
                {"action": "Irrigate early morning or evening", "action_ar": "الري في الصباح الباكر أو المساء"},
                {"action": "Apply mulch to reduce soil temperature", "action_ar": "تطبيق التغطية لتقليل حرارة التربة"},
            ] if has_heat_risk else [],
            "crop_specific_advice": crop_advice.get(crop_type, "Monitor crop stress signs") if crop_type else None,
            "crop_specific_advice_ar": crop_advice_ar.get(crop_type, "مراقبة علامات إجهاد المحصول") if crop_type else None,
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_weather_agent(
    tenant_id: str = "sahool",
    parent_agent: BaseAutonomousAgent | None = None,
) -> WeatherSubAgent:
    """
    Factory function to create a WeatherSubAgent.
    دالة لإنشاء وكيل الطقس الفرعي
    """
    return WeatherSubAgent(
        tenant_id=tenant_id,
        parent_agent=parent_agent,
    )
