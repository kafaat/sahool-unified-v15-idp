# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Simple Agent Router for LLM Orchestrator Service.

Rule-based routing for fast agent selection without LLM overhead.
Supports Arabic and English keyword matching with priority-based selection.

موجه الوكلاء البسيط لخدمة تنسيق نماذج اللغة الكبيرة.
توجيه قائم على القواعد لاختيار الوكلاء بسرعة دون عبء النماذج اللغوية.
يدعم مطابقة الكلمات المفتاحية بالعربية والإنجليزية مع الاختيار حسب الأولوية.
"""

from dataclasses import dataclass

import structlog

from .quick_responses import QuickResponse, get_quick_response
from .routing_rules import ROUTING_RULES, Priority, RoutingRule, get_rule

logger = structlog.get_logger(__name__)


@dataclass
class RoutingResult:
    """
    Result of agent routing.
    نتيجة توجيه الوكلاء.
    """

    agents: list[str]
    intent: str
    priority: Priority
    confidence: float
    requires_image: bool
    requires_field_id: bool
    is_quick_response: bool = False
    quick_response: QuickResponse | None = None
    matched_keywords: list[str] | None = None
    fallback_used: bool = False


class SimpleAgentRouter:
    """
    Simple rule-based agent router.

    Fast routing without LLM - uses keyword matching and predefined rules.
    Supports quick responses for common questions to save API costs.

    موجه الوكلاء البسيط القائم على القواعد.
    توجيه سريع بدون نماذج لغوية - يستخدم مطابقة الكلمات والقواعد المحددة مسبقاً.
    يدعم الردود السريعة للأسئلة الشائعة لتوفير تكاليف API.
    """

    def __init__(self, enable_quick_responses: bool = True) -> None:
        """
        Initialize the router.

        Args:
            enable_quick_responses: Whether to check for quick responses first
        """
        self._enable_quick_responses = enable_quick_responses
        self._rules = ROUTING_RULES

    def route(
        self,
        text: str,
        intent: str | None = None,
        has_image: bool = False,
        has_field_id: bool = False,
    ) -> RoutingResult:
        """
        Route a query to appropriate agents.

        توجيه الاستعلام إلى الوكلاء المناسبين.

        Args:
            text: User query text
            intent: Pre-classified intent (optional, will detect if not provided)
            has_image: Whether an image is provided
            has_field_id: Whether a field ID is provided

        Returns:
            RoutingResult with selected agents and metadata
        """
        # Step 1: Check for quick responses first
        if self._enable_quick_responses:
            quick_resp = get_quick_response(text)
            if quick_resp:
                logger.info(
                    "quick_response_matched",
                    category=quick_resp.category,
                )
                return RoutingResult(
                    agents=[],
                    intent="quick_response",
                    priority=Priority.LOW,
                    confidence=1.0,
                    requires_image=False,
                    requires_field_id=False,
                    is_quick_response=True,
                    quick_response=quick_resp,
                )

        # Step 2: Use provided intent or detect from text
        if intent:
            detected_intent = intent
            matched_keywords = []
            confidence = 0.9  # High confidence if intent provided
        else:
            detected_intent, matched_keywords, confidence = self._detect_intent(
                text, has_image
            )

        # Step 3: Get routing rule for intent
        rule = get_rule(detected_intent)

        if not rule:
            # Fallback to general advisory
            logger.warning(
                "no_rule_found",
                intent=detected_intent,
                fallback="general_advisory",
            )
            rule = get_rule("general_advisory")
            if not rule:
                # Ultimate fallback
                return RoutingResult(
                    agents=["advisory"],
                    intent="general_advisory",
                    priority=Priority.LOW,
                    confidence=0.5,
                    requires_image=False,
                    requires_field_id=False,
                    fallback_used=True,
                )

        # Step 4: Select agents based on rule and context
        agents = self._select_agents(rule, has_image, has_field_id)

        logger.info(
            "routing_completed",
            intent=detected_intent,
            agents=agents,
            priority=rule.priority.value,
            confidence=confidence,
            matched_keywords=matched_keywords[:3] if matched_keywords else [],
        )

        return RoutingResult(
            agents=agents,
            intent=detected_intent,
            priority=rule.priority,
            confidence=confidence,
            requires_image=rule.requires_image,
            requires_field_id=rule.requires_field_id,
            matched_keywords=matched_keywords,
            fallback_used=False,
        )

    def _detect_intent(
        self, text: str, has_image: bool
    ) -> tuple[str, list[str], float]:
        """
        Detect intent from text using keyword matching.

        كشف النية من النص باستخدام مطابقة الكلمات المفتاحية.

        Returns:
            Tuple of (intent, matched_keywords, confidence)
        """
        text_lower = text.lower()
        best_intent = "general_advisory"
        best_score = 0.0
        best_keywords: list[str] = []

        for intent_name, rule in self._rules.items():
            score, keywords = self._calculate_match_score(
                text_lower, rule.keywords_en, rule.keywords_ar
            )

            # Boost score if image matches requirement
            if has_image and rule.requires_image:
                score += 0.2

            if score > best_score:
                best_score = score
                best_intent = intent_name
                best_keywords = keywords

        # If we have an image but no strong intent, default to image_analysis
        if has_image and best_score < 0.3:
            best_intent = "image_analysis"
            best_score = 0.7
            best_keywords = ["image"]

        # Calculate confidence (cap at 0.95)
        confidence = min(best_score, 0.95) if best_score > 0 else 0.5

        return best_intent, best_keywords, confidence

    def _calculate_match_score(
        self,
        text: str,
        keywords_en: list[str],
        keywords_ar: list[str],
    ) -> tuple[float, list[str]]:
        """
        Calculate keyword match score.

        حساب درجة مطابقة الكلمات المفتاحية.

        Returns:
            Tuple of (score, matched_keywords)
        """
        matched = []
        all_keywords = keywords_en + keywords_ar

        for kw in all_keywords:
            if kw in text:
                matched.append(kw)

        if not matched:
            return 0.0, []

        # Base score from match ratio
        total_keywords = len(all_keywords) if all_keywords else 1
        base_score = len(matched) / total_keywords * 0.7

        # Bonus for multiple matches
        if len(matched) >= 2:
            base_score += 0.15
        if len(matched) >= 3:
            base_score += 0.10

        return min(base_score, 0.95), matched

    def _select_agents(
        self,
        rule: RoutingRule,
        has_image: bool,
        has_field_id: bool,
    ) -> list[str]:
        """
        Select agents based on rule and context.

        اختيار الوكلاء بناءً على القاعدة والسياق.
        """
        agents = list(rule.agents)  # Copy the list

        # If image is required but not provided, use fallback agents
        if rule.requires_image and not has_image:
            if rule.fallback_agents:
                agents = list(rule.fallback_agents)
                logger.info(
                    "using_fallback_agents",
                    reason="image_required_but_not_provided",
                    original=rule.agents,
                    fallback=agents,
                )

        # Limit to max 5 agents
        return agents[:5]

    def preview_route(
        self,
        intent: str,
        has_image: bool = False,
        has_field_id: bool = False,
    ) -> dict:
        """
        Preview routing for an intent without executing.

        معاينة التوجيه للنية بدون تنفيذ.

        Args:
            intent: The intent to preview routing for
            has_image: Whether an image would be provided
            has_field_id: Whether a field ID would be provided

        Returns:
            Dictionary with routing preview
        """
        rule = get_rule(intent)

        if not rule:
            return {
                "intent": intent,
                "found": False,
                "agents": [],
                "message_en": f"No routing rule found for intent: {intent}",
                "message_ar": f"لم يتم العثور على قاعدة توجيه للنية: {intent}",
            }

        agents = self._select_agents(rule, has_image, has_field_id)
        would_use_fallback = (
            rule.requires_image
            and not has_image
            and bool(rule.fallback_agents)
        )

        return {
            "intent": intent,
            "found": True,
            "agents": agents,
            "priority": rule.priority.value,
            "requires_image": rule.requires_image,
            "requires_field_id": rule.requires_field_id,
            "description_en": rule.description_en,
            "description_ar": rule.description_ar,
            "would_use_fallback": would_use_fallback,
            "fallback_agents": rule.fallback_agents if would_use_fallback else [],
            "sample_keywords_en": rule.keywords_en[:5],
            "sample_keywords_ar": rule.keywords_ar[:5],
        }

    def get_available_intents(self) -> list[str]:
        """
        Get all available intents.

        الحصول على جميع النوايا المتاحة.
        """
        return list(self._rules.keys())

    def get_agents_for_intent(self, intent: str) -> list[str]:
        """
        Get agents for a specific intent.

        الحصول على الوكلاء لنية محددة.
        """
        rule = get_rule(intent)
        return list(rule.agents) if rule else []


# Singleton instance
_router_instance: SimpleAgentRouter | None = None


def get_router(enable_quick_responses: bool = True) -> SimpleAgentRouter:
    """
    Get router instance (singleton).

    الحصول على نسخة الموجه (singleton).
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = SimpleAgentRouter(
            enable_quick_responses=enable_quick_responses
        )
    return _router_instance
