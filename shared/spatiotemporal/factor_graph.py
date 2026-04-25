# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Factor-graph batch optimizer — see ADR-011.

Pure-Python information-form smoother. Each frame is a unary measurement
on its containing alignment bundle (see
:func:`shared.spatiotemporal.align_streams`); the MAP estimate is the
solution of a Gaussian factor graph with the joint information matrix
``Λ = Σ_i H_iᵀ R_i⁻¹ H_i`` and information vector
``η = Σ_i H_iᵀ R_i⁻¹ z_i``.

Two solver backends are available, selected via ``FusionConfig.solver``:

* ``"closed_form"`` — channels are independent (diagonal ``R``), so each
  channel reduces to ``x_k* = Σ z_i/r_i / Σ 1/r_i`` and the system
  factorises by hand. This is the fastest path and matches the v3.1
  hot-path semantics exactly.

* ``"cholesky"`` — assemble the joint ``Λ``/``η`` and solve via dense
  Cholesky (see :mod:`shared.spatiotemporal.cholesky`). Bundle sizes
  are bounded (≤ 10 sensors × ≤ ~6 channels) so a dense factorisation
  comfortably fits the edge-CPU budget and avoids the
  ``scikit-sparse`` dependency.

* ``"auto"`` (default) — closed-form if every frame in the bundle has a
  diagonal covariance, otherwise Cholesky. ADR-011 keeps cross-channel
  coupling reserved for multi-band optical sensors with correlated
  noise; existing scalar sensors stay on the fast path.
"""

from __future__ import annotations

from collections.abc import Iterable

from .alignment import align_streams
from .cholesky import cholesky, invert_spd, solve_cholesky
from .models import FusedState, FusionConfig, SensorFrame

_DEFAULT_MEASUREMENT_NOISE = 1e-2


class FactorGraph:
    """Factor-graph batch optimizer for windowed offline refinement.

    Phase 4 implementation. ``add_frames()`` accumulates sensor frames;
    ``optimize()`` aligns them into bundles and emits one fused state
    per bundle. The dense Cholesky backend generalises the diagonal
    closed-form to multi-band sensors with correlated measurement
    noise (e.g. PROSAIL/SAIL bands fed in raw).
    """

    def __init__(self, config: FusionConfig) -> None:
        if config.solver not in {"auto", "closed_form", "cholesky"}:
            raise ValueError(
                f"FusionConfig.solver must be one of 'auto', 'closed_form', 'cholesky' — got {config.solver!r}"
            )
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
        solver = self.config.solver
        if solver == "auto":
            solver = "cholesky" if self._has_cross_terms(bundle) else "closed_form"

        if solver == "closed_form":
            if self._has_cross_terms(bundle):
                raise ValueError(
                    "closed-form solver cannot handle frames with cross_covariance; "
                    "switch FusionConfig.solver to 'auto' or 'cholesky'."
                )
            return self._solve_closed_form(bundle)
        return self._solve_cholesky(bundle)

    @staticmethod
    def _has_cross_terms(bundle: list[SensorFrame]) -> bool:
        return any(frame.cross_covariance for frame in bundle)

    def _solve_closed_form(self, bundle: list[SensorFrame]) -> FusedState:
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
                "solver": "closed_form",
            },
        )

    def _solve_cholesky(self, bundle: list[SensorFrame]) -> FusedState:
        # Stable channel ordering (sorted) lets the diagonal-only case
        # produce bit-identical results to the closed-form solver.
        channels: list[str] = sorted({k for frame in bundle for k in frame.values})
        index = {k: i for i, k in enumerate(channels)}
        n = len(channels)

        # Joint information matrix Λ and information vector η.
        info_matrix: list[list[float]] = [[0.0] * n for _ in range(n)]
        info_vector: list[float] = [0.0] * n

        for frame in bundle:
            present = [k for k in frame.values if k in index]
            if not present:
                continue
            r_block = self._frame_noise_block(frame, present)
            r_inv = invert_spd(r_block)
            # H is the identity restricted to channels present in the
            # frame; the contribution to Λ is R⁻¹ projected back into
            # the global indexing.
            for local_a, key_a in enumerate(present):
                global_a = index[key_a]
                for local_b, key_b in enumerate(present):
                    global_b = index[key_b]
                    info_matrix[global_a][global_b] += r_inv[local_a][local_b]
                # η contribution: R⁻¹ z restricted to present channels.
                rhs_a = sum(r_inv[local_a][local_b] * frame.values[present[local_b]] for local_b in range(len(present)))
                info_vector[global_a] += rhs_a

        lower = cholesky(info_matrix)
        mean = solve_cholesky(lower, info_vector)
        cov_full = invert_spd(info_matrix)

        state = {channels[i]: mean[i] for i in range(n)}
        cov: dict[tuple[str, str], float] = {}
        for i, key_i in enumerate(channels):
            cov[(key_i, key_i)] = cov_full[i][i]
            for j in range(i + 1, n):
                # Only emit non-trivial off-diagonal entries — keeps the
                # output API symmetric with the closed-form solver.
                if abs(cov_full[i][j]) > 1e-15:
                    cov[(key_i, channels[j])] = cov_full[i][j]
        ts = max(frame.timestamp for frame in bundle)
        return FusedState(
            timestamp=ts,
            state=state,
            covariance=cov,
            diagnostics={
                "bundle_size": len(bundle),
                "channels": list(channels),
                "mode": self.config.mode,
                "solver": "cholesky",
            },
        )

    @staticmethod
    def _frame_noise_block(
        frame: SensorFrame,
        present: list[str],
    ) -> list[list[float]]:
        """Build the per-frame measurement-noise covariance restricted to
        the channels the frame actually reports.

        Returns a (k × k) symmetric matrix where k is the number of
        channels present in the frame; the dense Cholesky inversion
        scales as O(k³) which is negligible at k ≤ ~6.
        """

        k = len(present)
        block: list[list[float]] = [[0.0] * k for _ in range(k)]
        position = {key: i for i, key in enumerate(present)}
        for i, key_i in enumerate(present):
            block[i][i] = max(
                frame.covariance.get(key_i, _DEFAULT_MEASUREMENT_NOISE),
                1e-12,
            )
        for (a, b), value in frame.cross_covariance.items():
            if a in position and b in position:
                ia, ib = position[a], position[b]
                block[ia][ib] = value
                block[ib][ia] = value
        return block
