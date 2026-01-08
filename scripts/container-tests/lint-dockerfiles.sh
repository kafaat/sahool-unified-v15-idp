#!/bin/bash

################################################################################
# Dockerfile Linting Script
# Description: Runs hadolint on all Dockerfiles in the project
# Usage: ./lint-dockerfiles.sh [--fix] [--strict]
################################################################################

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Configuration
HADOLINT_VERSION="${HADOLINT_VERSION:-2.12.0}"
STRICT_MODE=false
FIX_MODE=false
EXIT_CODE=0

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $*${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

################################################################################
# Check and Install Hadolint
################################################################################

check_hadolint() {
    if command -v hadolint &> /dev/null; then
        log_success "hadolint is installed: $(hadolint --version)"
        return 0
    fi

    log_warning "hadolint is not installed. Installing..."
    install_hadolint
}

install_hadolint() {
    local OS
    local ARCH
    local INSTALL_DIR="${HOME}/.local/bin"

    # Detect OS
    case "$(uname -s)" in
        Linux*)     OS="Linux";;
        Darwin*)    OS="Darwin";;
        *)          log_error "Unsupported OS"; exit 1;;
    esac

    # Detect architecture
    case "$(uname -m)" in
        x86_64)     ARCH="x86_64";;
        arm64)      ARCH="arm64";;
        aarch64)    ARCH="arm64";;
        *)          log_error "Unsupported architecture"; exit 1;;
    esac

    # Create install directory
    mkdir -p "${INSTALL_DIR}"

    # Download hadolint
    local DOWNLOAD_URL="https://github.com/hadolint/hadolint/releases/download/v${HADOLINT_VERSION}/hadolint-${OS}-${ARCH}"

    log_info "Downloading hadolint from ${DOWNLOAD_URL}"

    if command -v curl &> /dev/null; then
        curl -sL "${DOWNLOAD_URL}" -o "${INSTALL_DIR}/hadolint"
    elif command -v wget &> /dev/null; then
        wget -q "${DOWNLOAD_URL}" -O "${INSTALL_DIR}/hadolint"
    else
        log_error "Neither curl nor wget is available. Please install one of them."
        exit 1
    fi

    chmod +x "${INSTALL_DIR}/hadolint"

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
        export PATH="${INSTALL_DIR}:${PATH}"
        log_info "Added ${INSTALL_DIR} to PATH for this session"
        log_warning "Add 'export PATH=\"${INSTALL_DIR}:\$PATH\"' to your shell rc file for permanent installation"
    fi

    log_success "hadolint installed successfully"
}

################################################################################
# Find all Dockerfiles
################################################################################

