"""
SAHOOL Farmer CRM Service
==========================
Customer Relationship Management for farmers.

Inspired by: CordysCRM
Features:
- Farmer lifecycle management
- Harvest deal pipeline
- Interaction tracking
- Natural language queries (SQLBot-inspired)

Port: 8131
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Any
from datetime import datetime, date
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from shared.crm import (
    FarmerCRMService,
    FarmerQueryBot,
    Farmer,
    FarmerStatus,
    HarvestDeal,
    DealStage,
    Interaction,
    InteractionType,
    SupplyContract,
    ContractStatus,
)

# Service configuration
SERVICE_NAME = "crm-service"
SERVICE_NAME_AR = "خدمة إدارة علاقات المزارعين"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8131


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════

class FarmerCreateRequest(BaseModel):
    """Request to create a farmer"""
    name: str = Field(..., min_length=2, max_length=100)
    name_ar: str | None = Field(None, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    email: EmailStr | None = None
    national_id: str | None = None
    farm_location: str | None = None
    farm_location_ar: str | None = None
    farm_size_hectares: float | None = Field(None, ge=0)
    primary_crops: list[str] = []
    tenant_id: str


class FarmerUpdateRequest(BaseModel):
    """Request to update a farmer"""
    name: str | None = Field(None, min_length=2, max_length=100)
    name_ar: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    email: EmailStr | None = None
    farm_location: str | None = None
    farm_location_ar: str | None = None
    farm_size_hectares: float | None = Field(None, ge=0)
    primary_crops: list[str] | None = None
    status: str | None = None
    tags: list[str] | None = None


class FarmerResponse(BaseModel):
    """Farmer response model"""
    id: str
    name: str
    name_ar: str | None
    phone: str
    email: str | None
    national_id: str | None
    farm_location: str | None
    farm_location_ar: str | None
    farm_size_hectares: float | None
    primary_crops: list[str]
    status: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    last_interaction_at: datetime | None


class HarvestDealCreateRequest(BaseModel):
    """Request to create a harvest deal"""
    farmer_id: str
    crop_type: str
    crop_type_ar: str | None = None
    expected_quantity_tons: float = Field(..., gt=0)
    expected_harvest_date: date
    price_per_ton: float | None = Field(None, gt=0)
    notes: str | None = None
    notes_ar: str | None = None


class HarvestDealResponse(BaseModel):
    """Harvest deal response model"""
    id: str
    farmer_id: str
    crop_type: str
    crop_type_ar: str | None
    expected_quantity_tons: float
    actual_quantity_tons: float | None
    expected_harvest_date: date
    actual_harvest_date: date | None
    price_per_ton: float | None
    total_value: float | None
    stage: str
    notes: str | None
    notes_ar: str | None
    created_at: datetime
    updated_at: datetime


class InteractionCreateRequest(BaseModel):
    """Request to log an interaction"""
    farmer_id: str
    interaction_type: str = Field(..., description="Type: call, visit, whatsapp, sms, email")
    subject: str
    subject_ar: str | None = None
    notes: str | None = None
    notes_ar: str | None = None
    outcome: str | None = None
    follow_up_date: date | None = None


class InteractionResponse(BaseModel):
    """Interaction response model"""
    id: str
    farmer_id: str
    interaction_type: str
    subject: str
    subject_ar: str | None
    notes: str | None
    notes_ar: str | None
    outcome: str | None
    follow_up_date: date | None
    created_at: datetime
    created_by: str | None


class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., description="Natural language query in English or Arabic")
    tenant_id: str


class QueryResponse(BaseModel):
    """Query response model"""
    query: str
    interpreted_as: str
    interpreted_as_ar: str | None
    results: list[dict[str, Any]]
    result_count: int
    execution_time_ms: int


class PipelineStatsResponse(BaseModel):
    """Pipeline statistics response"""
    total_deals: int
    total_value: float
    by_stage: dict[str, dict[str, Any]]
    conversion_rate: float
    average_deal_size: float


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory storage (replace with database in production)
# ═══════════════════════════════════════════════════════════════════════════════

farmers: dict[str, Farmer] = {}
deals: dict[str, HarvestDeal] = {}
interactions: dict[str, Interaction] = {}

# Initialize services
crm_service = FarmerCRMService()
query_bot = FarmerQueryBot()


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Initialize NATS publisher (if available)
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            from shared.events.publisher import get_publisher
            app.state.publisher = await get_publisher(
                service_name=SERVICE_NAME,
                service_version=SERVICE_VERSION
            )
            app.state.nats_connected = True
            print(f"✅ NATS connected: {nats_url}")
        except Exception as e:
            print(f"⚠️ NATS connection failed: {e}")
            app.state.publisher = None
            app.state.nats_connected = False
    else:
        app.state.publisher = None
        app.state.nats_connected = False

    # Initialize database connection (if available)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            import asyncpg
            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            app.state.db_connected = True
            print(f"✅ Database connected")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            app.state.db_pool = None
            app.state.db_connected = False
    else:
        app.state.db_pool = None
        app.state.db_connected = False

    print(f"✅ {SERVICE_NAME} ready on port {SERVICE_PORT}")

    yield

    # Shutdown
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.close()
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
    print(f"👋 {SERVICE_NAME} shutdown complete")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="SAHOOL Farmer CRM Service",
    description="Customer Relationship Management for farmers | إدارة علاقات المزارعين",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/healthz", tags=["Health"])
def health():
    """Liveness probe"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """Readiness probe"""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


@app.get("/health", tags=["Health"])
def health_detailed():
    """Detailed health status"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
        "database_connected": getattr(app.state, "db_connected", False),
        "nats_connected": getattr(app.state, "nats_connected", False),
        "farmers_count": len(farmers),
        "deals_count": len(deals),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Farmer Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/farmers", response_model=FarmerResponse, tags=["Farmers"])
