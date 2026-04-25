# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Pure-Python dense Cholesky solver for the factor-graph backend (ADR-011).

The factor graph assembles a symmetric positive-definite information
matrix ``Λ = Σ_i H_iᵀ R_i⁻¹ H_i`` and an information vector
``η = Σ_i H_iᵀ R_i⁻¹ z_i``; the MAP estimate is ``x* = Λ⁻¹ η`` and the
posterior covariance is ``Λ⁻¹``.

Bundle sizes in SAHOOL are bounded (≤ 10 sensors × ≤ ~6 channels), so a
dense Cholesky factorisation is the right choice — it sidesteps the
``scikit-sparse`` dependency on edge devices, runs in well under 1 ms
for the target bundle, and is bit-equivalent to the closed-form solver
when ``Λ`` is diagonal.

This module is intentionally tiny and self-contained: the larger
process-models package already pulls Pydantic / structlog / asyncpg, but
the factor graph itself must keep its imports light because it ships in
the edge-orchestrator-service container.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

Matrix = list[list[float]]


def cholesky(matrix: Matrix) -> Matrix:
    """Return the lower-triangular Cholesky factor ``L`` of a symmetric
    positive-definite ``matrix`` such that ``matrix = L @ L.T``.

    Raises ``ValueError`` if the matrix is not positive-definite — that
    is a programming error in the factor-graph assembly (every
    information matrix built from a valid noise covariance must be PD).
    """

    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square")

    # Pre-allocate; algorithm fills strictly lower-triangular entries.
    lower: Matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                radicand = matrix[i][i] - s
                if radicand <= 0.0:
                    raise ValueError(f"matrix is not positive-definite (diagonal radicand {radicand!r} at row {i})")
                lower[i][j] = math.sqrt(radicand)
            else:
                lower[i][j] = (matrix[i][j] - s) / lower[j][j]
    return lower


def solve_cholesky(lower: Matrix, rhs: Sequence[float]) -> list[float]:
    """Solve ``L L.T x = rhs`` using forward + back substitution."""

    n = len(lower)
    if len(rhs) != n:
        raise ValueError("rhs length must match L")

    # Forward substitution: L y = rhs.
    y = [0.0] * n
    for i in range(n):
        s = sum(lower[i][k] * y[k] for k in range(i))
        y[i] = (rhs[i] - s) / lower[i][i]

    # Back substitution: L.T x = y.
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(lower[k][i] * x[k] for k in range(i + 1, n))
        x[i] = (y[i] - s) / lower[i][i]
    return x


def invert_spd(matrix: Matrix) -> Matrix:
    """Invert a symmetric positive-definite ``matrix`` via Cholesky.

    Used to recover the posterior covariance ``Λ⁻¹`` after MAP solve.
    """

    n = len(matrix)
    lower = cholesky(matrix)
    inverse: Matrix = [[0.0] * n for _ in range(n)]
    for column in range(n):
        e = [0.0] * n
        e[column] = 1.0
        col = solve_cholesky(lower, e)
        for row in range(n):
            inverse[row][column] = col[row]
    # Symmetrise to clean up floating-point asymmetry from forward/back-sub.
    for i in range(n):
        for j in range(i + 1, n):
            avg = 0.5 * (inverse[i][j] + inverse[j][i])
            inverse[i][j] = inverse[j][i] = avg
    return inverse