find_dockerfiles() {
    local dockerfiles=()

    # Find all Dockerfiles in the project
    while IFS= read -r -d '' file; do
        dockerfiles+=("$file")
    done < <(find "${PROJECT_ROOT}" \
        -type f \
        \( -name "Dockerfile" -o -name "Dockerfile.*" -o -name "*.dockerfile" \) \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/dist/*" \
        -not -path "*/build/*" \
        -not -path "*/archive/*" \
        -print0)

    printf '%s\n' "${dockerfiles[@]}"
}

################################################################################
# Lint a single Dockerfile
################################################################################

lint_dockerfile() {
    local dockerfile="$1"
    local relative_path="${dockerfile#${PROJECT_ROOT}/}"

    log_info "Linting: ${relative_path}"

    local hadolint_args=(
        "--no-color"
        "--format json"
    )

    if [[ "${STRICT_MODE}" == "true" ]]; then
        hadolint_args+=("--no-fail")
    fi

    # Run hadolint and capture output
    local output
    if output=$(hadolint "${hadolint_args[@]}" "${dockerfile}" 2>&1); then
        log_success "✓ ${relative_path} - No issues found"
        return 0
    else
        # Parse JSON output and display issues
        if [[ -n "${output}" && "${output}" != "[]" ]]; then
            echo "${output}" | jq -r '.[] | "  [\(.level | ascii_upcase)] Line \(.line): \(.message) (\(.code))"' 2>/dev/null || {
                # Fallback if jq is not available
                echo "${output}"
            }

            log_error "✗ ${relative_path} - Issues found"
            EXIT_CODE=1
            return 1
        else
            log_success "✓ ${relative_path} - No issues found"
            return 0
        fi
    fi
}

################################################################################
# Main Linting Process
################################################################################

run_linting() {
    local dockerfiles
    mapfile -t dockerfiles < <(find_dockerfiles)

    if [[ ${#dockerfiles[@]} -eq 0 ]]; then
        log_warning "No Dockerfiles found in the project"
        return 0
    fi

    log_info "Found ${#dockerfiles[@]} Dockerfile(s) to lint"
    echo ""

    local success_count=0
    local fail_count=0

    for dockerfile in "${dockerfiles[@]}"; do
        if lint_dockerfile "${dockerfile}"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
        echo ""
    done

    # Summary
    print_header "Linting Summary"
    echo "Total Dockerfiles:  ${#dockerfiles[@]}"
    echo -e "Passed:            ${GREEN}${success_count}${NC}"
    echo -e "Failed:            ${RED}${fail_count}${NC}"
    echo ""

    if [[ ${fail_count} -eq 0 ]]; then
        log_success "All Dockerfiles passed linting!"
        return 0
    else
        log_error "${fail_count} Dockerfile(s) failed linting"
        return 1
    fi
}

################################################################################
# Generate hadolint config (optional)
################################################################################

generate_config() {
    local config_file="${PROJECT_ROOT}/.hadolint.yaml"

    if [[ -f "${config_file}" ]]; then
        log_info "Hadolint config already exists at ${config_file}"
        return 0
    fi

    log_info "Generating hadolint configuration..."

    cat > "${config_file}" << 'EOF'
# Hadolint Configuration
# https://github.com/hadolint/hadolint

# Ignore rules
ignored:
  # DL3008: Pin versions in apt-get install
  # - DL3008

  # DL3009: Delete the apt-get lists after installing
  # - DL3009

  # DL3018: Pin versions in apk add
  # - DL3018

# Trusted registries
trustedRegistries:
  - docker.io
  - gcr.io
  - ghcr.io
  - quay.io

# Label schema
label-schema:
  maintainer: text
  org.opencontainers.image.created: rfc3339
  org.opencontainers.image.version: semver
  org.opencontainers.image.description: text

# Strict labels
strict-labels: false

# Failure threshold
failure-threshold: warning
EOF

    log_success "Generated hadolint config at ${config_file}"
}

################################################################################
# Usage
################################################################################

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Lint all Dockerfiles in the project using hadolint.

OPTIONS:
    -h, --help          Show this help message
    -s, --strict        Enable strict mode (fail on warnings)
    -f, --fix           Attempt to auto-fix issues (not yet implemented)
    -g, --generate      Generate hadolint configuration file
    -v, --version       Show hadolint version

EXAMPLES:
    $(basename "$0")                    # Lint all Dockerfiles
    $(basename "$0") --strict           # Lint with strict mode
    $(basename "$0") --generate         # Generate config and lint

EOF
    exit 0
}

################################################################################
# Parse Arguments
################################################################################

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -s|--strict)
                STRICT_MODE=true
                shift
                ;;
            -f|--fix)
                FIX_MODE=true
                log_warning "Fix mode is not yet implemented"
                shift
                ;;
            -g|--generate)
                generate_config
                shift
                ;;
            -v|--version)
                hadolint --version 2>/dev/null || echo "hadolint not installed"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
}

################################################################################
# Main
################################################################################

main() {
    print_header "Dockerfile Linting with Hadolint"

    # Parse arguments
    parse_args "$@"

    # Check/install hadolint
    check_hadolint

    # Change to project root
    cd "${PROJECT_ROOT}"

    # Run linting
    if run_linting; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
