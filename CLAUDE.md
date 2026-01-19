# CLAUDE.md - AI Assistant Guidelines for SAHOOL Platform

## Project Overview

SAHOOL is a **National Agricultural Intelligence Platform** - an offline-first agricultural operating system designed for low-connectivity environments in the Middle East. The platform provides real-time advisory, irrigation management, crop health monitoring (NDVI), and field operations management for smallholder farmers.

**Version**: 16.0.0
**Owner**: KAFAAT
**License**: Proprietary

### Key Differentiators

- **Offline-First Architecture**: Full functionality without internet connectivity
- **Geospatial Intelligence**: PostGIS-powered vector field rendering
- **AI-Driven Advisory**: Crop disease detection and fertilizer recommendations
- **Enterprise-Grade Security**: JWT authentication, RBAC, and audit logging
- **Event-Driven Architecture**: NATS-based messaging with 4-layer event architecture

---

## Repository Structure

```
sahool-unified-v15-idp/
├── apps/
│   ├── admin/                  # Admin portal (React)
│   ├── kernel/                 # Core backend modules (Python)
│   │   ├── analytics/          # Analytics processing
│   │   ├── common/             # Shared database, middleware, queue, monitoring
│   │   └── field_ops/          # Field operations logic
│   ├── mobile/                 # Flutter mobile apps
│   │   ├── sahool_field_app/   # Main field app
│   │   ├── lib/                # Core Flutter code
│   │   └── integration_test/   # Integration tests
│   ├── services/               # 57+ microservices (Python FastAPI & Node.js NestJS)
│   └── web/                    # Web dashboard (Next.js/React)
├── packages/                   # Shared packages (npm workspaces)
│   ├── shared-utils/           # Common utilities
│   ├── shared-ui/              # UI components
│   ├── shared-types/           # TypeScript types
│   ├── shared-hooks/           # React hooks
│   ├── shared-events/          # Event definitions
│   ├── shared-crypto/          # Cryptography utilities
│   ├── shared-db/              # Database utilities
│   ├── shared-audit/           # Audit logging
│   ├── nestjs-auth/            # NestJS auth module
│   ├── field-shared/           # Field domain types
│   ├── api-client/             # API client library
│   ├── design-system/          # Design system components
│   ├── mock-data/              # Test mock data
│   ├── i18n/                   # Internationalization
│   ├── tailwind-config/        # Tailwind configuration
│   ├── typescript-config/      # TypeScript configuration
│   ├── advisor/                # Advisory package
│   ├── field_suite/            # Field suite components
│   ├── kernel_domain/          # Kernel domain logic
│   ├── sahool-eo/              # Earth Observation (eo-learn integration)
│   ├── starter/                # Starter package config
│   ├── professional/           # Professional package config
│   └── enterprise/             # Enterprise package config
├── shared/                     # Python shared modules
│   ├── auth/                   # Authentication (JWT, 2FA, token revocation)
│   ├── cache/                  # Caching layer
│   ├── contracts/              # API contracts
│   ├── domain/                 # Domain models
│   ├── events/                 # Event definitions
│   ├── file_validation/        # File upload validation
│   ├── guardrails/             # Input guardrails
│   ├── libs/                   # Shared libraries
│   ├── mcp/                    # Model Context Protocol
│   ├── middleware/             # HTTP middleware
│   ├── monitoring/             # Prometheus metrics
│   ├── observability/          # Logging, tracing
│   ├── security/               # Security utilities
│   ├── secrets/                # Secrets management
│   ├── telemetry/              # OpenTelemetry
│   ├── a2a/                    # Agent-to-Agent communication
│   ├── ai/                     # AI utilities
│   ├── globalgap/              # GlobalGAP compliance
│   ├── versioning/             # API versioning utilities
│   └── python-lib/             # Python library utilities
├── config/                     # Configuration files
│   ├── certs/                  # TLS certificates
│   └── nats/                   # NATS configuration
├── docker/                     # Docker configurations
├── docs/                       # Technical documentation (178+ docs)
├── gitops/                     # ArgoCD applications
├── governance/                 # Security policies & service registry
├── helm/                       # Kubernetes Helm charts
├── idp/                        # Internal Developer Platform (Backstage)
├── infrastructure/             # IaC, monitoring, Terraform
├── tests/                      # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── smoke/                  # Smoke tests
│   ├── e2e/                    # End-to-end tests
│   ├── load/                   # Load tests (Locust)
│   ├── evaluation/             # AI agent evaluation
│   ├── guardrails/             # Input validation tests
│   ├── a2a/                    # Agent-to-Agent tests
│   ├── container/              # Container tests
│   ├── database/               # Database tests
│   ├── frontend/               # Frontend tests
│   ├── middleware/             # Middleware tests
│   ├── simulation/             # Simulation tests
│   └── golden-datasets/        # Golden dataset tests
└── scripts/                    # Utility scripts
```

---

## Technology Stack

### Backend Services

| Layer                  | Technology                                                            |
| ---------------------- | --------------------------------------------------------------------- |
| **Python Services**    | FastAPI 0.126.0, Tortoise ORM 0.21.7, asyncpg 0.30.0, Pydantic v2.10+ |
| **Node.js Services**   | NestJS, Prisma ORM, TypeScript 5.7.x                                  |
| **Database**           | PostgreSQL 16+ with PostGIS 3.4 (geospatial)                          |
| **Message Queue**      | NATS 2.x (event-driven architecture)                                  |
| **API Gateway**        | Kong (authentication, rate limiting)                                  |
| **Caching**            | Redis 7.x (sessions, rate limiting)                                   |
| **Connection Pooling** | PgBouncer (transaction mode, 250 max connections)                     |

### Mobile Application

| Layer                | Technology                             |
| -------------------- | -------------------------------------- |
| **Framework**        | Flutter 3.27.x (Dart >=3.2.0)          |
| **State Management** | Riverpod 2.6.x                         |
| **Local Database**   | Drift 2.24+ with SQLCipher (encrypted) |
| **Background Tasks** | Workmanager                            |
| **Maps**             | MapLibre GL, flutter_map               |
| **Network**          | Dio 5.x with certificate pinning       |

### Frontend (Web/Admin)

| Layer          | Technology                                    |
| -------------- | --------------------------------------------- |
| **Framework**  | Next.js / React with TypeScript               |
| **Testing**    | Vitest 3.x, React Testing Library, Playwright |
| **Build**      | Vite / Next.js                                |
| **Styling**    | Tailwind CSS                                  |
| **Monitoring** | Sentry                                        |

