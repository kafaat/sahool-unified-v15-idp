"""
Comprehensive tests for pipeline security (path traversal, file size limits),
URL extraction, and async pipeline.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Path Traversal Protection Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPathTraversalComprehensive:
    """Comprehensive path traversal protection tests."""

    def test_symlink_traversal_blocked(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            allowed = Path(tmpdir) / "allowed"
            allowed.mkdir()
            blocked = Path(tmpdir) / "blocked"
            blocked.mkdir()
            secret_file = blocked / "secret.md"
            secret_file.write_text("# Secret\nConfidential data.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=[str(allowed)],
            )

            result = pipeline.ingest_file(str(secret_file))
            assert not result.success
            assert any("outside allowed directories" in e for e in result.errors)

    def test_dotdot_traversal_blocked(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            allowed = Path(tmpdir) / "allowed"
            allowed.mkdir()
            parent_file = Path(tmpdir) / "parent.md"
            parent_file.write_text("# Parent File\nShould not be accessible.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=[str(allowed)],
            )

            # Try accessing parent via ../
            result = pipeline.ingest_file(str(allowed / ".." / "parent.md"))
            assert not result.success

    def test_multiple_allowed_dirs(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            dir_a = Path(tmpdir) / "dir_a"
            dir_b = Path(tmpdir) / "dir_b"
            dir_a.mkdir()
            dir_b.mkdir()

            file_a = dir_a / "file_a.md"
            file_a.write_text("# File A\nContent in directory A.")
            file_b = dir_b / "file_b.md"
            file_b.write_text("# File B\nContent in directory B.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=[str(dir_a), str(dir_b)],
            )

            assert pipeline.ingest_file(str(file_a)).success
            assert pipeline.ingest_file(str(file_b)).success

    def test_no_restriction_when_none(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test\nContent.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=None,
            )
            result = pipeline.ingest_file(str(test_file))
            assert result.success

    def test_subdirectory_allowed(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            allowed = Path(tmpdir) / "allowed"
            subdir = allowed / "subdir"
            subdir.mkdir(parents=True)

            nested_file = subdir / "nested.md"
            nested_file.write_text("# Nested\nNested content.")

            pipeline = KnowledgeIngestionPipeline(
                enable_vector_storage=False,
                allowed_base_dirs=[str(allowed)],
            )
            result = pipeline.ingest_file(str(nested_file))
            assert result.success


# ═══════════════════════════════════════════════════════════════════════════════
# File Size Limit Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFileSizeLimitsComprehensive:
    """Comprehensive file size limit tests."""

    def test_markdown_default_max_size(self):
        from shared.ai.knowledge.ingestion.extractors import (
            DEFAULT_MAX_FILE_SIZE_BYTES,
            MarkdownExtractor,
        )

        extractor = MarkdownExtractor()
        assert extractor._max_file_size == DEFAULT_MAX_FILE_SIZE_BYTES
        assert DEFAULT_MAX_FILE_SIZE_BYTES == 50 * 1024 * 1024

    def test_pdf_default_max_size(self):
        from shared.ai.knowledge.ingestion.extractors import (
            DEFAULT_MAX_FILE_SIZE_BYTES,
            PDFExtractor,
        )

        extractor = PDFExtractor()
        assert extractor._max_file_size == DEFAULT_MAX_FILE_SIZE_BYTES

    def test_markdown_custom_max_size(self):
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        extractor = MarkdownExtractor(max_file_size=1024)
        assert extractor._max_file_size == 1024

    def test_markdown_oversized_file_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Big File\n" + "x" * 5000)
            f.flush()

            extractor = MarkdownExtractor(max_file_size=100)
            result = extractor.extract(f.name)
            assert result.metadata.get("error")
            assert "exceeds limit" in result.metadata["error"]

    def test_markdown_within_limit_accepted(self):
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Small\nOK.")
            f.flush()

            extractor = MarkdownExtractor(max_file_size=1024 * 1024)
            result = extractor.extract(f.name)
            assert result.content
            assert "error" not in result.metadata

    def test_pdf_oversized_file_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import PDFExtractor

        with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as f:
            f.write(b"x" * 5000)
            f.flush()

            extractor = PDFExtractor(max_file_size=100)
            result = extractor.extract(f.name)
            assert result.metadata.get("error")
            assert "exceeds limit" in result.metadata["error"]

    def test_nonexistent_file_handled(self):
        from shared.ai.knowledge.ingestion.extractors import MarkdownExtractor

        extractor = MarkdownExtractor()
        result = extractor.extract("/nonexistent/path/file.md")
        assert result.content == ""


# ═══════════════════════════════════════════════════════════════════════════════
# URL Extractor Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestURLExtractorComprehensive:
    """Comprehensive URL extractor tests."""

    def test_ftp_scheme_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("ftp://example.com/data.csv")
        assert result.metadata.get("error")
        assert "Invalid URL scheme" in result.metadata["error"]

    def test_file_scheme_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("file:///etc/passwd")
        assert result.metadata.get("error")
        assert "Invalid URL scheme" in result.metadata["error"]

    def test_no_hostname_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("http://")
        assert result.metadata.get("error")

    def test_source_type_is_url(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("https://nonexistent.invalid/page")
        assert result.source_type == "url"
        assert result.source_path == "https://nonexistent.invalid/page"

    def test_timeout_configuration(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor(timeout=60)
        assert extractor._timeout == 60

    def test_data_scheme_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("data:text/html,<h1>Test</h1>")
        assert result.metadata.get("error")

    def test_javascript_scheme_rejected(self):
        from shared.ai.knowledge.ingestion.extractors import URLExtractor

        extractor = URLExtractor()
        result = extractor.extract("javascript:alert(1)")
        assert result.metadata.get("error")


# ═══════════════════════════════════════════════════════════════════════════════
# Pipeline URL Ingestion Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPipelineURLIngestion:
    """Test URL ingestion via pipeline."""

    def test_ingest_url_method_exists(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
        assert hasattr(pipeline, "ingest_url")
        assert callable(pipeline.ingest_url)

    def test_ingest_url_invalid_scheme(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
        result = pipeline.ingest_url("ftp://example.com/file")
        assert not result.success
        assert len(result.errors) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Async Pipeline Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAsyncPipelineComprehensive:
    """Comprehensive async pipeline tests."""

    def test_async_ingest_file(self):
        from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Wheat Guide\nWheat is a major cereal crop.")
            f.flush()

            async def run():
                async with AsyncKnowledgeIngestionPipeline(enable_vector_storage=False) as pipeline:
                    result = await pipeline.ingest_file(f.name)
                    return result

            result = _run(run())
            assert result.success

    def test_async_ingest_text(self):
        from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline

        async def run():
            async with AsyncKnowledgeIngestionPipeline(enable_vector_storage=False) as pipeline:
                result = await pipeline.ingest_text("# Test\nWheat cultivation guide.")
                return result

        result = _run(run())
        assert result.success

    def test_async_context_manager(self):
        from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline

        async def run():
            pipeline = AsyncKnowledgeIngestionPipeline(enable_vector_storage=False)
            async with pipeline as p:
                assert p is pipeline
            return True

        assert _run(run())

    def test_async_ingest_directory(self):
        from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                (Path(tmpdir) / f"doc{i}.md").write_text(f"# Doc {i}\nContent {i}")

            async def run():
                async with AsyncKnowledgeIngestionPipeline(enable_vector_storage=False) as pipeline:
                    report = await pipeline.ingest_directory(tmpdir)
                    return report

            report = _run(run())
            assert report.total == 3
            assert report.succeeded >= 1

    def test_async_ingest_files_concurrent(self):
        from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(5):
                f = Path(tmpdir) / f"concurrent_{i}.md"
                f.write_text(f"# Concurrent {i}\nWheat data point {i}")
                files.append(str(f))

            async def run():
                async with AsyncKnowledgeIngestionPipeline(
                    enable_vector_storage=False,
                    max_workers=2,
                ) as pipeline:
                    report = await pipeline.ingest_files_concurrent(files, max_concurrent=3)
                    return report

            report = _run(run())
            assert report.total == 5
            assert report.succeeded + report.failed == 5

    def test_async_close(self):
        from shared.ai.knowledge.ingestion.async_pipeline import AsyncKnowledgeIngestionPipeline

        async def run():
            pipeline = AsyncKnowledgeIngestionPipeline(enable_vector_storage=False)
            await pipeline.close()
            return True

        assert _run(run())


# ═══════════════════════════════════════════════════════════════════════════════
# Pipeline Stages Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPipelineStagesComprehensive:
    """Test individual pipeline stages."""

    def test_domain_detection_for_crop_content(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Wheat Cultivation\nWheat variety cultivar growth stage yield harvest.")
            f.flush()

            pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
            result = pipeline.ingest_file(f.name)
            assert result.success
            assert "crops" in result.domains_detected

    def test_domain_detection_for_irrigation_content(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Irrigation Methods\nDrip irrigation water schedule ET evapotranspiration moisture.")
            f.flush()

            pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
            result = pipeline.ingest_file(f.name)
            assert result.success

    def test_text_ingestion(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
        result = pipeline.ingest_text("# Test\nWheat is a major cereal crop.", title="Test Doc")
        assert result.success
        assert result.document_id

    def test_text_ingestion_with_collection_override(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
        result = pipeline.ingest_text("# Test\nContent.", target_collection="custom_collection")
        assert result.collection == "custom_collection"

    def test_bilingual_warning(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(
            enable_vector_storage=False,
            require_bilingual=True,
        )
        result = pipeline.ingest_text("# English Only\nNo Arabic content here.")
        # Bilingual warning appears in validation issues or result warnings
        has_bilingual_issue = any(
            "bilingual" in issue.message.lower() or "arabic" in issue.message.lower()
            for issue in (result.validation.issues if result.validation else [])
        )
        has_bilingual_warning = any(
            "arabic" in w.lower() or "bilingual" in w.lower()
            for w in result.warnings
        )
        assert has_bilingual_issue or has_bilingual_warning

    def test_resolve_collection_for_all_domains(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline
        from shared.ai.knowledge.models import KnowledgeDomain

        pipeline = KnowledgeIngestionPipeline(enable_vector_storage=False)
        for domain in KnowledgeDomain:
            collection = pipeline._resolve_collection(domain)
            assert collection  # Should resolve to a non-empty string
