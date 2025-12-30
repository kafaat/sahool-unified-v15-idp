#!/bin/bash

# ============================================================================
# CORS Configuration Applier Script
# سكريبت تطبيق تكوين CORS
# ============================================================================
# This script applies the appropriate CORS configuration based on environment
# هذا السكريبت يطبق تكوين CORS المناسب بناءً على البيئة
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KONG_DIR="$(dirname "$SCRIPT_DIR")"
CORS_CONFIG_DIR="${KONG_DIR}/cors-config"

# ============================================================================
# Functions
# ============================================================================

print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_header() {
    echo ""
    echo "============================================================================"
    echo " $1"
    echo "============================================================================"
    echo ""
}

# ============================================================================
# Validate environment variable
# ============================================================================

validate_environment() {
    local env="${1:-}"

    case "$env" in
        development|staging|production)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# ============================================================================
# Apply CORS configuration
# ============================================================================

apply_cors_config() {
    local environment="${1}"
    local cors_file="${CORS_CONFIG_DIR}/cors-${environment}.yml"

    print_header "Applying CORS Configuration for ${environment} environment"

    # Check if CORS config file exists
    if [[ ! -f "$cors_file" ]]; then
        print_error "CORS configuration file not found: ${cors_file}"
        exit 1
    fi

    print_info "Using CORS configuration: ${cors_file}"

    # Read CORS configuration
    if ! command -v yq &> /dev/null; then
        print_warning "yq not found. Installing yq..."

        # Install yq based on OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
            chmod +x /usr/local/bin/yq
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install yq
        else
            print_error "Unsupported OS. Please install yq manually."
            exit 1
        fi

        print_success "yq installed successfully"
    fi

    # Parse CORS configuration
    print_info "Parsing CORS configuration..."

    local origins=$(yq eval '.cors.origins[]' "$cors_file" 2>/dev/null | paste -sd "," -)
    local methods=$(yq eval '.cors.methods[]' "$cors_file" 2>/dev/null | paste -sd "," -)
    local headers=$(yq eval '.cors.headers[]' "$cors_file" 2>/dev/null | paste -sd "," -)
    local exposed_headers=$(yq eval '.cors.exposed_headers[]' "$cors_file" 2>/dev/null | paste -sd "," -)
    local credentials=$(yq eval '.cors.credentials' "$cors_file" 2>/dev/null)
    local max_age=$(yq eval '.cors.max_age' "$cors_file" 2>/dev/null)

    # Display configuration summary
    print_info "CORS Configuration Summary:"
    echo "  - Environment: ${environment}"
    echo "  - Origins: ${origins}"
    echo "  - Methods: ${methods}"
    echo "  - Credentials: ${credentials}"
    echo "  - Max Age: ${max_age}s"
    echo ""

    # Export environment variables for Kong
    export KONG_CORS_ORIGINS="${origins}"
    export KONG_CORS_METHODS="${methods}"
    export KONG_CORS_HEADERS="${headers}"
    export KONG_CORS_EXPOSED_HEADERS="${exposed_headers}"
    export KONG_CORS_CREDENTIALS="${credentials}"
    export KONG_CORS_MAX_AGE="${max_age}"

    # Create a temporary environment file
    local env_file="${KONG_DIR}/.cors.env"
    cat > "$env_file" <<EOF
# Auto-generated CORS configuration for ${environment} environment
# Generated at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
KONG_CORS_ORIGINS=${origins}
KONG_CORS_METHODS=${methods}
KONG_CORS_HEADERS=${headers}
KONG_CORS_EXPOSED_HEADERS=${exposed_headers}
KONG_CORS_CREDENTIALS=${credentials}
KONG_CORS_MAX_AGE=${max_age}
EOF

    print_success "CORS configuration applied successfully"
    print_info "Environment variables saved to: ${env_file}"

    # Optionally reload Kong if it's running
    if docker ps | grep -q kong-gateway; then
        print_info "Kong gateway is running. Reloading configuration..."

        if docker exec kong-gateway kong reload 2>/dev/null; then
            print_success "Kong configuration reloaded successfully"
        else
            print_warning "Failed to reload Kong. You may need to restart Kong manually."
        fi
    else
        print_warning "Kong gateway is not running. Configuration will be applied on next startup."
    fi

    echo ""
    print_success "CORS configuration for '${environment}' environment applied successfully!"
    echo ""
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Load environment from .env file or use argument
    local environment="${CORS_ENVIRONMENT:-${1:-}}"

    # If no environment specified, try to detect from .env
    if [[ -z "$environment" ]] && [[ -f "${KONG_DIR}/.env" ]]; then
        print_info "Loading environment from .env file..."
        source "${KONG_DIR}/.env"
        environment="${CORS_ENVIRONMENT:-}"
    fi

    # If still no environment, use default
    if [[ -z "$environment" ]]; then
        environment="development"
        print_warning "No environment specified. Using default: ${environment}"
    fi

    # Validate environment
    if ! validate_environment "$environment"; then
        print_error "Invalid environment: ${environment}"
        echo ""
        echo "Usage: $0 [environment]"
        echo ""
        echo "Valid environments:"
        echo "  - development"
        echo "  - staging"
        echo "  - production"
        echo ""
        echo "Alternatively, set CORS_ENVIRONMENT environment variable."
        exit 1
    fi

    # Apply CORS configuration
    apply_cors_config "$environment"
}

# Run main function
main "$@"
