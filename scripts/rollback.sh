#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Emergency Rollback Script
# Quickly rollback deployments in case of critical failures
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ───────────────────────────────────────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${ENVIRONMENT:-staging}"
NAMESPACE=""
ROLLBACK_REVISION=""
SERVICE=""
ALL_SERVICES=false
DRY_RUN=false
SKIP_CONFIRMATION=false
NOTIFICATION_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

# Service lists
STARTER_SERVICES=("field-ops" "weather-core" "agro-advisor")
PROFESSIONAL_SERVICES=("${STARTER_SERVICES[@]}" "crop-health" "ndvi-engine" "irrigation-smart")
ENTERPRISE_SERVICES=("${PROFESSIONAL_SERVICES[@]}" "satellite-service" "weather-advanced" "crop-health-ai" "yield-engine" "billing-core" "inventory-service")

# ───────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}━━━${NC} $1 ${BLUE}━━━${NC}"
}

show_usage() {
    cat << EOF
SAHOOL Emergency Rollback Script

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Target environment (staging|production) [default: staging]
    -s, --service SERVICE       Service to rollback (optional, rollback all if not specified)
    -r, --revision REVISION     Specific revision to rollback to (optional, uses previous if not specified)
    -a, --all                   Rollback all services
    -n, --namespace NAMESPACE   Kubernetes namespace (optional, auto-detected from environment)
    -d, --dry-run               Show what would be done without executing
    -y, --yes                   Skip confirmation prompts
    -h, --help                  Show this help message

Examples:
    # Rollback all services in staging
    $0 -e staging -a

    # Rollback specific service in production
    $0 -e production -s field-ops

    # Rollback to specific revision
    $0 -e staging -s weather-core -r 5

    # Dry run to see what would happen
    $0 -e production -a --dry-run

Environment Variables:
    ENVIRONMENT                 Target environment (same as -e)
    SLACK_WEBHOOK_URL          Slack webhook for notifications
    KUBE_CONFIG_STAGING        Kubeconfig for staging (base64 encoded)
    KUBE_CONFIG_PRODUCTION     Kubeconfig for production (base64 encoded)

EOF
}

# ───────────────────────────────────────────────────────────────────────────────
# Parse Arguments
# ───────────────────────────────────────────────────────────────────────────────

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -s|--service)
                SERVICE="$2"
                shift 2
                ;;
            -r|--revision)
                ROLLBACK_REVISION="$2"
                shift 2
                ;;
            -a|--all)
                ALL_SERVICES=true
                shift
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -y|--yes)
                SKIP_CONFIRMATION=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# ───────────────────────────────────────────────────────────────────────────────
# Validation
# ───────────────────────────────────────────────────────────────────────────────

validate_environment() {
    if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
        log_error "Invalid environment: $ENVIRONMENT (must be staging or production)"
        exit 1
    fi

    # Set namespace if not provided
    if [[ -z "$NAMESPACE" ]]; then
        if [[ "$ENVIRONMENT" == "production" ]]; then
            NAMESPACE="sahool-production"
        else
            NAMESPACE="sahool-staging"
        fi
    fi

    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
}

validate_prerequisites() {
    log_step "Validating Prerequisites"

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    log_success "kubectl found"

    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed"
        exit 1
    fi
    log_success "helm found"

    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        log_info "Make sure your kubeconfig is properly configured"
        exit 1
    fi
    log_success "Connected to Kubernetes cluster"

    # Verify namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE does not exist"
        exit 1
    fi
    log_success "Namespace $NAMESPACE exists"
}

# ───────────────────────────────────────────────────────────────────────────────
# Service Discovery
# ───────────────────────────────────────────────────────────────────────────────