### Infrastructure

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| **Container**  | Docker, Kubernetes (K8s)                |
| **IaC**        | Terraform, Helm Charts                  |
| **CI/CD**      | GitHub Actions (35 workflows), Argo CD  |
| **Monitoring** | Prometheus, Grafana, OpenTelemetry      |
| **Secrets**    | HashiCorp Vault                         |

---

## Event Architecture (4-Layer)

The platform uses a 4-layer event architecture via NATS 2.x with JetStream:

| Layer            | Services                                                                              | Purpose                        |
| ---------------- | ------------------------------------------------------------------------------------- | ------------------------------ |
| **Acquisition**  | satellite-service, iot-service, weather-service, virtual-sensors, iot-gateway         | Data ingestion & normalization |
| **Intelligence** | indicators-service, lai-estimation, crop-intelligence-service, vegetation-analysis-service, ndvi-processor, field-intelligence, skills-service | Feature extraction & AI        |
| **Decision**     | crop-growth-model, advisory-service, irrigation-smart, yield-engine, yield-prediction, agro-advisor | Recommendations & planning     |
| **Business**     | notification-service, marketplace-service, billing-core, community-chat, task-service, equipment-service, ws-gateway | User-facing operations         |

### Event Subject Patterns

```
sahool.{tenant_id}.{domain}.{event_type}

# Examples:
sahool.tenant123.field.created
sahool.tenant123.field.updated
sahool.tenant123.crop.planted
sahool.tenant123.irrigation.scheduled
sahool.tenant123.advisory.generated
sahool.tenant123.alert.triggered
```

### Event Flow Example

```
[IoT Sensor] → iot-gateway → NATS
                               ↓
                    sahool.*.sensor.reading
                               ↓
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
      indicators-service  virtual-sensors  weather-service
              ↓                ↓                ↓
      sahool.*.ndvi.calculated  sahool.*.et.calculated
                               ↓
                    irrigation-smart
                               ↓
                    sahool.*.irrigation.recommendation
                               ↓
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
    notification-service   ws-gateway    advisory-service
              ↓                ↓                ↓
         [Push]           [WebSocket]      [Dashboard]
```

### JetStream Configuration

```yaml
# NATS JetStream streams
streams:
  - name: SAHOOL_EVENTS
    subjects: ["sahool.>"]
    retention: limits
    max_age: 7d
    max_bytes: 10GB
    replicas: 3

  - name: SAHOOL_ALERTS
    subjects: ["sahool.*.alert.>"]
    retention: workqueue
    max_deliver: 5
```

### Event Publishing Pattern

```python
# Python service event publishing
from shared.events import publish_event

await publish_event(
    subject=f"sahool.{tenant_id}.field.updated",
    data={
        "field_id": field_id,
        "changes": {"ndvi": 0.72},
        "timestamp": datetime.utcnow().isoformat()
    },
    headers={"correlation_id": request_id}
)
```

---

## Development Commands

### Docker / Infrastructure

```bash
# Start development environment
make dev                    # Full stack
make dev-starter           # Starter package only
make dev-professional      # Professional package
make dev-enterprise        # All enterprise services
make infra-up              # Infrastructure only (postgres, redis, nats, kong)

# Build
make build                 # Build all Docker images (parallel)
make build-python          # Build Python services only
make build-node            # Build Node.js services only

# Manage
make up                    # Start all services
make down                  # Stop all services
make down-volumes          # Stop and remove volumes
make restart               # Restart all services

# Logs
make logs                  # All service logs
make logs-service SERVICE=field_ops  # Specific service
```

### Database

```bash
make db-migrate            # Run migrations (Prisma)
make db-seed              # Seed with sample data
make db-reset             # Reset database (WARNING: deletes data)
make db-shell             # Connect to PostgreSQL
make db-backup            # Create database backup
```

### Testing

```bash
# Python tests
make test                  # Run all tests
make test-python          # Python tests only
make test-unit            # Unit tests
make test-integration     # Integration tests
make test-coverage        # With coverage report

# Node.js tests
make test-node            # Node.js tests
npm run test              # Vitest tests
npm run test:coverage     # With coverage

# Docker tests
make test-docker          # Run tests in Docker containers

# Flutter tests
flutter test              # Unit tests
flutter test integration_test/  # Integration tests
```

### Code Quality

```bash
# Python
make lint                  # Run all linters
make fmt                   # Format code
ruff check apps/ shared/   # Linting
ruff format .              # Formatting

# Node.js
npm run lint              # ESLint
npm run typecheck         # TypeScript

# Flutter
flutter analyze           # Dart analyzer
dart fix --apply          # Auto-fix issues
```

### Monitoring

```bash
make monitoring-up        # Start Prometheus/Grafana stack
make monitoring-down      # Stop monitoring
make monitoring-logs      # View monitoring logs
make health               # Check health of all services
make status               # Show service status and URLs
```

### Utilities

```bash
make clean                # Clean containers, volumes, build artifacts
make shell SERVICE=name   # Open shell in container
make ps                   # List running containers
make stats                # Show project statistics
make quickstart           # Quick start for new developers
make ci                   # Run CI checks (lint + test)
```

---

## Monitoring & Observability

### Stack Overview

| Component | Purpose | Port |
|-----------|---------|------|
| **Prometheus** | Metrics collection | 9090 |
| **Grafana** | Dashboards & visualization | 3000 |
| **Jaeger** | Distributed tracing | 16686 |
| **Loki** | Log aggregation | 3100 |
| **AlertManager** | Alert routing | 9093 |

### Prometheus Metrics

All services expose metrics at `/metrics`:

```python
# Python service metrics pattern
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)
```

### Standard Metrics

```
# Service health
sahool_service_up{service="field-management"} 1

# Request metrics
http_requests_total{method="GET", endpoint="/api/v1/fields", status="200"}
http_request_duration_seconds_bucket{le="0.5"}

# Business metrics
sahool_fields_total{tenant_id="123"}
sahool_advisory_generated_total{crop_type="wheat"}
sahool_irrigation_scheduled_total
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# All logs include standard fields
logger.info(
    "field_created",
    field_id=field_id,
    tenant_id=tenant_id,
    user_id=user_id,
    request_id=request_id,  # Correlation ID
    duration_ms=elapsed
)
```

### Log Format (JSON)

```json
{
  "timestamp": "2026-01-19T10:30:00Z",
  "level": "info",
  "service": "field-management-service",
  "event": "field_created",
  "field_id": "F001",
  "tenant_id": "T123",
  "request_id": "req-abc-123",
  "trace_id": "trace-xyz-789"
}
```

