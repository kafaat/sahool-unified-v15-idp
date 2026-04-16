"""
Graph-Based Memory for AI Agents (Cognee-Inspired)
ذاكرة قائمة على الرسم البياني للوكلاء الذكية

Inspired by Cognee, this module provides:
1. Entity storage with vector embeddings
2. Relationship graphs between entities
3. ECL (Extract, Cognify, Load) pipeline pattern
4. Semantic + relationship-based search

مستوحى من Cognee، توفر هذه الوحدة:
١. تخزين الكيانات مع التضمينات المتجهية
٢. رسوم بيانية للعلاقات بين الكيانات
٣. نمط خط أنابيب ECL (استخراج، إدراك، تحميل)
٤. بحث دلالي + قائم على العلاقات

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class EntityType(StrEnum):
    """Types of entities in the agricultural domain"""

    FARM = "farm"
    FIELD = "field"
    CROP = "crop"
    FARMER = "farmer"
    EQUIPMENT = "equipment"
    SENSOR = "sensor"
    ADVISORY = "advisory"
    TREATMENT = "treatment"
    HARVEST = "harvest"
    WEATHER = "weather"
    PEST = "pest"
    DISEASE = "disease"
    DOCUMENT = "document"
    CUSTOM = "custom"


class RelationType(StrEnum):
    """Types of relationships between entities"""

    # Ownership/Containment
    OWNS = "owns"  # farmer OWNS farm
    CONTAINS = "contains"  # farm CONTAINS field
    BELONGS_TO = "belongs_to"  # field BELONGS_TO farm

    # Agricultural relationships
    GROWS = "grows"  # field GROWS crop
    PLANTED_IN = "planted_in"  # crop PLANTED_IN field
    APPLIED_TO = "applied_to"  # treatment APPLIED_TO field
    HARVESTED_FROM = "harvested_from"  # harvest HARVESTED_FROM field

    # Equipment relationships
    MONITORS = "monitors"  # sensor MONITORS field
    USED_IN = "used_in"  # equipment USED_IN field

    # Advisory relationships
    RECOMMENDS_FOR = "recommends_for"  # advisory RECOMMENDS_FOR field
    ADDRESSES = "addresses"  # treatment ADDRESSES pest/disease

    # Temporal relationships
    FOLLOWED_BY = "followed_by"  # crop FOLLOWED_BY crop (rotation)
    PRECEDED_BY = "preceded_by"  # crop PRECEDED_BY crop

    # Similarity/Association
    SIMILAR_TO = "similar_to"  # entity SIMILAR_TO entity
    RELATED_TO = "related_to"  # generic relationship

    # Custom
    CUSTOM = "custom"


@dataclass
class Entity:
    """
    An entity in the knowledge graph.
    كيان في رسم المعرفة البياني.
    """

    id: str
    type: EntityType
    name: str
    name_ar: str | None = None
    content: str = ""
    content_ar: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tenant_id: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "content": self.content,
            "content_ar": self.content_ar,
            "properties": self.properties,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tenant_id": self.tenant_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Entity:
        return cls(
            id=data["id"],
            type=EntityType(data["type"]),
            name=data["name"],
            name_ar=data.get("name_ar"),
            content=data.get("content", ""),
            content_ar=data.get("content_ar"),
            properties=data.get("properties", {}),
            embedding=data.get("embedding"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(UTC),
            tenant_id=data.get("tenant_id", "default"),
            metadata=data.get("metadata", {}),
        )

    def get_searchable_text(self) -> str:
        """Get all searchable text from the entity"""
        parts = [self.name, self.content]
        if self.name_ar:
            parts.append(self.name_ar)
        if self.content_ar:
            parts.append(self.content_ar)
        for key, value in self.properties.items():
            if isinstance(value, str):
                parts.append(f"{key}: {value}")
        return " ".join(filter(None, parts))


@dataclass
class Relationship:
    """
    A relationship between two entities.
    علاقة بين كيانين.
    """

    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0  # Relationship strength (0.0 to 1.0)
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Relationship:
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=RelationType(data["relation_type"]),
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(UTC),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SearchResult:
    """
    A search result with relevance scoring.
    نتيجة بحث مع تقييم الصلة.
    """

    entity: Entity
    score: float  # Combined score (semantic + graph)
    semantic_score: float  # Vector similarity score
    graph_score: float  # Graph connectivity score
    path: list[str] = field(default_factory=list)  # Entity IDs in path
    relationships: list[Relationship] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity": self.entity.to_dict(),
            "score": self.score,
            "semantic_score": self.semantic_score,
            "graph_score": self.graph_score,
            "path": self.path,
            "relationships": [r.to_dict() for r in self.relationships],
        }


class GraphStore:
    """
    In-memory graph store for entities and relationships.
    مخزن رسم بياني في الذاكرة للكيانات والعلاقات.

    Note: In production, this should be backed by a graph database
    like Neo4j or a PostgreSQL with graph extensions.
    """

    def __init__(self):
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[str, Relationship] = {}
        # Indexes for fast lookup
        self._type_index: dict[EntityType, set[str]] = {}
        self._outgoing_edges: dict[str, set[str]] = {}  # entity_id -> relationship_ids
        self._incoming_edges: dict[str, set[str]] = {}  # entity_id -> relationship_ids
        self._tenant_index: dict[str, set[str]] = {}

    async def add_entity(self, entity: Entity) -> None:
        """Add or update an entity"""
        self._entities[entity.id] = entity

        # Update type index
        if entity.type not in self._type_index:
            self._type_index[entity.type] = set()
        self._type_index[entity.type].add(entity.id)

        # Update tenant index
        if entity.tenant_id not in self._tenant_index:
            self._tenant_index[entity.tenant_id] = set()
        self._tenant_index[entity.tenant_id].add(entity.id)

    async def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID"""
        return self._entities.get(entity_id)

    async def get_entities_by_type(self, entity_type: EntityType, tenant_id: str | None = None) -> list[Entity]:
        """Get all entities of a specific type"""
        ids = self._type_index.get(entity_type, set())
        entities = [self._entities[id] for id in ids if id in self._entities]

        if tenant_id:
            entities = [e for e in entities if e.tenant_id == tenant_id]

        return entities

    async def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship between entities"""
        self._relationships[relationship.id] = relationship

        # Update edge indexes
        if relationship.source_id not in self._outgoing_edges:
            self._outgoing_edges[relationship.source_id] = set()
        self._outgoing_edges[relationship.source_id].add(relationship.id)

        if relationship.target_id not in self._incoming_edges:
            self._incoming_edges[relationship.target_id] = set()
        self._incoming_edges[relationship.target_id].add(relationship.id)

    async def get_relationship(self, rel_id: str) -> Relationship | None:
        """Get relationship by ID"""
        return self._relationships.get(rel_id)

    async def get_outgoing_relationships(self, entity_id: str) -> list[Relationship]:
        """Get all relationships where entity is the source"""
        rel_ids = self._outgoing_edges.get(entity_id, set())
        return [self._relationships[id] for id in rel_ids if id in self._relationships]

    async def get_incoming_relationships(self, entity_id: str) -> list[Relationship]:
        """Get all relationships where entity is the target"""
        rel_ids = self._incoming_edges.get(entity_id, set())
        return [self._relationships[id] for id in rel_ids if id in self._relationships]

    async def get_neighbors(
        self,
        entity_id: str,
        relation_type: RelationType | None = None,
        direction: str = "both",  # "outgoing", "incoming", "both"
    ) -> list[tuple[Entity, Relationship]]:
        """Get neighboring entities with their relationships"""
        neighbors = []

        if direction in ("outgoing", "both"):
            for rel in await self.get_outgoing_relationships(entity_id):
                if relation_type and rel.relation_type != relation_type:
                    continue
                target = await self.get_entity(rel.target_id)
                if target:
                    neighbors.append((target, rel))

        if direction in ("incoming", "both"):
            for rel in await self.get_incoming_relationships(entity_id):
                if relation_type and rel.relation_type != relation_type:
                    continue
                source = await self.get_entity(rel.source_id)
                if source:
                    neighbors.append((source, rel))

        return neighbors

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships"""
        if entity_id not in self._entities:
            return False

        entity = self._entities[entity_id]

        # Remove from indexes
        if entity.type in self._type_index:
            self._type_index[entity.type].discard(entity_id)
        if entity.tenant_id in self._tenant_index:
            self._tenant_index[entity.tenant_id].discard(entity_id)

        # Remove relationships
        for rel_id in list(self._outgoing_edges.get(entity_id, set())):
            await self.delete_relationship(rel_id)
        for rel_id in list(self._incoming_edges.get(entity_id, set())):
            await self.delete_relationship(rel_id)

        del self._entities[entity_id]
        return True

    async def delete_relationship(self, rel_id: str) -> bool:
        """Delete a relationship"""
        if rel_id not in self._relationships:
            return False

        rel = self._relationships[rel_id]

        # Remove from edge indexes
        if rel.source_id in self._outgoing_edges:
            self._outgoing_edges[rel.source_id].discard(rel_id)
        if rel.target_id in self._incoming_edges:
            self._incoming_edges[rel.target_id].discard(rel_id)

        del self._relationships[rel_id]
        return True

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics"""
        return {
            "total_entities": len(self._entities),
            "total_relationships": len(self._relationships),
            "entities_by_type": {t.value: len(ids) for t, ids in self._type_index.items()},
            "tenants": list(self._tenant_index.keys()),
        }


class SimpleEmbedder:
    """
    Simple text embedder using TF-IDF-like approach.
    For production, use shared.ai.embeddings.EmbeddingsAdapter.

    مُضمِّن نصي بسيط باستخدام نهج TF-IDF.
    للإنتاج، استخدم shared.ai.embeddings.EmbeddingsAdapter.
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._doc_count = 0

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization"""
        text = text.lower()
        # Handle Arabic text
        tokens = re.findall(r"[\w\u0600-\u06FF]+", text)
        return tokens

    def _hash_token(self, token: str) -> int:
        """Hash token to dimension index (not for security, just distribution)"""
        return int(hashlib.sha256(token.encode()).hexdigest(), 16) % self.dimension

    async def embed(self, text: str) -> list[float]:
        """Create embedding for text"""
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        # Create sparse embedding using hashing trick
        embedding = [0.0] * self.dimension
        token_counts: dict[str, int] = {}

        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        for token, count in token_counts.items():
            idx = self._hash_token(token)
            tf = count / len(tokens)
            # Use simple IDF approximation
            idf = self._idf.get(token, 1.0)
            embedding[idx] += tf * idf

        # Normalize
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for multiple texts"""
        return [await self.embed(text) for text in texts]

    def update_idf(self, documents: list[str]) -> None:
        """Update IDF values from documents"""
        self._doc_count = len(documents)
        doc_freq: dict[str, int] = {}

        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        for token, freq in doc_freq.items():
            self._idf[token] = math.log((self._doc_count + 1) / (freq + 1)) + 1


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


