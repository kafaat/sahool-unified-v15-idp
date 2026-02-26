# Unit Tests

Fast, isolated tests covering individual modules across the SAHOOL platform. No external services required — no live database, NATS, or Redis connections.

## Running

```bash
# All unit tests
pytest tests/unit/ -v

# By marker
pytest tests/unit/ -m unit -v

# With coverage
pytest tests/unit/ --cov=shared --cov=apps --cov-report=term-missing

# Specific subdirectory
pytest tests/unit/ai/ -v
pytest tests/unit/shared/ -v

# Via Makefile
make test-unit
```

## Structure

```
tests/unit/
├── ai/                   # AI subsystem tests (auto-fix, embeddings, LLM, RAG, vision)
├── auth/                 # Authentication endpoint tests
├── config/               # NATS configuration tests
├── contracts/            # API contracts and TypeScript contract tests
├── drift_detection/      # ML drift detection engine tests
├── edge_cloud/           # Edge/cloud architecture layer tests
├── irrigation/           # Irrigation models, collaborative engine, checklists
├── kernel/               # Kernel service (field ops, task queue) tests
├── ndvi/                 # NDVI analytics, caching, cloud cover, confidence
├── services/             # Service-level tests (YOLO26, terrain, hydrology, edge orchestrator)
├── shared/               # Shared module tests (auth, cache, domain, events, security)
├── smart_agriculture/    # Blockchain, IFTTT, PID controller tests
├── task_service/         # Task service cache, exceptions, validators
└── test_*.py             # Root-level tests for cross-cutting domain modules
```

## Key Test Files

| File | What It Tests |
|------|---------------|
| `test_agri_calendar.py` | Season calculations, Hijri date conversion, planting windows |
| `test_shared_auth.py` | JWT creation, verification, refresh, token pair generation |
| `test_architecture_conformance.py` | NATS JetStream, BaseEvent fields, OTel trace injection |
| `test_batch_operations.py` | Async batch processor patterns |
| `test_crop_rotation.py` | Crop rotation planning and soil health logic |
| `test_ndvi_calculation.py` | NDVI computation from satellite bands |
| `test_pest_scouting.py` | Pest identification and IPM threshold logic |
| `test_mobile_sync.py` | Offline-first sync, conflict resolution, delta sync |
| `test_weather_alerts.py` | Weather monitoring and spray window optimization |
| `test_yemen_data.py` | Yemen-specific crop, climate, and soil data |
| `ai/test_auto_fix.py` | Auto-Fix Engine: diagnostics, fix strategies, audit trail |
| `ai/test_embeddings.py` | Unified embedding adapters (local + cloud providers) |
| `ai/test_ultrarag_pipeline.py` | RAG pipeline retrieval and generation |
| `shared/test_jwt.py` | JWT handler edge cases and algorithm validation |
| `shared/test_rbac.py` | Role-based access control policy enforcement |
| `services/test_yolo26_vision.py` | YOLO26 pest/disease/weed detection model |
| `services/test_terrain_core.py` | DEM processing and terrain analysis |

## Environment

Tests run with the following environment variables set automatically via `tests/conftest.py`:

```bash
ENVIRONMENT=test
JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars
JWT_ALGORITHM=HS256
DATABASE_URL=""   # empty — no DB required
NATS_URL=""       # empty — no NATS required
```

## Coverage Requirement

Minimum 25% overall coverage enforced in CI (`fail_under = 25` in `pyproject.toml`).
