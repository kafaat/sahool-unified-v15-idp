"""
Entity Service - CRUD operations for graph entities
خدمة الكيانات - عمليات CRUD لكيانات الرسم البياني
"""

import logging
from typing import Any, Dict, List, Optional

from models import Crop, Disease, Treatment

logger = logging.getLogger(__name__)


class EntityService:
    """Service for managing individual entities"""

    def __init__(self, graph_service: Any):
        """Initialize entity service with graph service"""
        self.graph = graph_service

    async def create_crop(self, crop: Crop) -> bool:
        """Create a new crop"""
        try:
            await self.graph.add_crop(crop)
            logger.info(f"Created crop: {crop.id}")
            return True
        except Exception as e:
            logger.error(f"Error creating crop: {e}")
            return False

    async def create_disease(self, disease: Disease) -> bool:
        """Create a new disease"""
        try:
            await self.graph.add_disease(disease)
            logger.info(f"Created disease: {disease.id}")
            return True
        except Exception as e:
            logger.error(f"Error creating disease: {e}")
            return False

    async def create_treatment(self, treatment: Treatment) -> bool:
        """Create a new treatment"""
        try:
            await self.graph.add_treatment(treatment)
            logger.info(f"Created treatment: {treatment.id}")
            return True
        except Exception as e:
            logger.error(f"Error creating treatment: {e}")
            return False

    async def get_crop(self, crop_id: str) -> Crop | None:
        """Retrieve a crop by ID"""
        return await self.graph.get_crop(crop_id)

    async def get_disease(self, disease_id: str) -> Disease | None:
        """Retrieve a disease by ID"""
        return await self.graph.get_disease(disease_id)

    async def get_treatment(self, treatment_id: str) -> Treatment | None:
        """Retrieve a treatment by ID"""
        return await self.graph.get_treatment(treatment_id)

    async def list_crops(self, limit: int = 100) -> list[dict[str, Any]]:
        """List all crops"""
        crops = await self.graph.get_all_crops(limit)
        return [self._format_crop_response(crop) for crop in crops]

    async def list_diseases(self, limit: int = 100) -> list[dict[str, Any]]:
        """List all diseases"""
        diseases = await self.graph.get_all_diseases(limit)
        return [self._format_disease_response(disease) for disease in diseases]

    async def list_treatments(self, limit: int = 100) -> list[dict[str, Any]]:
        """List all treatments"""
        treatments = await self.graph.get_all_treatments(limit)
        return [self._format_treatment_response(treatment) for treatment in treatments]

    async def search(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Search across all entity types"""
        results = await self.graph.search_entities(query, entity_type, limit)

        # Organize results by type
        organized = {"crops": [], "diseases": [], "treatments": []}

        for result in results:
            entity_id = result.get("id", "")
            if entity_id.startswith("crop:"):
                organized["crops"].append(self._format_crop_response(result))
            elif entity_id.startswith("disease:"):
                organized["diseases"].append(self._format_disease_response(result))
            elif entity_id.startswith("treatment:"):
                organized["treatments"].append(self._format_treatment_response(result))

        return {
            "query": query,
            "total_results": len(results),
            "results": organized,
        }

    @staticmethod
    def _format_crop_response(crop: dict[str, Any]) -> dict[str, Any]:
        """Format crop response"""
        entity_id = crop.get("id", "")
        if entity_id.startswith("crop:"):
            entity_id = entity_id[5:]  # Remove 'crop:' prefix

        return {
            "id": entity_id,
            "name_en": crop.get("name_en"),
            "name_ar": crop.get("name_ar"),
            "description_en": crop.get("description_en"),
            "description_ar": crop.get("description_ar"),
            "growing_season": crop.get("growing_season"),
            "family": crop.get("family"),
        }

    @staticmethod
    def _format_disease_response(disease: dict[str, Any]) -> dict[str, Any]:
        """Format disease response"""
        entity_id = disease.get("id", "")
        if entity_id.startswith("disease:"):
            entity_id = entity_id[8:]  # Remove 'disease:' prefix

        return {
            "id": entity_id,
            "name_en": disease.get("name_en"),
            "name_ar": disease.get("name_ar"),
            "description_en": disease.get("description_en"),
            "description_ar": disease.get("description_ar"),
            "pathogen_type": disease.get("pathogen_type"),
            "symptoms_en": disease.get("symptoms_en"),
            "symptoms_ar": disease.get("symptoms_ar"),
            "severity_level": disease.get("severity_level"),
            "incubation_days": disease.get("incubation_days"),
        }

    @staticmethod
    def _format_treatment_response(treatment: dict[str, Any]) -> dict[str, Any]:
        """Format treatment response"""
        entity_id = treatment.get("id", "")
        if entity_id.startswith("treatment:"):
            entity_id = entity_id[10:]  # Remove 'treatment:' prefix

        return {
            "id": entity_id,
            "name_en": treatment.get("name_en"),
            "name_ar": treatment.get("name_ar"),
            "description_en": treatment.get("description_en"),
            "description_ar": treatment.get("description_ar"),
            "treatment_type": treatment.get("treatment_type"),
            "active_ingredient": treatment.get("active_ingredient"),
            "concentration": treatment.get("concentration"),
            "application_method": treatment.get("application_method"),
            "safety_level": treatment.get("safety_level"),
            "cost_per_liter": treatment.get("cost_per_liter"),
        }
