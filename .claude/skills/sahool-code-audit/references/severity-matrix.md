# SAHOOL Severity Matrix

Use this matrix to re-classify raw tool output into SAHOOL-specific severity during Phase 2 of the audit skill.

## CRITICAL — Block merge, fix immediately

| Pattern | Detection | Example |
|---|---|---|
| Secret in code | bandit B105/B106, gitleaks, manual | Hardcoded `JWT_SECRET_KEY = "abc"` |
| Auth bypass | Manual review | Route missing `Depends(get_current_user)` on protected resource |
| SQL injection | bandit B608 | `f"SELECT * FROM t WHERE id = {user_input}"` |
| Missing tenant_id | Manual + NATS subject check | `nc.publish("sahool.field.created", payload)` without tenant scoping |
| Missing RBAC | Manual | Handler accepts any authenticated user for tenant-scoped resource |
| Cert pinning disabled | grep in Dio setup | `InterceptorsWrapper` without pinning for `*.sahool.app` |
| SQLCipher disabled | Flutter Drift config | Local DB without encryption key |

## HIGH — Fix before merge unless explicitly deferred

| Pattern | Detection | Example |
|---|---|---|
| Contract drift | `/check-contracts` | New error code not in Dart side |
| Hardcoded port/endpoint | grep for numeric ports | `const PORT = 3025` instead of `SERVICE_PORTS.AUTH` |
| NATS subject violation | Manual | Subject not matching `sahool.{domain}.{action}` |
| PHI/dosage misstatement | Advisory review | Incorrect pesticide rate, missing PHI days |
| Missing request_id propagation | Manual | Middleware not chained correctly |
| Missing rate limiting | Manual | Public endpoint without tier check |
| Deprecated `@app.on_event` | ruff/grep | Should use `lifespan` async context manager |

## MEDIUM — Fix during normal flow

| Pattern | Detection | Example |
|---|---|---|
| Pydantic v1 style | ruff UP | `class Config:` instead of `model_config = ConfigDict(...)` |
| Unstructured logging | grep | `logger.info(f"...")` instead of `logger.info("event", key=value)` |
| Missing `/healthz` or `/readyz` | Manual route check | Service without required health probes |
| Missing type hints on public API | mypy | Exported function without annotations |
| Riverpod anti-pattern | flutter_lints | `setState` in feature code |
| Wrong version string | grep | `FastAPI(version="1.0")` instead of `"16.0.0"` |

## LOW — Fix with FixOps SAFE strategy

| Pattern | Detection |
|---|---|
| Import order | ruff I001 |
| Unused import/var | ruff F401, F841 |
| Line length | ruff E501 |
| Missing docstring | ruff D1xx |
| Trailing whitespace | ruff format |

## Domain overlay triggers

When a finding touches one of these areas, invoke the matching subagent via the Agent tool:

| Overlay | Trigger conditions | Subagent |
|---|---|---|
| PostGIS/PgBouncer | `*.sql`, `GeoAlchemy`, raster handling, `shared/field_boundaries/` | `postgis-optimizer` |
| Arabic/RTL/bilingual | User-facing text, Arabic strings, `shared/nlp/`, mobile advisor screens | `arabic-rtl-tester` |
| API contracts | Changes under `packages/shared-types/src/contracts/*` or imports from it | `contract-guard` |

Domain subagents produce their own pass/fail verdict. Incorporate their verdict into the audit report before moving to Phase 3.
