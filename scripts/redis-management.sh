#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Redis Management Script
# إدارة Redis - منصة سهول الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provides utilities for managing, monitoring, and maintaining Redis
# يوفر أدوات لإدارة ومراقبة وصيانة Redis
#
# Usage: ./redis-management.sh [command]
# Commands: status, info, memory, slowlog, latency, backup, restore, monitor, cli
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REDIS_CONTAINER="sahool-redis"
BACKUP_DIR="./backups/redis"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Check if Redis password is set
if [ -z "${REDIS_PASSWORD:-}" ]; then
    echo -e "${RED}Error: REDIS_PASSWORD not set in .env file${NC}"
    exit 1
fi

# Function to execute Redis CLI command
redis_cli() {
    docker exec -it "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" "$@" 2>/dev/null
}

# Function to display usage
usage() {
    cat <<EOF
${BLUE}═══════════════════════════════════════════════════════════════════════════════
SAHOOL Redis Management Script
إدارة Redis - منصة سهول الزراعية
═══════════════════════════════════════════════════════════════════════════════${NC}

${GREEN}Usage:${NC} $0 [command]

${GREEN}Commands:${NC}
  ${YELLOW}status${NC}      - Check Redis container status | التحقق من حالة حاوية Redis
  ${YELLOW}info${NC}        - Display Redis server information | عرض معلومات خادم Redis
  ${YELLOW}memory${NC}      - Show memory usage statistics | إحصائيات استخدام الذاكرة
  ${YELLOW}stats${NC}       - Show general statistics | الإحصائيات العامة
  ${YELLOW}slowlog${NC}     - Display slow queries log | سجل الاستعلامات البطيئة
  ${YELLOW}latency${NC}     - Show latency events | أحداث الكمون
  ${YELLOW}clients${NC}     - List connected clients | قائمة العملاء المتصلين
  ${YELLOW}keys${NC}        - Count keys per database | عدد المفاتيح لكل قاعدة بيانات
  ${YELLOW}backup${NC}      - Create backup of Redis data | إنشاء نسخة احتياطية
  ${YELLOW}restore${NC}     - Restore from backup | الاستعادة من النسخة الاحتياطية
  ${YELLOW}monitor${NC}     - Monitor Redis commands in real-time | مراقبة أوامر Redis
  ${YELLOW}cli${NC}         - Open Redis CLI | فتح واجهة سطر أوامر Redis
  ${YELLOW}flush-db${NC}    - Clear current database | مسح قاعدة البيانات الحالية
  ${YELLOW}flush-all${NC}   - Clear all databases | مسح جميع قواعد البيانات
  ${YELLOW}help${NC}        - Display this help message | عرض هذه الرسالة

${GREEN}Examples:${NC}
  $0 status
  $0 memory
  $0 backup
  $0 cli

${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}
EOF
}

# Check container status
check_status() {
    echo -e "${BLUE}Checking Redis container status...${NC}"
    if docker ps --filter "name=$REDIS_CONTAINER" --format "{{.Names}}" | grep -q "$REDIS_CONTAINER"; then
        echo -e "${GREEN}✓ Redis container is running${NC}"
        docker ps --filter "name=$REDIS_CONTAINER" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

        # Test connection
        if redis_cli PING > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis is responding to commands${NC}"
        else
            echo -e "${RED}✗ Redis is not responding${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Redis container is not running${NC}"
        exit 1
    fi
}

# Display server info
show_info() {
    echo -e "${BLUE}Redis Server Information${NC}"
    echo "════════════════════════════════════════"
    redis_cli INFO server | grep -E "(redis_version|os|arch|process_id|uptime_in_days)"
    echo ""
}

# Display memory statistics
show_memory() {
    echo -e "${BLUE}Redis Memory Statistics${NC}"
    echo "════════════════════════════════════════"
    redis_cli INFO memory | grep -E "(used_memory_human|used_memory_peak_human|used_memory_rss_human|maxmemory_human|mem_fragmentation_ratio)"
    echo ""

    echo -e "${BLUE}Memory Policy:${NC}"
    redis_cli CONFIG GET maxmemory-policy
    echo ""

    echo -e "${BLUE}Eviction Statistics:${NC}"
    redis_cli INFO stats | grep evicted
    echo ""
}

