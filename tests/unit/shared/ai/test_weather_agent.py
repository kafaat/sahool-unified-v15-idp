"""
Tests for shared/ai/agents/weather_agent.py
اختبارات وكيل الطقس

Tests cover:
- WeatherSubAgent instantiation and configuration
- Data model creation (WeatherCondition, WeatherAlert, etc.)
- Task decomposition for various weather queries
- Tool handler methods (forecast, climate risk, spray window, frost, heat, irrigation)
- Step result validation
- Factory function
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import UTC, datetime

from shared.ai.agents.weather_agent import (
    WeatherSubAgent,
    WeatherCondition,
    WeatherAlert,
    WeatherForecast,
    ClimateRiskAssessment,
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


class TestWeatherSubAgentInit:
    """Tests for WeatherSubAgent initialization.
    اختبارات تهيئة وكيل الطقس"""

    def test_default_initialization(self):
        """Test default agent initialization."""
        agent = WeatherSubAgent()
        assert agent.agent_id == "weather-sub-agent"
        assert agent.name == "Weather Specialist"
        assert agent.name_ar == "متخصص الطقس"
        assert agent.mode == AgentMode.EXECUTE
        assert agent.tenant_id == "sahool"
        assert agent.collaboration_role == CollaborationRole.SPECIALIST
        assert agent.weather_api_url is None

    def test_custom_initialization(self):
        """Test agent initialization with custom parameters."""
        agent = WeatherSubAgent(
            tenant_id="farm_001",
            weather_api_url="https://weather.api.example.com",
            agent_id="custom-weather",
            name="Custom Weather",
        )
        assert agent.tenant_id == "farm_001"
        assert agent.weather_api_url == "https://weather.api.example.com"
        assert agent.agent_id == "custom-weather"

    def test_thresholds(self):
        """Test weather threshold constants."""
        assert WeatherSubAgent.FROST_THRESHOLD_C == 4.0
        assert WeatherSubAgent.HEAT_STRESS_THRESHOLD_C == 35.0
        assert WeatherSubAgent.SPRAY_WIND_MAX_KMH == 15.0
        assert WeatherSubAgent.SPRAY_RAIN_THRESHOLD_MM == 2.0
        assert WeatherSubAgent.IRRIGATION_RAIN_THRESHOLD_MM == 10.0


class TestWeatherSubAgentDecompose:
    """Tests for task decomposition.
    اختبارات تحليل المهام"""

    @pytest.mark.asyncio
    async def test_decompose_forecast_task(self):
        """Test decomposing a forecast request."""
        agent = WeatherSubAgent()
        steps = await agent.decompose_task("Get weather forecast", {"location": {"lat": 24.7, "lon": 46.7}})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_weather_forecast"

    @pytest.mark.asyncio
    async def test_decompose_arabic_forecast_task(self):
        """Test decomposing an Arabic forecast request."""
        agent = WeatherSubAgent()
        steps = await agent.decompose_task("توقعات الطقس", {})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_weather_forecast"

    @pytest.mark.asyncio
    async def test_decompose_risk_task(self):
        """Test decomposing a climate risk request."""
        agent = WeatherSubAgent()
        steps = await agent.decompose_task("Assess climate risks", {})
        assert len(steps) == 1
        assert steps[0].tool_name == "assess_climate_risks"

    @pytest.mark.asyncio
    async def test_decompose_spray_task(self):
        """Test decomposing a spray window request."""
        agent = WeatherSubAgent()
        steps = await agent.decompose_task("Find spray window", {"field_id": "F003"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_optimal_spray_window"

    @pytest.mark.asyncio
    async def test_decompose_frost_task(self):
        """Test decomposing a frost risk request."""
        agent = WeatherSubAgent()
        steps = await agent.decompose_task("Check frost risk", {})
        assert len(steps) == 1
        assert steps[0].tool_name == "check_frost_risk"

    @pytest.mark.asyncio
    async def test_decompose_default_task(self):
        """Test default decomposition returns forecast + risk assessment."""
        agent = WeatherSubAgent()
        steps = await agent.decompose_task("general analysis", {})
        assert len(steps) == 2
        assert steps[0].tool_name == "get_weather_forecast"
        assert steps[1].tool_name == "assess_climate_risks"


class TestWeatherSubAgentValidation:
    """Tests for step result validation.
    اختبارات التحقق من نتائج الخطوات"""

    @pytest.mark.asyncio
    async def test_validate_success(self):
        """Test validating a successful result."""
        agent = WeatherSubAgent()
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_weather_forecast", tool_input={},
        )
        result = ToolResult(success=True, result={"daily_forecasts": [{"day": 1}]}, error=None)
        valid, msg = await agent.validate_step_result(step, result, {})
        assert valid is True
        assert msg is None

    @pytest.mark.asyncio
    async def test_validate_failure(self):
        """Test validating a failed result."""
        agent = WeatherSubAgent()
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="some_tool", tool_input={},
        )
        result = ToolResult(success=False, result=None, error="Connection timeout")
        valid, msg = await agent.validate_step_result(step, result, {})
        assert valid is False
        assert "Connection timeout" in msg

    @pytest.mark.asyncio
    async def test_validate_forecast_empty_data(self):
        """Test validating forecast with no data."""
        agent = WeatherSubAgent()
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_weather_forecast", tool_input={},
        )
        result = ToolResult(success=True, result={"daily_forecasts": []}, error=None)
        valid, msg = await agent.validate_step_result(step, result, {})
        assert valid is False
        assert "No forecast data" in msg


class TestWeatherToolHandlers:
    """Tests for tool handler methods.
    اختبارات معالجات الأدوات"""

    @pytest.mark.asyncio
    async def test_get_weather_forecast(self):
        """Test getting weather forecast."""
        agent = WeatherSubAgent()
        result = await agent._get_weather_forecast(
            location={"lat": 24.7, "lon": 46.7}, days=3,
        )
        assert "daily_forecasts" in result
        assert len(result["daily_forecasts"]) == 3
        assert result["confidence"] == 0.85
        assert result["source"] == "SAHOOL Weather Service"
        assert "location" in result

    @pytest.mark.asyncio
    async def test_assess_climate_risks(self):
        """Test assessing climate risks."""
        agent = WeatherSubAgent()
        result = await agent._assess_climate_risks(
            location={"lat": 24.7, "lon": 46.7},
            period="weekly",
        )
        assert "risks" in result
        assert "overall_risk" in result
        assert "overall_risk_ar" in result
        assert result["period"] == "weekly"
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_assess_climate_risks_with_crop(self):
        """Test assessing climate risks with crop type."""
        agent = WeatherSubAgent()
        result = await agent._assess_climate_risks(
            location={"lat": 24.7, "lon": 46.7},
            crop_type="wheat",
        )
        assert result["crop_type"] == "wheat"

    @pytest.mark.asyncio
    async def test_get_optimal_spray_window(self):
        """Test finding optimal spray window."""
        agent = WeatherSubAgent()
        result = await agent._get_optimal_spray_window(
            field_id="F003",
            application_type="fungicide",
            days_ahead=3,
        )
        assert result["field_id"] == "F003"
        assert result["application_type"] == "fungicide"
        assert "suitable_windows" in result
        assert "recommendation" in result
        assert "recommendation_ar" in result

    @pytest.mark.asyncio
    async def test_check_frost_risk(self):
        """Test checking frost risk."""
        agent = WeatherSubAgent()
        result = await agent._check_frost_risk(
            location={"lat": 24.7, "lon": 46.7}, days_ahead=3,
        )
        assert "frost_risk" in result
        assert "frost_risk_level" in result
        assert "frost_risk_level_ar" in result
        assert result["days_checked"] == 3

    @pytest.mark.asyncio
    async def test_get_irrigation_weather_adjustment(self):
        """Test calculating irrigation weather adjustment."""
        agent = WeatherSubAgent()
        result = await agent._get_irrigation_weather_adjustment(
            field_id="F001",
            planned_amount_mm=25.0,
        )
        assert result["field_id"] == "F001"
        assert result["planned_amount_mm"] == 25.0
        assert "adjusted_amount_mm" in result
        assert "recommendation" in result
        assert "skip_irrigation" in result

    @pytest.mark.asyncio
    async def test_get_heat_stress_alert(self):
        """Test checking heat stress alert."""
        agent = WeatherSubAgent()
        result = await agent._get_heat_stress_alert(
            location={"lat": 24.7, "lon": 46.7},
        )
        assert "heat_stress_risk" in result
        assert "risk_level" in result
        assert "risk_level_ar" in result

    @pytest.mark.asyncio
    async def test_get_heat_stress_alert_with_crop(self):
        """Test heat stress with crop-specific advice."""
        agent = WeatherSubAgent()
        result = await agent._get_heat_stress_alert(
            location={"lat": 24.7, "lon": 46.7},
            crop_type="wheat",
        )
        assert result["crop_type"] == "wheat"
        # Should have crop-specific advice when crop is known
        if result["heat_stress_risk"]:
            assert result["crop_specific_advice"] is not None


class TestWeatherFactoryFunction:
    """Tests for factory function.
    اختبارات دالة الإنشاء"""

    def test_create_weather_agent_default(self):
        """Test creating agent with defaults."""
        agent = create_weather_agent()
        assert isinstance(agent, WeatherSubAgent)
        assert agent.tenant_id == "sahool"

    def test_create_weather_agent_custom(self):
        """Test creating agent with custom tenant."""
        agent = create_weather_agent(tenant_id="farm_123")
        assert agent.tenant_id == "farm_123"
