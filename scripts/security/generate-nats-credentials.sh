#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - NATS Secure Credentials Generator
# Generates cryptographically secure passwords for all NATS accounts
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env.nats.generated"
PASSWORD_LENGTH=32

# ═══════════════════════════════════════════════════════════════════════════════
# Functions
# ═══════════════════════════════════════════════════════════════════════════════

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  SAHOOL NATS - Secure Credentials Generator${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

generate_password() {
    # Generate cryptographically secure random password
    openssl rand -base64 "$PASSWORD_LENGTH" | tr -d "=+/" | cut -c1-"$PASSWORD_LENGTH"
}

generate_encryption_key() {
    # Generate AES-256 encryption key (base64 encoded)
    openssl rand -base64 32
}

check_dependencies() {
    print_info "Checking dependencies..."

    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed. Please install it first."
        exit 1
    fi

    print_success "All dependencies satisfied"
}

generate_credentials() {
    print_info "Generating NATS credentials..."
    echo ""

    # Generate all passwords
    NATS_USER="sahool_app"
    NATS_PASSWORD=$(generate_password)

    NATS_ADMIN_USER="nats_admin"
    NATS_ADMIN_PASSWORD=$(generate_password)

    NATS_MONITOR_USER="nats_monitor"
    NATS_MONITOR_PASSWORD=$(generate_password)

    NATS_CLUSTER_USER="nats_cluster"
    NATS_CLUSTER_PASSWORD=$(generate_password)

    NATS_SYSTEM_USER="nats_system"
    NATS_SYSTEM_PASSWORD=$(generate_password)

    NATS_JETSTREAM_KEY=$(generate_encryption_key)

    print_success "Application user credentials generated"
    print_success "Admin user credentials generated"
    print_success "Monitor user credentials generated"
    print_success "Cluster user credentials generated"
    print_success "System user credentials generated"
    print_success "JetStream encryption key generated"
}

write_env_file() {
    print_info "Writing credentials to file..."

    cat > "$ENV_FILE" << EOF
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL NATS - Generated Secure Credentials
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠️  SECURITY WARNING:
# - Store this file securely (e.g., encrypted secrets manager)
# - Never commit this file to version control
# - Rotate credentials every 90 days
# - Use different credentials for each environment (dev/staging/prod)
#
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# NATS Application User
# Purpose: Standard application service connections
# Permissions: Granular subject-level publish/subscribe
# ─────────────────────────────────────────────────────────────────────────────
NATS_USER=$NATS_USER
NATS_PASSWORD=$NATS_PASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# NATS Admin User
# Purpose: Administrative operations, stream management, debugging
# Permissions: Full access to all subjects
# ─────────────────────────────────────────────────────────────────────────────
NATS_ADMIN_USER=$NATS_ADMIN_USER
NATS_ADMIN_PASSWORD=$NATS_ADMIN_PASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# NATS Monitor User
# Purpose: Read-only monitoring and observability
# Permissions: Subscribe only (no publish)
# ─────────────────────────────────────────────────────────────────────────────
NATS_MONITOR_USER=$NATS_MONITOR_USER
NATS_MONITOR_PASSWORD=$NATS_MONITOR_PASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# NATS Cluster User
# Purpose: Inter-node cluster authentication
# Permissions: Cluster route authentication
# ─────────────────────────────────────────────────────────────────────────────
NATS_CLUSTER_USER=$NATS_CLUSTER_USER
NATS_CLUSTER_PASSWORD=$NATS_CLUSTER_PASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# NATS System User
# Purpose: Internal NATS monitoring and metrics
# Permissions: System account access
# ─────────────────────────────────────────────────────────────────────────────
NATS_SYSTEM_USER=$NATS_SYSTEM_USER
NATS_SYSTEM_PASSWORD=$NATS_SYSTEM_PASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# JetStream Encryption Key
# Purpose: Encrypt JetStream messages at rest (AES-256)
# Note: Keep this key secure - losing it means data loss!
# ─────────────────────────────────────────────────────────────────────────────
NATS_JETSTREAM_KEY=$NATS_JETSTREAM_KEY

# ═══════════════════════════════════════════════════════════════════════════════
# Usage Instructions
# ═══════════════════════════════════════════════════════════════════════════════
#
# 1. Copy these credentials to your environment file:
#    cat .env.nats.generated >> .env.production
#
# 2. Or source them directly:
#    source .env.nats.generated
#
# 3. Or use with docker-compose:
#    docker-compose --env-file .env.nats.generated up -d
#
# 4. Verify credentials work:
#    docker exec sahool-nats nats-server --signal reload
#
# ═══════════════════════════════════════════════════════════════════════════════
EOF

    chmod 600 "$ENV_FILE"
    print_success "Credentials written to: $ENV_FILE"
    print_warning "File permissions set to 600 (owner read/write only)"
}

display_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Credentials Generated Successfully!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""

    echo -e "${YELLOW}Credentials Summary:${NC}"
    echo -e "  Application User:  ${GREEN}$NATS_USER${NC}"
    echo -e "  Admin User:        ${GREEN}$NATS_ADMIN_USER${NC}"
    echo -e "  Monitor User:      ${GREEN}$NATS_MONITOR_USER${NC}"
    echo -e "  Cluster User:      ${GREEN}$NATS_CLUSTER_USER${NC}"
    echo -e "  System User:       ${GREEN}$NATS_SYSTEM_USER${NC}"
    echo ""

    echo -e "${YELLOW}Security Features:${NC}"
    echo -e "  ✓ Password Length:     ${GREEN}${PASSWORD_LENGTH} characters${NC}"
    echo -e "  ✓ Password Entropy:    ${GREEN}~192 bits${NC}"
    echo -e "  ✓ Encryption Key:      ${GREEN}AES-256 (base64)${NC}"
    echo -e "  ✓ Generation Method:   ${GREEN}OpenSSL cryptographic RNG${NC}"
    echo ""

    echo -e "${YELLOW}Output File:${NC}"
    echo -e "  Location: ${GREEN}$ENV_FILE${NC}"
    echo -e "  Permissions: ${GREEN}600 (owner only)${NC}"
    echo ""

    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Review generated credentials: ${BLUE}cat $ENV_FILE${NC}"
    echo -e "  2. Add to your environment file: ${BLUE}cat $ENV_FILE >> .env.production${NC}"
    echo -e "  3. Restart NATS service: ${BLUE}docker-compose up -d nats${NC}"
    echo -e "  4. Verify connection: ${BLUE}docker logs sahool-nats${NC}"
    echo -e "  5. ${RED}IMPORTANT:${NC} Store credentials securely (e.g., AWS Secrets Manager, HashiCorp Vault)"
    echo ""

    echo -e "${RED}⚠️  Security Warnings:${NC}"
    echo -e "  • Never commit $ENV_FILE to version control"
    echo -e "  • Add to .gitignore: ${BLUE}echo '.env.nats.generated' >> .gitignore${NC}"
    echo -e "  • Use different credentials for dev/staging/prod"
    echo -e "  • Rotate credentials every 90 days"
    echo -e "  • Backup JetStream encryption key securely"
    echo ""
}

create_gitignore_entry() {
    local gitignore_file="${PROJECT_ROOT}/.gitignore"

    if [ -f "$gitignore_file" ]; then
        if ! grep -q ".env.nats.generated" "$gitignore_file"; then
            echo ".env.nats.generated" >> "$gitignore_file"
            print_success "Added .env.nats.generated to .gitignore"
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    print_header
    check_dependencies
    generate_credentials
    write_env_file
    create_gitignore_entry
    display_summary

    echo -e "${GREEN}✓ Credential generation complete!${NC}"
    echo ""
}

# Run main function
main "$@"
