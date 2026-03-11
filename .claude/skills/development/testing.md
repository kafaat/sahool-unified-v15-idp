# Testing Skill | مهارة الاختبارات

## Description

This skill enables test generation and testing workflows for the SAHOOL agricultural platform. It provides patterns for writing unit, integration, smoke, and end-to-end tests across Python (FastAPI), Node.js (NestJS), and Flutter (Dart) services. Designed to ensure code quality, reliability, and CI/CD compliance for all 72 microservices and 4 applications.

## Instructions

### Test Categories (19 Types)

The SAHOOL platform organizes tests into 19 categories under `tests/`:

```
tests/
├── unit/              # Fast unit tests, no I/O dependencies
├── integration/       # API & database interaction tests
├── smoke/             # Import verification and basic health
├── e2e/               # End-to-end scenario tests
├── load/              # Performance tests (k6, Locust)
├── evaluation/        # AI agent quality evaluation
├── guardrails/        # Input validation & safety tests
├── a2a/               # Agent-to-Agent protocol tests
├── ci/                # CI integration verification tests
├── container/         # Docker container tests
├── database/          # Database-specific migration & query tests
├── frontend/          # React component & UI tests
├── middleware/         # HTTP middleware tests
├── simulation/        # Agricultural simulation tests
├── security/          # Security-focused tests (auth, RBAC, injection)
├── golden-datasets/   # Golden reference datasets for regression
├── factories/         # Test data factories & builders
├── snapshots/         # Snapshot comparison tests
└── utils/             # Shared test utilities & helpers
```

### Python Test Patterns

#### Pytest Markers

Always apply the correct marker to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_calculate_ndvi():
    """Unit test - no external dependencies."""
    result = calculate_ndvi(nir=0.8, red=0.2)
    assert result == pytest.approx(0.6, abs=0.01)

@pytest.mark.integration
async def test_create_field_via_api(client, db_pool):
    """Integration test - requires database."""
    response = await client.post("/api/v1/fields", json={"name": "Test Field"})
    assert response.status_code == 201

@pytest.mark.smoke
def test_service_imports():
    """Smoke test - verify modules load without error."""
    from apps.services.advisory_service.src.main import app
    assert app is not None

@pytest.mark.slow
async def test_batch_ndvi_processing(large_dataset):
    """Slow test - long-running batch operation."""
    results = await process_ndvi_batch(large_dataset)
    assert len(results) == len(large_dataset)
```

#### FastAPI TestClient Usage

```python
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

@pytest.fixture
def app():
    """Create a fresh FastAPI app for testing."""
    from apps.services.advisory_service.src.main import app
    return app

