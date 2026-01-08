#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Database Backup Monitoring Script
# سكريبت مراقبة النسخ الاحتياطي لقاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Date: 2026-01-06
# Purpose: Monitor database backups and push metrics to Prometheus Pushgateway
#
# This script checks the status of database backups and pushes metrics to
# Prometheus Pushgateway for monitoring and alerting. It monitors:
# - Backup age (time since last backup)
# - Backup size
# - Backup status (exists/missing)
# - Backup integrity (optional)
#
# Usage:
#   ./backup_monitor.sh [OPTIONS]
#
# Options:
#   --backup-dir DIR         Backup directory (default: /backups/postgres)
#   --pushgateway URL        Pushgateway URL (default: localhost:9091)
#   --check-integrity        Verify backup integrity (slower)
#   --help                   Show this help message
#
# Environment Variables:
#   BACKUP_DIR               Override backup directory
#   PUSHGATEWAY              Override Pushgateway URL
#   BACKUP_MAX_AGE_HOURS     Alert if backup older than this (default: 24)
#
# Example Cron Entry:
#   */15 * * * * /scripts/backup_monitor.sh --pushgateway prometheus-pushgateway:9091
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration - الإعدادات
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Default values
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
PUSHGATEWAY="${PUSHGATEWAY:-localhost:9091}"
BACKUP_MAX_AGE_HOURS="${BACKUP_MAX_AGE_HOURS:-24}"
CHECK_INTEGRITY=0
VERBOSE=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Functions - الوظائف
# ─────────────────────────────────────────────────────────────────────────────

# Print colored message
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} ${timestamp} - ${message}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - ${message}"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} ${timestamp} - ${message}"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} ${timestamp} - ${message}"
            ;;
        *)
            echo "${timestamp} - ${message}"
            ;;
    esac
}

# Show help message
show_help() {
    cat << EOF
SAHOOL Backup Monitoring Script

Usage: $SCRIPT_NAME [OPTIONS]

Options:
    --backup-dir DIR         Backup directory (default: $BACKUP_DIR)
    --pushgateway URL        Pushgateway URL (default: $PUSHGATEWAY)
    --check-integrity        Verify backup integrity (slower)
    --verbose                Enable verbose output
    --help                   Show this help message

Environment Variables:
    BACKUP_DIR               Override backup directory
    PUSHGATEWAY              Override Pushgateway URL
    BACKUP_MAX_AGE_HOURS     Alert if backup older than this (default: 24 hours)

Example:
    $SCRIPT_NAME --backup-dir /var/backups/postgres --pushgateway prometheus-pushgateway:9091

Cron Example (every 15 minutes):
    */15 * * * * $SCRIPT_DIR/$SCRIPT_NAME --pushgateway prometheus-pushgateway:9091

EOF
    exit 0
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup-dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            --pushgateway)
                PUSHGATEWAY="$2"
                shift 2
                ;;
            --check-integrity)
                CHECK_INTEGRITY=1
                shift
                ;;
            --verbose)
                VERBOSE=1
                shift
                ;;
            --help)
                show_help
                ;;
            *)
                log ERROR "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

# Check if backup directory exists
check_backup_directory() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log WARNING "Backup directory does not exist: $BACKUP_DIR"
        return 1
    fi

    if [[ ! -r "$BACKUP_DIR" ]]; then
        log ERROR "Backup directory is not readable: $BACKUP_DIR"
        return 1
    fi

    [[ $VERBOSE -eq 1 ]] && log INFO "Backup directory exists: $BACKUP_DIR"
    return 0
}

# Get latest backup file
get_latest_backup() {
    local latest_backup

    # Look for common backup file patterns
    # PostgreSQL dumps: .sql, .sql.gz, .dump, .custom
    latest_backup=$(find "$BACKUP_DIR" -type f \( \
        -name "*.sql" -o \
        -name "*.sql.gz" -o \
        -name "*.sql.bz2" -o \
        -name "*.dump" -o \
        -name "*.custom" -o \
        -name "*.tar" -o \
        -name "*.tar.gz" \
    \) 2>/dev/null | sort -r | head -1)

    echo "$latest_backup"
}

# Calculate backup age in seconds
get_backup_age() {
    local backup_file="$1"
    local current_time=$(date +%s)
    local file_time

    if [[ -f "$backup_file" ]]; then
        file_time=$(stat -c %Y "$backup_file" 2>/dev/null || stat -f %m "$backup_file" 2>/dev/null)
        echo $((current_time - file_time))
    else
        echo -1
    fi
}

# Get backup size in bytes
get_backup_size() {
    local backup_file="$1"

    if [[ -f "$backup_file" ]]; then
        stat -c %s "$backup_file" 2>/dev/null || stat -f %z "$backup_file" 2>/dev/null
    else
        echo 0
    fi
}

# Check backup integrity (basic check)
check_backup_integrity() {
    local backup_file="$1"
    local integrity_status=1  # Assume valid

    if [[ ! -f "$backup_file" ]]; then
        return 0  # Unknown
    fi

    # Check file size (should be > 0)
    local size=$(get_backup_size "$backup_file")
    if [[ $size -le 0 ]]; then
        log WARNING "Backup file is empty: $backup_file"
        return 0
    fi

    # Check compressed files
    if [[ "$backup_file" == *.gz ]]; then
        if ! gunzip -t "$backup_file" 2>/dev/null; then
            log ERROR "Backup file is corrupted (gzip test failed): $backup_file"
            return 0
        fi
    elif [[ "$backup_file" == *.bz2 ]]; then
        if ! bunzip2 -t "$backup_file" 2>/dev/null; then
            log ERROR "Backup file is corrupted (bzip2 test failed): $backup_file"
            return 0
        fi
    fi

    [[ $VERBOSE -eq 1 ]] && log SUCCESS "Backup integrity check passed"
    return 1
}

