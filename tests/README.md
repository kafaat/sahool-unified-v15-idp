# SAHOOL Tests

## Overview

اختبارات منصة سهول - وحدوية، تكاملية، ودخانية.

---

## Structure

```
tests/
├── __init__.py
├── conftest.py             # Pytest fixtures
│
├── factories/              # Test data factories
│   ├── field_factory.py    # Field data generator
│   └── user_factory.py     # User data generator
│
├── integration/            # Integration tests
│   ├── test_audit_flow.py
│   ├── test_field_api.py
│   ├── test_health.py
│   ├── test_identity_flows.py
│   ├── test_outbox_event_flow.py
│   └── test_spatial_hierarchy.py
│
├── smoke/                  # Smoke tests
│   ├── test_arch_imports.py
│   └── test_startup.py
│
└── unit/                   # Unit tests
    ├── ai/                 # AI module tests
    ├── kernel/             # Kernel tests
    ├── ndvi/               # NDVI tests
    └── shared/             # Shared lib tests
```

---

## Test Categories

### Unit Tests

Fast, isolated tests for individual functions.

```bash
# Run all unit tests
pytest tests/unit/

# Specific module
pytest tests/unit/ai/
pytest tests/unit/kernel/
pytest tests/unit/ndvi/

# Single file
pytest tests/unit/shared/test_security.py
```

### Integration Tests

Tests that involve multiple components.

```bash
# Run all integration tests
pytest tests/integration/

# Specific test
pytest tests/integration/test_field_api.py
pytest tests/integration/test_identity_flows.py
```

**Integration Tests:**

| Test | Description |
|------|-------------|
| `test_audit_flow.py` | Audit logging flow |
| `test_field_api.py` | Field API endpoints |
| `test_health.py` | Health check endpoints |
| `test_identity_flows.py` | Authentication flows |
| `test_outbox_event_flow.py` | Event outbox pattern |
| `test_spatial_hierarchy.py` | Spatial queries |

### Smoke Tests

Quick sanity checks.

```bash
# Run smoke tests
pytest tests/smoke/

# Architecture imports
pytest tests/smoke/test_arch_imports.py

# Service startup
pytest tests/smoke/test_startup.py
```

---

## Fixtures (conftest.py)

Shared test fixtures:

```python
# Available fixtures

@pytest.fixture
def db_session():
    """Database session for tests"""
    pass

@pytest.fixture
def test_client():
    """FastAPI test client"""
    pass

@pytest.fixture
def auth_headers():
    """Authenticated request headers"""
    pass

@pytest.fixture
def mock_nats():
    """Mock NATS client"""
    pass
```

---

## Test Factories

### field_factory.py

```python
from tests.factories.field_factory import FieldFactory

# Create single field
field = FieldFactory.create()

# Create multiple
fields = FieldFactory.create_batch(5)

# With specific attributes
field = FieldFactory.create(
    name="Test Field",
    area_hectares=10.5
)
```

### user_factory.py

```python
from tests.factories.user_factory import UserFactory

# Create user
user = UserFactory.create()

# Admin user
admin = UserFactory.create(role="admin")

# Specific tenant
user = UserFactory.create(tenant_id="tenant-1")
```

---

## Running Tests

### All Tests

```bash
# Run all
pytest

# With coverage
pytest --cov=apps --cov-report=html

# Verbose
pytest -v
```

### By Category

```bash
# Unit only
pytest tests/unit/

# Integration only
pytest tests/integration/

# Smoke only
pytest tests/smoke/
```

### With Markers

```bash
# Slow tests
pytest -m slow

# Database tests
pytest -m database

# Skip slow
pytest -m "not slow"
```

### Parallel Execution

```bash
# Use multiple cores
pytest -n auto

# Specific number
pytest -n 4
```

---

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    database: marks tests requiring database
    integration: integration tests
    unit: unit tests
```

### conftest.py Highlights

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db():
    """Test database fixture"""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

---

## Writing Tests

### Unit Test Example

```python
# tests/unit/shared/test_utils.py

def test_format_date():
    from shared.utils import format_date
    result = format_date(datetime(2025, 12, 21))
    assert result == "21 Dec 2025"

def test_calculate_area():
    from shared.utils import calculate_area
    polygon = {...}
    area = calculate_area(polygon)
    assert area > 0
```

### Integration Test Example

```python
# tests/integration/test_field_api.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_field(test_client: AsyncClient, auth_headers):
    response = await test_client.post(
        "/api/v1/fields",
        json={"name": "Test Field", "geometry": {...}},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Field"
```

### Smoke Test Example

```python
# tests/smoke/test_startup.py

import pytest

def test_all_services_importable():
    """Verify all services can be imported"""
    from apps.services.field_service import main
    from apps.services.satellite_service import main
    from apps.services.weather_advanced import main
```

---

## Coverage

```bash
# Generate coverage report
pytest --cov=apps --cov=shared --cov-report=html

# View report
open htmlcov/index.html

# Coverage threshold
pytest --cov=apps --cov-fail-under=80
```

---

## Related Documentation

- [Tools](../tools/README.md)
- [Scripts](../scripts/README.md)
- [Services Map](../docs/SERVICES_MAP.md)

---

<p align="center">
  <sub>SAHOOL Tests</sub>
  <br>
  <sub>December 2025</sub>
</p>
