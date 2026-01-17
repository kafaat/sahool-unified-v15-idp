"""
SAHOOL AI Module
================
وحدة الذكاء الاصطناعي لمنصة سهول

AI utilities and context engineering for the SAHOOL agricultural platform.
Provides context compression, memory management, and recommendation evaluation.

Modules:
    - context_engineering: Context compression, memory, and evaluation

Author: SAHOOL Platform Team
Updated: January 2025
"""

from .context_engineering import (
    # Compression
    ContextCompressor,
    CompressionResult,
    CompressionStrategy,
    # Memory
    FarmMemory,
    MemoryEntry,
    MemoryConfig,
    # Evaluation
    RecommendationEvaluator,
    EvaluationResult,
    EvaluationCriteria,
)

__version__ = "1.0.0"

__all__ = [
    # Compression
    "ContextCompressor",
    "CompressionResult",
    "CompressionStrategy",
    # Memory
    "FarmMemory",
    "MemoryEntry",
    "MemoryConfig",
    # Evaluation
    "RecommendationEvaluator",
    "EvaluationResult",
    "EvaluationCriteria",
]
