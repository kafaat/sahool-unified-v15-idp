"""
SAHOOL Legacy Advisor Compatibility
Re-exports from advisor

DEPRECATED: Use advisor module instead
"""

import warnings

warnings.warn(
    "legacy.advisor is deprecated. Use advisor module instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from advisor import (
    AdvisorAI,
    AdvisorFeedback,
    AdvisorResponse,
    ContextBuilder,
    Document,
    FeedbackService,
    FieldContext,
    RAGService,
)

__all__ = [
    "AdvisorAI",
    "AdvisorResponse",
    "RAGService",
    "Document",
    "ContextBuilder",
    "FieldContext",
    "FeedbackService",
    "AdvisorFeedback",
]
