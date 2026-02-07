#!/usr/bin/env bash
# =============================================================================
# SAHOOL Kong Service Health Verification Script
# =============================================================================
# Description: Verifies health of all Kong-registered services
# Description (AR): التحقق من صحة جميع الخدمات المسجلة في Kong
#
# Usage:
#   ./verify-services.sh [options]
#
# Options:
#   -h, --help          Show this help message | عرض رسالة المساعدة
#   -v, --verbose       Enable verbose output | تفعيل الإخراج المفصل
#   -c, --critical      Check only critical services | فحص الخدمات الحرجة فقط
#   -j, --json          Output as JSON | الإخراج بتنسيق JSON
#   -f, --file FILE     Specify kong.yml path | تحديد مسار ملف kong.yml
#   -o, --output FILE   Write report to file | كتابة التقرير إلى ملف
#   --category CAT      Filter by category | تصفية حسب الفئة
#   --timeout SECONDS   Request timeout (default: 5) | مهلة الطلب
#
# Examples:
#   ./verify-services.sh                    # Check all services
#   ./verify-services.sh --critical         # Check critical services only
#   ./verify-services.sh --category ai      # Check AI services
#   ./verify-services.sh --json --output report.json
#
# Author: SAHOOL Platform Team
# Version: 16.0.0
# Last Updated: 2026-02-07
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration | التكوين
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KONG_YML_PATH="${SCRIPT_DIR}/../../infrastructure/gateway/kong/kong.yml"
SERVICES_JSON_PATH="${SCRIPT_DIR}/kong-services.json"
KONG_GATEWAY_URL="${KONG_GATEWAY_URL:-http://localhost:8000}"
DEFAULT_TIMEOUT=5
VERBOSE=false
CRITICAL_ONLY=false
JSON_OUTPUT=false
OUTPUT_FILE=""
CATEGORY_FILTER=""
TIMEOUT_SECONDS=${DEFAULT_TIMEOUT}

# Colors for output | ألوان الإخراج
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters | العدادات
TOTAL_SERVICES=0
HEALTHY_COUNT=0
UNHEALTHY_COUNT=0
UNREACHABLE_COUNT=0
SKIPPED_COUNT=0

# Results array for JSON output
declare -a RESULTS=()

# =============================================================================
# Functions | الدوال
# =============================================================================

show_help() {
    cat << 'EOF'
SAHOOL Kong Service Health Verification
========================================

Script to verify the health of all Kong-registered services.
سكريبت للتحقق من صحة جميع الخدمات المسجلة في Kong.

Usage / الاستخدام:
  ./verify-services.sh [options]

Options / الخيارات:
  -h, --help          Show this help message
                      عرض رسالة المساعدة
  -v, --verbose       Enable verbose output
                      تفعيل الإخراج المفصل
  -c, --critical      Check only critical services
                      فحص الخدمات الحرجة فقط
  -j, --json          Output as JSON
                      الإخراج بتنسيق JSON
  -f, --file FILE     Specify kong.yml path
                      تحديد مسار ملف kong.yml
  -o, --output FILE   Write report to file
                      كتابة التقرير إلى ملف
  --category CAT      Filter by category (core, ai, terrain, etc.)
                      تصفية حسب الفئة
  --timeout SECONDS   Request timeout in seconds (default: 5)
                      مهلة الطلب بالثواني

Categories / الفئات:
  core          Core platform services | الخدمات الأساسية
  ai            AI and ML services | خدمات الذكاء الاصطناعي
  analysis      Data analysis services | خدمات التحليل
  bridge        Bridge/transformation services | خدمات التحويل
  terrain       Terrain analysis services | خدمات التضاريس
  edge          Edge computing services | خدمات الحوسبة الطرفية
  iot           IoT services | خدمات إنترنت الأشياء
  communication Real-time communication | خدمات الاتصال
  marketplace   Marketplace services | خدمات السوق
  compliance    Compliance services | خدمات الامتثال

Examples / أمثلة:
  ./verify-services.sh
  ./verify-services.sh --critical
  ./verify-services.sh --category ai --verbose
  ./verify-services.sh --json --output report.json

EOF
    exit 0
}

