# SAHOOL Testing Strategy — Phase 1

_Last updated: 2026-04-19_

Phase 1 delivers the three foundations every later test layer depends on:
contract coverage for every FastAPI service, database-enforced tenant
isolation, and a reusable harness for integration tests that need real
infrastructure (Postgres/Redis/NATS).

Phases 2 and 3 (Playwright/Percy, Pact consumer-driven contracts, chaos,
synthetic monitoring, Flutter goldens) build on top and are tracked
separately.

---

## What's delivered

| Piece | Path | Executes where |
| ----- | ---- | -------------- |
| OpenAPI exporter | `scripts/export-openapi.py` | local + CI |
| OpenAPI specs (regenerated fresh on every run, uploaded as CI artifact) | `build/openapi-specs/` | CI (`build-specs` job) |
| Schemathesis static validation (every spec, per-spec matrix) | `.github/workflows/schemathesis-api-tests.yml` | CI |
| pgTAP suite — tenant isolation (RLS) | `tests/database/rls/` | local + CI |
| pgTAP workflow | `.github/workflows/pgtap-rls-tests.yml` | CI |
| Live-services fixtures (Postgres/Redis/NATS) | `tests/_helpers/live_services.py` | local + CI |
| Live-services smoke | `tests/live/` | local + CI |
| Live-smoke workflow | `.github/workflows/live-services-smoke.yml` | CI |

> **Design note:** generated OpenAPI specs are **not** committed to git
> (except the hand-authored `crop-intelligence-service/openapi.yaml`).
> They are regenerated on every CI run and published as the
> `openapi-specs` artifact. This eliminates the class of false failures
> that byte-compare drift checks produce when FastAPI's dict-insertion
> order varies across environments. Downloads: `Actions → your PR run →
> Artifacts → openapi-specs`.

## Usage

### Regenerate per-service OpenAPI specs

```bash
python3 scripts/export-openapi.py                       # all services
python3 scripts/export-openapi.py --service weather-service
python3 scripts/export-openapi.py --summary-json /tmp/summary.json
```

Services whose runtime dependencies are missing in the current environment
are skipped with a structured reason — the script never aborts the whole
run on a single import failure. In CI the same script runs inside the
`build-specs` job, and its output feeds the per-spec Schemathesis matrix.
There is no "committed spec vs. fresh spec" compare: the fresh spec *is*
the source of truth, so drift is impossible by construction.

### Run the pgTAP tenant-isolation suite

Locally, against any reachable Postgres 16 with pgTAP + PostGIS installed:

```bash
PG_USER=postgres PG_PASS=postgres bash tests/database/rls/run.sh
```

The suite is self-contained: `00_schema.sql` creates an isolated
`sahool_rls_test` schema, then `01_tenant_isolation.sql` asserts 14
properties (RLS enabled + FORCE, two policies, cross-tenant INSERT
rejected, super-admin bypass, etc.). CI wires the same script into a
service container running `postgis/postgis:16-3.4`.

### Run integration tests against real infrastructure

```bash
# Use services already running on localhost (dev shell, docker compose):
SAHOOL_TEST_FORCE_LOCAL=1 \
SAHOOL_TEST_POSTGRES_ADMIN_DSN=postgresql://postgres:postgres@127.0.0.1:5432/postgres \
pytest tests/live/

# Or let testcontainers manage everything (requires Docker daemon):
pip install testcontainers
pytest tests/live/
```

Fixtures auto-detect mode: explicit env vars win → testcontainers if a
Docker daemon is reachable → existing services on localhost → clean
`pytest.skip` if nothing works. The same test file runs on a dev laptop,
in GitHub Actions with a `services:` block, and in a containerised CI
runner without modification.

## Why these three, and why now

- **OpenAPI coverage first** because every later contract/E2E layer
  (Pact, Playwright, SDK codegen) consumes an OpenAPI spec as its source
  of truth. Without generated specs, 96 of the 97 services had no spec
  to consume and Schemathesis was blind to them.
- **RLS tests at the database** because tenant isolation is a
  correctness invariant, not a unit-test concern. A service can enforce
  it in code and still leak if someone forgets `WITH CHECK` in a
  migration. pgTAP catches that class of bug in the cheapest possible
  place.
- **Live-services harness** because mocking NATS/Redis/Postgres hides
  the exact bugs that bite in staging (pgbouncer transaction mode,
  JetStream ack semantics, Redis key TTL eviction). Testcontainers
  isolates each test run; the localhost fallback lets developers reuse
  the services they already have up.

## Runtime cost

| Job | Local | CI (cold) |
| --- | ----- | --------- |
| `scripts/export-openapi.py` (full) | ~25s | ~40s |
| `tests/database/rls/run.sh` | <2s | ~30s (container boot dominates) |
| `tests/live/` | ~3s | ~40s (container boot dominates) |
| Static Schemathesis matrix (per spec) | <5s each | ~2min total at 42 specs |

## What Phase 1 explicitly does NOT cover

- Live fuzz tests against running services — still gated on
  `workflow_dispatch`/schedule as before, because that needs Kong +
  staging auth to be meaningful.
- Consumer-driven contracts (Pact) — Phase 2.
- Visual regression (Percy/Chromatic, Flutter goldens) — Phase 3.
- Chaos testing on NATS — Phase 3.

## Extending the suite

- **New RLS tests**: drop a `NN_name.sql` file into `tests/database/rls/`
  (NN ≥ 01). `run.sh` and the CI workflow pick it up automatically;
  update the `plan(N)` count in the file header.
- **New integration tests**: use the existing fixtures from
  `tests/_helpers/live_services.py` — don't roll your own Postgres/Redis
  boot logic. Put the test under `tests/live/` or a new domain folder
  that imports the same fixtures via a local `conftest.py`.
- **New services**: the exporter picks them up automatically if the
  service ships `src/main.py` with an `app = FastAPI(...)` binding and
  its runtime deps are installable.
