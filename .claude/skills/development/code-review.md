# Code Review Skill | مهارة مراجعة الكود

## Purpose | الغرض

Systematic code review skill for the SAHOOL National Agricultural Intelligence Platform.
Ensures all contributions meet platform standards for security, performance, reliability,
and domain correctness across Python (FastAPI), Node.js (NestJS), and Flutter codebases.

مهارة مراجعة منهجية للكود في منصة سهول الزراعية الذكية الوطنية.
تضمن أن جميع المساهمات تستوفي معايير المنصة من حيث الأمان والأداء والموثوقية.

---

## Review Checklist | قائمة المراجعة

### Python Services (FastAPI)

- [ ] **Health endpoints**: Service exposes `/healthz` (liveness) and `/readyz` (readiness) returning `{"status": "ok"}`
- [ ] **Lifespan pattern**: Uses `@asynccontextmanager async def lifespan(app)` for startup/shutdown (not deprecated `on_event`)
- [ ] **Error handling**: Imports and calls `setup_exception_handlers(app)` and `add_request_id_middleware(app)` from `shared.errors_py`
- [ ] **Auth dependencies**: Protected routes use `Depends(get_current_user)` from `shared.auth.dependencies`
- [ ] **NATS events**: Event subjects follow `sahool.{domain}.{action}` pattern; payloads are JSON-encoded with `tenant_id`
- [ ] **Pydantic v2**: Models use `model_config = ConfigDict(...)` instead of inner `class Config`; validators use `@field_validator`
- [ ] **Async DB access**: Uses `asyncpg` connection pools (`create_pool`) with proper `min_size`/`max_size`
- [ ] **Structured logging**: Uses `structlog.get_logger()` with keyword arguments, not f-strings or `%` formatting
- [ ] **Version constant**: `version` parameter in `FastAPI()` constructor matches `16.0.0`

### Node.js Services (NestJS)

- [ ] **Prisma schema**: Schema file exists at `prisma/schema.prisma`; migrations are committed
- [ ] **TypeScript strict**: `tsconfig.json` has `strict: true` enabled
- [ ] **Module structure**: Follows NestJS module pattern (`*.module.ts`, `*.controller.ts`, `*.service.ts`)
- [ ] **Guards**: Auth endpoints use NestJS guards; imports from `@sahool/nestjs-auth` where applicable
- [ ] **Contract imports**: Ports and endpoints imported from `@sahool/shared-types/contracts`, not hardcoded
- [ ] **Error responses**: Consistent error shape using platform `ApiResponse` type from shared-types

### Flutter (Mobile)

- [ ] **Riverpod state**: Uses `@riverpod` code generation or `StateNotifierProvider`; no raw `setState` in feature code
- [ ] **Drift database**: Local DB uses Drift with SQLCipher encryption; schema changes include migration steps
- [ ] **Offline-first**: Network calls have offline fallback; data is persisted locally before sync
- [ ] **Certificate pinning**: Dio client configured with pinned certificates for `*.sahool.app` domains
- [ ] **Secure storage**: Secrets stored via `flutter_secure_storage`, never in `SharedPreferences`
- [ ] **Background sync**: Long-running sync uses `Workmanager`, not raw isolates

### Shared Modules (`shared/`)

- [ ] **Backward compatibility**: Public function signatures are not broken; deprecated items have `@deprecated` markers
- [ ] **Bilingual support**: User-facing strings include both English and Arabic (`_ar` suffix fields)
- [ ] **Test coverage**: New code includes unit tests; coverage does not regress below CI threshold (5%)
- [ ] **Type hints**: All public functions have complete type annotations (Python 3.11+ syntax)

---

## Security Review | مراجعة الأمان

### OWASP Top 10 Checks

| Category | What to Check | مراجعة |
|----------|--------------|--------|
| **Injection** | All SQL uses parameterized queries (`$1`, `$2` with asyncpg) or ORM; no string concatenation | استعلامات محددة المعاملات |
| **Broken Auth** | JWT validation on every protected endpoint; token expiry enforced; refresh token rotation | التحقق من JWT |
| **Sensitive Data** | No secrets in code, logs, or error responses; PII masked in structured logs | عدم كشف البيانات الحساسة |
| **XXE** | XML parsing disabled or uses defusedxml; JSON preferred for all APIs | منع هجمات XXE |
| **Broken Access** | RBAC enforced via `shared.security`; tenant isolation verified on every query | التحكم في الوصول |
| **Misconfig** | Debug mode off in production; CORS restricted; no default credentials | تكوين آمن |
| **XSS** | All user input escaped in templates; React JSX auto-escapes; no `dangerouslySetInnerHTML` | منع XSS |
| **Deserialization** | Pydantic validates all incoming data; no `pickle.loads` on untrusted input | التحقق من البيانات الواردة |
| **Logging** | Security events logged (auth failures, permission denials); no sensitive data in logs | تسجيل الأحداث الأمنية |
| **SSRF** | External URLs validated; internal service calls use service discovery, not user input | منع SSRF |

### Additional Security Checks