async def create_farmer(request: FarmerCreateRequest):
    """Create a new farmer | إنشاء مزارع جديد"""
    farmer_id = str(uuid4())
    now = datetime.utcnow()

    farmer = Farmer(
        id=farmer_id,
        name=request.name,
        name_ar=request.name_ar,
        phone=request.phone,
        email=request.email,
        national_id=request.national_id,
        farm_location=request.farm_location,
        farm_location_ar=request.farm_location_ar,
        farm_size_hectares=request.farm_size_hectares,
        primary_crops=request.primary_crops,
        status=FarmerStatus.LEAD,
        tags=[],
        tenant_id=request.tenant_id,
        created_at=now,
        updated_at=now,
    )

    farmers[farmer_id] = farmer

    return FarmerResponse(
        id=farmer.id,
        name=farmer.name,
        name_ar=farmer.name_ar,
        phone=farmer.phone,
        email=farmer.email,
        national_id=farmer.national_id,
        farm_location=farmer.farm_location,
        farm_location_ar=farmer.farm_location_ar,
        farm_size_hectares=farmer.farm_size_hectares,
        primary_crops=farmer.primary_crops,
        status=farmer.status.value,
        tags=farmer.tags,
        created_at=farmer.created_at,
        updated_at=farmer.updated_at,
        last_interaction_at=farmer.last_interaction_at,
    )