### Grafana Dashboards

Pre-configured dashboards in `infrastructure/monitoring/dashboards/`:
- `service-overview.json` - All services health
- `api-gateway.json` - Kong metrics
- `database.json` - PostgreSQL performance
- `redis.json` - Cache hit rates
- `nats.json` - Event throughput
- `business-metrics.json` - Agricultural KPIs

### Alerting Rules

```yaml
# Critical alerts
- alert: ServiceDown
  expr: up{job="sahool-services"} == 0
  for: 1m
  severity: critical

- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m
  severity: warning

- alert: DatabaseConnectionExhausted
  expr: pg_stat_activity_count > 200
  for: 2m
  severity: critical
```

---

## Python Service Conventions

### File Structure (FastAPI Service)

```
apps/services/[service-name]/
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   └── v1/              # API version
│   │       └── [resource].py
│   └── events/              # NATS event handlers
└── tests/
```

### Main.py Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, NATS connections
    logger.info("Starting service...")

    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        app.state.nc = await nats.connect(nats_url)

    yield

    # Shutdown: Close connections
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()

app = FastAPI(
    title="Service Name",
    version="16.0.0",
    lifespan=lifespan
)

# Setup unified error handling
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
setup_exception_handlers(app)
add_request_id_middleware(app)
```

### Authentication Pattern

```python
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

@router.get("/protected")
async def protected_endpoint(user: User = Depends(get_current_user)):
    return {"user_id": user.id}
```

### Health Endpoints (Required)

```python
@app.get("/healthz")
def health():
    return {"status": "ok", "service": "service_name", "version": "16.0.0"}

@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }
```

---

## Node.js Service Conventions

### File Structure (NestJS)

```
apps/services/[service-name]/
├── Dockerfile
├── package.json
├── tsconfig.json
├── prisma/
│   ├── schema.prisma
│   └── seed.ts
├── src/
│   ├── index.ts            # Entry point
│   ├── app.module.ts
│   └── __tests__/          # Tests
└── tests/
```

### Database Pattern (Prisma)

```typescript
// Generate client
npx prisma generate

// Run migrations
npx prisma migrate deploy

// Studio (GUI)
npx prisma studio
```

---

## Flutter Mobile Conventions

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Flutter 3.27.x (Dart >=3.2.0) |
| **State Management** | Riverpod 2.6.x with code generation |
| **Local Database** | Drift 2.24+ with SQLCipher encryption |
| **Network** | Dio 5.x with interceptors |
| **Maps** | MapLibre GL, flutter_map |
| **Background** | Workmanager for sync tasks |
| **Security** | Certificate pinning, biometric auth |

### State Management (Riverpod)

```dart
@riverpod
class FieldNotifier extends _$FieldNotifier {
  @override
  Future<List<Field>> build() async {
    return ref.watch(fieldRepositoryProvider).getFields();
  }

  Future<void> updateField(Field field) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(fieldRepositoryProvider).update(field);
      return ref.read(fieldRepositoryProvider).getFields();
    });
  }
}
```

### Offline-First Architecture

```dart
// Sync queue for offline operations
class SyncQueue {
  // Operations queued when offline
  Future<void> enqueue(SyncOperation op) async {
    await _localDb.insertOperation(op);
    if (await _connectivity.isOnline) {
      await _processQueue();
    }
  }

  // Conflict resolution strategy
  ConflictResolution resolveConflict(local, remote) {
    // Server wins for shared fields
    // Client wins for local-only data
    return local.updatedAt > remote.updatedAt
        ? ConflictResolution.keepLocal
        : ConflictResolution.keepRemote;
  }
}
```

### Security Features

```dart
// Certificate pinning
final dio = Dio()
  ..httpClientAdapter = IOHttpClientAdapter(
    createHttpClient: () {
      final client = HttpClient();
      client.badCertificateCallback = (cert, host, port) {
        return _pinnedCerts.contains(cert.sha256);
      };
      return client;
    },
  );

// Biometric authentication
final canAuth = await LocalAuthentication().canCheckBiometrics;
if (canAuth) {
  final authenticated = await LocalAuthentication().authenticate(
    localizedReason: 'Authenticate to access SAHOOL',
  );
}
```

### File Structure

```
lib/
├── core/
│   ├── database/           # Drift database & DAOs
│   ├── network/            # Dio client, interceptors
│   ├── notifications/      # FCM, local notifications
│   ├── security/           # Encryption, auth
│   └── sync/               # Offline sync engine
├── features/
│   ├── auth/               # Login, registration
│   ├── field/              # Field management
│   ├── crop/               # Crop tracking
│   ├── irrigation/         # Irrigation scheduling
│   ├── advisory/           # AI recommendations
│   ├── rotation/           # Crop rotation
│   └── spray/              # Spray logging
├── shared/
│   ├── widgets/            # Reusable UI components
│   └── utils/              # Utility functions
└── l10n/                   # Arabic/English translations
    ├── app_ar.arb
    └── app_en.arb
```

### Localization (Arabic/English)

```dart
// In widget
Text(context.l10n.fieldName)

// ARB files
// app_ar.arb
{
  "fieldName": "اسم الحقل",
  "irrigationSchedule": "جدول الري"
}

