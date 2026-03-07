"""
Knowledge Graph Service
خدمة الرسم البياني للمعرفة

Handles all graph operations including:
- Node/entity management
- Relationship management
- Path finding
- Graph queries

Uses shared/ai/knowledge/graph_builder.py as the canonical data source
for agricultural entities and relationships.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from models import (
    Crop,
    Disease,
    GraphEdge,
    GraphNode,
    PathResponse,
    Relationship,
    RelationshipType,
    Treatment,
)

# Import shared knowledge graph builder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../shared"))
try:
    from shared.ai.knowledge.graph_builder import build_agricultural_knowledge_graph

    _HAS_SHARED_KG = True
except ImportError:
    _HAS_SHARED_KG = False

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    In-memory knowledge graph using NetworkX.
    For production, this should be backed by PostgreSQL JSONB or Neo4j.
    """

    def __init__(self):
        """Initialize the knowledge graph"""
        self.graph: nx.DiGraph = nx.DiGraph()
        self.entities: dict[str, dict[str, Any]] = {}
        self.relationships: dict[str, Relationship] = {}
        logger.info("Knowledge Graph Service initialized")

    async def initialize(self):
        """Initialize with agricultural knowledge data from shared builder"""
        if _HAS_SHARED_KG:
            logger.info("Initializing Knowledge Graph from shared/ai/knowledge/graph_builder")
            await self._load_from_shared_builder()
        else:
            logger.warning("shared.ai.knowledge not available, using minimal fallback data")
            await self._load_fallback_data()

    async def _load_from_shared_builder(self):
        """Load knowledge graph from the shared canonical builder.

        Uses shared/ai/knowledge/graph_builder.py as the single source of truth
        for all agricultural entities and their relationships.
        """
        kg = build_agricultural_knowledge_graph()

        # Type mapping from builder entity_type to service node types
        _type_handlers = {
            "crop": lambda e: self.add_crop(
                Crop(
                    id=e.id.replace("crop_", ""),
                    name_en=e.name,
                    name_ar=e.name_ar,
                    growing_season=e.properties.get("growing_season", e.properties.get("season", "")),
                    family=e.properties.get("family", ""),
                )
            ),
            "disease": lambda e: self.add_disease(
                Disease(
                    id=e.id.replace("disease_", ""),
                    name_en=e.name,
                    name_ar=e.name_ar,
                    pathogen_type=e.properties.get("pathogen_type", ""),
                    severity_level=e.properties.get("severity_level", 5),
                    symptoms_en=e.properties.get("symptoms_en", []),
                    symptoms_ar=e.properties.get("symptoms_ar", []),
                )
            ),
            "pest": lambda e: self.add_disease(
                Disease(
                    id=e.id.replace("pest_", ""),
                    name_en=e.name,
                    name_ar=e.name_ar,
                    pathogen_type=e.properties.get("type", "insect"),
                    severity_level=e.properties.get("severity_level", 5),
                    symptoms_en=e.properties.get("symptoms_en", []),
                    symptoms_ar=e.properties.get("symptoms_ar", []),
                )
            ),
            "treatment": lambda e: self.add_treatment(
                Treatment(
                    id=e.id.replace("treat_", ""),
                    name_en=e.name,
                    name_ar=e.name_ar,
                    treatment_type=e.properties.get("treatment_type", e.properties.get("type", "")),
                    active_ingredient=e.properties.get("active_ingredient", ""),
                    concentration=str(e.properties.get("concentration", "")),
                    application_method=e.properties.get("application_method", ""),
                    safety_level=e.properties.get("safety_level", 2),
                    cost_per_liter=e.properties.get("cost_per_liter", 0.0),
                )
            ),
            "fertilizer": lambda e: self.add_treatment(
                Treatment(
                    id=e.id.replace("fert_", ""),
                    name_en=e.name,
                    name_ar=e.name_ar,
                    treatment_type="fertilizer",
                    active_ingredient=e.properties.get("type", ""),
                    concentration="",
                    application_method="broadcast",
                    safety_level=1,
                    cost_per_liter=0.0,
                )
            ),
            "irrigation": self._add_generic_entity,
            "equipment": self._add_generic_entity,
        }

        # Add entities
        entity_count = 0
        for entity in kg.entities:
            handler = _type_handlers.get(entity.entity_type)
            if handler:
                await handler(entity)
                entity_count += 1

        # Map relation types to service RelationshipType
        _rel_map = {
            "affects": RelationshipType.AFFECTS,
            "treats": RelationshipType.TREATED_BY,
            "compatible_with": RelationshipType.COMPATIBLE,
            "requires": RelationshipType.REQUIRES,
            "subtype_of": RelationshipType.FOLLOWS,  # closest available type
        }

        # Map entity IDs to their node type prefixes
        entity_type_map = {}
        for entity in kg.entities:
            entity_type_map[entity.id] = entity.entity_type

        # Type prefix mapping for node IDs
        _type_prefix = {
            "crop": "crop",
            "disease": "disease",
            "pest": "disease",
            "treatment": "treatment",
            "fertilizer": "treatment",
            "irrigation": "irrigation",
            "equipment": "equipment",
        }

        # ID strip prefix mapping
        _strip_prefix = {
            "crop": "crop_",
            "disease": "disease_",
            "pest": "pest_",
            "treatment": "treat_",
            "fertilizer": "fert_",
            "irrigation": "irr_",
            "equipment": "equip_",
        }

        # Add relations
        rel_count = 0
        for relation in kg.relations:
            src_type = entity_type_map.get(relation.source_id, "")
            tgt_type = entity_type_map.get(relation.target_id, "")

            src_node_type = _type_prefix.get(src_type, src_type)
            tgt_node_type = _type_prefix.get(tgt_type, tgt_type)

            src_stripped = relation.source_id.replace(_strip_prefix.get(src_type, ""), "", 1)
            tgt_stripped = relation.target_id.replace(_strip_prefix.get(tgt_type, ""), "", 1)

            rel_type = _rel_map.get(relation.relation_type, RelationshipType.AFFECTS)

            success = await self.add_relationship(
                source_type=src_node_type,
                source_id=src_stripped,
                target_type=tgt_node_type,
                target_id=tgt_stripped,
                relationship_type=rel_type,
                confidence=relation.confidence,
            )
            if success:
                rel_count += 1

        logger.info(f"Loaded {entity_count} entities, {rel_count} relationships from shared knowledge graph builder")

    async def _add_generic_entity(self, entity):
        """Add a generic entity (e.g., irrigation method) to the graph"""
        prefix = entity.entity_type
        stripped_id = entity.id.replace(f"{prefix}_", "").replace("irr_", "")
        node_id = f"{prefix}:{stripped_id}"
        self.entities[node_id] = {
            "id": stripped_id,
            "name_en": entity.name,
            "name_ar": entity.name_ar,
            **entity.properties,
        }
        self.graph.add_node(
            node_id,
            node_type=prefix,
            label=entity.name,
            label_ar=entity.name_ar,
        )
        return True

    async def _load_fallback_data(self):
        """Minimal fallback data when shared builder is not available"""
        crops = [
            {"id": "wheat", "name_en": "Wheat", "name_ar": "القمح", "growing_season": "winter", "family": "Poaceae"},
            {
                "id": "tomato",
                "name_en": "Tomato",
                "name_ar": "الطماطم",
                "growing_season": "summer",
                "family": "Solanaceae",
            },
        ]
        for crop in crops:
            await self.add_crop(Crop(**crop))
        logger.info(f"Loaded {len(crops)} fallback crops")

    async def add_crop(self, crop: Crop) -> bool:
        """Add a crop to the knowledge graph"""
        node_id = f"crop:{crop.id}"
        self.entities[node_id] = crop.model_dump()
        self.graph.add_node(
            node_id,
            node_type="crop",
            label=crop.name_en,
            label_ar=crop.name_ar,
        )
        logger.info(f"Added crop: {crop.id}")
        return True

    async def add_disease(self, disease: Disease) -> bool:
        """Add a disease to the knowledge graph"""
        node_id = f"disease:{disease.id}"
        self.entities[node_id] = disease.model_dump()
        self.graph.add_node(
            node_id,
            node_type="disease",
            label=disease.name_en,
            label_ar=disease.name_ar,
        )
        logger.info(f"Added disease: {disease.id}")
        return True

    async def add_treatment(self, treatment: Treatment) -> bool:
        """Add a treatment to the knowledge graph"""
        node_id = f"treatment:{treatment.id}"
        self.entities[node_id] = treatment.model_dump()
        self.graph.add_node(
            node_id,
            node_type="treatment",
            label=treatment.name_en,
            label_ar=treatment.name_ar,
        )
        logger.info(f"Added treatment: {treatment.id}")
        return True

    async def add_relationship(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
        relationship_type: RelationshipType,
        confidence: float = 1.0,
        evidence: list[str] | None = None,
    ) -> bool:
        """Add a relationship between two entities"""
        source_node = f"{source_type}:{source_id}"
        target_node = f"{target_type}:{target_id}"

        # Validate nodes exist
        if source_node not in self.graph or target_node not in self.graph:
            logger.warning(f"One or both nodes do not exist: {source_node}, {target_node}")
            return False

        rel_id = f"{source_node}--{relationship_type}--{target_node}"
        relationship = Relationship(
            id=rel_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type,
            confidence=confidence,
            evidence=evidence,
        )

        self.relationships[rel_id] = relationship
        self.graph.add_edge(
            source_node,
            target_node,
            relationship_type=relationship_type.value,
            confidence=confidence,
            rel_id=rel_id,
        )
        logger.info(f"Added relationship: {rel_id}")
        return True

    async def get_crop(self, crop_id: str) -> Crop | None:
        """Get a crop by ID"""
        node_id = f"crop:{crop_id}"
        if node_id in self.entities:
            return Crop(**self.entities[node_id])
        return None

    async def get_disease(self, disease_id: str) -> Disease | None:
        """Get a disease by ID"""
        node_id = f"disease:{disease_id}"
        if node_id in self.entities:
            return Disease(**self.entities[node_id])
        return None

    async def get_treatment(self, treatment_id: str) -> Treatment | None:
        """Get a treatment by ID"""
        node_id = f"treatment:{treatment_id}"
        if node_id in self.entities:
            return Treatment(**self.entities[node_id])
        return None

    async def get_related_entities(
        self,
        entity_type: str,
        entity_id: str,
        relationship_type: RelationshipType | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get entities related to a given entity"""
        node_id = f"{entity_type}:{entity_id}"

        if node_id not in self.graph:
            return []

        related = []
        successors = self.graph.successors(node_id)

        for successor in successors:
            edge_data = self.graph[node_id][successor]
            edge_rel_type = edge_data.get("relationship_type")

            # Filter by relationship type if specified
            if relationship_type and edge_rel_type != relationship_type.value:
                continue

            if successor in self.entities:
                entity_data = self.entities[successor].copy()
                entity_data["relationship"] = {
                    "type": edge_rel_type,
                    "confidence": edge_data.get("confidence", 1.0),
                }
                related.append(entity_data)

                if len(related) >= limit:
                    break

        return related

    async def find_shortest_path(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
    ) -> PathResponse | None:
        """Find shortest path between two entities"""
        source_node = f"{source_type}:{source_id}"
        target_node = f"{target_type}:{target_id}"

        if source_node not in self.graph or target_node not in self.graph:
            return None

        try:
            path = nx.shortest_path(self.graph, source_node, target_node)
            length = len(path) - 1

            # Build edges
            edges = []
            for i in range(len(path) - 1):
                curr = path[i]
                next_node = path[i + 1]
                edge_data = self.graph[curr][next_node]

                edges.append(
                    GraphEdge(
                        id=f"{curr}-->{next_node}",
                        source=curr,
                        target=next_node,
                        relationship_type=RelationshipType(edge_data.get("relationship_type")),
                        confidence=edge_data.get("confidence", 1.0),
                    )
                )

            # Get start and end node details
            start_node_data = self.entities.get(path[0], {})
            end_node_data = self.entities.get(path[-1], {})

            start_type, start_id = path[0].split(":", 1)
            end_type, end_id = path[-1].split(":", 1)

            return PathResponse(
                start_node=GraphNode(
                    id=path[0],
                    node_type=start_type,
                    label=start_node_data.get("name_en", ""),
                    label_ar=start_node_data.get("name_ar"),
                    metadata={},
                ),
                end_node=GraphNode(
                    id=path[-1],
                    node_type=end_type,
                    label=end_node_data.get("name_en", ""),
                    label_ar=end_node_data.get("name_ar"),
                    metadata={},
                ),
                path=path,
                length=length,
                edges=edges,
                explanation=f"Found path of length {length} from {start_id} to {end_id}",
            )
        except nx.NetworkXNoPath:
            return None

    async def search_entities(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for entities by name or description"""
        results = []
        query_lower = query.lower()

        for node_id, entity_data in self.entities.items():
            node_type = node_id.split(":")[0]

            # Filter by entity type if specified
            if entity_type and node_type != entity_type:
                continue

            # Search in English and Arabic names and descriptions
            matches = False
            for field in ["name_en", "name_ar", "description_en", "description_ar"]:
                if field in entity_data:
                    value = str(entity_data.get(field, "")).lower()
                    if query_lower in value:
                        matches = True
                        break

            if matches:
                entity_data_copy = entity_data.copy()
                entity_data_copy["id"] = node_id
                results.append(entity_data_copy)

                if len(results) >= limit:
                    break

        return results

    async def get_all_crops(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get all crops"""
        crops = []
        for node_id, data in self.entities.items():
            if node_id.startswith("crop:"):
                data_copy = data.copy()
                data_copy["id"] = node_id
                crops.append(data_copy)
                if len(crops) >= limit:
                    break
        return crops

    async def get_all_diseases(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get all diseases"""
        diseases = []
        for node_id, data in self.entities.items():
            if node_id.startswith("disease:"):
                data_copy = data.copy()
                data_copy["id"] = node_id
                diseases.append(data_copy)
                if len(diseases) >= limit:
                    break
        return diseases

    async def get_all_treatments(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get all treatments"""
        treatments = []
        for node_id, data in self.entities.items():
            if node_id.startswith("treatment:"):
                data_copy = data.copy()
                data_copy["id"] = node_id
                treatments.append(data_copy)
                if len(treatments) >= limit:
                    break
        return treatments

    async def get_graph_stats(self) -> dict[str, Any]:
        """Get graph statistics"""
        crop_count = sum(1 for node in self.graph.nodes() if node.startswith("crop:"))
        disease_count = sum(1 for node in self.graph.nodes() if node.startswith("disease:"))
        treatment_count = sum(1 for node in self.graph.nodes() if node.startswith("treatment:"))

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "crops": crop_count,
            "diseases": disease_count,
            "treatments": treatment_count,
            "relationships": len(self.relationships),
        }

    async def health_check(self) -> bool:
        """Check service health"""
        try:
            # Verify graph has data
            if self.graph.number_of_nodes() == 0:
                logger.warning("Knowledge graph is empty")
                return False
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
