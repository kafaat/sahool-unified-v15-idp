"""
SAHOOL Vector Store Protocol
Sprint 9: Abstract vector store interface

Defines the contract for vector stores. Implementations (Qdrant, Pinecone, etc.)
must implement this protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class DocChunk:
    """A document chunk for vector storage"""

    doc_id: str
    chunk_id: str
    text: str
    metadata: dict[str, Any]


class VectorStore(Protocol):
    """Protocol for vector store implementations.

    Any class implementing these methods can be used as a vector store.
    """

    def upsert_chunks(self, collection: str, chunks: list[DocChunk]) -> None:
        """Insert or update chunks in the collection.

        Args:
            collection: Collection name
            chunks: List of document chunks to upsert
        """
        ...

    def search(
        self, collection: str, query: str, limit: int
    ) -> list[tuple[DocChunk, float]]:
        """Search for similar chunks.

        Args:
            collection: Collection name
            query: Search query text
            limit: Maximum number of results

        Returns:
            List of (chunk, score) tuples, sorted by score descending
        """
        ...


class InMemoryVectorStore:
    """In-memory vector store for testing.

    Uses simple keyword matching instead of embeddings.
    NOT for production use.
    """

    def __init__(self) -> None:
        self._collections: dict[str, list[DocChunk]] = {}

    def upsert_chunks(self, collection: str, chunks: list[DocChunk]) -> None:
        if collection not in self._collections:
            self._collections[collection] = []

        # Simple upsert: replace existing chunks with same IDs
        existing_ids = {
            f"{c.doc_id}:{c.chunk_id}"
            for c in self._collections[collection]
        }
        for chunk in chunks:
            chunk_key = f"{chunk.doc_id}:{chunk.chunk_id}"
            if chunk_key in existing_ids:
                self._collections[collection] = [
                    c for c in self._collections[collection]
                    if f"{c.doc_id}:{c.chunk_id}" != chunk_key
                ]
        self._collections[collection].extend(chunks)

    def search(
        self, collection: str, query: str, limit: int
    ) -> list[tuple[DocChunk, float]]:
        if collection not in self._collections:
            return []

        # Simple keyword matching for testing
        query_words = set(query.lower().split())
        results: list[tuple[DocChunk, float]] = []

        for chunk in self._collections[collection]:
            chunk_words = set(chunk.text.lower().split())
            overlap = len(query_words & chunk_words)
            if overlap > 0 or not query_words:
                score = overlap / max(len(query_words), 1)
                results.append((chunk, score))

        # Sort by score descending
        results.sort(key=lambda x: -x[1])
        return results[:limit]

    def clear(self, collection: str) -> None:
        """Clear all chunks from a collection."""
        if collection in self._collections:
            self._collections[collection] = []

    def count(self, collection: str) -> int:
        """Get number of chunks in a collection."""
        return len(self._collections.get(collection, []))
