# Claude Code Integration Guide | دليل تكامل Claude Code مع منصة سهول

**Version**: 16.0.0
**Platform**: SAHOOL National Agricultural Intelligence Platform
**Last Updated**: March 2026

---

## 1. Overview | نظرة عامة

Claude Code serves as the primary AI-assisted development interface for the SAHOOL platform. It integrates deeply with the platform's offline-first architecture, 72 microservices, and agricultural domain intelligence to accelerate development, debugging, and operations across the entire stack.

Claude Code leverages three key integration points within the SAHOOL repository:

- **CLAUDE.md** (root configuration): A 112 KB context file that provides Claude Code with full architectural awareness of the platform, including service maps, conventions, and domain knowledge.
- **AI Skills** (`.claude/skills/`): Reusable skill modules for context engineering, crop advisory, farm documentation, and development workflows.
- **MCP Server** (`apps/services/mcp-server/`): Model Context Protocol server exposing SAHOOL-specific tools and data sources to Claude Code at runtime.

Together, these allow Claude Code to navigate the codebase with full understanding of service boundaries, event flows, database schemas, and agricultural domain semantics.

---

## 2. CLAUDE.md Configuration | تكوين ملف CLAUDE.md

### Purpose and Structure | الغرض والهيكل

The root `CLAUDE.md` file is the single most important configuration artifact for Claude Code integration. At approximately 112 KB, it encodes:

- **Repository structure**: Complete directory tree with descriptions for all 72 services, 27 npm workspaces, and 80 shared Python modules.
- **Technology stack**: Exact versions for FastAPI, NestJS, Flutter, PostgreSQL, NATS, Redis, and all infrastructure components.
- **Event architecture**: 4-layer event system (Acquisition, Intelligence, Decision, Business) with NATS subject patterns.
- **API conventions**: Health endpoints, versioning, rate limiting tiers, unified contracts.
- **Development commands**: All `make` targets, Docker Compose profiles, and testing commands.
- **Service registry**: Ports, types, and descriptions for every active and deprecated service.
- **Domain knowledge**: Agricultural integrations (NDVI, AraBERT, AgML, CrewAI agents).

### How Claude Code Uses It | كيف يستخدمه Claude Code

Claude Code reads `CLAUDE.md` at the start of every session. This provides:

1. **Architectural context**: Claude Code knows that `field-management-service` runs on port 3000 as a NestJS service, while `advisory-service` runs on port 8093 as a Python FastAPI service.
2. **Convention enforcement**: Claude Code follows the project's established patterns for health endpoints, error handling, authentication, and structured logging.
3. **Command awareness**: Claude Code can suggest and execute the correct `make` targets for building, testing, and deploying services.
4. **Deprecation awareness**: Claude Code avoids referencing archived services and suggests their active replacements.

### Best Practices for Maintaining CLAUDE.md | أفضل الممارسات للصيانة

- **Update on service changes**: When adding, removing, or modifying a service, update the corresponding section in `CLAUDE.md`.
- **Keep versions current**: Bump version numbers when dependencies change (e.g., FastAPI, Flutter SDK).
- **Document new patterns**: If a new architectural pattern is introduced (e.g., a new event layer), add it with examples.
- **Avoid secrets**: Never include credentials, API keys, or connection strings with real passwords.
- **Test readability**: Ensure tables render correctly and code blocks use proper syntax highlighting.
- **Section ordering**: Maintain the existing section order. Claude Code relies on consistent structure for efficient context retrieval.

---

## 3. AI Skills System | نظام المهارات الذكية

### Directory Structure | هيكل المجلدات

```
.claude/skills/
├── context-engineering/        # Context optimization modules
│   ├── memory.md              # Farm history & persistent memory
│   ├── compression.md         # Token-efficient data compression
│   └── evaluation.md          # LLM-as-Judge advisory quality assessment
├── sahool/                    # SAHOOL domain-specific skills
│   ├── crop-advisor.md        # Crop advisory & recommendations
│   └── farm-documentation.md  # Field & farm knowledge base
├── obsidian/                  # Documentation generation
│   ├── markdown.md            # Obsidian markdown formatting
│   └── canvas.md              # Canvas-based knowledge graphs
└── development/               # Development workflow skills (extensible)
```

