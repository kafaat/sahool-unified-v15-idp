#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL mTLS Certificate Generator
# Generates Root CA and service certificates for internal mTLS
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CERTS_DIR="${PROJECT_ROOT}/secrets/certs"
CA_DAYS=3650  # 10 years for CA
CERT_DAYS=365 # 1 year for service certs
KEY_SIZE=4096

# Services that need certificates
SERVICES=(
    "gateway"
    "field_ops"
    "ndvi_engine"
    "weather_core"
    "iot_gateway"
    "agro_rules"
    "field_chat"
    "nats"
    "postgres"
)

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

check_openssl() {
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL is required but not installed"
        exit 1
    fi
    log_info "OpenSSL version: $(openssl version)"
}

create_directories() {
    log_info "Creating certificate directories..."
    mkdir -p "$CERTS_DIR/ca"
    mkdir -p "$CERTS_DIR/services"

    # Secure permissions
    chmod 700 "$CERTS_DIR"
    chmod 700 "$CERTS_DIR/ca"
    chmod 700 "$CERTS_DIR/services"
}

generate_ca() {
    log_info "Generating Root CA..."

    local ca_key="$CERTS_DIR/ca/ca.key"
    local ca_cert="$CERTS_DIR/ca/ca.crt"

    if [[ -f "$ca_cert" ]] && [[ -f "$ca_key" ]]; then
        log_warn "CA already exists. Use --force to regenerate."
        return 0
    fi

    # Generate CA private key
    openssl genrsa -out "$ca_key" $KEY_SIZE
    chmod 600 "$ca_key"

    # Generate CA certificate
    openssl req -x509 -new -nodes \
        -key "$ca_key" \
        -sha256 \
        -days $CA_DAYS \
        -out "$ca_cert" \
        -subj "/C=SA/ST=Riyadh/L=Riyadh/O=SAHOOL/OU=Platform/CN=SAHOOL Root CA"

    log_success "Root CA generated: $ca_cert"
}

generate_service_cert() {
    local service_name="$1"
    local service_dir="$CERTS_DIR/services/$service_name"

    log_info "Generating certificate for: $service_name"

    mkdir -p "$service_dir"

    local key_file="$service_dir/$service_name.key"
    local csr_file="$service_dir/$service_name.csr"
    local cert_file="$service_dir/$service_name.crt"
    local ext_file="$service_dir/$service_name.ext"

    # Generate private key
    openssl genrsa -out "$key_file" $KEY_SIZE
    chmod 600 "$key_file"

    # Generate CSR
    openssl req -new \
        -key "$key_file" \
        -out "$csr_file" \
        -subj "/C=SA/ST=Riyadh/L=Riyadh/O=SAHOOL/OU=$service_name/CN=$service_name.sahool.local"

    # Create extensions file for SAN
    cat > "$ext_file" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $service_name
DNS.2 = $service_name.sahool.local
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF

    # Sign with CA
    openssl x509 -req \
        -in "$csr_file" \
        -CA "$CERTS_DIR/ca/ca.crt" \
        -CAkey "$CERTS_DIR/ca/ca.key" \
        -CAcreateserial \
        -out "$cert_file" \
        -days $CERT_DAYS \
        -sha256 \
        -extfile "$ext_file"

    # Cleanup CSR and ext file
    rm -f "$csr_file" "$ext_file"

    # Create combined PEM for services that need it
    cat "$cert_file" "$key_file" > "$service_dir/$service_name.pem"
    chmod 600 "$service_dir/$service_name.pem"

    log_success "Certificate generated for $service_name"
}

generate_all_service_certs() {
    for service in "${SERVICES[@]}"; do
        generate_service_cert "$service"
    done
}

create_docker_secrets() {
    log_info "Creating Docker secrets directory structure..."

    local docker_secrets="$PROJECT_ROOT/docker/secrets"
    mkdir -p "$docker_secrets"

    # Copy CA cert (public, can be shared)
    cp "$CERTS_DIR/ca/ca.crt" "$docker_secrets/ca.crt"

    # Create symlinks for each service
    for service in "${SERVICES[@]}"; do
        local service_dir="$docker_secrets/$service"
        mkdir -p "$service_dir"

        cp "$CERTS_DIR/services/$service/$service.crt" "$service_dir/tls.crt"
        cp "$CERTS_DIR/services/$service/$service.key" "$service_dir/tls.key"
        cp "$CERTS_DIR/ca/ca.crt" "$service_dir/ca.crt"
    done

    log_success "Docker secrets prepared in $docker_secrets"
}

verify_certificates() {
    log_info "Verifying certificates..."

    local ca_cert="$CERTS_DIR/ca/ca.crt"

    for service in "${SERVICES[@]}"; do
        local cert_file="$CERTS_DIR/services/$service/$service.crt"

        if openssl verify -CAfile "$ca_cert" "$cert_file" > /dev/null 2>&1; then
            log_success "$service: Certificate valid"
        else
            log_error "$service: Certificate verification failed!"
            return 1
        fi
    done
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                    Certificate Generation Complete"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "CA Certificate:     $CERTS_DIR/ca/ca.crt"
    echo "CA Key (PROTECT!):  $CERTS_DIR/ca/ca.key"
    echo ""
    echo "Service Certificates:"
    for service in "${SERVICES[@]}"; do
        echo "  - $service: $CERTS_DIR/services/$service/"
    done
    echo ""
    echo "Docker Secrets: $PROJECT_ROOT/docker/secrets/"
    echo ""
    echo "IMPORTANT:"
    echo "  1. NEVER commit ca.key or *.key files to git"
    echo "  2. Add 'secrets/' to .gitignore"
    echo "  3. Rotate certificates before expiration ($CERT_DAYS days)"
    echo ""
}

cleanup() {
    log_warn "Cleaning up existing certificates..."
    rm -rf "$CERTS_DIR"
    rm -rf "$PROJECT_ROOT/docker/secrets"
}

show_help() {
    cat <<EOF
SAHOOL mTLS Certificate Generator

Usage: $0 [OPTIONS]

Options:
    --help, -h      Show this help message
    --force, -f     Force regeneration of all certificates
    --verify, -v    Only verify existing certificates
    --service NAME  Generate certificate for a specific service only

Examples:
    $0                    # Generate all certificates
    $0 --force            # Regenerate all certificates
    $0 --verify           # Verify existing certificates
    $0 --service gateway  # Generate only gateway certificate

EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local force=false
    local verify_only=false
    local single_service=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --force|-f)
                force=true
                shift
                ;;
            --verify|-v)
                verify_only=true
                shift
                ;;
            --service)
                single_service="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "             SAHOOL mTLS Certificate Generator"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    check_openssl

    if [[ "$verify_only" == true ]]; then
        verify_certificates
        exit 0
    fi

    if [[ "$force" == true ]]; then
        cleanup
    fi

    create_directories
    generate_ca

    if [[ -n "$single_service" ]]; then
        generate_service_cert "$single_service"
    else
        generate_all_service_certs
    fi

    create_docker_secrets
    verify_certificates
    print_summary
}

main "$@"
