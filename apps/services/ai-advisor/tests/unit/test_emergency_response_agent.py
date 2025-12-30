"""
Unit tests for Emergency Response Agent
اختبارات الوحدة لوكيل الاستجابة للطوارئ
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any

from src.agents.emergency_response_agent import (
    EmergencyResponseAgent,
    EmergencyType,
    SeverityLevel
)


class TestEmergencyResponseAgent:
    """
    Test suite for Emergency Response Agent
    مجموعة اختبارات لوكيل الاستجابة للطوارئ
    """

    @pytest.fixture
    def agent(self):
        """
        Create EmergencyResponseAgent instance for testing
        إنشاء مثيل وكيل الاستجابة للطوارئ للاختبار
        """
        return EmergencyResponseAgent()

    @pytest.fixture
    def drought_field_data(self) -> Dict[str, Any]:
        """Sample drought field data | بيانات حقل الجفاف النموذجية"""
        return {
            "field_id": "TEST-FIELD-001",
            "crop_type": "wheat",
            "growth_stage": "grain_filling",
            "soil_moisture": 12,  # Critical
            "temperature": 42,
            "humidity": 15,
            "last_irrigation": "7_days_ago"
        }

    @pytest.fixture
    def flood_field_data(self) -> Dict[str, Any]:
        """Sample flood field data | بيانات حقل الفيضان النموذجية"""
        return {
            "field_id": "TEST-FIELD-002",
            "crop_type": "vegetables",
            "water_level_cm": 25,
            "soil_saturation": 95,
            "drainage_capacity": "poor",
            "rainfall_24h_mm": 120
        }

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response | استجابة LLM الوهمية"""
        mock_response = Mock()
        mock_response.content = """
        EMERGENCY ASSESSMENT:
        Severity: CRITICAL
        Immediate actions needed:
        1. Emergency irrigation within 2 hours
        2. Apply anti-transpirants
        3. Monitor soil moisture closely

        Risk factors: High temperature, low soil moisture, critical growth stage
        """
        return mock_response

    # ==================== Initialization Tests ====================

    def test_agent_initialization(self, agent):
        """
        Test agent initialization
        اختبار تهيئة الوكيل
        """
        assert agent.name == "emergency_response"
        assert agent.role == "Agricultural Emergency Response Coordinator"
        assert isinstance(agent.active_emergencies, dict)
        assert len(agent.active_emergencies) == 0

    def test_emergency_type_enum(self):
        """
        Test EmergencyType enum
        اختبار enum نوع الطوارئ
        """
        assert EmergencyType.DROUGHT.value == "drought"
        assert EmergencyType.FLOOD.value == "flood"
        assert EmergencyType.FROST.value == "frost"
        assert EmergencyType.HEAT_WAVE.value == "heat_wave"
        assert EmergencyType.PEST_OUTBREAK.value == "pest_outbreak"
        assert EmergencyType.DISEASE_EPIDEMIC.value == "disease_epidemic"
        assert EmergencyType.HAIL_DAMAGE.value == "hail_damage"
        assert EmergencyType.FIRE_RISK.value == "fire_risk"

    def test_severity_level_enum(self):
        """
        Test SeverityLevel enum
        اختبار enum مستوى الشدة
        """
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.MODERATE.value == "moderate"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_emergency_messages_exist(self, agent):
        """
        Test bilingual emergency messages exist
        اختبار وجود رسائل الطوارئ ثنائية اللغة
        """
        for emergency_type in EmergencyType:
            assert emergency_type in agent.EMERGENCY_MESSAGES
            assert "en" in agent.EMERGENCY_MESSAGES[emergency_type]
            assert "ar" in agent.EMERGENCY_MESSAGES[emergency_type]

    # ==================== Assess Emergency Tests ====================

    @pytest.mark.asyncio
    async def test_assess_emergency_drought(self, agent, drought_field_data, mock_llm_response):
        """
        Test drought emergency assessment
        اختبار تقييم طوارئ الجفاف
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.assess_emergency(
                emergency_type=EmergencyType.DROUGHT.value,
                field_data=drought_field_data
            )

            # Verify response structure
            assert "emergency_id" in result
            assert "emergency_type" in result
            assert "severity" in result
            assert "alert_en" in result
            assert "alert_ar" in result
            assert "assessment" in result
            assert "response_time_seconds" in result
            assert "within_target" in result
            assert "timestamp" in result

            # Verify content
            assert result["emergency_type"] == EmergencyType.DROUGHT.value
            assert result["severity"] in ["low", "moderate", "high", "critical"]
            assert isinstance(result["response_time_seconds"], float)

            # Verify emergency is tracked
            assert result["emergency_id"] in agent.active_emergencies

    @pytest.mark.asyncio
    async def test_assess_emergency_flood(self, agent, flood_field_data, mock_llm_response):
        """
        Test flood emergency assessment
        اختبار تقييم طوارئ الفيضان
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.assess_emergency(
                emergency_type=EmergencyType.FLOOD.value,
                field_data=flood_field_data,
                severity=SeverityLevel.CRITICAL.value
            )

            assert result["emergency_type"] == EmergencyType.FLOOD.value
            assert result["severity"] == SeverityLevel.CRITICAL.value
            assert "FLOOD" in result["alert_en"].upper()

    @pytest.mark.asyncio
    async def test_assess_emergency_response_time_target(self, agent, drought_field_data, mock_llm_response):
        """
        Test emergency assessment meets response time target
        اختبار تلبية تقييم الطوارئ للهدف الزمني للاستجابة
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            start = datetime.now()
            result = await agent.assess_emergency(
                emergency_type=EmergencyType.DROUGHT.value,
                field_data=drought_field_data
            )
            elapsed = (datetime.now() - start).total_seconds()

            # Should complete quickly (in test environment, LLM is mocked)
            assert elapsed < 1.0  # Very fast with mock

    @pytest.mark.asyncio
    async def test_assess_emergency_invalid_type(self, agent, drought_field_data):
        """
        Test assessment with invalid emergency type
        اختبار التقييم بنوع طوارئ غير صالح
        """
        with pytest.raises(ValueError):
            await agent.assess_emergency(
                emergency_type="invalid_emergency",
                field_data=drought_field_data
            )

    # ==================== Create Response Plan Tests ====================

    @pytest.mark.asyncio
    async def test_create_response_plan(self, agent, mock_llm_response):
        """
        Test creating emergency response plan
        اختبار إنشاء خطة الاستجابة للطوارئ
        """
        assessment = {
            "emergency_id": "drought_test_001",
            "emergency_type": EmergencyType.DROUGHT.value,
            "severity": SeverityLevel.HIGH.value
        }

        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.create_response_plan(
                emergency_type=EmergencyType.DROUGHT.value,
                assessment=assessment
            )

            assert "emergency_id" in result
            assert "plan" in result
            assert "created_at" in result
            assert isinstance(result["plan"], str)

    # ==================== Prioritize Actions Tests ====================

    @pytest.mark.asyncio
    async def test_prioritize_actions(self, agent, mock_llm_response):
        """
        Test action prioritization
        اختبار تحديد أولويات الإجراءات
        """
        actions = [
            {"action": "Emergency irrigation", "cost": 5000, "time_hours": 2},
            {"action": "Apply mulch", "cost": 2000, "time_hours": 8},
            {"action": "Adjust schedule", "cost": 0, "time_hours": 1}
        ]

        resources = {
            "budget_sar": 8000,
            "water_m3": 500,
            "labor_hours": 16
        }

        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.prioritize_actions(
                actions=actions,
                resources=resources,
                time_constraint=12
            )

            assert "prioritized_actions" in result
            assert "resource_allocation" in result
            assert "time_constraint_hours" in result
            assert result["time_constraint_hours"] == 12

    # ==================== Coordinate Response Tests ====================

    @pytest.mark.asyncio
    async def test_coordinate_response(self, agent, mock_llm_response):
        """
        Test multi-agent coordination
        اختبار التنسيق متعدد الوكلاء
        """
        plan = {
            "emergency_id": "test_001",
            "actions": ["action1", "action2"]
        }

        available_agents = [
            "irrigation_advisor",
            "soil_science",
            "yield_predictor"
        ]

        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.coordinate_response(
                plan=plan,
                available_agents=available_agents
            )

            assert "coordination_strategy" in result
            assert "engaged_agents" in result
            assert "created_at" in result
            assert result["engaged_agents"] == available_agents

    # ==================== Monitor Recovery Tests ====================

    @pytest.mark.asyncio
    async def test_monitor_recovery(self, agent, mock_llm_response):
        """
        Test recovery monitoring
        اختبار مراقبة التعافي
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.monitor_recovery(
                field_id="TEST-FIELD-001",
                emergency_type=EmergencyType.DROUGHT.value
            )

            assert "field_id" in result
            assert "emergency_type" in result
            assert "recovery_status" in result
            assert "monitored_at" in result
            assert result["field_id"] == "TEST-FIELD-001"

    # ==================== Estimate Damage Tests ====================

    @pytest.mark.asyncio
    async def test_estimate_damage(self, agent, mock_llm_response):
        """
        Test damage estimation
        اختبار تقدير الأضرار
        """
        crop_data = {
            "crop": "wheat",
            "area_hectares": 10,
            "growth_stage": "grain_filling",
            "expected_yield_tons": 30,
            "market_price_sar": 1200
        }

        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.estimate_damage(
                emergency_type=EmergencyType.DROUGHT.value,
                affected_area=10.0,
                crop_data=crop_data
            )

            assert "emergency_type" in result
            assert "affected_area_hectares" in result
            assert "damage_estimate" in result
            assert "estimated_at" in result
            assert result["affected_area_hectares"] == 10.0

    # ==================== Insurance Documentation Tests ====================

    @pytest.mark.asyncio
    async def test_insurance_documentation(self, agent, mock_llm_response):
        """
        Test insurance documentation generation
        اختبار إنشاء وثائق التأمين
        """
        emergency_data = {
            "emergency_id": "test_001",
            "type": EmergencyType.DROUGHT.value,
            "severity": SeverityLevel.HIGH.value,
            "field_data": {"crop": "wheat"},
            "damage_estimate": {"total": 50000}
        }

        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            result = await agent.insurance_documentation(
                emergency_data=emergency_data
            )

            assert "insurance_package" in result
            assert "emergency_reference" in result
            assert "generated_at" in result
            assert "languages" in result
            assert "English" in result["languages"]
            assert "Arabic" in result["languages"]

    # ==================== Lessons Learned Tests ====================

    @pytest.mark.asyncio
    async def test_lessons_learned(self, agent, drought_field_data, mock_llm_response):
        """
        Test lessons learned analysis
        اختبار تحليل الدروس المستفادة
        """
        # First create an emergency
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            assessment = await agent.assess_emergency(
                emergency_type=EmergencyType.DROUGHT.value,
                field_data=drought_field_data
            )

            emergency_id = assessment["emergency_id"]

            # Now analyze lessons learned
            result = await agent.lessons_learned(
                emergency_id=emergency_id
            )

            assert "emergency_id" in result
            assert "lessons_learned" in result
            assert "analyzed_at" in result
            assert "status" in result
            assert result["status"] == "complete"

            # Verify emergency status updated
            assert agent.active_emergencies[emergency_id]["status"] == "analyzed"

    # ==================== Severity Inference Tests ====================

    def test_infer_severity_drought_critical(self, agent):
        """Test drought severity inference - critical | اختبار استنتاج شدة الجفاف - حرج"""
        field_data = {"soil_moisture": 8}
        severity = agent._infer_severity(field_data, EmergencyType.DROUGHT.value)
        assert severity == SeverityLevel.CRITICAL.value

    def test_infer_severity_drought_high(self, agent):
        """Test drought severity inference - high | اختبار استنتاج شدة الجفاف - عالي"""
        field_data = {"soil_moisture": 15}
        severity = agent._infer_severity(field_data, EmergencyType.DROUGHT.value)
        assert severity == SeverityLevel.HIGH.value

    def test_infer_severity_flood_critical(self, agent):
        """Test flood severity inference - critical | اختبار استنتاج شدة الفيضان - حرج"""
        field_data = {"water_level_cm": 35}
        severity = agent._infer_severity(field_data, EmergencyType.FLOOD.value)
        assert severity == SeverityLevel.CRITICAL.value

    def test_infer_severity_frost_high(self, agent):
        """Test frost severity inference - high | اختبار استنتاج شدة الصقيع - عالي"""
        field_data = {"temperature": -2}
        severity = agent._infer_severity(field_data, EmergencyType.FROST.value)
        assert severity == SeverityLevel.HIGH.value

    def test_infer_severity_heat_wave_critical(self, agent):
        """Test heat wave severity inference - critical | اختبار استنتاج شدة موجة الحر - حرج"""
        field_data = {"temperature": 47}
        severity = agent._infer_severity(field_data, EmergencyType.HEAT_WAVE.value)
        assert severity == SeverityLevel.CRITICAL.value

    def test_infer_severity_pest_outbreak_high(self, agent):
        """Test pest outbreak severity inference - high | اختبار استنتاج شدة تفشي الآفات - عالي"""
        field_data = {"infestation_percentage": 50}
        severity = agent._infer_severity(field_data, EmergencyType.PEST_OUTBREAK.value)
        assert severity == SeverityLevel.HIGH.value

    def test_infer_severity_default_moderate(self, agent):
        """Test default severity inference | اختبار استنتاج الشدة الافتراضي"""
        field_data = {}
        severity = agent._infer_severity(field_data, EmergencyType.HAIL_DAMAGE.value)
        assert severity == SeverityLevel.MODERATE.value

    # ==================== Active Emergency Management Tests ====================

    def test_get_active_emergencies_empty(self, agent):
        """
        Test getting active emergencies when none exist
        اختبار الحصول على الطوارئ النشطة عند عدم وجود أي منها
        """
        active = agent.get_active_emergencies()
        assert isinstance(active, dict)
        assert len(active) == 0

    @pytest.mark.asyncio
    async def test_get_active_emergencies_with_data(self, agent, drought_field_data, mock_llm_response):
        """
        Test getting active emergencies with data
        اختبار الحصول على الطوارئ النشطة مع البيانات
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            assessment = await agent.assess_emergency(
                emergency_type=EmergencyType.DROUGHT.value,
                field_data=drought_field_data
            )

            active = agent.get_active_emergencies()
            assert len(active) == 1
            assert assessment["emergency_id"] in active

    @pytest.mark.asyncio
    async def test_clear_emergency(self, agent, drought_field_data, mock_llm_response):
        """
        Test clearing/resolving emergency
        اختبار مسح/حل الطوارئ
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            assessment = await agent.assess_emergency(
                emergency_type=EmergencyType.DROUGHT.value,
                field_data=drought_field_data
            )

            emergency_id = assessment["emergency_id"]

            # Clear emergency
            success = agent.clear_emergency(emergency_id)
            assert success is True

            # Verify status updated
            assert agent.active_emergencies[emergency_id]["status"] == "resolved"
            assert "resolved_at" in agent.active_emergencies[emergency_id]

    def test_clear_nonexistent_emergency(self, agent):
        """
        Test clearing non-existent emergency
        اختبار مسح طوارئ غير موجودة
        """
        success = agent.clear_emergency("nonexistent_id")
        assert success is False

    # ==================== System Prompt Tests ====================

    def test_get_system_prompt(self, agent):
        """
        Test system prompt generation
        اختبار إنشاء موجه النظام
        """
        prompt = agent.get_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # Check for key concepts
        assert "emergency" in prompt.lower()
        assert "drought" in prompt.lower()
        assert "flood" in prompt.lower()
        assert "arabic" in prompt.lower()
        assert "english" in prompt.lower()

    # ==================== Integration Tests ====================

    @pytest.mark.asyncio
    async def test_complete_workflow_drought(self, agent, drought_field_data, mock_llm_response):
        """
        Test complete emergency workflow for drought
        اختبار سير العمل الكامل للطوارئ للجفاف
        """
        with patch.object(agent.llm, 'ainvoke', return_value=mock_llm_response):
            # 1. Assess
            assessment = await agent.assess_emergency(
                emergency_type=EmergencyType.DROUGHT.value,
                field_data=drought_field_data
            )
            assert assessment["emergency_type"] == EmergencyType.DROUGHT.value

            # 2. Plan
            plan = await agent.create_response_plan(
                emergency_type=EmergencyType.DROUGHT.value,
                assessment=assessment
            )
            assert "plan" in plan

            # 3. Prioritize
            actions = [{"action": "test", "cost": 1000, "time_hours": 2}]
            resources = {"budget_sar": 5000}
            prioritized = await agent.prioritize_actions(actions, resources, 12)
            assert "prioritized_actions" in prioritized

            # 4. Coordinate
            coordination = await agent.coordinate_response(
                plan=plan,
                available_agents=["irrigation_advisor"]
            )
            assert "coordination_strategy" in coordination

            # 5. Estimate damage
            crop_data = {"crop": "wheat", "area_hectares": 10}
            damage = await agent.estimate_damage(
                emergency_type=EmergencyType.DROUGHT.value,
                affected_area=10.0,
                crop_data=crop_data
            )
            assert "damage_estimate" in damage

            # 6. Insurance
            insurance = await agent.insurance_documentation(
                emergency_data={"emergency_id": assessment["emergency_id"]}
            )
            assert "insurance_package" in insurance

            # 7. Monitor
            recovery = await agent.monitor_recovery(
                field_id=drought_field_data["field_id"],
                emergency_type=EmergencyType.DROUGHT.value
            )
            assert "recovery_status" in recovery

            # 8. Lessons
            lessons = await agent.lessons_learned(
                emergency_id=assessment["emergency_id"]
            )
            assert lessons["status"] == "complete"

            # 9. Clear
            success = agent.clear_emergency(assessment["emergency_id"])
            assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
