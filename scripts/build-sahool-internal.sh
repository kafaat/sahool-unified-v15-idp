#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Internal Environment Build Script with Comprehensive Logging
# سكريبت بناء منصة سهول للبيئة الداخلية مع تسجيل شامل
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: Sahool DevOps Team
# Date: $(date +%Y-%m-%d)
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Configuration / التكوين
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="${PROJECT_ROOT}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Log files
BUILD_LOG="${LOGS_DIR}/build_${TIMESTAMP}.log"
ERROR_LOG="${LOGS_DIR}/errors_${TIMESTAMP}.log"
SUMMARY_LOG="${LOGS_DIR}/summary_${TIMESTAMP}.log"
COMBINED_LOG="${LOGS_DIR}/sahool_build_${TIMESTAMP}.log"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Build counters
BUILD_SUCCESS=0
BUILD_FAILED=0
BUILD_WARNINGS=0
FAILED_SERVICES=()

# ─────────────────────────────────────────────────────────────────────────────
# Logging Functions / دوال التسجيل
# ─────────────────────────────────────────────────────────────────────────────
init_logging() {
    mkdir -p "${LOGS_DIR}"

    # Create log files with headers
    cat > "${BUILD_LOG}" << EOF
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Build Log - سجل بناء منصة سهول
Build Started: $(date)
Environment: Internal / البيئة الداخلية
═══════════════════════════════════════════════════════════════════════════════

EOF

    cat > "${ERROR_LOG}" << EOF
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Error Log - سجل أخطاء منصة سهول
Build Started: $(date)
═══════════════════════════════════════════════════════════════════════════════

EOF

    cat > "${COMBINED_LOG}" << EOF
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Combined Build Log
منصة سهول - سجل البناء الموحد
═══════════════════════════════════════════════════════════════════════════════
Build ID: ${TIMESTAMP}
Started: $(date)
Project Root: ${PROJECT_ROOT}
═══════════════════════════════════════════════════════════════════════════════

EOF
}

log_info() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${BLUE}[INFO]${NC} [${timestamp}] ${message}"
    echo "[INFO] [${timestamp}] ${message}" >> "${BUILD_LOG}"
    echo "[INFO] [${timestamp}] ${message}" >> "${COMBINED_LOG}"
}

log_success() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${GREEN}[SUCCESS]${NC} [${timestamp}] ${message}"
    echo "[SUCCESS] [${timestamp}] ${message}" >> "${BUILD_LOG}"
    echo "[SUCCESS] [${timestamp}] ${message}" >> "${COMBINED_LOG}"
}

log_warning() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${YELLOW}[WARNING]${NC} [${timestamp}] ${message}"
    echo "[WARNING] [${timestamp}] ${message}" >> "${BUILD_LOG}"
    echo "[WARNING] [${timestamp}] ${message}" >> "${COMBINED_LOG}"
    ((BUILD_WARNINGS++))
}

log_error() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${RED}[ERROR]${NC} [${timestamp}] ${message}"
    echo "[ERROR] [${timestamp}] ${message}" >> "${BUILD_LOG}"
    echo "[ERROR] [${timestamp}] ${message}" >> "${ERROR_LOG}"
    echo "[ERROR] [${timestamp}] ${message}" >> "${COMBINED_LOG}"
}

