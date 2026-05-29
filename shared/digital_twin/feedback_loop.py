# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Feedback Loop - حلقة التغذية الراجعة
=====================================
Closes the agricultural learning loop:

    analysis → prescription → execution → outcome collection → evaluation → recalibration

This module owns ONLY the evaluation + recalibration-trigger step. The
recalibration itself is performed by ``shared/calibration/`` (already complete);
this module emits a NATS signal (``sahool.feedback.recalibration_requested``)
that ``calibration/worker.py`` consumes.

Responsibility boundary (the discipline):
  • compute outcome metrics (MAPE)
  • emit a recalibration trigger when drift exceeds a threshold
  • DO NOT recompute calibration parameters here
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
    Compute MAPE for a single outcome and produce an OutcomeRecord.

    MAPE is bounded by handling expected_value=0 explicitly (returns 0.0 to
    avoid division by zero; the caller may interpret this as a degenerate case).
    """
    if expected_value == 0:
        mape = 0.0
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
