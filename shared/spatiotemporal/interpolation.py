# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Cubic-spline resampling. Skeleton — see ADR-011."""

from __future__ import annotations

from datetime import datetime


def resample_cubic(
    timestamps: list[datetime],
    values: list[float],
    target_timestamps: list[datetime],
) -> list[float]:
    """Resample irregular series onto ``target_timestamps`` via cubic spline.

    Phase 4 implementation. Boundary policy: clamp at endpoints.
    """

    raise NotImplementedError("ADR-011: implemented in Phase 4")
