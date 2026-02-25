# Test Utilities

Shared helper modules used across all test suites. Import these in any test file to avoid duplicating common assertions, mock objects, and JWT generation logic.

## Usage

```python
from tests.utils.assertions import assert_api_response, assert_field_shape, assert_event_shape
from tests.utils.helpers import create_test_token, async_test, make_jwt_header
from tests.utils.mocks import MockDatabase, MockNATS, MockRedis, MockHTTPClient
```

## Modules

### `assertions.py`

Custom assertion functions with informative failure messages:

```python
# Assert HTTP response status and parse JSON
data = assert_api_response(response, expected_status=200, expected_keys=["id", "name"])

# Assert field domain object shape
assert_field_shape(data, required_keys=["id", "tenant_id", "area_hectares", "geometry"])

# Assert event envelope fields
assert_event_shape(event_dict, event_type="FieldCreatedEvent")

# Assert pagination response structure
assert_paginated_response(data, min_items=1)

# Assert bilingual fields (Arabic + English)
assert_bilingual_fields(data, fields=["name", "description"])
```

**Key behaviors:**
- `assert_api_response()` returns the parsed JSON body for chaining
- Failure messages include the full response text (up to 500 chars) for debugging
- `assert_event_shape()` checks `event_id`, `tenant_id`, `timestamp`, `version` envelope fields

### `helpers.py`

Common helper functions and decorators:

```python
# Create a signed JWT for testing (uses TEST_SECRET_KEY)
token = create_test_token(
    user_id="user-123",
    roles=["farmer"],
    tenant_id="tenant-456",
    expires_in_hours=1,
)

# Build Authorization header dict
headers = make_jwt_header(token)  # {"Authorization": "Bearer <token>"}

# Decorator for running async tests without pytest-asyncio
@async_test
async def test_something():
    result = await some_async_function()
    assert result is not None

# Wait for a condition with timeout (polling helper)
await wait_for(lambda: service.is_ready(), timeout=30, interval=0.5)
```

### `mocks.py`

In-memory mock implementations of platform services:

**`MockDatabase`**
- In-memory `dict`-based store keyed by table name and record ID
- `connect()`, `disconnect()`, `insert()`, `get()`, `update()`, `delete()`, `list()`
- Automatically sets `created_at` and `updated_at` on `insert()`

**`MockNATS`**
- Records all published messages in `published` list
- `publish(subject, payload)` — stores `{"subject": ..., "payload": ...}`
- `subscribe(subject, handler)` — registers async handler
- `assert_published(subject)` — helper to verify event was emitted

**`MockRedis`**
- In-memory key-value store with TTL support
- `get()`, `set()`, `delete()`, `exists()`, `expire()`, `ttl()`
- `scan_keys(pattern)` for glob-style key listing

**`MockHTTPClient`**
- Configurable response map: `{(method, url): MockResponse}`
- `register(method, url, status, body)` — pre-configure responses
- Tracks all requests in `request_history` list

## Environment Constants

```python
from tests.utils.helpers import TEST_SECRET_KEY, TEST_ALGORITHM

TEST_SECRET_KEY = "test-secret-key-for-unit-tests-only-32chars"
TEST_ALGORITHM  = "HS256"
```

These match the values set in `tests/conftest.py` and are safe for test use only.

## Related

- Root conftest: `tests/conftest.py`
- Test factories: `tests/factories/`
- CI environment: `ENVIRONMENT=test` with empty `DATABASE_URL` and `NATS_URL`
