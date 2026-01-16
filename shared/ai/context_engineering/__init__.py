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
    ContextCompressor,
    CompressionResult,
    CompressionStrategy,
)
from .memory import (
    FarmMemory,
    MemoryEntry,
    MemoryConfig,
)
from .evaluation import (
    RecommendationEvaluator,
    EvaluationResult,
    EvaluationCriteria,
)
from .metrics import (
    AIMetricsRegistry,
    get_ai_metrics_registry,
    track_compression,
    track_memory_operation,
    track_evaluation,
    record_memory_entry_stored,
    record_memory_eviction,
    record_memory_ttl_expiration,
    update_memory_usage,
    track_operation_async,
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
