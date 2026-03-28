#!/bin/sh
set -e

# NestJS service entrypoint with Prisma migration support
# Handles P3005 (non-empty database) by baselining existing migrations
# Handles P3009 (failed migrations) by marking them as rolled back and retrying
# Includes wait-for-db and retry logic for environments where postgres starts slowly

MAX_MIGRATION_ATTEMPTS=3
DB_WAIT_TIMEOUT=${DB_WAIT_TIMEOUT:-30}
DB_WAIT_INTERVAL=2

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
      if npx prisma db execute --stdin <<< "SELECT 1;" >/dev/null 2>&1; then
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
    npx prisma migrate resolve --applied "$migration_name" >>/tmp/prisma_migrate.log 2>&1 || true
  done
  echo 'Baseline complete.'
}

# ---------------------------------------------------------------------------
# handle_p3009: mark the failed migration as rolled back
# ---------------------------------------------------------------------------
handle_p3009() {
  echo 'Failed migration detected (P3009). Attempting to resolve...'
  # Prisma outputs a line like:
  #   The `20250115120000_add_fields` migration started at ...
  failed_migration=$(grep -oP 'The `\K[^`]+' /tmp/prisma_migrate.log | head -n1)
  if [ -z "$failed_migration" ]; then
    echo 'ERROR: Could not extract failed migration name from P3009 error log.'
    cat /tmp/prisma_migrate.log
    return 1
  fi
  echo "Marking migration as rolled back: $failed_migration"
  if ! npx prisma migrate resolve --rolled-back "$failed_migration" >>/tmp/prisma_migrate.log 2>&1; then
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
    if npx prisma migrate deploy >/tmp/prisma_migrate.log 2>&1; then
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
  run_migrations
fi

exec node dist/main.js
