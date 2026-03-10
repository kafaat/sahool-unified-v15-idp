"""
Tests for Async Knowledge Ingestion Pipeline
=============================================
اختبارات خط أنابيب الاستيعاب غير المتزامن
"""

from __future__ import annotations

import asyncio

import pytest

from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline
from shared.ai.knowledge.ingestion.pipeline import BatchIngestionReport, IngestionResult


def _run(coro):
    """Helper to run async coroutines in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestAsyncKnowledgeIngestionPipeline:
    """Tests for async pipeline wrapper."""

    @pytest.fixture
    def pipeline(self) -> AsyncKnowledgeIngestionPipeline:
        return AsyncKnowledgeIngestionPipeline(max_workers=2)

    @pytest.mark.unit
    def test_ingest_text_async(self, pipeline: AsyncKnowledgeIngestionPipeline):
        """Async text ingestion works."""
        result = _run(
            pipeline.ingest_text(
                "# Wheat Guide\n\nWheat is a major crop.",
                title="Wheat Guide",
            )
        )
        assert isinstance(result, IngestionResult)
        assert result.success is True

    @pytest.mark.unit
    def test_ingest_text_with_arabic(self, pipeline: AsyncKnowledgeIngestionPipeline):
        """Async ingestion of Arabic content."""
        text = """---
title: دليل القمح
---

# دليل ري القمح

القمح يحتاج إلى ري منتظم خلال مرحلة التفريع.
"""
        result = _run(pipeline.ingest_text(text, title="Wheat AR"))
        assert isinstance(result, IngestionResult)

    @pytest.mark.unit
    def test_context_manager(self):
        """Pipeline supports async context manager."""

        async def _test():
            async with AsyncKnowledgeIngestionPipeline() as pipeline:
                result = await pipeline.ingest_text("Test content", title="Test")
                return result

        result = _run(_test())
        assert isinstance(result, IngestionResult)

    @pytest.mark.unit
    def test_concurrent_ingestion(self, pipeline: AsyncKnowledgeIngestionPipeline):
        """Multiple concurrent ingestions work."""

        async def _test():
            tasks = [pipeline.ingest_text(f"Content about topic {i}", title=f"Doc {i}") for i in range(5)]
            return await asyncio.gather(*tasks)

        results = _run(_test())
        assert len(results) == 5
        assert all(isinstance(r, IngestionResult) for r in results)

    @pytest.mark.unit
    def test_pipeline_creation(self):
        """Pipeline creates without errors."""
        p = AsyncKnowledgeIngestionPipeline(max_workers=1)
        assert p is not None

    @pytest.mark.unit
    def test_pipeline_with_kwargs(self):
        """Pipeline accepts forwarded kwargs."""
        p = AsyncKnowledgeIngestionPipeline(
            min_source_credibility=2,
            require_bilingual=True,
            enable_agrovoc=False,
        )
        assert p is not None
