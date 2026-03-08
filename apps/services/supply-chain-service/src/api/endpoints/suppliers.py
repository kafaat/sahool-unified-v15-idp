"""Supplier endpoints for Supply Chain Service."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from ...core.config import settings
from ..schemas import (
    QuoteRequest,
    Supplier,
    SupplierListResponse,
    SupplierQuote,
)

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

router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])

# Mock supplier data
MOCK_SUPPLIERS: dict[UUID, Supplier] = {}


def _init_mock_suppliers() -> None:
    """Initialize mock suppliers."""
    if MOCK_SUPPLIERS:
        return

    suppliers_data = [
        {
            "name": "Al-Rashid Agricultural Supplies",
            "name_ar": "مستلزمات الراشد الزراعية",
            "location": "Riyadh, Saudi Arabia",
            "location_ar": "الرياض، المملكة العربية السعودية",
            "latitude": 24.7136,
            "longitude": 46.6753,
            "rating": 4.8,
            "total_reviews": 245,
            "delivery_time_days": 2,
            "phone": "+966112345678",
            "email": "info@alrashid-agri.sa",
            "is_verified": True,
        },
        {
            "name": "Green Fields Trading",
            "name_ar": "تجارة الحقول الخضراء",
            "location": "Jeddah, Saudi Arabia",
            "location_ar": "جدة، المملكة العربية السعودية",
            "latitude": 21.4858,
            "longitude": 39.1925,
            "rating": 4.5,
            "total_reviews": 189,
            "delivery_time_days": 3,
            "phone": "+966126543210",
            "email": "sales@greenfields.sa",
            "is_verified": True,
        },
        {
            "name": "Sahara Agro Solutions",
            "name_ar": "حلول صحارى الزراعية",
            "location": "Dammam, Saudi Arabia",
            "location_ar": "الدمام، المملكة العربية السعودية",
            "latitude": 26.4207,
            "longitude": 50.0888,
            "rating": 4.3,
            "total_reviews": 156,
            "delivery_time_days": 4,
            "phone": "+966138765432",
            "email": "contact@sahara-agro.sa",
            "is_verified": True,
        },
        {
            "name": "Farm Fresh Supplies",
            "name_ar": "مستلزمات المزرعة الطازجة",
            "location": "Al-Kharj, Saudi Arabia",
            "location_ar": "الخرج، المملكة العربية السعودية",
            "latitude": 24.1500,
            "longitude": 47.3000,
            "rating": 4.6,
            "total_reviews": 98,
            "delivery_time_days": 1,
            "phone": "+966114567890",
            "email": "orders@farmfresh.sa",
            "is_verified": False,
        },
        {
            "name": "Desert Bloom Agricultural",
            "name_ar": "زهرة الصحراء الزراعية",
            "location": "Tabuk, Saudi Arabia",
            "location_ar": "تبوك، المملكة العربية السعودية",
            "latitude": 28.3838,
            "longitude": 36.5550,
            "rating": 4.2,
            "total_reviews": 67,
            "delivery_time_days": 5,
            "phone": "+966144321098",
            "email": "info@desertbloom.sa",
            "is_verified": True,
        },
    ]

    for data in suppliers_data:
        supplier_id = uuid4()
        MOCK_SUPPLIERS[supplier_id] = Supplier(id=supplier_id, **data)


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers."""
    import math

    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@router.get(
    "",
    response_model=SupplierListResponse,
    summary="List Suppliers | قائمة الموردين",
    description="Get a paginated list of agricultural suppliers. احصل على قائمة مُرقمة بالموردين الزراعيين.",
)
async def list_suppliers(
    is_verified: bool | None = Query(None, description="Filter by verification status"),
    min_rating: float | None = Query(None, ge=0, le=5, description="Minimum rating"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _user=Depends(get_current_user),
) -> SupplierListResponse:
    """List suppliers with optional filtering."""
    _init_mock_suppliers()

    logger.info("listing_suppliers", is_verified=is_verified, min_rating=min_rating)

    suppliers = list(MOCK_SUPPLIERS.values())

    # Apply filters
    if is_verified is not None:
        suppliers = [s for s in suppliers if s.is_verified == is_verified]

    if min_rating is not None:
        suppliers = [s for s in suppliers if s.rating >= min_rating]

    # Sort by rating (descending)
    suppliers.sort(key=lambda s: s.rating, reverse=True)

    # Pagination
    total = len(suppliers)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = suppliers[start:end]

    return SupplierListResponse(
        items=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/nearby",
    response_model=SupplierListResponse,
    summary="Find Nearby Suppliers | العثور على موردين قريبين",
    description="Find suppliers near a specific location. العثور على موردين بالقرب من موقع محدد.",
)
async def find_nearby_suppliers(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(
        default=settings.SUPPLIER_SEARCH_RADIUS_KM,
        ge=1,
        le=500,
        description="Search radius in kilometers",
    ),
    min_rating: float | None = Query(None, ge=0, le=5),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> SupplierListResponse:
    """Find suppliers within a radius of the given location."""
    _init_mock_suppliers()

    logger.info(
        "finding_nearby_suppliers",
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )

    nearby = []
    for supplier in MOCK_SUPPLIERS.values():
        distance = _haversine_distance(latitude, longitude, supplier.latitude, supplier.longitude)
        if distance <= radius_km:
            nearby.append((supplier, distance))

    # Filter by rating
    if min_rating is not None:
        nearby = [(s, d) for s, d in nearby if s.rating >= min_rating]

    # Sort by distance
    nearby.sort(key=lambda x: x[1])

    suppliers = [s for s, _ in nearby]

    # Pagination
    total = len(suppliers)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = suppliers[start:end]

    return SupplierListResponse(
        items=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{supplier_id}",
    response_model=Supplier,
    summary="Get Supplier | الحصول على مورد",
    description="Get detailed information about a specific supplier. الحصول على معلومات تفصيلية عن مورد محدد.",
)
async def get_supplier(supplier_id: UUID) -> Supplier:
    """Get supplier by ID."""
    _init_mock_suppliers()

    logger.info("getting_supplier", supplier_id=str(supplier_id))

    supplier = MOCK_SUPPLIERS.get(supplier_id)
    if not supplier:
        logger.warning("supplier_not_found", supplier_id=str(supplier_id))
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Supplier not found",
                "message_ar": "المورد غير موجود",
                "supplier_id": str(supplier_id),
            },
        )

    return supplier


