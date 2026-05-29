# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Workspace Models - نماذج فضاء العمل
=====================================
``AgriWorkspace`` = (tenant, farm, season) — the cognitive isolation key.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from shared.digital_twin.errors import ContextPipelineError


class AgriWorkspace(BaseModel):
    """
    Cognitive isolation triple-key.
    مفتاح العزل الإدراكي الثلاثي.

    Every decision is scoped to one workspace. Crossing workspaces requires
    an explicit handoff — never an implicit join.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: UUID
    farm_id: UUID
    season_id: str = Field(min_length=1, max_length=64)

    def key(self) -> str:
        """Stable string key for chain attribution. مفتاح نصّي مستقرّ."""
        return f"{self.tenant_id}/{self.farm_id}/{self.season_id}"


def workspace_key(ws: AgriWorkspace) -> str:
    """Convenience for callers that hold the workspace by reference."""
    return ws.key()


def validate_workspace_scope(recommendation: Any, ws: AgriWorkspace) -> None:
    """
    Enforce that a recommendation belongs to the supplied workspace.

    Reads ``tenant_id`` and ``field_id`` (or ``farm_id``) from the
    recommendation. The recommendation's ``field_id`` is treated as a member
    of the workspace's farm (the relation is one-to-many).

    Raises:
        ContextPipelineError(reason_code="WORKSPACE_SCOPE_VIOLATION") on mismatch.
    """
    rec_tenant = getattr(recommendation, "tenant_id", None)
    if rec_tenant is None or rec_tenant != ws.tenant_id:
        raise ContextPipelineError(
            "Recommendation tenant does not match workspace tenant.",
            reason_code="WORKSPACE_SCOPE_VIOLATION",
            missing=["tenant_match"],
        )

    rec_farm = getattr(recommendation, "farm_id", None)
    if rec_farm is not None and rec_farm != ws.farm_id:
        raise ContextPipelineError(
            "Recommendation farm does not match workspace farm.",
            reason_code="WORKSPACE_SCOPE_VIOLATION",
            missing=["farm_match"],
        )


__all__ = [
    "AgriWorkspace",
    "workspace_key",
    "validate_workspace_scope",
]
