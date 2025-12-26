#!/bin/bash

# ============================================================================
# SAHOOL Platform - Kong API Gateway Setup Script
# منصة سهول - سكريبت إعداد بوابة Kong API
# ============================================================================
# This script sets up and configures Kong API Gateway for SAHOOL platform
# يقوم هذا السكريبت بإعداد وتكوين بوابة Kong API لمنصة سهول
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
KONG_ADMIN_URL="http://localhost:8001"
MAX_RETRIES=30
RETRY_INTERVAL=5

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}"
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================================================
# Check Prerequisites
# ============================================================================

check_prerequisites() {
    print_header "Checking Prerequisites | فحص المتطلبات الأساسية"

    # Check for Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        print_error "Docker غير مثبت. يرجى تثبيت Docker أولاً."
        exit 1
    fi
    print_success "Docker is installed"

    # Check for Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        print_error "Docker Compose غير مثبت. يرجى تثبيت Docker Compose أولاً."
        exit 1
    fi
    print_success "Docker Compose is installed"

    # Check for curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install curl first."
        exit 1
    fi
    print_success "curl is installed"

    # Check for jq
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some features may not work properly."
        print_warning "jq غير مثبت. قد لا تعمل بعض الميزات بشكل صحيح."
    else
        print_success "jq is installed"
    fi
}

# ============================================================================
# Generate Environment File
# ============================================================================

generate_env_file() {
    print_header "Generating Environment File | إنشاء ملف البيئة"

    if [ -f "$ENV_FILE" ]; then
        print_warning "Environment file already exists at $ENV_FILE"
        print_warning "ملف البيئة موجود بالفعل في $ENV_FILE"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping environment file generation"
            return 0
        fi
    fi

    # Generate random secrets
    print_info "Generating JWT secrets..."
    STARTER_SECRET=$(openssl rand -base64 32)
    PROFESSIONAL_SECRET=$(openssl rand -base64 32)
    ENTERPRISE_SECRET=$(openssl rand -base64 32)
    RESEARCH_SECRET=$(openssl rand -base64 32)
    ADMIN_SECRET=$(openssl rand -base64 32)
    SERVICE_SECRET=$(openssl rand -base64 32)
    TRIAL_SECRET=$(openssl rand -base64 32)

    POSTGRES_PASSWORD=$(openssl rand -base64 16)
    GRAFANA_PASSWORD=$(openssl rand -base64 16)
    REDIS_PASSWORD=$(openssl rand -base64 16)

    # Create .env file from template
    cp "${SCRIPT_DIR}/.env.example" "$ENV_FILE"

    # Replace placeholders with actual values
    sed -i "s|STARTER_JWT_SECRET=.*|STARTER_JWT_SECRET=${STARTER_SECRET}|g" "$ENV_FILE"
    sed -i "s|PROFESSIONAL_JWT_SECRET=.*|PROFESSIONAL_JWT_SECRET=${PROFESSIONAL_SECRET}|g" "$ENV_FILE"
    sed -i "s|ENTERPRISE_JWT_SECRET=.*|ENTERPRISE_JWT_SECRET=${ENTERPRISE_SECRET}|g" "$ENV_FILE"
    sed -i "s|RESEARCH_JWT_SECRET=.*|RESEARCH_JWT_SECRET=${RESEARCH_SECRET}|g" "$ENV_FILE"
    sed -i "s|ADMIN_JWT_SECRET=.*|ADMIN_JWT_SECRET=${ADMIN_SECRET}|g" "$ENV_FILE"
    sed -i "s|SERVICE_JWT_SECRET=.*|SERVICE_JWT_SECRET=${SERVICE_SECRET}|g" "$ENV_FILE"
    sed -i "s|TRIAL_JWT_SECRET=.*|TRIAL_JWT_SECRET=${TRIAL_SECRET}|g" "$ENV_FILE"

    sed -i "s|KONG_PG_PASSWORD=.*|KONG_PG_PASSWORD=${POSTGRES_PASSWORD}|g" "$ENV_FILE"
    sed -i "s|GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=${GRAFANA_PASSWORD}|g" "$ENV_FILE"
    sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|g" "$ENV_FILE"

    print_success "Environment file generated at $ENV_FILE"
    print_warning "Please review and update the values as needed"
    print_warning "يرجى مراجعة وتحديث القيم حسب الحاجة"
}

# ============================================================================
# Start Kong Services
# ============================================================================

start_kong_services() {
    print_header "Starting Kong Services | بدء خدمات Kong"

    cd "$SCRIPT_DIR"

    # Pull images
    print_info "Pulling Docker images..."
    docker-compose pull

    # Start services
    print_info "Starting services..."
    docker-compose up -d

    print_success "Kong services started"
}

# ============================================================================
# Wait for Kong to be Ready
# ============================================================================

wait_for_kong() {
    print_header "Waiting for Kong to be Ready | انتظار جاهزية Kong"

    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -s -f "$KONG_ADMIN_URL/status" > /dev/null 2>&1; then
            print_success "Kong is ready!"
            return 0
        fi

        retries=$((retries + 1))
        print_info "Waiting for Kong... Attempt $retries/$MAX_RETRIES"
        sleep $RETRY_INTERVAL
    done

    print_error "Kong failed to start within the expected time"
    print_error "فشل بدء Kong في الوقت المتوقع"
    exit 1
}

