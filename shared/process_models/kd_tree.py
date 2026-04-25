# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Small pure-Python KD-tree used by the PROSAIL LUT inversion (ADR-015).

Keeping the dependency footprint small matters because PROSAIL inversion
ships in two contexts:

* the ``digital-twin-engine`` service (port 8253), where the LUT is
  resident in memory and the search is the hot-path;
* the edge-orchestrator-service container, which already pulls the
  forward-model code via :mod:`shared.process_models.radiative_transfer`
  but does not have ``scikit-learn`` / ``scipy`` available.

The tree handles k-NN search in ``D``-dimensional reflectance space.
For the typical SAHOOL LUT (≤ 32 768 entries × ≤ 6 bands) build cost is
around 50 ms and per-query cost is sub-millisecond — well below the
50 ms edge-CPU budget that the original brute-force baseline targeted.

Dimensions (band ordering) are fixed at construction so a single tree
can be reused across many inversions of the same scene.
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class _Node:
    point: tuple[float, ...]
    index: int  # back-reference into the original LUT
    axis: int
    left: "_Node | None" = None
    right: "_Node | None" = None


class KDTree:
    """Static KD-tree for k-NN reflectance retrieval.

    Build is ``O(N log N)``; ``query()`` is ``O(log N)`` average and
    ``O(N)`` worst-case (degenerate inputs). For our axis-aligned LUTs
    the average is essentially always realised.
    """

    def __init__(self, points: Sequence[Sequence[float]]) -> None:
        if not points:
            raise ValueError("KDTree requires at least one point")
        self._dimensions = len(points[0])
        if any(len(p) != self._dimensions for p in points):
            raise ValueError("all points must share the same dimensionality")
        indexed = [(tuple(p), i) for i, p in enumerate(points)]
        self._root = self._build(indexed, depth=0)
        self._size = len(points)

    # -- public API ------------------------------------------------------

    @property
    def size(self) -> int:
        return self._size

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def query(
        self, target: Sequence[float], k: int
    ) -> list[tuple[float, int]]:
        """Return the ``k`` nearest neighbours as ``(distance, lut_index)``.

        Distances are Euclidean (matches the brute-force baseline).
        Ties broken by node identity, so results are deterministic.
        """

        if k < 1:
            raise ValueError("k must be >= 1")
        if len(target) != self._dimensions:
            raise ValueError(
                "target dimensionality "
                f"{len(target)} does not match tree dimensionality "
                f"{self._dimensions}"
            )

        target_tuple = tuple(target)
        # Max-heap of (-distance, counter, index). Python's heapq is a
        # min-heap, so we negate the distance to get max-pop semantics.
        heap: list[tuple[float, int, int]] = []
        counter = 0
        self._search(self._root, target_tuple, k, heap, counter)
        # Pop into ascending-distance order.
        ordered = sorted((-neg_d, idx) for neg_d, _, idx in heap)
        return [(math.sqrt(d2), idx) for d2, idx in ordered]

    # -- internals -------------------------------------------------------

    def _build(
        self,
        items: list[tuple[tuple[float, ...], int]],
        depth: int,
    ) -> _Node | None:
        if not items:
            return None
        axis = depth % self._dimensions
        items.sort(key=lambda entry: entry[0][axis])
        median = len(items) // 2
        point, idx = items[median]
        return _Node(
            point=point,
            index=idx,
            axis=axis,
            left=self._build(items[:median], depth + 1),
            right=self._build(items[median + 1 :], depth + 1),
        )

    def _search(
        self,
        node: _Node | None,
        target: tuple[float, ...],
        k: int,
        heap: list[tuple[float, int, int]],
        counter: int,
    ) -> int:
        if node is None:
            return counter
        # Squared Euclidean keeps the comparison branch sqrt-free.
        d2 = sum((a - b) ** 2 for a, b in zip(node.point, target, strict=True))
        if len(heap) < k:
            heapq.heappush(heap, (-d2, counter, node.index))
            counter += 1
        elif -d2 > heap[0][0]:
            heapq.heapreplace(heap, (-d2, counter, node.index))
            counter += 1

        diff = target[node.axis] - node.point[node.axis]
        first, second = (
            (node.left, node.right) if diff < 0 else (node.right, node.left)
        )
        counter = self._search(first, target, k, heap, counter)
        # Only descend the "far" branch if a closer neighbour might still
        # exist there, i.e. the perpendicular distance to the splitting
        # hyperplane is smaller than the current k-th best.
        if len(heap) < k or diff * diff < -heap[0][0]:
            counter = self._search(second, target, k, heap, counter)
        return counter
