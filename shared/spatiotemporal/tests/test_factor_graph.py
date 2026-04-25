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
    assert solutions[0].covariance[("ndvi", "ndvi")] == pytest.approx(
        1 / (1 / 0.04 + 1 / 0.01), abs=1e-9
    )


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
