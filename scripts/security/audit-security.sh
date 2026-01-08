#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Comprehensive Security Audit Script
# Orchestrates all security audits and generates compliance reports
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/security"
REPORT_DIR="${PROJECT_ROOT}/reports/security"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/security-audit-${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/security-audit-${TIMESTAMP}.md"

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Logging
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
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
# Global Variables
# ─────────────────────────────────────────────────────────────────────────────

TOTAL_SCORE=0
TOTAL_MAX_SCORE=0
CRITICAL_FINDINGS=0
HIGH_FINDINGS=0
MEDIUM_FINDINGS=0
LOW_FINDINGS=0

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
# Report Generation
# ─────────────────────────────────────────────────────────────────────────────

init_report() {
    cat > "$REPORT_FILE" <<EOF
# SAHOOL Platform Security Audit Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')
**Platform:** SAHOOL Unified v15
**Auditor:** Automated Security Scanner

---

## Executive Summary

This report provides a comprehensive security assessment of the SAHOOL platform, covering all infrastructure components, containers, and configurations.

### Audit Scope

- Docker Infrastructure
- PostgreSQL Database
- Redis Cache
- NATS Message Broker
- Network Configuration
- Secrets Management
- Container Security
- Compliance Checks

---

EOF
}

add_to_report() {
    echo "$1" >> "$REPORT_FILE"
}

finalize_report() {
    local overall_percentage
    if [[ $TOTAL_MAX_SCORE -gt 0 ]]; then
        overall_percentage=$((TOTAL_SCORE * 100 / TOTAL_MAX_SCORE))
    else
        overall_percentage=0
    fi

    cat >> "$REPORT_FILE" <<EOF

---

## Overall Security Score

**Total Score:** ${TOTAL_SCORE}/${TOTAL_MAX_SCORE} (${overall_percentage}%)

### Findings Summary

| Severity | Count |
|----------|-------|
| Critical | ${CRITICAL_FINDINGS} |
| High     | ${HIGH_FINDINGS} |
| Medium   | ${MEDIUM_FINDINGS} |
| Low      | ${LOW_FINDINGS} |

### Risk Assessment

EOF

    if [[ $overall_percentage -ge 90 ]]; then
        cat >> "$REPORT_FILE" <<EOF
**Risk Level:** LOW

The platform demonstrates excellent security posture with ${overall_percentage}% compliance. Continue regular security audits and monitoring.
EOF
    elif [[ $overall_percentage -ge 70 ]]; then
        cat >> "$REPORT_FILE" <<EOF
**Risk Level:** MEDIUM

The platform has good security with ${overall_percentage}% compliance, but improvements are recommended to address identified gaps.
EOF
    elif [[ $overall_percentage -ge 50 ]]; then
        cat >> "$REPORT_FILE" <<EOF
**Risk Level:** HIGH

The platform security requires immediate attention with only ${overall_percentage}% compliance. Priority should be given to critical and high severity findings.
EOF
    else
        cat >> "$REPORT_FILE" <<EOF
**Risk Level:** CRITICAL

The platform has significant security vulnerabilities with only ${overall_percentage}% compliance. Immediate remediation required for all critical findings.
EOF
    fi

    cat >> "$REPORT_FILE" <<EOF

---

## Recommendations

### Immediate Actions (Critical/High Priority)

1. Address all critical severity findings within 24 hours
2. Implement missing authentication mechanisms
3. Enable TLS/SSL for all network communications
4. Review and restrict container privileges

### Short-term Actions (1-2 Weeks)

1. Implement automated secret rotation
2. Enable comprehensive audit logging
3. Configure network segmentation
4. Implement rate limiting and DDoS protection

### Long-term Actions (1-3 Months)

1. Establish security monitoring and alerting
2. Conduct penetration testing
3. Implement security training program
4. Establish incident response procedures

---

## Compliance Status

### CIS Benchmarks

- Docker CIS Benchmark: In Progress
- PostgreSQL CIS Benchmark: In Progress
- Redis Security Best Practices: In Progress

### Security Standards

- OWASP Top 10: Under Review
- SOC 2: Not Assessed
- ISO 27001: Not Assessed

---

## Next Steps

1. Review this report with the security team
2. Prioritize findings based on severity
3. Create remediation tickets for all findings
4. Schedule follow-up audit in 30 days
5. Implement continuous security monitoring

---

**Report Location:** \`${REPORT_FILE}\`
**Log File:** \`${LOG_FILE}\`

EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Audit Functions
# ─────────────────────────────────────────────────────────────────────────────

audit_docker() {
    log_section "Auditing Docker Infrastructure"
    add_to_report "## Docker Infrastructure Audit"
    add_to_report ""

    local score=0
    local max_score=20

    # Run Docker hardening audit
    if [[ -x "$SCRIPT_DIR/harden-docker.sh" ]]; then
        log_info "Running Docker security audit..."
        "$SCRIPT_DIR/harden-docker.sh" --audit 2>&1 | tee -a "$LOG_FILE" || true
    fi

    # Check Docker version
    local docker_version
    docker_version=$(docker --version 2>/dev/null || echo "Not installed")
    add_to_report "**Docker Version:** $docker_version"
    add_to_report ""

    # Check for privileged containers
    local priv_count
    priv_count=$(docker ps -q | xargs docker inspect --format '{{.HostConfig.Privileged}}' 2>/dev/null | grep -c "true" || echo "0")
    if [[ "$priv_count" -eq 0 ]]; then
        add_to_report "- ✅ No privileged containers running"
        ((score+=5))
    else
        add_to_report "- ❌ **CRITICAL:** $priv_count privileged container(s) running"
        ((CRITICAL_FINDINGS++))
    fi

    # Check for containers running as root
    local root_containers
    root_containers=$(docker ps -q | xargs docker inspect --format '{{.Name}}: {{.Config.User}}' 2>/dev/null | grep -c ": $" || echo "0")
    if [[ "$root_containers" -eq 0 ]]; then
        add_to_report "- ✅ All containers run as non-root users"
        ((score+=5))
    else
        add_to_report "- ⚠️ **HIGH:** $root_containers container(s) running as root"
        ((HIGH_FINDINGS++))
    fi

    # Check Docker socket permissions
    if [[ -S /var/run/docker.sock ]]; then
        local perms
        perms=$(stat -c '%a' /var/run/docker.sock 2>/dev/null || echo "unknown")
        if [[ "$perms" == "660" ]] || [[ "$perms" == "600" ]]; then
            add_to_report "- ✅ Docker socket has restrictive permissions ($perms)"
            ((score+=5))
        else
            add_to_report "- ⚠️ **MEDIUM:** Docker socket permissions too permissive ($perms)"
            ((MEDIUM_FINDINGS++))
        fi
    fi

    # Resource limits check
    local containers_without_limits
    containers_without_limits=$(docker ps -q | while read cid; do
        memory_limit=$(docker inspect --format '{{.HostConfig.Memory}}' $cid 2>/dev/null)
        if [[ "$memory_limit" == "0" ]]; then
            echo $cid
        fi
    done | wc -l)

    if [[ "$containers_without_limits" -eq 0 ]]; then
        add_to_report "- ✅ All containers have resource limits"
        ((score+=5))
    else
        add_to_report "- ⚠️ **LOW:** $containers_without_limits container(s) without resource limits"
        ((LOW_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**Docker Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "Docker audit score: ${score}/${max_score}"
}

audit_postgres() {
    log_section "Auditing PostgreSQL"
    add_to_report "## PostgreSQL Database Audit"
    add_to_report ""

    local score=0
    local max_score=15

    # Run PostgreSQL hardening audit
    if [[ -x "$SCRIPT_DIR/harden-postgres.sh" ]]; then
        log_info "Running PostgreSQL security audit..."
        "$SCRIPT_DIR/harden-postgres.sh" --audit 2>&1 | tee -a "$LOG_FILE" || true
    fi

    local container="sahool-postgres"

    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        add_to_report "- ⚠️ PostgreSQL container not running"
        add_to_report ""
        return
    fi

    # Check SSL
    local ssl_enabled
    ssl_enabled=$(docker exec "$container" psql -U sahool -d sahool -t -c "SHOW ssl;" 2>/dev/null | xargs || echo "off")
    if [[ "$ssl_enabled" == "on" ]]; then
        add_to_report "- ✅ SSL/TLS enabled"
        ((score+=5))
    else
        add_to_report "- ❌ **CRITICAL:** SSL/TLS not enabled"
        ((CRITICAL_FINDINGS++))
    fi

    # Check password encryption
    local pwd_enc
    pwd_enc=$(docker exec "$container" psql -U sahool -d sahool -t -c "SHOW password_encryption;" 2>/dev/null | xargs || echo "md5")
    if [[ "$pwd_enc" == "scram-sha-256" ]]; then
        add_to_report "- ✅ Using SCRAM-SHA-256 password encryption"
        ((score+=5))
    else
        add_to_report "- ⚠️ **HIGH:** Not using SCRAM-SHA-256 encryption (using: $pwd_enc)"
        ((HIGH_FINDINGS++))
    fi

    # Check logging
    local log_connections
    log_connections=$(docker exec "$container" psql -U sahool -d sahool -t -c "SHOW log_connections;" 2>/dev/null | xargs || echo "off")
    if [[ "$log_connections" == "on" ]]; then
        add_to_report "- ✅ Connection logging enabled"
        ((score+=5))
    else
        add_to_report "- ⚠️ **MEDIUM:** Connection logging not enabled"
        ((MEDIUM_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**PostgreSQL Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "PostgreSQL audit score: ${score}/${max_score}"
}

audit_redis() {
    log_section "Auditing Redis"
    add_to_report "## Redis Cache Audit"
    add_to_report ""

    local score=0
    local max_score=15

    # Run Redis hardening audit
    if [[ -x "$SCRIPT_DIR/harden-redis.sh" ]]; then
        log_info "Running Redis security audit..."
        "$SCRIPT_DIR/harden-redis.sh" --audit 2>&1 | tee -a "$LOG_FILE" || true
    fi

    local container="sahool-redis"

    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        add_to_report "- ⚠️ Redis container not running"
        add_to_report ""
        return
    fi

    # Check authentication
    if docker exec "$container" redis-cli ping 2>&1 | grep -q "NOAUTH"; then
        add_to_report "- ✅ Password authentication required"
        ((score+=5))
    elif docker exec "$container" redis-cli ping 2>&1 | grep -q "PONG"; then
        add_to_report "- ❌ **CRITICAL:** No password authentication configured"
        ((CRITICAL_FINDINGS++))
    fi

    # Check protected mode (requires password)
    local protected_mode
    protected_mode=$(docker exec "$container" redis-cli -a "${REDIS_PASSWORD:-}" CONFIG GET protected-mode 2>/dev/null | tail -1 || echo "no")
    if [[ "$protected_mode" == "yes" ]]; then
        add_to_report "- ✅ Protected mode enabled"
        ((score+=5))
    else
        add_to_report "- ⚠️ **HIGH:** Protected mode not enabled"
        ((HIGH_FINDINGS++))
    fi

    # Check memory limits
    local maxmemory
    maxmemory=$(docker exec "$container" redis-cli -a "${REDIS_PASSWORD:-}" CONFIG GET maxmemory 2>/dev/null | tail -1 || echo "0")
    if [[ "$maxmemory" != "0" ]]; then
        add_to_report "- ✅ Memory limit configured"
        ((score+=5))
    else
        add_to_report "- ⚠️ **MEDIUM:** No memory limit configured"
        ((MEDIUM_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**Redis Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "Redis audit score: ${score}/${max_score}"
}

audit_nats() {
    log_section "Auditing NATS"
    add_to_report "## NATS Message Broker Audit"
    add_to_report ""

    local score=0
    local max_score=10

    # Run NATS hardening audit
    if [[ -x "$SCRIPT_DIR/harden-nats.sh" ]]; then
        log_info "Running NATS security audit..."
        "$SCRIPT_DIR/harden-nats.sh" --audit 2>&1 | tee -a "$LOG_FILE" || true
    fi

    local container="sahool-nats"

    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        add_to_report "- ⚠️ NATS container not running"
        add_to_report ""
        return
    fi

    # Check if NATS is accessible
    if docker exec "$container" nats-server --help >/dev/null 2>&1; then
        add_to_report "- ✅ NATS server is running"
        ((score+=5))
    fi

    # Check for NKeys
    if [[ -d "${PROJECT_ROOT}/scripts/nats/keys/nsc" ]]; then
        add_to_report "- ✅ NKeys configured"
        ((score+=5))
    else
        add_to_report "- ⚠️ **HIGH:** NKeys not configured"
        ((HIGH_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**NATS Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "NATS audit score: ${score}/${max_score}"
}

audit_network() {
    log_section "Auditing Network Configuration"
    add_to_report "## Network Configuration Audit"
    add_to_report ""

    local score=0
    local max_score=10

    # Check Docker networks
    add_to_report "### Docker Networks"
    add_to_report ""
    docker network ls --format "- {{.Name}} ({{.Driver}})" >> "$REPORT_FILE"
    add_to_report ""

    # Check for bridge network isolation
    local bridge_icc
    bridge_icc=$(docker network inspect bridge --format '{{index .Options "com.docker.network.bridge.enable_icc"}}' 2>/dev/null || echo "true")
    if [[ "$bridge_icc" == "false" ]]; then
        add_to_report "- ✅ Inter-container communication disabled on default bridge"
        ((score+=5))
    else
        add_to_report "- ⚠️ **MEDIUM:** Inter-container communication enabled on default bridge"
        ((MEDIUM_FINDINGS++))
    fi

    # Check for custom networks
    local custom_networks
    custom_networks=$(docker network ls --filter type=custom --format '{{.Name}}' | wc -l)
    if [[ "$custom_networks" -gt 0 ]]; then
        add_to_report "- ✅ Using custom networks ($custom_networks networks)"
        ((score+=5))
    else
        add_to_report "- ⚠️ **LOW:** No custom networks configured"
        ((LOW_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**Network Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "Network audit score: ${score}/${max_score}"
}

audit_secrets() {
    log_section "Auditing Secrets Management"
    add_to_report "## Secrets Management Audit"
    add_to_report ""

    local score=0
    local max_score=10

    # Check for secrets directory
    if [[ -d "${PROJECT_ROOT}/secrets" ]]; then
        add_to_report "- ✅ Secrets directory exists"
        ((score+=3))

        # Check permissions
        local perms
        perms=$(stat -c '%a' "${PROJECT_ROOT}/secrets" 2>/dev/null || echo "777")
        if [[ "$perms" == "700" ]]; then
            add_to_report "- ✅ Secrets directory has restrictive permissions"
            ((score+=3))
        else
            add_to_report "- ⚠️ **HIGH:** Secrets directory permissions too permissive ($perms)"
            ((HIGH_FINDINGS++))
        fi
    else
        add_to_report "- ⚠️ **MEDIUM:** Secrets directory not found"
        ((MEDIUM_FINDINGS++))
    fi

    # Check .env file
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        add_to_report "- ⚠️ **LOW:** .env file exists (ensure it's in .gitignore)"
        ((LOW_FINDINGS++))

        # Check if in gitignore
        if grep -q "^.env$" "${PROJECT_ROOT}/.gitignore" 2>/dev/null; then
            add_to_report "- ✅ .env is in .gitignore"
            ((score+=2))
        else
            add_to_report "- ❌ **CRITICAL:** .env is NOT in .gitignore"
            ((CRITICAL_FINDINGS++))
        fi
    else
        add_to_report "- ✅ No .env file in root (good practice)"
        ((score+=2))
    fi

    # Check for hardcoded secrets in docker-compose
    if grep -r "password.*=" "${PROJECT_ROOT}/docker-compose"*.yml 2>/dev/null | grep -qv "POSTGRES_PASSWORD"; then
        add_to_report "- ⚠️ **HIGH:** Potential hardcoded passwords in docker-compose files"
        ((HIGH_FINDINGS++))
    else
        add_to_report "- ✅ No obvious hardcoded passwords in docker-compose"
        ((score+=2))
    fi

    add_to_report ""
    add_to_report "**Secrets Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "Secrets audit score: ${score}/${max_score}"
}

audit_logging() {
    log_section "Auditing Logging Configuration"
    add_to_report "## Logging Configuration Audit"
    add_to_report ""

    local score=0
    local max_score=10

    # Check if logs directory exists
    if [[ -d "${PROJECT_ROOT}/logs" ]]; then
        add_to_report "- ✅ Logs directory exists"
        ((score+=5))
    else
        add_to_report "- ⚠️ **LOW:** Logs directory not found"
        ((LOW_FINDINGS++))
    fi

    # Check container logging configuration
    local containers_with_logging
    containers_with_logging=$(docker ps -q | while read cid; do
        driver=$(docker inspect --format '{{.HostConfig.LogConfig.Type}}' $cid 2>/dev/null)
        if [[ "$driver" != "none" ]]; then
            echo $cid
        fi
    done | wc -l)

    local total_containers
    total_containers=$(docker ps -q | wc -l)

    if [[ "$containers_with_logging" -eq "$total_containers" ]]; then
        add_to_report "- ✅ All containers have logging configured"
        ((score+=5))
    else
        add_to_report "- ⚠️ **MEDIUM:** Some containers without logging"
        ((MEDIUM_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**Logging Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "Logging audit score: ${score}/${max_score}"
}

audit_certificates() {
    log_section "Auditing TLS Certificates"
    add_to_report "## TLS/SSL Certificates Audit"
    add_to_report ""

    local score=0
    local max_score=10

    # Check for certificates directory
    local cert_dirs=("${PROJECT_ROOT}/config/certs" "${PROJECT_ROOT}/scripts/certs" "${PROJECT_ROOT}/infrastructure/certs")

    local found_certs=false
    for cert_dir in "${cert_dirs[@]}"; do
        if [[ -d "$cert_dir" ]]; then
            add_to_report "- ✅ Certificates directory found: $cert_dir"
            ((score+=3))
            found_certs=true

            # Check for certificate files
            if ls "$cert_dir"/*.crt >/dev/null 2>&1; then
                add_to_report "- ✅ Certificate files exist"
                ((score+=3))

                # Check certificate expiration
                for cert in "$cert_dir"/*.crt; do
                    if [[ -f "$cert" ]]; then
                        local expiry
                        expiry=$(openssl x509 -in "$cert" -noout -enddate 2>/dev/null | cut -d= -f2 || echo "unknown")
                        local days_until_expiry
                        days_until_expiry=$(( ( $(date -d "$expiry" +%s) - $(date +%s) ) / 86400 )) 2>/dev/null || echo "unknown"

                        if [[ "$days_until_expiry" == "unknown" ]]; then
                            add_to_report "- ⚠️ Could not determine expiry for: $(basename "$cert")"
                        elif [[ "$days_until_expiry" -lt 30 ]]; then
                            add_to_report "- ❌ **CRITICAL:** Certificate expires soon: $(basename "$cert") ($days_until_expiry days)"
                            ((CRITICAL_FINDINGS++))
                        elif [[ "$days_until_expiry" -lt 90 ]]; then
                            add_to_report "- ⚠️ **MEDIUM:** Certificate expires in $days_until_expiry days: $(basename "$cert")"
                            ((MEDIUM_FINDINGS++))
                        else
                            add_to_report "- ✅ Certificate valid: $(basename "$cert") ($days_until_expiry days)"
                            ((score+=2))
                        fi
                    fi
                done
            else
                add_to_report "- ⚠️ **HIGH:** No certificate files in $cert_dir"
                ((HIGH_FINDINGS++))
            fi
            break
        fi
    done

    if ! $found_certs; then
        add_to_report "- ⚠️ **HIGH:** No certificates directory found"
        ((HIGH_FINDINGS++))
    fi

    add_to_report ""
    add_to_report "**Certificates Score:** ${score}/${max_score}"
    add_to_report ""

    TOTAL_SCORE=$((TOTAL_SCORE + score))
    TOTAL_MAX_SCORE=$((TOTAL_MAX_SCORE + max_score))

    log_info "Certificates audit score: ${score}/${max_score}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat <<EOF
SAHOOL Comprehensive Security Audit Script

Usage: $0 [OPTIONS]

Options:
    --help          Show this help message
    --full          Run full security audit (default)
    --docker        Audit Docker only
    --postgres      Audit PostgreSQL only
    --redis         Audit Redis only
    --nats          Audit NATS only
    --network       Audit network configuration only
    --secrets       Audit secrets management only
    --quick         Run quick audit (skip detailed scans)

Examples:
    $0              # Run full audit
    $0 --docker     # Audit Docker only
    $0 --quick      # Quick audit

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
            --docker)
                mode="docker"
                shift
                ;;
            --postgres)
                mode="postgres"
                shift
                ;;
            --redis)
                mode="redis"
                shift
                ;;
            --nats)
                mode="nats"
                shift
                ;;
            --network)
                mode="network"
                shift
                ;;
            --secrets)
                mode="secrets"
                shift
                ;;
            --quick)
                mode="quick"
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
    echo "           SAHOOL Comprehensive Security Audit"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    preflight_checks
    init_report

    case $mode in
        docker)
            audit_docker
            ;;
        postgres)
            audit_postgres
            ;;
        redis)
            audit_redis
            ;;
        nats)
            audit_nats
            ;;
        network)
            audit_network
            ;;
        secrets)
            audit_secrets
            ;;
        quick)
            audit_docker
            audit_secrets
            audit_network
            ;;
        full)
            audit_docker
            audit_postgres
            audit_redis
            audit_nats
            audit_network
            audit_secrets
            audit_logging
            audit_certificates
            ;;
    esac

    finalize_report

    echo "" | tee -a "$LOG_FILE"
    log_success "Security audit completed!"
    log_info "Report: $REPORT_FILE"
    log_info "Log: $LOG_FILE"
    log_info "Overall Score: ${TOTAL_SCORE}/${TOTAL_MAX_SCORE}"
    log_info "Findings: Critical=${CRITICAL_FINDINGS}, High=${HIGH_FINDINGS}, Medium=${MEDIUM_FINDINGS}, Low=${LOW_FINDINGS}"
}

main "$@"
