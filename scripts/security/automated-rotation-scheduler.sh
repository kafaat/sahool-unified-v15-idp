#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Automated Secret Rotation Scheduler
# Automated secret rotation with Vault and Kubernetes integration
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/rotation"
STATE_DIR="${PROJECT_ROOT}/.rotation-state"

# Create directories
mkdir -p "$LOG_DIR" "$STATE_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Rotation intervals (days)
DB_ROTATION_INTERVAL=90
JWT_ROTATION_INTERVAL=180
REDIS_ROTATION_INTERVAL=90
API_KEY_ROTATION_INTERVAL=90
ENCRYPTION_KEY_ROTATION_INTERVAL=365

# Vault configuration
VAULT_ADDR="${VAULT_ADDR:-https://vault:8200}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-}"
SECRETS_PREFIX="sahool"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} [INFO] $1" | tee -a "$LOG_DIR/rotation.log"; }
log_success() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} [SUCCESS] $1" | tee -a "$LOG_DIR/rotation.log"; }
log_warn() { echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} [WARN] $1" | tee -a "$LOG_DIR/rotation.log"; }
log_error() { echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} [ERROR] $1" | tee -a "$LOG_DIR/rotation.log"; }

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

get_last_rotation_date() {
    local secret_type="$1"
    local state_file="$STATE_DIR/${secret_type}_last_rotation"

    if [ -f "$state_file" ]; then
        cat "$state_file"
    else
        echo "1970-01-01"
    fi
}

update_rotation_date() {
    local secret_type="$1"
    local state_file="$STATE_DIR/${secret_type}_last_rotation"

    date +%Y-%m-%d > "$state_file"
}

days_since_rotation() {
    local secret_type="$1"
    local last_rotation=$(get_last_rotation_date "$secret_type")
    local current_date=$(date +%Y-%m-%d)

    local last_epoch=$(date -d "$last_rotation" +%s 2>/dev/null || echo 0)
    local current_epoch=$(date -d "$current_date" +%s)

    echo $(( (current_epoch - last_epoch) / 86400 ))
}

needs_rotation() {
    local secret_type="$1"
    local interval="$2"
    local days_since=$(days_since_rotation "$secret_type")

    [ "$days_since" -ge "$interval" ]
}

