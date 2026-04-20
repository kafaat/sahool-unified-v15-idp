# test-harness-sidecar

**Location**: `apps/services/test-harness-sidecar/`
**Port**: 8299 (outside production HTTP service ranges)
**Status**: PR 1 — lifecycle + introspection only

---

## Why this exists

The SAHOOL E2E test framework needs three capabilities that production
services can't expose safely:

1. **Seed** test data deterministically (re-runs don't drift)
2. **Introspect** DB invariants (RLS enforcement, geometry validity)
3. **Observe** NATS events deterministically (without flaky polling)

A separate sidecar isolates these capabilities behind hard production
guards.

---

## Scope of THIS PR (PR 1)

| Endpoint | Status |
|----------|--------|
| `GET /healthz` | ✅ Implemented |
| `GET /readyz` | ✅ Implemented |
| `GET /version` | ✅ Implemented |
| `GET /test-introspect/v1/invariants/fields/{fieldId}` | ✅ Implemented |
| `GET /test-introspect/v1/invariants/rls/{tenantId}` | ✅ Implemented |

Out of scope — deferred to follow-up PRs:
- `/test-seed/v1/farmers` — needs schema design discussion (current
  `farmers` table has UUID PK, requires NOT NULL `name`, no
  `password_hash` column, no `region` column)
- `/test-events/v1/sinks/*` — depends on `shared/events/nats_client.py`
  which doesn't exist yet on main
- `/test-introspect/v1/invariants/advice/{id}/audit` — depends on
  `advice_audit` table which doesn't exist yet

---

## Production-guard stack (7 layers)

| # | Layer | Where |
|---|-------|-------|
| 1 | Pydantic ENVIRONMENT validator refuses 'production' | `src/config.py` |
| 2 | Module-level `_enforce_production_guard()` at import time | `src/main.py` |
| 3 | Lifespan re-checks at runtime | `src/main.py` |
| 4 | Per-request: tenant_id MUST be in `TEST_TENANT_WHITELIST` | (PR 2 — on seed) |
| 5 | Helm chart `{{ fail }}` if `values.environment == 'production'` | `helm/templates/deployment.yaml` |
| 6 | Non-root user in container | `Dockerfile` |
| 7 | Production Kong ingress class is NOT bound (staging-only class) | `helm/templates/deployment.yaml` |

There is **no override flag** in this version. Production accidents
require renaming `ENVIRONMENT` in source — visible diff, mandatory PR review.

---

## Adapter shim around `shared.db.tenant_connection`

The introspection probe wants a simple two-method API:

```python
async with admin_connection() as conn: ...
async with tenant_connection(tenant_id) as conn: ...
```

The shared module's actual signature takes the pool as its first
argument:

```python
async with tenant_connection(pool, tenant_id="...") as conn: ...
```

`src/db_adapter.py` holds the singleton pool and exposes the simpler
signatures, **delegating to the SAME `shared.db.tenant_connection`
function** production services use. If RLS-context handling has a bug
in production, this probe inherits it — which is the point.

---

## Local development

```bash
cd apps/services/test-harness-sidecar
pip install -r requirements.txt

export ENVIRONMENT=local
export TEST_SEED_TOKEN=$(openssl rand -hex 32)
export POSTGRES_DSN=postgresql://sahool:sahool@localhost:5432/sahool_dev

uvicorn src.main:app --port 8299 --reload

curl http://localhost:8299/healthz   # {"alive": true}
curl http://localhost:8299/readyz    # {"ready": ..., "database": ..., "test_mode": true, "nats": null}
curl http://localhost:8299/version   # {"sidecar_version": "1.0.0", "contract_version": "1.0.0", ...}
```

---

## Testing the tester (3 layers)

### Schemathesis dogfooding — `tests/test_openapi_dogfood.py`

The sidecar's own `openapi.yaml` is loaded through the same
property-based contract tooling the sidecar exists to enable.

```bash
pytest apps/services/test-harness-sidecar/tests/test_openapi_dogfood.py -v
```

### pgTAP truthfulness — `tests/pgtap/test_introspection_truthfulness.sql`

Verifies the introspection probe is **not a yes-man**:
- WHEN RLS is enforced → leakage probe reports `false` (cross-tenant blocked)
- WHEN RLS is DISABLED → leakage probe reports `true` (probe sees the leak)

If both branches return the same answer, the probe is a lie and the
entire E2E confidence is fake.

```bash
PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d postgres \
  -f apps/services/test-harness-sidecar/tests/pgtap/test_introspection_truthfulness.sql
```

### Lifecycle + config-guards — `tests/test_lifecycle.py` + `test_config_guards.py`

Pure unit tests, no DB needed. Verify:
- `/healthz`, `/version` work without lifespan startup
- `/readyz` returns 503 when DB pool is missing (correct behaviour)
- Auth-protected endpoints reject missing/wrong tokens
- Pydantic validators refuse `ENVIRONMENT=production`, unsafe tenant
  prefixes, short seed tokens

```bash
pytest apps/services/test-harness-sidecar/tests/ -v
```

---

## Contract version: bumped on EVERY shape change to openapi.yaml

The framework reads `contract_version` from `/version` and aborts if
it doesn't match the version it was built against. This prevents
silent contract drift between the sidecar and the test suite.

Semver:
- **MAJOR**: removed endpoint, renamed field, type change → framework breaks
- **MINOR**: new endpoint, new optional field → backward-compatible
- **PATCH**: docs, examples → no compatibility impact
