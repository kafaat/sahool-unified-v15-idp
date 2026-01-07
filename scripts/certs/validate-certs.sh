#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Certificate Validation Script
# Validates TLS certificates and checks for expiration
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./validate-certs.sh [--service <service>] [--warning-days <days>]
#
# Options:
#   --service <name>       Validate specific service only
#   --warning-days <days>  Days before expiration to warn (default: 30)
#   --json                 Output results in JSON format
#   --nagios               Output in Nagios plugin format
#   --help                 Show this help message
#
# Exit codes:
#   0 - All certificates valid
#   1 - Certificate validation error or expired
#   2 - Certificate expiring soon (within warning period)
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CERT_BASE_DIR="$PROJECT_ROOT/config/certs"

WARNING_DAYS=30
CRITICAL_DAYS=7
SERVICES=("postgres" "pgbouncer" "redis" "nats" "kong")

# Output format
OUTPUT_FORMAT="text"
SPECIFIC_SERVICE=""

# ─────────────────────────────────────────────────────────────────────────────
# Colors for output
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Logging functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} $1"
    fi
}

log_warning() {
    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        echo -e "${YELLOW}[WARNING]${NC} $1"
    fi
}

log_error() {
    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        echo -e "${RED}[ERROR]${NC} $1"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat << EOF
SAHOOL Certificate Validation Script

Usage:
  $0 [OPTIONS]

Options:
  --service <name>       Validate specific service only
  --warning-days <days>  Days before expiration to warn (default: 30)
  --json                 Output results in JSON format
  --nagios               Output in Nagios plugin format
  --help                 Show this help message

Services:
  postgres, pgbouncer, redis, nats, kong

Exit Codes:
  0 - All certificates valid
  1 - Certificate validation error or expired
  2 - Certificate expiring soon (within warning period)

Examples:
  # Validate all certificates
  $0

  # Validate Redis certificate only
  $0 --service redis

  # Set warning threshold to 60 days
  $0 --warning-days 60

  # Output as JSON for monitoring integration
  $0 --json

  # Nagios plugin mode
  $0 --nagios

EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Certificate validation functions
# ─────────────────────────────────────────────────────────────────────────────

validate_certificate() {
    local service="$1"
    local service_dir="$CERT_BASE_DIR/$service"
    local ca_file="$CERT_BASE_DIR/ca/ca.crt"

    local result="valid"
    local message=""
    local days_until_expiry=0
    local expiry_date=""

    # Check if certificate files exist
    if [[ ! -f "$service_dir/server.crt" ]]; then
        result="missing"
        message="Certificate file not found"
        echo "$service|$result|$days_until_expiry|$message"
        return 1
    fi

    if [[ ! -f "$service_dir/server.key" ]]; then
        result="missing"
        message="Private key file not found"
        echo "$service|$result|$days_until_expiry|$message"
        return 1
    fi

    if [[ ! -f "$ca_file" ]]; then
        result="missing"
        message="CA certificate not found"
        echo "$service|$result|$days_until_expiry|$message"
        return 1
    fi

    # Verify certificate chain
    if ! openssl verify -CAfile "$ca_file" "$service_dir/server.crt" &>/dev/null; then
        result="invalid"
        message="Certificate chain validation failed"
        echo "$service|$result|$days_until_expiry|$message"
        return 1
    fi

    # Check if private key matches certificate
    cert_modulus=$(openssl x509 -noout -modulus -in "$service_dir/server.crt" | openssl md5)
    key_modulus=$(openssl rsa -noout -modulus -in "$service_dir/server.key" 2>/dev/null | openssl md5)

    if [[ "$cert_modulus" != "$key_modulus" ]]; then
        result="mismatch"
        message="Private key does not match certificate"
        echo "$service|$result|$days_until_expiry|$message"
        return 1
    fi

    # Check expiration
    expiry_date=$(openssl x509 -in "$service_dir/server.crt" -noout -enddate | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -jf "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s 2>/dev/null)
    local current_epoch=$(date +%s)
    days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))

    # Determine status based on expiration
    if [[ $days_until_expiry -lt 0 ]]; then
        result="expired"
        message="Certificate expired $((days_until_expiry * -1)) days ago"
        echo "$service|$result|$days_until_expiry|$message|$expiry_date"
        return 1
    elif [[ $days_until_expiry -lt $CRITICAL_DAYS ]]; then
        result="critical"
        message="Certificate expires in $days_until_expiry days (CRITICAL)"
        echo "$service|$result|$days_until_expiry|$message|$expiry_date"
        return 2
    elif [[ $days_until_expiry -lt $WARNING_DAYS ]]; then
        result="warning"
        message="Certificate expires in $days_until_expiry days"
        echo "$service|$result|$days_until_expiry|$message|$expiry_date"
        return 2
    else
        result="valid"
        message="Certificate valid for $days_until_expiry days"
        echo "$service|$result|$days_until_expiry|$message|$expiry_date"
        return 0
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Output formatting functions
# ─────────────────────────────────────────────────────────────────────────────

output_text() {
    local results=("$@")
    local total_count=${#results[@]}
    local valid_count=0
    local warning_count=0
    local error_count=0

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Certificate Validation Report"
    echo "  Date: $(date)"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    for result in "${results[@]}"; do
        IFS='|' read -r service status days message expiry <<< "$result"

        case "$status" in
            valid)
                log_success "$service: $message"
                ((valid_count++))
                ;;
            warning)
                log_warning "$service: $message (Expires: $expiry)"
                ((warning_count++))
                ;;
            critical)
                log_error "$service: $message (Expires: $expiry)"
                ((error_count++))
                ;;
            expired|invalid|mismatch|missing)
                log_error "$service: $message"
                ((error_count++))
                ;;
        esac
    done

    echo ""
    echo "─────────────────────────────────────────────────────────────────────────────"
    echo "Summary:"
    echo "  Total Certificates:   $total_count"
    echo "  Valid:                $valid_count"
    echo "  Warnings:             $warning_count"
    echo "  Errors/Critical:      $error_count"
    echo "─────────────────────────────────────────────────────────────────────────────"
    echo ""

    if [[ $error_count -gt 0 ]]; then
        log_error "Certificate validation FAILED! $error_count certificate(s) have errors."
        return 1
    elif [[ $warning_count -gt 0 ]]; then
        log_warning "Certificate validation completed with warnings. $warning_count certificate(s) expiring soon."
        return 2
    else
        log_success "All certificates are valid!"
        return 0
    fi
}

