"""
Tests for remaining knowledge base gap implementations:
- GAP-12: NATS event publishing
- GAP-17: URL ingestion
- GAP-18: CRAG semantic similarity
- Security: Path traversal protection
- Security: File size limits
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


def _run(coro):
    """Helper to run async coroutines in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-12: NATS Event Publisher Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestKnowledgeEventPublisher:
    """Tests for NATS event publishing integration."""

    def test_import_event_publisher(self):
        """KnowledgeEventPublisher should be importable from knowledge package."""
        from shared.ai.knowledge import KnowledgeEventPublisher

        publisher = KnowledgeEventPublisher()
        assert publisher is not None

    def test_publisher_disabled_without_nats(self):
        """Publisher should be disabled when no NATS client provided."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        publisher = KnowledgeEventPublisher(nc=None)
        assert publisher.enabled is False

    def test_publisher_enabled_with_nats(self):
        """Publisher should be enabled when NATS client is provided."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)
        assert publisher.enabled is True

    def test_document_ingested_event(self):
        """Should publish document_ingested event."""
        from shared.ai.knowledge.events import (
            KnowledgeEventPublisher,
            SUBJECT_DOCUMENT_INGESTED,
        )

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)

        _run(publisher.document_ingested(
            document_id="doc-001",
            collection="crop_knowledge",
            domain="crops",
            source_credibility=4,
            chunks_count=3,
        ))

        mock_nc.publish.assert_called_once()
        call_args = mock_nc.publish.call_args
        assert call_args[0][0] == SUBJECT_DOCUMENT_INGESTED

    def test_document_verified_event(self):
        """Should publish document_verified event."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)

        _run(publisher.document_verified(
            document_id="doc-002",
            status="approved",
            confidence_score=0.92,
            layers_passed=["structural", "semantic", "safety"],
        ))

        mock_nc.publish.assert_called_once()

    def test_document_expired_event(self):
        """Should publish document_expired event."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)

        _run(publisher.document_expired(
            document_id="doc-003",
            title="Old Pesticide Guide",
            domain="pest_disease",
            days_past_expiry=15,
        ))

        mock_nc.publish.assert_called_once()

    def test_collection_populated_event(self):
        """Should publish collection_populated event."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)

        _run(publisher.collection_populated(
            collection="crop_knowledge",
            total_files=19,
            succeeded=18,
            failed=1,
        ))

        mock_nc.publish.assert_called_once()

    def test_ingestion_failed_event(self):
        """Should publish ingestion_failed event."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)

        _run(publisher.ingestion_failed(
            document_id="doc-004",
            source_path="/path/to/file.md",
            errors=["Validation failed"],
        ))

        mock_nc.publish.assert_called_once()

    def test_publish_skipped_without_client(self):
        """Should not raise when NATS client is None."""
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        publisher = KnowledgeEventPublisher(nc=None)

        # Should not raise
        _run(publisher.document_ingested(
            document_id="doc-005",
            collection="test",
            domain="crops",
        ))

    def test_event_payload_contains_timestamp(self):
        """Published event payload should include a timestamp."""
        import json

        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        publisher = KnowledgeEventPublisher(nc=mock_nc)

        _run(publisher.document_ingested(
            document_id="doc-006",
            collection="soil_knowledge",
            domain="soil",
        ))

        payload_bytes = mock_nc.publish.call_args[0][1]
        payload = json.loads(payload_bytes)
        assert "timestamp" in payload
        assert "event" in payload
        assert "data" in payload

    def test_subject_constants(self):
        """All subject constants should be defined."""
        from shared.ai.knowledge.events import (
            SUBJECT_COLLECTION_POPULATED,
            SUBJECT_DOCUMENT_EXPIRED,
            SUBJECT_DOCUMENT_INGESTED,
            SUBJECT_DOCUMENT_VERIFIED,
            SUBJECT_INGESTION_FAILED,
        )

        assert SUBJECT_DOCUMENT_INGESTED == "sahool.knowledge.document_ingested"
        assert SUBJECT_DOCUMENT_VERIFIED == "sahool.knowledge.document_verified"
        assert SUBJECT_DOCUMENT_EXPIRED == "sahool.knowledge.document_expired"
        assert SUBJECT_COLLECTION_POPULATED == "sahool.knowledge.collection_populated"
        assert SUBJECT_INGESTION_FAILED == "sahool.knowledge.ingestion_failed"


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-17: URL Ingestion Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestURLExtractor:
    """Tests for URL content extraction."""

    def test_import_url_extractor(self):
        """URLExtractor should be importable from ingestion package."""
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        assert extractor is not None

    def test_invalid_scheme_rejected(self):
        """Should reject non-http/https URLs."""
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("ftp://example.com/data.csv")
        assert result.metadata.get("error")
        assert "Invalid URL scheme" in result.metadata["error"]

    def test_no_hostname_rejected(self):
        """Should reject URLs without hostname."""
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("http://")
        assert result.metadata.get("error")

    def test_httpx_not_installed_handled(self):
        """Should handle missing httpx gracefully."""
        from shared.ai.knowledge.ingestion.extractors import URLExtractor
        from unittest.mock import patch

        extractor = URLExtractor()

        # Patch the import inside the method
        with patch.dict("sys.modules", {"httpx": None}):
            result = extractor.extract("https://example.com")
            # Either succeeds or gives import error - both acceptable
            assert result is not None

    def test_url_extractor_source_type(self):
        """Extracted content should have source_type 'url'."""
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("https://invalid-domain-that-does-not-exist.xyz/page")
        assert result.source_type == "url"
        assert result.source_path == "https://invalid-domain-that-does-not-exist.xyz/page"


