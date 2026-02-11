"""
Flight planning endpoints - نقاط نهاية تخطيط الرحلات
"""

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/flights", tags=["flight-planning"])


class Coordinate(BaseModel):
    """Coordinate model"""

    lat: float
    lng: float


class SprayFlightRequest(BaseModel):
    """Spray flight plan request"""

    field_id: str
    boundary: List[Coordinate]
    spray_rate_l_ha: float = 10.0
    swath_width_m: float = 5.0
    altitude_m: float = 3.0
    name: str
    name_ar: str | None = None


class FlightPlanResponse(BaseModel):
    """Flight plan response"""

    id: str
    name: str
    total_distance_m: float
    estimated_duration_min: float
    waypoints_count: int


@router.post("/plan/spray", response_model=FlightPlanResponse, status_code=201)
async def create_spray_flight_plan(request: SprayFlightRequest):
    """
    Create spray flight plan - إنشاء خطة رحلة رش

    Args:
        request: Spray flight parameters

    Returns:
        Flight plan details
    """
    # TODO: Use shared.drone_integration.create_spray_flight_plan
    raise HTTPException(
        status_code=501, detail="Not implemented - غير منفذ | قيد التطوير"
    )


@router.post("/plan/mapping", status_code=201)
async def create_mapping_flight_plan():
    """Create mapping flight plan - إنشاء خطة رحلة تصوير"""
    raise HTTPException(
        status_code=501, detail="Not implemented - غير منفذ | قيد التطوير"
    )


@router.post("/plan/perimeter", status_code=201)
async def create_perimeter_flight_plan():
    """Create perimeter flight plan - إنشاء خطة رحلة محيطية"""
    raise HTTPException(
        status_code=501, detail="Not implemented - غير منفذ | قيد التطوير"
    )


@router.post("/weather-check")
async def check_flight_weather():
    """Check weather conditions for flight - فحص حالة الطقس للرحلة"""
    raise HTTPException(
        status_code=501, detail="Not implemented - غير منفذ | قيد التطوير"
    )


@router.post("/estimate")
async def estimate_flight_resources():
    """Estimate flight resources - تقدير موارد الرحلة"""
    raise HTTPException(
        status_code=501, detail="Not implemented - غير منفذ | قيد التطوير"
    )
