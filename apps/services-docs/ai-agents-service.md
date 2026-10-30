# AI Agents Service - Comprehensive Analysis

**Service Name:** `ai-agents-service`
**Arabic Name:** `خدمة الوكلاء الذكية`
**Version:** 16.0.0
**Port:** 8130
**Type:** Python/FastAPI
**Layer:** Intelligence
**Status:** Active

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [NATS Events](#nats-events)
6. [AI Agent Orchestration](#ai-agent-orchestration)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Database Schema](#database-schema)
10. [Bugs, Issues, and Recommendations](#bugs-issues-and-recommendations)

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
| Multi-Agent System | Three specialized agent types for different agricultural tasks |
| Dual-Mode Execution | Plan-only, Execute-only, or Hybrid modes |
| Event-Driven | NATS integration for real-time event publishing |
| Multi-Tenancy | Full tenant isolation with JWT authentication |
| Bilingual Support | Arabic and English responses throughout |
| Rate Limiting | Tiered rate limits based on endpoint sensitivity |
| Audit Trail | Full logging of agent executions for compliance |
| Redis Caching | Caches agent listings and completed execution statuses |
| Graceful Degradation | Runs without database (in-memory fallback) |

### Kong Gateway Configuration

```yaml
Host: ai-agents-service
Port: 8130
Routes:
  - /api/v1/ai-agents-service
  - /ai-agents-service
strip_path: true
```

---

## Architecture

### Service Layer

The AI Agents Service is part of the **Intelligence Layer** in SAHOOL's 4-layer event architecture:

```
Acquisition -> Intelligence -> Decision -> Business
                    ^
                    |
            ai-agents-service
```

### Agent Types

#### 1. Farm Advisor Agent (`farm_advisor`)

| Property | Value |
|----------|-------|
| Name | Farm Advisor Agent |
| Arabic Name | وكيل المستشار الزراعي |
| Modes | `plan`, `execute`, `hybrid` |
| Use Cases | Irrigation scheduling, fertilizer recommendations, disease diagnosis |

**Available Tools:**
- `get_field_status` - Get current field status
- `calculate_irrigation_need` - Calculate irrigation requirements
- `calculate_fertilizer_need` - Calculate fertilizer requirements
- `diagnose_crop_issue` - Diagnose crop health issues
- `create_task` - Create farm tasks (execute mode only)
- `schedule_irrigation` - Schedule irrigation events (execute mode only)
- `generate_advisory_report` - Generate comprehensive advisory reports

**Specialized Sub-Agents:**
- `IrrigationSubAgent` - ET calculation, water balance, schedule optimization
- `FertilizerSubAgent` - Nutrient analysis, requirement calculation, product recommendations
- `PestControlSubAgent` - Pest identification, infestation assessment, IPM treatments
- `HarvestPlannerSubAgent` - Maturity assessment, harvest window, logistics planning

#### 2. Agricultural Research Agent (`research`)

| Property | Value |
|----------|-------|
| Name | Agricultural Research Agent |
| Arabic Name | وكيل البحث الزراعي |
| Modes | `execute`, `hybrid` |
| Use Cases | Field health analysis, yield prediction, historical trend analysis |

**Available Tools:**
- `fetch_satellite_data` - Satellite imagery and indices
- `fetch_weather_data` - Weather data retrieval
- `fetch_sensor_data` - Sensor data collection
- `analyze_crop_health` - Health score calculation
- `calculate_irrigation_need` - Water requirement calculation
- `diagnose_crop_issue` - Disease and pest diagnosis

#### 3. Planner Agent (`planner`)

| Property | Value |
|----------|-------|
| Name | Planner Agent |
| Arabic Name | وكيل التخطيط |
| Modes | `plan` only |
| Use Cases | Crop rotation planning, resource allocation, cost estimation |

**Available Tools:**
- `fetch_satellite_data` - Historical satellite data
- `fetch_weather_data` - Weather outlook
- `analyze_crop_health` - Current status assessment

### Execution Modes

| Mode | Description | Initial State |
|------|-------------|---------------|
| `plan` | Generate a plan without execution | `planning` |
| `execute` | Execute tasks directly | `executing` |
| `hybrid` | Plan first, then execute | `planning` |

### Execution States

```
idle -> planning -> executing -> validating -> completed
                                          \-> error
                                          \-> cancelled
                                          \-> timeout
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

---

## API Endpoints

### Health Endpoints

| Method | Path | Description | Auth | Rate Limit |
|--------|------|-------------|------|------------|
| `GET` | `/healthz` | Liveness probe | No | None |
| `GET` | `/readyz` | Readiness probe | No | None |
| `GET` | `/health` | Detailed health status | No | None |
| `GET` | `/metrics` | Prometheus metrics | No | None |

### Agent Management Endpoints

| Method | Path | Description | Auth | Rate Limit |
|--------|------|-------------|------|------------|
| `GET` | `/api/v1/agents` | List available agents | Yes | 60/min |
| `POST` | `/api/v1/agents/execute` | Execute an agent task | Yes | 10/min |
| `GET` | `/api/v1/agents/executions` | List recent executions | Yes | 60/min |
| `GET` | `/api/v1/agents/executions/{id}` | Get execution details | Yes | 60/min |
| `GET` | `/api/v1/agents/executions/{id}/status` | Get brief status | Yes | 60/min |
| `DELETE` | `/api/v1/agents/executions/{id}` | Cancel execution | Yes | 60/min |

### Quick Action Endpoints

| Method | Path | Description | Auth | Rate Limit |
|--------|------|-------------|------|------------|
| `POST` | `/api/v1/agents/quick/analyze` | Quick field analysis | Yes | 60/min |

### Documentation Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |
| `GET` | `/openapi.json` | OpenAPI schema |

---

## Request/Response Schemas

### AgentExecuteRequest

```json
{
  "task": "string (required) - Task description in natural language",
  "task_ar": "string (optional) - Task description in Arabic",
  "agent_type": "string (default: 'farm_advisor') - Agent type: farm_advisor, research, planner",
  "mode": "string (default: 'hybrid') - Execution mode: plan, execute, hybrid",
  "context": "object (optional) - Additional context for the agent",
  "tenant_id": "string (required) - Tenant ID for multi-tenancy",
  "field_id": "string (optional) - Field ID for field-specific tasks",
  "farm_id": "string (optional) - Farm ID",
  "max_steps": "integer (default: 50, min: 1, max: 100) - Maximum execution steps",
  "timeout_seconds": "integer (default: 300, min: 30, max: 600) - Execution timeout"
}
```

### AgentExecuteResponse

```json
{
  "execution_id": "string - UUID of the execution",
  "tenant_id": "string - Tenant ID",
  "agent_type": "string - Agent type used",
  "mode": "string - Execution mode",
  "task": "string - Original task",
  "status": "string - running|completed|failed|timeout|cancelled",
  "state": "string - idle|planning|executing|validating|completed|error|cancelled",
  "steps": [
    {
      "step_number": "integer",
      "action": "string - Step action description",
      "action_ar": "string (optional) - Arabic description",
      "tool_used": "string (optional) - Tool name",
      "result": "object (optional) - Step result",
      "timestamp": "datetime",
      "duration_ms": "integer (optional)"
    }
  ],
  "final_result": "object (optional) - Final execution result",
  "error": "string (optional) - Error message if failed",
  "started_at": "datetime",
  "completed_at": "datetime (optional)",
  "total_duration_ms": "integer (optional)"
}
```

### AgentListItem

```json
{
  "agent_type": "string - Agent type identifier",
  "name": "string - Agent name",
  "name_ar": "string - Arabic name",
  "description": "string - Agent description",
  "description_ar": "string - Arabic description",
  "supported_modes": ["string"] - List of supported modes,
  "available_tools": ["string"] - List of available tools
}
```

### ExecutionStatusResponse

```json
{
  "execution_id": "string",
  "status": "string",
  "state": "string",
  "current_step": "integer",
  "total_steps": "integer",
  "progress_percent": "float",
  "last_action": "string (optional)"
}
```

### QuickAnalysisRequest

```json
{
  "field_id": "string (required) - Field to analyze",
  "tenant_id": "string (required) - Tenant ID",
  "analysis_type": "string (default: 'crop_health') - Type: crop_health, irrigation, yield"
}
```

### QuickAnalysisResponse

```json
{
  "field_id": "string",
  "analysis_type": "string",
  "summary": "string - English summary",
  "summary_ar": "string - Arabic summary",
  "recommendations": [
    {
      "action": "string",
      "action_ar": "string",
      "priority": "string",
      "reason": "string (optional)"
    }
  ],
  "confidence": "float (0-1)",
  "timestamp": "datetime"
}
```

### ErrorResponse

```json
{
  "error": "string - Error message",
  "error_ar": "string (optional) - Arabic error message",
  "error_code": "string - Error code",
  "detail": "string (optional) - Additional details",
  "request_id": "string (optional) - Request ID for tracing"
}
```

---

## NATS Events

### Events Produced

| Event | Subject Pattern | Description |
|-------|-----------------|-------------|
| `AgentExecutionStartedEvent` | `sahool.{tenant_id}.agent.execution.started` | Agent begins task |
| `AgentStepCompletedEvent` | `sahool.{tenant_id}.agent.step.completed` | Individual step finished |
| `AgentExecutionCompletedEvent` | `sahool.{tenant_id}.agent.execution.completed` | Task completed successfully |
| `AgentExecutionFailedEvent` | `sahool.{tenant_id}.agent.execution.failed` | Task failed with error |

### Event Schemas (from shared/events/contracts.py)

#### AgentExecutionStartedEvent

```python
class AgentExecutionStartedEvent(BaseEvent):
    execution_id: str
    agent_type: str
    goal: str
    mode: str = "hybrid"
    field_id: str | None = None
    farm_id: str | None = None
```

#### AgentExecutionCompletedEvent

```python
class AgentExecutionCompletedEvent(BaseEvent):
    execution_id: str
    agent_type: str
    goal: str
    status: str = "completed"
    steps_completed: int = 0
    duration_ms: int = 0
    result_summary: str | None = None
    result_summary_ar: str | None = None
```

#### AgentExecutionFailedEvent

```python
class AgentExecutionFailedEvent(BaseEvent):
    execution_id: str
    agent_type: str
    goal: str
    error_code: str
    error_message: str
    error_message_ar: str | None = None
    failed_at_step: int | None = None
    duration_ms: int = 0
```

#### AgentStepCompletedEvent

```python
class AgentStepCompletedEvent(BaseEvent):
    execution_id: str
    step_number: int
    step_description: str
    step_description_ar: str | None = None
    tool_used: str | None = None
    duration_ms: int = 0
    success: bool = True
```

### Events Consumed

Currently, the service does not subscribe to any NATS events. It operates as an event producer only.

---

## AI Agent Orchestration

### Agent Framework

The service uses a sophisticated agent framework from `shared/ai/agents/`:

```
shared/ai/agents/
├── __init__.py          # Exports all agent classes
├── base.py              # BaseAutonomousAgent + enums + data classes
├── agricultural_research.py  # AgriculturalResearchAgent
├── farm_advisor.py      # FarmAdvisorAgent + sub-agents
├── planner.py           # PlannerAgent
└── examples.py          # Usage examples
```

### Base Agent Features

- **Agent Modes**: Plan, Execute, Hybrid
- **Collaboration Roles**: Coordinator, Specialist, Observer
- **Consensus Types**: Unanimous, Majority, Weighted, Coordinator
- **Memory Types**: Episodic, Semantic, Procedural

### FarmAdvisorAgent Capabilities

#### Sub-Agent Delegation

```python
# Get specialized advice from sub-agents
result = await advisor.get_specialized_advice(
    domain="irrigation",  # or fertilizer, pest, harvest
    task="Calculate water needs for wheat field",
    context={"field_id": "F003"}
)
```

#### Collaborative Decision Making

```python
# Make decisions with multiple specialists
decision = await advisor.make_collaborative_decision(
    topic="Best approach for water stress and N deficiency",
    topic_ar="أفضل نهج لإجهاد المياه ونقص النيتروجين",
    options=[
        {"id": 0, "name": "Irrigate first"},
        {"id": 1, "name": "Fertilize first"},
        {"id": 2, "name": "Combined approach"},
    ],
    domains_involved=["irrigation", "fertilizer"],
)
```

#### Farmer Feedback Learning

```python
# Record feedback for continuous improvement
await advisor.record_farmer_feedback(
    recommendation_id="rec_001",
    rating=4,
    outcome="success",
    comments="The irrigation advice worked well"
)

# Get recommendations enhanced by past learning
advice = await advisor.get_recommendation_with_learning(
    task="When should I irrigate?",
    context={"field_id": "F003"}
)
```

### Execution Flow

1. **Request Received**: API validates request, generates execution ID
2. **Initial Response**: Returns immediately with `status: running`
3. **Background Task**: Agent executes asynchronously
   - Decomposes task into steps using LLM
   - Executes each step using registered tools
   - Validates step results
   - Handles errors and retries
4. **Completion**: Updates execution status, publishes NATS event
5. **Client Polling**: Client polls status endpoint for results

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.126.0,<1.0.0 | Web framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | >=2.10.0,<3.0.0 | Data validation |
| httpx | >=0.27.0,<1.0.0 | Async HTTP client |
| aiofiles | >=24.0.0,<25.0.0 | Async file operations |
| nats-py | >=2.9.0,<3.0.0 | NATS messaging |
| asyncpg | >=0.30.0,<1.0.0 | PostgreSQL async driver |
| structlog | >=24.0.0,<25.0.0 | Structured logging |
| numpy | >=1.26.0,<2.0.0 | Numerical operations |
| pyjwt | >=2.9.0,<3.0.0 | JWT authentication |
| slowapi | >=0.1.9,<1.0.0 | Rate limiting |
| redis | >=5.0.0,<6.0.0 | Redis caching |

### Shared Module Dependencies

| Module | Purpose |
|--------|---------|
| `shared.auth.dependencies` | JWT authentication (`get_current_user`) |
| `shared.auth.models` | User model |
| `shared.ai.agents` | Agent classes (FarmAdvisorAgent, AgriculturalResearchAgent, PlannerAgent) |
| `shared.events.publisher` | NATS event publishing |
| `shared.events.contracts` | Event schemas |

### Infrastructure Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL/PgBouncer | Persistence | Optional (falls back to in-memory) |
| Redis | Caching | Optional |
| NATS | Event messaging | Optional |

---

## Environment Variables

### Required Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | **Yes** | - | JWT signing key (min 32 chars) |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection URL |
| `NATS_URL` | - | NATS server URL |
| `REDIS_URL` | - | Redis connection URL |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:8080` | CORS origins (comma-separated) |
| `ENVIRONMENT` | `development` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8130` | Server port |

### Docker-Compose Configuration

```yaml
ai-agents-service:
  environment:
    - PORT=8130
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - ENVIRONMENT=${ENVIRONMENT:-development}
    - NATS_URL=${NATS_URL:-nats://nats:4222}
    - REDIS_URL=${REDIS_URL:-redis://redis:6379}
    - DATABASE_URL=${DATABASE_URL:-postgresql://sahool:sahool@pgbouncer:6432/sahool}
    - JWT_SECRET_KEY=${JWT_SECRET_KEY:-development-secret-key-min-32-chars}
    - JWT_ALGORITHM=${JWT_ALGORITHM:-HS256}
```

### Missing Environment Variables

The following environment variables are used by the service but not documented:

| Variable | Used In | Should Add |
|----------|---------|------------|
| `OLLAMA_BASE_URL` | Agent LLM integration | Yes, if using local LLM |
| `OPENAI_API_KEY` | External LLM provider | Yes, if using OpenAI |

---

## Database Schema

### Table: agent_executions

```sql
CREATE TABLE IF NOT EXISTS agent_executions (
    -- Primary Key
    id UUID PRIMARY KEY,

    -- Agent Configuration
    agent_type VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL DEFAULT 'hybrid',

    -- Task Information
    goal TEXT NOT NULL,

    -- Execution Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    state VARCHAR(20) NOT NULL DEFAULT 'idle',

    -- Results
    result JSONB,
    steps JSONB DEFAULT '[]'::jsonb,
    error TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_duration_ms INTEGER,

    -- Multi-tenancy & Context
    tenant_id VARCHAR(100) NOT NULL,
    field_id VARCHAR(100),
    farm_id VARCHAR(100),

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_state CHECK (state IN ('idle', 'planning', 'executing', 'validating', 'completed', 'error', 'cancelled')),
    CONSTRAINT valid_mode CHECK (mode IN ('plan', 'execute', 'hybrid'))
);
```

### Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_agent_executions_tenant_id ON agent_executions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON agent_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_type ON agent_executions(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_executions_tenant_status_created ON agent_executions(tenant_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_field_id ON agent_executions(field_id) WHERE field_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_executions_farm_id ON agent_executions(farm_id) WHERE farm_id IS NOT NULL;
```

### Update Trigger

```sql
CREATE OR REPLACE FUNCTION update_agent_executions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_agent_executions_updated_at
    BEFORE UPDATE ON agent_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_executions_updated_at();
```

---

## Bugs, Issues, and Recommendations

### Critical Issues

#### 1. Database Persistence Not Used in Execution Flow

**Severity:** High
**Location:** `src/main.py` lines 719-731, 874-879

**Description:** While the service creates database records when persisting executions (`db.create_execution`), it doesn't update the database when executions complete. The background task only updates the in-memory `executions` dict.

**Impact:** Execution results are lost on service restart; database always shows `running` status.

**Recommendation:**
```python
# In _execute_agent_task, after updating response:
if _use_database():
    await db.update_execution(
        execution_id=execution_id,
        status=response.status,
        state=response.state,
        result=response.final_result,
        steps=[s.model_dump() for s in response.steps],
        error=response.error,
        completed_at=response.completed_at,
        total_duration_ms=response.total_duration_ms,
    )
```

#### 2. NATS Events Not Published

**Severity:** High
**Location:** `src/main.py`

**Description:** The service initializes NATS publisher but never publishes events during agent execution. The NATS events (AgentExecutionStarted, AgentExecutionCompleted, etc.) are defined in contracts but not used.

**Impact:** Other services cannot react to agent events; audit trail incomplete.

**Recommendation:**
```python
# At start of _execute_agent_task:
if hasattr(app.state, "publisher") and app.state.publisher:
    await app.state.publisher.publish(
        AgentExecutionStartedEvent(
            execution_id=execution_id,
            agent_type=request.agent_type,
            goal=request.task,
            mode=request.mode,
            field_id=request.field_id,
            farm_id=request.farm_id,
        )
    )

# At completion:
if hasattr(app.state, "publisher") and app.state.publisher:
    await app.state.publisher.publish(
        AgentExecutionCompletedEvent(
            execution_id=execution_id,
            agent_type=request.agent_type,
            goal=request.task,
            status="completed",
            steps_completed=len(response.steps),
            duration_ms=response.total_duration_ms or 0,
        )
    )
```

### Medium Issues

#### 3. get_execution Endpoint is Synchronous

**Severity:** Medium
**Location:** `src/main.py` line 883

**Description:** The `get_execution` endpoint is defined as a sync function (`def get_execution`) but should be async to support database lookups.

**Impact:** Cannot retrieve executions from database; only works with in-memory store.

**Recommendation:** Change to `async def get_execution` and add database lookup:
```python
@app.get("/api/v1/agents/executions/{execution_id}", ...)
@limiter.limit("60/minute")
async def get_execution(...):
    # First check in-memory
    if execution_id in executions:
        execution = executions[execution_id]
        if user.tenant_id != execution.tenant_id:
            raise TenantAccessDeniedError(...)
        return execution

    # Then check database
    if _use_database():
        db_exec = await db.get_execution(execution_id)
        if db_exec:
            # Validate tenant
            if user.tenant_id != db_exec.get("tenant_id"):
                raise TenantAccessDeniedError(...)
            return db_exec

    raise ResourceNotFoundError(...)
```

#### 4. list_executions Endpoint is Synchronous

**Severity:** Medium
**Location:** `src/main.py` line 977

**Description:** Same issue as above - sync function that only uses in-memory store.

**Recommendation:** Change to async and add database query support.

#### 5. Invalid Agent Type Silently Accepted

**Severity:** Medium
**Location:** `src/main.py` lines 749-775

**Description:** When an invalid agent type is provided, the request is accepted and starts running, but fails in the background task. The error is logged but the user only sees `status: failed` later.

**Impact:** Poor user experience; validation should happen upfront.

**Recommendation:** Add validation in the endpoint:
```python
VALID_AGENT_TYPES = {"farm_advisor", "research", "planner"}

if agent_request.agent_type not in VALID_AGENT_TYPES:
    raise ValueError(f"Invalid agent_type: {agent_request.agent_type}. Must be one of: {VALID_AGENT_TYPES}")
```

#### 6. Quick Analysis Returns Mock Data

**Severity:** Medium
**Location:** `src/main.py` lines 1025-1057

**Description:** The `quick_analyze` endpoint returns hardcoded mock data instead of actual analysis.

**Impact:** Feature doesn't provide real value.

**Recommendation:** Integrate with actual analysis services or remove endpoint until implemented.

### Low Issues

#### 7. Redis Cache Missing in list_executions

**Severity:** Low
**Location:** `src/main.py` line 977

**Description:** The `list_executions` endpoint doesn't use Redis caching, while `get_execution_status` does.

**Recommendation:** Add caching for frequently accessed execution lists.

#### 8. Missing Pagination in list_executions

**Severity:** Low
**Location:** `src/main.py` line 977

**Description:** The endpoint has `limit` but no `offset` parameter for proper pagination.

**Recommendation:** Add `offset` parameter:
```python
offset: int = Query(0, ge=0),
```

#### 9. Coverage Configuration Excludes db.py

**Severity:** Low
**Location:** `.coveragerc`

**Description:** Database module is excluded from coverage, but it contains critical persistence logic.

**Recommendation:** Remove `src/db.py` from coverage exclusions and add tests.

### Security Considerations

#### 10. Tenant ID Validation Timing

**Severity:** Low
**Location:** `src/main.py` lines 699, 893-896, etc.

**Description:** Tenant validation happens after execution lookup. If execution doesn't exist, a generic 404 is returned. An attacker could potentially enumerate execution IDs.

**Recommendation:** Consider returning same error for both "not found" and "wrong tenant" cases:
```python
if execution_id not in executions or executions[execution_id].tenant_id != user.tenant_id:
    raise ResourceNotFoundError(...)
```

### Performance Recommendations

#### 11. Add Execution Cleanup Job

**Description:** In-memory executions dict grows unbounded. Old completed executions should be cleaned up.

**Recommendation:** Add a background cleanup task:
```python
async def cleanup_old_executions():
    cutoff = datetime.utcnow() - timedelta(hours=24)
    to_remove = [
        eid for eid, e in executions.items()
        if e.status in ["completed", "failed", "cancelled"]
        and e.completed_at and e.completed_at < cutoff
    ]
    for eid in to_remove:
        del executions[eid]
```

#### 12. Add Connection Pool Health Checks

**Description:** Service doesn't verify database pool health during readiness check.

**Recommendation:** Add pool health verification:
```python
if _use_database():
    try:
        await db.get_pool().fetchval("SELECT 1")
    except Exception:
        return {"status": "degraded", "database": False, ...}
```

### Documentation Improvements

#### 13. Add API Versioning Strategy

**Description:** Service uses `/api/v1/` but there's no documentation on versioning strategy.

**Recommendation:** Document in README:
- How breaking changes will be handled
- Deprecation policy
- Multiple version support timeline

#### 14. Add OpenTelemetry Tracing

**Description:** Service has structured logging but no distributed tracing integration.

**Recommendation:** Add OpenTelemetry instrumentation for:
- HTTP requests
- Database queries
- NATS publishing
- Agent execution spans

---

## Summary

The AI Agents Service is a well-structured microservice that provides a powerful agent orchestration framework. The main areas requiring attention are:

1. **Critical**: Database persistence is not used for execution updates
2. **Critical**: NATS events are not published despite being defined
3. **Medium**: Several endpoints are synchronous when they should be async
4. **Medium**: Quick analysis returns mock data

Once these issues are addressed, the service will provide reliable, persistent, event-driven AI agent orchestration for the SAHOOL platform.

---

## File Locations

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/ai-agents-service/src/main.py` | Main FastAPI application |
| `/home/user/sahool-unified-v15-idp/apps/services/ai-agents-service/src/db.py` | Database layer |
| `/home/user/sahool-unified-v15-idp/apps/services/ai-agents-service/requirements.txt` | Python dependencies |
| `/home/user/sahool-unified-v15-idp/apps/services/ai-agents-service/Dockerfile` | Container definition |
| `/home/user/sahool-unified-v15-idp/apps/services/ai-agents-service/migrations/001_create_agent_executions.sql` | Database migration |
| `/home/user/sahool-unified-v15-idp/shared/ai/agents/` | Agent implementations |
| `/home/user/sahool-unified-v15-idp/shared/events/contracts.py` | Event schemas |
| `/home/user/sahool-unified-v15-idp/governance/services.yaml` | Service registry |

---

_Last Updated: January 2026_
_Analysis performed by Claude_
