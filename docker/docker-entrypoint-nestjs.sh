#!/bin/sh
set -e

# NestJS service entrypoint with Prisma migration support
# Handles P3005 (non-empty database) by creating empty _prisma_migrations table
# Handles P3009/P3018 (failed migrations) by marking them as rolled back and retrying
# Includes wait-for-db, self-healing sentinel check, and retry logic

MAX_MIGRATION_ATTEMPTS=3
DB_WAIT_TIMEOUT=${DB_WAIT_TIMEOUT:-30}
DB_WAIT_INTERVAL=2

# All SAHOOL Node.js services pin Prisma ~5.22.0 in their package.json, but
# only @prisma/client is copied into the production image — the `prisma` CLI
# is not — so a bare `npx prisma …` call here would fetch the current latest
# (7.x) from the registry, whose schema format is incompatible with ours and
# fails with P1012 ("url/directUrl no longer supported"). Pin the exact
# version (not just the major) so migrations always run with a CLI whose
# behavior matches the @prisma/client baked into the image.
PRISMA_CLI="npx prisma@5.22.0"

# ---------------------------------------------------------------------------
# wait_for_db: block until PostgreSQL accepts connections or timeout expires
# ---------------------------------------------------------------------------
wait_for_db() {
  echo "Waiting for database to be ready (timeout: ${DB_WAIT_TIMEOUT}s)..."
  elapsed=0
  while [ "$elapsed" -lt "$DB_WAIT_TIMEOUT" ]; do
    # Try pg_isready first (available in most postgres-client packages)
    if command -v pg_isready >/dev/null 2>&1; then
      if pg_isready -d "$DATABASE_URL" -q 2>/dev/null; then
        echo "Database is ready (pg_isready)."
        return 0
      fi
    else
      # Fallback: use node to attempt a raw TCP connection via prisma
      if printf 'SELECT 1;' | $PRISMA_CLI db execute --stdin >/dev/null 2>&1; then
        echo "Database is ready (prisma probe)."
        return 0
      fi
    fi
    sleep "$DB_WAIT_INTERVAL"
    elapsed=$((elapsed + DB_WAIT_INTERVAL))
  done
  echo "WARNING: Database readiness check timed out after ${DB_WAIT_TIMEOUT}s. Proceeding anyway..."
  return 0
}

# ---------------------------------------------------------------------------
# handle_p3005: create the empty migration-tracking table so Prisma can run
# ---------------------------------------------------------------------------
# P3005 means: the database has tables but no _prisma_migrations tracking
# table. This happens when Python services (Alembic/raw SQL) create tables
# before the first NestJS service runs. The OLD approach (baseline every
# migration as "applied") is wrong — it permanently prevents Prisma from
# running the SQL that actually creates this service's tables.
#
# The correct fix: create _prisma_migrations as an empty table and let
# `prisma migrate deploy` run normally to create this service's tables.
handle_p3005() {
  echo 'Database not empty (P3005). Creating empty migration tracking table...'
  printf 'CREATE TABLE IF NOT EXISTS "_prisma_migrations" (
    "id"                  VARCHAR(36)  NOT NULL,
    "checksum"            VARCHAR(64)  NOT NULL,
    "finished_at"         TIMESTAMPTZ  DEFAULT NULL,
    "migration_name"      VARCHAR(255) NOT NULL,
    "logs"                TEXT         DEFAULT NULL,
    "rolled_back_at"      TIMESTAMPTZ  DEFAULT NULL,
    "started_at"          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    "applied_steps_count" INTEGER      NOT NULL DEFAULT 0,
    PRIMARY KEY ("id")
  );' | $PRISMA_CLI db execute --stdin >>/tmp/prisma_migrate.log 2>&1 || true
  echo 'Migration tracking table created. Prisma will now apply all pending migrations.'
}

# ---------------------------------------------------------------------------
# verify_migration_state: self-heal falsely-baselined migrations
# ---------------------------------------------------------------------------
# When upgrading from the old buggy handle_p3005, _prisma_migrations may have
# rows for every migration but the actual tables were never created. If
# MIGRATION_SENTINEL_TABLE is set and that table is missing, clear the false
# records so that `prisma migrate deploy` re-applies all migrations.
verify_migration_state() {
  [ -z "$MIGRATION_SENTINEL_TABLE" ] && return 0

  # Try to SELECT from the sentinel table. If it fails, the table does not exist.
  if printf 'SELECT 1 FROM "%s" LIMIT 1;' "$MIGRATION_SENTINEL_TABLE" | \
       $PRISMA_CLI db execute --stdin >/dev/null 2>&1; then
    return 0  # table exists — migrations are correct
  fi

  # Sentinel table missing. Check if _prisma_migrations has (false) records.
  if printf 'SELECT 1 FROM "_prisma_migrations" LIMIT 1;' | \
       $PRISMA_CLI db execute --stdin >/dev/null 2>&1; then
    echo "WARNING: sentinel table '${MIGRATION_SENTINEL_TABLE}' is absent but _prisma_migrations has records."
    echo "Clearing false migration records so Prisma will re-apply all SQL..."
    printf 'DELETE FROM "_prisma_migrations";' | \
      $PRISMA_CLI db execute --stdin >>/tmp/prisma_migrate.log 2>&1 || true
    echo 'Migration records cleared.'
  fi
}

