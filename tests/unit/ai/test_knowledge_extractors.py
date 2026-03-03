"""
Tests for Knowledge Content Extractors
========================================
اختبارات مستخرجات المحتوى المعرفي

Tests for Markdown, PDF, and HTML content extraction.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.ai.knowledge.ingestion.extractors import (
    ExtractedContent,
    HTMLExtractor,
    MarkdownExtractor,
    PDFExtractor,
)


@pytest.fixture
def md_extractor() -> MarkdownExtractor:
    """Create a MarkdownExtractor instance."""
    return MarkdownExtractor()


@pytest.fixture
def html_extractor() -> HTMLExtractor:
    """Create an HTMLExtractor instance."""
    return HTMLExtractor()


@pytest.fixture
def sample_md_file(tmp_path: Path) -> Path:
    """Create a sample Markdown file with frontmatter."""
    content = """---
title: Wheat Irrigation Guide
title_ar: دليل ري القمح
category: irrigation
tags:
  - wheat
  - irrigation
  - scheduling
---

# Wheat Irrigation Guide | دليل ري القمح

## Overview | نظرة عامة

Wheat requires 450-650mm of water per season.

القمح يحتاج 450-650 ملم من المياه في الموسم.

## Scheduling | الجدولة

Irrigate every 10-14 days during tillering stage.

قم بالري كل 10-14 يوم خلال مرحلة التفريع.

## Related Documents | وثائق ذات صلة

- [[crops/wheat|القمح]]
- [[irrigation/drip|الري بالتنقيط]]
"""
    filepath = tmp_path / "wheat-irrigation.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


@pytest.fixture
def sample_html_file(tmp_path: Path) -> Path:
    """Create a sample HTML file."""
    content = """<!DOCTYPE html>
<html>
<head>
    <title>Soil Analysis Guide</title>
    <meta name="description" content="A guide to soil analysis for agriculture">
</head>
<body>
    <h1>Soil Analysis</h1>
    <p>Test pH levels between 6.0 and 8.0 for optimal growth.</p>
</body>
</html>"""
    filepath = tmp_path / "soil-analysis.html"
    filepath.write_text(content, encoding="utf-8")
    return filepath


# ─── ExtractedContent Tests ──────────────────────────────────────────────────


class TestExtractedContent:
    """Tests for ExtractedContent dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default extracted content values."""
        content = ExtractedContent()
        assert content.title == ""
        assert content.content == ""
        assert content.metadata == {}
        assert content.sections == []
        assert content.source_type == ""

    @pytest.mark.unit
    def test_bilingual_content(self):
        """Test bilingual content storage | اختبار التخزين ثنائي اللغة"""
        content = ExtractedContent(
            title="Wheat",
            title_ar="القمح",
            content="English content",
            content_ar="محتوى عربي",
        )
        assert content.title_ar == "القمح"
        assert content.content_ar == "محتوى عربي"


# ─── Markdown Extractor Tests ────────────────────────────────────────────────


class TestMarkdownExtractor:
    """Tests for MarkdownExtractor."""

    @pytest.mark.unit
    def test_extract_frontmatter(self, md_extractor: MarkdownExtractor, sample_md_file: Path):
        """Test YAML frontmatter extraction."""
        result = md_extractor.extract(sample_md_file)
        assert result.title == "Wheat Irrigation Guide"
        assert result.title_ar == "دليل ري القمح"
        assert "category" in result.metadata
        assert result.metadata["category"] == "irrigation"

    @pytest.mark.unit
    def test_extract_tags_from_frontmatter(self, md_extractor: MarkdownExtractor, sample_md_file: Path):
        """Test tag extraction from frontmatter."""
        result = md_extractor.extract(sample_md_file)
        assert "tags" in result.metadata
        assert "wheat" in result.metadata["tags"]

    @pytest.mark.unit
    def test_extract_sections(self, md_extractor: MarkdownExtractor, sample_md_file: Path):
        """Test section extraction from headings."""
        result = md_extractor.extract(sample_md_file)
        assert len(result.sections) > 0
        headings = [s["heading"] for s in result.sections]
        assert any("Overview" in h or "نظرة عامة" in h for h in headings)

    @pytest.mark.unit
    def test_extract_wikilinks(self, md_extractor: MarkdownExtractor, sample_md_file: Path):
        """Test wikilink extraction."""
        result = md_extractor.extract(sample_md_file)
        assert "cross_references" in result.metadata
        assert any("wheat" in ref for ref in result.metadata["cross_references"])

    @pytest.mark.unit
    def test_bilingual_separation(self, md_extractor: MarkdownExtractor, sample_md_file: Path):
        """Test Arabic/English content separation."""
        result = md_extractor.extract(sample_md_file)
        # Should have some content in at least one language
        assert result.content or result.content_ar

    @pytest.mark.unit
    def test_extract_nonexistent_file(self, md_extractor: MarkdownExtractor):
        """Test extracting from a non-existent file."""
        result = md_extractor.extract("/nonexistent/path/file.md")
        assert result.content == ""
        assert result.source_type == "md"

    @pytest.mark.unit
    def test_extract_from_text(self, md_extractor: MarkdownExtractor):
        """Test extracting from raw Markdown text."""
        text = """---
