"""
SAHOOL RAG Service
Retrieval-Augmented Generation service
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .models import Document, DocumentChunk, SearchResult


class RAGService:
    """Service for RAG operations"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, DocumentChunk] = {}

    def add_document(
        self,
        title: str,
        content: str,
        source: str,
        category: str,
        tenant_id: Optional[str] = None,
        title_ar: Optional[str] = None,
        content_ar: Optional[str] = None,
    ) -> Document:
        """Add a document to the knowledge base"""
        document = Document.create(
            title=title,
            content=content,
            source=source,
            category=category,
            tenant_id=tenant_id,
            title_ar=title_ar,
            content_ar=content_ar,
        )

        # Create chunks
        chunks = self._create_chunks(document, content, content_ar)
        document.chunks = chunks

        # Store document and chunks
        self._documents[document.id] = document
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

        return document

    def _create_chunks(
        self,
        document: Document,
        content: str,
        content_ar: Optional[str],
    ) -> list[DocumentChunk]:
        """Split content into chunks"""
        chunks = []
        words = content.split()
        chunk_index = 0

        i = 0
        while i < len(words):
            chunk_words = words[i : i + self.chunk_size]
            chunk_content = " ".join(chunk_words)

            chunk = DocumentChunk(
                id=str(uuid4()),
                document_id=document.id,
                content=chunk_content,
                content_ar=None,  # Arabic chunking would need separate handling
                chunk_index=chunk_index,
                metadata={"category": document.category},
            )
            chunks.append(chunk)

            i += self.chunk_size - self.chunk_overlap
            chunk_index += 1

        return chunks

    def search(
        self,
        query: str,
        tenant_id: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Search for relevant document chunks.

        In production, this would use vector similarity search.
        This is a simple keyword-based placeholder.
        """
        results = []
        query_words = set(query.lower().split())

        for chunk in self._chunks.values():
            # Get parent document
            document = self._documents.get(chunk.document_id)
            if not document:
                continue

            # Filter by tenant (include global documents)
            if tenant_id and document.tenant_id and document.tenant_id != tenant_id:
                continue

            # Filter by category
            if category and document.category != category:
                continue

            # Simple keyword matching (placeholder for vector search)
            chunk_words = set(chunk.content.lower().split())
            overlap = len(query_words & chunk_words)

            if overlap > 0:
                score = overlap / len(query_words)
                results.append(
                    SearchResult(
                        chunk=chunk,
                        document=document,
                        score=score,
                    )
                )

        # Sort by score and return top-k
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self._documents.get(document_id)

    def list_documents(
        self,
        tenant_id: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list[Document]:
        """List documents"""
        documents = list(self._documents.values())

        if tenant_id:
            documents = [
                d for d in documents if d.tenant_id is None or d.tenant_id == tenant_id
            ]

        if category:
            documents = [d for d in documents if d.category == category]

        return documents

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks"""
        document = self._documents.get(document_id)
        if not document:
            return False

        # Delete chunks
        for chunk in document.chunks:
            self._chunks.pop(chunk.id, None)

        # Delete document
        del self._documents[document_id]
        return True
