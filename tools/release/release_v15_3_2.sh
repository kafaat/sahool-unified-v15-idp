#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL v15.3.2 Release Builder
# One script to prepare, build, and package the entire platform
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERSION="15.3.2"
RELEASE_NAME="sahool-kernel-v${VERSION//./-}-final"
RELEASE_DIR="$HOME/$RELEASE_NAME"
ZIP_FILE="$HOME/$RELEASE_NAME.zip"

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"; echo -e "${CYAN}  $1${NC}"; echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"; }

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SERVICES=(
    "field_ops:8080"
    "ndvi_engine:8097"
    "weather_core:8098"
    "field_chat:8099"
    "iot_gateway:8094"
    "agro_advisor:8095"
    "ws_gateway:8090"
)

SKIP_CERTS=${SKIP_CERTS:-false}
SKIP_DOCKER=${SKIP_DOCKER:-false}
SKIP_MIGRATE=${SKIP_MIGRATE:-false}
SKIP_SMOKE=${SKIP_SMOKE:-false}
SKIP_ZIP=${SKIP_ZIP:-false}

# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

print_banner() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                               ║${NC}"
    echo -e "${CYAN}║     ███████╗ █████╗ ██╗  ██╗ ██████╗  ██████╗ ██╗            ║${NC}"
    echo -e "${CYAN}║     ██╔════╝██╔══██╗██║  ██║██╔═══██╗██╔═══██╗██║            ║${NC}"
    echo -e "${CYAN}║     ███████╗███████║███████║██║   ██║██║   ██║██║            ║${NC}"
    echo -e "${CYAN}║     ╚════██║██╔══██║██╔══██║██║   ██║██║   ██║██║            ║${NC}"
    echo -e "${CYAN}║     ███████║██║  ██║██║  ██║╚██████╔╝╚██████╔╝███████╗       ║${NC}"
    echo -e "${CYAN}║     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝       ║${NC}"
    echo -e "${CYAN}║                                                               ║${NC}"
    echo -e "${CYAN}║                   v$VERSION Release Builder                    ║${NC}"
    echo -e "${CYAN}║                                                               ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_prerequisites() {
    log_step "Step 1: Checking Prerequisites"

    local missing=()

    command -v docker &>/dev/null || missing+=("docker")

    # Check for Docker Compose v2 (preferred)
    if ! docker compose version &>/dev/null; then
        log_error "Docker Compose v2 is required (docker compose)"
        log_info "Install with: Docker Desktop or docker-compose-plugin"
        exit 1
    fi

    command -v openssl &>/dev/null || missing+=("openssl")
    command -v zip &>/dev/null || missing+=("zip")

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        exit 1
    fi

    log_success "All prerequisites satisfied"
    log_info "Docker Compose version: $(docker compose version --short)"
}

generate_env() {
    log_step "Step 2: Generating Environment Files"

    local env_file="$PROJECT_ROOT/.env"

    if [[ -f "$env_file" ]] && [[ "${FORCE_ENV:-false}" != "true" ]]; then
        log_info ".env already exists, skipping (use FORCE_ENV=true to override)"
        return 0
    fi

    cat > "$env_file" <<EOF
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL v$VERSION Environment Configuration
# Generated: $(date -Iseconds)
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Core Settings
# ─────────────────────────────────────────────────────────────────────────────
SAHOOL_VERSION=$VERSION
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FORMAT=json

# ─────────────────────────────────────────────────────────────────────────────
# Database (PostgreSQL)
# ─────────────────────────────────────────────────────────────────────────────
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=sahool
POSTGRES_USER=sahool
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
DATABASE_URL=postgres://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@\${POSTGRES_HOST}:\${POSTGRES_PORT}/\${POSTGRES_DB}

# ─────────────────────────────────────────────────────────────────────────────
# Message Queue (NATS)
# ─────────────────────────────────────────────────────────────────────────────
NATS_URL=nats://nats:4222
NATS_CLUSTER_ID=sahool-cluster

# ─────────────────────────────────────────────────────────────────────────────
# Cache (Redis)
# ─────────────────────────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ─────────────────────────────────────────────────────────────────────────────
# MQTT (IoT)
# ─────────────────────────────────────────────────────────────────────────────
MQTT_BROKER_URL=mqtt://mqtt:1883

# ─────────────────────────────────────────────────────────────────────────────
# JWT Authentication
# ─────────────────────────────────────────────────────────────────────────────
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)
JWT_ISSUER=sahool-idp
JWT_AUDIENCE=sahool-platform
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7

# ─────────────────────────────────────────────────────────────────────────────
# Service Ports
# ─────────────────────────────────────────────────────────────────────────────
FIELD_OPS_PORT=8080
NDVI_ENGINE_PORT=8097
WEATHER_CORE_PORT=8098
FIELD_CHAT_PORT=8099
IOT_GATEWAY_PORT=8094
AGRO_ADVISOR_PORT=8095
WS_GATEWAY_PORT=8090
DASHBOARD_PORT=3000

