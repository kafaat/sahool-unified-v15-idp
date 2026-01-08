#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Vulnerability Scanning Script
# Scans containers, images, and dependencies for vulnerabilities
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/security"
REPORT_DIR="${PROJECT_ROOT}/reports/security"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/vulnerability-scan-${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/vulnerability-scan-${TIMESTAMP}.json"

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Logging
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
    echo -e "${BLUE}${msg}${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
    echo -e "${GREEN}${msg}${NC}" | tee -a "$LOG_FILE"
}

log_warn() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1"
    echo -e "${YELLOW}${msg}${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1"
    echo -e "${RED}${msg}${NC}" | tee -a "$LOG_FILE"
}

log_section() {
    local msg="$1"
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}  $msg${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# ─────────────────────────────────────────────────────────────────────────────
# Pre-flight Checks
# ─────────────────────────────────────────────────────────────────────────────

preflight_checks() {
    log_section "Pre-flight Checks"

    # Create directories
    mkdir -p "$LOG_DIR" "$REPORT_DIR"

    # Check if Docker is running
    if ! docker ps >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        exit 1
    fi

    log_success "Pre-flight checks completed"
}

# ─────────────────────────────────────────────────────────────────────────────
# Scanner Installation Functions
# ─────────────────────────────────────────────────────────────────────────────

install_trivy() {
    log_info "Checking for Trivy..."

    if command -v trivy &> /dev/null; then
        log_success "Trivy is already installed"
        return
    fi

    log_info "Installing Trivy..."

    # Detect OS
    local os_type
    os_type=$(uname -s | tr '[:upper:]' '[:lower:]')

    if [[ "$os_type" == "linux" ]]; then
        # Install Trivy on Linux
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        log_success "Trivy installed successfully"
    else
        log_warn "Automatic installation not supported on $os_type. Install manually from: https://github.com/aquasecurity/trivy"
    fi
}

install_grype() {
    log_info "Checking for Grype..."

    if command -v grype &> /dev/null; then
        log_success "Grype is already installed"
        return
    fi

    log_info "Installing Grype..."

    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
    log_success "Grype installed successfully"
}

install_snyk() {
    log_info "Checking for Snyk..."

    if command -v snyk &> /dev/null; then
        log_success "Snyk is already installed"
        return
    fi

    log_info "Installing Snyk..."

    if command -v npm &> /dev/null; then
        npm install -g snyk
        log_success "Snyk installed successfully"
    else
        log_warn "npm not found. Install Node.js first to use Snyk"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Vulnerability Scanning Functions
# ─────────────────────────────────────────────────────────────────────────────

scan_with_trivy() {
    log_section "Scanning with Trivy"

    if ! command -v trivy &> /dev/null; then
        log_warn "Trivy not installed, skipping..."
        return
    fi

    # Update Trivy database
    log_info "Updating Trivy vulnerability database..."
    trivy image --download-db-only 2>&1 | tee -a "$LOG_FILE"

    # Scan all running containers
    local containers
    containers=$(docker ps --format '{{.Names}}')

    if [[ -z "$containers" ]]; then
        log_warn "No running containers to scan"
        return
    fi

    while IFS= read -r container; do
        log_info "Scanning container: $container"

        local image
        image=$(docker inspect --format='{{.Config.Image}}' "$container" 2>/dev/null || echo "")

        if [[ -z "$image" ]]; then
            log_warn "Could not determine image for $container"
            continue
        fi

        # Scan image with Trivy
        local trivy_output="${REPORT_DIR}/trivy-${container}-${TIMESTAMP}.json"

        trivy image \
            --severity CRITICAL,HIGH,MEDIUM \
            --format json \
            --output "$trivy_output" \
            "$image" 2>&1 | tee -a "$LOG_FILE" || true

        # Generate summary
        if [[ -f "$trivy_output" ]]; then
            local critical_count high_count medium_count
            critical_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "$trivy_output" 2>/dev/null || echo "0")
            high_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "$trivy_output" 2>/dev/null || echo "0")
            medium_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' "$trivy_output" 2>/dev/null || echo "0")

            log_info "  Vulnerabilities: Critical=$critical_count, High=$high_count, Medium=$medium_count"

            if [[ "$critical_count" -gt 0 ]]; then
                log_error "  Found $critical_count CRITICAL vulnerabilities!"
            fi
        fi
    done <<< "$containers"

    log_success "Trivy scan completed"
}

