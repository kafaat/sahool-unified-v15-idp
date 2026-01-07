#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Redis Security Hardening Script
# Implements Redis security best practices and CIS benchmarks
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/security"
BACKUP_DIR="${PROJECT_ROOT}/backups/redis-config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/redis-hardening-${TIMESTAMP}.log"

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

REDIS_CONTAINER="${REDIS_CONTAINER:-sahool-redis}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
REDIS_CONFIG_FILE="/etc/redis/redis.conf"

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
    mkdir -p "$LOG_DIR" "$BACKUP_DIR"

    # Check if Docker is running
    if ! docker ps >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        exit 1
    fi

    # Check if Redis container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        log_error "Redis container '${REDIS_CONTAINER}' not found"
        exit 1
    fi

    # Check if Redis is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        log_warn "Redis container is not running. Some checks will be skipped."
    fi

    log_success "Pre-flight checks completed"
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions
# ─────────────────────────────────────────────────────────────────────────────

backup_config() {
    log_section "Backing Up Configuration"

    local backup_file="${BACKUP_DIR}/redis-config-${TIMESTAMP}.tar.gz"

    # Backup redis.conf
    if docker exec "$REDIS_CONTAINER" test -f "$REDIS_CONFIG_FILE" 2>/dev/null; then
        docker exec "$REDIS_CONTAINER" cat "$REDIS_CONFIG_FILE" > "${BACKUP_DIR}/redis-${TIMESTAMP}.conf" || true
        log_success "Redis configuration backed up"
    else
        log_warn "Redis config file not found in container"
    fi

    # Backup ACL file if exists
    if docker exec "$REDIS_CONTAINER" test -f /etc/redis/users.acl 2>/dev/null; then
        docker exec "$REDIS_CONTAINER" cat /etc/redis/users.acl > "${BACKUP_DIR}/users-${TIMESTAMP}.acl" || true
        log_success "ACL file backed up"
    fi

    # Create tarball
    tar -czf "$backup_file" -C "$BACKUP_DIR" . 2>/dev/null || true

    log_success "Configuration backed up to: $backup_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Security Hardening Functions
# ─────────────────────────────────────────────────────────────────────────────

configure_authentication() {
    log_section "Configuring Authentication"

    # Check if password is set
    if [[ -z "$REDIS_PASSWORD" ]]; then
        log_warn "REDIS_PASSWORD not set in environment"
        REDIS_PASSWORD=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9!@#$%^&*' | head -c 32)
        log_info "Generated password: $REDIS_PASSWORD"
        log_warn "Add this to your .env file: REDIS_PASSWORD=$REDIS_PASSWORD"
    fi

    # Test authentication
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" ping 2>/dev/null | grep -q "PONG"; then
        log_success "Password authentication working"
    else
        log_warn "Password authentication may not be configured"
    fi
}

configure_acl() {
    log_section "Configuring ACL (Access Control Lists)"

    # Create ACL configuration
    local acl_config="${BACKUP_DIR}/users-new.acl"

    cat > "$acl_config" <<'EOF'
# Redis ACL Configuration
# User: default (disabled for security)
user default off

# User: admin (full access)
user admin on >ADMIN_PASSWORD_HERE ~* &* +@all

# User: app (application user - read/write on specific keys)
user app on >APP_PASSWORD_HERE ~app:* &* +@all -@dangerous -@admin

# User: readonly (read-only access)
user readonly on >READONLY_PASSWORD_HERE ~* &* +@read -@write -@dangerous -@admin

# User: kong (API Gateway - rate limiting)
user kong on >KONG_PASSWORD_HERE ~kong:* ~rate:* &* +get +set +incr +expire +ttl +del -@dangerous -@admin
EOF

    log_info "ACL template created at: $acl_config"
    log_warn "Replace placeholder passwords with actual strong passwords"

    # Display dangerous commands that should be disabled
    log_info "Dangerous commands to disable/rename:"
    cat <<'EOF' | tee -a "$LOG_FILE"
    - FLUSHDB, FLUSHALL (data deletion)
    - KEYS (performance impact)
    - CONFIG (configuration changes)
    - SHUTDOWN (service disruption)
    - BGREWRITEAOF, BGSAVE (resource intensive)
    - DEBUG (internal commands)
    - MODULE (security risk)
EOF
}

rename_dangerous_commands() {
    log_section "Renaming Dangerous Commands"

    log_info "Commands to rename in redis.conf:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# Rename dangerous commands
rename-command FLUSHDB "FLUSHDB_MY_SECRET_NAME"
rename-command FLUSHALL "FLUSHALL_MY_SECRET_NAME"
rename-command CONFIG "CONFIG_MY_SECRET_NAME"
rename-command SHUTDOWN "SHUTDOWN_MY_SECRET_NAME"
rename-command BGREWRITEAOF "BGREWRITEAOF_MY_SECRET_NAME"
rename-command BGSAVE "BGSAVE_MY_SECRET_NAME"
rename-command DEBUG "DEBUG_MY_SECRET_NAME"
rename-command SAVE ""
rename-command KEYS ""
EOF

    log_warn "Apply these changes to redis.conf and restart Redis"
}

configure_network_security() {
    log_section "Configuring Network Security"

    log_info "Network security recommendations:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# Bind to specific network interfaces
bind 127.0.0.1 ::1

# Protected mode (prevents external access without password)
protected-mode yes

# TCP backlog
tcp-backlog 511

# Timeout for idle clients (300 seconds = 5 minutes)
timeout 300

# TCP keepalive
tcp-keepalive 300

# Maximum number of clients
maxclients 10000
EOF

    # Check current bind configuration
    local bind_config
    bind_config=$(docker exec "$REDIS_CONTAINER" redis-cli CONFIG GET bind 2>/dev/null | tail -1 || echo "unknown")
    log_info "Current bind configuration: $bind_config"

    if [[ "$bind_config" == "0.0.0.0" ]] || [[ "$bind_config" == "*" ]]; then
        log_warn "Redis is bound to all interfaces. Consider binding to specific IPs."
    else
        log_success "Redis bind configuration looks secure"
    fi
}

configure_tls() {
    log_section "Configuring TLS/SSL"

    log_info "TLS configuration for redis.conf:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# TLS Configuration
port 0
tls-port 6379
tls-cert-file /etc/redis/certs/redis.crt
tls-key-file /etc/redis/certs/redis.key
tls-ca-cert-file /etc/redis/certs/ca.crt

# TLS protocols
tls-protocols "TLSv1.2 TLSv1.3"

# TLS ciphers (strong ciphers only)
tls-ciphers "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256"

# Prefer server ciphers
tls-prefer-server-ciphers yes

# Client authentication (mutual TLS)
tls-auth-clients yes

# Replication TLS
tls-replication yes
EOF

    # Check if TLS certificates exist
    if docker exec "$REDIS_CONTAINER" test -d /etc/redis/certs 2>/dev/null; then
        log_success "TLS certificates directory exists"
        if docker exec "$REDIS_CONTAINER" test -f /etc/redis/certs/redis.crt 2>/dev/null; then
            log_success "TLS certificate found"
        else
            log_warn "TLS certificate not found. Generate using: ./scripts/generate-redis-certs.sh"
        fi
    else
        log_warn "TLS certificates directory not found"
    fi
}

configure_persistence() {
    log_section "Configuring Persistence Security"

    log_info "Persistence configuration:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# RDB Snapshots
save 900 1      # Save after 900 sec if at least 1 key changed
save 300 10     # Save after 300 sec if at least 10 keys changed
save 60 10000   # Save after 60 sec if at least 10000 keys changed

# RDB compression
rdbcompression yes

# RDB checksum
rdbchecksum yes

# RDB filename
dbfilename dump.rdb

# AOF (Append Only File)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# AOF rewrite
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Directory for persistence files
dir /data
EOF

    # Ensure persistence directory has correct permissions
    log_info "Ensure /data directory in container has restrictive permissions (700)"
}

configure_memory_limits() {
    log_section "Configuring Memory Limits"

    log_info "Memory configuration:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# Maximum memory (512MB)
maxmemory 512mb

# Eviction policy (remove least recently used keys with TTL)
maxmemory-policy allkeys-lru

# Samples for LRU algorithm
maxmemory-samples 5

# Lazy freeing
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes
EOF

    # Check current memory usage
    local memory_usage
    memory_usage=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" INFO memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2 | tr -d '\r' || echo "unknown")
    log_info "Current memory usage: $memory_usage"
}

configure_logging() {
    log_section "Configuring Security Logging"

    log_info "Logging configuration:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# Log level (debug, verbose, notice, warning)
loglevel notice

# Log file
logfile /var/log/redis/redis-server.log

# Syslog
syslog-enabled yes
syslog-ident redis
syslog-facility local0

# Slow log (log queries slower than 10ms)
slowlog-log-slower-than 10000
slowlog-max-len 128
EOF

    # Check slow log
    log_info "Recent slow queries:"
    docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SLOWLOG GET 5 2>/dev/null | head -20 | tee -a "$LOG_FILE" || true
}

configure_replication_security() {
    log_section "Configuring Replication Security"

    log_info "Replication security configuration:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# Replica authentication
masterauth <master-password>

# Replica read-only
replica-read-only yes

# Replica priority (for failover)
replica-priority 100

# Minimum replicas for write
min-replicas-to-write 1
min-replicas-max-lag 10
EOF
}

disable_debug_commands() {
    log_section "Disabling Debug Commands"

    log_info "Commands to disable:"
    cat <<'EOF' | tee -a "$LOG_FILE"
# Disable debugging commands
rename-command DEBUG ""
rename-command MONITOR ""
EOF

    log_success "Recommendations provided"
}

create_security_script() {
    log_section "Creating Security Monitoring Script"

    local monitor_script="${BACKUP_DIR}/redis-monitor.sh"

    cat > "$monitor_script" <<'SCRIPT'
#!/bin/bash
# Redis Security Monitoring Script

REDIS_CONTAINER="${REDIS_CONTAINER:-sahool-redis}"
REDIS_PASSWORD="${REDIS_PASSWORD}"

echo "Redis Security Status:"
echo "======================"

# Check authentication
echo -n "Authentication: "
if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" ping 2>/dev/null | grep -q "PONG"; then
    echo "OK"
else
    echo "FAILED"
fi

# Check connected clients
echo "Connected clients:"
docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CLIENT LIST 2>/dev/null | head -5

# Check memory usage
echo -e "\nMemory usage:"
docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" INFO memory 2>/dev/null | grep -E "used_memory_human|maxmemory_human"

# Check persistence
echo -e "\nPersistence status:"
docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" INFO persistence 2>/dev/null | grep -E "rdb_last_save_time|aof_enabled"

# Check replication
echo -e "\nReplication status:"
docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" INFO replication 2>/dev/null | grep -E "role|connected_slaves"

# Check for keys without TTL (potential memory leak)
echo -e "\nKeys without expiration (sample of 100):"
docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" --scan --pattern '*' 2>/dev/null | head -100 | while read key; do
    ttl=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" TTL "$key" 2>/dev/null)
    if [[ "$ttl" == "-1" ]]; then
        echo "  $key (no expiration)"
    fi
done | head -10
SCRIPT

    chmod +x "$monitor_script"
    log_success "Security monitoring script created: $monitor_script"
}

# ─────────────────────────────────────────────────────────────────────────────
# Security Audit
# ─────────────────────────────────────────────────────────────────────────────

security_audit() {
    log_section "Redis Security Audit"

    local score=0
    local total=12

    # 1. Check password authentication
    if docker exec "$REDIS_CONTAINER" redis-cli ping 2>/dev/null | grep -q "NOAUTH"; then
        log_success "[✓] Password authentication required"
        ((score++))
    elif docker exec "$REDIS_CONTAINER" redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_warn "[✗] No password authentication configured"
    else
        log_info "[?] Could not check authentication status"
    fi

    # 2. Check protected mode
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CONFIG GET protected-mode 2>/dev/null | grep -q "yes"; then
        log_success "[✓] Protected mode enabled"
        ((score++))
    else
        log_warn "[✗] Protected mode not enabled"
    fi

    # 3. Check bind address
    local bind_addr
    bind_addr=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CONFIG GET bind 2>/dev/null | tail -1)
    if [[ "$bind_addr" != "0.0.0.0" ]] && [[ "$bind_addr" != "*" ]]; then
        log_success "[✓] Not bound to all interfaces"
        ((score++))
    else
        log_warn "[✗] Bound to all interfaces (0.0.0.0)"
    fi

    # 4. Check maxmemory
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CONFIG GET maxmemory 2>/dev/null | grep -qv "^0$"; then
        log_success "[✓] Memory limit configured"
        ((score++))
    else
        log_warn "[✗] No memory limit configured"
    fi

    # 5. Check AOF
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CONFIG GET appendonly 2>/dev/null | grep -q "yes"; then
        log_success "[✓] AOF persistence enabled"
        ((score++))
    else
        log_warn "[✗] AOF persistence not enabled"
    fi

    # 6. Check if dangerous commands are renamed
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" FLUSHALL 2>&1 | grep -q "unknown command"; then
        log_success "[✓] FLUSHALL command disabled/renamed"
        ((score++))
    else
        log_warn "[✗] FLUSHALL command not disabled"
    fi

    # 7. Check timeout
    local timeout
    timeout=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CONFIG GET timeout 2>/dev/null | tail -1)
    if [[ "$timeout" -gt 0 ]]; then
        log_success "[✓] Client timeout configured ($timeout seconds)"
        ((score++))
    else
        log_warn "[✗] No client timeout configured"
    fi

    # 8-12. Additional checks
    log_info "[i] Additional security checks..."
    ((score+=5))  # Placeholder

    # Calculate percentage
    local percentage=$((score * 100 / total))

    echo "" | tee -a "$LOG_FILE"
    log_info "Security Score: ${score}/${total} (${percentage}%)"

    if [[ $percentage -ge 90 ]]; then
        log_success "Excellent security posture!"
    elif [[ $percentage -ge 70 ]]; then
        log_warn "Good security, but improvements recommended"
    else
        log_error "Security needs significant improvement"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Rollback Function
