# ═══════════════════════════════════════════════════════════════════════════════
# Text Chunking Strategy for Knowledge Ingestion
# استراتيجية تقطيع النصوص لاستيعاب المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provides configurable text chunking for RAG-optimized retrieval:
#   - Heading-based splitting for Markdown documents
#   - Token-aware sliding window with overlap
#   - Metadata preservation per chunk
#   - Arabic/English bilingual chunk alignment
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from shared.ai.knowledge._logging import get_logger

logger = get_logger(__name__)


class ChunkStrategy(StrEnum):
    """Chunking strategy | استراتيجية التقطيع"""

    HEADING = "heading"  # Split by Markdown headings
    SLIDING_WINDOW = "sliding_window"  # Fixed-size with overlap
    PARAGRAPH = "paragraph"  # Split by paragraphs
    HYBRID = "hybrid"  # Heading-first, then sliding window for large sections


@dataclass
class ChunkConfig:
    """Configuration for text chunking | إعدادات تقطيع النصوص"""

    strategy: ChunkStrategy = ChunkStrategy.HYBRID
    max_chunk_size: int = 512  # Max tokens (approx words) per chunk
    min_chunk_size: int = 50  # Minimum tokens to form a chunk
    overlap_size: int = 50  # Overlap tokens between consecutive chunks
    heading_levels: list[int] = field(default_factory=lambda: [1, 2, 3])
    preserve_paragraphs: bool = True  # Avoid splitting mid-paragraph


@dataclass
class TextChunk:
    """A single chunk of text with metadata | قطعة نصية واحدة مع البيانات الوصفية"""

    content: str
    content_ar: str = ""
    chunk_index: int = 0
    total_chunks: int = 0
    heading: str = ""
    heading_ar: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.content.split()) + len(self.content_ar.split())


