#!/bin/sh
set -e

# NestJS service entrypoint with Prisma migration support
# Handles P3005 (non-empty database) by baselining existing migrations

if [ "$SKIP_DB_INIT" = "true" ]; then
  echo 'Skipping database migrations (SKIP_DB_INIT=true)'
else
  echo 'Running Prisma migrations...'
  if ! npx prisma migrate deploy >/tmp/prisma_err.log 2>&1; then
    if grep -q 'P3005' /tmp/prisma_err.log; then
      echo 'Database not empty (P3005). Baselining existing migrations...'
      for dir in prisma/migrations/*/; do
        [ -d "$dir" ] || continue
        migration_name=$(basename "$dir")
        echo "Resolving migration: $migration_name"
        npx prisma migrate resolve --applied "$migration_name" 2>&1 || true
      done
      echo 'Baseline complete. Re-running migrate deploy...'
      npx prisma migrate deploy
    else
      echo 'Migration error (non-P3005):'
      cat /tmp/prisma_err.log
      exit 1
    fi
  else
    cat /tmp/prisma_err.log
  fi
fi

exec node dist/main.js
