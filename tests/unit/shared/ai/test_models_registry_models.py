"""
Tests for shared/ai/models_registry/models.py
================================================

Tests cover:
- All enums: AIModelCategory, ModelCapability, ModelLicense, ModelStatus,
  ModelArchitecture
- Dataclass models: LanguageSupport, ModelEndpoint, DeveloperInfo,
  ModelPerformance, AIModelInfo, ModelComparison, ModelDiscoveryResult
- Methods: supports(), has_capability(), supports_language(), is_available(),
  get_display_name(), get_description(), to_dict(), from_dict()
"""

import pytest

from shared.ai.models_registry.models import (
    AIModelCategory,
    AIModelInfo,
    DeveloperInfo,
    LanguageSupport,
    ModelArchitecture,
    ModelCapability,
    ModelComparison,
    ModelDiscoveryResult,
    ModelEndpoint,
    ModelLicense,
    ModelPerformance,
    ModelStatus,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAIModelCategory:
    def test_all_values(self):
        assert AIModelCategory.GENERAL_AGRICULTURE.value == "general_agriculture"
        assert AIModelCategory.BREEDING_BIOSCIENCE.value == "breeding_bioscience"
        assert AIModelCategory.LIVESTOCK_VETERINARY.value == "livestock_veterinary"
        assert AIModelCategory.REMOTE_SENSING_GEO.value == "remote_sensing_geo"
        assert AIModelCategory.SPECIALTY.value == "specialty"
        assert AIModelCategory.FOOD_SAFETY.value == "food_safety"
        assert AIModelCategory.AGRICULTURAL_LAW.value == "agricultural_law"
        assert AIModelCategory.CLIMATE_WEATHER.value == "climate_weather"

    def test_member_count(self):
        assert len(AIModelCategory) == 8


class TestModelCapability:
    def test_knowledge_capabilities(self):
        assert ModelCapability.QA.value == "qa"
        assert ModelCapability.DECISION_SUPPORT.value == "decision_support"
        assert ModelCapability.EXPERT_CONSULTATION.value == "expert_consultation"
        assert ModelCapability.KNOWLEDGE_GRAPH.value == "knowledge_graph"

    def test_crop_capabilities(self):
        assert ModelCapability.PEST_DETECTION.value == "pest_detection"
        assert ModelCapability.DISEASE_DETECTION.value == "disease_detection"
        assert ModelCapability.YIELD_PREDICTION.value == "yield_prediction"

    def test_agent_capabilities(self):
        assert ModelCapability.AUTONOMOUS_OPERATION.value == "autonomous_operation"
        assert ModelCapability.MULTI_AGENT.value == "multi_agent"
        assert ModelCapability.TOOL_USE.value == "tool_use"
        assert ModelCapability.PLANNING.value == "planning"

    def test_member_count(self):
        assert len(ModelCapability) == 35


class TestModelLicense:
    def test_all_values(self):
        assert ModelLicense.OPEN_SOURCE.value == "open_source"
        assert ModelLicense.ACADEMIC.value == "academic"
        assert ModelLicense.COMMERCIAL.value == "commercial"
        assert ModelLicense.PROPRIETARY.value == "proprietary"
        assert ModelLicense.GOVERNMENT.value == "government"
        assert ModelLicense.FREEMIUM.value == "freemium"
        assert ModelLicense.UNKNOWN.value == "unknown"

    def test_member_count(self):
        assert len(ModelLicense) == 7


class TestModelStatus:
    def test_all_values(self):
        assert ModelStatus.ACTIVE.value == "active"
        assert ModelStatus.BETA.value == "beta"
        assert ModelStatus.DEPRECATED.value == "deprecated"
        assert ModelStatus.RESEARCH.value == "research"
        assert ModelStatus.COMING_SOON.value == "coming_soon"
        assert ModelStatus.OFFLINE.value == "offline"

    def test_member_count(self):
        assert len(ModelStatus) == 6


class TestModelArchitecture:
    def test_all_values(self):
        assert ModelArchitecture.LLM.value == "llm"
        assert ModelArchitecture.VLM.value == "vlm"
        assert ModelArchitecture.CNN.value == "cnn"
        assert ModelArchitecture.TRANSFORMER.value == "transformer"
        assert ModelArchitecture.FOUNDATION.value == "foundation"
        assert ModelArchitecture.ENSEMBLE.value == "ensemble"
        assert ModelArchitecture.AGENT.value == "agent"
        assert ModelArchitecture.HYBRID.value == "hybrid"

    def test_member_count(self):
        assert len(ModelArchitecture) == 8


# ─────────────────────────────────────────────────────────────────────────────
# LanguageSupport Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestLanguageSupport:
    def test_defaults(self):
        ls = LanguageSupport()
        assert ls.english is True
        assert ls.arabic is False
        assert ls.chinese is False
        assert ls.spanish is False
        assert ls.french is False
        assert ls.hindi is False
        assert ls.other_languages == []

    def test_supports_standard_languages(self):
        ls = LanguageSupport(english=True, arabic=True)
        assert ls.supports("en") is True
        assert ls.supports("ar") is True
        assert ls.supports("zh") is False
        assert ls.supports("EN") is True  # Case insensitive

    def test_supports_other_languages(self):
        ls = LanguageSupport(other_languages=["ur", "fa"])
        assert ls.supports("ur") is True
        assert ls.supports("fa") is True
        assert ls.supports("de") is False

    def test_supports_case_insensitive_other(self):
        ls = LanguageSupport(other_languages=["UR"])
        assert ls.supports("ur") is True

    def test_to_dict(self):
        ls = LanguageSupport(english=True, arabic=True, other_languages=["ur"])
        d = ls.to_dict()
        assert d["english"] is True
        assert d["arabic"] is True
        assert d["chinese"] is False
        assert d["other_languages"] == ["ur"]


# ─────────────────────────────────────────────────────────────────────────────
# ModelEndpoint Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestModelEndpoint:
    def test_defaults(self):
        ep = ModelEndpoint(url="https://api.example.com/v1/chat")
        assert ep.url == "https://api.example.com/v1/chat"
        assert ep.method == "POST"
        assert ep.auth_required is True
        assert ep.auth_type == "api_key"
        assert ep.rate_limit is None
        assert ep.timeout_seconds == 60
        assert ep.is_streaming is False

    def test_to_dict(self):
        ep = ModelEndpoint(
            url="https://api.example.com",
            method="GET",
            auth_required=False,
            rate_limit=100,
        )
        d = ep.to_dict()
        assert d["url"] == "https://api.example.com"
        assert d["method"] == "GET"
        assert d["auth_required"] is False
        assert d["rate_limit"] == 100


# ─────────────────────────────────────────────────────────────────────────────
# DeveloperInfo Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDeveloperInfo:
    def test_defaults(self):
        dev = DeveloperInfo(name="SAHOOL Team")
        assert dev.name == "SAHOOL Team"
        assert dev.name_ar == ""
        assert dev.name_cn == ""
        assert dev.organization_type == "academic"
        assert dev.country == "Unknown"
        assert dev.website is None

    def test_to_dict(self):
        dev = DeveloperInfo(
            name="SAHOOL",
            name_ar="سهول",
            country="SA",
            organization_type="commercial",
        )
        d = dev.to_dict()
        assert d["name"] == "SAHOOL"
        assert d["name_ar"] == "سهول"
        assert d["country"] == "SA"


# ─────────────────────────────────────────────────────────────────────────────
# ModelPerformance Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestModelPerformance:
    def test_defaults(self):
        perf = ModelPerformance()
        assert perf.accuracy is None
        assert perf.f1_score is None
        assert perf.latency_ms is None
        assert perf.throughput is None

    def test_to_dict(self):
        perf = ModelPerformance(accuracy=0.95, f1_score=0.93, latency_ms=50.0)
        d = perf.to_dict()
        assert d["accuracy"] == 0.95
        assert d["f1_score"] == 0.93
        assert d["latency_ms"] == 50.0


# ─────────────────────────────────────────────────────────────────────────────
# AIModelInfo Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAIModelInfo:
    def _make_model(self, **kwargs):
        defaults = {
            "model_id": "agri-gpt-1",
            "name": "AgriGPT",
            "name_ar": "زراعة GPT",
            "name_cn": "农业GPT",
            "category": AIModelCategory.GENERAL_AGRICULTURE,
            "capabilities": [ModelCapability.QA, ModelCapability.DECISION_SUPPORT],
            "architecture": ModelArchitecture.LLM,
            "status": ModelStatus.ACTIVE,
            "description": "Agricultural AI model",
            "description_ar": "نموذج ذكاء اصطناعي زراعي",
            "description_cn": "农业AI模型",
        }
        defaults.update(kwargs)
        return AIModelInfo(**defaults)

    def test_basic_creation(self):
        model = self._make_model()
        assert model.model_id == "agri-gpt-1"
        assert model.name == "AgriGPT"
        assert model.category == AIModelCategory.GENERAL_AGRICULTURE

    def test_has_capability(self):
        model = self._make_model()
        assert model.has_capability(ModelCapability.QA) is True
        assert model.has_capability(ModelCapability.PEST_DETECTION) is False

    def test_supports_language(self):
        model = self._make_model(
            language_support=LanguageSupport(english=True, arabic=True),
        )
        assert model.supports_language("en") is True
        assert model.supports_language("ar") is True
        assert model.supports_language("zh") is False

    def test_is_available_active(self):
        model = self._make_model(status=ModelStatus.ACTIVE)
        assert model.is_available() is True

    def test_is_available_beta(self):
        model = self._make_model(status=ModelStatus.BETA)
        assert model.is_available() is True

    def test_is_available_deprecated(self):
        model = self._make_model(status=ModelStatus.DEPRECATED)
        assert model.is_available() is False

    def test_is_available_offline(self):
        model = self._make_model(status=ModelStatus.OFFLINE)
        assert model.is_available() is False

    def test_get_display_name_english(self):
        model = self._make_model()
        assert model.get_display_name("en") == "AgriGPT"

    def test_get_display_name_arabic(self):
        model = self._make_model()
        assert model.get_display_name("ar") == "زراعة GPT"

    def test_get_display_name_chinese(self):
        model = self._make_model()
        assert model.get_display_name("zh") == "农业GPT"

    def test_get_display_name_fallback(self):
        model = self._make_model(name_ar="")
        assert model.get_display_name("ar") == "AgriGPT"

    def test_get_description(self):
        model = self._make_model()
        assert model.get_description("en") == "Agricultural AI model"
        assert model.get_description("ar") == "نموذج ذكاء اصطناعي زراعي"
        assert model.get_description("zh") == "农业AI模型"

    def test_get_description_fallback(self):
        model = self._make_model(description_cn="")
        assert model.get_description("zh") == "Agricultural AI model"

    def test_to_dict(self):
        model = self._make_model(
            developer=DeveloperInfo(name="KAFAAT"),
            endpoint=ModelEndpoint(url="https://api.example.com"),
            performance=ModelPerformance(accuracy=0.95),
            license=ModelLicense.OPEN_SOURCE,
            version="1.0",
            base_model="Qwen2",
            parameter_count="7B",
            tags=["agriculture", "arabic"],
        )
        d = model.to_dict()
        assert d["model_id"] == "agri-gpt-1"
        assert d["name"] == "AgriGPT"
        assert d["category"] == "general_agriculture"
        assert d["capabilities"] == ["qa", "decision_support"]
        assert d["architecture"] == "llm"
        assert d["status"] == "active"
        assert d["license"] == "open_source"
        assert d["developer"]["name"] == "KAFAAT"
        assert d["endpoint"]["url"] == "https://api.example.com"
        assert d["performance"]["accuracy"] == 0.95
        assert d["base_model"] == "Qwen2"
        assert d["parameter_count"] == "7B"
        assert d["tags"] == ["agriculture", "arabic"]

    def test_to_dict_minimal(self):
        model = self._make_model()
        d = model.to_dict()
        assert d["developer"] is None
        assert d["endpoint"] is None
        assert d["performance"] is None

    def test_from_dict(self):
        data = {
            "model_id": "test-1",
            "name": "TestModel",
            "name_ar": "نموذج اختبار",
            "category": "remote_sensing_geo",
            "capabilities": ["satellite_analysis", "ndvi_analysis"],
            "architecture": "cnn",
            "status": "beta",
            "license": "academic",
            "developer": {
                "name": "Test Org",
                "name_ar": "منظمة اختبار",
                "name_cn": "",
                "organization_type": "academic",
                "country": "US",
                "website": None,
                "contact_email": None,
            },
            "language_support": {
                "english": True,
                "arabic": True,
                "chinese": False,
                "spanish": False,
                "french": False,
                "hindi": False,
                "other_languages": [],
            },
        }
        model = AIModelInfo.from_dict(data)
        assert model.model_id == "test-1"
        assert model.name == "TestModel"
        assert model.category == AIModelCategory.REMOTE_SENSING_GEO
        assert ModelCapability.SATELLITE_ANALYSIS in model.capabilities
        assert model.architecture == ModelArchitecture.CNN
        assert model.status == ModelStatus.BETA
        assert model.license == ModelLicense.ACADEMIC
        assert model.developer is not None
        assert model.developer.name == "Test Org"
        assert model.language_support.english is True
        assert model.language_support.arabic is True

    def test_from_dict_minimal(self):
        data = {"model_id": "m1", "name": "Minimal"}
        model = AIModelInfo.from_dict(data)
        assert model.model_id == "m1"
        assert model.name == "Minimal"
        assert model.category == AIModelCategory.GENERAL_AGRICULTURE
        assert model.capabilities == []
        assert model.developer is None
        assert model.endpoint is None
        assert model.performance is None

    def test_roundtrip_to_dict_from_dict(self):
        original = self._make_model(
            developer=DeveloperInfo(name="KAFAAT", name_ar="كفاءت"),
            endpoint=ModelEndpoint(url="https://api.test.com"),
            performance=ModelPerformance(accuracy=0.9),
            tags=["test"],
            use_cases=["crop advisory"],
        )
        d = original.to_dict()
        restored = AIModelInfo.from_dict(d)
        assert restored.model_id == original.model_id
        assert restored.name == original.name
        assert restored.developer.name == "KAFAAT"
        assert restored.tags == ["test"]


# ─────────────────────────────────────────────────────────────────────────────
# ModelComparison Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestModelComparison:
    def test_creation(self):
        model1 = AIModelInfo(model_id="m1", name="Model A")
        model2 = AIModelInfo(model_id="m2", name="Model B")
        comp = ModelComparison(
            query="Best model for pest detection?",
            models=[model1, model2],
            responses={"m1": "Answer A", "m2": "Answer B"},
            scores={"m1": 0.8, "m2": 0.9},
            winner="m2",
        )
        assert comp.query == "Best model for pest detection?"
        assert len(comp.models) == 2
        assert comp.winner == "m2"

    def test_to_dict(self):
        model = AIModelInfo(model_id="m1", name="Model A")
        comp = ModelComparison(
            query="Q",
            models=[model],
            scores={"m1": 0.9},
            winner="m1",
        )
        d = comp.to_dict()
        assert d["query"] == "Q"
        assert d["models"] == ["m1"]
        assert d["scores"] == {"m1": 0.9}
        assert d["winner"] == "m1"

    def test_defaults(self):
        comp = ModelComparison(query="Q", models=[])
        assert comp.responses == {}
        assert comp.latencies == {}
        assert comp.scores == {}
        assert comp.winner is None
        assert comp.comparison_criteria == []


# ─────────────────────────────────────────────────────────────────────────────
# ModelDiscoveryResult Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestModelDiscoveryResult:
    def test_creation(self):
        model = AIModelInfo(model_id="m1", name="Model A")
        result = ModelDiscoveryResult(
            models=[model],
            total_count=1,
            filter_criteria={"category": "general_agriculture"},
            search_duration_ms=15.0,
        )
        assert len(result.models) == 1
        assert result.total_count == 1
        assert result.filter_criteria == {"category": "general_agriculture"}
        assert result.search_duration_ms == 15.0

    def test_to_dict(self):
        model = AIModelInfo(model_id="m1", name="Model A")
        result = ModelDiscoveryResult(models=[model], total_count=1)
        d = result.to_dict()
        assert d["total_count"] == 1
        assert len(d["models"]) == 1
        assert d["models"][0]["model_id"] == "m1"

    def test_empty(self):
        result = ModelDiscoveryResult(models=[], total_count=0)
        d = result.to_dict()
        assert d["total_count"] == 0
        assert d["models"] == []
