#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - PostgreSQL Automated Failover Script
# سكريبت التبديل التلقائي لقاعدة البيانات PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Automated failover and manual switchover for PostgreSQL cluster
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Patroni configuration
PATRONI_API_HOST="${PATRONI_API_HOST:-localhost}"
PATRONI_API_PORT="${PATRONI_API_PORT:-8008}"
CLUSTER_NAME="${CLUSTER_NAME:-sahool-postgres-cluster}"

# Notification settings
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
ENABLE_NOTIFICATIONS="${ENABLE_NOTIFICATIONS:-true}"

# Logging
LOG_DIR="${PROJECT_ROOT}/logs/disaster-recovery"
LOG_FILE="${LOG_DIR}/failover_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "${LOG_DIR}"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "${LOG_FILE}"
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_FILE}"
}

error_exit() {
    print_message "${RED}" "ERROR: $1"
    send_notification "failure" "PostgreSQL failover failed: $1"
    exit 1
}

success_message() {
    print_message "${GREEN}" "✓ $1"
}

warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

info_message() {
    print_message "${BLUE}" "ℹ $1"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2

    if [ "$ENABLE_NOTIFICATIONS" != "true" ]; then
        return
    fi

    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local color="good"
        local emoji=":white_check_mark:"

        if [ "$status" = "failure" ]; then
            color="danger"
            emoji=":x:"
        elif [ "$status" = "warning" ]; then
            color="warning"
            emoji=":warning:"
        fi

        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-Type: application/json' \
            -d @- > /dev/null 2>&1 <<EOF
{
    "attachments": [{
        "color": "${color}",
        "title": "${emoji} PostgreSQL Failover - ${CLUSTER_NAME}",
        "text": "${message}",
        "fields": [
            {"title": "Cluster", "value": "${CLUSTER_NAME}", "short": true},
            {"title": "Timestamp", "value": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "short": true}
        ],
        "footer": "SAHOOL Disaster Recovery System",
        "ts": $(date +%s)
    }]
}
EOF
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Patroni API Functions
# ─────────────────────────────────────────────────────────────────────────────

# Get cluster status
get_cluster_status() {
    curl -s "http://${PATRONI_API_HOST}:${PATRONI_API_PORT}/cluster" || echo "{}"
}

# Get current primary
get_primary() {
    get_cluster_status | jq -r '.members[] | select(.role == "leader") | .name'
}

# Get replicas
get_replicas() {
    get_cluster_status | jq -r '.members[] | select(.role == "replica") | .name'
}

# Check node health
check_node_health() {
    local node=$1
    local api_url="http://${node}:8008/health"

    if curl -sf "${api_url}" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Get replication lag
get_replication_lag() {
    local replica=$1
    get_cluster_status | jq -r ".members[] | select(.name == \"${replica}\") | .lag"
}

# ─────────────────────────────────────────────────────────────────────────────
# Failover Functions
# ─────────────────────────────────────────────────────────────────────────────

# Check if failover is needed
check_primary_health() {
    info_message "Checking primary node health..."

    local primary=$(get_primary)
    if [ -z "$primary" ]; then
        warning_message "No primary node found in cluster"
        return 1
    fi

    info_message "Current primary: ${primary}"

    if check_node_health "$primary"; then
        success_message "Primary node is healthy"
        return 0
    else
        warning_message "Primary node is unhealthy!"
        return 1
    fi
}

# Select best candidate for promotion
select_failover_candidate() {
    info_message "Selecting best failover candidate..."

    local replicas=$(get_replicas)
    local best_candidate=""
    local min_lag=999999

    for replica in $replicas; do
        if check_node_health "$replica"; then
            local lag=$(get_replication_lag "$replica")
            info_message "Replica ${replica}: lag=${lag}bytes"

            # Convert lag to number (remove 'MB' suffix if present)
            lag_num=$(echo "$lag" | sed 's/[^0-9]//g')

            if [ "$lag_num" -lt "$min_lag" ]; then
                min_lag=$lag_num
                best_candidate=$replica
            fi
        else
            warning_message "Replica ${replica} is unhealthy, skipping"
        fi
    done

    if [ -z "$best_candidate" ]; then
        error_exit "No healthy replica found for failover"
    fi

    success_message "Best candidate: ${best_candidate} (lag: ${min_lag}bytes)"
    echo "$best_candidate"
}

# Perform manual switchover
perform_switchover() {
    local target_node="${1:-}"

    info_message "Performing manual switchover..."

    if [ -z "$target_node" ]; then
        target_node=$(select_failover_candidate)
    fi

    info_message "Target node for switchover: ${target_node}"

    # Perform switchover via Patroni API
    local response=$(curl -s -X POST \
        "http://${PATRONI_API_HOST}:${PATRONI_API_PORT}/switchover" \
        -H "Content-Type: application/json" \
        -d "{\"leader\": \"$(get_primary)\", \"candidate\": \"${target_node}\"}")

    if echo "$response" | grep -q "Successfully"; then
        success_message "Switchover initiated successfully"
        send_notification "success" "Switchover to ${target_node} completed"
        return 0
    else
        error_exit "Switchover failed: ${response}"
    fi
}

# Perform automated failover
perform_failover() {
    local target_node="${1:-}"

    info_message "Performing automated failover..."
    send_notification "warning" "Initiating automated failover for cluster ${CLUSTER_NAME}"

    local start_time=$(date +%s)

    if [ -z "$target_node" ]; then
        target_node=$(select_failover_candidate)
    fi

    info_message "Promoting ${target_node} to primary..."

    # Perform failover via Patroni API
    local response=$(curl -s -X POST \
        "http://${PATRONI_API_HOST}:${PATRONI_API_PORT}/failover" \
        -H "Content-Type: application/json" \
        -d "{\"candidate\": \"${target_node}\"}")

    # Wait for failover to complete
    info_message "Waiting for failover to complete..."
    sleep 5

    # Verify new primary
    local new_primary=$(get_primary)
    if [ "$new_primary" = "$target_node" ]; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        success_message "Failover completed successfully in ${duration} seconds"
        success_message "New primary: ${new_primary}"
        send_notification "success" "Failover completed: ${new_primary} is now primary (${duration}s)"
        return 0
    else
        error_exit "Failover failed: Expected ${target_node} to be primary, but got ${new_primary}"
    fi
}

# Check cluster health after failover
verify_cluster_health() {
    info_message "Verifying cluster health after failover..."

    local primary=$(get_primary)
    if [ -z "$primary" ]; then
        error_exit "No primary found after failover"
    fi

    success_message "Primary: ${primary}"

    local replicas=$(get_replicas)
    local replica_count=$(echo "$replicas" | wc -w)

    info_message "Replicas: ${replica_count}"

    for replica in $replicas; do
        if check_node_health "$replica"; then
            local lag=$(get_replication_lag "$replica")
            info_message "  - ${replica}: healthy (lag: ${lag})"
        else
            warning_message "  - ${replica}: unhealthy"
        fi
    done

    success_message "Cluster health verification completed"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

show_usage() {
    cat <<EOF
SAHOOL Platform - PostgreSQL Automated Failover Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    status              Show cluster status
    check              Check if failover is needed
    switchover [NODE]  Perform manual switchover to NODE (or best candidate)
    failover [NODE]    Perform automated failover to NODE (or best candidate)
    verify             Verify cluster health

Options:
    -h, --help         Show this help message

Examples:
    $0 status                          # Show cluster status
    $0 check                           # Check primary health
    $0 switchover                      # Switchover to best candidate
    $0 switchover postgres-replica1    # Switchover to specific node
    $0 failover                        # Automated failover
    $0 verify                          # Verify cluster health

EOF
}

main() {
    local command="${1:-status}"

    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - PostgreSQL Failover Manager"
    print_message "${BLUE}" "  إدارة التبديل التلقائي لقاعدة البيانات"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    case "$command" in
        status)
            info_message "Cluster: ${CLUSTER_NAME}"
            get_cluster_status | jq '.'
            ;;

        check)
            if check_primary_health; then
                success_message "No failover needed"
                exit 0
            else
                warning_message "Failover may be needed"
                exit 1
            fi
            ;;

        switchover)
            local target="${2:-}"
            perform_switchover "$target"
            verify_cluster_health
            ;;

        failover)
            local target="${2:-}"
            perform_failover "$target"
            verify_cluster_health
            ;;

        verify)
            verify_cluster_health
            ;;

        -h|--help)
            show_usage
            exit 0
            ;;

        *)
            error_exit "Unknown command: $command. Use -h for help."
            ;;
    esac

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "Operation completed successfully"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
}

main "$@"