scan_with_grype() {
    log_section "Scanning with Grype"

    if ! command -v grype &> /dev/null; then
        log_warn "Grype not installed, skipping..."
        return
    fi

    # Update Grype database
    log_info "Updating Grype vulnerability database..."
    grype db update 2>&1 | tee -a "$LOG_FILE" || true

    # Scan all running containers
    local containers
    containers=$(docker ps --format '{{.Names}}')

    if [[ -z "$containers" ]]; then
        log_warn "No running containers to scan"
        return
    fi

    while IFS= read -r container; do
        log_info "Scanning container: $container"

        local image
        image=$(docker inspect --format='{{.Config.Image}}' "$container" 2>/dev/null || echo "")

        if [[ -z "$image" ]]; then
            log_warn "Could not determine image for $container"
            continue
        fi

        # Scan image with Grype
        local grype_output="${REPORT_DIR}/grype-${container}-${TIMESTAMP}.json"

        grype "$image" \
            --output json \
            --file "$grype_output" 2>&1 | tee -a "$LOG_FILE" || true

        # Generate summary
        if [[ -f "$grype_output" ]]; then
            local critical_count high_count
            critical_count=$(jq '[.matches[]? | select(.vulnerability.severity=="Critical")] | length' "$grype_output" 2>/dev/null || echo "0")
            high_count=$(jq '[.matches[]? | select(.vulnerability.severity=="High")] | length' "$grype_output" 2>/dev/null || echo "0")

            log_info "  Vulnerabilities: Critical=$critical_count, High=$high_count"
        fi
    done <<< "$containers"

    log_success "Grype scan completed"
}

scan_dependencies_npm() {
    log_section "Scanning NPM Dependencies"

    # Find all package.json files
    local package_files
    package_files=$(find "$PROJECT_ROOT" -name "package.json" -not -path "*/node_modules/*" 2>/dev/null || echo "")

    if [[ -z "$package_files" ]]; then
        log_warn "No package.json files found"
        return
    fi

    while IFS= read -r package_file; do
        local package_dir
        package_dir=$(dirname "$package_file")

        log_info "Scanning: $package_file"

        # Run npm audit
        cd "$package_dir"
        npm audit --json > "${REPORT_DIR}/npm-audit-$(basename $package_dir)-${TIMESTAMP}.json" 2>&1 || true

        # Get summary
        local vulnerabilities
        vulnerabilities=$(npm audit --json 2>/dev/null | jq '.metadata.vulnerabilities' 2>/dev/null || echo "{}")

        if [[ "$vulnerabilities" != "{}" ]] && [[ "$vulnerabilities" != "null" ]]; then
            log_info "  Found vulnerabilities: $vulnerabilities"
        fi

        cd - > /dev/null
    done <<< "$package_files"

    log_success "NPM dependency scan completed"
}

scan_dependencies_python() {
    log_section "Scanning Python Dependencies"

    # Find all requirements.txt files
    local req_files
    req_files=$(find "$PROJECT_ROOT" -name "requirements.txt" -o -name "Pipfile" 2>/dev/null || echo "")

    if [[ -z "$req_files" ]]; then
        log_warn "No Python dependency files found"
        return
    fi

    # Check if safety is installed
    if ! command -v safety &> /dev/null; then
        log_info "Installing safety..."
        pip install safety 2>&1 | tee -a "$LOG_FILE" || true
    fi

    while IFS= read -r req_file; do
        if [[ -z "$req_file" ]]; then
            continue
        fi

        log_info "Scanning: $req_file"

        # Run safety check
        safety check -r "$req_file" --json > "${REPORT_DIR}/safety-$(basename $(dirname $req_file))-${TIMESTAMP}.json" 2>&1 || true
    done <<< "$req_files"

    log_success "Python dependency scan completed"
}

scan_docker_images() {
    log_section "Scanning Docker Images"

    # Get all images
    local images
    images=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>')

    if [[ -z "$images" ]]; then
        log_warn "No Docker images found"
        return
    fi

    log_info "Found $(echo "$images" | wc -l) images to scan"

    # Scan each image
    while IFS= read -r image; do
        log_info "Scanning image: $image"

        # Scan with Docker scan (if available)
        if command -v docker scan &> /dev/null; then
            docker scan "$image" 2>&1 | tee -a "$LOG_FILE" || true
        fi
    done <<< "$images"

    log_success "Docker image scan completed"
}

scan_secrets_in_code() {
    log_section "Scanning for Secrets in Code"

    # Check if gitleaks is installed
    if ! command -v gitleaks &> /dev/null; then
        log_info "Installing gitleaks..."
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz | tar -xz -C /usr/local/bin gitleaks || true
    fi

    if command -v gitleaks &> /dev/null; then
        log_info "Scanning for secrets with gitleaks..."

        gitleaks detect \
            --source "$PROJECT_ROOT" \
            --report-path "${REPORT_DIR}/gitleaks-${TIMESTAMP}.json" \
            --report-format json \
            --verbose 2>&1 | tee -a "$LOG_FILE" || true

        log_success "Secret scanning completed"
    else
        log_warn "gitleaks not available, skipping secret scan"
    fi
}

