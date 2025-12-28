#!/bin/bash
#
# SAHOOL Canary Promotion Script
# Promotes canary deployment to stable after verifying metrics and health
#
# Usage: ./canary-promote.sh [OPTIONS]
#
# Options:
#   -n, --namespace NAMESPACE    Kubernetes namespace (default: sahool)
#   -s, --service SERVICE        Service name (default: sahool-agent)
#   -f, --force                  Skip verification checks (USE WITH CAUTION)
#   -d, --dry-run                Show what would be done without executing
#   -w, --wait                   Wait time in seconds for traffic shift (default: 300)
#   -t, --threshold THRESHOLD    Success rate threshold (default: 0.95)
#   --skip-metrics               Skip metrics verification
#   --skip-health                Skip health checks
#   -h, --help                   Show this help message
#
# Examples:
#   ./canary-promote.sh
#   ./canary-promote.sh --namespace production --service my-service
#   ./canary-promote.sh --dry-run
#   ./canary-promote.sh --force --skip-metrics
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="${NAMESPACE:-sahool}"
SERVICE_NAME="${SERVICE_NAME:-sahool-agent}"
FORCE=false
DRY_RUN=false
WAIT_TIME=300
SUCCESS_THRESHOLD=0.95
SKIP_METRICS=false
SKIP_HEALTH=false
PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus.monitoring.svc.cluster.local:9090}"
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

# Send notification to Slack
send_notification() {
    local message=$1
    local color=${2:-"good"}

    if [[ -n "$SLACK_WEBHOOK" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"text\":\"$message\"}]}" \
            "$SLACK_WEBHOOK" 2>/dev/null || log_warning "Failed to send Slack notification"
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
            -f|--force)
                FORCE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -w|--wait)
                WAIT_TIME="$2"
                shift 2
                ;;
            -t|--threshold)
                SUCCESS_THRESHOLD="$2"
                shift 2
                ;;
            --skip-metrics)
                SKIP_METRICS=true
                shift
                ;;
            --skip-health)
                SKIP_HEALTH=true
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
    command -v curl >/dev/null 2>&1 || missing_tools+=("curl")
    command -v jq >/dev/null 2>&1 || missing_tools+=("jq")

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install missing tools and try again"
        exit 1
    fi

    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        log_error "Please check your kubeconfig and cluster connectivity"
        exit 1
    fi

    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_error "Namespace '$NAMESPACE' does not exist"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Check if canary deployment exists
check_canary_exists() {
    log_info "Checking if canary deployment exists..."

    if ! kubectl get deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" >/dev/null 2>&1; then
        log_error "Canary deployment '${SERVICE_NAME}-canary' not found in namespace '$NAMESPACE'"
        exit 1
    fi

    log_success "Canary deployment found"
}

