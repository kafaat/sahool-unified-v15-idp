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
│   │   ├── sahol_atmosphere/   # Weather/atmosphere companion app
│   │   ├── sahool-mobile/      # Secondary mobile variant
│   │   ├── lib/                # Core Flutter code
│   │   └── integration_test/   # Integration tests
│   ├── services/               # 71 microservices (Python FastAPI & Node.js NestJS)
│   │   ├── yolo26-vision-service/      # YOLO26 computer vision
│   │   ├── terrain-core-service/       # DEM processing & terrain analysis
│   │   ├── hydrology-service/          # Hydrology & drainage analysis
│   │   ├── leveling-optimizer-service/ # Field leveling optimization
│   │   ├── edge-orchestrator-service/  # Edge device management (Jetson Orin)
│   ├── services-docs/           # Service documentation & API specs
│   └── web/                    # Web dashboard (Next.js/React)
├── packages/                   # Shared packages (24 npm workspaces)
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
│   ├── shared/                 # Shared package utilities
│   ├── starter/                # Starter package config
│   ├── professional/           # Professional package config
│   └── enterprise/             # Enterprise package config
├── shared/                     # Python shared modules (65+ modules)
│   ├── auth/                   # Authentication (JWT, 2FA, token revocation)
│   ├── cache/                  # Caching layer (Redis Sentinel HA)
│   ├── contracts/              # API contracts & event schemas
│   ├── domain/                 # Domain models (auth, users, tenancy)
│   ├── events/                 # NATS event definitions & DLQ
│   ├── file_validation/        # File upload validation & virus scanning
│   ├── guardrails/             # AI safety guardrails
│   ├── libs/                   # Shared libraries (outbox, audit, caching)
│   ├── mcp/                    # Model Context Protocol
│   ├── middleware/             # HTTP middleware (rate limiting, CORS, logging)
│   ├── monitoring/             # Prometheus metrics & SLI/SLO
│   ├── observability/          # OpenTelemetry, Jaeger tracing
│   ├── security/               # RBAC, JWT, policy engine
│   ├── secrets/                # HashiCorp Vault integration
│   ├── telemetry/              # Distributed tracing
│   ├── versioning/             # API versioning utilities
│   ├── a2a/                    # Agent-to-Agent protocol (Linux Foundation)
│   ├── ai/                     # AI utilities & Auto-Fix Engine
│   │   ├── auto_fix/           # Automated code diagnostics & fixing
│   │   ├── context_engineering/ # Token compression, memory, evaluation
│   │   ├── agents/             # CrewAI multi-agent orchestration
│   │   ├── orchestration/      # Multi-agent consensus & swarm intelligence
│   │   ├── guardrails/         # AI safety (input/output filtering)
│   │   ├── models_registry/    # Agricultural AI models registry (50+ models)
│   │   ├── ultrarag/           # Advanced RAG system
│   │   ├── diffusion/          # Image generation
│   │   ├── ollama_client.py    # Local LLM hosting via Ollama
│   │   ├── llm_provider.py     # Multi-provider LLM (Claude, OpenAI, Gemini, DeepSeek)
│   │   ├── embeddings.py       # Unified embedding providers
│   │   ├── vector_store.py     # Persistent vector database for RAG
│   │   ├── crop_vision.py      # Computer vision for disease/pest detection
│   │   ├── explainability.py   # AI recommendation explanations
│   │   ├── feedback.py         # User feedback collection
│   │   └── model_training.py   # Model fine-tuning & evaluation
│   ├── nlp/                    # Arabic NLP (AraBERT)
│   ├── satellite/              # Sentinel Hub NDVI integration
│   ├── ml/                     # AgML agricultural datasets
│   ├── agents/                 # CrewAI multi-agent orchestration
│   ├── llm/                    # LLM provider config & routing
│   ├── agri_calendar/          # Agricultural calendar & planting timing
│   ├── irrigation/             # Smart irrigation management
│   ├── water_management/       # Water usage monitoring & efficiency
│   ├── ml_irrigation/          # ML-based irrigation optimization
│   ├── soil_testing/           # Soil analysis & interpretation
│   ├── soil_sensors/           # IoT soil sensor integration
│   ├── salinity/               # Soil salinity management
│   ├── fertilizer_management/  # Nutrient & fertilizer recommendations
│   ├── crop_rotation/          # Crop rotation planning
│   ├── pest_scouting/          # Pest identification & IPM
│   ├── pesticide_compliance/   # PHI & pesticide compliance
│   ├── weather_alerts/         # Weather monitoring & alerts
│   ├── terrain/                # Terrain analysis & DEM processing
│   ├── field_boundaries/       # Field geometry & geospatial ops
│   ├── geofencing/             # Geofence alerts & monitoring
│   ├── harvest_quality/        # Post-harvest quality management
│   ├── traceability/           # Supply chain traceability & QR codes
│   ├── market_prices/          # Market price tracking & analysis
│   ├── mobile_sync/            # Offline-first mobile sync & conflict resolution
│   ├── batch_operations/       # Async batch processing
│   ├── labor_management/       # Workforce scheduling & safety
│   ├── equipment_maintenance/  # Equipment lifecycle & predictive maintenance
│   ├── cooperatives/           # Multi-farm cooperative management
│   ├── learning_marketplace/   # Farmer education & progress tracking
│   ├── drone_integration/      # Drone flight planning & VRA
│   ├── crop_insurance/         # Crop insurance & risk assessment
│   ├── farm_documents/         # Farm documentation & compliance
│   ├── smart_agriculture/      # Blockchain, IFTTT, PID controllers
│   ├── edge_cloud/             # Edge-cloud architecture
│   ├── globalgap/              # GlobalGAP compliance (IFA v6)
│   ├── yemen/                  # Yemen-specific agricultural data
│   ├── integrations/           # External integrations
│   ├── notification_preferences/ # Notification preference management
│   ├── audit_trail/            # Audit trail utilities
│   ├── crm/                    # Farmer CRM module
│   ├── db/                     # Database utilities
│   ├── design-system/          # Design system tokens & utilities
│   ├── lowcode/                # Low-code workflow automation
│   ├── scraping/               # Data scraping utilities
│   ├── service_enhancements/   # Service improvement modules
│   ├── templates/              # Configuration/code templates
│   └── python-lib/             # Python library utilities
├── config/                     # Configuration files
│   ├── certs/                  # TLS certificates
│   └── nats/                   # NATS configuration
├── docker/                     # Docker configurations
├── docs/                       # Technical documentation (385+ docs)
├── gitops/                     # ArgoCD applications
├── governance/                 # Security policies & service registry
├── helm/                       # Kubernetes Helm charts
├── idp/                        # Internal Developer Platform (Backstage)
├── infrastructure/             # IaC, monitoring, Terraform
├── tests/                      # Test suites (18 categories)
│   ├── unit/                   # Fast unit tests
│   ├── integration/            # API & database tests
│   ├── smoke/                  # Import verification
│   ├── e2e/                    # End-to-end scenarios
│   ├── load/                   # Load tests (k6, Locust)
│   ├── evaluation/             # AI agent evaluation
│   ├── guardrails/             # Input validation tests
│   ├── a2a/                    # Agent-to-Agent tests
│   ├── container/              # Docker container tests
│   ├── database/               # Database-specific tests
│   ├── frontend/               # React component tests
│   ├── middleware/             # Middleware tests
│   ├── simulation/             # Simulation tests
│   ├── security/               # Security tests
│   ├── golden-datasets/        # Golden test datasets
│   ├── factories/              # Test data factories
│   ├── snapshots/              # Snapshot comparisons
│   └── utils/                  # Test utilities
├── tools/                      # Developer tools (FixOps CLI, Kimi repair agent)
└── scripts/                    # Utility scripts
```

---

## Technology Stack

### Backend Services

| Layer                  | Technology                                                            |
| ---------------------- | --------------------------------------------------------------------- |
| **Python Services**    | FastAPI 0.128.5, Tortoise ORM 0.25.4, asyncpg 0.31.0, Pydantic v2.10+ |
| **Python Version**     | >= 3.11 (target: py311)                                                |
| **Node.js Services**   | NestJS 10.x, Prisma 5.x, TypeScript 5.9.x, React 19.x               |
| **Node.js Version**    | >= 20.0.0 (npm >= 10.0.0)                                             |
| **Database**           | PostgreSQL 16+ with PostGIS 3.4 (geospatial)                          |
| **Message Queue**      | NATS 2.10.x with JetStream (event-driven architecture)               |
| **API Gateway**        | Kong 3.x (authentication, rate limiting, 105 routes)                  |
| **Caching**            | Redis 7.x (sessions, rate limiting)                                   |
| **Connection Pooling** | PgBouncer (transaction mode, 250 max connections)                     |

### Mobile Application

| Layer                | Technology                             |
| -------------------- | -------------------------------------- |
| **Framework**        | Flutter 3.27.x (Dart 3.6.0, SDK >=3.2.0) |
| **State Management** | Riverpod 2.6.x                         |
| **Local Database**   | Drift 2.24+ with SQLCipher (encrypted) |
| **Background Tasks** | Workmanager                            |
| **Maps**             | flutter_map 8.1.x, latlong2            |
| **Network**          | Dio 5.x with certificate pinning       |
| **Crash Reporting**  | Sentry (@sentry/nextjs 8.x for web)    |

### Frontend (Web/Admin)

| Layer          | Technology                                             |
| -------------- | ------------------------------------------------------ |
| **Framework**  | Next.js 15.x, React 19.x with TypeScript 5.9.x        |
| **Testing**    | Vitest 3.x, React Testing Library 16.x, Playwright 1.57.x |
| **Build**      | Vite 6.x / Next.js 15.x                               |
| **Styling**    | Tailwind CSS 3.4.x                                    |
| **Monitoring** | Sentry                                                 |

### Infrastructure

| Layer            | Technology                                        |
| ---------------- | ------------------------------------------------- |
| **Container**    | Docker, Kubernetes (K8s)                          |
| **IaC**          | Terraform (AWS me-south-1), Helm Charts (32)      |
| **CI/CD**        | GitHub Actions (49 workflows), Argo CD (18 apps)  |
| **Monitoring**   | Prometheus, Grafana (4 dashboards), OpenTelemetry  |
| **Tracing**      | Jaeger, OpenTelemetry Collector                    |
| **Secrets**      | HashiCorp Vault 1.17                               |
| **Object Store** | MinIO (S3-compatible)                              |
| **Vector DB**    | Qdrant 1.7.x, Milvus 2.3.x                       |
| **ML Tracking**  | MLflow 2.15.x                                      |
| **IoT Broker**   | Mosquitto (MQTT) 2.x                               |
| **Local LLM**    | Ollama 0.5.x                                       |

---

## Event Architecture (4-Layer)

The platform uses a 4-layer event architecture via NATS:

| Layer            | Services                                                                              | Purpose                        |
| ---------------- | ------------------------------------------------------------------------------------- | ------------------------------ |
| **Acquisition**  | vegetation-analysis-service, iot-service, weather-service, virtual-sensors, iot-gateway, edge-orchestrator-service | Data ingestion & normalization |
| **Intelligence** | indicators-service, lai-estimation, crop-intelligence-service, vegetation-analysis-service, ndvi-processor, field-intelligence, skills-service, yolo26-vision-service, terrain-core-service | Feature extraction & AI        |
| **Decision**     | crop-growth-model, advisory-service, irrigation-smart, yield-prediction, yield-prediction-service, hydrology-service, leveling-optimizer-service | Recommendations & planning     |
| **Business**     | notification-service, marketplace-service, billing-core, chat-service, task-service, equipment-service, ws-gateway | User-facing operations         |

Event subject patterns:
- Base: `sahool.{domain}.{action}` (e.g., `sahool.field.created`)
- Tenant-scoped: `sahool.tenant.{tenant_id}.{domain}.{action}` (via `get_tenant_subject()`)
- Inline tenant: `sahool.{tenant_id}.{domain}.{action}` (some services)

`tenant_id` is a UUID string, extracted from JWT `tid` claim.

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

### AI & Agent Services

```bash
make dev-ai               # Start AI services
make dev-agents           # Start agent services
make build-ai             # Build AI service images
make test-ai              # Run AI service tests
make dev-mcp              # Start MCP server
make test-mcp             # Run MCP server tests
```

### FixOps (Auto-Fix)

```bash
make fixops               # Preview issues (dry-run)
make fixops-run           # Apply safe fixes
make fixops-comprehensive # Fix all issues
make fixops-json          # JSON output for CI/CD integration
```

### Mobile Development

```bash
make mobile-test          # Run Flutter tests
make mobile-build         # Build debug APK
make mobile-build-release # Build release APK
make mobile-build-aab     # Build Android App Bundle
make mobile-analyze       # Run Dart analyzer
make mobile-format        # Format Dart code
make mobile-clean         # Clean Flutter build artifacts
make mobile-deps          # Install Flutter dependencies
make mobile-codegen       # Run code generation
make mobile-ci            # Full mobile CI pipeline
```

### Utilities

```bash
make clean                # Clean containers, volumes, build artifacts
make shell SERVICE=name   # Open shell in container
make ps                   # List running containers
make stats                # Show project statistics
make quickstart           # Quick start for new developers
make ci                   # Run CI checks (lint + test)
make ci-full              # Full CI pipeline (lint + test + build)
make dead-code            # Detect unused code (knip)
make complexity           # Check code complexity
make secrets-scan         # Scan for leaked secrets
make deps-check           # Check dependency health
make deps-audit           # Security audit of dependencies
```

---

## Docker Build Conventions

### Dockerfiles Overview

The platform contains **109 Dockerfiles** across Python, Node.js, and infrastructure services.

| File | Purpose |
| ---- | ------- |
| `docker/Dockerfile.python.base` | Base Python image (no mirror, basic pip config) |
| `docker/Dockerfile.ai-base` | AI services base (Aliyun + Tsinghua mirrors) |
| `docker/Dockerfile.node.base` | Node.js base |
| `apps/services/*/Dockerfile` | Per-service Dockerfiles (72 services) |
| `config/postgres/Dockerfile.walg` | PostgreSQL 16 + PostGIS 3.4 + WAL-G |
| `idp/templates/python-fastapi/skeleton/Dockerfile` | IDP service template |

### Python Base Image

All Python services use `python:${PYTHON_VERSION}-slim-bookworm` (default 3.11).
Exception: `yolo26-vision-service` uses `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`.

### Pip Environment Variables (Standard)

```dockerfile
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10
```

### Pip Mirror Configuration (3 Patterns)

**Pattern A: Multi-Mirror Fallback** (42 services - recommended)

```dockerfile
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt
```

**Pattern B: Aliyun Mirror Only** (20 services)

```dockerfile
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

**Pattern C: No Mirror** (1 service - not recommended)

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

### pip.conf (AI Base Image)

```ini
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               pypi.org
               files.pythonhosted.org
               download.pytorch.org
[install]
prefer-binary = true
```

### Available Pip Mirrors

| Mirror | URL | Region |
| ------ | --- | ------ |
| Official PyPI | `https://pypi.org/simple` | Global |
| Alibaba Cloud | `https://mirrors.aliyun.com/pypi/simple/` | Asia (primary) |
| Tsinghua University | `https://pypi.tuna.tsinghua.edu.cn/simple/` | Asia (secondary) |
| Tencent Cloud | `https://mirrors.cloud.tencent.com/pypi/simple` | Asia (tertiary) |
| PyTorch CUDA | `https://download.pytorch.org/whl/cu121` | GPU services only |

### Constraints Files

| File | Purpose |
| ---- | ------- |
| `constraints.txt` | Platform-wide version constraints (100+ packages) |
| `docker/constraints-ai.txt` | AI service version pins with CVE patches |

Usage: `pip install --no-cache-dir -c constraints.txt -r requirements.txt`

### NPM Mirror (Node.js Services)

```dockerfile
RUN npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps || \
    (npm config set registry https://registry.npmjs.org && npm install --legacy-peer-deps)
```

### Docker Security Pattern

All services follow:
- Non-root user `sahool` (UID 1000)
- Read-only filesystem where possible
- Multi-stage builds (35+ services)
- HEALTHCHECK directives

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

### Mobile Apps

| App | Location | Description |
| --- | -------- | ----------- |
| sahool_field_app | `apps/mobile/sahool_field_app/` | Main field operations app |
| sahol_atmosphere | `apps/mobile/sahol_atmosphere/` | Companion weather/atmosphere app |

### Offline-First Pattern

- Use Drift for local SQLite database with SQLCipher 256-bit AES encryption
- Secure key storage via flutter_secure_storage (Android Keystore / iOS Keychain)
- Background sync with Workmanager
- Conflict resolution for offline edits (ETag-based, schema v4)
- Certificate pinning for secure connections (3-tier: production, staging, development)

### Mobile Security Features

- **Certificate Pinning**: 3 production domains configured (api.sahool.app, ws.sahool.app, *.sahool.io)
- **Device Integrity**: Root/jailbreak detection via safe_device
- **Screen Security**: Screenshot prevention via secure_application
- **Biometric Auth**: local_auth for fingerprint/face authentication
- **Request Signing**: HMAC signing for API requests

### File Structure

```
lib/
├── core/
│   ├── ai/                 # AI utilities
│   ├── api/                # API client & interceptors
│   ├── auth/               # JWT, 2FA authentication
│   ├── http/               # Dio client, retry, rate limiter
│   ├── offline/            # Offline-first sync engine
│   ├── security/           # Certificate pinning, device integrity
│   ├── storage/            # Drift database + SQLCipher encryption
│   ├── sync/               # Background sync
│   ├── notifications/      # Push & local notifications
│   ├── voice/              # Speech-to-text, TTS
│   ├── websocket/          # Real-time updates
│   └── ...                 # config, geo, map, ml, theme, etc.
├── features/               # 57 feature modules
│   ├── field/              # Core field operations
│   ├── irrigation/         # Irrigation management
│   ├── crop_health/        # Crop health monitoring
│   ├── ndvi/               # NDVI analysis
│   ├── advisor/            # Agricultural advisory
│   ├── marketplace/        # Marketplace
│   ├── chat/               # Field chat
│   ├── equipment/          # Equipment tracking
│   ├── ai_advisor/         # AI advisory
│   ├── astronomical_calendar/ # Islamic calendar
│   └── ...                 # 48+ more feature modules
├── l10n/                   # Localization (Arabic/English)
└── main.dart               # Entry point
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

- **Minimum**: 25% code coverage (enforced in CI via `fail_under = 25`)
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
| `tests/load/`        | Load tests (k6, Locust)    |
| `tests/evaluation/`  | AI agent evaluation        |
| `tests/guardrails/`  | Input validation tests     |
| `tests/a2a/`         | Agent-to-Agent tests       |
| `tests/container/`   | Docker container tests     |
| `tests/database/`    | Database-specific tests    |
| `tests/frontend/`    | React component tests      |
| `tests/middleware/`   | Middleware tests           |
| `tests/simulation/`  | Simulation tests           |
| `tests/security/`    | Security-focused tests     |
| `tests/golden-datasets/` | Golden test datasets   |
| `tests/factories/`   | Test data factories        |
| `tests/snapshots/`   | Snapshot comparisons       |
| `tests/utils/`       | Test helper utilities      |

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
GET /healthz         # Liveness probe (most services)
GET /readyz          # Readiness probe (most services)
GET /health          # Combined status (some services)
GET /metrics         # Prometheus metrics (some services)
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

### Unified API Contracts

All service ports, error codes, and API endpoints are defined in a single source of truth:

```
packages/shared-types/src/contracts/
├── index.ts              # CONTRACT_VERSION (semver), barrel export
├── service-ports.ts      # SERVICE_PORTS, SERVICE_PORT_ALIASES
├── error-codes.ts        # ERROR_CODES, ERROR_MESSAGES (bilingual EN/AR)
├── api-endpoints.ts      # *_ENDPOINTS constants, buildUrl() helper
└── api-responses.ts      # Unified response shapes (ApiResponse, PaginatedResponse)
```

**Import convention** (enforced by ESLint `no-restricted-imports`):

```typescript
// Correct - import from unified contracts
import { SERVICE_PORTS, AUTH_ENDPOINTS, buildUrl } from "@sahool/shared-types/contracts";

// Incorrect - do not define local port/error constants
const AUTH_PORT = 3025; // ❌ Use SERVICE_PORTS.AUTH instead
```

**Dart (Mobile)**: Generated from TypeScript via `npx tsx scripts/sync-contracts-to-dart.ts`. Located in `apps/mobile/lib/core/contracts/`. Do NOT edit Dart contract files manually.

**CONTRACT_VERSION**: Follows semver. Bump on every contract change:
- **Patch** (1.0.x): New additive constants (new port, new error code)
- **Minor** (1.x.0): New contract modules or structural additions
- **Major** (x.0.0): Removed/renamed exports (breaking change)

### Contract Deprecation Policy

When deprecating a contract constant (port, error code, or endpoint):

1. **Add to `SERVICE_PORT_ALIASES`** (or equivalent alias map) mapping old name → new name
2. **Add `@deprecated` JSDoc tag** with migration target and sunset version
3. **Bump `CONTRACT_VERSION`** minor version
4. **Update Dart codegen** to include deprecation annotations
5. **Allow 2 minor versions** before removing the deprecated constant
6. **CI guard** (`api-contracts-guard.yml`) will flag removed exports as breaking changes

Example:
```typescript
/** @deprecated Use SERVICE_PORTS.FIELD_MANAGEMENT instead. Removal: v2.0.0 */
export const SERVICE_PORT_ALIASES = {
  FIELD_CORE: "FIELD_MANAGEMENT",
  FIELD_SERVICE: "FIELD_MANAGEMENT",
} as const;
```

### Rate Limiting Tiers

| Tier       | Requests/min | Requests/hour |
| ---------- | ------------ | ------------- |
| Starter    | 30           | 500           |
| Professional | 60         | 2000          |
| Enterprise | 120          | 5000          |
| Research   | 120          | 10000         |
| Internal   | 1000         | 50000         |

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
# Python - using subject constants
from shared.events.subjects import SAHOOL_FIELD_CREATED
await app.state.nc.publish(
    SAHOOL_FIELD_CREATED,  # "sahool.field.created"
    json.dumps({"field_id": field_id, "tenant_id": tenant_id}).encode()
)

# Tenant-scoped event
from shared.events.subjects import get_tenant_subject
subject = get_tenant_subject(tenant_id, "field", "created")
await app.state.nc.publish(subject, payload)
```

