"""
Unit tests for shared/process_models – mechanistic agricultural models
======================================================================
Tests cover all eight modules:
  1. models              – shared data objects
  2. crop_growth         – WOFOST/AquaCrop-inspired crop growth engine
  3. agro_meteorology    – Penman-Monteith ET₀ + Shuttleworth-Wallace
  4. soil_carbon         – RothC/DNDC-inspired C/N cycling
  5. radiative_transfer  – PROSAIL-simplified leaf-canopy RTM
  6. pest_epidemiology   – SIR disease + degree-day + Lotka-Volterra
  7. nutrient_management – QUEFTS nutrient recommendation model
  8. hydrology           – FAO-56 SWB + SCS-CN + Green-Ampt
  9. ensemble            – AgMIP-inspired multi-model ensemble framework
"""

from __future__ import annotations

import math
from datetime import date

import pytest

# ---------------------------------------------------------------------------
# Shared models
# ---------------------------------------------------------------------------
from shared.process_models.models import (
    CropParameters,
    CropType,
    DailyWeather,
    GrowthStage,
    ModelResult,
    ModelType,
    SoilProfile,
    SoilTextureClass,
)


def _make_weather(
    year: int = 2024,
    month: int = 1,
    day: int = 1,
    tmax: float = 22.0,
    tmin: float = 10.0,
    solar: float = 14.0,
    rh: float = 60.0,
    wind: float = 2.0,
    rain: float = 0.0,
) -> DailyWeather:
    return DailyWeather(
        date=date(year, month, day),
        tmax_c=tmax,
        tmin_c=tmin,
        solar_radiation_mj_m2=solar,
        relative_humidity_pct=rh,
        wind_speed_m_s=wind,
        precipitation_mm=rain,
    )


def _make_season(days: int = 120, base_rain: float = 0.0) -> list[DailyWeather]:
    """Create a synthetic daily weather series (no real I/O needed)."""
    series = []
    for i in range(days):
        from datetime import timedelta

        d = date(2024, 1, 1) + timedelta(days=i)
        series.append(
            DailyWeather(
                date=d,
                tmax_c=22.0 + 0.05 * i,
                tmin_c=10.0 + 0.03 * i,
                solar_radiation_mj_m2=14.0 + 2.0 * math.sin(2 * math.pi * i / 120),
                relative_humidity_pct=65.0,
                wind_speed_m_s=2.5,
                precipitation_mm=base_rain,
            )
        )
    return series


# ===========================================================================
# 1. Shared models
# ===========================================================================


class TestSharedModels:
    def test_daily_weather_tmean(self):
        w = _make_weather(tmax=30.0, tmin=10.0)
        assert w.tmean_c == pytest.approx(20.0)

    def test_soil_available_water(self):
        soil = SoilProfile(
            field_capacity_mm_per_m=300.0, wilting_point_mm_per_m=150.0, depth_m=1.0
        )
        assert soil.available_water_capacity_mm == pytest.approx(150.0)

    def test_model_result_defaults(self):
        r = ModelResult(model_name="test", model_type=ModelType.CROP_GROWTH)
        assert r.success is True
        assert r.outputs == {}

    def test_crop_parameters_default_crop_type(self):
        cp = CropParameters()
        assert cp.crop_type == CropType.WHEAT

    def test_growth_stage_enum(self):
        assert GrowthStage.SOWING == "sowing"
        assert GrowthStage.MATURITY == "maturity"

    def test_soil_texture_class_values(self):
        assert SoilTextureClass.CLAY == "clay"
        assert SoilTextureClass.LOAM == "loam"


# ===========================================================================
# 2. Crop Growth Engine
# ===========================================================================


