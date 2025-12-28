#!/bin/bash
#
# SAHOOL Emergency Rollback Script
# Quickly rollback failed deployments and restore service
#
# Usage: ./rollback.sh [OPTIONS]
#
# Options:
#   -n, --namespace NAMESPACE       Kubernetes namespace (default: sahool)
#   -s, --service SERVICE           Service name (default: sahool-agent)
#   -r, --revision REVISION         Target revision to rollback to (default: previous)
#   -t, --type TYPE                 Rollback type: rollout|deployment|traffic (default: auto)
#   -f, --force                     Skip confirmation prompts
#   -d, --dry-run                   Show what would be done without executing
#   --zero-downtime                 Use traffic shifting for zero-downtime rollback
#   --immediate                     Immediate rollback (ignore traffic shifting)
#   --notify                        Send notifications (requires SLACK_WEBHOOK)
#   -h, --help                      Show this help message
#
# Examples:
#   ./rollback.sh                                    # Auto-detect and rollback
#   ./rollback.sh --service my-service --revision 5  # Rollback to specific revision
#   ./rollback.sh --type traffic --zero-downtime     # Traffic-only rollback
#   ./rollback.sh --immediate --force                # Emergency immediate rollback
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="${NAMESPACE:-sahool}"
SERVICE_NAME="${SERVICE_NAME:-sahool-agent}"
REVISION=""
ROLLBACK_TYPE="auto"
FORCE=false
DRY_RUN=false
ZERO_DOWNTIME=false
IMMEDIATE=false
NOTIFY=false
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_emergency() {
    echo -e "${MAGENTA}[EMERGENCY]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# Send notification
send_notification() {
    local message=$1
    local color=${2:-"warning"}

    if [[ "$NOTIFY" == "true" ]] && [[ -n "$SLACK_WEBHOOK" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"text\":\"$message\"}]}" \
            "$SLACK_WEBHOOK" 2>/dev/null || log_warning "Failed to send notification"
    fi
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -s|--service)
                SERVICE_NAME="$2"
                shift 2
                ;;
            -r|--revision)
                REVISION="$2"
                shift 2
                ;;
            -t|--type)
                ROLLBACK_TYPE="$2"
                shift 2
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            --zero-downtime)
                ZERO_DOWNTIME=true
                shift
                ;;
            --immediate)
                IMMEDIATE=true
                shift
                ;;
            --notify)
                NOTIFY=true
                shift
                ;;
            -h|--help)
                grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# //'
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
    command -v jq >/dev/null 2>&1 || missing_tools+=("jq")

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi

    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_error "Namespace '$NAMESPACE' does not exist"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Detect rollback type
detect_rollback_type() {
    if [[ "$ROLLBACK_TYPE" != "auto" ]]; then
        log_info "Using specified rollback type: $ROLLBACK_TYPE"
        return
    fi

    log_info "Auto-detecting rollback type..."

    # Check for Argo Rollouts
    if kubectl get rollout "$SERVICE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
        ROLLBACK_TYPE="rollout"
        log_info "Detected Argo Rollouts deployment"
        return
    fi

    # Check for standard deployment
    if kubectl get deployment "$SERVICE_NAME" -n "$NAMESPACE" >/dev/null 2>&1 || \
       kubectl get deployment "${SERVICE_NAME}-stable" -n "$NAMESPACE" >/dev/null 2>&1; then
        ROLLBACK_TYPE="deployment"
        log_info "Detected standard Kubernetes deployment"
        return
    fi

    log_error "Could not detect deployment type"
    exit 1
}

# Get current deployment status
get_deployment_status() {
    log_info "Getting current deployment status..."

    local deployment
    if [[ "$ROLLBACK_TYPE" == "rollout" ]]; then
        kubectl get rollout "$SERVICE_NAME" -n "$NAMESPACE" -o wide
    else
        deployment="${SERVICE_NAME}-stable"
        if ! kubectl get deployment "$deployment" -n "$NAMESPACE" >/dev/null 2>&1; then
            deployment="$SERVICE_NAME"
        fi
        kubectl get deployment "$deployment" -n "$NAMESPACE" -o wide
    fi

    echo ""
    log_info "Recent events:"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | grep "$SERVICE_NAME" | tail -10
}

# Get rollout history
get_rollout_history() {
    log_info "Deployment history:"

    if [[ "$ROLLBACK_TYPE" == "rollout" ]]; then
        kubectl argo rollouts history "$SERVICE_NAME" -n "$NAMESPACE" 2>/dev/null || \
            log_warning "Could not get rollout history (Argo Rollouts CLI required)"
    else
        local deployment="${SERVICE_NAME}-stable"
        if ! kubectl get deployment "$deployment" -n "$NAMESPACE" >/dev/null 2>&1; then
            deployment="$SERVICE_NAME"
        fi
        kubectl rollout history "deployment/$deployment" -n "$NAMESPACE"
    fi
}

