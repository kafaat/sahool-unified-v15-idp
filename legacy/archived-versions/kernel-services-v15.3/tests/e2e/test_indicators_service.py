"""
E2E Tests for Indicators Service - خدمة المؤشرات الزراعية
Tests dashboard indicators, alerts, and trends
"""

import pytest
import httpx
from conftest import INDICATORS_URL, TEST_FIELD_ID, TEST_TENANT_ID


class TestIndicatorsServiceHealth:
    """Health check tests for indicators service."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: httpx.AsyncClient):
        """Test /healthz returns healthy status."""
        response = await async_client.get(f"{INDICATORS_URL}/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "indicator_count" in data
        assert data["indicator_count"] >= 20  # At least 20 indicators


class TestIndicatorDefinitions:
    """Tests for /v1/indicators/definitions endpoint."""

    @pytest.mark.asyncio
    async def test_get_all_indicator_definitions(self, async_client: httpx.AsyncClient):
        """Test listing all indicator definitions."""
        response = await async_client.get(f"{INDICATORS_URL}/v1/indicators/definitions")
        assert response.status_code == 200
        data = response.json()

        assert "indicators" in data
        indicators = data["indicators"]

        # Should have at least 20 indicators across 7 categories
        assert len(indicators) >= 20

        # Check indicator structure
        for indicator in indicators:
            assert "id" in indicator
            assert "name" in indicator
            assert "name_ar" in indicator
            assert "category" in indicator
            assert "unit" in indicator
            assert "range" in indicator

            # Range should have min/max
            assert "min" in indicator["range"]
            assert "max" in indicator["range"]

    @pytest.mark.asyncio
    async def test_indicator_categories(self, async_client: httpx.AsyncClient):
        """Test that all 7 categories are present."""
        response = await async_client.get(f"{INDICATORS_URL}/v1/indicators/definitions")
        data = response.json()

        categories = set(ind["category"] for ind in data["indicators"])

        expected_categories = [
            "vegetation", "water", "soil", "weather",
            "crop_health", "productivity", "financial"
        ]

        for expected in expected_categories:
            assert expected in categories

    @pytest.mark.asyncio
    async def test_indicator_thresholds(self, async_client: httpx.AsyncClient):
        """Test that indicators have warning thresholds."""
        response = await async_client.get(f"{INDICATORS_URL}/v1/indicators/definitions")
        data = response.json()

        # NDVI should have thresholds
        ndvi = next(ind for ind in data["indicators"] if ind["id"] == "ndvi")
        assert "thresholds" in ndvi or "optimal_range" in ndvi


class TestFieldIndicators:
    """Tests for /v1/field/{field_id}/indicators endpoint."""

    @pytest.mark.asyncio
    async def test_get_field_indicators(self, async_client: httpx.AsyncClient):
        """Test getting indicators for a specific field."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/field/{TEST_FIELD_ID}/indicators"
        )
        assert response.status_code == 200
        data = response.json()

        assert "field_id" in data
        assert "indicators" in data
        assert "last_updated" in data

        indicators = data["indicators"]

        # Should have multiple indicator values
        assert len(indicators) > 0

        for indicator in indicators:
            assert "id" in indicator
            assert "value" in indicator
            assert "status" in indicator
            assert "trend" in indicator

            # Status should be one of expected values
            assert indicator["status"] in ["optimal", "good", "warning", "critical"]
            # Trend should indicate direction
            assert indicator["trend"] in ["up", "down", "stable"]

    @pytest.mark.asyncio
    async def test_field_indicators_by_category(self, async_client: httpx.AsyncClient):
        """Test filtering indicators by category."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/field/{TEST_FIELD_ID}/indicators",
            params={"category": "vegetation"}
        )
        assert response.status_code == 200
        data = response.json()

        # All returned indicators should be vegetation category
        for indicator in data["indicators"]:
            assert indicator["category"] == "vegetation"


class TestTenantDashboard:
    """Tests for /v1/dashboard/{tenant_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self, async_client: httpx.AsyncClient):
        """Test tenant dashboard aggregation."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/dashboard/{TEST_TENANT_ID}"
        )
        assert response.status_code == 200
        data = response.json()

        assert "tenant_id" in data
        assert "summary" in data
        assert "fields_count" in data
        assert "alerts_count" in data

        summary = data["summary"]

        # Summary should have key metrics
        assert "average_ndvi" in summary or "vegetation_health" in summary
        assert "water_status" in summary or "irrigation_efficiency" in summary
        assert "overall_score" in summary

        # Overall score should be 0-100
        assert 0 <= summary["overall_score"] <= 100

    @pytest.mark.asyncio
    async def test_dashboard_field_breakdown(self, async_client: httpx.AsyncClient):
        """Test dashboard includes per-field breakdown."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/dashboard/{TEST_TENANT_ID}"
        )
        data = response.json()

        assert "fields" in data

        for field in data["fields"]:
            assert "field_id" in field
            assert "name" in field
            assert "health_score" in field
            assert "status" in field