log_step() {
    local step_name="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}[STEP]${NC} ${step_name}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo "" >> "${BUILD_LOG}"
    echo "═══════════════════════════════════════════════════════════════" >> "${BUILD_LOG}"
    echo "[STEP] [${timestamp}] ${step_name}" >> "${BUILD_LOG}"
    echo "═══════════════════════════════════════════════════════════════" >> "${BUILD_LOG}"
    echo "" >> "${COMBINED_LOG}"
    echo "═══════════════════════════════════════════════════════════════" >> "${COMBINED_LOG}"
    echo "[STEP] [${timestamp}] ${step_name}" >> "${COMBINED_LOG}"
    echo "═══════════════════════════════════════════════════════════════" >> "${COMBINED_LOG}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Environment Check / فحص البيئة
# ─────────────────────────────────────────────────────────────────────────────
check_prerequisites() {
    log_step "Checking Prerequisites / فحص المتطلبات الأساسية"

    local has_errors=0

    # Check Docker
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version 2>/dev/null)
        log_success "Docker installed: ${docker_version}"
    else
        log_error "Docker is not installed or not in PATH"
        log_error "Docker غير مثبت أو غير موجود في PATH"
        has_errors=1
    fi

    # Check Docker Compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        if docker compose version &> /dev/null; then
            local compose_version=$(docker compose version 2>/dev/null)
            log_success "Docker Compose (V2) installed: ${compose_version}"
        else
            local compose_version=$(docker-compose --version 2>/dev/null)
            log_success "Docker Compose (V1) installed: ${compose_version}"
        fi
    else
        log_error "Docker Compose is not installed"
        log_error "Docker Compose غير مثبت"
        has_errors=1
    fi

    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        log_success "Docker daemon is running"
    else
        log_error "Docker daemon is not running"
        log_error "خدمة Docker غير تعمل"
        has_errors=1
    fi

    # Check .env file
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        log_success ".env file exists"
    else
        log_warning ".env file not found. Creating from .env.example..."
        if [[ -f "${PROJECT_ROOT}/.env.example" ]]; then
            cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
            log_success "Created .env from .env.example"
            log_warning "Please update .env with your actual values"
        else
            log_error ".env.example not found"
            has_errors=1
        fi
    fi

    # Check docker-compose.yml
    if [[ -f "${PROJECT_ROOT}/docker-compose.yml" ]]; then
        log_success "docker-compose.yml exists"
    else
        log_error "docker-compose.yml not found"
        has_errors=1
    fi

    return $has_errors
}

# ─────────────────────────────────────────────────────────────────────────────
# Build Functions / دوال البناء
# ─────────────────────────────────────────────────────────────────────────────
build_infrastructure() {
    log_step "Building Infrastructure Services / بناء خدمات البنية التحتية"

    local infra_services=("postgres" "pgbouncer" "redis" "nats")

    for service in "${infra_services[@]}"; do
        log_info "Starting ${service}..."

        if docker compose up -d "${service}" 2>> "${ERROR_LOG}"; then
            log_success "${service} started successfully"
            ((BUILD_SUCCESS++))
        else
            log_error "Failed to start ${service}"
            FAILED_SERVICES+=("${service}")
            ((BUILD_FAILED++))
        fi
    done

    # Wait for infrastructure to be healthy
    log_info "Waiting for infrastructure services to be healthy..."
    sleep 10
}

build_core_services() {
    log_step "Building Core Application Services / بناء الخدمات الأساسية"

    local core_services=(
        "user-service"
        "field-service"
        "weather-service"
        "field-core"
        "field-ops"
    )

    for service in "${core_services[@]}"; do
        build_single_service "${service}"
    done
}

build_ai_services() {
    log_step "Building AI & Analytics Services / بناء خدمات الذكاء الاصطناعي"

    local ai_services=(
        "ai-advisor"
        "crop-health-ai"
        "agro-advisor"
        "yield-prediction"
        "ndvi-engine"
    )

    for service in "${ai_services[@]}"; do
        build_single_service "${service}"
    done
}

build_integration_services() {
    log_step "Building Integration Services / بناء خدمات التكامل"

    local integration_services=(
        "iot-service"
        "notification-service"
        "chat-service"
        "ws-gateway"
    )

    for service in "${integration_services[@]}"; do
        build_single_service "${service}"
    done
}

