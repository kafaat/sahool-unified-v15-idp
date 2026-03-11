# Claude Code Quick Start for SAHOOL Platform

## دليل البدء السريع لـ Claude Code

A practical guide for developers using Claude Code to work with the SAHOOL National Agricultural Intelligence Platform.

دليل عملي للمطورين لاستخدام Claude Code مع منصة سهول الوطنية للذكاء الزراعي.

---

## What is Claude Code | ما هو Claude Code

Claude Code is Anthropic's official CLI for Claude, designed for AI-assisted software development directly from the terminal. It reads the project's `CLAUDE.md` file to understand the codebase structure, conventions, and tooling, allowing it to provide context-aware assistance across all layers of the SAHOOL platform.

Claude Code هو واجهة سطر الأوامر الرسمية من Anthropic، مصممة للتطوير البرمجي بمساعدة الذكاء الاصطناعي مباشرة من الطرفية.

---

## Prerequisites | المتطلبات الأساسية

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Node.js | >= 20.0.0 | Claude Code runtime, NestJS services |
| Python | >= 3.11 | FastAPI services, shared modules |
| Docker & Docker Compose | Latest | Container orchestration |
| Flutter | 3.27.x | Mobile app development |
| Git | Latest | Version control |
| Claude Code CLI | Latest | AI-assisted development |

Ensure Docker is running before starting any SAHOOL services.

---

## Installation & Setup | التثبيت والإعداد

### Step 1: Install Claude Code CLI | تثبيت واجهة سطر الأوامر

```bash
npm install -g @anthropic-ai/claude-code
```

Verify the installation:

```bash
claude --version
```

### Step 2: Clone and Setup SAHOOL Repo | استنساخ وإعداد المستودع

```bash
git clone <repository-url> sahool-unified-v15-idp
cd sahool-unified-v15-idp

# Install Node.js dependencies (27 workspace packages)
npm install

# Install Python dependencies
pip install -r requirements/dev.txt

# Copy environment template
cp .env.example .env

# Quick start for new developers
make quickstart
```

### Step 3: Configure Claude Code with CLAUDE.md | تهيئة Claude Code

The repository includes a `CLAUDE.md` file at the project root that Claude Code reads automatically. No additional configuration is needed. Simply launch Claude Code from the project directory:

```bash
cd sahool-unified-v15-idp
claude
```

Claude Code will detect `CLAUDE.md` and load the full project context, including:

- Repository structure (72 microservices, 80 shared Python modules, 27 npm packages)
- Technology stack (FastAPI, NestJS, Flutter, PostGIS, NATS)
- Development commands and conventions
- API contracts and event architecture

---

## Key Commands for SAHOOL Development | أوامر التطوير الرئيسية

### Exploring the Codebase | استكشاف الكود

| Task | Command | Scope |
|------|---------|-------|
| List all services | `ls apps/services/` | 72 microservices |
| List shared modules | `ls shared/` | 80 Python modules |
| List npm packages | `ls packages/` | 27 workspace packages |
| View service registry | `cat governance/services.yaml` | Source of truth |
| Project statistics | `make stats` | LOC, file counts |
| Service status | `make status` | Running containers and URLs |

