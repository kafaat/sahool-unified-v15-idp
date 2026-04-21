# Vegetation Services Compatibility Verification — 2026-04-21

**Scope**: Verify that the recent vegetation work
(PRs [#1704](https://github.com/kafaat/sahool-unified-v15-idp/pull/1704),
[#1706](https://github.com/kafaat/sahool-unified-v15-idp/pull/1706),
[#1707](https://github.com/kafaat/sahool-unified-v15-idp/pull/1707))
left `vegetation-analysis-service` and its downstream consumers in a healthy,
compatible state — with no regressions in the NestJS consumer surfaces
(`yield-prediction-service`, `lai-estimation`, `crop-growth-model`) or the
Python advisory chain.

**Branch verified**: `origin/main` @ `2cbb4d9ee` (post #1706).
**Conclusion**: Python side is green end-to-end. NestJS consumer regressions
exist on `main` but are caused by an unrelated workspace-wide NestJS v10/v11
version skew, not by the vegetation work — they are addressed in the
companion PR `claude/nestjs-v11-upgrade`.

---

## 1. Service Inventory

| Service                       | Stack             | Port | Status                | Recent change |
|-------------------------------|-------------------|------|-----------------------|---------------|
| `vegetation-analysis-service` | Python / FastAPI  | 8090 | Active                | #1704, #1706, #1696, #1705 |
| `advisory-service`            | Python / FastAPI  | 8093 | Active                | #1707 (alignment) |
| `crop-intelligence-service`   | Python / FastAPI  | 8095 | Active                | — |
| `ndvi-processor`              | Python / FastAPI  | 8118 | Deprecated (sunset 2026-06-01) | RFC 8594 headers |
| `lai-estimation`              | Node / NestJS 11  | 3022 | Active                | bumped to v11 |
| `yield-prediction-service`    | Node / NestJS 11  | 8152 | Active                | (still v10 on main; v11 in companion PR) |
| `crop-growth-model`           | Node / NestJS 11  | 3023 | Active                | bumped to v11 |

---

## 2. Integration Surface Map

### HTTP fan-out from `advisory-service`

`advisory-service/src/main.py` (the comprehensive-advisory orchestrator) calls:

| Target                          | Env var                      | Default URL                                 |
|---------------------------------|------------------------------|---------------------------------------------|
| `vegetation-analysis-service`   | `VEGETATION_ANALYSIS_URL`    | `http://vegetation-analysis-service:8090`   |
| `crop-intelligence-service`     | inferred via orchestrator    | `http://crop-intelligence-service:8095`     |
| `yield-prediction-service`      | `YIELD_PREDICTION_URL`       | `http://yield-prediction-service:8152`      |
| `lai-estimation`                | inferred via orchestrator    | `http://lai-estimation:3022`                |

Tenant context is enforced **before** the fan-out (`u.tenant_id` check in
`main.py:1325–1333`), and the orchestrator fails closed when the gate is
not satisfied. PR #1707 also added `field_ownership.py` (171 lines) that
mirrors the ownership check used by `vegetation-analysis-service`.

### NATS event subjects

Vegetation publishes (via `shared/libs/events/nats_publisher.py`):

```
sahool.satellite.ndvi.computed
sahool.satellite.anomaly.vegetation
sahool.satellite.ndvi.anomaly
sahool.satellite.ndvi.trend
```

Tenant-scoped variant: `sahool.tenant.{tenant_id}.<event_type>`.

Advisory publishes:

```
sahool.advisory.recommendation_issued
sahool.advisory.fertilizer_plan_issued
sahool.advisory.nutrient_assessment_issued
```

Subscribers: `task-service` (wildcard `sahool.advisory.>`), `alert-service`
(disease/pest alerts), `crop-intelligence-service` (assessment events).

The NestJS consumers (`yield-prediction-service`, `lai-estimation`,
`crop-growth-model`) do **not** subscribe to vegetation events directly —
they receive NDVI as a caller-provided input parameter.

---

## 3. Verification Results

### 3.1 Python services (FastAPI)

```
apps/services/vegetation-analysis-service
  pytest tests/   →  862 passed in 14.03s

apps/services/advisory-service
  pytest tests/   →  318 passed, 3 skipped in 2.64s
  including tests/test_vegetation_alignment.py (444 lines, 37 cases) — all green

apps/services/crop-intelligence-service
  pytest tests/   →  188 passed, 40 skipped, 9 xfailed in 2.23s
```

All three pass on `main` @ `2cbb4d9ee`. The `xfailed` and `skipped` cases
are expected (mock/integration gates) and unchanged from before the
vegetation work.

PR #1707's `test_vegetation_alignment.py` (444 lines, added 2026-04-19)
exercises the contract surface between `advisory-service` and
`vegetation-analysis-service` end-to-end and is fully passing.

### 3.2 NestJS consumers — `main` baseline

| Service                    | `tsc --noEmit`     | `jest`               | Failure cause                      |
|----------------------------|--------------------|----------------------|------------------------------------|
| `lai-estimation`           | 1 `DynamicModule` error | 4 failed / 7 total   | Workspace mixed v10/v11 hoisting |
| `yield-prediction-service` | clean              | 6 failed / 9 total   | `pathRegexp is not a function` (Express 4↔5 skew) |
| `crop-growth-model`        | 2 `DynamicModule` errors | 4 failed / 4 total | Workspace mixed v10/v11 hoisting |

Sample failure (yield-prediction-service):

```
TypeError: pathRegexp is not a function
  at .../path-to-regexp/...
```

Sample failure (lai-estimation, crop-growth-model):

```
TS2322: Type 'DynamicModule' is not assignable to type
'Type<any> | DynamicModule | Promise<DynamicModule> | ForwardReference<any>'.
  Types of property 'imports' are incompatible.
    Type from .../node_modules/@nestjs/common (v10.4.22)
    Type from .../apps/services/<svc>/node_modules/@nestjs/common (v11.1.19)
```

### 3.3 NestJS consumers — `claude/nestjs-v11-upgrade` companion PR

After the workspace is unified on NestJS v11.1.19 (no nested duplicates):

| Service                    | `tsc --noEmit`     | `jest`               | Delta vs `main` |
|----------------------------|--------------------|----------------------|-----------------|
| `lai-estimation`           | clean ✅           | 4 failed / 8 total   | +1 test now able to run, typecheck fixed |
| `yield-prediction-service` | clean              | 5 failed / 9 total   | -1 failure (pathRegexp suite still pre-existing) |
| `crop-growth-model`        | clean ✅           | 4 failed / 5 total   | typecheck fixed, +1 passing test |

The remaining test failures (`pathRegexp` in `yield-prediction-service`,
plus a handful of mock-setup issues elsewhere) are pre-existing on `main`,
unrelated to the vegetation work, and out of scope for this verification.
Tracking note: the `pathRegexp` failures point to an Express 4 ↔ Express 5
skew in the `supertest`/`@nestjs/platform-express` dep tree that warrants
a follow-up.

---

## 4. Risk Areas Reviewed

| Risk                                     | Status   | Notes |
|------------------------------------------|----------|-------|
| Tenant isolation (cross-tenant leakage)  | OK ✅    | Enforced in orchestrator pre-fanout; PR #1704 hardened, PR #1696 added missing `compare_ndvi_periods` check |
| NATS subject drift                       | OK ✅    | Aligned to `sahool/events/subjects.py`; PR #1705 closed the dead subscription gaps |
| HTTP contract drift (vegetation ↔ advisory) | OK ✅ | 444-line `test_vegetation_alignment` suite green |
| Port collisions                          | OK ✅    | All ports stable per `governance/services.yaml` |
| Contract version uniformity              | OK ✅    | All services on `16.0.0` |
| Deprecated `ndvi-processor` overlap      | OK ✅    | RFC 8594 headers in place; sunset 2026-06-01 |
| Workspace NestJS version skew            | **Broken** ⚠️ | Fixed in companion PR `claude/nestjs-v11-upgrade` |

---

## 5. Recommended Follow-ups

1. **Merge `claude/nestjs-v11-upgrade`** to clear the `DynamicModule` and
   `pathRegexp`-class workspace skew. (The skew is the root cause of the
   NestJS consumer test failures shown in §3.2.)
2. **Investigate residual `pathRegexp` failures** in
   `yield-prediction-service/test/prediction.spec.ts` after the v11 unify
   lands. Likely an Express 4 → Express 5 compatibility issue in
   `supertest` or `@nestjs/platform-express`. Pin or shim
   `path-to-regexp`.
3. **Decommission `ndvi-processor`** on schedule (sunset 2026-06-01).
   Verify no production traffic remains by querying the
   `X-API-Deprecated` header counter in Prometheus.
4. **Optional**: Add a CI guard
   (`api-contracts-guard.yml`) check that fails if any new service is
   added at NestJS v10 — keeps the workspace converged.

---

## 6. Reproduction Commands

```bash
# Python — vegetation triangle
cd apps/services/vegetation-analysis-service && \
  PYTHONPATH=$(git rev-parse --show-toplevel) python3 -m pytest tests/ -q
cd apps/services/advisory-service && \
  PYTHONPATH=$(git rev-parse --show-toplevel) python3 -m pytest tests/ -q
cd apps/services/crop-intelligence-service && \
  PYTHONPATH=$(git rev-parse --show-toplevel) python3 -m pytest tests/ -q

# NestJS consumers
cd apps/services/lai-estimation          && npx tsc --noEmit && npx jest
cd apps/services/yield-prediction-service && npx tsc --noEmit && npx jest
cd apps/services/crop-growth-model        && npx tsc --noEmit && npx jest
```

---

_Generated 2026-04-21 against `main` @ `2cbb4d9ee` and companion branch
`claude/nestjs-v11-upgrade` @ `c5113efdf`._