### Logging (Structured JSON)

```python
import structlog
logger = structlog.get_logger()
logger.info("event_name", field_id=field_id, action="create")
```

### Ruff Configuration

The project uses Ruff for Python linting and formatting (configured in `pyproject.toml`):

- **Line length**: 120 characters
- **Target**: Python 3.11
- **Complexity threshold**: 20 (McCabe, relaxed for AI/RAG services)
- **Selected rules**: `E, F, I, UP, B, SIM, N, W, C4, C90`
- **Excluded dirs**: `archive/`, `idp/templates/`, `.git`, `.venv`, `__pycache__`

---

## Important Files Reference

| File                            | Purpose                                     |
| ------------------------------- | ------------------------------------------- |
| `Makefile`                      | All development commands (~140 targets)      |
| `docker-compose.yml`            | Full service stack (main)                    |
| `docker-compose.test.yml`       | Testing environment                          |
| `docker-compose.prod.yml`       | Production configuration                     |
| `docker-compose.ha.yml`         | High Availability setup                      |
| `docker-compose.redis-ha.yml`   | Redis Cluster HA                             |
| `docker-compose.telemetry.yml`  | OpenTelemetry stack                          |
| `docker-compose.tls.yml`        | TLS/SSL configuration                        |
| `docker-compose.walg.yml`       | Backup/recovery (WAL-G)                      |
| `docker/docker-compose.dlq.yml` | Dead Letter Queue configuration             |
| `docker/docker-compose.iot.yml` | IoT services                                |
| `docker/docker-compose.secrets.yml` | Secrets management                       |
| `docker/docker-compose.infra.yml` | Infrastructure-only services               |
| `pyproject.toml`                | Python config, Ruff, pytest, MyPy            |
| `package.json`                  | Node.js root workspace (25 packages + services) |
| `.env.example`                  | Environment template                         |
| `governance/services.yaml`      | Service registry v3.2.0 (source of truth)    |
| `governance/agents.yaml`        | AI agent definitions (11 categories)         |
| `shared/errors_py.py`           | Unified error handling for FastAPI            |
| `shared/logging_config.py`      | Structured logging configuration             |