log_info() {
    if [[ "$JSON_OUTPUT" == "false" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    if [[ "$JSON_OUTPUT" == "false" ]]; then
        echo -e "${GREEN}[PASS]${NC} $1"
    fi
}

log_warning() {
    if [[ "$JSON_OUTPUT" == "false" ]]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
    fi
}

log_error() {
    if [[ "$JSON_OUTPUT" == "false" ]]; then
        echo -e "${RED}[FAIL]${NC} $1"
    fi
}

log_verbose() {
    if [[ "$VERBOSE" == "true" && "$JSON_OUTPUT" == "false" ]]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

# Check if required tools are installed
check_dependencies() {
    local missing_deps=()

    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi

    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_error "Please install them using: apt-get install ${missing_deps[*]}"
        exit 1
    fi
}

# Load services from JSON registry
load_services_from_json() {
    if [[ ! -f "$SERVICES_JSON_PATH" ]]; then
        log_error "Service registry not found: $SERVICES_JSON_PATH"
        log_error "لم يتم العثور على سجل الخدمات"
        exit 1
    fi

    log_verbose "Loading services from: $SERVICES_JSON_PATH"
}

# Check single service health
check_service_health() {
    local name="$1"
    local host="$2"
    local port="$3"
    local health_endpoint="$4"
    local expected_status="$5"
    local timeout_ms="$6"
    local category="$7"
    local critical="$8"
    local name_ar="${9:-}"

    local url="http://${host}:${port}${health_endpoint}"
    local start_time end_time response_time status_code response_body

    log_verbose "Checking: $name ($url)"

    start_time=$(date +%s%3N)

    # Make HTTP request with timeout
    local curl_timeout=$((timeout_ms / 1000))
    if [[ $curl_timeout -lt 1 ]]; then
        curl_timeout=1
    fi

    set +e
    response=$(curl -s -w "\n%{http_code}" \
        --connect-timeout "$curl_timeout" \
        --max-time "$((curl_timeout * 2))" \
        "$url" 2>/dev/null)
    local curl_exit_code=$?
    set -e

    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))

    if [[ $curl_exit_code -ne 0 ]]; then
        # Service unreachable
        status="unreachable"
        status_code="N/A"
        response_body=""
        ((UNREACHABLE_COUNT++))
        log_error "$name: UNREACHABLE (${host}:${port}) | غير قابل للوصول"
    else
        status_code=$(echo "$response" | tail -n1)
        response_body=$(echo "$response" | head -n -1)

        if [[ "$status_code" == "$expected_status" ]]; then
            status="healthy"
            ((HEALTHY_COUNT++))
            log_success "$name: HEALTHY (${status_code}) [${response_time}ms] | صحي"
        else
            status="unhealthy"
            ((UNHEALTHY_COUNT++))
            log_error "$name: UNHEALTHY (expected ${expected_status}, got ${status_code}) | غير صحي"
        fi
    fi

    # Build result object
    local result
    result=$(jq -n \
        --arg name "$name" \
        --arg name_ar "$name_ar" \
        --arg host "$host" \
        --argjson port "$port" \
        --arg endpoint "$health_endpoint" \
        --arg status "$status" \
        --arg status_code "$status_code" \
        --argjson response_time "$response_time" \
        --arg category "$category" \
        --argjson critical "$critical" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            name: $name,
            name_ar: $name_ar,
            host: $host,
            port: $port,
            health_endpoint: $endpoint,
            status: $status,
            status_code: $status_code,
            response_time_ms: $response_time,
            category: $category,
            critical: $critical,
            timestamp: $timestamp
        }')

    RESULTS+=("$result")
}

# Parse services from kong.yml
parse_kong_yml() {
    if [[ ! -f "$KONG_YML_PATH" ]]; then
        log_warning "kong.yml not found at: $KONG_YML_PATH"
        log_warning "Using service registry instead"
        return 1
    fi

    log_info "Parsing kong.yml: $KONG_YML_PATH"
    return 0
}

# Generate summary report
generate_summary() {
    local total=$((HEALTHY_COUNT + UNHEALTHY_COUNT + UNREACHABLE_COUNT + SKIPPED_COUNT))
    local health_percentage=0

    if [[ $total -gt 0 ]]; then
        health_percentage=$((HEALTHY_COUNT * 100 / total))
    fi

    if [[ "$JSON_OUTPUT" == "true" ]]; then
        # JSON summary
        local summary
        summary=$(jq -n \
            --argjson total "$total" \
            --argjson healthy "$HEALTHY_COUNT" \
            --argjson unhealthy "$UNHEALTHY_COUNT" \
            --argjson unreachable "$UNREACHABLE_COUNT" \
            --argjson skipped "$SKIPPED_COUNT" \
            --argjson health_percentage "$health_percentage" \
            --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            --arg platform "SAHOOL" \
            --arg version "16.0.0" \
            '{
                summary: {
                    platform: $platform,
                    version: $version,
                    timestamp: $timestamp,
                    total_services: $total,
                    healthy: $healthy,
                    unhealthy: $unhealthy,
                    unreachable: $unreachable,
                    skipped: $skipped,
                    health_percentage: $health_percentage
                }
            }')

        # Combine results with summary
        local all_results
        all_results=$(printf '%s\n' "${RESULTS[@]}" | jq -s '.')

        local full_report
        full_report=$(echo "$summary" | jq --argjson services "$all_results" '. + {services: $services}')

        if [[ -n "$OUTPUT_FILE" ]]; then
            echo "$full_report" > "$OUTPUT_FILE"
            log_info "Report written to: $OUTPUT_FILE" >&2
        else
            echo "$full_report"
        fi
    else
        # Text summary
        echo ""
        echo "=============================================================================="
        echo "SAHOOL Kong Service Health Report | تقرير صحة خدمات Kong"
        echo "=============================================================================="
        echo ""
        echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "Platform Version: 16.0.0"
        echo ""
        echo "------------------------------------------------------------------------------"
        echo "Summary | ملخص"
        echo "------------------------------------------------------------------------------"
        echo ""
        printf "  Total Services Checked:   %d\n" "$total"
        printf "  Healthy:                  %d ${GREEN}OK${NC}\n" "$HEALTHY_COUNT"
        printf "  Unhealthy:                %d ${RED}FAIL${NC}\n" "$UNHEALTHY_COUNT"
        printf "  Unreachable:              %d ${YELLOW}WARN${NC}\n" "$UNREACHABLE_COUNT"
        printf "  Skipped:                  %d\n" "$SKIPPED_COUNT"
        echo ""
        printf "  Health Percentage:        %d%%\n" "$health_percentage"
        echo ""
        echo "------------------------------------------------------------------------------"

        if [[ $UNHEALTHY_COUNT -gt 0 || $UNREACHABLE_COUNT -gt 0 ]]; then
            echo ""
            echo "Issues Found | المشاكل المكتشفة:"
            echo ""
            for result in "${RESULTS[@]}"; do
                local status name
                status=$(echo "$result" | jq -r '.status')
                name=$(echo "$result" | jq -r '.name')
                if [[ "$status" != "healthy" ]]; then
                    local host port
                    host=$(echo "$result" | jq -r '.host')
                    port=$(echo "$result" | jq -r '.port')
                    echo "  - $name (${host}:${port}): $status"
                fi
            done
            echo ""
        fi

        echo "=============================================================================="

        if [[ -n "$OUTPUT_FILE" ]]; then
            # Write text report to file
            {
                echo "SAHOOL Kong Service Health Report"
                echo "================================="
                echo ""
                echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
                echo "Total: $total, Healthy: $HEALTHY_COUNT, Unhealthy: $UNHEALTHY_COUNT, Unreachable: $UNREACHABLE_COUNT"
                echo ""
                echo "Details:"
                for result in "${RESULTS[@]}"; do
                    local name status host port response_time
                    name=$(echo "$result" | jq -r '.name')
                    status=$(echo "$result" | jq -r '.status')
                    host=$(echo "$result" | jq -r '.host')
                    port=$(echo "$result" | jq -r '.port')
                    response_time=$(echo "$result" | jq -r '.response_time_ms')
                    echo "  $name: $status (${host}:${port}) [${response_time}ms]"
                done
            } > "$OUTPUT_FILE"
            log_info "Report written to: $OUTPUT_FILE"
        fi
    fi
}

# Main verification logic
run_verification() {
    log_info "Starting Kong service health verification..."
    log_info "Kong Gateway URL: $KONG_GATEWAY_URL"
    echo ""

    # Load services from JSON
    load_services_from_json

    # Read services and check health
    local services
    services=$(jq -r '.services[]' "$SERVICES_JSON_PATH")

    local service_count
    service_count=$(jq '.services | length' "$SERVICES_JSON_PATH")
    log_info "Found $service_count services in registry"
    echo ""

    # Iterate through services
    while IFS= read -r service; do
        local name host port health_endpoint expected_status timeout_ms category critical name_ar deprecated

        name=$(echo "$service" | jq -r '.name')
        name_ar=$(echo "$service" | jq -r '.name_ar // ""')
        host=$(echo "$service" | jq -r '.host')
        port=$(echo "$service" | jq -r '.port')
        health_endpoint=$(echo "$service" | jq -r '.health_endpoint')
        expected_status=$(echo "$service" | jq -r '.expected_status')
        timeout_ms=$(echo "$service" | jq -r '.timeout_ms')
        category=$(echo "$service" | jq -r '.category')
        critical=$(echo "$service" | jq -r '.critical')
        deprecated=$(echo "$service" | jq -r '.deprecated // false')

        # Apply filters
        if [[ "$CRITICAL_ONLY" == "true" && "$critical" != "true" ]]; then
            ((SKIPPED_COUNT++))
            log_verbose "Skipping non-critical service: $name"
            continue
        fi

        if [[ -n "$CATEGORY_FILTER" && "$category" != "$CATEGORY_FILTER" ]]; then
            ((SKIPPED_COUNT++))
            log_verbose "Skipping service (category filter): $name"
            continue
        fi

        ((TOTAL_SERVICES++))
        check_service_health "$name" "$host" "$port" "$health_endpoint" "$expected_status" "$timeout_ms" "$category" "$critical" "$name_ar"

    done < <(jq -c '.services[]' "$SERVICES_JSON_PATH")

    # Generate summary report
    generate_summary

    # Return exit code based on results
    if [[ $UNHEALTHY_COUNT -gt 0 || $UNREACHABLE_COUNT -gt 0 ]]; then
        return 1
    fi
    return 0
}

# =============================================================================
# Parse Arguments | تحليل المعطيات
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--critical)
            CRITICAL_ONLY=true
            shift
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        -f|--file)
            KONG_YML_PATH="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --category)
            CATEGORY_FILTER="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT_SECONDS="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Main Execution | التنفيذ الرئيسي
# =============================================================================

main() {
    # Check dependencies
    check_dependencies

    # Print header (if not JSON mode)
    if [[ "$JSON_OUTPUT" == "false" ]]; then
        echo ""
        echo "=============================================================================="
        echo "  SAHOOL Kong Service Health Verification"
        echo "  منصة سهول - التحقق من صحة خدمات Kong"
        echo "=============================================================================="
        echo ""
    fi

    # Run verification
    if run_verification; then
        if [[ "$JSON_OUTPUT" == "false" ]]; then
            echo ""
            log_success "All services are healthy! | جميع الخدمات صحية!"
        fi
        exit 0
    else
        if [[ "$JSON_OUTPUT" == "false" ]]; then
            echo ""
            log_error "Some services have issues. Please check the report above."
            log_error "بعض الخدمات بها مشاكل. يرجى مراجعة التقرير أعلاه."
        fi
        exit 1
    fi
}

# Run main function
main
