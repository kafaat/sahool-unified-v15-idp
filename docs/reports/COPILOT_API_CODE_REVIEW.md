# Copilot API Code Review Report
# تقرير مراجعة كود Copilot API

**Service**: `apps/services/copilot-api/`
**Port**: 8088
**Date**: 2026-03-16
**Reviewer**: Claude Code Review Agent
**Branch**: `main` (commit `961bda2`)

---

## Executive Summary | ملخص تنفيذي

The Copilot API is a **well-architected** FastAPI service serving as SAHOOL's unified AI assistant. It implements multi-LLM support (Ollama, Claude, OpenAI, Gemini, DeepSeek), RAG with Qdrant vector search, tool execution with 6-layer guardrails, bilingual Arabic/English support, and agent routing. The codebase is clean and modular, but has **several issues** ranging from critical security concerns to maintainability improvements.

**Overall Assessment**: 7/10 - Solid foundation with notable gaps to address.

---

## Architecture Overview | نظرة عامة على البنية

```
src/
├── main.py              # FastAPI app, lifespan, provider detection
├── api/
│   ├── deps.py          # JWT auth dependencies
│   └── v1/
│       ├── chat.py      # Main chat endpoint + streaming
│       ├── tools.py     # Tool execution with guardrails
│       ├── rag.py       # RAG document management
│       └── health.py    # Liveness/readiness probes + metrics
├── core/
│   ├── config.py        # Pydantic Settings (env-based)
│   └── agents.py        # Intent-based agent router
├── models/
│   └── schemas.py       # Pydantic request/response models
├── security/
│   ├── allowlists.py    # Tool/domain/pattern allowlists
│   ├── guardrails.py    # 6-layer ToolGuard system
│   └── prompt_guard.py  # Prompt injection detection
├── rag/
│   ├── service.py       # CopilotRAGService (Qdrant + keyword fallback)
│   ├── embeddings.py    # Multi-provider embedding service
│   └── ultrarag_integration.py  # Tri-RAG with Agri/Code/GEE providers
├── db/
│   └── chat_store.py    # PostgreSQL chat history persistence
└── events/
    └── publisher.py     # NATS event publishing
```

---

## Critical Issues (P0) | مشاكل حرجة

### 1. JWT Auth: Empty Secret Key Allows Service to Start
**File**: `src/api/deps.py:19-21`

```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = ""  # Will cause decode to fail
```

**Problem**: Setting the secret to empty string means `jwt.decode()` will fail for all tokens, but the service still starts and accepts requests. In production, if `JWT_SECRET_KEY` is accidentally unset, all authenticated endpoints return 401 — a silent denial-of-service.

**Recommendation**: Fail fast on startup in production. Add a check in `lifespan()` or `Settings` validator:
```python
if settings.is_production and not settings.jwt_secret_key:
    raise RuntimeError("JWT_SECRET_KEY must be set in production")
```

### 2. PyJWT vs python-jose Dependency Conflict
**File**: `requirements.txt:30` + `src/api/deps.py:8`

`requirements.txt` lists `python-jose[cryptography]>=3.5.0` but `deps.py` imports `import jwt` (PyJWT). These are **different packages** with incompatible APIs. If both are installed, import resolution depends on installation order. `python-jose` has known CVEs (CVE-2024-33663, CVE-2024-33664) listed in the requirements comment itself.

**Recommendation**: Pick one. For new code, use `PyJWT>=2.8.0` (actively maintained) and remove `python-jose`. Update `requirements.txt` accordingly.

### 3. NATS Connection Never Established in Lifespan
**File**: `src/main.py:76-143`

The lifespan initializes RAG, Audit, FixOps, and DB, but **never connects to NATS**. Yet `chat.py:96` does `nc = getattr(req.app.state, "nc", None)` which will always be `None`. Events are silently never published.

**Recommendation**: Add NATS connection initialization in lifespan:
```python
if settings.nats_url:
    import nats
    app.state.nc = await nats.connect(settings.nats_url)
```

### 4. Readiness Probe Creates New Connections Every Call
**File**: `src/api/v1/health.py:60-79`

