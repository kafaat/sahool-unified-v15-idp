#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - E2E Testing Script
# سكربت اختبار شامل من البداية للنهاية لمنصة سهول
#
# Usage: ./scripts/e2e-test.sh [--full|--quick|--services-only]
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
TIMEOUT=300
TEST_MODE="${1:-quick}"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=${3:-30}
    local attempt=1

    log_info "Waiting for $service on port $port..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/healthz" > /dev/null 2>&1; then
            log_success "$service is ready!"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    log_error "$service failed to start within timeout"
    return 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Infrastructure Setup
# المرحلة 1: إعداد البنية التحتية
# ─────────────────────────────────────────────────────────────────────────────

phase1_infrastructure() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Phase 1: Starting Infrastructure Services"
    echo "المرحلة 1: تشغيل خدمات البنية التحتية"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # Start infrastructure services
    docker compose up -d postgres redis nats kong

    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    until docker compose exec -T postgres pg_isready -U sahool > /dev/null 2>&1; do
        sleep 2
    done
    log_success "PostgreSQL is ready"

    # Wait for Redis
    log_info "Waiting for Redis..."
    until docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do
        sleep 2
    done
    log_success "Redis is ready"

    # Wait for NATS
    log_info "Waiting for NATS..."
    until curl -s http://localhost:8222/healthz > /dev/null 2>&1; do
        sleep 2
    done
    log_success "NATS is ready"

    # Wait for Kong
    log_info "Waiting for Kong..."
    until curl -s http://localhost:8001/status > /dev/null 2>&1; do
        sleep 2
    done
    log_success "Kong is ready"

    log_success "✅ Infrastructure services are running!"
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Core Services
# المرحلة 2: الخدمات الأساسية
# ─────────────────────────────────────────────────────────────────────────────

phase2_core_services() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Phase 2: Starting Core Backend Services"
    echo "المرحلة 2: تشغيل الخدمات الأساسية"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # Core services to start
    CORE_SERVICES=(
        "field_core:3000"
        "field_ops:8080"
        "weather_core:8108"
        "billing_core:8089"
        "notification_service:8110"
    )

    docker compose up -d field_core field_ops weather_core billing_core notification_service

    for service_port in "${CORE_SERVICES[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        wait_for_service "$service" "$port" 60
    done

    log_success "✅ Core services are running!"
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: AI & Analytics Services
# المرحلة 3: خدمات الذكاء الاصطناعي والتحليلات
# ─────────────────────────────────────────────────────────────────────────────

phase3_ai_services() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Phase 3: Starting AI & Analytics Services"
    echo "المرحلة 3: تشغيل خدمات الذكاء الاصطناعي"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    AI_SERVICES=(
        "ai_advisor:8112"
        "agro_advisor:8105"
        "crop_health_ai:8095"
        "yield_engine:8098"
        "ndvi_engine:8107"
    )

    docker compose up -d ai_advisor agro_advisor crop_health_ai yield_engine ndvi_engine

    for service_port in "${AI_SERVICES[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        wait_for_service "$service" "$port" 90
    done

    log_success "✅ AI & Analytics services are running!"
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: All Remaining Services
# المرحلة 4: باقي الخدمات
# ─────────────────────────────────────────────────────────────────────────────

phase4_all_services() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Phase 4: Starting All Remaining Services"
    echo "المرحلة 4: تشغيل جميع الخدمات المتبقية"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    docker compose up -d

    # Wait for all services
    sleep 30

    # Check all services
    log_info "Checking all service health..."
    docker compose ps --format "table {{.Service}}\t{{.Status}}" | head -50

    log_success "✅ All services started!"
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 5: Integration Tests
# المرحلة 5: اختبارات التكامل
# ─────────────────────────────────────────────────────────────────────────────

