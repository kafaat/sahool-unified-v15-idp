# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.digital_twin.field_lifecycle."""

from __future__ import annotations

import pytest

from shared.digital_twin.field_lifecycle import (
    GOVERNING_OBSERVABLES,
    FieldQualityState,
    SoilTestChoice,
    effective_confidence_cap,
    resolve_state,
)


pytestmark = pytest.mark.unit


# ── State transitions ────────────────────────────────────────────────────


def test_not_decided_with_missing_governors_is_blocked() -> None:
    a = resolve_state(soil_choice=SoilTestChoice.NOT_DECIDED, provided_governors=frozenset())
    assert a.state == FieldQualityState.BLOCKED
    assert a.confidence_cap == 0
    assert set(a.missing_governors) == GOVERNING_OBSERVABLES


def test_skip_yields_limited() -> None:
    a = resolve_state(soil_choice=SoilTestChoice.SKIP, provided_governors=frozenset())
    assert a.state == FieldQualityState.LIMITED
    assert a.confidence_cap == 1


def test_request_lab_yields_pending_lab() -> None:
    a = resolve_state(
        soil_choice=SoilTestChoice.REQUEST_LAB,
        provided_governors=frozenset({"soil_ec"}),
    )
    assert a.state == FieldQualityState.PENDING_LAB
    assert a.confidence_cap == 2


def test_lab_request_pending_overrides_not_decided() -> None:
    a = resolve_state(
        soil_choice=SoilTestChoice.NOT_DECIDED,
        provided_governors=frozenset(),
        lab_request_pending=True,
    )
    assert a.state == FieldQualityState.PENDING_LAB


def test_completed_with_all_governors_yields_ready() -> None:
    a = resolve_state(
        soil_choice=SoilTestChoice.COMPLETED,
        provided_governors=GOVERNING_OBSERVABLES,
    )
    assert a.state == FieldQualityState.READY
    assert a.confidence_cap == 3
    assert a.missing_governors == ()


def test_completed_with_partial_governors_is_not_ready() -> None:
    a = resolve_state(
        soil_choice=SoilTestChoice.COMPLETED,
        provided_governors=frozenset({"soil_ec"}),
    )
    # COMPLETED + missing governors → falls to BLOCKED (no other choice path)
    assert a.state == FieldQualityState.BLOCKED


# ── Confidence ceiling invariant (Decision Kernel) ───────────────────────


def test_zone_factor_none_never_reaches_high() -> None:
    """Decision Kernel invariant: uncalibrated → max MEDIUM."""
    for state in (FieldQualityState.READY, FieldQualityState.PENDING_LAB):
        cap = effective_confidence_cap(state, zone_factor=None)
        assert cap <= 2  # MEDIUM


def test_ready_with_calibration_reaches_high() -> None:
    cap = effective_confidence_cap(FieldQualityState.READY, zone_factor=1.05)
    assert cap == 3


def test_blocked_state_zero_cap_regardless_of_calibration() -> None:
    assert effective_confidence_cap(FieldQualityState.BLOCKED, zone_factor=1.0) == 0
    assert effective_confidence_cap(FieldQualityState.BLOCKED, zone_factor=None) == 0


# ── allows_recommendation rules ──────────────────────────────────────────


def test_blocked_allows_no_recommendation() -> None:
    a = resolve_state(soil_choice=SoilTestChoice.NOT_DECIDED, provided_governors=frozenset())
    assert not a.allows_recommendation("irrigation")
    assert not a.allows_recommendation("fertilizer")
    assert not a.allows_recommendation("pesticide")


def test_pesticide_requires_ready_state() -> None:
    """Safety-critical: pesticide cannot be issued in LIMITED or PENDING_LAB."""
    for state, choice, governors in (
        (FieldQualityState.LIMITED, SoilTestChoice.SKIP, frozenset()),
        (FieldQualityState.PENDING_LAB, SoilTestChoice.REQUEST_LAB, frozenset()),
    ):
        a = resolve_state(soil_choice=choice, provided_governors=governors)
        assert a.state == state
        assert not a.allows_recommendation("pesticide")


def test_irrigation_allowed_in_limited_and_pending() -> None:
    for choice, governors in (
        (SoilTestChoice.SKIP, frozenset()),
        (SoilTestChoice.REQUEST_LAB, frozenset()),
    ):
        a = resolve_state(soil_choice=choice, provided_governors=governors)
        assert a.allows_recommendation("irrigation")
        assert a.allows_recommendation("fertilizer")


def test_ready_allows_all_recommendations_including_pesticide() -> None:
    a = resolve_state(
        soil_choice=SoilTestChoice.COMPLETED,
        provided_governors=GOVERNING_OBSERVABLES,
    )
    assert a.allows_recommendation("irrigation")
    assert a.allows_recommendation("fertilizer")
    assert a.allows_recommendation("pesticide")