@pytest.fixture
async def client(app):
    """Async test client for FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.unit
async def test_health_endpoint(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

@pytest.mark.unit
async def test_readiness_endpoint(client):
    response = await client.get("/readyz")
    assert response.status_code == 200
```

#### Mock Patterns for External Dependencies

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# --- NATS Mock ---
@pytest.fixture
def mock_nats():
    nc = AsyncMock()
    nc.publish = AsyncMock()
    nc.subscribe = AsyncMock()
    nc.close = AsyncMock()
    return nc

# --- Redis Mock ---
@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    return redis

# --- PostgreSQL Mock ---
@pytest.fixture
def mock_db_pool():
    pool = AsyncMock()
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchrow = AsyncMock(return_value=None)
    conn.execute = AsyncMock(return_value="INSERT 0 1")
    pool.acquire = AsyncMock(return_value=conn)
    pool.acquire.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.__aexit__ = AsyncMock(return_value=False)
    return pool

# --- Usage in tests ---
@pytest.mark.unit
async def test_publish_field_event(mock_nats):
    from shared.events.subjects import SAHOOL_FIELD_CREATED
    await mock_nats.publish(
        SAHOOL_FIELD_CREATED,
        b'{"field_id": "F001", "tenant_id": "T001"}'
    )
    mock_nats.publish.assert_called_once()
```

#### Async Test Patterns (pytest-asyncio)

```python
import pytest

# Mark entire module as async
pytestmark = pytest.mark.asyncio

async def test_async_operation():
    result = await some_async_function()
    assert result is not None

# Or mark individual tests
@pytest.mark.asyncio
async def test_single_async():
    await asyncio.sleep(0)  # Example async operation
```

#### Test Environment Variables

Always set these for test isolation:

```python
# conftest.py
import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")  # Empty for unit tests
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("LOG_LEVEL", "WARNING")
```

#### Coverage Requirements

```ini
# pyproject.toml
[tool.coverage.run]
source = ["apps/", "shared/"]
omit = ["*/tests/*", "*/__pycache__/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 5
show_missing = true
```

Minimum coverage: **5%** (incrementally raising). Coverage artifacts: `coverage.xml` and `coverage_html/`.

### Node.js Test Patterns

#### Vitest 3.x Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.spec.ts", "src/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
    },
  },
});
```

#### NestJS Testing Module

```typescript
import { Test, TestingModule } from "@nestjs/testing";
import { FieldService } from "./field.service";
import { PrismaService } from "../prisma.service";

describe("FieldService", () => {
  let service: FieldService;
  let prisma: PrismaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FieldService,
        {
          provide: PrismaService,
          useValue: {
            field: {
              findMany: vi.fn().mockResolvedValue([]),
              create: vi.fn().mockResolvedValue({ id: "1", name: "Test" }),
            },
          },
        },
      ],
    }).compile();

    service = module.get<FieldService>(FieldService);
    prisma = module.get<PrismaService>(PrismaService);
  });

  it("should return all fields", async () => {
    const result = await service.findAll();
    expect(result).toEqual([]);
  });
});
```

#### React Testing Library 16.x

```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import { FieldCard } from "./FieldCard";

describe("FieldCard", () => {
  it("renders field name and area", () => {
    render(<FieldCard name="Al-Rashid North" area={5.2} crop="wheat" />);
    expect(screen.getByText("Al-Rashid North")).toBeInTheDocument();
    expect(screen.getByText("5.2 ha")).toBeInTheDocument();
  });

  it("handles click event", async () => {
    const onClick = vi.fn();
    render(<FieldCard name="Test" area={1.0} crop="wheat" onClick={onClick} />);
    fireEvent.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledOnce();
  });
});
```

### Flutter Test Patterns

#### Widget Testing with Riverpod

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/features/field/field_screen.dart';

void main() {
  testWidgets('FieldScreen displays field list', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          fieldListProvider.overrideWith((ref) => [
            Field(id: '1', name: 'Test Field', area: 5.2),
          ]),
        ],
        child: const MaterialApp(home: FieldScreen()),
      ),
    );

    await tester.pumpAndSettle();
    expect(find.text('Test Field'), findsOneWidget);
    expect(find.text('5.2 ha'), findsOneWidget);
  });
}
```

#### Drift Database Testing

```dart
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/storage/app_database.dart';

void main() {
  late AppDatabase db;

  setUp(() {
    db = AppDatabase(NativeDatabase.memory());
  });

  tearDown(() async {
    await db.close();
  });

  test('insert and retrieve field', () async {
    await db.into(db.fields).insert(FieldsCompanion.insert(
      name: 'Test Field',
      areaHectares: 5.2,
    ));

    final fields = await db.select(db.fields).get();
    expect(fields.length, 1);
    expect(fields.first.name, 'Test Field');
  });
}
```

#### Mock Patterns for Offline-First Sync

```dart
import 'package:mockito/mockito.dart';
import 'package:sahool_field_app/core/sync/sync_engine.dart';

class MockSyncEngine extends Mock implements SyncEngine {}

void main() {
  late MockSyncEngine mockSync;

  setUp(() {
    mockSync = MockSyncEngine();
    when(mockSync.syncStatus).thenReturn(SyncStatus.idle);
    when(mockSync.pendingChanges).thenReturn(0);
  });

  test('sync engine reports idle when no pending changes', () {
    expect(mockSync.syncStatus, SyncStatus.idle);
    expect(mockSync.pendingChanges, 0);
  });
}
```

### Test Generation Rules

When generating tests, follow these rules strictly:

1. **AAA Pattern**: Structure every test as Arrange, Act, Assert.

```python
# Arrange
field_data = {"name": "Test Field", "area_hectares": 5.2}

# Act
result = await create_field(field_data)

# Assert
assert result.id is not None
assert result.name == "Test Field"
```

2. **File Location Conventions**:
   - Python: `tests/unit/`, `tests/integration/`, or `apps/services/<name>/tests/`
   - Node.js: `src/__tests__/` or co-located `*.spec.ts` files
   - Flutter: `test/` directory mirroring `lib/` structure

3. **Naming Conventions**:
   - Python: `test_*.py` files, `test_*` functions
   - Node.js: `*.spec.ts` or `*.test.ts` files
   - Flutter: `*_test.dart` files

4. **Mock External Dependencies**: Always mock DB, NATS, Redis, and HTTP calls in unit tests. Never connect to real services.

5. **No Real Credentials**: Never use production secrets. Use the test environment variables defined above.

6. **Bilingual Test Data**: Include Arabic strings in test data where the feature supports bilingual content.

```python
@pytest.mark.unit
def test_bilingual_field_name():
    field = Field(name="North Field", name_ar="الحقل الشمالي")
    assert field.name_ar == "الحقل الشمالي"
```

### Running Tests

#### Python

```bash
make test                  # Run all tests
make test-python           # Python tests only
make test-unit             # Unit tests only
make test-integration      # Integration tests only
make test-coverage         # With coverage report

# Direct pytest
pytest -v -m unit          # Unit tests by marker
pytest -v -m integration   # Integration tests by marker
pytest -v -m smoke         # Smoke tests
pytest -v -m "not slow"    # Exclude slow tests

# Specific service
pytest apps/services/advisory-service/tests/ -v

# Vision, Terrain, Edge
make test-vision           # Vision service tests
make test-terrain          # Terrain service tests
make test-edge             # Edge orchestrator tests
```

#### Node.js

```bash
make test-node             # All Node.js tests
npm run test               # Vitest tests
npm run test:coverage      # With coverage report
```

#### Flutter

```bash
make mobile-test           # Flutter tests via Make
flutter test               # Unit & widget tests
flutter test integration_test/  # Integration tests
flutter test --coverage    # With coverage
```

#### Docker

```bash
make test-docker           # Run tests inside Docker containers
```

### CI Integration

Tests run automatically in GitHub Actions workflows:

| Workflow | Trigger | Tests Run |
|----------|---------|-----------|
| `ci.yml` | Push, PR | Lint + unit + smoke |
| `test.yml` | Push, PR | Full test suite |
| `ci-yolo26-vision.yml` | Changes to vision service | Vision-specific tests |
| `ci-terrain-services.yml` | Changes to terrain services | Terrain + hydrology tests |
| `ci-edge-orchestrator.yml` | Changes to edge service | Edge orchestrator tests |
| `frontend-tests.yml` | Frontend changes | React component tests |
| `mobile-ci.yml` | Mobile changes | Flutter tests |
| `e2e-tests.yml` | Scheduled / manual | End-to-end scenarios |
| `load-testing.yml` | Scheduled / manual | k6 + Locust load tests |

#### Coverage Report Generation

Coverage artifacts are generated in CI and published as workflow artifacts:

```bash
# Python coverage
pytest --cov=apps --cov=shared --cov-report=xml:coverage.xml --cov-report=html:coverage_html/

# Node.js coverage
npm run test:coverage  # Outputs to coverage/ directory

# Flutter coverage
flutter test --coverage  # Outputs to coverage/lcov.info
```

### Test Data Factories

Use factories from `tests/factories/` to generate consistent test data:

```python
from tests.factories import FieldFactory, UserFactory, TenantFactory

@pytest.mark.unit
def test_field_creation():
    tenant = TenantFactory.build()
    user = UserFactory.build(tenant_id=tenant.id)
    field = FieldFactory.build(
        owner_id=user.id,
        tenant_id=tenant.id,
        crop_type="wheat",
    )
    assert field.crop_type == "wheat"
    assert field.tenant_id == tenant.id
```

### Golden Dataset Tests

Use golden datasets from `tests/golden-datasets/` for regression testing:

```python
@pytest.mark.unit
def test_ndvi_calculation_against_golden(golden_ndvi_dataset):
    for sample in golden_ndvi_dataset:
        result = calculate_ndvi(nir=sample["nir"], red=sample["red"])
        assert result == pytest.approx(sample["expected_ndvi"], abs=0.001), \
            f"NDVI mismatch for sample {sample['id']}"
```
