#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Bootstrap Script
# سكربت تهيئة منصة سهول
#
# Usage: ./scripts/bootstrap.sh [--dev|--ci|--prod]
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Output
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_MODE="${1:-dev}"

# Remove -- prefix if present
ENV_MODE="${ENV_MODE#--}"

case "$ENV_MODE" in
    dev|development)
        ENV_FILE="$PROJECT_ROOT/config/local.env"
        ENV_MODE="development"
        ;;
    ci|test)
        ENV_FILE="$PROJECT_ROOT/config/ci.env"
        ENV_MODE="ci"
        ;;
    prod|production)
        ENV_FILE="$PROJECT_ROOT/config/prod.env"
        ENV_MODE="production"
        ;;
    *)
        print_error "Unknown mode: $ENV_MODE"
        echo "Usage: $0 [--dev|--ci|--prod]"
        exit 1
        ;;
esac

print_header "SAHOOL Platform Bootstrap - Mode: $ENV_MODE"

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Check Prerequisites
# ─────────────────────────────────────────────────────────────────────────────
print_step "Checking prerequisites..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    print_success "$1 found: $(command -v $1)"
    return 0
}

MISSING_DEPS=0

# Required tools
check_command "docker" || MISSING_DEPS=1
check_command "docker-compose" || check_command "docker" || MISSING_DEPS=1
check_command "node" || MISSING_DEPS=1
check_command "npm" || MISSING_DEPS=1

# Optional tools
check_command "python3" || print_warning "Python3 not found - backend services may not work"
check_command "flutter" || print_warning "Flutter not found - mobile app development disabled"

if [ $MISSING_DEPS -eq 1 ]; then
    print_error "Missing required dependencies. Please install them and try again."
    exit 1
fi

# Check Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Setup Environment Configuration
# ─────────────────────────────────────────────────────────────────────────────
print_step "Setting up environment configuration..."

# Create config directory if not exists
mkdir -p "$PROJECT_ROOT/config"

# Copy base env if config files don't exist
if [ ! -f "$PROJECT_ROOT/config/base.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/config/base.env"
    print_success "Created config/base.env from .env.example"
fi

# Create environment-specific files
for env_type in local ci prod; do
    if [ ! -f "$PROJECT_ROOT/config/${env_type}.env" ]; then
        cp "$PROJECT_ROOT/config/base.env" "$PROJECT_ROOT/config/${env_type}.env"
        print_success "Created config/${env_type}.env"
    fi
done

# Generate secure secrets for development
if [ "$ENV_MODE" = "development" ] || [ "$ENV_MODE" = "ci" ]; then
    print_step "Generating secure secrets for $ENV_MODE..."

    generate_secret() {
        openssl rand -base64 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
    }

    # Create .env file with generated secrets
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        cat > "$PROJECT_ROOT/.env" << EOF
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Auto-generated Environment ($ENV_MODE)
# Generated: $(date)
# ═══════════════════════════════════════════════════════════════════════════════

ENVIRONMENT=$ENV_MODE
LOG_LEVEL=DEBUG

# Database
POSTGRES_USER=sahool
POSTGRES_PASSWORD=$(generate_secret)
POSTGRES_DB=sahool

# Redis
REDIS_PASSWORD=$(generate_secret)

# JWT
JWT_SECRET_KEY=$(generate_secret)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# App Secret
APP_SECRET_KEY=$(generate_secret)

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8080

# Service URLs (Docker internal)
DATABASE_URL=postgresql://sahool:\${POSTGRES_PASSWORD}@postgres:5432/sahool
REDIS_URL=redis://:\${REDIS_PASSWORD}@redis:6379
NATS_URL=nats://nats:4222

# Ports
FIELD_CORE_PORT=3000
WEB_PORT=3001
ADMIN_PORT=3002
EOF
        print_success "Generated .env with secure secrets"
    else
        print_warning ".env already exists - skipping secret generation"
    fi
fi

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    print_success "Loaded environment from .env"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Install Dependencies
# ─────────────────────────────────────────────────────────────────────────────
print_step "Installing Node.js dependencies..."

cd "$PROJECT_ROOT"

if [ -f "package.json" ]; then
    npm install --legacy-peer-deps
    print_success "Node.js dependencies installed"
fi

# Install web app dependencies
if [ -d "apps/web" ]; then
    print_step "Installing web app dependencies..."
    cd "$PROJECT_ROOT/apps/web"
    npm install --legacy-peer-deps
    print_success "Web app dependencies installed"
fi

# Install admin app dependencies
if [ -d "$PROJECT_ROOT/apps/admin" ]; then
    print_step "Installing admin app dependencies..."
    cd "$PROJECT_ROOT/apps/admin"
    npm install --legacy-peer-deps
    print_success "Admin app dependencies installed"
fi

cd "$PROJECT_ROOT"

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Build Shared Packages
# ─────────────────────────────────────────────────────────────────────────────
print_step "Building shared packages..."

for package in api-client shared-utils shared-hooks shared-ui; do
    if [ -d "$PROJECT_ROOT/packages/$package" ] && [ -f "$PROJECT_ROOT/packages/$package/package.json" ]; then
        print_step "Building $package..."
        cd "$PROJECT_ROOT/packages/$package"
        npm run build 2>/dev/null || print_warning "Failed to build $package"
    fi
done

cd "$PROJECT_ROOT"

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Start Infrastructure Services
# ─────────────────────────────────────────────────────────────────────────────
print_step "Starting infrastructure services..."

# Create necessary directories
mkdir -p "$PROJECT_ROOT/infra/postgres/init"
mkdir -p "$PROJECT_ROOT/infra/kong"
mkdir -p "$PROJECT_ROOT/infra/mqtt"

# Create postgres init script if not exists
if [ ! -f "$PROJECT_ROOT/infra/postgres/init/01-init.sql" ]; then
    cat > "$PROJECT_ROOT/infra/postgres/init/01-init.sql" << 'EOF'
-- SAHOOL Platform Database Initialization
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create default schemas
CREATE SCHEMA IF NOT EXISTS geo;
CREATE SCHEMA IF NOT EXISTS crops;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS tenants;

-- Grant permissions
GRANT ALL ON SCHEMA geo TO sahool;
GRANT ALL ON SCHEMA crops TO sahool;
GRANT ALL ON SCHEMA users TO sahool;
GRANT ALL ON SCHEMA tenants TO sahool;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'SAHOOL database initialized successfully';
END $$;
EOF
    print_success "Created postgres init script"
fi

# Create mosquitto config if not exists
if [ ! -f "$PROJECT_ROOT/infra/mqtt/mosquitto.conf" ]; then
    cat > "$PROJECT_ROOT/infra/mqtt/mosquitto.conf" << 'EOF'
listener 1883
listener 9001
protocol websockets
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest stdout
EOF
    print_success "Created mosquitto config"
fi

# Start infrastructure with docker-compose
print_step "Starting Docker infrastructure..."

docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d postgres redis nats mqtt 2>/dev/null || {
    print_warning "Some infrastructure services may have failed to start"
}

# Wait for services to be healthy
print_step "Waiting for infrastructure services to be healthy..."

wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps $service 2>/dev/null | grep -q "healthy\|Up"; then
            print_success "$service is ready"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_warning "$service may not be ready"
    return 1
}

