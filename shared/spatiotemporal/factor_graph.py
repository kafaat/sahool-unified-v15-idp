# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Factor-graph batch optimizer (sparse Cholesky). Skeleton — see ADR-011."""

from __future__ import annotations

from collections.abc import Iterable

from .models import FusedState, FusionConfig, SensorFrame


class FactorGraph:
    """Factor-graph batch optimizer for windowed offline refinement.

    Sparse-Cholesky backend choice (``scikit-sparse`` vs ``sksparse``)
    is deferred to Phase 4.
    """

    def __init__(self, config: FusionConfig) -> None:
        self.config = config

    def add_frames(self, frames: Iterable[SensorFrame]) -> None:
        raise NotImplementedError("ADR-011: implemented in Phase 4")

    def optimize(self) -> list[FusedState]:
        raise NotImplementedError("ADR-011: implemented in Phase 4")