# ---------------------------------------------------------------------------
# handle_p3018: a migration SQL statement failed mid-apply.
# The migration is recorded as "started" but not finished. Mark it rolled-back
# so that Prisma will re-attempt it on the next deploy.
# ---------------------------------------------------------------------------
handle_p3018() {
  echo 'Mid-migration failure detected (P3018). Marking failed migration as rolled back...'
  # Prisma error includes: Migration name: <migration_name>
  failed_migration=$(grep -oP 'Migration name: \K\S+' /tmp/prisma_migrate.log | head -n1)
  if [ -z "$failed_migration" ]; then
    # Fallback: try backtick pattern used in other error messages
    failed_migration=$(sed -n "s/.*The \`\([^\`]*\)\` migration.*/\1/p" /tmp/prisma_migrate.log | head -n1)
  fi
  if [ -z "$failed_migration" ]; then
    echo 'ERROR: Could not extract failed migration name from P3018 error log.'
    cat /tmp/prisma_migrate.log
    return 1
  fi
  echo "Marking migration as rolled back: $failed_migration"
  if ! $PRISMA_CLI migrate resolve --rolled-back "$failed_migration" >>/tmp/prisma_migrate.log 2>&1; then
    echo 'ERROR: Failed to mark migration as rolled back.'
    cat /tmp/prisma_migrate.log
    return 1
  fi
  echo "Migration '$failed_migration' marked as rolled back (P3018 resolved)."
  return 0
}

# ---------------------------------------------------------------------------
# handle_p3009: mark the failed migration as rolled back
# ---------------------------------------------------------------------------
handle_p3009() {
  echo 'Failed migration detected (P3009). Attempting to resolve...'
  # Prisma outputs a line like:
  #   The `20250115120000_add_fields` migration started at ...
  failed_migration=$(sed -n "s/.*The \`\([^\`]*\)\` migration.*/\1/p" /tmp/prisma_migrate.log | head -n1)
  if [ -z "$failed_migration" ]; then
    echo 'ERROR: Could not extract failed migration name from P3009 error log.'
    cat /tmp/prisma_migrate.log
    return 1
  fi
  echo "Marking migration as rolled back: $failed_migration"
  if ! $PRISMA_CLI migrate resolve --rolled-back "$failed_migration" >>/tmp/prisma_migrate.log 2>&1; then
    echo 'ERROR: Failed to mark migration as rolled back.'
    cat /tmp/prisma_migrate.log
    return 1
  fi
  echo "Migration '$failed_migration' marked as rolled back."
  return 0
}

# ---------------------------------------------------------------------------
# run_migrations: deploy with retry loop and error handling
# ---------------------------------------------------------------------------
run_migrations() {
  attempt=1
  while [ "$attempt" -le "$MAX_MIGRATION_ATTEMPTS" ]; do
    echo "Migration attempt ${attempt}/${MAX_MIGRATION_ATTEMPTS}..."
    if $PRISMA_CLI migrate deploy >/tmp/prisma_migrate.log 2>&1; then
      cat /tmp/prisma_migrate.log
      echo 'Migrations applied successfully.'
      return 0
    fi

    # ---- P3005: non-empty database ----
    if grep -q 'P3005' /tmp/prisma_migrate.log; then
      handle_p3005
      attempt=$((attempt + 1))
      continue
    fi

    # ---- P3009: failed migration ----
    if grep -q 'P3009' /tmp/prisma_migrate.log; then
      if ! handle_p3009; then
        exit 1
      fi
      attempt=$((attempt + 1))
      continue
    fi

    # ---- P3018: mid-migration SQL failure ----
    if grep -q 'P3018' /tmp/prisma_migrate.log; then
      if ! handle_p3018; then
        exit 1
      fi
      attempt=$((attempt + 1))
      continue
    fi

    # ---- Unknown error ----
    echo "Migration failed on attempt ${attempt}/${MAX_MIGRATION_ATTEMPTS}:"
    cat /tmp/prisma_migrate.log
    if [ "$attempt" -ge "$MAX_MIGRATION_ATTEMPTS" ]; then
      echo 'Max migration attempts reached. Exiting.'
      exit 1
    fi
    echo "Retrying in 5 seconds..."
    sleep 5
    attempt=$((attempt + 1))
  done

  echo 'Max migration attempts reached. Exiting.'
  exit 1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if [ "$SKIP_DB_INIT" = "true" ]; then
  echo 'Skipping database migrations (SKIP_DB_INIT=true)'
else
  wait_for_db
  verify_migration_state
  run_migrations
fi

exec node dist/main.js
