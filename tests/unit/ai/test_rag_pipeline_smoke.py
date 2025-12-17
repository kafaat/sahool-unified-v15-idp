"""
SAHOOL RAG Pipeline Smoke Tests
Sprint 9: Integration smoke tests without external dependencies
"""

import pytest
import sys
sys.path.insert(0, ".")

from advisor.ai.llm_client import LlmClient, LlmResponse
from advisor.ai.rag_models import RagRequest, RetrievedChunk
from advisor.ai.rag_pipeline import run_rag, _chunks_to_text
from advisor.rag.doc_store import DocChunk, InMemoryVectorStore


class FakeLLM(LlmClient):
    """Fake LLM for testing"""

    def __init__(self, response: str = "نصيحة زراعية"):
        self._response = response

    def generate(self, prompt: str) -> LlmResponse:
        return LlmResponse(text=self._response)


class TestRagPipeline:
    """Test RAG pipeline end-to-end"""

    def test_rag_returns_answer(self):
        """RAG pipeline returns valid response"""
        store = InMemoryVectorStore()
        store.upsert_chunks(
            "kb",
            [DocChunk("doc1", "0", "irrigation best practices", {"source": "manual"})],
        )

        req = RagRequest(
            tenant_id="t1",
            field_id="f1",
            question="irrigation practices",
        )

        resp = run_rag(
            req=req,
            store=store,
            llm=FakeLLM("ننصح بالري في الصباح الباكر"),
            field_context="حقل القمح - 50 هكتار",
            collection="kb",
        )

        assert resp.mode == "rag"
        assert resp.answer == "ننصح بالري في الصباح الباكر"
        assert "doc1" in resp.sources

    def test_rag_fallback_when_no_chunks(self):
        """Returns fallback when no chunks found"""
        store = InMemoryVectorStore()  # Empty store

        req = RagRequest(
            tenant_id="t1",
            field_id="f1",
            question="something completely unrelated xyz",
        )

        resp = run_rag(
            req=req,
            store=store,
            llm=FakeLLM(),
            field_context="CTX",
            collection="kb",
        )

        assert resp.mode == "fallback"
        assert resp.confidence < 0.5
        assert "غير كافية" in resp.answer

    def test_confidence_based_on_scores(self):
        """Confidence reflects retrieval scores"""
        store = InMemoryVectorStore()
        # High overlap query
        store.upsert_chunks(
            "kb",
            [
                DocChunk("doc1", "0", "wheat irrigation timing", {"source": "kb"}),
                DocChunk("doc2", "0", "wheat fertilizer schedule", {"source": "kb"}),
            ],
        )

        req = RagRequest(
            tenant_id="t1",
            field_id="f1",
            question="wheat irrigation",
        )

        resp = run_rag(
            req=req,
            store=store,
            llm=FakeLLM(),
            field_context="CTX",
            collection="kb",
        )

        # Should have reasonable confidence with matching chunks
        assert resp.confidence > 0


class TestChunksToText:
    """Test chunk formatting"""

    def test_empty_chunks(self):
        """Empty chunks return placeholder"""
        text = _chunks_to_text([])
        assert "(لا يوجد مقتطفات)" in text

    def test_formats_chunk_correctly(self):
        """Chunks are formatted with doc/chunk IDs"""
        chunks = [
            RetrievedChunk("doc1", "0", "text content", 0.9, "source"),
        ]
        text = _chunks_to_text(chunks)
        assert "[doc1/0]" in text
        assert "text content" in text

    def test_multiple_chunks(self):
        """Multiple chunks are joined with newlines"""
        chunks = [
            RetrievedChunk("doc1", "0", "first", 0.9, "s"),
            RetrievedChunk("doc2", "0", "second", 0.8, "s"),
        ]
        text = _chunks_to_text(chunks)
        assert "[doc1/0]" in text
        assert "[doc2/0]" in text
        assert "first" in text
        assert "second" in text
