"""
SAHOOL Advisor AI Service
AI engine for generating agricultural recommendations
"""

from __future__ import annotations

from .models import (
    AdvisorResponse,
    ConfidenceLevel,
    RecommendationAction,
    RecommendationType,
)


class AdvisorAI:
    """AI service for agricultural recommendations"""

    def __init__(self, model_name: str = "sahool-agri-v1"):
        self.model_name = model_name
        self._response_history: dict[str, list[AdvisorResponse]] = {}

    def get_recommendation(
        self,
        tenant_id: str,
        query: str,
        context: dict | None = None,
        field_id: str | None = None,
    ) -> AdvisorResponse:
        """
        Generate an AI recommendation based on query and context.

        In production, this would call the actual AI model.
        This is a placeholder implementation.
        """
        # Determine recommendation type from query
        rec_type = self._classify_query(query)

        # Generate recommendation (placeholder)
        response = AdvisorResponse.create(
            tenant_id=tenant_id,
            field_id=field_id,
            query=query,
            recommendation_type=rec_type,
            summary=f"Recommendation for: {query}",
            summary_ar=f"توصية لـ: {query}",
            actions=[
                RecommendationAction(
                    action="Analyze current conditions",
                    action_ar="تحليل الظروف الحالية",
                    priority=1,
                ),
            ],
            confidence=ConfidenceLevel.MEDIUM,
            sources=["SAHOOL Agricultural Knowledge Base"],
            explanation="Based on agricultural best practices.",
            explanation_ar="بناءً على أفضل الممارسات الزراعية.",
        )

        # Store in history
        if tenant_id not in self._response_history:
            self._response_history[tenant_id] = []
        self._response_history[tenant_id].append(response)

        return response

    def _classify_query(self, query: str) -> RecommendationType:
        """Classify query into recommendation type"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["water", "irrigation", "ري", "ماء"]):
            return RecommendationType.IRRIGATION
        elif any(word in query_lower for word in ["fertiliz", "سماد", "تسميد"]):
            return RecommendationType.FERTILIZATION
        elif any(word in query_lower for word in ["pest", "disease", "آفة", "مرض"]):
            return RecommendationType.PEST_CONTROL
        elif any(word in query_lower for word in ["plant", "seed", "زراعة", "بذور"]):
            return RecommendationType.PLANTING
        elif any(word in query_lower for word in ["harvest", "حصاد"]):
            return RecommendationType.HARVESTING
        elif any(word in query_lower for word in ["soil", "تربة"]):
            return RecommendationType.SOIL_MANAGEMENT
        elif any(word in query_lower for word in ["weather", "rain", "طقس", "مطر"]):
            return RecommendationType.WEATHER_ALERT
        else:
            return RecommendationType.GENERAL

    def get_response_history(
        self,
        tenant_id: str,
        limit: int = 10,
    ) -> list[AdvisorResponse]:
        """Get response history for a tenant"""
        history = self._response_history.get(tenant_id, [])
        return history[-limit:] if limit else history
