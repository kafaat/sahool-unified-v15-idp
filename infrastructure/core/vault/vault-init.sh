#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Vault Production Initialization Script
# Initializes HashiCorp Vault with SAHOOL secrets structure
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

VAULT_ADDR="${VAULT_ADDR:-https://vault:8200}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-}"
SECRETS_PREFIX="sahool"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Colors
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

check_vault_connectivity() {
    log_info "Checking Vault connectivity..."
    if ! vault status &>/dev/null; then
        log_error "Cannot connect to Vault at $VAULT_ADDR"
        log_info "Make sure Vault is running and VAULT_TOKEN is set"
        exit 1
    fi
    log_success "Connected to Vault"
}

enable_secrets_engines() {
    log_info "Enabling secrets engines..."

    # Enable KV v2 secrets engine
    if ! vault secrets list | grep -q "^secret/"; then
        vault secrets enable -version=2 -path=secret kv
        log_success "KV v2 secrets engine enabled at 'secret/'"
    else
        log_info "KV v2 secrets engine already enabled"
    fi

    # Enable database secrets engine (for dynamic credentials)
    if ! vault secrets list | grep -q "^database/"; then
        vault secrets enable database
        log_success "Database secrets engine enabled"
    else
        log_info "Database secrets engine already enabled"
    fi

    # Enable PKI for certificate management
    if ! vault secrets list | grep -q "^pki/"; then
        vault secrets enable pki
        vault secrets tune -max-lease-ttl=87600h pki  # 10 years
        log_success "PKI secrets engine enabled"
    else
        log_info "PKI secrets engine already enabled"
    fi
}

configure_database_secrets() {
    log_info "Configuring database dynamic secrets..."

    # Configure PostgreSQL connection
    vault write database/config/postgresql \
        plugin_name=postgresql-database-plugin \
        allowed_roles="sahool-app,sahool-readonly" \
        connection_url="postgresql://{{username}}:{{password}}@postgres:5432/sahool?sslmode=require" \
        username="vault_admin" \
        password="${POSTGRES_VAULT_ADMIN_PASSWORD:-changeme}"

    # Create application role (read-write)
    vault write database/roles/sahool-app \
        db_name=postgresql \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE sahool_app;" \
        default_ttl="24h" \
        max_ttl="168h"

    # Create read-only role
    vault write database/roles/sahool-readonly \
        db_name=postgresql \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE sahool_readonly;" \
        default_ttl="24h" \
        max_ttl="168h"

    log_success "Database dynamic secrets configured"
}

create_static_secrets() {
    log_info "Creating static secrets structure..."

    # Database (for services that don't support dynamic credentials yet)
    vault kv put secret/${SECRETS_PREFIX}/database/postgres \
        username="sahool" \
        password="${POSTGRES_PASSWORD:-changeme}" \
        host="postgres" \
        port="5432" \
        database="sahool" \
        ssl_mode="require"

    # Redis
    vault kv put secret/${SECRETS_PREFIX}/cache/redis \
        password="${REDIS_PASSWORD:-changeme}" \
        host="redis" \
        port="6379" \
        db="0" \
        ssl_enabled="true"

    # NATS
    vault kv put secret/${SECRETS_PREFIX}/messaging/nats \
        user="sahool_app" \
        password="${NATS_PASSWORD:-changeme}" \
        url="nats://nats:4222"

    # JWT Configuration
    vault kv put secret/${SECRETS_PREFIX}/auth/jwt \
        secret_key="${JWT_SECRET_KEY:-changeme}" \
        algorithm="HS256" \
        access_token_expire_minutes="60" \
        refresh_token_expire_days="7" \
        issuer="sahool-platform" \
        audience="sahool-api"

    # Encryption keys
    vault kv put secret/${SECRETS_PREFIX}/encryption \
        data_key="${ENCRYPTION_KEY:-$(openssl rand -base64 32)}" \
        backup_key="$(openssl rand -base64 32)"

    # External API keys (placeholders - replace in production)
    vault kv put secret/${SECRETS_PREFIX}/external/openweather \
        api_key="${OPENWEATHER_API_KEY:-placeholder}"

    vault kv put secret/${SECRETS_PREFIX}/external/sentinel \
        client_id="${SENTINEL_HUB_CLIENT_ID:-placeholder}" \
        client_secret="${SENTINEL_HUB_CLIENT_SECRET:-placeholder}"

    vault kv put secret/${SECRETS_PREFIX}/external/stripe \
        api_key="${STRIPE_API_KEY:-placeholder}" \
        webhook_secret="${STRIPE_WEBHOOK_SECRET:-placeholder}"

    # MinIO
    vault kv put secret/${SECRETS_PREFIX}/storage/minio \
        access_key="${MINIO_ROOT_USER:-changeme}" \
        secret_key="${MINIO_ROOT_PASSWORD:-changeme}" \
        endpoint="https://minio:9000"

    log_success "Static secrets created"
}

