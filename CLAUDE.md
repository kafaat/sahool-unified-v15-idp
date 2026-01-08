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

---

## Repository Structure

```
sahool-unified-v15-idp/
├── apps/
│   ├── admin/              # Admin portal (React)
│   ├── kernel/             # Core backend modules (Python)
│   │   ├── analytics/      # Analytics processing
│   │   ├── common/         # Shared database, middleware, queue, monitoring
│   │   └── field_ops/      # Field operations logic
│   ├── mobile/             # Flutter mobile apps
│   │   ├── sahool_field_app/   # Main field app
│   │   └── lib/            # Core Flutter code
│   ├── services/           # 50+ microservices (Python FastAPI & Node.js)
│   └── web/                # Web dashboard (React)
├── packages/               # Shared packages (npm workspaces)
│   ├── shared-utils/       # Common utilities
│   ├── shared-ui/          # UI components
│   ├── shared-types/       # TypeScript types
│   ├── nestjs-auth/        # NestJS auth module
│   ├── field-shared/       # Field domain types
│   └── i18n/               # Internationalization
├── shared/                 # Python shared modules
│   ├── auth/               # Authentication
│   ├── cache/              # Caching layer
│   ├── errors_py/          # Error handling
│   ├── observability/      # Metrics, logging
│   └── security/           # Security utilities
├── config/                 # Configuration files
│   ├── certs/              # TLS certificates
│   └── nats/               # NATS configuration
├── docker/                 # Docker configurations
├── docs/                   # Technical documentation
├── gitops/                 # ArgoCD applications
├── governance/             # Security policies
├── helm/                   # Kubernetes Helm charts
├── idp/                    # Internal Developer Platform (Backstage)
├── infrastructure/         # IaC, monitoring, Terraform
├── tests/                  # Test suites
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── smoke/              # Smoke tests
│   ├── e2e/                # End-to-end tests
│   └── load/               # Load tests
└── scripts/                # Utility scripts
```

---

## Technology Stack

### Backend Services

| Layer | Technology |
|-------|------------|
| **Python Services** | FastAPI, Tortoise ORM, asyncpg, Pydantic v2 |
| **Node.js Services** | Express/NestJS, Prisma ORM, TypeScript |
| **Database** | PostgreSQL 16+ with PostGIS (geospatial) |
| **Message Queue** | NATS (event-driven architecture) |
| **API Gateway** | Kong (authentication, rate limiting) |
| **Caching** | Redis (sessions, rate limiting) |
| **Connection Pooling** | PgBouncer |

### Mobile Application

| Layer | Technology |
|-------|------------|
| **Framework** | Flutter 3.x (Dart 3.6.0+) |
| **State Management** | Riverpod 2.x |
| **Local Database** | Drift + SQLCipher (encrypted) |
| **Background Tasks** | Workmanager |
| **Maps** | MapLibre GL, flutter_map |

### Frontend (Web/Admin)

| Layer | Technology |
|-------|------------|
| **Framework** | React with TypeScript |
| **Testing** | Vitest, React Testing Library |
| **Build** | Vite |

### Infrastructure

| Layer | Technology |
|-------|------------|
| **Container** | Docker, Kubernetes (K8s) |
| **IaC** | Terraform, Helm Charts |
| **CI/CD** | GitHub Actions, Argo CD |
| **Monitoring** | Prometheus, Grafana, OpenTelemetry |

---

## Development Commands

### Docker / Infrastructure

```bash
# Start development environment
make dev                    # Full stack
make dev-starter           # Starter package only
make up                    # Start all services
make down                  # Stop all services
make down-volumes          # Stop and remove volumes

# Build
make build                 # Build all Docker images
make build-python          # Build Python services only
make build-node            # Build Node.js services only

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
```

### Testing

```bash
# Python tests
make test                  # Run all tests
make test-cov             # With coverage
pytest tests/unit/         # Unit tests
pytest tests/integration/  # Integration tests
pytest tests/smoke/        # Smoke tests

# Node.js tests
npm run test              # Jest tests
npm run test:coverage     # With coverage

# Flutter tests
flutter test              # Unit tests
flutter test integration_test/  # Integration tests
```

