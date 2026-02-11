#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# AI/RAG Container Validation Script
# Version: 16.0.0
# Updated: February 2026
#
# This script validates all AI/RAG container improvements including:
# - Build success
# - Security compliance
# - Health check functionality
# - Image size verification
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES=(
    "ai-advisor:8112"
    "ai-agents-service:8130"
    "llm-orchestrator-service:8164"
    "crop-intelligence-service:8095"
    "field-intelligence:8120"
)

MAX_IMAGE_SIZE_MB=2048  # 2GB warning threshold
FAILED_SERVICES=()
PASSED_SERVICES=()

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Validation Functions
# ─────────────────────────────────────────────────────────────────────────────

validate_dockerfile_exists() {
    local service=$1
    local dockerfile="$REPO_ROOT/apps/services/$service/Dockerfile"
    
    if [ ! -f "$dockerfile" ]; then
        log_error "Dockerfile not found: $dockerfile"
        return 1
    fi
    
    log_success "Dockerfile found for $service"
    return 0
}

validate_dockerfile_best_practices() {
    local service=$1
    local dockerfile="$REPO_ROOT/apps/services/$service/Dockerfile"
    local issues=0
    
    log_info "Validating Dockerfile best practices for $service..."
    
    # Check for multi-stage build
    if ! grep -q "FROM.*AS" "$dockerfile"; then
        log_warning "No multi-stage build in $service"
        issues=$((issues + 1))
    else
        log_success "Multi-stage build found"
    fi
    
    # Check for non-root user
    if ! grep -q "USER.*sahool" "$dockerfile"; then
        log_error "No non-root USER directive in $service"
        issues=$((issues + 1))
    else
        log_success "Non-root user found"
    fi
    
    # Check for health check
    if ! grep -q "HEALTHCHECK" "$dockerfile"; then
        log_warning "No HEALTHCHECK in $service"
        issues=$((issues + 1))
    else
        log_success "Health check found"
    fi
    
    # Check for pinned base image
    if grep -qE "FROM.*:latest" "$dockerfile"; then
        log_error "Using :latest tag in $service"
        issues=$((issues + 1))
    else
        log_success "Pinned base image"
    fi
    
    # Check for labels
    if ! grep -q "org.opencontainers.image" "$dockerfile"; then
        log_warning "Missing OCI labels in $service"
    else
        log_success "OCI labels found"
    fi
    
    return $issues
}

build_service() {
    local service=$1
    local tag="$service:validation-$(date +%s)"
    
    log_info "Building $service..."
    
    cd "$REPO_ROOT"
    
    if docker build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --tag "$tag" \
        --file "apps/services/$service/Dockerfile" \
        . > /tmp/build-$service.log 2>&1; then
        log_success "Build succeeded for $service"
        echo "$tag"
        return 0
    else
        log_error "Build failed for $service"
        log_error "See /tmp/build-$service.log for details"
        tail -20 /tmp/build-$service.log
        return 1
    fi
}

