# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Backpressure controller (80/60 % hysteresis) — see ADR-014.

Pure, no I/O. Holds the current discrete level and updates it on every
observation. Hysteresis avoids thrashing when the WAL fill ratio oscillates
near a single threshold: enter ``STALLED`` only when ``fill > high``, exit
only when ``fill < low``.
"""

from __future__ import annotations

from .models import BackpressureLevel, ResilienceConfig


class BackpressureController:
    """Hysteresis controller stalling ingestion when the WAL fills up.

    Stall when ``fill > backpressure_high``; resume when
    ``fill < backpressure_low``. Hysteresis avoids thrash near the threshold.
    """

    def __init__(self, config: ResilienceConfig) -> None:
        if not 0.0 <= config.backpressure_low < config.backpressure_high <= 1.0:
            raise ValueError("backpressure_low must be < backpressure_high and both in [0, 1]")
        self.config = config
        self._level: BackpressureLevel = BackpressureLevel.NORMAL

    @property
    def level(self) -> BackpressureLevel:
        return self._level

    def evaluate(self, fill_ratio: float) -> BackpressureLevel:
        """Return the new level after observing ``fill_ratio``.

        Boundary semantics:

        * ``fill_ratio > high`` → ``STALLED``
        * ``fill_ratio < low``  → ``NORMAL``
        * otherwise              → unchanged (stay in current state)
        """

        if fill_ratio < 0.0 or fill_ratio > 1.0:
            raise ValueError(f"fill_ratio must be in [0, 1], got {fill_ratio!r}")

        if self._level is BackpressureLevel.NORMAL:
            if fill_ratio > self.config.backpressure_high:
                self._level = BackpressureLevel.STALLED
        else:  # currently STALLED
            if fill_ratio < self.config.backpressure_low:
                self._level = BackpressureLevel.NORMAL
        return self._level
