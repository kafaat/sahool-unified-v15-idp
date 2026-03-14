# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Vector Store Integration
# تكامل مخزن المتجهات لقاعدة المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provides vector store integration for the knowledge ingestion pipeline:
#   - Store documents (whole or chunked) as vector embeddings
#   - Search with domain, region, and credibility filters
#   - Bilingual (Arabic/English) search with result merging
#   - Collection-level statistics and management
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from shared.ai.knowledge._logging import get_logger

from .ingestion.chunker import TextChunk
from .models import BaseKnowledgeDocument, KnowledgeDomain

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Protocols
# ─────────────────────────────────────────────────────────────────────────────


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers.
    بروتوكول لمزودي التضمينات"""

    def embed(self, text: str) -> list[float]: ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class VectorSearchResult:
    """Single vector search result.
    نتيجة بحث متجهي واحدة"""

    document_id: str
    content: str
    content_ar: str = ""
    score: float = 0.0
    collection: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class _StoredVector:
    """Internal representation of a stored vector entry.
    تمثيل داخلي لعنصر متجه مخزن"""

    vector_id: str
    document_id: str
    content: str
    content_ar: str
    collection: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Vector Store
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeVectorStore:
    """Vector store integration for knowledge base.
    تكامل مخزن المتجهات لقاعدة المعرفة

    Stores knowledge documents (whole or chunked) as vector embeddings and
    provides filtered similarity search with bilingual support.
    """

    def __init__(
        self,
        collection_prefix: str = "kb_",
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self._collection_prefix = collection_prefix
        self._embedding_provider = embedding_provider
        # In-memory storage; a production implementation would delegate to
        # shared.ai.vector_store backends (SQLite, Qdrant, etc.).
        self._vectors: dict[str, _StoredVector] = {}
        # Mapping from document_id to list of vector_ids for deletion
        self._doc_index: dict[str, list[str]] = {}
        logger.info(
            "knowledge_vector_store_init",
            collection_prefix=collection_prefix,
            has_embedding_provider=embedding_provider is not None,
        )

    # ─── Public API ───────────────────────────────────────────────────────

    def store_document(
        self,
        document: BaseKnowledgeDocument,
        chunks: list[TextChunk] | None = None,
    ) -> list[str]:
        """Store document (optionally chunked) in vector store. Returns list of stored IDs.
        تخزين وثيقة (مقطعة اختياريا) في مخزن المتجهات. يرجع قائمة المعرفات المخزنة"""
        collection = self._prefixed_collection(document._get_collection())
        base_metadata = self._build_document_metadata(document)
        stored_ids: list[str] = []

        if chunks:
            for chunk in chunks:
                vector_id = self._store_single(
                    document_id=document.id,
                    content=chunk.content,
                    content_ar=chunk.content_ar,
                    collection=collection,
                    metadata={
                        **base_metadata,
                        "chunk_index": chunk.chunk_index,
                        "total_chunks": chunk.total_chunks,
                        "heading": chunk.heading,
                        "heading_ar": chunk.heading_ar,
                        **chunk.metadata,
                    },
                )
                stored_ids.append(vector_id)
        else:
            vector_id = self._store_single(
                document_id=document.id,
                content=document.content,
                content_ar=document.content_ar,
                collection=collection,
                metadata=base_metadata,
            )
            stored_ids.append(vector_id)

        logger.info(
            "document_stored",
            document_id=document.id,
            collection=collection,
            vector_count=len(stored_ids),
            chunked=chunks is not None,
        )
        return stored_ids

    def search(
        self,
        query: str,
        collection: str | None = None,
        top_k: int = 10,
        domain_filter: KnowledgeDomain | None = None,
        region_filter: list[str] | None = None,
        min_credibility: int = 1,
    ) -> list[VectorSearchResult]:
        """Search knowledge base with optional filters.
        البحث في قاعدة المعرفة مع مرشحات اختيارية"""
        if not self._embedding_provider:
            logger.warning("search_skipped_no_embedding_provider")
            return []

        query_embedding = self._embedding_provider.embed(query)
        metadata_filter = self._build_metadata_filter(domain_filter, region_filter, min_credibility)
        prefixed = self._prefixed_collection(collection) if collection else None

        candidates = self._filter_vectors(prefixed, metadata_filter)
        scored = self._rank_by_similarity(query_embedding, candidates)

        results = [
            VectorSearchResult(
                document_id=v.document_id,
                content=v.content,
                content_ar=v.content_ar,
                score=score,
                collection=v.collection,
                metadata=v.metadata,
            )
            for score, v in scored[:top_k]
        ]

        logger.debug(
            "search_completed",
            query_length=len(query),
            candidates=len(candidates),
            results=len(results),
            collection=prefixed,
        )
        return results

    def search_bilingual(
        self,
        query: str,
        query_ar: str = "",
        **kwargs: Any,
    ) -> list[VectorSearchResult]:
        """Search with both English and Arabic queries, merge and deduplicate results.
        البحث بالاستعلام الإنجليزي والعربي ودمج النتائج"""
        top_k = kwargs.pop("top_k", 10)

        # Retrieve up to top_k from each query to ensure enough merged results
        en_results = self.search(query, top_k=top_k, **kwargs) if query else []
        ar_results = self.search(query_ar, top_k=top_k, **kwargs) if query_ar else []

        # Merge and deduplicate, keeping highest score per (document_id, chunk_index)
        seen: dict[str, VectorSearchResult] = {}
        for result in en_results + ar_results:
            key = f"{result.document_id}:{result.metadata.get('chunk_index', 0)}"
            if key not in seen or result.score > seen[key].score:
                seen[key] = result

        merged = sorted(seen.values(), key=lambda r: r.score, reverse=True)[:top_k]

        logger.debug(
            "bilingual_search_completed",
            en_results=len(en_results),
            ar_results=len(ar_results),
            merged_results=len(merged),
        )
        return merged

    def delete_document(self, document_id: str) -> bool:
        """Delete all vectors for a document.
        حذف جميع المتجهات لوثيقة"""
        vector_ids = self._doc_index.pop(document_id, [])
        if not vector_ids:
            logger.debug("delete_document_not_found", document_id=document_id)
            return False

        for vid in vector_ids:
            self._vectors.pop(vid, None)

        logger.info(
            "document_deleted",
            document_id=document_id,
            vectors_removed=len(vector_ids),
        )
        return True

    def get_collection_stats(self, collection: str | None = None) -> dict[str, Any]:
        """Get vector count and metadata stats per collection.
        الحصول على إحصائيات العدد والبيانات الوصفية لكل مجموعة"""
        prefixed = self._prefixed_collection(collection) if collection else None

        stats: dict[str, dict[str, Any]] = {}
        for v in self._vectors.values():
            if prefixed and v.collection != prefixed:
                continue
            coll = v.collection
            if coll not in stats:
                stats[coll] = {"vector_count": 0, "document_ids": set()}
            stats[coll]["vector_count"] += 1
            stats[coll]["document_ids"].add(v.document_id)

        # Convert sets to counts for serialisability
        result: dict[str, Any] = {}
        for coll, info in stats.items():
            result[coll] = {
                "vector_count": info["vector_count"],
                "document_count": len(info["document_ids"]),
            }

        result["total_vectors"] = sum(v["vector_count"] for v in result.values())
        result["total_collections"] = len(stats)

        logger.debug("collection_stats", stats=result)
        return result

    # ─── Internal Helpers ─────────────────────────────────────────────────

    def _prefixed_collection(self, collection: str) -> str:
        """Add collection prefix if not already present."""
        if collection.startswith(self._collection_prefix):
            return collection
        return f"{self._collection_prefix}{collection}"

    def _store_single(
        self,
        document_id: str,
        content: str,
        content_ar: str,
        collection: str,
        metadata: dict[str, Any],
    ) -> str:
        """Embed and store a single text entry."""
        vector_id = f"vec_{uuid.uuid4().hex[:12]}"

        text_for_embedding = f"{content} {content_ar}".strip()
        embedding: list[float] = []
        if self._embedding_provider and text_for_embedding:
            embedding = self._embedding_provider.embed(text_for_embedding)

        stored = _StoredVector(
            vector_id=vector_id,
            document_id=document_id,
            content=content,
            content_ar=content_ar,
            collection=collection,
            embedding=embedding,
            metadata=metadata,
        )
        self._vectors[vector_id] = stored
        self._doc_index.setdefault(document_id, []).append(vector_id)
        return vector_id

    def _build_document_metadata(self, document: BaseKnowledgeDocument) -> dict[str, Any]:
        """Extract metadata dict from a knowledge document for storage."""
        return {
            "domain": document.domain.value,
            "tags": document.tags,
            "regions": document.geospatial.applicable_regions,
            "climate_zones": document.geospatial.climate_zones,
            "credibility": document.source.credibility.value,
            "verification_status": document.verification_status.value,
            "hierarchy_level": document.fresh.hierarchy_level.value,
            "sensitivity": document.fresh.sensitivity.value,
            "seasonal_relevance": document.fresh.seasonal_relevance.value,
            "source_name": document.source.source_name,
            "title": document.title,
            "title_ar": document.title_ar,
            "version": document.version,
        }

    def _build_metadata_filter(
        self,
        domain_filter: KnowledgeDomain | None,
        region_filter: list[str] | None,
        min_credibility: int,
    ) -> dict[str, Any]:
        """Build metadata filter dict for vector store queries.
        بناء مرشح البيانات الوصفية لاستعلامات مخزن المتجهات"""
        filters: dict[str, Any] = {}
        if domain_filter is not None:
            filters["domain"] = domain_filter.value
        if region_filter:
            filters["regions"] = region_filter
        if min_credibility > 1:
            filters["min_credibility"] = min_credibility
        return filters

    def _filter_vectors(
        self,
        collection: str | None,
        metadata_filter: dict[str, Any],
    ) -> list[_StoredVector]:
        """Filter stored vectors by collection and metadata criteria."""
        candidates: list[_StoredVector] = []
        for v in self._vectors.values():
            if collection and v.collection != collection:
                continue
            if not v.embedding:
                continue
            if not self._matches_filter(v.metadata, metadata_filter):
                continue
            candidates.append(v)
        return candidates

    def _matches_filter(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        """Check if metadata matches all filter criteria."""
        if not filters:
            return True

        # Domain exact match
        if "domain" in filters and metadata.get("domain") != filters["domain"]:
            return False

        # Region overlap: at least one requested region must be present
        if "regions" in filters:
            doc_regions = metadata.get("regions", [])
            if not any(r in doc_regions for r in filters["regions"]):
                return False

        # Credibility minimum threshold
        if "min_credibility" in filters:
            doc_cred = metadata.get("credibility", 1)
            if doc_cred < filters["min_credibility"]:
                return False

        return True

    def _rank_by_similarity(
        self,
        query_embedding: list[float],
        candidates: list[_StoredVector],
    ) -> list[tuple[float, _StoredVector]]:
        """Rank candidates by cosine similarity to query embedding."""
        scored: list[tuple[float, _StoredVector]] = []
        for v in candidates:
            score = self._cosine_similarity(query_embedding, v.embedding)
            scored.append((score, v))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)