// app_en.arb
{
  "fieldName": "Field Name",
  "irrigationSchedule": "Irrigation Schedule"
}
```

---

## Testing Guidelines

### Test Markers (Python)

```python
@pytest.mark.unit       # Fast, no I/O
@pytest.mark.integration # API, database
@pytest.mark.smoke      # Import verification
@pytest.mark.slow       # Long-running
```

### Coverage Requirements

- **Minimum**: 60% code coverage (enforced in CI)
- Coverage report: `coverage.xml` and `coverage_html/`

### Test Environment Variables

```bash
ENVIRONMENT=test
JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars
JWT_ALGORITHM=HS256
DATABASE_URL=""  # Empty for unit tests
NATS_URL=""
```

### Test Folders

| Folder               | Purpose                    |
| -------------------- | -------------------------- |
| `tests/unit/`        | Fast unit tests            |
| `tests/integration/` | API & database tests       |
| `tests/smoke/`       | Import verification        |
| `tests/e2e/`         | End-to-end tests           |
| `tests/load/`        | Locust load tests          |
| `tests/evaluation/`  | AI agent evaluation        |
| `tests/guardrails/`  | Input validation tests     |
| `tests/a2a/`         | Agent-to-Agent tests       |
| `tests/container/`   | Container tests            |
| `tests/database/`    | Database-specific tests    |
| `tests/frontend/`    | Frontend component tests   |
| `tests/middleware/`  | Middleware tests           |
| `tests/simulation/`  | Simulation tests           |

---

## Security Considerations

### Authentication & Authorization

| Feature | Implementation |
|---------|---------------|
| **JWT Tokens** | HS256 (development), RS256 (production) |
| **Token Expiry** | Access: 15 min, Refresh: 7 days |
| **2FA Support** | TOTP (Google Authenticator compatible) |
| **Password Hashing** | Argon2id with secure defaults |
| **Token Revocation** | Redis-backed blacklist |

### RBAC Roles (6 Levels)

```
admin          # Full system access
farm_manager   # Farm-level operations
agronomist     # Advisory and analysis
field_operator # Field-level tasks
viewer         # Read-only access
api_client     # Machine-to-machine
```

### DO NOT

- Commit secrets or credentials (`.env`, API keys)
- Use hardcoded passwords
- Skip authentication checks
- Disable TLS/SSL in production
- Run containers as root
- Use `--no-verify` for git hooks
- Store sensitive data in logs
- Expose internal service ports publicly

### DO

- Use environment variables for secrets
- Follow RBAC patterns (check user roles)
- Validate all user input (use Pydantic models)
- Use parameterized queries (no SQL injection)
- Enable rate limiting on endpoints
- Use TLS for all connections (sslmode=require)
- Implement certificate pinning for mobile
- Audit log security-sensitive operations
- Use request IDs for traceability

### Security Scanning (CI/CD)

| Tool | Purpose | Trigger |
|------|---------|---------|
| **CodeQL** | Semantic analysis for Python/TypeScript | PR, main branch |
| **Bandit** | Python security linter | Every commit |
| **Semgrep** | Pattern-based vulnerability scanning | PR |
| **Trivy** | Container & dependency scanning | Image builds |
| **Gitleaks** | Secret detection in commits | Pre-commit, PR |
| **Dependency Review** | Known vulnerability check | PR |

### Security Headers (Kong Gateway)

```yaml
# Applied to all responses
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Input Validation (Guardrails)

All user input passes through `shared/guardrails/`:
- SQL injection prevention
- XSS sanitization
- Path traversal protection
- File upload validation (type, size, content)
- Rate limiting per endpoint and user tier

---

## API Conventions

### Health Endpoints (Required for all services)

```
GET /healthz         # Liveness probe (alias: /health/live)
GET /readyz          # Readiness probe (alias: /health/ready)
GET /health          # Combined status
GET /metrics         # Prometheus metrics
```

### API Versioning

```
/api/v1/[resource]   # Current version
/api/v2/[resource]   # New version (if applicable)
```

### Rate Limiting Tiers

| Tier     | Requests/min | Requests/hour |
| -------- | ------------ | ------------- |
| Free     | 30           | 500           |
| Standard | 60           | 2000          |
| Premium  | 120          | 5000          |
| Internal | 1000         | 50000         |

---

## Environment Configuration

### Required Environment Variables

```bash
# Database (TLS enforced)
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=sahool
POSTGRES_SSL_MODE=require

# Redis
REDIS_PASSWORD=<secure_password>
REDIS_URL=redis://redis:6379

# NATS
NATS_URL=nats://nats:4222

# JWT
JWT_SECRET_KEY=<32_char_minimum_secret_key>
JWT_ALGORITHM=HS256

# General
ENVIRONMENT=development|staging|production
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
```

---

## Deployment Tiers (Package System)

SAHOOL uses a 3-tier package system for scalable deployment:

### Starter Package
- **Services**: 5 core services
- **Target**: Small farms, individual farmers
- **Features**: Basic field management, weather, simple advisory
- **Resource**: Minimal infrastructure requirements

### Professional Package
- **Services**: 13 services (includes Starter)
- **Target**: Medium farms, cooperatives
- **Features**: Full analytics, IoT integration, marketplace access
- **Additional**: Yield prediction, smart irrigation, crop intelligence

### Enterprise Package
- **Services**: 21+ services (includes Professional)
- **Target**: Large agricultural operations, government programs
- **Features**: Full platform with research tools, disaster assessment, advanced AI
- **Additional**: Multi-tenant support, custom integrations, SLA guarantees

### Docker Compose Profiles

```bash
# Start by tier
make dev-starter           # Starter services only
make dev-professional      # Professional tier
make dev-enterprise        # Full enterprise stack

# Docker Compose files (33 total)
docker/
├── docker-compose.yml           # Base configuration
├── docker-compose.starter.yml   # Starter tier services
├── docker-compose.professional.yml
├── docker-compose.enterprise.yml
├── docker-compose.monitoring.yml
├── docker-compose.test.yml
└── docker-compose.override.yml  # Local development overrides
```

---

## Kubernetes Deployment

### Helm Charts Structure

```
helm/
├── sahool-platform/            # Umbrella chart
│   ├── Chart.yaml
│   ├── values.yaml             # Default values
│   ├── values-staging.yaml     # Staging overrides
│   ├── values-production.yaml  # Production overrides
│   └── charts/                 # Subcharts
├── sahool-starter/             # Starter package chart
├── sahool-professional/        # Professional package chart
└── sahool-enterprise/          # Enterprise package chart
```

### Kubernetes Features

| Feature | Description |
|---------|-------------|
| **HPA** | Horizontal Pod Autoscaler for CPU/memory-based scaling |
| **VPA** | Vertical Pod Autoscaler for resource optimization |
| **PDB** | Pod Disruption Budgets for high availability |
| **Argo Rollouts** | Progressive delivery with canary/blue-green deployments |
| **Network Policies** | Service-to-service communication control |
| **Pod Security** | Non-root containers, read-only filesystems |

### ArgoCD Applications

```yaml
# gitops/applications/
- sahool-core.yaml          # Core infrastructure
- sahool-services.yaml      # Microservices
- sahool-monitoring.yaml    # Prometheus/Grafana stack
- sahool-secrets.yaml       # External Secrets Operator
```

---

## Infrastructure (Terraform)

### AWS Multi-Region Architecture

```
infrastructure/terraform/
├── modules/
│   ├── eks/                # Kubernetes cluster
│   ├── rds/                # PostgreSQL RDS
│   ├── elasticache/        # Redis cluster
│   ├── s3/                 # Object storage (satellite imagery)
│   ├── cloudfront/         # CDN for static assets
│   ├── vpc/                # Network configuration
│   └── iam/                # IAM roles and policies
├── environments/
│   ├── staging/
│   └── production/
└── global/                 # Cross-region resources
```

