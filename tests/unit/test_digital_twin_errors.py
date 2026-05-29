# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.digital_twin.errors."""

from __future__ import annotations

import pytest

from shared.digital_twin.errors import (
    ContextPipelineError,
    DigitalTwinError,
    NeutralityViolation,
    UnsafeRecommendationError,
)


pytestmark = pytest.mark.unit


def test_context_pipeline_error_carries_reason_code_and_missing() -> None:
    err = ContextPipelineError("soil_ec missing", reason_code="MISSING_GOVERNOR", missing=["soil_ec"])
    assert err.reason_code == "MISSING_GOVERNOR"
    assert err.missing == ("soil_ec",)
    assert "soil_ec missing" in str(err)


def test_context_pipeline_error_missing_defaults_to_empty_tuple() -> None:
    err = ContextPipelineError("x", reason_code="X")
    assert err.missing == ()


def test_neutrality_violation_carries_path() -> None:
    err = NeutralityViolation("region leaked", path="shared/crop_cards/wheat.yaml")
    assert err.path == "shared/crop_cards/wheat.yaml"


def test_unsafe_recommendation_error_carries_gate_and_reason() -> None:
    err = UnsafeRecommendationError("PHI not elapsed", gate="pesticide", reason_code="PHI_REMAINING")
    assert err.gate == "pesticide"
    assert err.reason_code == "PHI_REMAINING"


def test_all_errors_inherit_from_digital_twin_error() -> None:
    assert issubclass(ContextPipelineError, DigitalTwinError)
    assert issubclass(NeutralityViolation, DigitalTwinError)
    assert issubclass(UnsafeRecommendationError, DigitalTwinError)
    assert issubclass(DigitalTwinError, Exception)
