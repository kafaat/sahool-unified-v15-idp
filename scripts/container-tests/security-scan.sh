#!/bin/bash

################################################################################
# Docker Security Scan Script
# Description: Run Trivy security scanner on all Docker images
# Usage: ./security-scan.sh [--severity LEVEL] [--format FORMAT]
################################################################################

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Configuration
TRIVY_VERSION="${TRIVY_VERSION:-0.48.0}"
SEVERITY="${SEVERITY:-CRITICAL,HIGH,MEDIUM}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-table}"
REPORT_DIR="${PROJECT_ROOT}/security-reports"
SCAN_TYPE="${SCAN_TYPE:-image}"
FAIL_ON_SEVERITY="${FAIL_ON_SEVERITY:-CRITICAL,HIGH}"
IGNORE_UNFIXED=false
EXIT_CODE=0

# Scan tracking
declare -a SCANNED_IMAGES=()
declare -a VULNERABLE_IMAGES=()
declare -a SCAN_FAILURES=()

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
# Check and Install Trivy
################################################################################

check_trivy() {
    if command -v trivy &> /dev/null; then
        log_success "Trivy is installed: $(trivy --version | head -n1)"
        return 0
    fi

    log_warning "Trivy is not installed. Installing..."
    install_trivy
}

install_trivy() {
    local OS
    local ARCH
    local INSTALL_DIR="${HOME}/.local/bin"

    # Detect OS
    case "$(uname -s)" in
        Linux*)     OS="Linux";;
        Darwin*)    OS="macOS";;
        *)          log_error "Unsupported OS"; exit 1;;
    esac

    # Detect architecture
    case "$(uname -m)" in
        x86_64)     ARCH="64bit";;
        arm64)      ARCH="ARM64";;
        aarch64)    ARCH="ARM64";;
        *)          log_error "Unsupported architecture"; exit 1;;
    esac

    # Create install directory
    mkdir -p "${INSTALL_DIR}"

    # Download and install Trivy
    local DOWNLOAD_URL="https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_${OS}-${ARCH}.tar.gz"

    log_info "Downloading Trivy from ${DOWNLOAD_URL}"

    local TEMP_DIR
    TEMP_DIR=$(mktemp -d)

    if command -v curl &> /dev/null; then
        curl -sL "${DOWNLOAD_URL}" | tar -xz -C "${TEMP_DIR}"
    elif command -v wget &> /dev/null; then
        wget -q "${DOWNLOAD_URL}" -O - | tar -xz -C "${TEMP_DIR}"
    else
        log_error "Neither curl nor wget is available"
        exit 1
    fi

    mv "${TEMP_DIR}/trivy" "${INSTALL_DIR}/trivy"
    chmod +x "${INSTALL_DIR}/trivy"
    rm -rf "${TEMP_DIR}"

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
        export PATH="${INSTALL_DIR}:${PATH}"
        log_info "Added ${INSTALL_DIR} to PATH for this session"
    fi

    log_success "Trivy installed successfully"
}

################################################################################
# Get all Docker images to scan
################################################################################

get_docker_images() {
    local images=()

    # Get all sahool images
    while IFS= read -r image; do
        images+=("$image")
    done < <(docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "^sahool/|^${REGISTRY:-none}/" | grep -v "<none>" || true)

    printf '%s\n' "${images[@]}"
}

################################################################################
# Scan a single image
################################################################################

