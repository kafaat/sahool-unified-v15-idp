"""Tests for dashboard aggregation module."""

import pytest
from shared.dashboard import DashboardAggregator, FarmDashboard


class TestDashboardAggregator:
    def setup_method(self):
        self.agg = DashboardAggregator(tenant_id="test-tenant")

    def test_ndvi_health_healthy(self):
        en, ar = self.agg.get_ndvi_health(0.72)
        assert en == "healthy"
        assert ar == "صحي"

    def test_ndvi_health_moderate(self):
        en, ar = self.agg.get_ndvi_health(0.45)
        assert en == "moderate"

    def test_ndvi_health_stressed(self):
        en, ar = self.agg.get_ndvi_health(0.3)
        assert en == "stressed"

    def test_ndvi_health_critical(self):
        en, ar = self.agg.get_ndvi_health(0.1)
        assert en == "critical"

    def test_pest_risk_levels(self):
        assert self.agg.get_pest_risk(0)[0] == "none"
        assert self.agg.get_pest_risk(1)[0] == "low"
        assert self.agg.get_pest_risk(4)[0] == "moderate"
        assert self.agg.get_pest_risk(8)[0] == "high"
        assert self.agg.get_pest_risk(15)[0] == "critical"

    def test_roi_calculation(self):
        assert self.agg.calculate_roi(185000, 42000) == pytest.approx(340.5, abs=0.5)
        assert self.agg.calculate_roi(0, 0) == 0.0

    @pytest.mark.asyncio
    async def test_build_dashboard(self):
        dashboard = await self.agg.build_dashboard(
            farm_name="Test Farm",
            farm_name_ar="مزرعة اختبار",
            ndvi_data={"average": 0.72, "fields_count": 5},
            weather_data={"temp": 28, "humidity": 65},
        )
        assert isinstance(dashboard, FarmDashboard)
        assert dashboard.ndvi.average_ndvi == 0.72
        assert dashboard.ndvi.health_status == "healthy"
        assert dashboard.weather.temperature_c == 28

    @pytest.mark.asyncio
    async def test_build_dashboard_empty(self):
        dashboard = await self.agg.build_dashboard()
        assert dashboard.ndvi.average_ndvi == 0.0
        assert dashboard.ndvi.health_status == "unknown"
