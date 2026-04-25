# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the PROSAIL LUT generator and inversion (ADR-015)."""

from __future__ import annotations

import pytest

from shared.process_models.prosail_inversion import (
    ProsailGeometry,
    generate_lut,
    invert,
)
from shared.process_models.radiative_transfer import (
    CanopyParameters,
    LeafOpticalProperties,
    prospect_reflectance,
    sail_canopy_reflectance,
)


_GEOM = ProsailGeometry(sun_zenith_deg=30.0, view_zenith_deg=0.0, relative_azimuth_deg=0.0)


def _forward_truth(lai: float, cab: float) -> dict[str, float]:
    leaf = LeafOpticalProperties(chlorophyll_ug_cm2=cab)
    canopy = CanopyParameters(
        lai=lai,
        sun_zenith_deg=_GEOM.sun_zenith_deg,
        view_zenith_deg=_GEOM.view_zenith_deg,
    )
    return sail_canopy_reflectance(prospect_reflectance(leaf), canopy)


def test_generate_lut_size_is_density_per_axis() -> None:
    lut = generate_lut(
        {"LAI": (0.5, 6.0), "Cab": (10.0, 60.0)},
        density=4,
        geometry=_GEOM,
    )
    assert len(lut) == 4 * 4


def test_generate_lut_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        generate_lut({}, density=4, geometry=_GEOM)
    with pytest.raises(ValueError):
        generate_lut({"LAI": (0.5, 0.5)}, density=4, geometry=_GEOM)
    with pytest.raises(ValueError):
        generate_lut({"LAI": (0.5, 6.0)}, density=1, geometry=_GEOM)
    with pytest.raises(ValueError):
        generate_lut({"unknown_param": (0.0, 1.0)}, density=4, geometry=_GEOM)


def test_invert_recovers_lut_grid_point_exactly() -> None:
    lut = generate_lut(
        {"LAI": (0.5, 6.0), "Cab": (10.0, 60.0)},
        density=8,
        geometry=_GEOM,
    )
    truth_idx = 17  # arbitrary interior index
    target_params = lut.parameters[truth_idx]
    target_ref = lut.reflectances[truth_idx]
    retrieval = invert(target_ref, _GEOM, lut=lut, top_k=1)
    assert retrieval.parameters["LAI"] == pytest.approx(target_params["LAI"], abs=1e-9)
    assert retrieval.parameters["Cab"] == pytest.approx(target_params["Cab"], abs=1e-9)
    assert retrieval.diagnostics["best_distance"] == pytest.approx(0.0, abs=1e-9)


def test_invert_recovers_known_truth_within_grid_tolerance() -> None:
    lut = generate_lut(
        {"LAI": (0.5, 6.0), "Cab": (10.0, 60.0)},
        density=12,
        geometry=_GEOM,
    )
    truth = _forward_truth(lai=2.5, cab=35.0)
    retrieval = invert(truth, _GEOM, lut=lut, top_k=5)
    # Grid step on LAI is (6.0-0.5)/11 ≈ 0.5; on Cab (60-10)/11 ≈ 4.5.
    assert retrieval.parameters["LAI"] == pytest.approx(2.5, abs=0.6)
    assert retrieval.parameters["Cab"] == pytest.approx(35.0, abs=6.0)
    assert retrieval.uncertainty["LAI"] >= 0.0
    assert retrieval.uncertainty["Cab"] >= 0.0


def test_invert_rejects_geometry_mismatch() -> None:
    lut = generate_lut(
        {"LAI": (0.5, 6.0)},
        density=4,
        geometry=_GEOM,
    )
    other = ProsailGeometry(sun_zenith_deg=45.0, view_zenith_deg=0.0, relative_azimuth_deg=0.0)
    with pytest.raises(ValueError, match="geometry mismatch"):
        invert(lut.reflectances[0], other, lut=lut)


def test_invert_rejects_invalid_top_k() -> None:
    lut = generate_lut({"LAI": (0.5, 6.0)}, density=4, geometry=_GEOM)
    with pytest.raises(ValueError):
        invert(lut.reflectances[0], _GEOM, lut=lut, top_k=0)
