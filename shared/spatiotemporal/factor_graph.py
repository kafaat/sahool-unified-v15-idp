# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Factor-graph batch optimizer — see ADR-011.

Pure-Python information-form solver. Each frame is a unary measurement on
its containing alignment bundle (see :func:`shared.spatiotemporal.align_streams`),
and the smoother is the analytic MAP solution of a Gaussian factor graph
with diagonal information matrices. The full sparse-Cholesky backend is
reserved for the future "windowed offline refinement at scale" use case;
for the current SAHOOL cadence (≤ 500 ms windows, ≤ 10 sensors per bundle)
this closed-form solution is bit-equivalent and avoids the
``scikit-sparse`` dependency on edge devices.
"""

from __future__ import annotations

from collections.abc import Iterable

from .alignment import align_streams
from .models import FusedState, FusionConfig, SensorFrame

_DEFAULT_MEASUREMENT_NOISE = 1e-2


class FactorGraph:
    """Factor-graph batch optimizer for windowed offline refinement.

    Phase 4 implementation. ``add_frames()`` accumulates sensor frames;
    ``optimize()`` aligns them into bundles and emits one fused state per
    bundle.
    """

    def __init__(self, config: FusionConfig) -> None:
        self.config = config
        self._frames: list[SensorFrame] = []

    def add_frames(self, frames: Iterable[SensorFrame]) -> None:
        for frame in frames:
            self._frames.append(frame)

    def optimize(self) -> list[FusedState]:
        if not self._frames:
            return []

        bundles = align_streams(self._frames, window_ms=self.config.alignment_window_ms)
        results: list[FusedState] = []
        for bundle in bundles:
            results.append(self._solve_bundle(bundle))
        return results

    # -- internals -------------------------------------------------------

    def _solve_bundle(self, bundle: list[SensorFrame]) -> FusedState:
        # MAP solution of Σ_i (z_i - x)^2 / r_i is x* = Σ z_i/r_i / Σ 1/r_i,
        # with posterior variance 1 / Σ 1/r_i. Channels are independent.
        info: dict[str, float] = {}  # Σ 1/r_i
        weighted: dict[str, float] = {}  # Σ z_i/r_i
        for frame in bundle:
            for key, z in frame.values.items():
                r = max(
                    frame.covariance.get(key, _DEFAULT_MEASUREMENT_NOISE),
                    1e-12,
                )
                info[key] = info.get(key, 0.0) + 1.0 / r
                weighted[key] = weighted.get(key, 0.0) + z / r

        state = {k: weighted[k] / info[k] for k in info}
        cov = {(k, k): 1.0 / info[k] for k in info}
        ts = max(frame.timestamp for frame in bundle)
        return FusedState(
            timestamp=ts,
            state=state,
            covariance=cov,
            diagnostics={
                "bundle_size": len(bundle),
                "channels": sorted(state),
                "mode": self.config.mode,
            },
        )
