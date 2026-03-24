"""
Integrations API Endpoints
نقاط نهاية API للتكاملات

Exposes AraBERT, Sentinel Hub, AgML, and CrewAI integrations.
"""

from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...integrations import CrewService, MLService, NLPService, SatelliteService

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}


logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/integrations",
    tags=["Integrations | التكاملات"],
)

# Global service instances (initialized in main.py)
nlp_service: NLPService | None = None
satellite_service: SatelliteService | None = None
ml_service: MLService | None = None
crew_service: CrewService | None = None


# ==============================================================================
# Schemas
# ==============================================================================


class NLPRequest(BaseModel):
    """Request for NLP processing."""

    text: str = Field(..., description="Text to process | النص للمعالجة")


class NLPResponse(BaseModel):
    """Response from NLP processing."""

    original_text: str
    normalized_text: str
    is_arabic: bool
    intent: dict[str, Any]
    entities: list[dict[str, Any]]
    sentiment: dict[str, Any]


class NDVIRequest(BaseModel):
    """Request for NDVI analysis."""

    field_id: str = Field(..., description="Field ID | معرف الحقل")
    coordinates: list[list[float]] = Field(
        ...,
        description="Field coordinates [[lon, lat], ...] | إحداثيات الحقل",
        min_length=3,
    )
    area_hectares: float = Field(default=1.0, ge=0.1, le=1000)
    date: str | None = Field(default=None, description="Analysis date (ISO format)")


class CropHealthResponse(BaseModel):
    """Response from crop health analysis."""

    field_id: str
    analysis_date: str
    ndvi: dict[str, float]
    health_status: str
    health_status_ar: str
    trend: str
    trend_ar: str
    data_source: str
    recommendations: list[str]
    recommendations_ar: list[str]


class DatasetListRequest(BaseModel):
    """Request for listing datasets."""

    dataset_type: str | None = Field(default=None, description="Filter by type")
    crop_type: str | None = Field(default=None, description="Filter by crop")


class CrewQueryRequest(BaseModel):
    """Request for crew query."""

    query: str = Field(..., description="Query for the agricultural crew | استعلام للطاقم الزراعي")
    context: dict[str, Any] | None = Field(
        default=None,
        description="Additional context | سياق إضافي",
    )


class CrewQueryResponse(BaseModel):
    """Response from crew query."""

    query: str
    answer: str
    answer_ar: str
    agents_used: list[str]
    execution_time_ms: float
    tasks: list[dict[str, Any]]


# ==============================================================================
# Helper Functions
# ==============================================================================


def get_nlp_service() -> NLPService:
    """Get NLP service instance."""
    if nlp_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP service not initialized",
        )
    return nlp_service


def get_satellite_service() -> SatelliteService:
    """Get satellite service instance."""
    if satellite_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Satellite service not initialized",
        )
    return satellite_service


def get_ml_service() -> MLService:
    """Get ML service instance."""
    if ml_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML service not initialized",
        )
    return ml_service


def get_crew_service() -> CrewService:
    """Get crew service instance."""
    if crew_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Crew service not initialized",
        )
    return crew_service


# ==============================================================================
# NLP Endpoints
# ==============================================================================


@router.post("/nlp/process", response_model=NLPResponse)
async def process_nlp(request: NLPRequest, _user=Depends(get_current_user)) -> NLPResponse:
    """
    Process text with Arabic NLP (AraBERT).
    معالجة النص باستخدام NLP العربية (AraBERT)

    Features:
    - Intent classification
    - Named Entity Recognition (crops, diseases, pests)
    - Sentiment analysis
    - Arabic text normalization
    """
    svc = get_nlp_service()
    result = svc.process_query(request.text)
    return NLPResponse(**result)


@router.get("/nlp/intent/{text}")
async def classify_intent(text: str, _user=Depends(get_current_user)) -> dict[str, Any]:
    """
    Classify the intent of a query.
    تصنيف نية الاستعلام
    """
    svc = get_nlp_service()
    intent, confidence = svc.classify_intent(text)
    return {
        "text": text,
        "intent": intent,
        "confidence": confidence,
    }


# ==============================================================================
# Satellite/NDVI Endpoints
# ==============================================================================


