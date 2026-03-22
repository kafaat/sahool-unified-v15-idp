"""
Comprehensive tests for Irrigation Cycle Engine
اختبارات شاملة لمحرك دورة الري

Covers: Pydantic models, ET0 calculation, irrigation cycle, schedule generation,
engine initialization, edge cases, recommendations logic
"""

import math
import os
import sys
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.main import (
    CropInfoResponse,
    ET0Request,
    ET0Response,
    IrrigationCycleEngine,
    IrrigationCycleRequest,
    IrrigationCycleResponse,
    ScheduleDay,
    ScheduleRequest,
    ScheduleResponse,
    WeatherInput,
    YemenCropListResponse,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestWeatherInput:
    """Tests for WeatherInput model."""

    def test_basic_creation(self):
        w = WeatherInput(date=date(2026, 1, 15), temp_min_c=5.0, temp_max_c=25.0)
        assert w.temp_min_c == 5.0
        assert w.temp_max_c == 25.0
        assert w.humidity_min_pct == 30.0  # default
        assert w.humidity_max_pct == 70.0  # default
        assert w.wind_speed_2m_ms == 2.0  # default
        assert w.solar_radiation_mjm2 == 20.0  # default
        assert w.rainfall_mm == 0.0  # default

    def test_all_fields(self):
        w = WeatherInput(
            date=date(2026, 6, 1),
            temp_min_c=20.0,
            temp_max_c=40.0,
            humidity_min_pct=15.0,
            humidity_max_pct=50.0,
            wind_speed_2m_ms=4.5,
            solar_radiation_mjm2=28.0,
            rainfall_mm=12.5,
        )
        assert w.rainfall_mm == 12.5
        assert w.wind_speed_2m_ms == 4.5


class TestET0Models:
    """Tests for ET0 request/response models."""

    def test_et0_request(self):
        req = ET0Request(
            latitude=15.0,
            elevation_m=500,
            weather=[WeatherInput(date=date(2026, 1, 1), temp_min_c=10, temp_max_c=25)],
        )
        assert req.latitude == 15.0
        assert len(req.weather) == 1

    def test_et0_request_requires_weather(self):
        with pytest.raises(Exception):
            ET0Request(latitude=15.0, elevation_m=500, weather=[])

    def test_et0_response(self):
        resp = ET0Response(date=date(2026, 1, 1), et0_mm=4.5)
        assert resp.et0_mm == 4.5
        assert resp.method == "penman_monteith_fao56"


class TestIrrigationCycleModels:
    """Tests for irrigation cycle request/response models."""

    def test_cycle_request_minimal(self):
        req = IrrigationCycleRequest(
            crop="wheat",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=5.0,
        )
        assert req.crop == "wheat"
        assert req.root_depth_m == 1.0  # default
        assert req.bulk_density == 1.4  # default
        assert req.depletion_fraction == 0.5  # default
        assert req.alpha == 1.0
        assert req.beta == 1.0
        assert req.gamma == 1.0
        assert req.kc is None
        assert req.ec_water is None

    def test_cycle_request_full(self):
        req = IrrigationCycleRequest(
            crop="tomato",
            growth_stage="flowering",
            field_capacity=0.28,
            wilting_point=0.10,
            root_depth_m=0.6,
            bulk_density=1.35,
            depletion_fraction=0.4,
            et0_mm_day=6.0,
            kc=1.15,
            ec_water=2.5,
            ec_soil=3.0,
            alpha=0.95,
            beta=1.05,
            gamma=0.9,
        )
        assert req.kc == 1.15
        assert req.ec_water == 2.5

    def test_cycle_response(self):
        resp = IrrigationCycleResponse(
            cycle_days=7.5,
            net_irrigation_mm=45.0,
            gross_irrigation_mm=52.9,
            etc_mm_day=4.5,
            kc_used=1.0,
            total_water_mm=52.9,
            available_water_mm=180.0,
            readily_available_mm=90.0,
            crop_name="wheat",
            crop_name_ar="القمح",
        )
        assert resp.cycle_days == 7.5
        assert resp.crop_name_ar == "القمح"
        assert resp.recommendations == []

    def test_schedule_day(self):
        day = ScheduleDay(
            date=date(2026, 1, 15),
            day_of_season=1,
            growth_stage="initial",
            kc=0.4,
            et0_mm=4.0,
            etc_mm=1.6,
            soil_moisture_pct=80.0,
            irrigate=False,
            irrigation_mm=0.0,
            cumulative_water_mm=0.0,
        )
        assert day.irrigate is False
        assert day.kc == 0.4


class TestScheduleModels:
    """Tests for schedule request/response models."""

    def test_schedule_request_defaults(self):
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
        )
        assert req.days == 30
        assert req.field_area_ha == 1.0
        assert req.irrigation_efficiency == 0.85
        assert req.ec_water is None

    def test_schedule_request_max_days(self):
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="prof",
            climate_zone="zone",
            start_date=date(2026, 1, 1),
            days=365,
        )
        assert req.days == 365

    def test_schedule_request_invalid_days(self):
        with pytest.raises(Exception):
            ScheduleRequest(
                crop="wheat",
                soil_profile="prof",
                climate_zone="zone",
                start_date=date(2026, 1, 1),
                days=0,
            )

    def test_yemen_crop_list_response(self):
        resp = YemenCropListResponse(crops=[{"name": "wheat"}], total=1)
        assert resp.total == 1

    def test_crop_info_response(self):
        resp = CropInfoResponse(
            name="Wheat",
            name_ar="القمح",
            crop_type="cereal",
            root_depth_m=1.2,
            depletion_fraction=0.55,
            growth_stages=[],
            salinity_threshold_dsm=6.0,
            regions=["highlands"],
        )
        assert resp.crop_type == "cereal"