# Display general statistics
show_stats() {
    echo -e "${BLUE}Redis General Statistics${NC}"
    echo "════════════════════════════════════════"
    redis_cli INFO stats | grep -E "(total_connections|total_commands|instantaneous_ops|keyspace_hits|keyspace_misses)"
    echo ""

    # Calculate hit rate
    hits=$(redis_cli INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
    misses=$(redis_cli INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')

    if [ "$hits" != "0" ] || [ "$misses" != "0" ]; then
        total=$((hits + misses))
        hit_rate=$(awk "BEGIN {printf \"%.2f\", ($hits/$total)*100}")
        echo -e "${GREEN}Cache Hit Rate: ${hit_rate}%${NC}"
    fi
    echo ""
}

# Display slow queries
show_slowlog() {
    echo -e "${BLUE}Redis Slow Queries (Last 10)${NC}"
    echo "════════════════════════════════════════"
    redis_cli SLOWLOG GET 10
    echo ""

    echo -e "${BLUE}Slow Log Configuration:${NC}"
    redis_cli CONFIG GET slowlog-log-slower-than
    redis_cli CONFIG GET slowlog-max-len
    echo ""
}

# Display latency events
show_latency() {
    echo -e "${BLUE}Redis Latency Events${NC}"
    echo "════════════════════════════════════════"
    redis_cli LATENCY LATEST
    echo ""

    echo -e "${BLUE}Latency Configuration:${NC}"
    redis_cli CONFIG GET latency-monitor-threshold
    echo ""
}

# Display connected clients
show_clients() {
    echo -e "${BLUE}Connected Clients${NC}"
    echo "════════════════════════════════════════"
    redis_cli CLIENT LIST
    echo ""

    echo -e "${BLUE}Client Statistics:${NC}"
    redis_cli INFO clients
    echo ""
}

# Count keys per database
count_keys() {
    echo -e "${BLUE}Keys Count Per Database${NC}"
    echo "════════════════════════════════════════"

    for db in {0..15}; do
        redis_cli -n "$db" DBSIZE > /dev/null 2>&1 && {
            count=$(redis_cli -n "$db" DBSIZE | tr -d '\r')
            if [ "$count" != "0" ]; then
                echo -e "Database $db: ${GREEN}$count keys${NC}"
            fi
        }
    done
    echo ""
}

# Create backup
create_backup() {
    echo -e "${BLUE}Creating Redis backup...${NC}"

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Timestamp for backup files
    timestamp=$(date +%Y%m%d_%H%M%S)

    # Trigger background save using renamed command
    echo "Triggering background save..."
    redis_cli SAHOOL_BGSAVE_ADMIN_d4b8f2c5 || {
        echo -e "${YELLOW}Warning: Could not trigger BGSAVE (using existing snapshot)${NC}"
    }

    # Wait for save to complete
    sleep 2

    # Copy RDB file
    echo "Copying RDB snapshot..."
    docker cp "$REDIS_CONTAINER:/data/sahool-dump.rdb" "$BACKUP_DIR/sahool-dump-${timestamp}.rdb" 2>/dev/null || {
        echo -e "${YELLOW}Warning: Could not copy RDB file${NC}"
    }

    # Copy AOF file
    echo "Copying AOF file..."
    docker cp "$REDIS_CONTAINER:/data/sahool-appendonly.aof" "$BACKUP_DIR/sahool-appendonly-${timestamp}.aof" 2>/dev/null || {
        echo -e "${YELLOW}Warning: Could not copy AOF file${NC}"
    }

    # Create metadata file
    cat > "$BACKUP_DIR/backup-${timestamp}.info" <<EOF
Backup Created: $(date)
Redis Version: $(redis_cli INFO server | grep redis_version | cut -d: -f2)
Total Keys: $(redis_cli DBSIZE)
Memory Used: $(redis_cli INFO memory | grep used_memory_human | cut -d: -f2)
EOF

    echo -e "${GREEN}✓ Backup created successfully in $BACKUP_DIR${NC}"
    echo "Files:"
    ls -lh "$BACKUP_DIR/"*"${timestamp}"*
    echo ""
}

# Restore from backup
restore_backup() {
    echo -e "${YELLOW}WARNING: This will replace current Redis data!${NC}"
    echo -e "${YELLOW}Make sure to create a backup first if needed.${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "Restore cancelled."
        exit 0
    fi

    # List available backups
    echo -e "${BLUE}Available backups:${NC}"
    ls -1 "$BACKUP_DIR/"*.rdb 2>/dev/null | sort -r || {
        echo -e "${RED}No backups found in $BACKUP_DIR${NC}"
        exit 1
    }

    read -p "Enter the timestamp of the backup to restore (e.g., 20260106_120000): " timestamp

    rdb_file="$BACKUP_DIR/sahool-dump-${timestamp}.rdb"
    aof_file="$BACKUP_DIR/sahool-appendonly-${timestamp}.aof"

    if [ ! -f "$rdb_file" ]; then
        echo -e "${RED}Error: Backup file not found: $rdb_file${NC}"
        exit 1
    fi

    echo "Stopping Redis..."
    docker-compose stop redis

    echo "Copying backup files..."
    docker cp "$rdb_file" "$REDIS_CONTAINER:/data/sahool-dump.rdb"

    if [ -f "$aof_file" ]; then
        docker cp "$aof_file" "$REDIS_CONTAINER:/data/sahool-appendonly.aof"
    fi

    echo "Starting Redis..."
    docker-compose start redis

    # Wait for Redis to start
    sleep 5

    if redis_cli PING > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Restore completed successfully${NC}"
    else
        echo -e "${RED}✗ Redis failed to start after restore${NC}"
        exit 1
    fi
}

# Monitor Redis commands
monitor_redis() {
    echo -e "${BLUE}Monitoring Redis commands (press Ctrl+C to stop)...${NC}"
    redis_cli MONITOR
}

# Open Redis CLI
open_cli() {
    echo -e "${BLUE}Opening Redis CLI (type 'exit' to close)${NC}"
    redis_cli
}

# Flush current database
flush_db() {
    echo -e "${YELLOW}WARNING: This will delete all keys in the current database!${NC}"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "Operation cancelled."
        exit 0
    fi

    redis_cli SAHOOL_FLUSHDB_DANGER_f5a8d2e9
    echo -e "${GREEN}✓ Current database cleared${NC}"
}

# Flush all databases
flush_all() {
    echo -e "${RED}WARNING: This will delete ALL keys in ALL databases!${NC}"
    echo -e "${RED}This operation cannot be undone!${NC}"
    read -p "Are you ABSOLUTELY sure? (type 'DELETE ALL DATA' to confirm): " confirm

    if [ "$confirm" != "DELETE ALL DATA" ]; then
        echo "Operation cancelled."
        exit 0
    fi

    redis_cli SAHOOL_FLUSHALL_DANGER_b3c7f1a4
    echo -e "${GREEN}✓ All databases cleared${NC}"
}

# Main command handler
case "${1:-help}" in
    status)
        check_status
        ;;
    info)
        show_info
        ;;
    memory)
        show_memory
        ;;
    stats)
        show_stats
        ;;
    slowlog)
        show_slowlog
        ;;
    latency)
        show_latency
        ;;
    clients)
        show_clients
        ;;
    keys)
        count_keys
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup
        ;;
    monitor)
        monitor_redis
        ;;
    cli)
        open_cli
        ;;
    flush-db)
        flush_db
        ;;
    flush-all)
        flush_all
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo ""
        usage
        exit 1
        ;;
esac