@app.get("/api/v1/farmers", response_model=list[FarmerResponse], tags=["Farmers"])
def list_farmers(
    tenant_id: str = Query(...),
    status: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List farmers | قائمة المزارعين"""
    results = list(farmers.values())

    # Filter by status
    if status:
        results = [f for f in results if f.status.value == status]

    # Search by name or phone
    if search:
        search_lower = search.lower()
        results = [
            f for f in results
            if search_lower in f.name.lower()
            or (f.name_ar and search_lower in f.name_ar)
            or search in f.phone
        ]

    # Paginate
    results = results[offset:offset + limit]

    return [
        FarmerResponse(
            id=f.id,
            name=f.name,
            name_ar=f.name_ar,
            phone=f.phone,
            email=f.email,
            national_id=f.national_id,
            farm_location=f.farm_location,
            farm_location_ar=f.farm_location_ar,
            farm_size_hectares=f.farm_size_hectares,
            primary_crops=f.primary_crops,
            status=f.status.value,
            tags=f.tags,
            created_at=f.created_at,
            updated_at=f.updated_at,
            last_interaction_at=f.last_interaction_at,
        )
        for f in results
    ]


@app.get("/api/v1/farmers/{farmer_id}", response_model=FarmerResponse, tags=["Farmers"])
def get_farmer(farmer_id: str):
    """Get farmer by ID | الحصول على مزارع بالمعرف"""
    if farmer_id not in farmers:
        raise HTTPException(status_code=404, detail="Farmer not found")

    f = farmers[farmer_id]
    return FarmerResponse(
        id=f.id,
        name=f.name,
        name_ar=f.name_ar,
        phone=f.phone,
        email=f.email,
        national_id=f.national_id,
        farm_location=f.farm_location,
        farm_location_ar=f.farm_location_ar,
        farm_size_hectares=f.farm_size_hectares,
        primary_crops=f.primary_crops,
        status=f.status.value,
        tags=f.tags,
        created_at=f.created_at,
        updated_at=f.updated_at,
        last_interaction_at=f.last_interaction_at,
    )


@app.patch("/api/v1/farmers/{farmer_id}", response_model=FarmerResponse, tags=["Farmers"])
def update_farmer(farmer_id: str, request: FarmerUpdateRequest):
    """Update farmer | تحديث مزارع"""
    if farmer_id not in farmers:
        raise HTTPException(status_code=404, detail="Farmer not found")

    f = farmers[farmer_id]

    if request.name is not None:
        f.name = request.name
    if request.name_ar is not None:
        f.name_ar = request.name_ar
    if request.phone is not None:
        f.phone = request.phone
    if request.email is not None:
        f.email = request.email
    if request.farm_location is not None:
        f.farm_location = request.farm_location
    if request.farm_location_ar is not None:
        f.farm_location_ar = request.farm_location_ar
    if request.farm_size_hectares is not None:
        f.farm_size_hectares = request.farm_size_hectares
    if request.primary_crops is not None:
        f.primary_crops = request.primary_crops
    if request.status is not None:
        f.status = FarmerStatus(request.status)
    if request.tags is not None:
        f.tags = request.tags

    f.updated_at = datetime.utcnow()

    return FarmerResponse(
        id=f.id,
        name=f.name,
        name_ar=f.name_ar,
        phone=f.phone,
        email=f.email,
        national_id=f.national_id,
        farm_location=f.farm_location,
        farm_location_ar=f.farm_location_ar,
        farm_size_hectares=f.farm_size_hectares,
        primary_crops=f.primary_crops,
        status=f.status.value,
        tags=f.tags,
        created_at=f.created_at,
        updated_at=f.updated_at,
        last_interaction_at=f.last_interaction_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Harvest Deal Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/deals", response_model=HarvestDealResponse, tags=["Deals"])
async def create_deal(request: HarvestDealCreateRequest):
    """Create a harvest deal | إنشاء صفقة حصاد"""
    if request.farmer_id not in farmers:
        raise HTTPException(status_code=404, detail="Farmer not found")

    deal_id = str(uuid4())
    now = datetime.utcnow()

    deal = HarvestDeal(
        id=deal_id,
        farmer_id=request.farmer_id,
        crop_type=request.crop_type,
        crop_type_ar=request.crop_type_ar,
        expected_quantity_tons=request.expected_quantity_tons,
        expected_harvest_date=request.expected_harvest_date,
        price_per_ton=request.price_per_ton,
        stage=DealStage.PROSPECTING,
        notes=request.notes,
        notes_ar=request.notes_ar,
        created_at=now,
        updated_at=now,
    )

    deals[deal_id] = deal

    return HarvestDealResponse(
        id=deal.id,
        farmer_id=deal.farmer_id,
        crop_type=deal.crop_type,
        crop_type_ar=deal.crop_type_ar,
        expected_quantity_tons=deal.expected_quantity_tons,
        actual_quantity_tons=deal.actual_quantity_tons,
        expected_harvest_date=deal.expected_harvest_date,
        actual_harvest_date=deal.actual_harvest_date,
        price_per_ton=deal.price_per_ton,
        total_value=deal.total_value,
        stage=deal.stage.value,
        notes=deal.notes,
        notes_ar=deal.notes_ar,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
    )


@app.get("/api/v1/deals", response_model=list[HarvestDealResponse], tags=["Deals"])
def list_deals(
    tenant_id: str = Query(...),
    farmer_id: str | None = Query(None),
    stage: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List harvest deals | قائمة صفقات الحصاد"""
    results = list(deals.values())

    if farmer_id:
        results = [d for d in results if d.farmer_id == farmer_id]
    if stage:
        results = [d for d in results if d.stage.value == stage]

    return [
        HarvestDealResponse(
            id=d.id,
            farmer_id=d.farmer_id,
            crop_type=d.crop_type,
            crop_type_ar=d.crop_type_ar,
            expected_quantity_tons=d.expected_quantity_tons,
            actual_quantity_tons=d.actual_quantity_tons,
            expected_harvest_date=d.expected_harvest_date,
            actual_harvest_date=d.actual_harvest_date,
            price_per_ton=d.price_per_ton,
            total_value=d.total_value,
            stage=d.stage.value,
            notes=d.notes,
            notes_ar=d.notes_ar,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in results[:limit]
    ]


@app.patch("/api/v1/deals/{deal_id}/stage", response_model=HarvestDealResponse, tags=["Deals"])
def update_deal_stage(deal_id: str, stage: str = Query(...)):
    """Update deal stage | تحديث مرحلة الصفقة"""
    if deal_id not in deals:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal = deals[deal_id]
    deal.stage = DealStage(stage)
    deal.updated_at = datetime.utcnow()

    return HarvestDealResponse(
        id=deal.id,
        farmer_id=deal.farmer_id,
        crop_type=deal.crop_type,
        crop_type_ar=deal.crop_type_ar,
        expected_quantity_tons=deal.expected_quantity_tons,
        actual_quantity_tons=deal.actual_quantity_tons,
        expected_harvest_date=deal.expected_harvest_date,
        actual_harvest_date=deal.actual_harvest_date,
        price_per_ton=deal.price_per_ton,
        total_value=deal.total_value,
        stage=deal.stage.value,
        notes=deal.notes,
        notes_ar=deal.notes_ar,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
    )


@app.get("/api/v1/deals/pipeline", response_model=PipelineStatsResponse, tags=["Deals"])
def get_pipeline_stats(tenant_id: str = Query(...)):
    """Get pipeline statistics | إحصائيات خط الأنابيب"""
    all_deals = list(deals.values())

    by_stage: dict[str, dict[str, Any]] = {}
    for stage in DealStage:
        stage_deals = [d for d in all_deals if d.stage == stage]
        total_value = sum(
            (d.price_per_ton or 0) * d.expected_quantity_tons
            for d in stage_deals
        )
        by_stage[stage.value] = {
            "count": len(stage_deals),
            "total_value": total_value,
            "name_ar": {
                "prospecting": "استكشاف",
                "qualified": "مؤهل",
                "proposal": "عرض",
                "negotiation": "تفاوض",
                "won": "فاز",
                "lost": "خسر",
            }.get(stage.value, stage.value),
        }

    total_deals = len(all_deals)
    won_deals = len([d for d in all_deals if d.stage == DealStage.WON])
    total_value = sum(
        (d.price_per_ton or 0) * d.expected_quantity_tons
        for d in all_deals
    )

    return PipelineStatsResponse(
        total_deals=total_deals,
        total_value=total_value,
        by_stage=by_stage,
        conversion_rate=(won_deals / total_deals * 100) if total_deals > 0 else 0,
        average_deal_size=(total_value / total_deals) if total_deals > 0 else 0,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Interaction Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/interactions", response_model=InteractionResponse, tags=["Interactions"])
async def log_interaction(request: InteractionCreateRequest):
    """Log an interaction with a farmer | تسجيل تفاعل مع مزارع"""
    if request.farmer_id not in farmers:
        raise HTTPException(status_code=404, detail="Farmer not found")

    interaction_id = str(uuid4())
    now = datetime.utcnow()

    interaction = Interaction(
        id=interaction_id,
        farmer_id=request.farmer_id,
        interaction_type=InteractionType(request.interaction_type),
        subject=request.subject,
        subject_ar=request.subject_ar,
        notes=request.notes,
        notes_ar=request.notes_ar,
        outcome=request.outcome,
        follow_up_date=request.follow_up_date,
        created_at=now,
    )

    interactions[interaction_id] = interaction

    # Update farmer's last interaction
    farmers[request.farmer_id].last_interaction_at = now

    return InteractionResponse(
        id=interaction.id,
        farmer_id=interaction.farmer_id,
        interaction_type=interaction.interaction_type.value,
        subject=interaction.subject,
        subject_ar=interaction.subject_ar,
        notes=interaction.notes,
        notes_ar=interaction.notes_ar,
        outcome=interaction.outcome,
        follow_up_date=interaction.follow_up_date,
        created_at=interaction.created_at,
        created_by=interaction.created_by,
    )


@app.get("/api/v1/interactions", response_model=list[InteractionResponse], tags=["Interactions"])
def list_interactions(
    farmer_id: str = Query(...),
    interaction_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List interactions for a farmer | قائمة التفاعلات لمزارع"""
    results = [i for i in interactions.values() if i.farmer_id == farmer_id]

    if interaction_type:
        results = [i for i in results if i.interaction_type.value == interaction_type]

    # Sort by created_at descending
    results.sort(key=lambda x: x.created_at, reverse=True)

    return [
        InteractionResponse(
            id=i.id,
            farmer_id=i.farmer_id,
            interaction_type=i.interaction_type.value,
            subject=i.subject,
            subject_ar=i.subject_ar,
            notes=i.notes,
            notes_ar=i.notes_ar,
            outcome=i.outcome,
            follow_up_date=i.follow_up_date,
            created_at=i.created_at,
            created_by=i.created_by,
        )
        for i in results[:limit]
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Natural Language Query Endpoint (SQLBot-inspired)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/query", response_model=QueryResponse, tags=["Query"])
async def natural_language_query(request: QueryRequest):
    """
    Execute a natural language query (SQLBot-inspired)

    تنفيذ استعلام بلغة طبيعية

    Examples:
    - "Show me all active farmers"
    - "أرني جميع المزارعين النشطين"
    - "Farmers with farm size > 10 hectares"
    - "Deals in negotiation stage"
    """
    import time
    start_time = time.time()

    query_lower = request.query.lower()
    results: list[dict[str, Any]] = []
    interpreted_as = ""
    interpreted_as_ar = ""

    # Parse query and execute
    if "active" in query_lower or "نشط" in request.query:
        interpreted_as = "SELECT * FROM farmers WHERE status = 'active'"
        interpreted_as_ar = "اختر جميع المزارعين حيث الحالة = نشط"
        results = [
            {
                "id": f.id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
                "farm_size_hectares": f.farm_size_hectares,
            }
            for f in farmers.values()
            if f.status == FarmerStatus.ACTIVE
        ]

    elif "lead" in query_lower or "محتمل" in request.query:
        interpreted_as = "SELECT * FROM farmers WHERE status = 'lead'"
        interpreted_as_ar = "اختر جميع المزارعين حيث الحالة = محتمل"
        results = [
            {
                "id": f.id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
            }
            for f in farmers.values()
            if f.status == FarmerStatus.LEAD
        ]

    elif "deal" in query_lower or "صفقة" in request.query:
        if "negotiation" in query_lower or "تفاوض" in request.query:
            interpreted_as = "SELECT * FROM deals WHERE stage = 'negotiation'"
            interpreted_as_ar = "اختر جميع الصفقات حيث المرحلة = تفاوض"
            results = [
                {
                    "id": d.id,
                    "crop_type": d.crop_type,
                    "expected_quantity_tons": d.expected_quantity_tons,
                    "stage": d.stage.value,
                }
                for d in deals.values()
                if d.stage == DealStage.NEGOTIATION
            ]
        else:
            interpreted_as = "SELECT * FROM deals"
            interpreted_as_ar = "اختر جميع الصفقات"
            results = [
                {
                    "id": d.id,
                    "crop_type": d.crop_type,
                    "expected_quantity_tons": d.expected_quantity_tons,
                    "stage": d.stage.value,
                }
                for d in deals.values()
            ]

    elif "farmer" in query_lower or "مزارع" in request.query:
        interpreted_as = "SELECT * FROM farmers"
        interpreted_as_ar = "اختر جميع المزارعين"
        results = [
            {
                "id": f.id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
                "farm_size_hectares": f.farm_size_hectares,
            }
            for f in farmers.values()
        ]

    else:
        interpreted_as = "Unknown query pattern"
        interpreted_as_ar = "نمط استعلام غير معروف"

    execution_time = int((time.time() - start_time) * 1000)

    return QueryResponse(
        query=request.query,
        interpreted_as=interpreted_as,
        interpreted_as_ar=interpreted_as_ar,
        results=results,
        result_count=len(results),
        execution_time_ms=execution_time,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics"""
    return f"""# HELP crm_farmers_total Total number of farmers
# TYPE crm_farmers_total gauge
crm_farmers_total {len(farmers)}

# HELP crm_deals_total Total number of deals
# TYPE crm_deals_total gauge
crm_deals_total {len(deals)}

# HELP crm_interactions_total Total number of interactions
# TYPE crm_interactions_total counter
crm_interactions_total {len(interactions)}
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
