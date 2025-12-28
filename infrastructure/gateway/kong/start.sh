#!/bin/bash

# ============================================================================
# Kong API Gateway Startup Script
# سكريبت بدء بوابة Kong API
# ============================================================================
# SAHOOL Platform - Agricultural Intelligence Platform
# منصة سهول - منصة الذكاء الزراعي
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ============================================================================
# Step 1: Create sahool-network if it doesn't exist
# الخطوة 1: إنشاء شبكة sahool-network إذا لم تكن موجودة
# ============================================================================

print_info "Checking for sahool-network..."

if docker network inspect sahool-network >/dev/null 2>&1; then
    print_success "sahool-network already exists"
else
    print_info "Creating sahool-network..."
    docker network create sahool-network
    print_success "sahool-network created successfully"
fi

# ============================================================================
# Step 2: Check if .env file exists
# الخطوة 2: التحقق من وجود ملف .env
# ============================================================================

if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_info "Please update .env file with your configuration"
        print_info "Especially JWT secrets and database passwords"
    else
        print_warning "No .env.example found. Using default values..."
    fi
fi

# ============================================================================
# Step 3: Start Kong services in correct order
# الخطوة 3: بدء خدمات Kong بالترتيب الصحيح
# ============================================================================

print_info "Starting Kong infrastructure services..."

# Start Redis first (needed for rate limiting)
print_info "Starting Kong Redis..."
docker-compose up -d kong-redis
sleep 5

# Wait for Redis to be healthy
print_info "Waiting for Redis to be healthy..."
timeout=60
elapsed=0
while ! docker-compose exec -T kong-redis redis-cli ping >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        print_error "Redis failed to start within $timeout seconds"
        exit 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo -n "."
done
echo ""
print_success "Redis is healthy"

# Start Kong Database (PostgreSQL) for Konga
print_info "Starting Kong PostgreSQL database..."
docker-compose up -d kong-database
sleep 5

# Wait for PostgreSQL to be healthy
print_info "Waiting for PostgreSQL to be healthy..."
timeout=60
elapsed=0
while ! docker-compose exec -T kong-database pg_isready -U kong >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        print_error "PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo -n "."
done
echo ""
print_success "PostgreSQL is healthy"

# Check Kong mode from docker-compose.yml
KONG_MODE=$(grep -A 5 "kong:" docker-compose.yml | grep "KONG_DATABASE" | awk -F'"' '{print $2}')

if [ "$KONG_MODE" = "off" ]; then
    print_info "Kong is running in DB-less mode (declarative config)"

    # Start Kong directly in DB-less mode
    print_info "Starting Kong Gateway..."
    docker-compose up -d kong

else
    print_info "Kong is running in DB mode"

    # Run Kong migrations
    print_info "Running Kong database migrations..."
    docker-compose up -d kong-migrations

    # Wait for migrations to complete
    print_info "Waiting for migrations to complete..."
    docker-compose logs -f kong-migrations &
    LOGS_PID=$!

    timeout=120
    elapsed=0
    while docker-compose ps kong-migrations | grep -q "Up"; do
        if [ $elapsed -ge $timeout ]; then
            print_error "Migrations failed to complete within $timeout seconds"
            kill $LOGS_PID 2>/dev/null || true
            exit 1
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done

    kill $LOGS_PID 2>/dev/null || true

    # Check if migrations were successful
    if docker-compose ps kong-migrations | grep -q "Exit 0"; then
        print_success "Migrations completed successfully"
    else
        print_error "Migrations failed"
        docker-compose logs kong-migrations
        exit 1
    fi

    # Run migrations up
    print_info "Running Kong migrations up..."
    docker-compose up -d kong-migrations-up

    # Wait for migrations up to complete
    timeout=120
    elapsed=0
    while docker-compose ps kong-migrations-up | grep -q "Up"; do
        if [ $elapsed -ge $timeout ]; then
            print_error "Migrations up failed to complete within $timeout seconds"
            exit 1
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done

    if docker-compose ps kong-migrations-up | grep -q "Exit 0"; then
        print_success "Migrations up completed successfully"
    else
        print_error "Migrations up failed"
        docker-compose logs kong-migrations-up
        exit 1
    fi

    # Start Kong
    print_info "Starting Kong Gateway..."
    docker-compose up -d kong