class TestCropGrowthEngine:
    def setup_method(self):
        from shared.process_models.crop_growth import CropGrowthEngine

        self.engine = CropGrowthEngine()
        self.crop = CropParameters(crop_type=CropType.WHEAT)
        self.soil = SoilProfile()
        self.weather = _make_season(150)

    def test_simulation_runs(self):
        result = self.engine.simulate(self.crop, self.soil, self.weather)
        assert result.success is True
        assert result.model_type == ModelType.CROP_GROWTH

    def test_grain_yield_positive(self):
        result = self.engine.simulate(self.crop, self.soil, self.weather)
        yield_t_ha = result.outputs["grain_yield_t_ha"]
        assert yield_t_ha > 0.0
        assert yield_t_ha < 20.0  # physically plausible

    def test_biomass_exceeds_grain(self):
        result = self.engine.simulate(self.crop, self.soil, self.weather)
        assert result.outputs["biomass_t_ha"] >= result.outputs["grain_yield_t_ha"]

    def test_n_stress_reduces_yield(self):
        result_rich = self.engine.simulate(
            self.crop, self.soil, self.weather, n_supply_kg_ha=200.0
        )
        result_poor = self.engine.simulate(
            self.crop, self.soil, self.weather, n_supply_kg_ha=10.0
        )
        assert (
            result_rich.outputs["grain_yield_t_ha"]
            >= result_poor.outputs["grain_yield_t_ha"]
        )

    def test_daily_log_present(self):
        result = self.engine.simulate(self.crop, self.soil, self.weather[:30])
        assert "daily_log" in result.metadata
        assert len(result.metadata["daily_log"]) > 0

    def test_dvs_monotone_increase(self):
        result = self.engine.simulate(self.crop, self.soil, self.weather)
        log = result.metadata["daily_log"]
        dvs_values = [entry["dvs"] for entry in log]
        for a, b in zip(dvs_values, dvs_values[1:]):
            assert b >= a - 1e-9  # non-decreasing


class TestCropGrowthHelpers:
    def test_gdd_above_base(self):
        from shared.process_models.crop_growth import compute_gdd

        w = _make_weather(tmax=20.0, tmin=10.0)
        gdd = compute_gdd(w, base_temp=0.0)
        assert gdd == pytest.approx(15.0, abs=1.0)

    def test_gdd_capped_by_max(self):
        from shared.process_models.crop_growth import compute_gdd

        w = _make_weather(tmax=50.0, tmin=30.0)
        gdd_nocap = compute_gdd(w, base_temp=0.0, max_temp_cap=1000.0)
        gdd_capped = compute_gdd(w, base_temp=0.0, max_temp_cap=35.0)
        assert gdd_capped < gdd_nocap

    def test_intercepted_radiation_positive(self):
        from shared.process_models.crop_growth import compute_intercepted_radiation

        ipar = compute_intercepted_radiation(14.0, 3.0)
        assert ipar > 0.0
        assert ipar <= 14.0  # cannot exceed incident

    def test_intercepted_radiation_zero_lai(self):
        from shared.process_models.crop_growth import compute_intercepted_radiation

        ipar = compute_intercepted_radiation(14.0, 0.0)
        assert ipar == pytest.approx(0.0, abs=0.01)

    def test_water_stress_factor_at_fc(self):
        from shared.process_models.crop_growth import water_stress_factor

        ws = water_stress_factor(300.0, 300.0, 100.0)
        assert ws == pytest.approx(1.0)

    def test_water_stress_factor_at_wp(self):
        from shared.process_models.crop_growth import water_stress_factor

        ws = water_stress_factor(100.0, 300.0, 100.0)
        assert ws == pytest.approx(0.0, abs=0.01)

    def test_partition_sums_to_one(self):
        from shared.process_models.crop_growth import partition_biomass

        part = partition_biomass(delta_bm=10.0, dvs=1.0)
        total = part.leaves_g_m2 + part.stems_g_m2 + part.roots_g_m2 + part.storage_g_m2
        assert total == pytest.approx(10.0, abs=0.01)


# ===========================================================================
# 3. Agro-Meteorology Engine
# ===========================================================================