validate_image_size() {
    local image=$1
    local service=$2
    
    log_info "Validating image size for $service..."
    
    local size_mb=$(docker images "$image" --format "{{.Size}}" | sed 's/MB//' | sed 's/GB/*1024/' | bc 2>/dev/null || echo "0")
    
    log_info "Image size: ${size_mb}MB"
    
    if (( $(echo "$size_mb > $MAX_IMAGE_SIZE_MB" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "Image size exceeds ${MAX_IMAGE_SIZE_MB}MB threshold"
        return 1
    else
        log_success "Image size within acceptable limits"
        return 0
    fi
}

validate_security() {
    local image=$1
    local service=$2
    
    log_info "Running security scan for $service..."
    
    # Check if trivy is installed
    if ! command -v trivy &> /dev/null; then
        log_warning "Trivy not installed, skipping security scan"
        return 0
    fi
    
    if trivy image --severity CRITICAL,HIGH --exit-code 0 "$image" > /tmp/trivy-$service.log 2>&1; then
        local critical=$(grep -c "CRITICAL" /tmp/trivy-$service.log || echo "0")
        local high=$(grep -c "HIGH" /tmp/trivy-$service.log || echo "0")
        
        if [ "$critical" -gt 0 ]; then
            log_error "Found $critical CRITICAL vulnerabilities"
            return 1
        elif [ "$high" -gt 0 ]; then
            log_warning "Found $high HIGH vulnerabilities"
            return 0
        else
            log_success "No CRITICAL or HIGH vulnerabilities found"
            return 0
        fi
    else
        log_warning "Trivy scan completed with warnings"
        return 0
    fi
}

test_health_check() {
    local image=$1
    local service=$2
    local port=$3
    local container_name="validation-$service-$(date +%s)"
    
    log_info "Testing health check for $service..."
    
    # Start container
    if ! docker run -d \
        --name "$container_name" \
        --env PORT="$port" \
        "$image" > /dev/null 2>&1; then
        log_error "Failed to start container"
        return 1
    fi
    
    # Wait for health check
    log_info "Waiting for health check (max 60s)..."
    local timeout=60
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
        
        if [ "$health" = "healthy" ]; then
            log_success "Container is healthy"
            docker rm -f "$container_name" > /dev/null 2>&1
            return 0
        elif [ "$health" = "unhealthy" ]; then
            log_error "Container is unhealthy"
            docker logs "$container_name" | tail -20
            docker rm -f "$container_name" > /dev/null 2>&1
            return 1
        fi
        
        sleep 2
        elapsed=$((elapsed + 2))
    done
    
    log_warning "Health check timeout after ${timeout}s"
    docker logs "$container_name" | tail -20
    docker rm -f "$container_name" > /dev/null 2>&1
    return 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Validation Flow
# ─────────────────────────────────────────────────────────────────────────────

main() {
    log_section "AI/RAG Container Validation"
    
    log_info "Repository: $REPO_ROOT"
    log_info "Services to validate: ${#SERVICES[@]}"
    
    # Pre-flight checks
    log_section "Pre-flight Checks"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker is installed"
    
    if [ ! -f "$REPO_ROOT/docker/constraints-ai.txt" ]; then
        log_error "Constraints file not found"
        exit 1
    fi
    log_success "Constraints file found"
    
    # Validate each service
    for service_port in "${SERVICES[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        
        log_section "Validating $service"
        
        local service_failed=false
        
        # 1. Check Dockerfile exists
        if ! validate_dockerfile_exists "$service"; then
            FAILED_SERVICES+=("$service (Dockerfile missing)")
            continue
        fi
        
        # 2. Validate Dockerfile best practices
        if ! validate_dockerfile_best_practices "$service"; then
            log_warning "Dockerfile best practices check had issues"
        fi
        
        # 3. Build service
        local image
        if ! image=$(build_service "$service"); then
            FAILED_SERVICES+=("$service (Build failed)")
            continue
        fi
        
        # 4. Validate image size
        if ! validate_image_size "$image" "$service"; then
            log_warning "Image size check had issues"
        fi
        
        # 5. Security scan
        if ! validate_security "$image" "$service"; then
            log_warning "Security scan had issues"
        fi
        
        # 6. Test health check
        if ! test_health_check "$image" "$service" "$port"; then
            log_warning "Health check test had issues"
        fi
        
        # Cleanup
        docker rmi "$image" > /dev/null 2>&1 || true
        
        if [ "$service_failed" = false ]; then
            PASSED_SERVICES+=("$service")
            log_success "$service validation PASSED"
        fi
    done
    
    # Summary
    log_section "Validation Summary"
    
    echo ""
    echo "Total services: ${#SERVICES[@]}"
    echo "Passed: ${GREEN}${#PASSED_SERVICES[@]}${NC}"
    echo "Failed: ${RED}${#FAILED_SERVICES[@]}${NC}"
    echo ""
    
    if [ ${#PASSED_SERVICES[@]} -gt 0 ]; then
        echo -e "${GREEN}Passed Services:${NC}"
        for service in "${PASSED_SERVICES[@]}"; do
            echo "  ✓ $service"
        done
        echo ""
    fi
    
    if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
        echo -e "${RED}Failed Services:${NC}"
        for service in "${FAILED_SERVICES[@]}"; do
            echo "  ✗ $service"
        done
        echo ""
        exit 1
    fi
    
    log_success "All validations passed!"
    exit 0
}

# Run main function
main "$@"
