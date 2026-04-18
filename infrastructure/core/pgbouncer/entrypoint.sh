#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# PgBouncer Entrypoint Script for SAHOOL Platform
# Generates userlist.txt from environment variables before starting PgBouncer
#
# This script:
# 1. Waits for PostgreSQL to be ready (using netcat/nc)
# 2. Generates userlist.txt with auth_user credentials
# 3. Starts PgBouncer with the generated configuration
#
# Compatible with Alpine-based images (edoburu/pgbouncer)
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Create runtime directory for userlist.txt and pidfile
# The docker-compose mounts a tmpfs at /etc/pgbouncer/runtime (writable by any user)
# Previously used a named volume which caused "Permission denied" for non-root containers
mkdir -p /etc/pgbouncer/runtime 2>/dev/null || true
chmod 750 /etc/pgbouncer/runtime 2>/dev/null || true

# FIX: Create default PgBouncer directories as fallback
# The edoburu/pgbouncer image normally creates these in its own entrypoint,
# but since we override it, these directories may not exist
mkdir -p /var/run/pgbouncer 2>/dev/null || true
mkdir -p /var/log/pgbouncer 2>/dev/null || true
chmod 750 /var/run/pgbouncer 2>/dev/null || true
chmod 750 /var/log/pgbouncer 2>/dev/null || true

# Configuration from environment
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-sahool}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-sahool}"
PGBOUNCER_CONFIG="${PGBOUNCER_CONFIG:-/etc/pgbouncer/pgbouncer.ini}"
USERLIST_FILE="${USERLIST_FILE:-/etc/pgbouncer/runtime/userlist.txt}"