### Key Infrastructure Components

| Component | Configuration |
|-----------|---------------|
| **EKS** | Kubernetes 1.28+, managed node groups, Karpenter autoscaling |
| **RDS** | PostgreSQL 16, Multi-AZ, automated backups, 7-day retention |
| **ElastiCache** | Redis 7.x cluster mode, encrypted at rest |
| **S3** | Versioning enabled, lifecycle policies, cross-region replication |
| **CloudFront** | TLS 1.3, HTTP/3 support, edge caching |
| **Route 53** | Geo-routing for regional failover |

---

## Common Patterns

### Database Connection

```python
# Python (asyncpg with pool)
app.state.db_pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=2,
    max_size=10
)
```

### NATS Event Publishing

```python
# Python
await app.state.nc.publish(
    "sahool.fields.created",
    json.dumps({"field_id": field_id, "tenant_id": tenant_id}).encode()
)
```

### Logging (Structured JSON)

```python
import structlog
logger = structlog.get_logger()
logger.info("event_name", field_id=field_id, action="create")
```

---

## Shared Modules Reference

### Python Shared Modules (25+)

Located in `shared/`:

| Module | Purpose |
|--------|---------|
| `auth/` | JWT authentication, 2FA, token revocation, RBAC |
| `cache/` | Redis caching layer with TTL management |
| `contracts/` | API request/response contracts (Pydantic) |
| `domain/` | Domain models and business logic |
| `events/` | NATS event definitions and handlers |
| `file_validation/` | File upload validation (type, size, malware) |
| `guardrails/` | Input validation and sanitization |
| `libs/` | Utility libraries |
| `mcp/` | Model Context Protocol for AI integration |
| `middleware/` | HTTP middleware (CORS, logging, auth) |
| `monitoring/` | Prometheus metrics exporters |
| `observability/` | Structured logging, OpenTelemetry tracing |
| `security/` | Encryption, hashing, security utilities |
| `secrets/` | HashiCorp Vault integration |
| `telemetry/` | OpenTelemetry SDK configuration |
| `a2a/` | Agent-to-Agent communication protocol |
| `ai/` | AI/ML utilities and model integration |
| `globalgap/` | GlobalGAP compliance checking |
| `versioning/` | API versioning utilities |

### NPM Packages (26)

Located in `packages/`:

| Package | Purpose |
|---------|---------|
| `@sahool/shared-utils` | Common utility functions |
| `@sahool/shared-ui` | React UI component library |
| `@sahool/shared-types` | TypeScript type definitions |
| `@sahool/shared-hooks` | React hooks (data fetching, state) |
| `@sahool/shared-events` | NATS event type definitions |
| `@sahool/shared-crypto` | Cryptography utilities |
| `@sahool/shared-db` | Database utilities (Prisma helpers) |
| `@sahool/shared-audit` | Audit logging for compliance |
| `@sahool/nestjs-auth` | NestJS authentication module |
| `@sahool/field-shared` | Field domain types |
| `@sahool/api-client` | Generated API client |
| `@sahool/design-system` | Design tokens, themes |
| `@sahool/mock-data` | Test fixtures and mocks |
| `@sahool/i18n` | Arabic/English translations |
| `@sahool/tailwind-config` | Shared Tailwind configuration |
| `@sahool/typescript-config` | Shared tsconfig base |

---

## Important Files Reference

| File                       | Purpose                               |
| -------------------------- | ------------------------------------- |
| `Makefile`                 | All development commands (50+ targets)|
| `docker-compose.yml`       | Full service stack                    |
| `pyproject.toml`           | Python project config, linting (Ruff) |
| `package.json`             | Node.js root workspace                |
| `.env.example`             | Environment template                  |
| `governance/services.yaml` | Service registry (57+ services)       |
| `governance/agents.yaml`   | AI agent definitions                  |
| `governance/security.yaml` | Security policies                     |
| `helm/sahool-platform/`    | Kubernetes deployment charts          |
| `infrastructure/terraform/`| AWS infrastructure as code            |
| `.github/workflows/`       | CI/CD pipeline definitions (35)       |

---

## Git Workflow

### Branch Naming

```
main           # Production
develop        # Development
feature/**     # Feature branches
release/**     # Release preparation
claude/**      # AI-assisted branches
```

### Commit Convention

Use conventional commits:

```
feat: add field boundary mapping
fix: resolve sync conflict in offline mode
docs: update API documentation
test: add integration tests for weather service
refactor: simplify auth middleware
chore: update dependencies
```

### CI/CD Pipeline

1. **Lint**: Code quality checks (Ruff, ESLint)
2. **Test**: Unit, integration, smoke tests
3. **Build**: Docker images
4. **Security**: CodeQL, Trivy, Bandit, Gitleaks
5. **Deploy**: ArgoCD to staging/production

GitHub Workflows (35 total):

**Testing Workflows (13)**:
- `ci.yml` - Main CI pipeline
- `container-tests.yml` - Docker container tests
- `frontend-tests.yml` - Frontend tests
- `load-testing.yml` - Performance tests (k6, Locust)
- `agent-evaluation.yml` - AI agent evaluation
- `test-python.yml`, `test-node.yml`, `test-flutter.yml` - Language-specific tests

**Deployment Workflows (5)**:
- `cd-staging.yml` - Staging deployment
- `cd-production.yml` - Production deployment
- `deploy-preview.yml` - PR preview environments
- `argocd-sync.yml` - GitOps synchronization

**Security Workflows (6)**:
- `codeql-analysis.yml` - Semantic code analysis
- `security-checks.yml` - Security audits
- `trivy-scan.yml` - Container vulnerability scanning
- `gitleaks.yml` - Secret detection
- `dependency-review.yml` - Dependency vulnerability checks

**Build & Release Workflows (4)**:
- `build-images.yml` - Docker image builds
- `release.yml` - Semantic versioning releases
- `changelog.yml` - Automatic changelog generation

**Governance & Quality (4)**:
- `governance-ci.yml` - Service registry validation
- `lint.yml` - Code quality checks
- `docs-check.yml` - Documentation validation
- `schema-validation.yml` - API schema validation

---

## Deprecated Services

Some services are deprecated and have been replaced. Check deprecation warnings in service logs:

```
DEPRECATION WARNING: [service] is DEPRECATED
This service has been migrated to [new-service]
```

