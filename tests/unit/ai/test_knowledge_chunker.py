"""
Tests for Knowledge Text Chunker
=================================
اختبارات تقطيع النصوص المعرفية

Tests for heading-based, sliding window, paragraph, and hybrid chunking strategies.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.ingestion.chunker import (
    ChunkConfig,
    ChunkStrategy,
    TextChunk,
    TextChunker,
)


@pytest.fixture
def default_chunker() -> TextChunker:
    """Create a TextChunker with default config."""
    return TextChunker()


@pytest.fixture
def heading_chunker() -> TextChunker:
    """Create a TextChunker with heading strategy and low min size."""
    return TextChunker(ChunkConfig(strategy=ChunkStrategy.HEADING, min_chunk_size=2))


@pytest.fixture
def sliding_chunker() -> TextChunker:
    """Create a TextChunker with sliding window strategy."""
    return TextChunker(ChunkConfig(
        strategy=ChunkStrategy.SLIDING_WINDOW,
        max_chunk_size=10,
        overlap_size=3,
        min_chunk_size=3,
    ))


@pytest.fixture
def paragraph_chunker() -> TextChunker:
    """Create a TextChunker with paragraph strategy."""
    return TextChunker(ChunkConfig(strategy=ChunkStrategy.PARAGRAPH, max_chunk_size=20))


# ─── Basic Tests ─────────────────────────────────────────────────────────────


class TestTextChunkerBasic:
    """Basic chunker tests."""

    @pytest.mark.unit
    def test_empty_content_returns_empty(self, default_chunker: TextChunker):
        """Empty content returns empty list."""
        assert default_chunker.chunk("") == []

    @pytest.mark.unit
    def test_empty_both_returns_empty(self, default_chunker: TextChunker):
        """Empty content and content_ar returns empty list."""
        assert default_chunker.chunk("", "") == []

    @pytest.mark.unit
    def test_chunk_returns_text_chunks(self, default_chunker: TextChunker):
        """Chunker returns list of TextChunk objects."""
        chunks = default_chunker.chunk("Some text content.")
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)

    @pytest.mark.unit
    def test_chunk_indices_set(self, default_chunker: TextChunker):
        """Chunks have correct indices and total_chunks."""
        content = "## Section One\n\nContent one.\n\n## Section Two\n\nContent two."
        chunks = default_chunker.chunk(content)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.total_chunks == len(chunks)

    @pytest.mark.unit
    def test_base_metadata_propagated(self, default_chunker: TextChunker):
        """Base metadata is added to all chunks."""
        meta = {"source": "test", "domain": "crops"}
        chunks = default_chunker.chunk("Some content", base_metadata=meta)
        for chunk in chunks:
            assert chunk.metadata["source"] == "test"
            assert chunk.metadata["domain"] == "crops"


# ─── TextChunk Dataclass ─────────────────────────────────────────────────────


class TestTextChunk:
    """Tests for TextChunk dataclass."""

    @pytest.mark.unit
    def test_word_count_english(self):
        """Word count for English content."""
        chunk = TextChunk(content="one two three four")
        assert chunk.word_count == 4

    @pytest.mark.unit
    def test_word_count_bilingual(self):
        """Word count combines English and Arabic."""
        chunk = TextChunk(content="one two", content_ar="واحد اثنان ثلاثة")
        assert chunk.word_count == 5

    @pytest.mark.unit
    def test_word_count_empty(self):
        """Empty chunk has word count of 0."""
        chunk = TextChunk(content="")
        assert chunk.word_count == 0


# ─── Heading Strategy ────────────────────────────────────────────────────────


class TestHeadingStrategy:
    """Tests for heading-based chunking."""

    @pytest.mark.unit
    def test_split_by_h2(self, heading_chunker: TextChunker):
        """Splits on level-2 headings."""
        content = "## Irrigation\n\nDrip system.\n\n## Fertilizer\n\nUrea application."
        chunks = heading_chunker.chunk(content)
        assert len(chunks) >= 2
        assert any("Drip" in c.content for c in chunks)
        assert any("Urea" in c.content for c in chunks)

    @pytest.mark.unit
    def test_heading_preserved(self, heading_chunker: TextChunker):
        """Heading text is stored in chunk.heading."""
        content = "## Water Management\n\nSchedule irrigation properly."
        chunks = heading_chunker.chunk(content)
        heading_chunks = [c for c in chunks if c.heading]
        assert any("Water Management" in c.heading for c in heading_chunks)

    @pytest.mark.unit
    def test_text_before_first_heading(self, heading_chunker: TextChunker):
        """Text before the first heading becomes its own chunk."""
        content = "Introduction text.\n\n## First Section\n\nSection content."
        chunks = heading_chunker.chunk(content)
        assert any("Introduction" in c.content for c in chunks)

    @pytest.mark.unit
    def test_no_headings_single_chunk(self, heading_chunker: TextChunker):
        """Content without headings returns single chunk."""
        content = "Just plain text with no headings at all."
        chunks = heading_chunker.chunk(content)
        assert len(chunks) == 1

    @pytest.mark.unit
    def test_heading_levels_filter(self):
        """Only configured heading levels are split on."""
        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.HEADING,
            heading_levels=[2],
            min_chunk_size=2,
        ))
        content = "## Section A\n\nContent A here.\n\n## Section B\n\nContent B here."
        chunks = chunker.chunk(content)
        assert len(chunks) == 2
        assert chunks[0].heading == "Section A"
        assert chunks[1].heading == "Section B"


# ─── Sliding Window Strategy ─────────────────────────────────────────────────


class TestSlidingWindowStrategy:
    """Tests for sliding window chunking."""

    @pytest.mark.unit
    def test_fixed_size_chunks(self, sliding_chunker: TextChunker):
        """Creates chunks of configured max size."""
        words = " ".join(f"word{i}" for i in range(30))
        chunks = sliding_chunker.chunk(words)
        assert len(chunks) >= 2

    @pytest.mark.unit
    def test_overlap_between_chunks(self, sliding_chunker: TextChunker):
        """Consecutive chunks have overlapping content."""
        words = " ".join(f"w{i}" for i in range(25))
        chunks = sliding_chunker.chunk(words)
        if len(chunks) >= 2:
            words_0 = set(chunks[0].content.split())
            words_1 = set(chunks[1].content.split())
            assert len(words_0 & words_1) > 0

    @pytest.mark.unit
    def test_small_text_single_chunk(self, sliding_chunker: TextChunker):
        """Text smaller than max_chunk_size is a single chunk."""
        chunks = sliding_chunker.chunk("one two three")
        assert len(chunks) == 1

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_arabic_sliding_window(self, sliding_chunker: TextChunker):
        """Arabic content chunked via sliding window."""
        ar_words = " ".join(["كلمة"] * 25)
        chunks = sliding_chunker.chunk("", ar_words)
        assert len(chunks) >= 1
        assert any(c.content_ar for c in chunks)


# ─── Paragraph Strategy ──────────────────────────────────────────────────────


class TestParagraphStrategy:
    """Tests for paragraph-based chunking."""

    @pytest.mark.unit
    def test_split_by_paragraphs(self, paragraph_chunker: TextChunker):
        """Splits on double newlines."""
        content = "Paragraph one with text.\n\nParagraph two with more text.\n\nParagraph three final."
        chunks = paragraph_chunker.chunk(content)
        assert len(chunks) >= 1

    @pytest.mark.unit
    def test_paragraphs_merged_within_limit(self, paragraph_chunker: TextChunker):
        """Small paragraphs are merged within max_chunk_size."""
        content = "Short one.\n\nShort two.\n\nShort three."
        chunks = paragraph_chunker.chunk(content)
        # All should fit in one chunk since max_chunk_size=20 words
        assert len(chunks) == 1

    @pytest.mark.unit
    def test_large_paragraph_separate(self):
        """Large paragraph exceeding limit starts new chunk."""
        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.PARAGRAPH,
            max_chunk_size=5,
            min_chunk_size=2,
        ))
        content = "word " * 10 + "\n\n" + "other " * 10
        chunks = chunker.chunk(content)
        assert len(chunks) >= 2


# ─── Hybrid Strategy ─────────────────────────────────────────────────────────


class TestHybridStrategy:
    """Tests for hybrid chunking (heading + sliding window fallback)."""

    @pytest.mark.unit
    def test_hybrid_splits_headings_first(self):
        """Hybrid uses headings as primary split points."""
        chunker = TextChunker(ChunkConfig(strategy=ChunkStrategy.HYBRID, min_chunk_size=2))
        content = "## Section A\n\nSmall section content here.\n\n## Section B\n\nAnother small section content."
        chunks = chunker.chunk(content)
        assert len(chunks) >= 2

    @pytest.mark.unit
    def test_hybrid_subdivides_large_sections(self):
        """Large sections get further split by sliding window."""
        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.HYBRID,
            max_chunk_size=10,
            min_chunk_size=3,
            overlap_size=2,
        ))
        large_section = " ".join(f"word{i}" for i in range(30))
        content = f"## Big Section\n\n{large_section}"
        chunks = chunker.chunk(content)
        assert len(chunks) >= 2


# ─── Merge Small Chunks ──────────────────────────────────────────────────────


class TestMergeSmallChunks:
    """Tests for small chunk merging."""

    @pytest.mark.unit
    def test_small_chunks_merged(self):
        """Chunks below min_chunk_size merge with previous."""
        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.HEADING,
            min_chunk_size=10,
        ))
        content = "## A\n\nOne word.\n\n## B\n\nAnother word."
        chunks = chunker.chunk(content)
        # Should be merged since each section < 10 words
        assert len(chunks) <= 2

    @pytest.mark.unit
    def test_merged_chunks_reindexed(self):
        """After merging, chunk indices are consecutive."""
        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.HEADING,
            min_chunk_size=10,
        ))
        content = "## A\n\nShort.\n\n## B\n\nAlso short.\n\n## C\n\nStill short."
        chunks = chunker.chunk(content)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.total_chunks == len(chunks)


# ─── ChunkConfig ──────────────────────────────────────────────────────────────


class TestChunkConfig:
    """Tests for ChunkConfig defaults."""

    @pytest.mark.unit
    def test_default_values(self):
        """Default config values."""
        config = ChunkConfig()
        assert config.strategy == ChunkStrategy.HYBRID
        assert config.max_chunk_size == 512
        assert config.min_chunk_size == 50
        assert config.overlap_size == 50
        assert config.heading_levels == [1, 2, 3]
        assert config.preserve_paragraphs is True

    @pytest.mark.unit
    def test_custom_values(self):
        """Custom config values."""
        config = ChunkConfig(
            strategy=ChunkStrategy.SLIDING_WINDOW,
            max_chunk_size=256,
            overlap_size=32,
        )
        assert config.strategy == ChunkStrategy.SLIDING_WINDOW
        assert config.max_chunk_size == 256
        assert config.overlap_size == 32


# ─── ChunkStrategy Enum ──────────────────────────────────────────────────────


class TestChunkStrategy:
    """Tests for ChunkStrategy enum."""

    @pytest.mark.unit
    def test_strategy_values(self):
        """All strategy values are correct strings."""
        assert ChunkStrategy.HEADING == "heading"
        assert ChunkStrategy.SLIDING_WINDOW == "sliding_window"
        assert ChunkStrategy.PARAGRAPH == "paragraph"
        assert ChunkStrategy.HYBRID == "hybrid"

    @pytest.mark.unit
    def test_strategy_count(self):
        """There are exactly 4 strategies."""
        assert len(ChunkStrategy) == 4