# Format bytes to human readable
format_bytes() {
    local bytes=$1
    local units=("B" "KB" "MB" "GB" "TB")
    local unit=0

    while [[ $bytes -ge 1024 && $unit -lt 4 ]]; do
        bytes=$((bytes / 1024))
        unit=$((unit + 1))
    done

    echo "${bytes}${units[$unit]}"
}

# Format seconds to human readable duration
format_duration() {
    local seconds=$1
    local days=$((seconds / 86400))
    local hours=$(((seconds % 86400) / 3600))
    local minutes=$(((seconds % 3600) / 60))

    if [[ $days -gt 0 ]]; then
        echo "${days}d ${hours}h ${minutes}m"
    elif [[ $hours -gt 0 ]]; then
        echo "${hours}h ${minutes}m"
    else
        echo "${minutes}m"
    fi
}

# Push metrics to Prometheus Pushgateway
push_metrics() {
    local backup_age=$1
    local backup_size=$2
    local backup_status=$3
    local integrity_status=$4
    local backup_file=$5

    local metrics_data

    # Build metrics in Prometheus format
    metrics_data=$(cat <<EOF
# HELP postgres_backup_age_seconds Age of the latest PostgreSQL backup in seconds
# TYPE postgres_backup_age_seconds gauge
postgres_backup_age_seconds{backup_dir="$BACKUP_DIR"} $backup_age

# HELP postgres_backup_size_bytes Size of the latest PostgreSQL backup in bytes
# TYPE postgres_backup_size_bytes gauge
postgres_backup_size_bytes{backup_dir="$BACKUP_DIR"} $backup_size

# HELP postgres_backup_status Status of the latest backup (1=exists, 0=missing)
# TYPE postgres_backup_status gauge
postgres_backup_status{backup_dir="$BACKUP_DIR"} $backup_status

# HELP postgres_backup_integrity Backup integrity status (1=valid, 0=invalid/unknown)
# TYPE postgres_backup_integrity gauge
postgres_backup_integrity{backup_dir="$BACKUP_DIR"} $integrity_status

# HELP postgres_backup_info Backup file information
# TYPE postgres_backup_info gauge
postgres_backup_info{backup_dir="$BACKUP_DIR",backup_file="$(basename "$backup_file")"} 1

# HELP postgres_backup_monitoring_timestamp_seconds Last time backup monitoring ran
# TYPE postgres_backup_monitoring_timestamp_seconds gauge
postgres_backup_monitoring_timestamp_seconds $(date +%s)
EOF
)

    # Push to Pushgateway using curl
    if curl -s --data-binary "$metrics_data" "http://$PUSHGATEWAY/metrics/job/backup_monitor/instance/$(hostname)" > /dev/null 2>&1; then
        log SUCCESS "Metrics pushed to Pushgateway: $PUSHGATEWAY"
        [[ $VERBOSE -eq 1 ]] && echo "$metrics_data"
        return 0
    else
        log ERROR "Failed to push metrics to Pushgateway: $PUSHGATEWAY"
        return 1
    fi
}

# Main monitoring logic
monitor_backup() {
    log INFO "Starting backup monitoring..."
    log INFO "Backup directory: $BACKUP_DIR"
    log INFO "Pushgateway: $PUSHGATEWAY"

    # Check backup directory
    if ! check_backup_directory; then
        # Push metrics indicating no backup directory
        push_metrics -1 0 0 0 "none"
        return 1
    fi

    # Get latest backup
    local latest_backup=$(get_latest_backup)

    if [[ -z "$latest_backup" ]]; then
        log WARNING "No backup files found in $BACKUP_DIR"
        push_metrics -1 0 0 0 "none"
        return 1
    fi

    log INFO "Latest backup: $(basename "$latest_backup")"

    # Get backup metrics
    local backup_age=$(get_backup_age "$latest_backup")
    local backup_size=$(get_backup_size "$latest_backup")
    local backup_status=1
    local integrity_status=1

    # Check integrity if requested
    if [[ $CHECK_INTEGRITY -eq 1 ]]; then
        log INFO "Checking backup integrity..."
        check_backup_integrity "$latest_backup"
        integrity_status=$?
    fi

    # Display backup information
    log INFO "Backup age: $(format_duration $backup_age) (${backup_age}s)"
    log INFO "Backup size: $(format_bytes $backup_size) (${backup_size} bytes)"

    # Check if backup is too old
    local max_age_seconds=$((BACKUP_MAX_AGE_HOURS * 3600))
    if [[ $backup_age -gt $max_age_seconds ]]; then
        log WARNING "Backup is older than ${BACKUP_MAX_AGE_HOURS} hours!"
        log WARNING "Last backup: $(format_duration $backup_age) ago"
    else
        log SUCCESS "Backup is up to date (less than ${BACKUP_MAX_AGE_HOURS} hours old)"
    fi

    # Push metrics to Pushgateway
    push_metrics "$backup_age" "$backup_size" "$backup_status" "$integrity_status" "$latest_backup"

    log SUCCESS "Backup monitoring completed"
    return 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution - التنفيذ الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main() {
    parse_args "$@"
    monitor_backup
}

# Run main function
main "$@"
