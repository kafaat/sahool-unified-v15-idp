# SAHOOL Low-Code Engine Service

**Visual Application Builder for Agricultural Apps | منصة بناء التطبيقات المرئية للتطبيقات الزراعية**

[![Version](https://img.shields.io/badge/version-16.0.0-blue.svg)](./package.json)
[![Port](https://img.shields.io/badge/port-8132-green.svg)](./Dockerfile)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](./requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.126+-green.svg)](./requirements.txt)

---

## Table of Contents

- [Service Overview](#service-overview)
- [Features](#features)
- [Component Categories](#component-categories)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Examples](#examples)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Arabic Section | القسم العربي](#arabic-section--القسم-العربي)

---

## Service Overview

The **Low-Code Engine** service provides a visual application builder platform for creating agricultural applications without extensive coding. Inspired by [Alibaba LowCode Engine](https://lowcode-engine.cn/) and [NocoBase](https://www.nocobase.com/), it enables farmers, agronomists, and developers to rapidly build custom dashboards, forms, and data management interfaces.

| Property | Value |
|----------|-------|
| **Service Name** | `lowcode-engine` |
| **Service Name (AR)** | `محرك التطوير منخفض الكود` |
| **Version** | `16.0.0` |
| **Port** | `8132` |
| **Framework** | FastAPI (Python) |
| **Database** | PostgreSQL (with in-memory fallback) |
| **Messaging** | NATS |

### Architecture

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
│           API Layer (FastAPI + Rate Limiting)                   │
├────────────────────────────┼────────────────────────────────────┤
│    PostgreSQL (asyncpg)    │    NATS (Events)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Component Library** | Rich set of pre-built components for forms, tables, charts, and maps |
| **Data Model Designer** | Define data structures with fields, validation, and relationships |
| **Page Builder** | Visual drag-and-drop page composition with blocks |
| **AI Suggestions** | AI-powered component recommendations based on context |
| **Agricultural Components** | Specialized components for field mapping, irrigation, sensors, and crop health |
| **Bilingual Support** | Full Arabic and English support for all components and APIs |
| **Multi-tenant** | Tenant isolation for enterprise deployments |
| **Plugin Architecture** | Extensible through custom plugins |

### Supported Component Types

- **Layout**: Container, Grid, Flex layouts
- **Form**: Text input, Number input, Select, Date picker
- **Data**: Data tables with pagination and sorting
- **Chart**: Line charts, Bar charts, Pie charts
- **Map**: Interactive field maps with NDVI layers
- **Agricultural**: Crop selector, Irrigation scheduler, Sensor display
- **AI**: AI advisor widget with contextual recommendations

---

## Component Categories

The service includes a comprehensive component library organized by category:

### Layout Components | مكونات التخطيط

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `container` | Container | حاوية | Flexible container with padding and direction |
| `grid` | Grid | شبكة | Grid layout with configurable columns |

### Form Components | مكونات النموذج

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `text_input` | Text Input | حقل نصي | Single-line text input field |
| `number_input` | Number Input | حقل رقمي | Numeric input with min/max validation |
| `select` | Select | قائمة منسدلة | Dropdown selection with single/multi mode |
| `date_picker` | Date Picker | منتقي التاريخ | Date selection with Hijri calendar support |

### Data Components | مكونات البيانات

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `data_table` | Data Table | جدول البيانات | Paginated, sortable data table |

### Chart Components | مكونات الرسم البياني

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `line_chart` | Line Chart | رسم بياني خطي | Time-series line visualization |

### Map Components | مكونات الخريطة

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `field_map` | Field Map | خريطة الحقل | Interactive map with NDVI, satellite, and sensor layers |

### Agricultural Components | المكونات الزراعية

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `crop_selector` | Crop Selector | منتقي المحصول | Crop selection with regional recommendations |
| `irrigation_scheduler` | Irrigation Scheduler | جدولة الري | Irrigation planning with auto-scheduling |
| `sensor_display` | Sensor Display | عرض المستشعر | Real-time sensor readings with history |
| `crop_health_card` | Crop Health Card | بطاقة صحة المحصول | NDVI-based crop health visualization |

### AI Components | مكونات الذكاء الاصطناعي

| Component | Name | Name (AR) | Description |
|-----------|------|-----------|-------------|
| `ai_advisor` | AI Advisor | مستشار الذكاء الاصطناعي | Context-aware agricultural advisory |

---

## API Endpoints

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthz` | Liveness probe |
| `GET` | `/readyz` | Readiness probe (includes DB and NATS status) |
| `GET` | `/health` | Detailed health status |
| `GET` | `/metrics` | Prometheus-compatible metrics |

### Component Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `GET` | `/api/v1/components` | List all components | 60/min |
| `GET` | `/api/v1/components/{component_name}` | Get component details | 60/min |
| `GET` | `/api/v1/components/categories` | List component categories | 60/min |

**Query Parameters for List Components:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category (e.g., `form`, `agriculture`, `map`) |

### Data Model Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/models` | Create a data model | 30/min |
| `GET` | `/api/v1/models` | List data models | 60/min |
| `GET` | `/api/v1/models/{model_id}` | Get data model by ID | 60/min |

**Query Parameters for List Models:**

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
| `PATCH` | `/api/v1/pages/{page_id}` | Update a page | 30/min |
| `POST` | `/api/v1/pages/{page_id}/publish` | Publish a page | 30/min |
| `GET` | `/api/v1/pages/{page_id}/render` | Render page with data | 60/min |

**Query Parameters for List Pages:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant identifier |
| `is_published` | boolean | No | Filter by published status |
| `limit` | integer | No | Max results (default: 50, max: 200) |

### AI Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/ai/suggest` | Get AI component suggestions | 10/min |
| `GET` | `/api/v1/ai/templates` | List page templates | 60/min |
| `POST` | `/api/v1/ai/generate-page` | Generate page from template | 30/min |

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | - | PostgreSQL connection URL |
| `NATS_URL` | No | - | NATS server URL |
| `JWT_SECRET_KEY` | Yes | - | JWT secret for authentication |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `CORS_ALLOWED_ORIGINS` | No | `http://localhost:3000,http://localhost:8080` | Comma-separated CORS origins |
| `ENVIRONMENT` | No | `development` | Environment name |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Example `.env` File

```bash
# Database
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool?sslmode=require

# NATS Messaging
NATS_URL=nats://nats:4222

# Authentication
JWT_SECRET_KEY=your-32-character-minimum-secret-key
JWT_ALGORITHM=HS256

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# General
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Examples

### Authentication

All API endpoints (except health checks) require JWT authentication. Include the token in the `Authorization` header:

```bash
export TOKEN="your-jwt-token"
```

### List All Components

```bash
curl -X GET "http://localhost:8132/api/v1/components" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### List Components by Category (Agricultural)

```bash
curl -X GET "http://localhost:8132/api/v1/components?category=agriculture" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Get Component Details

```bash
curl -X GET "http://localhost:8132/api/v1/components/field_map" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Create a Data Model

```bash
curl -X POST "http://localhost:8132/api/v1/models" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Field",
    "name_ar": "حقل",
    "description": "Agricultural field data model",
    "description_ar": "نموذج بيانات الحقل الزراعي",
    "tenant_id": "farm-001",
    "fields": [
      {
        "name": "name",
        "name_ar": "الاسم",
        "field_type": "string",
        "required": true
      },
      {
        "name": "area_ha",
        "name_ar": "المساحة (هكتار)",
        "field_type": "number",
        "required": true
      },
      {
        "name": "crop_type",
        "name_ar": "نوع المحصول",
        "field_type": "string"
      },
      {
        "name": "boundary",
        "name_ar": "الحدود",
        "field_type": "geojson"
      }
    ]
  }'
```

### List Data Models

```bash
curl -X GET "http://localhost:8132/api/v1/models?tenant_id=farm-001&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Create a Page

```bash
curl -X POST "http://localhost:8132/api/v1/pages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Field Dashboard",
    "name_ar": "لوحة تحكم الحقل",
    "description": "Dashboard showing field health and sensor data",
    "route": "/dashboard/field",
    "tenant_id": "farm-001",
    "blocks": [
      {
        "component_name": "field_map",
        "props": {
          "show_ndvi": true,
          "show_sensors": true,
          "satellite_layer": "ndvi"
        }
      },
      {
        "component_name": "crop_health_card",
        "props": {
          "show_score": true,
          "show_recommendations": true
        }
      },
      {
        "component_name": "sensor_display",
        "props": {
          "sensor_type": "soil_moisture",
          "show_history": true
        }
      }
    ]
  }'
```

### List Pages

```bash
curl -X GET "http://localhost:8132/api/v1/pages?tenant_id=farm-001&is_published=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Publish a Page

```bash
curl -X POST "http://localhost:8132/api/v1/pages/{page_id}/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Render a Page

```bash
curl -X GET "http://localhost:8132/api/v1/pages/{page_id}/render" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Get AI Component Suggestions

```bash
curl -X POST "http://localhost:8132/api/v1/ai/suggest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a dashboard for monitoring field irrigation and soil moisture sensors",
    "description_ar": "إنشاء لوحة تحكم لمراقبة ري الحقل ومستشعرات رطوبة التربة",
    "context": {
      "crop_type": "wheat",
      "region": "riyadh"
    }
  }'
```

### List Page Templates

```bash
curl -X GET "http://localhost:8132/api/v1/ai/templates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Generate Page from Template

```bash
curl -X POST "http://localhost:8132/api/v1/ai/generate-page?template_id=field-dashboard&name=My%20Dashboard&name_ar=%D9%84%D9%88%D8%AD%D8%AA%D9%8A&tenant_id=farm-001" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Check Health

```bash
# Liveness probe
curl -X GET "http://localhost:8132/healthz"

# Readiness probe
curl -X GET "http://localhost:8132/readyz"

# Detailed health
curl -X GET "http://localhost:8132/health"

# Prometheus metrics
curl -X GET "http://localhost:8132/metrics"
```

---

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ (optional, has in-memory fallback)
- NATS 2.x (optional)

### Local Development

1. **Clone the repository:**

   ```bash
   cd sahool-unified-v15-idp
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate   # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r apps/services/lowcode-engine/requirements.txt
   ```

4. **Set environment variables:**

   ```bash
   export ENVIRONMENT=development
   export JWT_SECRET_KEY=test-secret-key-for-development-32ch
   export JWT_ALGORITHM=HS256
   # Optional: DATABASE_URL, NATS_URL
   ```

5. **Run the service:**

   ```bash
   cd apps/services/lowcode-engine
   uvicorn src.main:app --host 0.0.0.0 --port 8132 --reload
   ```

6. **Access the API documentation:**

   - Swagger UI: http://localhost:8132/docs
   - ReDoc: http://localhost:8132/redoc

### Docker Development

```bash
# Build the image
docker build -t sahool-lowcode-engine -f apps/services/lowcode-engine/Dockerfile .

# Run the container
docker run -p 8132:8132 \
  -e JWT_SECRET_KEY=test-secret-key-for-development-32ch \
  -e ENVIRONMENT=development \
  sahool-lowcode-engine
```

### Using Make Commands

```bash
# Start full development environment
make dev

# Start infrastructure only
make infra-up

# View logs
make logs-service SERVICE=lowcode-engine
```

---

## Testing

### Run All Tests

```bash
# From project root
pytest apps/services/lowcode-engine/tests/ -v

# With coverage
pytest apps/services/lowcode-engine/tests/ -v --cov=apps/services/lowcode-engine/src --cov-report=html
```

### Run Specific Test Classes

```bash
# Health endpoint tests
pytest apps/services/lowcode-engine/tests/test_main.py::TestHealthEndpoints -v

# Component endpoint tests
pytest apps/services/lowcode-engine/tests/test_main.py::TestComponentEndpoints -v

# Data model endpoint tests
pytest apps/services/lowcode-engine/tests/test_main.py::TestDataModelEndpoints -v

# Page endpoint tests
pytest apps/services/lowcode-engine/tests/test_main.py::TestPageEndpoints -v

# AI suggestion endpoint tests
pytest apps/services/lowcode-engine/tests/test_main.py::TestAISuggestionEndpoints -v
```

### Test Environment Variables

```bash
export ENVIRONMENT=test
export JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars
export JWT_ALGORITHM=HS256
export DATABASE_URL=""  # Empty for in-memory storage
export NATS_URL=""
```

### Test Coverage Requirements

- Minimum coverage: 60%
- All API endpoints must have tests
- Health checks must return correct status

---

## Database Schema

The service uses two main tables:

### `lowcode_data_models`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | VARCHAR(100) | Tenant identifier |
| `name` | VARCHAR(100) | Model name |
| `name_ar` | VARCHAR(100) | Model name (Arabic) |
| `description` | TEXT | Description |
| `description_ar` | TEXT | Description (Arabic) |
| `fields` | JSONB | Field definitions array |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

### `lowcode_pages`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | VARCHAR(100) | Tenant identifier |
| `name` | VARCHAR(100) | Page name |
| `name_ar` | VARCHAR(100) | Page name (Arabic) |
| `description` | TEXT | Description |
| `description_ar` | TEXT | Description (Arabic) |
| `route` | VARCHAR(255) | URL route |
| `layout` | VARCHAR(50) | Layout type |
| `blocks` | JSONB | Block configurations array |
| `data_model_id` | UUID | Reference to data model (FK) |
| `is_published` | BOOLEAN | Published status |
| `version` | INTEGER | Page version |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

### Run Migrations

```bash
# Migrations are applied automatically on startup when DATABASE_URL is set
# Manual migration:
psql $DATABASE_URL -f apps/services/lowcode-engine/migrations/001_create_data_models_pages_tables.sql
```

---

## NATS Events

The service publishes events to NATS for integration with other services:

| Event Subject | Description |
|---------------|-------------|
| `sahool.{tenant_id}.lowcode.model.created` | Data model created |
| `sahool.{tenant_id}.lowcode.page.created` | Page created |
| `sahool.{tenant_id}.lowcode.page.published` | Page published |

### Event Payload Example

```json
{
  "model_id": "uuid",
  "tenant_id": "farm-001",
  "name": "Field",
  "name_ar": "حقل",
  "field_count": 4,
  "timestamp": "2026-01-22T10:30:00Z"
}
```

---

## Arabic Section | القسم العربي

### نظرة عامة على الخدمة

خدمة **محرك التطوير منخفض الكود** توفر منصة لبناء التطبيقات المرئية لإنشاء تطبيقات زراعية بدون الحاجة إلى برمجة مكثفة. مستوحاة من [Alibaba LowCode Engine](https://lowcode-engine.cn/) و [NocoBase](https://www.nocobase.com/)، تتيح للمزارعين والمهندسين الزراعيين والمطورين بناء لوحات تحكم ونماذج وواجهات إدارة بيانات مخصصة بسرعة.

### الميزات الرئيسية

| الميزة | الوصف |
|--------|-------|
| **مكتبة المكونات** | مجموعة غنية من المكونات الجاهزة للنماذج والجداول والرسوم البيانية والخرائط |
| **مصمم نماذج البيانات** | تعريف هياكل البيانات مع الحقول والتحقق والعلاقات |
| **منشئ الصفحات** | تكوين صفحات مرئي بالسحب والإفلات مع الكتل |
| **اقتراحات الذكاء الاصطناعي** | توصيات مكونات مدعومة بالذكاء الاصطناعي بناءً على السياق |
| **المكونات الزراعية** | مكونات متخصصة لرسم خرائط الحقول والري والمستشعرات وصحة المحاصيل |
| **دعم ثنائي اللغة** | دعم كامل للعربية والإنجليزية لجميع المكونات وواجهات برمجة التطبيقات |

### فئات المكونات

#### مكونات التخطيط
- **حاوية (Container)**: حاوية مرنة مع الحشو والاتجاه
- **شبكة (Grid)**: تخطيط شبكي مع أعمدة قابلة للتكوين

#### مكونات النموذج
- **حقل نصي (Text Input)**: حقل إدخال نص سطر واحد
- **حقل رقمي (Number Input)**: إدخال رقمي مع التحقق من الحد الأدنى/الأقصى
- **قائمة منسدلة (Select)**: اختيار منسدل مع وضع فردي/متعدد
- **منتقي التاريخ (Date Picker)**: اختيار التاريخ مع دعم التقويم الهجري

#### المكونات الزراعية
- **خريطة الحقل (Field Map)**: خريطة تفاعلية مع طبقات NDVI والأقمار الصناعية والمستشعرات
- **منتقي المحصول (Crop Selector)**: اختيار المحصول مع توصيات إقليمية
- **جدولة الري (Irrigation Scheduler)**: تخطيط الري مع الجدولة التلقائية
- **عرض المستشعر (Sensor Display)**: قراءات المستشعر في الوقت الفعلي مع السجل
- **بطاقة صحة المحصول (Crop Health Card)**: تصور صحة المحصول المستند إلى NDVI
- **مستشار الذكاء الاصطناعي (AI Advisor)**: استشارات زراعية مدركة للسياق

### أمثلة على الاستخدام

#### إنشاء نموذج بيانات

```bash
curl -X POST "http://localhost:8132/api/v1/models" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Field",
    "name_ar": "حقل",
    "description": "Agricultural field data model",
    "description_ar": "نموذج بيانات الحقل الزراعي",
    "tenant_id": "farm-001",
    "fields": [
      {
        "name": "name",
        "name_ar": "الاسم",
        "field_type": "string",
        "required": true
      },
      {
        "name": "area_ha",
        "name_ar": "المساحة (هكتار)",
        "field_type": "number"
      }
    ]
  }'
```

#### إنشاء صفحة

```bash
curl -X POST "http://localhost:8132/api/v1/pages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Field Dashboard",
    "name_ar": "لوحة تحكم الحقل",
    "route": "/dashboard/field",
    "tenant_id": "farm-001",
    "blocks": [
      {
        "component_name": "field_map",
        "props": {
          "show_ndvi": true,
          "show_sensors": true
        }
      }
    ]
  }'
```

#### الحصول على اقتراحات الذكاء الاصطناعي

```bash
curl -X POST "http://localhost:8132/api/v1/ai/suggest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create irrigation monitoring dashboard",
    "description_ar": "إنشاء لوحة تحكم لمراقبة الري"
  }'
```

### قوالب الصفحات المتاحة

| المعرف | الاسم | الوصف |
|--------|------|-------|
| `field-dashboard` | لوحة تحكم الحقل | لوحة تحكم تعرض صحة الحقل والطقس وحالة الري |
| `farm-overview` | نظرة عامة على المزرعة | نظرة عامة على جميع الحقول في المزرعة مع المقاييس الرئيسية |
| `irrigation-planner` | مخطط الري | تخطيط وجدولة الري للحقول |

---

## Related Documentation

- [SAHOOL Platform Overview](../../../docs/README.md)
- [API Gateway Configuration](../../../docs/API_GATEWAY.md)
- [Authentication Guide](../../../docs/AUTHENTICATION.md)
- [Shared Low-Code Module](../../../shared/lowcode/README.md)

---

## License

Proprietary - KAFAAT

---

_Last Updated: January 2026_
