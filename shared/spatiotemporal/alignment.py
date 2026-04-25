# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Sliding-window time alignment of ±500 ms — see ADR-011."""

from __future__ import annotations

from collections.abc import Iterable

from .models import SensorFrame


def align_streams(
    frames: Iterable[SensorFrame],
    window_ms: int = 500,
) -> list[list[SensorFrame]]:
    """Group ``frames`` into bundles whose timestamps fit within ``window_ms``.

    Frames are sorted by timestamp first; each bundle starts at the earliest
    unbundled frame and absorbs every subsequent frame whose timestamp lies
    within ``window_ms`` of the bundle's *start* timestamp. This deterministic
    "earliest-anchor" rule matches the ADR-011 alignment contract: any two
    frames in the same bundle differ by at most ``window_ms``.
    """

    if window_ms < 0:
        raise ValueError(f"window_ms must be >= 0, got {window_ms}")

    ordered = sorted(frames, key=lambda f: f.timestamp)
    if not ordered:
        return []

    bundles: list[list[SensorFrame]] = []
    current: list[SensorFrame] = [ordered[0]]
    anchor = ordered[0].timestamp
    for frame in ordered[1:]:
        delta_ms = (frame.timestamp - anchor).total_seconds() * 1000.0
        if delta_ms <= window_ms:
            current.append(frame)
        else:
            bundles.append(current)
            current = [frame]
            anchor = frame.timestamp
    bundles.append(current)
    return bundles