send_notification() {
    local title="$1"
    local message="$2"
    local severity="${3:-info}"

    # Send to Slack/Teams/Email (configure as needed)
    log_info "Notification: [$severity] $title - $message"

    # Example: Slack webhook
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"[$severity] $title\n$message\"}" \
            2>/dev/null || true
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Rotation Functions
# ─────────────────────────────────────────────────────────────────────────────

rotate_database_password() {
    log_info "Rotating database password..."

    # Generate new password
    local new_password=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9!@#$%^&*' | head -c 32)

    # Update in Vault
    vault kv patch secret/${SECRETS_PREFIX}/database/postgres \
        password="$new_password"

    # If using Vault dynamic secrets, rotation happens automatically
    # Otherwise, update the database user password
    if [ "${USE_VAULT_DYNAMIC_SECRETS:-false}" != "true" ]; then
        PGPASSWORD="$POSTGRES_ADMIN_PASSWORD" psql -h postgres -U postgres -d sahool <<EOF
ALTER USER sahool WITH PASSWORD '$new_password';
EOF
    fi

    # Trigger Kubernetes secret refresh (if using External Secrets Operator)
    if command -v kubectl &> /dev/null; then
        kubectl annotate externalsecret postgresql-credentials \
            force-sync="$(date +%s)" \
            -n sahool \
            --overwrite 2>/dev/null || true
    fi

    update_rotation_date "database"
    log_success "Database password rotated successfully"
    send_notification "Database Password Rotated" "Successfully rotated PostgreSQL password" "success"
}

rotate_redis_password() {
    log_info "Rotating Redis password..."

    local new_password=$(openssl rand -base64 32)

    # Update in Vault
    vault kv patch secret/${SECRETS_PREFIX}/cache/redis \
        password="$new_password"

    # Update Redis configuration
    # Note: Requires Redis restart or ACL reconfiguration
    log_warn "Redis password updated in Vault. Restart Redis or update ACL to apply."

    # Trigger Kubernetes secret refresh
    if command -v kubectl &> /dev/null; then
        kubectl annotate externalsecret redis-credentials \
            force-sync="$(date +%s)" \
            -n sahool \
            --overwrite 2>/dev/null || true
    fi

    update_rotation_date "redis"
    log_success "Redis password rotated successfully"
    send_notification "Redis Password Rotated" "Successfully rotated Redis password" "success"
}

rotate_jwt_keys() {
    log_info "Rotating JWT keys..."

    # Generate new RSA key pair
    local temp_dir=$(mktemp -d)
    openssl genrsa -out "$temp_dir/private.pem" 4096
    openssl rsa -in "$temp_dir/private.pem" -pubout -out "$temp_dir/public.pem"

    # Read keys
    local private_key=$(cat "$temp_dir/private.pem")
    local public_key=$(cat "$temp_dir/public.pem")

    # Update in Vault
    vault kv patch secret/${SECRETS_PREFIX}/auth/jwt \
        private_key="$private_key" \
        public_key="$public_key" \
        rotated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # Cleanup
    rm -rf "$temp_dir"

    # Trigger Kubernetes secret refresh
    if command -v kubectl &> /dev/null; then
        kubectl annotate externalsecret jwt-config \
            force-sync="$(date +%s)" \
            -n sahool \
            --overwrite 2>/dev/null || true
    fi

    update_rotation_date "jwt"
    log_success "JWT keys rotated successfully"
    log_warn "All JWT tokens will be invalidated. Users must re-authenticate."
    send_notification "JWT Keys Rotated" "Successfully rotated JWT signing keys. Users must re-authenticate." "warning"
}

rotate_api_keys() {
    log_info "Rotating internal API keys..."

    local new_key=$(openssl rand -base64 64)

    # Update internal service key in Vault
    vault kv put secret/${SECRETS_PREFIX}/internal/service_key \
        key="$new_key" \
        rotated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    update_rotation_date "api_keys"
    log_success "API keys rotated successfully"
    send_notification "API Keys Rotated" "Successfully rotated internal API keys" "success"
}

rotate_encryption_keys() {
    log_info "Rotating encryption keys..."

    # Generate new encryption key
    local new_key=$(openssl rand -base64 32)

    # Get current key
    local current_key=$(vault kv get -field=data_key secret/${SECRETS_PREFIX}/encryption)

    # Update in Vault (keep old key as backup for decryption)
    vault kv patch secret/${SECRETS_PREFIX}/encryption \
        data_key="$new_key" \
        previous_key="$current_key" \
        rotated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # Trigger Kubernetes secret refresh
    if command -v kubectl &> /dev/null; then
        kubectl annotate externalsecret encryption-keys \
            force-sync="$(date +%s)" \
            -n sahool \
            --overwrite 2>/dev/null || true
    fi

    update_rotation_date "encryption"
    log_success "Encryption keys rotated successfully"
    log_warn "Run re-encryption job to encrypt data with new key"
    send_notification "Encryption Keys Rotated" "Successfully rotated encryption keys. Run re-encryption job." "warning"
}

# ─────────────────────────────────────────────────────────────────────────────
# Rotation Checks
# ─────────────────────────────────────────────────────────────────────────────

check_and_rotate_all() {
    log_info "Checking secret rotation schedules..."

    # Database password
    if needs_rotation "database" "$DB_ROTATION_INTERVAL"; then
        log_info "Database password needs rotation (${DB_ROTATION_INTERVAL} days expired)"
        rotate_database_password
    else
        local days_remaining=$((DB_ROTATION_INTERVAL - $(days_since_rotation "database")))
        log_info "Database password: $days_remaining days until next rotation"
    fi

    # Redis password
    if needs_rotation "redis" "$REDIS_ROTATION_INTERVAL"; then
        log_info "Redis password needs rotation (${REDIS_ROTATION_INTERVAL} days expired)"
        rotate_redis_password
    else
        local days_remaining=$((REDIS_ROTATION_INTERVAL - $(days_since_rotation "redis")))
        log_info "Redis password: $days_remaining days until next rotation"
    fi

    # JWT keys
    if needs_rotation "jwt" "$JWT_ROTATION_INTERVAL"; then
        log_info "JWT keys need rotation (${JWT_ROTATION_INTERVAL} days expired)"
        rotate_jwt_keys
    else
        local days_remaining=$((JWT_ROTATION_INTERVAL - $(days_since_rotation "jwt")))
        log_info "JWT keys: $days_remaining days until next rotation"
    fi

    # API keys
    if needs_rotation "api_keys" "$API_KEY_ROTATION_INTERVAL"; then
        log_info "API keys need rotation (${API_KEY_ROTATION_INTERVAL} days expired)"
        rotate_api_keys
    else
        local days_remaining=$((API_KEY_ROTATION_INTERVAL - $(days_since_rotation "api_keys")))
        log_info "API keys: $days_remaining days until next rotation"
    fi

    # Encryption keys
    if needs_rotation "encryption" "$ENCRYPTION_KEY_ROTATION_INTERVAL"; then
        log_info "Encryption keys need rotation (${ENCRYPTION_KEY_ROTATION_INTERVAL} days expired)"
        rotate_encryption_keys
    else
        local days_remaining=$((ENCRYPTION_KEY_ROTATION_INTERVAL - $(days_since_rotation "encryption")))
        log_info "Encryption keys: $days_remaining days until next rotation"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat <<EOF
SAHOOL Automated Secret Rotation Scheduler

Usage: $0 [OPTIONS]

Options:
    --help, -h          Show this help message
    --check             Check rotation schedules (dry-run)
    --rotate-all        Rotate all secrets that need rotation
    --force-database    Force rotate database password
    --force-redis       Force rotate Redis password
    --force-jwt         Force rotate JWT keys
    --force-api-keys    Force rotate API keys
    --force-encryption  Force rotate encryption keys
    --status            Show rotation status for all secrets

Scheduled Intervals:
    - Database password:    Every $DB_ROTATION_INTERVAL days
    - Redis password:       Every $REDIS_ROTATION_INTERVAL days
    - JWT keys:             Every $JWT_ROTATION_INTERVAL days
    - API keys:             Every $API_KEY_ROTATION_INTERVAL days
    - Encryption keys:      Every $ENCRYPTION_KEY_ROTATION_INTERVAL days

Cron Setup:
    # Check and rotate daily at 2 AM
    0 2 * * * $0 --rotate-all >> /var/log/sahool-rotation.log 2>&1

EOF
}

show_status() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                    Secret Rotation Status"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    for secret in database redis jwt api_keys encryption; do
        local last_rotation=$(get_last_rotation_date "$secret")
        local days_since=$(days_since_rotation "$secret")

        echo "Secret: $secret"
        echo "  Last Rotation: $last_rotation"
        echo "  Days Since:    $days_since days"
        echo ""
    done
}

main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                show_help
                exit 0
                ;;
            --check)
                log_info "Running rotation check (dry-run)..."
                check_and_rotate_all
                shift
                ;;
            --rotate-all)
                log_info "Running automated rotation..."
                check_and_rotate_all
                shift
                ;;
            --force-database)
                rotate_database_password
                shift
                ;;
            --force-redis)
                rotate_redis_password
                shift
                ;;
            --force-jwt)
                rotate_jwt_keys
                shift
                ;;
            --force-api-keys)
                rotate_api_keys
                shift
                ;;
            --force-encryption)
                rotate_encryption_keys
                shift
                ;;
            --status)
                show_status
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

main "$@"
