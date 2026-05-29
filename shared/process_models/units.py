# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit Normalisation Boundary - توحيد الوحدات عند الحدود
========================================================
Strict validator/converter run at every measurement entry into the
decision pipeline. Refuses ambiguous units rather than guessing silently.

Canonical units used downstream by digital_twin and process_models engines:

    salinity:     dS/m   (1 dS/m == 1 mS/cm — not 10:1)
    fertiliser:   kg/ha
    irrigation:   mm
    rainfall:     mm
    radiation:    MJ/m²/day
    temperature:  °C

Decision Kernel invariant: ambiguous units are rejected — silent guessing
is the most expensive failure mode in agriculture.
"""

from __future__ import annotations

from dataclasses import dataclass


class UnitError(ValueError):
    """Raised when a unit is unsupported, ambiguous, or wrongly converted."""


# Canonical EC equivalence: 1 dS/m == 1 mS/cm (== 0.1 S/m).
# A 10× mis-conversion is a recurring literature error; we encode the truth.
_SALINITY_TO_DS_M: dict[str, float] = {
    "ds/m": 1.0,
    "ds m-1": 1.0,
    "ds·m-1": 1.0,
    "ms/cm": 1.0,
    "mmho/cm": 1.0,  # historical synonym
    "umho/cm": 1e-3,
    "us/cm": 1e-3,
    "s/m": 10.0,
}

# Fertiliser dose conversions to kg/ha.
_FERTILISER_TO_KG_HA: dict[str, float] = {
    "kg/ha": 1.0,
    "kg ha-1": 1.0,
    "kg/acre": 2.4710538147,  # 1 ha = 2.4710538147 acres
    "lb/acre": 1.12085,  # to kg/ha
    "g/m2": 10.0,
}

# Depth conversions to mm.
_DEPTH_TO_MM: dict[str, float] = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
    "in": 25.4,
    "inch": 25.4,
}


def _norm(unit: str) -> str:
    """Lower-case, strip whitespace. Internal — keep stable."""
    return unit.strip().lower().replace(" ", "")


def _lookup(table: dict[str, float], unit: str) -> float:
    """Find a normalised unit in a table; raise UnitError if missing."""
    key = _norm(unit)
    for raw, factor in table.items():
        if _norm(raw) == key:
            return factor
    raise UnitError(f"Unsupported unit: {unit!r}")


def to_ds_per_m(value: float, unit: str) -> float:
    """Convert a salinity reading to dS/m. Raises UnitError on unknown unit."""
    return value * _lookup(_SALINITY_TO_DS_M, unit)


def to_kg_per_ha(
    value: float,
    unit: str,
    *,
    area_ha: float | None = None,
) -> float:
    """
    Convert a fertiliser dose to kg/ha.

    Vague volumetric units like ``litres/feddan`` are REJECTED — they require
    both a product density and a parcel area to be expressed in kg/ha, and
    silently filling in either of those is the most expensive failure mode.
    """
    key = _norm(unit)
    if key in {"l/feddan", "liter/feddan", "litre/feddan", "litres/feddan"}:
        raise UnitError("Ambiguous unit 'litres/feddan' — supply product density and parcel area explicitly.")
    return value * _lookup(_FERTILISER_TO_KG_HA, unit)


def to_mm(value: float, unit: str) -> float:
    """Convert an irrigation/rainfall depth to mm. Raises UnitError on unknown unit."""
    return value * _lookup(_DEPTH_TO_MM, unit)


@dataclass(frozen=True)
class NormalisedMeasurement:
    """A measurement after unit normalisation. Use this past the boundary."""

    value: float
    unit: str  # canonical unit after normalisation
    original_unit: str  # the unit as supplied by the caller


__all__ = [
    "UnitError",
    "to_ds_per_m",
    "to_kg_per_ha",
    "to_mm",
    "NormalisedMeasurement",
]
