# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the small KD-tree helper used by PROSAIL inversion (ADR-015)."""

from __future__ import annotations

import math
import random

import pytest

from shared.process_models.kd_tree import KDTree


def _brute_force_knn(points: list[tuple[float, ...]], target: tuple[float, ...], k: int) -> list[tuple[float, int]]:
    distances = [
        (math.sqrt(sum((a - b) ** 2 for a, b in zip(p, target, strict=True))), i) for i, p in enumerate(points)
    ]
    distances.sort(key=lambda entry: entry[0])
    return distances[:k]


def test_kd_tree_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        KDTree([])


def test_kd_tree_rejects_mismatched_dimensions() -> None:
    with pytest.raises(ValueError, match="dimensionality"):
        KDTree([[1.0, 2.0], [1.0, 2.0, 3.0]])


def test_kd_tree_size_and_dimensions_metadata() -> None:
    tree = KDTree([[0.0, 0.0], [1.0, 1.0], [2.0, 0.5]])
    assert tree.size == 3
    assert tree.dimensions == 2


def test_kd_tree_query_rejects_invalid_k() -> None:
    tree = KDTree([[0.0, 0.0]])
    with pytest.raises(ValueError, match=">= 1"):
        tree.query([0.0, 0.0], k=0)


def test_kd_tree_query_rejects_dim_mismatch() -> None:
    tree = KDTree([[0.0, 0.0]])
    with pytest.raises(ValueError, match="dimensionality"):
        tree.query([0.0], k=1)


def test_kd_tree_returns_exact_match_first() -> None:
    points = [(0.0, 0.0), (3.0, 4.0), (1.0, 1.0)]
    tree = KDTree(points)
    result = tree.query((3.0, 4.0), k=1)
    assert result == [(0.0, 1)]


def test_kd_tree_matches_brute_force_on_random_inputs() -> None:
    """The KD-tree must return the same k-NN set (modulo ordering of
    ties) as the brute-force baseline. This is the regression contract
    that lets PROSAIL ``invert()`` switch backends without changing the
    retrieval result.
    """

    rng = random.Random(20260425)
    points = [tuple(rng.random() for _ in range(4)) for _ in range(200)]
    tree = KDTree(points)
    for _ in range(25):
        target = tuple(rng.random() for _ in range(4))
        k = rng.randint(1, 8)
        kd_result = tree.query(target, k=k)
        bf_result = _brute_force_knn(points, target, k)
        kd_distances = [d for d, _ in kd_result]
        bf_distances = [d for d, _ in bf_result]
        for a, b in zip(kd_distances, bf_distances, strict=True):
            assert a == pytest.approx(b, abs=1e-12)
        assert sorted(idx for _, idx in kd_result) == sorted(idx for _, idx in bf_result)