# Abort ongoing rollout
abort_rollout() {
    log_emergency "Aborting ongoing rollout..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would abort rollout: $SERVICE_NAME"
        return 0
    fi

    if [[ "$ROLLBACK_TYPE" == "rollout" ]]; then
        if kubectl argo rollouts abort "$SERVICE_NAME" -n "$NAMESPACE" 2>/dev/null; then
            log_success "Rollout aborted"
            return 0
        else
            log_warning "Could not abort rollout (Argo Rollouts CLI required)"
        fi
    fi

    # For deployments, pause the rollout
    local deployment="${SERVICE_NAME}-stable"
    if ! kubectl get deployment "$deployment" -n "$NAMESPACE" >/dev/null 2>&1; then
        deployment="$SERVICE_NAME"
    fi

    kubectl rollout pause "deployment/$deployment" -n "$NAMESPACE" 2>/dev/null || \
        log_warning "Could not pause deployment rollout"
}

# Rollback using Argo Rollouts
rollback_argo_rollout() {
    log_info "Rolling back using Argo Rollouts..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would rollback rollout: $SERVICE_NAME"
        return 0
    fi

    # Undo the rollout
    if kubectl argo rollouts undo "$SERVICE_NAME" -n "$NAMESPACE" ${REVISION:+--to-revision="$REVISION"} 2>/dev/null; then
        log_success "Rollout undo initiated"

        # Wait for rollback to complete
        log_info "Waiting for rollback to complete..."
        kubectl argo rollouts status "$SERVICE_NAME" -n "$NAMESPACE" --timeout=300s 2>/dev/null
        log_success "Rollback completed successfully"
    else
        log_error "Argo Rollouts CLI not available or command failed"
        return 1
    fi
}

# Rollback standard deployment
rollback_deployment() {
    log_info "Rolling back standard deployment..."

    local deployment="${SERVICE_NAME}-stable"
    if ! kubectl get deployment "$deployment" -n "$NAMESPACE" >/dev/null 2>&1; then
        deployment="$SERVICE_NAME"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would rollback deployment: $deployment"
        return 0
    fi

    # Rollback deployment
    if [[ -n "$REVISION" ]]; then
        kubectl rollout undo "deployment/$deployment" -n "$NAMESPACE" --to-revision="$REVISION"
    else
        kubectl rollout undo "deployment/$deployment" -n "$NAMESPACE"
    fi

    # Wait for rollout to complete
    log_info "Waiting for rollback to complete..."
    kubectl rollout status "deployment/$deployment" -n "$NAMESPACE" --timeout=300s

    log_success "Deployment rollback completed"
}

# Traffic-only rollback (shift traffic back to stable)
rollback_traffic() {
    log_info "Performing traffic rollback..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would shift traffic to stable"
        return 0
    fi

    # Set traffic to 0% canary, 100% stable
    if kubectl get virtualservice "$SERVICE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
        log_info "Updating VirtualService to route 100% traffic to stable..."

        kubectl patch virtualservice "$SERVICE_NAME" -n "$NAMESPACE" --type='json' \
            -p='[{"op": "replace", "path": "/spec/http/0/route/0/weight", "value": 0},
                 {"op": "replace", "path": "/spec/http/0/route/1/weight", "value": 100}]' \
            2>/dev/null || log_warning "Could not update VirtualService"

        log_success "Traffic shifted to stable"
    else
        log_warning "VirtualService not found, skipping traffic shift"
    fi

    # If using Argo Rollouts, set weight to 0
    if [[ "$ROLLBACK_TYPE" == "rollout" ]]; then
        kubectl argo rollouts set weight "$SERVICE_NAME" 0 -n "$NAMESPACE" 2>/dev/null || \
            log_warning "Could not set rollout weight"
    fi
}

# Scale down canary deployment
scale_down_canary() {
    log_info "Scaling down canary deployment..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would scale down canary"
        return 0
    fi

    if kubectl get deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" >/dev/null 2>&1; then
        kubectl scale deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" --replicas=0
        log_success "Canary scaled down"
    fi
}

