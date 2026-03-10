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

# Install postgresql-client for healthcheck.sh (SHOW POOLS queries)
# This enables deep health checks instead of simple port checks
# FIX: Added timeout to prevent blocking in environments without internet access
# DNS resolution for Alpine repos can hang for minutes without network connectivity
if ! command -v psql >/dev/null 2>&1; then
    if command -v timeout >/dev/null 2>&1; then
        timeout 15 apk add --no-cache postgresql-client >/dev/null 2>&1 || true
    else
        apk add --no-cache postgresql-client >/dev/null 2>&1 || true
    fi
fi

# Create runtime directory for userlist.txt
# The docker-compose mounts a tmpfs at /etc/pgbouncer/runtime (writable by any user)
# Previously used a named volume which caused "Permission denied" for non-root containers
mkdir -p /etc/pgbouncer/runtime 2>/dev/null || true
chmod 700 /etc/pgbouncer/runtime 2>/dev/null || true

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

# ═══════════════════════════════════════════════════════════════════════════════
# Wait for PostgreSQL to be ready using netcat (available in Alpine)
# ═══════════════════════════════════════════════════════════════════════════════
wait_for_postgres() {
    _max_attempts=30
    _attempt=1

    log_info "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."

    while [ "$_attempt" -le "$_max_attempts" ]; do
        # Try to connect to PostgreSQL port using nc (netcat)
        if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            log_info "PostgreSQL port is open!"
            # Give PostgreSQL a moment to finish initialization
            sleep 2
            return 0
        fi

        log_warn "Attempt $_attempt/$_max_attempts: PostgreSQL not ready, waiting..."
        sleep 2
        _attempt=$((_attempt + 1))
    done

    log_error "PostgreSQL did not become ready in time"
    return 1
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
        _hash=$(PGPASSWORD="$_pass" psql -h "$DB_HOST" -p "$DB_PORT" -U "$_user" -d "$DB_NAME" \
            -t -A -c "SELECT passwd FROM pgbouncer.get_auth('$_user')" 2>/dev/null || echo "")
        if echo "$_hash" | grep -q "^SCRAM-SHA-256\$"; then
            echo "$_hash"
            return 0
        fi
    fi
    # Fallback: return plaintext (PgBouncer accepts both formats)
    # SECURITY NOTE: plaintext is less secure but functional
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
    if echo "$_db_user_hash" | grep -q "^SCRAM-SHA-256\$"; then
        log_info "Using SCRAM-SHA-256 hashed password for auth_user"
    else
        log_warn "Using plaintext password for auth_user (SCRAM hash unavailable)"
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

    # Wait for PostgreSQL
    if ! wait_for_postgres; then
        log_warn "PostgreSQL not available, but continuing anyway..."
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

    # Execute pgbouncer with the config file
    # Use exec to replace the shell process with pgbouncer
    exec pgbouncer "$PGBOUNCER_CONFIG"
}

main "$@"
