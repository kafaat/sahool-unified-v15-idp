#!/usr/bin/env bash

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL NATS NKey Generation Script
# Generates operator, account, and user NKeys for secure NATS authentication
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OPERATOR_NAME="${OPERATOR_NAME:-SAHOOL}"
NATS_DIR="${NATS_DIR:-/home/user/sahool-unified-v15-idp/config/nats}"
NKEYS_DIR="${NKEYS_DIR:-${NATS_DIR}/nkeys}"
CREDS_DIR="${CREDS_DIR:-${NATS_DIR}/creds}"
OUTPUT_DIR="${OUTPUT_DIR:-${NATS_DIR}/generated}"

# Default accounts and users
SYSTEM_ACCOUNT="SYS"
APP_ACCOUNT="APP"

# Users per account
declare -A ACCOUNT_USERS=(
    ["SYS"]="system-monitor"
    ["APP"]="admin service1 service2 monitor field-service weather-service iot-service notification-service marketplace-service billing-service chat-service"
)

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

check_nsc() {
    if ! command -v nsc &> /dev/null; then
        log_error "nsc command not found!"
        log_info "Please install nsc from: https://github.com/nats-io/nsc"
        log_info "Installation commands:"
        echo ""
        echo "  # Using curl:"
        echo "  curl -L https://raw.githubusercontent.com/nats-io/nsc/master/install.sh | sh"
        echo ""
        echo "  # Or using go:"
        echo "  go install github.com/nats-io/nsc/v2@latest"
        echo ""
        exit 1
    fi
    log_success "nsc tool found: $(which nsc)"
}

check_nk() {
    if ! command -v nk &> /dev/null; then
        log_warning "nk command not found (optional utility)"
        log_info "You can install nk from: https://github.com/nats-io/nkeys"
        return 0
    fi
    log_success "nk tool found: $(which nk)"
}

create_directories() {
    log_info "Creating directory structure..."
    mkdir -p "${NKEYS_DIR}"
    mkdir -p "${CREDS_DIR}"
    mkdir -p "${OUTPUT_DIR}"
    mkdir -p "${NKEYS_DIR}/operator"
    mkdir -p "${NKEYS_DIR}/accounts"
    mkdir -p "${NKEYS_DIR}/users"
    log_success "Directories created"
}

init_nsc_environment() {
    log_info "Initializing NSC environment..."

    # Set NSC store directory
    export NKEYS_PATH="${NKEYS_DIR}"
    export NSC_HOME="${NKEYS_DIR}"

    # Initialize NSC if not already done
    if [ ! -d "${NKEYS_DIR}/.nsc" ]; then
        nsc env -s "${NKEYS_DIR}"
        log_success "NSC environment initialized"
    else
        log_warning "NSC environment already exists"
    fi
}

generate_operator() {
    log_info "Generating operator: ${OPERATOR_NAME}..."

    # Check if operator already exists
    if nsc describe operator "${OPERATOR_NAME}" &> /dev/null; then
        log_warning "Operator ${OPERATOR_NAME} already exists, skipping..."
        return 0
    fi

    # Create operator
    nsc add operator "${OPERATOR_NAME}" \
        --sys \
        --generate-signing-key

    log_success "Operator ${OPERATOR_NAME} created"

    # Export operator JWT
    nsc describe operator -J > "${OUTPUT_DIR}/operator.jwt"
    log_success "Operator JWT exported to ${OUTPUT_DIR}/operator.jwt"
}

generate_account() {
    local account_name="$1"

    log_info "Generating account: ${account_name}..."

    # Check if account already exists
    if nsc describe account "${account_name}" &> /dev/null; then
        log_warning "Account ${account_name} already exists, skipping..."
        return 0
    fi

    # Create account with JetStream enabled
    if [ "${account_name}" = "${SYSTEM_ACCOUNT}" ]; then
        # System account
        nsc add account "${account_name}" \
            --name "${account_name}"
    else
        # Application account with JetStream
        nsc add account "${account_name}" \
            --name "${account_name}" \
            --js-mem-storage 1G \
            --js-disk-storage 10G \
            --js-streams 100 \
            --js-consumer 1000
    fi

    log_success "Account ${account_name} created"

    # Export account JWT
    nsc describe account "${account_name}" -J > "${OUTPUT_DIR}/${account_name}_account.jwt"
    log_success "Account JWT exported to ${OUTPUT_DIR}/${account_name}_account.jwt"
}

