"""
SAHOOL Retriever
Sprint 9: Document retrieval from vector store

Retrieves relevant chunks from the vector store for RAG.
"""

from __future__ import annotations

from advisor.ai.rag_models import RetrievedChunk
from advisor.rag.doc_store import VectorStore


def retrieve(
    store: VectorStore,
    *,
    collection: str,
    query: str,
    k: int = 6,
) -> list[RetrievedChunk]:
    """Retrieve relevant chunks from the vector store.

    Args:
        store: Vector store instance
        collection: Collection to search
        query: Search query
        k: Number of chunks to retrieve

    Returns:
        List of retrieved chunks with scores
    """
    results = store.search(collection=collection, query=query, limit=k)

    chunks: list[RetrievedChunk] = []
    for doc_chunk, score in results:
        chunks.append(
            RetrievedChunk(
                doc_id=doc_chunk.doc_id,
                chunk_id=doc_chunk.chunk_id,
                text=doc_chunk.text,
                score=score,
                source=str(doc_chunk.metadata.get("source", "")),
            )
        )

    return chunks


def retrieve_with_threshold(
    store: VectorStore,
    *,
    collection: str,
    query: str,
    k: int = 6,
    min_score: float = 0.3,
) -> list[RetrievedChunk]:
    """Retrieve chunks above a minimum score threshold.

    Args:
        store: Vector store instance
        collection: Collection to search
        query: Search query
        k: Maximum number of chunks to retrieve
        min_score: Minimum score threshold

    Returns:
        List of retrieved chunks with scores >= min_score
    """
    chunks = retrieve(store, collection=collection, query=query, k=k)
    return [c for c in chunks if c.score >= min_score]
