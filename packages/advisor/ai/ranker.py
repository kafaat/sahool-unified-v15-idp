"""
SAHOOL Ranker
Sprint 9: Deterministic chunk ranking

Provides stable, deterministic ranking of retrieved chunks
to prevent flaky results in tests and production.
"""

from __future__ import annotations

from advisor.ai.rag_models import RetrievedChunk


def rank(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """Rank chunks with deterministic ordering.

    Sorting is stable and deterministic:
    1. Primary: Score (descending)
    2. Secondary: doc_id (ascending) - for tie-breaking
    3. Tertiary: chunk_id (ascending) - for tie-breaking

    This ensures the same input always produces the same output,
    preventing flaky tests and unpredictable behavior.

    Args:
        chunks: List of retrieved chunks

    Returns:
        Sorted list of chunks
    """
    return sorted(
        chunks,
        key=lambda c: (-c.score, c.doc_id, c.chunk_id),
    )


def rank_with_diversity(
    chunks: list[RetrievedChunk],
    max_per_doc: int = 2,
) -> list[RetrievedChunk]:
    """Rank chunks with document diversity constraint.

    Limits chunks from the same document to promote diversity
    in the retrieved context.

    Args:
        chunks: List of retrieved chunks
        max_per_doc: Maximum chunks per document

    Returns:
        Ranked and diversified list of chunks
    """
    ranked = rank(chunks)

    doc_counts: dict[str, int] = {}
    diversified: list[RetrievedChunk] = []

    for chunk in ranked:
        current = doc_counts.get(chunk.doc_id, 0)
        if current < max_per_doc:
            diversified.append(chunk)
            doc_counts[chunk.doc_id] = current + 1

    return diversified


def top_k(chunks: list[RetrievedChunk], k: int) -> list[RetrievedChunk]:
    """Get top k ranked chunks.

    Args:
        chunks: List of retrieved chunks
        k: Number of chunks to return

    Returns:
        Top k chunks after ranking
    """
    return rank(chunks)[:k]
