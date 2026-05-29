# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.digital_twin.feedback_loop (closed feedback loop spine)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from shared.digital_twin.feedback_loop import (
    OutcomeRecord,
    evaluate_outcome,
    should_trigger_recalibration,
)


pytestmark = pytest.mark.unit


def test_evaluate_outcome_computes_mape() -> None:
    rec_id = uuid4()
    o = evaluate_outcome(
        recommendation_id=rec_id,
        observed_value=8.0,
        expected_value=10.0,
    )
    assert o.recommendation_id == rec_id
    assert o.mape == pytest.approx(0.2)


def test_evaluate_outcome_handles_expected_zero() -> None:
    """expected=0 must not raise; we report mape=0.0 as a degenerate case."""
    o = evaluate_outcome(recommendation_id=uuid4(), observed_value=5.0, expected_value=0.0)
    assert o.mape == 0.0


def test_outcome_record_rejects_negative_mape() -> None:
    """Pydantic enforces mape >= 0 — degenerate inputs cannot fabricate negatives."""
    with pytest.raises(Exception):
        OutcomeRecord(
            recommendation_id=uuid4(),
            observed_value=10.0,
            expected_value=10.0,
            mape=-0.1,
        )


def test_should_trigger_recalibration_below_threshold_false() -> None:
    outcomes = [
        evaluate_outcome(recommendation_id=uuid4(), observed_value=10.1, expected_value=10.0),
        evaluate_outcome(recommendation_id=uuid4(), observed_value=9.9, expected_value=10.0),
        evaluate_outcome(recommendation_id=uuid4(), observed_value=10.0, expected_value=10.0),
    ]
    assert should_trigger_recalibration(outcomes, threshold_mape=0.20) is False


def test_should_trigger_recalibration_above_threshold_true() -> None:
    outcomes = [
        evaluate_outcome(recommendation_id=uuid4(), observed_value=5.0, expected_value=10.0),
        evaluate_outcome(recommendation_id=uuid4(), observed_value=4.0, expected_value=10.0),
        evaluate_outcome(recommendation_id=uuid4(), observed_value=6.0, expected_value=10.0),
    ]
    assert should_trigger_recalibration(outcomes, threshold_mape=0.20) is True


def test_empty_outcomes_returns_false() -> None:
    """A single bad outcome cannot trigger; we need at least min_samples."""
    assert should_trigger_recalibration([], threshold_mape=0.20) is False


def test_below_min_samples_returns_false() -> None:
    outcomes = [
        evaluate_outcome(recommendation_id=uuid4(), observed_value=5.0, expected_value=10.0),
    ]
    assert should_trigger_recalibration(outcomes, threshold_mape=0.20) is False
