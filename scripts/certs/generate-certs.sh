#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Certificate Generation Script
# Generates TLS certificates for all infrastructure services
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./generate-certs.sh [--force] [--service <service>]
#
# Options:
#   --force          Force regeneration of all certificates
#   --service <name> Generate certificates for a specific service only
#   --info <service> Display certificate information for a service
#   --verify         Verify all certificates
#   --help           Show this help message
#
# Services:
#   - postgres       PostgreSQL database
#   - pgbouncer      PostgreSQL connection pooler
#   - redis          Redis cache
#   - nats           NATS message queue
#   - kong           Kong API Gateway
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CERT_BASE_DIR="$PROJECT_ROOT/config/certs"

# Certificate validity periods
CA_VALIDITY_DAYS=3650        # 10 years
CERT_VALIDITY_DAYS=825       # ~2.25 years
WARNING_DAYS=30              # Warn if expiring within 30 days

# Certificate subject information
COUNTRY="SA"
STATE="Riyadh"
CITY="Riyadh"
ORG="SAHOOL Agricultural Platform"
ORG_UNIT="Infrastructure"

# Key size
KEY_SIZE=4096

# Services that require certificates
SERVICES=("postgres" "pgbouncer" "redis" "nats" "kong")

# ─────────────────────────────────────────────────────────────────────────────
# Colors for output
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Logging functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

log_detail() {
    echo -e "       $1"
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat << EOF
SAHOOL Certificate Generation Script

Usage:
  $0 [OPTIONS]

Options:
  --force              Force regeneration of all certificates
  --service <name>     Generate certificates for a specific service only
  --info <service>     Display certificate information for a service
  --verify             Verify all certificates
  --help               Show this help message

Services:
  postgres, pgbouncer, redis, nats, kong

Examples:
  # Generate all certificates
  $0

  # Force regenerate all certificates
  $0 --force

  # Generate certificate for Redis only
  $0 --service redis

  # Show certificate info for PostgreSQL
  $0 --info postgres

  # Verify all certificates
  $0 --verify

EOF
}

check_dependencies() {
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL is not installed. Please install it first."
        log_detail "Ubuntu/Debian: sudo apt-get install openssl"
        log_detail "CentOS/RHEL: sudo yum install openssl"
        log_detail "macOS: brew install openssl"
        exit 1
    fi
    log_info "OpenSSL version: $(openssl version)"
}

# ─────────────────────────────────────────────────────────────────────────────
# Certificate generation functions
# ─────────────────────────────────────────────────────────────────────────────

generate_ca() {
    local ca_dir="$CERT_BASE_DIR/ca"

    if [[ -f "$ca_dir/ca.crt" ]] && [[ "$FORCE" != "true" ]]; then
        log_info "CA certificate already exists, skipping generation"
        return 0
    fi

    log_step "Generating Certificate Authority (CA)"

    mkdir -p "$ca_dir"
    cd "$ca_dir"

    # Generate CA private key
    log_detail "Generating CA private key ($KEY_SIZE bits)..."
    openssl genrsa -out ca.key $KEY_SIZE 2>/dev/null

    # Generate CA certificate
    log_detail "Generating CA certificate (valid for $((CA_VALIDITY_DAYS / 365)) years)..."
    openssl req -new -x509 -days $CA_VALIDITY_DAYS -key ca.key -out ca.crt \
        -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$ORG_UNIT/CN=SAHOOL Root CA" \
        2>/dev/null

    # Set permissions
    chmod 600 ca.key
    chmod 644 ca.crt

    log_success "CA certificate generated successfully"

    cd "$PROJECT_ROOT"
}

