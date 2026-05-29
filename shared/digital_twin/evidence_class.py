# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Evidence Classification - تصنيف الأدلّة
=========================================
Codifies the SAHOOL Decision Kernel invariant:

    "الاستشعار يوجّه، المختبر يحكم"
    Remote sensing GUIDES; lab measurement GOVERNS.

Operationally:
  • INDICATION – satellite/spectral/proxy. Capped at LOW alone.
                 Multiple INDICATIONS from INDEPENDENT sources may corroborate
                 up to MEDIUM. Never reaches HIGH by itself.
  • EVIDENCE   – lab analysis, calibrated sensor, weighed harvest. Can reach HIGH.

Corroboration handles AGREEMENT and DISAGREEMENT explicitly:
  3 agree                → HIGH (for EVIDENCE) / MEDIUM (for INDICATION)
  2 agree, 1 contradict  → MEDIUM
  1 agree, 2 contradict  → LOW (contradiction dominates)

Composes with — never duplicates — shared.process_models.uncertainty.QualityFlag.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum

from shared.process_models.uncertainty import QualityFlag


class EvidenceClass(StrEnum):
    """Whether a signal guides or governs decisions."""

    INDICATION = "indication"
    EVIDENCE = "evidence"


class Confidence(IntEnum):
    """
    Ordered confidence categories. IntEnum makes min()/max() and comparison natural.
    NONE < LOW < MEDIUM < HIGH.
    """

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


_INDICATION_QUALITY: frozenset[QualityFlag] = frozenset(
    {
        QualityFlag.INTERPOLATED,
        QualityFlag.SIMULATED,
        QualityFlag.UNCALIBRATED,
    }
)

_EVIDENCE_QUALITY: frozenset[QualityFlag] = frozenset(
    {
        QualityFlag.CALIBRATED,
    }
)


def classify_quality(quality: QualityFlag, *, is_lab: bool = False) -> EvidenceClass:
    """
    Map a process-models QualityFlag to an evidence class.

    QualityFlag.OBSERVED is INDICATION by default (e.g. satellite NDVI is
    observed but proxy). Pass ``is_lab=True`` to mark a lab observation as
    EVIDENCE.
    """
    if quality in _INDICATION_QUALITY:
        return EvidenceClass.INDICATION
    if quality in _EVIDENCE_QUALITY:
        return EvidenceClass.EVIDENCE
    if quality == QualityFlag.OBSERVED:
        return EvidenceClass.EVIDENCE if is_lab else EvidenceClass.INDICATION
    return EvidenceClass.INDICATION


@dataclass(frozen=True)
class IndicationSignal:
    """A single indication contributing to a corroboration decision."""

    name: str
    agrees: bool  # Supports the hypothesis under test
    source: str  # Independence key (e.g. "sentinel2", "sar", "soil_sensor")
    confidence: Confidence = Confidence.LOW


def enforce_indication_ceiling(
    proposed: Confidence,
    klass: EvidenceClass,
) -> Confidence:
    """
    Cap confidence at LOW when the source is INDICATION (alone).
    Passes EVIDENCE through unchanged.
    """
    if klass == EvidenceClass.EVIDENCE:
        return proposed
    return min(proposed, Confidence.LOW)


def corroborate_indications(signals: list[IndicationSignal]) -> Confidence:
    """
    Combine multiple indication signals with explicit handling of:
      • agreement (supportive signals)
      • disagreement (contradictory signals — dominates the result)
      • source independence (same source ≠ corroboration)

    Ceiling for indication-only corroboration is MEDIUM. EVIDENCE alone reaches
    HIGH, so this function is for INDICATION-only combinations.
    """
    if not signals:
        return Confidence.NONE

    agree = [s for s in signals if s.agrees]
    contradict = [s for s in signals if not s.agrees]

    if len(contradict) > len(agree):
        return Confidence.LOW

    if contradict:
        # Mixed but agree-majority. Independent agreement (≥2 distinct sources)
        # still earns MEDIUM; otherwise LOW.
        if len(agree) >= 2 and len({s.source for s in agree}) >= 2:
            return Confidence.MEDIUM
        return Confidence.LOW

    # All agree.
    distinct = {s.source for s in agree}
    if len(distinct) >= 2 and len(agree) >= 2:
        return Confidence.MEDIUM

    # Single signal or single source: not true corroboration.
    return Confidence.LOW


__all__ = [
    "EvidenceClass",
    "Confidence",
    "IndicationSignal",
    "classify_quality",
    "enforce_indication_ceiling",
    "corroborate_indications",
]
