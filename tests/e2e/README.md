# End-to-End Tests

Full-stack tests that exercise complete user workflows and service interactions. These tests require running services and connect over HTTP to live service endpoints.

## Running

```bash
# All e2e tests
pytest tests/e2e/ -v -m e2e

# Single workflow
pytest tests/e2e/test_farmer_journey.py -v --e2e
pytest tests/e2e/test_field_management_e2e.py -v -m e2e

# With async support
pytest tests/e2e/ -v -m e2e --asyncio-mode=auto

# Skip if services are not running (graceful)
pytest tests/e2e/ -v -m e2e --ignore-glob="*vision*"
```

## Prerequisites

Services must be running before executing e2e tests:

```bash
make dev           # Start all services
# or
make infra-up      # Infrastructure only, then start services individually
```

## Configuration

Set these environment variables to point tests at your running services:

```bash
E2E_FIELD_BASE_URL=http://localhost:3000     # field-management-service
E2E_AUTH_BASE_URL=http://localhost:3025      # user-service
E2E_ADVISORY_URL=http://localhost:8093       # advisory-service
E2E_VISION_URL=http://localhost:8150         # yolo26-vision-service
```

## Test Files

| File | Workflow Covered |
|------|-----------------|
| `test_farmer_journey.py` | Complete farmer lifecycle: registration, onboarding, field creation, advisory, harvest |
| `test_field_management_e2e.py` | Field CRUD, GeoJSON boundary, PostGIS nearby search, ETag locking |
| `test_field_workflow.py` | Field state transitions and operational workflows |
| `test_user_auth_e2e.py` | User registration, login, token refresh, logout |
| `test_ai_advisor_workflow.py` | AI advisory request, recommendation generation, feedback loop |
| `test_irrigation_advisory_e2e.py` | Irrigation scheduling and smart advisory end-to-end |
| `test_iot_device_e2e.py` | IoT device registration, sensor data ingestion, alerting |
| `test_marketplace_e2e.py` | Product listing, search, purchase workflow |
| `test_payment_workflow.py` | Billing and payment processing flow |
| `test_vision_detection_e2e.py` | Image upload through YOLO26 pest/disease detection |
| `test_ux_scenarios.py` | Common UX patterns and error recovery scenarios |
| `conftest.py` | Shared fixtures: auth tokens, unique IDs, test data generators |

## Markers

```python
@pytest.mark.e2e          # Full stack, requires running services
@pytest.mark.integration  # Combined with e2e for cross-service tests
@pytest.mark.asyncio      # Async HTTP calls via httpx
```

## Notes

- Tests use `httpx.AsyncClient` for async HTTP calls (30-second timeout by default).
- Retry count defaults to 3 (configurable via `e2e_retry_count` fixture).
- Session timeout is 120 seconds (configurable via `e2e_timeout` fixture).
- Test data uses unique UUIDs to prevent collisions between parallel runs.
- Arabic farmer names and Yemen/Saudi coordinates are used for realistic data.
