"""
Tests for shared/ai/agents/weather_agent.py
اختبارات وكيل الطقس

Tests cover:
- Data model creation (WeatherCondition, WeatherAlert, etc.)
- WeatherSubAgent initialization (via patched base)
- Task decomposition for various weather queries
- Tool handler methods (forecast, climate risk, spray window, frost, heat, irrigation)
- Step result validation
- Factory function
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import UTC, datetime

from shared.ai.agents.weather_agent import (
    WeatherCondition,
    WeatherAlert,
    WeatherForecast,
    ClimateRiskAssessment,
    WeatherSubAgent,
    create_weather_agent,
)
from shared.ai.agents.base import AgentMode, AgentStep, CollaborationRole, ToolResult


class TestWeatherDataModels:
    """Tests for weather data models.
    اختبارات نماذج بيانات الطقس"""

    def test_weather_condition_creation(self):
        """Test creating a WeatherCondition instance."""
        now = datetime.now(UTC)
        cond = WeatherCondition(
            timestamp=now,
            temperature_c=25.0,
            temperature_min_c=18.0,
            temperature_max_c=32.0,
            humidity_percent=55.0,
            wind_speed_kmh=12.0,
            wind_direction="NW",
            precipitation_mm=0.0,
            cloud_cover_percent=20.0,
            uv_index=7.0,
            condition="sunny",
            condition_ar="مشمس",
        )
        assert cond.temperature_c == 25.0
        assert cond.condition_ar == "مشمس"
        assert cond.wind_direction == "NW"

    def test_weather_alert_creation(self):
        """Test creating a WeatherAlert instance."""
        now = datetime.now(UTC)
        alert = WeatherAlert(
            alert_id="alert-001",
            alert_type="frost",
            severity="high",
            severity_ar="مرتفع",
            title="Frost Warning",
            title_ar="تحذير صقيع",
            description="Frost expected tonight",
            description_ar="صقيع متوقع الليلة",
            start_time=now,
            end_time=now,
            affected_operations=["irrigation", "spraying"],
            recommendations=["Cover crops"],
            recommendations_ar=["تغطية المحاصيل"],
        )
        assert alert.alert_type == "frost"
        assert alert.severity == "high"
        assert len(alert.affected_operations) == 2

    def test_weather_forecast_creation(self):
        """Test creating a WeatherForecast instance."""
        forecast = WeatherForecast(
            location="Riyadh",
            location_ar="الرياض",
            generated_at=datetime.now(UTC),
            daily_forecasts=[],
            alerts=[],
            confidence=0.85,
            source="SAHOOL",
        )
        assert forecast.confidence == 0.85
        assert forecast.daily_forecasts == []
        assert forecast.source == "SAHOOL"

    def test_climate_risk_assessment_creation(self):
        """Test creating a ClimateRiskAssessment instance."""
        risk = ClimateRiskAssessment(
            assessment_id="risk-001",
            period="weekly",
            frost_risk=0.3,
            heat_stress_risk=0.6,
            drought_risk=0.4,
            flood_risk=0.1,
            storm_risk=0.15,
            overall_risk="medium",
            overall_risk_ar="متوسط",
            recommendations=[{"risk": "heat", "action": "Irrigate more"}],
        )
        assert risk.overall_risk == "medium"
        assert risk.heat_stress_risk == 0.6
        assert risk.created_at is not None


@pytest.fixture
def weather_agent():
    """Create a WeatherSubAgent with mocked base init.
    إنشاء وكيل طقس مع تهيئة أساسية محاكاة"""
    with patch("shared.ai.agents.weather_agent.BaseAutonomousAgent.__init__", return_value=None):
        agent = WeatherSubAgent.__new__(WeatherSubAgent)
        agent.agent_id = "weather-sub-agent"
        agent.name = "Weather Specialist"
        agent.name_ar = "متخصص الطقس"
        agent.description = "Specialized agent for weather-based agricultural decisions"
        agent.description_ar = "وكيل متخصص للقرارات الزراعية المبنية على الطقس"
        agent.mode = AgentMode.EXECUTE
        agent.tenant_id = "sahool"
        agent.collaboration_role = CollaborationRole.SPECIALIST
        agent.weather_api_url = None
        agent._forecast_cache = {}
        agent.tools = {}
        agent.capabilities = []
        agent.state = "idle"
        agent.current_task = None
        agent.steps = []
        agent.current_step_index = 0
        agent.execution_history = []
        return agent


class TestWeatherSubAgentInit:
    """Tests for WeatherSubAgent configuration.
    اختبارات تكوين وكيل الطقس"""

    def test_thresholds(self):
        """Test weather threshold constants."""
        assert WeatherSubAgent.FROST_THRESHOLD_C == 4.0
        assert WeatherSubAgent.HEAT_STRESS_THRESHOLD_C == 35.0
        assert WeatherSubAgent.SPRAY_WIND_MAX_KMH == 15.0
        assert WeatherSubAgent.SPRAY_RAIN_THRESHOLD_MM == 2.0
        assert WeatherSubAgent.IRRIGATION_RAIN_THRESHOLD_MM == 10.0

    def test_agent_attributes(self, weather_agent):
        """Test agent attributes after creation."""
        assert weather_agent.agent_id == "weather-sub-agent"
        assert weather_agent.name == "Weather Specialist"
        assert weather_agent.weather_api_url is None
        assert weather_agent._forecast_cache == {}


class TestWeatherSubAgentDecompose:
    """Tests for task decomposition.
    اختبارات تحليل المهام"""

    @pytest.mark.asyncio
    async def test_decompose_forecast_task(self, weather_agent):
        """Test decomposing a forecast request."""
        steps = await weather_agent.decompose_task(
            "Get weather forecast",
            {"location": {"lat": 24.7, "lon": 46.7}},
        )
        assert len(steps) == 1
        assert steps[0].tool_name == "get_weather_forecast"

    @pytest.mark.asyncio
    async def test_decompose_arabic_forecast_task(self, weather_agent):
        """Test decomposing an Arabic forecast request."""
        steps = await weather_agent.decompose_task("توقعات الطقس", {})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_weather_forecast"

    @pytest.mark.asyncio
    async def test_decompose_risk_task(self, weather_agent):
        """Test decomposing a climate risk request."""
        steps = await weather_agent.decompose_task("Assess climate risks", {})
        assert len(steps) == 1
        assert steps[0].tool_name == "assess_climate_risks"

    @pytest.mark.asyncio
    async def test_decompose_spray_task(self, weather_agent):
        """Test decomposing a spray window request."""
        steps = await weather_agent.decompose_task("Find spray window", {"field_id": "F003"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_optimal_spray_window"

    @pytest.mark.asyncio
    async def test_decompose_frost_task(self, weather_agent):
        """Test decomposing a frost risk request."""
        steps = await weather_agent.decompose_task("Is there frost danger tonight?", {})
        assert len(steps) == 1
        assert steps[0].tool_name == "check_frost_risk"

    @pytest.mark.asyncio
    async def test_decompose_default_task(self, weather_agent):
        """Test default decomposition returns forecast + risk assessment."""
        steps = await weather_agent.decompose_task("general analysis", {})
        assert len(steps) == 2
        assert steps[0].tool_name == "get_weather_forecast"
        assert steps[1].tool_name == "assess_climate_risks"


class TestWeatherSubAgentValidation:
    """Tests for step result validation.
    اختبارات التحقق من نتائج الخطوات"""

    @pytest.mark.asyncio
    async def test_validate_success(self, weather_agent):
        """Test validating a successful result."""
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_weather_forecast", tool_input={},
        )
        result = ToolResult(tool_name="get_weather_forecast", success=True, result={"daily_forecasts": [{"day": 1}]}, error=None)
        valid, msg = await weather_agent.validate_step_result(step, result, {})
        assert valid is True
        assert msg is None

    @pytest.mark.asyncio
    async def test_validate_failure(self, weather_agent):
        """Test validating a failed result."""
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="some_tool", tool_input={},
        )
        result = ToolResult(tool_name="some_tool", success=False, result=None, error="Connection timeout")
        valid, msg = await weather_agent.validate_step_result(step, result, {})
        assert valid is False
        assert "Connection timeout" in msg

    @pytest.mark.asyncio
    async def test_validate_forecast_empty_data(self, weather_agent):
        """Test validating forecast with no data."""
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_weather_forecast", tool_input={},
        )
        result = ToolResult(tool_name="get_weather_forecast", success=True, result={"daily_forecasts": []}, error=None)
        valid, msg = await weather_agent.validate_step_result(step, result, {})
        assert valid is False
        assert "No forecast data" in msg


class TestWeatherToolHandlers:
    """Tests for tool handler methods.
    اختبارات معالجات الأدوات"""

    @pytest.mark.asyncio
    async def test_get_weather_forecast(self, weather_agent):
        """Test getting weather forecast."""
        result = await weather_agent._get_weather_forecast(
            location={"lat": 24.7, "lon": 46.7}, days=3,
        )
        assert "daily_forecasts" in result
        assert len(result["daily_forecasts"]) == 3
        assert result["confidence"] == 0.85
        assert result["source"] == "SAHOOL Weather Service"

    @pytest.mark.asyncio
    async def test_assess_climate_risks(self, weather_agent):
        """Test assessing climate risks."""
        result = await weather_agent._assess_climate_risks(
            location={"lat": 24.7, "lon": 46.7},
            period="weekly",
        )
        assert "risks" in result
        assert "overall_risk" in result
        assert "overall_risk_ar" in result
        assert result["period"] == "weekly"

    @pytest.mark.asyncio
    async def test_assess_climate_risks_with_crop(self, weather_agent):
        """Test assessing climate risks with crop type."""
        result = await weather_agent._assess_climate_risks(
            location={"lat": 24.7, "lon": 46.7},
            crop_type="wheat",
        )
        assert result["crop_type"] == "wheat"

    @pytest.mark.asyncio
    async def test_get_optimal_spray_window(self, weather_agent):
        """Test finding optimal spray window."""
        result = await weather_agent._get_optimal_spray_window(
            field_id="F003",
            application_type="fungicide",
            days_ahead=3,
        )
        assert result["field_id"] == "F003"
        assert result["application_type"] == "fungicide"
        assert "suitable_windows" in result

    @pytest.mark.asyncio
    async def test_check_frost_risk(self, weather_agent):
        """Test checking frost risk."""
        result = await weather_agent._check_frost_risk(
            location={"lat": 24.7, "lon": 46.7}, days_ahead=3,
        )
        assert "frost_risk" in result
        assert "frost_risk_level" in result
        assert result["days_checked"] == 3

    @pytest.mark.asyncio
    async def test_get_irrigation_weather_adjustment(self, weather_agent):
        """Test calculating irrigation weather adjustment."""
        result = await weather_agent._get_irrigation_weather_adjustment(
            field_id="F001",
            planned_amount_mm=25.0,
        )
        assert result["field_id"] == "F001"
        assert result["planned_amount_mm"] == 25.0
        assert "adjusted_amount_mm" in result
        assert "skip_irrigation" in result

    @pytest.mark.asyncio
    async def test_get_heat_stress_alert(self, weather_agent):
        """Test checking heat stress alert."""
        result = await weather_agent._get_heat_stress_alert(
            location={"lat": 24.7, "lon": 46.7},
        )
        assert "heat_stress_risk" in result
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_get_heat_stress_alert_with_crop(self, weather_agent):
        """Test heat stress with crop-specific advice."""
        result = await weather_agent._get_heat_stress_alert(
            location={"lat": 24.7, "lon": 46.7},
            crop_type="wheat",
        )
        assert result["crop_type"] == "wheat"


class TestWeatherFactoryFunction:
    """Tests for factory function.
    اختبارات دالة الإنشاء"""

    def test_create_weather_agent_factory(self):
        """Test factory function creates correct type."""
        with patch("shared.ai.agents.weather_agent.BaseAutonomousAgent.__init__", return_value=None):
            with patch.object(WeatherSubAgent, "_register_default_tools"):
                with patch.object(WeatherSubAgent, "_register_default_capabilities"):
                    agent = create_weather_agent(tenant_id="farm_123")
                    assert isinstance(agent, WeatherSubAgent)