- [ ] **SQL injection**: Verify all database queries use parameterized arguments, never f-strings or `.format()`
- [ ] **XSS prevention**: React components do not use `dangerouslySetInnerHTML`; API responses set proper `Content-Type`
- [ ] **Auth bypass**: No endpoints skip authentication unintentionally; public endpoints are explicitly marked
- [ ] **Secret exposure**: No API keys, passwords, or tokens in source code; `.env` files are gitignored
- [ ] **Rate limiting**: Public-facing endpoints have rate limits matching tier (Starter: 30/min, Enterprise: 120/min)
- [ ] **Input validation**: File uploads checked via `shared.file_validation`; size limits enforced (`MAX_UPLOAD_SIZE_MB`)
- [ ] **Container security**: Dockerfile uses non-root user `sahool` (UID 1000); no `--privileged` flags

---

## Performance Review | مراجعة الأداء

### Database Query Optimization

- [ ] **N+1 queries**: No loops issuing individual queries; use `JOIN`, `IN`, or batch fetch patterns
- [ ] **Missing indexes**: Columns used in `WHERE`, `ORDER BY`, and `JOIN` clauses have database indexes
- [ ] **Query complexity**: No unbounded `SELECT *`; pagination enforced on list endpoints (`LIMIT`/`OFFSET` or cursor)
- [ ] **Connection pooling**: asyncpg pool sizes are reasonable (`min_size=2, max_size=10`); PgBouncer in transaction mode

### Caching Patterns

- [ ] **Redis usage**: Frequently accessed, rarely changing data is cached; cache keys include `tenant_id` for isolation
- [ ] **TTL set**: All cache entries have explicit TTL; no unbounded cache growth
- [ ] **Cache invalidation**: Write operations invalidate related cache entries

### Memory and Compute

- [ ] **Large payloads**: Streaming used for file uploads/downloads; no full file buffering in memory
- [ ] **Batch processing**: Large datasets processed in chunks via `shared.batch_operations`
- [ ] **GPU resources**: Vision service models use LRU cache (`MODEL_CACHE_SIZE=5`); FP16 enabled for inference

---

## SAHOOL-Specific Patterns | أنماط سهول

### Event Subject Naming

Events MUST follow the 4-layer architecture naming convention:

```
sahool.{domain}.{action}                              # Base pattern
sahool.tenant.{tenant_id}.{domain}.{action}           # Tenant-scoped (preferred)
```

Verify: imported from `shared.events.subjects`, not hardcoded strings.

### Tenant Isolation

- `tenant_id` is extracted from JWT `tid` claim via `get_current_user`
- Every database query on tenant-scoped data MUST filter by `tenant_id`
- NATS events include `tenant_id` in payload; use `get_tenant_subject()` for scoped subjects

### Service Port Contracts

- Service ports MUST come from `@sahool/shared-types/contracts` (`SERVICE_PORTS.*`)
- Python services reference port via `PORT` environment variable, not hardcoded integers
- No local `const PORT = 3000` definitions; use the contract source of truth

### Unified Error Handling

- Python services call `setup_exception_handlers(app)` from `shared.errors_py`
- Error responses include bilingual messages (EN/AR) and request ID
- HTTP status codes follow platform conventions (400 validation, 401 auth, 403 forbidden, 404 not found, 429 rate limit, 503 service unavailable)

### Structured Logging

```python
# Correct
logger.info("field_created", field_id=field_id, tenant_id=tenant_id, area_ha=area)

# Incorrect - do not use
logger.info(f"Field {field_id} created")
logging.info("Field %s created", field_id)
```

---

## Review Output Format | تنسيق مخرجات المراجعة

### Severity Levels

| Level | Label | وصف | When to Use |
|-------|-------|------|-------------|
| **CRITICAL** | `[CRITICAL]` | حرج | Security vulnerabilities, data loss risks, auth bypass |
| **WARNING** | `[WARNING]` | تحذير | Performance issues, missing error handling, convention violations |
| **INFO** | `[INFO]` | معلومات | Minor style issues, documentation gaps, improvement opportunities |
| **SUGGESTION** | `[SUGGESTION]` | اقتراح | Optional enhancements, alternative approaches, refactoring ideas |

### Comment Format

Each review comment follows this structure:

```
[SEVERITY] file/path.py:LINE - Summary (EN)
الملخص (AR)

Description of the issue and recommended fix.
وصف المشكلة والإصلاح الموصى به.

Example fix (if applicable):
>>> before
>>> after
```

### Review Summary Template

At the end of a review, produce a summary:

```
## Review Summary | ملخص المراجعة

**Files reviewed**: N
**Issues found**: N (critical: X, warning: Y, info: Z, suggestion: W)

### Critical Issues | مشاكل حرجة
- [file:line] Description

### Warnings | تحذيرات
- [file:line] Description

### Verdict | الحكم
APPROVE | REQUEST_CHANGES | COMMENT

### Notes | ملاحظات
Additional context or recommendations for the author.
ملاحظات إضافية أو توصيات للمؤلف.
```

---

## Invocation | الاستدعام

This skill is triggered when reviewing code changes in the SAHOOL platform.
Apply all relevant checklist sections based on the files under review.
Prioritize critical security and data integrity issues above style concerns.

يتم تفعيل هذه المهارة عند مراجعة تغييرات الكود في منصة سهول.
طبّق جميع أقسام القائمة ذات الصلة بناءً على الملفات قيد المراجعة.
أعطِ الأولوية لمشاكل الأمان وسلامة البيانات على مسائل التنسيق.
