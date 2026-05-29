# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Field Quality Lifecycle - دورة جودة الحقل
==========================================
Models the farmer-facing data-completeness state machine:

    BLOCKED       – no recommendation; governing measurements absent
    LIMITED       – farmer skipped lab tests → general advice only
    PENDING_LAB   – lab requested → general advice until results arrive
    READY         – full governors present → precise advice

Used to gate which recommendations a field can receive, and to cap the
confidence ceiling of any output (effective_confidence_cap).

Decision Kernel invariant: zone_factor is None → confidence never reaches HIGH.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FieldQualityState(StrEnum):
    """Lifecycle state for a field's recommendation eligibility."""

    BLOCKED = "blocked"
    LIMITED = "limited"
    PENDING_LAB = "pending_lab"
    READY = "ready"


class SoilTestChoice(StrEnum):
    """Farmer decision about lab soil testing. اختيار المزارع للفحص المخبري."""

    NOT_DECIDED = "not_decided"
    SKIP = "skip"
    REQUEST_LAB = "request_lab"
    COMPLETED = "completed"


# Governing observables that MUST be present (lab-grade) for READY state.
# الـobservables الحاكمة التي يجب توفّرها لحالة READY.
GOVERNING_OBSERVABLES: frozenset[str] = frozenset(
    {
        "soil_ec",  # Soil salinity (electrical conductivity)
        "soil_ph",  # Soil pH
        "water_ec",  # Irrigation water salinity
    }
)


# Confidence ceilings per state (0=blocked, 1=LOW, 2=MEDIUM, 3=HIGH).
# Mirrors shared.digital_twin.evidence_class.Confidence ordering.
_CEILING_BY_STATE: dict[FieldQualityState, int] = {
    FieldQualityState.BLOCKED: 0,
    FieldQualityState.LIMITED: 1,
    FieldQualityState.PENDING_LAB: 2,
    FieldQualityState.READY: 3,
}


@dataclass(frozen=True)
class LifecycleAssessment:
    """Outcome of resolving a field's lifecycle state. نتيجة تقييم دورة الحياة."""

    state: FieldQualityState
    confidence_cap: int  # 0..3
    missing_governors: tuple[str, ...]
    reason_ar: str
    reason_en: str

    def allows_recommendation(self, kind: str) -> bool:
        """Whether a recommendation of `kind` may be produced in this state."""
        if self.state == FieldQualityState.BLOCKED:
            return False
        # Safety-critical: pesticide requires READY (lab data + PHI clearance).
        if kind == "pesticide":
            return self.state == FieldQualityState.READY
        return True


def resolve_state(
    *,
    soil_choice: SoilTestChoice,
    provided_governors: frozenset[str],
    lab_request_pending: bool = False,
) -> LifecycleAssessment:
    """
    Compute lifecycle state from farmer intent + measurement availability.
    احتساب حالة دورة الحياة من نية المزارع وتوفّر القياسات.
    """
    missing = tuple(sorted(GOVERNING_OBSERVABLES - provided_governors))
    has_all = not missing

    if has_all and soil_choice == SoilTestChoice.COMPLETED:
        return LifecycleAssessment(
            state=FieldQualityState.READY,
            confidence_cap=3,
            missing_governors=(),
            reason_ar="كل الفحوصات الحاكمة متوفّرة — توصيات دقيقة.",
            reason_en="All governing tests present — precise advice.",
        )

    if lab_request_pending or soil_choice == SoilTestChoice.REQUEST_LAB:
        return LifecycleAssessment(
            state=FieldQualityState.PENDING_LAB,
            confidence_cap=2,
            missing_governors=missing,
            reason_ar="بانتظار نتائج المختبر — توصيات عامة مؤقّتاً.",
            reason_en="Awaiting lab results — general advice in the meantime.",
        )

    if soil_choice == SoilTestChoice.SKIP:
        return LifecycleAssessment(
            state=FieldQualityState.LIMITED,
            confidence_cap=1,
            missing_governors=missing,
            reason_ar="فحوصات التربة تُخطّيت — توصيات عامة فقط.",
            reason_en="Soil testing skipped — general advice only.",
        )

    return LifecycleAssessment(
        state=FieldQualityState.BLOCKED,
        confidence_cap=0,
        missing_governors=missing,
        reason_ar="لا توصية: قياسات حاكمة مفقودة (تحاليل التربة/الماء).",
        reason_en="No recommendation: governing measurements missing (soil/water analysis).",
    )


def effective_confidence_cap(
    state: FieldQualityState,
    *,
    zone_factor: float | None,
) -> int:
    """
    Final ceiling on a recommendation's confidence category (0..3):
      - lifecycle state's own cap, AND
      - uncalibrated (zone_factor is None) → cannot exceed MEDIUM (cap 2).

    Decision Kernel invariant: zone_factor is None → never HIGH.
    """
    state_cap = _CEILING_BY_STATE[state]
    calibration_cap = 3 if zone_factor is not None else 2
    return min(state_cap, calibration_cap)


__all__ = [
    "FieldQualityState",
    "SoilTestChoice",
    "LifecycleAssessment",
    "GOVERNING_OBSERVABLES",
    "resolve_state",
    "effective_confidence_cap",
]
