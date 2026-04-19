# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Tests for LLM Orchestrator Service.
اختبارات لخدمة تنسيق نماذج اللغة الكبيرة.
"""

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)
try:
    from src.agents.registry import AgentCapability, AgentCategory, AgentRegistry
    from src.api.schemas import IntentType, UserIntent
    from src.utils.intent_classifier import (
        IntentClassifier,
        calculate_intent_score,
        detect_language,
        extract_entities,
    )
except ImportError:
    pytest.skip("llm-orchestrator-service dependencies not installed", allow_module_level=True)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client: TestClient):
        """Test liveness probe."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "llm-orchestrator-service"
        assert "version" in data

    def test_readyz(self, client: TestClient):
        """Test readiness probe."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data

    def test_root(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "endpoints" in data


class TestLanguageDetection:
    """Test language detection functionality."""

    def test_detect_arabic(self):
        """Test detecting Arabic language."""
        text = "ما هو المرض الذي يصيب محصول القمح؟"
        assert detect_language(text) == "ar"

    def test_detect_english(self):
        """Test detecting English language."""
        text = "What disease is affecting my wheat crop?"
        assert detect_language(text) == "en"

    def test_detect_mixed(self):
        """Test detecting mixed language (defaults to majority)."""
        text = "My wheat محصول has disease مرض"
        # Should detect based on character count
        result = detect_language(text)
        assert result in ("ar", "en")


class TestIntentClassification:
    """Test intent classification functionality."""

    def test_crop_disease_intent_english(self):
        """Test classifying crop disease intent in English."""
        score = calculate_intent_score(
            "My wheat has yellow spots and rust disease",
            IntentType.CROP_DISEASE,
            "en",
        )
        assert score > 0.5

    def test_crop_disease_intent_arabic(self):
        """Test classifying crop disease intent in Arabic."""
        score = calculate_intent_score(
            "يوجد مرض وصدأ على أوراق القمح",
            IntentType.CROP_DISEASE,
            "ar",
        )
        assert score > 0.5

    def test_irrigation_intent(self):
        """Test classifying irrigation intent."""
        score = calculate_intent_score(
            "When should I water my field?",
            IntentType.IRRIGATION_QUERY,
            "en",
        )
        assert score > 0.3

    def test_fertilizer_intent(self):
        """Test classifying fertilizer intent."""
        score = calculate_intent_score(
            "I need nitrogen fertilizer recommendation",
            IntentType.FERTILIZER_ADVICE,
            "en",
        )
        assert score > 0.3

    def test_weather_intent(self):
        """Test classifying weather intent."""
        score = calculate_intent_score(
            "What is the weather forecast for tomorrow?",
            IntentType.WEATHER_QUERY,
            "en",
        )
        assert score > 0.3

    def test_yield_intent(self):
        """Test classifying yield prediction intent."""
        score = calculate_intent_score(
            "Predict my wheat harvest yield",
            IntentType.YIELD_PREDICTION,
            "en",
        )
        assert score > 0.3


class TestEntityExtraction:
    """Test entity extraction functionality."""

    def test_extract_crop_type_english(self):
        """Test extracting crop type in English."""
        entities = extract_entities("My wheat field has a problem", "en")
        assert "crop_type" in entities
        assert entities["crop_type"] == "wheat"

    def test_extract_crop_type_arabic(self):
        """Test extracting crop type in Arabic."""
        entities = extract_entities("حقل القمح يعاني من مشكلة", "ar")
        assert "crop_type" in entities
        assert entities["crop_type"] == "قمح"

    def test_extract_severity(self):
        """Test extracting severity."""
        entities = extract_entities("There is severe damage to the crop", "en")
        assert "severity" in entities
        assert entities["severity"] == "severe"


class TestAgentRegistry:
    """Test agent registry functionality."""

    def test_registry_initialization(self):
        """Test registry initializes with agents."""
        registry = AgentRegistry()
        agents = registry.get_all_agents()
        assert len(agents) > 0

    def test_get_agent_by_name(self):
        """Test getting agent by name."""
        registry = AgentRegistry()
        agent = registry.get_agent("crop-intelligence")
        assert agent is not None
        assert agent.name == "crop-intelligence"

    def test_get_agents_by_category(self):
        """Test getting agents by category."""
        registry = AgentRegistry()
        agents = registry.get_agents_by_category(AgentCategory.CROP_HEALTH)
        assert len(agents) > 0
        for agent in agents:
            assert agent.category == AgentCategory.CROP_HEALTH

    def test_get_agents_by_capability(self):
        """Test getting agents by capability."""
        registry = AgentRegistry()
        agents = registry.get_agents_by_capability(AgentCapability.DISEASE_DETECTION)
        assert len(agents) > 0
        for agent in agents:
            assert AgentCapability.DISEASE_DETECTION in agent.capabilities

    def test_get_agents_for_intent(self):
        """Test getting agents for intent type."""
        registry = AgentRegistry()
        agents = registry.get_agents_for_intent("crop_disease")
        assert len(agents) > 0

    def test_registry_to_dict(self):
        """Test converting registry to dictionary."""
        registry = AgentRegistry()
        data = registry.to_dict()
        assert "agents" in data
        assert "total" in data
        assert "active" in data


class TestIntentClassifier:
    """Test IntentClassifier class."""

    @pytest.mark.asyncio
    async def test_classify_disease_intent(self, sample_user_intent):
        """Test classifying disease intent."""
        classifier = IntentClassifier()
        user_intent = UserIntent(**sample_user_intent)
        result = await classifier.classify(user_intent)

        assert result.intent_type == IntentType.CROP_DISEASE
        assert result.confidence > 0.5
        assert result.language_detected == "en"

    @pytest.mark.asyncio
    async def test_classify_arabic_intent(self, sample_user_intent_arabic):
        """Test classifying Arabic intent."""
        classifier = IntentClassifier()
        user_intent = UserIntent(**sample_user_intent_arabic)
        result = await classifier.classify(user_intent)

        assert result.intent_type == IntentType.CROP_DISEASE
        assert result.language_detected == "ar"

    @pytest.mark.asyncio
    async def test_classify_irrigation_intent(self, sample_irrigation_intent):
        """Test classifying irrigation intent."""
        classifier = IntentClassifier()
        user_intent = UserIntent(**sample_irrigation_intent)
        result = await classifier.classify(user_intent)

        assert result.intent_type == IntentType.IRRIGATION_QUERY
        assert result.confidence > 0.3


class TestOrchestratorEndpoints:
    """Test orchestrator API endpoints."""

    def test_list_agents(self, client: TestClient):
        """Test listing agents endpoint."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert data["total"] > 0

    def test_get_plans(self, client: TestClient):
        """Test getting available plans endpoint."""
        response = client.get("/api/v1/orchestrate/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "total" in data

    def test_orchestrate_endpoint_validation(self, client: TestClient):
        """Test orchestrate endpoint validation."""
        # Empty text should fail Pydantic min_length=1 validation → 422.
        # A valid UUID tenant header is supplied so we exercise body validation
        # rather than the tenant-header guard, which would otherwise return 400.
        response = client.post(
            "/api/v1/orchestrate",
            json={"text": ""},
            headers={"X-Tenant-Id": "00000000-0000-0000-0000-000000000000"},
        )
        assert response.status_code == 422

    def test_orchestrate_image_requires_image(self, client: TestClient):
        """Test orchestrate/image endpoint requires image."""
        response = client.post(
            "/api/v1/orchestrate/image",
            json={"text": "Analyze this image"},
        )
        assert response.status_code == 400


class TestSchemas:
    """Test Pydantic schemas."""

    def test_user_intent_validation(self):
        """Test UserIntent schema validation."""
        intent = UserIntent(text="Test query", language="en")
        assert intent.text == "Test query"
        assert intent.language == "en"

    def test_user_intent_with_image(self):
        """Test UserIntent with image."""
        intent = UserIntent(
            text="Analyze",
            image_base64="base64data",
            language="en",
        )
        assert intent.image_base64 == "base64data"

    def test_user_intent_auto_language(self):
        """Test UserIntent with auto language detection."""
        intent = UserIntent(text="Test query")
        assert intent.language == "auto"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