### How Skills Are Invoked | كيفية استدعاء المهارات

Skills are invoked within Claude Code sessions either explicitly by the developer or automatically when Claude Code identifies a matching task context:

```bash
# Explicit invocation
claude code --skill crop-advisor --context "Field-003 wheat yellowing"

# Evaluate advisory quality
claude code --skill evaluate --advisory "irrigation_recommendation_001"

# Compress farm data for token efficiency
claude code --skill compress --level 2 --input "farm_sensor_data.json"

# Generate Obsidian-compatible farm documentation
claude code --skill farm-documentation --field "FIELD-003" --format obsidian
```

### Creating Custom Skills | إنشاء مهارات مخصصة

To add a new skill:

1. Create a Markdown file in the appropriate subdirectory under `.claude/skills/`.
2. Define the skill's purpose, input schema, output format, and examples.
3. Include bilingual (Arabic/English) descriptions where applicable.
4. Reference relevant shared modules (e.g., `shared/irrigation/`, `shared/pest_scouting/`).

Example skill file structure:

```markdown
# Skill: Irrigation Scheduler | جدولة الري

## Purpose
Generate optimized irrigation schedules based on field sensors, weather, and crop stage.

## Inputs
- field_id: Field identifier
- crop_stage: Current growth stage
- soil_moisture: Current SM reading (%)
- weather_forecast: 72-hour forecast data

## Output Format
YAML-structured schedule with timing, volume, and method.

## Examples
[Include 2-3 worked examples with bilingual output]
```

### Skill Categories | فئات المهارات

| Category | Directory | Purpose |
|----------|-----------|---------|
| Context Engineering | `context-engineering/` | Token compression, memory management, evaluation rubrics |
| Domain Advisory | `sahool/` | Crop recommendations, pest management, irrigation scheduling |
| Documentation | `obsidian/` | Markdown formatting, knowledge graph generation |
| Development | `development/` | Code generation, testing, CI/CD assistance |

---

## 4. MCP Integration | تكامل بروتوكول سياق النموذج

### Connection to SAHOOL MCP Server | الاتصال بخادم MCP

The SAHOOL MCP server runs on port **8201** and exposes platform-specific tools and data sources to Claude Code via the Model Context Protocol.

```bash
# Start MCP server
make dev-mcp

# Test MCP server
make test-mcp
```

### Available MCP Tools | الأدوات المتاحة

The MCP server provides Claude Code with access to:

- **Field data queries**: Retrieve field boundaries, crop history, and sensor readings.
- **Service health checks**: Query `/healthz` and `/readyz` across all 72 services.
- **Event inspection**: View recent NATS events by subject pattern.
- **Database queries**: Execute read-only queries against PostgreSQL with PostGIS.
- **Knowledge base search**: Query the agricultural knowledge base (91 documents in `docs/knowledge-base/`).

### Configuration | التكوين

Add the SAHOOL MCP server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "sahool": {
      "command": "python",
      "args": ["-m", "apps.services.mcp-server.src.main"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:6432/sahool",
        "NATS_URL": "nats://localhost:4222",
        "REDIS_URL": "redis://localhost:6379",
        "MCP_PORT": "8201"
      }
    }
  }
}
```

Ensure the infrastructure is running (`make infra-up`) before connecting.

---

## 5. Event-Driven Development with Claude | التطوير المبني على الأحداث

### 4-Layer Event Architecture | معمارية الأحداث ذات الطبقات الأربع

SAHOOL uses NATS with JetStream for its event-driven architecture. Claude Code understands all four layers:

| Layer | Purpose | Example Services |
|-------|---------|-----------------|
| **Acquisition** | Data ingestion and normalization | iot-service, weather-service, edge-orchestrator |
| **Intelligence** | Feature extraction and AI processing | indicators-service, yolo26-vision-service, terrain-core |
| **Decision** | Recommendations and planning | advisory-service, irrigation-smart, yield-prediction |
| **Business** | User-facing operations | notification-service, marketplace-service, chat-service |

### Event Subject Patterns | أنماط موضوعات الأحداث

```python
# Base pattern
"sahool.{domain}.{action}"              # e.g., sahool.field.created

# Tenant-scoped pattern (preferred)
"sahool.tenant.{tenant_id}.{domain}.{action}"  # via get_tenant_subject()