# ============================================================================
# Apply Kong Configuration
# ============================================================================

apply_kong_config() {
    print_header "Applying Kong Configuration | تطبيق تكوين Kong"

    # Check if deck is installed
    if command -v deck &> /dev/null; then
        print_info "Using deck to apply configuration..."

        # Validate configurations
        print_info "Validating kong.yml..."
        deck validate -s "${SCRIPT_DIR}/kong.yml" || print_warning "Validation failed for kong.yml"

        print_info "Validating kong-packages.yml..."
        deck validate -s "${SCRIPT_DIR}/kong-packages.yml" || print_warning "Validation failed for kong-packages.yml"

        print_info "Validating consumers.yml..."
        deck validate -s "${SCRIPT_DIR}/consumers.yml" || print_warning "Validation failed for consumers.yml"

        # Sync configurations
        print_info "Syncing configurations..."
        deck sync -s "${SCRIPT_DIR}/kong.yml" --kong-addr "$KONG_ADMIN_URL"
        deck sync -s "${SCRIPT_DIR}/kong-packages.yml" --kong-addr "$KONG_ADMIN_URL"
        deck sync -s "${SCRIPT_DIR}/consumers.yml" --kong-addr "$KONG_ADMIN_URL"

        print_success "Configuration applied using deck"
    else
        print_warning "deck is not installed. Using manual configuration..."
        print_info "You can install deck with: brew install kong/deck/deck"

        # Manual configuration using Kong Admin API
        print_info "Applying configuration manually is not fully supported in this script."
        print_info "Please install deck or configure Kong manually through the Admin API."
    fi
}

# ============================================================================
# Verify Kong Configuration
# ============================================================================

verify_kong_config() {
    print_header "Verifying Kong Configuration | التحقق من تكوين Kong"

    # Check services
    print_info "Checking services..."
    local services_count=$(curl -s "$KONG_ADMIN_URL/services" | jq -r '.data | length' 2>/dev/null || echo "0")
    print_info "Services configured: $services_count"

    # Check routes
    print_info "Checking routes..."
    local routes_count=$(curl -s "$KONG_ADMIN_URL/routes" | jq -r '.data | length' 2>/dev/null || echo "0")
    print_info "Routes configured: $routes_count"

    # Check consumers
    print_info "Checking consumers..."
    local consumers_count=$(curl -s "$KONG_ADMIN_URL/consumers" | jq -r '.data | length' 2>/dev/null || echo "0")
    print_info "Consumers configured: $consumers_count"

    # Check plugins
    print_info "Checking plugins..."
    local plugins_count=$(curl -s "$KONG_ADMIN_URL/plugins" | jq -r '.data | length' 2>/dev/null || echo "0")
    print_info "Plugins configured: $plugins_count"

    if [ "$services_count" -gt 0 ] && [ "$routes_count" -gt 0 ]; then
        print_success "Kong configuration verified successfully!"
    else
        print_warning "Kong may not be fully configured. Please check manually."
    fi
}

# ============================================================================
# Test Health Endpoint
# ============================================================================

test_health_endpoint() {
    print_header "Testing Health Endpoint | اختبار نقطة فحص الصحة"

    local response=$(curl -s "http://localhost:8000/health")

    if [ -n "$response" ]; then
        print_success "Health endpoint is responding"
        print_info "Response: $response"
    else
        print_error "Health endpoint is not responding"
    fi
}

# ============================================================================
# Print Summary
# ============================================================================

print_summary() {
    print_header "Setup Complete! | اكتمل الإعداد!"

    echo ""
    echo "Kong API Gateway URLs:"
    echo "  • Proxy HTTP:    http://localhost:8000"
    echo "  • Proxy HTTPS:   https://localhost:8443"
    echo "  • Admin API:     http://localhost:8001"
    echo "  • Health Check:  http://localhost:8000/health"
    echo ""
    echo "Kong Admin UI (Konga):"
    echo "  • URL:           http://localhost:1337"
    echo ""
    echo "Monitoring:"
    echo "  • Prometheus:    http://localhost:9090"
    echo "  • Grafana:       http://localhost:3002"
    echo "    Default credentials: admin / (check .env file)"
    echo ""
    echo "Next Steps:"
    echo "  1. Review the configuration files"
    echo "  2. Test the API endpoints"
    echo "  3. Configure Grafana dashboards"
    echo "  4. Set up alerts in Prometheus"
    echo ""
    echo "Useful Commands:"
    echo "  • View logs:     docker-compose logs -f kong"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart:       docker-compose restart kong"
    echo ""
    print_info "For more information, see README.md"
    print_info "لمزيد من المعلومات، راجع README.md"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    clear

    print_header "SAHOOL Platform - Kong API Gateway Setup"
    print_header "منصة سهول - إعداد بوابة Kong API"

    check_prerequisites
    generate_env_file
    start_kong_services
    wait_for_kong
    apply_kong_config
    verify_kong_config
    test_health_endpoint
    print_summary
}

# Run main function
main "$@"