---

## Governance

The `governance/` directory maintains the platform's service registry and agent definitions:

| File | Version | Purpose |
|------|---------|---------|
| `services.yaml` | 3.2.0 | Service registry - single source of truth for all microservices |
| `agents.yaml` | 16.0.0 | AI agent definitions (11 categories, A2A protocol-compliant) |
| `credentials.template.yaml` | - | Credential template for service configuration |
| `DEDUP_MATRIX.md` | - | Service deduplication matrix |

### Agent Categories (defined in `agents.yaml`)

intelligence, advisory, analysis, monitoring, security, iot, precision, sustainability, market, social, operations

### Governance Subdirectories

- `decisions/` - Architecture Decision Records (ADRs)
- `design/` - Design patterns and standards
- `events/` - Event definitions and schemas
- `policies/` - Security and operational policies
- `reliability/` - Reliability patterns
- `schemas/` - Data schemas
- `templates/` - Configuration templates

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

GitHub Workflows (49):

- **Core CI/CD**: `ci.yml`, `test.yml`, `release.yml`, `release-candidate.yml`
- **Specialized CI**: `ci-yolo26-vision.yml`, `ci-terrain-services.yml`, `ci-edge-orchestrator.yml`, `ci-ai-rag-security.yml`
- **Deployment**: `cd-production.yml`, `cd-staging.yml`, `cd-new-services.yml`, `canary-deploy.yml`, `blue-green-deploy.yml`
- **Testing**: `frontend-tests.yml`, `container-tests.yml`, `e2e-tests.yml`, `load-testing.yml`, `load-test-validation.yml`
- **Security**: `security-checks.yml`, `codeql-analysis.yml`, `security-audit.yml`, `security.yml`
- **Governance**: `event-contracts-guard.yml`, `governance-validation.yml`, `governance-ci.yml`, `governance-structure.yml`
- **Contracts**: `api-contracts-guard.yml`
- **Quality**: `quality-gates.yml`, `advanced-quality.yml`, `skills-tests.yml`
- **Frontend/Mobile**: `frontend-ci.yml`, `flutter-apk.yml`, `mobile-ci.yml`, `mobile-release.yml`
- **Infrastructure**: `docker-buildx.yml`, `docker-image.yml`, `infra-sync.yml`
- **AI/Evaluation**: `agent-evaluation.yml`
- **PR Automation**: `auto-merge-prs.yml`, `pr-status-monitor.yml`
- **Docs/Preview**: `docs.yml`, `lighthouse-ci.yml`, `deploy-preview.yml`, `vercel-preview.yml`, `playwright-e2e.yml`
- **Other**: `notifications.yml`, `scorecard.yml`, `reusable-setup.yml`, `generator-guard.yml`

