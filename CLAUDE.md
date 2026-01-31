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
│   ├── services/               # 62+ microservices (Python FastAPI & Node.js NestJS)
│   │   ├── yolo26-vision-service/      # YOLO26 computer vision
│   │   ├── terrain-core-service/       # DEM processing & terrain analysis
│   │   ├── hydrology-service/          # Hydrology & drainage analysis
│   │   ├── leveling-optimizer-service/ # Field leveling optimization
│   │   ├── edge-orchestrator-service/  # Edge device management (Jetson Orin)
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
│   ├── ai/                     # AI utilities & Auto-Fix Engine
│   │   ├── auto_fix/           # Automated code diagnostics & fixing
│   │   ├── ollama_client.py    # Local LLM hosting via Ollama
│   │   └── model_training.py   # Model fine-tuning & evaluation
│   ├── globalgap/              # GlobalGAP compliance
│   ├── versioning/             # API versioning utilities
│   └── python-lib/             # Python library utilities
├── config/                     # Configuration files
│   ├── certs/                  # TLS certificates
│   └── nats/                   # NATS configuration
├── docker/                     # Docker configurations
├── docs/                       # Technical documentation (109+ docs)
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
| **CI/CD**      | GitHub Actions (37 workflows), Argo CD  |
| **Monitoring** | Prometheus, Grafana, OpenTelemetry      |
| **Secrets**    | HashiCorp Vault                         |

---

## Event Architecture (4-Layer)

The platform uses a 4-layer event architecture via NATS:

| Layer            | Services                                                                              | Purpose                        |
| ---------------- | ------------------------------------------------------------------------------------- | ------------------------------ |
| **Acquisition**  | satellite-service, iot-service, weather-service, virtual-sensors, iot-gateway, edge-orchestrator-service | Data ingestion & normalization |
| **Intelligence** | indicators-service, lai-estimation, crop-intelligence-service, vegetation-analysis-service, ndvi-processor, field-intelligence, skills-service, yolo26-vision-service, terrain-core-service | Feature extraction & AI        |
| **Decision**     | crop-growth-model, advisory-service, irrigation-smart, yield-engine, yield-prediction, agro-advisor, hydrology-service, leveling-optimizer-service | Recommendations & planning     |
| **Business**     | notification-service, marketplace-service, billing-core, community-chat, task-service, equipment-service, ws-gateway | User-facing operations         |

Event subject pattern: `sahool.{tenant_id}.{event_type}`

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
make dev-vision            # Start vision services (yolo26-vision-service)
make dev-terrain           # Start terrain services (terrain-core, hydrology, leveling)
make dev-edge              # Start edge orchestrator service

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

# Vision & Terrain tests
make test-vision          # Run vision service tests
make test-terrain         # Run terrain service tests
make test-edge            # Run edge orchestrator tests

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

### State Management (Riverpod)

```dart
@riverpod
class FieldNotifier extends _$FieldNotifier {
  @override
  Future<List<Field>> build() async {
    return ref.watch(fieldRepositoryProvider).getFields();
  }
}
```

### Offline-First Pattern

- Use Drift for local SQLite database with SQLCipher encryption
- Background sync with Workmanager
- Conflict resolution for offline edits
- Certificate pinning for secure connections

### File Structure

