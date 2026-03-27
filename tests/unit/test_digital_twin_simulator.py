"""Tests for digital twin simulation module."""

import pytest

from shared.digital_twin.simulator import (
    DigitalTwinSimulator,
    ImpactLevel,
    ScenarioType,
)


class TestDigitalTwinSimulator:
    def setup_method(self):
        self.sim = DigitalTwinSimulator()

    def test_irrigation_increase(self):
        result = self.sim.simulate_irrigation_change(
            field_id="F-001",
            tenant_id="T-001",
            crop_type="wheat",
            current_water_mm=400,
            proposed_change_percent=20,
        )
        assert result.scenario_type == ScenarioType.IRRIGATION_CHANGE
        assert result.water_impact.change_percent == 20

    def test_irrigation_decrease(self):
        result = self.sim.simulate_irrigation_change(
            field_id="F-001",
            tenant_id="T-001",
            crop_type="wheat",
            current_water_mm=400,
            proposed_change_percent=-30,
        )
        assert result.water_impact.change_percent == -30

    def test_excess_water_warning(self):
        result = self.sim.simulate_irrigation_change(
            field_id="F-001",
            tenant_id="T-001",
            crop_type="wheat",
            current_water_mm=500,
            proposed_change_percent=50,
        )
        assert len(result.risk_assessment.warnings) > 0

    def test_fertilizer_delay(self):
        result = self.sim.simulate_fertilizer_timing(
            field_id="F-001",
            tenant_id="T-001",
            crop_type="wheat",
            delay_days=7,
        )
        assert result.yield_impact.change_percent < 0

    def test_fertilizer_delay_critical_stage(self):
        result = self.sim.simulate_fertilizer_timing(
            field_id="F-001",
            tenant_id="T-001",
            crop_type="wheat",
            delay_days=7,
            growth_stage="heading",
        )
        assert result.yield_impact.change_percent < 0

    def test_crop_variety_change(self):
        result = self.sim.simulate_crop_variety(
            field_id="F-001",
            tenant_id="T-001",
            current_crop="wheat",
            proposed_crop="barley",
        )
        assert result.scenario_type == ScenarioType.CROP_VARIETY
        assert result.yield_impact.predicted_yield_ton_ha > 0

    def test_simulation_has_arabic(self):
        result = self.sim.simulate_irrigation_change(
            field_id="F-001",
            tenant_id="T-001",
            crop_type="wheat",
            current_water_mm=400,
            proposed_change_percent=20,
        )
        assert result.scenario_type_ar != ""
        assert result.description_ar != ""
        assert result.recommendation_ar != ""
