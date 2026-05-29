# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.workspace (cognitive isolation)."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from shared.digital_twin.errors import ContextPipelineError
from shared.digital_twin.models import IrrigationRecommendation
from shared.workspace import (
    AgriWorkspace,
    validate_workspace_scope,
    workspace_key,
)


pytestmark = pytest.mark.unit


def test_workspace_key_is_stable_for_same_inputs() -> None:
    tenant = uuid4()
    farm = uuid4()
    ws1 = AgriWorkspace(tenant_id=tenant, farm_id=farm, season_id="winter_2026")
    ws2 = AgriWorkspace(tenant_id=tenant, farm_id=farm, season_id="winter_2026")
    assert ws1.key() == ws2.key()
    assert workspace_key(ws1) == ws1.key()


def test_workspace_is_frozen() -> None:
    ws = AgriWorkspace(tenant_id=uuid4(), farm_id=uuid4(), season_id="winter_2026")
    with pytest.raises(ValidationError):
        ws.season_id = "summer_2026"  # type: ignore[misc]


def test_empty_season_id_rejected() -> None:
    with pytest.raises(ValidationError):
        AgriWorkspace(tenant_id=uuid4(), farm_id=uuid4(), season_id="")


def test_validate_scope_passes_for_matching_tenant() -> None:
    tenant = uuid4()
    farm = uuid4()
    ws = AgriWorkspace(tenant_id=tenant, farm_id=farm, season_id="winter_2026")
    rec = IrrigationRecommendation(
        tenant_id=tenant,
        field_id=uuid4(),
        day=date.today(),
        recommended_mm=20.0,
    )
    validate_workspace_scope(rec, ws)  # no exception


def test_validate_scope_raises_for_tenant_mismatch() -> None:
    ws = AgriWorkspace(tenant_id=uuid4(), farm_id=uuid4(), season_id="winter_2026")
    rec = IrrigationRecommendation(
        tenant_id=uuid4(),  # different tenant
        field_id=uuid4(),
        day=date.today(),
        recommended_mm=20.0,
    )
    with pytest.raises(ContextPipelineError) as exc:
        validate_workspace_scope(rec, ws)
    assert exc.value.reason_code == "WORKSPACE_SCOPE_VIOLATION"


def test_workspace_rejects_unknown_field() -> None:
    """extra='forbid' on the workspace prevents silently adding region/farm-name keys."""
    with pytest.raises(ValidationError):
        AgriWorkspace(
            tenant_id=uuid4(),
            farm_id=uuid4(),
            season_id="winter_2026",
            region="north",  # type: ignore[call-arg]
        )
