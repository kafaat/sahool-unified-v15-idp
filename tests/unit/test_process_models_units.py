# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.process_models.units."""

from __future__ import annotations

import pytest

from shared.process_models.units import (
    UnitError,
    to_ds_per_m,
    to_kg_per_ha,
    to_mm,
)


pytestmark = pytest.mark.unit


# ── Salinity ─────────────────────────────────────────────────────────────


def test_ds_per_m_is_identity() -> None:
    assert to_ds_per_m(3.5, "dS/m") == 3.5


def test_ms_per_cm_equals_ds_per_m() -> None:
    """The classic literature error: 1 dS/m == 1 mS/cm, not 10:1."""
    assert to_ds_per_m(3.5, "mS/cm") == 3.5


def test_s_per_m_is_ten_times_ds_per_m() -> None:
    assert to_ds_per_m(0.5, "S/m") == pytest.approx(5.0)


def test_micro_units_scale_correctly() -> None:
    assert to_ds_per_m(1500.0, "uS/cm") == pytest.approx(1.5)


def test_unknown_salinity_unit_rejected() -> None:
    with pytest.raises(UnitError):
        to_ds_per_m(1.0, "ppm")


# ── Fertiliser ───────────────────────────────────────────────────────────


def test_kg_ha_identity() -> None:
    assert to_kg_per_ha(120.0, "kg/ha") == 120.0


def test_g_per_m2_to_kg_per_ha() -> None:
    assert to_kg_per_ha(10.0, "g/m2") == pytest.approx(100.0)


def test_litres_per_feddan_is_rejected_not_guessed() -> None:
    """Decision Kernel invariant: ambiguous units are rejected, not guessed."""
    with pytest.raises(UnitError, match="Ambiguous"):
        to_kg_per_ha(50.0, "litres/feddan")


def test_litres_feddan_variants_all_rejected() -> None:
    for unit in ("l/feddan", "liter/feddan", "litre/feddan", "Litres/Feddan"):
        with pytest.raises(UnitError):
            to_kg_per_ha(50.0, unit)


# ── Irrigation depth ─────────────────────────────────────────────────────


def test_mm_identity() -> None:
    assert to_mm(20.0, "mm") == 20.0


def test_cm_to_mm() -> None:
    assert to_mm(2.5, "cm") == 25.0


def test_inch_to_mm() -> None:
    assert to_mm(1.0, "in") == pytest.approx(25.4)


def test_unknown_depth_unit_rejected() -> None:
    with pytest.raises(UnitError):
        to_mm(1.0, "leagues")