The `/readyz` endpoint creates a **new Redis client** and a **new NATS connection** on every health check call, then immediately closes them. Under Kubernetes with frequent probes (every 10-30s), this creates connection churn.

**Recommendation**: Use the app-level connections from `app.state` instead of creating new ones. Or cache the health check result with a short TTL (e.g., 5 seconds).

---

## High Issues (P1) | مشاكل عالية

### 5. Streaming Endpoint is Fake Streaming
**File**: `src/api/v1/chat.py:223-252`

The `/chat/stream` endpoint calls the synchronous `chat()` function, waits for the **full response**, then simulates streaming by chunking the complete text into 50-char pieces. This gives no latency benefit — it's worse than regular chat because of SSE overhead.

**Recommendation**: Implement actual LLM streaming using Ollama's `"stream": True` and yield chunks as they arrive. Or remove the endpoint and document it as not-yet-implemented.

### 6. `datetime.utcnow()` Deprecation
**Files**: `src/models/schemas.py:85,204`, `src/events/publisher.py:39`

`datetime.utcnow()` is deprecated since Python 3.12. The codebase inconsistently uses both `datetime.now(UTC)` (correct, used in `chat.py`, `health.py`) and `datetime.utcnow()` (deprecated, used in schemas and events).

**Recommendation**: Replace all `datetime.utcnow()` with `datetime.now(UTC)`.

### 7. Version Inconsistency
**Files**: `src/main.py:85` vs `src/core/config.py:33` vs `src/api/v1/health.py:33`

- `main.py` and app description: `"16.0.0"`
- `config.py` Settings default: `"1.0.0"`
- `health.py` HealthResponse default: `"1.0.0"`
- `schemas.py` HealthResponse default: `"1.0.0"`

**Recommendation**: Use a single `SERVICE_VERSION` constant. The correct version per `pyproject.toml` / CLAUDE.md is `16.0.0`.

### 8. RAG `add_document` Endpoint Uses Query Params for Body Data
**File**: `src/api/v1/rag.py:74-107`

```python
@router.post("/documents", response_model=RAGDocument)
async def add_document(
    text: str,
    text_ar: str | None = None,
    ...
```

POST endpoint parameters without `Body()` annotation are interpreted as **query parameters** by FastAPI, not request body. This means document text is sent in the URL, which has length limits and is logged by proxies.

**Recommendation**: Use a Pydantic model for the request body:
```python
class AddDocumentRequest(BaseModel):
    text: str
    text_ar: str | None = None
    category: str | None = None
    metadata: dict[str, Any] | None = None
```

### 9. In-Memory Document Store Not Synced with Qdrant
**File**: `src/rag/service.py:112,464`

`CopilotRAGService` maintains `_documents: dict[str, RAGDocument]` as an in-memory fallback. But `list_documents()` only returns from this dict, not from Qdrant. After a service restart, all documents added via Qdrant are "lost" from listing even though they're searchable.

**Recommendation**: Implement `list_documents()` to query Qdrant using `scroll()` API when Qdrant is available.

### 10. Embedding Cache Has No Size Limit
**File**: `src/rag/embeddings.py:92`

```python
self._cache: dict[str, tuple[list[float], float]] = {}
```

The embedding cache grows unbounded. Each entry is ~1.5KB (384-dim float vector), so 100K unique queries = ~150MB. No eviction policy.

**Recommendation**: Use `functools.lru_cache` or implement a max-size eviction policy (e.g., LRU with max 10K entries).

---

## Medium Issues (P2) | مشاكل متوسطة

### 11. Duplicate Request ID Middleware
**File**: `src/main.py:176-204`

The code calls `_add_req_id(app)` from `shared.errors_py` (line 180) AND defines its own `add_request_id` middleware (line 196-204). This means request IDs are processed twice.

**Recommendation**: Remove the custom middleware and rely on `shared.errors_py`.

### 12. Global Mutable Singletons with `global` Keyword
**Files**: `src/rag/service.py:529-537`, `src/rag/embeddings.py:344-352`, `src/core/agents.py:249-257`, `src/security/guardrails.py:406-414`

Four modules use `global _instance` pattern. This is not thread-safe in multi-worker deployments and makes testing harder.