title: Test Document
---

# Test Heading

Some content here about irrigation and crops.
"""
        result = md_extractor.extract_from_text(text, source="test")
        assert result.title == "Test Document"
        assert len(result.sections) > 0

    @pytest.mark.unit
    def test_extract_text_no_frontmatter(self, md_extractor: MarkdownExtractor):
        """Test extracting text without frontmatter."""
        text = "# Simple Title\n\nSome paragraph content."
        result = md_extractor.extract_from_text(text)
        assert result.metadata == {}
        assert len(result.sections) == 1

    @pytest.mark.unit
    def test_source_type_set(self, md_extractor: MarkdownExtractor, sample_md_file: Path):
        """Test source type is set correctly."""
        result = md_extractor.extract(sample_md_file)
        assert result.source_type == "md"

    @pytest.mark.unit
    def test_title_from_filename(self, md_extractor: MarkdownExtractor, tmp_path: Path):
        """Test title fallback to filename when no frontmatter title."""
        f = tmp_path / "my-document.md"
        f.write_text("# Some heading\nContent", encoding="utf-8")
        result = md_extractor.extract(f)
        # Title should be derived from filename if no frontmatter
        assert result.title != ""


# ─── PDF Extractor Tests ─────────────────────────────────────────────────────


class TestPDFExtractor:
    """Tests for PDFExtractor."""

    @pytest.mark.unit
    def test_extract_nonexistent_pdf(self):
        """Test extracting from non-existent PDF returns empty content."""
        extractor = PDFExtractor()
        result = extractor.extract("/nonexistent/file.pdf")
        assert result.content == ""
        assert result.source_type == "pdf"

    @pytest.mark.unit
    def test_extract_without_pymupdf(self, tmp_path: Path):
        """Test graceful handling when PyMuPDF is not installed."""
        # Create a dummy file so path exists
        pdf = tmp_path / "test.pdf"
        pdf.write_text("not a real pdf")
        extractor = PDFExtractor()
        # This should handle the error gracefully
        result = extractor.extract(pdf)
        assert result.source_type == "pdf"


# ─── HTML Extractor Tests ────────────────────────────────────────────────────


class TestHTMLExtractor:
    """Tests for HTMLExtractor."""

    @pytest.mark.unit
    def test_extract_html_file(self, html_extractor: HTMLExtractor, sample_html_file: Path):
        """Test extracting from an HTML file."""
        result = html_extractor.extract(sample_html_file)
        assert result.title == "Soil Analysis Guide"
        assert "description" in result.metadata
        assert result.source_type == "html"

    @pytest.mark.unit
    def test_extract_from_html_string(self, html_extractor: HTMLExtractor):
        """Test extracting from raw HTML string."""
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Agriculture Guide</h1>
            <p>Important farming information.</p>
        </body>
        </html>
        """
        result = html_extractor.extract_from_html(html, source="test.html")
        assert result.title == "Test Page"
        assert "farming" in result.content.lower()
        assert result.source_type == "html"

    @pytest.mark.unit
    def test_html_tag_stripping(self, html_extractor: HTMLExtractor):
        """Test HTML tags are stripped from content."""
        html = "<p><strong>Bold</strong> text with <a href='#'>links</a></p>"
        result = html_extractor.extract_from_html(html)
        assert "<" not in result.content
        assert "Bold" in result.content
        assert "text with" in result.content

    @pytest.mark.unit
    def test_meta_description_extraction(self, html_extractor: HTMLExtractor):
        """Test meta description extraction."""
        html = '<html><head><meta name="description" content="A farming guide"></head><body>Content</body></html>'
        result = html_extractor.extract_from_html(html)
        assert result.metadata.get("description") == "A farming guide"

    @pytest.mark.unit
    def test_extract_nonexistent_html(self, html_extractor: HTMLExtractor):
        """Test extracting from non-existent HTML file."""
        result = html_extractor.extract("/nonexistent/file.html")
        assert result.content == ""