generate_user() {
    local account_name="$1"
    local user_name="$2"

    log_info "Generating user: ${user_name} for account ${account_name}..."

    # Check if user already exists
    if nsc describe user -a "${account_name}" "${user_name}" &> /dev/null; then
        log_warning "User ${user_name} already exists in ${account_name}, skipping..."
        return 0
    fi

    # Define permissions based on user type
    case "${user_name}" in
        admin)
            # Admin user - full access with limits
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub ">" \
                --allow-sub ">" \
                --max-connections 10 \
                --max-subscriptions 100 \
                --max-data 8M \
                --max-payload 8M
            ;;
        monitor|system-monitor)
            # Monitor user - read-only
            nsc add user -a "${account_name}" "${user_name}" \
                --deny-pub ">" \
                --allow-sub "sahool.>,field.>,weather.>,iot.>,notification.>,marketplace.>,billing.>,chat.>,alert.>" \
                --deny-sub "\$SYS.>,\$JS.API.>" \
                --max-connections 5 \
                --max-subscriptions 50 \
                --max-data 1M \
                --max-payload 1M
            ;;
        field-service)
            # Field service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "field.>,sahool.field.>,_INBOX.>" \
                --allow-sub "field.>,sahool.field.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 50 \
                --max-subscriptions 200 \
                --max-data 8M \
                --max-payload 8M
            ;;
        weather-service)
            # Weather service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "weather.>,sahool.weather.>,_INBOX.>" \
                --allow-sub "weather.>,sahool.weather.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 20 \
                --max-subscriptions 100 \
                --max-data 4M \
                --max-payload 4M
            ;;
        iot-service)
            # IoT service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "iot.>,sahool.iot.>,_INBOX.>" \
                --allow-sub "iot.>,sahool.iot.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 100 \
                --max-subscriptions 500 \
                --max-data 8M \
                --max-payload 8M
            ;;
        notification-service)
            # Notification service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "notification.>,sahool.notification.>,_INBOX.>" \
                --allow-sub "notification.>,sahool.notification.>,sahool.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 50 \
                --max-subscriptions 200 \
                --max-data 4M \
                --max-payload 4M
            ;;
        marketplace-service)
            # Marketplace service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "marketplace.>,sahool.marketplace.>,_INBOX.>" \
                --allow-sub "marketplace.>,sahool.marketplace.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 50 \
                --max-subscriptions 200 \
                --max-data 8M \
                --max-payload 8M
            ;;
        billing-service)
            # Billing service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "billing.>,sahool.billing.>,_INBOX.>" \
                --allow-sub "billing.>,sahool.billing.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 30 \
                --max-subscriptions 100 \
                --max-data 4M \
                --max-payload 4M
            ;;
        chat-service)
            # Chat service - specific permissions
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "chat.>,sahool.chat.>,_INBOX.>" \
                --allow-sub "chat.>,sahool.chat.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --max-connections 100 \
                --max-subscriptions 500 \
                --max-data 8M \
                --max-payload 8M
            ;;
        *)
            # Default service user
            nsc add user -a "${account_name}" "${user_name}" \
                --allow-pub "sahool.>,field.>,weather.>,iot.>,notification.>,marketplace.>,billing.>,chat.>,alert.>,_INBOX.>" \
                --allow-sub "sahool.>,field.>,weather.>,iot.>,notification.>,marketplace.>,billing.>,chat.>,alert.>,_INBOX.>" \
                --deny-pub "\$SYS.>,\$JS.API.>" \
                --deny-sub "\$SYS.>" \
                --max-connections 50 \
                --max-subscriptions 200 \
                --max-data 8M \
                --max-payload 8M
            ;;
    esac

    log_success "User ${user_name} created in account ${account_name}"

    # Generate credentials file
    nsc generate creds -a "${account_name}" -n "${user_name}" > "${CREDS_DIR}/${account_name}_${user_name}.creds"
    chmod 600 "${CREDS_DIR}/${account_name}_${user_name}.creds"
    log_success "Credentials file created: ${CREDS_DIR}/${account_name}_${user_name}.creds"
}

generate_resolver_config() {
    log_info "Generating account resolver configuration..."

    # Create resolver directory
    mkdir -p "${OUTPUT_DIR}/resolver"

    # Generate account JWTs for resolver
    for account in "${SYSTEM_ACCOUNT}" "${APP_ACCOUNT}"; do
        nsc describe account "${account}" -J > "${OUTPUT_DIR}/resolver/${account}.jwt"
    done

    # Create resolver configuration
    cat > "${OUTPUT_DIR}/resolver.conf" << EOF
# NATS Account Resolver Configuration
# Generated on $(date)

resolver {
    type: full
    dir: "${OUTPUT_DIR}/resolver"
    allow_delete: false
    interval: "2m"
    limit: 1000
}

# Alternative: Memory resolver (for testing)
# resolver: MEMORY

# Alternative: URL resolver (for production with resolver server)
# resolver: URL(http://nats-account-server:9090/jwt/v1/accounts/)
EOF

    log_success "Resolver configuration created: ${OUTPUT_DIR}/resolver.conf"
}