class TestAlertsEndpoint:
    """Tests for /v1/alerts/{tenant_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_tenant_alerts(self, async_client: httpx.AsyncClient):
        """Test getting alerts for a tenant."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/alerts/{TEST_TENANT_ID}"
        )
        assert response.status_code == 200
        data = response.json()

        assert "tenant_id" in data
        assert "alerts" in data

        for alert in data["alerts"]:
            assert "id" in alert
            assert "field_id" in alert
            assert "indicator_id" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "message_ar" in alert
            assert "created_at" in alert

            # Severity validation
            assert alert["severity"] in ["info", "warning", "critical"]

    @pytest.mark.asyncio
    async def test_filter_alerts_by_severity(self, async_client: httpx.AsyncClient):
        """Test filtering alerts by severity level."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/alerts/{TEST_TENANT_ID}",
            params={"severity": "critical"}
        )
        assert response.status_code == 200
        data = response.json()

        for alert in data["alerts"]:
            assert alert["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_alerts_have_recommendations(self, async_client: httpx.AsyncClient):
        """Test that alerts include action recommendations."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/alerts/{TEST_TENANT_ID}"
        )
        data = response.json()

        # Critical alerts should have recommendations
        critical_alerts = [a for a in data["alerts"] if a["severity"] == "critical"]

        for alert in critical_alerts:
            assert "recommendation" in alert or "action" in alert


class TestTrends:
    """Tests for /v1/trends/{field_id}/{indicator_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_indicator_trend(self, async_client: httpx.AsyncClient):
        """Test historical trend for an indicator."""
        response = await async_client.get(
            f"{INDICATORS_URL}/v1/trends/{TEST_FIELD_ID}/ndvi",
            params={"days": 30}
        )
        assert response.status_code == 200
        data = response.json()

        assert "field_id" in data
        assert "indicator_id" in data
        assert "trend_data" in data
        assert "trend_direction" in data
        assert "change_percent" in data

        trend_data = data["trend_data"]
        assert len(trend_data) > 0

        for point in trend_data:
            assert "date" in point
            assert "value" in point

    @pytest.mark.asyncio
    async def test_trend_different_periods(self, async_client: httpx.AsyncClient):
        """Test trends for different time periods."""
        for days in [7, 30, 90, 365]:
            response = await async_client.get(
                f"{INDICATORS_URL}/v1/trends/{TEST_FIELD_ID}/ndvi",
                params={"days": days}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_trend_multiple_indicators(self, async_client: httpx.AsyncClient):
        """Test trends for various indicators."""
        indicators = ["ndvi", "soil_moisture", "temperature", "yield_estimate"]

        for indicator in indicators:
            response = await async_client.get(
                f"{INDICATORS_URL}/v1/trends/{TEST_FIELD_ID}/{indicator}",
                params={"days": 30}
            )
            # Should either succeed or return 404 if indicator not tracked
            assert response.status_code in [200, 404]