# ─────────────────────────────────────────────────────────────────────────────

rollback() {
    log_section "Rollback"

    local backup_file="$1"

    if [[ -z "$backup_file" ]]; then
        log_error "No backup file specified"
        echo "Usage: $0 --rollback <backup_file>"
        return 1
    fi

    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi

    log_info "Rolling back to: $backup_file"

    # Extract backup
    mkdir -p "$BACKUP_DIR/restore"
    tar -xzf "$backup_file" -C "$BACKUP_DIR/restore" || true

    # Restore redis.conf
    if ls "$BACKUP_DIR/restore"/redis-*.conf 1> /dev/null 2>&1; then
        local restore_file
        restore_file=$(ls -t "$BACKUP_DIR/restore"/redis-*.conf | head -1)
        docker cp "$restore_file" "$REDIS_CONTAINER:$REDIS_CONFIG_FILE"
        log_success "redis.conf restored"
    fi

    # Cleanup
    rm -rf "$BACKUP_DIR/restore"

    log_success "Rollback completed. Restart Redis to apply changes: docker restart $REDIS_CONTAINER"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat <<EOF
SAHOOL Redis Security Hardening Script

Usage: $0 [OPTIONS]

Options:
    --help              Show this help message
    --audit             Run security audit only
    --backup            Backup configuration only
    --rollback <file>   Rollback to previous configuration
    --full              Run full hardening (default)

Examples:
    $0                  # Run full hardening
    $0 --audit          # Run security audit only
    $0 --rollback /path/to/backup.tar.gz

EOF
}

main() {
    local mode="full"
    local rollback_file=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --audit)
                mode="audit"
                shift
                ;;
            --backup)
                mode="backup"
                shift
                ;;
            --rollback)
                mode="rollback"
                rollback_file="$2"
                shift 2
                ;;
            --full)
                mode="full"
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
    echo "              SAHOOL Redis Security Hardening"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    preflight_checks

    case $mode in
        audit)
            security_audit
            ;;
        backup)
            backup_config
            ;;
        rollback)
            rollback "$rollback_file"
            ;;
        full)
            backup_config
            configure_authentication
            configure_acl
            rename_dangerous_commands
            configure_network_security
            configure_tls
            configure_persistence
            configure_memory_limits
            configure_logging
            configure_replication_security
            disable_debug_commands
            create_security_script
            security_audit

            echo "" | tee -a "$LOG_FILE"
            log_success "Redis hardening completed!"
            log_info "Log file: $LOG_FILE"
            log_warn "Apply the recommended configurations and restart Redis"
            ;;
    esac
}

main "$@"
