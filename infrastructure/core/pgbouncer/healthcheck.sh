#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# PgBouncer Health Check Script (POSIX-compliant version)
# Comprehensive health verification for PgBouncer connection pooler
#
# Usage:
#   ./healthcheck.sh [--verbose] [--json]
#
# Exit codes:
#   0 - Healthy
#   1 - Unhealthy
#   2 - Warning (degraded but operational)
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Configuration
PGBOUNCER_HOST="${PGBOUNCER_HOST:-localhost}"
PGBOUNCER_PORT="${PGBOUNCER_PORT:-6432}"
POSTGRES_USER="${POSTGRES_USER:-sahool}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
WARN_THRESHOLD=80  # Warn at 80% pool utilization
CRIT_THRESHOLD=95  # Critical at 95% pool utilization

# Output format
VERBOSE=false
JSON_OUTPUT=false

# Parse arguments
while [ $# -gt 0 ]; do
  case $1 in
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--verbose] [--json]"
      echo "  --verbose  Show detailed output"
      echo "  --json     Output in JSON format"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Colors for output (disabled in JSON mode)
if [ "$JSON_OUTPUT" = "false" ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  NC='\033[0m' # No Color
else
  RED=''
  GREEN=''
  YELLOW=''
  NC=''
fi

# Function to log messages
log() {
  if [ "$VERBOSE" = "true" ] && [ "$JSON_OUTPUT" = "false" ]; then
    printf "%b\n" "$1"
  fi
}

# Function to execute query against PgBouncer admin console
# Uses psql if available (preferred), falls back to netcat TCP check
# NOTE: PgBouncer's virtual "pgbouncer" database only accepts admin_users/stats_users.
# We try the stats user first, then the main DB user, then fall back to TCP check.
execute_query() {
  _query=$1
  if command -v psql >/dev/null 2>&1; then
    # Try stats user first (can run SHOW POOLS, SHOW STATS, etc.)
    _stats_user="${ADMIN_USERS:-pgbouncer_admin}"
    _stats_pass="${PGBOUNCER_ADMIN_PASSWORD:-${POSTGRES_PASSWORD}}"
    PGPASSWORD="$_stats_pass" psql -h "$PGBOUNCER_HOST" -p "$PGBOUNCER_PORT" \
      -U "$_stats_user" -d pgbouncer -t -A -c "$_query" 2>/dev/null && return 0

    # Try main DB user connecting to actual database (not pgbouncer admin db)
    # This verifies end-to-end connectivity through PgBouncer to PostgreSQL
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$PGBOUNCER_HOST" -p "$PGBOUNCER_PORT" \
      -U "$POSTGRES_USER" -d "${DB_NAME:-sahool}" -t -A -c "SELECT 1" 2>/dev/null && return 0

    # psql available but queries failed - return failure
    return 1
  else
    # Fallback: basic TCP connectivity check
    # edoburu/pgbouncer Alpine image may not have psql
    nc -z "$PGBOUNCER_HOST" "$PGBOUNCER_PORT" 2>/dev/null
    return $?
  fi
}

# Check if psql is available for deep health checks
HAS_PSQL=false
if command -v psql >/dev/null 2>&1; then
  HAS_PSQL=true
fi

# Check 1: Basic connectivity
log "${YELLOW}Checking PgBouncer connectivity...${NC}"
if [ "$HAS_PSQL" = "true" ]; then
  # Deep check: try admin console or end-to-end query through PgBouncer
  if ! execute_query "SELECT 1" >/dev/null; then
    if [ "$JSON_OUTPUT" = "true" ]; then
      echo '{"status":"unhealthy","error":"Cannot connect to PgBouncer","checks":{"connectivity":false}}'
    else
      printf "%b\n" "${RED}✗ Cannot connect to PgBouncer${NC}"
    fi
    exit 1
  fi
else
  # Shallow check: verify TCP port is open + attempt auth via PgBouncer protocol
  if ! nc -z "$PGBOUNCER_HOST" "$PGBOUNCER_PORT" 2>/dev/null; then
    if [ "$JSON_OUTPUT" = "true" ]; then
      echo '{"status":"unhealthy","error":"PgBouncer port not reachable","checks":{"connectivity":false}}'
    else
      printf "%b\n" "${RED}✗ PgBouncer port not reachable${NC}"
    fi
    exit 1
  fi
  # Without psql, we can only verify port liveness - output warning
  if [ "$JSON_OUTPUT" = "true" ]; then
    echo '{"status":"healthy","warning":"psql not available - limited healthcheck","checks":{"connectivity":true,"pools":"skipped"}}'
  else
    echo "PgBouncer port reachable (install postgresql-client for deep healthchecks)"
  fi
  exit 0
fi
log "${GREEN}✓ PgBouncer is reachable${NC}"

# Check 2: Pool status
log "${YELLOW}Checking pool status...${NC}"
POOL_DATA=$(execute_query "SHOW POOLS;" 2>/dev/null || echo "")
if [ -z "$POOL_DATA" ]; then
  if [ "$JSON_OUTPUT" = "true" ]; then
    echo '{"status":"unhealthy","error":"Cannot retrieve pool status","checks":{"connectivity":true,"pools":false}}'
  else
    printf "%b\n" "${RED}✗ Cannot retrieve pool status${NC}"
  fi
  exit 1
fi
log "${GREEN}✓ Pool status retrieved${NC}"

# Parse pool data (database|user|cl_active|cl_waiting|sv_active|sv_idle|sv_used|sv_tested|sv_login|maxwait|pool_mode)
TOTAL_CL_ACTIVE=0
TOTAL_CL_WAITING=0
TOTAL_SV_ACTIVE=0
TOTAL_SV_IDLE=0
MAX_WAIT=0

# Use printf and read in a subshell to avoid here-string
echo "$POOL_DATA" | while IFS='|' read -r db user cl_active cl_waiting sv_active sv_idle sv_used sv_tested sv_login maxwait pool_mode; do
  # Skip header and pgbouncer database
  if [ "$db" = "pgbouncer" ] || [ "$db" = "database" ]; then
    continue
  fi

  # Output values to be collected (POSIX doesn't preserve variables from pipe subshell)
  echo "$cl_active $cl_waiting $sv_active $sv_idle $maxwait"
done > /tmp/pgbouncer_pool_data.$$

# Read and aggregate pool data
while read -r cl_active cl_waiting sv_active sv_idle maxwait; do
  TOTAL_CL_ACTIVE=$((TOTAL_CL_ACTIVE + cl_active))
  TOTAL_CL_WAITING=$((TOTAL_CL_WAITING + cl_waiting))
  TOTAL_SV_ACTIVE=$((TOTAL_SV_ACTIVE + sv_active))
  TOTAL_SV_IDLE=$((TOTAL_SV_IDLE + sv_idle))

  if [ "$maxwait" -gt "$MAX_WAIT" ] 2>/dev/null; then
    MAX_WAIT=$maxwait
  fi
done < /tmp/pgbouncer_pool_data.$$
rm -f /tmp/pgbouncer_pool_data.$$

# Calculate utilization (matching max_db_connections in pgbouncer.ini)
# UPDATED: Changed from 150 to 250 to match pgbouncer.ini configuration
MAX_CONNECTIONS=250
TOTAL_SV_CONNECTIONS=$((TOTAL_SV_ACTIVE + TOTAL_SV_IDLE))
UTILIZATION=0
if [ "$MAX_CONNECTIONS" -gt 0 ]; then
  UTILIZATION=$((TOTAL_SV_CONNECTIONS * 100 / MAX_CONNECTIONS))
fi

log "${YELLOW}Pool Statistics:${NC}"
log "  Client connections (active): $TOTAL_CL_ACTIVE"
log "  Client connections (waiting): $TOTAL_CL_WAITING"
log "  Server connections (active): $TOTAL_SV_ACTIVE"
log "  Server connections (idle): $TOTAL_SV_IDLE"
log "  Server connections (total): $TOTAL_SV_CONNECTIONS"
log "  Pool utilization: ${UTILIZATION}%"
log "  Max wait time: ${MAX_WAIT}s"

# Determine health status
STATUS="healthy"
EXIT_CODE=0

if [ "$UTILIZATION" -ge "$CRIT_THRESHOLD" ]; then
  STATUS="critical"
  EXIT_CODE=1
  log "${RED}✗ CRITICAL: Pool utilization at ${UTILIZATION}% (threshold: ${CRIT_THRESHOLD}%)${NC}"
elif [ "$UTILIZATION" -ge "$WARN_THRESHOLD" ]; then
  STATUS="warning"
  # FIX: Docker healthcheck treats any non-zero exit as unhealthy
  # Use exit code 0 for warning (degraded but still operational)
  EXIT_CODE=0
  log "${YELLOW}⚠ WARNING: Pool utilization at ${UTILIZATION}% (threshold: ${WARN_THRESHOLD}%)${NC}"
else
  log "${GREEN}✓ Pool utilization healthy (${UTILIZATION}%)${NC}"
fi

if [ "$TOTAL_CL_WAITING" -gt 0 ]; then
  # Preserve critical severity if already set; only escalate to warning from healthy
  if [ "$STATUS" != "critical" ]; then STATUS="warning"; fi
  # Docker healthcheck treats any non-zero exit as unhealthy; warning = exit 0
  if [ "$EXIT_CODE" -ne 1 ]; then EXIT_CODE=0; fi
  log "${YELLOW}⚠ WARNING: ${TOTAL_CL_WAITING} clients waiting for connections${NC}"
fi

if [ "$MAX_WAIT" -gt 10 ]; then
  if [ "$STATUS" != "critical" ]; then STATUS="warning"; fi
  if [ "$EXIT_CODE" -ne 1 ]; then EXIT_CODE=0; fi
  log "${YELLOW}⚠ WARNING: Maximum wait time is ${MAX_WAIT}s (>10s)${NC}"
fi

# Check 3: Configuration verification
log "${YELLOW}Checking configuration...${NC}"
CONFIG_DATA=$(execute_query "SHOW CONFIG;" 2>/dev/null || echo "")
if [ -n "$CONFIG_DATA" ]; then
  log "${GREEN}✓ Configuration accessible${NC}"

  if [ "$VERBOSE" = "true" ]; then
    # Extract key settings
    MAX_DB_CONN=$(echo "$CONFIG_DATA" | grep "max_db_connections" | cut -d'|' -f2 | tr -d ' ')
    DEFAULT_POOL=$(echo "$CONFIG_DATA" | grep "default_pool_size" | cut -d'|' -f2 | tr -d ' ')
    POOL_MODE=$(echo "$CONFIG_DATA" | grep "pool_mode" | cut -d'|' -f2 | tr -d ' ')

    log "  max_db_connections: $MAX_DB_CONN"
    log "  default_pool_size: $DEFAULT_POOL"
    log "  pool_mode: $POOL_MODE"
  fi
fi

# Output results
if [ "$JSON_OUTPUT" = "true" ]; then
  cat <<EOF
{
  "status": "$STATUS",
  "exit_code": $EXIT_CODE,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": {
    "connectivity": true,
    "pools": true,
    "configuration": true
  },
  "metrics": {
    "client_active": $TOTAL_CL_ACTIVE,
    "client_waiting": $TOTAL_CL_WAITING,
    "server_active": $TOTAL_SV_ACTIVE,
    "server_idle": $TOTAL_SV_IDLE,
    "server_total": $TOTAL_SV_CONNECTIONS,
    "utilization_percent": $UTILIZATION,
    "max_wait_seconds": $MAX_WAIT,
    "max_connections": $MAX_CONNECTIONS
  },
  "thresholds": {
    "warning": $WARN_THRESHOLD,
    "critical": $CRIT_THRESHOLD
  }
}
EOF
else
  echo ""
  echo "═══════════════════════════════════════"
  echo "PgBouncer Health Check Summary"
  echo "═══════════════════════════════════════"

  # Print status with color
  case $STATUS in
    healthy)
      printf "Status: %b\n" "${GREEN}✓ HEALTHY${NC}"
      ;;
    warning)
      printf "Status: %b\n" "${YELLOW}⚠ WARNING${NC}"
      ;;
    critical)
      printf "Status: %b\n" "${RED}✗ CRITICAL${NC}"
      ;;
  esac

  echo "Pool Utilization: ${UTILIZATION}% (${TOTAL_SV_CONNECTIONS}/${MAX_CONNECTIONS} connections)"
  echo "Active Clients: $TOTAL_CL_ACTIVE"
  echo "Waiting Clients: $TOTAL_CL_WAITING"
  echo "Max Wait Time: ${MAX_WAIT}s"
  echo "═══════════════════════════════════════"
fi

exit $EXIT_CODE
