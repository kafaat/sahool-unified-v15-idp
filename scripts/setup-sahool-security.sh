#!/bin/bash
# scripts/setup-sahool-security.sh
# One-Click SAHOOL Security Infrastructure Setup
# Usage: ./setup-sahool-security.sh --org kafaat --workspace sahoop-github-security

set -euo pipefail

# COLORS
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# CONFIG
GITHUB_ORG=""
TF_WORKSPACE=""
TF_ORG="kafaat-devops"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../infra/github-security"
SECRETS_DIR="${SCRIPT_DIR}/../secrets"
LOCK_FILE="/tmp/sahool-setup.lock"

# FUNCTIONS
log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1" >&2; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }
check_cmd() { command -v "$1" >/dev/null 2>&1 || error "$1 is required but not installed."; }

# LOCK FILE (prevent double execution)
acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        error "Setup already running (PID $(cat $LOCK_FILE)). If stuck, delete $LOCK_FILE"
    fi
    echo $$ > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
}

# PARSE ARGS
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --org) GITHUB_ORG="$2"; shift 2 ;;
            --workspace) TF_WORKSPACE="$2"; shift 2 ;;
            --auto-approve) AUTO_APPROVE="true"; shift ;;
            --help)
                echo "Usage: $0 --org <github-org> --workspace <tf-workspace> [--auto-approve]"
                echo ""
                echo "Options:"
                echo "  --org          GitHub organization name (required)"
                echo "  --workspace    Terraform Cloud workspace name (default: sahoop-github-security)"
                echo "  --auto-approve Skip confirmation prompts"
                exit 0 ;;
            *) error "Unknown argument: $1" ;;
        esac
    done

    [ -z "$GITHUB_ORG" ] && error "--org is required"
    [ -z "$TF_WORKSPACE" ] && TF_WORKSPACE="sahoop-github-security"
}

# PREREQUISITES
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    check_cmd gh
    check_cmd terraform
    check_cmd openssl
    check_cmd jq
    check_cmd curl

    # Check gh auth
    gh auth status >/dev/null 2>&1 || error "GitHub CLI not authenticated. Run: gh auth login"

    # Check Terraform Cloud token
    if [ -z "${TF_API_TOKEN:-}" ]; then
        error "TF_API_TOKEN not set. Get it from: https://app.terraform.io/app/settings/tokens"
    fi

    log "✅ All prerequisites met"
}

# SETUP DIRECTORIES
setup_directories() {
    log "📁 Setting up directories..."
    mkdir -p "$TF_DIR" "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
    log "✅ Directories created"
}

# GENERATE SECRETS
generate_secrets() {
    log "🔐 Generating secrets..."

    # JWT Secret (256-bit)
    if [ ! -f "$SECRETS_DIR/jwt.secret" ]; then
        openssl rand -hex 32 > "$SECRETS_DIR/jwt.secret"
        chmod 600 "$SECRETS_DIR/jwt.secret"
        log "✅ JWT secret generated"
    else
        warn "JWT secret already exists, skipping"
    fi

    # DB Password
    if [ ! -f "$SECRETS_DIR/db.password" ]; then
        openssl rand -base64 32 > "$SECRETS_DIR/db.password"
        chmod 600 "$SECRETS_DIR/db.password"
        log "✅ DB password generated"
    else
        warn "DB password already exists, skipping"
    fi

    # Snyk Token placeholder
    if [ ! -f "$SECRETS_DIR/snyk.token" ]; then
        echo "PLACEHOLDER_SNYK_TOKEN" > "$SECRETS_DIR/snyk.token"
        chmod 600 "$SECRETS_DIR/snyk.token"
        warn "Snyk token is placeholder. Replace with real token from snyk.io"
    fi

    # API Keys
    if [ ! -f "$SECRETS_DIR/api.key" ]; then
        openssl rand -hex 32 > "$SECRETS_DIR/api.key"
        chmod 600 "$SECRETS_DIR/api.key"
        log "✅ API key generated"
    fi
}

