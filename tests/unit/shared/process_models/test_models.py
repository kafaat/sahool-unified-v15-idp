"""
Unit tests for shared/process_models/models.py
Tests process model data classes including enums, DailyWeather,
SoilProfile, CropParameters, and ModelResult.
"""

import pytest
from datetime import date

from shared.process_models.models import (
    # Enums
    CropType,
    GrowthStage,
    SoilTextureClass,
    ModelType,
    # Dataclasses
    DailyWeather,
    SoilProfile,
    CropParameters,
    ModelResult,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_crop_type(self):
        assert CropType.WHEAT == "wheat"
        assert CropType.DATE_PALM == "date_palm"
        assert CropType.GENERIC == "generic"

    def test_growth_stage(self):
        assert GrowthStage.SOWING == "sowing"
        assert GrowthStage.GERMINATION == "germination"
        assert GrowthStage.TILLERING == "tillering"
        assert GrowthStage.HARVEST == "harvest"

    def test_soil_texture_class(self):
        assert SoilTextureClass.SAND == "sand"
        assert SoilTextureClass.LOAM == "loam"
        assert SoilTextureClass.CLAY == "clay"
        assert SoilTextureClass.SILTY_CLAY_LOAM == "silty_clay_loam"

    def test_model_type(self):
        assert ModelType.CROP_GROWTH == "crop_growth"
        assert ModelType.HYDROLOGY == "hydrology"
        assert ModelType.ENSEMBLE == "ensemble"


# =============================================================================
# DailyWeather Tests
# =============================================================================


class TestDailyWeather:
    def _make_weather(self, **kwargs):
        defaults = dict(
            date=date(2026, 3, 15),
            tmax_c=30.0,
            tmin_c=15.0,
            solar_radiation_mj_m2=20.0,
            relative_humidity_pct=50.0,
            wind_speed_m_s=3.0,
        )
        defaults.update(kwargs)
        return DailyWeather(**defaults)

    def test_creation(self):
        w = self._make_weather()
        assert w.tmax_c == 30.0
        assert w.tmin_c == 15.0
        assert w.precipitation_mm == 0.0  # default

    def test_tmean_c(self):
        w = self._make_weather(tmax_c=30.0, tmin_c=20.0)
        assert w.tmean_c == pytest.approx(25.0)

    def test_with_precipitation(self):
        w = self._make_weather(precipitation_mm=10.0)
        assert w.precipitation_mm == 10.0

    def test_with_vapor_pressure(self):
        w = self._make_weather(actual_vapor_pressure_kpa=1.5)
        assert w.actual_vapor_pressure_kpa == 1.5

    # Validation tests
    def test_tmax_less_than_tmin_raises(self):
        with pytest.raises(ValueError, match="tmax_c"):
            self._make_weather(tmax_c=10.0, tmin_c=20.0)

    def test_tmax_out_of_range_high(self):
        with pytest.raises(ValueError, match="tmax_c"):
            self._make_weather(tmax_c=65.0)

    def test_tmin_out_of_range_low(self):
        with pytest.raises(ValueError, match="tmin_c"):
            self._make_weather(tmin_c=-55.0, tmax_c=-50.0)

    def test_solar_radiation_out_of_range(self):
        with pytest.raises(ValueError, match="solar_radiation"):
            self._make_weather(solar_radiation_mj_m2=55.0)

    def test_solar_radiation_negative(self):
        with pytest.raises(ValueError, match="solar_radiation"):
            self._make_weather(solar_radiation_mj_m2=-1.0)

    def test_humidity_out_of_range(self):
        with pytest.raises(ValueError, match="relative_humidity"):
            self._make_weather(relative_humidity_pct=105.0)

    def test_humidity_negative(self):
        with pytest.raises(ValueError, match="relative_humidity"):
            self._make_weather(relative_humidity_pct=-5.0)

    def test_wind_speed_negative(self):
        with pytest.raises(ValueError, match="wind_speed"):
            self._make_weather(wind_speed_m_s=-1.0)

    def test_precipitation_negative(self):
        with pytest.raises(ValueError, match="precipitation"):
            self._make_weather(precipitation_mm=-1.0)

    def test_boundary_values_valid(self):
        # tmax = tmin (valid)
        w = self._make_weather(tmax_c=20.0, tmin_c=20.0)
        assert w.tmean_c == 20.0

        # Solar radiation at boundaries
        w = self._make_weather(solar_radiation_mj_m2=0.0)
        assert w.solar_radiation_mj_m2 == 0.0

        w = self._make_weather(solar_radiation_mj_m2=50.0)
        assert w.solar_radiation_mj_m2 == 50.0

        # Humidity at boundaries
        w = self._make_weather(relative_humidity_pct=0.0)
        assert w.relative_humidity_pct == 0.0

        w = self._make_weather(relative_humidity_pct=100.0)
        assert w.relative_humidity_pct == 100.0


# =============================================================================
# SoilProfile Tests
# =============================================================================


class TestSoilProfile:
    def test_creation_defaults(self):
        sp = SoilProfile()
        assert sp.texture == SoilTextureClass.LOAM
        assert sp.clay_pct == 25.0
        assert sp.sand_pct == 40.0
        assert sp.ph == 7.2
        assert sp.depth_m == 1.2

    def test_available_water_capacity(self):
        sp = SoilProfile(
            field_capacity_mm_per_m=250.0,
            wilting_point_mm_per_m=120.0,
            depth_m=1.0,
        )
        assert sp.available_water_capacity_mm == pytest.approx(130.0)

    def test_available_water_capacity_deeper_soil(self):
        sp = SoilProfile(
            field_capacity_mm_per_m=300.0,
            wilting_point_mm_per_m=100.0,
            depth_m=1.5,
        )
        assert sp.available_water_capacity_mm == pytest.approx(300.0)

    def test_fc_less_than_wp_raises(self):
        with pytest.raises(ValueError, match="field_capacity"):
            SoilProfile(
                field_capacity_mm_per_m=100.0,
                wilting_point_mm_per_m=200.0,
            )

    def test_fc_equal_wp_raises(self):
        with pytest.raises(ValueError, match="field_capacity"):
            SoilProfile(
                field_capacity_mm_per_m=200.0,
                wilting_point_mm_per_m=200.0,
            )

    def test_bulk_density_zero_raises(self):
        with pytest.raises(ValueError, match="bulk_density"):
            SoilProfile(bulk_density_g_cm3=0.0)

    def test_depth_zero_raises(self):
        with pytest.raises(ValueError, match="depth_m"):
            SoilProfile(depth_m=0.0)

    def test_clay_pct_out_of_range(self):
        with pytest.raises(ValueError, match="clay_pct"):
            SoilProfile(clay_pct=105.0)

    def test_sand_pct_out_of_range(self):
        with pytest.raises(ValueError, match="sand_pct"):
            SoilProfile(sand_pct=-5.0)

    def test_organic_carbon_out_of_range(self):
        with pytest.raises(ValueError, match="organic_carbon"):
            SoilProfile(organic_carbon_pct=110.0)

    def test_valid_boundary_values(self):
        sp = SoilProfile(clay_pct=0.0, sand_pct=100.0, organic_carbon_pct=0.0)
        assert sp.clay_pct == 0.0


# =============================================================================
# CropParameters Tests
# =============================================================================


class TestCropParameters:
    def test_creation_defaults(self):
        cp = CropParameters()
        assert cp.crop_type == CropType.WHEAT
        assert cp.name_en == "Wheat"
        assert cp.name_ar == "قمح"
        assert cp.harvest_index == 0.42

    def test_creation_custom(self):
        cp = CropParameters(
            crop_type=CropType.RICE,
            name_en="Rice",
            name_ar="أرز",
            base_temp_c=10.0,
            gdd_maturity=2000.0,
            lai_max=8.0,
        )
        assert cp.crop_type == CropType.RICE
        assert cp.base_temp_c == 10.0
        assert cp.lai_max == 8.0

    def test_nutrient_requirements(self):
        cp = CropParameters(
            n_requirement_kg_per_ton=25.0,
            p_requirement_kg_per_ton=4.0,
            k_requirement_kg_per_ton=6.0,
        )
        assert cp.n_requirement_kg_per_ton == 25.0
        assert cp.p_requirement_kg_per_ton == 4.0


# =============================================================================
# ModelResult Tests
# =============================================================================


class TestModelResult:
    def test_creation(self):
        result = ModelResult(
            model_name="AquaCrop",
            model_type=ModelType.CROP_GROWTH,
        )
        assert result.model_name == "AquaCrop"
        assert result.success is True
        assert result.message == ""
        assert result.outputs == {}
        assert result.metadata == {}

    def test_creation_with_outputs(self):
        result = ModelResult(
            model_name="DSSAT",
            model_type=ModelType.CROP_GROWTH,
            success=True,
            message="Simulation completed",
            message_ar="اكتملت المحاكاة",
            outputs={"yield_kg_ha": 4500, "biomass_kg_ha": 10000},
            metadata={"version": "4.8", "run_time_s": 2.5},
        )
        assert result.outputs["yield_kg_ha"] == 4500
        assert result.metadata["version"] == "4.8"

    def test_failed_result(self):
        result = ModelResult(
            model_name="FailModel",
            model_type=ModelType.ENSEMBLE,
            success=False,
            message="Input data missing",
            message_ar="بيانات الإدخال مفقودة",
        )
        assert result.success is False
        assert result.message == "Input data missing"
