# shared/service_enhancements - Service Enhancement Utilities

وحدة تحسينات الخدمات

Common patterns and utilities for SAHOOL Python backend services. Provides a consistent toolkit for caching, structured logging, database query optimization, API response formatting, service configuration, and input validation — reducing boilerplate and enforcing platform standards across all microservices.

## File Structure

```
shared/service_enhancements/
├── __init__.py       # Package exports (v1.0.0)
├── cache.py          # Redis + in-memory LRU caching with decorators
├── database.py       # Query builder, pagination, batch insert, retry
├── logging_utils.py  # Structured service logger with context
├── response.py       # Unified API response shapes
├── setup.py          # Service bootstrap (ServiceConfig + setup_service)
└── validation.py     # Pydantic-based validation, Arabic text, coordinates
```

## Modules

### Caching (`cache.py`)

Redis-primary with automatic in-memory LRU fallback.

**`CacheConfig`**: `redis_url`, `default_ttl=300s`, `max_memory_items=1000`, `key_prefix="sahool"`

**`CacheManager`**: Full async cache interface:
- `get(key)` / `set(key, value, ttl)` / `delete(key)` / `clear_prefix(prefix)`
- Automatic JSON serialization/deserialization
- Tenant-scoped key prefixing

**Decorators:**
```python
@cache(ttl=300, prefix="weather")
async def get_forecast(location_id: str): ...

@cache_response(ttl=60, key_func=lambda req: req.path_params["field_id"])
async def get_field_ndvi(request: Request): ...
```

**Functions:** `get_cache_manager()` (singleton), `invalidate_cache(pattern)`

### Database Utilities (`database.py`)

**`QueryBuilder`** - Fluent query construction:
- `select(table, *fields)`, `where(condition)`, `order_by(field, desc)`, `limit(n)`, `offset(n)`
- `build()` → `(sql, params)` tuple for asyncpg

**`PaginatedQuery`** - Cursor/offset pagination helper:
- `paginate(query, page, page_size)` → `(items, total, has_next)`

**`DatabaseOptimizer`** - Query analysis:
- `explain(pool, sql, params)` → execution plan
- `suggest_indexes(table)` → index recommendations based on query patterns

**`batch_insert(pool, table, rows)`** - Efficient bulk insert using `COPY` protocol.

**`with_retry(func, max_attempts=3)`** - Decorator for transient DB failure retry.

### Structured Logging (`logging_utils.py`)

**`ServiceLogger`** - Structlog wrapper with automatic context injection:
- Auto-includes: `service_name`, `version`, `tenant_id` (from context), `correlation_id`
- Methods: `info`, `warning`, `error`, `debug` — all accept keyword context fields

**`get_service_logger(name)`** - Factory that returns a configured `ServiceLogger`.

**Decorators:**
```python
@log_operation("create_field")
async def create_field(data): ...
# Logs: start, success/error, duration_ms

@log_performance(threshold_ms=500)
async def expensive_query(): ...
# Logs warning if execution exceeds threshold
```

### API Response Formatting (`response.py`)

Uniform response shapes for all SAHOOL endpoints:

```python
# Success
SuccessResponse(data={"field_id": "..."}, message="Field created")
# → {"status": "success", "data": {...}, "message": "...", "timestamp": "..."}

# Paginated
PaginatedResponse(data=items, total=150, page=1, page_size=20)
# → {"status": "success", "data": [...], "pagination": {...}}

# Error
ErrorResponse(code="E1001", message="Invalid input", details={...})
# → {"status": "error", "error": {"code": "E1001", "message": "...", "details": {...}}}
```

**`create_response(data, status, message)`** - Generic factory.

**`ApiResponse`** - TypeVar-generic Pydantic model for typed endpoint return annotations.

### Service Setup (`setup.py`)

**`ServiceConfig`** - Validated service configuration from environment:
- `service_name`, `service_version`, `port`, `environment`
- `database_url`, `redis_url`, `nats_url`, `jwt_secret_key`
- `log_level`, `cors_origins`

**`setup_service(config)`** - Bootstrap helper:
- Configures structlog
- Sets up Prometheus metrics
- Validates environment
- Returns initialized `FastAPI` app with health endpoints

### Input Validation (`validation.py`)

**`ValidatedModel`** - Base Pydantic model with:
- `str_strip_whitespace=True`, `validate_assignment=True`, `extra="forbid"`
- `normalize_arabic(text)` - Remove diacritics, normalize Arabic characters

**Validation Functions:**

| Function | Validates |
|----------|-----------|
| `validate_arabic_text(text, min_length, max_length)` | Arabic text with optional normalization |
| `validate_coordinates(lat, lon, region="middle_east")` | Geographic bounds for Middle East |
| `validate_phone(phone)` | International format with Yemen/Saudi prefixes |
| `validate_uuid(value)` | UUID v4 format |
| `validate_field_id(field_id)` | FIELD-XXXXXXXX pattern |
| `validate_date_range(start, end, max_days)` | Date ordering and max span |

**`validate_input` decorator** - Automatically raises `HTTPException(422)` on validation failure.

## Usage Example

```python
from shared.service_enhancements import (
    setup_service, ServiceConfig,
    cache, ServiceLogger, get_service_logger,
    PaginatedResponse, ErrorResponse,
    ValidatedModel, validate_coordinates, validate_input,
)

# Service bootstrap
config = ServiceConfig.from_env(service_name="field-management-service")
app = setup_service(config)

logger = get_service_logger("field_service")

# Cached endpoint
@cache(ttl=120, prefix="fields")
async def get_field_ndvi(field_id: str) -> dict:
    logger.info("fetching NDVI", field_id=field_id)
    ...

# Validated input model
class CreateFieldRequest(ValidatedModel):
    name: str
    name_ar: str
    latitude: float
    longitude: float

    @field_validator("latitude", "longitude")
    def check_coords(cls, v, info):
        validate_coordinates(info.data.get("latitude", v), info.data.get("longitude", v))
        return v

# Paginated response
@app.get("/api/v1/fields")
async def list_fields(page: int = 1, page_size: int = 20):
    fields, total = await field_repo.list(page, page_size)
    return PaginatedResponse(data=fields, total=total, page=page, page_size=page_size)
```

## Notes

- `CacheManager` uses Redis when `REDIS_URL` is set; falls back to in-memory LRU automatically.
- `ServiceLogger` integrates with `UnifiedContextMiddleware` from `shared/stability/` to inject tenant and correlation IDs.
- Phone validation supports Yemen (`+967`), Saudi Arabia (`+966`), and generic international formats.
- `ValidatedModel.normalize_arabic()` removes harakat (diacritics) and normalizes alef/teh marbuta variants.
