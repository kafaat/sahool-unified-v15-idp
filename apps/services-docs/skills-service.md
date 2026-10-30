# Skills Service Analysis Document

**Service Name:** skills-service
**Version:** 16.0.0
**Type:** Python/FastAPI
**Layer:** Intelligence
**Category:** Crop
**Status:** Active (with issues)
**Analysis Date:** 2026-01-25

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [NATS Events](#nats-events)
6. [Skills Assessment Features](#skills-assessment-features)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Configuration Sources](#configuration-sources)
10. [Bugs and Issues](#bugs-and-issues)
11. [Recommended Fixes](#recommended-fixes)
12. [Security Considerations](#security-considerations)
13. [Testing](#testing)

---

## Overview

The Skills Service manages AI model skill compression, memory storage/recall, and performance evaluation for the SAHOOL platform. According to the governance registry, it is intended to provide AI-powered farmer skills assessment and adaptive learning recommendations.

### Service Descriptions

| Language | Description |
|----------|-------------|
| English | AI-powered farmer skills assessment and adaptive learning recommendations |
| Arabic | تقييم مهارات المزارعين والتوصيات التعليمية المخصصة |

### Service Names

| Language | Name |
|----------|------|
| English | Skills Service |
| Arabic | خدمة المهارات |

### File Location

```
/home/user/sahool-unified-v15-idp/apps/services/skills-service/
├── Dockerfile
├── .dockerignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── main.py
└── tests/
    ├── __init__.py
    └── test_endpoints.py
```

---

## Architecture

### Service Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.126.0 |
| Server | Uvicorn |
| Validation | Pydantic 2.9.2 |
| HTTP Client | httpx 0.28.1 |
| Logging | structlog 24.1.0 |
| Cache | Redis 5.2.1 (with hiredis) |
| In-Memory Cache | cachetools 5.3.0 |

### Data Flow

```
Client Request
    │
    ▼
┌─────────────────────────────────────┐
│ Middleware Layer                     │
│ - Request ID (X-Request-ID)          │
│ - Token Revocation (if available)    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Route Handler                        │
│ - Authentication (optional)          │
│ - Input Validation (Pydantic)        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Business Logic                       │
│ - Compression                        │
│ - Memory Operations                  │
│ - Evaluation                         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Response                             │
│ - Standardized JSON format           │
│ - Error handling via SahoolException │
└─────────────────────────────────────┘
```

### Container Configuration

| Setting | Value |
|---------|-------|
| User | sahool (non-root) |
| Python Version | 3.11 |
| Security | no-new-privileges |
| Resource Limits (CPU) | 0.5 cores (limit), 0.25 cores (reservation) |
| Resource Limits (Memory) | 384MB (limit), 128MB (reservation) |
| Health Check Interval | 30s |
| Health Check Timeout | 10s |
| Restart Policy | unless-stopped |

---

## API Endpoints

### Health Check Endpoints

#### GET /healthz
Liveness probe for Kubernetes/Docker health checks.

**Response:**
```json
{
  "status": "ok",
  "service": "skills_service",
  "version": "16.0.0"
}
```

#### GET /readyz
Readiness probe indicating service can handle requests.

**Response:**
```json
{
  "status": "ok",
  "revocation_store": true
}
```

#### GET /
Root endpoint providing service information.

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "skills_service",
    "version": "16.0.0",
    "endpoints": [
      "POST /compress",
      "POST /memory/store",
      "POST /memory/recall",
      "POST /evaluate",
      "GET /healthz",
      "GET /readyz"
    ]
  }
}
```

---

### Core Business Endpoints

#### POST /compress
Compress skill data using configurable compression levels.

**Request Body:**
```json
{
  "skill_id": "model-v1-compress",
  "skill_data": {
    "weights": [0.1, 0.2, 0.3],
    "config": {"layers": 3}
  },
  "compression_level": 6,
  "target_size_kb": 512
}
```

**Response:**
```json
{
  "skill_id": "model-v1-compress",
  "original_size_kb": 0.12,
  "compressed_size_kb": 0.05,
  "compression_ratio": 0.583,
  "compression_level": 6,
  "compressed_data": "eyJza2lsbF9pZCI6ICJtb2RlbC12MS1jb21wcmVzcyIsICJvcmlnaW5hbF9zaXplIjogMC4xMiwgImRhdGEiOiB7fX0="
}
```

**Errors:**
- 422: Empty skill_data
- 422: compression_level out of range (1-9)

---

#### POST /memory/store
Store skill in volatile memory for fast access with TTL support.

**Request Body:**
```json
{
  "skill_id": "model-v1",
  "namespace": "inference",
  "skill_data": {
    "weights": [0.1, 0.2],
    "config": {}
  },
  "ttl_seconds": 3600,
  "metadata": {
    "version": "1.0",
    "algorithm": "transformer"
  }
}
```

**Response:**
```json
{
  "skill_id": "model-v1",
  "namespace": "inference",
  "stored_at": "2026-01-25T12:00:00.000000",
  "ttl_seconds": 3600,
  "success": true
}
```

**Errors:**
- 422: Empty skill_id
- 422: Empty skill_data

---

#### POST /memory/recall
Recall previously stored skill from memory.

**Request Body:**
```json
{
  "skill_id": "model-v1",
  "namespace": "inference",
  "include_metadata": true
}
```

**Response:**
```json
{
  "skill_id": "model-v1",
  "namespace": "inference",
  "found": false,
  "skill_data": null,
  "metadata": {},
  "retrieved_at": "2026-01-25T12:00:00.000000"
}
```

**Note:** Currently returns `found: false` always as this is a simulated implementation without actual Redis backing.

**Errors:**
- 422: Empty skill_id

---

#### POST /evaluate
Evaluate skill performance against configurable metrics.

**Request Body:**
```json
{
  "skill_id": "model-v1",
  "input_data": {
    "text": "sample input"
  },
  "expected_output": {
    "prediction": "expected value"
  },
  "metrics": ["accuracy", "latency", "memory"]
}
```

**Response:**
```json
{
  "skill_id": "model-v1",
  "status": "completed",
  "metrics": {
    "accuracy": 0.923,
    "latency_ms": 125.45,
    "memory_mb": 45.67
  },
  "performance_score": 0.923,
  "timestamp": "2026-01-25T12:00:00.000000"
}
```

**Supported Metrics:**
- `accuracy` - Returns value between 0.8-0.99
- `latency` - Returns latency_ms between 10-500ms
- `memory` - Returns memory_mb between 10-100MB
- Other metrics - Returns value between 0.5-1.0

**Errors:**
- 422: Empty skill_id
- 422: Empty input_data

---

## Request/Response Schemas

### Request Models

#### CompressRequest
```python
class CompressRequest(BaseModel):
    skill_id: str           # Required - Unique identifier for the skill
    skill_data: dict[str, Any]  # Required - The skill data to compress
    compression_level: int = 1  # Optional - 1-9 (1=fastest, 9=best)
    target_size_kb: int = None  # Optional - Target compressed size in KB
```

#### MemoryStoreRequest
```python
class MemoryStoreRequest(BaseModel):
    skill_id: str           # Required - Unique skill identifier
    namespace: str = "default"  # Optional - Memory namespace
    skill_data: dict[str, Any]  # Required - Skill data to store
    ttl_seconds: int = 3600     # Optional - TTL in seconds (0=permanent)
    metadata: dict[str, Any] = {}  # Optional - Metadata
```

#### MemoryRecallRequest
```python
class MemoryRecallRequest(BaseModel):
    skill_id: str           # Required - Skill ID to recall
    namespace: str = "default"  # Optional - Memory namespace
    include_metadata: bool = False  # Optional - Include metadata in response
```

#### EvaluateRequest
```python
class EvaluateRequest(BaseModel):
    skill_id: str           # Required - Skill ID to evaluate
    input_data: dict[str, Any]  # Required - Test input data
    expected_output: dict[str, Any] = None  # Optional - Expected output
    metrics: list[str] = ["accuracy", "latency"]  # Metrics to evaluate
```

### Response Models

#### CompressResponse
```python
class CompressResponse(BaseModel):
    skill_id: str
    original_size_kb: float
    compressed_size_kb: float
    compression_ratio: float
    compression_level: int
    compressed_data: str  # Base64 encoded
```

#### MemoryStoreResponse
```python
class MemoryStoreResponse(BaseModel):
    skill_id: str
    namespace: str
    stored_at: str  # ISO 8601 timestamp
    ttl_seconds: int
    success: bool
```

#### MemoryRecallResponse
```python
class MemoryRecallResponse(BaseModel):
    skill_id: str
    namespace: str
    found: bool
    skill_data: dict[str, Any] = None
    metadata: dict[str, Any] = None
    retrieved_at: str = None  # ISO 8601 timestamp
```

#### EvaluateResponse
```python
class EvaluateResponse(BaseModel):
    skill_id: str
    status: str  # "completed"
    metrics: dict[str, Any]
    performance_score: float  # 0.0-1.0
    timestamp: str  # ISO 8601 timestamp
```

---

## NATS Events

### Events Defined in Governance (NOT IMPLEMENTED)

According to `/home/user/sahool-unified-v15-idp/governance/services.yaml`, the service should produce and consume the following events:

#### Events Produced (NOT IMPLEMENTED)

| Event | Description |
|-------|-------------|
| `FarmerSkillsAssessed.v1` | Published when farmer skills assessment completes |
| `LearningPathRecommended.v1` | Published when learning path is generated |
| `SkillsProgressTracked.v1` | Published when skill progress is updated |

#### Events Consumed (NOT IMPLEMENTED)

| Event | Description |
|-------|-------------|
| `FieldIndicatorsComputed.v1` | Subscribe to field indicator updates |
| `TaskCompleted.v1` | Subscribe to task completion events |
| `CropHealthAssessed.v1` | Subscribe to crop health assessments |
| `YieldPredicted.v1` | Subscribe to yield predictions |

### Current Implementation Status

**WARNING:** The current implementation does NOT connect to NATS and does NOT publish or subscribe to any events. This is a significant gap between the service specification and actual implementation.

---

## Skills Assessment Features

### Features Defined in Governance (NOT IMPLEMENTED)

According to the governance registry, the following modules should be available:

| Module ID | Name | Endpoint | Status |
|-----------|------|----------|--------|
| skill-assessment | Skill Assessment Engine | /assessment | NOT IMPLEMENTED |
| learning-pathway | Learning Pathway Generator | /learning-path | NOT IMPLEMENTED |
| skill-progress | Progress Tracking | /progress | NOT IMPLEMENTED |
| competency-matrix | Competency Matrix | /competencies | NOT IMPLEMENTED |
| adaptive-learning | Adaptive Learning Engine | /adaptive | NOT IMPLEMENTED |
| peer-benchmarking | Peer Benchmarking | /benchmarking | NOT IMPLEMENTED |

### Currently Implemented Features

| Feature | Description | Status |
|---------|-------------|--------|
| Skill Compression | Base64 encoding with simulated compression | SIMULATED |
| Memory Store | Store skills in memory (no actual persistence) | SIMULATED |
| Memory Recall | Recall skills (always returns not found) | SIMULATED |
| Skill Evaluation | Performance metrics (random values) | SIMULATED |

---

## Dependencies

### Python Dependencies (requirements.txt)

```
# Base requirements
fastapi==0.126.0
starlette>=0.49.1
uvicorn[standard]>=0.30.0,<1.0.0
pydantic==2.9.2
httpx==0.28.1
python-dotenv==1.0.1

# Testing requirements
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==4.1.0
pytest-mock==3.12.0

# Service-specific dependencies
structlog>=24.1.0

# Redis for token revocation and caching
redis[hiredis]==5.2.1

# In-memory cache support
cachetools>=5.3.0
```

### Shared Module Dependencies

The service imports from the `shared` directory:

```python
from shared.errors_py import (
    ErrorCode,
    ValidationException,
    add_request_id_middleware,
    create_success_response,
    setup_exception_handlers,
)
```

**Optional Auth Dependencies (gracefully handled if missing):**
```python
from auth.dependencies import get_current_user
from auth.models import User
from auth.revocation_middleware import TokenRevocationMiddleware
from auth.token_revocation import get_revocation_store
```

### Infrastructure Dependencies (docker-compose.yml)

| Dependency | Purpose | Required |
|------------|---------|----------|
| redis | Token revocation, session caching | Yes |

### Missing Dependencies (per governance/services.yaml)

| Dependency | Purpose | Status |
|------------|---------|--------|
| postgres | Skills database | NOT CONNECTED |
| nats | Event messaging | NOT CONNECTED |

---

## Environment Variables

### Currently Used

| Variable | Default | Description | Source |
|----------|---------|-------------|--------|
| `PORT` | 8170 (Dockerfile), 8121 (docker-compose) | Service port | main.py, Dockerfile, docker-compose |
| `LOG_LEVEL` | INFO | Logging level | docker-compose.yml |
| `ENVIRONMENT` | development | Environment mode | docker-compose.yml |

### Expected but NOT Used (per governance/services.yaml)

| Variable | Purpose | Status |
|----------|---------|--------|
| `DATABASE_URL` | PostgreSQL connection | NOT IMPLEMENTED |
| `REDIS_URL` | Redis connection | NOT IMPLEMENTED |
| `NATS_URL` | NATS connection | NOT IMPLEMENTED |
| `SKILL_ASSESSMENT_MODEL` | AI model for assessment | NOT IMPLEMENTED |
| `LEARNING_RECOMMENDATION_ENGINE` | Learning engine config | NOT IMPLEMENTED |

---

## Configuration Sources

### Port Configuration Inconsistencies

| Source | Port Value | Location |
|--------|------------|----------|
| main.py | 8170 | Comment + os.getenv default |
| Dockerfile | 8170 | ENV PORT, EXPOSE, HEALTHCHECK |
| docker-compose.yml | 8121 | environment + ports mapping |
| Kong Gateway | 8121 | infrastructure/gateway/kong/kong.yml |
| governance/services.yaml | 8170 | Service registry |
| README.md | 8110 | Documentation |

### Kong Gateway Configuration

**Location:** `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/kong.yml`

```yaml
- name: skills-service
  host: skills-service
  port: 8121
  protocol: http
  routes:
    - name: skills-service-route
      paths: ["/api/v1/skills", "/skills"]
      strip_path: true
      protocols: ["http", "https"]
```

### Docker Compose Configuration

**Location:** `/home/user/sahool-unified-v15-idp/docker-compose.yml`

```yaml
skills-service:
  build:
    context: .
    dockerfile: apps/services/skills-service/Dockerfile
  container_name: sahool-skills-service
  environment:
    - PORT=8121
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - ENVIRONMENT=${ENVIRONMENT:-development}
  ports:
    - "8121:8121"
  depends_on:
    redis:
      condition: service_healthy
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8121/healthz')"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 15s
```

---

## Bugs and Issues

### Critical Issues

#### 1. Port Configuration Inconsistency (CRITICAL)

**Description:** Multiple configuration sources specify different ports, causing deployment confusion and potential service discovery failures.

| Source | Port |
|--------|------|
| main.py | 8170 |
| Dockerfile | 8170 |
| docker-compose.yml | 8121 |
| Kong Gateway | 8121 |
| governance/services.yaml | 8170 |
| README.md | 8110 |

**Impact:** Service may not be reachable through Kong gateway if container runs on wrong port.

**File Locations:**
- `/home/user/sahool-unified-v15-idp/apps/services/skills-service/src/main.py` (line 4, 430)
- `/home/user/sahool-unified-v15-idp/apps/services/skills-service/Dockerfile` (lines 48-52)
- `/home/user/sahool-unified-v15-idp/docker-compose.yml` (lines 2704, 2708)

---

#### 2. Missing Database Connection (CRITICAL)

**Description:** governance/services.yaml specifies PostgreSQL database requirements, but the service has no database connection code.

**Expected (per governance):**
```yaml
database:
  type: postgresql
  name: sahool_skills
  schema: "skills"
```

**Actual:** No database connection in main.py.

**Impact:** Cannot persist farmer skills, learning paths, or progress tracking.

---

#### 3. Missing NATS Event Integration (CRITICAL)

**Description:** The service should produce and consume NATS events but has no NATS connection code.

**Expected Events (Produces):**
- FarmerSkillsAssessed.v1
- LearningPathRecommended.v1
- SkillsProgressTracked.v1

**Expected Events (Consumes):**
- FieldIndicatorsComputed.v1
- TaskCompleted.v1
- CropHealthAssessed.v1
- YieldPredicted.v1

**Impact:** Service cannot participate in the event-driven architecture.

---

### High Priority Issues

#### 4. Missing Core API Endpoints (HIGH)

**Description:** Six endpoints defined in governance/services.yaml are not implemented.

| Missing Endpoint | Module |
|------------------|--------|
| `/assessment` | Skill Assessment Engine |
| `/learning-path` | Learning Pathway Generator |
| `/progress` | Progress Tracking |
| `/competencies` | Competency Matrix |
| `/adaptive` | Adaptive Learning Engine |
| `/benchmarking` | Peer Benchmarking |

**Impact:** Service does not provide advertised farmer skills functionality.

---

#### 5. Simulated Implementation Only (HIGH)

**Description:** All current endpoints return simulated/fake data:

- `/compress` - Uses base64 encoding, not actual compression
- `/memory/store` - Does not actually persist to Redis
- `/memory/recall` - Always returns `found: false`
- `/evaluate` - Returns random metric values

**Impact:** Service provides no real value in production.

---

### Medium Priority Issues

#### 6. Health Endpoint Mismatch (MEDIUM)

**Description:** governance/services.yaml specifies `/health` but actual endpoint is `/healthz`.

**governance/services.yaml:**
```yaml
health_endpoint: "/health"
```

**Actual:** `/healthz`

**Impact:** Health monitoring may fail if using governance config.

---

#### 7. ValidationException Usage Error (MEDIUM)

**Description:** In main.py, `ValidationException` is called with `ErrorCode` as first argument, but the constructor expects a string message.

**Code (line 238-241):**
```python
raise ValidationException(
    ErrorCode.INVALID_INPUT,  # Should be a string message
    details={"field": "skill_data", "message": "Skill data cannot be empty"},
)
```

**Expected:**
```python
raise ValidationException(
    message="Skill data cannot be empty",
    details={"field": "skill_data"},
)
```

**Impact:** May cause unexpected error messages.

---

#### 8. Missing Redis URL Configuration (MEDIUM)

**Description:** Redis dependency is declared in docker-compose.yml but REDIS_URL is not passed to the container.

**Impact:** Token revocation store may not function correctly.

---

### Low Priority Issues

#### 9. Compression Algorithm is Simulated (LOW)

**Description:** The compression implementation uses base64 encoding with simulated compression ratios rather than actual compression (gzip, zlib).

**Code (line 250):**
```python
compression_ratio = 0.7 - (request.compression_level * 0.03)  # 0.7 to 0.4
```

---

#### 10. Random Evaluation Metrics (LOW)

**Description:** Evaluation metrics return random values, not actual measurements.

**Code (lines 381-388):**
```python
if metric == "accuracy":
    metrics["accuracy"] = round(random.uniform(0.8, 0.99), 3)
elif metric == "latency":
    metrics["latency_ms"] = round(random.uniform(10, 500), 2)
```

---

#### 11. datetime.utcnow() Deprecation (LOW)

**Description:** Code uses deprecated `datetime.utcnow()`. Should use `datetime.now(timezone.utc)`.

**Locations:** Lines 304, 338, 376, 401

---

## Recommended Fixes

### Fix 1: Standardize Port Configuration

**Priority:** CRITICAL

Update all configuration sources to use port 8121 (as used by Kong and docker-compose):

1. Update `main.py` line 4:
```python
# Port: 8121
```

2. Update `main.py` line 430:
```python
port = int(os.getenv("PORT", 8121))
```

3. Update `Dockerfile` lines 48-52:
```dockerfile
ENV PORT=8121
EXPOSE 8121
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8121/healthz')" || exit 1
```

4. Update `governance/services.yaml`:
```yaml
port: 8121
```

5. Update `README.md` to use port 8121.

---

### Fix 2: Add Database Connection

**Priority:** CRITICAL

Add PostgreSQL connection in main.py lifespan:

```python
import asyncpg

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10
            )
            print("Database connected")
        except Exception as e:
            print(f"Database connection failed: {e}")

    yield

    # Cleanup
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
```

Add to requirements.txt:
```
asyncpg>=0.30.0
```

---

### Fix 3: Add NATS Event Integration

**Priority:** CRITICAL

Add NATS connection and event handlers:

```python
import nats
from nats.aio.client import Client as NATS

@asynccontextmanager
async def lifespan(app: FastAPI):
    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            nc = await nats.connect(nats_url)
            app.state.nc = nc

            # Subscribe to events
            await nc.subscribe("sahool.field.indicators.computed", cb=handle_indicators)
            await nc.subscribe("sahool.task.completed", cb=handle_task_completed)

            print("NATS connected")
        except Exception as e:
            print(f"NATS connection failed: {e}")

    yield

    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()

async def handle_indicators(msg):
    """Handle field indicators computed events"""
    # Process for skills assessment
    pass

async def handle_task_completed(msg):
    """Handle task completion events"""
    # Update skill progress
    pass
```

Add to requirements.txt:
```
nats-py>=2.7.0
```

---

### Fix 4: Implement Missing Endpoints

**Priority:** HIGH

Add the six missing endpoints defined in governance:

```python
@app.post("/assessment")
async def assess_farmer_skills(request: AssessmentRequest):
    """Evaluate farmer competency levels"""
    pass

@app.post("/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """Generate personalized learning recommendations"""
    pass

@app.get("/progress/{farmer_id}")
async def get_skill_progress(farmer_id: str):
    """Monitor skill development over time"""
    pass

@app.get("/competencies")
async def get_competency_matrix():
    """Map agricultural competencies and skill levels"""
    pass

@app.post("/adaptive")
async def adaptive_learning(request: AdaptiveLearningRequest):
    """Adjust learning content based on performance"""
    pass

@app.get("/benchmarking/{farmer_id}")
async def peer_benchmarking(farmer_id: str):
    """Compare skills against peer groups"""
    pass
```

---

### Fix 5: Fix ValidationException Usage

**Priority:** MEDIUM

Update ValidationException calls to use proper message argument:

```python
# Before (incorrect)
raise ValidationException(
    ErrorCode.INVALID_INPUT,
    details={"field": "skill_data", "message": "Skill data cannot be empty"},
)

# After (correct)
raise ValidationException(
    message="Skill data cannot be empty",
    message_ar="لا يمكن أن تكون بيانات المهارة فارغة",
    details={"field": "skill_data"},
)
```

---

### Fix 6: Add Health Endpoint Alias

**Priority:** MEDIUM

Add `/health` alias to match governance specification:

```python
@app.get("/health")
def health_alias():
    """Health check endpoint (alias for /healthz)"""
    return health()
```

---

### Fix 7: Implement Real Redis Storage

**Priority:** MEDIUM

Replace simulated memory operations with actual Redis:

```python
import redis.asyncio as redis

@app.post("/memory/store")
async def store_in_memory(request: MemoryStoreRequest):
    redis_client = await redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

    key = f"skill:{request.namespace}:{request.skill_id}"
    await redis_client.set(
        key,
        json.dumps(request.skill_data),
        ex=request.ttl_seconds if request.ttl_seconds > 0 else None
    )

    return MemoryStoreResponse(...)
```

---

### Fix 8: Update datetime Usage

**Priority:** LOW

Replace deprecated `datetime.utcnow()`:

```python
# Before
from datetime import datetime
stored_at = datetime.utcnow().isoformat()

# After
from datetime import datetime, timezone
stored_at = datetime.now(timezone.utc).isoformat()
```

---

## Security Considerations

### Current Security Features

| Feature | Status | Implementation |
|---------|--------|----------------|
| Non-root container user | Implemented | `sahool` user in Dockerfile |
| No privilege escalation | Implemented | `no-new-privileges:true` in docker-compose |
| JWT Authentication | Optional | Falls back gracefully if auth not available |
| Token Revocation | Optional | Redis-backed, middleware exempt paths configured |
| Request ID Tracing | Implemented | X-Request-ID header middleware |
| Input Validation | Implemented | Pydantic models |
| Unified Error Handling | Implemented | SahoolException framework |

### Security Exempt Paths

The following paths are exempt from token revocation checks:
- `/healthz`
- `/health`
- `/docs`
- `/redoc`
- `/openapi.json`

### Recommendations

1. **Add rate limiting** - No rate limiting is currently implemented
2. **Add input sanitization** - skill_data accepts arbitrary dict, should validate structure
3. **Add audit logging** - No audit trail for skill operations
4. **Implement RBAC** - No role-based access control for different operations

---

## Testing

### Test Coverage

**Location:** `/home/user/sahool-unified-v15-idp/apps/services/skills-service/tests/test_endpoints.py`

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestHealthEndpoints | 3 | /healthz, /readyz, / |
| TestCompressionEndpoint | 3 | Valid compression, invalid data, level validation |
| TestMemoryEndpoints | 4 | Store, store validation, recall, recall with metadata |
| TestEvaluationEndpoint | 3 | Basic evaluation, custom metrics, missing input |

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test class
pytest tests/test_endpoints.py::TestCompressionEndpoint -v
```

### Test Markers

```python
@pytest.mark.unit       # Fast, no I/O
@pytest.mark.integration # API, database
@pytest.mark.slow       # Long-running
```

### Missing Test Coverage

- Authentication flow testing
- Redis integration testing
- Database integration testing
- NATS event testing
- Error handling edge cases
- Concurrent request handling

---

## Summary

The skills-service is currently a **skeleton implementation** that:

1. **Works:** Basic health checks, simulated compression/memory/evaluation endpoints
2. **Missing:** Database persistence, NATS events, farmer skills assessment, learning paths
3. **Critical Issues:** Port inconsistency across 5 configuration sources
4. **Gap:** Significant difference between governance specification and actual implementation

### Implementation Completeness

| Category | Governance Spec | Actual | Gap |
|----------|-----------------|--------|-----|
| API Endpoints | 12 | 6 | 6 missing |
| NATS Events (Produce) | 3 | 0 | 3 missing |
| NATS Events (Consume) | 4 | 0 | 4 missing |
| Database Tables | 1 schema | 0 | Not connected |
| Environment Variables | 5 | 2 | 3 missing |

### Priority Actions

1. **Immediate:** Fix port configuration inconsistency
2. **High:** Add database connection and NATS integration
3. **High:** Implement missing farmer skills endpoints
4. **Medium:** Replace simulated logic with real implementations
5. **Low:** Add comprehensive test coverage

---

*Document generated: 2026-01-25*
*Service path: /home/user/sahool-unified-v15-idp/apps/services/skills-service/*
