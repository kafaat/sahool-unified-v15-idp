"""
SAHOOL Low-Code Engine Service
===============================
Low-code application development platform for agricultural apps.

Inspired by: Alibaba LowCode Engine, NocoBase
Features:
- Material Protocol for components
- Data Model System
- Page & Block System
- Plugin Architecture
- AI-powered component suggestions

Port: 8132
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Any
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from shared.lowcode import (
    LowCodeEngine,
    ComponentCategory,
    DataModel,
    FieldDefinition,
    FieldType,
    PageDefinition,
    BlockConfig,
    AIComponentSuggester,
)

# Service configuration
SERVICE_NAME = "lowcode-engine"
SERVICE_NAME_AR = "محرك التطوير منخفض الكود"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8132


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════

class ComponentResponse(BaseModel):
    """Component material response"""
    component_id: str
    name: str
    name_ar: str | None
    category: str
    description: str | None
    description_ar: str | None
    props: list[dict[str, Any]]
    slots: list[dict[str, Any]]
    events: list[dict[str, Any]]
    is_container: bool
    icon: str | None = None


class DataModelCreateRequest(BaseModel):
    """Request to create a data model"""
    name: str = Field(..., min_length=1, max_length=100)
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    fields: list[dict[str, Any]]
    tenant_id: str


class DataModelResponse(BaseModel):
    """Data model response"""
    id: str
    name: str
    name_ar: str | None
    description: str | None
    description_ar: str | None
    fields: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class PageCreateRequest(BaseModel):
    """Request to create a page"""
    name: str = Field(..., min_length=1, max_length=100)
    name_ar: str | None = None
    description: str | None = None
    route: str = Field(..., pattern=r"^/[a-z0-9\-/]*$")
    blocks: list[dict[str, Any]] = []
    data_model_id: str | None = None
    tenant_id: str


class PageResponse(BaseModel):
    """Page response"""
    id: str
    name: str
    name_ar: str | None
    description: str | None
    route: str
    blocks: list[dict[str, Any]]
    data_model_id: str | None
    is_published: bool
    version: int
    created_at: datetime
    updated_at: datetime


class PageRenderResponse(BaseModel):
    """Rendered page response"""
    page_id: str
    name: str
    route: str
    rendered_blocks: list[dict[str, Any]]
    data: dict[str, Any] | None


class AISuggestionRequest(BaseModel):
    """Request for AI component suggestions"""
    description: str = Field(..., min_length=10, description="Page description in natural language")
    description_ar: str | None = None
    context: dict[str, Any] | None = None


class AISuggestionResponse(BaseModel):
    """AI suggestion response"""
    suggestions: list[dict[str, Any]]
    reasoning: str
    reasoning_ar: str | None
    confidence: float


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory storage (replace with database in production)
# ═══════════════════════════════════════════════════════════════════════════════

data_models: dict[str, DataModel] = {}
pages: dict[str, PageDefinition] = {}

# Initialize Low-Code Engine (includes built-in components)
lowcode_engine = LowCodeEngine(tenant_id="sahool")
ai_suggester = AIComponentSuggester(lowcode_engine)


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
    print(f"📦 Registered {len(lowcode_engine.list_components())} components")

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
    title="SAHOOL Low-Code Engine",
    description="Low-code application development platform | منصة تطوير التطبيقات منخفضة الكود",
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
        "components_loaded": len(lowcode_engine.list_components()) > 0,
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
        "components_count": len(lowcode_engine.list_components()),
        "data_models_count": len(data_models),
        "pages_count": len(pages),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Component Material Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/components", response_model=list[ComponentResponse], tags=["Components"])
def list_components(
    category: str | None = Query(None, description="Filter by category"),
):
    """List available components | قائمة المكونات المتاحة"""
    components = lowcode_engine.list_components()

    if category:
        components = [c for c in components if c.category.value == category]

    return [
        ComponentResponse(
            component_id=c.component_id,
            name=c.name,
            name_ar=c.name_ar,
            category=c.category.value,
            description=c.description,
            description_ar=c.description_ar,
            props=[{"name": p.name, "type": p.type, "default": p.default} for p in c.props],
            slots=[{"name": s.name, "title": s.title} for s in c.slots],
            events=[{"name": e.name, "description": e.description} for e in c.events],
            is_container=c.is_container,
            icon=c.icon,
        )
        for c in components
    ]


@app.get("/api/v1/components/{component_name}", response_model=ComponentResponse, tags=["Components"])
def get_component(component_name: str):
    """Get component by name | الحصول على مكون بالاسم"""
    component = lowcode_engine.get_component(component_name)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    return ComponentResponse(
        component_id=component.component_id,
        name=component.name,
        name_ar=component.name_ar,
        category=component.category.value,
        description=component.description,
        description_ar=component.description_ar,
        props=[{"name": p.name, "type": p.type, "default": p.default} for p in component.props],
        slots=[{"name": s.name, "title": s.title} for s in component.slots],
        events=[{"name": e.name, "description": e.description} for e in component.events],
        is_container=component.is_container,
        icon=component.icon,
    )


@app.get("/api/v1/components/categories", tags=["Components"])
def list_categories():
    """List component categories | قائمة فئات المكونات"""
    return [
        {
            "value": cat.value,
            "name": cat.value.replace("_", " ").title(),
            "name_ar": {
                "form": "نموذج",
                "display": "عرض",
                "layout": "تخطيط",
                "chart": "رسم بياني",
                "agricultural": "زراعي",
                "navigation": "تنقل",
                "data": "بيانات",
            }.get(cat.value, cat.value),
        }
        for cat in ComponentCategory
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Data Model Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/models", response_model=DataModelResponse, tags=["Data Models"])
async def create_data_model(request: DataModelCreateRequest):
    """Create a data model | إنشاء نموذج بيانات"""
    model_id = str(uuid4())
    now = datetime.utcnow()

    # Parse fields
    fields = []
    for field_data in request.fields:
        field = FieldDefinition(
            name=field_data["name"],
            name_ar=field_data.get("name_ar"),
            field_type=FieldType(field_data.get("field_type", "text")),
            required=field_data.get("required", False),
            default_value=field_data.get("default_value"),
            options=field_data.get("options"),
            validation=field_data.get("validation"),
        )
        fields.append(field)

    model = DataModel(
        id=model_id,
        name=request.name,
        name_ar=request.name_ar,
        description=request.description,
        description_ar=request.description_ar,
        fields=fields,
        created_at=now,
        updated_at=now,
    )

    data_models[model_id] = model

    return DataModelResponse(
        id=model.id,
        name=model.name,
        name_ar=model.name_ar,
        description=model.description,
        description_ar=model.description_ar,
        fields=[f.model_dump() for f in model.fields],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@app.get("/api/v1/models", response_model=list[DataModelResponse], tags=["Data Models"])
def list_data_models(
    tenant_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
):
    """List data models | قائمة نماذج البيانات"""
    results = list(data_models.values())[:limit]

    return [
        DataModelResponse(
            id=m.id,
            name=m.name,
            name_ar=m.name_ar,
            description=m.description,
            description_ar=m.description_ar,
            fields=[f.model_dump() for f in m.fields],
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in results
    ]


@app.get("/api/v1/models/{model_id}", response_model=DataModelResponse, tags=["Data Models"])
def get_data_model(model_id: str):
    """Get data model by ID | الحصول على نموذج بيانات بالمعرف"""
    if model_id not in data_models:
        raise HTTPException(status_code=404, detail="Data model not found")

    m = data_models[model_id]
    return DataModelResponse(
        id=m.id,
        name=m.name,
        name_ar=m.name_ar,
        description=m.description,
        description_ar=m.description_ar,
        fields=[f.model_dump() for f in m.fields],
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Page Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/pages", response_model=PageResponse, tags=["Pages"])
async def create_page(request: PageCreateRequest):
    """Create a page | إنشاء صفحة"""
    page_id = str(uuid4())
    now = datetime.utcnow()

    # Parse blocks
    blocks = []
    for block_data in request.blocks:
        block = BlockConfig(
            id=block_data.get("id", str(uuid4())),
            component_name=block_data["component_name"],
            props=block_data.get("props", {}),
            children=block_data.get("children", []),
            conditions=block_data.get("conditions"),
            loop=block_data.get("loop"),
        )
        blocks.append(block)

    page = PageDefinition(
        id=page_id,
        name=request.name,
        name_ar=request.name_ar,
        description=request.description,
        route=request.route,
        blocks=blocks,
        data_model_id=request.data_model_id,
        is_published=False,
        version=1,
        created_at=now,
        updated_at=now,
    )

    pages[page_id] = page

    return PageResponse(
        id=page.id,
        name=page.name,
        name_ar=page.name_ar,
        description=page.description,
        route=page.route,
        blocks=[b.model_dump() for b in page.blocks],
        data_model_id=page.data_model_id,
        is_published=page.is_published,
        version=page.version,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@app.get("/api/v1/pages", response_model=list[PageResponse], tags=["Pages"])
def list_pages(
    tenant_id: str = Query(...),
    is_published: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List pages | قائمة الصفحات"""
    results = list(pages.values())

    if is_published is not None:
        results = [p for p in results if p.is_published == is_published]

    return [
        PageResponse(
            id=p.id,
            name=p.name,
            name_ar=p.name_ar,
            description=p.description,
            route=p.route,
            blocks=[b.model_dump() for b in p.blocks],
            data_model_id=p.data_model_id,
            is_published=p.is_published,
            version=p.version,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in results[:limit]
    ]


@app.get("/api/v1/pages/{page_id}", response_model=PageResponse, tags=["Pages"])
def get_page(page_id: str):
    """Get page by ID | الحصول على صفحة بالمعرف"""
    if page_id not in pages:
        raise HTTPException(status_code=404, detail="Page not found")

    p = pages[page_id]
    return PageResponse(
        id=p.id,
        name=p.name,
        name_ar=p.name_ar,
        description=p.description,
        route=p.route,
        blocks=[b.model_dump() for b in p.blocks],
        data_model_id=p.data_model_id,
        is_published=p.is_published,
        version=p.version,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@app.post("/api/v1/pages/{page_id}/publish", response_model=PageResponse, tags=["Pages"])
def publish_page(page_id: str):
    """Publish a page | نشر صفحة"""
    if page_id not in pages:
        raise HTTPException(status_code=404, detail="Page not found")

    p = pages[page_id]
    p.is_published = True
    p.updated_at = datetime.utcnow()

    return PageResponse(
        id=p.id,
        name=p.name,
        name_ar=p.name_ar,
        description=p.description,
        route=p.route,
        blocks=[b.model_dump() for b in p.blocks],
        data_model_id=p.data_model_id,
        is_published=p.is_published,
        version=p.version,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@app.get("/api/v1/pages/{page_id}/render", response_model=PageRenderResponse, tags=["Pages"])
def render_page(page_id: str, data: str | None = Query(None)):
    """
    Render a page with data

    عرض صفحة مع البيانات
    """
    if page_id not in pages:
        raise HTTPException(status_code=404, detail="Page not found")

    p = pages[page_id]

    # Render blocks (simplified)
    rendered_blocks = []
    for block in p.blocks:
        component = lowcode_engine.get_component(block.component_name)
        rendered_blocks.append({
            "id": block.id,
            "component_name": block.component_name,
            "component_title": component.title if component else block.component_name,
            "component_title_ar": component.title_ar if component else None,
            "props": block.props,
            "children": block.children,
        })

    return PageRenderResponse(
        page_id=p.id,
        name=p.name,
        route=p.route,
        rendered_blocks=rendered_blocks,
        data=None,  # Would load from data model
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AI Suggestion Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/suggest", response_model=AISuggestionResponse, tags=["AI"])
async def suggest_components(request: AISuggestionRequest):
    """
    AI-powered component suggestions based on page description

    اقتراحات مكونات مدعومة بالذكاء الاصطناعي بناءً على وصف الصفحة
    """
    # Simple keyword-based suggestion
    suggestions = []
    desc_lower = request.description.lower()

    # Map keywords to components
    keyword_components = {
        ("map", "field", "location", "حقل", "موقع"): "field_map",
        ("crop", "plant", "محصول", "نبات"): "crop_selector",
        ("irrigation", "water", "ري", "ماء"): "irrigation_scheduler",
        ("sensor", "reading", "مستشعر", "قراءة"): "sensor_display",
        ("health", "ndvi", "صحة"): "crop_health_card",
        ("advisor", "recommendation", "مستشار", "توصية"): "ai_advisor",
    }

    for keywords, component_id in keyword_components.items():
        if any(kw in desc_lower or kw in request.description for kw in keywords):
            component = lowcode_engine.get_component(component_id)
            if component:
                suggestions.append({
                    "component_id": component_id,
                    "component_name": component.name,
                    "component_name_ar": component.name_ar,
                    "confidence": 0.85,
                    "reason": f"Matches keywords in description",
                })

    return AISuggestionResponse(
        suggestions=suggestions,
        reasoning=f"Based on your description, I recommend these components for building a {request.description[:50]}...",
        reasoning_ar=f"بناءً على وصفك، أوصي بهذه المكونات لبناء {request.description_ar or request.description[:50]}...",
        confidence=0.85 if suggestions else 0.5,
    )


@app.get("/api/v1/ai/templates", tags=["AI"])
def list_templates():
    """List available page templates | قائمة قوالب الصفحات المتاحة"""
    return [
        {
            "id": "field-dashboard",
            "name": "Field Dashboard",
            "name_ar": "لوحة تحكم الحقل",
            "description": "Dashboard showing field health, weather, and irrigation status",
            "description_ar": "لوحة تحكم تعرض صحة الحقل والطقس وحالة الري",
            "components": ["field_map", "sensor_display", "crop_health_card", "ai_advisor"],
        },
        {
            "id": "farm-overview",
            "name": "Farm Overview",
            "name_ar": "نظرة عامة على المزرعة",
            "description": "Overview of all fields in a farm with key metrics",
            "description_ar": "نظرة عامة على جميع الحقول في المزرعة مع المقاييس الرئيسية",
            "components": ["field_map", "crop_selector", "sensor_display"],
        },
        {
            "id": "irrigation-planner",
            "name": "Irrigation Planner",
            "name_ar": "مخطط الري",
            "description": "Plan and schedule irrigation for fields",
            "description_ar": "تخطيط وجدولة الري للحقول",
            "components": ["irrigation_scheduler", "sensor_display", "ai_advisor"],
        },
    ]


@app.post("/api/v1/ai/generate-page", response_model=PageResponse, tags=["AI"])
async def generate_page_from_template(
    template_id: str = Query(...),
    name: str = Query(...),
    name_ar: str | None = Query(None),
    tenant_id: str = Query(...),
):
    """
    Generate a page from a template

    إنشاء صفحة من قالب
    """
    templates = {
        "field-dashboard": {
            "components": ["field_map", "sensor_display", "crop_health_card", "ai_advisor"],
            "route": "/dashboard/field",
        },
        "farm-overview": {
            "components": ["field_map", "crop_selector", "sensor_display"],
            "route": "/dashboard/farm",
        },
        "irrigation-planner": {
            "components": ["irrigation_scheduler", "sensor_display", "ai_advisor"],
            "route": "/irrigation/plan",
        },
    }

    if template_id not in templates:
        raise HTTPException(status_code=404, detail="Template not found")

    template = templates[template_id]
    page_id = str(uuid4())
    now = datetime.utcnow()

    # Generate blocks from template
    blocks = []
    for comp_name in template["components"]:
        block = BlockConfig(
            id=str(uuid4()),
            component_name=comp_name,
            props={},
            children=[],
        )
        blocks.append(block)

    page = PageDefinition(
        id=page_id,
        name=name,
        name_ar=name_ar,
        description=f"Generated from template: {template_id}",
        route=f"{template['route']}/{page_id[:8]}",
        blocks=blocks,
        is_published=False,
        version=1,
        created_at=now,
        updated_at=now,
    )

    pages[page_id] = page

    return PageResponse(
        id=page.id,
        name=page.name,
        name_ar=page.name_ar,
        description=page.description,
        route=page.route,
        blocks=[b.model_dump() for b in page.blocks],
        data_model_id=page.data_model_id,
        is_published=page.is_published,
        version=page.version,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics"""
    return f"""# HELP lowcode_components_total Total number of registered components
# TYPE lowcode_components_total gauge
lowcode_components_total {len(lowcode_engine.list_components())}

# HELP lowcode_data_models_total Total number of data models
# TYPE lowcode_data_models_total gauge
lowcode_data_models_total {len(data_models)}

# HELP lowcode_pages_total Total number of pages
# TYPE lowcode_pages_total gauge
lowcode_pages_total {len(pages)}

# HELP lowcode_pages_published Published pages
# TYPE lowcode_pages_published gauge
lowcode_pages_published {len([p for p in pages.values() if p.is_published])}
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
