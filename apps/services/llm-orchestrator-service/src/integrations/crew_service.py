# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Crew Service Integration
تكامل خدمة الطاقم

Wraps the shared CrewAI module for use in the orchestrator.
"""

import sys
import os
from typing import Any

import structlog

# Add shared module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

logger = structlog.get_logger()


class CrewService:
    """
    Multi-agent crew service using CrewAI.
    خدمة طاقم الوكلاء المتعددين باستخدام CrewAI
    """

    def __init__(self):
        self._orchestrator = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the crew orchestrator."""
        if self._initialized:
            return True

        try:
            from shared.agents import CrewAIOrchestrator

            self._orchestrator = CrewAIOrchestrator()
            await self._orchestrator.initialize()
            self._initialized = True
            logger.info("Crew service initialized")
            return True

        except ImportError as e:
            logger.warning("shared.agents not available", error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to initialize crew service", error=str(e))
            return False

    async def query(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a query with the agricultural crew.
        تنفيذ استعلام مع الطاقم الزراعي
        """
        if not self._initialized or not self._orchestrator:
            return self._fallback_response(query)

        try:
            result = await self._orchestrator.query(query, context=context)

            return {
                "query": result.query,
                "answer": result.final_answer,
                "answer_ar": result.final_answer_ar,
                "agents_used": [a.value for a in result.agents_used],
                "execution_time_ms": result.total_time_ms,
                "tasks": [
                    {
                        "agent": t.agent_role.value,
                        "result": t.result,
                        "result_ar": t.result_ar,
                        "confidence": t.confidence,
                    }
                    for t in result.tasks_completed
                ],
            }

        except Exception as e:
            logger.error("Crew query failed", error=str(e))
            return self._fallback_response(query)

    def get_available_agents(self) -> list[dict[str, str]]:
        """
        Get list of available agent roles.
        الحصول على قائمة أدوار الوكلاء المتاحة
        """
        if not self._orchestrator:
            return [
                {"role": "crop_advisor", "goal": "Provide crop management advice"},
                {"role": "irrigation_expert", "goal": "Optimize irrigation"},
                {"role": "disease_diagnostician", "goal": "Diagnose crop diseases"},
            ]

        return self._orchestrator.get_available_agents()

    def _fallback_response(self, query: str) -> dict[str, Any]:
        """Generate fallback response when crew not available."""
        # Simple rule-based response
        query_lower = query.lower()

        if any(kw in query_lower for kw in ["ري", "water", "irrigation"]):
            answer = (
                "For irrigation advice, please check your soil moisture levels. "
                "Typical wheat requires 500-600mm total water during the growing season."
            )
            answer_ar = (
                "للحصول على نصائح الري، يرجى التحقق من مستويات رطوبة التربة. "
                "يحتاج القمح عادة إلى 500-600 مم من المياه خلال موسم النمو."
            )
        elif any(kw in query_lower for kw in ["مرض", "disease", "yellow"]):
            answer = (
                "For disease diagnosis, please provide an image of the affected plant. "
                "Yellowing can indicate nitrogen deficiency or fungal infection."
            )
            answer_ar = (
                "لتشخيص المرض، يرجى تقديم صورة للنبات المصاب. "
                "يمكن أن يشير الاصفرار إلى نقص النيتروجين أو العدوى الفطرية."
            )
        else:
            answer = (
                "I'm here to help with your agricultural questions. "
                "Please describe your crop and the issue you're facing."
            )
            answer_ar = (
                "أنا هنا للمساعدة في أسئلتك الزراعية. يرجى وصف محصولك والمشكلة التي تواجهها."
            )

        return {
            "query": query,
            "answer": answer,
            "answer_ar": answer_ar,
            "agents_used": ["fallback"],
            "execution_time_ms": 0,
            "tasks": [],
        }
