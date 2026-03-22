"""
Extended unit tests for NDVI Client module.
اختبارات موسعة لوحدة عميل NDVI
"""

import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ndvi_client import (
    AlertSeverity,
    FieldHealthData,
    HealthStatus,
    NDVIClient,
    get_ndvi_client,
    get_task_priority_from_health,
    get_task_suggestions_from_health,
)


class TestFieldHealthDataValidation:
    """Tests for FieldHealthData validation"""

    def test_valid_ndvi_range(self):
        data = FieldHealthData(
            field_id="f1",
            health_score=7.0,
            health_status=HealthStatus.GOOD,
            ndvi_mean=0.5,
            ndvi_min=-0.1,
            ndvi_max=0.9,
            ndvi_std_dev=0.1,
            vegetation_coverage=70.0,
            zones={},
            alerts=[],
            needs_attention=False,
            suggested_actions=[],
        )
        assert data.ndvi_mean == 0.5

    def test_invalid_ndvi_mean_raises(self):
        with pytest.raises(ValueError, match="outside valid NDVI range"):
            FieldHealthData(
                field_id="f1",
                health_score=5.0,
                health_status=HealthStatus.MODERATE,
                ndvi_mean=1.5,  # Invalid: > 1.0
                ndvi_min=0.0,
                ndvi_max=0.8,
                ndvi_std_dev=0.1,
                vegetation_coverage=50.0,
                zones={},
                alerts=[],
                needs_attention=True,
                suggested_actions=[],
            )

    def test_invalid_ndvi_min_raises(self):
        with pytest.raises(ValueError, match="outside valid NDVI range"):
            FieldHealthData(
                field_id="f1",
                health_score=5.0,
                health_status=HealthStatus.MODERATE,
                ndvi_mean=0.5,
                ndvi_min=-1.5,  # Invalid: < -1.0
                ndvi_max=0.8,
                ndvi_std_dev=0.1,
                vegetation_coverage=50.0,
                zones={},
                alerts=[],
                needs_attention=True,
                suggested_actions=[],
            )

    def test_to_dict_rounding(self):
        data = FieldHealthData(
            field_id="f1",
            health_score=7.123456,
            health_status=HealthStatus.GOOD,
            ndvi_mean=0.55555,
            ndvi_min=0.33333,
            ndvi_max=0.77777,
            ndvi_std_dev=0.11111,
            vegetation_coverage=75.5555,
            zones={"healthy": 80},
            alerts=[],
            needs_attention=False,
            suggested_actions=["Monitor"],
        )
        d = data.to_dict()
        assert d["ndvi_mean"] == round(0.55555, 4)
        assert d["ndvi_min"] == round(0.33333, 4)
        assert d["ndvi_max"] == round(0.77777, 4)
        assert d["vegetation_coverage"] == round(75.5555, 2)


class TestAlertSeverity:
    """Tests for AlertSeverity enum"""

    def test_values(self):
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.CRITICAL == "critical"


class TestNDVIClientInit:
    """Tests for NDVIClient initialization"""

    def test_default_url(self):
        client = NDVIClient()
        assert "vegetation-analysis-service" in client.base_url
        assert client.timeout == 30.0

    def test_custom_url_trailing_slash(self):
        client = NDVIClient(base_url="http://custom:8000/")
        assert client.base_url == "http://custom:8000"  # trailing slash removed

    def test_client_initially_none(self):
        client = NDVIClient()
        assert client._client is None


class TestNDVIClientGetClient:
    """Tests for NDVIClient._get_client"""

    @pytest.mark.asyncio
    async def test_creates_client(self):
        client = NDVIClient()
        http_client = await client._get_client()
        assert http_client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_reuses_client(self):
        client = NDVIClient()
        c1 = await client._get_client()
        c2 = await client._get_client()
        assert c1 is c2
        await client.close()


