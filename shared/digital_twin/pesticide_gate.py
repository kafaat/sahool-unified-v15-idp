# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Pesticide Safety Gate - بوّابة سلامة المبيدات
================================================
Three-layer evaluation in a FIXED order. Order is not optional —
the safety invariant is that PHI is checked first and short-circuits.

    1. PHI (Pre-Harvest Interval) — HARD GATE
       Days-since-application < phi_days → BLOCKED.
       Ignores all lower layers entirely.

    2. RRI (Residue Risk Index)    — ADVISORY ONLY
       Exponential decay estimate. NEVER permits harvest by itself —
       lab analysis governs final clearance.

    3. Economic                    — WARNING, NOT BLOCKER
       Spray-cost vs. expected-damage. Does not affect safety.

Decision Kernel invariant: pesticide clearance always requires lab confirmation
even after PHI elapses. The gate emits LAB_REQUIRED, not CLEARED, on its own.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class PesticideGateStatus(StrEnum):
    """Outcome categories for the pesticide safety gate."""

    BLOCKED = "blocked"
    LAB_REQUIRED = "lab_required"
    CAUTION = "caution"
    CLEARED = "cleared"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass(frozen=True)
class PesticideGateResult:
    """Structured outcome of running the three-layer evaluation."""

    status: PesticideGateStatus
    reason_ar: str
    reason_en: str
    phi_days_remaining: int | None = None
    rri: float | None = None  # 0..1 (lower = lower residue estimate)
    economic_warning: bool = False
    requires_lab: bool = True  # Default: lab analysis must clear harvest

    @property
    def is_safe(self) -> bool:
        return self.status == PesticideGateStatus.CLEARED


def evaluate(
    *,
    last_application_date: date | None,
    phi_days: int | None,
    today: date,
    half_life_days: float | None = None,
    economic_threshold_exceeded: bool | None = None,
) -> PesticideGateResult:
    """
    Run the three-layer gate in fixed order.

    Args:
        last_application_date: When the pesticide was last applied to the field.
        phi_days: Pre-harvest interval mandated by the product label.
        today: Reference date for the evaluation.
        half_life_days: Optional environmental half-life; enables RRI estimate.
        economic_threshold_exceeded: Optional flag from an economic model.

    Returns:
        PesticideGateResult with status, bilingual reason, and supporting fields.
    """
    # Layer 0: data sufficiency.
    if last_application_date is None or phi_days is None:
        return PesticideGateResult(
            status=PesticideGateStatus.INSUFFICIENT_DATA,
            reason_ar="بيانات الرشّ ناقصة (لا تاريخ تطبيق أو فترة أمان).",
            reason_en="Spray data missing (no application date or PHI).",
        )

    # Layer 1: PHI hard block (short-circuits lower layers).
    days_since = (today - last_application_date).days
    remaining = phi_days - days_since
    if remaining > 0:
        return PesticideGateResult(
            status=PesticideGateStatus.BLOCKED,
            phi_days_remaining=remaining,
            reason_ar=f"لم تنقضِ فترة الأمان: متبقّي {remaining} يوماً.",
            reason_en=f"Pre-harvest interval not elapsed: {remaining} day(s) remaining.",
        )

    # Layer 2: RRI advisory (computed only when half-life is supplied;
    # never permits clearance on its own — lab analysis governs).
    rri: float | None = None
    if half_life_days is not None and half_life_days > 0:
        rri = math.exp(-math.log(2) * days_since / half_life_days)
        rri = max(0.0, min(1.0, rri))

    # Layer 3: economic advisory (warning only — does not affect safety).
    econ_warn = bool(economic_threshold_exceeded)

    # PHI elapsed, but lab analysis still governs the final harvest clearance.
    return PesticideGateResult(
        status=PesticideGateStatus.LAB_REQUIRED,
        phi_days_remaining=0,
        rri=rri,
        economic_warning=econ_warn,
        reason_ar="انقضت فترة الأمان — يلزم تحليل مخبري للتأكيد قبل الحصاد.",
        reason_en="PHI elapsed — lab analysis required to confirm clearance before harvest.",
        requires_lab=True,
    )


__all__ = [
    "PesticideGateStatus",
    "PesticideGateResult",
    "evaluate",
]