### Running Tests | تشغيل الاختبارات

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-python` | Python tests only |
| `make test-unit` | Unit tests (fast, no I/O) |
| `make test-integration` | Integration tests (API, database) |
| `make test-node` | Node.js tests (Vitest) |
| `npm run test` | Vitest test runner |
| `flutter test` | Flutter unit tests |
| `flutter test integration_test/` | Flutter integration tests |
| `make test-vision` | YOLO26 vision service tests |
| `make test-terrain` | Terrain service tests |
| `make test-coverage` | Tests with coverage report |

### Code Quality | جودة الكود

| Command | Description |
|---------|-------------|
| `ruff check apps/ shared/` | Python linting |
| `ruff format .` | Python formatting |
| `npm run lint` | ESLint for Node.js/TypeScript |
| `npm run typecheck` | TypeScript type checking |
| `flutter analyze` | Dart analyzer |
| `dart fix --apply` | Auto-fix Dart issues |
| `make lint` | Run all linters |
| `make fmt` | Format all code |
| `make fixops` | Preview auto-fix issues (dry-run) |
| `make fixops-run` | Apply safe auto-fixes |

### Docker Operations | عمليات Docker

| Command | Description |
|---------|-------------|
| `make dev` | Start full development stack |
| `make infra-up` | Infrastructure only (postgres, redis, nats, kong) |
| `make dev-starter` | Starter package services |
| `make dev-professional` | Professional package services |
| `make dev-enterprise` | All enterprise services |
| `make dev-vision` | Vision services (yolo26) |
| `make dev-terrain` | Terrain services |
| `make dev-edge` | Edge orchestrator service |
| `make down` | Stop all services |
| `make down-volumes` | Stop and remove volumes |
| `make logs` | View all service logs |
| `make logs-service SERVICE=field_ops` | Logs for a specific service |
| `make health` | Health check all services |
| `make build` | Build all Docker images (parallel) |

### Database Operations | عمليات قاعدة البيانات

| Command | Description |
|---------|-------------|
| `make db-migrate` | Run Prisma migrations |
| `make db-seed` | Seed sample data |
| `make db-shell` | Connect to PostgreSQL |
| `make db-backup` | Create database backup |
| `make db-reset` | Reset database (destroys data) |

---

## Working with SAHOOL Services | العمل مع خدمات سهول

### Python FastAPI Services | خدمات Python FastAPI

All Python services follow a standard structure under `apps/services/[service-name]/`:

```
src/
├── main.py          # FastAPI entry point with lifespan
├── api/v1/          # Versioned API routes
└── events/          # NATS event handlers
```

**Key conventions:**

- Every service must expose `/healthz` (liveness) and `/readyz` (readiness) endpoints
- Use `shared.auth.dependencies.get_current_user` for authentication
- Use `shared.errors_py` for unified error handling with `setup_exception_handlers(app)`
- Structured JSON logging via `structlog`
- Database connections through `asyncpg` with connection pooling (min 2, max 10)
- NATS event publishing with subject pattern `sahool.{domain}.{action}`

**Port assignments** are defined in `packages/shared-types/src/contracts/service-ports.ts`. Always use `SERVICE_PORTS.*` constants rather than hardcoded port numbers.

### Node.js NestJS Services | خدمات Node.js NestJS

Located under `apps/services/[service-name]/` with the structure:

```
src/
├── index.ts         # Entry point
├── app.module.ts    # Root module
└── __tests__/       # Tests
prisma/
├── schema.prisma    # Database schema
└── seed.ts          # Seed data
```

**Key conventions:**

- Prisma for database access (`npx prisma generate`, `npx prisma migrate deploy`)
- Import contracts from `@sahool/shared-types/contracts`
- NestJS auth module from `packages/nestjs-auth/`
- TypeScript 5.9.x with strict mode

### Flutter Mobile App | تطبيق Flutter للجوال

The main mobile app is at `apps/mobile/sahool_field_app/` with core code in `apps/mobile/lib/`:

```
lib/
├── core/            # Infrastructure (api, auth, offline, security, storage)
├── features/        # 57 feature modules
├── l10n/            # Localization (Arabic/English)
└── main.dart        # Entry point
```

**Key conventions:**

- State management with Riverpod 2.6.x
- Local database with Drift + SQLCipher (256-bit AES encryption)
- Offline-first: background sync via Workmanager, conflict resolution with ETags (schema v4)
- Certificate pinning for 3 production domains
- Contract files in `apps/mobile/lib/core/contracts/` are auto-generated -- do not edit manually

---

## AI Skills Available | مهارات الذكاء الاصطناعي المتاحة

Claude Code can leverage the specialized skills defined in `.claude/skills/`:

### Context Engineering | هندسة السياق

| Skill | File | Purpose |
|-------|------|---------|
| Memory | `context-engineering/memory.md` | Persistent farm history: entity, event, decision, outcome memory |
| Compression | `context-engineering/compression.md` | Token-efficient data compression (3 levels: 80%, 50%, 25% retention) |
| Evaluation | `context-engineering/evaluation.md` | LLM-as-Judge advisory quality scoring across 5 dimensions |

### SAHOOL Domain Skills | مهارات منصة سهول

| Skill | File | Purpose |
|-------|------|---------|
| Crop Advisor | `sahool/crop-advisor.md` | Crop management recommendations, decision trees, bilingual alerts |
| Farm Documentation | `sahool/farm-documentation.md` | Obsidian-compatible field documentation with YAML frontmatter |

### Documentation Skills | مهارات التوثيق

| Skill | File | Purpose |
|-------|------|---------|
| Markdown | `obsidian/markdown.md` | Obsidian markdown formatting with wikilinks and callouts |
| Canvas | `obsidian/canvas.md` | Knowledge graph visualization |

---

## Common Workflows | سير العمل الشائع

### Creating a New Microservice | إنشاء خدمة جديدة

1. Use the IDP template as a starting point:
   - Python FastAPI: `idp/templates/python-fastapi/`
   - Node.js NestJS: `idp/templates/node-service/`
2. Register the service port in `packages/shared-types/src/contracts/service-ports.ts`
3. Add service entry to `governance/services.yaml`
4. Create a Dockerfile following the multi-mirror fallback pattern (Pattern A recommended)
5. Add health endpoints (`/healthz`, `/readyz`)
6. Add the service to `docker-compose.yml`
7. Run `make ci` to validate

### Adding an API Endpoint | إضافة نقطة وصول API

1. Create or update the route file under `src/api/v1/`
2. Add authentication with `get_current_user` dependency (Python) or NestJS auth guard
3. Use Pydantic v2 models (Python) or Prisma types (Node.js) for request/response validation
4. Publish NATS events for state changes using `sahool.{domain}.{action}` subject pattern
5. Add unit tests in the service's `tests/` directory
6. Update the OpenAPI spec if the endpoint is gateway-exposed
7. Run `ruff check` or `npm run lint` before committing

### Fixing a Bug | إصلاح خطأ

1. Reproduce the issue and identify the affected service
2. Check the service logs: `make logs-service SERVICE=<name>`
3. Read the relevant source files and tests
4. Apply the fix following existing code conventions
5. Add or update tests to cover the bug scenario
6. Run `make lint` and `make test-unit` to verify
7. Commit with conventional format: `fix: resolve <description>`

### Running CI Locally | تشغيل CI محليا

```bash
# Quick CI check (lint + test)
make ci

