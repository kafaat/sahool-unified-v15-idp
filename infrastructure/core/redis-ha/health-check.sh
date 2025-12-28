#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Redis Sentinel Health Check Script
# سكريبت فحص صحة Redis Sentinel
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REDIS_PASSWORD="${REDIS_PASSWORD:-redis_password}"
SENTINEL_PORTS=(26379 26380 26381)
REDIS_PORTS=(6379 6380 6381)
MASTER_NAME="sahool-master"

echo "═══════════════════════════════════════════════════════════════"
echo "  Redis Sentinel Health Check"
echo "  فحص صحة Redis Sentinel"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Function to check Redis instance
check_redis() {
    local port=$1
    local name=$2

    if redis-cli -p "$port" -a "$REDIS_PASSWORD" --no-auth-warning ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name (port $port): OK"
        return 0
    else
        echo -e "${RED}✗${NC} $name (port $port): FAILED"
        return 1
    fi
}

# Function to check Sentinel
check_sentinel() {
    local port=$1
    local num=$2

    if redis-cli -p "$port" ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Sentinel $num (port $port): OK"

        # Get master info
        master_info=$(redis-cli -p "$port" SENTINEL master "$MASTER_NAME" 2>/dev/null | grep -E "^ip|^port|^flags" | paste - - | head -3)
        if [ -n "$master_info" ]; then
            echo "  Master Info:"
            echo "$master_info" | while read line; do
                echo "    $line"
            done
        fi
        return 0
    else
        echo -e "${RED}✗${NC} Sentinel $num (port $port): FAILED"
        return 1
    fi
}

# Check Redis Master
echo "─────────────────────────────────────────────────────────────────"
echo "Checking Redis Master:"
echo "─────────────────────────────────────────────────────────────────"
check_redis 6379 "Redis Master"
echo ""

# Check Redis Replicas
echo "─────────────────────────────────────────────────────────────────"
echo "Checking Redis Replicas:"
echo "─────────────────────────────────────────────────────────────────"
check_redis 6380 "Redis Replica 1"
check_redis 6381 "Redis Replica 2"
echo ""

# Check Sentinels
echo "─────────────────────────────────────────────────────────────────"
echo "Checking Sentinels:"
echo "─────────────────────────────────────────────────────────────────"
for i in "${!SENTINEL_PORTS[@]}"; do
    check_sentinel "${SENTINEL_PORTS[$i]}" "$((i + 1))"
    echo ""
done

# Get replication info
echo "─────────────────────────────────────────────────────────────────"
echo "Replication Status:"
echo "─────────────────────────────────────────────────────────────────"
repl_info=$(redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning INFO replication | grep -E "role|connected_slaves|slave[0-9]")
echo "$repl_info"
echo ""

# Get Sentinel info
echo "─────────────────────────────────────────────────────────────────"
echo "Sentinel Master Info:"
echo "─────────────────────────────────────────────────────────────────"
redis-cli -p 26379 SENTINEL master "$MASTER_NAME" | grep -E "ip|port|num-slaves|num-other-sentinels|flags" | paste - -
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}Health check completed!${NC}"
echo "═══════════════════════════════════════════════════════════════"
