#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Certificate Rotation Script
# Automates certificate rotation for all infrastructure services
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./rotate-certs.sh [--service <service>] [--dry-run] [--backup]
#
# Options:
#   --service <name>  Rotate certificate for specific service only
#   --dry-run         Show what would be done without making changes
#   --backup          Create backup of existing certificates
#   --skip-restart    Generate new certs but don't restart services
#   --force           Force rotation even if not expiring soon
#   --help            Show this help message
#
# Services:
#   - postgres       PostgreSQL database
#   - pgbouncer      PostgreSQL connection pooler
#   - redis          Redis cache
#   - nats           NATS message queue
#   - kong           Kong API Gateway
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CERT_BASE_DIR="$PROJECT_ROOT/config/certs"
BACKUP_DIR="$PROJECT_ROOT/config/certs/backups"

# Rotation settings
ROTATION_THRESHOLD_DAYS=30  # Rotate if expiring within 30 days
SERVICES=("postgres" "pgbouncer" "redis" "nats" "kong")

# Flags
DRY_RUN=false
CREATE_BACKUP=true
SKIP_RESTART=false
FORCE_ROTATION=false
SPECIFIC_SERVICE=""

# ─────────────────────────────────────────────────────────────────────────────
# Colors for output
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Logging functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

log_detail() {
    echo -e "       $1"
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

show_help() {
    cat << EOF
SAHOOL Certificate Rotation Script

Usage:
  $0 [OPTIONS]

Options:
  --service <name>  Rotate certificate for specific service only
  --dry-run         Show what would be done without making changes
  --backup          Create backup of existing certificates (default)
  --no-backup       Skip backup creation
  --skip-restart    Generate new certs but don't restart services
  --force           Force rotation even if not expiring soon
  --help            Show this help message

Services:
  postgres, pgbouncer, redis, nats, kong

Examples:
  # Rotate all expiring certificates
  $0

  # Dry run to see what would be rotated
  $0 --dry-run

  # Rotate Redis certificate only
  $0 --service redis

  # Force rotation without backup
  $0 --force --no-backup

  # Generate new certificates but don't restart services
  $0 --skip-restart

EOF
}

check_certificate_expiration() {
    local service="$1"
    local cert_file="$CERT_BASE_DIR/$service/server.crt"

    if [[ ! -f "$cert_file" ]]; then
        echo "999999"  # Certificate missing, needs generation
        return 0
    fi

    local expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -jf "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s 2>/dev/null)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))

    echo "$days_until_expiry"
}

needs_rotation() {
    local service="$1"
    local days_until_expiry=$(check_certificate_expiration "$service")

    if [[ "$FORCE_ROTATION" == "true" ]]; then
        return 0
    fi

    if [[ $days_until_expiry -le $ROTATION_THRESHOLD_DAYS ]]; then
        return 0
    fi

    return 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup functions
# ─────────────────────────────────────────────────────────────────────────────

backup_certificate() {
    local service="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local service_dir="$CERT_BASE_DIR/$service"
    local backup_subdir="$BACKUP_DIR/$service"

    if [[ ! -f "$service_dir/server.crt" ]]; then
        log_warning "No certificate to backup for $service"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would backup certificate for $service"
        return 0
    fi

    mkdir -p "$backup_subdir"

    log_step "Backing up certificate for: $service"

    # Create timestamped backup
    local backup_file="$backup_subdir/server_${timestamp}.crt"
    local backup_key="$backup_subdir/server_${timestamp}.key"

    cp "$service_dir/server.crt" "$backup_file"
    cp "$service_dir/server.key" "$backup_key"

    # Set permissions
    chmod 600 "$backup_key"
    chmod 644 "$backup_file"

    log_success "Certificate backed up to: $backup_subdir/"

    # Keep only last 10 backups
    cleanup_old_backups "$backup_subdir"
}

cleanup_old_backups() {
    local backup_subdir="$1"
    local keep_count=10

    # Count backup files
    local backup_count=$(find "$backup_subdir" -name "server_*.crt" | wc -l)

    if [[ $backup_count -gt $keep_count ]]; then
        log_info "Cleaning up old backups (keeping last $keep_count)"

        # Remove oldest backups
        find "$backup_subdir" -name "server_*.crt" -type f -printf '%T+ %p\n' | \
            sort | head -n -$keep_count | cut -d' ' -f2- | while read -r file; do
            rm -f "$file"
            rm -f "${file%.crt}.key"
        done
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Rotation functions
# ─────────────────────────────────────────────────────────────────────────────

rotate_certificate() {
    local service="$1"

    log_step "Rotating certificate for: $service"

    # Backup existing certificate
    if [[ "$CREATE_BACKUP" == "true" ]]; then
        backup_certificate "$service"
    fi

    # Generate new certificate
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would generate new certificate for $service"
    else
        log_detail "Generating new certificate..."
        "$SCRIPT_DIR/generate-certs.sh" --force --service "$service" &>/dev/null
        log_success "New certificate generated"
    fi
}

restart_service() {
    local service="$1"

    if [[ "$SKIP_RESTART" == "true" ]]; then
        log_info "Skipping service restart (--skip-restart flag set)"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would restart service: $service"
        return 0
    fi

    log_step "Restarting service: $service"

    # Check if running in Docker or Kubernetes
    if command -v docker-compose &> /dev/null && [[ -f "$PROJECT_ROOT/docker-compose.yml" ]]; then
        cd "$PROJECT_ROOT"
        if docker-compose ps "$service" &> /dev/null; then
            log_detail "Restarting Docker container..."
            docker-compose restart "$service" &>/dev/null
            log_success "Service restarted successfully"

            # Wait for health check
            log_detail "Waiting for service to be healthy..."
            sleep 5

            # Verify service is running
            if docker-compose ps "$service" | grep -q "Up"; then
                log_success "Service is running and healthy"
            else
                log_error "Service failed to start properly"
                return 1
            fi
        else
            log_warning "Service $service not found in Docker Compose"
        fi
    elif command -v kubectl &> /dev/null; then
        log_detail "Restarting Kubernetes pod..."
        kubectl rollout restart deployment/"sahool-$service" &>/dev/null || true
        log_success "Deployment restart initiated"
    else
        log_warning "Could not determine how to restart service"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Notification functions
# ─────────────────────────────────────────────────────────────────────────────

send_notification() {
    local subject="$1"
    local message="$2"

    # Send email notification if configured
    if [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "$message" | mail -s "$subject" "$NOTIFICATION_EMAIL" 2>/dev/null || true
    fi

    # Send Slack notification if configured
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$subject\\n$message\"}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi

    # Log to syslog
    logger -t sahool-cert-rotation "$subject: $message" 2>/dev/null || true
}

# ─────────────────────────────────────────────────────────────────────────────
# Main script
# ─────────────────────────────────────────────────────────────────────────────

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --service)
                SPECIFIC_SERVICE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --backup)
                CREATE_BACKUP=true
                shift
                ;;
            --no-backup)
                CREATE_BACKUP=false
                shift
                ;;
            --skip-restart)
                SKIP_RESTART=true
                shift
                ;;
            --force)
                FORCE_ROTATION=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Certificate Rotation"
    echo "  Platform: SAHOOL v16.0.0"
    echo "  Date: $(date)"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  Mode: DRY RUN (no changes will be made)"
    fi
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    # Determine which services to process
    local services_to_rotate=("${SERVICES[@]}")
    if [[ -n "$SPECIFIC_SERVICE" ]]; then
        if [[ ! " ${SERVICES[@]} " =~ " ${SPECIFIC_SERVICE} " ]]; then
            log_error "Invalid service: $SPECIFIC_SERVICE"
            log_info "Available services: ${SERVICES[*]}"
            exit 1
        fi
        services_to_rotate=("$SPECIFIC_SERVICE")
    fi

    # Check which certificates need rotation
    log_step "Checking certificate expiration status"
    echo ""

    local rotation_needed=()
    for service in "${services_to_rotate[@]}"; do
        local days=$(check_certificate_expiration "$service")

        if needs_rotation "$service"; then
            if [[ $days -eq 999999 ]]; then
                log_warning "$service: Certificate missing, will generate"
            elif [[ $days -lt 0 ]]; then
                log_error "$service: Certificate EXPIRED $((days * -1)) days ago!"
            else
                log_warning "$service: Certificate expires in $days days (threshold: $ROTATION_THRESHOLD_DAYS)"
            fi
            rotation_needed+=("$service")
        else
            log_info "$service: Certificate valid for $days days, no rotation needed"
        fi
    done

    echo ""

    # Exit if no rotation needed
    if [[ ${#rotation_needed[@]} -eq 0 ]]; then
        log_success "No certificates need rotation at this time"
        exit 0
    fi

    # Confirm rotation
    if [[ "$DRY_RUN" != "true" ]] && [[ -z "${UNATTENDED:-}" ]]; then
        echo "═══════════════════════════════════════════════════════════════════════════════"
        log_warning "The following ${#rotation_needed[@]} certificate(s) will be rotated:"
        for service in "${rotation_needed[@]}"; do
            echo "  - $service"
        done
        echo ""
        read -p "Continue with rotation? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Rotation cancelled by user"
            exit 0
        fi
        echo "═══════════════════════════════════════════════════════════════════════════════"
        echo ""
    fi

    # Perform rotation
    local rotated_count=0
    local failed_count=0
    local rotated_services=()

    for service in "${rotation_needed[@]}"; do
        echo ""
        if rotate_certificate "$service"; then
            ((rotated_count++))
            rotated_services+=("$service")

            # Restart service
            if restart_service "$service"; then
                log_success "Certificate rotation completed for: $service"
            else
                log_error "Service restart failed for: $service"
                ((failed_count++))
            fi
        else
            log_error "Certificate rotation failed for: $service"
            ((failed_count++))
        fi
        echo ""
    done

    # Summary
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  Rotation Summary"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Certificates Rotated:  $rotated_count"
    echo "Failed:                $failed_count"
    echo ""

    if [[ ${#rotated_services[@]} -gt 0 ]]; then
        echo "Rotated Services:"
        for service in "${rotated_services[@]}"; do
            echo "  ✓ $service"
        done
        echo ""
    fi

    if [[ "$DRY_RUN" != "true" ]]; then
        # Send notification
        if [[ $rotated_count -gt 0 ]]; then
            send_notification \
                "SAHOOL: Certificate Rotation Completed" \
                "Successfully rotated $rotated_count certificate(s): ${rotated_services[*]}"
        fi

        # Log rotation to file
        local log_file="$CERT_BASE_DIR/rotation.log"
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - Rotated $rotated_count certificates: ${rotated_services[*]}" >> "$log_file"
    fi

    echo "═══════════════════════════════════════════════════════════════════════════════"

    if [[ $failed_count -gt 0 ]]; then
        log_error "Certificate rotation completed with errors"
        exit 1
    else
        log_success "Certificate rotation completed successfully!"

        if [[ "$DRY_RUN" != "true" ]]; then
            echo ""
            log_info "Next Steps:"
            log_detail "1. Verify services are running: docker-compose ps"
            log_detail "2. Test connectivity to services"
            log_detail "3. Check logs for any TLS errors"
            log_detail "4. Validate new certificates: ./validate-certs.sh"
        fi
    fi

    exit 0
}

# Run main function
main "$@"
