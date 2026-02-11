"""
Copilot RAG Module
وحدة RAG لـ Copilot

Retrieval-Augmented Generation with Qdrant vector search.
"""

from .embeddings import (
    EmbeddingService,
    get_embedding_service,
)
from .service import (
    CopilotRAGService,
    get_rag_service,
)

__all__ = [
    "CopilotRAGService",
    "get_rag_service",
    "EmbeddingService",
    "get_embedding_service",
]
