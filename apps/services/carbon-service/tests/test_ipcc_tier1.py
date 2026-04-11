"""
Unit tests for the IPCC Tier 1 engine — pure function, no I/O, fast.

Golden values here were hand-computed from the public IPCC 2019
refinement factors and rounded to two decimal places. Changes that
bump the engine's outputs will fail these tests — intentional, so
factor updates require explicit developer review.
"""

from __future__ import annotations

import pytest
from src.engine import IpccTier1Engine, OperationInput


@pytest.fixture
def engine() -> IpccTier1Engine:
    return IpccTier1Engine()


# ---------------------------------------------------------------------------
# Fuel
# ---------------------------------------------------------------------------


def test_diesel_fuel_only(engine: IpccTier1Engine):
    """10 L diesel → 10 × 2.70 = 27.0 kg CO2e."""
    result = engine.compute(
        OperationInput(
            operation_id="op-1",
            operation_type="plowing",
            fuel_liters=10.0,
            fuel_type="diesel",
        )
    )
    assert result.emissions_kg == 27.0
    assert result.sequestration_kg == 0.0
    assert result.net_kg == 27.0
    assert result.emission_source_type == "fuel"
    assert not result.carbon_credit_eligible


def test_gasoline_fuel_only(engine: IpccTier1Engine):
    """5 L gasoline → 5 × 2.34 = 11.70 kg CO2e."""
    result = engine.compute(
        OperationInput(
            operation_id="op-2",
            operation_type="spraying",
            fuel_liters=5.0,
            fuel_type="gasoline",
        )
    )
    assert result.emissions_kg == 11.70


# ---------------------------------------------------------------------------
# Fertiliser
# ---------------------------------------------------------------------------


def test_nitrogen_fertilizer(engine: IpccTier1Engine):
    """50 kg N → 50 × 6.11 = 305.50 kg CO2e."""
    result = engine.compute(
        OperationInput(
            operation_id="op-3",
            operation_type="fertilization",
            nitrogen_kg=50.0,
        )
    )
    assert result.emissions_kg == 305.50
    assert result.breakdown.fertilizer_n == 305.50
    assert result.emission_source_type == "fertilizer_n"


def test_mixed_npk(engine: IpccTier1Engine):
    """N=46, P=30, K=20 → 46×6.11 + 30×1.50 + 20×0.65 = 334.06."""
    result = engine.compute(
        OperationInput(
            operation_id="op-4",
            operation_type="fertilization",
            nitrogen_kg=46.0,
            phosphorus_kg=30.0,
            potassium_kg=20.0,
        )
    )
    expected = 46 * 6.11 + 30 * 1.50 + 20 * 0.65
    assert result.emissions_kg == round(expected, 2)


# ---------------------------------------------------------------------------
# Machinery
# ---------------------------------------------------------------------------


def test_machinery_hours(engine: IpccTier1Engine):
    """6 h × 3.2 = 19.20 kg CO2e."""
    result = engine.compute(
        OperationInput(
            operation_id="op-5",
            operation_type="plowing",
            duration_hours=6.0,
        )
    )
    assert result.emissions_kg == 19.20
    # breakdown.machinery is NOT rounded (the engine only rounds the
    # aggregated emissions_kg/sequestration_kg/net_kg totals), so use
    # pytest.approx to absorb the trailing-float-precision residue.
    assert result.breakdown.machinery == pytest.approx(19.20, abs=1e-6)


def test_combined_fuel_and_machinery(engine: IpccTier1Engine):
    """Plowing: 10 L diesel + 4 h machinery = 27.0 + 12.8 = 39.80."""
    result = engine.compute(
        OperationInput(
            operation_id="op-6",
            operation_type="plowing",
            duration_hours=4.0,
            fuel_liters=10.0,
        )
    )
    assert result.emissions_kg == 39.80


# ---------------------------------------------------------------------------
# Sequestration
# ---------------------------------------------------------------------------


