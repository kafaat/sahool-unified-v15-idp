# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the natural cubic-spline resampler (ADR-011)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.spatiotemporal import resample_cubic


def _t(ms: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms)


def test_passes_through_anchor_points() -> None:
    ts = [_t(0), _t(1000), _t(2000), _t(3000)]
    ys = [0.0, 1.0, 4.0, 9.0]
    out = resample_cubic(ts, ys, ts)
    for got, want in zip(out, ys, strict=True):
        assert got == pytest.approx(want, abs=1e-9)


def test_clamps_outside_input_range() -> None:
    ts = [_t(0), _t(1000), _t(2000)]
    ys = [10.0, 20.0, 30.0]
    out = resample_cubic(ts, ys, [_t(-500), _t(2500)])
    assert out == [10.0, 30.0]


def test_two_point_input_is_linear() -> None:
    ts = [_t(0), _t(1000)]
    ys = [0.0, 100.0]
    out = resample_cubic(ts, ys, [_t(250), _t(500), _t(750)])
    assert out == pytest.approx([25.0, 50.0, 75.0])


def test_monotonic_input_yields_monotonic_resample() -> None:
    ts = [_t(i * 1000) for i in range(5)]
    ys = [0.0, 1.0, 2.0, 3.0, 4.0]
    targets = [_t(i * 250) for i in range(17)]  # 0..4000 ms
    out = resample_cubic(ts, ys, targets)
    for prev, nxt in zip(out, out[1:], strict=False):
        assert nxt + 1e-9 >= prev


def test_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        resample_cubic([_t(0), _t(1000)], [0.0], [_t(500)])


def test_rejects_too_few_anchors() -> None:
    with pytest.raises(ValueError):
        resample_cubic([_t(0)], [0.0], [_t(0)])


def test_rejects_unsorted_anchors() -> None:
    with pytest.raises(ValueError):
        resample_cubic([_t(1000), _t(0), _t(2000)], [0.0, 1.0, 2.0], [_t(500)])
