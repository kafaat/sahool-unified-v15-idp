#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Database Health Check Script
# سكريبت فحص صحة قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════
#
# Purpose / الغرض:
#   Comprehensive database health monitoring for PostgreSQL and PgBouncer
#   مراقبة شاملة لصحة قواعد البيانات PostgreSQL و PgBouncer
#
# Features / المميزات:
#   - PostgreSQL connectivity check / فحص اتصال PostgreSQL
#   - PgBouncer pool status / حالة تجمع اتصالات PgBouncer
#   - Active connections monitoring / مراقبة الاتصالات النشطة
#   - Long-running queries detection / كشف الاستعلامات طويلة التنفيذ
#   - Disk space monitoring / مراقبة مساحة القرص
#   - Replication lag check / فحص تأخر النسخ الاحتياطي
#   - JSON output for monitoring systems / إخراج JSON لأنظمة المراقبة
#   - Kubernetes probe compatible / متوافق مع مجسات Kubernetes
#
# Exit Codes / رموز الخروج:
#   0 = Healthy / صحي
#   1 = Warning / تحذير
#   2 = Critical / حرج
#
# Usage / الاستخدام:
#   ./db_health_check.sh [OPTIONS]
#
# Options:
#   --postgres-host HOST    PostgreSQL host (default: localhost)
#   --postgres-port PORT    PostgreSQL port (default: 5432)
#   --pgbouncer-host HOST   PgBouncer host (default: localhost)
#   --pgbouncer-port PORT   PgBouncer port (default: 6432)
#   --check-replication     Enable replication lag check
#   --disk-warning PCT      Disk space warning threshold (default: 80)
#   --disk-critical PCT     Disk space critical threshold (default: 90)
#   --conn-warning NUM      Connection count warning (default: 80)
#   --conn-critical NUM     Connection count critical (default: 95)
#   --query-timeout SEC     Long query threshold in seconds (default: 30)
#   --json                  Output in JSON format only
#   --help                  Show this help message
#
# Environment Variables:
#   POSTGRES_USER           Database user (default: sahool)
#   POSTGRES_PASSWORD       Database password (required)
#   POSTGRES_DB             Database name (default: sahool)
#   DB_CHECK_TIMEOUT        Overall check timeout in seconds (default: 30)
#
# Examples:
#   # Basic health check
#   ./db_health_check.sh
#
#   # JSON output for monitoring
#   ./db_health_check.sh --json
#
#   # Custom thresholds
#   ./db_health_check.sh --disk-warning 85 --conn-critical 90
#
#   # Check replication lag
#   ./db_health_check.sh --check-replication
#
# Kubernetes Integration:
#   livenessProbe:
#     exec:
#       command: ["/scripts/db_health_check.sh", "--json"]
#     initialDelaySeconds: 30
#     periodSeconds: 30
#     timeoutSeconds: 10
#     failureThreshold: 3
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration / الإعدادات
# ─────────────────────────────────────────────────────────────────────────────

# Default values / القيم الافتراضية
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
PGBOUNCER_HOST="${PGBOUNCER_HOST:-localhost}"
PGBOUNCER_PORT="${PGBOUNCER_PORT:-6432}"
POSTGRES_USER="${POSTGRES_USER:-sahool}"
POSTGRES_DB="${POSTGRES_DB:-sahool}"
PGPASSWORD="${POSTGRES_PASSWORD:-}"

# Thresholds / العتبات
DISK_WARNING_THRESHOLD=80
DISK_CRITICAL_THRESHOLD=90
CONN_WARNING_THRESHOLD=80
CONN_CRITICAL_THRESHOLD=95
QUERY_TIMEOUT_SECONDS=30
DB_CHECK_TIMEOUT="${DB_CHECK_TIMEOUT:-30}"

# Flags / العلامات
CHECK_REPLICATION=false
JSON_OUTPUT=false

# Health status / حالة الصحة
OVERALL_STATUS="healthy"
EXIT_CODE=0

# Results storage / تخزين النتائج
declare -A HEALTH_CHECKS
declare -A METRICS

# Timestamp / الطابع الزمني
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ─────────────────────────────────────────────────────────────────────────────
# Colors for terminal output / ألوان لمخرجات الطرفية
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions / وظائف مساعدة
# ─────────────────────────────────────────────────────────────────────────────