# CREATE TERRAFORM TFVARS
create_tfvars() {
    log "📝 Creating terraform.tfvars..."

    cat > "$TF_DIR/terraform.tfvars" <<EOF
github_organization = "$GITHUB_ORG"
snyk_token          = "$(cat "$SECRETS_DIR/snyk.token")"
jwt_secret          = "$(cat "$SECRETS_DIR/jwt.secret")"
db_password         = "$(cat "$SECRETS_DIR/db.password")"

teams = {
  security = {
    name        = "sahool-security"
    description = "Security team for SAHOOL Platform"
    privacy     = "closed"
    members     = ["security-lead", "devsecops-engineer"]
  }
  backend = {
    name        = "sahool-backend"
    description = "Backend team"
    privacy     = "closed"
    members     = ["backend-lead"]
    permission  = "push"
  }
  mobile = {
    name        = "sahool-mobile"
    description = "Mobile team"
    privacy     = "closed"
    members     = ["mobile-lead"]
    permission  = "push"
  }
}
EOF

    chmod 600 "$TF_DIR/terraform.tfvars"
    log "✅ terraform.tfvars created"
}

# SETUP TERRAFORM CLOUD WORKSPACE
setup_tf_cloud() {
    log "☁️  Setting up Terraform Cloud workspace..."

    # Check if workspace exists
    WORKSPACE_RESPONSE=$(curl -s \
        -H "Authorization: Bearer $TF_API_TOKEN" \
        -H "Content-Type: application/vnd.api+json" \
        "https://app.terraform.io/api/v2/organizations/$TF_ORG/workspaces/$TF_WORKSPACE")

    if echo "$WORKSPACE_RESPONSE" | jq -e '.data' >/dev/null 2>&1; then
        log "✅ Workspace $TF_WORKSPACE already exists"
    else
        # Create workspace
        curl -s -X POST \
            -H "Authorization: Bearer $TF_API_TOKEN" \
            -H "Content-Type: application/vnd.api+json" \
            "https://app.terraform.io/api/v2/organizations/$TF_ORG/workspaces" \
            -d "$(jq -n --arg ws "$TF_WORKSPACE" --arg org "$GITHUB_ORG" '{
                "data": {
                    "type": "workspaces",
                    "attributes": {
                        "name": $ws,
                        "execution-mode": "remote",
                        "working-directory": "infra/github-security",
                        "auto-apply": false
                    }
                }
            }')" > /dev/null

        log "✅ Workspace $TF_WORKSPACE created"
    fi
}

# TERRAFORM INIT & PLAN
terraform_plan() {
    log "🔍 Running terraform plan..."

    cd "$TF_DIR"

    # Initialize
    terraform init -input=false

    # Plan
    terraform plan -input=false -out=tfplan -detailed-exitcode || {
        exit_code=$?
        if [ $exit_code -eq 2 ]; then
            log "✅ Plan shows changes, proceeding..."
            return 0
        elif [ $exit_code -eq 0 ]; then
            log "✅ No changes needed"
            return 0
        else
            error "Terraform plan failed"
        fi
    }
}

# TERRAFORM APPLY
terraform_apply() {
    log "🚀 Applying infrastructure..."

    cd "$TF_DIR"

    if [ ! -f "tfplan" ]; then
        log "No plan file found, skipping apply"
        return 0
    fi

    # Confirm with user (unless auto-approve)
    if [ "${AUTO_APPROVE:-false}" = "true" ]; then
        terraform apply -auto-approve tfplan
    else
        read -p "⚠️  Apply changes? (yes/no): " confirm
        [ "$confirm" = "yes" ] || error "Apply cancelled"
        terraform apply tfplan
    fi

    log "✅ Terraform apply complete"
}

