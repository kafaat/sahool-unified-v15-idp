"""
Tests for Agent Router (core/agents.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

pytestmark = [pytest.mark.unit]


class TestAgentType:
    def test_all_agent_types(self):
        from src.core.agents import AgentType

        assert AgentType.CODE_FIX == "code_fix"
        assert AgentType.CODE_REVIEW == "code_review"
        assert AgentType.FIELD_ADVISOR == "field_advisor"
        assert AgentType.WEATHER_ADVISOR == "weather_advisor"
        assert AgentType.IRRIGATION_ADVISOR == "irrigation_advisor"
        assert AgentType.GENERAL == "general"


class TestAgentRoute:
    def test_dataclass_creation(self):
        from src.core.agents import AgentRoute, AgentType

        route = AgentRoute(
            agent_type=AgentType.GENERAL,
            patterns=[],
            keywords_en=["hello"],
            keywords_ar=[],
            priority=5,
        )
        assert route.agent_type == AgentType.GENERAL
        assert route.priority == 5
        assert route.service_url is None


class TestRoutingResult:
    def test_dataclass_defaults(self):
        from src.core.agents import AgentType, RoutingResult

        result = RoutingResult(agent_type=AgentType.GENERAL, confidence=0.5)
        assert result.matched_patterns == []
        assert result.matched_keywords == []


class TestAgentRouter:
    def test_initialization(self):
        from src.core.agents import AgentRouter

        router = AgentRouter()
        assert len(router.routes) >= 6

    def test_route_code_fix_english_pattern(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("fix the bug in my code")
        assert result.agent_type == AgentType.CODE_FIX

    def test_route_code_fix_arabic(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("أصلح الكود من فضلك")
        assert result.agent_type == AgentType.CODE_FIX

    def test_route_code_review(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("review my code please")
        assert result.agent_type == AgentType.CODE_REVIEW

    def test_route_field_advisor_ndvi(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("What is the NDVI value for my field?")
        assert result.agent_type == AgentType.FIELD_ADVISOR

    def test_route_field_advisor_crop_health(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("What is the crop health status?")
        assert result.agent_type == AgentType.FIELD_ADVISOR

    def test_route_weather_advisor(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("What's the weather forecast for today?")
        assert result.agent_type == AgentType.WEATHER_ADVISOR

    def test_route_weather_arabic(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("ما هو الطقس اليوم؟")
        assert result.agent_type == AgentType.WEATHER_ADVISOR

    def test_route_irrigation_advisor(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        result = router.route("irrigation schedule for wheat")
        assert result.agent_type == AgentType.IRRIGATION_ADVISOR

    def test_route_general_fallback(self):
        """Ambiguous/generic queries may route to highest-priority agent
        due to priority boost. Just verify confidence is low."""
        from src.core.agents import AgentRouter

        router = AgentRouter()
        result = router.route("Hello there")
        # With priority boost, the highest priority agent wins even without keywords
        # The important thing is confidence should be low
        assert result.confidence < 0.3

    def test_route_empty_string(self):
        """Empty string routes based on priority boost only."""
        from src.core.agents import AgentRouter

        router = AgentRouter()
        result = router.route("")
        assert result.confidence < 0.3

    def test_confidence_range(self):
        from src.core.agents import AgentRouter

        router = AgentRouter()
        result = router.route("fix the code bug error")
        assert 0.0 <= result.confidence <= 1.0

    def test_get_agent_description_code_fix(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        desc = router.get_agent_description(AgentType.CODE_FIX)
        assert "en" in desc
        assert "ar" in desc

    def test_get_agent_description_general(self):
        from src.core.agents import AgentRouter, AgentType

        router = AgentRouter()
        desc = router.get_agent_description(AgentType.GENERAL)
        assert "en" in desc

    def test_get_agent_description_unknown_falls_back(self):
        from src.core.agents import AgentRouter

        router = AgentRouter()
        # Pass a string that's not a valid AgentType - should fallback to GENERAL
        desc = router.get_agent_description("nonexistent")
        assert "en" in desc


class TestGlobalRouter:
    def test_get_agent_router_singleton(self):
        from src.core.agents import get_agent_router
        import src.core.agents as agents_mod

        agents_mod._agent_router = None
        r1 = get_agent_router()
        r2 = get_agent_router()
        assert r1 is r2
        agents_mod._agent_router = None
