# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.digital_twin.evidence_class."""

from __future__ import annotations

import pytest

from shared.digital_twin.evidence_class import (
    Confidence,
    EvidenceClass,
    IndicationSignal,
    classify_quality,
    corroborate_indications,
    enforce_indication_ceiling,
)
from shared.process_models.uncertainty import QualityFlag


pytestmark = pytest.mark.unit


# ── classify_quality ─────────────────────────────────────────────────────


def test_interpolated_is_indication() -> None:
    assert classify_quality(QualityFlag.INTERPOLATED) == EvidenceClass.INDICATION


def test_simulated_is_indication() -> None:
    assert classify_quality(QualityFlag.SIMULATED) == EvidenceClass.INDICATION


def test_uncalibrated_is_indication() -> None:
    assert classify_quality(QualityFlag.UNCALIBRATED) == EvidenceClass.INDICATION


def test_calibrated_is_evidence() -> None:
    assert classify_quality(QualityFlag.CALIBRATED) == EvidenceClass.EVIDENCE


def test_observed_default_is_indication() -> None:
    """Satellite NDVI is OBSERVED but proxy — must default to INDICATION."""
    assert classify_quality(QualityFlag.OBSERVED) == EvidenceClass.INDICATION


def test_observed_lab_is_evidence() -> None:
    """Lab analysis is OBSERVED + is_lab → EVIDENCE."""
    assert classify_quality(QualityFlag.OBSERVED, is_lab=True) == EvidenceClass.EVIDENCE


# ── enforce_indication_ceiling ───────────────────────────────────────────


def test_indication_capped_at_low_even_when_high_proposed() -> None:
    assert enforce_indication_ceiling(Confidence.HIGH, EvidenceClass.INDICATION) == Confidence.LOW


def test_evidence_passes_through_unchanged() -> None:
    assert enforce_indication_ceiling(Confidence.HIGH, EvidenceClass.EVIDENCE) == Confidence.HIGH


def test_confidence_is_intenum_orderable() -> None:
    """IntEnum lets us use min()/max() naturally without conversions."""
    assert Confidence.NONE < Confidence.LOW < Confidence.MEDIUM < Confidence.HIGH
    assert min(Confidence.HIGH, Confidence.LOW) == Confidence.LOW


# ── corroborate_indications ──────────────────────────────────────────────


def test_empty_signals_gives_none() -> None:
    assert corroborate_indications([]) == Confidence.NONE


def test_three_independent_agreeing_indications_give_medium() -> None:
    """Indication-only corroboration ceiling is MEDIUM."""
    signals = [
        IndicationSignal("ndvi_drop", agrees=True, source="sentinel2"),
        IndicationSignal("sar_drop", agrees=True, source="sar"),
        IndicationSignal("soil_moisture_low", agrees=True, source="iot"),
    ]
    assert corroborate_indications(signals) == Confidence.MEDIUM


def test_two_agree_one_contradict_gives_medium_when_sources_independent() -> None:
    signals = [
        IndicationSignal("ndvi_drop", agrees=True, source="sentinel2"),
        IndicationSignal("sar_drop", agrees=True, source="sar"),
        IndicationSignal("soil_sensor_normal", agrees=False, source="iot"),
    ]
    assert corroborate_indications(signals) == Confidence.MEDIUM


def test_one_agree_two_contradict_gives_low_contradiction_dominates() -> None:
    signals = [
        IndicationSignal("ndvi_drop", agrees=True, source="sentinel2"),
        IndicationSignal("sar_normal", agrees=False, source="sar"),
        IndicationSignal("soil_normal", agrees=False, source="iot"),
    ]
    assert corroborate_indications(signals) == Confidence.LOW


def test_single_signal_is_low_not_corroborated() -> None:
    signals = [IndicationSignal("ndvi_drop", agrees=True, source="sentinel2")]
    assert corroborate_indications(signals) == Confidence.LOW


def test_two_agree_same_source_is_low_not_independent() -> None:
    """Same source agreeing twice ≠ corroboration."""
    signals = [
        IndicationSignal("ndvi_drop_jan", agrees=True, source="sentinel2"),
        IndicationSignal("ndvi_drop_feb", agrees=True, source="sentinel2"),
    ]
    assert corroborate_indications(signals) == Confidence.LOW
