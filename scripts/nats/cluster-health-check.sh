#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL NATS Cluster Health Check Script
# Comprehensive health monitoring for NATS cluster
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./scripts/nats/cluster-health-check.sh [options]
#
# Options:
#   -e, --environment ENV    Environment (docker|kubernetes) [default: docker]
#   -n, --namespace NS       Kubernetes namespace [default: nats-system]
#   -c, --continuous         Run continuously (every 30 seconds)
#   -v, --verbose            Verbose output
#   -j, --json               Output in JSON format
#   -a, --alerts             Check for alerts and anomalies
#   -h, --help               Show this help message
#
# Examples:
#   ./scripts/nats/cluster-health-check.sh
#   ./scripts/nats/cluster-health-check.sh -e kubernetes -n nats-system
#   ./scripts/nats/cluster-health-check.sh -c -v
#   ./scripts/nats/cluster-health-check.sh -j > health-report.json
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
ENVIRONMENT="${NATS_ENV:-docker}"
NAMESPACE="nats-system"
CONTINUOUS=false
VERBOSE=false
JSON_OUTPUT=false
CHECK_ALERTS=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Thresholds
MAX_CONNECTIONS_WARNING=1500
MAX_CONNECTIONS_CRITICAL=1800
MAX_MEMORY_PCT_WARNING=70
MAX_MEMORY_PCT_CRITICAL=85
MAX_CPU_PCT_WARNING=70
MAX_CPU_PCT_CRITICAL=85
MIN_CLUSTER_SIZE=3

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

print_header() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║${NC}  SAHOOL NATS Cluster Health Check"
        echo -e "${BLUE}║${NC}  $(date '+%Y-%m-%d %H:%M:%S %Z')"
        echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
    fi
}

log_info() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${GREEN}[✓]${NC} $1"
    fi
}

log_warning() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${YELLOW}[⚠]${NC} $1"
    fi
}

log_error() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${RED}[✗]${NC} $1"
    fi
}

verbose() {
    if [ "$VERBOSE" = true ] && [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Parse Arguments
# ─────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -c|--continuous)
            CONTINUOUS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        -a|--alerts)
            CHECK_ALERTS=true
            shift
            ;;
        -h|--help)
            grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# //' | sed 's/^#//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────────────────────────────────────
# Environment Detection
# ─────────────────────────────────────────────────────────────────────────────

