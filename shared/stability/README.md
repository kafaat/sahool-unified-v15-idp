# shared/stability - Platform Stability Framework

إطار استقرار منصة سهول

A comprehensive stability framework for SAHOOL microservices that prevents configuration drift, detects anomalies, and auto-remediates common failure patterns. Provides six capabilities that replace fragmented per-service implementations with consistent, platform-wide stability patterns.

## File Structure

```
shared/stability/
├── __init__.py           # Package exports (v1.0.0)
├── context.py            # UnifiedContextMiddleware + RequestContext
├── config_policy.py      # ConfigPolicy / ConfigPolicyEngine
├── contracts.py          # ContractValidator (API + event schema)
├── drift_detector.py     # DriftDetector (lightweight, service-embedded)
├── remediation.py        # RemediationEngine
└── observability.py      # StabilityHealthCheck + unified metrics
```

## Six Core Capabilities

### 1. Unified Request Context (`context.py`)

**`RequestContext`** - Single object consolidating all request metadata:
- `tenant_id` (from JWT `tid` claim or `X-Tenant-ID` header)
- `correlation_id` (from `X-Correlation-ID` / `X-Request-ID` or auto-generated UUID)
- `trace_context` (W3C `traceparent` / OpenTelemetry)
- `user_id`, `roles`
- `service_name`, `service_version`

**`UnifiedContextMiddleware`** - FastAPI/Starlette middleware:
- Replaces 3+ separate middleware (tenant, correlation, trace) with one
- Auto-propagates context to downstream HTTP calls
- `enrich_event(event)` - Stamps events with current context

```python
from shared.stability.context import UnifiedContextMiddleware, get_request_context

app.add_middleware(
    UnifiedContextMiddleware,
    service_name="field-management-service",
    service_version="16.0.0",
    require_tenant=False,
)

@app.get("/api/v1/fields")
async def list_fields():
    ctx = get_request_context()
    logger.info("listing", tenant_id=ctx.tenant_id, correlation_id=ctx.correlation_id)
    headers = ctx.to_propagation_headers()  # For downstream calls
```

### 2. Config Policy (`config_policy.py`)

**`ConfigPolicy`** - Policy-as-code environment validation:
- Validates required environment variables are set and non-empty
- Enforces format constraints (JWT secret minimum length, valid URLs, etc.)
- Supports `CRITICAL` / `WARNING` / `INFO` policy levels

**`ConfigPolicyEngine`** - Evaluates a list of `ConfigPolicy` rules:
- `validate()` → `PolicyReport` with violations and remediation hints
- Run at service startup to fail-fast on misconfiguration

### 3. Contract Validation (`contracts.py`)

**`ContractValidator`** - Two-level contract verification:

*Static (CI-time):*
- Compare OpenAPI schemas against golden files
- Validate event schemas against `governance/events/schemas/`

*Runtime:*
- `validate_health_contract(service_url)` - Probe `/healthz` + `/readyz` format
- `validate_event_contract(subject, payload)` - Check event envelope structure
- `validate_api_contract(endpoint, schema)` - Response schema conformance

**`ContractSeverity`**: `BREAKING`, `WARNING`, `INFO`
**`ContractType`**: `EVENT_SCHEMA`, `API_ENDPOINT`, `HEALTH_ENDPOINT`, `MIGRATION`

### 4. Drift Detection (`drift_detector.py`)

**`DriftDetector`** - Lightweight, service-embedded detector (complements `shared/drift_detection/` for per-service use):
- Config drift: env var changes since last check
- Schema drift: migration hash comparison
- API drift: endpoint signature changes

Returns `DriftReport` with severity-tagged `DriftResult` items.

### 5. Auto-Remediation (`remediation.py`)

**`RemediationEngine`** - Automated fix execution:
- Restart stale connections (DB pool, NATS)
- Clear invalid cache entries
- Re-apply missing configuration defaults
- All actions are logged with before/after state for audit trail

### 6. Observability Kit (`observability.py`)

**`StabilityHealthCheck`** - Unified health aggregator:
- Checks: database connectivity, NATS connection, Redis ping, disk space
- Returns structured `HealthStatus` for `/healthz` and `/readyz` endpoints
- Emits Prometheus metrics: `sahool_stability_health_gauge`, `sahool_context_propagation_total`

## Usage Example

```python
from fastapi import FastAPI
from shared.stability.context import UnifiedContextMiddleware, get_request_context
from shared.stability.contracts import ContractValidator
from shared.stability.observability import StabilityHealthCheck

app = FastAPI()

# 1. Add unified context middleware
app.add_middleware(UnifiedContextMiddleware, service_name="my-service", service_version="16.0.0")

# 2. Config policy at startup
from shared.stability.config_policy import ConfigPolicyEngine, ConfigPolicy
engine = ConfigPolicyEngine([
    ConfigPolicy("DATABASE_URL", required=True, level="CRITICAL"),
    ConfigPolicy("JWT_SECRET_KEY", required=True, min_length=32, level="CRITICAL"),
    ConfigPolicy("NATS_URL", required=False, level="WARNING"),
])
report = engine.validate()
if report.has_critical_violations:
    raise SystemExit(str(report))

# 3. Health check
checker = StabilityHealthCheck(db_pool=pool, nats_client=nc)

@app.get("/healthz")
async def health():
    return await checker.liveness()

@app.get("/readyz")
async def ready():
    return await checker.readiness()

# 4. Contract validation (startup or CI)
validator = ContractValidator()
contract_report = await validator.validate_health_contract("http://other-service:8090")
```

## Notes

- `shared/stability` provides lightweight, embeddable patterns. For platform-wide drift detection with database persistence, use `shared/drift_detection/`.
- `UnifiedContextMiddleware` should replace all existing per-service tenant/correlation/trace middleware.
- The `DriftDetector` in this module is suitable for per-service embedding. The `DriftDetectionEngine` in `shared/drift_detection/` is for platform-wide orchestrated scanning.
- All remediation actions produce structured log entries compatible with `shared/audit_trail/`.