class TestNDVIClientClose:
    """Tests for NDVIClient.close"""

    @pytest.mark.asyncio
    async def test_close_open_client(self):
        client = NDVIClient()
        await client._get_client()
        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_close_no_client(self):
        client = NDVIClient()
        # No client created, should not raise
        await client.close()


class TestNDVIClientHealthStatus:
    """Tests for health status determination"""

    def test_boundary_values(self):
        client = NDVIClient()
        # Test exact boundary values
        assert client._get_health_status(2.9) == HealthStatus.CRITICAL
        assert client._get_health_status(3.0) == HealthStatus.POOR
        assert client._get_health_status(4.9) == HealthStatus.POOR
        assert client._get_health_status(5.0) == HealthStatus.MODERATE
        assert client._get_health_status(6.9) == HealthStatus.MODERATE
        assert client._get_health_status(7.0) == HealthStatus.GOOD
        assert client._get_health_status(8.4) == HealthStatus.GOOD
        assert client._get_health_status(8.5) == HealthStatus.EXCELLENT
        assert client._get_health_status(10.0) == HealthStatus.EXCELLENT


class TestNDVIClientSuggestedActions:
    """Tests for suggested actions generation"""

    def test_max_five_actions(self):
        client = NDVIClient()
        # Create conditions that generate many actions
        actions = client._generate_suggested_actions(
            health_score=1.0,
            zones={"critical": 50, "stressed": 50, "bare_soil": 25},
            alerts=[
                {"type": "low_vegetation"},
                {"type": "non_uniform_growth"},
            ],
        )
        assert len(actions) <= 5

    def test_bare_soil_action(self):
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=8.0,
            zones={"critical": 0, "stressed": 5, "bare_soil": 20},
            alerts=[],
        )
        assert any("bare soil" in a.lower() for a in actions)

    def test_low_vegetation_alert(self):
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=8.0,
            zones={"critical": 0, "stressed": 5, "bare_soil": 5},
            alerts=[{"type": "low_vegetation"}],
        )
        assert any("nutrient" in a.lower() for a in actions)

    def test_non_uniform_growth_alert(self):
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=8.0,
            zones={"critical": 0, "stressed": 5, "bare_soil": 5},
            alerts=[{"type": "non_uniform_growth"}],
        )
        assert any("pattern" in a.lower() or "growth" in a.lower() for a in actions)

    def test_no_actions_for_excellent(self):
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=9.5,
            zones={"critical": 0, "stressed": 2, "bare_soil": 3},
            alerts=[],
        )
        assert len(actions) == 0

    def test_poor_health_actions(self):
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=4.0,
            zones={"critical": 5, "stressed": 10, "bare_soil": 5},
            alerts=[],
        )
        assert any("inspection" in a.lower() or "24 hours" in a.lower() for a in actions)


class TestNDVIClientParseResponse:
    """Tests for _parse_ndvi_response"""

    def test_basic_parse(self):
        client = NDVIClient()
        data = {
            "statistics": {
                "mean": 0.6,
                "min": 0.3,
                "max": 0.9,
                "std_dev": 0.1,
                "coverage_percent": 80.0,
            },
            "zones": {"healthy": 70, "stressed": 20, "critical": 5, "bare_soil": 5},
            "alerts": [],
            "health_score": 8.0,
        }

        result = client._parse_ndvi_response("field_1", data)
        assert result.field_id == "field_1"
        assert result.health_score == 8.0
        assert result.health_status == HealthStatus.GOOD
        assert result.ndvi_mean == 0.6
        assert result.needs_attention is False

    def test_needs_attention_low_score(self):
        client = NDVIClient()
        data = {
            "statistics": {"mean": 0.3, "min": 0.1, "max": 0.5, "std_dev": 0.1, "coverage_percent": 40.0},
            "zones": {"healthy": 30, "stressed": 40, "critical": 20, "bare_soil": 10},
            "alerts": [],
            "health_score": 4.0,
        }
        result = client._parse_ndvi_response("f1", data)
        assert result.needs_attention is True

    def test_needs_attention_high_critical(self):
        client = NDVIClient()
        data = {
            "statistics": {"mean": 0.5, "min": 0.2, "max": 0.8, "std_dev": 0.1, "coverage_percent": 60.0},
            "zones": {"healthy": 50, "stressed": 20, "critical": 15, "bare_soil": 15},
            "alerts": [],
            "health_score": 7.5,
        }
        result = client._parse_ndvi_response("f1", data)
        assert result.needs_attention is True  # critical > 10

    def test_needs_attention_alerts(self):
        client = NDVIClient()
        data = {
            "statistics": {"mean": 0.6, "min": 0.4, "max": 0.8, "std_dev": 0.08, "coverage_percent": 80.0},
            "zones": {"healthy": 80, "stressed": 10, "critical": 5, "bare_soil": 5},
            "alerts": [{"type": "low_vegetation", "severity": "medium"}],
            "health_score": 8.0,
        }
        result = client._parse_ndvi_response("f1", data)
        assert result.needs_attention is True  # has alerts