---

## Deprecated Services

### Overview

Total deprecated: **15 services** (all archived).
All deprecated services emit HTTP headers (RFC 8594): `X-API-Deprecated: true`, `X-API-Sunset`, `Deprecation: true`.
Active-deprecated services require `--profile deprecated` to start.

```
DEPRECATION WARNING: [service] is DEPRECATED
This service has been migrated to [new-service]
```

### Archived Services (15) - Moved to `archive/deprecated-services/`

| Deprecated Service   | Replaced By                   | Deprecation Date | Sunset Date |
| -------------------- | ----------------------------- | ---------------- | ----------- |
| `satellite-service`  | `vegetation-analysis-service` | 2025-01-01       | 2025-06-01  |
| `weather-advanced`   | `weather-service`             | 2025-01-01       | 2025-06-01  |
| `crop-health-ai`     | `crop-intelligence-service`   | 2025-01-01       | 2025-06-01  |
| `crop-health`        | `crop-intelligence-service`   | 2026-01-06       | 2026-06-01  |
| `fertilizer-advisor` | `advisory-service`            | 2025-01-01       | 2025-06-01  |
| `field-ops`          | `field-management-service`    | 2026-01-06       | v17.0.0     |
| `field-core`         | `field-management-service`    | Legacy           | v17.0.0     |
| `field-service`      | `field-management-service`    | Legacy           | v17.0.0     |
| `agro-advisor`       | `advisory-service`            | 2025-01-06       | 2026-02     |
| `ndvi-engine`        | `vegetation-analysis-service` | 2026-01-06       | 2026-02     |
| `weather-core`       | `weather-service`             | Implicit         | 2026-02     |
| `community-chat`     | `chat-service`                | 2026-01-15       | 2026-02     |
| `field-chat`         | `chat-service`                | 2026-01-15       | 2026-02     |
| `ndvi-processor`     | `vegetation-analysis-service` | 2026-01-15       | 2026-02     |
| `yield-engine`       | `yield-prediction-service`    | 2026-01-15       | 2026-02     |

### Migration Documentation

| Guide | Location |
| ----- | -------- |
| Field-Ops Migration | `docs/migrations/FIELD_OPS_MIGRATION_SUMMARY.md` |
| Agro-Advisor Migration | `docs/migrations/AGRO_ADVISOR_MIGRATION_SUMMARY.md` |
| Deduplication Matrix | `governance/DEDUP_MATRIX.md` |
| Deprecation Summary | `apps/services/DEPRECATION_SUMMARY.md` |
| Archive Index | `archive/deprecated-services/README.md` |

### Running Deprecated Services (Testing Only)

```bash
# Default: deprecated services NOT started
docker-compose up

# Enable deprecated services for migration testing
docker-compose --profile deprecated up
docker-compose --profile legacy up
```

---

## Key Services Overview

**Platform Totals**: 71 microservices (active service directories) + 4 applications (admin, web, mobile, kernel), 15 archived

### Service Status Summary

| Status | Count | Description |
| ------ | ----- | ----------- |
| Active | 71 | Service directories in apps/services/ |
| Archived | 15 | Deprecated and moved to archive (see Deprecated Services) |

### Applications

| Application | Type | Framework | Version | LOC | Status |
| ----------- | ---- | --------- | ------- | --- | ------ |
| admin | Frontend | React/Next.js | 16.0.0 | 35,367 | Active |
| web | Frontend | React/Next.js | 16.0.0 | 93,769 | Active |
| mobile | Mobile | Flutter 3.27.x | 16.0.0+1 | 335,301 | Active |
| kernel | Backend | Python 3.11 | 16.0.0 | 26,253 | Active |

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
| provider-config            | Python  | 8104 | Provider configuration           |
| audit-service              | Python  | 8114 | Audit logging                    |

### Analytics & Intelligence

| Service                      | Type    | Port | Description                    |
| ---------------------------- | ------- | ---- | ------------------------------ |
| vegetation-analysis-service  | Python  | 8090 | Satellite imagery analysis     |
| crop-intelligence-service    | Python  | 8095 | Crop health AI                 |
| indicators-service           | Python  | 8091 | Field indicators computation   |
| ndvi-processor               | Python  | 8118 | NDVI processing (deprecating)  |
| field-intelligence           | Python  | 8120 | Field analytics                |
| lai-estimation               | Node.js | 3022 | Leaf Area Index estimation     |
| skills-service               | Python  | 8121 | Farmer skills assessment       |
| soil-analysis-service        | Python  | 8134 | Soil analysis                  |
| pest-detection-service       | Python  | 8125 | Pest detection AI              |
| digital-twin-engine          | Python  | 8253 | Digital twin simulation        |
| yield-prediction-service     | Node.js | 8152 | Yield prediction ML (NestJS)   |

### Decision & Advisory

| Service                  | Type    | Port | Description                  |
| ------------------------ | ------- | ---- | ---------------------------- |
| crop-growth-model        | Node.js | 3023 | Crop growth simulation       |
| advisory-service         | Python  | 8093 | Advisory & recommendations   |
| irrigation-smart         | Python  | 8094 | Smart irrigation             |
| yield-prediction         | Node.js | 3021 | Yield prediction (legacy)    |
| agro-rules               | Python  | 8151 | Agronomic rules engine       |

