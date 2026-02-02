# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Arabic NLP Integration Module
وحدة تكامل معالجة اللغة العربية الطبيعية

Provides Arabic-first NLP capabilities using AraBERT and other models.
"""

from .arabic_nlp import (
    ArabicNLPProcessor,
    ArabicTextPreprocessor,
    IntentClassifier,
    EntityExtractor,
    SentimentAnalyzer,
)

__all__ = [
    "ArabicNLPProcessor",
    "ArabicTextPreprocessor",
    "IntentClassifier",
    "EntityExtractor",
    "SentimentAnalyzer",
]
