#!/usr/bin/env bash

# ═══════════════════════════════════════════════════════════════════════════════
# NATS NKey Environment Setup Script
# Extracts generated values and creates .env.nkey file
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NATS_DIR="${NATS_DIR:-/home/user/sahool-unified-v15-idp/config/nats}"
GENERATED_DIR="${NATS_DIR}/generated"
RESOLVER_DIR="${NATS_DIR}/resolver"
ENV_FILE="${NATS_DIR}/.env.nkey"

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

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

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if generated directory exists
    if [ ! -d "${GENERATED_DIR}" ]; then
        log_error "Generated directory not found: ${GENERATED_DIR}"
        log_info "Please run ./scripts/nats/generate-nkeys.sh first"
        exit 1
    fi

    # Check if operator JWT exists
    if [ ! -f "${GENERATED_DIR}/operator.jwt" ]; then
        log_error "Operator JWT not found: ${GENERATED_DIR}/operator.jwt"
        log_info "Please run ./scripts/nats/generate-nkeys.sh first"
        exit 1
    fi

    # Check for required tools
    if ! command -v nsc &> /dev/null; then
        log_error "nsc command not found!"
        log_info "Please install nsc from: https://github.com/nats-io/nsc"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_warning "jq command not found (optional but recommended)"
        log_info "Install with: sudo apt-get install jq (or equivalent)"
    fi

    if ! command -v openssl &> /dev/null; then
        log_error "openssl command not found!"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

extract_values() {
    log_info "Extracting generated values..."

    # Set NSC environment
    export NKEYS_PATH="${NATS_DIR}/nkeys"
    export NSC_HOME="${NATS_DIR}/nkeys"

    # Extract operator JWT
    log_info "Extracting operator JWT..."
    OPERATOR_JWT=$(cat "${GENERATED_DIR}/operator.jwt")

    # Extract operator public key
    log_info "Extracting operator public key..."
    if command -v jq &> /dev/null; then
        OPERATOR_PUBLIC_KEY=$(nsc describe operator SAHOOL -J | jq -r '.nats.signing_keys[0]')
    else
        OPERATOR_PUBLIC_KEY=$(nsc describe operator SAHOOL | grep -A1 "Signing Keys:" | tail -1 | awk '{print $1}')
    fi

    # Extract system account public key
    log_info "Extracting system account public key..."
    if command -v jq &> /dev/null; then
        SYSTEM_ACCOUNT_PUBLIC_KEY=$(nsc describe account SYS -J | jq -r '.sub')
    else
        SYSTEM_ACCOUNT_PUBLIC_KEY=$(nsc describe account SYS | grep "Subject:" | awk '{print $2}')
    fi

    # Generate JetStream encryption key
    log_info "Generating JetStream encryption key..."
    JETSTREAM_KEY=$(openssl rand -base64 32)

    # Generate cluster password
    log_info "Generating cluster password..."
    CLUSTER_PASSWORD=$(openssl rand -base64 32)

    log_success "Values extracted successfully"
}

create_env_file() {
    log_info "Creating .env.nkey file..."

    # Backup existing file if it exists
    if [ -f "${ENV_FILE}" ]; then
        log_warning "Existing .env.nkey found, creating backup..."
        cp "${ENV_FILE}" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    # Create .env.nkey file
    cat > "${ENV_FILE}" << EOF
# ═══════════════════════════════════════════════════════════════════════════════
# NATS NKey Authentication Environment Variables
# Generated on: $(date)
# ═══════════════════════════════════════════════════════════════════════════════
#
# WARNING: This file contains sensitive credentials!
# - Do NOT commit to version control
# - Protect with proper file permissions (chmod 600)
# - Rotate credentials regularly
#
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Operator Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Operator JWT
NATS_OPERATOR_JWT=${OPERATOR_JWT}

# Operator public NKey
NATS_OPERATOR_PUBLIC_KEY=${OPERATOR_PUBLIC_KEY}

# ─────────────────────────────────────────────────────────────────────────────
# System Account Configuration
# ─────────────────────────────────────────────────────────────────────────────

# System account public key
NATS_SYSTEM_ACCOUNT_PUBLIC_KEY=${SYSTEM_ACCOUNT_PUBLIC_KEY}

# ─────────────────────────────────────────────────────────────────────────────
# JetStream Encryption
# ─────────────────────────────────────────────────────────────────────────────

# JetStream encryption key (base64 encoded, 32 bytes)
NATS_JETSTREAM_KEY=${JETSTREAM_KEY}

# ─────────────────────────────────────────────────────────────────────────────
# Cluster Authentication
# ─────────────────────────────────────────────────────────────────────────────

# Cluster authentication user
NATS_CLUSTER_USER=cluster_user

# Cluster authentication password
NATS_CLUSTER_PASSWORD=${CLUSTER_PASSWORD}

# ═══════════════════════════════════════════════════════════════════════════════
# Optional Configuration (uncomment if needed)
# ═══════════════════════════════════════════════════════════════════════════════

# Gateway authentication (for multi-cluster federation)
# NATS_GATEWAY_USER=gateway_user
# NATS_GATEWAY_PASSWORD=<generate-with-openssl-rand>

# Leaf node authentication (for edge deployments)
# NATS_LEAF_NODE_NKEY=<generate-with-nsc>

# Authorization service (for dynamic authorization)
# NATS_AUTH_SERVICE_NKEY=<generate-with-nsc>

# ═══════════════════════════════════════════════════════════════════════════════
EOF

    # Set proper permissions
    chmod 600 "${ENV_FILE}"

    log_success "Environment file created: ${ENV_FILE}"
}

