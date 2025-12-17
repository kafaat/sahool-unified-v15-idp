# SAHOOL Platform - Testing Guide

## Overview

This document describes the testing strategy and guidelines for the SAHOOL Platform.
Sprint 2 establishes the testing baseline that enables safe refactoring in future sprints.

## Testing Pyramid

We follow the standard testing pyramid with these ratios:

| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| Unit Tests | 60% | Protect business logic |
| Integration Tests | 30% | Protect API contracts |
| Smoke Tests | 10% | Verify system starts |

## Directory Structure

```
tests/
├── conftest.py          # Shared fixtures (Single Source of Truth)
├── unit/                # Fast, isolated tests
│   ├── kernel/          # Kernel module tests
│   └── shared/          # Shared module tests
├── integration/         # API and contract tests
├── smoke/               # Import and startup tests
└── factories/           # Test data generators
```

## Running Tests

### Quick Commands

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run only unit tests (fast)
make test-unit

# Run only integration tests
make test-integration

# Run only smoke tests
make test-smoke

# Full CI check
make ci-full
```

### Pytest Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/shared/test_rbac.py

# Run specific test class
pytest tests/unit/shared/test_rbac.py::TestHasPermission

# Run specific test
pytest tests/unit/shared/test_rbac.py::TestHasPermission::test_worker_has_task_read

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=shared --cov-report=html

# Run marked tests
pytest -m unit
pytest -m integration
pytest -m smoke
```

## Writing Tests

### Golden Rules

1. **No Test imports from main.py** - Import from domain/service modules directly
2. **No external I/O in unit tests** - Mock databases, HTTP, message queues
3. **Use fixtures from conftest.py** - Don't duplicate test setup
4. **One assertion focus per test** - Test one behavior at a time
5. **Descriptive test names** - Name should describe what's being tested

### Unit Test Example

```python
"""Tests for RBAC permissions"""

from shared.security.rbac import has_permission, Permission


class TestHasPermission:
    """Tests for has_permission function"""

    def test_worker_has_task_read(self, test_principal):
        """Worker should have task read permission"""
        test_principal["roles"] = ["worker"]

        assert has_permission(test_principal, Permission.FIELDOPS_TASK_READ) is True

    def test_worker_lacks_task_delete(self, test_principal):
        """Worker should not have task delete permission"""
        test_principal["roles"] = ["worker"]

        assert has_permission(test_principal, Permission.FIELDOPS_TASK_DELETE) is False
```

### Integration Test Example

```python
"""Tests for Field Operations API"""

from fastapi.testclient import TestClient


class TestFieldCRUD:
    """Integration tests for Field CRUD operations"""

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def test_create_field(self, client, sample_field_data):
        """Should create a new field"""
        response = client.post("/fields", json=sample_field_data)

        assert response.status_code == 200
        assert "id" in response.json()
```

### Using Test Factories

```python
from tests.factories.user_factory import make_user, make_admin_user
from tests.factories.field_factory import make_field

def test_admin_can_delete_field():
    admin = make_admin_user()
    field = make_field(tenant_id=admin.tenant_id)

    # Test admin deleting field...
```

## Fixtures

### Available Fixtures (from conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `test_user_id` | function | Standard test user ID |
| `test_tenant_id` | function | Standard test tenant ID |
| `test_roles` | function | Default test roles |
| `test_scopes` | function | Default test scopes |
| `test_principal` | function | Decoded JWT payload |
| `admin_principal` | function | Admin JWT payload |
| `sample_field_data` | function | Field creation data |
| `sample_operation_data` | function | Operation creation data |
| `mock_nats` | function | Mock NATS client |
| `mock_redis` | function | Mock Redis client |
| `db_session` | function | Database session |

### Creating Custom Fixtures

Add to `tests/conftest.py`:

```python
@pytest.fixture
def my_custom_fixture(test_tenant_id):
    """Custom fixture with dependency"""
    return {"tenant_id": test_tenant_id, "custom": "data"}
```

## Coverage

### Requirements

- **Minimum**: 60% coverage to pass CI
- **Target**: 75% coverage for Sprint 3+
- **Branch coverage**: Enabled

### Excluded from Coverage

- Test files themselves
- `__pycache__` directories
- Migration files
- `conftest.py`
- Type checking blocks
- `__repr__` methods

### Viewing Coverage

```bash
# Generate HTML report
make test-cov

# Open report
open coverage_html/index.html
```

## CI Integration

Tests run automatically on:
- Push to `main`, `develop`, `feature/**`, `release/**`, `claude/**`
- Pull requests to `main`, `develop`

### CI Gates

| Gate | Requirement |
|------|-------------|
| Lint | Ruff format and check pass |
| Unit Tests | All tests pass |
| Coverage | ≥ 60% |
| Integration | API contracts valid |

## Test Categories

### Unit Tests (`tests/unit/`)

- **Speed**: < 10ms per test
- **Dependencies**: None (mocked)
- **Database**: Never
- **Network**: Never

### Integration Tests (`tests/integration/`)

- **Speed**: < 100ms per test
- **Dependencies**: FastAPI TestClient
- **Database**: In-memory or mock
- **Network**: Mocked

### Smoke Tests (`tests/smoke/`)

- **Speed**: < 50ms per test
- **Purpose**: Verify imports work
- **Coverage**: All main modules

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Add path to sys.path in test file
import sys
sys.path.insert(0, "kernel/services/field_ops/src")
```

**Missing Fixtures**
```bash
# Check conftest.py is in tests/ directory
# Ensure pytest finds it: pytest --fixtures
```

**Coverage Too Low**
```bash
# Check what's not covered
pytest --cov=shared --cov-report=term-missing
```

## Best Practices

1. **Test behavior, not implementation**
2. **Keep tests independent** - No shared state between tests
3. **Use descriptive names** - `test_user_with_admin_role_can_delete_field`
4. **Arrange-Act-Assert** pattern
5. **One test file per module**
6. **Group related tests in classes**

## Sprint 2 Checklist

- [ ] `pytest` passes
- [ ] Coverage ≥ 60%
- [ ] No flaky tests
- [ ] No test order dependencies
- [ ] CI green on PR and main
