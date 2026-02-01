"""
Multi-Level Memory System for AI Agents
========================================
نظام الذاكرة متعدد المستويات لوكلاء الذكاء الاصطناعي

Implements a comprehensive memory system with:
- Working Memory: Current task state
- Episodic Memory: Specific past events with context
- Semantic Memory: Factual knowledge & patterns
- Procedural Memory: How to perform tasks (skill library)

Based on cognitive science models of human memory.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any
import uuid

import structlog

logger = structlog.get_logger()


# ============================================================================
# ENUMS & TYPES
# ============================================================================


class MemoryType(str, Enum):
    """أنواع الذاكرة"""
    WORKING = "working"           # Current task state
    EPISODIC = "episodic"         # Specific events
    SEMANTIC = "semantic"         # Factual knowledge
    PROCEDURAL = "procedural"     # Skills & procedures


class MemoryPriority(str, Enum):
    """أولوية الذاكرة"""
    CRITICAL = "critical"         # Never forget
    HIGH = "high"                 # Keep for long time
    MEDIUM = "medium"             # Standard retention
    LOW = "low"                   # Can be forgotten


class RetrievalStrategy(str, Enum):
    """استراتيجية الاسترجاع"""
    EXACT = "exact"               # Exact match
    SIMILARITY = "similarity"     # Semantic similarity
    RECENCY = "recency"           # Most recent first
    RELEVANCE = "relevance"       # Most relevant to context
    COMBINED = "combined"         # Combine multiple strategies


# ============================================================================
# MEMORY ENTRIES
# ============================================================================


@dataclass
class MemoryEntry:
    """
    Base class for all memory entries.
    الفئة الأساسية لجميع إدخالات الذاكرة
    """
    memory_id: str
    memory_type: MemoryType
    content: Any
    content_ar: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    priority: MemoryPriority = MemoryPriority.MEDIUM
    ttl_hours: int | None = None  # None = never expires
    embedding: list[float] | None = None  # Vector embedding for similarity search
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "content_ar": self.content_ar,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "priority": self.priority.value,
            "ttl_hours": self.ttl_hours,
            "metadata": self.metadata,
            "tags": self.tags,
        }

    @property
    def is_expired(self) -> bool:
        """Check if this memory has expired."""
        if self.ttl_hours is None:
            return False
        expiry_time = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now(UTC) > expiry_time

    def touch(self) -> None:
        """Update access time and count."""
        self.last_accessed = datetime.now(UTC)
        self.access_count += 1


@dataclass
class EpisodicMemory(MemoryEntry):
    """
    Episodic Memory - Specific past events with context.
    الذاكرة العرضية - أحداث ماضية محددة مع السياق

    Stores:
    - What happened (event)
    - When it happened (timestamp)
    - Where it happened (context)
    - What was the outcome
    - Emotional valence (positive/negative)
    """
    event_type: str = ""           # Type of event
    context: dict[str, Any] = field(default_factory=dict)  # Situational context
    actors: list[str] = field(default_factory=list)  # Who was involved
    outcome: str = ""              # What happened
    outcome_ar: str = ""
    success: bool = True           # Was it successful
    emotional_valence: float = 0.0  # -1 (negative) to 1 (positive)
    lessons_learned: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.memory_type = MemoryType.EPISODIC


@dataclass
class SemanticMemory(MemoryEntry):
    """
    Semantic Memory - Factual knowledge & patterns.
    الذاكرة الدلالية - المعرفة الواقعية والأنماط

    Stores:
    - Facts about the world
    - Relationships between concepts
    - Patterns observed over time
    - Statistical information
    """
    category: str = ""             # Knowledge category
    concepts: list[str] = field(default_factory=list)  # Related concepts
    relationships: list[dict[str, str]] = field(default_factory=list)  # Concept relationships
    confidence: float = 0.8        # How confident in this knowledge
    source: str = ""               # Where this knowledge came from
    verified: bool = False         # Has it been verified

    def __post_init__(self):
        self.memory_type = MemoryType.SEMANTIC


@dataclass
class ProceduralMemory(MemoryEntry):
    """
    Procedural Memory - How to perform tasks (skills).
    الذاكرة الإجرائية - كيفية أداء المهام (المهارات)

    Stores:
    - Step-by-step procedures
    - Conditions for applying the procedure
    - Success rate history
    - Variations and alternatives
    """
    skill_name: str = ""           # Name of the skill/procedure
    skill_name_ar: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)  # Procedure steps
    preconditions: list[str] = field(default_factory=list)  # When to apply
    postconditions: list[str] = field(default_factory=list)  # Expected outcomes
    success_rate: float = 0.0      # Historical success rate
    execution_count: int = 0       # How many times executed
    average_duration_ms: float = 0.0
    variations: list[str] = field(default_factory=list)  # Alternative approaches

    def __post_init__(self):
        self.memory_type = MemoryType.PROCEDURAL

    def update_success_rate(self, success: bool, duration_ms: float) -> None:
        """Update success rate with new execution."""
        self.execution_count += 1
        # Exponential moving average
        alpha = 0.1
        new_success = 1.0 if success else 0.0
        self.success_rate = (1 - alpha) * self.success_rate + alpha * new_success
        self.average_duration_ms = (1 - alpha) * self.average_duration_ms + alpha * duration_ms


@dataclass
class WorkingMemory:
    """
    Working Memory - Current task state.
    الذاكرة العاملة - حالة المهمة الحالية

    Short-term storage for active processing.
    Limited capacity, regularly updated.
    """
    task_id: str = ""
    task_description: str = ""
    task_description_ar: str = ""
    current_goal: str = ""
    current_goal_ar: str = ""
    focus_items: list[dict[str, Any]] = field(default_factory=list)  # Items in focus
    scratch_pad: dict[str, Any] = field(default_factory=dict)  # Temporary calculations
    context_stack: list[dict[str, Any]] = field(default_factory=list)  # Nested contexts
    last_action: dict[str, Any] | None = None
    last_observation: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    MAX_FOCUS_ITEMS = 7  # Miller's Law: 7 ± 2 items

    def add_to_focus(self, item: dict[str, Any]) -> None:
        """Add item to focus, maintaining capacity limit."""
        self.focus_items.append(item)
        if len(self.focus_items) > self.MAX_FOCUS_ITEMS:
            # Remove oldest item
            self.focus_items.pop(0)
        self.updated_at = datetime.now(UTC)

    def clear(self) -> None:
        """Clear working memory for new task."""
        self.task_id = ""
        self.task_description = ""
        self.task_description_ar = ""
        self.current_goal = ""
        self.current_goal_ar = ""
        self.focus_items = []
        self.scratch_pad = {}
        self.context_stack = []
        self.last_action = None
        self.last_observation = None
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "task_description_ar": self.task_description_ar,
            "current_goal": self.current_goal,
            "current_goal_ar": self.current_goal_ar,
            "focus_items": self.focus_items,
            "scratch_pad": self.scratch_pad,
            "context_stack": self.context_stack,
            "last_action": self.last_action,
            "last_observation": self.last_observation,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# MEMORY STORE
# ============================================================================


class MemoryStore:
    """
    In-memory store for agent memories.
    مخزن الذاكرة للوكيل

    Provides:
    - Fast retrieval by ID
    - Tag-based filtering
    - Similarity search (if embeddings available)
    - Automatic expiration
    """

    def __init__(
        self,
        max_entries: int = 10000,
        enable_compression: bool = True,
    ):
        self.max_entries = max_entries
        self.enable_compression = enable_compression

        # Storage by type
        self.episodic: dict[str, EpisodicMemory] = {}
        self.semantic: dict[str, SemanticMemory] = {}
        self.procedural: dict[str, ProceduralMemory] = {}

        # Indices
        self.tag_index: dict[str, set[str]] = {}  # tag -> memory_ids
        self.category_index: dict[str, set[str]] = {}  # category -> memory_ids

        logger.debug("memory_store_initialized", max_entries=max_entries)

    def store(self, memory: MemoryEntry) -> str:
        """Store a memory entry."""
        # Select appropriate storage
        if isinstance(memory, EpisodicMemory):
            self.episodic[memory.memory_id] = memory
        elif isinstance(memory, SemanticMemory):
            self.semantic[memory.memory_id] = memory
            # Index by category
            if memory.category:
                if memory.category not in self.category_index:
                    self.category_index[memory.category] = set()
                self.category_index[memory.category].add(memory.memory_id)
        elif isinstance(memory, ProceduralMemory):
            self.procedural[memory.memory_id] = memory
        else:
            raise ValueError(f"Unknown memory type: {type(memory)}")

        # Index by tags
        for tag in memory.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(memory.memory_id)

        # Check capacity
        self._enforce_capacity()

        logger.debug(
            "memory_stored",
            memory_id=memory.memory_id,
            type=memory.memory_type.value,
        )

        return memory.memory_id

    def retrieve(
        self,
        memory_id: str,
        memory_type: MemoryType | None = None,
    ) -> MemoryEntry | None:
        """Retrieve a memory by ID."""
        memory = None

        if memory_type == MemoryType.EPISODIC or memory_type is None:
            memory = self.episodic.get(memory_id)
        if memory is None and (memory_type == MemoryType.SEMANTIC or memory_type is None):
            memory = self.semantic.get(memory_id)
        if memory is None and (memory_type == MemoryType.PROCEDURAL or memory_type is None):
            memory = self.procedural.get(memory_id)

        if memory:
            memory.touch()

        return memory

    def query(
        self,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        category: str | None = None,
        since: datetime | None = None,
        limit: int = 10,
        strategy: RetrievalStrategy = RetrievalStrategy.RECENCY,
    ) -> list[MemoryEntry]:
        """Query memories with filters."""
        results: list[MemoryEntry] = []

        # Get candidate memories
        candidates: list[MemoryEntry] = []

        if memory_type == MemoryType.EPISODIC or memory_type is None:
            candidates.extend(self.episodic.values())
        if memory_type == MemoryType.SEMANTIC or memory_type is None:
            candidates.extend(self.semantic.values())
        if memory_type == MemoryType.PROCEDURAL or memory_type is None:
            candidates.extend(self.procedural.values())

        # Filter by tags
        if tags:
            tag_memory_ids: set[str] = set()
            for tag in tags:
                if tag in self.tag_index:
                    tag_memory_ids.update(self.tag_index[tag])
            candidates = [m for m in candidates if m.memory_id in tag_memory_ids]

        # Filter by category (semantic only)
        if category and category in self.category_index:
            category_ids = self.category_index[category]
            candidates = [m for m in candidates if m.memory_id in category_ids]

        # Filter by time
        if since:
            candidates = [m for m in candidates if m.created_at >= since]

        # Filter expired
        candidates = [m for m in candidates if not m.is_expired]

        # Sort by strategy
        if strategy == RetrievalStrategy.RECENCY:
            candidates.sort(key=lambda m: m.created_at, reverse=True)
        elif strategy == RetrievalStrategy.RELEVANCE:
            candidates.sort(key=lambda m: m.access_count, reverse=True)
        elif strategy == RetrievalStrategy.COMBINED:
            # Score based on recency and access count
            now = datetime.now(UTC)
            for m in candidates:
                age_hours = (now - m.created_at).total_seconds() / 3600
                m.metadata["_score"] = m.access_count - age_hours * 0.1
            candidates.sort(key=lambda m: m.metadata.get("_score", 0), reverse=True)

        results = candidates[:limit]

        # Touch accessed memories
        for m in results:
            m.touch()

        return results

    def find_similar(
        self,
        query_embedding: list[float],
        memory_type: MemoryType | None = None,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[tuple[MemoryEntry, float]]:
        """Find memories similar to query embedding."""
        if not query_embedding:
            return []

        results: list[tuple[MemoryEntry, float]] = []

        # Get candidates
        candidates: list[MemoryEntry] = []
        if memory_type == MemoryType.EPISODIC or memory_type is None:
            candidates.extend(self.episodic.values())
        if memory_type == MemoryType.SEMANTIC or memory_type is None:
            candidates.extend(self.semantic.values())
        if memory_type == MemoryType.PROCEDURAL or memory_type is None:
            candidates.extend(self.procedural.values())

        # Calculate similarities
        for memory in candidates:
            if memory.embedding:
                similarity = self._cosine_similarity(query_embedding, memory.embedding)
                if similarity >= threshold:
                    results.append((memory, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        deleted = False

        if memory_id in self.episodic:
            memory = self.episodic.pop(memory_id)
            deleted = True
        elif memory_id in self.semantic:
            memory = self.semantic.pop(memory_id)
            deleted = True
        elif memory_id in self.procedural:
            memory = self.procedural.pop(memory_id)
            deleted = True

        if deleted:
            # Remove from indices
            for tag_set in self.tag_index.values():
                tag_set.discard(memory_id)
            for cat_set in self.category_index.values():
                cat_set.discard(memory_id)

        return deleted

    def _enforce_capacity(self) -> None:
        """Enforce maximum capacity by removing oldest low-priority memories."""
        total = len(self.episodic) + len(self.semantic) + len(self.procedural)

        if total <= self.max_entries:
            return

        # Collect all memories with scores
        all_memories: list[tuple[str, MemoryEntry, float]] = []

        for memory_id, memory in self.episodic.items():
            score = self._calculate_eviction_score(memory)
            all_memories.append((memory_id, memory, score))
        for memory_id, memory in self.semantic.items():
            score = self._calculate_eviction_score(memory)
            all_memories.append((memory_id, memory, score))
        for memory_id, memory in self.procedural.items():
            score = self._calculate_eviction_score(memory)
            all_memories.append((memory_id, memory, score))

        # Sort by score (lower = more likely to evict)
        all_memories.sort(key=lambda x: x[2])

        # Evict until under capacity
        to_evict = total - self.max_entries
        for i in range(to_evict):
            memory_id = all_memories[i][0]
            self.delete(memory_id)

    def _calculate_eviction_score(self, memory: MemoryEntry) -> float:
        """
        Calculate eviction score (lower = more likely to evict).
        """
        score = 0.0

        # Priority factor
        priority_scores = {
            MemoryPriority.CRITICAL: 1000,
            MemoryPriority.HIGH: 100,
            MemoryPriority.MEDIUM: 10,
            MemoryPriority.LOW: 1,
        }
        score += priority_scores.get(memory.priority, 10)

        # Access frequency
        score += memory.access_count * 5

        # Recency (hours since last access)
        hours_since_access = (
            datetime.now(UTC) - memory.last_accessed
        ).total_seconds() / 3600
        score -= hours_since_access * 0.5

        return score

    def get_stats(self) -> dict[str, Any]:
        """Get memory store statistics."""
        return {
            "episodic_count": len(self.episodic),
            "semantic_count": len(self.semantic),
            "procedural_count": len(self.procedural),
            "total_count": len(self.episodic) + len(self.semantic) + len(self.procedural),
            "max_entries": self.max_entries,
            "tag_count": len(self.tag_index),
            "category_count": len(self.category_index),
        }


# ============================================================================
# AGENT MEMORY SYSTEM
# ============================================================================


class AgentMemorySystem:
    """
    Complete memory system for AI agents.
    نظام ذاكرة كامل لوكلاء الذكاء الاصطناعي

    Integrates:
    - Working memory for current task
    - Episodic memory for past events
    - Semantic memory for knowledge
    - Procedural memory for skills

    Provides:
    - Automatic memory consolidation
    - Context-aware retrieval
    - Memory compression for efficiency
    - Cross-memory integration
    """

    def __init__(
        self,
        agent_id: str,
        tenant_id: str = "sahool",
        max_entries: int = 10000,
        enable_persistence: bool = True,
    ):
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.enable_persistence = enable_persistence

        # Memory stores
        self.working = WorkingMemory()
        self.store = MemoryStore(max_entries=max_entries)

        # Embedding function (can be replaced with actual embedder)
        self._embedding_fn: Any = None

        logger.info(
            "agent_memory_system_initialized",
            agent_id=agent_id,
            max_entries=max_entries,
        )

    def set_embedding_function(self, fn: Any) -> None:
        """Set the function used to generate embeddings."""
        self._embedding_fn = fn

    # ========================================================================
    # WORKING MEMORY
    # ========================================================================

    def start_task(
        self,
        task_id: str,
        description: str,
        description_ar: str,
        goal: str,
        goal_ar: str,
    ) -> None:
        """Initialize working memory for a new task."""
        self.working.clear()
        self.working.task_id = task_id
        self.working.task_description = description
        self.working.task_description_ar = description_ar
        self.working.current_goal = goal
        self.working.current_goal_ar = goal_ar
        self.working.created_at = datetime.now(UTC)

    def update_focus(self, item: dict[str, Any]) -> None:
        """Add item to current focus."""
        self.working.add_to_focus(item)

    def record_action(self, action: dict[str, Any]) -> None:
        """Record an action in working memory."""
        self.working.last_action = action
        self.working.updated_at = datetime.now(UTC)

    def record_observation(self, observation: dict[str, Any]) -> None:
        """Record an observation in working memory."""
        self.working.last_observation = observation
        self.working.updated_at = datetime.now(UTC)

    def get_working_context(self) -> dict[str, Any]:
        """Get current working memory context."""
        return self.working.to_dict()

    # ========================================================================
    # EPISODIC MEMORY
    # ========================================================================

    def remember_episode(
        self,
        event_type: str,
        content: str,
        content_ar: str | None = None,
        context: dict[str, Any] | None = None,
        actors: list[str] | None = None,
        outcome: str = "",
        outcome_ar: str = "",
        success: bool = True,
        emotional_valence: float = 0.0,
        lessons: list[str] | None = None,
        tags: list[str] | None = None,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        ttl_hours: int | None = None,
    ) -> str:
        """
        Store an episodic memory.
        تخزين ذاكرة عرضية
        """
        memory = EpisodicMemory(
            memory_id=str(uuid.uuid4()),
            memory_type=MemoryType.EPISODIC,
            content=content,
            content_ar=content_ar,
            event_type=event_type,
            context=context or {},
            actors=actors or [],
            outcome=outcome,
            outcome_ar=outcome_ar,
            success=success,
            emotional_valence=emotional_valence,
            lessons_learned=lessons or [],
            tags=tags or [],
            priority=priority,
            ttl_hours=ttl_hours,
        )

        # Generate embedding if function available
        if self._embedding_fn:
            try:
                memory.embedding = self._embedding_fn(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")

        return self.store.store(memory)

    def recall_similar_episodes(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.7,
    ) -> list[EpisodicMemory]:
        """
        Recall episodes similar to query.
        استرجاع الحلقات المشابهة للاستعلام
        """
        if not self._embedding_fn:
            # Fallback to tag-based retrieval
            return [
                m for m in self.store.query(
                    memory_type=MemoryType.EPISODIC,
                    limit=top_k,
                )
                if isinstance(m, EpisodicMemory)
            ]

        try:
            query_embedding = self._embedding_fn(query)
            results = self.store.find_similar(
                query_embedding=query_embedding,
                memory_type=MemoryType.EPISODIC,
                top_k=top_k,
                threshold=min_similarity,
            )
            return [m for m, _ in results if isinstance(m, EpisodicMemory)]
        except Exception as e:
            logger.warning(f"Similarity search failed: {e}")
            return []

    def find_past_solutions(
        self,
        problem_description: str,
        min_success_rate: float = 0.5,
        top_k: int = 3,
    ) -> list[tuple[EpisodicMemory, float]]:
        """
        Find past successful solutions to similar problems.
        إيجاد حلول سابقة ناجحة لمشاكل مماثلة
        """
        # Get similar episodes
        similar = self.recall_similar_episodes(problem_description, top_k=top_k * 2)

        # Filter for successful ones
        successful = [
            ep for ep in similar
            if ep.success and ep.emotional_valence >= 0
        ]

        # Sort by success and recency
        successful.sort(
            key=lambda ep: (ep.access_count, -len(ep.lessons_learned)),
            reverse=True,
        )

        # Return with pseudo-confidence scores
        return [(ep, 0.8) for ep in successful[:top_k]]

    # ========================================================================
    # SEMANTIC MEMORY
    # ========================================================================

    def learn_fact(
        self,
        content: str,
        content_ar: str | None = None,
        category: str = "",
        concepts: list[str] | None = None,
        relationships: list[dict[str, str]] | None = None,
        confidence: float = 0.8,
        source: str = "",
        verified: bool = False,
        tags: list[str] | None = None,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
    ) -> str:
        """
        Store a semantic memory (fact/knowledge).
        تخزين ذاكرة دلالية (حقيقة/معرفة)
        """
        memory = SemanticMemory(
            memory_id=str(uuid.uuid4()),
            memory_type=MemoryType.SEMANTIC,
            content=content,
            content_ar=content_ar,
            category=category,
            concepts=concepts or [],
            relationships=relationships or [],
            confidence=confidence,
            source=source,
            verified=verified,
            tags=tags or [],
            priority=priority,
        )

        # Generate embedding
        if self._embedding_fn:
            try:
                memory.embedding = self._embedding_fn(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")

        return self.store.store(memory)

    def query_knowledge(
        self,
        query: str,
        category: str | None = None,
        concepts: list[str] | None = None,
        min_confidence: float = 0.5,
        top_k: int = 5,
    ) -> list[SemanticMemory]:
        """
        Query semantic knowledge.
        استعلام المعرفة الدلالية
        """
        if self._embedding_fn:
            try:
                query_embedding = self._embedding_fn(query)
                results = self.store.find_similar(
                    query_embedding=query_embedding,
                    memory_type=MemoryType.SEMANTIC,
                    top_k=top_k,
                    threshold=min_confidence,
                )
                return [m for m, _ in results if isinstance(m, SemanticMemory)]
            except Exception as e:
                logger.warning(f"Similarity search failed: {e}")

        # Fallback to category-based
        memories = self.store.query(
            memory_type=MemoryType.SEMANTIC,
            category=category,
            limit=top_k,
        )
        return [m for m in memories if isinstance(m, SemanticMemory)]

    # ========================================================================
    # PROCEDURAL MEMORY
    # ========================================================================

    def learn_procedure(
        self,
        skill_name: str,
        skill_name_ar: str,
        steps: list[dict[str, Any]],
        preconditions: list[str] | None = None,
        postconditions: list[str] | None = None,
        variations: list[str] | None = None,
        tags: list[str] | None = None,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
    ) -> str:
        """
        Store a procedural memory (skill).
        تخزين ذاكرة إجرائية (مهارة)
        """
        memory = ProceduralMemory(
            memory_id=str(uuid.uuid4()),
            memory_type=MemoryType.PROCEDURAL,
            content=skill_name,
            content_ar=skill_name_ar,
            skill_name=skill_name,
            skill_name_ar=skill_name_ar,
            steps=steps,
            preconditions=preconditions or [],
            postconditions=postconditions or [],
            variations=variations or [],
            tags=tags or [],
            priority=priority,
        )

        return self.store.store(memory)

    def find_applicable_skills(
        self,
        situation: str,
        min_success_rate: float = 0.5,
        top_k: int = 3,
    ) -> list[ProceduralMemory]:
        """
        Find skills applicable to the current situation.
        إيجاد المهارات المناسبة للحالة الحالية
        """
        all_procedures = self.store.query(
            memory_type=MemoryType.PROCEDURAL,
            limit=100,
        )

        # Filter by success rate
        applicable = [
            p for p in all_procedures
            if isinstance(p, ProceduralMemory) and p.success_rate >= min_success_rate
        ]

        # Sort by success rate and execution count
        applicable.sort(
            key=lambda p: (p.success_rate, p.execution_count),
            reverse=True,
        )

        return applicable[:top_k]

    def update_skill_performance(
        self,
        memory_id: str,
        success: bool,
        duration_ms: float,
    ) -> None:
        """
        Update skill performance after execution.
        تحديث أداء المهارة بعد التنفيذ
        """
        memory = self.store.retrieve(memory_id, MemoryType.PROCEDURAL)
        if memory and isinstance(memory, ProceduralMemory):
            memory.update_success_rate(success, duration_ms)

    # ========================================================================
    # CONTEXT RETRIEVAL
    # ========================================================================

    def retrieve_relevant_context(
        self,
        query: str,
        max_items: int = 10,
    ) -> dict[str, Any]:
        """
        Retrieve multi-level context for current task.
        استرجاع سياق متعدد المستويات للمهمة الحالية

        Combines:
        - Working memory (current state)
        - Episodic (similar past events)
        - Semantic (relevant knowledge)
        - Procedural (applicable skills)
        """
        context: dict[str, Any] = {
            "working": self.working.to_dict(),
            "episodic": [],
            "semantic": [],
            "procedural": [],
        }

        # Get similar episodes
        episodes = self.recall_similar_episodes(query, top_k=max_items // 3)
        context["episodic"] = [ep.to_dict() for ep in episodes]

        # Get relevant knowledge
        knowledge = self.query_knowledge(query, top_k=max_items // 3)
        context["semantic"] = [k.to_dict() for k in knowledge]

        # Get applicable skills
        skills = self.find_applicable_skills(query, top_k=max_items // 3)
        context["procedural"] = [s.to_dict() for s in skills]

        return context

    def format_context_for_prompt(
        self,
        context: dict[str, Any],
        max_tokens: int = 2000,
    ) -> str:
        """
        Format context for inclusion in LLM prompt.
        تنسيق السياق للتضمين في موجه LLM
        """
        sections = []

        # Working memory
        if context.get("working", {}).get("current_goal"):
            sections.append(
                f"## Current Task\n"
                f"Goal: {context['working']['current_goal']}\n"
                f"Last Action: {context['working'].get('last_action', 'None')}\n"
                f"Last Observation: {context['working'].get('last_observation', 'None')}"
            )

        # Episodic
        if context.get("episodic"):
            ep_lines = ["## Relevant Past Events"]
            for ep in context["episodic"][:3]:
                ep_lines.append(f"- {ep['event_type']}: {ep['content'][:100]}...")
                if ep.get("lessons_learned"):
                    ep_lines.append(f"  Lessons: {', '.join(ep['lessons_learned'][:2])}")
            sections.append("\n".join(ep_lines))

        # Semantic
        if context.get("semantic"):
            sem_lines = ["## Relevant Knowledge"]
            for sem in context["semantic"][:3]:
                sem_lines.append(f"- [{sem.get('category', 'General')}] {sem['content'][:100]}...")
            sections.append("\n".join(sem_lines))

        # Procedural
        if context.get("procedural"):
            proc_lines = ["## Applicable Skills"]
            for proc in context["procedural"][:3]:
                success_pct = int(proc.get("success_rate", 0) * 100)
                proc_lines.append(f"- {proc['skill_name']} (Success rate: {success_pct}%)")
            sections.append("\n".join(proc_lines))

        result = "\n\n".join(sections)

        # Truncate if too long (rough estimate)
        if len(result) > max_tokens * 4:  # Rough char to token ratio
            result = result[:max_tokens * 4] + "\n...[truncated]"

        return result

    # ========================================================================
    # MEMORY CONSOLIDATION
    # ========================================================================

    def consolidate_task_memory(
        self,
        success: bool,
        summary: str,
        summary_ar: str,
        lessons: list[str] | None = None,
    ) -> str:
        """
        Consolidate working memory into long-term episodic memory.
        دمج الذاكرة العاملة في الذاكرة العرضية طويلة المدى

        Called at end of task to preserve important information.
        """
        return self.remember_episode(
            event_type="task_completion",
            content=f"{self.working.task_description}: {summary}",
            content_ar=f"{self.working.task_description_ar}: {summary_ar}",
            context={
                "task_id": self.working.task_id,
                "goal": self.working.current_goal,
                "focus_items": self.working.focus_items[-5:],  # Last 5 focus items
            },
            outcome=summary,
            outcome_ar=summary_ar,
            success=success,
            emotional_valence=0.5 if success else -0.3,
            lessons=lessons or [],
            tags=["task_completion", self.working.task_id],
            priority=MemoryPriority.MEDIUM if success else MemoryPriority.HIGH,
        )

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory system statistics."""
        return {
            "agent_id": self.agent_id,
            "store_stats": self.store.get_stats(),
            "working_memory": {
                "active": bool(self.working.task_id),
                "task_id": self.working.task_id,
                "focus_items": len(self.working.focus_items),
            },
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_memory_system(
    agent_id: str,
    tenant_id: str = "sahool",
    max_entries: int = 10000,
) -> AgentMemorySystem:
    """Factory function to create a memory system."""
    return AgentMemorySystem(
        agent_id=agent_id,
        tenant_id=tenant_id,
        max_entries=max_entries,
    )