# Print colored log message / طباعة رسالة سجل ملونة
log() {
    local level=$1
    shift
    local message="$*"

    if [[ "$JSON_OUTPUT" == "false" ]]; then
        case $level in
            INFO)
                echo -e "${BLUE}[INFO]${NC} $message" >&2
                ;;
            SUCCESS)
                echo -e "${GREEN}[✓]${NC} $message" >&2
                ;;
            WARNING)
                echo -e "${YELLOW}[⚠]${NC} $message" >&2
                ;;
            ERROR)
                echo -e "${RED}[✗]${NC} $message" >&2
                ;;
        esac
    fi
}

# Update overall health status / تحديث حالة الصحة العامة
update_status() {
    local new_status=$1

    case $new_status in
        critical)
            OVERALL_STATUS="critical"
            EXIT_CODE=2
            ;;
        warning)
            if [[ "$OVERALL_STATUS" != "critical" ]]; then
                OVERALL_STATUS="warning"
                EXIT_CODE=1
            fi
            ;;
    esac
}

# Execute SQL query with timeout / تنفيذ استعلام SQL مع مهلة زمنية
execute_sql() {
    local host=$1
    local port=$2
    local query=$3
    local timeout=${4:-$DB_CHECK_TIMEOUT}

    timeout "$timeout" psql -h "$host" -p "$port" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -t -A -c "$query" 2>&1 || echo "ERROR"
}

# Show help message / عرض رسالة المساعدة
show_help() {
    grep "^#" "$0" | grep -v "^#!/" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Parse Command Line Arguments / تحليل معاملات سطر الأوامر
# ─────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case $1 in
        --postgres-host)
            POSTGRES_HOST="$2"
            shift 2
            ;;
        --postgres-port)
            POSTGRES_PORT="$2"
            shift 2
            ;;
        --pgbouncer-host)
            PGBOUNCER_HOST="$2"
            shift 2
            ;;
        --pgbouncer-port)
            PGBOUNCER_PORT="$2"
            shift 2
            ;;
        --check-replication)
            CHECK_REPLICATION=true
            shift
            ;;
        --disk-warning)
            DISK_WARNING_THRESHOLD="$2"
            shift 2
            ;;
        --disk-critical)
            DISK_CRITICAL_THRESHOLD="$2"
            shift 2
            ;;
        --conn-warning)
            CONN_WARNING_THRESHOLD="$2"
            shift 2
            ;;
        --conn-critical)
            CONN_CRITICAL_THRESHOLD="$2"
            shift 2
            ;;
        --query-timeout)
            QUERY_TIMEOUT_SECONDS="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────────────────────────────────────
# Validation / التحقق من الصحة
# ─────────────────────────────────────────────────────────────────────────────

if [[ -z "$PGPASSWORD" ]]; then
    log ERROR "POSTGRES_PASSWORD environment variable is required"
    log ERROR "متغير البيئة POSTGRES_PASSWORD مطلوب"
    exit 2
fi

export PGPASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# Health Check Functions / وظائف فحص الصحة
# ─────────────────────────────────────────────────────────────────────────────

# Check 1: PostgreSQL Connectivity / الفحص 1: اتصال PostgreSQL
check_postgres_connectivity() {
    log INFO "Checking PostgreSQL connectivity... / فحص اتصال PostgreSQL..."

    local result
    result=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "SELECT 1;" 5)

    if [[ "$result" == "1" ]]; then
        HEALTH_CHECKS[postgres_connectivity]="healthy"
        log SUCCESS "PostgreSQL is reachable / PostgreSQL متاح"
    else
        HEALTH_CHECKS[postgres_connectivity]="critical"
        update_status "critical"
        log ERROR "Cannot connect to PostgreSQL / لا يمكن الاتصال بـ PostgreSQL"
        log ERROR "Error: $result"
    fi
}

# Check 2: PgBouncer Pool Status / الفحص 2: حالة تجمع PgBouncer
check_pgbouncer_status() {
    log INFO "Checking PgBouncer status... / فحص حالة PgBouncer..."

    # Try to connect to PgBouncer admin database
    local result
    result=$(timeout 5 psql -h "$PGBOUNCER_HOST" -p "$PGBOUNCER_PORT" -U "$POSTGRES_USER" \
        -d pgbouncer -t -A -c "SHOW POOLS;" 2>&1 || echo "ERROR")

    if [[ "$result" == "ERROR" ]] || [[ -z "$result" ]]; then
        HEALTH_CHECKS[pgbouncer_status]="warning"
        update_status "warning"
        log WARNING "PgBouncer not available or not configured / PgBouncer غير متاح أو غير مكون"
        METRICS[pgbouncer_pools]=0
    else
        HEALTH_CHECKS[pgbouncer_status]="healthy"
        log SUCCESS "PgBouncer is operational / PgBouncer يعمل"

        # Count active pools / عد التجمعات النشطة
        local pool_count
        pool_count=$(echo "$result" | grep -c "^" || echo "0")
        METRICS[pgbouncer_pools]=$pool_count

        log INFO "Active pools: $pool_count / التجمعات النشطة: $pool_count"
    fi
}

