"""
RAG (Retrieval-Augmented Generation) Module
وحدة RAG (التوليد المعزز بالاسترجاع)

Provides knowledge retrieval capabilities for agents.
توفر قدرات استرجاع المعرفة للوكلاء.
"""

from .embeddings import EmbeddingsManager
from .retriever import KnowledgeRetriever

__all__ = [
    "EmbeddingsManager",
    "KnowledgeRetriever",
]