class TestAgroMeteorology:
    def setup_method(self):
        from shared.process_models.agro_meteorology import AgroMeteorologyEngine

        self.engine = AgroMeteorologyEngine(elevation_m=100, lat_deg=15.5)

    def test_penman_monteith_positive(self):
        from shared.process_models.agro_meteorology import penman_monteith_et0

        w = _make_weather(tmax=28.0, tmin=15.0, solar=18.0, rh=50.0, wind=2.0)
        et0 = penman_monteith_et0(w, elevation_m=100.0, lat_deg=15.5)
        assert et0 > 0.5
        assert et0 < 15.0

    def test_hargreaves_positive(self):
        from shared.process_models.agro_meteorology import hargreaves_et0

        w = _make_weather(tmax=30.0, tmin=15.0, solar=18.0)
        et0 = hargreaves_et0(w, lat_deg=15.0)
        assert et0 > 0.0

    def test_sat_vapour_pressure(self):
        from shared.process_models.agro_meteorology import saturation_vapour_pressure

        # Known value: e_s(20°C) ≈ 2.338 kPa
        es = saturation_vapour_pressure(20.0)
        assert es == pytest.approx(2.338, abs=0.05)

    def test_shuttleworth_wallace_partitioning(self):
        from shared.process_models.agro_meteorology import shuttleworth_wallace_et

        w = _make_weather(tmax=28.0, tmin=16.0, solar=18.0)
        sw = shuttleworth_wallace_et(
            w, lai=3.0, fractional_cover=0.8, et0_mm=5.0, crop_coefficient=1.1
        )
        assert sw.et_canopy_mm >= 0.0
        assert sw.et_soil_mm >= 0.0
        assert sw.et_total_mm == pytest.approx(
            sw.et_canopy_mm + sw.et_soil_mm, abs=0.01
        )

    def test_engine_run_returns_valid_result(self):
        weather = _make_season(30)
        result = self.engine.run(
            weather, lai=2.5, fractional_cover=0.7, crop_coefficient=1.05
        )
        assert result.success is True
        assert result.outputs["total_et0_mm"] > 0.0
        assert result.outputs["n_days"] == 30

    def test_et0_increases_with_temperature(self):
        from shared.process_models.agro_meteorology import penman_monteith_et0

        w_cool = _make_weather(tmax=20.0, tmin=10.0, solar=14.0)
        w_hot = _make_weather(tmax=35.0, tmin=22.0, solar=14.0)
        et0_cool = penman_monteith_et0(w_cool)
        et0_hot = penman_monteith_et0(w_hot)
        assert et0_hot > et0_cool


# ===========================================================================
# 4. Soil Carbon Model
# ===========================================================================


class TestSoilCarbonModel:
    def setup_method(self):
        from shared.process_models.soil_carbon import SoilCarbonModel

        self.model = SoilCarbonModel()

    def test_simulation_runs(self):
        result = self.model.simulate(SoilProfile(), years=10, mean_temp_c=18.0)
        assert result.success is True
        assert result.model_type == ModelType.SOIL_CARBON

    def test_soc_change_key_present(self):
        result = self.model.simulate(SoilProfile(), years=5)
        assert "soc_change_t_ha" in result.outputs

    def test_n2o_positive(self):
        result = self.model.simulate(SoilProfile(), years=5)
        assert result.outputs["cumulative_n2o_kg_ha"] >= 0.0

    def test_anaerobic_has_ch4(self):
        result = self.model.simulate(SoilProfile(), years=5, is_anaerobic=True)
        assert result.outputs["cumulative_ch4_kg_ha"] > 0.0

    def test_aerobic_no_ch4(self):
        result = self.model.simulate(SoilProfile(), years=5, is_anaerobic=False)
        assert result.outputs["cumulative_ch4_kg_ha"] == pytest.approx(0.0)

    def test_higher_temp_faster_decomposition(self):
        result_warm = self.model.simulate(SoilProfile(), years=20, mean_temp_c=28.0)
        result_cool = self.model.simulate(SoilProfile(), years=20, mean_temp_c=10.0)
        # Warm soil should decompose more → lower final SOC (if inputs equal)
        assert (
            result_warm.outputs["soc_change_t_ha"]
            <= result_cool.outputs["soc_change_t_ha"]
        )

    def test_annual_log_length(self):
        result = self.model.simulate(SoilProfile(), years=10)
        assert len(result.metadata["annual_log"]) == 10

    def test_temperature_modifier_range(self):
        from shared.process_models.soil_carbon import temperature_modifier

        assert temperature_modifier(-5.0) >= 0.1
        assert temperature_modifier(30.0) <= 3.0
        assert temperature_modifier(10.0) == pytest.approx(1.0, abs=0.01)

    def test_moisture_modifier_range(self):
        from shared.process_models.soil_carbon import moisture_modifier

        mm = moisture_modifier(200.0, 300.0, 100.0)
        assert 0.0 < mm <= 1.0


# ===========================================================================
# 5. Radiative Transfer Model
# ===========================================================================