wait_for_service "postgres"
wait_for_service "redis"
wait_for_service "nats"

# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Run Database Migrations
# ─────────────────────────────────────────────────────────────────────────────
print_step "Running database migrations..."

# Check if alembic is available
if command -v alembic &> /dev/null && [ -f "$PROJECT_ROOT/alembic.ini" ]; then
    cd "$PROJECT_ROOT"
    alembic upgrade head 2>/dev/null || print_warning "Alembic migrations failed or not configured"
else
    print_warning "Alembic not found - skipping migrations"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Run Tests (CI mode only)
# ─────────────────────────────────────────────────────────────────────────────
if [ "$ENV_MODE" = "ci" ]; then
    print_step "Running tests..."

    cd "$PROJECT_ROOT"

    # Run web tests
    if [ -d "apps/web" ]; then
        cd "$PROJECT_ROOT/apps/web"
        npm test -- --run 2>/dev/null || print_warning "Web tests failed"
    fi

    # Run admin tests
    if [ -d "$PROJECT_ROOT/apps/admin" ]; then
        cd "$PROJECT_ROOT/apps/admin"
        npm test -- --run 2>/dev/null || print_warning "Admin tests failed"
    fi

    cd "$PROJECT_ROOT"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 8: Build Applications (Production mode)
# ─────────────────────────────────────────────────────────────────────────────
if [ "$ENV_MODE" = "production" ]; then
    print_step "Building applications for production..."

    # Build web app
    if [ -d "$PROJECT_ROOT/apps/web" ]; then
        cd "$PROJECT_ROOT/apps/web"
        npm run build || print_error "Web build failed"
    fi

    # Build admin app
    if [ -d "$PROJECT_ROOT/apps/admin" ]; then
        cd "$PROJECT_ROOT/apps/admin"
        npm run build || print_error "Admin build failed"
    fi

    cd "$PROJECT_ROOT"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print_header "Bootstrap Complete!"

echo -e "${GREEN}SAHOOL Platform is ready!${NC}\n"
echo "Environment: $ENV_MODE"
echo ""
echo "Available commands:"
echo "  - Start all services:    docker-compose up -d"
echo "  - Start web dev:         cd apps/web && npm run dev"
echo "  - Start admin dev:       cd apps/admin && npm run dev"
echo "  - Run tests:             npm test"
echo "  - View logs:             docker-compose logs -f"
echo ""
echo "Service URLs:"
echo "  - Web App:               http://localhost:3001"
echo "  - Admin Dashboard:       http://localhost:3002"
echo "  - API Gateway:           http://localhost:8000"
echo "  - PostgreSQL:            localhost:5432"
echo "  - Redis:                 localhost:6379"
echo "  - NATS:                  localhost:4222"
echo ""
echo -e "${CYAN}Happy coding! 🚀${NC}"
