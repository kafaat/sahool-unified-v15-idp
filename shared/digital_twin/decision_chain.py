# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Decision Chain - سلسلة القرار
==============================
Runtime trace of every step that contributed to a recommendation.

Each ChainStep records what entered, what came out, the confidence shift,
whether a gate passed, and an approximate compute cost (ms).

The DecisionChain attaches to an IrrigationRecommendation (or any future
recommendation type) so consumers can answer:

    Why this recommendation? — describe_recommendation(rec)
    How much did it cost?    — sum(step.cost_estimate_ms for step in chain.steps)
    Where in which workspace? — chain.workspace_key

Pure dataclass. Zero I/O. No DB.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ChainStep:
    """One step in a decision chain. خطوة واحدة في سلسلة القرار."""

    name: str  # e.g. "fao56_et0", "field_lifecycle_gate"
    kind: str  # e.g. "engine", "guard", "adapter", "view"
    inputs_summary: str = ""  # Short textual summary for explainability
    outputs_summary: str = ""
    confidence_before: int | None = None  # 0..3 (Confidence)
    confidence_after: int | None = None  # 0..3
    gate_passed: bool = True  # False ≠ failure — captured for trace
    cost_estimate_ms: float = 0.0  # Approximate compute cost in milliseconds


@dataclass
class DecisionChain:
    """A complete trace of steps that produced one recommendation."""

    workspace_key: str | None = None
    steps: list[ChainStep] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None

    def add(self, step: ChainStep) -> None:
        self.steps.append(step)

    def total_cost_ms(self) -> float:
        return sum(s.cost_estimate_ms for s in self.steps)

    def summary(self) -> dict[str, object]:
        return {
            "workspace_key": self.workspace_key,
            "step_count": len(self.steps),
            "total_cost_ms": self.total_cost_ms(),
            "gates_failed": [s.name for s in self.steps if not s.gate_passed],
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


@contextmanager
def start_chain(workspace_key: str | None = None) -> Iterator[DecisionChain]:
    """
    Context manager that builds a DecisionChain and stamps `finished_at` on exit.

    Usage::

        with start_chain(workspace_key="t1/f1/winter_2026") as chain:
            chain.add(ChainStep(name="fao56_et0", kind="engine", cost_estimate_ms=2.1))
            ...
        # chain.finished_at is set; chain is ready to attach to a recommendation.
    """
    chain = DecisionChain(workspace_key=workspace_key)
    t0 = time.perf_counter()
    try:
        yield chain
    finally:
        chain.finished_at = datetime.now(UTC)
        # If no step recorded its own cost, attribute the wall-clock delta to a
        # bookkeeping step so total_cost_ms() is non-zero (useful for FinOps).
        if not chain.steps:
            chain.add(
                ChainStep(
                    name="empty_chain",
                    kind="bookkeeping",
                    cost_estimate_ms=(time.perf_counter() - t0) * 1000.0,
                )
            )


__all__ = [
    "ChainStep",
    "DecisionChain",
    "start_chain",
]
