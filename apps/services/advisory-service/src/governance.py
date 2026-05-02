"""
Governance engine: classify a candidate decision into an action policy
(auto-approve / human-review / reject) based on action type and risk score.

محرك الحوكمة: تصنيف القرار المقترح حسب نوع الإجراء ودرجة الخطر.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionStatus(StrEnum):
    APPROVED = "approved"
    PENDING = "pending_approval"
    REJECTED = "rejected"


# Threshold tuning — module-level for testability.
HIGH_RISK_THRESHOLD = 0.85
MEDIUM_RISK_THRESHOLD = 0.60


class GovernanceEngine:
    """Decide whether a candidate action is auto-approved, requires human
    review, or must be rejected outright."""

    def __init__(self) -> None:
        # Low-risk actions that execute automatically.
        self.auto_approve_actions: set[str] = {
            "increase_irrigation",
            "reduce_irrigation",
            "no_action",
            "monitor_only",
        }
        # Medium-risk actions that require human review.
        self.review_required_actions: set[str] = {
            "add_nitrogen",
            "add_phosphorus",
            "add_potassium",
            "apply_pesticide",
            "apply_fungicide",
            "harvest_early",
        }
        # High-risk actions that are rejected outright.
        self.reject_actions: set[str] = {
            "increase_fertilizer_high",
            "emergency_harvest",
            "apply_banned_pesticide",
        }

    def evaluate(self, decision: dict[str, Any]) -> dict[str, Any]:
        """Annotate the decision with governance metadata.

        Returns a new dict with the additional fields:
        ``risk_level``, ``risk_score``, ``requires_approval``, ``status``,
        ``governance_reason``, ``approved_by``.
        """
        action = decision.get("action", "unknown")
        risk_score = float(decision.get("risk_score", 0.5))

        if action in self.reject_actions or risk_score > HIGH_RISK_THRESHOLD:
            risk_level = RiskLevel.HIGH
            requires_approval = False
            status = DecisionStatus.REJECTED
            reason = f"Action rejected: high risk (score {risk_score:.2f})"
        elif action in self.review_required_actions or risk_score > MEDIUM_RISK_THRESHOLD:
            risk_level = RiskLevel.MEDIUM
            requires_approval = True
            status = DecisionStatus.PENDING
            reason = f"Requires human review: {action} with risk {risk_score:.2f}"
        else:
            risk_level = RiskLevel.LOW
            requires_approval = False
            status = DecisionStatus.APPROVED
            reason = "Auto-approved: low risk action"

        return {
            **decision,
            "risk_level": risk_level.value,
            "risk_score": risk_score,
            "requires_approval": requires_approval,
            "status": status.value,
            "governance_reason": reason,
            "approved_by": None,
        }

    def approve(
        self,
        decision: dict[str, Any],
        approved_by: str = "human",
        modified_action: str | None = None,
    ) -> dict[str, Any]:
        """Apply human approval. Optionally override the action."""
        out = dict(decision)
        out["status"] = DecisionStatus.APPROVED.value
        out["requires_approval"] = False
        out["approved_by"] = approved_by
        if modified_action:
            out["action"] = modified_action
            out["governance_reason"] = f"Modified by {approved_by}: {modified_action}"
        else:
            out["governance_reason"] = f"Approved by {approved_by}"
        return out

    def reject(
        self,
        decision: dict[str, Any],
        rejected_by: str = "human",
        reason: str = "",
    ) -> dict[str, Any]:
        """Apply human rejection."""
        out = dict(decision)
        out["status"] = DecisionStatus.REJECTED.value
        out["requires_approval"] = False
        out["approved_by"] = rejected_by
        out["governance_reason"] = f"Rejected by {rejected_by}: {reason}".rstrip(": ")
        return out
