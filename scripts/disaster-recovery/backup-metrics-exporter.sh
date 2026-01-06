#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Backup Metrics Exporter for Prometheus
# مُصدّر مقاييس النسخ الاحتياطي لـ Prometheus
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Exports backup and DR metrics to Prometheus Pushgateway
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Prometheus Pushgateway configuration
PUSHGATEWAY_URL="${PROMETHEUS_PUSHGATEWAY_URL:-http://localhost:9091}"
JOB_NAME="sahool_backup_metrics"
INSTANCE_NAME="${HOSTNAME:-localhost}"

# Backup directories
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"

# ─────────────────────────────────────────────────────────────────────────────
# Metrics Collection Functions
# ─────────────────────────────────────────────────────────────────────────────

# Initialize metrics buffer
METRICS=""

add_metric() {
    local metric_name="$1"
    local metric_value="$2"
    local labels="${3:-}"

    if [ -n "$labels" ]; then
        METRICS+="${metric_name}{${labels}} ${metric_value}"$'\n'
    else
        METRICS+="${metric_name} ${metric_value}"$'\n'
    fi
}

# Collect PostgreSQL backup metrics
collect_postgres_metrics() {
    local backup_dir="${BACKUP_BASE_DIR}/postgres/daily"

    if [ ! -d "$backup_dir" ]; then
        add_metric "sahool_backup_last_success_timestamp" "0" "service=\"postgresql\""
        add_metric "sahool_backup_last_status" "0" "service=\"postgresql\""
        return
    fi

    # Find most recent backup
    local recent_backup=$(find "$backup_dir" -type d -name "2*" | sort -r | head -1)

    if [ -n "$recent_backup" ]; then
        local backup_timestamp=$(stat -c %Y "$recent_backup")
        local backup_age=$(($(date +%s) - backup_timestamp))

        add_metric "sahool_backup_last_success_timestamp" "$backup_timestamp" "service=\"postgresql\""
        add_metric "sahool_backup_age_seconds" "$backup_age" "service=\"postgresql\""

        # Check if backup was successful (metadata exists)
        if [ -f "${recent_backup}/metadata.json" ]; then
            add_metric "sahool_backup_last_status" "1" "service=\"postgresql\""

            # Extract backup size from metadata
            local backup_size=$(jq -r '.backup_file.size // 0' "${recent_backup}/metadata.json")
            add_metric "sahool_backup_size_bytes" "$backup_size" "service=\"postgresql\""
        else
            add_metric "sahool_backup_last_status" "0" "service=\"postgresql\""
        fi
    else
        add_metric "sahool_backup_last_success_timestamp" "0" "service=\"postgresql\""
        add_metric "sahool_backup_last_status" "0" "service=\"postgresql\""
    fi
}

# Collect Redis backup metrics
collect_redis_metrics() {
    local backup_dir="${BACKUP_BASE_DIR}/redis/daily"

    if [ ! -d "$backup_dir" ]; then
        add_metric "sahool_backup_last_success_timestamp" "0" "service=\"redis\""
        return
    fi

    local recent_backup=$(find "$backup_dir" -type d -name "2*" | sort -r | head -1)

    if [ -n "$recent_backup" ]; then
        local backup_timestamp=$(stat -c %Y "$recent_backup")
        add_metric "sahool_backup_last_success_timestamp" "$backup_timestamp" "service=\"redis\""

        if [ -f "${recent_backup}/dump.rdb" ]; then
            local backup_size=$(stat -c %s "${recent_backup}/dump.rdb")
            add_metric "sahool_backup_size_bytes" "$backup_size" "service=\"redis\""
            add_metric "sahool_backup_last_status" "1" "service=\"redis\""
        else
            add_metric "sahool_backup_last_status" "0" "service=\"redis\""
        fi
    fi
}

# Collect MinIO backup metrics
collect_minio_metrics() {
    local backup_dir="${BACKUP_BASE_DIR}/minio/daily"

    if [ ! -d "$backup_dir" ]; then
        add_metric "sahool_backup_last_success_timestamp" "0" "service=\"minio\""
        return
    fi

    local recent_backup=$(find "$backup_dir" -type d -name "2*" | sort -r | head -1)

    if [ -n "$recent_backup" ]; then
        local backup_timestamp=$(stat -c %Y "$recent_backup")
        add_metric "sahool_backup_last_success_timestamp" "$backup_timestamp" "service=\"minio\""

        local backup_size=$(du -sb "$recent_backup" 2>/dev/null | awk '{print $1}')
        add_metric "sahool_backup_size_bytes" "$backup_size" "service=\"minio\""
        add_metric "sahool_backup_last_status" "1" "service=\"minio\""
    fi
}

# Collect WAL archive metrics
collect_wal_metrics() {
    if docker exec postgres-primary test -d /var/lib/postgresql/wal-archive 2>/dev/null; then
        local wal_count=$(docker exec postgres-primary sh -c \
            'ls -1 /var/lib/postgresql/wal-archive 2>/dev/null | wc -l' || echo 0)
        add_metric "sahool_wal_archive_file_count" "$wal_count"

        local wal_size=$(docker exec postgres-primary sh -c \
            'du -sb /var/lib/postgresql/wal-archive 2>/dev/null | awk "{print \$1}"' || echo 0)
        add_metric "sahool_wal_archive_size_bytes" "$wal_size"

        # Last WAL archived timestamp (most recent file modification)
        local last_wal_time=$(docker exec postgres-primary sh -c \
            'stat -c %Y $(ls -t /var/lib/postgresql/wal-archive/* 2>/dev/null | head -1) 2>/dev/null' || echo 0)
        if [ "$last_wal_time" != "0" ]; then
            add_metric "sahool_wal_archive_last_timestamp" "$last_wal_time"
        fi
    fi
}