### Integration & IoT

| Service               | Type    | Port | Description                  |
| --------------------- | ------- | ---- | ---------------------------- |
| iot-service           | Node.js | 8117 | IoT device management        |
| iot-gateway           | Python  | 8106 | IoT protocol gateway         |
| iot-sensor-hub        | Python  | 8251 | IoT sensor hub               |
| weather-service       | Python  | 8092 | Weather data                 |
| virtual-sensors       | Python  | 8119 | Virtual sensor computation   |
| ws-gateway            | Python  | 8081 | WebSocket gateway            |
| mcp-server            | Python  | 8201 | Model Context Protocol (skeleton) |
| astronomical-calendar | Python  | 8111 | Islamic calendar & timings   |
| drone-service         | Python  | 8126 | Drone integration (skeleton) |
| ussd-gateway          | Python  | 8183 | USSD gateway                 |
| whatsapp-bot-service  | Python  | 8240 | WhatsApp bot integration     |

### Community & Business

| Service              | Type    | Port | Description              |
| -------------------- | ------- | ---- | ------------------------ |
| marketplace-service  | Node.js | 3010 | Agricultural marketplace |
| chat-service         | Node.js | 8000 | Real-time messaging      |
| research-core        | Node.js | 3015 | Research trials          |
| disaster-assessment  | Node.js | 3020 | Disaster risk assessment |
| inventory-service    | Python  | 8116 | Inventory management     |
| cooperative-service  | Python  | 8127 | Cooperative management (skeleton) |
| crm-service          | Python  | 8131 | Farmer CRM               |
| logistics-service    | Python  | 8167 | Logistics management     |
| supply-chain-service | Python  | 8230 | Supply chain management  |
| traceability-service | Python  | 8123 | Product traceability (skeleton) |
| globalgap-compliance | Python  | 8128 | GlobalGAP compliance     |
| wechat-service       | Python  | 8133 | WeChat integration       |

### AI & Agents

| Service                  | Type    | Port | Description                 |
| ------------------------ | ------- | ---- | --------------------------- |
| agent-registry           | Python  | 8160 | Agent registry service      |
| code-fix-agent           | Python  | 8162 | Code fix AI agent           |
| code-review-agent        | Node.js | 8145 | Code review agent (NestJS)  |
| code-review-service      | Python  | 8102 | Code review service         |
| ai-advisor               | Python  | 8112 | AI advisory service         |
| ai-agents-core           | Python  | 8161 | AI agents core module       |
| ai-agents-service        | Python  | 8130 | AI agents service           |
| ai-chat-assistant        | Python  | 8260 | AI chat assistant           |
| llm-orchestrator-service | Python  | 8164 | LLM orchestration           |
| copilot-api              | Python  | 8088 | AI copilot (multi-LLM, RAG) |
| knowledge-graph          | Python  | 8140 | Knowledge graph service     |

### Vision, Terrain & Edge Services

| Service                    | Type   | Port | Description                                        |
| -------------------------- | ------ | ---- | -------------------------------------------------- |
| yolo26-vision-service      | Python | 8150 | YOLO26 computer vision for pest/disease/weed detection |
| ground-vision-service      | Python | 8182 | Ground-level vision analysis                       |
| terrain-core-service       | Python | 8185 | DEM processing and terrain analysis                |
| hydrology-service          | Python | 8165 | Hydrology and drainage analysis                    |
| leveling-optimizer-service | Python | 8170 | Field leveling optimization                        |
| edge-orchestrator-service  | Python | 8180 | Edge device management (Jetson Orin)               |

### Specialized & Domain Services

| Service                   | Type    | Port | Description                      |
| ------------------------- | ------- | ---- | -------------------------------- |
| fertigation-engine        | Python  | 8252 | Fertigation management           |
| irrigation-cycle-engine   | Python  | 8250 | Irrigation cycle optimization    |
| digital-twin-engine       | Python  | 8253 | Digital twin simulation          |
| lowcode-engine            | Python  | 8132 | Low-code workflow automation     |
| demo-data                 | Python  | 8261 | Demo data generator              |

---

## YOLO26 Vision Service

The YOLO26 Vision Service (`apps/services/yolo26-vision-service/`) is a production-grade computer vision microservice for agricultural pest, disease, and weed detection. Port **8150**.

### Architecture

```
FastAPI Application Layer
├── Detection Endpoints (pest, disease, weed)
├── Analysis Endpoints (counting, ripeness, segmentation, tracking)
├── Batch Endpoints (multi-image processing)
└── Model Management Endpoints (version registry)
    ↓
Model Manager & Inference Engine
├── YOLO26 Model Loader (5 variants: n/s/m/l/x)
├── LRU Cache (5 models max in-memory)
├── TensorRT Optimization (optional)
└── GPU Memory Management (FP16 half-precision)
    ↓
External Integrations (Optional)
├── PostgreSQL (asyncpg), Redis, NATS
└── NVIDIA GPU (CUDA 12.1)
```

### Model Variants

| Variant | Size | Parameters | GPU VRAM | Latency (RTX 3090) | mAP@0.5 | Best For |
| ------- | ---- | ---------- | -------- | ------------------- | ------- | -------- |
| Nano (n) | 6.5 MB | 3.2M | 512 MB | 2.2 ms | 0.78 | Edge devices, real-time |
| Small (s) | 22 MB | 11.2M | 1024 MB | 3.6 ms | 0.84 | Balanced |
| **Medium (m)** | 49 MB | 25.9M | 2048 MB | 5.5 ms | 0.88 | **Default** |
| Large (l) | 85 MB | 43.7M | 3072 MB | 8.3 ms | 0.91 | High accuracy |
| XLarge (x) | 131 MB | 68.2M | 4096 MB | 12.5 ms | 0.93 | Research |

### Detection Tasks (7 Total)

| Task | Classes | Description |
| ---- | ------- | ----------- |
| Pest Detection | 22 species | Red Palm Weevil, aphid, whitefly, locust, etc. |
| Disease Detection | 34 diseases | Wheat rust, blight, fusarium, nutrient deficiency, etc. |
| Weed Detection | 12 species | Wild oat, bermuda grass, bindweed, nutsedge, etc. |
| Plant Counting | 1 class | Grid-based density mapping with GSD support |
| Ripeness Classification | 5 stages | Unripe → early ripe → half ripe → ripe → overripe |
| Leaf Segmentation | 1 class | Instance segmentation, LAI calculation |
| Object Tracking | Generic | ByteTrack/BoT-SORT with persistent IDs |

### API Endpoints

```
# Detection (Single Image)
POST /api/v1/detect/pest       # Pest detection with severity & recommendations
POST /api/v1/detect/disease    # Disease detection with affected area %
POST /api/v1/detect/weed       # Weed detection with coverage %

# Analysis
POST /api/v1/count/plants           # Plant counting with density map
POST /api/v1/classify/ripeness      # 5-stage fruit ripeness
POST /api/v1/segment/leaf           # Leaf segmentation + LAI
POST /api/v1/track/objects          # Object tracking (ByteTrack/BoT-SORT)
DELETE /api/v1/track/{tracker_id}   # Clear tracking session

# Batch Processing
POST /api/v1/batch/detect/pest     # Batch pest detection
POST /api/v1/batch/detect/disease  # Batch disease detection
GET  /api/v1/batch/status          # Queue status
GET  /api/v1/batch/cache/stats     # Cache statistics

# Model Management
GET  /api/v1/models/versions                   # List all model versions
GET  /api/v1/models/{variant}/info             # Model info
POST /api/v1/models/warmup                     # Preload models
GET  /api/v1/models/loaded                     # Currently loaded models
POST /api/v1/models/register                   # Register new version
GET  /api/v1/models/compare/{task}/{v1}/{v2}   # Compare versions

# Health & Metrics
GET  /healthz, /readyz, /health, /metrics
```

### Key Dependencies

