"""
SAHOOL AI Context Engineering Module
=====================================
وحدة هندسة السياق للذكاء الاصطناعي

Comprehensive context engineering for AI interactions in the SAHOOL platform.
Implements context compression, farm memory management, and recommendation evaluation.

Features:
- Context compression with Arabic text support
- Tenant-isolated farm memory with sliding window
- LLM-as-Judge recommendation evaluation
- Token estimation and optimization

Based on modern context engineering best practices for agricultural AI systems.

المميزات:
- ضغط السياق مع دعم النص العربي
- ذاكرة المزرعة المعزولة لكل مستأجر مع نافذة منزلقة
- تقييم التوصيات باستخدام نموذج اللغة كحكم
- تقدير وتحسين الرموز

Author: SAHOOL Platform Team
Updated: January 2025
"""

from .compression import (
    CompressionResult,
    CompressionStrategy,
    ContextCompressor,
)
from .evaluation import (
    EvaluationCriteria,
    EvaluationResult,
    RecommendationEvaluator,
)
from .memory import (
    FarmMemory,
    MemoryConfig,
    MemoryEntry,
)
from .metrics import (
    AIMetricsRegistry,
    get_ai_metrics_registry,
    record_memory_entry_stored,
    record_memory_eviction,
    record_memory_ttl_expiration,
    track_compression,
    track_evaluation,
    track_memory_operation,
    track_operation_async,
    update_memory_usage,
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
    # Metrics
    "AIMetricsRegistry",
    "get_ai_metrics_registry",
    "track_compression",
    "track_memory_operation",
    "track_evaluation",
    "record_memory_entry_stored",
    "record_memory_eviction",
    "record_memory_ttl_expiration",
    "update_memory_usage",
    "track_operation_async",
]