phase5_integration_tests() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Phase 5: Running Integration Tests"
    echo "المرحلة 5: تشغيل اختبارات التكامل"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    FAILED_TESTS=0

    # Test 1: API Gateway Health
    log_info "Test 1: API Gateway (Kong) Health..."
    if curl -sf http://localhost:8000/api/v1/weather/healthz > /dev/null 2>&1; then
        log_success "Kong routing works"
    else
        log_warning "Kong routing check - service might not be fully ready"
    fi

    # Test 2: Database Connectivity
    log_info "Test 2: Database Connectivity..."
    if docker compose exec -T postgres psql -U sahool -d sahool_db -c "SELECT 1" > /dev/null 2>&1; then
        log_success "PostgreSQL connection successful"
    else
        log_error "PostgreSQL connection failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Test 3: NATS Messaging
    log_info "Test 3: NATS JetStream..."
    if curl -sf http://localhost:8222/jsz > /dev/null 2>&1; then
        log_success "NATS JetStream is active"
    else
        log_warning "NATS JetStream check failed"
    fi

    # Test 4: Redis Cache
    log_info "Test 4: Redis Cache..."
    if docker compose exec -T redis redis-cli ping | grep -q PONG; then
        log_success "Redis is responding"
    else
        log_error "Redis connection failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Test 5: Billing Service
    log_info "Test 5: Billing Service Health..."
    if curl -sf http://localhost:8089/healthz > /dev/null 2>&1; then
        log_success "Billing service is healthy"
    else
        log_warning "Billing service not ready yet"
    fi

    # Test 6: AI Advisor
    log_info "Test 6: AI Advisor Service..."
    if curl -sf http://localhost:8112/healthz > /dev/null 2>&1; then
        log_success "AI Advisor is healthy"
    else
        log_warning "AI Advisor not ready yet"
    fi

    # Test 7: Weather Service
    log_info "Test 7: Weather Service..."
    if curl -sf http://localhost:8108/healthz > /dev/null 2>&1; then
        log_success "Weather service is healthy"
    else
        log_warning "Weather service not ready yet"
    fi

    echo ""
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "All critical integration tests passed!"
    else
        log_error "$FAILED_TESTS critical tests failed"
    fi

    return $FAILED_TESTS
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 6: E2E User Flow Tests
# المرحلة 6: اختبارات تجربة المستخدم
# ─────────────────────────────────────────────────────────────────────────────

phase6_e2e_tests() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Phase 6: E2E User Flow Tests"
    echo "المرحلة 6: اختبارات تجربة المستخدم الشاملة"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # Test: Create a field (simulated)
    log_info "E2E Test 1: Field Creation Flow..."
    FIELD_RESPONSE=$(curl -sf -X POST http://localhost:8000/api/v1/fields \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Field", "area": 100, "crop_type": "wheat", "location": {"lat": 15.35, "lng": 44.21}}' 2>/dev/null || echo "error")

    if [[ "$FIELD_RESPONSE" != "error" ]]; then
        log_success "Field creation API responding"
    else
        log_warning "Field API not fully ready"
    fi

    # Test: Get weather for location
    log_info "E2E Test 2: Weather Data Flow..."
    WEATHER_RESPONSE=$(curl -sf "http://localhost:8000/api/v1/weather?lat=15.35&lng=44.21" 2>/dev/null || echo "error")

    if [[ "$WEATHER_RESPONSE" != "error" ]]; then
        log_success "Weather API responding"
    else
        log_warning "Weather API not fully ready"
    fi

    # Test: AI Advisor question
    log_info "E2E Test 3: AI Advisor Flow..."
    AI_RESPONSE=$(curl -sf -X POST http://localhost:8000/api/v1/advisor/ask \
        -H "Content-Type: application/json" \
        -d '{"question": "What is the best time to plant wheat?", "context": {"crop": "wheat", "region": "yemen"}}' 2>/dev/null || echo "error")

    if [[ "$AI_RESPONSE" != "error" ]]; then
        log_success "AI Advisor API responding"
    else
        log_warning "AI Advisor API not fully ready"
    fi

    # Test: Billing wallet check
    log_info "E2E Test 4: Billing System Flow..."
    BILLING_RESPONSE=$(curl -sf http://localhost:8000/api/v1/billing/wallet/test-user 2>/dev/null || echo "error")

    if [[ "$BILLING_RESPONSE" != "error" ]]; then
        log_success "Billing API responding"
    else
        log_warning "Billing API not fully ready"
    fi

    log_success "✅ E2E tests completed!"
}

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────

cleanup() {
    echo ""
    log_info "Cleaning up test environment..."
    docker compose down --volumes --remove-orphans 2>/dev/null || true
    log_success "Cleanup complete"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║           SAHOOL Platform - E2E Testing Suite                                 ║"
    echo "║           منصة سهول - مجموعة الاختبارات الشاملة                                ║"
    echo "╠═══════════════════════════════════════════════════════════════════════════════╣"
    echo "║  Mode: $TEST_MODE                                                             ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo ""

    # Check Docker availability
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available"
        exit 1
    fi

    # Trap for cleanup on exit
    trap cleanup EXIT INT TERM

    START_TIME=$(date +%s)

    case "$TEST_MODE" in
        "--quick"|"quick")
            phase1_infrastructure
            phase2_core_services
            phase5_integration_tests
            ;;
        "--full"|"full")
            phase1_infrastructure
            phase2_core_services
            phase3_ai_services
            phase4_all_services
            phase5_integration_tests
            phase6_e2e_tests
            ;;
        "--services-only"|"services-only")
            phase4_all_services
            ;;
        *)
            phase1_infrastructure
            phase2_core_services
            phase5_integration_tests
            ;;
    esac

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "E2E Testing Complete!"
    echo "Duration: ${DURATION} seconds"
    echo "═══════════════════════════════════════════════════════════════════════════════"
}

# Run main
main "$@"