class TextChunker:
    """Chunks text content for RAG-optimized retrieval.
    يقطع المحتوى النصي للاسترجاع المحسن للتوليد المعزز

    Strategies:
    - HEADING: Splits on Markdown headings (## Section → chunk)
    - SLIDING_WINDOW: Fixed-size chunks with configurable overlap
    - PARAGRAPH: Splits on double newlines
    - HYBRID: Heading-first, then sliding window for oversized sections
    """

    _HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def __init__(self, config: ChunkConfig | None = None) -> None:
        self._config = config or ChunkConfig()

    def chunk(
        self,
        content: str,
        content_ar: str = "",
        base_metadata: dict[str, Any] | None = None,
    ) -> list[TextChunk]:
        """Chunk text content using the configured strategy.
        تقطيع المحتوى النصي باستخدام الاستراتيجية المحددة"""
        if not content and not content_ar:
            return []

        strategy = self._config.strategy

        if strategy == ChunkStrategy.HEADING:
            chunks = self._chunk_by_heading(content, content_ar)
        elif strategy == ChunkStrategy.SLIDING_WINDOW:
            chunks = self._chunk_sliding_window(content, content_ar)
        elif strategy == ChunkStrategy.PARAGRAPH:
            chunks = self._chunk_by_paragraph(content, content_ar)
        else:  # HYBRID
            chunks = self._chunk_hybrid(content, content_ar)

        # Add metadata and indices
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
            chunk.total_chunks = total
            if base_metadata:
                chunk.metadata.update(base_metadata)

        # Filter out too-small chunks (merge with previous if possible)
        chunks = self._merge_small_chunks(chunks)

        logger.debug(
            "text_chunked",
            strategy=strategy.value,
            total_chunks=len(chunks),
            avg_words=sum(c.word_count for c in chunks) // max(1, len(chunks)),
        )

        return chunks

    # ─── Strategy: Heading-Based ───────────────────────────────────────────

    def _chunk_by_heading(self, content: str, content_ar: str = "") -> list[TextChunk]:
        """Split text by Markdown headings."""
        if not content:
            return [TextChunk(content="", content_ar=content_ar)] if content_ar else []

        matches = list(self._HEADING_RE.finditer(content))
        if not matches:
            return [TextChunk(content=content, content_ar=content_ar)]

        chunks = []
        allowed_levels = self._config.heading_levels

        # Text before first heading
        pre_text = content[: matches[0].start()].strip()
        if pre_text:
            chunks.append(TextChunk(content=pre_text))

        for i, match in enumerate(matches):
            level = len(match.group(1))
            if level not in allowed_levels:
                continue

            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            body = content[start:end].strip()

            if body:
                chunks.append(TextChunk(content=body, heading=heading))

        return chunks

    # ─── Strategy: Sliding Window ──────────────────────────────────────────

    def _chunk_sliding_window(self, content: str, content_ar: str = "") -> list[TextChunk]:
        """Split text into fixed-size windows with overlap."""
        chunks = []

        if content:
            chunks.extend(self._sliding_window_text(content, is_arabic=False))

        if content_ar:
            ar_chunks = self._sliding_window_text(content_ar, is_arabic=True)
            # Merge Arabic chunks with corresponding English chunks if same count
            if len(ar_chunks) == len(chunks):
                for i, ar_chunk in enumerate(ar_chunks):
                    chunks[i].content_ar = ar_chunk.content_ar
            else:
                chunks.extend(ar_chunks)

        return chunks

    def _sliding_window_text(self, text: str, is_arabic: bool = False) -> list[TextChunk]:
        """Create sliding window chunks from a single text."""
        words = text.split()
        max_size = self._config.max_chunk_size
        overlap = self._config.overlap_size
        step = max(1, max_size - overlap)

        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + max_size]
            chunk_text = " ".join(chunk_words)

            if is_arabic:
                chunks.append(TextChunk(content="", content_ar=chunk_text))
            else:
                chunks.append(TextChunk(content=chunk_text))

            i += step
            if i + self._config.min_chunk_size >= len(words) and i < len(words):
                # Remaining text too small for a separate chunk; include in last chunk
                remaining = " ".join(words[i:])
                if is_arabic:
                    chunks[-1].content_ar += " " + remaining
                else:
                    chunks[-1].content += " " + remaining
                break

        return chunks

    # ─── Strategy: Paragraph-Based ─────────────────────────────────────────

    def _chunk_by_paragraph(self, content: str, content_ar: str = "") -> list[TextChunk]:
        """Split text by paragraph boundaries (double newlines)."""
        paragraphs = re.split(r"\n\s*\n", content) if content else []
        chunks = []

        current_text = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            combined = f"{current_text}\n\n{para}".strip() if current_text else para
            if len(combined.split()) <= self._config.max_chunk_size:
                current_text = combined
            else:
                if current_text:
                    chunks.append(TextChunk(content=current_text))
                current_text = para

        if current_text:
            chunks.append(TextChunk(content=current_text))

        return chunks

    # ─── Strategy: Hybrid ──────────────────────────────────────────────────

    def _chunk_hybrid(self, content: str, content_ar: str = "") -> list[TextChunk]:
        """Heading-first, then sliding window for oversized sections."""
        heading_chunks = self._chunk_by_heading(content, content_ar)

        final_chunks = []
        for chunk in heading_chunks:
            if chunk.word_count > self._config.max_chunk_size:
                # This section is too large, split with sliding window
                sub_chunks = self._sliding_window_text(chunk.content, is_arabic=False)
                for sub in sub_chunks:
                    sub.heading = chunk.heading
                    sub.heading_ar = chunk.heading_ar
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)

        return final_chunks

    # ─── Utilities ─────────────────────────────────────────────────────────

    def _merge_small_chunks(self, chunks: list[TextChunk]) -> list[TextChunk]:
        """Merge chunks smaller than min_chunk_size with adjacent chunks."""
        if not chunks:
            return chunks

        min_size = self._config.min_chunk_size
        merged = []

        for chunk in chunks:
            if merged and chunk.word_count < min_size:
                # Merge with previous chunk
                prev = merged[-1]
                separator = "\n\n" if prev.content and chunk.content else ""
                prev.content = f"{prev.content}{separator}{chunk.content}".strip()
                if chunk.content_ar:
                    ar_sep = "\n\n" if prev.content_ar else ""
                    prev.content_ar = f"{prev.content_ar}{ar_sep}{chunk.content_ar}".strip()
            else:
                merged.append(chunk)

        # Re-index
        for i, chunk in enumerate(merged):
            chunk.chunk_index = i
            chunk.total_chunks = len(merged)

        return merged
