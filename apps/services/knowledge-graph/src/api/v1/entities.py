"""
Entity API endpoints
نقاط نهاية API الكيانات
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models import Crop, Disease, Treatment

router = APIRouter(prefix="/api/v1/entities", tags=["entities"])


# ═══════════════════════════════════════════════════════════════════════════════
# Crop Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/crops")
async def list_crops(
    request,
    limit: int = Query(100, ge=1, le=500, description="Maximum crops to return"),
):
    """
    List all crops in the knowledge graph

    Returns a paginated list of all crops with their properties.
    """
    entity_service = request.app.state.entity_service
    try:
        crops = await entity_service.list_crops(limit)
        return {
            "status": "success",
            "total": len(crops),
            "data": crops,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crops/{crop_id}")
async def get_crop(
    request,
    crop_id: str,
):
    """
    Get a specific crop by ID

    Returns detailed information about a crop including its properties and attributes.
    """
    entity_service = request.app.state.entity_service
    try:
        crop = await entity_service.get_crop(crop_id)
        if not crop:
            raise HTTPException(status_code=404, detail=f"Crop '{crop_id}' not found")

        return {
            "status": "success",
            "data": crop.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crops")
async def create_crop(
    request,
    crop: Crop,
):
    """
    Create a new crop in the knowledge graph

    Adds a new crop entity with all its properties.
    """
    entity_service = request.app.state.entity_service
    try:
        success = await entity_service.create_crop(crop)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create crop")

        return {
            "status": "success",
            "message": f"Crop '{crop.id}' created successfully",
            "data": crop.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Disease Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/diseases")
async def list_diseases(
    request,
    limit: int = Query(100, ge=1, le=500, description="Maximum diseases to return"),
):
    """
    List all diseases in the knowledge graph

    Returns a paginated list of all diseases with their properties.
    """
    entity_service = request.app.state.entity_service
    try:
        diseases = await entity_service.list_diseases(limit)
        return {
            "status": "success",
            "total": len(diseases),
            "data": diseases,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diseases/{disease_id}")
async def get_disease(
    request,
    disease_id: str,
):
    """
    Get a specific disease by ID

    Returns detailed information about a disease including symptoms, severity, and pathogen type.
    """
    entity_service = request.app.state.entity_service
    try:
        disease = await entity_service.get_disease(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease '{disease_id}' not found")

        return {
            "status": "success",
            "data": disease.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diseases")
async def create_disease(
    request,
    disease: Disease,
):
    """
    Create a new disease in the knowledge graph

    Adds a new disease entity with all its properties.
    """
    entity_service = request.app.state.entity_service
    try:
        success = await entity_service.create_disease(disease)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create disease")

        return {
            "status": "success",
            "message": f"Disease '{disease.id}' created successfully",
            "data": disease.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Treatment Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/treatments")
async def list_treatments(
    request,
    limit: int = Query(100, ge=1, le=500, description="Maximum treatments to return"),
):
    """
    List all treatments in the knowledge graph

    Returns a paginated list of all treatments with their properties.
    """
    entity_service = request.app.state.entity_service
    try:
        treatments = await entity_service.list_treatments(limit)
        return {
            "status": "success",
            "total": len(treatments),
            "data": treatments,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/treatments/{treatment_id}")
async def get_treatment(
    request,
    treatment_id: str,
):
    """
    Get a specific treatment by ID

    Returns detailed information about a treatment including ingredients, dosage, and safety level.
    """
    entity_service = request.app.state.entity_service
    try:
        treatment = await entity_service.get_treatment(treatment_id)
        if not treatment:
            raise HTTPException(status_code=404, detail=f"Treatment '{treatment_id}' not found")

        return {
            "status": "success",
            "data": treatment.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/treatments")
async def create_treatment(
    request,
    treatment: Treatment,
):
    """
    Create a new treatment in the knowledge graph

    Adds a new treatment entity with all its properties.
    """
    entity_service = request.app.state.entity_service
    try:
        success = await entity_service.create_treatment(treatment)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create treatment")

        return {
            "status": "success",
            "message": f"Treatment '{treatment.id}' created successfully",
            "data": treatment.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Search Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/search")
async def search_entities(
    request,
    q: str = Query(..., description="Search query"),
    entity_type: str | None = Query(None, description="Filter by type (crop, disease, treatment)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
):
    """
    Search for entities by name or description

    Searches across crops, diseases, and treatments.
    """
    entity_service = request.app.state.entity_service
    try:
        results = await entity_service.search(
            query=q,
            entity_type=entity_type,
            limit=limit,
        )
        return {
            "status": "success",
            "data": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