# ─────────────────────────────────────────────────────────────────────────────
# Feature Flags
# ─────────────────────────────────────────────────────────────────────────────
ENABLE_SECURITY=true
ENABLE_AUDIT_LOGGING=true
ENABLE_MTLS=false
ENABLE_RATE_LIMITING=true

EOF

    chmod 600 "$env_file"
    log_success "Environment file generated: $env_file"
}

generate_certs() {
    if [[ "$SKIP_CERTS" == "true" ]]; then
        log_info "Skipping certificate generation (SKIP_CERTS=true)"
        return 0
    fi

    log_step "Step 3: Generating TLS Certificates"

    local cert_script="$PROJECT_ROOT/scripts/security/generate-certs.sh"

    if [[ -f "$cert_script" ]]; then
        bash "$cert_script" --force
    else
        log_warn "Certificate script not found, skipping"
    fi
}

start_infrastructure() {
    if [[ "$SKIP_DOCKER" == "true" ]]; then
        log_info "Skipping Docker startup (SKIP_DOCKER=true)"
        return 0
    fi

    log_step "Step 4: Starting Infrastructure"

    cd "$PROJECT_ROOT"

    # Start infrastructure services first
    log_info "Starting postgres, nats, redis, mqtt..."
    docker compose up -d postgres nats redis mqtt

    # Wait for services
    log_info "Waiting for infrastructure to be ready..."
    sleep 10

    # Start application services
    log_info "Starting application services..."
    docker compose up -d

    log_success "All services started"
}

run_migrations() {
    if [[ "$SKIP_MIGRATE" == "true" ]]; then
        log_info "Skipping migrations (SKIP_MIGRATE=true)"
        return 0
    fi

    log_step "Step 5: Running Database Migrations"

    local migrate_script="$PROJECT_ROOT/tools/env/migrate.sh"

    if [[ -f "$migrate_script" ]]; then
        bash "$migrate_script"
    else
        log_warn "Migration script not found, skipping"
    fi
}

run_smoke_tests() {
    if [[ "$SKIP_SMOKE" == "true" ]]; then
        log_info "Skipping smoke tests (SKIP_SMOKE=true)"
        return 0
    fi

    log_step "Step 6: Running Smoke Tests"

    local smoke_script="$PROJECT_ROOT/tools/release/smoke_test.sh"

    if [[ -f "$smoke_script" ]]; then
        bash "$smoke_script"
    else
        # Basic health checks
        log_info "Running basic health checks..."

        local all_healthy=true

        for service_port in "${SERVICES[@]}"; do
            local service="${service_port%%:*}"
            local port="${service_port##*:}"

            if curl -sf "http://localhost:$port/healthz" > /dev/null 2>&1; then
                log_success "$service (port $port): Healthy"
            else
                log_warn "$service (port $port): Not responding"
                all_healthy=false
            fi
        done

        if [[ "$all_healthy" == "true" ]]; then
            log_success "All services healthy"
        else
            log_warn "Some services not responding (may need more time)"
        fi
    fi
}

