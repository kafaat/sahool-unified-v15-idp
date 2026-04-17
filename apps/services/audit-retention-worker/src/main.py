"""
SAHOOL Audit Retention Worker — CLI entrypoint.

Usage::

    python -m src.main [--dry-run]

Environment variables (see README for the full list):

* ``AUDIT_RETENTION_DATABASE_URL`` — asyncpg DSN. Must connect as the
  ``audit_retention`` role (created by migration 002) so the append-only
  trigger on ``audit_log`` lets the DELETE through. Falling back to
  ``DATABASE_URL`` is supported for local development.
* ``AUDIT_RETENTION_DEFAULT_DAYS`` — platform-wide default.
* ``AUDIT_RETENTION_<CATEGORY>_DAYS`` — per-category override.
* ``AUDIT_RETENTION_DRY_RUN=true`` — skip DELETE + event insert;
  equivalent to ``--dry-run``.

Exit codes:

* 0 — sweep completed, one event row per tenant × policy with deletions.
* 1 — configuration error (no policies resolved, bad DSN, etc.).
* 2 — runtime error (DB unreachable, trigger not bypassed, etc.).

Designed for a Kubernetes CronJob: one process per scheduled run,
exits when the sweep finishes. Output is structured JSON to stderr —
Kubernetes' log collector (Loki / CloudWatch / Stackdriver) picks up
the fields as searchable labels. A Prometheus-pushgateway integration
for short-lived CronJob metrics is a documented follow-up (see README
§ "Follow-ups"); today the sweep summary is only visible in logs.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from .policies import describe, resolve_policies
from .retention import SweepSummary, run_sweep

logger = logging.getLogger("audit-retention-worker")


def _configure_logging() -> None:
    """JSON logs to stderr so Kubernetes' log collector picks them up
    structurally (keys surface as Loki/CloudWatch labels)."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)


class _JsonFormatter(logging.Formatter):
    """Minimal JSON formatter — no external dependency."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # structlog-style extras attached via `extra={}` end up as record
        # attributes; surface any that aren't standard LogRecord fields.
        std_keys = set(vars(logging.LogRecord("", 0, "", 0, "", None, None)).keys())
        for key, value in record.__dict__.items():
            if key not in std_keys and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="audit-retention-worker",
        description="Delete audit_log rows older than the configured retention window.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=_env_bool("AUDIT_RETENTION_DRY_RUN", default=False),
        help="Preview deletions without writing. Also set via AUDIT_RETENTION_DRY_RUN=true.",
    )
    return parser.parse_args(argv)


def _env_bool(name: str, *, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_dsn() -> str | None:
    """Prefer the worker-specific DSN, fall back to the shared one.

    Production deployments MUST set AUDIT_RETENTION_DATABASE_URL so the
    worker connects as the ``audit_retention`` role. DATABASE_URL is
    usually the service role which can't bypass the append-only trigger.
    """
    return os.getenv("AUDIT_RETENTION_DATABASE_URL") or os.getenv("DATABASE_URL")


async def _apply_worker_migrations(pool: Any) -> None:
    """Apply the worker's own migrations (003 + anything we add later).

    Kept separate from audit-service's migration runner so the two
    services can ship independently without colliding on version numbers
    in their respective bookkeeping tables.
    """
    here = Path(__file__).resolve().parent
    migrations_dir = here.parent / "migrations"
    if not migrations_dir.exists():
        # Container layout.
        migrations_dir = Path("/app/migrations")
    if not migrations_dir.exists():
        logger.warning("migrations.dir_missing", extra={"searched": str(migrations_dir)})
        return

    files = sorted(p for p in migrations_dir.glob("*.sql") if p.is_file())
    async with pool.acquire() as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_retention_schema_migrations ("
            "version VARCHAR(64) PRIMARY KEY, "
            "applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
        )
        already = {r["version"] for r in await conn.fetch("SELECT version FROM audit_retention_schema_migrations")}
        for path in files:
            version = path.stem
            if version in already:
                continue
            async with conn.transaction():
                await conn.execute(path.read_text())
            logger.info("migrations.applied", extra={"version": version})


def _summarise(summary: SweepSummary, *, dry_run: bool) -> dict[str, Any]:
    """Flatten the summary into a single log line for the CronJob exit."""
    by_tenant: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for run in summary.runs:
        if run.rows_deleted:
            by_tenant[run.tenant_id] = by_tenant.get(run.tenant_id, 0) + run.rows_deleted
            by_category[run.category] = by_category.get(run.category, 0) + run.rows_deleted
    duration_s = (summary.finished_at - summary.started_at).total_seconds()
    return {
        "dry_run": dry_run,
        "total_deleted": summary.total_deleted,
        "tenants_touched": summary.tenants_touched,
        "duration_seconds": round(duration_s, 3),
        "by_tenant": by_tenant,
        "by_category": by_category,
    }


async def _run(*, dry_run: bool) -> int:
    policies = resolve_policies(os.environ)
    if not policies:
        logger.error(
            "policies.none_configured",
            extra={
                "hint": "set AUDIT_RETENTION_DEFAULT_DAYS or at least one AUDIT_RETENTION_<CATEGORY>_DAYS env var",
            },
        )
        return 1

    logger.info("policies.resolved", extra={"text": describe(policies)})

    dsn = _resolve_dsn()
    if not dsn:
        logger.error(
            "dsn.missing",
            extra={
                "hint": "set AUDIT_RETENTION_DATABASE_URL (preferred) or DATABASE_URL",
            },
        )
        return 1

    try:
        import asyncpg  # type: ignore[import-untyped]
    except ImportError:  # pragma: no cover - asyncpg missing in dev shell
        logger.error("asyncpg.not_installed")
        return 2

    try:
        pool = await asyncpg.create_pool(dsn, min_size=1, max_size=2)
    except Exception as exc:  # noqa: BLE001 — surface the root cause then exit
        logger.error("dsn.connect_failed", extra={"error": str(exc)})
        return 2

    try:
        await _apply_worker_migrations(pool)
        summary = await run_sweep(pool, policies, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001 — catch-all so CronJob exits cleanly
        logger.exception("sweep.failed", extra={"error": str(exc)})
        return 2
    finally:
        await pool.close()

    logger.info("sweep.complete", extra=_summarise(summary, dry_run=dry_run))
    return 0


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    return asyncio.run(_run(dry_run=args.dry_run))


if __name__ == "__main__":  # pragma: no cover - module runner
    raise SystemExit(main())
