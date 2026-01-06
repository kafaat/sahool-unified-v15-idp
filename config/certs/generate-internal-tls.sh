#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Internal TLS Certificate Generator
# Generates self-signed certificates for internal service communication
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR"
CA_DAYS=3650  # 10 years for CA
CERT_DAYS=825 # ~2.25 years for service certs (Apple max)
KEY_SIZE=2048

# Services that need certificates
SERVICES=(
    "postgres"
    "pgbouncer"
    "redis"
    "nats"
    "kong"
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

    for service in "${SERVICES[@]}"; do
        mkdir -p "$CERTS_DIR/$service"
    done

    log_success "Directory structure created"
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
    openssl genrsa -out "$ca_key" 4096 2>/dev/null
    chmod 600 "$ca_key"

    # Generate CA certificate
    openssl req -x509 -new -nodes \
        -key "$ca_key" \
        -sha256 \
        -days $CA_DAYS \
        -out "$ca_cert" \
        -subj "/C=YE/ST=Sana'a/L=Sana'a/O=SAHOOL/OU=Platform Security/CN=SAHOOL Internal CA" \
        2>/dev/null

    chmod 644 "$ca_cert"
    log_success "Root CA generated: $ca_cert"
}

generate_service_cert() {
    local service_name="$1"
    local service_dir="$CERTS_DIR/$service_name"

    log_info "Generating certificate for: $service_name"

    local key_file="$service_dir/server.key"
    local csr_file="$service_dir/server.csr"
    local cert_file="$service_dir/server.crt"
    local ext_file="$service_dir/server.ext"

    # Generate private key
    openssl genrsa -out "$key_file" $KEY_SIZE 2>/dev/null
    chmod 600 "$key_file"

    # Generate CSR
    openssl req -new \
        -key "$key_file" \
        -out "$csr_file" \
        -subj "/C=YE/ST=Sana'a/L=Sana'a/O=SAHOOL/OU=Services/CN=${service_name}" \
        2>/dev/null

    # Create extensions file for SAN
    cat > "$ext_file" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${service_name}
DNS.2 = ${service_name}.sahool.local
DNS.3 = ${service_name}.default.svc.cluster.local
DNS.4 = sahool-${service_name}
DNS.5 = localhost
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
        -extfile "$ext_file" \
        2>/dev/null

    chmod 644 "$cert_file"

    # Cleanup CSR and ext file
    rm -f "$csr_file" "$ext_file"

    # Copy CA cert to service directory for convenience
    cp "$CERTS_DIR/ca/ca.crt" "$service_dir/ca.crt"

    log_success "Certificate generated for $service_name"
}

generate_all_service_certs() {
    for service in "${SERVICES[@]}"; do
        generate_service_cert "$service"
    done
}

verify_certificates() {
    log_info "Verifying certificates..."

    local ca_cert="$CERTS_DIR/ca/ca.crt"
    local all_valid=true

    for service in "${SERVICES[@]}"; do
        local cert_file="$CERTS_DIR/$service/server.crt"

        if openssl verify -CAfile "$ca_cert" "$cert_file" > /dev/null 2>&1; then
            log_success "$service: Certificate valid"
        else
            log_error "$service: Certificate verification failed!"
            all_valid=false
        fi
    done

    if [ "$all_valid" = true ]; then
        return 0
    else
        return 1
    fi
}

print_certificate_info() {
    local service="$1"
    local cert_file="$CERTS_DIR/$service/server.crt"

    echo ""
    log_info "Certificate Info for $service:"
    openssl x509 -in "$cert_file" -noout -subject -dates
    echo "  SANs:"
    openssl x509 -in "$cert_file" -noout -ext subjectAltName 2>/dev/null | grep -v "X509v3" || echo "  (none)"
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "          Internal TLS Certificate Generation Complete"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "CA Certificate:     $CERTS_DIR/ca/ca.crt"
    echo "CA Key (PROTECT!):  $CERTS_DIR/ca/ca.key"
    echo ""
    echo "Service Certificates:"
    for service in "${SERVICES[@]}"; do
        echo "  - $service:"
        echo "      cert: $CERTS_DIR/$service/server.crt"
        echo "      key:  $CERTS_DIR/$service/server.key"
        echo "      ca:   $CERTS_DIR/$service/ca.crt"
    done
    echo ""
    echo "Directory structure:"
    tree -L 2 "$CERTS_DIR" 2>/dev/null || find "$CERTS_DIR" -type f | sort
    echo ""
    echo "IMPORTANT:"
    echo "  1. NEVER commit *.key files to git (already in .gitignore)"
    echo "  2. These are self-signed certificates for INTERNAL use only"
    echo "  3. Rotate certificates before expiration ($CERT_DAYS days)"
    echo "  4. For production external traffic, use proper CA-signed certificates"
    echo ""
}

cleanup() {
    log_warn "Cleaning up existing certificates..."
    for service in "${SERVICES[@]}"; do
        rm -rf "$CERTS_DIR/$service"
    done
    rm -rf "$CERTS_DIR/ca"
}

show_help() {
    cat <<EOF
SAHOOL Internal TLS Certificate Generator

Usage: $0 [OPTIONS]

Options:
    --help, -h      Show this help message
    --force, -f     Force regeneration of all certificates
    --verify, -v    Only verify existing certificates
    --service NAME  Generate certificate for a specific service only
    --info NAME     Show certificate information for a service

Examples:
    $0                    # Generate all certificates
    $0 --force            # Regenerate all certificates
    $0 --verify           # Verify existing certificates
    $0 --service postgres # Generate only postgres certificate
    $0 --info redis       # Show redis certificate information

Services:
$(printf "    - %s\n" "${SERVICES[@]}")

EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local force=false
    local verify_only=false
    local single_service=""
    local show_info=""

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
            --info)
                show_info="$2"
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
    echo "         SAHOOL Internal TLS Certificate Generator"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    check_openssl

    if [[ -n "$show_info" ]]; then
        print_certificate_info "$show_info"
        exit 0
    fi

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

    verify_certificates
    print_summary
}

main "$@"