# ═══════════════════════════════════════════════════════════════════════════════
# IrrigationCycleEngine Core Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIrrigationCycleEngineInit:
    """Tests for engine initialization."""

    def test_engine_creates_without_shared_modules(self):
        """Engine should initialize even without shared Yemen modules."""
        engine = IrrigationCycleEngine()
        assert engine._yemen_crops is not None  # Could be {} or real data
        assert engine._yemen_soils is not None

    def test_engine_fallback_when_imports_fail(self):
        """Test engine handles ImportError gracefully."""
        with patch.dict(sys.modules, {"shared.yemen.crops": None, "shared.salinity": None}):
            engine = IrrigationCycleEngine()
            # Should still be functional
            assert engine is not None


class TestET0PenmanMonteith:
    """Tests for calculate_et0_penman_monteith method."""

    @pytest.fixture
    def engine(self):
        return IrrigationCycleEngine()

    def test_typical_summer_day(self, engine):
        """Test ET0 for a hot summer day in Yemen highlands."""
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=20.0,
            temp_max=35.0,
            humidity_min=20.0,
            humidity_max=60.0,
            wind_speed_2m=2.5,
            solar_radiation=25.0,
            latitude=15.35,
            elevation=2200.0,
            day_of_year=180,
        )
        assert et0 > 0
        assert et0 < 15  # Reasonable upper bound

    def test_cold_winter_day(self, engine):
        """Test ET0 for a cold day."""
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=0.0,
            temp_max=10.0,
            humidity_min=50.0,
            humidity_max=90.0,
            wind_speed_2m=1.0,
            solar_radiation=8.0,
            latitude=15.35,
            elevation=2200.0,
            day_of_year=15,
        )
        assert et0 >= 0
        assert et0 < 5  # Low ET expected

    def test_zero_wind_speed(self, engine):
        """Test ET0 with zero wind speed."""
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=15.0,
            temp_max=30.0,
            humidity_min=30.0,
            humidity_max=70.0,
            wind_speed_2m=0.0,
            solar_radiation=20.0,
            latitude=15.35,
            elevation=100.0,
            day_of_year=100,
        )
        assert et0 >= 0

    def test_high_elevation(self, engine):
        """Test ET0 at high elevation."""
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=5.0,
            temp_max=20.0,
            humidity_min=30.0,
            humidity_max=60.0,
            wind_speed_2m=2.0,
            solar_radiation=22.0,
            latitude=15.35,
            elevation=3000.0,
            day_of_year=100,
        )
        assert et0 >= 0

    def test_et0_never_negative(self, engine):
        """ET0 should never be negative regardless of inputs."""
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=-10.0,
            temp_max=0.0,
            humidity_min=90.0,
            humidity_max=100.0,
            wind_speed_2m=0.5,
            solar_radiation=2.0,
            latitude=45.0,
            elevation=0.0,
            day_of_year=355,
        )
        assert et0 >= 0

    def test_equatorial_latitude(self, engine):
        """Test ET0 near equator."""
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=22.0,
            temp_max=32.0,
            humidity_min=60.0,
            humidity_max=90.0,
            wind_speed_2m=1.5,
            solar_radiation=18.0,
            latitude=0.0,
            elevation=50.0,
            day_of_year=80,
        )
        assert et0 > 0

    def test_higher_wind_increases_et0(self, engine):
        """Higher wind speed should generally increase ET0."""
        common = dict(  # noqa: C408
            temp_min=20.0,
            temp_max=35.0,
            humidity_min=30.0,
            humidity_max=60.0,
            solar_radiation=22.0,
            latitude=15.0,
            elevation=500.0,
            day_of_year=150,
        )
        et0_low_wind = engine.calculate_et0_penman_monteith(wind_speed_2m=0.5, **common)
        et0_high_wind = engine.calculate_et0_penman_monteith(wind_speed_2m=6.0, **common)
        assert et0_high_wind > et0_low_wind