@router.post(
    "/{supplier_id}/quote",
    response_model=SupplierQuote,
    summary="Request Quote | طلب عرض سعر",
    description="Request a quote from a supplier for a specific product. طلب عرض سعر من مورد لمنتج محدد.",
)
async def request_quote(supplier_id: UUID, request: QuoteRequest) -> SupplierQuote:
    """Request a quote from a supplier."""
    _init_mock_suppliers()

    logger.info(
        "requesting_quote",
        supplier_id=str(supplier_id),
        product_id=str(request.product_id),
        quantity=request.quantity,
    )

    supplier = MOCK_SUPPLIERS.get(supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Supplier not found",
                "message_ar": "المورد غير موجود",
            },
        )

    # Mock quote generation
    import random

    unit_price = round(random.uniform(10, 100), 2)
    total_price = round(unit_price * request.quantity, 2)

    quote = SupplierQuote(
        id=uuid4(),
        supplier_id=supplier_id,
        supplier_name=supplier.name,
        supplier_name_ar=supplier.name_ar,
        product_id=request.product_id,
        product_name="Requested Product",
        product_name_ar="المنتج المطلوب",
        quantity=request.quantity,
        unit_price=unit_price,
        total_price=total_price,
        delivery_days=supplier.delivery_time_days,
        availability="in_stock",
        valid_until=datetime.utcnow() + timedelta(hours=settings.QUOTE_VALIDITY_HOURS),
        notes="Quote valid for 24 hours",
        notes_ar="العرض صالح لمدة 24 ساعة",
    )

    logger.info(
        "quote_generated",
        quote_id=str(quote.id),
        total_price=total_price,
    )

    return quote