| Deprecated Service   | Replaced By                   | Deprecation Date |
| -------------------- | ----------------------------- | ---------------- |
| `satellite-service`  | `vegetation-analysis-service` | 2026-01-11       |
| `weather-advanced`   | `weather-service`             | 2026-01-11       |
| `crop-health-ai`     | `crop-intelligence-service`   | 2026-01-11       |
| `fertilizer-advisor` | `advisory-service`            | 2026-01-11       |
| `field-ops`          | `field-management-service`    | Legacy           |
| `field-core`         | `field-management-service`    | Legacy           |
| `field-service`      | `field-management-service`    | Legacy           |

---

## Key Services Overview

### Core Services

| Service                    | Type    | Port | Description                      |
| -------------------------- | ------- | ---- | -------------------------------- |
| field-management-service   | Node.js | 3000 | Field management (consolidated)  |
| user-service               | Node.js | 3025 | Authentication & user management |
| notification-service       | Python  | 8110 | Push notifications               |
| billing-core               | Python  | 8089 | Billing & invoicing              |
| task-service               | Python  | 8103 | Task management                  |
| equipment-service          | Python  | 8101 | Equipment tracking               |
| alert-service              | Python  | 8113 | Alert management                 |

### Analytics & Intelligence

| Service                      | Type    | Port | Description                    |
| ---------------------------- | ------- | ---- | ------------------------------ |
| vegetation-analysis-service  | Python  | 8090 | Satellite imagery analysis     |
| crop-intelligence-service    | Python  | 8095 | Crop health AI                 |
| indicators-service           | Python  | 8091 | Field indicators computation   |
| ndvi-processor               | Python  | 8118 | NDVI processing                |
| field-intelligence           | Python  | 8120 | Field analytics                |
| lai-estimation               | Node.js | 3022 | Leaf Area Index estimation     |
| skills-service               | Python  | 8121 | Farmer skills assessment       |

### Decision & Advisory

| Service          | Type    | Port | Description                  |
| ---------------- | ------- | ---- | ---------------------------- |
| crop-growth-model| Node.js | 3023 | Crop growth simulation       |
| advisory-service | Python  | 8093 | Advisory & recommendations   |
| irrigation-smart | Python  | 8094 | Smart irrigation             |
| yield-engine     | Python  | 8098 | Yield estimation             |
| yield-prediction | Node.js | 3021 | Yield prediction ML          |
| agro-advisor     | Python  | 8105 | Agricultural advisory        |
| agro-rules       | Python  | 8151 | Agronomic rules engine       |

### Integration & IoT

| Service               | Type    | Port | Description                  |
| --------------------- | ------- | ---- | ---------------------------- |
| iot-service           | Node.js | 8117 | IoT device management        |
| iot-gateway           | Python  | 8106 | IoT protocol gateway         |
| weather-service       | Python  | 8092 | Weather data                 |
| virtual-sensors       | Python  | 8119 | Virtual sensor computation   |
| ws-gateway            | Python  | 8081 | WebSocket gateway            |
| mcp-server            | Python  | 8200 | Model Context Protocol       |
| astronomical-calendar | Python  | 8111 | Islamic calendar & timings   |

### Community & Business

| Service             | Type    | Port | Description              |
| ------------------- | ------- | ---- | ------------------------ |
| marketplace-service | Node.js | 3010 | Agricultural marketplace |
| community-chat      | Node.js | 8097 | Community features       |
| research-core       | Node.js | 3015 | Research trials          |
| disaster-assessment | Node.js | 3020 | Disaster risk assessment |
| field-chat          | Python  | 8099 | Field-level chat         |
| inventory-service   | Python  | 8116 | Inventory management     |

---

## AI Skills

SAHOOL platform includes a comprehensive AI skills system located in `.claude/skills/` that enables advanced context engineering, agricultural advisory generation, and farm documentation using Claude and other AI models. Skills provide reusable modules for agricultural intelligence and farmer guidance.

### Directory Structure

```
.claude/skills/
├── context-engineering/        # Context optimization modules
│   ├── memory.md              # Farm history & persistent memory
│   ├── compression.md         # Token-efficient data compression
│   └── evaluation.md          # LLM-as-Judge advisory quality assessment
├── sahool/                    # SAHOOL-specific domain skills
│   ├── crop-advisor.md        # Crop advisory & recommendations
│   └── farm-documentation.md  # Field & farm knowledge base
└── obsidian/                  # Documentation generation
    ├── markdown.md            # Obsidian markdown formatting
    └── canvas.md              # Canvas-based knowledge graphs
```

### Context Engineering Modules

Context engineering modules optimize AI model performance for agricultural advisory by managing token usage, preserving critical information, and structuring knowledge bases efficiently.

#### Memory Skill

**Location**: `.claude/skills/context-engineering/memory.md`

Enables persistent memory management for farm operations:

- **Entity Memory**: Stores farmers, farms, fields, equipment with full history
- **Event Memory**: Logs planting, treatment, harvest, inspection events
- **Observation Memory**: Captures sensor readings and field inspections
- **Decision Memory**: Records advisory given and farmer responses
- **Outcome Memory**: Tracks yield results, costs, and lessons learned
- **Preference Memory**: Maintains farmer preferences and constraints

**Key Features**:
- Bilingual Arabic/English support
- Hierarchical namespace organization (entities, events, observations)
- YAML schema for structured storage
- Query patterns for historical situation matching
- Offline-first synchronization support

**Usage Example**:
```yaml
# Store treatment event
event_type: treatment
field_id: FIELD-003
crop: wheat
treatment_type: fertilizer
product: Urea 46%
rate: 46 kg/ha
timestamp: 2025-01-14T07:30:00Z
cost: 850 SAR

# Query similar situations
QUERY: similar_situations(
  crop: wheat,
  stage: tillering,
  issue: nitrogen_deficiency,
  min_yield_improvement: 10%
)
# Returns historical decisions and outcomes
```

#### Compression Skill

**Location**: `.claude/skills/context-engineering/compression.md`

Reduces token usage while preserving critical agricultural information:

**Compression Levels**:
- **Level 1** (80% retention): Remove redundancy, apply abbreviations, keep numerical data
- **Level 2** (50% retention): Summarize patterns, aggregate time-series, remove non-essential metadata
- **Level 3** (25% retention): Extract key metrics only, single-line summaries

**Standard Agricultural Abbreviations**:
```
ha = Hectare | هـ
NDVI = Vegetation Index | م.غ.ن
LAI = Leaf Area Index | م.م.و
ET = Evapotranspiration | ت.ن
ppm = Parts Per Million | ج.م
SM = Soil Moisture | ر.ت
EC = Electrical Conductivity | ت.ك
```

