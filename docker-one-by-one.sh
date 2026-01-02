#!/usr/bin/env bash
# ================================================================================
# Docker Compose Build and Up - One by One
# Builds and starts Docker containers sequentially to avoid resource conflicts
# ================================================================================
# This script is particularly useful for:
# - M1/M2 Mac machines with limited resources
# - Development environments with memory constraints
# - Debugging individual service build/startup issues
# ================================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_separator() {
    echo "--------------------------------------------------------------------------------"
}

print_double_separator() {
    echo "================================================================================"
}

# Main script
print_double_separator
print_info "           Docker Compose - Build and Up (One by One)                        "
print_double_separator
echo ""

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "ERROR: docker-compose.yml not found in current directory"
    exit 1
fi

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    print_error "ERROR: docker command not found"
    print_error "Please ensure Docker is installed and running"
    exit 1
fi

# Check docker compose version
if ! docker compose version &> /dev/null; then
    print_error "ERROR: docker compose command not available"
    print_error "Please ensure Docker Compose v2 is installed"
    exit 1
fi

# Get list of services from docker-compose.yml
print_info "Getting list of services from docker-compose.yml..."
if ! services=$(docker compose config --services 2>&1); then
    print_error "ERROR: Failed to parse docker-compose.yml"
    print_error "$services"
    exit 1
fi

# Filter out warnings and empty lines
services=$(echo "$services" | grep -v "^WARN" | grep -v "^$" || true)

if [ -z "$services" ]; then
    print_error "ERROR: No services found in docker-compose.yml"
    exit 1
fi

# Convert services to array
mapfile -t service_array <<< "$services"
service_count=${#service_array[@]}

print_success "Found $service_count service(s)"
echo ""

# ================================================================================
# Phase 1: Build containers (one by one)
# ================================================================================

print_double_separator
print_info "PHASE 1: Building containers (--no-cache)"
print_double_separator
echo ""

build_failures=()
build_count=0

for service in "${service_array[@]}"; do
    ((build_count++)) || true
    print_info "[$build_count/$service_count] Building: $service"
    print_separator
    
    if docker compose build --no-cache "$service" 2>&1; then
        print_success "[OK] Successfully built: $service"
    else
        print_error "[FAIL] Failed to build: $service"
        build_failures+=("$service")
    fi
    
    echo ""
done

# Summary of build phase
print_double_separator
print_info "Build Phase Summary"
print_double_separator
print_success "Successfully built: $((service_count - ${#build_failures[@]}))/$service_count"

if [ ${#build_failures[@]} -gt 0 ]; then
    print_warning "Failed builds: ${#build_failures[@]}"
    for failed in "${build_failures[@]}"; do
        print_warning "  - $failed"
    done
    echo ""
    read -p "Some builds failed. Continue with 'up' phase anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Exiting..."
        exit 1
    fi
fi
echo ""

# ================================================================================
# Phase 2: Start containers (one by one)
# ================================================================================

print_double_separator
print_info "PHASE 2: Starting containers (up -d)"
print_double_separator
echo ""

up_failures=()
up_count=0

for service in "${service_array[@]}"; do
    ((up_count++)) || true
    print_info "[$up_count/$service_count] Starting: $service"
    print_separator
    
    if docker compose up -d "$service" 2>&1; then
        print_success "[OK] Successfully started: $service"
    else
        print_error "[FAIL] Failed to start: $service"
        up_failures+=("$service")
    fi
    
    echo ""
done

# Final Summary
print_double_separator
print_info "Final Summary"
print_double_separator
print_success "Builds completed: $((service_count - ${#build_failures[@]}))/$service_count"
print_success "Containers started: $((service_count - ${#up_failures[@]}))/$service_count"

if [ ${#build_failures[@]} -gt 0 ]; then
    print_warning "Build failures:"
    for failed in "${build_failures[@]}"; do
        print_warning "  - $failed"
    done
fi

if [ ${#up_failures[@]} -gt 0 ]; then
    print_warning "Start failures:"
    for failed in "${up_failures[@]}"; do
        print_warning "  - $failed"
    done
fi

echo ""
print_info "Check container status with: docker compose ps"
print_info "View logs with: docker compose logs [service-name]"
echo ""

if [ ${#build_failures[@]} -eq 0 ] && [ ${#up_failures[@]} -eq 0 ]; then
    print_success "All operations completed successfully!"
    exit 0
else
    print_warning "Some operations had failures. Review the output above."
    exit 1
fi
