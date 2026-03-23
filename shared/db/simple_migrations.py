"""
SAHOOL Simple Migration Runner
==============================

Lightweight migration helper for Python services that use inline CREATE TABLE
statements with asyncpg. Provides versioned, tracked migrations with optional
rollback support.

أداة ترحيل خفيفة للخدمات التي تستخدم asyncpg مع عبارات CREATE TABLE المضمنة.

Usage:
    from shared.db.simple_migrations import Migration, SimpleMigrationRunner

    migrations = [
        Migration(
            version=1,
            description="Create hydrology_analyses table",
            up="CREATE TABLE IF NOT EXISTS hydrology_analyses (...)",
            down="DROP TABLE IF EXISTS hydrology_analyses",
        ),
        Migration(
            version=2,
            description="Add tenant_id index",
            up="CREATE INDEX IF NOT EXISTS idx_tenant ON hydrology_analyses(tenant_id)",
            down="DROP INDEX IF EXISTS idx_tenant",
        ),
    ]

    runner = SimpleMigrationRunner(db_pool)
    await runner.run(migrations)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class Migration:
    """
    A single versioned migration.

    Attributes:
        version: Monotonically increasing integer. Must be unique.
        description: Human-readable summary of what the migration does.
        up: SQL statement(s) to apply the migration. May contain multiple
            statements separated by semicolons.
        down: Optional SQL to revert the migration. If None, rollback for
            this version is not supported.
    """

    version: int
    description: str
    up: str
    down: str | None = None


@dataclass
class MigrationResult:
    """Result of running a set of migrations."""

    applied: list[int] = field(default_factory=list)
    skipped: list[int] = field(default_factory=list)
    failed: int | None = None
    error: str | None = None
    dry_run: bool = False


# The tracking table name. Prefixed with underscore to distinguish it from
# application tables.
_TRACKING_TABLE = "_schema_migrations"

_CREATE_TRACKING_TABLE = f"""
CREATE TABLE IF NOT EXISTS {_TRACKING_TABLE} (
    version     INTEGER     PRIMARY KEY,
    description TEXT        NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER
)
"""


class SimpleMigrationRunner:
    """
    Runs a sequence of :class:`Migration` objects against an asyncpg pool,
    tracking which versions have already been applied.

    Features:
      - Idempotent: safe to call on every startup.
      - Ordered: migrations are always applied in version order.
      - Logged: each step is emitted via structlog.
      - Dry-run mode: preview which migrations would be applied.
      - Rollback: revert to a target version (requires ``down`` SQL).

    Parameters:
        db_pool: An ``asyncpg.Pool`` instance.
        service_name: Optional service identifier included in log messages.
    """

    def __init__(self, db_pool: asyncpg.Pool, *, service_name: str = "unknown") -> None:
        self._pool = db_pool
        self._service_name = service_name
        self._log = logger.bind(service=service_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(
        self,
        migrations: list[Migration],
        *,
        dry_run: bool = False,
    ) -> MigrationResult:
        """
        Apply all pending migrations in version order.

        Args:
            migrations: Full list of migrations for this service.
            dry_run: If True, log what *would* happen without executing.

        Returns:
            A :class:`MigrationResult` summarising what was applied.
        """
        result = MigrationResult(dry_run=dry_run)

        # Validate: no duplicate versions
        versions = [m.version for m in migrations]
        if len(versions) != len(set(versions)):
            raise ValueError("Duplicate migration versions detected")

        sorted_migrations = sorted(migrations, key=lambda m: m.version)

        async with self._pool.acquire() as conn:
            # Ensure tracking table exists (always real, even in dry-run)
            if not dry_run:
                await conn.execute(_CREATE_TRACKING_TABLE)

            applied_versions = await self._get_applied_versions(conn, dry_run=dry_run)

            for migration in sorted_migrations:
                if migration.version in applied_versions:
                    result.skipped.append(migration.version)
                    continue

                if dry_run:
                    self._log.info(
                        "migration_pending",
                        version=migration.version,
                        description=migration.description,
                        dry_run=True,
                    )
                    result.applied.append(migration.version)
                    continue

                # Apply inside a transaction so a failure rolls back cleanly.
                try:
                    t0 = time.monotonic()
                    async with conn.transaction():
                        await conn.execute(migration.up)
                        duration_ms = int((time.monotonic() - t0) * 1000)
                        await conn.execute(
                            f"""
                            INSERT INTO {_TRACKING_TABLE} (version, description, duration_ms)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (version) DO NOTHING
                            """,
                            migration.version,
                            migration.description,
                            duration_ms,
                        )
                    result.applied.append(migration.version)
                    self._log.info(
                        "migration_applied",
                        version=migration.version,
                        description=migration.description,
                        duration_ms=duration_ms,
                    )
                except Exception as exc:
                    result.failed = migration.version
                    result.error = str(exc)
                    self._log.error(
                        "migration_failed",
                        version=migration.version,
                        description=migration.description,
                        error=str(exc),
                    )
                    # Stop on first failure - do not apply subsequent migrations.
                    break

        if not dry_run:
            self._log.info(
                "migrations_complete",
                applied=len(result.applied),
                skipped=len(result.skipped),
                failed=result.failed,
            )
        return result

    async def rollback(
        self,
        migrations: list[Migration],
        *,
        target_version: int = 0,
        dry_run: bool = False,
    ) -> MigrationResult:
        """
        Revert applied migrations down to (but not including) *target_version*.

        Migrations are reverted in reverse version order. Only migrations that
        provide a ``down`` SQL string can be rolled back.

        Args:
            migrations: Full list of migrations for this service.
            target_version: Revert all versions above this number. Defaults to 0
                (revert everything).
            dry_run: If True, log what would happen without executing.

        Returns:
            A :class:`MigrationResult` summarising what was reverted.

        Raises:
            ValueError: If a migration that needs to be reverted has no ``down`` SQL.
        """
        result = MigrationResult(dry_run=dry_run)
        sorted_desc = sorted(migrations, key=lambda m: m.version, reverse=True)

        async with self._pool.acquire() as conn:
            applied_versions = await self._get_applied_versions(conn, dry_run=dry_run)

            for migration in sorted_desc:
                if migration.version <= target_version:
                    break
                if migration.version not in applied_versions:
                    result.skipped.append(migration.version)
                    continue
                if migration.down is None:
                    raise ValueError(
                        f"Migration v{migration.version} ({migration.description}) "
                        "has no rollback SQL"
                    )

                if dry_run:
                    self._log.info(
                        "rollback_pending",
                        version=migration.version,
                        description=migration.description,
                        dry_run=True,
                    )
                    result.applied.append(migration.version)
                    continue

                try:
                    t0 = time.monotonic()
                    async with conn.transaction():
                        await conn.execute(migration.down)
                        await conn.execute(
                            f"DELETE FROM {_TRACKING_TABLE} WHERE version = $1",
                            migration.version,
                        )
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    result.applied.append(migration.version)
                    self._log.info(
                        "rollback_applied",
                        version=migration.version,
                        description=migration.description,
                        duration_ms=duration_ms,
                    )
                except Exception as exc:
                    result.failed = migration.version
                    result.error = str(exc)
                    self._log.error(
                        "rollback_failed",
                        version=migration.version,
                        description=migration.description,
                        error=str(exc),
                    )
                    break

        return result

    async def get_current_version(self) -> int | None:
        """Return the highest applied migration version, or None if none applied."""
        async with self._pool.acquire() as conn:
            applied = await self._get_applied_versions(conn)
            return max(applied) if applied else None

    async def get_status(self, migrations: list[Migration]) -> dict:
        """
        Return a status dict showing applied, pending, and current version.
        Useful for health-check / readiness endpoints.
        """
        async with self._pool.acquire() as conn:
            applied = await self._get_applied_versions(conn)
        all_versions = {m.version for m in migrations}
        pending = sorted(all_versions - applied)
        return {
            "current_version": max(applied) if applied else None,
            "applied": sorted(applied),
            "pending": pending,
            "up_to_date": len(pending) == 0,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_applied_versions(
        self, conn: asyncpg.Connection, *, dry_run: bool = False
    ) -> set[int]:
        """Return set of already-applied version numbers."""
        try:
            rows = await conn.fetch(
                f"SELECT version FROM {_TRACKING_TABLE} ORDER BY version"
            )
            return {row["version"] for row in rows}
        except Exception:
            # Table may not exist yet (first run or dry_run before real run).
            if dry_run:
                return set()
            raise