build_single_service() {
    local service="$1"
    local start_time=$(date +%s)

    log_info "Building ${service}..."

    # Build the service
    if docker compose build --no-cache "${service}" >> "${BUILD_LOG}" 2>> "${ERROR_LOG}"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_success "${service} built successfully (${duration}s)"
        ((BUILD_SUCCESS++))

        # Try to start the service
        log_info "Starting ${service}..."
        if docker compose up -d "${service}" >> "${BUILD_LOG}" 2>> "${ERROR_LOG}"; then
            log_success "${service} started successfully"
        else
            log_warning "${service} built but failed to start"
            FAILED_SERVICES+=("${service}:start")
        fi
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_error "${service} build FAILED after ${duration}s"
        FAILED_SERVICES+=("${service}")
        ((BUILD_FAILED++))

        # Capture detailed error
        echo "" >> "${ERROR_LOG}"
        echo "─────────────────────────────────────────────────────────" >> "${ERROR_LOG}"
        echo "Service: ${service}" >> "${ERROR_LOG}"
        echo "Time: $(date)" >> "${ERROR_LOG}"
        docker compose logs "${service}" 2>/dev/null >> "${ERROR_LOG}" || true
        echo "─────────────────────────────────────────────────────────" >> "${ERROR_LOG}"
    fi
}

build_all_services() {
    log_step "Building All Services / بناء جميع الخدمات"

    log_info "Running docker compose build..."

    if docker compose build 2>&1 | tee -a "${BUILD_LOG}"; then
        log_success "All services built successfully"
    else
        log_warning "Some services may have failed to build. Check error log."
    fi

    log_info "Starting all services..."

    if docker compose up -d 2>&1 | tee -a "${BUILD_LOG}"; then
        log_success "All services started"
    else
        log_warning "Some services may have failed to start. Check error log."
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Health Check / فحص الصحة
# ─────────────────────────────────────────────────────────────────────────────
check_services_health() {
    log_step "Checking Services Health / فحص صحة الخدمات"

    local healthy=0
    local unhealthy=0
    local starting=0

    # Get all running containers
    while IFS= read -r line; do
        local container_name=$(echo "$line" | awk '{print $1}')
        local status=$(echo "$line" | awk '{print $2}')

        case "$status" in
            "healthy")
                log_success "${container_name}: healthy"
                ((healthy++))
                ;;
            "unhealthy")
                log_error "${container_name}: unhealthy"
                ((unhealthy++))
                # Get logs for unhealthy container
                docker logs --tail 50 "${container_name}" 2>&1 >> "${ERROR_LOG}" || true
                ;;
            "starting")
                log_warning "${container_name}: still starting..."
                ((starting++))
                ;;
            *)
                log_info "${container_name}: ${status}"
                ;;
        esac
    done < <(docker ps --format "{{.Names}} {{.Status}}" 2>/dev/null | grep sahool || true)

    log_info "Health Summary: ${healthy} healthy, ${unhealthy} unhealthy, ${starting} starting"
}

