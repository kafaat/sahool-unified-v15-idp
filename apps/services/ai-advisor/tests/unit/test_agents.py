"""
Unit Tests for AI Agents
اختبارات وحدة للوكلاء الذكيين
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.agents import (
    FieldAnalystAgent,
    DiseaseExpertAgent,
    IrrigationAdvisorAgent,
    YieldPredictorAgent
)


class TestFieldAnalystAgent:
    """Test suite for FieldAnalystAgent"""

    @pytest.mark.asyncio
    async def test_analyze_field_success(self, mock_knowledge_retriever):
        """Test successful field analysis"""
        agent = FieldAnalystAgent(tools=[], retriever=mock_knowledge_retriever)

        satellite_data = {
            "ndvi_average": 0.75,
            "ndvi_min": 0.6,
            "ndvi_max": 0.85,
            "date": "2024-12-01"
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value="Field analysis result")):
            result = await agent.analyze_field(
                field_id="test-field-123",
                satellite_data=satellite_data
            )

            assert result is not None
            assert isinstance(result, (dict, str))

    @pytest.mark.asyncio
    async def test_analyze_field_with_invalid_data(self, mock_knowledge_retriever):
        """Test field analysis with invalid satellite data"""
        agent = FieldAnalystAgent(tools=[], retriever=mock_knowledge_retriever)

        invalid_data = {"invalid": "data"}

        with pytest.raises(Exception):
            await agent.analyze_field(
                field_id="test-field-123",
                satellite_data=invalid_data
            )

    @pytest.mark.asyncio
    async def test_analyze_field_uses_rag(self, mock_knowledge_retriever):
        """Test that field analysis uses RAG retrieval"""
        agent = FieldAnalystAgent(tools=[], retriever=mock_knowledge_retriever)

        satellite_data = {
            "ndvi_average": 0.75,
            "field_id": "test-field-123"
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value="Result")):
            await agent.analyze_field(
                field_id="test-field-123",
                satellite_data=satellite_data
            )

            # Verify RAG retrieval was called
            mock_knowledge_retriever.retrieve.assert_called()


class TestDiseaseExpertAgent:
    """Test suite for DiseaseExpertAgent"""

    @pytest.mark.asyncio
    async def test_diagnose_disease_with_symptoms(self, mock_knowledge_retriever):
        """Test disease diagnosis with symptoms"""
        agent = DiseaseExpertAgent(tools=[], retriever=mock_knowledge_retriever)

        symptoms = {
            "leaf_color": "yellow",
            "spots": True,
            "wilting": False
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "disease_name": "Leaf Blight",
            "confidence": 0.85,
            "treatment": "Apply fungicide"
        })):
            result = await agent.diagnose(
                symptoms=symptoms,
                crop_type="wheat"
            )

            assert result is not None
            assert "disease_name" in result or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_diagnose_with_image_analysis(self, mock_knowledge_retriever, mock_crop_health_tool):
        """Test diagnosis with image analysis integration"""
        agent = DiseaseExpertAgent(tools=[mock_crop_health_tool], retriever=mock_knowledge_retriever)

        image_analysis = {
            "disease_detected": True,
            "disease_name": "Leaf Blight",
            "confidence": 0.85
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "disease_name": "Leaf Blight",
            "treatment": "Apply fungicide"
        })):
            result = await agent.diagnose(
                symptoms={},
                crop_type="wheat",
                image_analysis=image_analysis
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_assess_risk(self, mock_knowledge_retriever):
        """Test disease risk assessment"""
        agent = DiseaseExpertAgent(tools=[], retriever=mock_knowledge_retriever)

        environmental_conditions = {
            "temperature": 28.5,
            "humidity": 75,
            "precipitation": 10
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "risk_level": "high",
            "diseases": ["Rust", "Blight"],
            "recommendations": "Monitor closely"
        })):
            result = await agent.assess_risk(
                crop_type="wheat",
                location="test-location",
                season="winter",
                environmental_conditions=environmental_conditions
            )

            assert result is not None


class TestIrrigationAdvisorAgent:
    """Test suite for IrrigationAdvisorAgent"""

    @pytest.mark.asyncio
    async def test_recommend_irrigation(self, mock_knowledge_retriever):
        """Test irrigation recommendation"""
        agent = IrrigationAdvisorAgent(tools=[], retriever=mock_knowledge_retriever)

        soil_data = {
            "moisture": 45,
            "type": "loamy"
        }

        weather_data = {
            "temperature": 25,
            "humidity": 60,
            "forecast": "sunny"
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "recommendation": "Irrigate 20mm",
            "timing": "early morning",
            "frequency": "every 3 days"
        })):
            result = await agent.recommend_irrigation(
                crop_type="tomato",
                growth_stage="flowering",
                soil_data=soil_data,
                weather_data=weather_data
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_recommend_irrigation_drought_conditions(self, mock_knowledge_retriever):
        """Test irrigation recommendations during drought"""
        agent = IrrigationAdvisorAgent(tools=[], retriever=mock_knowledge_retriever)

        soil_data = {
            "moisture": 15,  # Very low
            "type": "sandy"
        }

        weather_data = {
            "temperature": 35,  # High
            "humidity": 30,  # Low
            "forecast": "sunny"
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "recommendation": "Immediate irrigation required",
            "amount": "40mm",
            "urgency": "high"
        })):
            result = await agent.recommend_irrigation(
                crop_type="corn",
                growth_stage="vegetative",
                soil_data=soil_data,
                weather_data=weather_data
            )

            assert result is not None


class TestYieldPredictorAgent:
    """Test suite for YieldPredictorAgent"""

    @pytest.mark.asyncio
    async def test_predict_yield_basic(self, mock_knowledge_retriever):
        """Test basic yield prediction"""
        agent = YieldPredictorAgent(tools=[], retriever=mock_knowledge_retriever)

        field_data = {
            "soil_quality": "good",
            "ndvi_average": 0.75
        }

        weather_data = {
            "rainfall": 500,
            "temperature_avg": 25
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "predicted_yield": 4.5,
            "unit": "tons/hectare",
            "confidence": 0.8
        })):
            result = await agent.predict_yield(
                crop_type="wheat",
                area=5.0,
                growth_stage="reproductive",
                field_data=field_data,
                weather_data=weather_data
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_predict_yield_with_historical_data(self, mock_knowledge_retriever):
        """Test yield prediction with historical data"""
        agent = YieldPredictorAgent(tools=[], retriever=mock_knowledge_retriever)

        field_data = {
            "soil_quality": "good",
            "historical_yields": [4.0, 4.2, 4.5]
        }

        weather_data = {
            "rainfall": 500,
            "temperature_avg": 25
        }

        with patch.object(agent, '_query_llm', new=AsyncMock(return_value={
            "predicted_yield": 4.6,
            "trend": "increasing",
            "confidence": 0.85
        })):
            result = await agent.predict_yield(
                crop_type="wheat",
                area=10.0,
                growth_stage="reproductive",
                field_data=field_data,
                weather_data=weather_data
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_predict_yield_handles_insufficient_data(self, mock_knowledge_retriever):
        """Test yield prediction with insufficient data"""
        agent = YieldPredictorAgent(tools=[], retriever=mock_knowledge_retriever)

        with pytest.raises(Exception):
            await agent.predict_yield(
                crop_type="wheat",
                area=5.0,
                growth_stage="",
                field_data={},
                weather_data={}
            )