| Package | Version | Purpose |
| ------- | ------- | ------- |
| torch | 2.2.0 (CUDA 12.1) | Deep learning framework |
| torchvision | 0.17.0 | Vision transformations |
| ultralytics | 8.1.0-9.0.0 | YOLO model framework |
| opencv-python-headless | 4.8.0-5.0.0 | Image processing |
| asyncpg | 0.29.0-0.31.0 | PostgreSQL async driver |
| nats-py | 2.6.0-3.0.0 | NATS event publishing |
| redis | 7.1.0-8.0.0 | Result caching |
| tenacity | 8.2.0-9.0.0 | Retry with backoff |
| onnxruntime-gpu | 1.16.0-2.0.0 | ONNX inference (x86_64) |

### Dockerfile (5 Stages)

| Stage | Base Image | Purpose |
| ----- | ---------- | ------- |
| base | `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` | CUDA runtime + Python 3.11 |
| builder | (inherits base) | venv, pip install with 3-tier mirror |
| **production** | (inherits base) | Runtime, non-root user, healthcheck |
| development | (inherits production) | Debug tools, hot-reload |
| cpu-only | `python:3.11-slim-bookworm` | CPU variant (no CUDA) |

### NATS Events Published

| Event Subject | Trigger |
| ------------- | ------- |
| `sahool.vision.pest_detected` | Pest detection |
| `sahool.vision.disease_detected` | Disease detection |
| `sahool.vision.weed_detected` | Weed detection |
| `sahool.vision.critical_alert` | Critical pest (RPW, locust) |
| `sahool.vision.plant_count_completed` | Plant counting |
| `sahool.vision.analysis_completed` | Analysis (ripeness, segmentation) |
| `sahool.vision.analysis_started` | Analysis started |
| `sahool.vision.analysis_failed` | Analysis failed |

### Error Handling (26 Codes)

| Category | HTTP | Codes | Examples |
| -------- | ---- | ----- | -------- |
| Validation | 400 | E1001-E1006 | Invalid format, file too large |
| Model | 503 | E2001-E2005 | Model not found, inference failed |
| Processing | 400 | E3001-E3004 | Image decode, batch failed |
| Resource | 503 | E4001-E4004 | GPU OOM, max concurrent |
| External | 502 | E5001-E5003 | DB error, cache error |
| Rate Limit | 429 | E6001-E6002 | Rate/quota exceeded |
| Timeout | 504 | E7001-E7002 | Inference/request timeout |
| Auth | 401 | E8001-E8003 | Invalid/expired token |

All error responses are bilingual (Arabic/English) with circuit breaker and retry patterns.

### Environment Variables

```bash
# Core
ENVIRONMENT=production          # development|staging|production|test
PORT=8150
HOST=0.0.0.0

# GPU
DEVICE=cuda:0                   # cuda:0|cuda:1|cpu
HALF_PRECISION=true             # FP16 optimization
ENABLE_TENSORRT=false

# Model
MODEL_BASE_PATH=/app/models
DEFAULT_MODEL_VARIANT=m         # n|s|m|l|x
MODEL_CACHE_SIZE=5              # Max models in memory

# Inference
DEFAULT_CONFIDENCE_THRESHOLD=0.25
DEFAULT_IOU_THRESHOLD=0.45
MAX_DETECTIONS=300
DEFAULT_IMAGE_SIZE=640

# Upload
MAX_UPLOAD_SIZE_MB=50

# Database (optional)
DATABASE_URL=postgresql://...
NATS_URL=nats://nats:4222
REDIS_URL=redis://redis:6379
```

---

## Platform Integrations

The SAHOOL platform includes integrations with external tools and libraries for enhanced agricultural intelligence.

### Architecture Overview

```
shared/
├── nlp/                         # Arabic NLP (AraBERT)
│   ├── __init__.py
│   └── arabic_nlp.py           # Intent classification, NER, sentiment
├── satellite/                   # Satellite Imagery (Sentinel Hub)
│   ├── __init__.py
│   └── sentinel_ndvi.py        # NDVI analysis, crop health
├── ml/                          # Agricultural ML (AgML)
│   ├── __init__.py
│   └── agml_integration.py     # Dataset management, disease detection
└── agents/                      # Multi-Agent (CrewAI)
    ├── __init__.py
    └── crewai_orchestrator.py  # Agent orchestration
```

### Arabic NLP Integration (`shared/nlp/`)

Uses AraBERT for Arabic-first natural language processing.

#### Features

| Feature | Description |
|---------|-------------|
| **Intent Classification** | Detects agricultural intents (irrigation, disease, fertilizer, pest, weather, yield) |
| **Named Entity Recognition** | Extracts crops, diseases, pests, fertilizers, quantities |
| **Sentiment Analysis** | Analyzes farmer feedback sentiment and urgency |
| **Text Preprocessing** | Arabic normalization, diacritics removal |

#### Usage Example

```python
from shared.nlp import ArabicNLPProcessor

processor = ArabicNLPProcessor()
await processor.initialize()

result = processor.process("القمح يعاني من اصفرار الأوراق")
print(result["intent"])      # {"primary": "crop_disease", "confidence": 0.85}
print(result["entities"])    # [{"text": "القمح", "type": "crop"}]
print(result["is_arabic"])   # True
```

#### Supported Intents

| Intent | Arabic | English |
|--------|--------|---------|
| `crop_disease` | مرض المحصول | Crop disease |
| `irrigation` | الري | Irrigation |
| `fertilizer` | السماد | Fertilizer |
| `pest` | الآفات | Pests |
| `weather` | الطقس | Weather |
| `yield` | الإنتاجية | Yield |

### Satellite NDVI Integration (`shared/satellite/`)

Uses Sentinel Hub for free satellite imagery analysis.

#### Features

| Feature | Description |
|---------|-------------|
| **NDVI Analysis** | Normalized Difference Vegetation Index |
| **LAI Estimation** | Leaf Area Index calculation |
| **Time Series** | Historical trend analysis |
| **Crop Health** | Automatic health status classification |

#### Usage Example

```python
from shared.satellite import SentinelNDVIAnalyzer, FieldBoundary

analyzer = SentinelNDVIAnalyzer()
await analyzer.initialize()

field = FieldBoundary(
    field_id="FIELD-001",
    coordinates=[(46.7, 24.7), (46.8, 24.7), (46.8, 24.8), (46.7, 24.8)],
    area_hectares=10.0
)

result = await analyzer.get_ndvi(field)
print(result.mean_value)       # 0.65
print(result.health_status)    # "healthy"
print(result.health_status_ar) # "صحي"
```

#### Health Status Classification

| NDVI Range | Status | Status (AR) |
|------------|--------|-------------|
| ≥ 0.6 | healthy | صحي |
| 0.4 - 0.6 | moderate | معتدل |
| 0.2 - 0.4 | stressed | مجهد |
| < 0.2 | critical | حرج |

### Agricultural ML Integration (`shared/ml/`)

Uses AgML for standardized agricultural ML datasets.

#### Available Datasets

| Dataset | Crop | Classes | Images |
|---------|------|---------|--------|
| PlantVillage | General | 38 | 54,306 |
| Wheat Rust | Wheat | 4 | 1,400 |
| Rice Disease | Rice | 5 | 3,355 |
| Tomato Disease | Tomato | 10 | 18,160 |
| Corn Disease | Corn | 4 | 4,188 |
| DeepWeeds | General | 9 | 17,509 |

#### Usage Example

```python
from shared.ml import AgMLDatasetManager, DatasetType, CropType

manager = AgMLDatasetManager()
await manager.initialize()

# List datasets for wheat
datasets = manager.list_datasets(crop_type=CropType.WHEAT)

# Get disease classes
diseases = manager.get_disease_classes(CropType.WHEAT)
# [{"en": "Leaf Rust", "ar": "صدأ الأوراق"}, ...]
```

### Multi-Agent Integration (`shared/agents/`)

Uses CrewAI for simpler multi-agent orchestration.

#### Available Agents

| Role | Goal (EN) | Goal (AR) |
|------|-----------|-----------|
| `crop_advisor` | Crop management advice | نصائح إدارة المحاصيل |
| `irrigation_expert` | Optimize irrigation | تحسين الري |
| `disease_diagnostician` | Diagnose diseases | تشخيص الأمراض |
| `pest_controller` | IPM solutions | حلول الإدارة المتكاملة |
| `soil_analyst` | Soil analysis | تحليل التربة |
| `yield_predictor` | Yield prediction | تنبؤ الإنتاجية |
| `market_analyst` | Market prices | أسعار السوق |
| `coordinator` | Coordinate specialists | تنسيق المتخصصين |