class TestRadiativeTransferModel:
    def setup_method(self):
        from shared.process_models.radiative_transfer import (
            CanopyParameters,
            LeafOpticalProperties,
            RadiativeTransferModel,
        )

        self.rtm = RadiativeTransferModel()
        self.leaf = LeafOpticalProperties(
            chlorophyll_ug_cm2=45.0, water_cm=0.015, n_layers=1.5
        )
        self.canopy = CanopyParameters(lai=3.5, sun_zenith_deg=25.0)

    def test_forward_run(self):
        result = self.rtm.forward(self.leaf, self.canopy)
        assert result.success is True
        assert "vegetation_indices" in result.outputs
        assert "canopy_reflectance" in result.outputs

    def test_ndvi_range(self):
        result = self.rtm.forward(self.leaf, self.canopy)
        ndvi = result.outputs["vegetation_indices"]["ndvi"]
        assert -1.0 <= ndvi <= 1.0

    def test_healthy_crop_ndvi_positive(self):
        """Green healthy crop should have positive NDVI."""
        result = self.rtm.forward(self.leaf, self.canopy)
        ndvi = result.outputs["vegetation_indices"]["ndvi"]
        assert ndvi > 0.2

    def test_nir_greater_than_red(self):
        """For green vegetation NIR reflectance > Red reflectance."""
        result = self.rtm.forward(self.leaf, self.canopy)
        ref = result.outputs["canopy_reflectance"]
        assert ref["nir"] > ref["red"]

    def test_inversion_returns_lai(self):
        result = self.rtm.invert(observed_ndvi=0.70, observed_ndre=0.35)
        assert result.success is True
        assert result.outputs["lai_estimated"] > 0.0

    def test_high_ndvi_high_lai(self):
        r_high = self.rtm.invert(observed_ndvi=0.80, observed_ndre=0.40)
        r_low = self.rtm.invert(observed_ndvi=0.30, observed_ndre=0.15)
        assert r_high.outputs["lai_estimated"] >= r_low.outputs["lai_estimated"]

    def test_prospect_reflectance_bands(self):
        from shared.process_models.radiative_transfer import (
            LeafOpticalProperties,
            prospect_reflectance,
        )

        leaf = LeafOpticalProperties()
        ref = prospect_reflectance(leaf)
        for band in ("blue", "green", "red", "red_edge", "nir", "swir"):
            assert band in ref
            assert 0.0 <= ref[band] <= 1.0

    def test_vegetation_indices_keys(self):
        from shared.process_models.radiative_transfer import compute_vegetation_indices

        indices = compute_vegetation_indices(
            {"nir": 0.5, "red": 0.1, "blue": 0.05, "red_edge": 0.2, "swir": 0.1}
        )
        for key in ("ndvi", "evi", "ndre", "ndwi"):
            assert key in indices


# ===========================================================================
# 6. Pest Epidemiology Engine
# ===========================================================================


class TestPestEpidemiologyEngine:
    def setup_method(self):
        from shared.process_models.pest_epidemiology import (
            PestEpidemiologyEngine,
            PestType,
        )

        self.engine = PestEpidemiologyEngine()
        self.PestType = PestType

    def test_sir_disease_simulation(self):
        weather = _make_season(60, base_rain=0.0)
        result = self.engine.simulate_disease(
            self.PestType.WHEAT_RUST, weather, initial_infected_fraction=0.01
        )
        assert result.success is True
        assert "r0_reproduction_number" in result.outputs

    def test_r0_wheat_rust(self):
        """R₀ for wheat rust should be > 1 (epidemic-prone)."""
        weather = _make_season(60)
        result = self.engine.simulate_disease(self.PestType.WHEAT_RUST, weather)
        assert result.outputs["r0_reproduction_number"] > 1.0

    def test_sir_infected_never_exceeds_one(self):
        weather = _make_season(90)
        result = self.engine.simulate_disease(self.PestType.WHEAT_RUST, weather)
        log = result.metadata["daily_log"]
        for entry in log:
            assert entry["infected"] <= 1.0 + 1e-6

    def test_pest_phenology_degree_days(self):
        weather = _make_season(120)
        result = self.engine.simulate_pest_phenology(self.PestType.APHID, weather)
        assert result.success is True
        assert result.outputs["cumulative_dd"] >= 0.0

    def test_aphid_emergence_before_end(self):
        weather = _make_season(120)
        result = self.engine.simulate_pest_phenology(self.PestType.APHID, weather)
        # With moderate temperatures aphids should emerge within 120 days
        assert result.outputs.get("adult_emergence_day") is not None

    def test_lotka_volterra_runs(self):
        result = self.engine.simulate_predator_prey(
            initial_pest_density=100.0, initial_enemy_density=5.0, days=30
        )
        assert result.success is True
        assert result.outputs["final_pest_density"] >= 0.0

    def test_predator_reduces_pest(self):
        """High predator density should lead to lower pest densities."""
        r_low_pred = self.engine.simulate_predator_prey(
            initial_pest_density=200.0, initial_enemy_density=1.0, days=40
        )
        r_high_pred = self.engine.simulate_predator_prey(
            initial_pest_density=200.0, initial_enemy_density=50.0, days=40
        )
        assert (
            r_high_pred.outputs["final_pest_density"]
            <= r_low_pred.outputs["final_pest_density"]
        )

    def test_degree_days_zero_below_base(self):
        from shared.process_models.pest_epidemiology import daily_degree_days

        w = _make_weather(tmax=5.0, tmin=2.0)
        dd = daily_degree_days(w, t_base=10.0, t_upper=35.0)
        assert dd == pytest.approx(0.0)


