"""
Relationship API endpoints
نقاط نهاية API العلاقات
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

logger = logging.getLogger(__name__)

from models import RelationshipType

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/api/v1/relationships", tags=["relationships"])


@router.get("/affected-crops/{disease_id}")
async def get_affected_crops(
    request,
    disease_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    _user=Depends(get_current_user),
):
    """
    Get all crops affected by a disease

    Returns a list of crops that are affected by the specified disease.
    """
    relationship_service = request.app.state.relationship_service
    try:
        crops = await relationship_service.get_affected_crops(disease_id, limit)
        return {
            "status": "success",
            "disease_id": disease_id,
            "affected_crops_count": len(crops),
            "data": crops,
        }
    except Exception as e:
        logger.error("Failed to get affected crops for disease %s: %s", disease_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/disease-treatments/{disease_id}")
async def get_disease_treatments(
    request,
    disease_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """
    Get all treatments for a disease

    Returns a list of treatments that can be used to treat the specified disease.
    """
    relationship_service = request.app.state.relationship_service
    try:
        treatments = await relationship_service.get_disease_treatments(disease_id, limit)
        return {
            "status": "success",
            "disease_id": disease_id,
            "treatments_count": len(treatments),
            "data": treatments,
        }
    except Exception as e:
        logger.error("Failed to get treatments for disease %s: %s", disease_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/crop-compatible-treatments/{crop_id}")
async def get_compatible_treatments(
    request,
    crop_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """
    Get treatments compatible with a crop

    Returns a list of treatments that are safe to use on the specified crop.
    """
    relationship_service = request.app.state.relationship_service
    try:
        treatments = await relationship_service.get_crop_compatible_treatments(crop_id, limit)
        return {
            "status": "success",
            "crop_id": crop_id,
            "compatible_treatments_count": len(treatments),
            "data": treatments,
        }
    except Exception as e:
        logger.error("Failed to get compatible treatments for crop %s: %s", crop_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/diseases-by-crop/{crop_id}")
async def get_diseases_by_crop(
    request,
    crop_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """
    Get diseases that affect a crop

    Returns a list of diseases that can affect the specified crop.
    """
    relationship_service = request.app.state.relationship_service
    try:
        diseases = await relationship_service.get_diseases_affecting_crop(crop_id, limit)
        return {
            "status": "success",
            "crop_id": crop_id,
            "diseases_count": len(diseases),
            "data": diseases,
        }
    except Exception as e:
        logger.error("Failed to get diseases for crop %s: %s", crop_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/preventive-treatments/{disease_id}")
async def get_preventive_treatments(
    request,
    disease_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """
    Get preventive treatments for a disease

    Returns treatments that can prevent the specified disease.
    """
    relationship_service = request.app.state.relationship_service
    try:
        treatments = await relationship_service.get_preventive_treatments(disease_id, limit)
        return {
            "status": "success",
            "disease_id": disease_id,
            "preventive_treatments_count": len(treatments),
            "data": treatments,
        }
    except Exception as e:
        logger.error("Failed to get preventive treatments for disease %s: %s", disease_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/related/{entity_type}/{entity_id}")
async def get_all_related(
    request,
    entity_type: str = Path(..., description="Entity type (crop, disease, treatment)"),
    entity_id: str = Path(..., description="Entity ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """
    Get all entities related to a given entity

    Returns all entities (of any type) that have a relationship with the specified entity.
    """
    relationship_service = request.app.state.relationship_service
    try:
        related = await relationship_service.get_all_related(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
        )
        return {
            "status": "success",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "related_count": len(related),
            "data": related,
        }
    except Exception as e:
        logger.error("Failed to get related entities for %s/%s: %s", entity_type, entity_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/path/{source_type}/{source_id}/{target_type}/{target_id}")
async def find_path(
    request,
    source_type: str = Query(..., description="Source entity type"),
    source_id: str = Query(..., description="Source entity ID"),
    target_type: str = Query(..., description="Target entity type"),
    target_id: str = Query(..., description="Target entity ID"),
):
    """
    Find the relationship path between two entities

    Shows how two entities are connected through intermediate relationships.
    Useful for understanding the connection chain between crops, diseases, and treatments.
    """
    relationship_service = request.app.state.relationship_service
    try:
        path = await relationship_service.find_relationship_path(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
        )

        if not path:
            raise HTTPException(
                status_code=404,
                detail=f"No path found between {source_type}:{source_id} and {target_type}:{target_id}",
            )

        return {
            "status": "success",
            "data": path,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to find relationship path: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.post("/validate")
async def validate_relationship(
    request,
    source_type: str = Query(..., description="Source entity type"),
    source_id: str = Query(..., description="Source entity ID"),
    target_type: str = Query(..., description="Target entity type"),
    target_id: str = Query(..., description="Target entity ID"),
    relationship_type: RelationshipType = Query(..., description="Relationship type"),
    current_user: User = Depends(get_current_user),
):
    """
    Validate if a specific relationship exists

    Checks whether a specific relationship exists between two entities.
    """
    relationship_service = request.app.state.relationship_service
    try:
        result = await relationship_service.validate_relationship(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type,
        )

        return {
            "status": "success",
            "data": result,
        }
    except Exception as e:
        logger.error("Failed to validate relationship: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.post("/add")
async def add_relationship(
    request,
    source_type: str = Query(..., description="Source entity type"),
    source_id: str = Query(..., description="Source entity ID"),
    target_type: str = Query(..., description="Target entity type"),
    target_id: str = Query(..., description="Target entity ID"),
    relationship_type: RelationshipType = Query(..., description="Relationship type"),
    confidence: float = Query(1.0, ge=0.0, le=1.0, description="Confidence score"),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new relationship between two entities

    Adds a new relationship between two entities in the knowledge graph.
    """
    relationship_service = request.app.state.relationship_service
    try:
        success = await relationship_service.add_relationship(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type,
            confidence=confidence,
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to create relationship")

        return {
            "status": "success",
            "message": f"Relationship created: {source_type}:{source_id} -{relationship_type.value}-> {target_type}:{target_id}",
            "data": {
                "source_type": source_type,
                "source_id": source_id,
                "target_type": target_type,
                "target_id": target_id,
                "relationship_type": relationship_type,
                "confidence": confidence,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to add relationship: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")
