# Middleware Tests

Tests for HTTP middleware components: JWT authentication middleware, rate limiting, and associated audit reports from full middleware review passes. Tests use mock request/response objects and require no live services.

## Running

```bash
# All middleware tests
pytest tests/middleware/ -v

# Authentication middleware
pytest tests/middleware/test_auth_middleware.py -v

# Rate limiting
pytest tests/middleware/test_rate_limiting.py -v

# Via Makefile
make test-unit -k middleware
```

## Test Files

### `test_auth_middleware.py`

Tests the JWT authentication middleware layer:

**Token Extraction**
- Bearer token from `Authorization: Bearer <token>` header
- Fallback to `access_token` cookie
- Missing/malformed header handling

**Token Verification**
- Valid token decoded and user context attached to `request.state`
- Expired token returns 401
- Invalid signature returns 401
- Missing required claims returns 401

**Path Exclusions**
- Health endpoints (`/healthz`, `/readyz`) bypass authentication
- API documentation (`/docs`, `/openapi.json`) accessible without token
- All other paths require valid JWT

**Authorization**
- Role-based access control (RBAC) enforcement per route
- Tenant ID (`tid` claim) extracted and validated
- Multi-tenant isolation: requests can only access own tenant's resources

### `test_rate_limiting.py`

Tests the rate limiter implementation:

**Rate Limit Tiers** (matching Kong configuration)

| Tier | Per Minute | Per Hour |
|------|-----------|---------|
| Starter | 30 | 500 |
| Professional | 60 | 2000 |
| Enterprise | 120 | 5000 |

**Token Bucket Algorithm**
- `burst_tokens` allow brief traffic spikes above sustained rate
- Sliding window counter reset after `minute_reset` / `hour_reset` timestamps
- Per-user keying (`user:{id}`) when authenticated, per-IP fallback (`ip:{address}`)

**Blocking Logic**
- IP blocking after repeated violations with `cooldown_seconds`
- `blocked_ips` dictionary with expiry timestamps
- `get_wait_time()` returns seconds until next allowed request

## Audit Reports

Generated reference reports from middleware review passes:

| Report | Contents |
|--------|----------|
| `FASTAPI_MIDDLEWARE_AUDIT.md` | FastAPI middleware stack ordering and configuration |
| `AUTH_FLOW_AUDIT.md` | Authentication flow analysis across all services |
| `RATE_LIMITING_AUDIT.md` | Rate limit configuration and enforcement |
| `CORS_AUDIT.md` | CORS policy per service |
| `LOGGING_MIDDLEWARE_AUDIT.md` | Request/response structured logging |
| `ERROR_HANDLING_AUDIT.md` | Error response shape consistency |
| `KONG_ROUTES_AUDIT.md` | Kong API gateway route definitions (105 routes) |
| `KONG_PLUGINS_AUDIT.md` | Kong plugin configuration (auth, rate-limit, CORS) |
| `KONG_SECURITY_AUDIT.md` | Kong security posture review |
| `NESTJS_GUARDS_AUDIT.md` | NestJS guard and interceptor patterns |
| `SHARED_MIDDLEWARE_AUDIT.md` | Shared middleware module (`shared/middleware/`) review |

## Related

- Implementation: `shared/middleware/`
- Security middleware: `shared/security/`
- Kong configuration: `infrastructure/gateway/kong/`
- Unit tests: `tests/unit/shared/test_security_middleware.py`, `test_request_tenant_middleware.py`