class TestGetNdviClient:
    """Tests for get_ndvi_client singleton"""

    def test_returns_client(self):
        import src.ndvi_client as module
        old = module._ndvi_client
        module._ndvi_client = None
        client = get_ndvi_client()
        assert isinstance(client, NDVIClient)
        # Reset
        module._ndvi_client = old

    def test_returns_same_instance(self):
        import src.ndvi_client as module
        old = module._ndvi_client
        module._ndvi_client = None
        c1 = get_ndvi_client()
        c2 = get_ndvi_client()
        assert c1 is c2
        module._ndvi_client = old


class TestTaskSuggestionsFromHealth:
    """Extended tests for get_task_suggestions_from_health"""

    def test_high_variance_suggestion(self):
        health = FieldHealthData(
            field_id="f1",
            health_score=7.5,
            health_status=HealthStatus.GOOD,
            ndvi_mean=0.6,
            ndvi_min=0.3,
            ndvi_max=0.9,
            ndvi_std_dev=0.2,  # High variance
            vegetation_coverage=80.0,
            zones={"critical": 0, "stressed": 10, "healthy": 85, "bare_soil": 5},
            alerts=[],
            needs_attention=False,
            suggested_actions=[],
        )
        suggestions = get_task_suggestions_from_health(health)
        assert any(s.get("task_type") == "scouting" for s in suggestions)
        assert any("variation" in s.get("title", "").lower() or "Variation" in s.get("title", "") for s in suggestions)

    def test_poor_health_includes_inspection(self):
        health = FieldHealthData(
            field_id="f1",
            health_score=4.0,
            health_status=HealthStatus.POOR,
            ndvi_mean=0.25,
            ndvi_min=0.1,
            ndvi_max=0.4,
            ndvi_std_dev=0.08,
            vegetation_coverage=40.0,
            zones={"critical": 15, "stressed": 30, "healthy": 45, "bare_soil": 10},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )
        suggestions = get_task_suggestions_from_health(health)
        assert any("Inspection" in s.get("title", "") or "inspection" in s.get("title", "").lower() for s in suggestions)

    def test_critical_confidence_higher(self):
        health = FieldHealthData(
            field_id="f1",
            health_score=2.0,
            health_status=HealthStatus.CRITICAL,
            ndvi_mean=0.1,
            ndvi_min=0.0,
            ndvi_max=0.2,
            ndvi_std_dev=0.05,
            vegetation_coverage=15.0,
            zones={"critical": 60, "stressed": 25, "healthy": 10, "bare_soil": 5},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )
        suggestions = get_task_suggestions_from_health(health)
        # Critical should have 0.9 confidence
        urgent_suggestion = [s for s in suggestions if s.get("priority") == "urgent"]
        if urgent_suggestion:
            assert urgent_suggestion[0]["confidence"] == 0.9