#### Usage Example

```python
from shared.agents import CrewAIOrchestrator

orchestrator = CrewAIOrchestrator()
await orchestrator.initialize()

result = await orchestrator.query("متى أسقي القمح؟")
print(result.final_answer)       # English answer
print(result.final_answer_ar)    # Arabic answer
print(result.agents_used)        # ["irrigation_expert"]
```

### LLM Orchestrator API Endpoints

All integrations are exposed via the LLM Orchestrator Service:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/integrations/nlp/process` | POST | Process text with Arabic NLP |
| `/api/v1/integrations/nlp/intent/{text}` | GET | Classify intent |
| `/api/v1/integrations/satellite/ndvi` | POST | Get field NDVI |
| `/api/v1/integrations/satellite/crop-health` | POST | Analyze crop health |
| `/api/v1/integrations/ml/datasets` | GET | List ML datasets |
| `/api/v1/integrations/ml/diseases/{crop}` | GET | Get disease classes |
| `/api/v1/integrations/crew/query` | POST | Query agent crew |
| `/api/v1/integrations/crew/agents` | GET | List available agents |

### Environment Variables

```bash
# AraBERT Configuration
ARABERT_MODEL=aubmindlab/bert-base-arabertv2
ARABERT_REVISION=main  # Pin revision for security

# Sentinel Hub Configuration (free registration)
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_CLIENT_SECRET=your_client_secret
SENTINEL_HUB_INSTANCE_ID=your_instance_id

# AgML Configuration
AGML_CACHE_DIR=/tmp/agml
```

---

## AI Auto-Fix Engine

The SAHOOL platform includes a comprehensive AI-powered code auto-fix system located in `shared/ai/` that enables automated code diagnostics, fixing, and model training capabilities.

### Architecture Overview

```
shared/ai/
├── auto_fix/                    # Auto-Fix Engine
│   ├── models.py               # Data models (Diagnostic, CodeFix, AuditEntry)
│   ├── diagnostics.py          # Multi-tool code analysis
│   ├── fixers.py               # Automated code fixing
│   └── engine.py               # Main orchestration engine
├── context_engineering/         # Context Engineering
│   ├── compression.py          # Token compression
│   ├── memory.py               # Farm memory management
│   └── evaluation.py           # LLM-as-Judge evaluation
├── agents/                      # CrewAI multi-agent orchestration
├── orchestration/               # Multi-agent consensus & swarm intelligence
├── guardrails/                  # AI safety (input/output filtering, policy)
├── models_registry/             # Agricultural AI models registry (50+ models)
├── ultrarag/                    # Advanced RAG system
├── diffusion/                   # Image generation capabilities
├── ollama_client.py            # Local LLM integration via Ollama
├── model_training.py           # Model fine-tuning & evaluation
├── audit.py                    # AI audit logging with cost tracking
├── circuit_breaker.py          # Resilience pattern for services
├── metrics.py                  # Prometheus-compatible metrics
├── llm_provider.py             # Multi-provider LLM (Ollama, Claude, OpenAI, Gemini, DeepSeek)
├── code_llm_provider.py        # Code-specialized LLM (completion, review, fix)
├── huggingface_provider.py     # Arabic & multilingual embeddings
├── validation.py               # Input/output validation
├── embeddings.py               # Unified embedding providers
├── ot_embeddings.py            # OpenTelemetry-instrumented embeddings
├── vector_store.py             # Persistent vector database for RAG
├── crop_vision.py              # Computer vision for disease/pest detection
├── explainability.py           # Recommendation explanations
├── feedback.py                 # User feedback collection
├── experience_learning.py      # Self-learning agents with SOP generation
├── graph_memory.py             # Graph-based memory with ECL pipeline
├── grpo_trainer.py             # Group Relative Policy Optimization trainer
├── hardware_optimizer.py       # Hardware resource optimization
├── quality_orchestrator.py     # Quality assurance orchestration
├── tool_registry.py            # Tool management and guardrails
└── observability.py            # AI-specific observability metrics
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
| `mistral:7b` | 7B | General code tasks |
| `llama2:7b` | 7B | Code generation |
| `qwen2.5-coder:7b` | 7B | Multi-language code |

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

## Shared Agricultural Domain Modules

The `shared/` directory contains 65+ Python modules organized by domain. Below is the complete listing:

### Core Infrastructure

| Module | Purpose |
|--------|---------|
| `auth/` | Authentication (JWT, 2FA, token revocation) |
| `cache/` | Caching layer (Redis Sentinel HA) |
| `contracts/` | API contracts & event schemas |
| `db/` | Database utilities |
| `domain/` | Domain models (auth, users, tenancy) |
| `events/` | NATS event definitions & DLQ |
| `file_validation/` | File upload validation & virus scanning |
| `guardrails/` | AI safety guardrails |
| `libs/` | Shared libraries (outbox, audit, caching) |
| `middleware/` | HTTP middleware (rate limiting, CORS, logging) |
| `monitoring/` | Prometheus metrics & SLI/SLO |
| `observability/` | OpenTelemetry, Jaeger tracing |
| `security/` | RBAC, JWT, policy engine |
| `secrets/` | HashiCorp Vault integration |
| `telemetry/` | Distributed tracing |
| `versioning/` | API versioning utilities |
| `notification_preferences/` | Notification preference management |
| `audit_trail/` | Audit trail utilities |
| `service_enhancements/` | Service improvement modules |
| `design-system/` | Design system tokens and utilities |
| `templates/` | Configuration/code templates |
| `integrations/` | External system integrations |
| `python-lib/` | Python library utilities |

### AI & Intelligence

| Module | Purpose |
|--------|---------|
| `ai/` | AI utilities, Auto-Fix Engine, context engineering |
| `a2a/` | Agent-to-Agent protocol (Linux Foundation) |
| `agents/` | CrewAI multi-agent orchestration |
| `llm/` | LLM provider config & routing |
| `mcp/` | Model Context Protocol |
| `nlp/` | Arabic NLP (AraBERT) |
| `satellite/` | Sentinel Hub NDVI integration |
| `ml/` | AgML agricultural datasets |
| `crm/` | Farmer CRM module |

### Crop & Field Management

| Module | Purpose |
|--------|---------|
| `agri_calendar/` | Agricultural calendar, Islamic calendar integration, planting/harvest timing |
| `crop_rotation/` | Crop rotation planning for soil health optimization |
| `field_boundaries/` | Field geometry, geospatial operations (PostGIS, Shapely) |
| `geofencing/` | Geofence-based alerts and field access monitoring |
| `terrain/` | DEM processing, terrain analysis, batch processing |
| `harvest_quality/` | Post-harvest grading, pricing, quality assessment |

### Irrigation & Water

| Module | Purpose |
|--------|---------|
| `irrigation/` | Smart irrigation scheduling, collaborative engine, checklists |
| `water_management/` | Water usage monitoring, efficiency reporting |
| `ml_irrigation/` | ML-based irrigation optimization and prediction |
| `salinity/` | Soil salinity monitoring and mitigation |

### Soil & Nutrients

| Module | Purpose |
|--------|---------|
| `soil_testing/` | Soil test interpretation and recommendations |
| `soil_sensors/` | IoT soil sensor data processing and adapters |
| `fertilizer_management/` | Nutrient recommendations, inventory tracking |

### Pest & Disease

| Module | Purpose |
|--------|---------|
| `pest_scouting/` | Pest identification, IPM, threshold-based control |
| `pesticide_compliance/` | PHI, pesticide registration, safety alerts |
| `weather_alerts/` | Weather monitoring, spray window optimization |

### Business & Operations

| Module | Purpose |
|--------|---------|
| `mobile_sync/` | Offline-first sync, conflict resolution, delta sync |
| `batch_operations/` | Async batch processing and scheduling |
| `labor_management/` | Workforce scheduling and safety management |
| `equipment_maintenance/` | Equipment lifecycle and predictive maintenance |
| `cooperatives/` | Multi-farm cooperative resource pooling |
| `market_prices/` | Market price tracking and trend analysis |
| `traceability/` | Supply chain traceability and QR codes |
| `drone_integration/` | Drone flight planning and Variable Rate Application |
| `crop_insurance/` | Crop insurance and risk assessment |
| `farm_documents/` | Farm documentation, compliance, and alerts |
| `learning_marketplace/` | Farmer education and progress tracking |