generate_summary() {
    log_info "Generating setup summary..."

    cat > "${OUTPUT_DIR}/SETUP_SUMMARY.md" << EOF
# NATS NKey Setup Summary

Generated on: $(date)

## Operator
- Name: ${OPERATOR_NAME}
- JWT: ${OUTPUT_DIR}/operator.jwt

## Accounts

### System Account (${SYSTEM_ACCOUNT})
- JWT: ${OUTPUT_DIR}/${SYSTEM_ACCOUNT}_account.jwt
- Users: ${ACCOUNT_USERS[SYS]}

### Application Account (${APP_ACCOUNT})
- JWT: ${OUTPUT_DIR}/${APP_ACCOUNT}_account.jwt
- Users: ${ACCOUNT_USERS[APP]}

## Credentials Files Location
\`\`\`
${CREDS_DIR}/
EOF

    # List all credential files
    for account in "${SYSTEM_ACCOUNT}" "${APP_ACCOUNT}"; do
        for user in ${ACCOUNT_USERS[$account]}; do
            echo "  - ${account}_${user}.creds" >> "${OUTPUT_DIR}/SETUP_SUMMARY.md"
        done
    done

    cat >> "${OUTPUT_DIR}/SETUP_SUMMARY.md" << EOF
\`\`\`

## Using Credentials in Your Application

### Node.js Example
\`\`\`javascript
const { connect } = require('nats');

const nc = await connect({
    servers: 'nats://localhost:4222',
    userCreds: '${CREDS_DIR}/APP_service1.creds'
});
\`\`\`

### Go Example
\`\`\`go
import "github.com/nats-io/nats.go"

nc, err := nats.Connect(
    "nats://localhost:4222",
    nats.UserCredentials("${CREDS_DIR}/APP_service1.creds"),
)
\`\`\`

### Python Example
\`\`\`python
import asyncio
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect(
        servers=["nats://localhost:4222"],
        user_credentials="${CREDS_DIR}/APP_service1.creds"
    )
\`\`\`

## Next Steps

1. Update your NATS server configuration to use the generated resolver
2. Copy credential files to your application deployment
3. Update environment variables or configuration to point to credential files
4. Test connectivity using nats-cli:
   \`\`\`bash
   nats context save sahool --creds ${CREDS_DIR}/APP_admin.creds --server nats://localhost:4222
   nats pub test "Hello NATS"
   \`\`\`

## Security Notes

⚠️ **IMPORTANT**: Keep credential files secure!
- Credential files contain private keys
- Never commit them to version control
- Use Kubernetes secrets or vault for deployment
- Rotate credentials regularly

## Troubleshooting

If you encounter connection issues:
1. Verify NATS server is running with resolver configured
2. Check credential file permissions (should be 600)
3. Verify account has required permissions
4. Check NATS server logs for authentication errors
EOF

    log_success "Setup summary created: ${OUTPUT_DIR}/SETUP_SUMMARY.md"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "   SAHOOL NATS NKey Generation"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"

    # Pre-flight checks
    check_nsc
    check_nk

    # Setup
    create_directories
    init_nsc_environment

    # Generate operator
    generate_operator

    # Generate accounts
    for account in "${SYSTEM_ACCOUNT}" "${APP_ACCOUNT}"; do
        generate_account "${account}"
    done

    # Generate users for each account
    for account in "${!ACCOUNT_USERS[@]}"; do
        for user in ${ACCOUNT_USERS[$account]}; do
            generate_user "${account}" "${user}"
        done
    done

    # Generate resolver configuration
    generate_resolver_config

    # Generate summary
    generate_summary

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ NKey generation completed successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review generated files in: ${OUTPUT_DIR}"
    echo "  2. Update NATS server configuration with resolver"
    echo "  3. Distribute credential files to services"
    echo "  4. Test connectivity"
    echo ""
    echo -e "${BLUE}For more information, see:${NC}"
    echo "  - Setup Summary: ${OUTPUT_DIR}/SETUP_SUMMARY.md"
    echo "  - Documentation: docs/NATS_NKEY_SETUP.md"
    echo ""
}

# Run main function
main "$@"
