# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the dense Cholesky helpers (ADR-011)."""

from __future__ import annotations

import pytest

from shared.spatiotemporal.cholesky import cholesky, invert_spd, solve_cholesky


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    n, m = len(a), len(b[0])
    inner = len(b)
    result = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            result[i][j] = sum(a[i][k] * b[k][j] for k in range(inner))
    return result


def test_cholesky_factorises_2x2_spd_matrix() -> None:
    matrix = [[4.0, 2.0], [2.0, 3.0]]
    lower = cholesky(matrix)
    # L L.T must equal the input.
    transpose = [[lower[j][i] for j in range(2)] for i in range(2)]
    product = _matmul(lower, transpose)
    for i in range(2):
        for j in range(2):
            assert product[i][j] == pytest.approx(matrix[i][j], abs=1e-12)


def test_cholesky_rejects_non_positive_definite() -> None:
    # Symmetric but indefinite (eigenvalues 1, -1).
    matrix = [[0.0, 1.0], [1.0, 0.0]]
    with pytest.raises(ValueError, match="positive-definite"):
        cholesky(matrix)


def test_cholesky_rejects_non_square_input() -> None:
    with pytest.raises(ValueError, match="square"):
        cholesky([[1.0, 0.0]])


def test_solve_cholesky_recovers_known_solution() -> None:
    # Given a = [[4, 2], [2, 3]] and x_true = [1, 2], rhs = a @ x_true.
    matrix = [[4.0, 2.0], [2.0, 3.0]]
    expected = [1.0, 2.0]
    rhs = [
        sum(matrix[i][j] * expected[j] for j in range(2)) for i in range(2)
    ]
    lower = cholesky(matrix)
    solution = solve_cholesky(lower, rhs)
    assert solution[0] == pytest.approx(expected[0], abs=1e-12)
    assert solution[1] == pytest.approx(expected[1], abs=1e-12)


def test_invert_spd_round_trips_identity() -> None:
    matrix = [[4.0, 2.0, 1.0], [2.0, 3.0, 0.5], [1.0, 0.5, 2.0]]
    inverse = invert_spd(matrix)
    product = _matmul(matrix, inverse)
    for i in range(3):
        for j in range(3):
            target = 1.0 if i == j else 0.0
            assert product[i][j] == pytest.approx(target, abs=1e-10)


def test_solve_cholesky_rejects_mismatched_rhs() -> None:
    lower = cholesky([[4.0, 2.0], [2.0, 3.0]])
    with pytest.raises(ValueError, match="rhs length"):
        solve_cholesky(lower, [1.0])