@pytest.mark.unit
class TestPipelineURLIngestion:
    """Tests for URL ingestion via the pipeline."""

    def test_ingest_url_method_exists(self):
        """Pipeline should have ingest_url method."""
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
        assert hasattr(pipeline, "ingest_url")
        assert callable(pipeline.ingest_url)


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-18: CRAG Semantic Similarity Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCRAGSemanticSimilarity:
    """Tests for optional semantic similarity in CRAG engine."""

    def test_crag_accepts_semantic_provider(self):
        """CRAG engine should accept semantic_provider parameter."""
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine(semantic_provider=None)
        assert engine is not None
        assert engine._semantic_provider is None

    def test_crag_with_mock_semantic_provider(self):
        """CRAG should use semantic provider when available."""
        from shared.ai.knowledge.corrective_retrieval import (
            CorrectiveRetrievalEngine,
            SemanticSimilarityProvider,
        )

        # Create mock provider
        mock_provider = MagicMock(spec=SemanticSimilarityProvider)
        mock_provider.similarity.return_value = 0.85

        engine = CorrectiveRetrievalEngine(semantic_provider=mock_provider)

        chunks = [
            {
                "content": "Wheat requires adequate nitrogen during tillering stage.",
                "metadata": {"domain": "crops", "source_credibility": 4},
            },
        ]

        result = engine.evaluate_and_refine(
            query="wheat nitrogen needs during growth",
            retrieved_chunks=chunks,
            query_domain="crops",
        )

        assert result is not None
        # Semantic provider should have been called
        assert mock_provider.similarity.called

    def test_crag_keyword_fallback_on_semantic_error(self):
        """CRAG should fall back to keywords when semantic provider fails."""
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        # Provider that raises an exception
        mock_provider = MagicMock()
        mock_provider.similarity.side_effect = RuntimeError("Model not loaded")

        engine = CorrectiveRetrievalEngine(semantic_provider=mock_provider)

        chunks = [
            {
                "content": "Wheat irrigation scheduling for arid regions.",
                "metadata": {"domain": "crops"},
            },
        ]

        # Should not raise - falls back to keyword-based scoring
        result = engine.evaluate_and_refine(
            query="wheat irrigation",
            retrieved_chunks=chunks,
            query_domain="crops",
        )

        assert result is not None

    def test_crag_without_semantic_uses_keywords(self):
        """Without semantic provider, CRAG should use keyword scoring."""
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine(semantic_provider=None)

        chunks = [
            {
                "content": "Wheat is a major cereal crop grown in arid regions.",
                "metadata": {"domain": "crops"},
            },
        ]

        result = engine.evaluate_and_refine(
            query="wheat cultivation arid",
            retrieved_chunks=chunks,
            query_domain="crops",
        )

        assert result is not None
        assert result.evaluation.relevance_score >= 0.0

    def test_semantic_similarity_provider_class_exists(self):
        """SemanticSimilarityProvider should be importable."""
        from shared.ai.knowledge.corrective_retrieval import SemanticSimilarityProvider

        assert SemanticSimilarityProvider is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Security: Path Traversal Protection Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPathTraversalProtection:
    """Tests for path traversal protection in the pipeline."""

    def test_allowed_base_dirs_blocks_external_path(self):
        """Pipeline should block files outside allowed directories."""
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            allowed_dir = Path(tmpdir) / "allowed"
            allowed_dir.mkdir()
            blocked_dir = Path(tmpdir) / "blocked"
            blocked_dir.mkdir()

            # Create a file in blocked dir
            blocked_file = blocked_dir / "secret.md"
            blocked_file.write_text("# Secret Data\nShould not be ingested.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=[str(allowed_dir)],
            )

            result = pipeline.ingest_file(str(blocked_file))
            assert not result.success
            assert any("outside allowed directories" in e for e in result.errors)

    def test_allowed_base_dirs_permits_allowed_path(self):
        """Pipeline should allow files in allowed directories."""
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            allowed_dir = Path(tmpdir) / "allowed"
            allowed_dir.mkdir()

            # Create a file in allowed dir
            allowed_file = allowed_dir / "wheat.md"
            allowed_file.write_text("# Wheat Guide\nWheat is a major cereal crop.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=[str(allowed_dir)],
            )

            result = pipeline.ingest_file(str(allowed_file))
            assert result.success

    def test_no_restriction_when_allowed_dirs_none(self):
        """Pipeline should allow any path when allowed_base_dirs is None."""
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test\nContent here.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=None,
            )

            result = pipeline.ingest_file(str(test_file))
            assert result.success