### Advanced Technology

| Module | Purpose |
|--------|---------|
| `smart_agriculture/` | Blockchain traceability, IFTTT automation, PID controllers |
| `edge_cloud/` | Edge-cloud architecture, cooperative systems |
| `lowcode/` | Low-code/no-code workflow automation engine |
| `scraping/` | Data scraping for price and weather data |

### Regional

| Module | Purpose |
|--------|---------|
| `yemen/` | Yemen-specific crop varieties, climate, and soil data |
| `globalgap/` | GlobalGAP IFA v6 compliance checklists and API |

---

## Platform Documentation Map

The platform contains **385+ documentation files** spread across multiple directories. Here is the complete reference:

### Main Documentation (`docs/` - 385+ files)

| Directory | Files | Purpose |
| --------- | ----- | ------- |
| `docs/` (root) | 145 | Core platform docs (API, architecture, deployment, security, operations) |
| `docs/adr/` | 9 | Architectural Decision Records (ADR-001 through ADR-007) |
| `docs/api/` | 8 | API endpoint documentation (AI, auth, fields, sensors, weather) |
| `docs/architecture/` | 9 | Architecture proposals, principles, service activation maps |
| `docs/audits/` | 3 | Audit reports (security, rate limiting, secrets) |
| `docs/compliance/` | 1 | Compliance checklists |
| `docs/database/` | 3 | Database audit summaries |
| `docs/disaster-recovery/` | 3 | DR runbook and implementation guide |
| `docs/engineering/` | 2 | Engineering recovery plans |
| `docs/guides/` | 20 | Quick start guides (2FA, build, deployment, MCP, testing) |
| `docs/implementations/` | 35 | Implementation summaries (caching, DLQ, encryption, NATS, etc.) |
| `docs/infrastructure/` | 3 | Circuit breaker, Kong HA, PostGIS optimization |
| `docs/knowledge-base/` | 11 | Agricultural knowledge (crops, diseases, irrigation, monitoring) |
| `docs/migrations/` | 4 | Service migration summaries |
| `docs/proposals/` | 1 | AI code agent proposal |
| `docs/reports/` | 52 | Comprehensive audit and analysis reports |
| `docs/research/` | 4 | AI landscape, open source exploration, vision integration |
| `docs/security/` | 2 | Data classification, STRIDE threat model |
| `docs/summaries/` | 42 | Work summaries (API fixes, CI/CD, security, rate limiting) |
| `docs/tools/` | 1 | Platform tools reference |

### Key Documents Quick Reference

| Document | Path |
| -------- | ---- |
| API Gateway | `docs/API_GATEWAY.md` |
| Architecture | `docs/ARCHITECTURE_DIAGRAMS.md` |
| Deployment | `docs/DEPLOYMENT.md` |
| Security | `docs/SECURITY.md` |
| Observability | `docs/OBSERVABILITY.md` |
| Runbooks | `docs/RUNBOOKS.md` |
| Environment Variables | `docs/ENVIRONMENT_VARIABLES.md` |
| Services Map | `docs/SERVICES_MAP.md` |
| Testing | `docs/TESTING.md` |
| Troubleshooting | `docs/TROUBLESHOOTING.md` |
| Feature Flags | `docs/FEATURE_FLAGS.md` |
| Future Roadmap | `docs/FUTURE_ROADMAP.md` |
| Mobile Architecture | `docs/MOBILE_ARCHITECTURE_ANALYSIS.md` |

### Service Documentation (`apps/services-docs/` - 48 files)

Detailed per-service documentation with API endpoints, architecture, and admin integration guides.

| File | Description |
| ---- | ----------- |
| `README.md` | Master index & service registry |
| `CODING-AGENT-GUIDE.md` | AI coding agent guide for admin portal integration |
| `BUGS-AND-FIXES.md` | Known bugs and recommended fixes |
| `infrastructure.md` | PostgreSQL, PgBouncer, NATS, Kong, Redis config |
| `ollama-infrastructure.md` | Ollama LLM server setup & GPU profiles |
| `kong-routes.md` | Kong API Gateway routing configuration |
| `service-dependencies.md` | Service dependency matrix & critical paths |
| `admin-migration-guide.md` | Admin portal migration guide |
| `environment-variables.md` | Environment configuration reference |
| `field-management-service.md` | Largest service doc (42.8 KB) |
| `user-service.md` | Authentication & user management |
| `advisory-service.md` | Advisory & recommendations |
| `weather-service.md` | Weather data service |
| *...and 35+ more service docs* | One per major service |

> **Note**: Individual services also have `README.md` files (69+ services) with bilingual (EN/AR) docs.

### Governance (`governance/` - 26 files)

| Path | Purpose |
| ---- | ------- |
| `services.yaml` | **Source of truth** - Service registry (v3.2.0) |
| `agents.yaml` | AI agent definitions (v16.0.0, 11 categories) |
| `events/catalog.yaml` | Event catalog |
| `events/schemas/` | JSON schemas (alert, field, NDVI, weather events) |
| `policies/` | Kyverno policies (security, labels, resource limits) |
| `reliability/slo-definitions.yaml` | SLO definitions |
| `templates/` | Service scaffolding templates (API, backend, worker) |
| `design/design-tokens.yaml` | Design system tokens |

### Internal Developer Platform (`idp/` - 41 files)

| Path | Purpose |
| ---- | ------- |
| `backstage/app-config.yaml` | Backstage configuration |
| `backstage/catalog/` | Service catalog & system definitions |
| `catalog/apis/` | API definitions (vision, terrain, hydrology, leveling, edge) |
| `templates/python-fastapi/` | Python FastAPI service template |
| `templates/node-service/` | Node.js NestJS service template |
| `templates/flutter-mobile/` | Flutter mobile app template |
| `templates/data-pipeline/` | Data pipeline template |
| `sahoolctl/README.md` | CLI tool documentation |

### Infrastructure Documentation (`infrastructure/` - 182+ files)

| Path | Purpose |
| ---- | ------- |
| `gateway/kong/` | Kong gateway setup, runbook, security (15+ files) |
| `monitoring/` | Prometheus, Grafana dashboards, alert rules (20+ files) |
| `monitoring/grafana/dashboards/` | 4 Grafana dashboards (agricultural insights, disaster recovery, SLO, AI skills) |
| `monitoring/prometheus/rules/` | Alert rules (agricultural, DR, NATS, SLO) |
| `core/postgres/` | PostgreSQL HA with Patroni |
| `core/pgbouncer/` | PgBouncer connection pooling |
| `core/redis-ha/` | Redis HA with Sentinel |
| `core/vault/` | HashiCorp Vault secrets |
| `core/ollama/` | Ollama local LLM deployment |
| `core/qdrant/` | Qdrant vector database |
| `nats/` | NATS cluster & K8s deployment |
| `terraform/` | Infrastructure as Code |
| `redis/` | Redis security & deployment checklist |

### AI Skills (`.claude/skills/` - 7 files)

| Path | Purpose |
| ---- | ------- |
| `context-engineering/memory.md` | Farm memory & persistent storage |
| `context-engineering/compression.md` | Token-efficient data compression |
| `context-engineering/evaluation.md` | LLM-as-Judge advisory evaluation |
| `sahool/crop-advisor.md` | Crop advisory & recommendations |
| `sahool/farm-documentation.md` | Farm knowledge base documentation |
| `obsidian/markdown.md` | Obsidian markdown formatting |
| `obsidian/canvas.md` | Knowledge graph visualization |

---

## Quick Reference

```bash
# Start everything
make dev

# Quick start for new developers
make quickstart

# Run Python tests
pytest apps/services/ -v
make test-python

# Run Node.js tests
npm run test
make test-node

# Check code quality (Python)
ruff check apps/ shared/
make lint

# Check code quality (Node.js)
npm run lint
npm run typecheck

# Auto-fix code issues
make fixops-run

# View logs
docker compose logs -f [service_name]

# Database access
make db-shell

# Service status
make status
make health

# Run full CI locally
make ci
```

---

_Last Updated: February 2026_