### Code Quality

```bash
# Python
ruff check apps/ shared/   # Linting
black apps/ shared/        # Formatting
isort apps/ shared/        # Import sorting

# Node.js
npm run lint              # ESLint
npm run typecheck         # TypeScript

# Flutter
flutter analyze           # Dart analyzer
dart fix --apply          # Auto-fix issues
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
    yield
    # Shutdown: Close connections

app = FastAPI(
    title="Service Name",
    version="16.0.0",
    lifespan=lifespan
)
```

### Authentication Pattern

```python
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

@router.get("/protected")
async def protected_endpoint(user: User = Depends(get_current_user)):
    return {"user_id": user.id}
```

### Error Handling

```python
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# In main.py
setup_exception_handlers(app)
add_request_id_middleware(app)
```

---

## Node.js Service Conventions

### File Structure

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

- Use Drift for local SQLite database
- Background sync with Workmanager
- Conflict resolution for offline edits

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
└── l10n/                   # Localization
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

---

## Security Considerations

### DO NOT
- Commit secrets or credentials (`.env`, API keys)
- Use hardcoded passwords
- Skip authentication checks
- Disable TLS/SSL in production
- Run containers as root

### DO
- Use environment variables for secrets
- Follow RBAC patterns
- Validate all user input
- Use parameterized queries (no SQL injection)
- Enable rate limiting on endpoints
- Use TLS for all connections

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
GET /health/live     # Liveness probe
GET /health/ready    # Readiness probe
GET /health/startup  # Startup probe
GET /health          # Combined status
GET /metrics         # Prometheus metrics
```

### API Versioning

```
/api/v1/[resource]   # Current version
/api/v2/[resource]   # New version (if applicable)
```

### Rate Limiting Tiers

| Tier | Requests/min | Requests/hour |
|------|--------------|---------------|
| Free | 30 | 500 |
| Standard | 60 | 2000 |
| Premium | 120 | 5000 |
| Internal | 1000 | 50000 |

---

## Environment Configuration

### Required Environment Variables

```bash
# Database (TLS enforced)
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require
POSTGRES_SSL_MODE=require

# Redis
REDIS_PASSWORD=secure_password
REDIS_URL=redis://redis:6379

# NATS
NATS_URL=nats://nats:4222

# JWT
JWT_SECRET_KEY=32_char_minimum_secret_key
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
await app.state.nc.publish("field.created", json.dumps(event).encode())
```

### Logging (Structured JSON)

```python
import structlog
logger = structlog.get_logger()
logger.info("event_name", field_id=field_id, action="create")
```

---

## Important Files Reference

| File | Purpose |
|------|---------|
| `Makefile` | All development commands |
| `docker-compose.yml` | Full service stack |
| `pyproject.toml` | Python project config, linting |
| `package.json` | Node.js root workspace |
| `.env.example` | Environment template |
| `governance/services.yaml` | Service registry |

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
```

### CI/CD Pipeline

1. **Lint**: Code quality checks (Ruff, Black)
2. **Test**: Unit, integration, smoke tests
3. **Build**: Docker images
4. **Security**: CodeQL, Trivy, Bandit
5. **Deploy**: ArgoCD to staging/production

---

## Deprecated Services

Check deprecation warnings in service logs. Deprecated services will log:
```
⚠️  DEPRECATION WARNING: [service] is DEPRECATED
This service has been migrated to [new-service]
```

---

## Getting Help

- **Documentation**: `docs/` directory
- **API Gateway**: `docs/API_GATEWAY.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Security**: `docs/SECURITY.md`
- **Observability**: `docs/OBSERVABILITY.md`
- **Runbooks**: `docs/RUNBOOKS.md`

---

## Quick Reference

```bash
# Start everything
make dev

# Run Python tests
pytest apps/services/ -v

# Check code quality
ruff check apps/ shared/

# View logs
docker compose logs -f [service_name]

# Database access
make db-shell
```

---

*Last Updated: January 2025*
