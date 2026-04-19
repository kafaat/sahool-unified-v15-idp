#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# Run SAHOOL's pgTAP suite.
#
# Steps:
#   1. Apply the fixture schema (00_schema.sql) once.
#   2. Run every test file via pg_prove (TAP runner).
#
# Env vars (defaults target a local install):
#   PG_HOST   default 127.0.0.1
#   PG_PORT   default 5432
#   PG_USER   default postgres
#   PG_PASS   default <empty>
#   PG_DB     default postgres
#
# Exit non-zero if any assertion fails.
# ----------------------------------------------------------------------------
set -euo pipefail

PG_HOST="${PG_HOST:-127.0.0.1}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-postgres}"

: "${PG_PASS:=}"
export PGPASSWORD="$PG_PASS"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ applying RLS fixture schema"
psql -v ON_ERROR_STOP=1 \
     -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
     -f "$HERE/00_schema.sql" \
     >/dev/null

echo "→ running pgTAP tests"
# Only files prefixed with NN_ where NN != 00 are test files; 00_schema.sql
# is the fixture and must not be given to pg_prove.
shopt -s nullglob
TEST_FILES=( "$HERE"/[0-9][0-9]_*.sql )
RUN_FILES=()
for f in "${TEST_FILES[@]}"; do
    base="$(basename "$f")"
    [[ "$base" == 00_* ]] && continue
    RUN_FILES+=( "$f" )
done

if [[ ${#RUN_FILES[@]} -eq 0 ]]; then
    echo "no pgTAP test files found" >&2
    exit 1
fi

pg_prove --ext .sql \
    -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    "${RUN_FILES[@]}"

echo "✓ pgTAP suite passed"
