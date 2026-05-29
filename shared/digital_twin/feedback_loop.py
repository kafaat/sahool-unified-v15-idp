# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Feedback Loop - حلقة التغذية الراجعة
=====================================
Closes the agricultural learning loop:

    analysis → prescription → execution → outcome collection → evaluation → recalibration

This module owns ONLY the evaluation + recalibration-decision step. It
DOES NOT publish to NATS — it computes a boolean trigger that the caller
(typically the crop-intelligence-service) inspects and, when ``True``,
publishes ``sahool.feedback.recalibration_requested`` (defined in
``shared/events/subjects.py``) for ``shared/calibration/worker.py`` to
consume. Keeping the I/O outside this module preserves its pure-function
character and lets the bus client live with the rest of the service plumbing.

Responsibility boundary (the discipline):
  • compute outcome metrics (MAPE / sMAPE for degenerate expected=0)
  • return a recalibration trigger when drift exceeds a threshold
  • DO NOT publish to NATS, DO NOT recompute calibration parameters here
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OutcomeRecord(BaseModel):
    """
    A recorded outcome paired with the recommendation it followed.
    سجلّ نتيجة مقترنة بالتوصية التي اتُّبعت.

    Used by ``should_trigger_recalibration`` to decide whether the calibration
    has drifted enough to warrant retraining.
    """

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    observed_value: float
    expected_value: float
    mape: float = Field(ge=0.0)
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    note: str | None = None


def evaluate_outcome(
    *,
    recommendation_id: UUID,
    observed_value: float,
    expected_value: float,
    ts: datetime | None = None,
    note: str | None = None,
) -> OutcomeRecord:
    """
    Compute a relative-error metric for a single outcome and produce an OutcomeRecord.

    Behaviour around the degenerate ``expected_value == 0`` case:
      • ``observed == 0`` → mape = 0.0 (truly no error)
      • ``observed != 0`` → mape = 2.0 (maximum sMAPE)

    Returning the maximum sMAPE here is deliberate: silently emitting 0.0 would
    let a stream of "expected zero but observed nonzero" outcomes never trip
    ``should_trigger_recalibration``, which is the opposite of conservative for
    a safety/quality feedback loop.

    For all other cases the value is the classic MAPE
    ``|observed - expected| / |expected|`` so existing thresholds keep their
    operational meaning at the working point.
    """
    if expected_value == 0:
        mape = 0.0 if observed_value == 0 else 2.0
    else:
        mape = abs(observed_value - expected_value) / abs(expected_value)
    return OutcomeRecord(
        recommendation_id=recommendation_id,
        observed_value=observed_value,
        expected_value=expected_value,
        mape=mape,
        ts=ts or datetime.now(UTC),
        note=note,
    )


def should_trigger_recalibration(
    outcomes: list[OutcomeRecord],
    *,
    threshold_mape: float = 0.20,
    min_samples: int = 3,
) -> bool:
    """
    Decide whether accumulated outcomes show enough drift to ask for
    recalibration. Returns True only when the mean MAPE across at least
    ``min_samples`` outcomes exceeds ``threshold_mape``.

    The trigger is conservative on purpose: a single bad outcome does not
    invalidate calibration; persistent drift does.
    """
    if len(outcomes) < min_samples:
        return False
    mean_mape = sum(o.mape for o in outcomes) / len(outcomes)
    return mean_mape > threshold_mape


__all__ = [
    "OutcomeRecord",
    "evaluate_outcome",
    "should_trigger_recalibration",
]