build_zip() {
    if [[ "$SKIP_ZIP" == "true" ]]; then
        log_info "Skipping ZIP build (SKIP_ZIP=true)"
        return 0
    fi

    log_step "Step 7: Building Release Package"

    # Clean previous release
    rm -rf "$RELEASE_DIR" "$ZIP_FILE"
    mkdir -p "$RELEASE_DIR"

    log_info "Copying project files..."

    # Copy essential directories
    cp -r "$PROJECT_ROOT/kernel" "$RELEASE_DIR/"
    cp -r "$PROJECT_ROOT/shared" "$RELEASE_DIR/"
    cp -r "$PROJECT_ROOT/tools" "$RELEASE_DIR/"
    cp -r "$PROJECT_ROOT/scripts" "$RELEASE_DIR/"
    cp -r "$PROJECT_ROOT/docs" "$RELEASE_DIR/" 2>/dev/null || mkdir -p "$RELEASE_DIR/docs"
    cp -r "$PROJECT_ROOT/helm" "$RELEASE_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/.github" "$RELEASE_DIR/" 2>/dev/null || true

    # Copy root files
    cp "$PROJECT_ROOT/docker-compose.yml" "$RELEASE_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/.env.template" "$RELEASE_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/README.md" "$RELEASE_DIR/" 2>/dev/null || true

    # Create version file
    cat > "$RELEASE_DIR/VERSION" <<EOF
SAHOOL Platform
Version: $VERSION
Build Date: $(date -Iseconds)
Build Host: $(hostname)
EOF

    # Create release notes
    cat > "$RELEASE_DIR/RELEASE_NOTES.md" <<EOF
# SAHOOL v$VERSION Release Notes

## Services Included

| Service | Port | Description |
|---------|------|-------------|
| field_ops | 8080 | Task management and field operations |
| ndvi_engine | 8097 | NDVI satellite analysis |
| weather_core | 8098 | Weather forecasting and alerts |
| field_chat | 8099 | Real-time collaboration |
| iot_gateway | 8094 | IoT device management |
| agro_advisor | 8095 | Disease and fertilizer recommendations |
| ws_gateway | 8090 | WebSocket event broadcasting |

## Infrastructure

- PostgreSQL 15+
- NATS JetStream
- Redis 7+
- Mosquitto MQTT

## Quick Start

\`\`\`bash
# 1. Generate environment
./tools/release/release_v15_3_2.sh --env-only

# 2. Start services
docker compose up -d

# 3. Run migrations
./tools/env/migrate.sh

# 4. Verify health
curl http://localhost:8080/healthz
\`\`\`

## Security

- JWT authentication enabled
- RBAC with 6 role levels
- Audit logging to database
- mTLS ready (optional)

## Documentation

See \`docs/\` directory for:
- DEPLOYMENT.md - Deployment guide
- SECURITY.md - Security configuration
- OPERATIONS.md - Operations runbook

EOF

    # Exclude unnecessary files
    log_info "Cleaning up unnecessary files..."
    find "$RELEASE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$RELEASE_DIR" -type d -name ".git" -exec rm -rf {} + 2>/dev/null || true
    find "$RELEASE_DIR" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
    find "$RELEASE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "$RELEASE_DIR" -type f -name ".DS_Store" -delete 2>/dev/null || true

    # Create ZIP
    log_info "Creating ZIP archive..."
    cd "$HOME"
    zip -r "$ZIP_FILE" "$RELEASE_NAME" -x "*.git*"

    local zip_size=$(du -h "$ZIP_FILE" | cut -f1)
    log_success "Release package created: $ZIP_FILE ($zip_size)"
}

print_summary() {
    log_step "Release Complete!"

    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  SAHOOL v$VERSION Release Build Complete${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Release Directory: $RELEASE_DIR"
    echo "  ZIP Archive:       $ZIP_FILE"
    echo ""
    echo -e "${CYAN}GitHub Release Commands:${NC}"
    echo ""
    echo "  # Create a new release"
    echo "  gh release create v$VERSION $ZIP_FILE \\"
    echo "    -t \"SAHOOL v$VERSION\" \\"
    echo "    -n \"Final release: FieldOps + NDVI + Weather + IoT + Chat + Security\""
    echo ""
    echo "  # Or upload to existing release"
    echo "  gh release upload v$VERSION $ZIP_FILE"
    echo ""
    echo -e "${CYAN}Docker Commands:${NC}"
    echo ""
    echo "  # Start all services"
    echo "  docker compose up -d"
    echo ""
    echo "  # View logs"
    echo "  docker compose logs -f"
    echo ""
    echo "  # Stop all services"
    echo "  docker compose down"
    echo ""
}

show_help() {
    cat <<EOF
SAHOOL v$VERSION Release Builder

Usage: $0 [OPTIONS]

Options:
    --help, -h        Show this help message
    --env-only        Only generate environment file
    --no-certs        Skip certificate generation
    --no-docker       Skip Docker startup
    --no-migrate      Skip database migrations
    --no-smoke        Skip smoke tests
    --no-zip          Skip ZIP creation
    --force-env       Force regenerate .env file

Environment Variables:
    SKIP_CERTS=true    Skip certificate generation
    SKIP_DOCKER=true   Skip Docker startup
    SKIP_MIGRATE=true  Skip migrations
    SKIP_SMOKE=true    Skip smoke tests
    SKIP_ZIP=true      Skip ZIP creation
    FORCE_ENV=true     Force regenerate .env

Examples:
    $0                    # Full release build
    $0 --env-only         # Only generate .env
    $0 --no-docker        # Build without starting services

EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local env_only=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --env-only)
                env_only=true
                shift
                ;;
            --no-certs)
                SKIP_CERTS=true
                shift
                ;;
            --no-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --no-migrate)
                SKIP_MIGRATE=true
                shift
                ;;
            --no-smoke)
                SKIP_SMOKE=true
                shift
                ;;
            --no-zip)
                SKIP_ZIP=true
                shift
                ;;
            --force-env)
                FORCE_ENV=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    print_banner

    if [[ "$env_only" == "true" ]]; then
        generate_env
        exit 0
    fi

    check_prerequisites
    generate_env
    generate_certs
    start_infrastructure
    run_migrations
    run_smoke_tests
    build_zip
    print_summary
}

main "$@"
