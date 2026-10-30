# Low-Code Engine Service Analysis

**Service**: `lowcode-engine`
**Port**: 8132
**Framework**: FastAPI (Python 3.11+)
**Version**: 16.0.0

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [NATS Events](#nats-events)
6. [Low-Code Features](#low-code-features)
7. [Component Library](#component-library)
8. [Database Schema](#database-schema)
9. [Dependencies](#dependencies)
10. [Environment Variables](#environment-variables)
11. [Bugs and Recommended Fixes](#bugs-and-recommended-fixes)

---

## Service Overview

The **Low-Code Engine** is a visual application builder platform for creating agricultural applications without extensive coding. It provides:

- **Component Material Library**: Pre-built UI components following Alibaba's Material Protocol
- **Data Model Designer**: Define data structures with field validation and relationships
- **Page Builder**: Visual drag-and-drop page composition with blocks
- **AI Suggestions**: Keyword-based component recommendations
- **Plugin Architecture**: Extensible through custom plugins

### Service Names
| Language | Name |
|----------|------|
| English | Low-Code Engine |
| Arabic | محرك التطوير منخفض الكود |

### Kong Gateway Routes
| Route | Strip Path |
|-------|------------|
| `/api/v1/lowcode` | Yes |
| `/lowcode` | Yes |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Low-Code Engine Service                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Component   │  │  Data Model  │  │    Page      │          │
│  │   Material   │  │    System    │  │   Builder    │          │
│  │   Library    │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │              AI Component Suggester               │          │
│  └──────────────────────────────────────────────────┘          │
│                            │                                    │
├────────────────────────────┼────────────────────────────────────┤
│        API Layer (FastAPI + Rate Limiting + CORS)              │
├────────────────────────────┼────────────────────────────────────┤
│  PostgreSQL (asyncpg)  │  Redis (cache)  │  NATS (events)      │
└─────────────────────────────────────────────────────────────────┘
```

### Core Modules
| Module | Location | Purpose |
|--------|----------|---------|
| `shared.lowcode.engine` | `/shared/lowcode/engine.py` | Core engine, component registry, page builder |
| `shared.lowcode` | `/shared/lowcode/__init__.py` | Module exports |
| `main.py` | `/apps/services/lowcode-engine/src/main.py` | FastAPI application |

---

## API Endpoints

### Health Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe (DB, Redis, NATS status) | No |
| `GET` | `/health` | Detailed health status with counts | No |
| `GET` | `/metrics` | Prometheus-compatible metrics | No |

### Component Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `GET` | `/api/v1/components` | List all components | 60/min |
| `GET` | `/api/v1/components/categories` | List component categories | 60/min |
| `GET` | `/api/v1/components/{component_name}` | Get component by name | 60/min |

**Query Parameters for `/api/v1/components`:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Filter by category (form, agriculture, map, etc.) |

### Data Model Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/models` | Create a data model | 30/min |
| `GET` | `/api/v1/models` | List data models | 60/min |
| `GET` | `/api/v1/models/{model_id}` | Get data model by ID | 60/min |

**Query Parameters for `/api/v1/models` (GET):**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant identifier |
| `limit` | integer | No | Max results (default: 50, max: 200) |

### Page Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/pages` | Create a page | 30/min |
| `GET` | `/api/v1/pages` | List pages | 60/min |
| `GET` | `/api/v1/pages/{page_id}` | Get page by ID | 60/min |
| `POST` | `/api/v1/pages/{page_id}/publish` | Publish a page | 30/min |
| `GET` | `/api/v1/pages/{page_id}/render` | Render page with data | 60/min |

**Query Parameters for `/api/v1/pages` (GET):**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant identifier |
| `is_published` | boolean | No | Filter by published status |
| `limit` | integer | No | Max results (default: 50, max: 200) |

### AI Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/ai/suggest` | AI component suggestions | 10/min |
| `GET` | `/api/v1/ai/templates` | List page templates | 60/min |
| `POST` | `/api/v1/ai/generate-page` | Generate page from template | 30/min |

**Query Parameters for `/api/v1/ai/generate-page`:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_id` | string | Yes | Template identifier |
| `name` | string | Yes | Page name |
| `name_ar` | string | No | Page name (Arabic) |
| `tenant_id` | string | Yes | Tenant identifier |

---

## Request/Response Schemas

### ErrorResponse

```json
{
  "error": "string",
  "error_ar": "string | null",
  "error_code": "string",
  "detail": "string | null",
  "request_id": "string | null"
}
```

### ComponentResponse

```json
{
  "component_id": "string",
  "name": "string",
  "name_ar": "string | null",
  "category": "string",
  "description": "string | null",
  "description_ar": "string | null",
  "props": [
    {
      "name": "string",
      "type": "string",
      "default": "any"
    }
  ],
  "slots": [
    {
      "name": "string",
      "title": "string"
    }
  ],
  "events": [
    {
      "name": "string",
      "description": "string"
    }
  ],
  "is_container": "boolean",
  "icon": "string | null"
}
```

### DataModelCreateRequest

```json
{
  "name": "string (1-100 chars)",
  "name_ar": "string | null",
  "description": "string | null",
  "description_ar": "string | null",
  "fields": [
    {
      "name": "string",
      "name_ar": "string | null",
      "field_type": "string | number | boolean | date | datetime | enum | array | object | geojson | image | file | relation",
      "required": "boolean (default: false)",
      "default_value": "any | null",
      "options": "array<string> | null",
      "validation": "object | null"
    }
  ],
  "tenant_id": "string"
}
```

### DataModelResponse

```json
{
  "id": "string (UUID)",
  "name": "string",
  "name_ar": "string | null",
  "description": "string | null",
  "description_ar": "string | null",
  "fields": "array<FieldDefinition>",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### PageCreateRequest

```json
{
  "name": "string (1-100 chars)",
  "name_ar": "string | null",
  "description": "string | null",
  "route": "string (pattern: ^/[a-z0-9\\-/]*$)",
  "blocks": [
    {
      "id": "string | null",
      "component_name": "string",
      "props": "object",
      "children": "array<BlockConfig>",
      "conditions": "object | null",
      "loop": "object | null"
    }
  ],
  "data_model_id": "string | null",
  "tenant_id": "string"
}
```

### PageResponse

```json
{
  "id": "string (UUID)",
  "name": "string",
  "name_ar": "string | null",
  "description": "string | null",
  "route": "string",
  "blocks": "array<BlockConfig>",
  "data_model_id": "string | null",
  "is_published": "boolean",
  "version": "integer",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### PageRenderResponse

```json
{
  "page_id": "string",
  "name": "string",
  "route": "string",
  "rendered_blocks": [
    {
      "id": "string",
      "component_name": "string",
      "component_title": "string",
      "component_title_ar": "string | null",
      "props": "object",
      "children": "array"
    }
  ],
  "data": "object | null"
}
```

### AISuggestionRequest

```json
{
  "description": "string (min 10 chars)",
  "description_ar": "string | null",
  "context": "object | null"
}
```

### AISuggestionResponse

```json
{
  "suggestions": [
    {
      "component_id": "string",
      "component_name": "string",
      "component_name_ar": "string | null",
      "confidence": "float (0-1)",
      "reason": "string"
    }
  ],
  "reasoning": "string",
  "reasoning_ar": "string | null",
  "confidence": "float (0-1)"
}
```

---

## NATS Events

### Subject Pattern

```
sahool.{tenant_id}.lowcode.{resource}.{action}
```

### Published Events

| Subject | Trigger | Payload |
|---------|---------|---------|
| `sahool.{tenant_id}.lowcode.model.created` | Data model created | `{ model_id, tenant_id, name, name_ar, field_count, timestamp }` |
| `sahool.{tenant_id}.lowcode.page.created` | Page created | `{ page_id, tenant_id, name, route, timestamp }` |
| `sahool.{tenant_id}.lowcode.page.published` | Page published | `{ page_id, tenant_id, name, route, timestamp }` |

### Event Payload Example

```json
{
  "model_id": "uuid",
  "tenant_id": "farm-001",
  "name": "Field",
  "name_ar": "حقل",
  "field_count": 4,
  "timestamp": "2026-01-25T10:30:00Z"
}
```

### Subscribed Events

Currently, the service does **not** subscribe to any NATS events.

---

## Low-Code Features

### Material Protocol

The service follows Alibaba's Material Protocol for component interoperability:

| Feature | Description |
|---------|-------------|
| **ComponentMaterial** | Component definition with props, slots, events |
| **PropDefinition** | Property schema with types, defaults, validation |
| **SlotDefinition** | Named slots for nested components |
| **EventDefinition** | Event handlers with payload schemas |

### Data Model System (NocoBase-inspired)

| Feature | Description |
|---------|-------------|
| **FieldDefinition** | Field schema with types and validation |
| **DataModel** | Collection/table structure definition |
| **Field Types** | STRING, NUMBER, BOOLEAN, DATE, DATETIME, ENUM, ARRAY, OBJECT, GEOJSON, IMAGE, FILE, RELATION |
| **Relations** | Foreign key support with relation types |

### Page & Block System

| Feature | Description |
|---------|-------------|
| **PageDefinition** | Page composition with blocks |
| **BlockConfig** | Block configuration with props, styles, children |
| **Layouts** | default, full-width, sidebar, dashboard |
| **Conditional Rendering** | Visibility conditions |
| **Loop Directive** | Render blocks for collections |

### Plugin Architecture

| Feature | Description |
|---------|-------------|
| **PluginBase** | Abstract base class for plugins |
| **Component Registration** | Plugins can register custom components |
| **Model Registration** | Plugins can register data models |
| **Page Registration** | Plugins can register pages |
| **Lifecycle Hooks** | on_install, on_activate, on_deactivate |

### AI Component Suggester

| Feature | Description |
|---------|-------------|
| **Keyword Matching** | Simple keyword-based suggestions |
| **Field-to-Component Mapping** | Suggests components based on field types |
| **Layout Suggestions** | Grid layout recommendations |

---

## Component Library

### Layout Components

| Component ID | Name | Name (AR) | Container | Description |
|--------------|------|-----------|-----------|-------------|
| `container` | Container | حاوية | Yes | Flexible container with padding and direction |
| `grid` | Grid | شبكة | Yes | Grid layout with configurable columns |

### Form Components

| Component ID | Name | Name (AR) | Description |
|--------------|------|-----------|-------------|
| `text_input` | Text Input | حقل نصي | Single-line text input |
| `number_input` | Number Input | حقل رقمي | Numeric input with min/max |
| `select` | Select | قائمة منسدلة | Dropdown selection |
| `date_picker` | Date Picker | منتقي التاريخ | Date selection with Hijri support |

### Data Components

| Component ID | Name | Name (AR) | Description |
|--------------|------|-----------|-------------|
| `data_table` | Data Table | جدول البيانات | Paginated, sortable data table |

### Chart Components

| Component ID | Name | Name (AR) | Description |
|--------------|------|-----------|-------------|
| `line_chart` | Line Chart | رسم بياني خطي | Time-series line visualization |

### Map Components

| Component ID | Name | Name (AR) | Description |
|--------------|------|-----------|-------------|
| `field_map` | Field Map | خريطة الحقل | Interactive map with NDVI, satellite, sensor layers |

### Agricultural Components

| Component ID | Name | Name (AR) | Description |
|--------------|------|-----------|-------------|
| `crop_selector` | Crop Selector | منتقي المحصول | Crop selection with regional recommendations |
| `irrigation_scheduler` | Irrigation Scheduler | جدولة الري | Irrigation planning with auto-scheduling |
| `sensor_display` | Sensor Display | عرض المستشعر | Real-time sensor readings with history |
| `crop_health_card` | Crop Health Card | بطاقة صحة المحصول | NDVI-based crop health visualization |

### AI Components

| Component ID | Name | Name (AR) | Description |
|--------------|------|-----------|-------------|
| `ai_advisor` | AI Advisor | مستشار الذكاء الاصطناعي | Context-aware agricultural advisory |

### Available Page Templates

| Template ID | Name | Name (AR) | Components |
|-------------|------|-----------|------------|
| `field-dashboard` | Field Dashboard | لوحة تحكم الحقل | field_map, sensor_display, crop_health_card, ai_advisor |
| `farm-overview` | Farm Overview | نظرة عامة على المزرعة | field_map, crop_selector, sensor_display |
| `irrigation-planner` | Irrigation Planner | مخطط الري | irrigation_scheduler, sensor_display, ai_advisor |

---

## Database Schema

### Table: `lowcode_data_models`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `tenant_id` | VARCHAR(100) | No | Tenant identifier |
| `name` | VARCHAR(100) | No | Model name (English) |
| `name_ar` | VARCHAR(100) | Yes | Model name (Arabic) |
| `description` | TEXT | Yes | Description (English) |
| `description_ar` | TEXT | Yes | Description (Arabic) |
| `fields` | JSONB | No | Field definitions array |
| `created_at` | TIMESTAMPTZ | No | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |

**Constraints:**
- `uq_lowcode_data_models_tenant_name` - UNIQUE (tenant_id, name)

**Indexes:**
- `idx_lowcode_dm_tenant_id` - tenant_id
- `idx_lowcode_dm_name` - name
- `idx_lowcode_dm_created_at` - created_at DESC
- `idx_lowcode_dm_tenant_created` - (tenant_id, created_at DESC)

### Table: `lowcode_pages`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `tenant_id` | VARCHAR(100) | No | Tenant identifier |
| `name` | VARCHAR(100) | No | Page name (English) |
| `name_ar` | VARCHAR(100) | Yes | Page name (Arabic) |
| `description` | TEXT | Yes | Description (English) |
| `description_ar` | TEXT | Yes | Description (Arabic) |
| `route` | VARCHAR(255) | No | URL route |
| `layout` | VARCHAR(50) | No | Layout type (default: 'default') |
| `blocks` | JSONB | No | Block configurations array |
| `data_model_id` | UUID | Yes | Reference to data model (FK) |
| `is_published` | BOOLEAN | No | Published status (default: false) |
| `version` | INTEGER | No | Page version (default: 1) |
| `created_at` | TIMESTAMPTZ | No | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |

**Constraints:**
- `uq_lowcode_pages_tenant_route` - UNIQUE (tenant_id, route)
- `fk_lowcode_pages_data_model` - FK to lowcode_data_models(id) ON DELETE SET NULL

**Indexes:**
- `idx_lowcode_pages_tenant_id` - tenant_id
- `idx_lowcode_pages_route` - route
- `idx_lowcode_pages_is_published` - is_published
- `idx_lowcode_pages_data_model_id` - data_model_id
- `idx_lowcode_pages_created_at` - created_at DESC
- `idx_lowcode_pages_tenant_published` - (tenant_id, is_published)
- `idx_lowcode_pages_tenant_created` - (tenant_id, created_at DESC)

**Triggers:**
- `trigger_update_lowcode_dm_updated_at` - Auto-update updated_at on lowcode_data_models
- `trigger_update_lowcode_pages_updated_at` - Auto-update updated_at on lowcode_pages

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.126.0,<1.0.0 | Web framework |
| `uvicorn[standard]` | >=0.30.0,<1.0.0 | ASGI server |
| `pydantic` | >=2.10.0,<3.0.0 | Data validation |
| `httpx` | >=0.27.0,<1.0.0 | Async HTTP client |
| `aiofiles` | >=24.0.0,<25.0.0 | Async file I/O |
| `nats-py` | >=2.9.0,<3.0.0 | NATS messaging |
| `asyncpg` | >=0.30.0,<1.0.0 | PostgreSQL driver |
| `structlog` | >=24.0.0,<25.0.0 | Structured logging |
| `pyjwt` | >=2.9.0,<3.0.0 | JWT handling |
| `slowapi` | >=0.1.9,<1.0.0 | Rate limiting |
| `redis` | >=5.0.0,<6.0.0 | Redis client |
| `jsonschema` | >=4.23.0,<5.0.0 | JSON schema validation |

### Shared Module Dependencies

| Module | Location | Purpose |
|--------|----------|---------|
| `shared.auth.dependencies` | `/shared/auth/dependencies.py` | Authentication (get_current_user) |
| `shared.auth.models` | `/shared/auth/models.py` | User model |
| `shared.lowcode` | `/shared/lowcode/` | Core low-code engine |
| `shared.events.publisher` | `/shared/events/publisher.py` | NATS event publisher |

---

## Environment Variables

### Required Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | **Yes** | - | JWT secret for authentication (min 32 chars) |

### Optional Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | - | PostgreSQL connection URL |
| `NATS_URL` | No | - | NATS server URL |
| `REDIS_URL` | No | - | Redis connection URL |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `CORS_ALLOWED_ORIGINS` | No | `http://localhost:3000,http://localhost:8080` | Comma-separated CORS origins |
| `ENVIRONMENT` | No | `development` | Environment name |
| `HOST` | No | `0.0.0.0` | Server bind host |

### Missing Environment Variables

The following environment variables are documented but NOT used in the code:

| Variable | Documented | Used | Impact |
|----------|------------|------|--------|
| `LOG_LEVEL` | Yes | No | Logging level not configurable |

### Undocumented but Used

| Variable | Used In | Purpose |
|----------|---------|---------|
| `HOST` | `main.py` | Server bind address |

---

## Bugs and Recommended Fixes

### Critical Issues

#### 1. In-Memory Storage Not Persisted to Database

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 270-272)

**Issue**: Data models and pages are stored in Python dictionaries (`data_models` and `pages`), not in the database. Data is lost on service restart.

```python
# Current implementation
data_models: dict[str, InternalDataModel] = {}
pages: dict[str, InternalPage] = {}
```

**Recommendation**: Implement database persistence using asyncpg:

```python
async def create_data_model(request: DataModelCreateRequest):
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO lowcode_data_models (tenant_id, name, name_ar, description, fields)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, created_at, updated_at
            """,
            request.tenant_id, request.name, request.name_ar,
            request.description, json.dumps(request.fields)
        )
        return DataModelResponse(id=str(row['id']), ...)
```

---

#### 2. Tenant Filtering Not Enforced

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 863-883, 959-986)

**Issue**: The `tenant_id` query parameter is required but not used to filter results. All data is returned regardless of tenant.

```python
# Current implementation - tenant_id is accepted but not used
@app.get("/api/v1/models", response_model=list[DataModelResponse], tags=["Data Models"])
def list_data_models(
    tenant_id: str = Query(...),  # Required but unused!
    limit: int = Query(50, ge=1, le=200),
):
    results = list(data_models.values())[:limit]  # No filtering by tenant_id
```

**Recommendation**: Filter by tenant_id:

```python
def list_data_models(tenant_id: str = Query(...), limit: int = Query(50)):
    results = [m for m in data_models.values() if m.tenant_id == tenant_id][:limit]
```

---

#### 3. NATS Events Never Published

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 663-679)

**Issue**: The `publish_event` function is defined but never called. Events are not published to NATS.

**Recommendation**: Add event publishing to create/update endpoints:

```python
@app.post("/api/v1/models", response_model=DataModelResponse)
async def create_data_model(request: DataModelCreateRequest):
    # ... model creation logic ...

    # Publish event
    await publish_event(
        f"sahool.{request.tenant_id}.lowcode.model.created",
        {
            "model_id": model_id,
            "tenant_id": request.tenant_id,
            "name": request.name,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    return response
```

---

### High Severity Issues

#### 4. Missing Authentication on Endpoints

**Location**: `/apps/services/lowcode-engine/src/main.py`

**Issue**: Authentication dependencies (`get_current_user`) are imported but not applied to any endpoints.

**Recommendation**: Add authentication to all non-health endpoints:

```python
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

@app.post("/api/v1/models", response_model=DataModelResponse)
async def create_data_model(
    request: DataModelCreateRequest,
    user: User = Depends(get_current_user),  # Add this
):
    validate_tenant_access(user, request.tenant_id)
    # ... rest of implementation
```

---

#### 5. validate_tenant_access Never Used

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 650-656)

**Issue**: The `validate_tenant_access` function is defined but never called.

```python
def validate_tenant_access(user: User, tenant_id: str) -> None:
    """Validate that user has access to the specified tenant."""
    if user.tenant_id and user.tenant_id != tenant_id:
        raise TenantAccessDeniedError(tenant_id=tenant_id)
```

**Recommendation**: Use this function after authentication in all tenant-scoped endpoints.

---

#### 6. Rate Limiting Not Applied

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 417-418)

**Issue**: Rate limiter is configured but decorators are not applied to any endpoints.

```python
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
# But no @limiter.limit() decorators used!
```

**Recommendation**: Apply rate limiting decorators:

```python
@app.post("/api/v1/ai/suggest", response_model=AISuggestionResponse)
@limiter.limit("10/minute")  # Add this
async def suggest_components(request: AISuggestionRequest):
    # ...
```

---

### Medium Severity Issues

#### 7. Missing PATCH Endpoint for Pages

**Location**: Documentation vs Implementation

**Issue**: README documents a `PATCH /api/v1/pages/{page_id}` endpoint, but it is not implemented.

**Recommendation**: Implement the update endpoint:

```python
@app.patch("/api/v1/pages/{page_id}", response_model=PageResponse)
async def update_page(page_id: str, request: PageUpdateRequest):
    if page_id not in pages:
        raise ResourceNotFoundError(resource_type="Page", resource_id=page_id)

    page = pages[page_id]
    if request.name:
        page.name = request.name
    # ... update other fields
    page.updated_at = datetime.utcnow()

    await cache_delete(f"lowcode:page:{page_id}")
    return page
```

---

#### 8. Test Assertions Don't Match Error Response Format

**Location**: `/apps/services/lowcode-engine/tests/test_main.py` (lines 145, 272, 384, etc.)

**Issue**: Tests expect `data["detail"]` but error responses use `data["error"]` and `data["detail"]` fields differently.

```python
# Test expects:
assert data["detail"] == "Component not found"

# But error response has:
{
    "error": "Resource not found",
    "detail": "Component not found"  # This should work
}
```

**Note**: Some tests may fail due to inconsistent error message expectations.

---

#### 9. AI Suggestion is Keyword-Based, Not AI

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 1089-1127)

**Issue**: The "AI" suggestion endpoint uses simple keyword matching, not actual AI/ML.

```python
# Current implementation - simple keyword matching
keyword_components = {
    ("map", "field", "location"): "field_map",
    ("crop", "plant"): "crop_selector",
    # ...
}
```

**Recommendation**: Consider integrating with actual AI service or documenting that this is keyword-based.

---

### Low Severity Issues

#### 10. Missing Database Migration Automation

**Location**: `/apps/services/lowcode-engine/migrations/`

**Issue**: Database migrations exist but are not automatically applied on startup.

**Recommendation**: Add migration running to lifespan:

```python
async def run_migrations(pool):
    async with pool.acquire() as conn:
        with open("migrations/001_create_data_models_pages_tables.sql") as f:
            await conn.execute(f.read())
```

---

#### 11. Redis Cache Keys Without TTL Validation

**Location**: `/apps/services/lowcode-engine/src/main.py` (lines 357-398)

**Issue**: Cache TTL is hardcoded and inconsistent (300s for pages, 3600s for components).

**Recommendation**: Make cache TTL configurable via environment variables.

---

#### 12. datetime.utcnow() Deprecation

**Location**: Multiple locations

**Issue**: `datetime.utcnow()` is deprecated in Python 3.12+.

**Recommendation**: Use `datetime.now(timezone.utc)`:

```python
from datetime import datetime, timezone

# Instead of:
datetime.utcnow()

# Use:
datetime.now(timezone.utc)
```

---

## Summary of Recommended Actions

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| Critical | Implement database persistence | High | Data loss on restart |
| Critical | Enforce tenant filtering | Low | Data isolation breach |
| Critical | Publish NATS events | Low | Event-driven features broken |
| High | Apply authentication | Medium | Security vulnerability |
| High | Use validate_tenant_access | Low | Authorization bypass |
| High | Apply rate limiting | Low | DoS vulnerability |
| Medium | Implement PATCH endpoint | Medium | API completeness |
| Medium | Fix test assertions | Low | Test reliability |
| Low | Migration automation | Medium | Deployment reliability |
| Low | Cache TTL configuration | Low | Operational flexibility |

---

## File Locations

| File | Purpose |
|------|---------|
| `/apps/services/lowcode-engine/src/main.py` | Main FastAPI application |
| `/apps/services/lowcode-engine/requirements.txt` | Python dependencies |
| `/apps/services/lowcode-engine/Dockerfile` | Container definition |
| `/apps/services/lowcode-engine/migrations/001_create_data_models_pages_tables.sql` | Database schema |
| `/shared/lowcode/engine.py` | Core low-code engine |
| `/shared/lowcode/__init__.py` | Module exports |
| `/apps/services/lowcode-engine/tests/test_main.py` | API endpoint tests |
| `/apps/services/lowcode-engine/tests/test_lowcode_engine.py` | Engine unit tests |
| `/apps/services/lowcode-engine/tests/test_models.py` | Pydantic model tests |
| `/apps/services/lowcode-engine/tests/conftest.py` | Test fixtures |

---

*Analysis Date: January 25, 2026*
*Service Version: 16.0.0*