# Check 3: Active Connections Count / الفحص 3: عدد الاتصالات النشطة
check_active_connections() {
    log INFO "Checking active connections... / فحص الاتصالات النشطة..."

    local query="SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
    local active_conn
    active_conn=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "$query")

    if [[ "$active_conn" =~ ^[0-9]+$ ]]; then
        METRICS[active_connections]=$active_conn

        # Get max connections / الحصول على الحد الأقصى للاتصالات
        local max_conn
        max_conn=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "SHOW max_connections;")
        METRICS[max_connections]=$max_conn

        # Calculate percentage / حساب النسبة المئوية
        local conn_pct=$((active_conn * 100 / max_conn))
        METRICS[connection_usage_pct]=$conn_pct

        if [[ $conn_pct -ge $CONN_CRITICAL_THRESHOLD ]]; then
            HEALTH_CHECKS[connection_count]="critical"
            update_status "critical"
            log ERROR "Active connections critical: $active_conn/$max_conn ($conn_pct%) / الاتصالات النشطة حرجة"
        elif [[ $conn_pct -ge $CONN_WARNING_THRESHOLD ]]; then
            HEALTH_CHECKS[connection_count]="warning"
            update_status "warning"
            log WARNING "Active connections high: $active_conn/$max_conn ($conn_pct%) / الاتصالات النشطة عالية"
        else
            HEALTH_CHECKS[connection_count]="healthy"
            log SUCCESS "Active connections normal: $active_conn/$max_conn ($conn_pct%) / الاتصالات النشطة طبيعية"
        fi
    else
        HEALTH_CHECKS[connection_count]="warning"
        update_status "warning"
        log WARNING "Could not retrieve connection count / لا يمكن الحصول على عدد الاتصالات"
        METRICS[active_connections]=0
    fi
}

# Check 4: Long-Running Queries / الفحص 4: الاستعلامات طويلة التنفيذ
check_long_running_queries() {
    log INFO "Checking for long-running queries (>${QUERY_TIMEOUT_SECONDS}s)... / فحص الاستعلامات طويلة التنفيذ..."

    local query="SELECT count(*) FROM pg_stat_activity
                 WHERE state = 'active'
                 AND query NOT LIKE '%pg_stat_activity%'
                 AND NOW() - query_start > INTERVAL '${QUERY_TIMEOUT_SECONDS} seconds';"

    local long_queries
    long_queries=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "$query")

    if [[ "$long_queries" =~ ^[0-9]+$ ]]; then
        METRICS[long_running_queries]=$long_queries

        if [[ $long_queries -gt 10 ]]; then
            HEALTH_CHECKS[long_queries]="critical"
            update_status "critical"
            log ERROR "Too many long-running queries: $long_queries / عدد كبير من الاستعلامات طويلة التنفيذ"
        elif [[ $long_queries -gt 0 ]]; then
            HEALTH_CHECKS[long_queries]="warning"
            update_status "warning"
            log WARNING "Long-running queries detected: $long_queries / تم اكتشاف استعلامات طويلة التنفيذ"
        else
            HEALTH_CHECKS[long_queries]="healthy"
            log SUCCESS "No long-running queries / لا توجد استعلامات طويلة التنفيذ"
        fi
    else
        HEALTH_CHECKS[long_queries]="warning"
        update_status "warning"
        log WARNING "Could not check long-running queries / لا يمكن فحص الاستعلامات طويلة التنفيذ"
        METRICS[long_running_queries]=0
    fi
}

