# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the factor-graph batch optimizer (ADR-011)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.spatiotemporal import FactorGraph, FusionConfig, SensorFrame


def _frame(ms: int, value: float, var: float = 0.01) -> SensorFrame:
    return SensorFrame(
        sensor_id=f"s{ms}",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms),
        position=(0.0, 0.0, None),
        values={"ndvi": value},
        covariance={"ndvi": var},
    )


def test_empty_graph_returns_empty_solution() -> None:
    fg = FactorGraph(FusionConfig())
    assert fg.optimize() == []


def test_single_bundle_information_weighted_mean() -> None:
    fg = FactorGraph(FusionConfig(alignment_window_ms=500))
    fg.add_frames([_frame(0, 0.6, var=0.04), _frame(100, 0.8, var=0.01)])
    solutions = fg.optimize()
    assert len(solutions) == 1
    # Information-weighted mean: (0.6/0.04 + 0.8/0.01) / (1/0.04 + 1/0.01)
    expected = (0.6 / 0.04 + 0.8 / 0.01) / (1 / 0.04 + 1 / 0.01)
    assert solutions[0].state["ndvi"] == pytest.approx(expected, abs=1e-9)
    # Posterior variance is 1 / sum-of-information.
    assert solutions[0].covariance[("ndvi", "ndvi")] == pytest.approx(1 / (1 / 0.04 + 1 / 0.01), abs=1e-9)


def test_multiple_windows_emit_one_state_each() -> None:
    fg = FactorGraph(FusionConfig(alignment_window_ms=500))
    fg.add_frames([_frame(0, 0.5), _frame(700, 0.9)])
    solutions = fg.optimize()
    assert len(solutions) == 2
    assert solutions[0].state["ndvi"] == pytest.approx(0.5)
    assert solutions[1].state["ndvi"] == pytest.approx(0.9)


def test_diagnostics_contain_bundle_size_and_channels() -> None:
    fg = FactorGraph(FusionConfig())
    fg.add_frames([_frame(0, 0.5), _frame(100, 0.6)])
    solutions = fg.optimize()
    assert solutions[0].diagnostics["bundle_size"] == 2
    assert solutions[0].diagnostics["channels"] == ["ndvi"]


def test_auto_solver_picks_closed_form_for_diagonal_inputs() -> None:
    fg = FactorGraph(FusionConfig(solver="auto"))
    fg.add_frames([_frame(0, 0.5), _frame(100, 0.6)])
    solutions = fg.optimize()
    assert solutions[0].diagnostics["solver"] == "closed_form"


def test_cholesky_solver_matches_closed_form_on_diagonal_inputs() -> None:
    """Bit-equivalence on diagonal R is the contract that lets us
    swap solvers without changing observed behaviour for v3.1 callers.
    """

    frames = [_frame(0, 0.6, var=0.04), _frame(100, 0.8, var=0.01)]
    fg_closed = FactorGraph(FusionConfig(alignment_window_ms=500, solver="closed_form"))
    fg_cholesky = FactorGraph(FusionConfig(alignment_window_ms=500, solver="cholesky"))
    fg_closed.add_frames(frames)
    fg_cholesky.add_frames(frames)
    a = fg_closed.optimize()[0]
    b = fg_cholesky.optimize()[0]
    assert a.state["ndvi"] == pytest.approx(b.state["ndvi"], abs=1e-12)
    assert a.covariance[("ndvi", "ndvi")] == pytest.approx(b.covariance[("ndvi", "ndvi")], abs=1e-12)


def test_cholesky_solver_handles_correlated_two_band_measurement() -> None:
    """A single sensor reports two correlated bands; Cholesky must
    propagate the correlation into the posterior covariance.
    """

    frame = SensorFrame(
        sensor_id="multispec",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        position=(0.0, 0.0, None),
        values={"red": 0.10, "nir": 0.45},
        covariance={"red": 0.0004, "nir": 0.0009},  # ~0.02 / 0.03 1-σ
        cross_covariance={("red", "nir"): 0.0003},  # ρ ≈ 0.5
    )
    fg = FactorGraph(FusionConfig(solver="auto"))
    fg.add_frames([frame])
    solutions = fg.optimize()
    assert len(solutions) == 1
    sol = solutions[0]
    assert sol.diagnostics["solver"] == "cholesky"
    # Mean must equal the single observation (only one frame in the bundle).
    assert sol.state["red"] == pytest.approx(0.10, abs=1e-9)
    assert sol.state["nir"] == pytest.approx(0.45, abs=1e-9)
    # Posterior covariance must equal the input covariance for a single
    # frame with H = I (the information matrix is just R⁻¹).
    assert sol.covariance[("red", "red")] == pytest.approx(0.0004, abs=1e-12)
    assert sol.covariance[("nir", "nir")] == pytest.approx(0.0009, abs=1e-12)
    # The off-diagonal must be present and equal the input cross term.
    off = sol.covariance.get(("red", "nir")) or sol.covariance.get(("nir", "red"))
    assert off == pytest.approx(0.0003, abs=1e-12)


def test_closed_form_solver_rejects_cross_covariance() -> None:
    frame = SensorFrame(
        sensor_id="s",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        position=(0.0, 0.0, None),
        values={"red": 0.1, "nir": 0.4},
        covariance={"red": 0.01, "nir": 0.01},
        cross_covariance={("red", "nir"): 0.001},
    )
    fg = FactorGraph(FusionConfig(solver="closed_form"))
    fg.add_frames([frame])
    with pytest.raises(ValueError, match="closed-form solver cannot handle"):
        fg.optimize()


def test_invalid_solver_choice_rejected() -> None:
    with pytest.raises(ValueError, match="solver must be one of"):
        FactorGraph(FusionConfig(solver="quantum"))
