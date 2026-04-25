# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the time-window aligner (ADR-011)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.spatiotemporal import SensorFrame, align_streams


def _frame(sensor_id: str, ms: int, value: float = 0.0) -> SensorFrame:
    return SensorFrame(
        sensor_id=sensor_id,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms),
        position=(24.7, 46.7, None),
        values={"ndvi": value},
    )


def test_empty_input_returns_empty_list() -> None:
    assert align_streams([]) == []


def test_frames_within_window_are_bundled() -> None:
    bundles = align_streams(
        [_frame("a", 0), _frame("b", 200), _frame("c", 480)],
        window_ms=500,
    )
    assert len(bundles) == 1
    assert {f.sensor_id for f in bundles[0]} == {"a", "b", "c"}


def test_frame_outside_window_starts_new_bundle() -> None:
    bundles = align_streams(
        [_frame("a", 0), _frame("b", 600), _frame("c", 1000)],
        window_ms=500,
    )
    assert [len(b) for b in bundles] == [1, 2]


def test_unsorted_input_is_sorted_first() -> None:
    bundles = align_streams(
        [_frame("late", 400), _frame("early", 100), _frame("mid", 300)],
        window_ms=500,
    )
    assert len(bundles) == 1
    timestamps = [f.timestamp for f in bundles[0]]
    assert timestamps == sorted(timestamps)


def test_zero_window_each_frame_is_its_own_bundle_when_distinct() -> None:
    bundles = align_streams([_frame("a", 0), _frame("b", 1)], window_ms=0)
    assert len(bundles) == 2


def test_negative_window_rejected() -> None:
    with pytest.raises(ValueError):
        align_streams([_frame("a", 0)], window_ms=-1)
