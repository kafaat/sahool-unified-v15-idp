"""
Relationship Service - Manage relationships between entities
خدمة العلاقات - إدارة العلاقات بين الكيانات
"""

import logging
from typing import Any, Dict, List, Optional

from models import RelationshipType

logger = logging.getLogger(__name__)


class RelationshipService:
    """Service for managing relationships between entities"""

    def __init__(self, graph_service: Any):
        """Initialize relationship service with graph service"""
        self.graph = graph_service

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
        """Add a new relationship"""
        try:
            result = await self.graph.add_relationship(
                source_type=source_type,
                source_id=source_id,
                target_type=target_type,
                target_id=target_id,
                relationship_type=relationship_type,
                confidence=confidence,
                evidence=evidence,
            )
            if result:
                logger.info(
                    f"Created relationship: {source_type}:{source_id} "
                    f"-[{relationship_type.value}]-> {target_type}:{target_id}"
                )
            return result
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False

    async def get_related_by_type(
        self,
        entity_type: str,
        entity_id: str,
        relationship_type: RelationshipType,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get entities related by a specific relationship type"""
        try:
            return await self.graph.get_related_entities(
                entity_type=entity_type,
                entity_id=entity_id,
                relationship_type=relationship_type,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"Error getting related entities: {e}")
            return []

    async def get_all_related(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all entities related to a given entity"""
        try:
            return await self.graph.get_related_entities(
                entity_type=entity_type,
                entity_id=entity_id,
                relationship_type=None,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"Error getting related entities: {e}")
            return []

    async def find_relationship_path(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Find a path of relationships between two entities"""
        try:
            path = await self.graph.find_shortest_path(
                source_type=source_type,
                source_id=source_id,
                target_type=target_type,
                target_id=target_id,
            )
            if path:
                return path.model_dump()
            return None
        except Exception as e:
            logger.error(f"Error finding relationship path: {e}")
            return None

    async def get_affected_crops(
        self,
        disease_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all crops affected by a disease"""
        return await self.get_related_by_type(
            entity_type="disease",
            entity_id=disease_id,
            relationship_type=RelationshipType.AFFECTS,
            limit=limit,
        )

    async def get_disease_treatments(
        self,
        disease_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all treatments for a disease"""
        return await self.get_related_by_type(
            entity_type="disease",
            entity_id=disease_id,
            relationship_type=RelationshipType.TREATED_BY,
            limit=limit,
        )

    async def get_crop_compatible_treatments(
        self,
        crop_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get treatments compatible with a crop"""
        return await self.get_related_by_type(
            entity_type="crop",
            entity_id=crop_id,
            relationship_type=RelationshipType.COMPATIBLE,
            limit=limit,
        )

    async def get_diseases_affecting_crop(
        self,
        crop_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get diseases that affect a specific crop"""
        # Get all nodes connected to this crop
        related = await self.get_all_related(
            entity_type="crop",
            entity_id=crop_id,
            limit=limit,
        )
        # Filter to only diseases
        return [r for r in related if r.get("id", "").startswith("disease:")]

    async def get_preventive_treatments(
        self,
        disease_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get preventive treatments for a disease"""
        return await self.get_related_by_type(
            entity_type="disease",
            entity_id=disease_id,
            relationship_type=RelationshipType.PREVENTS,
            limit=limit,
        )

    async def validate_relationship(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
        relationship_type: RelationshipType,
    ) -> Dict[str, Any]:
        """Validate if a relationship exists and return its details"""
        try:
            rel_id = f"{source_type}:{source_id}--{relationship_type.value}--{target_type}:{target_id}"
            if rel_id in self.graph.relationships:
                rel = self.graph.relationships[rel_id]
                return {
                    "exists": True,
                    "relationship": rel.model_dump(),
                }
            return {
                "exists": False,
                "relationship": None,
            }
        except Exception as e:
            logger.error(f"Error validating relationship: {e}")
            return {
                "exists": False,
                "relationship": None,
                "error": str(e),
            }