# Check canary pod health
check_canary_health() {
    if [[ "$SKIP_HEALTH" == "true" ]]; then
        log_warning "Skipping health checks (--skip-health)"
        return 0
    fi

    log_info "Checking canary pod health..."

    local ready_pods
    ready_pods=$(kubectl get deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

    local desired_pods
    desired_pods=$(kubectl get deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" \
        -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

    if [[ "$ready_pods" -lt "$desired_pods" ]]; then
        log_error "Canary pods not ready: $ready_pods/$desired_pods"
        log_error "Please ensure all canary pods are healthy before promotion"
        return 1
    fi

    log_success "All canary pods are healthy ($ready_pods/$desired_pods)"

    # Check pod restart count
    local max_restarts=3
    local pods_with_restarts
    pods_with_restarts=$(kubectl get pods -n "$NAMESPACE" \
        -l "app=${SERVICE_NAME},deployment-type=canary" \
        -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}' | \
        awk -v max="$max_restarts" '$2 > max {print $1}')

    if [[ -n "$pods_with_restarts" ]]; then
        log_warning "Some canary pods have excessive restarts:"
        echo "$pods_with_restarts"

        if [[ "$FORCE" != "true" ]]; then
            log_error "Use --force to proceed despite pod restarts"
            return 1
        fi
    fi

    return 0
}

# Query Prometheus for metrics
query_prometheus() {
    local query=$1
    local result

    result=$(curl -s -G --data-urlencode "query=$query" \
        "${PROMETHEUS_URL}/api/v1/query" 2>/dev/null | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "")

    if [[ -z "$result" ]] || [[ "$result" == "null" ]]; then
        return 1
    fi

    echo "$result"
}

# Check canary metrics
check_canary_metrics() {
    if [[ "$SKIP_METRICS" == "true" ]]; then
        log_warning "Skipping metrics verification (--skip-metrics)"
        return 0
    fi

    log_info "Verifying canary metrics..."

    # Check success rate
    log_info "Checking success rate (threshold: $SUCCESS_THRESHOLD)..."
    local success_rate_query="sum(rate(http_requests_total{service=\"${SERVICE_NAME}-canary\",status=~\"2..\"}[5m])) / sum(rate(http_requests_total{service=\"${SERVICE_NAME}-canary\"}[5m]))"
    local success_rate
    success_rate=$(query_prometheus "$success_rate_query")

    if [[ -n "$success_rate" ]]; then
        log_info "Current success rate: $success_rate"
        if (( $(echo "$success_rate < $SUCCESS_THRESHOLD" | bc -l) )); then
            log_error "Success rate below threshold: $success_rate < $SUCCESS_THRESHOLD"
            if [[ "$FORCE" != "true" ]]; then
                return 1
            fi
            log_warning "Proceeding despite low success rate (--force)"
        else
            log_success "Success rate: $success_rate ✓"
        fi
    else
        log_warning "Could not retrieve success rate metrics"
        if [[ "$FORCE" != "true" ]]; then
            log_error "Use --force to proceed without metrics"
            return 1
        fi
    fi

    # Check error rate
    log_info "Checking error rate..."
    local error_rate_query="sum(rate(http_requests_total{service=\"${SERVICE_NAME}-canary\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"${SERVICE_NAME}-canary\"}[5m]))"
    local error_rate
    error_rate=$(query_prometheus "$error_rate_query")

    if [[ -n "$error_rate" ]]; then
        log_info "Current error rate: $error_rate"
        if (( $(echo "$error_rate > 0.05" | bc -l) )); then
            log_warning "Error rate is high: $error_rate"
            if [[ "$FORCE" != "true" ]]; then
                return 1
            fi
        else
            log_success "Error rate: $error_rate ✓"
        fi
    fi

    # Check latency (P95)
    log_info "Checking P95 latency..."
    local latency_query="histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=\"${SERVICE_NAME}-canary\"}[5m])) by (le)) * 1000"
    local p95_latency
    p95_latency=$(query_prometheus "$latency_query")

    if [[ -n "$p95_latency" ]]; then
        log_info "Current P95 latency: ${p95_latency}ms"
        if (( $(echo "$p95_latency > 1000" | bc -l) )); then
            log_warning "P95 latency is high: ${p95_latency}ms"
        else
            log_success "P95 latency: ${p95_latency}ms ✓"
        fi
    fi

    log_success "Metrics verification completed"
    return 0
}

# Promote canary to stable using Argo Rollouts
promote_with_argo_rollouts() {
    log_info "Promoting canary using Argo Rollouts..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would promote rollout: ${SERVICE_NAME}"
        return 0
    fi

    # Promote the rollout
    if kubectl argo rollouts promote "$SERVICE_NAME" -n "$NAMESPACE" 2>/dev/null; then
        log_success "Rollout promoted successfully"

        # Wait for rollout to complete
        log_info "Waiting for rollout to complete (timeout: ${WAIT_TIME}s)..."
        if kubectl argo rollouts status "$SERVICE_NAME" -n "$NAMESPACE" --timeout="${WAIT_TIME}s" 2>/dev/null; then
            log_success "Rollout completed successfully"
            return 0
        else
            log_error "Rollout did not complete within timeout"
            return 1
        fi
    else
        log_warning "Argo Rollouts CLI not available, using manual promotion..."
        promote_manual
    fi
}

# Manual promotion (without Argo Rollouts)
promote_manual() {
    log_info "Performing manual promotion..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would perform manual promotion"
        return 0
    fi

    # Update stable deployment with canary image
    local canary_image
    canary_image=$(kubectl get deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" \
        -o jsonpath='{.spec.template.spec.containers[0].image}')

    log_info "Updating stable deployment with image: $canary_image"

    kubectl set image "deployment/${SERVICE_NAME}-stable" \
        "${SERVICE_NAME}=${canary_image}" -n "$NAMESPACE"

    # Wait for rollout
    log_info "Waiting for stable deployment rollout..."
    kubectl rollout status "deployment/${SERVICE_NAME}-stable" -n "$NAMESPACE" \
        --timeout="${WAIT_TIME}s"

    # Update traffic weights to 100% stable
    log_info "Updating traffic weights to 100% stable..."
    update_traffic_weights 0 100

    log_success "Manual promotion completed"
}

# Update traffic weights in Istio VirtualService
update_traffic_weights() {
    local canary_weight=$1
    local stable_weight=$2

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would update traffic weights: canary=$canary_weight%, stable=$stable_weight%"
        return 0
    fi

    log_info "Updating traffic weights: canary=$canary_weight%, stable=$stable_weight%"

    # Update VirtualService if it exists
    if kubectl get virtualservice "$SERVICE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
        kubectl patch virtualservice "$SERVICE_NAME" -n "$NAMESPACE" --type='json' \
            -p="[{\"op\": \"replace\", \"path\": \"/spec/http/0/route/0/weight\", \"value\": $canary_weight},
                 {\"op\": \"replace\", \"path\": \"/spec/http/0/route/1/weight\", \"value\": $stable_weight}]" \
            2>/dev/null || log_warning "Could not update VirtualService traffic weights"
    fi
}

# Scale down canary deployment
scale_down_canary() {
    log_info "Scaling down canary deployment..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would scale down canary deployment"
        return 0
    fi

    kubectl scale deployment "${SERVICE_NAME}-canary" -n "$NAMESPACE" --replicas=0

    log_success "Canary deployment scaled down"
}

# Main function
main() {
    parse_args "$@"

    log_info "=== SAHOOL Canary Promotion ==="
    log_info "Namespace: $NAMESPACE"
    log_info "Service: $SERVICE_NAME"
    log_info "Force: $FORCE"
    log_info "Dry Run: $DRY_RUN"
    log_info ""

    # Send start notification
    send_notification "🚀 Starting canary promotion for ${SERVICE_NAME} in ${NAMESPACE}" "warning"

    # Run checks
    check_prerequisites
    check_canary_exists

    if ! check_canary_health; then
        log_error "Canary health check failed"
        send_notification "❌ Canary promotion failed for ${SERVICE_NAME}: Health check failed" "danger"
        exit 1
    fi

    if ! check_canary_metrics; then
        log_error "Canary metrics verification failed"
        send_notification "❌ Canary promotion failed for ${SERVICE_NAME}: Metrics verification failed" "danger"
        exit 1
    fi

    # Confirm promotion
    if [[ "$FORCE" != "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
        log_warning "About to promote canary to stable. This will update production traffic."
        read -p "Continue? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_info "Promotion cancelled by user"
            exit 0
        fi
    fi

    # Promote canary
    if ! promote_with_argo_rollouts; then
        log_error "Promotion failed"
        send_notification "❌ Canary promotion failed for ${SERVICE_NAME}" "danger"
        exit 1
    fi

    # Scale down canary (optional)
    # scale_down_canary

    log_success "=== Canary promotion completed successfully ==="
    send_notification "✅ Canary promotion completed successfully for ${SERVICE_NAME} in ${NAMESPACE}" "good"
}

# Run main function
main "$@"
