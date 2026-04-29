#!/bin/sh
set -e

# NestJS service entrypoint with Prisma migration support
# Handles P3005 (non-empty database) by baselining existing migrations
# Handles P3009 (failed migrations) by marking them as rolled back and retrying
# Includes wait-for-db and retry logic for environments where postgres starts slowly.
# Default DB wait is 60s; compose can override it to 120s for bulk startup.

MAX_MIGRATION_ATTEMPTS=3
DB_WAIT_TIMEOUT=${DB_WAIT_TIMEOUT:-60}
DB_WAIT_INTERVAL=2
ORIGINAL_DATABASE_URL=${DATABASE_URL:-}
# POSIX ${var+x}: expands to "x" only when the variable was originally set.
DATABASE_URL_SET_MARKER=${DATABASE_URL+x}

# All SAHOOL Node.js services pin Prisma ~5.22.0 in their package.json, but
# only @prisma/client is copied into the production image — the `prisma` CLI
# is not — so a bare `npx prisma …` call here would fetch the current latest
# (7.x) from the registry, whose schema format is incompatible with ours and
# fails with P1012 ("url/directUrl no longer supported"). Pin the exact
# version (not just the major) so migrations always run with a CLI whose
# behavior matches the @prisma/client baked into the image.
PRISMA_CLI="npx prisma@5.22.0"

# ---------------------------------------------------------------------------
# Migrations must use a direct Postgres connection (postgres:5432), NOT the
# PgBouncer pool. PgBouncer in transaction mode reassigns server connections
# between statements, which breaks Prisma's session-level advisory lock and
# causes concurrent services to corrupt _prisma_migrations with stuck rows.
# DATABASE_URL_DIRECT is set in docker-compose.yml for every NestJS service.
# Keep the application DATABASE_URL intact for runtime; switch to the direct
# URL only while running Prisma migrations below.
# ---------------------------------------------------------------------------
use_migration_database_url() {
  if [ -n "$DATABASE_URL_DIRECT" ]; then
    export DATABASE_URL="$DATABASE_URL_DIRECT"
  fi
  if [ -z "${DATABASE_URL:-}" ]; then
    echo 'ERROR: No database URL configured for Prisma migrations. Set DATABASE_URL_DIRECT (recommended to bypass PgBouncer) or DATABASE_URL.'
    exit 1
  fi
}

