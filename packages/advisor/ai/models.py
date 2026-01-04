"""
SAHOOL Advisor AI Models
Data models for AI recommendations
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class RecommendationType(str, Enum):
    """Type of recommendation"""

    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PEST_CONTROL = "pest_control"
    PLANTING = "planting"
    HARVESTING = "harvesting"
    SOIL_MANAGEMENT = "soil_management"
    WEATHER_ALERT = "weather_alert"
    GENERAL = "general"


class ConfidenceLevel(str, Enum):
    """AI confidence level"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RecommendationAction:
    """Specific action within a recommendation"""

    action: str
    action_ar: str | None
    priority: int  # 1 = highest
    estimated_impact: str | None = None

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "action_ar": self.action_ar,
            "priority": self.priority,
            "estimated_impact": self.estimated_impact,
        }


@dataclass
class AdvisorResponse:
    """AI advisor response"""

    id: str
    tenant_id: str
    field_id: str | None
    query: str
    recommendation_type: RecommendationType
    summary: str
    summary_ar: str | None
    actions: list[RecommendationAction]
    confidence: ConfidenceLevel
    sources: list[str]
    explanation: str | None
    explanation_ar: str | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: str,
        query: str,
        recommendation_type: RecommendationType,
        summary: str,
        actions: list[RecommendationAction],
        confidence: ConfidenceLevel,
        sources: list[str],
        field_id: str | None = None,
        summary_ar: str | None = None,
        explanation: str | None = None,
        explanation_ar: str | None = None,
    ) -> AdvisorResponse:
        """Factory method to create a new advisor response"""
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            field_id=field_id,
            query=query,
            recommendation_type=recommendation_type,
            summary=summary,
            summary_ar=summary_ar,
            actions=actions,
            confidence=confidence,
            sources=sources,
            explanation=explanation,
            explanation_ar=explanation_ar,
            created_at=datetime.now(UTC),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "query": self.query,
            "recommendation_type": self.recommendation_type.value,
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "actions": [a.to_dict() for a in self.actions],
            "confidence": self.confidence.value,
            "sources": self.sources,
            "explanation": self.explanation,
            "explanation_ar": self.explanation_ar,
            "created_at": self.created_at.isoformat(),
        }
