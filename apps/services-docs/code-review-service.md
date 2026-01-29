# Code Review Service - Microservice Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | code-review-service |
| **Type** | Python (FastAPI) |
| **Version** | 2.0.0 (Dockerfile HEALTHCHECK says 16.0.0 in readyz) |
| **Primary Port** | 8102 (docker-compose), 8124 (Dockerfile), 8096 (settings default) |
| **Container Name** | sahool-code-review |
| **Profile** | gpu (requires NVIDIA GPU via Ollama) |
| **Dependencies** | ollama |

### Description

Real-time AI-powered code review service for the SAHOOL agricultural platform. Uses Ollama with DeepSeek/CodeLlama models to provide intelligent code reviews with special focus on:

- Docker/containerization best practices
- Security vulnerability detection
- Agricultural domain-specific rules (NDVI, LAI, IoT sensors, irrigation)
- GitHub PR integration with automated reviews
- Multi-model fallback support
- Caching (memory, Redis, file backends)

### Bilingual Support

The service provides bilingual (English/Arabic) support for:
- Agricultural issue messages
- GitHub PR review comments
- Review summaries

---

## API Endpoints

### 1. Health Check

```
GET /health
```

**Response Model: `HealthResponse`**

```json
{
  "status": "healthy | degraded",
  "service": "code-review-service",
  "ollama_connected": true,
  "available_models": ["deepseek-coder-v2", "codellama"],
  "cache_enabled": true,
  "github_enabled": false,
  "version": "2.0.0"
}
```

### 2. Readiness Probe

```
GET /readyz
```

**Response:**