**Example Compression**:
```
Original (verbose):
"Field FIELD-003 covers 8.5 hectares of winter wheat variety Sakha 95,
currently in tillering stage with NDVI of 0.72"

Compressed (Level 2):
"F003: Wheat-Sakha95 | 8.5ha | NDVI:0.72 | Tillering | pH:7.2"

Compressed (Level 3):
"F003:Wht|8.5ha|N0.72|Till"
```

**Alert Priority Encoding**:
```
[!!!] Critical - immediate action (<6h) | حرج
[!!]  Warning - action within 24-48h | تحذير
[!]   Advisory - action within 1 week | استشارة
[.]   Informational - for awareness | معلومات
```

#### Evaluation Skill (LLM-as-Judge)

**Location**: `.claude/skills/context-engineering/evaluation.md`

Systematically evaluates agricultural AI advisory quality using multi-dimensional rubrics:

**Evaluation Dimensions** (weighted):
- **Accuracy** (30%): Technical correctness of agricultural advice
- **Relevance** (25%): Applicability to specific field/crop/farmer context
- **Actionability** (20%): Clarity and feasibility of actions
- **Timeliness** (15%): Appropriateness of timing recommendations
- **Safety** (10%): Risk awareness and safety considerations

**Scoring Scale**:
```
5 = Excellent | Expert-level advice, comprehensive
4 = Good      | Sound advice, minor gaps
3 = Adequate  | Acceptable but incomplete
2 = Poor      | Significant errors or omissions
1 = Failing   | Incorrect or potentially harmful
```

**Crop-Specific Validation**:
- **Wheat**: Zadoks growth stage alignment, nitrogen timing
- **Date Palm**: Seasonal timing (pollination, ripening stages)
- **Vegetables**: PHI (pre-harvest interval) compliance
- **All Crops**: Regional climate appropriateness

**Safety Critical Checks**:
- Pesticide: Product registration, PHI, REI, PPE, drift warnings
- Fertilizer: Soil test alignment, timing vs. rainfall, groundwater proximity
- Irrigation: Salinity management, disease risk, water quality

**Example Evaluation Output**:
```yaml
evaluation_result:
  advisory_type: irrigation
  scores:
    accuracy: 4/5 (minor ET calculation missing)
    relevance: 5/5 (field-specific with sensor data)
    actionability: 3/5 (lacks pivot operation details)
    timeliness: 4/5 (optimal window specified)
    safety: 3/5 (missing disease considerations)
  overall_score: 3.85/5.00
  grade: Good
  improvements:
    - "Add pivot run time calculation"
    - "Include target soil moisture level"
    - "Add morning irrigation recommendation"
```

### SAHOOL Domain Skills

Domain-specific skills for agricultural advisory and farm documentation.

#### Crop Advisory Skill

**Location**: `.claude/skills/sahool/crop-advisor.md`

Provides comprehensive crop management recommendations:

**Supported Crops**:
- Wheat (قمح): Sakha varieties, growth stages, pest/disease management
- Barley (شعير): Drought tolerance, yield optimization
- Date Palm (نخيل): Pollination, pest management, harvest timing
- Tomato (طماطم): Greenhouse and field production
- Cucumber, vegetables: General cultivation guidance

**Advisory Framework**:
```yaml
advisory_structure:
  situation:      # Current field/crop status assessment
  analysis:       # Data-driven analysis of conditions
  recommendation: # Specific actionable advice
  rationale:      # Why this recommendation
  action_plan:    # Step-by-step execution guide
  follow_up:      # Next steps and monitoring
```

**Decision Trees**:
- Irrigation Decision: Soil moisture → weather → crop stage → volume calculation → timing
- Fertilizer Decision: Soil test → crop stage → nutrient selection → rate calculation → method
- Pest Management: Identification → population assessment → natural enemies → threshold-based control

**Bilingual Communication**:
```markdown
## Recommendation | التوصية

**English:**
[Detailed recommendation with technical terms]

**العربية:**
[نفس التوصية بالعربية مع المصطلحات الزراعية]

### Action Steps | خطوات التنفيذ
1. [Step EN] | [الخطوة AR]
```

**Alert Priority Levels**:
- Critical (🔴): Immediate <6 hours (RPW detection, severe frost, acute water stress)
- Warning (🟠): 24-48 hours (pest threshold exceeded, nutrient deficiency)
- Advisory (🟡): Within 1 week (preventive treatments, planning)
- Informational (🟢): For awareness (market updates, weather outlook)

#### Farm Documentation Skill

**Location**: `.claude/skills/sahool/farm-documentation.md`

Generates Obsidian-compatible markdown documentation:

**Frontmatter Metadata**:
```yaml
---
title: Field Documentation Title
title_ar: عنوان التوثيق
farm_id: FARM-XXX
field_id: FIELD-XXX
crop_type: wheat | barley | date_palm | tomato
season: winter | summer | spring | fall
status: active | harvested | fallow | planned
tags:
  - sahool/field
  - sahool/crop/wheat
  - operational
---
```

**Obsidian Features**:
- **Wikilinks**: `[[Fields/FIELD-001]]`, `[[Crops/Wheat-2024]]`, `[[Advisory/Pest-Control]]`
- **Callouts**: `> [!warning]`, `> [!tip]`, `> [!info]`, `> [!success]`
- **Task Lists**: `- [ ]` for operation checklists
- **Tables**: Structured farm data in markdown format
- **Dataview Queries**: Dynamic content filtering

**Bilingual Structure**:
```markdown
## Field Overview | نظرة عامة على الحقل

**English:** Description with technical details

**العربية:** نفس الوصف بالعربية
```

**Tag Hierarchy**:
- `#sahool/field` - Field records
- `#sahool/crop/wheat` - Crop-specific
- `#sahool/irrigation` - Irrigation logs
- `#sahool/advisory` - Advisory content
- `#sahool/harvest` - Harvest records
- `#sahool/equipment` - Equipment maintenance

### Knowledge Base Structure

The AI skills system organizes agricultural knowledge in interconnected modules:

#### Data Layers

1. **Raw Data Layer**: Sensor readings, weather, satellite imagery
2. **Processing Layer**: NDVI calculations, feature extraction, trend analysis
3. **Intelligence Layer**: Decision trees, diagnostic algorithms, risk assessment
4. **Advisory Layer**: Farmer-facing recommendations, bilingual output
5. **Memory Layer**: Persistent farm history, outcomes, lessons learned

