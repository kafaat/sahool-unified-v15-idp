"""
Copilot RAG Service with Qdrant
خدمة RAG لـ Copilot مع Qdrant

Provides semantic search and document management for the Copilot.
Supports both Qdrant vector search and fallback keyword search.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from .embeddings import EmbeddingService, get_embedding_service

logger = structlog.get_logger(__name__)


@dataclass
class RAGDocument:
    """RAG document with metadata"""

    id: str
    text: str
    text_ar: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "text": self.text,
            "text_ar": self.text_ar,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SearchResult:
    """Search result with score"""

    document: RAGDocument
    score: float
    match_type: str = "semantic"


@dataclass
class RAGConfig:
    """Configuration for RAG service"""

    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "sahool_copilot_knowledge"

    # Search settings
    default_top_k: int = 5
    min_score_threshold: float = 0.3

    # Chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Feature flags
    use_qdrant: bool = True
    use_reranking: bool = False

    def __post_init__(self):
        """Load from environment"""
        self.qdrant_host = os.getenv("QDRANT_HOST", self.qdrant_host)
        self.qdrant_port = int(os.getenv("QDRANT_PORT", str(self.qdrant_port)))
        self.qdrant_collection = os.getenv("QDRANT_COLLECTION", self.qdrant_collection)
        self.use_qdrant = os.getenv("COPILOT_USE_QDRANT", "true").lower() == "true"


class CopilotRAGService:
    """
    RAG Service for Copilot with Qdrant integration.
    خدمة RAG لـ Copilot مع تكامل Qdrant

    Features:
    - Semantic search with vector embeddings
    - Keyword fallback for offline mode
    - Document chunking with overlap
    - Bilingual support (Arabic/English)
    - Tenant isolation
    """

    def __init__(
        self,
        config: RAGConfig | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        """Initialize RAG service"""
        self.config = config or RAGConfig()
        self.embedding_service = embedding_service or get_embedding_service()

        # In-memory fallback store
        self._documents: dict[str, RAGDocument] = {}

        # Qdrant client (lazy initialization)
        self._qdrant_client = None
        self._qdrant_available = False
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize RAG service and connections"""
        if self._initialized:
            return True

        # Initialize embedding service
        await self.embedding_service.initialize()

        # Try to connect to Qdrant
        if self.config.use_qdrant:
            self._qdrant_available = await self._init_qdrant()

        self._initialized = True
        logger.info(
            "RAG service initialized",
            qdrant_available=self._qdrant_available,
            embedding_dimension=self.embedding_service.dimension,
        )
        return True

    async def _init_qdrant(self) -> bool:
        """Initialize Qdrant connection and collection"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            self._qdrant_client = QdrantClient(
                host=self.config.qdrant_host,
                port=self.config.qdrant_port,
            )

            # Check if collection exists
            collections = self._qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.config.qdrant_collection not in collection_names:
                # Create collection
                self._qdrant_client.create_collection(
                    collection_name=self.config.qdrant_collection,
                    vectors_config=VectorParams(
                        size=self.embedding_service.dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    "Created Qdrant collection",
                    collection=self.config.qdrant_collection,
                )

            logger.info("Qdrant connected", host=self.config.qdrant_host)
            return True

        except ImportError:
            logger.warning("qdrant-client not installed")
            return False
        except Exception as e:
            logger.warning("Qdrant connection failed", error=str(e))
            return False

    async def add_document(
        self,
        text: str,
        text_ar: str | None = None,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> RAGDocument:
        """
        Add a document to the knowledge base.
        إضافة وثيقة إلى قاعدة المعرفة

        Args:
            text: Document text (English)
            text_ar: Document text (Arabic, optional)
            metadata: Document metadata
            doc_id: Optional document ID

        Returns:
            Created RAGDocument
        """
        if not self._initialized:
            await self.initialize()

        doc_id = doc_id or str(uuid.uuid4())
        metadata = metadata or {}

        # Generate embedding
        embedding_result = await self.embedding_service.embed(text)

        document = RAGDocument(
            id=doc_id,
            text=text,
            text_ar=text_ar,
            metadata=metadata,
            embedding=embedding_result.embedding,
        )

        # Store in memory (fallback)
        self._documents[doc_id] = document

        # Store in Qdrant if available
        if self._qdrant_available and self._qdrant_client:
            try:
                from qdrant_client.models import PointStruct

                self._qdrant_client.upsert(
                    collection_name=self.config.qdrant_collection,
                    points=[
                        PointStruct(
                            id=doc_id,
                            vector=embedding_result.embedding,
                            payload={
                                "text": text,
                                "text_ar": text_ar,
                                "metadata": metadata,
                                "created_at": document.created_at.isoformat(),
                            },
                        )
                    ],
                )
            except Exception as e:
                logger.error("Failed to add document to Qdrant", error=str(e))

        logger.info("Document added", doc_id=doc_id)
        return document

    async def add_documents_batch(
        self,
        documents: list[dict[str, Any]],
    ) -> list[RAGDocument]:
        """
        Add multiple documents in batch.
        إضافة وثائق متعددة دفعة واحدة
        """
        results = []
        for doc in documents:
            result = await self.add_document(
                text=doc["text"],
                text_ar=doc.get("text_ar"),
                metadata=doc.get("metadata"),
                doc_id=doc.get("id"),
            )
            results.append(result)
        return results

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        metadata_filter: dict[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> list[SearchResult]:
        """
        Search for relevant documents.
        البحث عن وثائق ذات صلة

        Args:
            query: Search query
            top_k: Number of results to return
            metadata_filter: Filter by metadata
            tenant_id: Tenant ID for isolation

        Returns:
            List of SearchResult
        """
        if not self._initialized:
            await self.initialize()

        top_k = top_k or self.config.default_top_k
        start_time = time.time()

        # Try Qdrant semantic search first
        if self._qdrant_available and self._qdrant_client:
            results = await self._search_qdrant(query, top_k, metadata_filter, tenant_id)
            if results:
                logger.info(
                    "Qdrant search completed",
                    query=query[:50],
                    results=len(results),
                    time_ms=(time.time() - start_time) * 1000,
                )
                return results

        # Fallback to keyword search
        results = await self._search_keywords(query, top_k, metadata_filter, tenant_id)
        logger.info(
            "Keyword search completed",
            query=query[:50],
            results=len(results),
            time_ms=(time.time() - start_time) * 1000,
        )
        return results

    async def _search_qdrant(
        self,
        query: str,
        top_k: int,
        metadata_filter: dict[str, Any] | None,
        tenant_id: str | None,
    ) -> list[SearchResult]:
        """Semantic search using Qdrant"""
        try:
            # Generate query embedding
            embedding_result = await self.embedding_service.embed(query)

            # Build filter
            qdrant_filter = None
            if metadata_filter or tenant_id:
                from qdrant_client.models import FieldCondition, Filter, MatchValue

                conditions = []
                if tenant_id:
                    conditions.append(
                        FieldCondition(
                            key="metadata.tenant_id",
                            match=MatchValue(value=tenant_id),
                        )
                    )
                if metadata_filter:
                    for key, value in metadata_filter.items():
                        conditions.append(
                            FieldCondition(
                                key=f"metadata.{key}",
                                match=MatchValue(value=value),
                            )
                        )
                if conditions:
                    qdrant_filter = Filter(must=conditions)

            # Search
            search_results = self._qdrant_client.search(
                collection_name=self.config.qdrant_collection,
                query_vector=embedding_result.embedding,
                limit=top_k,
                query_filter=qdrant_filter,
                score_threshold=self.config.min_score_threshold,
            )

            results = []
            for hit in search_results:
                document = RAGDocument(
                    id=str(hit.id),
                    text=hit.payload.get("text", ""),
                    text_ar=hit.payload.get("text_ar"),
                    metadata=hit.payload.get("metadata", {}),
                )
                results.append(
                    SearchResult(
                        document=document,
                        score=hit.score,
                        match_type="semantic",
                    )
                )

            return results

        except Exception as e:
            logger.error("Qdrant search failed", error=str(e))
            return []

    async def _search_keywords(
        self,
        query: str,
        top_k: int,
        metadata_filter: dict[str, Any] | None,
        tenant_id: str | None,
    ) -> list[SearchResult]:
        """Keyword-based fallback search"""
        query_words = {w.lower() for w in re.findall(r"\w+", query) if len(w) > 2}

        if not query_words:
            return []

        scored_results = []
        for doc_id, doc in self._documents.items():
            # Apply filters
            if tenant_id and doc.metadata.get("tenant_id") != tenant_id:
                continue
            if metadata_filter:
                skip = False
                for key, value in metadata_filter.items():
                    if doc.metadata.get(key) != value:
                        skip = True
                        break
                if skip:
                    continue

            # Calculate keyword overlap score
            doc_text = f"{doc.text} {doc.text_ar or ''}"
            doc_words = {w.lower() for w in re.findall(r"\w+", doc_text) if len(w) > 2}

            intersection = query_words & doc_words
            if not intersection:
                continue

            # TF-IDF-like scoring
            score = len(intersection) / (len(query_words) + 1)
            # Boost for exact phrase match
            if query.lower() in doc_text.lower():
                score += 0.3

            scored_results.append(
                SearchResult(
                    document=doc,
                    score=min(score, 1.0),
                    match_type="keyword",
                )
            )

        # Sort by score and return top k
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the knowledge base.
        حذف وثيقة من قاعدة المعرفة
        """
        # Delete from memory
        if doc_id in self._documents:
            del self._documents[doc_id]

        # Delete from Qdrant
        if self._qdrant_available and self._qdrant_client:
            try:
                self._qdrant_client.delete(
                    collection_name=self.config.qdrant_collection,
                    points_selector=[doc_id],
                )
            except Exception as e:
                logger.error("Failed to delete from Qdrant", error=str(e))
                return False

        logger.info("Document deleted", doc_id=doc_id)
        return True

    async def list_documents(
        self,
        tenant_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RAGDocument]:
        """
        List documents in the knowledge base.
        عرض قائمة الوثائق في قاعدة المعرفة

        Uses Qdrant scroll() when available, falls back to in-memory store.
        """
        if self._qdrant_available and self._qdrant_client:
            try:
                return await self._list_documents_qdrant(tenant_id, limit, offset)
            except Exception as e:
                logger.warning("Qdrant list_documents failed, falling back to memory", error=str(e))

        # Fallback to in-memory store
        documents = list(self._documents.values())

        if tenant_id:
            documents = [d for d in documents if d.metadata.get("tenant_id") == tenant_id]

        return documents[offset : offset + limit]

    async def _list_documents_qdrant(
        self,
        tenant_id: str | None,
        limit: int,
        offset: int,
    ) -> list[RAGDocument]:
        """List documents from Qdrant using scroll API"""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        scroll_filter = None
        if tenant_id:
            scroll_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.tenant_id",
                        match=MatchValue(value=tenant_id),
                    )
                ]
            )

        # Qdrant scroll doesn't support offset natively, so we fetch offset+limit
        # and slice. For large offsets, consider cursor-based pagination.
        # Run sync Qdrant client in threadpool to avoid blocking the event loop.
        fetch_limit = offset + limit
        results, _next_page = await asyncio.to_thread(
            self._qdrant_client.scroll,
            collection_name=self.config.qdrant_collection,
            scroll_filter=scroll_filter,
            limit=fetch_limit,
            with_payload=True,
            with_vectors=False,
        )

        documents = []
        for point in results[offset:]:
            payload = point.payload or {}
            documents.append(
                RAGDocument(
                    id=str(point.id),
                    text=payload.get("text", ""),
                    text_ar=payload.get("text_ar"),
                    metadata=payload.get("metadata", {}),
                )
            )

        return documents

    async def get_stats(self) -> dict[str, Any]:
        """Get RAG service statistics"""
        stats = {
            "total_documents": len(self._documents),
            "qdrant_available": self._qdrant_available,
            "embedding_dimension": self.embedding_service.dimension,
            "embedding_provider": self.embedding_service.config.provider.value,
        }

        if self._qdrant_available and self._qdrant_client:
            try:
                collection_info = self._qdrant_client.get_collection(self.config.qdrant_collection)
                stats["qdrant_points_count"] = collection_info.points_count
                stats["qdrant_vectors_count"] = collection_info.vectors_count
            except Exception:
                pass

        return stats

    def format_context_for_prompt(
        self,
        results: list[SearchResult],
        max_chars: int = 4000,
        language: str = "en",
    ) -> str:
        """
        Format search results for inclusion in LLM prompt.
        تنسيق نتائج البحث لتضمينها في prompt

        Args:
            results: Search results to format
            max_chars: Maximum total characters
            language: Preferred language ("ar" for Arabic, "en" for English)
        """
        if not results:
            return ""

        context_parts = []
        total_chars = 0

        for i, result in enumerate(results):
            doc = result.document
            # Select text based on requested language
            if language == "ar":
                text = doc.text_ar if doc.text_ar else doc.text
            else:
                text = doc.text if doc.text else (doc.text_ar or "")

            # Truncate if needed
            available_chars = max_chars - total_chars - 50
            if available_chars <= 0:
                break
            if len(text) > available_chars:
                text = text[:available_chars] + "..."

            part = f"[DOC {i + 1}] {text}"
            context_parts.append(part)
            total_chars += len(part)

            if total_chars >= max_chars:
                break

        return "\n\n".join(context_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_rag_service: CopilotRAGService | None = None


def get_rag_service() -> CopilotRAGService:
    """Get or create global RAG service"""
    global _rag_service
    if _rag_service is None:
        _rag_service = CopilotRAGService()
    return _rag_service