output_json() {
    local results=("$@")

    echo "{"
    echo '  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",'
    echo '  "validation_results": ['

    local first=true
    for result in "${results[@]}"; do
        IFS='|' read -r service status days message expiry <<< "$result"

        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo ","
        fi

        echo "    {"
        echo '      "service": "'$service'",'
        echo '      "status": "'$status'",'
        echo '      "days_until_expiry": '$days','
        echo '      "message": "'$message'",'
        echo '      "expiry_date": "'$expiry'"'
        echo -n "    }"
    done

    echo ""
    echo "  ]"
    echo "}"
}

output_nagios() {
    local results=("$@")
    local critical_count=0
    local warning_count=0
    local ok_count=0
    local output_message=""

    for result in "${results[@]}"; do
        IFS='|' read -r service status days message expiry <<< "$result"

        case "$status" in
            valid)
                ((ok_count++))
                ;;
            warning)
                ((warning_count++))
                output_message="$output_message $service($days days);"
                ;;
            *)
                ((critical_count++))
                output_message="$output_message $service($message);"
                ;;
        esac
    done

    # Nagios output format: STATUS: message | performance_data
    if [[ $critical_count -gt 0 ]]; then
        echo "CRITICAL: $critical_count certificate(s) expired/invalid:$output_message | critical=$critical_count warning=$warning_count ok=$ok_count"
        return 2
    elif [[ $warning_count -gt 0 ]]; then
        echo "WARNING: $warning_count certificate(s) expiring soon:$output_message | critical=$critical_count warning=$warning_count ok=$ok_count"
        return 1
    else
        echo "OK: All $ok_count certificates valid | critical=$critical_count warning=$warning_count ok=$ok_count"
        return 0
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main script
# ─────────────────────────────────────────────────────────────────────────────

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --service)
                SPECIFIC_SERVICE="$2"
                shift 2
                ;;
            --warning-days)
                WARNING_DAYS="$2"
                shift 2
                ;;
            --json)
                OUTPUT_FORMAT="json"
                shift
                ;;
            --nagios)
                OUTPUT_FORMAT="nagios"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Determine which services to validate
    local services_to_validate=("${SERVICES[@]}")
    if [[ -n "$SPECIFIC_SERVICE" ]]; then
        if [[ ! " ${SERVICES[@]} " =~ " ${SPECIFIC_SERVICE} " ]]; then
            log_error "Invalid service: $SPECIFIC_SERVICE"
            log_info "Available services: ${SERVICES[*]}"
            exit 1
        fi
        services_to_validate=("$SPECIFIC_SERVICE")
    fi

    # Validate all certificates
    local results=()
    local return_code=0

    for service in "${services_to_validate[@]}"; do
        validation_result=$(validate_certificate "$service")
        validation_exit=$?
        results+=("$validation_result")

        # Track worst return code
        if [[ $validation_exit -gt $return_code ]]; then
            return_code=$validation_exit
        fi
    done

    # Output results in requested format
    case "$OUTPUT_FORMAT" in
        json)
            output_json "${results[@]}"
            ;;
        nagios)
            output_nagios "${results[@]}"
            exit_code=$?
            exit $exit_code
            ;;
        *)
            output_text "${results[@]}"
            exit_code=$?
            exit $exit_code
            ;;
    esac

    exit $return_code
}

# Run main function
main "$@"