**Recommendation**: Use FastAPI's dependency injection with `app.state` or `Depends()` with cache.

### 13. `chat.py` Calls `rag_service.initialize()` on Every Request
**File**: `src/api/v1/chat.py:112`

Despite RAG being initialized in lifespan, every chat request calls `await rag_service.initialize()` again. The method has an `_initialized` guard, but it still acquires the service singleton and checks state on every request.

**Recommendation**: Trust the lifespan initialization and remove the redundant `initialize()` call in the hot path.

### 14. Proxy Functions Create New `httpx.AsyncClient` Per Request
**Files**: `src/api/v1/tools.py:248,271,306`, `src/api/v1/chat.py:368,389`

Every tool proxy call and LLM call creates a new `httpx.AsyncClient`. This means new TCP connections each time, no connection pooling.

**Recommendation**: Create a shared `httpx.AsyncClient` in `app.state` during lifespan and reuse it.

### 15. Agent Router Always Matches General (Score > 0)
**File**: `src/core/agents.py:136-143`

The `GENERAL` route has pattern `r".*"` which matches everything with score 0.5. Combined with `priority=0` giving a 0.0 boost, any message without specific keywords still gets a base score. But the routing loop sorts by `-priority` and iterates all routes, meaning `GENERAL` is checked last. If a specialized agent scores only 0.2 (e.g., one keyword match), it still beats `GENERAL`'s `0.0 + 0.5` pattern match... Actually, `GENERAL` gets `0.5` from pattern + `0.0` from priority = `0.5`. A specialized agent with one keyword gets `0.2 + 0.1 = 0.3`, so **GENERAL wins**. This means agent routing underperforms for weak intent signals.

**Recommendation**: Remove the `r".*"` pattern from GENERAL or give it score 0. Use GENERAL only as the fallback when no other route scores above a threshold.

### 16. Tests Are Outdated / Don't Match Current Code
**File**: `tests/test_copilot_api.py`

Multiple test assertions reference non-existent APIs:
- `healthz()` is tested as a function call, but it's an async FastAPI endpoint
- `ChatRequest` is tested with `message=` field but actual schema uses `messages=` (list)
- `ChatContext` is imported but doesn't exist in `schemas.py`
- `TOOL_ALLOWLIST` is checked for `"read_file"` which isn't in the actual allowlist
- `ToolCallRequest` is tested with `tool_name=` but actual schema uses `tool=`
- `BLOCKED_PATTERNS` is tested against regex patterns but it's actually file glob patterns
- `Settings.enable_guardrails` doesn't exist
- `Settings.get_available_providers()` doesn't exist

**Recommendation**: Rewrite tests to match the current API. Use `TestClient` from FastAPI for endpoint testing.

---

## Low Issues (P3) | مشاكل منخفضة

### 17. Weather Service Port Mismatch
**File**: `src/core/config.py:135`

```python
weather_service_url: str = Field(default="http://localhost:8108")
```

Per `CLAUDE.md` / governance, weather-service runs on port **8092**, not 8108.

### 18. Unused Imports
- `src/main.py:23`: `timezone` imported but only `UTC` is used
- `src/core/agents.py:5,16`: `Enum`, `Optional` imported but unused
- `src/models/schemas.py:11`: `Enum` imported but unused (uses `StrEnum`)

### 19. `get_guard()` Export Missing from `security/__init__.py`
**File**: `src/security/__init__.py`

`health.py:110` imports `get_guard` from `...security`, but `__init__.py` doesn't re-export it. This import works via Python module resolution but is inconsistent with the `__all__` list.

### 20. `format_context_for_prompt` Prefers Arabic Over English
**File**: `src/rag/service.py:508`

```python
text = doc.text_ar if doc.text_ar else doc.text
```

This unconditionally prefers Arabic text even for English queries. Should be language-aware based on the query language.

### 21. Batch Document Addition is Sequential
**File**: `src/rag/service.py:244-261`

`add_documents_batch()` calls `add_document()` in a serial loop. For Qdrant, this could be a single `upsert()` call with all points.

---

