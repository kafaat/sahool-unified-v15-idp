#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Backup Monitoring and Alerting Script
# نظام مراقبة وتنبيهات النسخ الاحتياطي
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Monitor backup health, generate metrics, and send alerts
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting - الألوان والتنسيق
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Configuration - التكوين
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Paths
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
LOG_DIR="${BACKUP_BASE_DIR}/logs"
METRICS_DIR="${BACKUP_BASE_DIR}/metrics"
REPORTS_DIR="${PROJECT_ROOT}/logs/backup-reports"

# Create directories
mkdir -p "${LOG_DIR}"
mkdir -p "${METRICS_DIR}"
mkdir -p "${REPORTS_DIR}"

# Metrics file (Prometheus format)
METRICS_FILE="${METRICS_DIR}/backup_metrics.prom"

# Health check thresholds
MAX_BACKUP_AGE_HOURS="${MAX_BACKUP_AGE_HOURS:-26}"  # 26 hours (daily + 2hr buffer)
MIN_BACKUP_SIZE_MB="${MIN_BACKUP_SIZE_MB:-1}"  # 1 MB minimum

# Notification configuration
SLACK_NOTIFICATIONS="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
EMAIL_NOTIFICATIONS="${EMAIL_NOTIFICATIONS_ENABLED:-false}"
BACKUP_EMAIL_TO="${BACKUP_EMAIL_TO:-admin@sahool.com}"

# Components to monitor
COMPONENTS=("postgres" "redis" "minio" "etcd" "qdrant")

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

success_message() {
    print_message "${GREEN}" "✓ $1"
}

warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

error_message() {
    print_message "${RED}" "✗ $1"
}

info_message() {
    print_message "${BLUE}" "ℹ $1"
}

# Send Slack notification
send_slack_notification() {
    local status=$1
    local component=$2
    local message=$3

    [ "$SLACK_NOTIFICATIONS" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ] && return

    local color="good"
    local emoji=":white_check_mark:"

    case "$status" in
        error)
            color="danger"
            emoji=":x:"
            ;;
        warning)
            color="warning"
            emoji=":warning:"
            ;;
    esac

    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d @- > /dev/null 2>&1 <<EOF
{
    "attachments": [{
        "color": "${color}",
        "title": "${emoji} Backup Monitor Alert - ${component}",
        "text": "${message}",
        "footer": "SAHOOL Backup Monitor",
        "ts": $(date +%s)
    }]
}
EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Monitoring Functions - دوال المراقبة
# ─────────────────────────────────────────────────────────────────────────────

# Check backup age - فحص عمر النسخة الاحتياطية
check_backup_age() {
    local component=$1
    local backup_type=${2:-daily}

    local backup_dir="${BACKUP_BASE_DIR}/${component}/${backup_type}"

    if [ ! -d "$backup_dir" ]; then
        return 1
    fi

    # Find most recent backup
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | sort -r | head -n 1)

    if [ -z "$latest_backup" ]; then
        return 1
    fi

    # Get backup age in hours
    local backup_timestamp=$(stat -f%m "$latest_backup" 2>/dev/null || stat -c%Y "$latest_backup" 2>/dev/null)
    local current_timestamp=$(date +%s)
    local age_hours=$(( (current_timestamp - backup_timestamp) / 3600 ))

    echo "$age_hours"
}

# Check backup size - فحص حجم النسخة الاحتياطية
check_backup_size() {
    local component=$1
    local backup_type=${2:-daily}

    local backup_dir="${BACKUP_BASE_DIR}/${component}/${backup_type}"

    if [ ! -d "$backup_dir" ]; then
        return 1
    fi

    # Find most recent backup
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | sort -r | head -n 1)

    if [ -z "$latest_backup" ]; then
        return 1
    fi

    # Get total size in MB
    local size_mb=$(du -sm "$latest_backup" 2>/dev/null | awk '{print $1}')

    echo "$size_mb"
}

# Count backups - عد النسخ الاحتياطية
count_backups() {
    local component=$1
    local backup_type=${2:-daily}

    local backup_dir="${BACKUP_BASE_DIR}/${component}/${backup_type}"

    if [ ! -d "$backup_dir" ]; then
        echo "0"
        return
    fi

    local count=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | wc -l)
    echo "$count"
}

