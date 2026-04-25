# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Sliding-window time alignment of ±500 ms. Skeleton — see ADR-011."""

from __future__ import annotations

from collections.abc import Iterable

from .models import SensorFrame


def align_streams(
    frames: Iterable[SensorFrame],
    window_ms: int = 500,
) -> list[list[SensorFrame]]:
    """Group ``frames`` into bundles whose timestamps fit within ``window_ms``.

    Phase 4 implementation.
    """

    raise NotImplementedError("ADR-011: implemented in Phase 4")
