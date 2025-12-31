#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL IDP - Advanced Load Testing Runner
# سكريبت اختبار الحمل المتقدم لمنصة سهول
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./run-advanced.sh start              # Start infrastructure (5 instances)
#   ./run-advanced.sh standard [agents]  # Standard test (default: 20 agents)
#   ./run-advanced.sh stress [agents]    # Stress test (50+ agents)
#   ./run-advanced.sh spike [agents]     # Spike test (sudden load)
#   ./run-advanced.sh chaos [level]      # Chaos test (low/medium/high/extreme)
#   ./run-advanced.sh all                # Run all tests
#   ./run-advanced.sh status             # Check status
#   ./run-advanced.sh stop               # Stop services
#   ./run-advanced.sh clean              # Clean everything
#
# ═══════════════════════════════════════════════════════════════════════════════

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose-advanced.yml"
DEFAULT_AGENTS=20

print_banner() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  SAHOOL IDP - Advanced Load Testing"
    echo "  اختبار الحمل المتقدم لمنصة سهول"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running"
        exit 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

start_infrastructure() {
    print_banner
    info "Starting advanced infrastructure (5 app instances)..."
    check_docker

    cd "$SCRIPT_DIR"

    # Start infrastructure
    docker-compose -f "$COMPOSE_FILE" up -d \
        sahool-db sahool-pgbouncer sahool-redis \
        sahool-prometheus sahool-alertmanager \
        sahool-influxdb sahool-grafana

    info "Waiting for databases (30s)..."
    sleep 30

    # Start app instances
    docker-compose -f "$COMPOSE_FILE" up -d \
        sahool-app-1 sahool-app-2 sahool-app-3 sahool-app-4 sahool-app-5 sahool-nginx

    info "Waiting for apps (30s)..."
    sleep 30

    success "Advanced infrastructure started!"
    echo ""
    echo -e "${YELLOW}Access Points:${NC}"
    echo "  Grafana:      http://localhost:3032"
    echo "  Prometheus:   http://localhost:9091"
    echo "  Alertmanager: http://localhost:9094"
    echo "  App LB:       http://localhost:8081"
    echo ""
}

run_standard_test() {
    local agents=${1:-$DEFAULT_AGENTS}
    print_banner
    info "Running STANDARD test ($agents agents)..."

    cd "$SCRIPT_DIR"
    docker-compose -f "$COMPOSE_FILE" --profile standard-test run --rm \
        -e AGENT_COUNT=$agents \
        sahool-k6-standard

    success "Standard test completed!"
}

run_stress_test() {
    local agents=${1:-$DEFAULT_AGENTS}
    print_banner
    info "Running STRESS test ($agents base agents, scaling to $((agents * 5)))..."

    cd "$SCRIPT_DIR"
    docker-compose -f "$COMPOSE_FILE" --profile stress-test run --rm \
        -e AGENT_COUNT=$agents \
        sahool-k6-stress

    success "Stress test completed!"
}

run_spike_test() {
    local agents=${1:-$DEFAULT_AGENTS}
    print_banner
    info "Running SPIKE test (sudden load to $((agents * 10)) agents)..."

    cd "$SCRIPT_DIR"
    docker-compose -f "$COMPOSE_FILE" --profile spike-test run --rm \
        -e AGENT_COUNT=$agents \
        sahool-k6-spike

    success "Spike test completed!"
}

run_chaos_test() {
    local level=${1:-medium}
    local agents=${2:-$DEFAULT_AGENTS}
    print_banner
    info "Running CHAOS test (level: $level)..."

    cd "$SCRIPT_DIR"
    docker-compose -f "$COMPOSE_FILE" --profile chaos-test run --rm \
        -e AGENT_COUNT=$agents \
        -e CHAOS_LEVEL=$level \
        sahool-k6-chaos

    success "Chaos test completed!"
}

run_all_tests() {
    print_banner
    info "Running ALL tests sequentially..."

    run_standard_test $DEFAULT_AGENTS
    sleep 30

    run_stress_test $DEFAULT_AGENTS
    sleep 30

    run_spike_test $DEFAULT_AGENTS
    sleep 30

    run_chaos_test "medium" $DEFAULT_AGENTS

    success "All tests completed! Check Grafana for results."
}

show_status() {
    print_banner
    cd "$SCRIPT_DIR"
    docker-compose -f "$COMPOSE_FILE" ps
}

stop_services() {
    print_banner
    info "Stopping all services..."
    cd "$SCRIPT_DIR"
    docker-compose -f "$COMPOSE_FILE" down
    success "Services stopped."
}

clean_all() {
    print_banner
    warning "This will remove ALL data!"
    read -p "Continue? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        cd "$SCRIPT_DIR"
        docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
        success "Cleanup complete."
    fi
}

show_help() {
    print_banner
    echo "Usage: ./run-advanced.sh <command> [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start              Start advanced infrastructure (5 instances)"
    echo "  standard [agents]  Run standard test (default: 20 agents)"
    echo "  stress [agents]    Run stress test (50+ agents)"
    echo "  spike [agents]     Run spike test (sudden load)"
    echo "  chaos [level]      Run chaos test (low/medium/high/extreme)"
    echo "  all                Run all tests sequentially"
    echo "  status             Check service status"
    echo "  stop               Stop all services"
    echo "  clean              Remove everything"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./run-advanced.sh start"
    echo "  ./run-advanced.sh stress 50"
    echo "  ./run-advanced.sh chaos high"
    echo "  ./run-advanced.sh all"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

case "${1:-help}" in
    start)    start_infrastructure ;;
    standard) run_standard_test "$2" ;;
    stress)   run_stress_test "$2" ;;
    spike)    run_spike_test "$2" ;;
    chaos)    run_chaos_test "$2" "$3" ;;
    all)      run_all_tests ;;
    status)   show_status ;;
    stop)     stop_services ;;
    clean)    clean_all ;;
    help|*)   show_help ;;
esac