## Security Assessment | تقييم أمني

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Authentication** | Good | JWT with algorithm whitelist, required `exp` and `sub` claims |
| **Prompt Injection** | Good | 16 patterns (EN/AR), compiled regex, LLM token detection |
| **Tool Guardrails** | Excellent | 6-layer system with allowlists, size limits, pattern blocking, dangerous command detection |
| **Secrets Handling** | Good | Env vars, no hardcoded secrets, blocked patterns for sensitive files |
| **CORS** | Good | Configurable origins, explicit headers |
| **Error Handling** | Moderate | Debug info leaks in non-production (`str(exc)` in global handler) |
| **Input Validation** | Good | Pydantic models, field validators, size limits |
| **Dependency Security** | Needs Work | python-jose CVEs acknowledged but still used; PyJWT/jose conflict |

---

## Positive Highlights | نقاط إيجابية

1. **Excellent guardrails architecture**: The 6-layer `ToolGuard` system is well-designed with audit callbacks and statistics tracking
2. **Bilingual throughout**: Arabic/English error messages, agent routing, and advisory content
3. **Offline-first design**: Graceful degradation from Qdrant to keyword search, from LLM to fallback response
4. **Clean separation of concerns**: Security, RAG, agents, DB are all well-isolated modules
5. **UltraRAG integration**: Tri-RAG with agricultural, code, and satellite providers is architecturally sound
6. **Chat persistence**: Well-implemented PostgreSQL chat history with graceful no-op when DB unavailable
7. **NATS event publishing**: Copilot events are well-defined with clear subject naming
8. **Structured logging**: Consistent use of structlog throughout
9. **Docker best practices**: Multi-stage build, non-root user, health check, multi-mirror fallback
10. **Prompt injection detection**: Covers both English and Arabic patterns plus LLM special tokens

---

## Recommended Priority Order | ترتيب الأولوية الموصى به

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| P0-1 | JWT empty secret / fail-fast | Low | High |
| P0-2 | PyJWT vs python-jose conflict | Low | High |
| P0-3 | NATS connection never established | Low | High |
| P0-4 | Health probe connection churn | Medium | Medium |
| P1-5 | Fake streaming endpoint | Medium | Medium |
| P1-6 | `datetime.utcnow()` deprecation | Low | Low |
| P1-7 | Version inconsistency | Low | Low |
| P1-8 | RAG POST uses query params | Low | Medium |
| P1-9 | In-memory doc store not synced | Medium | Medium |
| P1-10 | Embedding cache unbounded | Low | Medium |
| P2-16 | Tests outdated | High | High |

---

## File-by-File Summary | ملخص ملف بملف

| File | LOC | Issues | Quality |
|------|-----|--------|---------|
| `main.py` | 356 | Duplicate middleware, no NATS init | Good |
| `config.py` | 171 | Version mismatch, weather port wrong | Good |
| `agents.py` | 258 | GENERAL always wins weak matches | Good |
| `schemas.py` | 217 | `utcnow()` deprecated, version mismatch | Good |
| `chat.py` | 436 | Fake streaming, redundant init, no connection pooling | Moderate |
| `tools.py` | 366 | New httpx client per request | Good |
| `rag.py` | 247 | POST params as query, no body model | Moderate |
| `health.py` | 129 | Connection churn in readiness | Moderate |
| `guardrails.py` | 450 | Global singleton pattern | Excellent |
| `prompt_guard.py` | 71 | Well-implemented | Excellent |
| `allowlists.py` | 198 | Comprehensive | Excellent |
| `deps.py` | 97 | Empty JWT secret, jose/pyjwt conflict | Moderate |
| `service.py` | 538 | Doc store not synced, list from memory only | Good |
| `embeddings.py` | 353 | Unbounded cache | Good |
| `ultrarag_integration.py` | 849 | Clean, well-structured | Excellent |
| `chat_store.py` | 479 | Graceful degradation, well-implemented | Excellent |
| `publisher.py` | 51 | `utcnow()`, never connected | Good |
| `Dockerfile` | 117 | Multi-stage, secure, mirrors | Excellent |
| `requirements.txt` | 42 | jose/pyjwt conflict | Moderate |
| `test_copilot_api.py` | 313 | Completely outdated, doesn't match code | Poor |

---

_End of Review_
