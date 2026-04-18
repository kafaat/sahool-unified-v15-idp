# syntax=docker/dockerfile:1.6
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL PgBouncer Image — extends edoburu/pgbouncer with postgresql-client
#
# WHY: entrypoint.sh needs psql for two critical steps that cannot be replaced
# by a TCP port check:
#   1. wait_for_postgres(): verifies the `pgbouncer` schema exists before
#      starting PgBouncer. Without this, PgBouncer races PostgreSQL init scripts
#      (PostGIS extension creation alone can take 60+ seconds) and fails
#      auth_query for every client.
#   2. generate_scram_hash(): fetches SCRAM-SHA-256 hashes from pg_shadow so
#      userlist.txt never holds plaintext passwords in production.
#
# Previously the entrypoint attempted `apk add postgresql-client` at runtime,
# but edoburu/pgbouncer runs as the unprivileged `postgres` user (uid 70),
# so apk fails silently and the script falls back to a 15-second sleep — which
# is too short for cold starts on slower machines and is the main cause of the
# "unhealthy pgbouncer" state that cascades into yield-prediction, lai, etc.
# ═══════════════════════════════════════════════════════════════════════════════

ARG PGBOUNCER_VERSION=v1.23.1-p3
FROM edoburu/pgbouncer:${PGBOUNCER_VERSION}

USER root
RUN apk add --no-cache postgresql-client \
    && rm -rf /var/cache/apk/*
USER postgres
