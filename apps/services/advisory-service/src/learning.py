"""
Learning engine: track outcomes per (crop, region, action) tuple
and surface a success rate that the advisor uses to bias action ranking.

محرك التعلم: تسجيل نتائج القرارات وحساب معدلات النجاح حسب (المحصول، المنطقة، الإجراء).

NOTE: This is an in-memory tracker, lost on restart. For a durable
implementation back this with Redis or a postgres table.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_NEUTRAL_RATE = 0.5
RESULT_IMPROVED = "improved"
RESULT_NO_CHANGE = "no_change"
RESULT_WORSENED = "worsened"

VALID_RESULTS: set[str] = {RESULT_IMPROVED, RESULT_NO_CHANGE, RESULT_WORSENED}


class LearningEngine:
    """Bounded, in-memory rolling window of outcomes per (crop, region, action)."""

    def __init__(self, memory_size: int = 10_000) -> None:
        self.memory_size = memory_size
        # Use a bounded deque per key: ``maxlen`` evicts the oldest entry on
        # overflow in O(1), avoiding the O(n) ``del bucket[: ...]`` slice that
        # the previous list-based implementation paid on every record after
        # the bucket was full.
        self.outcomes: dict[tuple[str, str, str], deque[str]] = defaultdict(
            lambda: deque(maxlen=memory_size)
        )

    def record_outcome(self, feedback: dict[str, Any]) -> None:
        """Persist a single outcome.

        feedback keys: ``crop``, ``region``, ``action``, ``result`` (one of
        ``improved`` / ``no_change`` / ``worsened``).
        """
        key = (
            feedback.get("crop", "unknown"),
            feedback.get("region", "unknown"),
            feedback.get("action", "unknown"),
        )
        result = feedback.get("result", RESULT_NO_CHANGE)
        if result not in VALID_RESULTS:
            logger.warning("learning.invalid_result", extra={"result": result})
            result = RESULT_NO_CHANGE

        # Bounded by ``maxlen`` set in the deque factory; oldest entry is
        # evicted automatically when the deque is at capacity.
        self.outcomes[key].append(result)

        logger.debug("learning.recorded", extra={"key": key, "result": result})

    def get_success_rate(self, crop: str, region: str, action: str) -> float:
        """Return P(improved | crop, region, action), or 0.5 if no data."""
        outcomes = self.outcomes.get((crop, region, action), [])
        if not outcomes:
            return DEFAULT_NEUTRAL_RATE
        return outcomes.count(RESULT_IMPROVED) / len(outcomes)

    def get_statistics(self) -> dict[str, Any]:
        """High-level statistics of the in-memory store."""
        total = sum(len(v) for v in self.outcomes.values())
        return {
            "unique_keys": len(self.outcomes),
            "total_recorded_outcomes": total,
            "sample_keys": [list(k) for k in list(self.outcomes.keys())[:10]],
        }
