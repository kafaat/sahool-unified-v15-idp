"""
SAHOOL RAG Models
Data models for RAG system
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class DocumentChunk:
    """A chunk of a document for embedding"""

    id: str
    document_id: str
    content: str
    content_ar: Optional[str]
    chunk_index: int
    embedding: Optional[list[float]] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "content_ar": self.content_ar,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
        }


@dataclass
class Document:
    """Knowledge base document"""

    id: str
    tenant_id: Optional[str]  # None for global documents
    title: str
    title_ar: Optional[str]
    content: str
    content_ar: Optional[str]
    source: str
    category: str
    chunks: list[DocumentChunk]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        source: str,
        category: str,
        tenant_id: Optional[str] = None,
        title_ar: Optional[str] = None,
        content_ar: Optional[str] = None,
    ) -> Document:
        """Factory method to create a new document"""
        now = datetime.now(timezone.utc)
        doc_id = str(uuid4())

        return cls(
            id=doc_id,
            tenant_id=tenant_id,
            title=title,
            title_ar=title_ar,
            content=content,
            content_ar=content_ar,
            source=source,
            category=category,
            chunks=[],  # Chunks created separately
            created_at=now,
            updated_at=now,
        )

    def to_dict(self, include_chunks: bool = False) -> dict:
        data = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "source": self.source,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_chunks:
            data["chunks"] = [c.to_dict() for c in self.chunks]
        return data


@dataclass
class SearchResult:
    """RAG search result"""

    chunk: DocumentChunk
    document: Document
    score: float

    def to_dict(self) -> dict:
        return {
            "chunk": self.chunk.to_dict(),
            "document": self.document.to_dict(),
            "score": self.score,
        }