# ═══════════════════════════════════════════════════════════════════════════════
# Security: File Size Limit Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFileSizeLimits:
    """Tests for file size limits in extractors."""

    def test_markdown_extractor_has_max_size(self):
        """MarkdownExtractor should accept max_file_size parameter."""
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        extractor = MarkdownExtractor(max_file_size=1024)
        assert extractor._max_file_size == 1024

    def test_pdf_extractor_has_max_size(self):
        """PDFExtractor should accept max_file_size parameter."""
        from shared.ai.knowledge.ingestion.extractors import PDFExtractor

        extractor = PDFExtractor(max_file_size=1024)
        assert extractor._max_file_size == 1024

    def test_markdown_rejects_oversized_file(self):
        """MarkdownExtractor should reject files exceeding max size."""
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            # Write content larger than our tiny limit
            f.write("# Big File\n" + "x" * 2000)
            f.flush()

            extractor = MarkdownExtractor(max_file_size=100)  # 100 bytes limit
            result = extractor.extract(f.name)

            assert result.metadata.get("error")
            assert "exceeds limit" in result.metadata["error"]

    def test_markdown_accepts_small_file(self):
        """MarkdownExtractor should accept files within size limit."""
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Small\nOK.")
            f.flush()

            extractor = MarkdownExtractor(max_file_size=1024 * 1024)
            result = extractor.extract(f.name)

            assert result.content  # Should have extracted content
            assert "error" not in result.metadata

    def test_default_max_file_size(self):
        """Default max file size should be 50MB."""
        from shared.ai.knowledge.ingestion.extractors import DEFAULT_MAX_FILE_SIZE_BYTES

        assert DEFAULT_MAX_FILE_SIZE_BYTES == 50 * 1024 * 1024