# Inline tenant pattern (some services)
"sahool.{tenant_id}.{domain}.{action}"
```

### Publishing Events | نشر الأحداث

```python
from shared.events.subjects import SAHOOL_FIELD_CREATED, get_tenant_subject

# Simple publish
await app.state.nc.publish(
    SAHOOL_FIELD_CREATED,
    json.dumps({"field_id": field_id, "tenant_id": tenant_id}).encode()
)

# Tenant-scoped publish
subject = get_tenant_subject(tenant_id, "field", "created")
await app.state.nc.publish(subject, payload)
```

When Claude Code generates new event handlers or publishers, it follows these patterns and imports subject constants from `shared/events/subjects.py` rather than using hardcoded strings.

---

## 6. Multi-Service Development | التطوير متعدد الخدمات

### Working Across 72 Microservices | العمل عبر 72 خدمة مصغرة

Claude Code navigates the service landscape using the unified contracts defined in `packages/shared-types/src/contracts/`:

```typescript
// Always import from contracts - never hardcode ports
import { SERVICE_PORTS, AUTH_ENDPOINTS, buildUrl } from "@sahool/shared-types/contracts";

// Correct
const fieldServiceUrl = `http://localhost:${SERVICE_PORTS.FIELD_MANAGEMENT}`;

// Incorrect - do not do this
const fieldServiceUrl = "http://localhost:3000";  // hardcoded port
```

### Service Port Conventions | اتفاقيات منافذ الخدمات

- **Node.js services**: Ports 3000-3025
- **Python services**: Ports 8081-8270
- **Infrastructure**: Standard ports (5432 PostgreSQL, 6379 Redis, 4222 NATS)

### Docker Compose Profiles | ملفات تعريف Docker Compose

```bash
make dev                    # Full stack (all active services)
make dev-starter           # Starter package only
make dev-professional      # Professional package
make dev-enterprise        # All enterprise services
make dev-vision            # Vision services (yolo26-vision-service)
make dev-terrain           # Terrain services (terrain-core, hydrology, leveling)
make dev-edge              # Edge orchestrator service
make dev-ai                # AI services
make dev-agents            # Agent services
make infra-up              # Infrastructure only (postgres, redis, nats, kong)

# Deprecated services (testing only)
docker-compose --profile deprecated up
```

---

## 7. Database Operations | عمليات قاعدة البيانات

### PostgreSQL + PostGIS | قاعدة البيانات الجغرافية

All services connect through PgBouncer (port 6432) in transaction mode with a 250 max connection pool. PostGIS 3.4 enables geospatial queries for field boundaries, NDVI analysis, and terrain operations.

```bash
make db-shell              # Connect to PostgreSQL
make db-migrate            # Run Prisma migrations
make db-seed              # Seed sample data
make db-backup            # Create backup
make db-reset             # Reset (WARNING: deletes data)
```

### Prisma for Node.js Services | Prisma للخدمات Node.js

```bash
npx prisma generate        # Generate client
npx prisma migrate deploy  # Run migrations
npx prisma studio          # GUI browser
```

### asyncpg for Python Services | asyncpg للخدمات Python

```python
# Standard connection pattern
app.state.db_pool = await asyncpg.create_pool(
    os.getenv("DATABASE_URL"),
    min_size=2,
    max_size=10
)