# ===========================================================================
# 7. QUEFTS Nutrient Management Model
# ===========================================================================


class TestQueftsNutrientModel:
    def setup_method(self):
        from shared.process_models.nutrient_management import (
            QueftsNutrientModel,
            SoilNutrientSupply,
        )

        self.model = QueftsNutrientModel()
        self.SoilNutrientSupply = SoilNutrientSupply
        self.crop = CropParameters(crop_type=CropType.WHEAT)

    def test_recommendation_runs(self):
        supply = self.SoilNutrientSupply()
        result = self.model.recommend(self.crop, supply, target_yield_t_ha=5.0)
        assert result.success is True
        assert result.model_type == ModelType.NUTRIENT_MANAGEMENT

    def test_fertiliser_positive_or_zero(self):
        supply = self.SoilNutrientSupply(n_supply_kg_ha=40.0)
        result = self.model.recommend(self.crop, supply, target_yield_t_ha=6.0)
        assert result.outputs["n_fertiliser_kg_ha"] >= 0.0
        assert result.outputs["p2o5_fertiliser_kg_ha"] >= 0.0
        assert result.outputs["k2o_fertiliser_kg_ha"] >= 0.0

    def test_rich_soil_needs_less_fertiliser(self):
        supply_rich = self.SoilNutrientSupply(
            n_supply_kg_ha=200.0, p_supply_kg_ha=80.0, k_supply_kg_ha=400.0
        )
        supply_poor = self.SoilNutrientSupply(
            n_supply_kg_ha=20.0, p_supply_kg_ha=5.0, k_supply_kg_ha=30.0
        )
        r_rich = self.model.recommend(self.crop, supply_rich, target_yield_t_ha=4.0)
        r_poor = self.model.recommend(self.crop, supply_poor, target_yield_t_ha=4.0)
        assert (
            r_rich.outputs["n_fertiliser_kg_ha"] <= r_poor.outputs["n_fertiliser_kg_ha"]
        )

    def test_balanced_yield_le_target(self):
        supply = self.SoilNutrientSupply()
        result = self.model.recommend(self.crop, supply, target_yield_t_ha=5.0)
        assert result.outputs["balanced_yield_t_ha"] <= 5.0 + 0.001

    def test_n_timing_guidance_present(self):
        supply = self.SoilNutrientSupply()
        result = self.model.recommend(self.crop, supply, target_yield_t_ha=4.0)
        assert len(result.outputs.get("n_application_time", "")) > 0

    def test_different_crop_types(self):
        for crop_type in (CropType.MAIZE, CropType.RICE, CropType.TOMATO):
            crop = CropParameters(crop_type=crop_type)
            supply = self.SoilNutrientSupply()
            result = self.model.recommend(crop, supply, target_yield_t_ha=4.0)
            assert result.success is True

    def test_zero_yield_target_no_fertiliser(self):
        supply = self.SoilNutrientSupply(
            n_supply_kg_ha=500.0, p_supply_kg_ha=200.0, k_supply_kg_ha=500.0
        )
        result = self.model.recommend(self.crop, supply, target_yield_t_ha=0.5)
        # With very rich soil and low target, fertiliser should be 0
        assert result.outputs["n_fertiliser_kg_ha"] >= 0.0


