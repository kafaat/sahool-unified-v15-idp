# SAHOOL Audit Retention Worker

Nightly CronJob that deletes rows from `audit_log` once they exceed their
configured retention window, and records the deletion in
`audit_retention_events` so compliance can reconstruct what was removed.

| | |
|---|---|
| **Runtime** | One-shot Python 3.11 CLI |
| **Trigger** | Kubernetes `CronJob` (default: `0 3 * * *` Asia/Riyadh) |
| **DB role** | `audit_retention` (created by audit-service migration 002) |
| **Writes** | `audit_log` (DELETE), `audit_retention_events` (INSERT) |
| **Reads** | `audit_log`, `audit_retention_schema_migrations` |
| **Owner** | Audit / Compliance platform team |

---

## Why this exists

Every row in `audit_log` stays forever unless someone deletes it. At
steady-state ingest the table grows by roughly a row per user-action,
which means tens of millions of rows per year for a mature tenant. Three
things break if this is allowed to run unbounded:

1. **Query latency** — even with the indexes from migration 001, a
   multi-year scan for a single tenant eventually runs out of buffer
   pool budget.
2. **Backup RPO** — nightly `pg_dump`s / WAL-G snapshots grow linearly
   and eventually exceed the backup window.
3. **GDPR Article 5(1)(e)** — personal data (authentication trails,
   user-management events) must be kept no longer than necessary.
   "Forever" is not a defensible retention period.

This worker fixes all three by applying per-category retention rules on
a nightly schedule.

---

## How it works

```
┌──────────────┐   1. SET LOCAL sahool.audit_retention_job = 'on'
│   CronJob    │───2. Find last-retained seq_num + entry_hash per (tenant × category)
│   (this)     │───3. DELETE FROM audit_log WHERE ... (single statement)
│              │───4. INSERT INTO audit_retention_events (audit trail of the deletion)
└──────────────┘   5. Commit, next (tenant × policy)
```

* Each `(tenant, policy)` pair runs in its own transaction — a failure
  in one tenant doesn't block the rest.
* The retention trigger bypass is set with `SET LOCAL`, so even a crash
  mid-run can't leave a session with mutation rights on `audit_log`.
* The append-only trigger from migration 001 is the last line of defence
  against accidental deletes; the worker is the *only* caller legally
  permitted to bypass it.

### Chain integrity

`audit_log` carries a per-tenant SHA-256 hash chain (see
`apps/services/audit-service/src/persistence.py::compute_entry_hash`).
Retention deletes break that chain at the retention boundary — this is
unavoidable and expected. To keep the break auditable:

* For each DELETE we record the **highest `seq_num` and `entry_hash`
  being deleted** in `audit_retention_events`.
* A future audit-service PR will teach `validate_chain()` to consult
  this table and accept chain gaps that align with a retention event.
  Until then, `validate_chain()` will report a broken chain for tenants
  with retention history — operators can cross-reference the
  `audit_retention_events` table to confirm the break is legitimate.

---

## Configuration

