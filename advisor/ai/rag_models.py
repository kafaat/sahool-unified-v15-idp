"""
SAHOOL RAG Pipeline Models
Sprint 9: Typed contracts for RAG operations
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk retrieved from the vector store"""

    doc_id: str
    chunk_id: str
    text: str
    score: float
    source: str


@dataclass(frozen=True)
class RagRequest:
    """Request for RAG-based answer generation"""

    tenant_id: str
    field_id: str
    question: str
    locale: str = "ar"


@dataclass(frozen=True)
class RagResponse:
    """Response from RAG pipeline"""

    answer: str
    confidence: float
    sources: list[str]
    explanation: str
    mode: Literal["rag", "fallback"]