generate_service_cert() {
    local service="$1"
    local service_dir="$CERT_BASE_DIR/$service"
    local ca_dir="$CERT_BASE_DIR/ca"

    if [[ -f "$service_dir/server.crt" ]] && [[ "$FORCE" != "true" ]]; then
        log_info "Certificate for $service already exists, skipping"
        return 0
    fi

    log_step "Generating certificate for: $service"

    mkdir -p "$service_dir"
    cd "$service_dir"

    # Copy CA certificate
    cp "$ca_dir/ca.crt" .

    # Generate service private key
    log_detail "Generating private key ($KEY_SIZE bits)..."
    openssl genrsa -out server.key $KEY_SIZE 2>/dev/null

    # Create certificate signing request (CSR)
    log_detail "Creating certificate signing request..."
    openssl req -new -key server.key -out server.csr \
        -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$ORG_UNIT/CN=sahool-$service" \
        2>/dev/null

    # Create extensions file with service-specific SANs
    create_cert_extensions "$service"

    # Sign certificate with CA
    log_detail "Signing certificate with CA (valid for $((CERT_VALIDITY_DAYS / 365)) years)..."
    openssl x509 -req -days $CERT_VALIDITY_DAYS -in server.csr \
        -CA "$ca_dir/ca.crt" -CAkey "$ca_dir/ca.key" -CAcreateserial \
        -out server.crt -extfile extensions.cnf \
        2>/dev/null

    # Clean up temporary files
    rm -f server.csr extensions.cnf "$ca_dir/ca.srl"

    # Set permissions
    chmod 600 server.key
    chmod 644 server.crt ca.crt

    log_success "Certificate for $service generated successfully"

    cd "$PROJECT_ROOT"
}

create_cert_extensions() {
    local service="$1"

    cat > extensions.cnf <<EOF
basicConstraints = CA:FALSE
nsCertType = server
nsComment = "SAHOOL $service Server Certificate"
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer:always
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
EOF

    # Add service-specific SANs
    case "$service" in
        postgres)
            cat >> extensions.cnf <<EOF
DNS.1 = postgres
DNS.2 = sahool-postgres
DNS.3 = postgresql
DNS.4 = localhost
DNS.5 = *.sahool.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
            ;;
        pgbouncer)
            cat >> extensions.cnf <<EOF
DNS.1 = pgbouncer
DNS.2 = sahool-pgbouncer
DNS.3 = localhost
DNS.4 = *.sahool.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
            ;;
        redis)
            cat >> extensions.cnf <<EOF
DNS.1 = redis
DNS.2 = sahool-redis
DNS.3 = redis-master
DNS.4 = redis-sentinel
DNS.5 = localhost
DNS.6 = *.sahool.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
            ;;
        nats)
            cat >> extensions.cnf <<EOF
DNS.1 = nats
DNS.2 = sahool-nats
DNS.3 = nats-cluster
DNS.4 = localhost
DNS.5 = *.sahool.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
            ;;
        kong)
            cat >> extensions.cnf <<EOF
DNS.1 = kong
DNS.2 = sahool-kong
DNS.3 = kong-gateway
DNS.4 = api.sahool.local
DNS.5 = localhost
DNS.6 = *.sahool.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
            ;;
    esac
}

# ─────────────────────────────────────────────────────────────────────────────
# Certificate verification and information functions
# ─────────────────────────────────────────────────────────────────────────────