# Query with PostGIS
row = await app.state.db_pool.fetchrow(
    "SELECT ST_AsGeoJSON(boundary) FROM fields WHERE id = $1",
    field_id
)
```

Claude Code generates database code following these patterns and ensures all queries use parameterized inputs to prevent SQL injection.

---

## 8. Testing Integration | تكامل الاختبارات

### 19 Test Categories | 19 فئة اختبار

| Category | Directory | Command |
|----------|-----------|---------|
| Unit | `tests/unit/` | `make test-unit` |
| Integration | `tests/integration/` | `make test-integration` |
| Smoke | `tests/smoke/` | `pytest tests/smoke/` |
| E2E | `tests/e2e/` | `pytest tests/e2e/` |
| Load | `tests/load/` | k6 / Locust |
| Security | `tests/security/` | `pytest tests/security/` |
| Frontend | `tests/frontend/` | `npm run test` |
| Container | `tests/container/` | `make test-docker` |
| Guardrails | `tests/guardrails/` | `pytest tests/guardrails/` |
| A2A | `tests/a2a/` | Agent-to-Agent protocol tests |

### Test Markers | علامات الاختبار

```python
@pytest.mark.unit           # Fast, no I/O - always run
@pytest.mark.integration    # Requires database/NATS
@pytest.mark.smoke          # Import verification only
@pytest.mark.slow           # Long-running tests
```

### Coverage Requirements | متطلبات التغطية

- **Current minimum**: 5% (enforced in CI via `fail_under = 5` in `pyproject.toml`)
- **Target**: Incrementally raising
- **Reports**: `coverage.xml` and `coverage_html/`

When Claude Code generates new code, it also generates corresponding test files using the appropriate markers and following the factory pattern from `tests/factories/`.

---

## 9. CI/CD Integration | تكامل التكامل والنشر المستمر

### 54 GitHub Actions Workflows | 54 سير عمل GitHub Actions

Claude Code assists with CI/CD in several ways:

- **Diagnosing failures**: When a CI workflow fails, Claude Code can read the workflow definition, understand the failure context, and suggest fixes.
- **Generating workflow updates**: Adding new services requires updates to CI workflows. Claude Code generates workflow steps following existing patterns.
- **Security scanning**: Claude Code ensures code passes CodeQL, Bandit, Semgrep, Trivy, and Gitleaks checks before suggesting commits.

### Key Workflow Categories | فئات سير العمل الرئيسية

| Category | Workflows | Examples |
|----------|-----------|---------|
| Core CI/CD | 5 | `ci.yml`, `test.yml`, `release.yml` |
| Specialized CI | 5 | `ci-yolo26-vision.yml`, `ci-terrain-services.yml` |
| Deployment | 5 | `cd-production.yml`, `canary-deploy.yml` |
| Security | 5 | `security-checks.yml`, `codeql-analysis.yml` |
| Governance | 5 | `event-contracts-guard.yml`, `api-contracts-guard.yml` |
| Quality | 3 | `quality-gates.yml`, `stability-gates.yml` |

### ArgoCD Deployment | نشر ArgoCD

SAHOOL uses ArgoCD with 18 application definitions in `gitops/`. Claude Code understands the GitOps flow:

1. Code merges to `main` or `develop`
2. Docker images build and push via GitHub Actions
3. ArgoCD detects changes in `gitops/` manifests
4. Rolling deployment to Kubernetes cluster

---

## 10. Security Considerations | اعتبارات الأمان

### Rules Claude Code Follows | القواعد التي يتبعها Claude Code

**Never do**:
- Commit `.env` files, API keys, or credentials
- Use hardcoded passwords or connection strings
- Skip authentication checks in endpoint handlers
- Disable TLS/SSL in any configuration
- Run containers as root
- Use `--no-verify` for git hooks

**Always do**:
- Use environment variables for all secrets
- Follow RBAC patterns via `shared/auth/dependencies.py`
- Validate all user input with Pydantic models
- Use parameterized queries (never string concatenation for SQL)
- Enable rate limiting on public endpoints
- Include authentication dependencies on protected routes

### Certificate Pinning (Mobile) | تثبيت الشهادات للموبايل

The Flutter apps use 3-tier certificate pinning:

- **Production**: `api.sahool.app`, `ws.sahool.app`, `*.sahool.io`
- **Staging**: Separate certificate set
- **Development**: Local development certificates

Claude Code never modifies pinning configuration without explicit instruction.

### Security Scanning | المسح الأمني

```bash
make secrets-scan          # Gitleaks secret detection
make deps-audit            # Dependency security audit
```

---

## 11. Monitoring and Observability | المراقبة والرصد

### Prometheus Metrics | مقاييس Prometheus

Services expose metrics at `/metrics` endpoints. Claude Code generates metrics following the existing patterns:

```python
from shared.monitoring import prometheus_metrics

