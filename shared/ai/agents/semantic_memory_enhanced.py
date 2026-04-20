"""
Enhanced Semantic Memory with OT Embeddings
============================================
الذاكرة الدلالية المحسنة مع تضمينات النقل الأمثل

Integrates Optimal Transport (OT) embeddings with the agent memory system
for improved cross-lingual similarity matching and knowledge retrieval.

Features:
- OT-based semantic similarity for Arabic/English
- Cross-lingual knowledge retrieval
- Embedding-based memory clustering
- Similarity-aware memory consolidation
- Bilingual knowledge base support

Author: SAHOOL Platform Team
Created: January 2026
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from ..embeddings import EmbeddingConfig, EmbeddingProvider, EmbeddingsAdapter
from ..ot_embeddings import (
    BilingualOTMatcher,
    OTConfig,
)
from .memory_system import (
    MemoryPriority,
    MemoryType,
)

logger = structlog.get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class SemanticMemoryEntry:
    """
    Memory entry with semantic embedding.
    إدخال ذاكرة مع تضمين دلالي
    """

    entry_id: str
    content: str
    content_ar: str | None = None
    embedding: list[float] | None = None
    embedding_ar: list[float] | None = None
    memory_type: MemoryType = MemoryType.SEMANTIC
    priority: MemoryPriority = MemoryPriority.MEDIUM
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime | None = None
    access_count: int = 0
    importance_score: float = 0.5
    cluster_id: str | None = None


@dataclass
class SemanticCluster:
    """
    Cluster of semantically related memories.
    مجموعة من الذكريات ذات الصلة الدلالية
    """

    cluster_id: str
    name: str
    name_ar: str
    centroid: list[float] | None = None
    member_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SemanticSearchResult:
    """
    Result of semantic memory search.
    نتيجة البحث الدلالي في الذاكرة
    """

    entry: SemanticMemoryEntry
    similarity_score: float
    match_type: str  # exact, semantic, cross_lingual
    reasoning: str | None = None


# ============================================================================
# ENHANCED SEMANTIC MEMORY
# ============================================================================


class EnhancedSemanticMemory:
    """
    Semantic memory system enhanced with OT embeddings.
    نظام الذاكرة الدلالية المحسن بتضمينات النقل الأمثل

    Provides:
    - Embedding-based memory storage
    - Cross-lingual similarity search (Arabic/English)
    - Memory clustering and consolidation
    - Importance-weighted retrieval
    - Bilingual knowledge base

    Example:
        memory = EnhancedSemanticMemory()

        # Store memory with embedding
        await memory.store(
            content="Wheat requires 25mm irrigation during tillering",
            content_ar="يحتاج القمح إلى 25 ملم ري خلال مرحلة التفريع",
            tags=["irrigation", "wheat", "tillering"]
        )

        # Search in either language
        results = await memory.search("متى أسقي القمح؟")  # Arabic query
        results = await memory.search("wheat irrigation needs")  # English query
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        enable_ot_matching: bool = True,
        ot_config: OTConfig | None = None,
        max_memory_size: int = 10000,
    ):
        """
        Initialize enhanced semantic memory.
        تهيئة الذاكرة الدلالية المحسنة

        Args:
            embedding_provider: Provider for embeddings
            embedding_model: Model name for embeddings
            enable_ot_matching: Enable OT-based cross-lingual matching
            ot_config: Configuration for OT matcher
            max_memory_size: Maximum number of memories to store
        """
        # Initialize embeddings adapter
        self.embeddings = EmbeddingsAdapter(
            EmbeddingConfig(
                provider=embedding_provider,
                model=embedding_model,
                cache_enabled=True,
            )
        )

        # Initialize OT matcher for cross-lingual support
        self.enable_ot = enable_ot_matching
        if enable_ot_matching:
            self.ot_matcher = BilingualOTMatcher(
                config=ot_config,
                arabic_model=embedding_model,
                english_model=embedding_model,
            )
        else:
            self.ot_matcher = None

        # Memory storage
        self._memories: dict[str, SemanticMemoryEntry] = {}
        self._clusters: dict[str, SemanticCluster] = {}
        self._max_size = max_memory_size

        # Index for fast retrieval
        self._tag_index: dict[str, set[str]] = {}  # tag -> memory_ids
        self._embedding_cache: dict[str, list[float]] = {}

        logger.info(
            "enhanced_semantic_memory_initialized",
            provider=embedding_provider.value,
            model=embedding_model,
            ot_enabled=enable_ot_matching,
        )

    async def store(
        self,
        content: str,
        content_ar: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        importance: float = 0.5,
    ) -> SemanticMemoryEntry:
        """
        Store a memory with semantic embedding.
        تخزين ذاكرة مع تضمين دلالي

        Args:
            content: Memory content (English)
            content_ar: Memory content (Arabic)
            tags: Tags for categorization
            metadata: Additional metadata
            priority: Memory priority
            importance: Importance score (0-1)

        Returns:
            Stored memory entry
        """
        entry_id = str(uuid.uuid4())
        tags = tags or []
        metadata = metadata or {}

        # Generate embeddings
        try:
            embedding_result = await self.embeddings.embed(content)
            embedding = embedding_result.embedding

            embedding_ar = None
            if content_ar:
                embedding_ar_result = await self.embeddings.embed(content_ar)
                embedding_ar = embedding_ar_result.embedding
        except Exception as e:
            logger.warning("embedding_generation_failed", error=str(e))
            embedding = None
            embedding_ar = None

        # Create memory entry
        entry = SemanticMemoryEntry(
            entry_id=entry_id,
            content=content,
            content_ar=content_ar,
            embedding=embedding,
            embedding_ar=embedding_ar,
            priority=priority,
            tags=tags,
            metadata=metadata,
            importance_score=importance,
        )

        # Store memory
        self._memories[entry_id] = entry

        # Update tag index
        for tag in tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(entry_id)

        # Check memory size limit
        if len(self._memories) > self._max_size:
            await self._consolidate_memories()

        logger.info(
            "memory_stored",
            entry_id=entry_id,
            content_preview=content[:50],
            tags=tags,
        )

        return entry

    async def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
        tags_filter: list[str] | None = None,
        include_cross_lingual: bool = True,
    ) -> list[SemanticSearchResult]:
        """
        Search memories semantically.
        البحث الدلالي في الذكريات

        Args:
            query: Search query (any language)
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            tags_filter: Filter by tags
            include_cross_lingual: Include cross-lingual matches

        Returns:
            List of search results ranked by similarity
        """
        if not self._memories:
            return []

        # Detect query language
        is_arabic = any(ord(c) > 0x600 and ord(c) < 0x6FF for c in query)

        # Generate query embedding
        try:
            query_embedding_result = await self.embeddings.embed(query)
            query_embedding = query_embedding_result.embedding
        except Exception as e:
            logger.warning("query_embedding_failed", error=str(e))
            return []

        results: list[SemanticSearchResult] = []

        # Filter by tags if specified
        candidate_ids = set(self._memories.keys())
        if tags_filter:
            filtered_ids = set()
            for tag in tags_filter:
                if tag in self._tag_index:
                    filtered_ids.update(self._tag_index[tag])
            candidate_ids = candidate_ids.intersection(filtered_ids)

        # Calculate similarities
        for entry_id in candidate_ids:
            entry = self._memories[entry_id]

            # Get appropriate embedding based on query language
            if is_arabic and entry.embedding_ar:
                target_embedding = entry.embedding_ar
                match_type = "same_language"
            elif not is_arabic and entry.embedding:
                target_embedding = entry.embedding
                match_type = "same_language"
            elif include_cross_lingual:
                # Cross-lingual matching
                if is_arabic and entry.embedding:
                    target_embedding = entry.embedding
                    match_type = "cross_lingual"
                elif not is_arabic and entry.embedding_ar:
                    target_embedding = entry.embedding_ar
                    match_type = "cross_lingual"
                else:
                    continue
            else:
                continue

            # Calculate similarity
            if target_embedding:
                similarity = self._cosine_similarity(query_embedding, target_embedding)

                # Apply OT adjustment for cross-lingual
                if match_type == "cross_lingual" and self.enable_ot and self.ot_matcher:
                    try:
                        ot_result = await self.ot_matcher.match(
                            query,
                            entry.content if not is_arabic else (entry.content_ar or entry.content),
                        )
                        # Blend cosine and OT similarity
                        similarity = 0.6 * similarity + 0.4 * ot_result.similarity_score
                    except Exception:
                        pass

                if similarity >= min_similarity:
                    results.append(
                        SemanticSearchResult(
                            entry=entry,
                            similarity_score=similarity,
                            match_type=match_type,
                        )
                    )

                    # Update access count
                    entry.access_count += 1
                    entry.last_accessed = datetime.now(UTC)

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    async def search_similar(
        self,
        entry_id: str,
        top_k: int = 5,
        exclude_self: bool = True,
    ) -> list[SemanticSearchResult]:
        """
        Find memories similar to a given memory.
        البحث عن ذكريات مشابهة لذاكرة معينة

        Args:
            entry_id: ID of the reference memory
            top_k: Number of results
            exclude_self: Exclude the reference memory

        Returns:
            List of similar memories
        """
        if entry_id not in self._memories:
            return []

        reference = self._memories[entry_id]

        if not reference.embedding:
            return []

        results = []

        for other_id, other in self._memories.items():
            if exclude_self and other_id == entry_id:
                continue

            if other.embedding:
                similarity = self._cosine_similarity(reference.embedding, other.embedding)
                results.append(
                    SemanticSearchResult(
                        entry=other,
                        similarity_score=similarity,
                        match_type="semantic",
                    )
                )

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    async def cluster_memories(
        self,
        num_clusters: int = 10,
        min_cluster_size: int = 3,
    ) -> list[SemanticCluster]:
        """
        Cluster memories by semantic similarity.
        تجميع الذكريات حسب التشابه الدلالي

        Args:
            num_clusters: Target number of clusters
            min_cluster_size: Minimum members per cluster

        Returns:
            List of semantic clusters
        """
        # Simple k-means-like clustering
        entries_with_embeddings = [(eid, entry) for eid, entry in self._memories.items() if entry.embedding]

        if len(entries_with_embeddings) < num_clusters:
            num_clusters = max(1, len(entries_with_embeddings) // 2)

        if not entries_with_embeddings:
            return []

        # Initialize cluster centroids (pick random entries)
        import random

        sample_size = min(num_clusters, len(entries_with_embeddings))
        initial_samples = random.sample(entries_with_embeddings, sample_size)

        clusters = []
        for i, (eid, entry) in enumerate(initial_samples):
            cluster = SemanticCluster(
                cluster_id=str(uuid.uuid4()),
                name=f"Cluster {i + 1}",
                name_ar=f"المجموعة {i + 1}",
                centroid=entry.embedding,
                member_ids=[eid],
            )
            clusters.append(cluster)

        # Assign remaining entries to nearest cluster
        for eid, entry in entries_with_embeddings:
            if any(eid in c.member_ids for c in clusters):
                continue

            best_cluster = None
            best_similarity = -1

            for cluster in clusters:
                if cluster.centroid:
                    sim = self._cosine_similarity(entry.embedding, cluster.centroid)
                    if sim > best_similarity:
                        best_similarity = sim
                        best_cluster = cluster

            if best_cluster:
                best_cluster.member_ids.append(eid)
                entry.cluster_id = best_cluster.cluster_id

        # Filter small clusters
        clusters = [c for c in clusters if len(c.member_ids) >= min_cluster_size]

        # Store clusters
        for cluster in clusters:
            self._clusters[cluster.cluster_id] = cluster

        logger.info(
            "memories_clustered",
            num_clusters=len(clusters),
            total_memories=len(entries_with_embeddings),
        )

        return clusters

    async def get_by_tag(self, tag: str) -> list[SemanticMemoryEntry]:
        """Get all memories with a specific tag."""
        if tag not in self._tag_index:
            return []

        return [self._memories[eid] for eid in self._tag_index[tag] if eid in self._memories]

    async def get_recent(self, limit: int = 10) -> list[SemanticMemoryEntry]:
        """Get most recently created memories."""
        sorted_entries = sorted(
            self._memories.values(),
            key=lambda x: x.created_at,
            reverse=True,
        )
        return sorted_entries[:limit]

    async def get_most_accessed(self, limit: int = 10) -> list[SemanticMemoryEntry]:
        """Get most frequently accessed memories."""
        sorted_entries = sorted(
            self._memories.values(),
            key=lambda x: x.access_count,
            reverse=True,
        )
        return sorted_entries[:limit]

    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        if entry_id not in self._memories:
            return False

        entry = self._memories[entry_id]

        # Remove from tag index
        for tag in entry.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(entry_id)

        del self._memories[entry_id]
        return True

    async def _consolidate_memories(self) -> int:
        """
        Consolidate memories when storage is full.
        Remove low-importance, rarely accessed memories.
        """
        # Calculate priority score for each memory
        scored = []
        for eid, entry in self._memories.items():
            # Score based on: importance, access count, recency
            age_days = (datetime.now(UTC) - entry.created_at).days
            recency_factor = max(0.1, 1 - (age_days / 365))

            score = entry.importance_score * 0.4 + min(1.0, entry.access_count / 100) * 0.3 + recency_factor * 0.3
            scored.append((eid, score))

        # Sort by score and remove bottom 20%
        scored.sort(key=lambda x: x[1])
        to_remove = scored[: len(scored) // 5]

        for eid, _ in to_remove:
            await self.delete(eid)

        logger.info("memories_consolidated", removed=len(to_remove))
        return len(to_remove)

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_stats(self) -> dict[str, Any]:
        """Get memory system statistics."""
        return {
            "total_memories": len(self._memories),
            "total_clusters": len(self._clusters),
            "total_tags": len(self._tag_index),
            "ot_enabled": self.enable_ot,
            "memories_by_priority": {
                p.value: sum(1 for m in self._memories.values() if m.priority == p) for p in MemoryPriority
            },
            "average_access_count": (
                sum(m.access_count for m in self._memories.values()) / len(self._memories) if self._memories else 0
            ),
        }


# ============================================================================
# INTEGRATION WITH AGENT MEMORY SYSTEM
# ============================================================================


class SemanticMemoryMixin:
    """
    Mixin to add enhanced semantic memory to agents.
    خليط لإضافة الذاكرة الدلالية المحسنة للوكلاء

    Add this mixin to any agent to enable semantic memory capabilities.

    Example:
        class MyAgent(BaseAutonomousAgent, SemanticMemoryMixin):
            def __init__(self, ...):
                super().__init__(...)
                self.init_semantic_memory()

            async def remember(self, knowledge: str, knowledge_ar: str = None):
                await self.semantic_store(knowledge, knowledge_ar)

            async def recall(self, query: str) -> list:
                return await self.semantic_search(query)
    """

    _semantic_memory: EnhancedSemanticMemory | None = None

    def init_semantic_memory(
        self,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        enable_ot: bool = True,
    ) -> None:
        """Initialize semantic memory for the agent."""
        self._semantic_memory = EnhancedSemanticMemory(
            embedding_model=embedding_model,
            enable_ot_matching=enable_ot,
        )

    async def semantic_store(
        self,
        content: str,
        content_ar: str | None = None,
        tags: list[str] | None = None,
        importance: float = 0.5,
    ) -> SemanticMemoryEntry:
        """Store knowledge in semantic memory."""
        if not self._semantic_memory:
            self.init_semantic_memory()

        return await self._semantic_memory.store(
            content=content,
            content_ar=content_ar,
            tags=tags,
            importance=importance,
        )

    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> list[SemanticSearchResult]:
        """Search semantic memory."""
        if not self._semantic_memory:
            return []

        return await self._semantic_memory.search(
            query=query,
            top_k=top_k,
            min_similarity=min_similarity,
        )

    def get_semantic_memory_stats(self) -> dict[str, Any]:
        """Get semantic memory statistics."""
        if not self._semantic_memory:
            return {"initialized": False}

        stats = self._semantic_memory.get_stats()
        stats["initialized"] = True
        return stats


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_enhanced_semantic_memory(
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
    enable_ot: bool = True,
) -> EnhancedSemanticMemory:
    """
    Factory function to create enhanced semantic memory.
    دالة لإنشاء ذاكرة دلالية محسنة
    """
    return EnhancedSemanticMemory(
        embedding_model=embedding_model,
        enable_ot_matching=enable_ot,
    )
