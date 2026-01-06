#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# PgBouncer Health Check Script
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

set -euo pipefail

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
while [[ $# -gt 0 ]]; do
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
if [[ "$JSON_OUTPUT" == "false" ]]; then
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
  if [[ "$VERBOSE" == "true" ]] && [[ "$JSON_OUTPUT" == "false" ]]; then
    echo -e "$1"
  fi
}

# Function to execute psql command
execute_query() {
  local query=$1
  PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$PGBOUNCER_HOST" -p "$PGBOUNCER_PORT" \
    -U "$POSTGRES_USER" -d pgbouncer -t -A -c "$query" 2>/dev/null
}

# Check 1: Basic connectivity
log "${YELLOW}Checking PgBouncer connectivity...${NC}"
if ! execute_query "SELECT 1" > /dev/null; then
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo '{"status":"unhealthy","error":"Cannot connect to PgBouncer","checks":{"connectivity":false}}'
  else
    echo -e "${RED}✗ Cannot connect to PgBouncer${NC}"
  fi
  exit 1
fi
log "${GREEN}✓ PgBouncer is reachable${NC}"

# Check 2: Pool status
log "${YELLOW}Checking pool status...${NC}"
POOL_DATA=$(execute_query "SHOW POOLS;" 2>/dev/null || echo "")
if [[ -z "$POOL_DATA" ]]; then
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo '{"status":"unhealthy","error":"Cannot retrieve pool status","checks":{"connectivity":true,"pools":false}}'
  else
    echo -e "${RED}✗ Cannot retrieve pool status${NC}"
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

while IFS='|' read -r db user cl_active cl_waiting sv_active sv_idle sv_used sv_tested sv_login maxwait pool_mode; do
  # Skip header and pgbouncer database
  if [[ "$db" == "pgbouncer" ]] || [[ "$db" == "database" ]]; then
    continue
  fi

  TOTAL_CL_ACTIVE=$((TOTAL_CL_ACTIVE + cl_active))
  TOTAL_CL_WAITING=$((TOTAL_CL_WAITING + cl_waiting))
  TOTAL_SV_ACTIVE=$((TOTAL_SV_ACTIVE + sv_active))
  TOTAL_SV_IDLE=$((TOTAL_SV_IDLE + sv_idle))

  if [[ $maxwait -gt $MAX_WAIT ]]; then
    MAX_WAIT=$maxwait
  fi
done <<< "$POOL_DATA"

# Calculate utilization (assuming max_db_connections = 150)
MAX_CONNECTIONS=150
TOTAL_SV_CONNECTIONS=$((TOTAL_SV_ACTIVE + TOTAL_SV_IDLE))
UTILIZATION=0
if [[ $MAX_CONNECTIONS -gt 0 ]]; then
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

if [[ $UTILIZATION -ge $CRIT_THRESHOLD ]]; then
  STATUS="critical"
  EXIT_CODE=1
  log "${RED}✗ CRITICAL: Pool utilization at ${UTILIZATION}% (threshold: ${CRIT_THRESHOLD}%)${NC}"
elif [[ $UTILIZATION -ge $WARN_THRESHOLD ]]; then
  STATUS="warning"
  EXIT_CODE=2
  log "${YELLOW}⚠ WARNING: Pool utilization at ${UTILIZATION}% (threshold: ${WARN_THRESHOLD}%)${NC}"
else
  log "${GREEN}✓ Pool utilization healthy (${UTILIZATION}%)${NC}"
fi

if [[ $TOTAL_CL_WAITING -gt 0 ]]; then
  STATUS="warning"
  EXIT_CODE=2
  log "${YELLOW}⚠ WARNING: ${TOTAL_CL_WAITING} clients waiting for connections${NC}"
fi

if [[ $MAX_WAIT -gt 10 ]]; then
  STATUS="warning"
  EXIT_CODE=2
  log "${YELLOW}⚠ WARNING: Maximum wait time is ${MAX_WAIT}s (>10s)${NC}"
fi

# Check 3: Configuration verification
log "${YELLOW}Checking configuration...${NC}"
CONFIG_DATA=$(execute_query "SHOW CONFIG;" 2>/dev/null || echo "")
if [[ -n "$CONFIG_DATA" ]]; then
  log "${GREEN}✓ Configuration accessible${NC}"

  if [[ "$VERBOSE" == "true" ]]; then
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
if [[ "$JSON_OUTPUT" == "true" ]]; then
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
  echo -e "Status: $(
    case $STATUS in
      healthy) echo "${GREEN}✓ HEALTHY${NC}" ;;
      warning) echo "${YELLOW}⚠ WARNING${NC}" ;;
      critical) echo "${RED}✗ CRITICAL${NC}" ;;
    esac
  )"
  echo "Pool Utilization: ${UTILIZATION}% (${TOTAL_SV_CONNECTIONS}/${MAX_CONNECTIONS} connections)"
  echo "Active Clients: $TOTAL_CL_ACTIVE"
  echo "Waiting Clients: $TOTAL_CL_WAITING"
  echo "Max Wait Time: ${MAX_WAIT}s"
  echo "═══════════════════════════════════════"
fi

exit $EXIT_CODE
