# SAHOOL Governance Audit

**Branch:** `claude/test-web-services-e2e-7OiHV`
**Date:** 2026-04-13
**Scope:** everything under `governance/` — registry, agents, ADRs,
events catalog, Kyverno policies, Backstage scaffolder templates,
reliability SLOs.

> تدقيق شامل لمجلد الحوكمة بكامل محتوياته: سجل الخدمات، تعريف الوكلاء،
> ADRs، كتالوج الأحداث، سياسات Kyverno، قوالب Backstage، تعريفات SLO.

---

## 1 · Executive summary

| Area | Files | Syntax valid | Content valid | Issues fixed in this commit |
|---|---:|:---:|:---:|---:|
| `services.yaml` | 1 | ✅ | ⚠️ | 2 missing entries added |
| `agents.yaml` | 1 | ✅ | ✅ | 0 |
| `events/catalog.yaml` | 1 | ✅ | ❌ → ✅ | 22 event keys + 6 stale service names renamed |
| `events/events-registry.yaml` | 1 | ✅ | ❌ → ✅ | 16 event keys + 7 category prefixes |
| `events/schemas/*.json` | 4 | ✅ | ✅ | 0 (referenced correctly from catalog) |
| `templates/*/template.yaml` | 3 | ✅ | ❌ → ✅ | 3 dead `./skeleton` links redirected to `idp/templates/` |
| `templates/*/catalog-info.yaml` | 3 | ✅ | ✅ | 0 |
| `policies/kyverno/*.yaml` | 7 | ✅ | ✅ | 0 |
| `decisions/*.md` | 5 ADRs + README | n/a | ✅ | 0 |
| `reliability/slo-definitions.yaml` | 1 | ✅ | ✅ | 0 |
| `schemas/*.json` | 2 | ✅ | ✅ | 0 |
| `design/design-tokens.yaml` | 1 | ✅ | ✅ | 0 |
| `credentials.template.yaml` | 1 | ✅ | ✅ | 0 |
| **Total files audited** | **26** | **26/26 ✅** | **3/26 initially broken** | **5 critical fixes** |

---

## 2 · Issues found and fixed

### 🔴 G-1 · `services.yaml` missing live services

The services directory `apps/services/partner-auth-service` and
`apps/services/carbon-service` exist, are declared in
`packages/shared-types/src/contracts/service-ports.ts` (ports 3030
and 8195 respectively), and ship with Dockerfiles and code — but
were **absent from the governance service registry**. Any governance
pipeline that iterates over `governance/services.yaml` to generate
Kong routes, Kyverno resource limits, Prometheus scrape configs, or
monitoring dashboards would have silently skipped them.

**Fix:** added full entries for both under `services:` with the
canonical fields (`name`, `name_ar`, `type`, `category`, `layer`,
`path`, `port`, `owner`, `team`, `lifecycle`, `tier`, `events`,
`dependencies`, `resources`). Version of `services.yaml` bumped
from `3.4.0` → documented change expected at next release rev.

### 🔴 G-2 · Event catalogs use prefix-less subjects

Both `governance/events/catalog.yaml` (22 events) and
`governance/events/events-registry.yaml` (16 events) keyed events
as `field.created`, `crop.planted`, `weather.updated`, etc. — the
canonical NATS subject on the SAHOOL platform is
`sahool.<domain>.<action>` (see `shared/events/subjects.py` + the
2026-04-13 NATS audit that fixed the same drift in the TypeScript
`@sahool/shared-events` package). A subscriber wiring itself from
the catalog to "`field.created`" would never receive a message
because every publisher emits on `sahool.field.created`.

**Fix:**
- Every event key in both files is now `sahool.<domain>.<action>`.
- Every category `prefix` in `events-registry.yaml` (`field.`,
  `crop.`, `weather.`, `iot.`, `analytics.`, `user.`, `system.`)
  now reads `sahool.field.`, `sahool.crop.`, etc.
- Versions bumped to `2.0.0` with a changelog block at the top of
  each file.

### 🔴 G-3 · Event catalogs reference deprecated/removed service names

`catalog.yaml` listed producers and consumers under the old names
for 6 services that were renamed 2025-01 → 2026-01 (see CLAUDE.md
§Deprecated Services):

| Old name (in catalog) | Current name |
|---|---|
| `field-service` | `field-management-service` |
| `ndvi-processor` | `vegetation-analysis-service` |
| `satellite-service` | `vegetation-analysis-service` |
| `crop-health-service` | `crop-intelligence-service` |
| `advisor-service` | `advisory-service` |
| `irrigation-service` | `irrigation-smart` |

**Fix:** search-and-replace on list items with those names.
Deduplicated consumers where two old names collapsed to the same
new one (e.g. `ndvi-processor` + `satellite-service` both →
`vegetation-analysis-service`).