setup_resolver() {
    log_info "Setting up account resolver..."

    # Create resolver directory if it doesn't exist
    mkdir -p "${RESOLVER_DIR}"

    # Copy resolver JWTs
    if [ -d "${GENERATED_DIR}/resolver" ]; then
        cp "${GENERATED_DIR}/resolver"/*.jwt "${RESOLVER_DIR}/"
        log_success "Resolver JWTs copied to ${RESOLVER_DIR}"
    else
        log_warning "Resolver directory not found in generated files"
        log_info "Creating resolver JWTs manually..."

        # Create resolver JWTs from accounts
        nsc describe account SYS -J > "${RESOLVER_DIR}/SYS.jwt"
        nsc describe account APP -J > "${RESOLVER_DIR}/APP.jwt"

        log_success "Resolver JWTs created in ${RESOLVER_DIR}"
    fi

    # Set proper permissions
    chmod 644 "${RESOLVER_DIR}"/*.jwt
}

print_summary() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ NKey environment setup completed successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Created files:${NC}"
    echo "  📄 ${ENV_FILE}"
    echo "  📁 ${RESOLVER_DIR}/"
    echo ""
    echo -e "${BLUE}Credentials available at:${NC}"
    echo "  📁 ${NATS_DIR}/creds/"
    ls -1 "${NATS_DIR}/creds"/*.creds 2>/dev/null | sed 's/^/  📝 /' || echo "  (No credential files found)"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review the generated .env.nkey file"
    echo "  2. Update docker-compose.yml to use nats-nkey.conf"
    echo "  3. Start NATS server:"
    echo "     ${BLUE}docker-compose up -d nats${NC}"
    echo ""
    echo "  4. Test connection:"
    echo "     ${BLUE}nats pub -s nats://localhost:4222 \\${NC}"
    echo "     ${BLUE}  --creds ${NATS_DIR}/creds/APP_admin.creds \\${NC}"
    echo "     ${BLUE}  test \"Hello NATS\"${NC}"
    echo ""
    echo -e "${RED}Security reminders:${NC}"
    echo "  ⚠️  Never commit .env.nkey to version control"
    echo "  ⚠️  Never commit .creds files to version control"
    echo "  ⚠️  Protect files with proper permissions (600)"
    echo "  ⚠️  Rotate credentials regularly"
    echo "  ⚠️  Use secrets management in production"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  📖 docs/NATS_NKEY_SETUP.md"
    echo "  📖 config/nats/generated/SETUP_SUMMARY.md"
    echo ""
}

update_gitignore() {
    log_info "Updating .gitignore..."

    local GITIGNORE_FILE="/home/user/sahool-unified-v15-idp/.gitignore"

    # Check if .gitignore exists
    if [ ! -f "${GITIGNORE_FILE}" ]; then
        log_warning ".gitignore not found, creating..."
        touch "${GITIGNORE_FILE}"
    fi

    # Add NATS credential patterns if not already present
    if ! grep -q "config/nats/creds/" "${GITIGNORE_FILE}" 2>/dev/null; then
        echo "" >> "${GITIGNORE_FILE}"
        echo "# NATS NKey credentials and keys (never commit!)" >> "${GITIGNORE_FILE}"
        echo "config/nats/creds/" >> "${GITIGNORE_FILE}"
        echo "config/nats/nkeys/" >> "${GITIGNORE_FILE}"
        echo "config/nats/.env.nkey" >> "${GITIGNORE_FILE}"
        echo "config/nats/generated/" >> "${GITIGNORE_FILE}"
        echo "*.creds" >> "${GITIGNORE_FILE}"
        log_success "Updated .gitignore with NATS credential patterns"
    else
        log_info ".gitignore already contains NATS credential patterns"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "   NATS NKey Environment Setup"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"

    # Run setup steps
    check_prerequisites
    extract_values
    create_env_file
    setup_resolver
    update_gitignore
    print_summary
}

# Run main function
main "$@"