def test_cover_cropping_sequestration(engine: IpccTier1Engine):
    """
    5 ha cover cropping — monthly share of 400 kg/ha/yr:
        5 × 400 / 12 = 166.67 kg CO2e sequestered
    """
    result = engine.compute(
        OperationInput(
            operation_id="op-7",
            operation_type="sowing",
            area_hectares=5.0,
            is_cover_cropping=True,
        )
    )
    assert result.sequestration_kg == pytest.approx(166.67, abs=0.01)
    assert result.net_kg == pytest.approx(-166.67, abs=0.01)
    assert result.carbon_credit_eligible is True
    assert result.emission_source_type == "sequestration"


def test_biochar_application(engine: IpccTier1Engine):
    """2 tonnes biochar × 2500 = 5000 kg CO2e sequestered."""
    result = engine.compute(
        OperationInput(
            operation_id="op-8",
            operation_type="other",
            biochar_tonnes=2.0,
        )
    )
    assert result.sequestration_kg == 5000.0
    assert result.carbon_credit_eligible is True


def test_mixed_emissions_and_sequestration(engine: IpccTier1Engine):
    """
    Cover crop (5 ha) + diesel fuel (3 L):
        Emissions    = 3 × 2.70 = 8.10
        Sequestration = 166.67
        Net = -158.57 (eligible because net < 0 AND cover cropping set)
    """
    result = engine.compute(
        OperationInput(
            operation_id="op-9",
            operation_type="sowing",
            area_hectares=5.0,
            fuel_liters=3.0,
            is_cover_cropping=True,
        )
    )
    assert result.emissions_kg == 8.10
    assert result.sequestration_kg == pytest.approx(166.67, abs=0.01)
    assert result.net_kg == pytest.approx(-158.57, abs=0.01)
    assert result.carbon_credit_eligible is True


def test_positive_net_not_eligible(engine: IpccTier1Engine):
    """Cover crop with HUGE fuel burn → net positive → not eligible."""
    result = engine.compute(
        OperationInput(
            operation_id="op-10",
            operation_type="sowing",
            area_hectares=5.0,
            fuel_liters=1000.0,
            is_cover_cropping=True,
        )
    )
    assert result.net_kg > 0
    assert result.carbon_credit_eligible is False


# ---------------------------------------------------------------------------
# Residue burning
# ---------------------------------------------------------------------------


def test_residue_burning_warning(engine: IpccTier1Engine):
    result = engine.compute(
        OperationInput(
            operation_id="op-11",
            operation_type="other",
            area_hectares=10.0,
            is_residue_burning=True,
        )
    )
    assert result.emissions_kg == 8500.0  # 10 × 850
    assert any("burning" in w.lower() for w in result.warnings)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_operation_produces_warning(engine: IpccTier1Engine):
    result = engine.compute(OperationInput(operation_id="op-12", operation_type="scouting"))
    assert result.emissions_kg == 0.0
    assert result.sequestration_kg == 0.0
    assert any("no computable inputs" in w.lower() for w in result.warnings)


def test_negative_values_ignored(engine: IpccTier1Engine):
    """Negative fuel liters (bad data) should not produce negative emissions."""
    result = engine.compute(
        OperationInput(
            operation_id="op-13",
            operation_type="plowing",
            fuel_liters=-5.0,
        )
    )
    assert result.emissions_kg == 0.0


def test_methodology_tag_is_ipcc_tier1(engine: IpccTier1Engine):
    result = engine.compute(
        OperationInput(
            operation_id="op-14",
            operation_type="plowing",
            fuel_liters=1.0,
        )
    )
    assert result.methodology == "IPCC-Tier1"


def test_rounding_to_two_decimals(engine: IpccTier1Engine):
    """Engine output is always rounded to 2 dp to match DECIMAL(12,2)."""
    result = engine.compute(
        OperationInput(
            operation_id="op-15",
            operation_type="fertilization",
            nitrogen_kg=1.0 / 3.0,  # 0.3333...
        )
    )
    # Rounded to 2dp: 0.333... × 6.11 = 2.0366... → 2.04
    assert result.emissions_kg == 2.04