# Counter
request_counter = prometheus_metrics.counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# Histogram
latency_histogram = prometheus_metrics.histogram(
    "request_duration_seconds",
    "Request latency",
    ["service", "endpoint"]
)
```

### Grafana Dashboards | لوحات Grafana

Four pre-built dashboards in `infrastructure/monitoring/grafana/dashboards/`:

| Dashboard | Purpose |
|-----------|---------|
| Agricultural Insights | Crop health, NDVI trends, irrigation efficiency |
| Disaster Recovery | DR status, RTO/RPO metrics |
| SLO Dashboard | Service level objectives tracking |
| AI Skills | Skill invocation metrics, quality scores |

```bash
make monitoring-up         # Start Prometheus/Grafana stack
make monitoring-down       # Stop monitoring
make monitoring-logs       # View monitoring logs
```

### OpenTelemetry Tracing | تتبع OpenTelemetry

Distributed tracing via Jaeger and OpenTelemetry Collector. Claude Code ensures new services include tracing middleware:

```python
from shared.observability import setup_tracing

# In service lifespan
setup_tracing(app, service_name="my-service")
```

---

## 12. Troubleshooting Common Issues | استكشاف المشكلات الشائعة وإصلاحها

### Service Won't Start | الخدمة لا تبدأ

1. Check infrastructure is running: `make health`
2. Verify environment variables: `make status`
3. Check port conflicts: `make ps`
4. Review logs: `docker compose logs -f [service_name]`

### Database Connection Failures | فشل الاتصال بقاعدة البيانات

- Ensure PgBouncer is running (port 6432, not 5432 directly)
- Verify `DATABASE_URL` includes `?sslmode=require` for TLS
- Check connection pool limits (250 max via PgBouncer)
- Run `make db-shell` to test direct connectivity

### NATS Event Issues | مشكلات أحداث NATS

- Verify NATS is running: `make health` or check port 4222
- Check subject patterns match the 4-layer convention
- Inspect Dead Letter Queue: `docker compose -f docker/docker-compose.dlq.yml up`
- Ensure `tenant_id` is a valid UUID from the JWT `tid` claim

### CI Pipeline Failures | فشل خط أنابيب CI

- **Lint failures**: Run `make lint` locally, then `make fmt` to auto-fix
- **Type errors**: Run `npm run typecheck` for Node.js or `mypy` for Python
- **Test failures**: Check `ENVIRONMENT=test` and empty `DATABASE_URL` for unit tests
- **Security scan failures**: Run `make secrets-scan` and `make deps-audit`
- **Contract guard failures**: Ensure `CONTRACT_VERSION` is bumped in `packages/shared-types/src/contracts/index.ts`

### Docker Build Failures | فشل بناء Docker

- **Pip timeout**: The platform uses 3-tier mirror fallback (PyPI, Aliyun, Tencent). If all fail, check network connectivity.
- **NPM timeout**: Falls back from `registry.npmmirror.com` to `registry.npmjs.org`.
- **GPU services**: `yolo26-vision-service` requires NVIDIA CUDA 12.1. Use the `cpu-only` stage for development without GPU.
- **Constraint conflicts**: Check `constraints.txt` and `docker/constraints-ai.txt` for version pin conflicts.

### Flutter / Mobile Issues | مشكلات Flutter والموبايل

```bash
make mobile-clean          # Clean build artifacts
make mobile-deps           # Reinstall dependencies
make mobile-codegen        # Regenerate code (Drift, Riverpod)
make mobile-analyze        # Run Dart analyzer
```

- **SQLCipher errors**: Ensure `flutter_secure_storage` is properly configured for the target platform.
- **Certificate pinning failures**: Check that development certificates are installed for local testing.
- **Sync conflicts**: Review `shared/mobile_sync/` conflict resolution logic (ETag-based, schema v4).

### Auto-Fix Engine | محرك الإصلاح التلقائي

For automated code diagnostics and fixing:

```bash
make fixops               # Preview issues (dry-run)
make fixops-run           # Apply safe fixes
make fixops-comprehensive # Fix all issues including refactoring
make fixops-json          # JSON output for CI/CD integration
```

The Auto-Fix Engine supports Ruff, ESLint, Mypy, Bandit, and Dart Analyze with four fix strategies: MINIMAL, SAFE, COMPREHENSIVE, and REFACTOR.

---

_This guide is maintained alongside the root CLAUDE.md. For the complete platform reference, see `/CLAUDE.md`._
_يتم صيانة هذا الدليل جنبا إلى جنب مع ملف CLAUDE.md الجذري. للمرجع الكامل للمنصة، راجع `/CLAUDE.md`._
