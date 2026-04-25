# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Backpressure controller (80/60 % hysteresis). Skeleton — see ADR-014."""

from __future__ import annotations

from .models import BackpressureLevel, ResilienceConfig


class BackpressureController:
    """Hysteresis controller stalling ingestion when the WAL fills up.

    Stall when ``fill > backpressure_high``; resume when
    ``fill < backpressure_low``. Hysteresis avoids thrash near the threshold.
    """

    def __init__(self, config: ResilienceConfig) -> None:
        self.config = config
        self._level: BackpressureLevel = BackpressureLevel.NORMAL

    def evaluate(self, fill_ratio: float) -> BackpressureLevel:
        """Return the new level after observing ``fill_ratio``.

        Phase 4 implementation.
        """

        raise NotImplementedError("ADR-014: implemented in Phase 4")