```
lib/
├── core/
│   ├── notifications/
│   └── security/
├── features/
│   ├── field/
│   ├── rotation/
│   └── spray/
└── l10n/                   # Localization (Arabic/English)
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

### DO NOT

- Commit secrets or credentials (`.env`, API keys)
- Use hardcoded passwords
- Skip authentication checks
- Disable TLS/SSL in production
- Run containers as root
- Use `--no-verify` for git hooks

### DO

- Use environment variables for secrets
- Follow RBAC patterns
- Validate all user input
- Use parameterized queries (no SQL injection)
- Enable rate limiting on endpoints
- Use TLS for all connections
- Implement certificate pinning for mobile

### Security Scanning

- **CodeQL**: Semantic analysis for Python/TypeScript
- **Bandit**: Python security linter
- **Semgrep**: Pattern-based scanning
- **Trivy**: Container vulnerability scanning
- **Gitleaks**: Secret detection

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

### Service API Routes

```
# Vision Services
/api/v1/vision/*              # Vision detection endpoints (pest, disease, weed)
/api/v1/vision/detect         # Image detection
/api/v1/vision/batch          # Batch image processing
/api/v1/vision/models         # Model management

# Terrain Services
/api/v1/terrain/*             # Terrain analysis endpoints
/api/v1/terrain/dem           # DEM processing
/api/v1/terrain/slope         # Slope analysis
/api/v1/terrain/aspect        # Aspect analysis

# Hydrology Services
/api/v1/hydrology/*           # Hydrology analysis endpoints
/api/v1/hydrology/drainage    # Drainage analysis
/api/v1/hydrology/watershed   # Watershed delineation
/api/v1/hydrology/flow        # Flow accumulation

# Leveling Services
/api/v1/leveling/*            # Field leveling endpoints
/api/v1/leveling/optimize     # Leveling optimization
/api/v1/leveling/cut-fill     # Cut/fill calculations
/api/v1/leveling/cost         # Cost estimation

# Edge Device Services
/api/v1/edge/*                # Edge device management endpoints
/api/v1/edge/devices          # Device registration & status
/api/v1/edge/deploy           # Model deployment to edge
/api/v1/edge/sync             # Data synchronization
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

## Important Files Reference

| File                       | Purpose                               |
| -------------------------- | ------------------------------------- |
| `Makefile`                 | All development commands              |
| `docker-compose.yml`       | Full service stack                    |
| `pyproject.toml`           | Python project config, linting (Ruff) |
| `package.json`             | Node.js root workspace                |
| `.env.example`             | Environment template                  |
| `governance/services.yaml` | Service registry (source of truth)    |
| `governance/agents.yaml`   | AI agent definitions                  |

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

GitHub Workflows (37):

- `ci.yml` - Main CI pipeline
- `cd-staging.yml` - Staging deployment
- `cd-production.yml` - Production deployment
- `container-tests.yml` - Docker container tests
- `codeql-analysis.yml` - Security scanning
- `frontend-tests.yml` - Frontend tests
- `load-testing.yml` - Performance tests
- `agent-evaluation.yml` - AI agent evaluation
- `governance-ci.yml` - Governance checks
- `security-checks.yml` - Security audits

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
| soil-analysis-service        | Python  | 8124 | Soil analysis                  |
| pest-detection-service       | Python  | 8125 | Pest detection AI              |

### Decision & Advisory

| Service          | Type    | Port | Description                  |
| ---------------- | ------- | ---- | ---------------------------- |
| crop-growth-model  | Node.js | 3023 | Crop growth simulation       |
| advisory-service   | Python  | 8093 | Advisory & recommendations   |
| irrigation-smart   | Python  | 8094 | Smart irrigation             |
| irrigation-service | Python  | 8094 | Irrigation management        |
| yield-engine       | Python  | 8098 | Yield estimation             |
| yield-prediction   | Node.js | 3021 | Yield prediction ML          |
| agro-advisor       | Python  | 8105 | Agricultural advisory        |
| agro-rules         | Python  | 8151 | Agronomic rules engine       |

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
| drone-service         | Python  | 8126 | Drone integration            |

### Community & Business

| Service             | Type    | Port | Description              |
| ------------------- | ------- | ---- | ------------------------ |
| marketplace-service | Node.js | 3010 | Agricultural marketplace |
| community-chat      | Node.js | 8097 | Community features       |
| research-core       | Node.js | 3015 | Research trials          |
| disaster-assessment | Node.js | 3020 | Disaster risk assessment |
| field-chat          | Python  | 8099 | Field-level chat         |
| inventory-service   | Python  | 8116 | Inventory management     |
| cooperative-service | Python  | 8127 | Cooperative management   |

### AI Agents

| Service             | Type    | Port | Description              |
| ------------------- | ------- | ---- | ------------------------ |
| agent-registry      | Python  | 8160 | Agent registry service   |
| code-fix-agent      | Python  | 8161 | Code fix AI agent        |
| code-review-agent   | Python  | 8162 | Code review agent        |

### Compliance & Traceability

| Service               | Type    | Port | Description              |
| --------------------- | ------- | ---- | ------------------------ |
| globalgap-compliance  | Python  | 8120 | GlobalGAP compliance     |
| audit-service         | Python  | 8122 | Audit logging            |
| traceability-service  | Python  | 8123 | Product traceability     |

### Vision, Terrain & Edge Services (New)

| Service                    | Type   | Port | Description                                        |
| -------------------------- | ------ | ---- | -------------------------------------------------- |
| yolo26-vision-service      | Python | 8150 | YOLO26 computer vision for pest/disease/weed detection |
| terrain-core-service       | Python | 8185 | DEM processing and terrain analysis                |
| hydrology-service          | Python | 8165 | Hydrology and drainage analysis                    |
| leveling-optimizer-service | Python | 8170 | Field leveling optimization                        |
| edge-orchestrator-service  | Python | 8190 | Edge device management (Jetson Orin)               |

---

## AI Auto-Fix Engine

The SAHOOL platform includes a comprehensive AI-powered code auto-fix system located in `shared/ai/` that enables automated code diagnostics, fixing, and model training capabilities.

### Architecture Overview

```
shared/ai/
├── auto_fix/                    # Auto-Fix Engine
│   ├── __init__.py             # Package exports
│   ├── models.py               # Data models (Diagnostic, CodeFix, AuditEntry)
│   ├── diagnostics.py          # Multi-tool code analysis
│   ├── fixers.py               # Automated code fixing
│   └── engine.py               # Main orchestration engine
├── context_engineering/         # Context Engineering
│   ├── compression.py          # Token compression
│   ├── memory.py               # Farm memory management
│   └── evaluation.py           # LLM-as-Judge evaluation
├── ollama_client.py            # Local LLM integration via Ollama
├── model_training.py           # Model fine-tuning & evaluation
├── audit.py                    # AI audit logging with cost tracking
├── circuit_breaker.py          # Resilience pattern for services
├── metrics.py                  # Prometheus-compatible metrics
├── llm_provider.py             # Multi-provider LLM manager
├── validation.py               # Input/output validation
├── embeddings.py               # Unified embedding providers
├── explainability.py           # Recommendation explanations
└── feedback.py                 # User feedback collection
```

### Auto-Fix Engine (`shared/ai/auto_fix/`)

The Auto-Fix Engine provides automated code diagnostics and fixing with full audit trail integration.

#### Supported Tools

| Tool | Language | Description |
|------|----------|-------------|
| **Ruff** | Python | Fast linting & formatting (F401, E501, etc.) |
| **ESLint** | TypeScript/JavaScript | Code quality & style |
| **Mypy** | Python | Static type checking |
| **Bandit** | Python | Security vulnerability scanning |
| **Dart Analyze** | Dart/Flutter | Flutter code analysis |

*Note: The ToolType enum also defines Semgrep, Pylint, and TypeScript, but these are not yet implemented in the diagnostics engine.*

#### Usage Example

```python
from shared.ai.auto_fix import AutoFixEngine, FixStrategy

# Initialize engine
engine = AutoFixEngine(
    working_dir="/path/to/project",
    audit_enabled=True
)

# Run diagnostics
report = await engine.diagnose(
    paths=["apps/services/", "shared/"],
    tools=["ruff", "mypy", "bandit"]
)

print(f"Found {report.total_diagnostics} issues")
print(f"Auto-fixable: {report.fixable_count}")

# Auto-fix issues
results = await engine.auto_fix(
    report=report,
    strategy=FixStrategy.SAFE,  # MINIMAL, SAFE, COMPREHENSIVE, or REFACTOR
    dry_run=False
)

# View audit trail
for entry in engine.get_audit_log():
    print(f"{entry.timestamp}: {entry.action} - {entry.description}")
```

#### Fix Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `MINIMAL` | Least changes, only safe fixes | Conservative fixes |
| `SAFE` | Safe changes only, no review required | Production code |
| `COMPREHENSIVE` | Apply all suggested fixes | Development |
| `REFACTOR` | Full restructuring allowed | Major cleanup |

#### Data Models

```python
from shared.ai.auto_fix.models import (
    Diagnostic,           # Single code issue
    DiagnosticReport,     # Collection of diagnostics
    CodeFix,              # Proposed fix
    FixPlan,              # Plan with multiple fixes
    FixResult,            # Result of applying fix
    AuditEntry,           # Audit log entry
    DiagnosticSeverity,   # ERROR, WARNING, INFO, HINT
    DiagnosticCategory,   # STYLE, SECURITY, PERFORMANCE, etc.
    FixConfidence,        # HIGH, MEDIUM, LOW
)
```

### Ollama Integration (`shared/ai/ollama_client.py`)

Local LLM hosting for code analysis and generation without external API dependencies.

#### Supported Models

| Model | Size | Use Case |
|-------|------|----------|
| `codellama:7b` | 7B | Code completion & fixing |
| `codellama:13b` | 13B | Complex code analysis |
| `deepseek-coder:6.7b` | 6.7B | Multi-language support |
| `starcoder2:7b` | 7B | Code generation |

#### Usage Example

```python
from shared.ai.ollama_client import OllamaClient, OllamaConfig

# Initialize client
client = OllamaClient(OllamaConfig(
    base_url="http://localhost:11434",
    model="codellama:7b",
    temperature=0.1
))

# Check availability
if await client.is_available():
    # Analyze code
    response = await client.generate(
        prompt="Review this code for security issues:\n```python\n...\n```"
    )
    print(response.text)

# Helper functions
from shared.ai.ollama_client import (
    analyze_code_with_ollama,
    fix_code_with_ollama,
    generate_tests_with_ollama
)

# Quick analysis
analysis = await analyze_code_with_ollama(code, language="python")
```

### Model Training (`shared/ai/model_training.py`)

Fine-tune models on SAHOOL-specific code patterns and agricultural domain knowledge.

#### Dataset Types

| Type | Description | Example |
|------|-------------|---------|
| `CODE_FIX` | Error → Fix pairs | Linting fixes |
| `CODE_REVIEW` | Code → Review pairs | Review comments |
| `TEST_GENERATION` | Code → Tests pairs | Unit tests |
| `AGRICULTURAL` | Query → Advisory pairs | Crop advice |

#### Usage Example

```python
from shared.ai.model_training import (
    DatasetBuilder,
    ModelTrainer,
    TrainingConfig
)

# Build dataset
builder = DatasetBuilder()
builder.add_code_fix_example(
    original="x= 1",
    fixed="x = 1",
    error_message="E225 missing whitespace"
)
builder.add_agricultural_advisory_example(
    query="متى أسقي القمح؟",
    response="يُنصح بالري كل 10-14 يوم في مرحلة التفريع",
    crop_type="wheat",
    language_code="ar"
)

dataset = builder.build(
    name="sahool-fixes",
    name_ar="إصلاحات سهول"
)

# Train model
trainer = ModelTrainer()
config = TrainingConfig(
    base_model="codellama:7b",
    output_model="sahool-codefix:latest",
    epochs=3
)

job = await trainer.create_training_job(dataset, config)
job = await trainer.start_training(job.id)

print(f"Accuracy: {job.evaluation_result.accuracy:.2%}")
```

### Integration with Audit System

All auto-fix operations are logged to the audit system for compliance:

```python
# Audit entry structure
{
    "id": "audit-uuid",
    "timestamp": "2026-01-20T10:30:00Z",
    "action": "auto_fix",
    "agent_id": "code-fix-agent",
    "description": "Fixed 15 linting issues in shared/ai/",
    "details": {
        "files_modified": 5,
        "fixes_applied": 15,
        "strategy": "SAFE"
    },
    "user_id": "system",
    "tenant_id": "sahool"
}
```

### Environment Variables

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b
OLLAMA_TIMEOUT=60

# Auto-Fix Configuration
AUTO_FIX_ENABLED=true
AUTO_FIX_DRY_RUN=false
AUTO_FIX_AUDIT_ENABLED=true
```

---

## Embeddings Adapter

The Embeddings Adapter provides a unified interface for multiple embedding providers, supporting offline-first architecture with automatic fallback.

### Supported Providers

| Provider | Type | Models |
|----------|------|--------|
| **Sentence Transformers** | Local | all-MiniLM-L6-v2, all-mpnet-base-v2, paraphrase-multilingual |
| **Ollama** | Local | nomic-embed-text, mxbai-embed-large |
| **OpenAI** | Cloud | text-embedding-3-small, text-embedding-3-large, ada-002 |
| **Google** | Cloud | textembedding-gecko, textembedding-gecko-multilingual |

### Usage Example

```python
from shared.ai.embeddings import (
    EmbeddingsAdapter,
    EmbeddingConfig,
    EmbeddingProvider,
)

# Initialize with local provider (offline-first)
config = EmbeddingConfig(
    provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
    model="all-MiniLM-L6-v2",
    cache_enabled=True,
)
adapter = EmbeddingsAdapter(config)

# Single embedding
result = await adapter.embed("Agricultural advisory for wheat irrigation")
print(f"Dimension: {result.dimension}, Latency: {result.latency_ms}ms")

# Batch embedding
results = await adapter.embed_batch([
    "Wheat irrigation schedule",
    "جدول ري القمح",
    "Nitrogen fertilizer application",
])

# Semantic similarity
similarity = await adapter.similarity(
    "wheat disease symptoms",
    "أعراض مرض القمح"
)
print(f"Similarity: {similarity:.2f}")

# Find most similar
matches = await adapter.find_most_similar(
    query="irrigation advice",
    candidates=["watering schedule", "fertilizer tips", "pest control"],
    top_k=2
)
```

---

## Explainability Layer

The Explainability Layer provides detailed explanations for AI recommendations, answering "Why this recommendation?" (لماذا هذه التوصية؟).

### Features

- **Factor-based explanations**: Soil, weather, crop stage contributions
- **Rule-based explanations**: Agronomic rules that were applied
- **Alternative comparison**: Other options considered with rejection reasons
- **Bilingual support**: Arabic and English explanations
- **Confidence analysis**: Uncertainty reasons and data sources

### Usage Example

```python
from shared.ai.explainability import (
    ExplainabilityEngine,
    ContributingFactor,
    FactorType,
    ImpactLevel,
)

engine = ExplainabilityEngine()

# Explain irrigation recommendation
explanation = engine.explain_irrigation(
    recommendation_id="irr_001",
    soil_moisture=35.0,
    weather_forecast={"rain_probability": 10, "temperature": 28},
    crop_stage="tillering",
    et_value=5.5,
    recommended_amount_mm=25.0,
)

# Get human-readable summary
print(explanation.summary)        # English
print(explanation.summary_ar)     # Arabic

# Get detailed explanation
print(engine.format_for_display(explanation, language="both"))

# Explain fertilizer recommendation
explanation = engine.explain_fertilizer(
    recommendation_id="fert_001",
    soil_test={"nitrogen": 18, "phosphorus": 25, "potassium": 150},
    crop_type="wheat",
    crop_stage="tillering",
    target_yield=5.0,
    recommended_fertilizer="Urea 46%",
    recommended_rate=46.0,
)

# Access contributing factors
for factor in explanation.primary_factors:
    print(f"{factor.name_ar}: {factor.value} ({factor.impact.value})")
```

### Explanation Output

```yaml
recommendation_id: irr_001
explanation_type: factor_based
overall_confidence: 85%

summary: "This irrigation recommendation is based on Soil Moisture, Weather Forecast."
summary_ar: "هذه التوصية بشأن الري مبنية على رطوبة التربة، توقعات الطقس."

factors:
  - name: Soil Moisture | رطوبة التربة
    value: 35%
    impact: HIGH
    direction: supports
  - name: Weather Forecast | توقعات الطقس
    value: "No rain expected"
    impact: HIGH
    direction: supports
```

---

## Feedback Collection

The Feedback Collection module enables collecting and analyzing user feedback on AI recommendations for continuous quality improvement.

### Features

- **Multiple feedback types**: Rating (1-5), thumbs up/down, outcome, correction
- **Sentiment analysis**: Automatic sentiment scoring
- **Outcome tracking**: Did the advice work? Yield and cost impact
- **Training data export**: Export for model fine-tuning
- **Summary statistics**: Analytics and insights

### Usage Example

```python
from shared.ai.feedback import (
    FeedbackCollector,
    RecommendationType,
    OutcomeStatus,
)

# Initialize collector
collector = FeedbackCollector(tenant_id="farm_001")

# Collect rating feedback (1-5 stars)
await collector.collect_rating(
    recommendation_id="rec_001",
    rating=4,
    recommendation_type=RecommendationType.IRRIGATION,
    comment="The irrigation advice worked well",
    comment_ar="نصيحة الري نجحت بشكل جيد",
)

# Collect thumbs up/down
await collector.collect_thumbs(
    recommendation_id="rec_002",
    thumbs_up=True,
)

# Collect outcome feedback (did it work?)
await collector.collect_outcome(
    recommendation_id="rec_001",
    outcome=OutcomeStatus.SUCCESS,
    yield_impact=15.0,  # 15% yield improvement
    cost_impact=500.0,  # Cost in local currency
    outcome_details="Crop health improved significantly",
    outcome_details_ar="تحسنت صحة المحصول بشكل ملحوظ",
)

# Collect correction (user provides correct answer)
await collector.collect_correction(
    recommendation_id="rec_003",
    correction="The correct irrigation amount is 30mm not 25mm",
)

# Get summary statistics
summary = await collector.get_summary(days=30)
print(f"Total feedback: {summary.total_feedback}")
print(f"Average rating: {summary.average_rating:.1f}")
print(f"Success rate: {summary.success_rate:.0%}")
print(f"By type: {summary.by_recommendation_type}")

# Export for model training
training_data = await collector.export_for_training(min_rating=4)
```

### Feedback Summary Output

```yaml
total_feedback: 150
average_rating: 4.2
success_rate: 78%
thumbs_up_count: 95
thumbs_down_count: 15

by_recommendation_type:
  irrigation:
    count: 60
    average_rating: 4.5
    positive: 52
    negative: 8
  fertilizer:
    count: 45
    average_rating: 4.1
    positive: 38
    negative: 7

outcome_distribution:
  success: 85
  partial_success: 20
  failure: 10
  not_applicable: 5
```

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

- **Documentation**: `docs/` directory (109+ documents)
- **API Gateway**: `docs/API_GATEWAY.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Security**: `docs/SECURITY.md`
- **Observability**: `docs/OBSERVABILITY.md`
- **Runbooks**: `docs/RUNBOOKS.md`
- **Service Registry**: `governance/services.yaml`
- **AI Skills**: `.claude/skills/` directory with context engineering modules

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