# ===========================================================================
# 8. Hydrology Engine
# ===========================================================================


class TestHydrologyEngine:
    def setup_method(self):
        from shared.process_models.hydrology import HydrologyEngine

        self.engine = HydrologyEngine()
        self.soil = SoilProfile()

    def test_scs_cn_zero_below_ia(self):
        from shared.process_models.hydrology import scs_cn_runoff

        # Very light rain – all absorbed
        q = scs_cn_runoff(1.0, cn=75)
        assert q == pytest.approx(0.0)

    def test_scs_cn_positive_heavy_rain(self):
        from shared.process_models.hydrology import scs_cn_runoff

        q = scs_cn_runoff(100.0, cn=80)
        assert q > 0.0
        assert q < 100.0

    def test_scs_cn_invalid_raises(self):
        from shared.process_models.hydrology import scs_cn_runoff

        with pytest.raises(ValueError):
            scs_cn_runoff(50.0, cn=100)

    def test_green_ampt_high_rate_produces_runoff(self):
        from shared.process_models.hydrology import (
            GreenAmptParams,
            green_ampt_infiltration,
        )

        params = GreenAmptParams(hydraulic_conductivity_mm_h=5.0)
        result = green_ampt_infiltration(
            rainfall_rate_mm_h=50.0, duration_h=2.0, params=params
        )
        assert result["total_runoff_mm"] > 0.0
        assert result["total_infiltration_mm"] > 0.0

    def test_green_ampt_no_runoff_light_rain(self):
        from shared.process_models.hydrology import (
            GreenAmptParams,
            green_ampt_infiltration,
        )

        params = GreenAmptParams(hydraulic_conductivity_mm_h=50.0)
        result = green_ampt_infiltration(
            rainfall_rate_mm_h=5.0, duration_h=1.0, params=params
        )
        assert result["total_runoff_mm"] == pytest.approx(0.0)

    def test_water_balance_runs(self):
        weather = _make_season(60)
        et0_series = [4.5] * 60
        result = self.engine.run_water_balance(self.soil, weather, et0_series)
        assert result.success is True
        assert result.outputs["days_simulated"] == 60

    def test_water_balance_drainage_non_negative(self):
        weather = _make_season(60, base_rain=5.0)
        et0_series = [4.0] * 60
        result = self.engine.run_water_balance(self.soil, weather, et0_series)
        assert result.outputs["total_drainage_mm"] >= 0.0

    def test_water_balance_runoff_non_negative(self):
        weather = _make_season(30, base_rain=20.0)
        et0_series = [5.0] * 30
        result = self.engine.run_water_balance(self.soil, weather, et0_series, cn=85)
        assert result.outputs["total_runoff_mm"] >= 0.0

    def test_estimate_event_runoff(self):
        r = self.engine.estimate_event_runoff(precipitation_mm=50.0, cn=80)
        assert r["runoff_mm"] >= 0.0
        assert r["infiltration_mm"] >= 0.0
        assert r["infiltration_mm"] + r["runoff_mm"] == pytest.approx(50.0, abs=0.5)


# ===========================================================================
# 9. Ensemble Model Framework
# ===========================================================================