# Check backup verification status - فحص حالة التحقق من النسخة
check_verification_status() {
    local latest_report=$(find "${REPORTS_DIR}" -type f -name "verification_*.txt" | sort -r | head -n 1)

    if [ -z "$latest_report" ]; then
        echo "0"
        return
    fi

    # Check if verification passed
    if grep -q "PASSED" "$latest_report"; then
        echo "1"
    else
        echo "0"
    fi
}

# Check disk usage - فحص استخدام القرص
check_disk_usage() {
    local backup_partition=$(df -h "$BACKUP_BASE_DIR" | tail -n 1)
    local usage_percent=$(echo "$backup_partition" | awk '{print $5}' | sed 's/%//')

    echo "$usage_percent"
}

# ─────────────────────────────────────────────────────────────────────────────
# Metrics Generation - إنشاء المقاييس
# ─────────────────────────────────────────────────────────────────────────────

generate_metrics() {
    info_message "Generating Prometheus metrics..."

    # Start metrics file
    {
        echo "# HELP sahool_backup_age_hours Age of the most recent backup in hours"
        echo "# TYPE sahool_backup_age_hours gauge"

        echo "# HELP sahool_backup_size_mb Size of the most recent backup in megabytes"
        echo "# TYPE sahool_backup_size_mb gauge"

        echo "# HELP sahool_backup_count Total number of backups"
        echo "# TYPE sahool_backup_count gauge"

        echo "# HELP sahool_backup_health Health status of backup (1=healthy, 0=unhealthy)"
        echo "# TYPE sahool_backup_health gauge"

        echo "# HELP sahool_backup_verification_status Last verification status (1=passed, 0=failed)"
        echo "# TYPE sahool_backup_verification_status gauge"

        echo "# HELP sahool_backup_disk_usage_percent Backup storage disk usage percentage"
        echo "# TYPE sahool_backup_disk_usage_percent gauge"

        # Component-specific metrics
        for component in "${COMPONENTS[@]}"; do
            local age=$(check_backup_age "$component" "daily" 2>/dev/null || echo "-1")
            local size=$(check_backup_size "$component" "daily" 2>/dev/null || echo "0")
            local count=$(count_backups "$component" "daily")

            # Health check
            local health=1
            if [ "$age" = "-1" ] || [ "$age" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
                health=0
            fi
            if [ "$size" -lt "$MIN_BACKUP_SIZE_MB" ]; then
                health=0
            fi

            echo "sahool_backup_age_hours{component=\"${component}\",type=\"daily\"} ${age}"
            echo "sahool_backup_size_mb{component=\"${component}\",type=\"daily\"} ${size}"
            echo "sahool_backup_count{component=\"${component}\",type=\"daily\"} ${count}"
            echo "sahool_backup_health{component=\"${component}\"} ${health}"
        done

        # Global metrics
        local verification_status=$(check_verification_status)
        local disk_usage=$(check_disk_usage)

        echo "sahool_backup_verification_status ${verification_status}"
        echo "sahool_backup_disk_usage_percent ${disk_usage}"

        # Timestamp
        echo "# HELP sahool_backup_metrics_timestamp Unix timestamp when metrics were generated"
        echo "# TYPE sahool_backup_metrics_timestamp gauge"
        echo "sahool_backup_metrics_timestamp $(date +%s)"

    } > "${METRICS_FILE}"

    success_message "Metrics generated: ${METRICS_FILE}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Health Checks - فحوصات الصحة
# ─────────────────────────────────────────────────────────────────────────────

perform_health_checks() {
    info_message "Performing backup health checks..."

    local total_checks=0
    local passed_checks=0
    local failed_checks=0
    local warnings=0

    for component in "${COMPONENTS[@]}"; do
        ((total_checks++))

        info_message "Checking ${component} backups..."

        # Check backup age
        local age=$(check_backup_age "$component" "daily" 2>/dev/null || echo "-1")

        if [ "$age" = "-1" ]; then
            error_message "${component}: No backup found"
            send_slack_notification "error" "$component" "No backup found for ${component}"
            ((failed_checks++))
            continue
        fi

        if [ "$age" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
            warning_message "${component}: Backup is ${age} hours old (threshold: ${MAX_BACKUP_AGE_HOURS}h)"
            send_slack_notification "warning" "$component" "Backup is ${age} hours old (threshold: ${MAX_BACKUP_AGE_HOURS}h)"
            ((warnings++))
        else
            success_message "${component}: Backup age OK (${age}h)"
        fi

        # Check backup size
        local size=$(check_backup_size "$component" "daily" 2>/dev/null || echo "0")

        if [ "$size" -lt "$MIN_BACKUP_SIZE_MB" ]; then
            error_message "${component}: Backup size too small (${size}MB, minimum: ${MIN_BACKUP_SIZE_MB}MB)"
            send_slack_notification "error" "$component" "Backup size too small (${size}MB)"
            ((failed_checks++))
        else
            success_message "${component}: Backup size OK (${size}MB)"
            ((passed_checks++))
        fi

        # Check backup count
        local count=$(count_backups "$component" "daily")
        info_message "${component}: ${count} daily backup(s) found"
    done

    # Check disk usage
    local disk_usage=$(check_disk_usage)
    if [ "$disk_usage" -gt 85 ]; then
        warning_message "Disk usage high: ${disk_usage}%"
        send_slack_notification "warning" "disk" "Backup storage usage at ${disk_usage}%"
        ((warnings++))
    else
        success_message "Disk usage OK: ${disk_usage}%"
    fi

    # Summary
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Health Check Summary"
    echo "════════════════════════════════════════════════════════════════"
    echo "  Total checks:  ${total_checks}"
    echo "  Passed:        ${passed_checks}"
    echo "  Failed:        ${failed_checks}"
    echo "  Warnings:      ${warnings}"
    echo "════════════════════════════════════════════════════════════════"

    # Return status
    if [ "$failed_checks" -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Report Generation - إنشاء التقارير
# ─────────────────────────────────────────────────────────────────────────────

generate_health_report() {
    local report_file="${REPORTS_DIR}/health_check_$(date +%Y%m%d_%H%M%S).txt"

    info_message "Generating health report..."

    {
        echo "═══════════════════════════════════════════════════════════════"
        echo "  SAHOOL Platform - Backup Health Report"
        echo "  تقرير صحة النسخ الاحتياطي لمنصة سهول"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        echo "Report Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Report Type: Health Check"
        echo ""

        echo "─────────────────────────────────────────────────────────────"
        echo "Component Status"
        echo "─────────────────────────────────────────────────────────────"

        for component in "${COMPONENTS[@]}"; do
            local age=$(check_backup_age "$component" "daily" 2>/dev/null || echo "-1")
            local size=$(check_backup_size "$component" "daily" 2>/dev/null || echo "0")
            local count=$(count_backups "$component" "daily")

            echo ""
            echo "Component: ${component}"
            echo "  Latest backup age: ${age} hours"
            echo "  Latest backup size: ${size} MB"
            echo "  Total daily backups: ${count}"

            if [ "$age" = "-1" ]; then
                echo "  Status: ✗ MISSING"
            elif [ "$age" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
                echo "  Status: ⚠ OLD"
            elif [ "$size" -lt "$MIN_BACKUP_SIZE_MB" ]; then
                echo "  Status: ✗ TOO SMALL"
            else
                echo "  Status: ✓ HEALTHY"
            fi
        done

        echo ""
        echo "─────────────────────────────────────────────────────────────"
        echo "System Metrics"
        echo "─────────────────────────────────────────────────────────────"
        echo "Disk usage: $(check_disk_usage)%"
        echo "Last verification: $(check_verification_status | grep -q '1' && echo 'PASSED' || echo 'NOT VERIFIED')"

        echo ""
        echo "─────────────────────────────────────────────────────────────"
        echo "Storage Details"
        echo "─────────────────────────────────────────────────────────────"
        df -h "$BACKUP_BASE_DIR" | tail -n 1

        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo "End of Report"
        echo "═══════════════════════════════════════════════════════════════"

    } > "$report_file"

    success_message "Health report generated: $report_file"
    echo ""
    cat "$report_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  SAHOOL Backup Monitor"
    echo "  نظام مراقبة النسخ الاحتياطي"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    # Generate Prometheus metrics
    generate_metrics

    echo ""

    # Perform health checks
    if perform_health_checks; then
        success_message "All health checks passed!"
        send_slack_notification "success" "all" "All backup health checks passed"
    else
        error_message "Some health checks failed!"
        send_slack_notification "error" "all" "Backup health checks failed - please review"
    fi

    echo ""

    # Generate health report
    generate_health_report

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Monitor run completed"
    echo "  Metrics available at: ${METRICS_FILE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
