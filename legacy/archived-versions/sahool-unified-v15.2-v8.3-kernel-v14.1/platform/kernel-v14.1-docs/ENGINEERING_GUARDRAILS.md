# 🔒 SAHOOL Engineering Guardrails

> القواعد الحاكمة للتطوير - لا يُسمح بتجاوزها

## 🚫 Forbidden Practices

### Architecture Violations
```
❌ Direct HTTP between services
   → Use Events instead

❌ Event without registered consumer
   → Every event must have at least one consumer

❌ Business logic in Platform Core
   → Core services are infrastructure only

❌ Schema-less events
   → All events must be registered in Schema Registry

❌ Service creation without sahool-gen
   → Use CLI: ./tools/sahool-gen/scripts/create-service.sh

❌ Shared database between services
   → Each service owns its data

❌ UI endpoints in Signal Producers (Layer 2)
   → Layer 2 services produce events only
```

### Code Violations
```
❌ Non-idempotent event consumers
   → All consumers must handle duplicates

❌ Service without health check
   → All services must have /healthz endpoint

❌ Hardcoded configuration
   → Use environment variables

❌ Missing error handling
   → All external calls must have try/catch

❌ Synchronous external API calls without timeout
   → Always set timeouts
```

## ✅ Required Practices

### Architecture Requirements
```
✅ Event → Schema Registry mandatory
   Before publishing any event, register its schema

✅ Consumer → Idempotent mandatory
   Use idempotency_keys table for all consumers

✅ Service → Healthz mandatory
   GET /healthz returning {"status": "healthy"}

✅ New Service → sahool-gen only
   Never create service folders manually

✅ Service Design Card → Required
   Every service must have a design card before coding
```

### Code Requirements
```
✅ Type hints in Python
   All functions must have type annotations

✅ Input validation
   Use Pydantic models for all inputs

✅ Structured logging
   Use JSON logging format

✅ Metrics exposure
   Prometheus metrics on /metrics

✅ Graceful shutdown
   Handle SIGTERM properly
```

## 🏗️ Layer Rules

### Layer 1: Platform Core
```yaml
Services: auth, gateway, schema-registry, process-manager, observability
Rules:
  - NO business logic
  - NO domain-specific code
  - Changes require architecture review
  - Locked after initial setup
```

### Layer 2: Signal Producers
```yaml
Services: astro-agri, weather, ndvi, soil, image-diagnosis
Rules:
  - Produce events only
  - NO decision logic
  - NO direct user interaction
  - NO public API endpoints
  - Internal APIs only
```

### Layer 3: Decision Services
```yaml
Services: disease-risk, crop-lifecycle, irrigation-engine, advisor-core
Rules:
  - Consume signals, produce decisions
  - Complex logic allowed
  - NO direct user interaction
  - Must document decision criteria
```

### Layer 4: Execution Services
```yaml
Services: tasks, alerts, equipment
Rules:
  - Execute decisions
  - User-facing allowed
  - Must be reversible when possible
  - Audit trail required
```

## 📝 Service Design Card Template

Every service MUST have a design card before coding:

```yaml
Service:
  name: <service-name>
  layer: <signal-producer|decision|execution>
  version: 1.0.0

Ownership:
  team: <team-name>
  sla: <best-effort|standard|critical>

Produces:
  - <event.name.1>
  - <event.name.2>

Consumes:
  - <event.name.1>
  - <event.name.2>

Triggers:
  - <saga-name>

Data:
  tables:
    - <table_name>

Non-Goals:
  - <what this service does NOT do>

Risks:
  - <identified risks>
```

## 🔄 Event Naming Convention

```
<domain>.<entity>.<action>

Examples:
- astro.star.rising
- weather.anomaly.detected
- crop.stage.changed
- disease.risk.calculated
- irrigation.schedule.proposed
- task.created
- alert.sent
```

## 📊 Database Rules

### Naming
```sql
-- Tables: snake_case, plural
CREATE TABLE agricultural_stars (...);

-- Columns: snake_case
created_at, updated_at, field_id

-- Indexes: idx_<table>_<columns>
CREATE INDEX idx_stars_region ON agricultural_stars(region);

-- Foreign Keys: fk_<table>_<referenced_table>
CONSTRAINT fk_proverbs_stars FOREIGN KEY (star_id) REFERENCES agricultural_stars(id)
```

### Required Columns
```sql
-- Every table must have:
id          VARCHAR(64) PRIMARY KEY  -- ULID/UUID
created_at  TIMESTAMP WITH TIME ZONE NOT NULL
updated_at  TIMESTAMP WITH TIME ZONE
tenant_id   VARCHAR(64) NOT NULL     -- Multi-tenancy
```

## 🔐 Security Rules

```
✅ All inter-service communication over mTLS
✅ API keys rotated every 90 days
✅ Secrets in environment variables, never in code
✅ Input sanitization on all user inputs
✅ Rate limiting on all public endpoints
✅ Audit logging for sensitive operations
```

## 📈 Monitoring Requirements

```yaml
Every service must expose:
  - /healthz     → Health check
  - /readyz      → Readiness check
  - /metrics     → Prometheus metrics

Required metrics:
  - request_duration_seconds
  - request_total
  - error_total
  - event_published_total
  - event_consumed_total
```

## 🔄 PR Checklist

Before merging any PR:

```markdown
## Architecture
- [ ] No direct HTTP calls between services
- [ ] Events registered in Schema Registry
- [ ] Service Design Card updated (if new service)

## Code Quality
- [ ] All functions have type hints
- [ ] Input validation with Pydantic
- [ ] Error handling complete
- [ ] Tests written and passing

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] CHANGELOG entry added

## Infrastructure
- [ ] Migrations included
- [ ] Docker config updated (if needed)
- [ ] Environment variables documented
```

## 🚨 Violation Consequences

| Severity | Violation | Consequence |
|----------|-----------|-------------|
| Critical | Direct HTTP between services | PR blocked |
| Critical | Schema-less event | PR blocked |
| High | Missing idempotency | PR blocked |
| High | No health check | Must fix in 24h |
| Medium | Missing tests | Must fix in 1 week |
| Low | Documentation gaps | Must fix in 2 weeks |

---

**Remember**: These rules exist to ensure platform stability and maintainability. When in doubt, ask before coding.