scan_image() {
    local image="$1"
    local image_name
    local report_file

    # Sanitize image name for filename
    image_name=$(echo "${image}" | sed 's/[^a-zA-Z0-9._-]/_/g')
    report_file="${REPORT_DIR}/${image_name}_$(date +%Y%m%d_%H%M%S)"

    log_info "Scanning ${CYAN}${image}${NC}"

    # Build Trivy arguments
    local trivy_args=(
        "image"
        "--severity" "${SEVERITY}"
        "--format" "${OUTPUT_FORMAT}"
    )

    if [[ "${IGNORE_UNFIXED}" == "true" ]]; then
        trivy_args+=("--ignore-unfixed")
    fi

    # Add exit code on severity
    if [[ -n "${FAIL_ON_SEVERITY}" ]]; then
        trivy_args+=("--exit-code" "1")
        trivy_args+=("--severity" "${FAIL_ON_SEVERITY}")
    fi

    # Scan the image
    local scan_output
    local scan_exit_code=0

    # Run scan and capture output
    if scan_output=$(trivy "${trivy_args[@]}" "${image}" 2>&1); then
        scan_exit_code=0
    else
        scan_exit_code=$?
    fi

    # Save report
    echo "${scan_output}" > "${report_file}.txt"

    # Also generate JSON report
    trivy image --severity "${SEVERITY}" --format json --output "${report_file}.json" "${image}" 2>/dev/null || true

    # Display results
    if [[ ${scan_exit_code} -eq 0 ]]; then
        log_success "✓ ${image} - No vulnerabilities found (or below threshold)"
        SCANNED_IMAGES+=("${image}")
    else
        log_error "✗ ${image} - Vulnerabilities found!"
        echo "${scan_output}"
        VULNERABLE_IMAGES+=("${image}")
        EXIT_CODE=1
    fi

    log_info "Report saved to: ${report_file}.{txt,json}"
    echo ""

    return ${scan_exit_code}
}

################################################################################
# Scan filesystem/repository
################################################################################

scan_filesystem() {
    local target="${1:-${PROJECT_ROOT}}"
    local report_file="${REPORT_DIR}/filesystem_scan_$(date +%Y%m%d_%H%M%S)"

    log_info "Scanning filesystem: ${target}"

    trivy fs \
        --severity "${SEVERITY}" \
        --format "${OUTPUT_FORMAT}" \
        --output "${report_file}.txt" \
        "${target}"

    trivy fs \
        --severity "${SEVERITY}" \
        --format json \
        --output "${report_file}.json" \
        "${target}"

    log_info "Filesystem scan report saved to: ${report_file}.{txt,json}"
}

################################################################################
# Run all scans
################################################################################