scan_infrastructure_as_code() {
    log_section "Scanning Infrastructure as Code"

    # Check if checkov is installed
    if ! command -v checkov &> /dev/null; then
        log_info "Installing checkov..."
        pip install checkov 2>&1 | tee -a "$LOG_FILE" || true
    fi

    if command -v checkov &> /dev/null; then
        log_info "Scanning with checkov..."

        # Scan docker-compose files
        checkov \
            --directory "$PROJECT_ROOT" \
            --framework docker-compose dockerfile \
            --output json \
            --output-file-path "${REPORT_DIR}" \
            --file-path "${REPORT_DIR}/checkov-${TIMESTAMP}.json" 2>&1 | tee -a "$LOG_FILE" || true

        log_success "IaC scanning completed"
    else
        log_warn "checkov not available, skipping IaC scan"
    fi
}

generate_summary_report() {
    log_section "Generating Summary Report"

    local summary_file="${REPORT_DIR}/vulnerability-summary-${TIMESTAMP}.md"

    cat > "$summary_file" <<EOF
# SAHOOL Vulnerability Scan Summary

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Platform:** SAHOOL Unified v15

---

## Scan Overview

This report summarizes vulnerability scans performed on the SAHOOL platform.

### Scan Types Performed

- Container Image Scanning (Trivy, Grype)
- Dependency Scanning (npm, pip, safety)
- Secret Detection (gitleaks)
- Infrastructure as Code (checkov)

---

## Findings

### Container Vulnerabilities

EOF

    # Aggregate Trivy results
    if ls "${REPORT_DIR}"/trivy-*-"${TIMESTAMP}".json >/dev/null 2>&1; then
        local total_critical=0
        local total_high=0
        local total_medium=0

        for trivy_file in "${REPORT_DIR}"/trivy-*-"${TIMESTAMP}".json; do
            local critical high medium
            critical=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "$trivy_file" 2>/dev/null || echo "0")
            high=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "$trivy_file" 2>/dev/null || echo "0")
            medium=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' "$trivy_file" 2>/dev/null || echo "0")

            total_critical=$((total_critical + critical))
            total_high=$((total_high + high))
            total_medium=$((total_medium + medium))
        done

        cat >> "$summary_file" <<EOF
| Severity | Count |
|----------|-------|
| Critical | $total_critical |
| High     | $total_high |
| Medium   | $total_medium |

EOF
    fi

    cat >> "$summary_file" <<EOF

### Dependency Vulnerabilities

Check individual scan reports in: \`${REPORT_DIR}\`

---

## Recommendations

### Immediate Actions

1. Review and patch all CRITICAL severity vulnerabilities
2. Update base images to latest secure versions
3. Remove any detected secrets from code
4. Update vulnerable dependencies

### Best Practices

1. Implement automated vulnerability scanning in CI/CD
2. Establish vulnerability management process
3. Regular dependency updates
4. Use minimal base images
5. Implement secret management solution

---

## Report Files

EOF

    # List all generated reports
    find "$REPORT_DIR" -name "*${TIMESTAMP}*" -type f | while read -r report; do
        echo "- \`$(basename $report)\`" >> "$summary_file"
    done

    log_success "Summary report generated: $summary_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat <<EOF
SAHOOL Vulnerability Scanning Script

Usage: $0 [OPTIONS]

Options:
    --help              Show this help message
    --full              Run all scans (default)
    --containers        Scan containers only
    --dependencies      Scan dependencies only
    --secrets           Scan for secrets only
    --iac               Scan infrastructure as code only
    --install-tools     Install scanning tools only

Examples:
    $0                      # Run all scans
    $0 --containers         # Scan containers only
    $0 --install-tools      # Install scanning tools

EOF
}

main() {
    local mode="full"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --full)
                mode="full"
                shift
                ;;
            --containers)
                mode="containers"
                shift
                ;;
            --dependencies)
                mode="dependencies"
                shift
                ;;
            --secrets)
                mode="secrets"
                shift
                ;;
            --iac)
                mode="iac"
                shift
                ;;
            --install-tools)
                mode="install"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "              SAHOOL Vulnerability Scanning"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    preflight_checks

    case $mode in
        install)
            install_trivy
            install_grype
            install_snyk
            ;;
        containers)
            install_trivy
            install_grype
            scan_with_trivy
            scan_with_grype
            scan_docker_images
            generate_summary_report
            ;;
        dependencies)
            scan_dependencies_npm
            scan_dependencies_python
            generate_summary_report
            ;;
        secrets)
            scan_secrets_in_code
            generate_summary_report
            ;;
        iac)
            scan_infrastructure_as_code
            generate_summary_report
            ;;
        full)
            install_trivy
            install_grype
            scan_with_trivy
            scan_with_grype
            scan_dependencies_npm
            scan_dependencies_python
            scan_docker_images
            scan_secrets_in_code
            scan_infrastructure_as_code
            generate_summary_report
            ;;
    esac

    echo "" | tee -a "$LOG_FILE"
    log_success "Vulnerability scanning completed!"
    log_info "Reports directory: $REPORT_DIR"
    log_info "Log file: $LOG_FILE"
}

main "$@"