# VERIFY GITHUB SETUP
verify_github() {
    log "🔍 Verifying GitHub setup..."

    # Check repository exists
    if gh api "/repos/$GITHUB_ORG/sahool-unified-v15-idp" --jq '.name' >/dev/null 2>&1; then
        log "✅ Repository exists"
    else
        warn "Repository not found"
        return 0
    fi

    # Check branch protection
    if gh api "/repos/$GITHUB_ORG/sahool-unified-v15-idp/branches/main/protection" >/dev/null 2>&1; then
        log "✅ Branch protection active"
    else
        warn "Branch protection may not be active yet"
    fi

    # Check secrets
    if gh secret list --repo "$GITHUB_ORG/sahool-unified-v15-idp" 2>/dev/null | grep -qE "SNYK|JWT|DB"; then
        log "✅ GitHub Actions secrets configured"
    else
        warn "Some secrets may not be configured"
    fi
}

# SETUP GITHUB SECRETS
setup_github_secrets() {
    log "🔑 Setting up GitHub secrets..."

    # Set secrets
    gh secret set JWT_SECRET --repo "$GITHUB_ORG/sahool-unified-v15-idp" < "$SECRETS_DIR/jwt.secret" 2>/dev/null || warn "Could not set JWT_SECRET"
    gh secret set DB_PASSWORD --repo "$GITHUB_ORG/sahool-unified-v15-idp" < "$SECRETS_DIR/db.password" 2>/dev/null || warn "Could not set DB_PASSWORD"

    if [ -f "$SECRETS_DIR/snyk.token" ] && [ "$(cat "$SECRETS_DIR/snyk.token")" != "PLACEHOLDER_SNYK_TOKEN" ]; then
        gh secret set SNYK_TOKEN --repo "$GITHUB_ORG/sahool-unified-v15-idp" < "$SECRETS_DIR/snyk.token" 2>/dev/null || warn "Could not set SNYK_TOKEN"
    fi

    log "✅ GitHub secrets configured"
}

# GENERATE REPORT
generate_report() {
    log "📊 Generating security report..."

    cat > "$SECRETS_DIR/setup-report.json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "organization": "$GITHUB_ORG",
  "workspace": "$TF_WORKSPACE",
  "repository": "sahool-unified-v15-idp",
  "secrets_generated": {
    "jwt_secret": "$(sha256sum "$SECRETS_DIR/jwt.secret" 2>/dev/null | cut -d' ' -f1 || echo 'N/A')",
    "db_password": "$(sha256sum "$SECRETS_DIR/db.password" 2>/dev/null | cut -d' ' -f1 || echo 'N/A')"
  },
  "teams_created": ["sahool-security", "sahool-backend", "sahool-mobile"],
  "security_features": ["secret_scanning", "push_protection", "advanced_security", "dependency_graph"]
}
EOF

    chmod 600 "$SECRETS_DIR/setup-report.json"
    log "✅ Report saved to $SECRETS_DIR/setup-report.json"
}

# PRINT SUMMARY
print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🎉 SAHOOL Security Infrastructure Setup Complete!"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "  Organization:  $GITHUB_ORG"
    echo "  Workspace:     $TF_WORKSPACE"
    echo "  Report:        $SECRETS_DIR/setup-report.json"
    echo ""
    echo "  Next Steps:"
    echo "  1. Replace placeholder in $SECRETS_DIR/snyk.token with real Snyk token"
    echo "  2. Review the setup report"
    echo "  3. Check GitHub security settings:"
    echo "     https://github.com/$GITHUB_ORG/sahool-unified-v15-idp/settings/security"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
}

# MAIN
main() {
    echo ""
    echo "🌾 SAHOOL Security Infrastructure Setup"
    echo "════════════════════════════════════════"
    echo ""

    parse_args "$@"

    log "Organization: $GITHUB_ORG | Workspace: $TF_WORKSPACE"

    acquire_lock
    check_prerequisites
    setup_directories
    generate_secrets
    create_tfvars
    setup_tf_cloud
    terraform_plan
    terraform_apply
    setup_github_secrets
    verify_github
    generate_report
    print_summary
}

main "$@"