get_services_to_rollback() {
    local services=()

    if [[ -n "$SERVICE" ]]; then
        # Single service specified
        services=("$SERVICE")
    elif [[ "$ALL_SERVICES" == true ]]; then
        # Get all deployed services from namespace
        mapfile -t services < <(helm list -n "$NAMESPACE" -q)

        if [[ ${#services[@]} -eq 0 ]]; then
            log_warning "No Helm releases found in namespace $NAMESPACE"
            return 1
        fi
    else
        log_error "Must specify either a service (-s) or all services (-a)"
        show_usage
        exit 1
    fi

    echo "${services[@]}"
}

# ───────────────────────────────────────────────────────────────────────────────
# Rollback Functions
# ───────────────────────────────────────────────────────────────────────────────

get_rollback_revision() {
    local service=$1
    local revision=""

    if [[ -n "$ROLLBACK_REVISION" ]]; then
        revision="$ROLLBACK_REVISION"
    else
        # Get previous revision (current - 1)
        local current_revision
        current_revision=$(helm list -n "$NAMESPACE" -f "^${service}$" -o json | jq -r '.[0].revision // 0')

        if [[ "$current_revision" -le 1 ]]; then
            log_warning "Service $service is at revision $current_revision, cannot rollback"
            return 1
        fi

        revision=$((current_revision - 1))
    fi

    echo "$revision"
}

show_helm_history() {
    local service=$1

    log_info "Helm history for $service:"
    helm history "$service" -n "$NAMESPACE" --max 10 2>/dev/null || {
        log_warning "No history found for $service"
        return 1
    }
}

rollback_service() {
    local service=$1

    log_step "Rolling back $service"

    # Check if release exists
    if ! helm list -n "$NAMESPACE" -f "^${service}$" -q | grep -q "^${service}$"; then
        log_warning "Helm release $service not found in namespace $NAMESPACE"
        return 1
    fi

    # Show history
    show_helm_history "$service"

    # Get rollback revision
    local revision
    revision=$(get_rollback_revision "$service") || return 1

    log_info "Rolling back $service to revision $revision..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would execute: helm rollback $service $revision -n $NAMESPACE --wait --timeout 10m"
        return 0
    fi

    # Execute rollback
    if helm rollback "$service" "$revision" -n "$NAMESPACE" --wait --timeout 10m; then
        log_success "Successfully rolled back $service to revision $revision"

        # Verify rollback
        kubectl rollout status deployment/"$service" -n "$NAMESPACE" --timeout=5m 2>/dev/null || {
            log_warning "Could not verify deployment status for $service"
        }

        return 0
    else
        log_error "Failed to rollback $service"
        return 1
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# Notification Functions
# ───────────────────────────────────────────────────────────────────────────────

send_notification() {
    local status=$1
    local message=$2

    if [[ -z "$NOTIFICATION_WEBHOOK" ]]; then
        return 0
    fi

    local color="danger"
    local emoji="🚨"

    if [[ "$status" == "success" ]]; then
        color="good"
        emoji="✅"
    elif [[ "$status" == "warning" ]]; then
        color="warning"
        emoji="⚠️"
    fi

    local payload
    payload=$(cat <<EOF
{
  "text": "$emoji SAHOOL Rollback - $ENVIRONMENT",
  "attachments": [
    {
      "color": "$color",
      "fields": [
        {
          "title": "Environment",
          "value": "$ENVIRONMENT",
          "short": true
        },
        {
          "title": "Namespace",
          "value": "$NAMESPACE",
          "short": true
        },
        {
          "title": "Status",
          "value": "$message",
          "short": false
        },
        {
          "title": "Executed by",
          "value": "${USER:-unknown}",
          "short": true
        },
        {
          "title": "Timestamp",
          "value": "$(date -u +'%Y-%m-%d %H:%M:%S UTC')",
          "short": true
        }
      ]
    }
  ]
}
EOF
)

    curl -s -X POST -H 'Content-type: application/json' --data "$payload" "$NOTIFICATION_WEBHOOK" > /dev/null || {
        log_warning "Failed to send notification"
    }
}

# ───────────────────────────────────────────────────────────────────────────────
# Confirmation
# ───────────────────────────────────────────────────────────────────────────────

confirm_rollback() {
    if [[ "$SKIP_CONFIRMATION" == true ]]; then
        return 0
    fi

    log_warning "You are about to rollback services in $ENVIRONMENT environment"
    log_warning "Namespace: $NAMESPACE"

    if [[ "$ALL_SERVICES" == true ]]; then
        log_warning "ALL services will be rolled back"
    else
        log_warning "Service: $SERVICE"
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "This is a DRY RUN - no changes will be made"
    fi

    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# Main Execution
# ───────────────────────────────────────────────────────────────────────────────

main() {
    log_step "SAHOOL Emergency Rollback"

    parse_args "$@"
    validate_environment
    validate_prerequisites

    # Get services to rollback
    local services
    IFS=' ' read -r -a services <<< "$(get_services_to_rollback)"

    if [[ ${#services[@]} -eq 0 ]]; then
        log_error "No services to rollback"
        exit 1
    fi

    log_info "Services to rollback: ${services[*]}"

    # Confirm rollback
    confirm_rollback

    # Send notification
    send_notification "warning" "Rollback started for ${#services[@]} service(s)"

    # Execute rollback
    local success_count=0
    local failure_count=0
    local failed_services=()

    for svc in "${services[@]}"; do
        if rollback_service "$svc"; then
            ((success_count++))
        else
            ((failure_count++))
            failed_services+=("$svc")
        fi
    done

    # Summary
    log_step "Rollback Summary"
    log_info "Total services: ${#services[@]}"
    log_success "Successful rollbacks: $success_count"

    if [[ $failure_count -gt 0 ]]; then
        log_error "Failed rollbacks: $failure_count"
        log_error "Failed services: ${failed_services[*]}"

        send_notification "danger" "Rollback completed with $failure_count failure(s): ${failed_services[*]}"
        exit 1
    else
        log_success "All services rolled back successfully"
        send_notification "success" "Rollback completed successfully for ${#services[@]} service(s)"
    fi

    # Final verification
    log_step "Verifying Services"

    for svc in "${services[@]}"; do
        local status
        status=$(kubectl get deployment "$svc" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown")

        if [[ "$status" == "True" ]]; then
            log_success "$svc is available"
        else
            log_warning "$svc status: $status"
        fi
    done

    log_success "Rollback complete!"
}

# Run main function
main "$@"
