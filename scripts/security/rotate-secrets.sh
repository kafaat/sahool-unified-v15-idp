#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Secret Rotation Script
# Rotates JWT keys, database passwords, and service secrets
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SECRETS_DIR="${PROJECT_ROOT}/secrets"

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

generate_random_password() {
    local length="${1:-32}"
    openssl rand -base64 48 | tr -dc 'a-zA-Z0-9!@#$%^&*' | head -c "$length"
}

generate_jwt_keys() {
    log_info "Generating new JWT RSA key pair..."

    local jwt_dir="$SECRETS_DIR/jwt"
    mkdir -p "$jwt_dir"

    # Backup old keys
    if [[ -f "$jwt_dir/private.pem" ]]; then
        mv "$jwt_dir/private.pem" "$jwt_dir/private.pem.bak.$(date +%Y%m%d%H%M%S)"
        mv "$jwt_dir/public.pem" "$jwt_dir/public.pem.bak.$(date +%Y%m%d%H%M%S)"
    fi

    # Generate new keys
    openssl genrsa -out "$jwt_dir/private.pem" 4096
    openssl rsa -in "$jwt_dir/private.pem" -pubout -out "$jwt_dir/public.pem"

    chmod 600 "$jwt_dir/private.pem"
    chmod 644 "$jwt_dir/public.pem"

    log_success "JWT keys generated in $jwt_dir"
}

