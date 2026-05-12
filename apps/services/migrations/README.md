# Platform-wide Migrations | الترحيلات المشتركة للمنصة

> **This is not a service.** This directory holds SQL migrations whose tables
> are shared across multiple SAHOOL services (typically because the tables
> back data flows that no single service owns end-to-end).
>
> هذا المجلد **ليس خدمة**. يحتوي على ترحيلات SQL مشتركة بين أكثر من
> خدمة سهول واحدة (عندما يكون الجدول يخدم تدفّقًا لا تملكه خدمة بعينها).

## When to add a migration here

Add a file here only when **all** of the following apply:

1. The new tables are read or written by **two or more services**.
2. No single service can be considered the "owner" of the schema.
3. The migration must run before the dependent services start.

If the tables belong to one service, put the migration under that service's
own `migrations/` (or `prisma/migrations/`) directory instead.

## File naming convention

Files follow Flyway-style naming so they sort lexicographically:

```
V{YYYYMMDD}[__{N}]__{snake_case_description}.sql
```

Examples already in this directory:

| File | Description |
| ---- | ----------- |
| `V20260131__add_integration_tables.sql` | YOLO26 detections, terrain analyses, hydrology results, leveling plans, edge device registrations |

## Drift annotation

Each file should begin with a `-- drift:safe reason=…` comment when it uses
`CREATE INDEX` without `CONCURRENTLY` inside the same transaction that
creates the table. The repository's drift-detection check parses this
annotation to suppress false positives. See
`V20260131__add_integration_tables.sql` lines 1–7 for the canonical example.

## Execution

The header comment of `V20260131__add_integration_tables.sql` references
"the SAHOOL migration runner" and assumes a single-transaction execution
model (which is why `CREATE INDEX CONCURRENTLY` is intentionally avoided —
see the `-- drift:safe reason=…` annotation on that file).

In practice, no central runner is wired up in `Makefile` for this
directory today (`make db-migrate` only invokes per-service
`npx prisma migrate deploy`, and `make db-migrate-all` additionally calls
`alembic upgrade head` when `alembic.ini` is present). Until a dedicated
runner target is added, apply these files manually inside a single
transaction:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 --single-transaction \
  -f apps/services/migrations/V20260131__add_integration_tables.sql
```

These files are **not** picked up by per-service Prisma or Alembic
migration tools.

## See also

- `database/seeds/` — sample data loaders (run **after** migrations).
- `docs/database/` — database audit summaries and ERDs.
- `docs/migrations/` — migration guides for deprecated-service moves.
