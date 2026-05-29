# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.digital_twin.pesticide_gate (safety-critical)."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from shared.digital_twin.pesticide_gate import (
    PesticideGateStatus,
    evaluate,
)


pytestmark = pytest.mark.unit


TODAY = date(2026, 5, 29)


def test_missing_application_date_returns_insufficient_data() -> None:
    res = evaluate(last_application_date=None, phi_days=14, today=TODAY)
    assert res.status == PesticideGateStatus.INSUFFICIENT_DATA
    assert "Spray data missing" in res.reason_en
    assert res.phi_days_remaining is None


def test_missing_phi_returns_insufficient_data() -> None:
    res = evaluate(last_application_date=TODAY - timedelta(days=5), phi_days=None, today=TODAY)
    assert res.status == PesticideGateStatus.INSUFFICIENT_DATA


def test_phi_not_elapsed_is_blocked() -> None:
    """PHI > 0 → hard block. Layer 1 short-circuits."""
    res = evaluate(
        last_application_date=TODAY - timedelta(days=3),
        phi_days=14,
        today=TODAY,
        half_life_days=7.0,
        economic_threshold_exceeded=True,
    )
    assert res.status == PesticideGateStatus.BLOCKED
    assert res.phi_days_remaining == 11
    # RRI and economic must NOT leak into a BLOCKED result.
    assert res.rri is None
    assert res.economic_warning is False


def test_phi_just_elapsed_requires_lab() -> None:
    """PHI = 0 → LAB_REQUIRED, never CLEARED on its own."""
    res = evaluate(
        last_application_date=TODAY - timedelta(days=14),
        phi_days=14,
        today=TODAY,
    )
    assert res.status == PesticideGateStatus.LAB_REQUIRED
    assert res.phi_days_remaining == 0
    assert res.requires_lab is True


def test_rri_computed_only_when_half_life_supplied() -> None:
    no_hl = evaluate(
        last_application_date=TODAY - timedelta(days=14),
        phi_days=14,
        today=TODAY,
    )
    assert no_hl.rri is None

    with_hl = evaluate(
        last_application_date=TODAY - timedelta(days=14),
        phi_days=14,
        today=TODAY,
        half_life_days=7.0,
    )
    assert with_hl.rri is not None
    assert 0.0 <= with_hl.rri <= 1.0


def test_economic_warning_does_not_block() -> None:
    """Layer 3 economic is a warning, not a blocker."""
    res = evaluate(
        last_application_date=TODAY - timedelta(days=14),
        phi_days=14,
        today=TODAY,
        economic_threshold_exceeded=True,
    )
    assert res.status == PesticideGateStatus.LAB_REQUIRED
    assert res.economic_warning is True


def test_phi_long_elapsed_still_requires_lab() -> None:
    """Lab analysis governs the final clearance no matter how long ago PHI elapsed."""
    res = evaluate(
        last_application_date=TODAY - timedelta(days=180),
        phi_days=14,
        today=TODAY,
        half_life_days=7.0,
    )
    assert res.status == PesticideGateStatus.LAB_REQUIRED
    assert res.is_safe is False


def test_bilingual_reasons_present() -> None:
    res = evaluate(
        last_application_date=TODAY - timedelta(days=3),
        phi_days=14,
        today=TODAY,
    )
    assert res.reason_ar
    assert res.reason_en
    assert "11" in res.reason_ar or "11" in res.reason_en
