#!/usr/bin/env bash
# scripts/prisma-check.sh
#
# Verify every Prisma schema in apps/services/* is:
#   1. Formatted to Prisma's canonical style (`prisma format --check`)
#   2. Structurally valid (`prisma validate`)
#
# Designed to run in CI and locally before commit. Returns non-zero on
# the first failure so the pipeline halts immediately.
#
# Usage:
#   ./scripts/prisma-check.sh
#
# Environment variables:
#   DATABASE_URL          Required for `prisma validate`. Falls back
#                         to a dummy value since we only validate
#                         schema structure, not the connection.
#   DATABASE_URL_DIRECT   Required because every schema declares
#                         `directUrl = env("DATABASE_URL_DIRECT")`.
#                         Falls back to DATABASE_URL.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Provide fallback dummy URLs so `prisma validate` doesn't fail with
# P1012 "Environment variable not found" — we're only checking schema
# structure here, not connecting.
export DATABASE_URL="${DATABASE_URL:-postgresql://prisma-check@localhost:5432/prisma-check}"
export DATABASE_URL_DIRECT="${DATABASE_URL_DIRECT:-$DATABASE_URL}"

SERVICES_WITH_PRISMA=()
while IFS= read -r schema; do
  svc_dir="$(dirname "$(dirname "$schema")")"
  SERVICES_WITH_PRISMA+=("$svc_dir")
done < <(find apps/services -name schema.prisma -not -path "*/generated/*" -not -path "*/.prisma/*" 2>/dev/null | sort)

if [[ ${#SERVICES_WITH_PRISMA[@]} -eq 0 ]]; then
  echo "✗ No Prisma schemas found under apps/services/" >&2
  exit 1
fi

echo "→ Checking ${#SERVICES_WITH_PRISMA[@]} Prisma schema(s)"
echo

failures=0

for svc_dir in "${SERVICES_WITH_PRISMA[@]}"; do
  svc_name="$(basename "$svc_dir")"
  printf "  %-32s " "$svc_name"

  if ! out=$(cd "$svc_dir" && npx prisma format --check 2>&1); then
    echo "✗ format check failed"
    echo "$out" | sed 's/^/      /'
    failures=$((failures + 1))
    continue
  fi

  if ! out=$(cd "$svc_dir" && npx prisma validate 2>&1); then
    echo "✗ validate failed"
    echo "$out" | sed 's/^/      /'
    failures=$((failures + 1))
    continue
  fi

  echo "✓ format + validate"
done

echo
if [[ $failures -gt 0 ]]; then
  echo "✗ $failures schema(s) failed checks" >&2
  exit 1
fi

echo "✓ All ${#SERVICES_WITH_PRISMA[@]} Prisma schemas pass format + validate"