run_scans() {
    local images
    mapfile -t images < <(get_docker_images)

    if [[ ${#images[@]} -eq 0 ]]; then
        log_warning "No Docker images found to scan"
        log_info "Build images first using: ./build-all.sh"
        return 0
    fi

    log_info "Found ${#images[@]} image(s) to scan"
    echo ""

    for image in "${images[@]}"; do
        scan_image "${image}" || true
    done
}

################################################################################
# Generate summary report
################################################################################

generate_summary() {
    local summary_file="${REPORT_DIR}/scan_summary_$(date +%Y%m%d_%H%M%S).md"

    print_header "Security Scan Summary"

    echo "Total Images Scanned:  ${#SCANNED_IMAGES[@]}"
    echo -e "Clean Images:          ${GREEN}$((${#SCANNED_IMAGES[@]} - ${#VULNERABLE_IMAGES[@]}))${NC}"
    echo -e "Vulnerable Images:     ${RED}${#VULNERABLE_IMAGES[@]}${NC}"
    echo ""

    # Create markdown summary
    cat > "${summary_file}" << EOF
# Security Scan Summary

**Date:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Severity Levels:** ${SEVERITY}
**Fail Threshold:** ${FAIL_ON_SEVERITY}

## Overview

- Total Images Scanned: ${#SCANNED_IMAGES[@]}
- Clean Images: $((${#SCANNED_IMAGES[@]} - ${#VULNERABLE_IMAGES[@]}))
- Vulnerable Images: ${#VULNERABLE_IMAGES[@]}

EOF

    if [[ ${#VULNERABLE_IMAGES[@]} -gt 0 ]]; then
        cat >> "${summary_file}" << EOF
## Vulnerable Images

$(for img in "${VULNERABLE_IMAGES[@]}"; do echo "- \`${img}\`"; done)

## Recommendations

1. Review the detailed reports for each vulnerable image
2. Update base images to latest stable versions
3. Update application dependencies
4. Consider using distroless or alpine-based images
5. Implement regular security scanning in CI/CD pipeline

EOF
        log_error "Found ${#VULNERABLE_IMAGES[@]} vulnerable image(s)"
        echo ""
        echo "Vulnerable images:"
        for img in "${VULNERABLE_IMAGES[@]}"; do
            echo "  - ${img}"
        done
    else
        cat >> "${summary_file}" << EOF
## Results

✅ All scanned images are free of vulnerabilities at the specified severity levels.

EOF
        log_success "All images passed security scan!"
    fi

    echo ""
    log_info "Summary report saved to: ${summary_file}"
    echo ""
    log_info "All detailed reports available in: ${REPORT_DIR}/"
}

################################################################################
# Update Trivy database
################################################################################

update_trivy_db() {
    log_info "Updating Trivy vulnerability database..."
    trivy image --download-db-only
    log_success "Database updated successfully"
}

################################################################################
# Clean old reports
################################################################################

clean_old_reports() {
    local days="${1:-7}"

    log_info "Cleaning reports older than ${days} days..."

    find "${REPORT_DIR}" -type f -mtime "+${days}" -delete 2>/dev/null || true

    log_success "Old reports cleaned"
}

################################################################################
# Usage
################################################################################

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Run Trivy security scanner on Docker images.

OPTIONS:
    -h, --help                  Show this help message
    -s, --severity LEVELS       Severity levels to scan (default: CRITICAL,HIGH,MEDIUM)
    -f, --format FORMAT         Output format: table, json, sarif (default: table)
    -t, --type TYPE             Scan type: image, fs (default: image)
    --fail-on LEVELS            Fail on severity levels (default: CRITICAL,HIGH)
    --ignore-unfixed            Ignore unfixed vulnerabilities
    --update-db                 Update Trivy database before scanning
    --filesystem PATH           Scan filesystem/repository instead of images
    --clean-reports DAYS        Clean reports older than N days (default: 7)

EXAMPLES:
    $(basename "$0")                                    # Scan all images
    $(basename "$0") --severity CRITICAL,HIGH           # Scan for critical/high only
    $(basename "$0") --format json                      # Output as JSON
    $(basename "$0") --filesystem .                     # Scan current directory
    $(basename "$0") --update-db                        # Update DB first
    $(basename "$0") --ignore-unfixed                   # Ignore unfixed CVEs

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
            -s|--severity)
                SEVERITY="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -t|--type)
                SCAN_TYPE="$2"
                shift 2
                ;;
            --fail-on)
                FAIL_ON_SEVERITY="$2"
                shift 2
                ;;
            --ignore-unfixed)
                IGNORE_UNFIXED=true
                shift
                ;;
            --update-db)
                update_trivy_db
                shift
                ;;
            --filesystem)
                SCAN_TYPE="fs"
                FILESYSTEM_PATH="$2"
                shift 2
                ;;
            --clean-reports)
                clean_old_reports "$2"
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
    print_header "Docker Security Scanner (Trivy)"

    # Parse arguments
    parse_args "$@"

    # Check/install Trivy
    check_trivy

    # Create report directory
    mkdir -p "${REPORT_DIR}"

    # Change to project root
    cd "${PROJECT_ROOT}"

    # Run scans based on type
    if [[ "${SCAN_TYPE}" == "fs" ]]; then
        scan_filesystem "${FILESYSTEM_PATH:-${PROJECT_ROOT}}"
    else
        run_scans
        generate_summary
    fi

    # Exit with appropriate code
    if [[ ${EXIT_CODE} -eq 0 ]]; then
        log_success "Security scan completed successfully!"
        exit 0
    else
        log_error "Security scan found vulnerabilities!"
        exit 1
    fi
}

# Run main function
main "$@"
