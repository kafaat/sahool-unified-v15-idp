#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Database Health Check - Usage Examples
# أمثلة استخدام فحص صحة قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

# This file demonstrates various ways to use the db_health_check.sh script
# يوضح هذا الملف طرق مختلفة لاستخدام سكريبت db_health_check.sh

# ─────────────────────────────────────────────────────────────────────────────
# Example 1: Basic Health Check / المثال 1: فحص الصحة الأساسي
# ─────────────────────────────────────────────────────────────────────────────

basic_health_check() {
    echo "Running basic health check..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    ./db_health_check.sh

    local exit_code=$?
    case $exit_code in
        0)
            echo "✓ Database is healthy"
            ;;
        1)
            echo "⚠ Database has warnings"
            ;;
        2)
            echo "✗ Database has critical issues"
            ;;
    esac
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 2: JSON Output for Monitoring / المثال 2: مخرجات JSON للمراقبة
# ─────────────────────────────────────────────────────────────────────────────

json_health_check() {
    echo "Running health check with JSON output..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    # Capture JSON output
    local json_output=$(./db_health_check.sh --json 2>/dev/null)

    # Parse with jq (if available)
    if command -v jq &> /dev/null; then
        echo "Status: $(echo "$json_output" | jq -r '.status')"
        echo "Active Connections: $(echo "$json_output" | jq -r '.metrics.active_connections // "N/A"')"
        echo "Disk Usage: $(echo "$json_output" | jq -r '.metrics.disk_usage_pct // "N/A"')%"
    else
        echo "$json_output"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 3: Custom Thresholds / المثال 3: حدود مخصصة
# ─────────────────────────────────────────────────────────────────────────────

custom_thresholds_check() {
    echo "Running health check with custom thresholds..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    ./db_health_check.sh \
        --disk-warning 85 \
        --disk-critical 95 \
        --conn-warning 75 \
        --conn-critical 90 \
        --query-timeout 60
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 4: Remote Database Check / المثال 4: فحص قاعدة بيانات بعيدة
# ─────────────────────────────────────────────────────────────────────────────

remote_health_check() {
    echo "Checking remote database..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    ./db_health_check.sh \
        --postgres-host db.example.com \
        --postgres-port 5432 \
        --pgbouncer-host pgbouncer.example.com \
        --pgbouncer-port 6432
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 5: Replication Monitoring / المثال 5: مراقبة النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

replication_check() {
    echo "Checking database replication status..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    ./db_health_check.sh --check-replication --json | \
        jq '{
            status: .status,
            replication: .checks.replication,
            replica_count: .metrics.replica_count,
            max_lag_seconds: .metrics.max_replication_lag_seconds
        }'
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 6: Continuous Monitoring / المثال 6: المراقبة المستمرة
# ─────────────────────────────────────────────────────────────────────────────

continuous_monitoring() {
    echo "Starting continuous monitoring (press Ctrl+C to stop)..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    while true; do
        clear
        echo "=== Database Health Check - $(date) ==="
        echo ""
        ./db_health_check.sh
        echo ""
        echo "Next check in 30 seconds..."
        sleep 30
    done
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 7: Alert on Critical Status / المثال 7: تنبيه عند الحالة الحرجة
# ─────────────────────────────────────────────────────────────────────────────

alert_on_critical() {
    echo "Running health check with alerting..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    ./db_health_check.sh --json > /tmp/db_health.json 2>&1
    local exit_code=$?

    if [ $exit_code -eq 2 ]; then
        # Critical status - send alert
        local status=$(jq -r '.status' /tmp/db_health.json)
        local message="Database health is CRITICAL: $status"

        # Example: Send to Slack
        # curl -X POST -H 'Content-type: application/json' \
        #     --data "{\"text\":\"$message\"}" \
        #     $SLACK_WEBHOOK_URL

        # Example: Send email
        # echo "$message" | mail -s "Database Alert" admin@example.com

        echo "ALERT: $message"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 8: Docker Container Health Check / المثال 8: فحص صحة حاوية Docker
# ─────────────────────────────────────────────────────────────────────────────

docker_healthcheck() {
    echo "Running health check in Docker container..."

    docker run --rm \
        --network sahool-network \
        -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}" \
        -e POSTGRES_HOST=postgres \
        -e PGBOUNCER_HOST=pgbouncer \
        -v "$(pwd)/db_health_check.sh:/check.sh:ro" \
        postgres:16-alpine \
        sh -c "apk add --no-cache bash bc && /check.sh --json"
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 9: Log to File / المثال 9: السجل إلى ملف
# ─────────────────────────────────────────────────────────────────────────────

log_to_file() {
    echo "Running health check and logging to file..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    local log_file="/var/log/sahool/db_health_$(date +%Y%m%d).log"

    {
        echo "=== Health Check - $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="
        ./db_health_check.sh --json
        echo ""
    } >> "$log_file"

    echo "Logged to: $log_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Example 10: Prometheus Metrics Export / المثال 10: تصدير مقاييس Prometheus
# ─────────────────────────────────────────────────────────────────────────────

prometheus_export() {
    echo "Exporting database metrics in Prometheus format..."
    export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

    local metrics=$(./db_health_check.sh --json 2>/dev/null)

    cat << EOF
# HELP db_health_status Database health status (0=healthy, 1=warning, 2=critical)
# TYPE db_health_status gauge
db_health_status $(echo "$metrics" | jq -r '.exit_code')

# HELP db_active_connections Number of active database connections
# TYPE db_active_connections gauge
db_active_connections $(echo "$metrics" | jq -r '.metrics.active_connections // 0')

# HELP db_connection_usage_percent Database connection usage percentage
# TYPE db_connection_usage_percent gauge
db_connection_usage_percent $(echo "$metrics" | jq -r '.metrics.connection_usage_pct // 0')

# HELP db_long_running_queries Number of long-running queries
# TYPE db_long_running_queries gauge
db_long_running_queries $(echo "$metrics" | jq -r '.metrics.long_running_queries // 0')

# HELP db_disk_usage_percent Database disk usage percentage
# TYPE db_disk_usage_percent gauge
db_disk_usage_percent $(echo "$metrics" | jq -r '.metrics.disk_usage_pct // 0')
EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Menu / القائمة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

show_menu() {
    cat << EOF

═══════════════════════════════════════════════════════════════════════════════
SAHOOL Database Health Check - Examples Menu
قائمة أمثلة فحص صحة قاعدة البيانات
═══════════════════════════════════════════════════════════════════════════════

Please select an example to run:

1)  Basic Health Check / فحص الصحة الأساسي
2)  JSON Output / مخرجات JSON
3)  Custom Thresholds / حدود مخصصة
4)  Remote Database Check / فحص قاعدة بيانات بعيدة
5)  Replication Monitoring / مراقبة النسخ الاحتياطي
6)  Continuous Monitoring / المراقبة المستمرة
7)  Alert on Critical / تنبيه عند الحالة الحرجة
8)  Docker Container Check / فحص حاوية Docker
9)  Log to File / السجل إلى ملف
10) Prometheus Export / تصدير Prometheus

0)  Exit / خروج

═══════════════════════════════════════════════════════════════════════════════
EOF

    read -p "Enter your choice (0-10): " choice
    echo ""

    case $choice in
        1) basic_health_check ;;
        2) json_health_check ;;
        3) custom_thresholds_check ;;
        4) remote_health_check ;;
        5) replication_check ;;
        6) continuous_monitoring ;;
        7) alert_on_critical ;;
        8) docker_healthcheck ;;
        9) log_to_file ;;
        10) prometheus_export ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid choice. Please try again." ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# ─────────────────────────────────────────────────────────────────────────────
# Script Entry Point / نقطة دخول السكريبت
# ─────────────────────────────────────────────────────────────────────────────

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed, show menu
    show_menu
else
    # Script is being sourced, functions are now available
    echo "Functions loaded. Available examples:"
    echo "  - basic_health_check"
    echo "  - json_health_check"
    echo "  - custom_thresholds_check"
    echo "  - remote_health_check"
    echo "  - replication_check"
    echo "  - continuous_monitoring"
    echo "  - alert_on_critical"
    echo "  - docker_healthcheck"
    echo "  - log_to_file"
    echo "  - prometheus_export"
fi