#### Knowledge Organization

```
Farm Knowledge Graph
├── Entities
│   ├── Farms (farm ID, location, total area, water sources)
│   ├── Fields (field ID, crop history, soil profile, irrigation type)
│   ├── Farmers (preferences, language, constraints, past responses)
│   └── Equipment (assets, maintenance history, capacity)
├── Events
│   ├── Planting (variety, date, seed rate, soil conditions)
│   ├── Treatment (type, product, rate, reason, cost)
│   ├── Harvest (yield, quality, storage, sale)
│   └── Inspection (growth stage, observations, issues)
├── Decisions
│   ├── Advisory Given (recommendations, rationale, farmer response)
│   ├── Treatment Outcomes (effectiveness, yield impact, cost-benefit)
│   └── Lessons Learned (successes, improvements, patterns)
└── Patterns
    ├── Seasonal Trends (crop performance by season, optimal timing)
    ├── Issue Patterns (recurring problems, effective solutions)
    └── Success Factors (high-yield practices, farmer preferences)
```

### Usage Examples

#### Example 1: Generate Contextual Advisory

Input: Farmer reports yellowing wheat leaves in Field 003

Process:
1. **Memory Retrieval**: Load field history, past N deficiencies, successful treatments
2. **Data Analysis**: Compare soil test (18 ppm N) to threshold (25 ppm)
3. **Decision Tree**: Navigate fertilizer decision tree with field context
4. **Compression**: Compress relevant historical data to preserve context tokens
5. **Advisory Generation**: Create bilingual recommendation with cost-benefit analysis
6. **Evaluation**: Score advisory for accuracy, actionability, safety using rubrics

Output:
```markdown
# Nitrogen Deficiency Advisory | استشارة نقص النيتروجين

## Situation
Soil analysis confirms nitrogen deficiency (18 ppm, target: 25 ppm)

## Recommendation
Apply Urea 46% at 46 kg/ha as top dressing early morning with dew

## Action Plan
1. Early morning application (6-8 AM) with dew present
2. Broadcast evenly, 2-pass method for uniformity
3. Light irrigation (15-20 mm) 1-2 days after to incorporate
4. Monitor leaf color in 7-10 days for improvement

## Economic Analysis
- Treatment cost: 115 SAR/ha
- Expected yield saved: 0.7 t/ha × 1850 SAR/t = 1,295 SAR/ha
- ROI: 1,025%
```

#### Example 2: Emergency Alert - Red Palm Weevil

Input: Detection of red palm weevil in date palm grove

Process:
1. **Memory Check**: Load RPW protocols, past cases, treatment success rates
2. **Severity Assessment**: Critical (lethal pest, 24-48h response window)
3. **Compression**: Summary format for rapid communication
4. **Protocol Activation**: Use critical advisory template with emergency procedures
5. **Evaluation**: Validate safety and completeness of recommendations

Output:
```
[!!!] CRITICAL ALERT: Red Palm Weevil Detection
Response window: 24-48 hours maximum

Phase 1 (Today):
- Mark trees with red paint/tape
- Report to Ministry of Agriculture (mandatory)

Phase 2 (Within 48h):
- Inject Emamectin benzoate 5% at 50-100ml per point (4-6 points/tree)
- Depth: 15-20cm into trunk at 45° angle

Phase 3 (Preventive):
- Treat all trees within 50m radius
- Apply pheromone traps (5 per hectare)

Value at Risk: 45,000 SAR (3 trees × 15,000 SAR)
Treatment Cost: 5,400 SAR
ROI: 733%
```

#### Example 3: Batch Farm Report with Compression

Input: Daily farm status for 5 fields with 12+ sensor readings

Process:
1. **Data Aggregation**: Collect all sensor, weather, and inspection data
2. **Compression** (Level 2): Reduce verbose data to structured format
3. **Alert Encoding**: Encode priority levels with bilingual labels
4. **Pattern Detection**: Identify anomalies against historical baselines
5. **Summarization**: Create executive summary with action items

Output:
```
=== Al-Rashid Farm | 2025-01-13 ===

WEATHER: 8-18°C | RH:65% | NW@12km/h | No rain 72h

FIELDS:
| ID  | Crop | Area  | NDVI | SM  | Status          |
|-----|------|-------|------|-----|-----------------|
| F01 | Wht  | 5.2ha | .68  | 45% | OK-Tillering    |
| F02 | Bar  | 3.8ha | .65  | 52% | OK-Heading      |
| F03 | Wht  | 8.5ha | .72↓ | 38% | [!!]N-deficient |
| F04 | Palm | 450t  | -    | -   | [!]3 RPW trees  |
| F05 | -    | 2.1ha | -    | -   | Prep-Tomato     |

ALERTS:
[!!] F03: N:18ppm<25 | Rx: Urea 46kg/ha | Cost:115 ريال/هـ
[!]  F04: RPW Block-B | Treatment active | Cost:5,400 ريال

WATER USAGE: 2,450m³ total | Well-001: 78% capacity

ACTION ITEMS:
- Apply nitrogen to F03 within 24h (optimal ROI 1,025%)
- Continue RPW treatment phase 2
- Monitor F02 for rust at heading stage (risk)
```

### Integration with Claude Code

AI skills can be invoked within Claude Code workflows:

```bash
# Generate crop advisory
claude code --skill crop-advisor --context "Field-003 wheat yellowing"

# Evaluate advisory quality
claude code --skill evaluate --advisory "irrigation_recommendation_001"

# Compress farm data for context window
claude code --skill compress --level 2 --input "farm_sensor_data.json"

# Create farm documentation
claude code --skill farm-documentation --field "FIELD-003" --format obsidian
```

---

## Getting Help

- **Documentation**: `docs/` directory (178+ documents, 77,900+ lines)
- **API Gateway**: `docs/API_GATEWAY.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Security**: `docs/SECURITY.md`
- **Observability**: `docs/OBSERVABILITY.md`
- **Runbooks**: `docs/RUNBOOKS.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Service Registry**: `governance/services.yaml` (57+ services defined)
- **AI Skills**: `.claude/skills/` directory (7 files, 4,010 lines)

---

## Quick Reference

```bash
# Start everything
make dev

# Quick start for new developers
make quickstart

# Run Python tests
pytest apps/services/ -v

# Check code quality
ruff check apps/ shared/

# View logs
docker compose logs -f [service_name]

# Database access
make db-shell

# Service status
make status
```

---

_Last Updated: January 2026_
