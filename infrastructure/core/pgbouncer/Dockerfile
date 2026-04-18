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
# Detect the base image's Alpine major.minor (e.g. 3.19) so mirror fallback
# writes a matching /etc/apk/repositories. `cut` keeps only the two leading
# version components; the final assertion fails the build if psql is missing.
RUN ALPINE_VER=$(cut -d. -f1,2 /etc/alpine-release) \
    && (apk add --no-cache postgresql-client \
        || (printf 'https://mirrors.aliyun.com/alpine/v%s/main\nhttps://mirrors.aliyun.com/alpine/v%s/community\n' "$ALPINE_VER" "$ALPINE_VER" > /etc/apk/repositories \
            && apk add --no-cache postgresql-client) \
        || (printf 'https://mirrors.tuna.tsinghua.edu.cn/alpine/v%s/main\nhttps://mirrors.tuna.tsinghua.edu.cn/alpine/v%s/community\n' "$ALPINE_VER" "$ALPINE_VER" > /etc/apk/repositories \
            && apk add --no-cache postgresql-client)) \
    && command -v psql >/dev/null 2>&1 \
    && rm -rf /var/cache/apk/*

# Drop back to the unprivileged user baked into the base image. Using the
# numeric UID (70 is the conventional Alpine `postgres` user) keeps this
# working even if upstream renames the account.
USER 70