verify_certificate() {
    local service="$1"
    local service_dir="$CERT_BASE_DIR/$service"
    local ca_file="$CERT_BASE_DIR/ca/ca.crt"

    if [[ ! -f "$service_dir/server.crt" ]]; then
        log_error "Certificate for $service does not exist"
        return 1
    fi

    log_step "Verifying certificate: $service"

    # Verify certificate chain
    if openssl verify -CAfile "$ca_file" "$service_dir/server.crt" 2>/dev/null | grep -q "OK"; then
        log_success "Certificate verification: OK"
    else
        log_error "Certificate verification failed"
        return 1
    fi

    # Check expiration
    local expiry_date=$(openssl x509 -in "$service_dir/server.crt" -noout -enddate | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -jf "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s 2>/dev/null)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))

    if [[ $days_until_expiry -lt 0 ]]; then
        log_error "Certificate has EXPIRED! (expired $((days_until_expiry * -1)) days ago)"
        return 1
    elif [[ $days_until_expiry -lt $WARNING_DAYS ]]; then
        log_warning "Certificate expires in $days_until_expiry days!"
    else
        log_info "Certificate expires in $days_until_expiry days"
    fi

    return 0
}

show_certificate_info() {
    local service="$1"
    local service_dir="$CERT_BASE_DIR/$service"

    if [[ ! -f "$service_dir/server.crt" ]]; then
        log_error "Certificate for $service does not exist"
        return 1
    fi

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  Certificate Information: $service"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    # Basic certificate info
    openssl x509 -in "$service_dir/server.crt" -noout -subject -issuer -dates

    echo ""
    echo "Subject Alternative Names (SANs):"
    openssl x509 -in "$service_dir/server.crt" -noout -text | grep -A 10 "Subject Alternative Name" | sed 's/^/  /'

    echo ""
    echo "Key Usage:"
    openssl x509 -in "$service_dir/server.crt" -noout -text | grep -A 3 "Key Usage" | sed 's/^/  /'

    echo ""
    echo "Certificate Fingerprint:"
    echo "  SHA256: $(openssl x509 -in "$service_dir/server.crt" -noout -fingerprint -sha256 | cut -d= -f2)"

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
}

# ─────────────────────────────────────────────────────────────────────────────
# Main script
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local force_mode=false
    local specific_service=""
    local show_info=""
    local verify_mode=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force_mode=true
                shift
                ;;
            --service)
                specific_service="$2"
                shift 2
                ;;
            --info)
                show_info="$2"
                shift 2
                ;;
            --verify)
                verify_mode=true
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

    # Export FORCE flag for use in functions
    export FORCE="$force_mode"

    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Certificate Generation"
    echo "  Platform: SAHOOL v16.0.0"
    echo "  Date: $(date)"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    # Check dependencies
    check_dependencies
    echo ""

    # Handle info mode
    if [[ -n "$show_info" ]]; then
        show_certificate_info "$show_info"
        exit 0
    fi

    # Handle verify mode
    if [[ "$verify_mode" == "true" ]]; then
        log_step "Verifying all certificates"
        echo ""
        local failed=0
        for service in "${SERVICES[@]}"; do
            verify_certificate "$service" || ((failed++))
            echo ""
        done

        if [[ $failed -eq 0 ]]; then
            log_success "All certificates verified successfully"
        else
            log_error "$failed certificate(s) failed verification"
            exit 1
        fi
        exit 0
    fi

    # Create certificate base directory
    mkdir -p "$CERT_BASE_DIR"

    # Generate CA
    generate_ca
    echo ""

    # Generate service certificates
    if [[ -n "$specific_service" ]]; then
        # Generate for specific service
        if [[ ! " ${SERVICES[@]} " =~ " ${specific_service} " ]]; then
            log_error "Invalid service: $specific_service"
            log_info "Available services: ${SERVICES[*]}"
            exit 1
        fi
        generate_service_cert "$specific_service"
    else
        # Generate for all services
        for service in "${SERVICES[@]}"; do
            generate_service_cert "$service"
            echo ""
        done
    fi

    # Verify all generated certificates
    echo ""
    log_step "Verifying generated certificates"
    echo ""

    local services_to_verify=("${SERVICES[@]}")
    if [[ -n "$specific_service" ]]; then
        services_to_verify=("$specific_service")
    fi

    for service in "${services_to_verify[@]}"; do
        verify_certificate "$service"
        echo ""
    done

    # Summary
    echo "═══════════════════════════════════════════════════════════════════════════════"
    log_success "Certificate generation completed successfully!"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    log_info "Certificate Directory: $CERT_BASE_DIR"
    log_info "CA Certificate: $CERT_BASE_DIR/ca/ca.crt"
    echo ""

    log_warning "IMPORTANT SECURITY NOTES:"
    log_detail "1. Private keys (*.key) must NEVER be committed to version control"
    log_detail "2. Protect CA private key with highest security level"
    log_detail "3. Rotate certificates before expiration ($CERT_VALIDITY_DAYS days)"
    log_detail "4. Use proper CA-signed certificates in production"
    echo ""

    log_info "Next Steps:"
    log_detail "1. Verify TLS is enabled in docker-compose.tls.yml"
    log_detail "2. Restart services to load new certificates"
    log_detail "3. Test connectivity with TLS enabled"
    log_detail "4. Schedule automatic rotation (see cert-rotation.timer)"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
}

# Run main function
main "$@"