configure_auth_methods() {
    log_info "Configuring authentication methods..."

    # Enable AppRole (for services)
    if ! vault auth list | grep -q "^approle/"; then
        vault auth enable approle
        log_success "AppRole auth method enabled"
    else
        log_info "AppRole auth method already enabled"
    fi

    # Create policy for SAHOOL application
    vault policy write sahool-app - <<EOF
# Allow reading all SAHOOL secrets
path "secret/data/${SECRETS_PREFIX}/*" {
  capabilities = ["read", "list"]
}

# Allow reading database dynamic credentials
path "database/creds/sahool-app" {
  capabilities = ["read"]
}

# Allow reading own token
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Allow renewing own token
path "auth/token/renew-self" {
  capabilities = ["update"]
}
EOF

    # Create AppRole for application
    vault write auth/approle/role/sahool-app \
        token_policies="sahool-app" \
        token_ttl=24h \
        token_max_ttl=168h \
        secret_id_ttl=0 \
        secret_id_num_uses=0

    log_success "Authentication methods configured"
}

configure_kubernetes_auth() {
    log_info "Configuring Kubernetes authentication..."

    # Enable Kubernetes auth
    if ! vault auth list | grep -q "^kubernetes/"; then
        vault auth enable kubernetes

        # Configure Kubernetes auth
        vault write auth/kubernetes/config \
            kubernetes_host="https://kubernetes.default.svc:443" \
            kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
            token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token

        # Create role for SAHOOL pods
        vault write auth/kubernetes/role/sahool \
            bound_service_account_names=sahool \
            bound_service_account_namespaces=sahool,sahool-prod,sahool-staging \
            policies=sahool-app \
            ttl=24h

        log_success "Kubernetes auth configured"
    else
        log_info "Kubernetes auth already enabled"
    fi
}

enable_audit_logging() {
    log_info "Enabling audit logging..."

    # Enable file audit device
    if ! vault audit list | grep -q "file/"; then
        vault audit enable file \
            file_path=/vault/logs/audit.log \
            log_raw=false
        log_success "Audit logging enabled"
    else
        log_info "Audit logging already enabled"
    fi
}

configure_pki() {
    log_info "Configuring PKI for internal certificates..."

    # Generate root CA
    vault write -field=certificate pki/root/generate/internal \
        common_name="SAHOOL Internal Root CA" \
        ttl=87600h > /vault/certs/ca.crt

    # Configure CA and CRL URLs
    vault write pki/config/urls \
        issuing_certificates="https://vault:8200/v1/pki/ca" \
        crl_distribution_points="https://vault:8200/v1/pki/crl"

    # Create role for service certificates
    vault write pki/roles/sahool-services \
        allowed_domains="sahool.local,sahool.com,*.sahool.local,*.sahool.com" \
        allow_subdomains=true \
        max_ttl="720h" \
        key_type="rsa" \
        key_bits="2048"

    log_success "PKI configured"
}

print_credentials() {
    log_info "Generating AppRole credentials..."

    ROLE_ID=$(vault read -field=role_id auth/approle/role/sahool-app/role-id)
    SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/sahool-app/secret-id)

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                    SAHOOL Vault Initialization Complete"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "AppRole Credentials (save these securely!):"
    echo ""
    echo "VAULT_ROLE_ID=${ROLE_ID}"
    echo "VAULT_SECRET_ID=${SECRET_ID}"
    echo ""
    echo "Add these to your .env file or Kubernetes secrets:"
    echo ""
    echo "  kubectl create secret generic sahool-vault-creds \\"
    echo "    --from-literal=role-id=${ROLE_ID} \\"
    echo "    --from-literal=secret-id=${SECRET_ID} \\"
    echo "    -n sahool"
    echo ""
    echo "Next steps:"
    echo "  1. Save the credentials above in a secure location"
    echo "  2. Update application configurations to use Vault"
    echo "  3. Test secret retrieval"
    echo "  4. Enable secret rotation policies"
    echo ""
    echo "Vault UI: ${VAULT_ADDR}/ui"
    echo ""
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                  SAHOOL Vault Initialization"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Environment: ${ENVIRONMENT}"
    echo "Vault Address: ${VAULT_ADDR}"
    echo "Secrets Prefix: ${SECRETS_PREFIX}"
    echo ""

    check_vault_connectivity
    enable_secrets_engines
    configure_database_secrets
    create_static_secrets
    configure_auth_methods

    # Only configure K8s auth if in Kubernetes
    if [ -f "/var/run/secrets/kubernetes.io/serviceaccount/token" ]; then
        configure_kubernetes_auth
    fi

    enable_audit_logging
    configure_pki
    print_credentials
}

main "$@"