class GraphMemory:
    """
    Main class for graph-based memory (Cognee-inspired).
    الفئة الرئيسية للذاكرة القائمة على الرسم البياني.

    Provides ECL (Extract, Cognify, Load) pipeline:
    - add(): Load documents/entities
    - cognify(): Extract relationships and create embeddings
    - search(): Semantic + graph search
    """

    def __init__(
        self,
        store: GraphStore | None = None,
        embedder: SimpleEmbedder | None = None,
        tenant_id: str = "default",
    ):
        self.store = store or GraphStore()
        self.embedder = embedder or SimpleEmbedder()
        self.tenant_id = tenant_id
        self._pending_entities: list[Entity] = []
        self._relationship_extractors: list[Callable] = []

        # Register default extractors
        self._register_default_extractors()

    def _register_default_extractors(self) -> None:
        """Register default relationship extractors"""

        # Farm-Field relationship
        async def extract_farm_field(entity: Entity, all_entities: list[Entity]) -> list[Relationship]:
            relationships = []
            if entity.type == EntityType.FIELD:
                farm_id = entity.properties.get("farm_id")
                if farm_id:
                    for e in all_entities:
                        if e.type == EntityType.FARM and e.id == farm_id:
                            relationships.append(
                                Relationship(
                                    id=str(uuid4()),
                                    source_id=e.id,
                                    target_id=entity.id,
                                    relation_type=RelationType.CONTAINS,
                                    weight=1.0,
                                )
                            )
            return relationships

        # Field-Crop relationship
        async def extract_field_crop(entity: Entity, all_entities: list[Entity]) -> list[Relationship]:
            relationships = []
            if entity.type == EntityType.CROP:
                field_id = entity.properties.get("field_id")
                if field_id:
                    for e in all_entities:
                        if e.type == EntityType.FIELD and e.id == field_id:
                            relationships.append(
                                Relationship(
                                    id=str(uuid4()),
                                    source_id=e.id,
                                    target_id=entity.id,
                                    relation_type=RelationType.GROWS,
                                    weight=1.0,
                                )
                            )
            return relationships

        # Farmer-Farm relationship
        async def extract_farmer_farm(entity: Entity, all_entities: list[Entity]) -> list[Relationship]:
            relationships = []
            if entity.type == EntityType.FARM:
                farmer_id = entity.properties.get("farmer_id") or entity.properties.get("owner_id")
                if farmer_id:
                    for e in all_entities:
                        if e.type == EntityType.FARMER and e.id == farmer_id:
                            relationships.append(
                                Relationship(
                                    id=str(uuid4()),
                                    source_id=e.id,
                                    target_id=entity.id,
                                    relation_type=RelationType.OWNS,
                                    weight=1.0,
                                )
                            )
            return relationships

        # Similarity relationship based on embeddings
        async def extract_similarity(entity: Entity, all_entities: list[Entity]) -> list[Relationship]:
            relationships = []
            if entity.embedding:
                for e in all_entities:
                    if e.id != entity.id and e.type == entity.type and e.embedding:
                        sim = cosine_similarity(entity.embedding, e.embedding)
                        if sim > 0.7:  # High similarity threshold
                            relationships.append(
                                Relationship(
                                    id=str(uuid4()),
                                    source_id=entity.id,
                                    target_id=e.id,
                                    relation_type=RelationType.SIMILAR_TO,
                                    weight=sim,
                                )
                            )
            return relationships

        self._relationship_extractors = [
            extract_farm_field,
            extract_field_crop,
            extract_farmer_farm,
            extract_similarity,
        ]

    async def add(
        self,
        content: str,
        entity_type: EntityType = EntityType.DOCUMENT,
        name: str | None = None,
        name_ar: str | None = None,
        content_ar: str | None = None,
        properties: dict[str, Any] | None = None,
        entity_id: str | None = None,
    ) -> Entity:
        """
        Add a document or entity to memory (Load phase).
        إضافة مستند أو كيان للذاكرة (مرحلة التحميل).

        Args:
            content: Text content of the entity
            entity_type: Type of entity
            name: Entity name
            name_ar: Arabic name
            content_ar: Arabic content
            properties: Additional properties
            entity_id: Optional custom ID

        Returns:
            Created entity
        """
        entity = Entity(
            id=entity_id or str(uuid4()),
            type=entity_type,
            name=name or content[:50],
            name_ar=name_ar,
            content=content,
            content_ar=content_ar,
            properties=properties or {},
            tenant_id=self.tenant_id,
        )

        self._pending_entities.append(entity)
        return entity

    async def add_entity(self, entity: Entity) -> Entity:
        """Add a pre-built entity"""
        entity.tenant_id = self.tenant_id
        self._pending_entities.append(entity)
        return entity

    async def cognify(self) -> dict[str, Any]:
        """
        Process pending entities: create embeddings and extract relationships.
        معالجة الكيانات المعلقة: إنشاء التضمينات واستخراج العلاقات.

        This is the "Cognify" phase - understanding and connecting data.

        Returns:
            Statistics about the cognification process
        """
        stats = {
            "entities_processed": 0,
            "embeddings_created": 0,
            "relationships_extracted": 0,
        }

        if not self._pending_entities:
            return stats

        # Get all existing entities for relationship extraction
        all_entities = list(self.store._entities.values()) + self._pending_entities

        # Update IDF for better embeddings
        all_texts = [e.get_searchable_text() for e in all_entities]
        self.embedder.update_idf(all_texts)

        # Process each pending entity
        for entity in self._pending_entities:
            # Create embedding
            text = entity.get_searchable_text()
            entity.embedding = await self.embedder.embed(text)
            stats["embeddings_created"] += 1

            # Store entity
            await self.store.add_entity(entity)
            stats["entities_processed"] += 1

            # Extract relationships
            for extractor in self._relationship_extractors:
                try:
                    relationships = await extractor(entity, all_entities)
                    for rel in relationships:
                        await self.store.add_relationship(rel)
                        stats["relationships_extracted"] += 1
                except Exception:
                    pass  # Skip failed extractors

        # Clear pending
        self._pending_entities.clear()

        return stats

    async def memify(self) -> dict[str, Any]:
        """
        Alias for cognify() - matches Cognee API.
        اسم مستعار لـ cognify() - يطابق واجهة Cognee.
        """
        return await self.cognify()

    async def search(
        self,
        query: str,
        limit: int = 10,
        entity_types: list[EntityType] | None = None,
        semantic_weight: float = 0.6,
        graph_weight: float = 0.4,
        min_score: float = 0.1,
    ) -> list[SearchResult]:
        """
        Search for entities using semantic + graph scoring.
        البحث عن الكيانات باستخدام التسجيل الدلالي + الرسم البياني.

        Args:
            query: Search query
            limit: Maximum results
            entity_types: Filter by entity types
            semantic_weight: Weight for semantic similarity (0-1)
            graph_weight: Weight for graph connectivity (0-1)
            min_score: Minimum score threshold

        Returns:
            List of search results sorted by score
        """
        # Create query embedding
        query_embedding = await self.embedder.embed(query)

        # Get candidate entities
        candidates = []
        for entity in self.store._entities.values():
            if entity.tenant_id != self.tenant_id:
                continue
            if entity_types and entity.type not in entity_types:
                continue
            candidates.append(entity)

        if not candidates:
            return []

        # Calculate scores
        results = []
        for entity in candidates:
            # Semantic score
            semantic_score = 0.0
            if entity.embedding:
                semantic_score = cosine_similarity(query_embedding, entity.embedding)

            # Graph score (based on connectivity)
            outgoing = await self.store.get_outgoing_relationships(entity.id)
            incoming = await self.store.get_incoming_relationships(entity.id)
            total_connections = len(outgoing) + len(incoming)

            # Normalize graph score (more connections = higher score, with diminishing returns)
            graph_score = min(1.0, total_connections / 10.0)

            # Combined score
            combined_score = semantic_weight * semantic_score + graph_weight * graph_score

            if combined_score >= min_score:
                results.append(
                    SearchResult(
                        entity=entity,
                        score=combined_score,
                        semantic_score=semantic_score,
                        graph_score=graph_score,
                        relationships=outgoing + incoming,
                    )
                )

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    async def search_connected(
        self,
        entity_id: str,
        depth: int = 2,
        relation_types: list[RelationType] | None = None,
    ) -> list[SearchResult]:
        """
        Search for entities connected to a given entity.
        البحث عن الكيانات المتصلة بكيان معين.

        Args:
            entity_id: Starting entity ID
            depth: How many hops to traverse
            relation_types: Filter by relationship types

        Returns:
            Connected entities with path information
        """
        start_entity = await self.store.get_entity(entity_id)
        if not start_entity:
            return []

        visited: set[str] = {entity_id}
        results: list[SearchResult] = []
        current_level = [(start_entity, [], [])]  # (entity, path, relationships)

        for level in range(depth):
            next_level = []
            for entity, path, rels in current_level:
                neighbors = await self.store.get_neighbors(entity.id)

                for neighbor, rel in neighbors:
                    if neighbor.id in visited:
                        continue
                    if relation_types and rel.relation_type not in relation_types:
                        continue

                    visited.add(neighbor.id)
                    new_path = path + [entity.id]
                    new_rels = rels + [rel]

                    # Score based on depth and relationship weights
                    score = rel.weight / (level + 1)

                    results.append(
                        SearchResult(
                            entity=neighbor,
                            score=score,
                            semantic_score=0.0,
                            graph_score=score,
                            path=new_path,
                            relationships=new_rels,
                        )
                    )

                    next_level.append((neighbor, new_path, new_rels))

            current_level = next_level

        results.sort(key=lambda x: x.score, reverse=True)
        return results

    async def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID"""
        return await self.store.get_entity(entity_id)

    async def get_relationships(self, entity_id: str) -> list[Relationship]:
        """Get all relationships for an entity"""
        outgoing = await self.store.get_outgoing_relationships(entity_id)
        incoming = await self.store.get_incoming_relationships(entity_id)
        return outgoing + incoming

    async def link(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        weight: float = 1.0,
        properties: dict[str, Any] | None = None,
    ) -> Relationship:
        """
        Manually create a relationship between entities.
        إنشاء علاقة يدوياً بين الكيانات.
        """
        rel = Relationship(
            id=str(uuid4()),
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            properties=properties or {},
        )
        await self.store.add_relationship(rel)
        return rel

    def add_relationship_extractor(self, extractor: Callable[[Entity, list[Entity]], list[Relationship]]) -> None:
        """Add a custom relationship extractor"""
        self._relationship_extractors.append(extractor)

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics"""
        store_stats = self.store.get_stats()
        return {
            **store_stats,
            "pending_entities": len(self._pending_entities),
            "tenant_id": self.tenant_id,
            "extractors_count": len(self._relationship_extractors),
        }