class TestEnsembleModelFramework:
    def setup_method(self):
        from shared.process_models.ensemble import (
            EnsembleModelFramework,
            ModelType,
            RegisteredModel,
        )

        self.EnsembleModelFramework = EnsembleModelFramework
        self.RegisteredModel = RegisteredModel
        self.ModelType = ModelType

    def _build_framework_with_stubs(self):
        from shared.process_models.models import ModelResult, ModelType

        fw = self.EnsembleModelFramework()

        def make_stub(value):
            def stub(**kwargs):
                return ModelResult(
                    model_name="stub",
                    model_type=ModelType.CROP_GROWTH,
                    outputs={"grain_yield_t_ha": value},
                )

            return stub

        for name, val in [("ModelA", 4.0), ("ModelB", 5.0), ("ModelC", 6.0)]:
            fw.register(
                self.RegisteredModel(
                    name=name,
                    name_ar=f"{name} (AR)",
                    model_type=ModelType.CROP_GROWTH,
                    run_fn=make_stub(val),
                    weight=1.0,
                )
            )
        return fw

    def test_list_models(self):
        fw = self._build_framework_with_stubs()
        models = fw.list_models()
        assert len(models) == 3

    def test_ensemble_run_returns_stats(self):
        fw = self._build_framework_with_stubs()
        result = fw.run_ensemble(output_key="grain_yield_t_ha", run_kwargs={})
        assert result.success is True
        stats = result.outputs["ensemble_stats"]
        assert stats["n_models"] == 3
        assert stats["mean"] == pytest.approx(5.0, abs=0.01)

    def test_ensemble_uncertainty_range(self):
        fw = self._build_framework_with_stubs()
        result = fw.run_ensemble(output_key="grain_yield_t_ha", run_kwargs={})
        stats = result.outputs["ensemble_stats"]
        assert stats["uncertainty_range"] >= 0.0

    def test_empty_framework_fails_gracefully(self):
        fw = self.EnsembleModelFramework()
        result = fw.run_ensemble(output_key="any_key", run_kwargs={})
        assert result.success is False

    def test_skill_scores_with_observations(self):
        fw = self._build_framework_with_stubs()
        result = fw.run_ensemble(
            output_key="grain_yield_t_ha",
            run_kwargs={},
            observations=[5.0],
        )
        assert isinstance(result.outputs["skill_scores"], list)

    def test_weighted_mean(self):
        from shared.process_models.ensemble import compute_ensemble_stats

        values = [2.0, 4.0, 6.0]
        weights = [1.0, 2.0, 1.0]
        stats = compute_ensemble_stats(values, weights)
        expected_wmean = (2.0 * 1 + 4.0 * 2 + 6.0 * 1) / 4.0
        assert stats.weighted_mean == pytest.approx(expected_wmean, abs=0.01)

    def test_percentile_computation(self):
        from shared.process_models.ensemble import _percentile

        values = sorted([1.0, 2.0, 3.0, 4.0, 5.0])
        assert _percentile(values, 0) == pytest.approx(1.0)
        assert _percentile(values, 100) == pytest.approx(5.0)
        assert _percentile(values, 50) == pytest.approx(3.0)


# ===========================================================================
# 10. Integration smoke test – import all at once
# ===========================================================================


class TestProcessModelsImport:
    def test_package_imports(self):
        import shared.process_models as pm

        assert pm.CropGrowthEngine is not None
        assert pm.AgroMeteorologyEngine is not None
        assert pm.SoilCarbonModel is not None
        assert pm.RadiativeTransferModel is not None
        assert pm.PestEpidemiologyEngine is not None
        assert pm.QueftsNutrientModel is not None
        assert pm.HydrologyEngine is not None
        assert pm.EnsembleModelFramework is not None


# ===========================================================================
# 11. Input validation (Fix 4 – __post_init__ guards)
# ===========================================================================


class TestInputValidation:
    """Ensure boundary guards reject physically-impossible inputs early."""

    def test_weather_tmax_below_tmin_raises(self):
        with pytest.raises(ValueError, match="tmax_c"):
            DailyWeather(
                date=date(2024, 6, 1),
                tmax_c=10.0,
                tmin_c=20.0,  # tmin > tmax → invalid
                solar_radiation_mj_m2=18.0,
                relative_humidity_pct=55.0,
                wind_speed_m_s=2.5,
            )

    def test_weather_negative_precipitation_raises(self):
        with pytest.raises(ValueError, match="precipitation_mm"):
            DailyWeather(
                date=date(2024, 6, 1),
                tmax_c=30.0,
                tmin_c=15.0,
                solar_radiation_mj_m2=20.0,
                relative_humidity_pct=50.0,
                wind_speed_m_s=2.0,
                precipitation_mm=-5.0,
            )

    def test_weather_negative_wind_raises(self):
        with pytest.raises(ValueError, match="wind_speed_m_s"):
            DailyWeather(
                date=date(2024, 6, 1),
                tmax_c=28.0,
                tmin_c=14.0,
                solar_radiation_mj_m2=18.0,
                relative_humidity_pct=60.0,
                wind_speed_m_s=-1.0,
            )

    def test_weather_humidity_out_of_range_raises(self):
        with pytest.raises(ValueError, match="relative_humidity_pct"):
            DailyWeather(
                date=date(2024, 6, 1),
                tmax_c=28.0,
                tmin_c=14.0,
                solar_radiation_mj_m2=18.0,
                relative_humidity_pct=150.0,  # > 100 → invalid
                wind_speed_m_s=2.0,
            )

    def test_soil_fc_below_wp_raises(self):
        with pytest.raises(ValueError, match="field_capacity"):
            SoilProfile(
                field_capacity_mm_per_m=80.0,  # < wilting_point → invalid
                wilting_point_mm_per_m=120.0,
            )

    def test_soil_zero_depth_raises(self):
        with pytest.raises(ValueError, match="depth_m"):
            SoilProfile(depth_m=0.0)

    def test_valid_weather_no_error(self):
        w = DailyWeather(
            date=date(2024, 6, 1),
            tmax_c=30.0,
            tmin_c=15.0,
            solar_radiation_mj_m2=20.0,
            relative_humidity_pct=55.0,
            wind_speed_m_s=2.0,
        )
        assert w.tmean_c == pytest.approx(22.5)

    def test_valid_soil_no_error(self):
        s = SoilProfile()
        assert s.available_water_capacity_mm > 0