# ═══════════════════════════════════════════════════════════════════════════════
# Irrigation Cycle Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalculateCycle:
    """Tests for IrrigationCycleEngine.calculate_cycle."""

    @pytest.fixture
    def engine(self):
        return IrrigationCycleEngine()

    def test_basic_cycle(self, engine):
        """Test basic irrigation cycle with default Kc."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.30,
            wilting_point=0.12,
            root_depth_m=1.0,
            et0_mm_day=5.0,
        )
        result = engine.calculate_cycle(req)
        assert result.cycle_days > 0
        assert result.cycle_days <= 60
        assert result.net_irrigation_mm > 0
        assert result.gross_irrigation_mm > result.net_irrigation_mm
        assert result.etc_mm_day > 0
        assert result.kc_used == 1.0  # Default for unknown crop
        assert result.crop_name == "unknown_crop"

    def test_cycle_with_explicit_kc(self, engine):
        """Test cycle with explicit Kc override."""
        req = IrrigationCycleRequest(
            crop="wheat",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=5.0,
            kc=1.15,
        )
        result = engine.calculate_cycle(req)
        assert result.kc_used == 1.15
        assert result.etc_mm_day == pytest.approx(5.0 * 1.15, rel=0.01)

    def test_cycle_zero_et0(self, engine):
        """Test cycle when ET0 is zero defaults to 30 days."""
        req = IrrigationCycleRequest(
            crop="wheat",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=0.0,
        )
        result = engine.calculate_cycle(req)
        assert result.cycle_days == 30.0
        assert result.etc_mm_day == 0.0

    def test_cycle_short_produces_recommendation(self, engine):
        """Very high ET should produce short cycle with drip recommendation."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.25,
            wilting_point=0.12,
            root_depth_m=0.3,
            depletion_fraction=0.5,
            et0_mm_day=12.0,
            kc=1.5,
        )
        result = engine.calculate_cycle(req)
        if result.cycle_days < 2:
            assert any("drip" in r.lower() for r in result.recommendations)

    def test_cycle_long_produces_recommendation(self, engine):
        """Very low ET with deep roots should produce long cycle with monitor recommendation."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.40,
            wilting_point=0.10,
            root_depth_m=2.0,
            depletion_fraction=0.6,
            et0_mm_day=1.0,
            kc=0.3,
        )
        result = engine.calculate_cycle(req)
        if result.cycle_days > 14:
            assert any("monitor" in r.lower() for r in result.recommendations)

    def test_cycle_clamped_to_max_60(self, engine):
        """Cycle should be clamped to 60 days max."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.45,
            wilting_point=0.05,
            root_depth_m=3.0,
            et0_mm_day=0.1,
            kc=0.1,
        )
        result = engine.calculate_cycle(req)
        assert result.cycle_days <= 60.0

    def test_cycle_clamped_to_min_1(self, engine):
        """Cycle should be at least 1 day."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.20,
            wilting_point=0.18,
            root_depth_m=0.1,
            et0_mm_day=15.0,
            kc=2.0,
        )
        result = engine.calculate_cycle(req)
        assert result.cycle_days >= 1.0

    def test_cycle_with_correction_factors(self, engine):
        """Test alpha, beta, gamma correction factors affect the cycle."""
        req_base = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=5.0,
            kc=1.0,
            alpha=1.0,
            beta=1.0,
            gamma=1.0,
        )
        result_base = engine.calculate_cycle(req_base)

        # Higher alpha should shorten the cycle (increases denominator)
        req_alpha = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=5.0,
            kc=1.0,
            alpha=2.0,
            beta=1.0,
            gamma=1.0,
        )
        result_alpha = engine.calculate_cycle(req_alpha)
        assert result_alpha.cycle_days < result_base.cycle_days

    def test_cycle_available_water_calculation(self, engine):
        """Test available and readily available water calculations."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.30,
            wilting_point=0.10,
            root_depth_m=1.0,
            depletion_fraction=0.5,
            et0_mm_day=5.0,
            kc=1.0,
        )
        result = engine.calculate_cycle(req)
        # Total AW = (0.30 - 0.10) * 1000 = 200 mm
        assert result.available_water_mm == pytest.approx(200.0, rel=0.01)
        # Readily AW = (0.30 - theta_min) * 1000
        # theta_min = 0.10 + (0.30 - 0.10) * (1 - 0.5) = 0.20
        # Readily AW = (0.30 - 0.20) * 1000 = 100 mm
        assert result.readily_available_mm == pytest.approx(100.0, rel=0.01)

    def test_cycle_next_irrigation_date(self, engine):
        """Test next irrigation date is set correctly."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=5.0,
            kc=1.0,
        )
        result = engine.calculate_cycle(req)
        assert result.next_irrigation_date is not None
        expected = date.today() + timedelta(days=int(result.cycle_days))
        assert result.next_irrigation_date == expected

    def test_cycle_gross_irrigation_includes_efficiency(self, engine):
        """Gross irrigation should be net / efficiency (0.85)."""
        req = IrrigationCycleRequest(
            crop="unknown_crop",
            field_capacity=0.30,
            wilting_point=0.12,
            et0_mm_day=5.0,
        )
        result = engine.calculate_cycle(req)
        expected_gross = result.net_irrigation_mm / 0.85
        assert result.gross_irrigation_mm == pytest.approx(expected_gross, rel=0.01)


# ═══════════════════════════════════════════════════════════════════════════════
# Schedule Generation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGenerateSchedule:
    """Tests for IrrigationCycleEngine.generate_schedule."""

    @pytest.fixture
    def engine(self):
        return IrrigationCycleEngine()

    def test_schedule_unknown_crop_raises(self, engine):
        """Unknown crop should raise ValueError."""
        req = ScheduleRequest(
            crop="nonexistent_crop",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
            days=10,
        )
        with pytest.raises(ValueError, match="Unknown crop"):
            engine.generate_schedule(req)

    def test_schedule_correct_length(self, engine):
        """Schedule should have exactly 'days' entries."""
        # Only works if 'wheat' is in Yemen crops
        if not engine._get_yemen_crop("wheat"):
            pytest.skip("Yemen crop data not available")
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
            days=14,
        )
        result = engine.generate_schedule(req)
        assert len(result.schedule) == 14

    def test_schedule_cumulative_water_increases(self, engine):
        """Cumulative water should only increase over time."""
        if not engine._get_yemen_crop("wheat"):
            pytest.skip("Yemen crop data not available")
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
            days=30,
        )
        result = engine.generate_schedule(req)
        for i in range(1, len(result.schedule)):
            assert result.schedule[i].cumulative_water_mm >= result.schedule[i - 1].cumulative_water_mm

    def test_schedule_irrigation_events_counted(self, engine):
        """Irrigation events count matches irrigate=True days."""
        if not engine._get_yemen_crop("wheat"):
            pytest.skip("Yemen crop data not available")
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
            days=30,
        )
        result = engine.generate_schedule(req)
        irrigate_count = sum(1 for d in result.schedule if d.irrigate)
        assert result.irrigation_events == irrigate_count

    def test_schedule_soil_moisture_bounded(self, engine):
        """Soil moisture percentage should stay in [0, 100]."""
        if not engine._get_yemen_crop("wheat"):
            pytest.skip("Yemen crop data not available")
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
            days=60,
        )
        result = engine.generate_schedule(req)
        for day in result.schedule:
            assert 0.0 <= day.soil_moisture_pct <= 100.0

    def test_schedule_total_water_m3_conversion(self, engine):
        """Total water m3/ha should be cumulative_water_mm * 10."""
        if not engine._get_yemen_crop("wheat"):
            pytest.skip("Yemen crop data not available")
        req = ScheduleRequest(
            crop="wheat",
            soil_profile="highland_clay_loam",
            climate_zone="highlands",
            start_date=date(2026, 1, 15),
            days=30,
        )
        result = engine.generate_schedule(req)
        assert result.total_water_m3_per_ha == pytest.approx(result.total_water_mm * 10.0, rel=0.01)


# ═══════════════════════════════════════════════════════════════════════════════
# API Endpoint Tests (using TestClient)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from fastapi.testclient import TestClient

    from src.main import app

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


@pytest.mark.skipif(not HAS_FASTAPI, reason="fastapi not installed")
class TestAPIEndpoints:
    """Tests for FastAPI endpoint responses."""

    TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_healthz_endpoint(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "irrigation-cycle-engine"

    def test_readyz_endpoint(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert "nats" in data

    def test_et0_single_day(self, client):
        response = client.post(
            "/api/v1/irrigation/et0",
            json={
                "latitude": 15.0,
                "elevation_m": 1000,
                "weather": [
                    {"date": "2026-03-15", "temp_min_c": 10, "temp_max_c": 28},
                ],
            },
            headers=self.TENANT_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["et0_mm"] > 0

    def test_et0_multiple_days(self, client):
        response = client.post(
            "/api/v1/irrigation/et0",
            json={
                "latitude": 15.0,
                "elevation_m": 1000,
                "weather": [
                    {"date": "2026-03-15", "temp_min_c": 10, "temp_max_c": 28},
                    {"date": "2026-03-16", "temp_min_c": 12, "temp_max_c": 30},
                    {"date": "2026-03-17", "temp_min_c": 11, "temp_max_c": 29},
                ],
            },
            headers=self.TENANT_HEADER,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_cycle_endpoint(self, client):
        response = client.post(
            "/api/v1/irrigation/cycle",
            json={
                "crop": "wheat",
                "field_capacity": 0.30,
                "wilting_point": 0.12,
                "et0_mm_day": 5.0,
            },
            headers=self.TENANT_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert "cycle_days" in data
        assert "net_irrigation_mm" in data

    def test_cycle_with_zero_et(self, client):
        response = client.post(
            "/api/v1/irrigation/cycle",
            json={
                "crop": "wheat",
                "field_capacity": 0.30,
                "wilting_point": 0.12,
                "et0_mm_day": 0.0,
            },
            headers=self.TENANT_HEADER,
        )
        assert response.status_code == 200
        assert response.json()["cycle_days"] == 30.0

    def test_climate_zones_endpoint(self, client):
        response = client.get("/api/v1/yemen/climate-zones", headers=self.TENANT_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert "total" in data

    def test_soils_endpoint(self, client):
        response = client.get("/api/v1/yemen/soils", headers=self.TENANT_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert "total" in data

    def test_missing_tenant_header_returns_400(self, client):
        """Endpoints that require tenant context should return 400 without header."""
        response = client.post(
            "/api/v1/irrigation/et0",
            json={"latitude": 15.0, "elevation_m": 1000, "weather": [{"date": "2026-01-01", "temp_min_c": 10, "temp_max_c": 25}]},
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