# Singleton instance
_default_graph_memory: GraphMemory | None = None


def get_graph_memory(tenant_id: str = "default") -> GraphMemory:
    """Get or create the default graph memory instance"""
    global _default_graph_memory
    if _default_graph_memory is None or _default_graph_memory.tenant_id != tenant_id:
        _default_graph_memory = GraphMemory(tenant_id=tenant_id)
    return _default_graph_memory


# Convenience functions (Cognee-style API)
async def add(content: str, entity_type: EntityType = EntityType.DOCUMENT, **kwargs) -> Entity:
    """Add content to graph memory"""
    memory = get_graph_memory()
    return await memory.add(content, entity_type, **kwargs)


async def cognify() -> dict[str, Any]:
    """Process and connect added content"""
    memory = get_graph_memory()
    return await memory.cognify()


async def memify() -> dict[str, Any]:
    """Alias for cognify"""
    return await cognify()


async def search(query: str, limit: int = 10, **kwargs) -> list[SearchResult]:
    """Search graph memory"""
    memory = get_graph_memory()
    return await memory.search(query, limit, **kwargs)


# ============================================================================
# Vector Store Integration
# ============================================================================


class PersistentGraphStore(GraphStore):
    """
    Graph store with vector database persistence.
    مخزن رسم بياني مع قاعدة بيانات متجهية للحفظ.

    Uses VectorStore for persistent storage of entities with embeddings.
    يستخدم VectorStore للتخزين المستمر للكيانات مع التضمينات.
    """

    def __init__(self, collection_prefix: str = "graph_memory"):
        super().__init__()
        self.collection_prefix = collection_prefix
        self._vector_store = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize vector store backend"""
        if self._initialized:
            return

        try:
            from .vector_store import (
                VectorStore,
                VectorStoreBackend,
                VectorStoreConfig,
            )

            config = VectorStoreConfig(
                backend=VectorStoreBackend.SQLITE,
                dimension=128,  # Match SimpleEmbedder dimension
                default_collection=f"{self.collection_prefix}_entities",
            )

            self._vector_store = VectorStore(config)
            await self._vector_store.initialize()

            # Create collections for entities and relationships
            try:
                await self._vector_store.create_collection(
                    name=f"{self.collection_prefix}_entities",
                    dimension=128,
                )
            except Exception:
                pass  # Collection may already exist

            try:
                await self._vector_store.create_collection(
                    name=f"{self.collection_prefix}_relationships",
                    dimension=1,  # Relationships don't need embeddings
                )
            except Exception:
                pass

            self._initialized = True

        except ImportError:
            # VectorStore not available, use in-memory only
            self._initialized = True

    async def add_entity(self, entity: Entity) -> None:
        """Add or update an entity with persistence"""
        await super().add_entity(entity)

        if self._vector_store and entity.embedding:
            from .vector_store import VectorDocument

            doc = VectorDocument(
                id=entity.id,
                vector=entity.embedding,
                content=entity.get_searchable_text(),
                metadata={
                    "type": entity.type.value,
                    "name": entity.name,
                    "tenant_id": entity.tenant_id,
                    "entity_data": entity.to_dict(),
                },
                collection=f"{self.collection_prefix}_entities",
            )

            await self._vector_store.add(
                vectors=[doc.vector],
                texts=[doc.content],
                ids=[doc.id],
                metadatas=[doc.metadata],
                collection=f"{self.collection_prefix}_entities",
            )

    async def search_by_vector(
        self,
        vector: list[float],
        limit: int = 10,
        entity_type: EntityType | None = None,
        tenant_id: str | None = None,
    ) -> list[Entity]:
        """Search entities by vector similarity using vector store

        البحث عن الكيانات بالتشابه المتجهي
        """
        if not self._vector_store:
            return []

        # Build filter
        filter_dict = {}
        if entity_type:
            filter_dict["type"] = entity_type.value
        if tenant_id:
            filter_dict["tenant_id"] = tenant_id

        results = await self._vector_store.search(
            vector=vector,
            collection=f"{self.collection_prefix}_entities",
            top_k=limit,
            filter=filter_dict if filter_dict else None,
        )

        entities = []
        for result in results:
            entity_data = result.metadata.get("entity_data")
            if entity_data:
                entities.append(Entity.from_dict(entity_data))
            else:
                # Fallback to in-memory store
                entity = await self.get_entity(result.id)
                if entity:
                    entities.append(entity)

        return entities

    async def persist(self) -> dict[str, int]:
        """Persist all in-memory data to vector store

        حفظ جميع البيانات من الذاكرة إلى مخزن المتجهات
        """
        if not self._vector_store:
            return {"entities": 0, "relationships": 0}

        entities_saved = 0
        relationships_saved = 0

        # Persist entities
        for entity in self._entities.values():
            if entity.embedding:
                await self.add_entity(entity)  # This will save to vector store
                entities_saved += 1

        return {
            "entities": entities_saved,
            "relationships": relationships_saved,
        }

    async def load(self, tenant_id: str | None = None) -> dict[str, int]:
        """Load entities from vector store into memory

        تحميل الكيانات من مخزن المتجهات إلى الذاكرة
        """
        if not self._vector_store:
            return {"entities": 0, "relationships": 0}

        # This is a simplified load - in production, you'd want pagination
        # For now, we rely on the search functionality

        return {"entities": len(self._entities), "relationships": len(self._relationships)}

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics including vector store info"""
        stats = super().get_stats()
        stats["persistent"] = self._vector_store is not None
        stats["initialized"] = self._initialized
        return stats


async def get_persistent_graph_memory(
    tenant_id: str = "default",
    collection_prefix: str = "graph_memory",
) -> GraphMemory:
    """Get graph memory with persistent storage

    الحصول على ذاكرة الرسم البياني مع التخزين المستمر

    Args:
        tenant_id: Tenant ID for multi-tenant support
        collection_prefix: Prefix for vector store collections

    Returns:
        GraphMemory instance with persistent backend
    """
    store = PersistentGraphStore(collection_prefix=collection_prefix)
    await store.initialize()

    return GraphMemory(
        store=store,
        tenant_id=tenant_id,
    )
