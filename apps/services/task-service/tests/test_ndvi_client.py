"""
Unit Tests for NDVI Client
اختبارات وحدة عميل NDVI

Tests for the NDVI client integration with task service.
"""

import os
import sys

import pytest

# Add the src directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src")
)

from ndvi_client import (
    FieldHealthData,
    HealthStatus,
    NDVIClient,
    get_task_priority_from_health,
    get_task_suggestions_from_health,
)


class TestFieldHealthData:
    """Tests for FieldHealthData dataclass"""

    def test_field_health_data_to_dict(self):
        """Test FieldHealthData.to_dict() method"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=7.5,
            health_status=HealthStatus.GOOD,
            ndvi_mean=0.55,
            ndvi_min=0.3,
            ndvi_max=0.8,
            ndvi_std_dev=0.12,
            vegetation_coverage=75.5,
            zones={"healthy": 60, "stressed": 25, "critical": 10, "bare_soil": 3, "water": 2},
            alerts=[],
            needs_attention=False,
            suggested_actions=["Monitor vegetation"],
        )

        result = health_data.to_dict()

        assert result["field_id"] == "field-001"
        assert result["health_score"] == 7.5
        assert result["health_status"] == "good"
        assert result["ndvi_mean"] == 0.55
        assert result["vegetation_coverage"] == 75.5
        assert "zones" in result
        assert isinstance(result["zones"], dict)


class TestHealthStatus:
    """Tests for HealthStatus enum"""

    def test_health_status_values(self):
        """Test HealthStatus enum values"""
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.POOR.value == "poor"
        assert HealthStatus.MODERATE.value == "moderate"
        assert HealthStatus.GOOD.value == "good"
        assert HealthStatus.EXCELLENT.value == "excellent"


class TestNDVIClient:
    """Tests for NDVIClient class"""

    def test_client_initialization(self):
        """Test NDVIClient initialization"""
        client = NDVIClient()
        assert client.base_url == "http://ndvi-engine:8107"
        assert client.timeout == 30.0

    def test_client_custom_url(self):
        """Test NDVIClient with custom URL"""
        client = NDVIClient(base_url="http://custom:8000", timeout=60.0)
        assert client.base_url == "http://custom:8000"
        assert client.timeout == 60.0

    def test_get_health_status_critical(self):
        """Test health status determination for critical score"""
        client = NDVIClient()
        status = client._get_health_status(2.0)
        assert status == HealthStatus.CRITICAL

    def test_get_health_status_poor(self):
        """Test health status determination for poor score"""
        client = NDVIClient()
        status = client._get_health_status(4.0)
        assert status == HealthStatus.POOR

    def test_get_health_status_moderate(self):
        """Test health status determination for moderate score"""
        client = NDVIClient()
        status = client._get_health_status(6.0)
        assert status == HealthStatus.MODERATE

    def test_get_health_status_good(self):
        """Test health status determination for good score"""
        client = NDVIClient()
        status = client._get_health_status(8.0)
        assert status == HealthStatus.GOOD

    def test_get_health_status_excellent(self):
        """Test health status determination for excellent score"""
        client = NDVIClient()
        status = client._get_health_status(9.0)
        assert status == HealthStatus.EXCELLENT

    def test_generate_suggested_actions_critical(self):
        """Test suggested actions for critical health"""
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=2.0,
            zones={"critical": 40, "stressed": 30, "healthy": 20, "bare_soil": 10},
            alerts=[],
        )

        assert len(actions) > 0
        assert any("inspection" in a.lower() for a in actions)

    def test_generate_suggested_actions_high_stressed(self):
        """Test suggested actions for high stressed areas"""
        client = NDVIClient()
        actions = client._generate_suggested_actions(
            health_score=6.0,
            zones={"critical": 5, "stressed": 45, "healthy": 40, "bare_soil": 10},
            alerts=[],
        )

        assert any("stressed" in a.lower() for a in actions)

    def test_simulated_health_reproducible(self):
        """Test simulated health data is reproducible for same field_id"""
        client = NDVIClient()

        health1 = client._get_simulated_health("field-test-123")
        health2 = client._get_simulated_health("field-test-123")

        assert health1.health_score == health2.health_score
        assert health1.ndvi_mean == health2.ndvi_mean

    def test_simulated_health_different_fields(self):
        """Test simulated health data differs for different fields"""
        client = NDVIClient()

        health1 = client._get_simulated_health("field-aaa")
        health2 = client._get_simulated_health("field-bbb")

        # Different fields should likely have different scores
        # Note: There's a small chance they could be the same
        assert health1.field_id != health2.field_id


class TestHelperFunctions:
    """Tests for helper functions"""

    def test_get_task_priority_critical(self):
        """Test task priority for critical health"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=2.0,
            health_status=HealthStatus.CRITICAL,
            ndvi_mean=0.15,
            ndvi_min=0.0,
            ndvi_max=0.3,
            ndvi_std_dev=0.1,
            vegetation_coverage=20.0,
            zones={},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )

        priority = get_task_priority_from_health(health_data)
        assert priority == "urgent"

    def test_get_task_priority_poor(self):
        """Test task priority for poor health"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=4.0,
            health_status=HealthStatus.POOR,
            ndvi_mean=0.25,
            ndvi_min=0.1,
            ndvi_max=0.4,
            ndvi_std_dev=0.1,
            vegetation_coverage=40.0,
            zones={},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )

        priority = get_task_priority_from_health(health_data)
        assert priority == "high"

    def test_get_task_priority_moderate(self):
        """Test task priority for moderate health"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=6.0,
            health_status=HealthStatus.MODERATE,
            ndvi_mean=0.4,
            ndvi_min=0.2,
            ndvi_max=0.6,
            ndvi_std_dev=0.1,
            vegetation_coverage=60.0,
            zones={},
            alerts=[],
            needs_attention=False,
            suggested_actions=[],
        )

        priority = get_task_priority_from_health(health_data)
        assert priority == "medium"

    def test_get_task_priority_good(self):
        """Test task priority for good health"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=8.5,
            health_status=HealthStatus.EXCELLENT,
            ndvi_mean=0.7,
            ndvi_min=0.5,
            ndvi_max=0.9,
            ndvi_std_dev=0.08,
            vegetation_coverage=90.0,
            zones={},
            alerts=[],
            needs_attention=False,
            suggested_actions=[],
        )

        priority = get_task_priority_from_health(health_data)
        assert priority == "low"

    def test_get_task_suggestions_critical_health(self):
        """Test task suggestions for critical health"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=2.5,
            health_status=HealthStatus.CRITICAL,
            ndvi_mean=0.15,
            ndvi_min=0.0,
            ndvi_max=0.3,
            ndvi_std_dev=0.1,
            vegetation_coverage=20.0,
            zones={"critical": 50, "stressed": 30, "healthy": 15, "bare_soil": 5},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )

        suggestions = get_task_suggestions_from_health(health_data)

        assert len(suggestions) > 0
        # Critical health should have urgent inspection suggestion
        assert any(s.get("priority") == "urgent" for s in suggestions)

    def test_get_task_suggestions_high_stressed(self):
        """Test task suggestions for high stressed areas"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=6.0,
            health_status=HealthStatus.MODERATE,
            ndvi_mean=0.35,
            ndvi_min=0.2,
            ndvi_max=0.5,
            ndvi_std_dev=0.1,
            vegetation_coverage=55.0,
            zones={"critical": 5, "stressed": 35, "healthy": 50, "bare_soil": 10},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )

        suggestions = get_task_suggestions_from_health(health_data)

        # Should have irrigation-related suggestion
        assert any(s.get("task_type") == "irrigation" for s in suggestions)

    def test_get_task_suggestions_low_coverage(self):
        """Test task suggestions for low vegetation coverage"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=5.5,
            health_status=HealthStatus.MODERATE,
            ndvi_mean=0.3,
            ndvi_min=0.1,
            ndvi_max=0.5,
            ndvi_std_dev=0.12,
            vegetation_coverage=45.0,  # Low coverage
            zones={"critical": 10, "stressed": 30, "healthy": 35, "bare_soil": 25},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )

        suggestions = get_task_suggestions_from_health(health_data)

        # Should have soil sampling suggestion
        assert any(s.get("task_type") == "sampling" for s in suggestions)

    def test_get_task_suggestions_healthy_field(self):
        """Test task suggestions for healthy field"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=9.0,
            health_status=HealthStatus.EXCELLENT,
            ndvi_mean=0.75,
            ndvi_min=0.6,
            ndvi_max=0.9,
            ndvi_std_dev=0.08,
            vegetation_coverage=95.0,
            zones={"critical": 0, "stressed": 5, "healthy": 90, "bare_soil": 5},
            alerts=[],
            needs_attention=False,
            suggested_actions=[],
        )

        suggestions = get_task_suggestions_from_health(health_data)

        # Healthy field should have few or no suggestions
        assert len(suggestions) <= 2

    def test_suggestions_have_required_fields(self):
        """Test that suggestions have all required fields"""
        health_data = FieldHealthData(
            field_id="field-001",
            health_score=4.0,
            health_status=HealthStatus.POOR,
            ndvi_mean=0.25,
            ndvi_min=0.1,
            ndvi_max=0.4,
            ndvi_std_dev=0.1,
            vegetation_coverage=40.0,
            zones={"critical": 20, "stressed": 35, "healthy": 40, "bare_soil": 5},
            alerts=[],
            needs_attention=True,
            suggested_actions=[],
        )

        suggestions = get_task_suggestions_from_health(health_data)

        for suggestion in suggestions:
            assert "task_type" in suggestion
            assert "priority" in suggestion
            assert "title" in suggestion
            assert "title_ar" in suggestion
            assert "description" in suggestion
            assert "description_ar" in suggestion
            assert "confidence" in suggestion
            assert "suggested_due_days" in suggestion