@router.post("/satellite/ndvi")
async def get_ndvi(request: NDVIRequest, _user=Depends(get_current_user)) -> dict[str, Any]:
    """
    Get NDVI for a field using Sentinel-2.
    الحصول على NDVI لحقل باستخدام Sentinel-2

    Uses free Sentinel Hub API for satellite imagery.
    """
    svc = get_satellite_service()

    # Parse date if provided
    date = None
    if request.date:
        date = datetime.fromisoformat(request.date.replace("Z", "+00:00"))

    # Convert coordinates
    coords = [(c[0], c[1]) for c in request.coordinates]

    return await svc.get_field_ndvi(
        field_id=request.field_id,
        coordinates=coords,
        area_hectares=request.area_hectares,
        date=date,
    )


@router.post("/satellite/crop-health", response_model=CropHealthResponse)
async def analyze_crop_health(request: NDVIRequest, _user=Depends(get_current_user)) -> CropHealthResponse:
    """
    Comprehensive crop health analysis.
    تحليل شامل لصحة المحصول

    Includes NDVI trends and recommendations.
    """
    svc = get_satellite_service()

    coords = [(c[0], c[1]) for c in request.coordinates]

    result = await svc.analyze_crop_health(
        field_id=request.field_id,
        coordinates=coords,
        area_hectares=request.area_hectares,
    )

    return CropHealthResponse(**result)


# ==============================================================================
# ML Dataset Endpoints
# ==============================================================================


@router.get("/ml/datasets")
async def list_datasets(
    dataset_type: str | None = None,
    crop_type: str | None = None,
) -> dict[str, Any]:
    """
    List available agricultural ML datasets (AgML).
    عرض مجموعات بيانات التعلم الآلي الزراعية المتاحة

    Includes PlantVillage, wheat rust, tomato diseases, etc.
    """
    svc = get_ml_service()
    datasets = svc.list_datasets(dataset_type, crop_type)
    return {
        "count": len(datasets),
        "datasets": datasets,
    }


@router.get("/ml/diseases/{crop}")
async def get_disease_classes(crop: str) -> dict[str, Any]:
    """
    Get disease classes for a crop type.
    الحصول على فئات الأمراض لنوع محصول
    """
    svc = get_ml_service()
    classes = svc.get_disease_classes(crop)
    return {
        "crop": crop,
        "diseases": classes,
    }


@router.get("/ml/yield-features")
async def get_yield_features() -> dict[str, Any]:
    """
    Get features used for yield prediction.
    الحصول على الميزات المستخدمة للتنبؤ بالإنتاجية
    """
    svc = get_ml_service()
    features = svc.get_yield_features()
    return {
        "count": len(features),
        "features": features,
    }


@router.get("/ml/recommended-datasets")
async def get_recommended_datasets(region: str = "middle_east") -> dict[str, Any]:
    """
    Get recommended datasets for a region.
    الحصول على مجموعات البيانات الموصى بها لمنطقة
    """
    svc = get_ml_service()
    datasets = svc.get_recommended_datasets(region)
    return {
        "region": region,
        "datasets": datasets,
    }


# ==============================================================================
# CrewAI Multi-Agent Endpoints
# ==============================================================================


@router.post("/crew/query", response_model=CrewQueryResponse)
async def query_crew(request: CrewQueryRequest, _user=Depends(get_current_user)) -> CrewQueryResponse:
    """
    Query the agricultural AI crew (CrewAI).
    استعلام طاقم الذكاء الاصطناعي الزراعي

    Uses multiple specialized agents:
    - Crop Advisor
    - Irrigation Expert
    - Disease Diagnostician
    - Pest Controller
    - Soil Analyst
    """
    svc = get_crew_service()
    result = await svc.query(request.query, request.context)
    return CrewQueryResponse(**result)


@router.get("/crew/agents")
async def list_agents() -> dict[str, Any]:
    """
    List available agent roles.
    عرض أدوار الوكلاء المتاحة
    """
    svc = get_crew_service()
    agents = svc.get_available_agents()
    return {
        "count": len(agents),
        "agents": agents,
    }


# ==============================================================================
# Health Check
# ==============================================================================


@router.get("/health")
async def integrations_health() -> dict[str, Any]:
    """
    Check health of all integrations.
    فحص صحة جميع التكاملات
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
        "integrations": {
            "nlp": nlp_service is not None,
            "satellite": satellite_service is not None,
            "ml": ml_service is not None,
            "crew": crew_service is not None,
        },
    }
