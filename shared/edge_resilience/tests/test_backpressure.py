# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the backpressure hysteresis controller (ADR-014)."""

from __future__ import annotations

import pytest

from shared.edge_resilience import (
    BackpressureController,
    BackpressureLevel,
    ResilienceConfig,
)


def _ctrl(high: float = 0.80, low: float = 0.60) -> BackpressureController:
    cfg = ResilienceConfig(backpressure_high=high, backpressure_low=low)
    return BackpressureController(cfg)


def test_starts_normal() -> None:
    assert _ctrl().level is BackpressureLevel.NORMAL


def test_stalls_above_high_threshold() -> None:
    ctrl = _ctrl()
    assert ctrl.evaluate(0.81) is BackpressureLevel.STALLED


def test_does_not_stall_at_or_below_high_threshold() -> None:
    ctrl = _ctrl()
    assert ctrl.evaluate(0.80) is BackpressureLevel.NORMAL
    assert ctrl.evaluate(0.79) is BackpressureLevel.NORMAL


def test_resumes_below_low_threshold() -> None:
    ctrl = _ctrl()
    ctrl.evaluate(0.95)  # → STALLED
    assert ctrl.level is BackpressureLevel.STALLED
    assert ctrl.evaluate(0.59) is BackpressureLevel.NORMAL


def test_hysteresis_avoids_thrash_between_thresholds() -> None:
    ctrl = _ctrl()
    ctrl.evaluate(0.95)  # STALLED
    # Between low and high while STALLED — must stay STALLED.
    assert ctrl.evaluate(0.70) is BackpressureLevel.STALLED
    assert ctrl.evaluate(0.65) is BackpressureLevel.STALLED


def test_invalid_thresholds_rejected() -> None:
    with pytest.raises(ValueError):
        BackpressureController(
            ResilienceConfig(backpressure_high=0.5, backpressure_low=0.5)
        )
    with pytest.raises(ValueError):
        BackpressureController(
            ResilienceConfig(backpressure_high=0.4, backpressure_low=0.6)
        )


def test_invalid_fill_ratio_rejected() -> None:
    ctrl = _ctrl()
    with pytest.raises(ValueError):
        ctrl.evaluate(-0.1)
    with pytest.raises(ValueError):
        ctrl.evaluate(1.01)