# Full CI pipeline (lint + test + build)
make ci-full

# Additional quality checks
make secrets-scan      # Scan for leaked secrets
make deps-audit        # Security audit of dependencies
make dead-code         # Detect unused code (knip)
make complexity        # Check code complexity
make deps-check        # Check dependency health
```

---

## Tips & Best Practices | نصائح وأفضل الممارسات

1. **Start infrastructure first**: Run `make infra-up` before working on services that need postgres, redis, or nats.

2. **Use conventional commits**: The project enforces `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:` prefixes.

3. **Check the service registry**: `governance/services.yaml` is the single source of truth for all service metadata.

4. **Never hardcode ports**: Import from `@sahool/shared-types/contracts` (TypeScript) or reference `SERVICE_PORTS` constants.

5. **Follow the bilingual pattern**: All user-facing text should include both English and Arabic translations.

6. **Use the auto-fix engine**: Run `make fixops` to preview issues, then `make fixops-run` to apply safe fixes automatically.

7. **Respect offline-first**: Mobile features must work without connectivity. Use Drift for local storage and Workmanager for background sync.

8. **Check deprecated services**: 15 services have been archived. See `apps/services/DEPRECATION_SUMMARY.md` before referencing legacy code.

9. **Test before pushing**: Run `make ci` locally to catch lint and test failures before they hit the CI pipeline.

10. **Security first**: Never commit secrets, always use environment variables, and run `make secrets-scan` periodically.

---

## Related Guides | أدلة ذات صلة

| Guide | Path |
|-------|------|
| General Quick Start | `docs/guides/SETUP_GUIDE.md` |
| Build Guide | `docs/guides/BUILD_GUIDE.md` |
| MCP Quick Start | `docs/guides/MCP_QUICK_START.md` |
| Deployment Checklist | `docs/guides/DEPLOYMENT_CHECKLIST.md` |
| Testing Guide | `docs/TESTING.md` |
| Deployment Guide | `docs/DEPLOYMENT.md` |
| Security Guide | `docs/SECURITY.md` |
| API Gateway | `docs/API_GATEWAY.md` |
| Mobile Architecture | `docs/MOBILE_ARCHITECTURE_ANALYSIS.md` |
| Service Documentation | `apps/services-docs/README.md` |
| Coding Agent Guide | `apps/services-docs/CODING-AGENT-GUIDE.md` |
| Environment Variables | `docs/ENVIRONMENT_VARIABLES.md` |
| Troubleshooting | `docs/TROUBLESHOOTING.md` |

---

_Last Updated: March 2026_