```json
{
  "status": "ready",
  "service": "code-review-service",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

### 3. List Available Models

```
GET /models
```

**Response Model: `list[ModelInfo]`**

```json
[
  {
    "name": "deepseek-coder-v2",
    "url": "http://ollama:11434",
    "available": true,
    "priority": 0
  },
  {
    "name": "codellama",
    "url": "http://ollama:11434",
    "available": true,
    "priority": 1
  }
]
```

### 4. Review Code Content

```
POST /review
```

**Request Model: `CodeReviewRequest`**

```json
{
  "code": "def hello():\n    print('world')",
  "language": "python",
  "filename": "example.py",
  "use_cache": true,
  "model": "deepseek-coder-v2"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| code | string | Yes | - | Code content to review |
| language | string | No | null | Programming language |
| filename | string | No | null | Optional filename for context |
| use_cache | boolean | No | true | Use cached review if available |
| model | string | No | null | Specific model to use |

**Response Model: `ReviewResponse`**

```json
{
  "summary": "Code looks good with proper Python syntax...",
  "critical_issues": [],
  "suggestions": ["Consider adding docstring"],
  "security_concerns": [],
  "agricultural_issues": [],
  "score": 85,
  "model_used": "deepseek-coder-v2",
  "cached": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| summary | string | Summary of the review |
| critical_issues | list[string] | Critical issues found |
| suggestions | list[string] | Improvement suggestions |
| security_concerns | list[string] | Security vulnerabilities |
| agricultural_issues | list[string] | SAHOOL-specific agricultural issues |
| score | int (0-100) | Review score |
| model_used | string | LLM model used for review |
| cached | boolean | Whether result was from cache |

### 5. Review File from Codebase

```
POST /review/file
```

**Request Model: `FileReviewRequest`**

```json
{
  "file_path": "infrastructure/core/pgbouncer/pgbouncer.ini"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file_path | string | Yes | Path to file in mounted codebase |

**Response:** Same as `/review` endpoint (`ReviewResponse`)

**Error Responses:**
- `404`: File not found
- `403`: File must be within codebase
- `413`: File too large

### 6. Review GitHub Pull Request

```
POST /review/pr
```

**Request Model: `PRReviewRequest`**

```json
{
  "pr_number": 123,
  "owner": "kafaat",
  "repo": "sahool-unified-v15-idp",
  "post_comment": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| pr_number | int | Yes | - | Pull request number |
| owner | string | No | github_repo_owner config | Repository owner |
| repo | string | No | github_repo_name config | Repository name |
| post_comment | boolean | No | true | Post review as PR comment |

**Response:**

```json
{
  "pr_number": 123,
  "files_reviewed": 5,
  "total_score": 78,
  "conclusion": "neutral",
  "has_critical_issues": false,
  "file_reviews": [
    {
      "file": "src/main.py",
      "summary": "...",
      "score": 80,
      "critical_issues": [],
      "suggestions": []
    }
  ]
}
```

**Error Response:**
- `400`: GitHub integration not configured
- `404`: PR not found

### 7. GitHub Webhook Handler

```
POST /webhook/github
```

**Headers:**
- `X-Hub-Signature-256`: Webhook signature (optional if no secret configured)
- `X-GitHub-Event`: Event type (e.g., "pull_request")

**Supported Events:**
- `pull_request` with actions: `opened`, `synchronize`

**Response:**

```json
{
  "status": "review_started",
  "pr": 123
}
```

or

```json
{
  "status": "ignored"
}
```

### 8. Cache Statistics

```
GET /cache/stats
```

**Response Model: `CacheStatsResponse`**

```json
{
  "backend": "memory",
  "size": 150,
  "hits": 1200,
  "misses": 300,
  "hit_rate": "80.0%"
}
```

### 9. Clear Cache

```
POST /cache/clear
```

**Response:**

```json
{
  "status": "cleared"
}
```

or

```json
{
  "status": "cache_disabled"
}
```

---

## NATS Events

**This service does NOT publish or subscribe to NATS events.**

The service operates independently via HTTP API and does not integrate with the SAHOOL event-driven architecture. NATS is only referenced in the agricultural rules engine for detecting IoT/messaging patterns in reviewed code.

### Potential Integration Opportunities

If NATS integration were added, suggested events could include:

| Event Subject | Direction | Description |
|---------------|-----------|-------------|
| `sahool.{tenant_id}.code.review.completed` | Publish | When a code review completes |
| `sahool.{tenant_id}.code.review.requested` | Subscribe | Trigger review from other services |
| `sahool.{tenant_id}.pr.opened` | Subscribe | Auto-review new PRs |

---

## Code Review Features

### Multi-Model Support

The service supports multiple LLM models with automatic fallback:

| Priority | Model | URL |
|----------|-------|-----|
| 1 | deepseek-coder-v2 | http://ollama:11434 |
| 2 | deepseek-coder | http://ollama:11434 |
| 3 | codellama | http://ollama:11434 |
| 4 | starcoder | http://ollama:11434 |
| 5 | llama2 | http://ollama:11434 |

Model selection strategies:
- `primary_first` (default): Try primary model first, then fallback
- `round_robin`: Distribute across available models
- `fastest`: Select based on response time (not implemented)

### Caching System

Three cache backends supported:

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| memory | Development, single instance | `cache_backend=memory`, `cache_max_size=1000` |
| redis | Production, distributed | `cache_backend=redis`, `redis_url=redis://redis:6379/2` |
| file | Persistence across restarts | `cache_backend=file`, `cache_file_path=/app/cache/reviews.json` |

Cache key is generated from: `SHA256(code + language + model)[:32]`

### Agricultural Domain Rules

The `AgriculturalRulesEngine` provides SAHOOL-specific code analysis:

#### Detected Domains

| Domain | Detection Patterns |
|--------|-------------------|
| NDVI | `ndvi`, `normalized difference vegetation index`, NDVI formula |
| LAI | `lai`, `leaf area index` |
| Sensor/IoT | `soil_moisture`, `temperature_sensor`, `mqtt`, `nats`, `iot` |
| Irrigation | `irrigation`, `water_flow`, `drip`, `sprinkler`, `evapotranspiration`, `et0` |
| Crop | `crop_health`, `yield_prediction`, `harvest`, `fertilizer`, `pesticide` |

#### Validation Rules

| Domain | Rule | Severity |
|--------|------|----------|
| NDVI | Values must be in range [-1, 1] | Critical |
| NDVI | Division by zero protection required | Warning |
| NDVI | Threshold values should have comments | Info |
| LAI | Values must be in range [0, 10] | Warning |
| LAI | Cannot be negative | Critical |
| Sensor | Soil moisture must be 0-100% | Warning |
| Sensor | Temperature -50 to 70C for agriculture | Warning |
| Sensor | Readings should be validated | Warning |
| Sensor | Timeout/retry logic recommended | Info |
| Irrigation | Water flow cannot be negative | Critical |
| Irrigation | ET0 needs multiple climate factors | Info |
| Irrigation | Consider soil moisture thresholds | Warning |
| Crop | Yield predictions need confidence intervals | Info |
| Crop | Crop health should use multiple indices | Info |
| General | Timestamps should handle timezones | Info |
| General | Unit documentation for measurements | Info |
| General | Geographic coordinates should be validated | Warning |

#### Score Modifiers

| Severity | Score Impact |
|----------|--------------|
| Critical | -15 points |
| Warning | -5 points |
| Info | -1 point |

### File Watcher (Real-time Reviews)

When `REVIEW_ON_CHANGE=true`, the service watches for file changes:

**Supported Extensions:**
`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.yml`, `.yaml`, `.json`, `.md`, `.sh`, `.dockerfile`, `.tf`, `.go`, `.rs`

**Features:**
- Debounce delay: 2.0 seconds (configurable)
- Maximum file size: 1MB (configurable)
- Watches paths specified in `WATCH_PATHS`

### GitHub Integration

**Capabilities:**
- Review all files in a PR
- Post review comments on PRs
- Verify webhook signatures (SHA256)
- Create check runs (requires GitHub App)
- Format bilingual review summaries

**PR Review Thresholds:**
- Score >= 80: Approved (success)
- Score >= 60: Needs Minor Changes (neutral)
- Score < 60: Needs Review (failure)

---

## Dependencies

### Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| watchdog | 3.0.0 | File system monitoring |
| requests | 2.31.0 | HTTP client (unused, aiohttp used instead) |
| python-dotenv | 1.0.1 | Environment variable loading |
| pydantic | 2.9.2 | Data validation |
| pydantic-settings | 2.7.1 | Settings management |
| aiohttp | >=3.11.12 | Async HTTP client |
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | 0.27.0 | ASGI server |
| pytest | 8.3.4 | Testing |
| pytest-asyncio | 0.24.0 | Async test support |
| httpx | 0.28.1 | HTTP testing client |
| structlog | >=24.1.0 | Structured logging |

### Shared Modules

- `shared.errors_py`: Exception handlers, request ID middleware

### Optional Dependencies (for Redis cache)

```
redis  # Not in requirements.txt - needed for redis cache backend
```

---

## Environment Variables

### Documented in Settings

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OLLAMA_URL` | `http://ollama:11434` | No | Ollama API URL |
| `OLLAMA_MODEL` | `deepseek-coder-v2` | No | Primary LLM model |
| `FALLBACK_MODELS` | `deepseek-coder@...,codellama@...,starcoder@...,llama2@...` | No | Fallback models (model@url format) |
| `MODEL_STRATEGY` | `primary_first` | No | Model selection strategy |
| `ENABLE_FALLBACK` | `true` | No | Enable automatic model fallback |
| `MAX_RETRIES` | `3` | No | Max retries per model |
| `RETRY_DELAY` | `1.0` | No | Delay between retries (seconds) |
| `GITHUB_TOKEN` | `None` | For PR reviews | GitHub personal access token |
| `GITHUB_API_URL` | `https://api.github.com` | No | GitHub API base URL |
| `GITHUB_WEBHOOK_SECRET` | `None` | No | Webhook signature verification |
| `GITHUB_AUTO_COMMENT` | `true` | No | Auto-comment on PRs |
| `GITHUB_COMMENT_THRESHOLD` | `70` | No | Only comment if score < threshold |
| `GITHUB_REPO_OWNER` | `kafaat` | No | Default repository owner |
| `GITHUB_REPO_NAME` | `sahool-unified-v15-idp` | No | Default repository name |
| `ENABLE_CACHE` | `true` | No | Enable review caching |
| `CACHE_BACKEND` | `memory` | No | Cache backend: memory, redis, file |
| `REDIS_URL` | `redis://redis:6379/2` | For Redis cache | Redis connection URL |
| `CACHE_TTL` | `3600` | No | Cache TTL in seconds (1 hour) |
| `CACHE_MAX_SIZE` | `1000` | No | Max entries for memory cache |
| `CACHE_FILE_PATH` | `/app/cache/reviews.json` | No | File cache path |
| `ENABLE_AGRICULTURAL_RULES` | `true` | No | Enable SAHOOL agricultural rules |
| `AGRICULTURAL_KEYWORDS` | `ndvi,lai,evapotranspiration,...` | No | Agricultural detection keywords |
| `NDVI_MIN_VALUE` | `-1.0` | No | NDVI minimum valid value |
| `NDVI_MAX_VALUE` | `1.0` | No | NDVI maximum valid value |
| `LAI_MIN_VALUE` | `0.0` | No | LAI minimum valid value |
| `LAI_MAX_VALUE` | `10.0` | No | LAI maximum valid value |
| `SOIL_MOISTURE_MIN` | `0.0` | No | Soil moisture minimum (%) |
| `SOIL_MOISTURE_MAX` | `100.0` | No | Soil moisture maximum (%) |
| `WATCH_PATHS` | `infrastructure:docker-compose.yml:docker:apps/services` | No | Colon-separated watch paths |
| `REVIEW_ON_CHANGE` | `true` | No | Enable file watcher |
| `MAX_FILE_SIZE` | `1000000` | No | Max file size to review (bytes) |
| `DEBOUNCE_DELAY` | `2.0` | No | File change debounce (seconds) |
| `API_HOST` | `0.0.0.0` | No | API server host |
| `API_PORT` | `8096` | No | API server port |
| `RATE_LIMIT_REQUESTS` | `100` | No | Rate limit (not implemented) |
| `RATE_LIMIT_PERIOD` | `60` | No | Rate limit period (not implemented) |
| `LOG_LEVEL` | `INFO` | No | Logging level |
| `LOG_REVIEWS_TO_FILE` | `true` | No | Log reviews to JSONL |
| `METRICS_ENABLED` | `true` | No | Enable metrics (not implemented) |

### Missing Environment Variables

The following environment variables are defined in settings but **NOT set in docker-compose.yml**:

| Variable | Impact |
|----------|--------|
| `FALLBACK_MODELS` | Using hardcoded defaults |
| `MODEL_STRATEGY` | Using default `primary_first` |
| `ENABLE_FALLBACK` | Using default `true` |
| `MAX_RETRIES` | Using default `3` |
| `RETRY_DELAY` | Using default `1.0` |
| `GITHUB_TOKEN` | GitHub integration disabled |
| `GITHUB_API_URL` | Using default GitHub API |
| `GITHUB_WEBHOOK_SECRET` | Webhook verification disabled |
| `GITHUB_AUTO_COMMENT` | Using default `true` |
| `GITHUB_COMMENT_THRESHOLD` | Using default `70` |
| `GITHUB_REPO_OWNER` | Using default `kafaat` |
| `GITHUB_REPO_NAME` | Using default `sahool-unified-v15-idp` |
| `ENABLE_CACHE` | Using default `true` |
| `CACHE_BACKEND` | Using default `memory` |
| `REDIS_URL` | Not needed unless cache_backend=redis |
| `CACHE_TTL` | Using default `3600` |
| `CACHE_MAX_SIZE` | Using default `1000` |
| `ENABLE_AGRICULTURAL_RULES` | Using default `true` |
| `DEBOUNCE_DELAY` | Using default `2.0` |
| `RATE_LIMIT_REQUESTS` | Not implemented |
| `LOG_REVIEWS_TO_FILE` | Using default `true` |
| `METRICS_ENABLED` | Not implemented |

---

## Bugs, Errors, and Recommendations

### Critical Issues

#### 1. Port Mismatch (Configuration Conflict)

**Location:** Multiple files

| Source | Port |
|--------|------|
| `config/settings.py` (default) | 8096 |
| `docker-compose.yml` | 8102 |
| `Dockerfile` (HEALTHCHECK, EXPOSE) | 8124 |
| Kong Gateway v1 | 8102 |
| Kong Gateway v2 | 8124 |

**Impact:** Service may fail health checks or be unreachable depending on which configuration is used.

**Recommendation:** Standardize on port 8102 (docker-compose) and update:
- Dockerfile: Change `EXPOSE 8124` to `EXPOSE 8102`
- Dockerfile HEALTHCHECK: Change port 8124 to 8102
- Remove Kong v2 route on port 8124 if not needed

#### 2. Redis Dependency Not in requirements.txt

**Location:** `requirements.txt`

**Issue:** The `RedisCache` backend imports `redis.asyncio` but `redis` package is not listed in requirements.txt.

**Impact:** Service will crash if `cache_backend=redis` is configured.

**Recommendation:** Add to requirements.txt:
```
redis>=5.0.0
```

#### 3. Version Inconsistency

**Location:** Multiple files

| Source | Version |
|--------|---------|
| `main.py` FastAPI title | 2.0.0 |
| `main.py` HealthResponse | 2.0.0 |
| `main.py` /readyz endpoint | 16.0.0 |
| Platform version | 16.0.0 |

**Recommendation:** Standardize version to 16.0.0 across all files.

### Medium Issues

#### 4. Unused requests Package

**Location:** `requirements.txt`

**Issue:** `requests==2.31.0` is listed but never used (service uses `aiohttp`).

**Recommendation:** Remove from requirements.txt to reduce image size.

#### 5. Rate Limiting Not Implemented

**Location:** `config/settings.py`

**Issue:** `rate_limit_requests` and `rate_limit_period` settings exist but no rate limiting is implemented.

**Recommendation:** Either implement rate limiting using FastAPI middleware or remove the settings to avoid confusion.

#### 6. Metrics Not Implemented

**Location:** `config/settings.py`

**Issue:** `metrics_enabled` setting exists but no Prometheus metrics are exposed.

**Recommendation:** Add `/metrics` endpoint with Prometheus metrics or remove the setting.

#### 7. Missing /healthz Endpoint

**Location:** `main.py`

**Issue:** SAHOOL convention requires `/healthz` for liveness probes, but only `/health` and `/readyz` are implemented.

**Recommendation:** Add `/healthz` endpoint aliasing `/health`:
```python
@app.get("/healthz")
async def healthz():
    return await health_check()
```

#### 8. asyncio.get_event_loop() Deprecation

**Location:** `main.py:214`

**Issue:** `asyncio.get_event_loop()` is deprecated in Python 3.10+ and may fail in some contexts.

**Code:**
```python
loop = asyncio.get_event_loop()
self._debounce_tasks[file_str] = loop.create_task(debounced_review())
```

**Recommendation:** Use `asyncio.create_task()` directly or `asyncio.get_running_loop()`.

### Low Issues

#### 9. PR Review Background Task Not Tracked

**Location:** `main.py:880`

**Issue:** `asyncio.create_task(service.review_pr(pr_number))` creates a task that isn't tracked, potentially causing unhandled exceptions.

**Recommendation:** Store task reference and handle exceptions:
```python
task = asyncio.create_task(service.review_pr(pr_number))
task.add_done_callback(lambda t: t.exception() if t.done() else None)
```

#### 10. Hardcoded Code Truncation

**Location:** `main.py:446`

**Issue:** Code is truncated to 5000 characters in the prompt, which may cut off important context.

**Recommendation:** Make configurable via settings or use a smarter truncation strategy.

#### 11. Empty /healthz Response Model Missing

**Location:** `main.py`

**Issue:** The `/readyz` endpoint doesn't have a Pydantic response model.

**Recommendation:** Add response model for OpenAPI documentation consistency.

#### 12. Log Directory Permission Issue

**Location:** `main.py:41-42`

**Issue:** Code creates `/app/logs` and `/app/cache` directories but the Dockerfile comment mentions the user may not have write permissions.

**Recommendation:** The Dockerfile already handles this, but remove the directory creation from main.py to avoid confusion.

---

## File Structure

```
apps/services/code-review-service/
├── Dockerfile                    # Container build (Python 3.11-slim)
├── IMPLEMENTATION_SUMMARY.md     # Implementation notes
├── README.md                     # Service documentation
├── requirements.txt              # Python dependencies
├── test_api.sh                   # API test script
├── config/
│   ├── __init__.py
│   └── settings.py               # Pydantic settings (45 config options)
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app (941 lines)
│   ├── agricultural_rules.py     # SAHOOL agricultural rules (477 lines)
│   ├── cache.py                  # Cache backends (341 lines)
│   └── github_integration.py     # GitHub API integration (396 lines)
└── tests/
    ├── __init__.py
    └── test_api.py               # API tests (125 lines)
```

---

## Gateway Routes

### Kong Gateway Configuration

**Primary Route (v1):**
```yaml
- name: code-review-service
  host: code-review-service
  port: 8102
  protocol: http
  routes:
    - name: code-review-service-route
      paths: ["/api/v1/code-review", "/code-review"]
      strip_path: true
      protocols: ["http", "https"]
```

**Secondary Route (v2):**
```yaml
- name: code-review-service-new
  host: code-review-service
  port: 8124
  protocol: http
  routes:
    - name: code-review-service-new-route
      paths: ["/api/v1/code-review-v2", "/code-review-v2"]
      strip_path: true
      protocols: ["http", "https"]
```

---

## Testing

### Running Tests

```bash
# Unit tests
cd apps/services/code-review-service
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

Current tests cover:
- Health endpoint
- Code review endpoint (with/without language)
- File review (not found case)

Missing test coverage:
- PR review endpoint
- GitHub webhook handler
- Cache operations
- Agricultural rules engine
- Model fallback logic

---

## Deployment Notes

### Docker Compose Profile

The service is in the `gpu` profile and requires:
- Ollama service to be healthy
- NVIDIA GPU for optimal performance (Ollama)

### Volumes

| Volume | Path | Purpose |
|--------|------|---------|
| `.:/app/codebase:ro` | Read-only | Codebase for file reviews |
| `code_review_logs:/app/logs` | Named volume | Review logs (JSONL) |

### Health Checks

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; r=urllib.request.urlopen('http://localhost:8102/health'); exit(0) if r.getcode()==200 else exit(1)"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

---

## Changelog Summary

Based on service description, this is version 2.0.0 with:
- Multi-model support with automatic fallback
- GitHub PR integration
- Review caching (memory, redis, file)
- Agricultural domain-specific rules for SAHOOL
- Bilingual (English/Arabic) support

---

*Generated: 2026-01-25*
*Source: /home/user/sahool-unified-v15-idp/apps/services/code-review-service/*
