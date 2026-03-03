"""
Tests for Knowledge Ingestion Pipeline
========================================
اختبارات خط أنابيب استيعاب المعرفة

Comprehensive tests for file, text, and directory ingestion
through the 6-stage pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.ai.knowledge.ingestion.pipeline import (
    BatchIngestionReport,
    IngestionResult,
    KnowledgeIngestionPipeline,
)


@pytest.fixture
def pipeline() -> KnowledgeIngestionPipeline:
    """Create a KnowledgeIngestionPipeline instance."""
    return KnowledgeIngestionPipeline()


@pytest.fixture
def strict_pipeline() -> KnowledgeIngestionPipeline:
    """Create a pipeline with bilingual requirement."""
    return KnowledgeIngestionPipeline(require_bilingual=True)


@pytest.fixture
def sample_md_file(tmp_path: Path) -> Path:
    """Create a sample Markdown file for ingestion."""
    content = """---
title: Wheat Cultivation Guide
title_ar: دليل زراعة القمح
category: crops
tags:
  - wheat
  - cultivation
---

# Wheat Cultivation Guide

Wheat is a major crop in Yemen and Saudi Arabia.
Optimal temperature: 15-25°C. Requires 450-650mm water per season.

## Growth Stages

Wheat goes through germination, tillering, heading, and maturity.

## Irrigation

Use drip irrigation for best efficiency.

