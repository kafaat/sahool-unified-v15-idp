"""
SAHOOL Advisor Domain
AI-powered agricultural advisory: AI Engine, RAG, Context, Feedback
"""

from .ai import AdvisorAI, AdvisorResponse
from .rag import RAGService, Document
from .context import ContextBuilder, FieldContext
from .feedback import FeedbackService, AdvisorFeedback

__version__ = "16.0.0"

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