fi

# Wait for Kong to be healthy
print_info "Waiting for Kong to be healthy..."
timeout=120
elapsed=0
while ! docker-compose exec -T kong kong health >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        print_error "Kong failed to start within $timeout seconds"
        docker-compose logs kong
        exit 1
    fi
    sleep 3
    elapsed=$((elapsed + 3))
    echo -n "."
done
echo ""
print_success "Kong is healthy"

# Sync declarative config if in DB mode
if [ "$KONG_MODE" != "off" ]; then
    print_info "Syncing declarative configuration to database..."
    if docker-compose exec -T kong kong config db_import /etc/kong/kong.yml; then
        print_success "Declarative config synced successfully"
    else
        print_warning "Failed to sync declarative config. Kong is running but config may be incomplete."
    fi
fi

# ============================================================================
# Step 4: Start additional services
# الخطوة 4: بدء الخدمات الإضافية
# ============================================================================

print_info "Starting Konga admin UI..."
docker-compose up -d konga

print_info "Starting monitoring stack (Prometheus, Grafana)..."
docker-compose up -d prometheus grafana

print_info "Starting metrics exporters..."
docker-compose up -d postgres-exporter redis-exporter node-exporter

print_info "Starting Alertmanager..."
docker-compose up -d alertmanager

# ============================================================================
# Step 5: Wait for all services to be healthy
# الخطوة 5: انتظار جميع الخدمات حتى تصبح سليمة
# ============================================================================

print_info "Waiting for all services to be healthy..."
sleep 10

# Check Konga
timeout=120
elapsed=0
while ! curl -s http://localhost:1337 >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        print_warning "Konga may not be ready yet, but continuing..."
        break
    fi
    sleep 3
    elapsed=$((elapsed + 3))
done

if curl -s http://localhost:1337 >/dev/null 2>&1; then
    print_success "Konga is ready"
fi

# Check Prometheus
if curl -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
    print_success "Prometheus is healthy"
else
    print_warning "Prometheus may not be ready yet"
fi

# Check Grafana
if curl -s http://localhost:3002/api/health >/dev/null 2>&1; then
    print_success "Grafana is healthy"
else
    print_warning "Grafana may not be ready yet"
fi

# ============================================================================
# Step 6: Display status and access information
# الخطوة 6: عرض الحالة ومعلومات الوصول
# ============================================================================

echo ""
print_success "=====================================================
Kong API Gateway started successfully!
بوابة Kong API بدأت بنجاح!
====================================================="
echo ""
print_info "Access URLs:"
echo ""
echo "  Kong Proxy HTTP:       http://localhost:8000"
echo "  Kong Proxy HTTPS:      https://localhost:8443"
echo "  Kong Admin API:        http://localhost:8001"
echo "  Konga Admin UI:        http://localhost:1337"
echo "  Prometheus:            http://localhost:9090"
echo "  Grafana:               http://localhost:3002"
echo "  Alertmanager:          http://localhost:9093"
echo ""
print_info "Health Check:"
echo "  curl http://localhost:8000/health"
echo ""
print_info "View logs:"
echo "  docker-compose logs -f kong"
echo ""
print_info "Stop services:"
echo "  docker-compose down"
echo ""

# Test health endpoint
print_info "Testing Kong health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [ "$HEALTH_RESPONSE" = "SAHOOL Platform is healthy" ]; then
    print_success "Health check passed: $HEALTH_RESPONSE"
else
    print_warning "Health check returned unexpected response: $HEALTH_RESPONSE"
fi

echo ""
print_success "Startup complete! Kong is ready to accept requests."
