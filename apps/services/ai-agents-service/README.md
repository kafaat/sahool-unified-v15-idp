# AI Agents Service

Autonomous AI agents for agricultural intelligence.

**Service Name:** `ai-agents-service`
**Arabic Name:** `خدمة الوكلاء الذكية`
**Version:** 16.0.0
**Port:** 8130
**License:** Proprietary (KAFAAT)

---

## Table of Contents

- [Service Overview](#service-overview)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [API Examples](#api-examples)
- [Development](#development)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Arabic Documentation](#arabic-documentation)

---

## Service Overview

The AI Agents Service provides autonomous AI agents for agricultural intelligence within the SAHOOL platform. Inspired by modern agentic patterns (Dexter, OpenCode, Claude Code), this service enables:

- **Task Decomposition**: Break down complex agricultural queries into executable steps
- **Agricultural Research**: Analyze satellite, weather, and sensor data for field insights
- **Farm Advisory**: Generate irrigation, fertilization, and crop health recommendations
- **Planning Support**: Create planting and rotation plans with cost analysis
- **Self-Validation**: Validate agent outputs with retry logic for reliability

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent System** | Three specialized agent types for different agricultural tasks |
| **Dual-Mode Execution** | Plan-only, Execute-only, or Hybrid modes |
| **Event-Driven** | NATS integration for real-time event publishing |
| **Multi-Tenancy** | Full tenant isolation with JWT authentication |
| **Bilingual Support** | Arabic and English responses throughout |
| **Rate Limiting** | Tiered rate limits based on user subscription |
| **Audit Trail** | Full logging of agent executions for compliance |

---

## Architecture

### Agent Types

The service provides three specialized agent types:

#### 1. Farm Advisor Agent (`farm_advisor`)

Dual-mode agent for comprehensive farm advisory with Plan and Execute modes.

| Property | Value |
|----------|-------|
| **Name** | Farm Advisor Agent |
| **Arabic Name** | وكيل المستشار الزراعي |
| **Modes** | `plan`, `execute`, `hybrid` |
| **Use Cases** | Irrigation scheduling, fertilizer recommendations, disease diagnosis |

**Available Tools:**
- `fetch_satellite_data` - Retrieve NDVI and vegetation indices
- `fetch_weather_data` - Get current and forecast weather
- `fetch_sensor_data` - Read IoT sensor values
- `analyze_crop_health` - AI-powered crop health assessment
- `generate_recommendations` - Create actionable recommendations
- `schedule_irrigation` - Schedule irrigation events
- `create_task` - Create tasks for farm workers

#### 2. Agricultural Research Agent (`research`)

Specialized agent for agricultural data analysis and research.

| Property | Value |
|----------|-------|
| **Name** | Agricultural Research Agent |
| **Arabic Name** | وكيل البحث الزراعي |
| **Modes** | `execute`, `hybrid` |
| **Use Cases** | Field health analysis, yield prediction, historical trend analysis |

**Available Tools:**
- `fetch_satellite_data` - Satellite imagery and indices
- `fetch_weather_data` - Weather data retrieval
- `fetch_sensor_data` - Sensor data collection
- `analyze_crop_health` - Health score calculation
- `calculate_irrigation_need` - Water requirement calculation
- `diagnose_crop_issue` - Disease and pest diagnosis

#### 3. Planner Agent (`planner`)

Read-only planning agent for task analysis and recommendations.

| Property | Value |
|----------|-------|
| **Name** | Planner Agent |
| **Arabic Name** | وكيل التخطيط |
| **Modes** | `plan` only |
| **Use Cases** | Crop rotation planning, resource allocation, cost estimation |

**Available Tools:**
- `fetch_satellite_data` - Historical satellite data
- `fetch_weather_data` - Weather outlook
- `analyze_crop_health` - Current status assessment

### Execution Modes

| Mode | Description | State Flow |
|------|-------------|------------|
| **Plan** | Generate a plan without execution | `idle` -> `planning` -> `completed` |
| **Execute** | Execute tasks directly | `idle` -> `executing` -> `completed` |
| **Hybrid** | Plan first, then execute | `idle` -> `planning` -> `executing` -> `completed` |

### Execution States

```
idle -> planning -> executing -> validating -> completed
                                          \-> error
                                          \-> cancelled
```

| State | Description |
|-------|-------------|
| `idle` | Agent ready, no active task |
| `planning` | Decomposing task into steps |
| `executing` | Running tool actions |
| `validating` | Validating step results |
| `completed` | Task finished successfully |
| `error` | Task failed with error |
| `cancelled` | Task cancelled by user |

### Event-Driven Integration

The service publishes events to NATS for real-time notifications:

| Event | Subject Pattern | Description |
|-------|-----------------|-------------|
| Execution Started | `sahool.{tenant_id}.agent.execution.started` | Agent begins task |
| Step Completed | `sahool.{tenant_id}.agent.step.completed` | Individual step finished |
| Execution Completed | `sahool.{tenant_id}.agent.execution.completed` | Task completed successfully |
| Execution Failed | `sahool.{tenant_id}.agent.execution.failed` | Task failed with error |

### Database Schema

Execution records are persisted in PostgreSQL:

```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL DEFAULT 'hybrid',
    goal TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    state VARCHAR(20) NOT NULL DEFAULT 'idle',
    result JSONB,
    steps JSONB DEFAULT '[]'::jsonb,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_duration_ms INTEGER,
    tenant_id VARCHAR(100) NOT NULL,
    field_id VARCHAR(100),
    farm_id VARCHAR(100)
);
```

---

## API Endpoints

### Health Endpoints

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| `GET` | `/healthz` | Liveness probe | None |
| `GET` | `/readyz` | Readiness probe | None |
| `GET` | `/health` | Detailed health status | None |
| `GET` | `/metrics` | Prometheus metrics | None |

### Agent Management Endpoints

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| `GET` | `/api/v1/agents` | List available agents | 60/min |
| `POST` | `/api/v1/agents/execute` | Execute an agent task | 10/min |
| `GET` | `/api/v1/agents/executions` | List recent executions | 60/min |
| `GET` | `/api/v1/agents/executions/{id}` | Get execution details | 60/min |
| `GET` | `/api/v1/agents/executions/{id}/status` | Get brief status | 60/min |
| `DELETE` | `/api/v1/agents/executions/{id}` | Cancel execution | 60/min |

### Quick Action Endpoints

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| `POST` | `/api/v1/agents/quick/analyze` | Quick field analysis | 60/min |

### Endpoint Details

#### GET /healthz

Liveness probe for Kubernetes.

**Response:**
```json
{
  "status": "ok",
  "service": "ai-agents-service",
  "service_ar": "خدمة الوكلاء الذكية",
  "version": "16.0.0"
}
```

#### GET /readyz

Readiness probe with dependency status.

**Response:**
```json
{
  "status": "ok",
  "database": true,
  "nats": true,
  "executions_active": 3
}
```

#### GET /api/v1/agents

List all available agent types.

**Response:**
```json
[
  {
    "agent_type": "farm_advisor",
    "name": "Farm Advisor Agent",
    "name_ar": "وكيل المستشار الزراعي",
    "description": "Dual-mode agent for farm advisory with Plan and Execute modes",
    "description_ar": "وكيل ثنائي الوضع للاستشارات الزراعية مع وضعي التخطيط والتنفيذ",
    "supported_modes": ["plan", "execute", "hybrid"],
    "available_tools": [
      "fetch_satellite_data",
      "fetch_weather_data",
      "fetch_sensor_data",
      "analyze_crop_health",
      "generate_recommendations",
      "schedule_irrigation",
      "create_task"
    ]
  }
]
```

#### POST /api/v1/agents/execute

Execute an agent task.

**Request Body:**
```json
{
  "task": "What is the irrigation need for field F003?",
  "task_ar": "ما هي احتياجات الري للحقل F003؟",
  "agent_type": "farm_advisor",
  "mode": "hybrid",
  "context": {
    "crop_type": "wheat",
    "current_moisture": 35
  },
  "tenant_id": "tenant-001",
  "field_id": "F003",
  "farm_id": "FARM-001",
  "max_steps": 50,
  "timeout_seconds": 300
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `task` | string | Yes | - | Task in natural language |
| `task_ar` | string | No | - | Task in Arabic |
| `agent_type` | string | No | `farm_advisor` | Agent type |
| `mode` | string | No | `hybrid` | Execution mode |
| `context` | object | No | `{}` | Additional context |
| `tenant_id` | string | Yes | - | Tenant ID |
| `field_id` | string | No | - | Field ID |
| `farm_id` | string | No | - | Farm ID |
| `max_steps` | integer | No | 50 | Max steps (1-100) |
| `timeout_seconds` | integer | No | 300 | Timeout (30-600) |

**Response:**
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "tenant-001",
  "agent_type": "farm_advisor",
  "mode": "hybrid",
  "task": "What is the irrigation need for field F003?",
  "status": "running",
  "state": "planning",
  "steps": [],
  "final_result": null,
  "error": null,
  "started_at": "2026-01-22T10:30:00Z",
  "completed_at": null,
  "total_duration_ms": null
}
```

#### GET /api/v1/agents/executions/{execution_id}

Get full execution details.

**Response:**
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "tenant-001",
  "agent_type": "farm_advisor",
  "mode": "hybrid",
  "task": "What is the irrigation need for field F003?",
  "status": "completed",
  "state": "completed",
  "steps": [
    {
      "step_number": 1,
      "action": "Fetching field status",
      "action_ar": "جلب حالة الحقل",
      "tool_used": "get_field_status",
      "result": {"field_id": "F003", "soil_moisture": 35},
      "timestamp": "2026-01-22T10:30:01Z",
      "duration_ms": 150
    },
    {
      "step_number": 2,
      "action": "Calculating irrigation need",
      "action_ar": "حساب احتياجات الري",
      "tool_used": "calculate_irrigation_need",
      "result": {"recommended_amount_mm": 25},
      "timestamp": "2026-01-22T10:30:02Z",
      "duration_ms": 200
    }
  ],
  "final_result": {
    "success": true,
    "summary": "Field F003 requires 25mm irrigation within the next 24 hours.",
    "summary_ar": "يحتاج الحقل F003 إلى 25 مم من الري خلال الـ 24 ساعة القادمة."
  },
  "error": null,
  "started_at": "2026-01-22T10:30:00Z",
  "completed_at": "2026-01-22T10:30:03Z",
  "total_duration_ms": 3000
}
```

#### POST /api/v1/agents/quick/analyze

Quick field analysis without full agent execution.

**Request Body:**
```json
{
  "field_id": "F003",
  "tenant_id": "tenant-001",
  "analysis_type": "crop_health"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field_id` | string | Yes | Field to analyze |
| `tenant_id` | string | Yes | Tenant ID |
| `analysis_type` | string | No | Type: `crop_health`, `irrigation`, `yield` |

**Response:**
```json
{
  "field_id": "F003",
  "analysis_type": "crop_health",
  "summary": "Field F003 shows healthy vegetation with NDVI of 0.72",
  "summary_ar": "يظهر الحقل F003 غطاء نباتي صحي بمؤشر NDVI يبلغ 0.72",
  "recommendations": [
    {
      "action": "Monitor soil moisture",
      "action_ar": "مراقبة رطوبة التربة",
      "priority": "medium",
      "reason": "Soil moisture levels are within normal range"
    }
  ],
  "confidence": 0.85,
  "timestamp": "2026-01-22T10:30:00Z"
}
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | - | PostgreSQL connection URL |
| `NATS_URL` | No | - | NATS server URL |
| `REDIS_URL` | No | - | Redis connection URL |
| `JWT_SECRET_KEY` | Yes | - | JWT signing key (min 32 chars) |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `CORS_ALLOWED_ORIGINS` | No | `http://localhost:3000,http://localhost:8080` | CORS origins |
| `ENVIRONMENT` | No | `development` | Environment name |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Example .env File

```bash
# Database (TLS enforced in production)
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require

# Messaging
NATS_URL=nats://nats:4222
REDIS_URL=redis://redis:6379

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
JWT_ALGORITHM=HS256

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Rate Limiting Tiers

| Tier | Requests/min | Use Case |
|------|--------------|----------|
| Free | 30 | Personal use |
| Standard | 60 | Most endpoints |
| Premium | 120 | High-volume users |
| Internal | 1000 | Service-to-service |
| Execute | 10 | Agent execution (resource intensive) |

---

## API Examples

### List Available Agents

```bash
curl -X GET http://localhost:8130/api/v1/agents \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Execute Farm Advisor Agent

```bash
curl -X POST http://localhost:8130/api/v1/agents/execute \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is the irrigation need for field F003?",
    "agent_type": "farm_advisor",
    "mode": "hybrid",
    "context": {"crop_type": "wheat"},
    "tenant_id": "tenant-001",
    "field_id": "F003"
  }'
```

### Execute Research Agent

```bash
curl -X POST http://localhost:8130/api/v1/agents/execute \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze the health status of my wheat field",
    "agent_type": "research",
    "mode": "execute",
    "context": {"crop_type": "wheat", "include_historical": true},
    "tenant_id": "tenant-001",
    "field_id": "F003"
  }'
```

### Execute Planner Agent

```bash
curl -X POST http://localhost:8130/api/v1/agents/execute \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Plan crop rotation for field F003 for next season",
    "agent_type": "planner",
    "mode": "plan",
    "context": {"current_crop": "wheat"},
    "tenant_id": "tenant-001",
    "field_id": "F003",
    "farm_id": "FARM-001"
  }'
```

### Get Execution Status

```bash
curl -X GET http://localhost:8130/api/v1/agents/executions/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Get Brief Execution Status

```bash
curl -X GET http://localhost:8130/api/v1/agents/executions/550e8400-e29b-41d4-a716-446655440000/status \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Cancel Running Execution

```bash
curl -X DELETE http://localhost:8130/api/v1/agents/executions/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### List Recent Executions

```bash
curl -X GET "http://localhost:8130/api/v1/agents/executions?tenant_id=tenant-001&status=completed&limit=10" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Quick Field Analysis

```bash
curl -X POST http://localhost:8130/api/v1/agents/quick/analyze \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "F003",
    "tenant_id": "tenant-001",
    "analysis_type": "crop_health"
  }'
```

### Health Check

```bash
curl -X GET http://localhost:8130/healthz
```

### Readiness Check

```bash
curl -X GET http://localhost:8130/readyz
```

### Prometheus Metrics

```bash
curl -X GET http://localhost:8130/metrics
```

---

## Development

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16+ (optional, service runs without database)
- NATS 2.x (optional, for event publishing)
- Redis 7.x (optional, for caching)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kafaat/sahool-unified-v15-idp.git
   cd sahool-unified-v15-idp
   ```

2. **Install dependencies:**
   ```bash
   cd apps/services/ai-agents-service
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export ENVIRONMENT=development
   export JWT_SECRET_KEY=dev-secret-key-minimum-32-characters
   export DATABASE_URL=""  # Optional
   export NATS_URL=""      # Optional
   ```

4. **Run the service:**
   ```bash
   # From service directory
   uvicorn src.main:app --host 0.0.0.0 --port 8130 --reload

   # Or from project root
   cd apps/services/ai-agents-service
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8130 --reload
   ```

5. **Access the API:**
   - Swagger UI: http://localhost:8130/docs
   - ReDoc: http://localhost:8130/redoc
   - OpenAPI JSON: http://localhost:8130/openapi.json

### Docker Development

1. **Build the image:**
   ```bash
   # From project root
   docker build -f apps/services/ai-agents-service/Dockerfile -t ai-agents-service .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8130:8130 \
     -e JWT_SECRET_KEY=dev-secret-key-minimum-32-characters \
     -e ENVIRONMENT=development \
     ai-agents-service
   ```

### Using Make Commands

```bash
# Start full development environment
make dev

# Start infrastructure only (postgres, redis, nats)
make infra-up

# Build all services
make build

# View logs
make logs-service SERVICE=ai-agents-service
```

### Project Structure

```
apps/services/ai-agents-service/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── README.md               # This file
├── migrations/
│   └── 001_create_agent_executions.sql
├── src/
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── db.py               # Database layer
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── __init__.py
│   └── events/
│       └── __init__.py
└── tests/
    ├── __init__.py
    ├── conftest.py         # Test fixtures
    ├── test_main.py        # API endpoint tests
    └── test_agents.py      # Agent logic tests
```

---

## Testing

### Run All Tests

```bash
# From service directory
pytest

# From project root
pytest apps/services/ai-agents-service/
```

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Smoke tests only
pytest -m smoke
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run with Verbose Output

```bash
pytest -v --tb=short
```

### Test Environment Variables

Tests automatically set these environment variables:

```bash
ENVIRONMENT=test
JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars
JWT_ALGORITHM=HS256
DATABASE_URL=""   # Empty for unit tests
NATS_URL=""       # Empty for unit tests
```

### Test Coverage Requirements

- Minimum coverage: 60%
- Coverage reports: `coverage.xml`, `coverage_html/`

### Test Categories

| Marker | Description | Example |
|--------|-------------|---------|
| `@pytest.mark.unit` | Fast tests, no I/O | Health endpoint tests |
| `@pytest.mark.integration` | Tests with database/NATS | Full execution flow |
| `@pytest.mark.smoke` | Import verification | Module loading tests |
| `@pytest.mark.asyncio` | Async test functions | Agent execution tests |

---

## Monitoring

### Prometheus Metrics

The `/metrics` endpoint exposes Prometheus-compatible metrics:

```
# HELP ai_agents_executions_total Total number of agent executions
# TYPE ai_agents_executions_total counter
ai_agents_executions_total 150

# HELP ai_agents_executions_running Currently running executions
# TYPE ai_agents_executions_running gauge
ai_agents_executions_running 3

# HELP ai_agents_executions_completed Completed executions
# TYPE ai_agents_executions_completed counter
ai_agents_executions_completed 140

# HELP ai_agents_executions_failed Failed executions
# TYPE ai_agents_executions_failed counter
ai_agents_executions_failed 7
```

### Health Monitoring

Configure Kubernetes probes:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8130
  initialDelaySeconds: 15
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /readyz
    port: 8130
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Logging

The service uses structured JSON logging via structlog:

```json
{
  "timestamp": "2026-01-22T10:30:00Z",
  "level": "info",
  "event": "agent_execution_started",
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_type": "farm_advisor",
  "tenant_id": "tenant-001"
}
```

---

## Arabic Documentation

# توثيق باللغة العربية

## نظرة عامة على الخدمة

توفر خدمة وكلاء الذكاء الاصطناعي وكلاء ذكاء اصطناعي مستقلين للذكاء الزراعي ضمن منصة سهول. تتيح هذه الخدمة:

- **تحليل المهام**: تقسيم الاستفسارات الزراعية المعقدة إلى خطوات قابلة للتنفيذ
- **البحث الزراعي**: تحليل بيانات الأقمار الصناعية والطقس والمستشعرات
- **الاستشارات الزراعية**: توليد توصيات الري والتسميد وصحة المحاصيل
- **دعم التخطيط**: إنشاء خطط الزراعة والتناوب مع تحليل التكاليف

## أنواع الوكلاء

### 1. وكيل المستشار الزراعي (farm_advisor)

وكيل ثنائي الوضع للاستشارات الزراعية الشاملة.

**الأوضاع المدعومة:**
- `plan` - التخطيط فقط
- `execute` - التنفيذ فقط
- `hybrid` - التخطيط ثم التنفيذ

**الأدوات المتاحة:**
- جلب بيانات الأقمار الصناعية
- جلب بيانات الطقس
- جلب بيانات المستشعرات
- تحليل صحة المحصول
- توليد التوصيات
- جدولة الري
- إنشاء المهام

### 2. وكيل البحث الزراعي (research)

وكيل متخصص لتحليل البيانات الزراعية والبحث.

**الأوضاع المدعومة:**
- `execute` - التنفيذ
- `hybrid` - الهجين

### 3. وكيل التخطيط (planner)

وكيل للقراءة فقط لتحليل المهام والتوصيات.

**الأوضاع المدعومة:**
- `plan` - التخطيط فقط

## أمثلة على الاستخدام

### تنفيذ مهمة الري

```bash
curl -X POST http://localhost:8130/api/v1/agents/execute \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "ما هي احتياجات الري للحقل F003؟",
    "agent_type": "farm_advisor",
    "mode": "hybrid",
    "tenant_id": "tenant-001",
    "field_id": "F003"
  }'
```

### التحليل السريع

```bash
curl -X POST http://localhost:8130/api/v1/agents/quick/analyze \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "F003",
    "tenant_id": "tenant-001",
    "analysis_type": "crop_health"
  }'
```

## حالات التنفيذ

| الحالة | الوصف |
|--------|-------|
| `idle` | الوكيل جاهز، لا توجد مهمة نشطة |
| `planning` | تحليل المهمة إلى خطوات |
| `executing` | تنفيذ الإجراءات |
| `validating` | التحقق من النتائج |
| `completed` | اكتملت المهمة بنجاح |
| `error` | فشلت المهمة |
| `cancelled` | تم إلغاء المهمة |

## حدود المعدل

| المستوى | الطلبات/دقيقة |
|---------|---------------|
| مجاني | 30 |
| قياسي | 60 |
| متميز | 120 |
| داخلي | 1000 |
| تنفيذ الوكيل | 10 |

---

## Related Documentation

- [CLAUDE.md](../../../CLAUDE.md) - Project guidelines
- [Shared AI Agents](../../../shared/ai/agents/) - Agent implementations
- [API Gateway](../../../docs/API_GATEWAY.md) - Gateway configuration
- [Observability](../../../docs/OBSERVABILITY.md) - Monitoring setup

---

## Support

For issues or questions:

1. Check the [documentation](../../../docs/)
2. Review the [service registry](../../../governance/services.yaml)
3. Contact the SAHOOL Platform Team

---

_Last Updated: January 2026_
