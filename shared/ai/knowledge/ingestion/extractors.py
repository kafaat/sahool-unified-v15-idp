# ═══════════════════════════════════════════════════════════════════════════════
# Content Extractors for Knowledge Ingestion
# مستخرجات المحتوى لاستيعاب المعرفة
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ExtractedContent:
    """Result of content extraction | نتيجة استخراج المحتوى"""

    title: str = ""
    title_ar: str = ""
    content: str = ""
    content_ar: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    sections: list[dict[str, str]] = field(default_factory=list)
    source_path: str = ""
    source_type: str = ""  # md, pdf, html, text


class MarkdownExtractor:
    """Extracts content from Markdown files with YAML frontmatter support.
    يستخرج المحتوى من ملفات Markdown مع دعم YAML frontmatter"""

    _FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    _HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    _WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

    def extract(self, file_path: str | Path) -> ExtractedContent:
        """Extract content from a Markdown file."""
        path = Path(file_path)
        if not path.exists():
            logger.error("file_not_found", path=str(path))
            return ExtractedContent(source_path=str(path), source_type="md")

        text = path.read_text(encoding="utf-8")
        result = ExtractedContent(source_path=str(path), source_type="md")

        # Extract YAML frontmatter
        frontmatter = self._extract_frontmatter(text)
        if frontmatter:
            result.metadata = frontmatter
            result.title = frontmatter.get("title", "")
            result.title_ar = frontmatter.get("title_ar", "")
            # Remove frontmatter from content
            text = self._FRONTMATTER_RE.sub("", text)

        # Extract sections
        result.sections = self._extract_sections(text)

        # Separate Arabic and English content
        content_en, content_ar = self._separate_bilingual(text)
        result.content = content_en.strip()
        result.content_ar = content_ar.strip()

        # Fallback: if no Arabic separation detected, use full text as English
        if not result.content and not result.content_ar:
            result.content = text.strip()

        if not result.title:
            result.title = path.stem.replace("-", " ").replace("_", " ").title()

        # Extract wikilinks as cross-references
        wikilinks = self._WIKILINK_RE.findall(text)
        if wikilinks:
            result.metadata["cross_references"] = wikilinks

        logger.debug("markdown_extracted", path=str(path), sections=len(result.sections))
        return result

    def extract_from_text(self, text: str, source: str = "") -> ExtractedContent:
        """Extract from raw Markdown text."""
        result = ExtractedContent(source_path=source, source_type="md")

        frontmatter = self._extract_frontmatter(text)
        if frontmatter:
            result.metadata = frontmatter
            result.title = frontmatter.get("title", "")
            result.title_ar = frontmatter.get("title_ar", "")
            text = self._FRONTMATTER_RE.sub("", text)

        result.sections = self._extract_sections(text)
        content_en, content_ar = self._separate_bilingual(text)
        result.content = content_en.strip() or text.strip()
        result.content_ar = content_ar.strip()

        return result

    def _extract_frontmatter(self, text: str) -> dict[str, Any]:
        match = self._FRONTMATTER_RE.match(text)
        if not match:
            return {}
        try:
            import yaml

            return yaml.safe_load(match.group(1)) or {}
        except Exception:
            return {}

    def _extract_sections(self, text: str) -> list[dict[str, str]]:
        sections = []
        matches = list(self._HEADING_RE.finditer(text))
        for i, m in enumerate(matches):
            level = len(m.group(1))
            heading = m.group(2).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            sections.append({"level": str(level), "heading": heading, "content": body})
        return sections

    def _separate_bilingual(self, text: str) -> tuple[str, str]:
        """Attempt to separate Arabic and English content."""
        arabic_pattern = re.compile(r"[\u0600-\u06FF]")
        lines = text.split("\n")
        en_lines = []
        ar_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            arabic_chars = len(arabic_pattern.findall(stripped))
            total_alpha = len(re.findall(r"[a-zA-Z\u0600-\u06FF]", stripped))
            if total_alpha > 0 and arabic_chars / total_alpha > 0.5:
                ar_lines.append(line)
            else:
                en_lines.append(line)
        return "\n".join(en_lines), "\n".join(ar_lines)


class PDFExtractor:
    """Extracts content from PDF files.
    يستخرج المحتوى من ملفات PDF"""

    def extract(self, file_path: str | Path) -> ExtractedContent:
        """Extract text content from a PDF file."""
        path = Path(file_path)
        result = ExtractedContent(source_path=str(path), source_type="pdf")

        if not path.exists():
            logger.error("file_not_found", path=str(path))
            return result

        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error(
                "pymupdf_not_installed",
                msg="PDF extraction requires PyMuPDF. Install with: pip install PyMuPDF",
                path=str(path),
            )
            result.metadata["error"] = "PyMuPDF not installed. Run: pip install PyMuPDF"
            return result

        try:
            doc = fitz.open(str(path))
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            doc.close()

            full_text = "\n\n".join(pages_text)
            result.content = full_text.strip()
            result.title = path.stem.replace("-", " ").replace("_", " ").title()
            result.metadata["page_count"] = len(pages_text)

            # Detect Arabic content
            arabic_pattern = re.compile(r"[\u0600-\u06FF]")
            arabic_chars = len(arabic_pattern.findall(full_text))
            total_chars = len(full_text)
            if total_chars > 0 and arabic_chars / total_chars > 0.3:
                result.content_ar = full_text.strip()
                result.content = ""

            logger.debug("pdf_extracted", path=str(path), pages=len(pages_text))
        except Exception:
            logger.exception("pdf_extraction_failed", path=str(path))

        return result


class HTMLExtractor:
    """Extracts content from HTML files or raw HTML strings.
    يستخرج المحتوى من ملفات HTML"""

    _TAG_RE = re.compile(r"<[^>]+>")
    _WHITESPACE_RE = re.compile(r"\s+")
    _TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
    _META_DESC_RE = re.compile(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
        re.IGNORECASE,
    )

    def extract(self, file_path: str | Path) -> ExtractedContent:
        """Extract content from an HTML file."""
        path = Path(file_path)
        result = ExtractedContent(source_path=str(path), source_type="html")

        if not path.exists():
            logger.error("file_not_found", path=str(path))
            return result

        html = path.read_text(encoding="utf-8")
        return self.extract_from_html(html, source=str(path))

    def extract_from_html(self, html: str, source: str = "") -> ExtractedContent:
        """Extract content from raw HTML string."""
        result = ExtractedContent(source_path=source, source_type="html")

        # Extract title
        title_match = self._TITLE_RE.search(html)
        if title_match:
            result.title = title_match.group(1).strip()

        # Extract meta description
        desc_match = self._META_DESC_RE.search(html)
        if desc_match:
            result.metadata["description"] = desc_match.group(1).strip()

        # Strip HTML tags and normalize whitespace
        text = self._TAG_RE.sub(" ", html)
        text = self._WHITESPACE_RE.sub(" ", text).strip()
        result.content = text

        logger.debug("html_extracted", source=source, length=len(text))
        return result
