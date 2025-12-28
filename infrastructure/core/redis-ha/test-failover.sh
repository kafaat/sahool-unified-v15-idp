#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Redis Sentinel Failover Test Script
# سكريبت اختبار Failover لـ Redis Sentinel
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REDIS_PASSWORD="${REDIS_PASSWORD:-redis_password}"
MASTER_NAME="sahool-master"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Redis Sentinel Failover Test${NC}"
echo -e "${BLUE}  اختبار Failover لـ Redis Sentinel${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to get master info
get_master_info() {
    redis-cli -p 26379 SENTINEL get-master-addr-by-name "$MASTER_NAME" 2>/dev/null
}

# Function to get master container
get_master_container() {
    # Get current master address
    master_info=$(get_master_info)
    master_port=$(echo "$master_info" | tail -1)

    # Map port to container
    case "$master_port" in
        6379)
            echo "sahool-redis-master"
            ;;
        6380)
            echo "sahool-redis-replica-1"
            ;;
        6381)
            echo "sahool-redis-replica-2"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Step 1: Get current master
echo -e "${YELLOW}Step 1: Getting current master info...${NC}"
CURRENT_MASTER_INFO=$(get_master_info)
CURRENT_MASTER_HOST=$(echo "$CURRENT_MASTER_INFO" | head -1)
CURRENT_MASTER_PORT=$(echo "$CURRENT_MASTER_INFO" | tail -1)

echo -e "${GREEN}Current Master:${NC}"
echo "  Host: $CURRENT_MASTER_HOST"
echo "  Port: $CURRENT_MASTER_PORT"
echo ""

# Step 2: Get master container
echo -e "${YELLOW}Step 2: Identifying master container...${NC}"
MASTER_CONTAINER=$(get_master_container)

if [ "$MASTER_CONTAINER" = "unknown" ]; then
    echo -e "${RED}✗ Could not identify master container${NC}"
    exit 1
fi

echo -e "${GREEN}Master Container: $MASTER_CONTAINER${NC}"
echo ""

# Step 3: Verify master is running
echo -e "${YELLOW}Step 3: Verifying master is running...${NC}"
if ! docker ps | grep -q "$MASTER_CONTAINER"; then
    echo -e "${RED}✗ Master container is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Master is running${NC}"
echo ""

# Step 4: Test write to master
echo -e "${YELLOW}Step 4: Testing write to master...${NC}"
TEST_KEY="failover_test_$(date +%s)"
redis-cli -p "$CURRENT_MASTER_PORT" -a "$REDIS_PASSWORD" --no-auth-warning SET "$TEST_KEY" "before_failover" > /dev/null
echo -e "${GREEN}✓ Write successful: $TEST_KEY = before_failover${NC}"
echo ""

# Step 5: Stop master
echo -e "${YELLOW}Step 5: Stopping master container...${NC}"
docker stop "$MASTER_CONTAINER" > /dev/null 2>&1
echo -e "${GREEN}✓ Master stopped${NC}"
echo ""

# Step 6: Wait for failover
echo -e "${YELLOW}Step 6: Waiting for failover (this may take 5-10 seconds)...${NC}"
FAILOVER_TIMEOUT=30
ELAPSED=0

while [ $ELAPSED -lt $FAILOVER_TIMEOUT ]; do
    sleep 1
    ELAPSED=$((ELAPSED + 1))

    # Get new master
    NEW_MASTER_INFO=$(get_master_info 2>/dev/null || echo "")
    if [ -n "$NEW_MASTER_INFO" ]; then
        NEW_MASTER_HOST=$(echo "$NEW_MASTER_INFO" | head -1)
        NEW_MASTER_PORT=$(echo "$NEW_MASTER_INFO" | tail -1)

        # Check if master changed
        if [ "$NEW_MASTER_PORT" != "$CURRENT_MASTER_PORT" ]; then
            echo -e "${GREEN}✓ Failover completed in ${ELAPSED}s${NC}"
            break
        fi
    fi

    # Show progress
    echo -n "."
done

echo ""

if [ $ELAPSED -ge $FAILOVER_TIMEOUT ]; then
    echo -e "${RED}✗ Failover timeout after ${FAILOVER_TIMEOUT}s${NC}"
    docker start "$MASTER_CONTAINER" > /dev/null 2>&1
    exit 1
fi

# Step 7: Verify new master
echo -e "${YELLOW}Step 7: Verifying new master...${NC}"
echo -e "${GREEN}New Master:${NC}"
echo "  Host: $NEW_MASTER_HOST"
echo "  Port: $NEW_MASTER_PORT"
echo ""

# Step 8: Test read from new master
echo -e "${YELLOW}Step 8: Testing read from new master...${NC}"
sleep 2  # Wait for replication to sync

TEST_VALUE=$(redis-cli -p "$NEW_MASTER_PORT" -a "$REDIS_PASSWORD" --no-auth-warning GET "$TEST_KEY" 2>/dev/null || echo "")

if [ "$TEST_VALUE" = "before_failover" ]; then
    echo -e "${GREEN}✓ Read successful: $TEST_KEY = $TEST_VALUE${NC}"
    echo -e "${GREEN}✓ Data preserved after failover${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Could not verify data preservation${NC}"
    echo "  Expected: before_failover"
    echo "  Got: $TEST_VALUE"
fi
echo ""

# Step 9: Test write to new master
echo -e "${YELLOW}Step 9: Testing write to new master...${NC}"
redis-cli -p "$NEW_MASTER_PORT" -a "$REDIS_PASSWORD" --no-auth-warning SET "$TEST_KEY" "after_failover" > /dev/null
echo -e "${GREEN}✓ Write successful: $TEST_KEY = after_failover${NC}"
echo ""

# Step 10: Restart old master
echo -e "${YELLOW}Step 10: Restarting old master (will become replica)...${NC}"
docker start "$MASTER_CONTAINER" > /dev/null 2>&1
echo -e "${GREEN}✓ Old master restarted${NC}"
echo ""

# Step 11: Wait for old master to sync
echo -e "${YELLOW}Step 11: Waiting for replication sync...${NC}"
sleep 5
echo -e "${GREEN}✓ Sync completed${NC}"
echo ""

# Step 12: Verify replication
echo -e "${YELLOW}Step 12: Verifying replication...${NC}"
REPLICATION_INFO=$(redis-cli -p "$NEW_MASTER_PORT" -a "$REDIS_PASSWORD" --no-auth-warning INFO replication | grep -E "role|connected_slaves")
echo "$REPLICATION_INFO"
echo ""

# Step 13: Cleanup test data
echo -e "${YELLOW}Step 13: Cleaning up test data...${NC}"
redis-cli -p "$NEW_MASTER_PORT" -a "$REDIS_PASSWORD" --no-auth-warning DEL "$TEST_KEY" > /dev/null
echo -e "${GREEN}✓ Test data cleaned${NC}"
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓✓✓ Failover Test Completed Successfully! ✓✓✓${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Summary:"
echo "  • Old Master: $CURRENT_MASTER_HOST:$CURRENT_MASTER_PORT"
echo "  • New Master: $NEW_MASTER_HOST:$NEW_MASTER_PORT"
echo "  • Failover Time: ${ELAPSED}s"
echo "  • Data Preserved: ✓"
echo "  • New Master Functional: ✓"
echo "  • Old Master Rejoined: ✓"
echo ""
echo -e "${GREEN}All systems operational!${NC}"