restore_application_database_url() {
  if [ -n "$DATABASE_URL_SET_MARKER" ]; then
    export DATABASE_URL="$ORIGINAL_DATABASE_URL"
  else
    unset DATABASE_URL
  fi
}

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
# handle_p3005: baseline all existing migrations as applied
# ---------------------------------------------------------------------------
handle_p3005() {
  echo 'Database not empty (P3005). Baselining existing migrations...'
  for dir in prisma/migrations/*/; do
    [ -d "$dir" ] || continue
    migration_name=$(basename "$dir")
    echo "Resolving migration as applied: $migration_name"
    $PRISMA_CLI migrate resolve --applied "$migration_name" >>/tmp/prisma_migrate.log 2>&1 || true
  done
  echo 'Baseline complete.'
}

# ---------------------------------------------------------------------------
# handle_p3018: a migration SQL statement failed mid-apply.
# The migration is recorded as "started" but not finished. Mark it rolled-back
# so that Prisma will re-attempt it on the next deploy.
# ---------------------------------------------------------------------------
handle_p3018() {
  echo 'Mid-migration failure detected (P3018). Attempting to resolve...'
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
  # If the underlying SQL error is "already exists" the migration's work is
  # already done (objects exist from a prior run). Mark it as applied so
  # Prisma stops retrying it. Otherwise mark rolled-back so it retries.
  if grep -qi 'already exists\|duplicate_object\|duplicate_table\|duplicate_column\|DuplicateObject' /tmp/prisma_migrate.log; then
    echo "Marking migration as applied (objects already exist): $failed_migration"
    if ! $PRISMA_CLI migrate resolve --applied "$failed_migration" >>/tmp/prisma_migrate.log 2>&1; then
      echo "WARNING: Could not mark '$failed_migration' as applied; falling back to rolled-back."
      $PRISMA_CLI migrate resolve --rolled-back "$failed_migration" >>/tmp/prisma_migrate.log 2>&1 || true
    else
      echo "Migration '$failed_migration' marked as applied (P3018/already-exists resolved)."
      return 0
    fi
  else
    echo "Marking migration as rolled back: $failed_migration"
    if ! $PRISMA_CLI migrate resolve --rolled-back "$failed_migration" >>/tmp/prisma_migrate.log 2>&1; then
      echo 'ERROR: Failed to mark migration as rolled back.'
      cat /tmp/prisma_migrate.log
      return 1
    fi
    echo "Migration '$failed_migration' marked as rolled back (P3018 resolved)."
  fi
  return 0
}

# ---------------------------------------------------------------------------
# handle_p3009: mark ALL failed migrations as rolled back in one pass
# ---------------------------------------------------------------------------
handle_p3009() {
  echo 'Failed migration detected (P3009). Attempting to resolve all failed migrations...'
  # Prisma outputs a line like:
  #   The `20250115120000_add_fields` migration started at ...
  # Collect every failed migration name from the log (may be more than one).
  failed_migrations=$(sed -n "s/.*The \`\([^\`]*\)\` migration.*/\1/p" /tmp/prisma_migrate.log)
  if [ -z "$failed_migrations" ]; then
    echo 'ERROR: Could not extract failed migration names from P3009 error log.'
    cat /tmp/prisma_migrate.log
    return 1
  fi
  resolved=0
  for failed_migration in $failed_migrations; do
    echo "Marking migration as rolled back: $failed_migration"
    if $PRISMA_CLI migrate resolve --rolled-back "$failed_migration" >>/tmp/prisma_migrate.log 2>&1; then
      echo "Migration '$failed_migration' marked as rolled back."
      resolved=$((resolved + 1))
    else
      echo "WARNING: Could not mark '$failed_migration' as rolled back (may already be resolved)."
    fi
  done
  [ "$resolved" -gt 0 ] && return 0 || return 1
}

# ---------------------------------------------------------------------------
# run_migrations: deploy with retry loop and error handling
# P3009 resolutions use a separate counter and do NOT consume the main
# MAX_MIGRATION_ATTEMPTS budget — there can be many phantom failed migrations
# in the DB that need clearing one-by-one before deploy can proceed.
# ---------------------------------------------------------------------------
run_migrations() {
  attempt=1
  p3009_resolutions=0
  p3018_resolutions=0
  MAX_P3009_RESOLUTIONS=30
  MAX_P3018_RESOLUTIONS=30

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

    # ---- P3009: failed migration(s) — resolve without burning the main budget ----
    if grep -q 'P3009' /tmp/prisma_migrate.log; then
      if [ "$p3009_resolutions" -ge "$MAX_P3009_RESOLUTIONS" ]; then
        echo "ERROR: Exceeded max P3009 resolutions (${MAX_P3009_RESOLUTIONS}). Giving up."
        cat /tmp/prisma_migrate.log
        exit 1
      fi
      if ! handle_p3009; then
        exit 1
      fi
      p3009_resolutions=$((p3009_resolutions + 1))
      # Do NOT increment attempt — P3009 cleanup is not a failed deploy attempt
      continue
    fi

    # ---- P3018: mid-migration SQL failure — resolve without burning the main budget ----
    if grep -q 'P3018' /tmp/prisma_migrate.log; then
      if [ "$p3018_resolutions" -ge "$MAX_P3018_RESOLUTIONS" ]; then
        echo "ERROR: Exceeded max P3018 resolutions (${MAX_P3018_RESOLUTIONS}). Giving up."
        cat /tmp/prisma_migrate.log
        exit 1
      fi
      if ! handle_p3018; then
        exit 1
      fi
      p3018_resolutions=$((p3018_resolutions + 1))
      # Do NOT increment attempt — P3018 recovery is not a failed deploy attempt
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
  use_migration_database_url
  wait_for_db
  run_migrations
fi

restore_application_database_url
exec node dist/main.js
