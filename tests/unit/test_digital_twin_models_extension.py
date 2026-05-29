# SPDX-License-Identifier: Proprietary
"""Unit tests for additive extensions to shared.digital_twin.models."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from shared.digital_twin.decision_chain import ChainStep, DecisionChain
from shared.digital_twin.models import (
    BackendDetail,
    FarmerView,
    IrrigationRecommendation,
)


pytestmark = pytest.mark.unit


def test_farmer_view_default_prompt_style_is_suggestion() -> None:
    """Decision Kernel invariant: default is 'suggestion', never 'command'."""
    v = FarmerView(
        signal="green",
        headline_ar="ري متوازن",
        headline_en="Balanced irrigation",
        next_action_ar="ري 20 ملم خلال يومين",
        next_action_en="Irrigate 20mm within 2 days",
    )
    assert v.prompt_style == "suggestion"
    assert v.confidence_label == "low"


def test_farmer_view_rejects_unknown_field() -> None:
    """extra='forbid' must mechanically reject unknown fields."""
    with pytest.raises(ValidationError):
        FarmerView(
            signal="green",
            headline_ar="x",
            headline_en="x",
            next_action_ar="x",
            next_action_en="x",
            region="al-jawf",  # type: ignore[call-arg]
        )


def test_farmer_view_rejects_bad_signal() -> None:
    with pytest.raises(ValidationError):
        FarmerView(
            signal="purple",
            headline_ar="x",
            headline_en="x",
            next_action_ar="x",
            next_action_en="x",
        )


def test_backend_detail_allows_extra_fields() -> None:
    """extra='allow' lets services attach domain-specific raw fields."""
    d = BackendDetail(
        engines_used=["fao56"],
        zone_factor=1.1,
        custom_metric=42,  # type: ignore[call-arg]
    )
    assert d.engines_used == ["fao56"]
    assert d.zone_factor == 1.1


def test_irrigation_recommendation_backward_compatible_without_views() -> None:
    """Existing consumers must be able to construct without the new fields."""
    rec = IrrigationRecommendation(
        tenant_id=uuid4(),
        field_id=uuid4(),
        day=date.today(),
        recommended_mm=20.0,
    )
    assert rec.farmer_view is None
    assert rec.backend_detail is None
    assert rec.decision_chain is None


def test_irrigation_recommendation_accepts_full_decision_kernel_payload() -> None:
    rec = IrrigationRecommendation(
        tenant_id=uuid4(),
        field_id=uuid4(),
        day=date.today(),
        recommended_mm=20.0,
        farmer_view=FarmerView(
            signal="yellow",
            headline_ar="انتباه",
            headline_en="Caution",
            next_action_ar="افحص الرطوبة",
            next_action_en="Check moisture",
        ),
        backend_detail=BackendDetail(
            engines_used=["fao56", "salinity"],
            workspace_key="t1/f1/winter_2026",
            compute_cost_summary={"total_ms": 12.3},
        ),
        decision_chain=DecisionChain(
            workspace_key="t1/f1/winter_2026",
            steps=[ChainStep(name="fao56_et0", kind="engine", cost_estimate_ms=2.0)],
        ),
    )
    assert rec.farmer_view is not None
    assert rec.backend_detail is not None
    assert rec.backend_detail.workspace_key == "t1/f1/winter_2026"
    assert rec.decision_chain is not None
    assert len(rec.decision_chain.steps) == 1