# Collect replication metrics
collect_replication_metrics() {
    # PostgreSQL replication
    if docker exec postgres-primary psql -U postgres -t -c \
        "SELECT COUNT(*) FROM pg_stat_replication;" 2>/dev/null | grep -q "[0-9]"; then

        local replica_count=$(docker exec postgres-primary psql -U postgres -t -c \
            "SELECT COUNT(*) FROM pg_stat_replication;" 2>/dev/null | xargs)
        add_metric "pg_stat_replication_count" "$replica_count"

        # Get max replication lag
        local max_lag=$(docker exec postgres-primary psql -U postgres -t -c \
            "SELECT COALESCE(MAX(pg_wal_lsn_diff(sent_lsn, replay_lsn)), 0)::bigint FROM pg_stat_replication;" \
            2>/dev/null | xargs)
        if [ -n "$max_lag" ]; then
            add_metric "pg_replication_lag_bytes" "$max_lag"
        fi
    else
        add_metric "pg_stat_replication_count" "0"
    fi
}

# Collect storage metrics
collect_storage_metrics() {
    if [ -d "$BACKUP_BASE_DIR" ]; then
        local used_space=$(du -sb "$BACKUP_BASE_DIR" 2>/dev/null | awk '{print $1}')
        add_metric "sahool_backup_storage_used_bytes" "$used_space"

        # Total space on the filesystem
        local total_space=$(df -B1 "$BACKUP_BASE_DIR" | tail -1 | awk '{print $2}')
        add_metric "sahool_backup_storage_total_bytes" "$total_space"

        # Calculate usage percentage
        local usage_percent=$(awk "BEGIN {printf \"%.2f\", ($used_space / $total_space) * 100}")
        add_metric "sahool_backup_storage_usage_percent" "$usage_percent"
    fi
}

# Collect RTO/RPO compliance metrics
collect_rto_rpo_metrics() {
    # RPO: Time since last backup
    local postgres_backup_dir="${BACKUP_BASE_DIR}/postgres/daily"
    if [ -d "$postgres_backup_dir" ]; then
        local recent_backup=$(find "$postgres_backup_dir" -type d -name "2*" | sort -r | head -1)
        if [ -n "$recent_backup" ]; then
            local backup_age=$(($(date +%s) - $(stat -c %Y "$recent_backup")))

            # RPO target is 1 hour (3600 seconds)
            if [ "$backup_age" -le 3600 ]; then
                add_metric "sahool_rpo_compliance_status" "1"
            else
                add_metric "sahool_rpo_compliance_status" "0"
            fi

            # Current worst-case RPO (time since last backup)
            add_metric "sahool_current_rpo_seconds" "$backup_age"
        fi
    fi

    # RTO: Check if restore scripts are available
    if [ -x "${PROJECT_ROOT}/scripts/backup/restore_postgres.sh" ]; then
        add_metric "sahool_rto_restore_ready" "1"
    else
        add_metric "sahool_rto_restore_ready" "0"
    fi
}

# Collect DR drill metrics
collect_dr_drill_metrics() {
    local drill_log_dir="${PROJECT_ROOT}/logs/dr-tests"

    if [ -d "$drill_log_dir" ]; then
        # Find most recent successful DR test
        local recent_test=$(find "$drill_log_dir" -name "dr_test_results_*.json" | sort -r | head -1)

        if [ -n "$recent_test" ]; then
            local test_timestamp=$(stat -c %Y "$recent_test")
            add_metric "sahool_dr_drill_last_timestamp" "$test_timestamp"

            # Check if test was successful (all tests passed)
            local failed_count=$(jq -r '.summary.failed' "$recent_test" 2>/dev/null || echo 1)
            if [ "$failed_count" -eq 0 ]; then
                add_metric "sahool_dr_drill_last_success_timestamp" "$test_timestamp"
                add_metric "sahool_dr_drill_last_status" "1"
            else
                add_metric "sahool_dr_drill_last_status" "0"
            fi
        else
            add_metric "sahool_dr_drill_last_timestamp" "0"
            add_metric "sahool_dr_drill_last_status" "0"
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Push Metrics to Pushgateway
# ─────────────────────────────────────────────────────────────────────────────

push_metrics() {
    if [ -z "$METRICS" ]; then
        echo "No metrics collected"
        return 1
    fi

    # Push to Pushgateway
    if curl -s --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/${JOB_NAME}/instance/${INSTANCE_NAME}" <<EOF
$METRICS
EOF
    then
        echo "Metrics pushed successfully to ${PUSHGATEWAY_URL}"
        return 0
    else
        echo "Failed to push metrics to Pushgateway"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo "Collecting backup and DR metrics..."

    # Collect all metrics
    collect_postgres_metrics
    collect_redis_metrics
    collect_minio_metrics
    collect_wal_metrics
    collect_replication_metrics
    collect_storage_metrics
    collect_rto_rpo_metrics
    collect_dr_drill_metrics

    echo "Collected $(echo "$METRICS" | grep -c '^sahool') metrics"

    # Push to Pushgateway
    if [ -n "${PUSHGATEWAY_URL}" ]; then
        push_metrics
    else
        echo "Pushgateway URL not configured, outputting metrics:"
        echo "$METRICS"
    fi
}

main "$@"