Set these environment variables on the CronJob pod (see also
`.env.example`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `AUDIT_RETENTION_DATABASE_URL` | yes* | — | asyncpg DSN connecting as the `audit_retention` role. |
| `DATABASE_URL` | fallback | — | Used if `AUDIT_RETENTION_DATABASE_URL` is unset (for local dev only). |
| `AUDIT_RETENTION_DEFAULT_DAYS` | no | — | Platform-wide fallback for any category without its own override. |
| `AUDIT_RETENTION_<CATEGORY>_DAYS` | no | — | Per-category override (e.g. `AUDIT_RETENTION_AUTHENTICATION_DAYS=90`). |
| `AUDIT_RETENTION_DRY_RUN` | no | `false` | If truthy, skip DELETE + event insert. |
| `LOG_LEVEL` | no | `INFO` | Standard Python log level. |

\* Either `AUDIT_RETENTION_DATABASE_URL` or `DATABASE_URL` must be set.
Production deployments should always use the former so the worker
connects as the dedicated role.

Categories must match the `chk_category` CHECK constraint on
`audit_log`:

```
authentication  authorization  configuration  catalog
kubernetes      field_ops      billing        compliance
security        data           system         user_management
code_change
```

A category with no policy (neither an override nor a default) is
**skipped** — the worker deletes nothing for it. This is the safe
default; a misconfigured deployment is a no-op, not a nuclear event.

### Suggested defaults

Aligned with the platform's compliance matrix:

| Category | Days | Rationale |
|---|---|---|
| `authentication` | 90 | GDPR minimisation — login/logout trails. |
| `user_management` | 90 | GDPR minimisation — profile changes. |
| `system` | 90 | Housekeeping only. |
| `authorization`, `configuration`, `catalog`, `security`, `data`, `kubernetes`, `code_change` | 365 | SOC 2 / ISO 27001 security event retention. |
| `field_ops`, `billing`, `compliance` | 1825 | GlobalGAP IFA v6 five-year retention. |

---

## Deployment

### Helm (recommended)

```bash
helm upgrade --install audit-retention-worker \
  helm/charts/audit-retention-worker \
  --namespace sahool \
  --set image.tag=16.0.0
```

See `helm/charts/audit-retention-worker/values.yaml` for the full
surface; the `retention.*` keys expand into the env vars above.

### Plain kubectl

```bash
kubectl apply -f apps/services/audit-retention-worker/k8s/cronjob.yaml
```

### Ad-hoc run (for backfill or debugging)

```bash
kubectl create job --from=cronjob/audit-retention-worker adhoc-$(date +%s)
```

Add `--dry-run` (via the pod's args) to preview without deleting.

---

## Operations

### Normal operation

```
{"level":"INFO","logger":"audit-retention-worker","msg":"policies.resolved","text":"retention policies:\n  authentication    →    90 days\n  ..."}
{"level":"INFO","logger":"audit-retention-worker.src.retention","msg":"retention.deleted","tenant_id":"t-1","category":"authentication","rows_deleted":42,"last_retained_seq_num":1839}
{"level":"INFO","logger":"audit-retention-worker","msg":"sweep.complete","dry_run":false,"total_deleted":42,"tenants_touched":1,"duration_seconds":0.187}
```

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ERROR policies.none_configured` | No `AUDIT_RETENTION_*_DAYS` env var set. | Set `AUDIT_RETENTION_DEFAULT_DAYS` or at least one per-category override. |
| `ERROR dsn.connect_failed` | `AUDIT_RETENTION_DATABASE_URL` is unset or points at an unreachable PgBouncer. | Provide the full DSN with the `audit_retention` role's password. |
| `audit_log is append-only; DELETE blocked` | The trigger bypass didn't fire. Almost always means the worker connected as the wrong role. | Confirm the DSN authenticates as `audit_retention`, not `sahool_audit`. |
| `0 rows deleted` every run | Retention windows are longer than the oldest row. | Expected for young deployments; check `audit_log` row age distribution. |
| `validate_chain()` reports BROKEN after retention | Expected. Cross-reference `audit_retention_events`. | Track the follow-up issue to teach `validate_chain()` about retention events. |

### Metrics (follow-up)

The worker currently emits structured logs only. A follow-up PR will
add Prometheus pushgateway support so the CronJob's short-lived runs
feed the same dashboard panels as audit-service's own metrics:
`audit_retention_rows_deleted_total`, `audit_retention_last_run_timestamp`,
`audit_retention_last_run_duration_seconds`.

---

## Testing

```bash
cd apps/services/audit-retention-worker
python -m pytest tests/ -v
```

The tests use an in-process asyncpg fake — no Postgres needed. Schema
correctness (append-only trigger, retention role privileges, migration
idempotence) is covered by audit-service's own integration suite.

---

## Related

* `apps/services/audit-service/migrations/001_create_audit_log.sql` — audit_log schema + append-only trigger.
* `apps/services/audit-service/migrations/002_audit_retention_role.sql` — `audit_retention` role.
* `apps/services/audit-retention-worker/migrations/003_audit_retention_events.sql` — deletion audit trail.
* `helm/charts/audit-retention-worker/values.yaml` — Helm deployment surface.