# Check 5: Disk Space Usage / الفحص 5: استخدام مساحة القرص
check_disk_space() {
    log INFO "Checking disk space... / فحص مساحة القرص..."

    # Get PostgreSQL data directory / الحصول على دليل بيانات PostgreSQL
    local data_dir
    data_dir=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "SHOW data_directory;")

    if [[ "$data_dir" != "ERROR" ]] && [[ -n "$data_dir" ]]; then
        # Get disk usage percentage / الحصول على نسبة استخدام القرص
        local disk_usage
        disk_usage=$(df -h "$data_dir" 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//')

        if [[ "$disk_usage" =~ ^[0-9]+$ ]]; then
            METRICS[disk_usage_pct]=$disk_usage

            if [[ $disk_usage -ge $DISK_CRITICAL_THRESHOLD ]]; then
                HEALTH_CHECKS[disk_space]="critical"
                update_status "critical"
                log ERROR "Disk space critical: ${disk_usage}% / مساحة القرص حرجة"
            elif [[ $disk_usage -ge $DISK_WARNING_THRESHOLD ]]; then
                HEALTH_CHECKS[disk_space]="warning"
                update_status "warning"
                log WARNING "Disk space high: ${disk_usage}% / مساحة القرص عالية"
            else
                HEALTH_CHECKS[disk_space]="healthy"
                log SUCCESS "Disk space normal: ${disk_usage}% / مساحة القرص طبيعية"
            fi

            # Get total and available space / الحصول على المساحة الإجمالية والمتاحة
            local disk_info
            disk_info=$(df -h "$data_dir" 2>/dev/null | awk 'NR==2 {print $2 " " $4}')
            METRICS[disk_total]=$(echo "$disk_info" | awk '{print $1}')
            METRICS[disk_available]=$(echo "$disk_info" | awk '{print $2}')
        else
            HEALTH_CHECKS[disk_space]="warning"
            update_status "warning"
            log WARNING "Could not determine disk usage / لا يمكن تحديد استخدام القرص"
        fi
    else
        HEALTH_CHECKS[disk_space]="warning"
        update_status "warning"
        log WARNING "Could not access data directory / لا يمكن الوصول إلى دليل البيانات"
    fi
}

