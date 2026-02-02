# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
NLP Service Integration
تكامل خدمة معالجة اللغة الطبيعية

Wraps the shared Arabic NLP module for use in the orchestrator.
"""

import sys
import os
from typing import Any

import structlog

# Add shared module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

logger = structlog.get_logger()


class NLPService:
    """
    NLP Service for Arabic text processing.
    خدمة معالجة اللغة الطبيعية للنصوص العربية
    """

    def __init__(self):
        self._processor = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the NLP processor."""
        if self._initialized:
            return True

        try:
            from shared.nlp import ArabicNLPProcessor

            self._processor = ArabicNLPProcessor()
            await self._processor.initialize()
            self._initialized = True
            logger.info("NLP service initialized")
            return True

        except ImportError as e:
            logger.warning("shared.nlp not available", error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to initialize NLP service", error=str(e))
            return False

    def process_query(self, text: str) -> dict[str, Any]:
        """
        Process a farmer query using Arabic NLP.
        معالجة استعلام المزارع باستخدام NLP العربية
        """
        if not self._initialized or not self._processor:
            return self._fallback_process(text)

        return self._processor.process(text)

    def _fallback_process(self, text: str) -> dict[str, Any]:
        """Fallback processing when NLP module not available."""
        # Simple keyword-based intent detection
        text_lower = text.lower()

        intent = "general"
        if any(kw in text_lower for kw in ["ري", "ماء", "water", "irrigation"]):
            intent = "irrigation"
        elif any(kw in text_lower for kw in ["مرض", "اصفرار", "disease", "yellow"]):
            intent = "crop_disease"
        elif any(kw in text_lower for kw in ["سماد", "fertilizer", "nitrogen"]):
            intent = "fertilizer"
        elif any(kw in text_lower for kw in ["آفة", "حشرة", "pest", "insect"]):
            intent = "pest"
        elif any(kw in text_lower for kw in ["طقس", "weather", "rain"]):
            intent = "weather"

        # Check if Arabic
        import re

        is_arabic = bool(re.search(r"[\u0600-\u06FF]", text))

        return {
            "original_text": text,
            "normalized_text": text.strip(),
            "is_arabic": is_arabic,
            "intent": {
                "primary": intent,
                "confidence": 0.7,
                "secondary": [],
            },
            "entities": [],
            "sentiment": {
                "label": "neutral",
                "score": 0.5,
                "is_urgent": any(kw in text_lower for kw in ["عاجل", "urgent", "emergency"]),
            },
        }

    def classify_intent(self, text: str) -> tuple[str, float]:
        """
        Classify the intent of a query.
        تصنيف نية الاستعلام
        """
        result = self.process_query(text)
        return result["intent"]["primary"], result["intent"]["confidence"]

    def is_urgent(self, text: str) -> bool:
        """Check if a query is urgent."""
        result = self.process_query(text)
        return result["sentiment"]["is_urgent"]