القمح محصول رئيسي في اليمن والسعودية.
"""
    filepath = tmp_path / "wheat.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


@pytest.fixture
def sample_directory(tmp_path: Path) -> Path:
    """Create a directory with multiple Markdown files."""
    docs_dir = tmp_path / "crops"
    docs_dir.mkdir()

    # Create several crop files
    for name, content in [
        ("wheat.md", "---\ntitle: Wheat\n---\n# Wheat\nWheat crop information."),
        ("barley.md", "---\ntitle: Barley\n---\n# Barley\nBarley crop information."),
        ("README.md", "# Crops\nOverview of crops."),
        (".hidden.md", "Hidden file"),
    ]:
        (docs_dir / name).write_text(content, encoding="utf-8")

    return docs_dir


# ─── IngestionResult Tests ───────────────────────────────────────────────────


class TestIngestionResult:
    """Tests for IngestionResult dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default ingestion result."""
        result = IngestionResult()
        assert result.success is False
        assert result.document_id == ""
        assert result.collection == ""
        assert result.errors == []
        assert result.warnings == []


class TestBatchIngestionReport:
    """Tests for BatchIngestionReport dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default batch report."""
        report = BatchIngestionReport()
        assert report.total == 0
        assert report.succeeded == 0
        assert report.failed == 0
        assert report.skipped == 0


# ─── File Ingestion Tests ────────────────────────────────────────────────────


class TestFileIngestion:
    """Tests for single file ingestion."""

    @pytest.mark.unit
    def test_ingest_markdown_file(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test ingesting a valid Markdown file."""
        result = pipeline.ingest_file(sample_md_file)
        assert result.success is True
        assert result.document_id.startswith("kb_")
        assert result.collection != ""

    @pytest.mark.unit
    def test_ingest_with_source_url(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test ingestion with FAO source URL gives high credibility."""
        result = pipeline.ingest_file(sample_md_file, source_url="https://www.fao.org/water")
        assert result.source_credibility == 5  # FAO is level 5

    @pytest.mark.unit
    def test_ingest_with_target_collection(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test ingestion with explicit target collection."""
        result = pipeline.ingest_file(sample_md_file, target_collection="crop_knowledge")
        assert result.collection == "crop_knowledge"

    @pytest.mark.unit
    def test_ingest_detects_domains(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test domain detection during ingestion."""
        result = pipeline.ingest_file(sample_md_file)
        assert len(result.domains_detected) > 0
        assert "crops" in result.domains_detected

    @pytest.mark.unit
    def test_ingest_detects_regions(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test region detection during ingestion."""
        result = pipeline.ingest_file(sample_md_file)
        assert "yemen" in result.regions_detected or "saudi_arabia" in result.regions_detected

    @pytest.mark.unit
    def test_ingest_extracts_tags(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test tag extraction during ingestion."""
        result = pipeline.ingest_file(sample_md_file)
        assert len(result.tags) > 0
        assert "crop:wheat" in result.tags

    @pytest.mark.unit
    def test_ingest_nonexistent_file(self, pipeline: KnowledgeIngestionPipeline):
        """Test ingesting a non-existent file."""
        result = pipeline.ingest_file("/nonexistent/file.md")
        assert result.success is False
        assert len(result.errors) > 0

    @pytest.mark.unit
    def test_ingest_empty_file(self, pipeline: KnowledgeIngestionPipeline, tmp_path: Path):
        """Test ingesting an empty file."""
        empty = tmp_path / "empty.md"
        empty.write_text("", encoding="utf-8")
        result = pipeline.ingest_file(empty)
        assert result.success is False

    @pytest.mark.unit
    def test_bilingual_warning(self, strict_pipeline: KnowledgeIngestionPipeline, tmp_path: Path):
        """Test bilingual requirement generates warning for English-only."""
        f = tmp_path / "english-only.md"
        f.write_text("---\ntitle: English Only\n---\n# Title\nEnglish content only.", encoding="utf-8")
        result = strict_pipeline.ingest_file(f)
        assert any("bilingual" in w.lower() or "Arabic" in w for w in result.warnings)


# ─── Text Ingestion Tests ────────────────────────────────────────────────────


class TestTextIngestion:
    """Tests for raw text ingestion."""

    @pytest.mark.unit
    def test_ingest_simple_text(self, pipeline: KnowledgeIngestionPipeline):
        """Test ingesting raw text about crops."""
        text = "Wheat is a major cereal crop. It requires irrigation during tillering."
        result = pipeline.ingest_text(text, title="Wheat Info")
        assert result.success is True
        assert result.document_id.startswith("kb_")

    @pytest.mark.unit
    def test_ingest_text_with_title(self, pipeline: KnowledgeIngestionPipeline):
        """Test title override for text ingestion."""
        text = "---\ntitle: Original Title\n---\nSome content about wheat."
        result = pipeline.ingest_text(text, title="Override Title")
        assert result.success is True

    @pytest.mark.unit
    def test_ingest_text_domain_detection(self, pipeline: KnowledgeIngestionPipeline):
        """Test domain detection from text."""
        text = "Apply nitrogen fertilizer and urea for wheat growth."
        result = pipeline.ingest_text(text, title="Fertilizer Guide")
        assert "fertilizer" in result.domains_detected

    @pytest.mark.unit
    def test_ingest_text_with_source_url(self, pipeline: KnowledgeIngestionPipeline):
        """Test text ingestion with source URL."""
        text = "Soil analysis for clay soil with pH 7.5"
        result = pipeline.ingest_text(text, title="Soil Guide", source_url="https://icarda.org/soil")
        assert result.source_credibility == 5


# ─── Directory Ingestion Tests ───────────────────────────────────────────────


class TestDirectoryIngestion:
    """Tests for batch directory ingestion."""

    @pytest.mark.unit
    def test_ingest_directory(self, pipeline: KnowledgeIngestionPipeline, sample_directory: Path):
        """Test ingesting a directory of Markdown files."""
        report = pipeline.ingest_directory(sample_directory)
        # Should process wheat.md and barley.md, skip README.md and .hidden.md
        assert report.total == 4  # Total files found by glob
        assert report.skipped >= 2  # README.md + .hidden.md
        assert report.succeeded >= 1

    @pytest.mark.unit
    def test_directory_skips_readme(self, pipeline: KnowledgeIngestionPipeline, sample_directory: Path):
        """Test that README.md is skipped during directory ingestion."""
        report = pipeline.ingest_directory(sample_directory)
        assert report.skipped >= 1

    @pytest.mark.unit
    def test_directory_skips_hidden_files(self, pipeline: KnowledgeIngestionPipeline, sample_directory: Path):
        """Test that hidden files are skipped."""
        report = pipeline.ingest_directory(sample_directory)
        # .hidden.md should be skipped
        assert report.skipped >= 1

    @pytest.mark.unit
    def test_ingest_nonexistent_directory(self, pipeline: KnowledgeIngestionPipeline):
        """Test ingesting a non-existent directory."""
        report = pipeline.ingest_directory("/nonexistent/directory")
        assert report.total == 0

    @pytest.mark.unit
    def test_directory_with_collection(self, pipeline: KnowledgeIngestionPipeline, sample_directory: Path):
        """Test directory ingestion with target collection."""
        report = pipeline.ingest_directory(sample_directory, target_collection="crop_knowledge")
        for result in report.results:
            assert result.collection == "crop_knowledge"

    @pytest.mark.unit
    def test_directory_batch_report(self, pipeline: KnowledgeIngestionPipeline, sample_directory: Path):
        """Test batch report counters are consistent."""
        report = pipeline.ingest_directory(sample_directory)
        assert report.succeeded + report.failed + report.skipped == report.total


# ─── Pipeline Stage Tests ────────────────────────────────────────────────────


class TestPipelineStages:
    """Tests for individual pipeline stages."""

    @pytest.mark.unit
    def test_source_credibility_no_url(self, pipeline: KnowledgeIngestionPipeline):
        """Test source credibility stage with no URL returns COMMUNITY."""
        cred = pipeline._check_source("")
        assert cred.value == 1  # COMMUNITY

    @pytest.mark.unit
    def test_resolve_collection_crops(self, pipeline: KnowledgeIngestionPipeline):
        """Test collection resolution for crop domain."""
        from shared.ai.knowledge.models import KnowledgeDomain

        assert pipeline._resolve_collection(KnowledgeDomain.CROPS) == "crop_knowledge"

    @pytest.mark.unit
    def test_resolve_collection_general(self, pipeline: KnowledgeIngestionPipeline):
        """Test fallback collection resolution."""
        from shared.ai.knowledge.models import KnowledgeDomain

        assert pipeline._resolve_collection(KnowledgeDomain.GENERAL) == "general_agriculture"

    @pytest.mark.unit
    def test_extract_markdown(self, pipeline: KnowledgeIngestionPipeline, sample_md_file: Path):
        """Test extract stage for Markdown files."""
        extracted = pipeline._extract(sample_md_file)
        assert extracted.source_type == "md"
        assert extracted.title != ""

    @pytest.mark.unit
    def test_extract_txt_fallback(self, pipeline: KnowledgeIngestionPipeline, tmp_path: Path):
        """Test extract stage treats .txt as markdown."""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("# Title\nSome text content")
        extracted = pipeline._extract(txt_file)
        assert extracted.source_type == "md"
