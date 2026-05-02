"""
Advisor engine — orchestrates: signal derivation → CRAG retrieval →
knowledge-graph context → action ranking → governance.

محرك المستشار الزراعي الرئيسي (CRAG + KG + Governance + Learning + Feedback).
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from .feedback import FeedbackPublisher
from .governance import GovernanceEngine
from .kb.crag_knowledge_base import CragKnowledgeBase
from .kb.knowledge_graph_client import KnowledgeGraphClient
from .learning import LearningEngine
from .signal_derivation import (
    DerivedSignals,
    FieldContext,
    compute_risk_score,
    derive_signals,
)

logger = logging.getLogger(__name__)

# Action ranking blend: 70 % rule-based, 30 % learned success rate.
RULE_WEIGHT = 0.7
LEARNED_WEIGHT = 0.3


class AdvisorEngine:
    """High-level advisor that combines knowledge sources with governance."""

    def __init__(
        self,
        kg_client: KnowledgeGraphClient,
        crag_kb: CragKnowledgeBase | None,
        governance: GovernanceEngine,
        learning: LearningEngine,
        feedback: FeedbackPublisher,
        embedding_func: Callable[[str], Awaitable[list[float]]] | None = None,
    ) -> None:
        self.kg_client = kg_client
        self.crag_kb = crag_kb
        self.governance = governance
        self.learning = learning
        self.feedback = feedback
        self.embedding_func = embedding_func

    # ---------- Public API --------------------------------------------------

    async def generate_recommendation(self, field: FieldContext) -> dict[str, Any]:
        """Compose a fully-governed recommendation for the given field."""
        signals = derive_signals(field)
        risk_score = compute_risk_score(signals, field)

        knowledge_context: list[str] = []
        if self.crag_kb is not None and self.embedding_func is not None:
            try:
                query = self._build_knowledge_query(signals, field)
                crag_results = await self.crag_kb.retrieve_with_crag(
                    query_text=query,
                    embedding_func=self.embedding_func,
                    region=field.region,
                    crop_type=field.crop_type,
                )
                knowledge_context = [r["text"] for r in crag_results if r.get("text")]
            except Exception as exc:  # noqa: BLE001 — degrade gracefully
                logger.error("advisor.crag_failed", extra={"error": str(exc)})

        graph_context = await self._get_graph_context(field)

        actions = self._candidate_actions(signals)
        scored = [
            (
                action,
                RULE_WEIGHT * self._rule_score(signals, action)
                + LEARNED_WEIGHT * self.learning.get_success_rate(field.crop_type, field.region, action),
            )
            for action in actions
        ]
        if scored:
            best_action, confidence = max(scored, key=lambda x: x[1])
        else:
            best_action, confidence = "no_action", 0.5

        decision: dict[str, Any] = {
            "action": best_action,
            "confidence": confidence,
            "risk_score": risk_score,
            "signals": {
                "water_stress": signals.water_stress,
                "heat_stress": signals.heat_stress,
                "nitrogen_deficiency": signals.nitrogen_deficiency,
                "pest_risk": signals.pest_risk,
                "growth_stage_appropriate": signals.growth_stage_appropriate,
                "critical_ndvi": signals.critical_ndvi,
            },
            "field_context": {
                "crop": field.crop_type,
                "region": field.region,
                "growth_stage": field.growth_stage,
                "ndvi": field.ndvi,
                "ndwi": field.ndwi,
                "soil_moisture": field.soil_moisture,
                "temperature": field.temperature,
            },
            "knowledge_context_summary": "\n".join(knowledge_context[:2]),
            "graph_context": graph_context,
        }
        return self.governance.evaluate(decision)

    async def record_feedback(
        self,
        decision_id: str,
        result: str,
        crop: str,
        region: str,
        action: str,
    ) -> None:
        """Persist outcome to the learning engine and publish to NATS."""
        feedback = {
            "decision_id": decision_id,
            "result": result,
            "crop": crop,
            "region": region,
            "action": action,
        }
        self.learning.record_outcome(feedback)
        await self.feedback.publish_feedback(feedback)
        logger.info("advisor.feedback_recorded", extra={"decision_id": decision_id})

    # ---------- Helpers -----------------------------------------------------

    @staticmethod
    def _build_knowledge_query(signals: DerivedSignals, field: FieldContext) -> str:
        parts: list[str] = []
        if signals.water_stress:
            parts.append("water stress")
        if signals.heat_stress:
            parts.append("heat stress")
        if signals.nitrogen_deficiency:
            parts.append("nitrogen deficiency")
        if signals.pest_risk == "high":
            parts.append("pest outbreak")
        parts.append(f"{field.crop_type} {field.growth_stage}")
        parts.append(field.region)
        return " ".join(parts)

    @staticmethod
    def _candidate_actions(signals: DerivedSignals) -> list[str]:
        actions: list[str] = []
        if signals.water_stress:
            actions.append("increase_irrigation")
        elif signals.heat_stress:
            actions.append("reduce_irrigation")
        if signals.nitrogen_deficiency:
            actions.append("add_nitrogen")
        if signals.pest_risk == "high":
            actions.append("apply_pesticide")
        if not actions:
            actions.append("no_action")
        return actions

    @staticmethod
    def _rule_score(signals: DerivedSignals, action: str) -> float:
        if action == "increase_irrigation" and signals.water_stress:
            return 0.9
        if action == "reduce_irrigation" and signals.heat_stress and not signals.water_stress:
            return 0.7
        if action == "add_nitrogen" and signals.nitrogen_deficiency:
            return 0.85
        if action == "apply_pesticide" and signals.pest_risk == "high":
            return 0.8
        if action == "no_action":
            return 0.5
        return 0.3

    async def _get_graph_context(self, field: FieldContext) -> dict[str, Any]:
        context: dict[str, Any] = {}
        try:
            diseases = await self.kg_client.search_entities(field.crop_type, entity_type="disease", limit=3)
            context["common_diseases"] = diseases
        except Exception as exc:  # noqa: BLE001 — degrade gracefully
            logger.error("advisor.graph_context_failed", extra={"error": str(exc)})
        return context