detect_environment() {
    if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
        ENVIRONMENT="kubernetes"
        verbose "Detected Kubernetes environment"
    elif command -v docker &> /dev/null && docker ps &> /dev/null; then
        ENVIRONMENT="docker"
        verbose "Detected Docker environment"
    else
        log_error "Could not detect environment (Docker or Kubernetes not available)"
        exit 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Docker Functions
# ─────────────────────────────────────────────────────────────────────────────

check_docker_nodes() {
    local nodes=(
        "sahool-nats-node1:8222"
        "sahool-nats-node2:8223"
        "sahool-nats-node3:8224"
    )

    local healthy_nodes=0
    local node_data='{"nodes":[]}'

    for node in "${nodes[@]}"; do
        IFS=':' read -r container port <<< "$node"

        verbose "Checking node: $container"

        # Check if container is running
        if ! docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            log_error "Node $container is not running"
            continue
        fi

        # Check health endpoint
        if ! curl -sf "http://localhost:${port}/healthz" > /dev/null 2>&1; then
            log_error "Node $container health check failed"
            continue
        fi

        # Get node stats
        local varz=$(curl -sf "http://localhost:${port}/varz" 2>/dev/null || echo "{}")
        local connz=$(curl -sf "http://localhost:${port}/connz" 2>/dev/null || echo "{}")
        local routez=$(curl -sf "http://localhost:${port}/routez" 2>/dev/null || echo "{}")
        local jsz=$(curl -sf "http://localhost:${port}/jsz" 2>/dev/null || echo "{}")

        # Parse data
        local server_name=$(echo "$varz" | jq -r '.server_name // "unknown"')
        local connections=$(echo "$varz" | jq -r '.connections // 0')
        local in_msgs=$(echo "$varz" | jq -r '.in_msgs // 0')
        local out_msgs=$(echo "$varz" | jq -r '.out_msgs // 0')
        local in_bytes=$(echo "$varz" | jq -r '.in_bytes // 0')
        local out_bytes=$(echo "$varz" | jq -r '.out_bytes // 0')
        local mem=$(echo "$varz" | jq -r '.mem // 0')
        local cpu=$(echo "$varz" | jq -r '.cpu // 0')
        local routes=$(echo "$routez" | jq -r '.num_routes // 0')

        # JetStream stats
        local js_memory=$(echo "$jsz" | jq -r '.memory // 0')
        local js_storage=$(echo "$jsz" | jq -r '.store // 0')
        local js_streams=$(echo "$jsz" | jq -r '.streams // 0')

        log_success "Node $container is healthy"

        if [ "$VERBOSE" = true ]; then
            echo "  Server: $server_name"
            echo "  Connections: $connections"
            echo "  Messages: In=$in_msgs, Out=$out_msgs"
            echo "  Bytes: In=$(numfmt --to=iec-i --suffix=B $in_bytes), Out=$(numfmt --to=iec-i --suffix=B $out_bytes)"
            echo "  Memory: $(numfmt --to=iec-i --suffix=B $mem)"
            echo "  CPU: ${cpu}%"
            echo "  Cluster Routes: $routes"
            echo "  JetStream: Memory=$(numfmt --to=iec-i --suffix=B $js_memory), Storage=$(numfmt --to=iec-i --suffix=B $js_storage), Streams=$js_streams"
        fi

        # Check thresholds
        if [ "$CHECK_ALERTS" = true ]; then
            if [ "$connections" -ge "$MAX_CONNECTIONS_CRITICAL" ]; then
                log_error "CRITICAL: $container has $connections connections (threshold: $MAX_CONNECTIONS_CRITICAL)"
            elif [ "$connections" -ge "$MAX_CONNECTIONS_WARNING" ]; then
                log_warning "WARNING: $container has $connections connections (threshold: $MAX_CONNECTIONS_WARNING)"
            fi
        fi

        healthy_nodes=$((healthy_nodes + 1))
    done

    echo ""
    log_info "Healthy nodes: $healthy_nodes/${#nodes[@]}"

    if [ "$healthy_nodes" -lt "$MIN_CLUSTER_SIZE" ]; then
        log_error "Cluster is unhealthy: only $healthy_nodes nodes are running (minimum: $MIN_CLUSTER_SIZE)"
        return 1
    fi

    log_success "Cluster is healthy: $healthy_nodes nodes are running"
    return 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Kubernetes Functions
# ─────────────────────────────────────────────────────────────────────────────

check_kubernetes_nodes() {
    verbose "Checking Kubernetes NATS cluster in namespace: $NAMESPACE"

    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE does not exist"
        return 1
    fi

    # Get NATS pods
    local pods=$(kubectl get pods -n "$NAMESPACE" -l app=nats --no-headers 2>/dev/null)

    if [ -z "$pods" ]; then
        log_error "No NATS pods found in namespace $NAMESPACE"
        return 1
    fi

    local total_pods=$(echo "$pods" | wc -l)
    local ready_pods=$(echo "$pods" | awk '$2 ~ /^[0-9]+\/[0-9]+$/ {split($2, a, "/"); if (a[1] == a[2]) print $1}' | wc -l)

    log_info "NATS pods: $ready_pods/$total_pods ready"

    # Check each pod
    while IFS= read -r line; do
        local pod_name=$(echo "$line" | awk '{print $1}')
        local pod_status=$(echo "$line" | awk '{print $3}')
        local pod_ready=$(echo "$line" | awk '{print $2}')

        if [ "$pod_status" = "Running" ] && [[ "$pod_ready" =~ ^[0-9]+/[0-9]+$ ]]; then
            IFS='/' read -r ready total <<< "$pod_ready"

            if [ "$ready" = "$total" ]; then
                log_success "Pod $pod_name is healthy ($pod_ready)"

                # Get detailed metrics if verbose
                if [ "$VERBOSE" = true ]; then
                    # Port forward and check metrics
                    kubectl exec -n "$NAMESPACE" "$pod_name" -- wget -qO- http://localhost:8222/varz 2>/dev/null | jq -r '
                        "  Server: \(.server_name)",
                        "  Connections: \(.connections)",
                        "  Messages: In=\(.in_msgs), Out=\(.out_msgs)",
                        "  Memory: \(.mem)",
                        "  CPU: \(.cpu)%",
                        "  Uptime: \(.uptime)"
                    ' 2>/dev/null || echo "  (Could not fetch detailed metrics)"
                fi
            else
                log_warning "Pod $pod_name is not fully ready ($pod_ready)"
            fi
        else
            log_error "Pod $pod_name is not healthy (Status: $pod_status, Ready: $pod_ready)"
        fi
    done <<< "$pods"

    # Check StatefulSet
    local statefulset=$(kubectl get statefulset -n "$NAMESPACE" nats --no-headers 2>/dev/null)

    if [ -n "$statefulset" ]; then
        local desired=$(echo "$statefulset" | awk '{print $2}')
        local current=$(echo "$statefulset" | awk '{print $3}')

        log_info "StatefulSet: $current/$desired replicas ready"

        if [ "$current" = "$desired" ]; then
            log_success "StatefulSet is fully scaled"
        else
            log_warning "StatefulSet is not fully scaled ($current/$desired)"
        fi
    fi

    # Check PVCs
    local pvcs=$(kubectl get pvc -n "$NAMESPACE" -l app=nats --no-headers 2>/dev/null)

    if [ -n "$pvcs" ]; then
        local pvc_count=$(echo "$pvcs" | wc -l)
        local bound_pvcs=$(echo "$pvcs" | grep "Bound" | wc -l)

        log_info "PersistentVolumeClaims: $bound_pvcs/$pvc_count bound"

        if [ "$bound_pvcs" = "$pvc_count" ]; then
            log_success "All PVCs are bound"
        else
            log_warning "Not all PVCs are bound ($bound_pvcs/$pvc_count)"
        fi
    fi

    # Check Services
    local services=$(kubectl get svc -n "$NAMESPACE" -l app=nats --no-headers 2>/dev/null)

    if [ -n "$services" ]; then
        local svc_count=$(echo "$services" | wc -l)
        log_success "Services: $svc_count found"
    else
        log_warning "No services found for NATS"
    fi

    # Overall health
    if [ "$ready_pods" -ge "$MIN_CLUSTER_SIZE" ]; then
        echo ""
        log_success "Cluster is healthy: $ready_pods pods are ready"
        return 0
    else
        echo ""
        log_error "Cluster is unhealthy: only $ready_pods pods are ready (minimum: $MIN_CLUSTER_SIZE)"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Cluster Connectivity Test
# ─────────────────────────────────────────────────────────────────────────────

test_cluster_connectivity() {
    log_info "Testing cluster connectivity..."

    if [ "$ENVIRONMENT" = "docker" ]; then
        # Test publishing to NATS
        if docker exec sahool-nats-node1 nats pub --server=nats://localhost:4222 test.health "$(date)" 2>/dev/null; then
            log_success "Successfully published test message"
        else
            log_error "Failed to publish test message"
            return 1
        fi
    elif [ "$ENVIRONMENT" = "kubernetes" ]; then
        # Get first NATS pod
        local pod=$(kubectl get pods -n "$NAMESPACE" -l app=nats --no-headers | head -1 | awk '{print $1}')

        if [ -n "$pod" ]; then
            if kubectl exec -n "$NAMESPACE" "$pod" -- nats pub --server=nats://localhost:4222 test.health "$(date)" 2>/dev/null; then
                log_success "Successfully published test message"
            else
                log_error "Failed to publish test message"
                return 1
            fi
        else
            log_error "No NATS pods available for testing"
            return 1
        fi
    fi

    return 0
}

# ─────────────────────────────────────────────────────────────────────────────
# JetStream Health Check
# ─────────────────────────────────────────────────────────────────────────────

check_jetstream() {
    log_info "Checking JetStream status..."

    if [ "$ENVIRONMENT" = "docker" ]; then
        local jsz=$(curl -sf "http://localhost:8222/jsz" 2>/dev/null || echo "{}")

        local js_enabled=$(echo "$jsz" | jq -r '.enabled // false')
        local js_streams=$(echo "$jsz" | jq -r '.streams // 0')
        local js_consumers=$(echo "$jsz" | jq -r '.consumers // 0')
        local js_messages=$(echo "$jsz" | jq -r '.messages // 0')
        local js_bytes=$(echo "$jsz" | jq -r '.bytes // 0')

        if [ "$js_enabled" = "true" ]; then
            log_success "JetStream is enabled"

            if [ "$VERBOSE" = true ]; then
                echo "  Streams: $js_streams"
                echo "  Consumers: $js_consumers"
                echo "  Messages: $js_messages"
                echo "  Storage: $(numfmt --to=iec-i --suffix=B $js_bytes 2>/dev/null || echo ${js_bytes}B)"
            fi
        else
            log_warning "JetStream is not enabled"
        fi
    elif [ "$ENVIRONMENT" = "kubernetes" ]; then
        local pod=$(kubectl get pods -n "$NAMESPACE" -l app=nats --no-headers | head -1 | awk '{print $1}')

        if [ -n "$pod" ]; then
            local jsz=$(kubectl exec -n "$NAMESPACE" "$pod" -- wget -qO- http://localhost:8222/jsz 2>/dev/null || echo "{}")

            local js_enabled=$(echo "$jsz" | jq -r '.enabled // false')

            if [ "$js_enabled" = "true" ]; then
                log_success "JetStream is enabled"
            else
                log_warning "JetStream is not enabled"
            fi
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Health Check Function
# ─────────────────────────────────────────────────────────────────────────────

run_health_check() {
    print_header

    # Detect environment if not specified
    if [ -z "$ENVIRONMENT" ]; then
        detect_environment
    fi

    log_info "Environment: $ENVIRONMENT"

    # Run environment-specific checks
    local health_status=0

    if [ "$ENVIRONMENT" = "docker" ]; then
        check_docker_nodes || health_status=1
    elif [ "$ENVIRONMENT" = "kubernetes" ]; then
        check_kubernetes_nodes || health_status=1
    else
        log_error "Unknown environment: $ENVIRONMENT"
        return 1
    fi

    # Additional checks
    echo ""
    test_cluster_connectivity || health_status=1

    echo ""
    check_jetstream

    # Summary
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"

    if [ $health_status -eq 0 ]; then
        echo -e "${BLUE}║${NC} ${GREEN}Overall Status: HEALTHY ✓${NC}"
    else
        echo -e "${BLUE}║${NC} ${RED}Overall Status: UNHEALTHY ✗${NC}"
    fi

    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

    return $health_status
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────────────────────

main() {
    # Check dependencies
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Please install jq."
        exit 1
    fi

    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed. Please install curl."
        exit 1
    fi

    # Run health check
    if [ "$CONTINUOUS" = true ]; then
        while true; do
            run_health_check
            echo ""
            log_info "Waiting 30 seconds before next check..."
            sleep 30
        done
    else
        run_health_check
        exit $?
    fi
}

# Run main function
main
