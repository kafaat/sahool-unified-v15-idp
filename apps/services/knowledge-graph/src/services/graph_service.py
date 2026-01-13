"""
Knowledge Graph Service
خدمة الرسم البياني للمعرفة

Handles all graph operations including:
- Node/entity management
- Relationship management
- Path finding
- Graph queries
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

from models import (
    Crop,
    Disease,
    Treatment,
    Relationship,
    RelationshipType,
    GraphNode,
    GraphEdge,
    PathResponse,
)

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    In-memory knowledge graph using NetworkX.
    For production, this should be backed by PostgreSQL JSONB or Neo4j.
    """

    def __init__(self):
        """Initialize the knowledge graph"""
        self.graph: nx.DiGraph = nx.DiGraph()
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Relationship] = {}
        logger.info("Knowledge Graph Service initialized")

    async def initialize(self):
        """Initialize with sample data"""
        logger.info("Initializing Knowledge Graph with sample data")
        await self._load_sample_data()

    async def _load_sample_data(self):
        """Load sample knowledge graph data"""
        # Sample crops
        crops = [
            {
                "id": "wheat",
                "name_en": "Wheat",
                "name_ar": "القمح",
                "growing_season": "winter",
                "family": "Poaceae",
            },
            {
                "id": "tomato",
                "name_en": "Tomato",
                "name_ar": "الطماطم",
                "growing_season": "summer",
                "family": "Solanaceae",
            },
            {
                "id": "potato",
                "name_en": "Potato",
                "name_ar": "البطاطس",
                "growing_season": "spring",
                "family": "Solanaceae",
            },
        ]

        # Sample diseases
        diseases = [
            {
                "id": "powdery-mildew",
                "name_en": "Powdery Mildew",
                "name_ar": "البياض الدقيقي",
                "pathogen_type": "fungal",
                "severity_level": 7,
                "symptoms_en": ["White powder coating", "Leaf distortion"],
                "symptoms_ar": ["طلاء أبيض ناعم", "تشويه الأوراق"],
            },
            {
                "id": "late-blight",
                "name_en": "Late Blight",
                "name_ar": "الآفة المتأخرة",
                "pathogen_type": "fungal",
                "severity_level": 9,
                "symptoms_en": ["Water-soaked lesions", "Brown spots"],
                "symptoms_ar": ["آفات مليئة بالماء", "بقع بنية"],
            },
            {
                "id": "leaf-spot",
                "name_en": "Leaf Spot",
                "name_ar": "بقعة الأوراق",
                "pathogen_type": "fungal",
                "severity_level": 5,
                "symptoms_en": ["Circular spots", "Yellow halo"],
                "symptoms_ar": ["بقع دائرية", "هالة صفراء"],
            },
        ]

        # Sample treatments
        treatments = [
            {
                "id": "sulfur-dust",
                "name_en": "Sulfur Dust",
                "name_ar": "مسحوق الكبريت",
                "treatment_type": "fungicide",
                "active_ingredient": "Sulfur",
                "concentration": "100%",
                "application_method": "dust",
                "safety_level": 1,
                "cost_per_liter": 5.0,
            },
            {
                "id": "copper-fungicide",
                "name_en": "Copper Fungicide",
                "name_ar": "مبيد فطري نحاسي",
                "treatment_type": "fungicide",
                "active_ingredient": "Copper sulfate",
                "concentration": "0.5%",
                "application_method": "spray",
                "safety_level": 2,
                "cost_per_liter": 8.0,
            },
            {
                "id": "neem-oil",
                "name_en": "Neem Oil",
                "name_ar": "زيت النيم",
                "treatment_type": "organic",
                "active_ingredient": "Azadirachtin",
                "concentration": "3%",
                "application_method": "spray",
                "safety_level": 1,
                "cost_per_liter": 12.0,
            },
        ]

        # Add entities
        for crop in crops:
            await self.add_crop(Crop(**crop))
        for disease in diseases:
            await self.add_disease(Disease(**disease))
        for treatment in treatments:
            await self.add_treatment(Treatment(**treatment))

        # Add relationships
        relationships = [
            # Powdery mildew affects wheat and tomato
            {
                "source_type": "disease",
                "source_id": "powdery-mildew",
                "target_type": "crop",
                "target_id": "wheat",
                "relationship_type": RelationshipType.AFFECTS,
                "confidence": 0.95,
            },
            {
                "source_type": "disease",
                "source_id": "powdery-mildew",
                "target_type": "crop",
                "target_id": "tomato",
                "relationship_type": RelationshipType.AFFECTS,
                "confidence": 0.90,
            },
            # Late blight affects potato and tomato
            {
                "source_type": "disease",
                "source_id": "late-blight",
                "target_type": "crop",
                "target_id": "potato",
                "relationship_type": RelationshipType.AFFECTS,
                "confidence": 0.99,
            },
            {
                "source_type": "disease",
                "source_id": "late-blight",
                "target_type": "crop",
                "target_id": "tomato",
                "relationship_type": RelationshipType.AFFECTS,
                "confidence": 0.95,
            },
            # Leaf spot affects tomato
            {
                "source_type": "disease",
                "source_id": "leaf-spot",
                "target_type": "crop",
                "target_id": "tomato",
                "relationship_type": RelationshipType.AFFECTS,
                "confidence": 0.85,
            },
            # Powdery mildew treated by sulfur and copper
            {
                "source_type": "disease",
                "source_id": "powdery-mildew",
                "target_type": "treatment",
                "target_id": "sulfur-dust",
                "relationship_type": RelationshipType.TREATED_BY,
                "confidence": 0.95,
            },
            {
                "source_type": "disease",
                "source_id": "powdery-mildew",
                "target_type": "treatment",
                "target_id": "copper-fungicide",
                "relationship_type": RelationshipType.TREATED_BY,
                "confidence": 0.90,
            },
            # Late blight treated by copper and neem
            {
                "source_type": "disease",
                "source_id": "late-blight",
                "target_type": "treatment",
                "target_id": "copper-fungicide",
                "relationship_type": RelationshipType.TREATED_BY,
                "confidence": 0.85,
            },
            {
                "source_type": "disease",
                "source_id": "late-blight",
                "target_type": "treatment",
                "target_id": "neem-oil",
                "relationship_type": RelationshipType.TREATED_BY,
                "confidence": 0.70,
            },
            # Sulfur is safe for wheat
            {
                "source_type": "treatment",
                "source_id": "sulfur-dust",
                "target_type": "crop",
                "target_id": "wheat",
                "relationship_type": RelationshipType.COMPATIBLE,
                "confidence": 0.99,
            },
        ]

        for rel_data in relationships:
            rel_type = rel_data.pop("relationship_type")
            confidence = rel_data.pop("confidence", 1.0)
            await self.add_relationship(
                source_type=rel_data["source_type"],
                source_id=rel_data["source_id"],
                target_type=rel_data["target_type"],
                target_id=rel_data["target_id"],
                relationship_type=rel_type,
                confidence=confidence,
            )

        logger.info(
            f"Loaded {len(crops)} crops, {len(diseases)} diseases, "
            f"{len(treatments)} treatments, {len(relationships)} relationships"
        )

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
        evidence: Optional[List[str]] = None,
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

    async def get_crop(self, crop_id: str) -> Optional[Crop]:
        """Get a crop by ID"""
        node_id = f"crop:{crop_id}"
        if node_id in self.entities:
            return Crop(**self.entities[node_id])
        return None

    async def get_disease(self, disease_id: str) -> Optional[Disease]:
        """Get a disease by ID"""
        node_id = f"disease:{disease_id}"
        if node_id in self.entities:
            return Disease(**self.entities[node_id])
        return None

    async def get_treatment(self, treatment_id: str) -> Optional[Treatment]:
        """Get a treatment by ID"""
        node_id = f"treatment:{treatment_id}"
        if node_id in self.entities:
            return Treatment(**self.entities[node_id])
        return None

    async def get_related_entities(
        self,
        entity_type: str,
        entity_id: str,
        relationship_type: Optional[RelationshipType] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
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

            target_type = successor.split(":")[0]
            target_id = successor.split(":", 1)[1]

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
    ) -> Optional[PathResponse]:
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
                        relationship_type=RelationshipType(
                            edge_data.get("relationship_type")
                        ),
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
        entity_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
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

    async def get_all_crops(self, limit: int = 100) -> List[Dict[str, Any]]:
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

    async def get_all_diseases(self, limit: int = 100) -> List[Dict[str, Any]]:
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

    async def get_all_treatments(self, limit: int = 100) -> List[Dict[str, Any]]:
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

    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        crop_count = sum(1 for node in self.graph.nodes() if node.startswith("crop:"))
        disease_count = sum(
            1 for node in self.graph.nodes() if node.startswith("disease:")
        )
        treatment_count = sum(
            1 for node in self.graph.nodes() if node.startswith("treatment:")
        )

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
