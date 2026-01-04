"""
SAHOOL AI Ranker Tests
Sprint 9: Unit tests for deterministic ranking
"""

import sys

sys.path.insert(0, "packages")

from advisor.ai.rag_models import RetrievedChunk
from advisor.ai.ranker import rank, rank_with_diversity, top_k


class TestRank:
    """Test deterministic ranking"""

    def test_rank_is_deterministic(self):
        """Same input always produces same output"""
        chunks = [
            RetrievedChunk("b", "1", "x", 0.8, "s"),
            RetrievedChunk("a", "2", "y", 0.8, "s"),
            RetrievedChunk("a", "1", "z", 0.9, "s"),
        ]

        result = rank(chunks)

        # Highest score first, then alphabetical doc_id, then chunk_id
        assert [c.doc_id + c.chunk_id for c in result] == ["a1", "a2", "b1"]

    def test_rank_empty_list(self):
        """Empty list returns empty list"""
        assert rank([]) == []

    def test_rank_single_chunk(self):
        """Single chunk returns list with that chunk"""
        chunk = RetrievedChunk("doc1", "0", "text", 0.9, "src")
        result = rank([chunk])
        assert len(result) == 1
        assert result[0] == chunk

    def test_rank_preserves_all_chunks(self):
        """All chunks are preserved after ranking"""
        chunks = [
            RetrievedChunk("a", "1", "text1", 0.5, "s"),
            RetrievedChunk("b", "2", "text2", 0.7, "s"),
            RetrievedChunk("c", "3", "text3", 0.6, "s"),
        ]
        result = rank(chunks)
        assert len(result) == 3


class TestRankWithDiversity:
    """Test diversity-constrained ranking"""

    def test_diversity_limits_per_doc(self):
        """Limits chunks from same document"""
        chunks = [
            RetrievedChunk("doc1", "0", "a", 0.9, "s"),
            RetrievedChunk("doc1", "1", "b", 0.8, "s"),
            RetrievedChunk("doc1", "2", "c", 0.7, "s"),
            RetrievedChunk("doc2", "0", "d", 0.6, "s"),
        ]

        result = rank_with_diversity(chunks, max_per_doc=2)

        doc1_count = sum(1 for c in result if c.doc_id == "doc1")
        assert doc1_count == 2
        assert len(result) == 3  # 2 from doc1, 1 from doc2

    def test_diversity_with_default(self):
        """Default max_per_doc=2 is applied"""
        chunks = [
            RetrievedChunk("doc1", "0", "a", 0.9, "s"),
            RetrievedChunk("doc1", "1", "b", 0.8, "s"),
            RetrievedChunk("doc1", "2", "c", 0.7, "s"),
        ]

        result = rank_with_diversity(chunks)
        assert len(result) == 2


class TestTopK:
    """Test top-k selection"""

    def test_top_k_returns_k_items(self):
        """Returns exactly k items when available"""
        chunks = [
            RetrievedChunk("a", "1", "x", 0.5, "s"),
            RetrievedChunk("b", "2", "y", 0.7, "s"),
            RetrievedChunk("c", "3", "z", 0.9, "s"),
        ]

        result = top_k(chunks, k=2)

        assert len(result) == 2
        assert result[0].score == 0.9
        assert result[1].score == 0.7

    def test_top_k_with_fewer_items(self):
        """Returns all items when k > len(chunks)"""
        chunks = [RetrievedChunk("a", "1", "x", 0.5, "s")]
        result = top_k(chunks, k=5)
        assert len(result) == 1