collect_all_logs() {
    log_step "Collecting Container Logs / جمع سجلات الحاويات"

    local container_logs_dir="${LOGS_DIR}/containers_${TIMESTAMP}"
    mkdir -p "${container_logs_dir}"

    docker compose ps -q 2>/dev/null | while read -r container_id; do
        local container_name=$(docker inspect --format '{{.Name}}' "$container_id" 2>/dev/null | sed 's/^\///')
        if [[ -n "$container_name" ]]; then
            log_info "Collecting logs for ${container_name}..."
            docker logs "$container_id" > "${container_logs_dir}/${container_name}.log" 2>&1 || true
        fi
    done

    log_success "Container logs saved to: ${container_logs_dir}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Summary Generation / إنشاء الملخص
# ─────────────────────────────────────────────────────────────────────────────
generate_summary() {
    log_step "Generating Build Summary / إنشاء ملخص البناء"

    local end_time=$(date)

    cat > "${SUMMARY_LOG}" << EOF
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Build Summary - ملخص بناء منصة سهول
═══════════════════════════════════════════════════════════════════════════════

Build Information:
─────────────────────────────────────────────────────────────────────────────
Build ID:        ${TIMESTAMP}
Start Time:      ${BUILD_START_TIME}
End Time:        ${end_time}
Project Root:    ${PROJECT_ROOT}

Build Results:
─────────────────────────────────────────────────────────────────────────────
Successful:      ${BUILD_SUCCESS}
Failed:          ${BUILD_FAILED}
Warnings:        ${BUILD_WARNINGS}

EOF

    if [[ ${#FAILED_SERVICES[@]} -gt 0 ]]; then
        cat >> "${SUMMARY_LOG}" << EOF
Failed Services:
─────────────────────────────────────────────────────────────────────────────
EOF
        for service in "${FAILED_SERVICES[@]}"; do
            echo "  - ${service}" >> "${SUMMARY_LOG}"
        done
        echo "" >> "${SUMMARY_LOG}"
    fi

    cat >> "${SUMMARY_LOG}" << EOF
Log Files:
─────────────────────────────────────────────────────────────────────────────
Build Log:       ${BUILD_LOG}
Error Log:       ${ERROR_LOG}
Combined Log:    ${COMBINED_LOG}
Summary:         ${SUMMARY_LOG}

Running Containers:
─────────────────────────────────────────────────────────────────────────────
EOF

    docker compose ps 2>/dev/null >> "${SUMMARY_LOG}" || echo "Unable to get container status" >> "${SUMMARY_LOG}"

    cat >> "${SUMMARY_LOG}" << EOF

═══════════════════════════════════════════════════════════════════════════════
End of Build Summary
═══════════════════════════════════════════════════════════════════════════════
EOF

    # Display summary
    echo ""
    cat "${SUMMARY_LOG}"

    # Copy summary to combined log
    cat "${SUMMARY_LOG}" >> "${COMBINED_LOG}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function / الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────
main() {
    BUILD_START_TIME=$(date)

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}   SAHOOL Platform - Internal Environment Build${NC}"
    echo -e "${CYAN}   منصة سهول - بناء البيئة الداخلية${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""

    cd "${PROJECT_ROOT}"

    # Initialize logging
    init_logging
    log_info "Build started at ${BUILD_START_TIME}"
    log_info "Project root: ${PROJECT_ROOT}"
    log_info "Logs directory: ${LOGS_DIR}"

    # Check prerequisites
    if ! check_prerequisites; then
        log_error "Prerequisites check failed. Please fix the issues above and try again."
        log_error "فشل فحص المتطلبات. يرجى إصلاح المشاكل أعلاه والمحاولة مرة أخرى."
        generate_summary
        exit 1
    fi

    # Parse command line arguments
    local build_mode="${1:-all}"

    case "$build_mode" in
        "infra"|"infrastructure")
            build_infrastructure
            ;;
        "core")
            build_infrastructure
            build_core_services
            ;;
        "ai")
            build_ai_services
            ;;
        "integration")
            build_integration_services
            ;;
        "all"|"")
            build_all_services
            ;;
        "health")
            check_services_health
            ;;
        "logs")
            collect_all_logs
            ;;
        *)
            log_error "Unknown build mode: ${build_mode}"
            echo "Usage: $0 [infra|core|ai|integration|all|health|logs]"
            exit 1
            ;;
    esac

    # Check health after build
    if [[ "$build_mode" != "health" && "$build_mode" != "logs" ]]; then
        sleep 15
        check_services_health
        collect_all_logs
    fi

    # Generate summary
    generate_summary

    # Final status
    if [[ ${BUILD_FAILED} -eq 0 ]]; then
        log_success "Build completed successfully!"
        log_success "اكتمل البناء بنجاح!"
        exit 0
    else
        log_error "Build completed with ${BUILD_FAILED} failures"
        log_error "اكتمل البناء مع ${BUILD_FAILED} فشل"
        exit 1
    fi
}

# Run main function
main "$@"
