# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Value objects for the Prescription Safety Gateway. Skeleton — see ADR-013."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class DecisionEnum(StrEnum):
    """Final aggregated decision."""

    APPROVED = "APPROVED"
    REVIEW = "REVIEW"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Reason:
    """One reason contributing to the final decision.

    Bilingual (Arabic / English) per platform conventions.
    """

    code: str
    message_en: str
    message_ar: str
    severity: str  # "critical" | "warning" | "info"
    source_checker: str  # e.g. "pesticide_compliance", "agro-rules"


@dataclass(frozen=True)
class Evidence:
    """Per-checker raw payload, retained for audit."""

    checker: str
    payload: dict[str, Any]
    checked_at: datetime


@dataclass(frozen=True)
class PrescriptionRequest:
    """Caller's prescription to be evaluated.

    Carries enough context for every checker to run independently. No nested
    network lookups inside ``models.py`` — all enrichment is the gateway's job.
    """

    tenant_id: str
    prescription_id: str
    prescription_type: str  # "pesticide" | "fertilizer" | "irrigation"
    field_id: str
    crop: str
    product: str  # e.g. "Urea 46%" or pesticide active ingredient
    rate: float
    rate_unit: str  # e.g. "kg/ha", "L/ha", "mm"
    target: dict[str, Any] = field(default_factory=dict)  # pest, disease, weed, etc.
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    """Aggregated decision returned to the caller."""

    decision: DecisionEnum
    reasons: list[Reason]
    evidence: list[Evidence]
    decided_at: datetime
    correlation_id: str
