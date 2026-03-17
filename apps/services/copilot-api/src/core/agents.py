"""
Agent Router for Copilot
موجه الوكلاء لـ Copilot

Routes requests to appropriate AI agents based on intent.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class AgentType(StrEnum):
    """Available agent types"""

    CODE_FIX = "code_fix"
    CODE_REVIEW = "code_review"
    FIELD_ADVISOR = "field_advisor"
    WEATHER_ADVISOR = "weather_advisor"
    IRRIGATION_ADVISOR = "irrigation_advisor"
    GENERAL = "general"


@dataclass
class AgentRoute:
    """Agent routing configuration"""

    agent_type: AgentType
    patterns: list[str]
    keywords_en: list[str]
    keywords_ar: list[str]
    priority: int = 0
    service_url: str | None = None


@dataclass
class RoutingResult:
    """Result of agent routing"""

    agent_type: AgentType
    confidence: float
    matched_patterns: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)


class AgentRouter:
    """
    Intelligent agent routing based on user intent.
    توجيه ذكي للوكلاء بناءً على نية المستخدم

    Analyzes user messages to determine the appropriate agent.
    """

    def __init__(self):
        """Initialize router with default routes"""
        self.routes = self._default_routes()

    def _default_routes(self) -> list[AgentRoute]:
        """Get default agent routes"""
        return [
            # Code Fix Agent
            AgentRoute(
                agent_type=AgentType.CODE_FIX,
                patterns=[
                    r"(fix|repair|correct|debug)\s+(the\s+)?(code|bug|error|issue)",
                    r"(أصلح|صحح|إصلاح)\s+(الكود|الخطأ|المشكلة)",
                    r"(lint|format|analyze)\s+(code|file|project)",
                    r"(تحليل|تنسيق)\s+الكود",
                ],
                keywords_en=["fix", "bug", "error", "lint", "debug", "code issue", "syntax"],
                keywords_ar=["أصلح", "خطأ", "مشكلة", "كود", "تصحيح", "إصلاح"],
                priority=10,
            ),
            # Code Review Agent
            AgentRoute(
                agent_type=AgentType.CODE_REVIEW,
                patterns=[
                    r"(review|check|audit)\s+(my\s+)?(code|pr|pull request)",
                    r"(راجع|فحص)\s+(الكود|البرنامج)",
                    r"code\s+quality",
                ],
                keywords_en=["review", "pr", "pull request", "code quality", "audit"],
                keywords_ar=["راجع", "مراجعة", "فحص", "جودة الكود"],
                priority=9,
            ),
            # Field Advisor
            AgentRoute(
                agent_type=AgentType.FIELD_ADVISOR,
                patterns=[
                    r"(field|crop|plant|farm)\s+(status|health|condition)",
                    r"(حالة|صحة)\s+(الحقل|المحصول|المزرعة)",
                    r"(ndvi|vegetation|growth)",
                    r"(الغطاء النباتي|النمو)",
                ],
                keywords_en=["field", "crop", "plant", "ndvi", "vegetation", "growth", "farm"],
                keywords_ar=["حقل", "محصول", "مزرعة", "نبات", "غطاء نباتي", "نمو"],
                priority=8,
            ),
            # Weather Advisor
            AgentRoute(
                agent_type=AgentType.WEATHER_ADVISOR,
                patterns=[
                    r"(weather|forecast|temperature|rain)",
                    r"(الطقس|الجو|درجة الحرارة|المطر)",
                    r"(climate|humidity|wind)",
                    r"(المناخ|الرطوبة|الرياح)",
                ],
                keywords_en=["weather", "forecast", "temperature", "rain", "humidity", "wind"],
                keywords_ar=["طقس", "توقعات", "حرارة", "مطر", "رطوبة", "رياح"],
                priority=7,
            ),
            # Irrigation Advisor
            AgentRoute(
                agent_type=AgentType.IRRIGATION_ADVISOR,
                patterns=[
                    r"(irrigation|water|watering)\s+(schedule|plan|advice)",
                    r"(الري|الماء|السقي)\s+(جدول|خطة|نصيحة)",
                    r"(soil\s+moisture|water\s+stress)",
                    r"(رطوبة التربة|إجهاد مائي)",
                ],
                keywords_en=["irrigation", "water", "watering", "soil moisture", "drought"],
                keywords_ar=["ري", "ماء", "سقي", "رطوبة", "جفاف"],
                priority=7,
            ),
            # General (fallback — no patterns; selected when no other agent matches)
            AgentRoute(
                agent_type=AgentType.GENERAL,
                patterns=[],
                keywords_en=[],
                keywords_ar=[],
                priority=0,
            ),
        ]

    def route(self, message: str) -> RoutingResult:
        """
        Route a message to the appropriate agent.
        توجيه رسالة إلى الوكيل المناسب

        Args:
            message: User message

        Returns:
            RoutingResult with agent type and confidence
        """
        message_lower = message.lower()
        best_result: RoutingResult | None = None
        best_score = 0.0

        for route in sorted(self.routes, key=lambda r: -r.priority):
            score = 0.0
            matched_patterns = []
            matched_keywords = []

            # Check patterns
            for pattern in route.patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    score += 0.5
                    matched_patterns.append(pattern)

            # Check English keywords
            for keyword in route.keywords_en:
                if keyword.lower() in message_lower:
                    score += 0.2
                    matched_keywords.append(keyword)

            # Check Arabic keywords
            for keyword in route.keywords_ar:
                if keyword in message:
                    score += 0.2
                    matched_keywords.append(keyword)

            # Apply priority boost
            score += route.priority * 0.01

            # Normalize score
            confidence = min(score, 1.0)

            if confidence > best_score:
                best_score = confidence
                best_result = RoutingResult(
                    agent_type=route.agent_type,
                    confidence=confidence,
                    matched_patterns=matched_patterns,
                    matched_keywords=matched_keywords,
                )

        # Fallback to general
        if best_result is None or best_score < 0.1:
            best_result = RoutingResult(
                agent_type=AgentType.GENERAL,
                confidence=0.5,
            )

        logger.debug(
            "Agent routed",
            agent=best_result.agent_type.value,
            confidence=best_result.confidence,
            keywords=best_result.matched_keywords[:3],
        )

        return best_result

    def get_agent_description(self, agent_type: AgentType) -> dict[str, str]:
        """Get description for an agent type"""
        descriptions = {
            AgentType.CODE_FIX: {
                "en": "Code analysis and bug fixing agent",
                "ar": "وكيل تحليل الكود وإصلاح الأخطاء",
            },
            AgentType.CODE_REVIEW: {
                "en": "Code review and quality assessment agent",
                "ar": "وكيل مراجعة الكود وتقييم الجودة",
            },
            AgentType.FIELD_ADVISOR: {
                "en": "Field and crop advisory agent",
                "ar": "وكيل استشارات الحقول والمحاصيل",
            },
            AgentType.WEATHER_ADVISOR: {
                "en": "Weather forecast and climate advisory agent",
                "ar": "وكيل توقعات الطقس واستشارات المناخ",
            },
            AgentType.IRRIGATION_ADVISOR: {
                "en": "Irrigation planning and water management agent",
                "ar": "وكيل تخطيط الري وإدارة المياه",
            },
            AgentType.GENERAL: {
                "en": "General purpose assistant",
                "ar": "مساعد عام",
            },
        }
        return descriptions.get(agent_type, descriptions[AgentType.GENERAL])


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_agent_router: AgentRouter | None = None


def get_agent_router() -> AgentRouter:
    """Get or create global agent router"""
    global _agent_router
    if _agent_router is None:
        _agent_router = AgentRouter()
    return _agent_router