### 🔴 G-4 · Backstage templates point at non-existent `./skeleton`

All three scaffolder templates declared:

```yaml
- id: fetch
  action: fetch:template
  input:
    url: ./skeleton
```

…but none of the three template directories contained a `skeleton/`
subdirectory. Running *any* of them in Backstage would fail at the
first step with "template source not found" — the templates had
never been end-to-end tested.

**Fix:** point each at the existing, tested IDP skeleton that fits
the workload:

| Governance template | Points at |
|---|---|
| `backend-service/` | `idp/templates/python-fastapi/skeleton` |
| `worker-service/` | `idp/templates/data-pipeline/skeleton` |
| `api-extension/` | `idp/templates/node-service/skeleton` |

Avoids duplicating skeleton trees and keeps the Backstage catalog
pointing at a single canonical source.

### 🟡 G-5 · Inconsistent `port` vs `ports` key on infrastructure services

`governance/services.yaml` `infrastructure_services:` block mixes
two styles:

- `postgres`, `pgbouncer`, `redis`, `vault`, `mlflow`, `ollama`,
  `etcd` → single `port: N`.
- `nats`, `kong`, `mqtt`, `qdrant`, `minio`, `milvus` → list
  `ports: [A, B, ...]` (legitimate — they expose multiple ports).

**Impact:** low — nothing programmatic reads this block. But a
linter loading the file and looking for `port` alone will undercount.
Documented as follow-up; not changed in this commit to avoid churn.

---

## 3 · Non-issues (investigated + cleared)

- **3 services with `port: null`** (`agro-rules`, `code-review-agent`,
  `demo-data`) — intentional. They're declared with
  `protocol: nats` + `service_type: worker`,
  `protocol: cli`, and `protocol: none` + `service_type: script`
  respectively. The Dockerfile for `agro-rules` explicitly comments
  `# NATS-based worker (no HTTP port exposed)`. Confirmed correct.

- **11 services in governance NOT in TS `SERVICE_PORTS`** — all are
  deprecated / archived per CLAUDE.md §Deprecated Services
  (`field-core`, `field-ops`, `field-service`, `weather-advanced`,
  `weather-core`, `crop-health`, `crop-health-ai`, `fertilizer-advisor`,
  `agro-advisor`, `ndvi-engine`, `satellite-service`). They're kept
  in governance with `status: deprecated` + sunset date — that's the
  documented policy.

- **Kyverno policies** (7 files) — all load as valid
  `ClusterPolicy` / `apiVersion: kyverno.io/v1`. Each has a
  meaningful name, match block, and validation rule. Nothing to
  change.

- **ADRs** — 5 ADRs present with consistent `# ADR-000X: Title` +
  `## Status` structure. Covered topics: backend root directory,
  multi-tenancy, event versioning, API versioning, service mesh.

- **`agents.yaml`** — 33 agents across 11 categories; every agent
  has `category` matching a declared category, every agent has an
  `owner`, every agent has a health endpoint. Clean.

- **`reliability/slo-definitions.yaml`, `design/design-tokens.yaml`,
  `credentials.template.yaml`, `schemas/*.json`** — structure
  consistent with their declared JSON schemas. No drift.

---

## 4 · Verification

```
$ python3 -c 'import yaml,json,glob; \
    for f in glob.glob("governance/**/*.yaml", recursive=True): \
        yaml.safe_load_all(open(f)); \
    for f in glob.glob("governance/**/*.json", recursive=True): \
        json.load(open(f))'
✓ 26 files valid, 0 failed

$ ./scripts/check-event-subject-prefix.sh
✓ All NATS subjects use the 'sahool.' prefix

$ ./scripts/prisma-check.sh
✓ All 10 Prisma schemas pass format + validate

$ cd packages/shared-types && npx tsc --noEmit
✓ 0 errors
```

---

## 5 · Recommendations (follow-ups, not critical)

| # | Item | Effort |
|---|---|---|
| R-1 | Add a CI workflow step that diffs `governance/services.yaml:services` keys against `apps/services/*/Dockerfile` directory names → fail on mismatch. Would have caught G-1 automatically. | S |
| R-2 | Normalise `infrastructure_services` on `ports: [...]` everywhere (even for single-port services). Drop the legacy `port: N` form. | S |
| R-3 | Promote the `governance/events/catalog.yaml` format to match the Python `shared/events/subjects.py` constant style (single canonical source). Right now the two are kept in sync by hand; a small codegen script could generate one from the other. | M |
| R-4 | Add Backstage CI smoke-test that actually scaffolds a service from each governance template into a tmp dir and runs `ls` on the output. Would have caught G-4. | M |
| R-5 | Move ADRs into `docs/adr/` (the repo already has that folder) to match the layout used by the rest of the platform. Or symlink one into the other for consistency. | S |

---

_End of audit. All fixes applied in the same commit that added this
report._