generate_database_passwords() {
    log_info "Generating new database passwords..."

    local db_dir="$SECRETS_DIR/database"
    mkdir -p "$db_dir"

    # Generate passwords
    echo "$(generate_random_password 32)" > "$db_dir/postgres_password"
    echo "$(generate_random_password 32)" > "$db_dir/postgres_replication_password"

    chmod 600 "$db_dir"/*

    log_success "Database passwords generated in $db_dir"
}

generate_nats_credentials() {
    log_info "Generating NATS credentials..."

    local nats_dir="$SECRETS_DIR/nats"
    mkdir -p "$nats_dir"

    # Generate system account key
    echo "$(generate_random_password 48)" > "$nats_dir/sys_account_key"

    # Generate operator key (for JWT auth mode)
    if command -v nsc &> /dev/null; then
        log_info "NSC found, generating operator..."
        # Advanced NATS security setup would go here
    fi

    chmod 600 "$nats_dir"/*

    log_success "NATS credentials generated in $nats_dir"
}

generate_api_keys() {
    log_info "Generating API keys..."

    local api_dir="$SECRETS_DIR/api_keys"
    mkdir -p "$api_dir"

    # Internal service-to-service API keys
    echo "$(generate_random_password 64)" > "$api_dir/internal_service_key"

    # External integration keys (example)
    echo "$(generate_random_password 48)" > "$api_dir/weather_api_key"
    echo "$(generate_random_password 48)" > "$api_dir/satellite_api_key"

    chmod 600 "$api_dir"/*

    log_success "API keys generated in $api_dir"
}

generate_encryption_keys() {
    log_info "Generating encryption keys..."

    local enc_dir="$SECRETS_DIR/encryption"
    mkdir -p "$enc_dir"

    # AES-256 key for data at rest
    openssl rand -base64 32 > "$enc_dir/data_encryption_key"

    # Backup encryption key
    openssl rand -base64 32 > "$enc_dir/backup_encryption_key"

    chmod 600 "$enc_dir"/*

    log_success "Encryption keys generated in $enc_dir"
}

create_env_template() {
    log_info "Creating .env.template..."

    cat > "$PROJECT_ROOT/.env.template" <<EOF
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Environment Variables
# Copy to .env and fill in values from secrets/
# NEVER commit .env to git!
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# JWT Configuration
# ─────────────────────────────────────────────────────────────────────────────
JWT_ALGORITHM=RS256
JWT_ISSUER=sahool-idp
JWT_AUDIENCE=sahool-platform
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7
# Load from secrets/jwt/
JWT_PRIVATE_KEY_FILE=/run/secrets/jwt_private_key
JWT_PUBLIC_KEY_FILE=/run/secrets/jwt_public_key

# ─────────────────────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────────────────────
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=sahool
POSTGRES_USER=sahool
# Load from secrets/database/
POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password

# ─────────────────────────────────────────────────────────────────────────────
# NATS
# ─────────────────────────────────────────────────────────────────────────────
NATS_URL=nats://nats:4222
# Load from secrets/nats/
NATS_CREDENTIALS_FILE=/run/secrets/nats_credentials

# ─────────────────────────────────────────────────────────────────────────────
# mTLS
# ─────────────────────────────────────────────────────────────────────────────
SSL_CERT_FILE=/run/secrets/tls.crt
SSL_KEY_FILE=/run/secrets/tls.key
SSL_CA_FILE=/run/secrets/ca.crt

# ─────────────────────────────────────────────────────────────────────────────
# Encryption
# ─────────────────────────────────────────────────────────────────────────────
DATA_ENCRYPTION_KEY_FILE=/run/secrets/data_encryption_key

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
LOG_FORMAT=json

# ─────────────────────────────────────────────────────────────────────────────
# Services (Internal URLs)
# ─────────────────────────────────────────────────────────────────────────────
FIELD_OPS_URL=http://field_ops:8080
NDVI_ENGINE_URL=http://ndvi_engine:8097
WEATHER_CORE_URL=http://weather_core:8098
FIELD_CHAT_URL=http://field_chat:8099
IOT_GATEWAY_URL=http://iot_gateway:8094

EOF

    log_success ".env.template created"
}

update_gitignore() {
    log_info "Updating .gitignore..."

    local gitignore="$PROJECT_ROOT/.gitignore"

    # Patterns to add
    local patterns=(
        "# Secrets - NEVER commit these"
        "secrets/"
        ".env"
        ".env.local"
        ".env.*.local"
        "*.pem"
        "*.key"
        "*.p12"
        "*.pfx"
        "docker/secrets/"
        "*.credentials"
    )

    for pattern in "${patterns[@]}"; do
        if ! grep -qF "$pattern" "$gitignore" 2>/dev/null; then
            echo "$pattern" >> "$gitignore"
        fi
    done

    log_success ".gitignore updated"
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                    Secret Rotation Complete"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Generated secrets:"
    echo "  - JWT Keys:           $SECRETS_DIR/jwt/"
    echo "  - Database:           $SECRETS_DIR/database/"
    echo "  - NATS:               $SECRETS_DIR/nats/"
    echo "  - API Keys:           $SECRETS_DIR/api_keys/"
    echo "  - Encryption:         $SECRETS_DIR/encryption/"
    echo ""
    echo "IMPORTANT:"
    echo "  1. Update .env with new secret paths"
    echo "  2. Restart all services to apply new secrets"
    echo "  3. Invalidate existing JWT tokens (users must re-login)"
    echo "  4. Update database connection strings"
    echo ""
}

show_help() {
    cat <<EOF
SAHOOL Secret Rotation Script

Usage: $0 [OPTIONS]

Options:
    --help, -h      Show this help message
    --all           Rotate all secrets
    --jwt           Rotate JWT keys only
    --database      Rotate database passwords only
    --nats          Rotate NATS credentials only
    --api-keys      Rotate API keys only
    --encryption    Rotate encryption keys only

Examples:
    $0 --all        # Rotate all secrets
    $0 --jwt        # Rotate only JWT keys

EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local rotate_all=false
    local rotate_jwt=false
    local rotate_db=false
    local rotate_nats=false
    local rotate_api=false
    local rotate_enc=false

    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --all)
                rotate_all=true
                shift
                ;;
            --jwt)
                rotate_jwt=true
                shift
                ;;
            --database)
                rotate_db=true
                shift
                ;;
            --nats)
                rotate_nats=true
                shift
                ;;
            --api-keys)
                rotate_api=true
                shift
                ;;
            --encryption)
                rotate_enc=true
                shift
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
    echo "                  SAHOOL Secret Rotation"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"

    if [[ "$rotate_all" == true ]] || [[ "$rotate_jwt" == true ]]; then
        generate_jwt_keys
    fi

    if [[ "$rotate_all" == true ]] || [[ "$rotate_db" == true ]]; then
        generate_database_passwords
    fi

    if [[ "$rotate_all" == true ]] || [[ "$rotate_nats" == true ]]; then
        generate_nats_credentials
    fi

    if [[ "$rotate_all" == true ]] || [[ "$rotate_api" == true ]]; then
        generate_api_keys
    fi

    if [[ "$rotate_all" == true ]] || [[ "$rotate_enc" == true ]]; then
        generate_encryption_keys
    fi

    create_env_template
    update_gitignore
    print_summary
}

main "$@"
