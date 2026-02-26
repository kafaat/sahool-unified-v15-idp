# Simulation Tests

Tests that simulate the SAHOOL platform's behavior without requiring external hardware, ML models, or live services. Simulations verify that event-driven flows, service communication patterns, authentication contexts, and computer vision pipelines behave correctly under controlled conditions.

## Running

```bash
# All simulation tests
pytest tests/simulation/ -v

# Platform architecture simulation
pytest tests/simulation/test_platform_simulation.py -v

# Ground vision pipeline simulation
pytest tests/simulation/test_ground_vision.py -v

# With verbose output showing simulation state
pytest tests/simulation/ -v -s
```

## Test Files

### `test_platform_simulation.py`

Simulates the SAHOOL platform's core runtime behavior end-to-end without live services:

**Authentication Context**
- `create_test_principal()` — generates JWT-like principal with tenant ID, roles, and expiry
- Multi-tenant isolation: verifies requests cannot cross tenant boundaries
- Role-based access: worker, agronomist, admin permission differentiation

**Field Operations**
- `create_test_field()` — generates Arabic-named field objects with realistic geometry
- Field state machine: `pending → active → harvested → fallow`
- Field update with optimistic locking (ETag simulation)

**Event-Driven Architecture**
- NATS subject routing simulation: `sahool.{domain}.{action}` patterns
- Tenant-scoped events: `sahool.tenant.{tenant_id}.{domain}.{action}`
- Event consumer acknowledgment and redelivery behavior
- Dead letter queue (DLQ) routing after max retries

**Service Communication**
- HTTP request/response cycle with correlation ID propagation
- Error handling: 400, 401, 403, 404, 422, 500 response shapes
- Retry with exponential backoff simulation

**Data Consistency**
- Soft-delete pattern (records retain data, `deleted_at` set)
- Audit trail entry generation on state change

### `test_ground_vision.py`

Simulates the ground-level vision pipeline (`apps/services/ground-vision-service/`) without GPU or camera hardware:

**Image Processing**
- `sample_frame` fixture — synthetic 640×480 numpy array with crop field patterns (green field area, brown path, yellow stress zone)
- `sample_camera_intrinsics` — realistic camera calibration parameters
- Image pre-processing: resize, normalize, channel reorder
- Color space analysis: HSV-based vegetation index extraction

**Object Detection Simulation**
- Bounding box generation and NMS (non-maximum suppression) logic
- Confidence threshold filtering at 0.25 default
- Mock YOLO-compatible result format: `[x_center, y_center, width, height, confidence, class_id]`

**Georeferencing**
- GPS coordinate to pixel mapping using camera intrinsics
- Ground sampling distance (GSD) calculation from altitude and focal length

## Design Principles

- All simulations use numpy arrays and pure Python — no model files loaded.
- `unittest.mock.AsyncMock` and `MagicMock` replace external services.
- Fixtures generate deterministic data with fixed seeds for reproducible results.
- Arabic field names and Middle East coordinates are used throughout.

## Related

- Ground vision service: `apps/services/ground-vision-service/`
- YOLO26 vision service: `apps/services/yolo26-vision-service/`
- Platform event contracts: `shared/events/contracts.py`
- Load simulations: `tests/load/` (k6, Locust scripts)
