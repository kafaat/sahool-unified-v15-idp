# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.digital_twin.decision_chain."""

from __future__ import annotations

import pytest

from shared.digital_twin.decision_chain import ChainStep, start_chain


pytestmark = pytest.mark.unit


def test_chain_step_captures_all_fields() -> None:
    step = ChainStep(
        name="fao56_et0",
        kind="engine",
        inputs_summary="weather=Apr 15",
        outputs_summary="et0=5.2mm",
        confidence_before=1,
        confidence_after=2,
        gate_passed=True,
        cost_estimate_ms=2.3,
    )
    assert step.name == "fao56_et0"
    assert step.confidence_before == 1
    assert step.confidence_after == 2
    assert step.gate_passed is True
    assert step.cost_estimate_ms == 2.3


def test_start_chain_collects_steps_and_stamps_finished_at() -> None:
    with start_chain(workspace_key="t1/f1/winter_2026") as chain:
        chain.add(ChainStep(name="fao56_et0", kind="engine", cost_estimate_ms=2.0))
        chain.add(ChainStep(name="field_lifecycle", kind="guard", cost_estimate_ms=0.5))

    assert len(chain.steps) == 2
    assert chain.workspace_key == "t1/f1/winter_2026"
    assert chain.finished_at is not None
    assert chain.total_cost_ms() == pytest.approx(2.5)


def test_empty_chain_records_bookkeeping_step() -> None:
    """Even an empty chain must report a non-zero total cost for FinOps."""
    with start_chain() as chain:
        pass
    assert len(chain.steps) == 1
    assert chain.steps[0].kind == "bookkeeping"
    assert chain.total_cost_ms() > 0


def test_failed_gate_is_captured_not_dropped() -> None:
    """A failed gate is part of the trace — it tells the consumer why."""
    with start_chain() as chain:
        chain.add(ChainStep(name="pesticide_gate", kind="gate", gate_passed=False))

    assert chain.steps[0].gate_passed is False
    summary = chain.summary()
    assert summary["gates_failed"] == ["pesticide_gate"]


def test_summary_contains_workspace_and_counts() -> None:
    with start_chain(workspace_key="t1/f1/winter_2026") as chain:
        chain.add(ChainStep(name="x", kind="engine"))

    summary = chain.summary()
    assert summary["workspace_key"] == "t1/f1/winter_2026"
    assert summary["step_count"] == 1
