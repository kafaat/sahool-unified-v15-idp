# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agricultural Cognitive Workspace - فضاء العمل الزراعي الإدراكي
================================================================
Triple-key cognitive isolation for SAHOOL decision pipelines:

    workspace = (tenant_id, farm_id, season_id)

Prevents decision/memory leakage across farms and growing seasons. Pure
dataclass — no storage, no tables, no shared state. The key is stamped on
each ``DecisionChain`` and ``IrrigationRecommendation.backend_detail`` so any
introspection can scope cleanly.
"""

from shared.workspace.models import (
    AgriWorkspace,
    validate_workspace_scope,
    workspace_key,
)

__all__ = [
    "AgriWorkspace",
    "workspace_key",
    "validate_workspace_scope",
]