# Logging functions
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warn() {
    echo "[WARN] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# Install postgresql-client for schema readiness check in wait_for_postgres().
# Without psql, we fall back to a simple TCP port check + delay, which is less
# reliable but avoids hard network dependencies that break offline/locked-down
# environments. Ideally, psql should be baked into a custom PgBouncer image.
HAVE_PSQL=false
if command -v psql >/dev/null 2>&1; then
    HAVE_PSQL=true
    log_info "psql already available: $(command -v psql)"
else
    _psql_installed=false
    for _psql_wait in 2 4; do
        log_info "Installing postgresql-client (attempt with ${_psql_wait}s timeout)..."
        if command -v timeout >/dev/null 2>&1; then
            timeout "$_psql_wait" apk add --no-cache postgresql-client >/dev/null 2>&1 && _psql_installed=true && break
        else
            apk add --no-cache postgresql-client >/dev/null 2>&1 && _psql_installed=true && break
        fi
        sleep 1
    done
    if [ "$_psql_installed" = true ]; then
        HAVE_PSQL=true
        log_info "psql installed: $(command -v psql)"
    else
        log_warn "Could not install postgresql-client. Will use TCP-only readiness check"
        log_warn "with extended delay as fallback. Consider baking psql into the image."
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Wait for PostgreSQL to be FULLY ready (init scripts completed)
# FIX (2026-03-13): Changed from simple port check to actual query verification.
# The port opens BEFORE init scripts finish, causing PgBouncer to fail auth_query
# because the pgbouncer schema (02-pgbouncer-user.sql) hasn't been created yet.
# ═══════════════════════════════════════════════════════════════════════════════
wait_for_postgres() {
    _max_attempts=60
    _attempt=1

    log_info "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."

    # Phase 1: Wait for TCP port to be open
    while [ "$_attempt" -le "$_max_attempts" ]; do
        if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            log_info "PostgreSQL port is open!"
            break
        fi
        log_warn "Attempt $_attempt/$_max_attempts: PostgreSQL port not ready, waiting..."
        sleep 2
        _attempt=$((_attempt + 1))
    done

    if [ "$_attempt" -gt "$_max_attempts" ]; then
        log_error "PostgreSQL port did not open in time"
        return 1
    fi

    # Phase 2: Wait for init scripts to complete by checking for pgbouncer schema
    # The pgbouncer schema is created by 02-pgbouncer-user.sql (one of the last init scripts)
    _attempt=1
    _max_init_attempts=30

    if [ "$HAVE_PSQL" = true ]; then
        log_info "Waiting for PostgreSQL init scripts to complete (checking pgbouncer schema)..."

        while [ "$_attempt" -le "$_max_init_attempts" ]; do
            _schema_exists=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
                -t -A -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'pgbouncer')" 2>/dev/null || echo "f")
            if [ "$_schema_exists" = "t" ]; then
                log_info "PostgreSQL init scripts completed (pgbouncer schema exists)"
                return 0
            fi

            log_info "Init scripts still running ($_attempt/$_max_init_attempts), waiting..."
            sleep 3
            _attempt=$((_attempt + 1))
        done

        # Self-heal: init scripts in /docker-entrypoint-initdb.d/ only run on
        # a fresh data directory, so pre-existing postgres volumes (common when
        # switching compose project names or upgrading) never gain the
        # pgbouncer schema. Rather than requiring operators to `docker compose
        # down -v` and lose their data, apply the minimal schema ourselves.
        # This is idempotent (CREATE SCHEMA IF NOT EXISTS + CREATE OR REPLACE).
        log_warn "pgbouncer schema not found after waiting — applying bootstrap"
        bootstrap_pgbouncer_schema
        return $?
    else
        # Fallback: psql not available, use a fixed delay after port is open
        # to allow init scripts time to complete
        log_warn "psql not available — using fixed 15s delay for init script completion"
        sleep 15
        log_info "Proceeding without schema verification (psql unavailable)"
        return 0
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Bootstrap pgbouncer schema + get_auth() function when init scripts never ran.
# Mirrors infrastructure/core/postgres/init/02-pgbouncer-user.sql but kept
# minimal: only the pieces PgBouncer strictly needs at runtime for auth_query.
# Runs as the main DB user (typically a superuser in the postgres docker image)
# so SECURITY DEFINER on get_auth() lets us read pg_shadow without granting
# pg_read_all_auth to every caller.
# ═══════════════════════════════════════════════════════════════════════════════
bootstrap_pgbouncer_schema() {
    log_info "Bootstrapping pgbouncer schema in ${DB_NAME}..."
    # Wrap psql in `if !` so set -e (active script-wide) does not abort the
    # entrypoint before we can log a controlled error and propagate the
    # failure to the caller.
    if ! PGPASSWORD="$DB_PASSWORD" psql -v ON_ERROR_STOP=1 \
        -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'EOSQL' 2>&1
CREATE SCHEMA IF NOT EXISTS pgbouncer;

CREATE OR REPLACE FUNCTION pgbouncer.get_auth(p_usename TEXT)
RETURNS TABLE(usename NAME, passwd TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT u.usename::NAME, u.passwd::TEXT
    FROM pg_catalog.pg_shadow u
    WHERE u.usename = p_usename;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

ALTER FUNCTION pgbouncer.get_auth(TEXT) SET search_path = pg_catalog;
EOSQL
    then
        log_error "pgbouncer schema bootstrap failed (CREATE phase)"
        return 1
    fi

    log_info "Bootstrap applied — locking down privileges for auth_user ${DB_USER}"
    # SECURITY: Lock down the SECURITY DEFINER function before granting it back to
    # the auth_user. PostgreSQL's default for new functions is EXECUTE TO PUBLIC,
    # which would let any DB role read pg_shadow password hashes via this helper.
    # REVOKE removes that default, then we re-GRANT only to CURRENT_USER (which
    # is the auth_user since psql connected as DB_USER above).
    if ! PGPASSWORD="$DB_PASSWORD" psql -v ON_ERROR_STOP=1 \
        -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'EOSQL' 2>&1
REVOKE ALL ON FUNCTION pgbouncer.get_auth(TEXT) FROM PUBLIC;
REVOKE ALL ON SCHEMA pgbouncer FROM PUBLIC;
GRANT USAGE ON SCHEMA pgbouncer TO CURRENT_USER;
GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO CURRENT_USER;
EOSQL
    then
        log_error "pgbouncer schema bootstrap failed (GRANT phase)"
        return 1
    fi

    log_info "pgbouncer schema bootstrap complete"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Generate SCRAM-SHA-256 hash for PgBouncer userlist.txt
# PgBouncer 1.21+ supports SCRAM hashes in auth_file
# ═══════════════════════════════════════════════════════════════════════════════
generate_scram_hash() {
    _user=$1
    _pass=$2
    # Try to get SCRAM hash from PostgreSQL if psql is available and PG is reachable
    # Uses pgbouncer.get_auth() SECURITY DEFINER function (defined in 02-pgbouncer-user.sql)
    # which wraps pg_shadow access, avoiding the need for superuser privileges
    if command -v psql >/dev/null 2>&1 && nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
        # Sanitize username to prevent SQL injection (alphanumeric + underscore only)
        _safe_user=$(printf '%s' "$_user" | tr -dc 'a-zA-Z0-9_')
        _hash=$(PGPASSWORD="$_pass" psql -h "$DB_HOST" -p "$DB_PORT" -U "$_user" -d "$DB_NAME" \
            -t -A -c "SELECT passwd FROM pgbouncer.get_auth('${_safe_user}')" 2>/dev/null || echo "")
        if echo "$_hash" | grep -q '^SCRAM-SHA-256\$'; then
            echo "$_hash"
            return 0
        fi
    fi
    # Fallback: use plaintext password (PgBouncer computes SCRAM proof on-the-fly)
    # FIX (2026-04-12): md5 hashes are INCOMPATIBLE with auth_type=scram-sha-256.
    # PgBouncer cannot derive SCRAM proofs from a one-way md5 hash, so auth_user
    # authentication to PostgreSQL fails, breaking auth_query for ALL clients.
    # Plaintext in auth_file is safe here: the file is chmod 600 on a tmpfs mount
    # that is never persisted, and PgBouncer hashes it in memory immediately.
    log_warn "SCRAM hash unavailable for $_user — using plaintext (PgBouncer will hash in memory)"
    echo "$_pass"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Generate userlist.txt with SCRAM-SHA-256 hashes when possible
# PgBouncer uses this to authenticate as auth_user to PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
generate_userlist() {
    log_info "Generating userlist.txt for auth_user: ${DB_USER}"

    if [ -z "$DB_PASSWORD" ]; then
        log_error "DB_PASSWORD is not set. Cannot generate userlist.txt"
        return 1
    fi

    # Create userlist.txt directory if it doesn't exist
    mkdir -p "$(dirname "$USERLIST_FILE")"

    # Generate SCRAM hash for the main DB user
    _db_user_hash=$(generate_scram_hash "$DB_USER" "$DB_PASSWORD")
    _admin_pass="${PGBOUNCER_ADMIN_PASSWORD:-${DB_PASSWORD}}"
    _stats_pass="${PGBOUNCER_STATS_PASSWORD:-${DB_PASSWORD}}"

    # Determine hash type for logging
    if echo "$_db_user_hash" | grep -q '^SCRAM-SHA-256\$'; then
        log_info "Using SCRAM-SHA-256 hashed password for auth_user"
    else
        log_warn "Using plaintext password for auth_user (PgBouncer will compute SCRAM in memory)"
    fi

    # Write userlist.txt with SCRAM hashes or plaintext fallback
    # Format: "username" "SCRAM-SHA-256$iterations:salt$StoredKey:ServerKey"
    cat > "$USERLIST_FILE" << EOF
;; PgBouncer User List - Auto-generated by entrypoint.sh
;; Generated: $(date '+%Y-%m-%d %H:%M:%S')
;; DO NOT EDIT MANUALLY - This file is regenerated on container start
;;
;; Format: "username" "SCRAM-SHA-256$..." or "username" "plaintext"
;; PgBouncer uses auth_user credentials to run auth_query against PostgreSQL

"${DB_USER}" "${_db_user_hash}"

;; Admin/stats users for PgBouncer console (separate credentials recommended)
"pgbouncer_admin" "${_admin_pass}"
"pgbouncer_stats" "${_stats_pass}"
EOF

    # Set strict permissions (readable only by pgbouncer process)
    chmod 600 "$USERLIST_FILE" 2>/dev/null || true

    log_info "userlist.txt generated successfully at ${USERLIST_FILE}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Verify PgBouncer configuration
# ═══════════════════════════════════════════════════════════════════════════════
verify_config() {
    log_info "Verifying PgBouncer configuration..."

    # Ensure the config file exists
    if [ ! -f "$PGBOUNCER_CONFIG" ]; then
        log_error "PgBouncer config file not found: $PGBOUNCER_CONFIG"
        return 1
    fi

    # Ensure userlist file exists
    if [ ! -f "$USERLIST_FILE" ]; then
        log_error "Userlist file not found: $USERLIST_FILE"
        return 1
    fi

    log_info "PgBouncer configuration verified"
    log_info "  Config: ${PGBOUNCER_CONFIG}"
    log_info "  Userlist: ${USERLIST_FILE}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main execution
# ═══════════════════════════════════════════════════════════════════════════════
main() {
    log_info "═══════════════════════════════════════════════════════════════════"
    log_info "SAHOOL PgBouncer Entrypoint v2.0"
    log_info "═══════════════════════════════════════════════════════════════════"
    log_info "DB_HOST: ${DB_HOST}"
    log_info "DB_PORT: ${DB_PORT}"
    log_info "DB_USER: ${DB_USER}"
    log_info "DB_NAME: ${DB_NAME}"
    log_info "═══════════════════════════════════════════════════════════════════"

    # Wait for PostgreSQL (exit if not available, auth_query requires pgbouncer schema)
    if ! wait_for_postgres; then
        log_error "PostgreSQL not available or init scripts incomplete. Cannot start PgBouncer without pgbouncer schema."
        exit 1
    fi

    # Generate userlist.txt
    if ! generate_userlist; then
        log_error "Failed to generate userlist.txt"
        exit 1
    fi

    # Verify config
    if ! verify_config; then
        log_error "Configuration verification failed"
        exit 1
    fi

    log_info "Starting PgBouncer..."
    log_info "═══════════════════════════════════════════════════════════════════"

    # Apply environment variable overrides to pgbouncer.ini
    # These env vars from docker-compose.yml were previously ignored (dead config)
    _runtime_ini="/etc/pgbouncer/runtime/pgbouncer.ini"
    cp "$PGBOUNCER_CONFIG" "$_runtime_ini"
    # CRITICAL: auth_user must match the PostgreSQL user we generated hashes for
    # in userlist.txt. pgbouncer.ini ships with a hardcoded default ('sahool');
    # override it so changing POSTGRES_USER in .env does not silently break auth.
    sed -i "s/^auth_user.*/auth_user = $DB_USER/" "$_runtime_ini"
    [ -n "${MAX_DB_CONNECTIONS:-}" ] && sed -i "s/^max_db_connections.*/max_db_connections = $MAX_DB_CONNECTIONS/" "$_runtime_ini"
    [ -n "${DEFAULT_POOL_SIZE:-}" ] && sed -i "s/^default_pool_size.*/default_pool_size = $DEFAULT_POOL_SIZE/" "$_runtime_ini"
    [ -n "${MIN_POOL_SIZE:-}" ] && sed -i "s/^min_pool_size.*/min_pool_size = $MIN_POOL_SIZE/" "$_runtime_ini"
    [ -n "${RESERVE_POOL_SIZE:-}" ] && sed -i "s/^reserve_pool_size.*/reserve_pool_size = $RESERVE_POOL_SIZE/" "$_runtime_ini"
    [ -n "${MAX_CLIENT_CONN:-}" ] && sed -i "s/^max_client_conn.*/max_client_conn = $MAX_CLIENT_CONN/" "$_runtime_ini"
    [ -n "${QUERY_TIMEOUT:-}" ] && sed -i "s/^query_timeout.*/query_timeout = $QUERY_TIMEOUT/" "$_runtime_ini"
    [ -n "${QUERY_WAIT_TIMEOUT:-}" ] && sed -i "s/^query_wait_timeout.*/query_wait_timeout = $QUERY_WAIT_TIMEOUT/" "$_runtime_ini"
    [ -n "${SERVER_IDLE_TIMEOUT:-}" ] && sed -i "s/^server_idle_timeout.*/server_idle_timeout = $SERVER_IDLE_TIMEOUT/" "$_runtime_ini"
    [ -n "${CLIENT_IDLE_TIMEOUT:-}" ] && sed -i "s/^client_idle_timeout.*/client_idle_timeout = $CLIENT_IDLE_TIMEOUT/" "$_runtime_ini"
    [ -n "${POOL_MODE:-}" ] && sed -i "s/^pool_mode.*/pool_mode = $POOL_MODE/" "$_runtime_ini"
    [ -n "${ADMIN_USERS:-}" ] && sed -i "s/^admin_users.*/admin_users = $ADMIN_USERS/" "$_runtime_ini"
    [ -n "${STATS_USERS:-}" ] && sed -i "s/^stats_users.*/stats_users = $STATS_USERS/" "$_runtime_ini"
    log_info "Applied environment variable overrides to runtime config"

    # Execute pgbouncer with runtime config (includes env var overrides)
    exec pgbouncer "$_runtime_ini"
}

main "$@"