# Verify rollback success
verify_rollback() {
    log_info "Verifying rollback success..."

    local deployment
    if [[ "$ROLLBACK_TYPE" == "rollout" ]]; then
        deployment="$SERVICE_NAME"
    else
        deployment="${SERVICE_NAME}-stable"
        if ! kubectl get deployment "$deployment" -n "$NAMESPACE" >/dev/null 2>&1; then
            deployment="$SERVICE_NAME"
        fi
    fi

    # Check pod health
    local ready_pods
    ready_pods=$(kubectl get deployment "$deployment" -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

    local desired_pods
    desired_pods=$(kubectl get deployment "$deployment" -n "$NAMESPACE" \
        -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

    if [[ "$ready_pods" -lt "$desired_pods" ]]; then
        log_warning "Not all pods are ready: $ready_pods/$desired_pods"
        return 1
    fi

    log_success "All pods are healthy: $ready_pods/$desired_pods"

    # Test service endpoint
    log_info "Testing service health endpoint..."
    local service_ip
    service_ip=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" \
        -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")

    if [[ -n "$service_ip" ]]; then
        if kubectl run test-rollback-curl --rm -i --restart=Never --image=curlimages/curl:latest \
            -n "$NAMESPACE" -- curl -sf "http://${service_ip}:8080/health/ready" >/dev/null 2>&1; then
            log_success "Service health check passed"
        else
            log_warning "Service health check failed"
        fi
    fi

    return 0
}

# Generate rollback report
generate_report() {
    log_info "=== Rollback Report ==="
    echo ""
    echo "Timestamp: $(date)"
    echo "Namespace: $NAMESPACE"
    echo "Service: $SERVICE_NAME"
    echo "Rollback Type: $ROLLBACK_TYPE"
    echo "Target Revision: ${REVISION:-previous}"
    echo ""

    get_deployment_status
    echo ""

    log_info "Pod Status:"
    kubectl get pods -n "$NAMESPACE" -l "app=$SERVICE_NAME" -o wide
    echo ""
}

# Main rollback function
perform_rollback() {
    log_emergency "=== INITIATING EMERGENCY ROLLBACK ==="
    log_emergency "Service: $SERVICE_NAME"
    log_emergency "Namespace: $NAMESPACE"
    log_emergency "Type: $ROLLBACK_TYPE"

    # Send start notification
    send_notification "🚨 EMERGENCY ROLLBACK initiated for ${SERVICE_NAME} in ${NAMESPACE}" "danger"

    # Step 1: Abort ongoing rollout if not immediate
    if [[ "$IMMEDIATE" != "true" ]]; then
        abort_rollout
    fi

    # Step 2: Traffic rollback for zero-downtime
    if [[ "$ZERO_DOWNTIME" == "true" ]] || [[ "$IMMEDIATE" != "true" ]]; then
        rollback_traffic
        sleep 5  # Brief pause for traffic shift
    fi

    # Step 3: Actual rollback
    case "$ROLLBACK_TYPE" in
        rollout)
            if ! rollback_argo_rollout; then
                log_warning "Argo Rollouts rollback failed, falling back to deployment rollback"
                rollback_deployment
            fi
            ;;
        deployment)
            rollback_deployment
            ;;
        traffic)
            # Already done above
            log_success "Traffic rollback completed"
            ;;
        *)
            log_error "Unknown rollback type: $ROLLBACK_TYPE"
            exit 1
            ;;
    esac

    # Step 4: Scale down canary
    scale_down_canary

    # Step 5: Verify rollback
    sleep 10  # Wait for pods to stabilize
    if verify_rollback; then
        log_success "Rollback verification passed"
    else
        log_warning "Rollback verification had warnings, please check manually"
    fi
}

# Main function
main() {
    parse_args "$@"

    log_info "=== SAHOOL Emergency Rollback ==="
    log_info "Namespace: $NAMESPACE"
    log_info "Service: $SERVICE_NAME"
    log_info "Force: $FORCE"
    log_info "Dry Run: $DRY_RUN"
    log_info "Zero Downtime: $ZERO_DOWNTIME"
    log_info "Immediate: $IMMEDIATE"
    echo ""

    # Run checks
    check_prerequisites
    detect_rollback_type

    # Show current status
    get_deployment_status
    echo ""
    get_rollout_history
    echo ""

    # Confirm rollback unless forced or immediate
    if [[ "$FORCE" != "true" ]] && [[ "$IMMEDIATE" != "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
        log_warning "⚠️  EMERGENCY ROLLBACK - This will revert production to previous version"
        log_warning "Service: $SERVICE_NAME"
        log_warning "Namespace: $NAMESPACE"
        read -p "Are you sure you want to proceed? Type 'ROLLBACK' to confirm: " -r
        if [[ "$REPLY" != "ROLLBACK" ]]; then
            log_info "Rollback cancelled by user"
            exit 0
        fi
    fi

    # Perform rollback
    if ! perform_rollback; then
        log_error "Rollback failed"
        send_notification "❌ Rollback FAILED for ${SERVICE_NAME} in ${NAMESPACE}" "danger"
        exit 1
    fi

    # Generate report
    generate_report

    log_success "=== EMERGENCY ROLLBACK COMPLETED ==="
    send_notification "✅ Emergency rollback completed successfully for ${SERVICE_NAME} in ${NAMESPACE}" "good"
}

# Run main function
main "$@"
