"""
SAHOOL RAG Pipeline
Sprint 9: Single entry point for RAG operations

This is the main orchestration layer that combines:
- Retrieval from vector store
- Ranking of results
- Prompt rendering
- LLM generation
"""

from __future__ import annotations

import logging
from typing import Optional

from advisor.ai.llm_client import LlmClient, LlmError
from advisor.ai.prompt_engine import render_prompt
from advisor.ai.rag_models import RagRequest, RagResponse, RetrievedChunk
from advisor.ai.ranker import rank
from advisor.ai.retriever import retrieve
from advisor.rag.doc_store import VectorStore


logger = logging.getLogger(__name__)


def _chunks_to_text(chunks: list[RetrievedChunk]) -> str:
    """Convert chunks to formatted text for prompt.

    Args:
        chunks: List of retrieved chunks

    Returns:
        Formatted string for prompt injection
    """
    if not chunks:
        return "(لا يوجد مقتطفات)"

    lines: list[str] = []
    for chunk in chunks:
        lines.append(f"[{chunk.doc_id}/{chunk.chunk_id}] {chunk.text}")
    return "\n".join(lines)


def run_rag(
    *,
    req: RagRequest,
    store: VectorStore,
    llm: LlmClient,
    field_context: str,
    collection: str,
    top_k: int = 6,
    min_chunk_score: float = 0.3,
) -> RagResponse:
    """Run the RAG pipeline.

    This is the main entry point for RAG-based answer generation.

    Args:
        req: RAG request with question and metadata
        store: Vector store for retrieval
        llm: LLM client for generation
        field_context: Pre-built field context string
        collection: Collection name in vector store
        top_k: Number of chunks to retrieve
        min_chunk_score: Minimum score for chunks to be considered relevant

    Returns:
        RagResponse with answer, confidence, and metadata
        
    Raises:
        LlmError: If LLM generation fails
        ValueError: If inputs are invalid
    """
    # Input validation
    if not req.question or not req.question.strip():
        raise ValueError("Question cannot be empty")
    
    if top_k < 1 or top_k > 20:
        raise ValueError(f"top_k must be between 1 and 20, got {top_k}")

    try:
        # Step 1: Retrieve relevant chunks
        logger.info(f"Retrieving top {top_k} chunks for query: {req.question[:100]}...")
        raw_chunks = retrieve(store, collection=collection, query=req.question, k=top_k)

        # Step 2: Rank chunks deterministically
        chunks = rank(raw_chunks)
        
        # Step 2.5: Filter low-scoring chunks
        chunks = [c for c in chunks if c.score >= min_chunk_score]
        logger.info(f"Retrieved {len(chunks)} chunks above threshold {min_chunk_score}")

        # Step 3: Format chunks for prompt
        retrieved_text = _chunks_to_text(chunks)

        # Step 4: Render the prompt
        prompt = render_prompt(
            question=req.question,
            field_context=field_context,
            retrieved_chunks=retrieved_text,
        )

        # Step 5: Handle fallback case (no relevant chunks)
        if not chunks:
            logger.warning("No relevant chunks found, using fallback response")
            fallback_text = (
                "المعلومات غير كافية لإعطاء توصية دقيقة. "
                "زودني بنوع المحصول، عمره، برنامج الري، وآخر تحليل تربة."
            )
            return RagResponse(
                answer=fallback_text,
                confidence=0.35,
                sources=[],
                explanation="No retrieved chunks; fallback response used.",
                mode="fallback",
            )

        # Step 6: Generate response from LLM with error handling
        try:
            logger.info("Generating LLM response...")
            llm_response = llm.generate(prompt)
        except LlmError as e:
            logger.error(f"LLM generation failed: {e}")
            # Return fallback on LLM failure
            fallback_text = (
                "عذراً، حدث خطأ في توليد التوصية. "
                "يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني."
            )
            return RagResponse(
                answer=fallback_text,
                confidence=0.2,
                sources=[],
                explanation=f"LLM generation failed: {str(e)}",
                mode="error",
            )

        # Step 7: Calculate confidence based on retrieval scores
        # Heuristic: base confidence + average retrieval score bonus
        avg_score = sum(c.score for c in chunks) / len(chunks)
        confidence = max(0.0, min(1.0, 0.5 + (avg_score / 2.0)))
        
        logger.info(f"RAG completed with confidence: {confidence:.2f}")

        # Step 8: Extract unique sources
        sources = sorted({c.doc_id for c in chunks})

        return RagResponse(
            answer=llm_response.text.strip(),
            confidence=confidence,
            sources=sources,
            explanation="RAG used with retrieved evidence and deterministic ranking.",
            mode="rag",
        )
        
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}", exc_info=True)
        # Return error response instead of raising
        return RagResponse(
            answer="عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.",
            confidence=0.0,
            sources=[],
            explanation=f"Pipeline error: {str(e)}",
            mode="error",
        )


def run_rag_with_fallback(
    *,
    req: RagRequest,
    store: VectorStore,
    llm: LlmClient,
    field_context: str,
    collection: str,
    min_confidence: float = 0.4,
) -> RagResponse:
    """Run RAG with automatic fallback for low confidence.

    If RAG confidence is below threshold, adds a disclaimer.

    Args:
        req: RAG request
        store: Vector store
        llm: LLM client
        field_context: Field context string
        collection: Collection name
        min_confidence: Minimum confidence threshold

    Returns:
        RagResponse, potentially with fallback disclaimer
    """
    response = run_rag(
        req=req,
        store=store,
        llm=llm,
        field_context=field_context,
        collection=collection,
    )

    if response.confidence < min_confidence and response.mode == "rag":
        # Add low confidence disclaimer
        disclaimer = "\n\n⚠️ ملاحظة: مستوى الثقة في هذه الإجابة منخفض. يرجى التحقق من المصادر."
        return RagResponse(
            answer=response.answer + disclaimer,
            confidence=response.confidence,
            sources=response.sources,
            explanation=f"Low confidence ({response.confidence:.2f}); disclaimer added.",
            mode=response.mode,
        )

    return response
