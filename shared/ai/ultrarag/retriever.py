# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Retriever - Multi-Strategy Retrieval System
# نظام الاسترجاع متعدد الاستراتيجيات
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
import hashlib
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .models import (
    KnowledgeChunk,
    RetrievalResult,
    RetrievalStrategy,
)

logger = structlog.get_logger(__name__)


@dataclass
class RetrievalConfig:
    """Configuration for retrieval | تكوين الاسترجاع"""
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 10
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    min_score_threshold: float = 0.1
    use_query_expansion: bool = True
    max_query_terms: int = 10
    collection: str = "default"
    filters: Dict[str, Any] = field(default_factory=dict)


class Retriever(ABC):
    """Abstract base class for retrievers | فئة أساسية مجردة للمسترجعات"""

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> List[RetrievalResult]:
        """Retrieve relevant chunks for a query"""
        pass

    @abstractmethod
    async def add_documents(
        self,
        chunks: List[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to the retriever index"""
        pass


class DenseRetriever(Retriever):
    """Dense vector-based retriever using embeddings | مسترجع كثيف يعتمد على المتجهات"""

    def __init__(
        self,
        vector_store: Any,  # VectorStore from shared/ai/vector_store.py
        embedding_service: Any,  # EmbeddingsAdapter from shared/ai/embeddings.py
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self._cache: Dict[str, List[float]] = {}
        self._cache_max_size = 10000

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> List[RetrievalResult]:
        """Retrieve using dense vector similarity"""
        start_time = time.time()

        try:
            # Get query embedding (with caching)
            query_vector = await self._get_embedding(query)

            # Search vector store
            search_results = await self.vector_store.search(
                vector=query_vector,
                collection=config.collection,
                top_k=config.top_k,
                filter=config.filters if config.filters else None,
            )

            # Convert to RetrievalResult
            results = []
            for i, result in enumerate(search_results):
                chunk = KnowledgeChunk(
                    id=result.id,
                    text=result.text or "",
                    text_ar=result.metadata.get("text_ar") if result.metadata else None,
                    document_id=result.metadata.get("document_id", "") if result.metadata else "",
                    collection=config.collection,
                    metadata=result.metadata or {},
                )
                results.append(RetrievalResult(
                    chunk=chunk,
                    score=result.score,
                    retrieval_method="dense",
                    rank=i + 1,
                ))

            # Filter by minimum score
            results = [r for r in results if r.score >= config.min_score_threshold]

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "dense_retrieval_complete",
                query_length=len(query),
                results_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("dense_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: List[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents with embeddings to vector store"""
        try:
            texts = [c.text for c in chunks]
            ids = [c.id for c in chunks]
            metadatas = [
                {
                    **c.metadata,
                    "text_ar": c.text_ar,
                    "document_id": c.document_id,
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ]

            # Generate embeddings
            embeddings = await self._get_embeddings_batch(texts)

            # Add to vector store
            await self.vector_store.add(
                texts=texts,
                vectors=embeddings,
                ids=ids,
                metadatas=metadatas,
                collection=collection,
            )

            logger.info(
                "documents_added",
                count=len(chunks),
                collection=collection,
            )
            return True

        except Exception as e:
            logger.error("add_documents_error", error=str(e))
            return False

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding with caching"""
        cache_key = hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = await self.embedding_service.embed(text)
        vector = result.vector

        # Cache management
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._cache.keys())[:1000]
            for key in keys_to_remove:
                del self._cache[key]

        self._cache[cache_key] = vector
        return vector

    async def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        results = await self.embedding_service.embed_batch(texts)
        return [r.vector for r in results]


class SparseRetriever(Retriever):
    """BM25-based sparse retriever | مسترجع متفرق يعتمد على BM25"""

    def __init__(self, vector_store: Any):
        self.vector_store = vector_store
        self._index: Dict[str, Dict[str, List[Tuple[str, int]]]] = {}  # collection -> term -> [(doc_id, count)]
        self._doc_lengths: Dict[str, Dict[str, int]] = {}  # collection -> doc_id -> length
        self._avg_doc_length: Dict[str, float] = {}  # collection -> avg_length
        self._k1 = 1.5
        self._b = 0.75

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> List[RetrievalResult]:
        """Retrieve using BM25 scoring"""
        start_time = time.time()

        try:
            # Tokenize query
            query_terms = self._tokenize(query)

            if not query_terms:
                return []

            collection = config.collection

            # Calculate BM25 scores
            scores: Dict[str, float] = {}
            N = len(self._doc_lengths.get(collection, {}))

            if N == 0:
                logger.warning("sparse_retrieval_empty_index", collection=collection)
                return []

            avg_dl = self._avg_doc_length.get(collection, 1.0)

            for term in query_terms:
                if collection not in self._index or term not in self._index[collection]:
                    continue

                doc_freqs = self._index[collection][term]
                df = len(doc_freqs)
                idf = self._calculate_idf(N, df)

                for doc_id, tf in doc_freqs:
                    dl = self._doc_lengths.get(collection, {}).get(doc_id, 1)
                    score = self._calculate_bm25_score(tf, idf, dl, avg_dl)

                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += score

            # Sort by score and get top_k
            sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_docs = sorted_docs[:config.top_k]

            # Convert to RetrievalResult
            results = []
            for i, (doc_id, score) in enumerate(top_docs):
                if score < config.min_score_threshold:
                    continue

                # Fetch document from vector store
                doc = await self.vector_store.get(doc_id, collection=collection)
                if doc:
                    chunk = KnowledgeChunk(
                        id=doc_id,
                        text=doc.text or "",
                        text_ar=doc.metadata.get("text_ar") if doc.metadata else None,
                        document_id=doc.metadata.get("document_id", "") if doc.metadata else "",
                        collection=collection,
                        metadata=doc.metadata or {},
                    )
                    results.append(RetrievalResult(
                        chunk=chunk,
                        score=score,
                        retrieval_method="sparse",
                        rank=i + 1,
                    ))

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "sparse_retrieval_complete",
                query_length=len(query),
                results_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("sparse_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: List[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Build BM25 index from documents"""
        try:
            if collection not in self._index:
                self._index[collection] = {}
                self._doc_lengths[collection] = {}

            total_length = 0

            for chunk in chunks:
                terms = self._tokenize(chunk.text)
                self._doc_lengths[collection][chunk.id] = len(terms)
                total_length += len(terms)

                term_counts: Dict[str, int] = {}
                for term in terms:
                    term_counts[term] = term_counts.get(term, 0) + 1

                for term, count in term_counts.items():
                    if term not in self._index[collection]:
                        self._index[collection][term] = []
                    self._index[collection][term].append((chunk.id, count))

            # Update average document length
            num_docs = len(self._doc_lengths[collection])
            self._avg_doc_length[collection] = total_length / num_docs if num_docs > 0 else 1.0

            logger.info(
                "sparse_index_updated",
                collection=collection,
                num_docs=num_docs,
                num_terms=len(self._index[collection]),
            )
            return True

        except Exception as e:
            logger.error("sparse_add_documents_error", error=str(e))
            return False

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization with Arabic support"""
        # Lowercase and split on non-alphanumeric (preserving Arabic)
        text = text.lower()
        # Pattern that matches word characters including Arabic
        tokens = re.findall(r'[\w\u0600-\u06FF]+', text)
        # Remove stopwords and short tokens
        tokens = [t for t in tokens if len(t) > 2]
        return tokens

    def _calculate_idf(self, N: int, df: int) -> float:
        """Calculate inverse document frequency"""
        import math
        return math.log((N - df + 0.5) / (df + 0.5) + 1)

    def _calculate_bm25_score(self, tf: int, idf: float, dl: int, avg_dl: float) -> float:
        """Calculate BM25 score for a term"""
        numerator = tf * (self._k1 + 1)
        denominator = tf + self._k1 * (1 - self._b + self._b * (dl / avg_dl))
        return idf * (numerator / denominator)


class HybridRetriever(Retriever):
    """Hybrid retriever combining dense and sparse methods | مسترجع هجين يجمع بين الكثيف والمتفرق"""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> List[RetrievalResult]:
        """Retrieve using both dense and sparse methods, then fuse results"""
        start_time = time.time()

        try:
            # Run both retrievers in parallel
            dense_task = asyncio.create_task(
                self.dense_retriever.retrieve(query, config)
            )
            sparse_task = asyncio.create_task(
                self.sparse_retriever.retrieve(query, config)
            )

            dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)

            # Reciprocal Rank Fusion (RRF)
            k = 60  # RRF constant
            fused_scores: Dict[str, Tuple[float, KnowledgeChunk]] = {}

            # Process dense results
            for result in dense_results:
                doc_id = result.chunk.id
                rrf_score = config.dense_weight / (k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk)
                else:
                    current_score, chunk = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk)

            # Process sparse results
            for result in sparse_results:
                doc_id = result.chunk.id
                rrf_score = config.sparse_weight / (k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk)
                else:
                    current_score, chunk = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk)

            # Sort by fused score
            sorted_results = sorted(
                fused_scores.items(),
                key=lambda x: x[1][0],
                reverse=True
            )

            # Create final results
            results = []
            for i, (doc_id, (score, chunk)) in enumerate(sorted_results[:config.top_k]):
                results.append(RetrievalResult(
                    chunk=chunk,
                    score=score,
                    retrieval_method="hybrid",
                    rank=i + 1,
                ))

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "hybrid_retrieval_complete",
                query_length=len(query),
                dense_count=len(dense_results),
                sparse_count=len(sparse_results),
                fused_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("hybrid_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: List[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to both dense and sparse indices"""
        dense_ok = await self.dense_retriever.add_documents(chunks, collection)
        sparse_ok = await self.sparse_retriever.add_documents(chunks, collection)
        return dense_ok and sparse_ok


class AdaptiveRetriever(Retriever):
    """Adaptive retriever that selects strategy based on query | مسترجع تكيفي يختار الاستراتيجية بناءً على الاستعلام"""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        hybrid_retriever: HybridRetriever,
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.hybrid_retriever = hybrid_retriever

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> List[RetrievalResult]:
        """Adaptively select retrieval strategy based on query characteristics"""
        # Analyze query
        query_type = self._analyze_query(query)

        logger.info(
            "adaptive_retrieval_strategy",
            query_type=query_type,
            query_preview=query[:50],
        )

        # Select strategy based on query type
        if query_type == "keyword":
            # Short, keyword-like queries benefit from sparse retrieval
            return await self.sparse_retriever.retrieve(query, config)
        elif query_type == "semantic":
            # Long, semantic queries benefit from dense retrieval
            return await self.dense_retriever.retrieve(query, config)
        else:
            # Mixed queries use hybrid approach
            return await self.hybrid_retriever.retrieve(query, config)

    async def add_documents(
        self,
        chunks: List[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to all retriever indices"""
        return await self.hybrid_retriever.add_documents(chunks, collection)

    def _analyze_query(self, query: str) -> str:
        """Analyze query to determine best retrieval strategy"""
        words = query.split()
        num_words = len(words)

        # Check for question words
        question_words = {"what", "how", "why", "when", "where", "who", "which", "ما", "كيف", "لماذا", "متى", "أين", "من"}
        has_question_word = any(w.lower() in question_words for w in words)

        # Check for technical terms or specific patterns
        has_special_chars = bool(re.search(r'[:\-_/\\.]', query))

        if num_words <= 3 and not has_question_word:
            return "keyword"
        elif num_words >= 8 or has_question_word:
            return "semantic"
        else:
            return "hybrid"


# Export classes
__all__ = [
    "Retriever",
    "DenseRetriever",
    "SparseRetriever",
    "HybridRetriever",
    "AdaptiveRetriever",
    "RetrievalConfig",
    "RetrievalResult",
]