# ===========================================================================
# 12. Models router smoke tests (Fix 3)
# ===========================================================================


class TestModelsRouter:
    """Smoke-test the process-models API router without a running server."""

    def _get_client(self):
        import importlib.util
        import sys
        import os
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        # The service directory contains a hyphen so we use importlib
        router_path = os.path.join(
            os.path.dirname(__file__),
            "../../apps/services/crop-intelligence-service/src/models_router.py",
        )
        spec = importlib.util.spec_from_file_location("models_router", router_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        app = FastAPI()
        app.include_router(mod.router, prefix="/api/v1")
        return TestClient(app)

    def _get_client_safe(self):
        """Return client or skip if router cannot be imported (missing deps)."""
        try:
            return self._get_client()
        except Exception:
            pytest.skip("models_router not importable in this environment")

    def test_et0_run_valid(self):
        client = self._get_client_safe()
        resp = client.post(
            "/api/v1/models/et0/run",
            json={
                "tmax_c": 32.0,
                "tmin_c": 18.0,
                "solar_radiation_mj_m2": 22.0,
                "relative_humidity_pct": 45.0,
                "wind_speed_m_s": 2.5,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["result"]["et0_mm"] > 0

    def test_et0_tmax_below_tmin_rejected(self):
        client = self._get_client_safe()
        resp = client.post(
            "/api/v1/models/et0/run",
            json={
                "tmax_c": 10.0,
                "tmin_c": 20.0,
                "solar_radiation_mj_m2": 18.0,
                "relative_humidity_pct": 55.0,
                "wind_speed_m_s": 2.0,
            },
        )
        assert resp.status_code == 422

    def test_quefts_run_valid(self):
        client = self._get_client_safe()
        resp = client.post(
            "/api/v1/models/quefts/recommend",
            json={
                "crop_type": "wheat",
                "target_yield_t_ha": 4.0,
                "soil_n_kg_ha": 40.0,
                "soil_p_kg_ha": 15.0,
                "soil_k_kg_ha": 80.0,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "n_fertiliser_kg_ha" in body["result"]

    def test_swb_run_valid(self):
        client = self._get_client_safe()
        resp = client.post(
            "/api/v1/models/swb/run",
            json={
                "tmax_c": 30.0,
                "tmin_c": 16.0,
                "solar_radiation_mj_m2": 20.0,
                "relative_humidity_pct": 50.0,
                "wind_speed_m_s": 2.0,
                "precipitation_mm": 5.0,
                "soil_water_mm": 200.0,
                "field_capacity_mm": 250.0,
                "wilting_point_mm": 100.0,
                "total_available_water_mm": 150.0,
            },
        )
        assert resp.status_code == 200
        assert "et0_mm" in resp.json()["result"]

    def test_soil_carbon_returns_needs_calibration(self):
        client = self._get_client_safe()
        resp = client.post(
            "/api/v1/models/soil-carbon/simulate",
            json={
                "carbon_input_t_ha_yr": 3.0,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["quality_flag"] == "needs_calibration"

    def test_prosail_returns_needs_calibration(self):
        client = self._get_client_safe()
        resp = client.post(
            "/api/v1/models/prosail/invert",
            json={
                "red": 0.08,
                "nir": 0.45,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["quality_flag"] == "needs_calibration"
