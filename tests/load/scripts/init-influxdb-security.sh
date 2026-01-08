#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - InfluxDB Security Initialization Script
# سكريبت تهيئة أمان قاعدة بيانات InfluxDB
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script initializes InfluxDB with proper security settings:
# - Creates scoped tokens (read-only for Grafana, write-only for k6)
# - Sets up bucket permissions
# - Configures retention policies
# - Creates additional buckets for aggregated data
#
# Prerequisites:
# - InfluxDB container must be running
# - Admin credentials must be set in environment variables
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
INFLUXDB_CONTAINER="${INFLUXDB_CONTAINER:-sahool-loadtest-influxdb}"
INFLUXDB_ORG="${INFLUXDB_ORG:-sahool}"
INFLUXDB_BUCKET="${INFLUXDB_BUCKET:-k6}"
INFLUXDB_URL="${INFLUXDB_URL:-http://localhost:8086}"

# Check if admin token is set
if [ -z "$INFLUXDB_ADMIN_TOKEN" ]; then
    echo -e "${RED}ERROR: INFLUXDB_ADMIN_TOKEN environment variable is not set${NC}"
    echo "Please set the admin token: export INFLUXDB_ADMIN_TOKEN=your-admin-token"
    exit 1
fi

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}SAHOOL InfluxDB Security Initialization${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to check if InfluxDB is ready
wait_for_influxdb() {
    echo -e "${YELLOW}Waiting for InfluxDB to be ready...${NC}"
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker exec $INFLUXDB_CONTAINER influx ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ InfluxDB is ready${NC}"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}ERROR: InfluxDB did not become ready in time${NC}"
    exit 1
}

# Wait for InfluxDB to be ready
wait_for_influxdb
echo ""

# Create read-only token for Grafana
echo -e "${YELLOW}Creating read-only token for Grafana...${NC}"
GRAFANA_TOKEN=$(docker exec $INFLUXDB_CONTAINER influx auth create \
    --org $INFLUXDB_ORG \
    --read-bucket $INFLUXDB_BUCKET \
    --description "Grafana read-only token (auto-generated)" \
    --json 2>/dev/null | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$GRAFANA_TOKEN" ]; then
    echo -e "${GREEN}✓ Grafana read-only token created${NC}"
    echo "INFLUXDB_GRAFANA_READ_TOKEN=$GRAFANA_TOKEN"
else
    echo -e "${RED}✗ Failed to create Grafana token${NC}"
fi
echo ""

# Create write-only token for k6
echo -e "${YELLOW}Creating write-only token for k6...${NC}"
K6_TOKEN=$(docker exec $INFLUXDB_CONTAINER influx auth create \
    --org $INFLUXDB_ORG \
    --write-bucket $INFLUXDB_BUCKET \
    --description "k6 write-only token (auto-generated)" \
    --json 2>/dev/null | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$K6_TOKEN" ]; then
    echo -e "${GREEN}✓ k6 write-only token created${NC}"
    echo "INFLUXDB_K6_WRITE_TOKEN=$K6_TOKEN"
else
    echo -e "${RED}✗ Failed to create k6 token${NC}"
fi
echo ""

# Create additional bucket for aggregated data
echo -e "${YELLOW}Creating aggregated data bucket...${NC}"
docker exec $INFLUXDB_CONTAINER influx bucket create \
    --name k6_hourly \
    --org $INFLUXDB_ORG \
    --retention 90d \
    --description "Hourly aggregated k6 metrics" \
    2>/dev/null || echo -e "${YELLOW}  (Bucket may already exist)${NC}"
echo ""

# Create continuous aggregation task (Flux script)
echo -e "${YELLOW}Creating data aggregation task...${NC}"
cat > /tmp/aggregate-task.flux << 'EOFTASK'
option task = {
  name: "Aggregate k6 metrics hourly",
  every: 1h,
  offset: 5m
}

from(bucket: "k6")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "http_req_duration" or r._measurement == "http_reqs")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> to(bucket: "k6_hourly", org: "sahool")
EOFTASK

docker cp /tmp/aggregate-task.flux $INFLUXDB_CONTAINER:/tmp/aggregate-task.flux
docker exec $INFLUXDB_CONTAINER influx task create \
    --org $INFLUXDB_ORG \
    --file /tmp/aggregate-task.flux \
    2>/dev/null || echo -e "${YELLOW}  (Task may already exist)${NC}"
rm -f /tmp/aggregate-task.flux
echo ""

# Display bucket information
echo -e "${YELLOW}Bucket Information:${NC}"
docker exec $INFLUXDB_CONTAINER influx bucket list --org $INFLUXDB_ORG
echo ""

# Display auth tokens summary
echo -e "${YELLOW}Authentication Tokens Summary:${NC}"
docker exec $INFLUXDB_CONTAINER influx auth list --org $INFLUXDB_ORG --json 2>/dev/null | \
    grep -o '"description":"[^"]*"' || echo "Tokens configured"
echo ""

# Save tokens to file (for reference)
echo -e "${YELLOW}Saving tokens to .env.influxdb.secret (append mode)...${NC}"
cat >> .env.influxdb.secret << EOF

# Auto-generated scoped tokens ($(date))
INFLUXDB_GRAFANA_READ_TOKEN=$GRAFANA_TOKEN
INFLUXDB_K6_WRITE_TOKEN=$K6_TOKEN
EOF
echo -e "${GREEN}✓ Tokens saved to .env.influxdb.secret${NC}"
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}InfluxDB Security Initialization Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update Grafana datasource with: INFLUXDB_GRAFANA_READ_TOKEN"
echo "2. Update k6 configuration with: INFLUXDB_K6_WRITE_TOKEN"
echo "3. Revoke admin token access from application services"
echo "4. Test connections with new tokens"
echo ""
echo -e "${RED}⚠️  SECURITY REMINDER:${NC}"
echo -e "${RED}   - Store tokens securely (use secrets management)${NC}"
echo -e "${RED}   - Rotate tokens regularly${NC}"
echo -e "${RED}   - Never commit .env.influxdb.secret to version control${NC}"
echo ""