# Check 6: Replication Lag / الفحص 6: تأخر النسخ الاحتياطي
check_replication_lag() {
    if [[ "$CHECK_REPLICATION" == "false" ]]; then
        return
    fi

    log INFO "Checking replication lag... / فحص تأخر النسخ الاحتياطي..."

    # Check if this is a primary or replica / فحص ما إذا كان هذا أساسي أو نسخة
    local is_primary
    is_primary=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "SELECT pg_is_in_recovery();")

    if [[ "$is_primary" == "f" ]]; then
        # This is primary, check for replicas / هذا أساسي، فحص النسخ
        local replica_count
        replica_count=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" "SELECT count(*) FROM pg_stat_replication;")

        if [[ "$replica_count" =~ ^[0-9]+$ ]]; then
            METRICS[replica_count]=$replica_count

            if [[ $replica_count -eq 0 ]]; then
                HEALTH_CHECKS[replication]="warning"
                update_status "warning"
                log WARNING "No replicas connected / لا توجد نسخ متصلة"
            else
                # Check replication lag / فحص تأخر النسخ
                local max_lag
                max_lag=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" \
                    "SELECT COALESCE(MAX(EXTRACT(EPOCH FROM (NOW() - replay_lag))), 0) FROM pg_stat_replication;")

                if [[ "$max_lag" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                    METRICS[max_replication_lag_seconds]=$max_lag

                    if (( $(echo "$max_lag > 60" | bc -l) )); then
                        HEALTH_CHECKS[replication]="critical"
                        update_status "critical"
                        log ERROR "Replication lag critical: ${max_lag}s / تأخر النسخ حرج"
                    elif (( $(echo "$max_lag > 10" | bc -l) )); then
                        HEALTH_CHECKS[replication]="warning"
                        update_status "warning"
                        log WARNING "Replication lag high: ${max_lag}s / تأخر النسخ عالي"
                    else
                        HEALTH_CHECKS[replication]="healthy"
                        log SUCCESS "Replication lag normal: ${max_lag}s / تأخر النسخ طبيعي"
                    fi
                fi
            fi
        fi
    else
        # This is a replica / هذه نسخة احتياطية
        log INFO "This is a replica server / هذا خادم نسخة احتياطية"
        HEALTH_CHECKS[replication]="healthy"
        METRICS[is_replica]=true
    fi
}

# Check 7: Database Size / الفحص 7: حجم قاعدة البيانات
check_database_size() {
    log INFO "Checking database size... / فحص حجم قاعدة البيانات..."

    local db_size
    db_size=$(execute_sql "$POSTGRES_HOST" "$POSTGRES_PORT" \
        "SELECT pg_size_pretty(pg_database_size('${POSTGRES_DB}'));")

    if [[ "$db_size" != "ERROR" ]] && [[ -n "$db_size" ]]; then
        METRICS[database_size]="$db_size"
        log SUCCESS "Database size: $db_size / حجم قاعدة البيانات"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution / التنفيذ الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main() {
    log INFO "═══════════════════════════════════════════════════════════"
    log INFO "SAHOOL Database Health Check / فحص صحة قاعدة بيانات SAHOOL"
    log INFO "═══════════════════════════════════════════════════════════"
    log INFO "Timestamp: $TIMESTAMP"
    log INFO ""

    # Run all health checks / تشغيل جميع فحوصات الصحة
    check_postgres_connectivity
    check_pgbouncer_status
    check_active_connections
    check_long_running_queries
    check_disk_space
    check_replication_lag
    check_database_size

    log INFO ""
    log INFO "═══════════════════════════════════════════════════════════"

    # Generate output / إنشاء المخرجات
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        generate_json_output
    else
        generate_text_output
    fi

    exit $EXIT_CODE
}

# ─────────────────────────────────────────────────────────────────────────────
# Output Functions / وظائف المخرجات
# ─────────────────────────────────────────────────────────────────────────────

generate_json_output() {
    # Build JSON output / بناء مخرجات JSON
    local json_output='{'
    json_output+='"timestamp":"'"$TIMESTAMP"'",'
    json_output+='"status":"'"$OVERALL_STATUS"'",'
    json_output+='"exit_code":'"$EXIT_CODE"','

    # Health checks / فحوصات الصحة
    json_output+='"checks":{'
    local first=true
    for check in "${!HEALTH_CHECKS[@]}"; do
        if [[ "$first" == "false" ]]; then
            json_output+=','
        fi
        json_output+='"'"$check"'":"'"${HEALTH_CHECKS[$check]}"'"'
        first=false
    done
    json_output+='"},'

    # Metrics / المقاييس
    json_output+='"metrics":{'
    first=true
    for metric in "${!METRICS[@]}"; do
        if [[ "$first" == "false" ]]; then
            json_output+=','
        fi

        # Handle different metric types
        local value="${METRICS[$metric]}"
        if [[ "$value" =~ ^[0-9]+\.?[0-9]*$ ]] || [[ "$value" == "true" ]] || [[ "$value" == "false" ]]; then
            json_output+='"'"$metric"'":'"$value"
        else
            json_output+='"'"$metric"'":"'"$value"'"'
        fi
        first=false
    done
    json_output+='}'

    json_output+='}'

    echo "$json_output"
}

generate_text_output() {
    case $OVERALL_STATUS in
        healthy)
            log SUCCESS "Overall Status: HEALTHY ✓ / الحالة العامة: صحية ✓"
            ;;
        warning)
            log WARNING "Overall Status: WARNING ⚠ / الحالة العامة: تحذير ⚠"
            ;;
        critical)
            log ERROR "Overall Status: CRITICAL ✗ / الحالة العامة: حرجة ✗"
            ;;
    esac

    log INFO ""
    log INFO "Health Checks Summary / ملخص فحوصات الصحة:"
    log INFO "───────────────────────────────────────────────────────────"

    for check in "${!HEALTH_CHECKS[@]}"; do
        local status="${HEALTH_CHECKS[$check]}"
        local formatted_check=$(echo "$check" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')

        case $status in
            healthy)
                log SUCCESS "$formatted_check: HEALTHY"
                ;;
            warning)
                log WARNING "$formatted_check: WARNING"
                ;;
            critical)
                log ERROR "$formatted_check: CRITICAL"
                ;;
        esac
    done

    if [[ ${#METRICS[@]} -gt 0 ]]; then
        log INFO ""
        log INFO "Metrics / المقاييس:"
        log INFO "───────────────────────────────────────────────────────────"

        for metric in "${!METRICS[@]}"; do
            local value="${METRICS[$metric]}"
            local formatted_metric=$(echo "$metric" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')
            log INFO "$formatted_metric: $value"
        done
    fi

    log INFO ""
    log INFO "Exit Code: $EXIT_CODE"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main Function / تنفيذ الوظيفة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main
