#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL IDP - Load Testing Simulation Runner
# سكريبت تشغيل محاكاة اختبار الحمل لمنصة سهول
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./run-simulation.sh [command]
#
# Commands:
#   start       - Start simulation infrastructure
#   stop        - Stop simulation infrastructure
#   test        - Run k6 agent simulation
#   status      - Check status of all services
#   logs        - View logs of all services
#   clean       - Clean up everything including volumes
#   help        - Show this help message
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose-sim.yml"

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  SAHOOL IDP - Load Testing Simulation"
    echo "  محاكاة اختبار الحمل لمنصة سهول"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Print status message
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Create results directory
create_results_dir() {
    mkdir -p "$SCRIPT_DIR/results"
    mkdir -p "$SCRIPT_DIR/init-scripts"
}

# Start simulation infrastructure
start_infrastructure() {
    print_banner
    info "Starting simulation infrastructure..."

    check_docker
    create_results_dir

    # Start all services except k6
    docker-compose -f "$COMPOSE_FILE" up -d \
        sahool-db \
        sahool-pgbouncer \
        sahool-redis \
        sahool-influxdb \
        sahool-grafana

    info "Waiting for databases to be ready..."
    sleep 10

    # Check if services are healthy
    check_health

    success "Infrastructure started successfully!"
    echo ""
    info "Access points:"
    echo "  - Grafana: http://localhost:3031 (admin/admin)"
    echo "  - InfluxDB: http://localhost:8087 (admin/adminpassword123)"
    echo "  - PostgreSQL: localhost:5433"
    echo "  - Redis: localhost:6380"
    echo ""
    info "To start application instances, run: ./run-simulation.sh start-apps"
}

# Start application instances
start_apps() {
    print_banner
    info "Starting 3 application instances..."

    check_docker

    # This would start the actual application instances
    # For now, we'll just show a message
    warning "Application instances require the actual SAHOOL service images."
    info "In production, run:"
    echo "  docker-compose -f $COMPOSE_FILE up -d sahool-app-1 sahool-app-2 sahool-app-3 sahool-nginx"
}

# Run k6 agent simulation
run_test() {
    print_banner
    info "Running k6 agent simulation with 10 virtual agents..."

    check_docker
    create_results_dir

    # Set agent count (default 10)
    AGENT_COUNT=${1:-10}

    info "Agent count: $AGENT_COUNT"
    info "Duration: 3 minutes"
    echo ""

    # Run k6 with the simulation script
    docker-compose -f "$COMPOSE_FILE" --profile testing run --rm \
        -e AGENT_COUNT=$AGENT_COUNT \
        sahool-k6

    success "Simulation completed!"
    info "Check results in: $SCRIPT_DIR/results/"
    info "View Grafana dashboard: http://localhost:3031"
}

# Run quick test (without full infrastructure)
run_quick_test() {
    print_banner
    info "Running quick k6 test (standalone mode)..."

    check_docker
    create_results_dir

    BASE_URL=${1:-http://localhost:8080}

    docker run --rm \
        --network host \
        -v "$SCRIPT_DIR/scripts:/scripts:ro" \
        -v "$SCRIPT_DIR/results:/results" \
        -e BASE_URL="$BASE_URL" \
        -e AGENT_COUNT=10 \
        -e ENVIRONMENT=quick-test \
        grafana/k6:0.48.0 run /scripts/agent-simulation.js

    success "Quick test completed!"
    info "Check results in: $SCRIPT_DIR/results/"
}

# Check health of services
check_health() {
    info "Checking service health..."

    # Check PostgreSQL
    if docker exec sahool_db_sim pg_isready -U sahool_admin > /dev/null 2>&1; then
        echo -e "  PostgreSQL: ${GREEN}HEALTHY${NC}"
    else
        echo -e "  PostgreSQL: ${RED}UNHEALTHY${NC}"
    fi

    # Check Redis
    if docker exec sahool_redis_sim redis-cli -a sim_redis_pass_123 ping > /dev/null 2>&1; then
        echo -e "  Redis: ${GREEN}HEALTHY${NC}"
    else
        echo -e "  Redis: ${RED}UNHEALTHY${NC}"
    fi

    # Check InfluxDB
    if docker exec sahool_influxdb_sim influx ping > /dev/null 2>&1; then
        echo -e "  InfluxDB: ${GREEN}HEALTHY${NC}"
    else
        echo -e "  InfluxDB: ${RED}UNHEALTHY${NC}"
    fi

    # Check Grafana
    if curl -s http://localhost:3031/api/health > /dev/null 2>&1; then
        echo -e "  Grafana: ${GREEN}HEALTHY${NC}"
    else
        echo -e "  Grafana: ${RED}UNHEALTHY${NC}"
    fi
}

# Show status of all services
show_status() {
    print_banner
    info "Service status:"
    docker-compose -f "$COMPOSE_FILE" ps

    echo ""
    check_health
}

# View logs
show_logs() {
    SERVICE=${1:-""}

    if [ -z "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" logs --tail=100 -f
    else
        docker-compose -f "$COMPOSE_FILE" logs --tail=100 -f "$SERVICE"
    fi
}

# Stop all services
stop_services() {
    print_banner
    info "Stopping simulation services..."

    docker-compose -f "$COMPOSE_FILE" down

    success "All services stopped."
}

# Clean up everything
clean_all() {
    print_banner
    warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? (y/N): " confirm

    if [[ $confirm =~ ^[Yy]$ ]]; then
        info "Cleaning up..."
        docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
        rm -rf "$SCRIPT_DIR/results/*"
        success "Cleanup complete."
    else
        info "Cleanup cancelled."
    fi
}

# Show help
show_help() {
    print_banner
    echo "Usage: ./run-simulation.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start           Start simulation infrastructure (DB, Redis, monitoring)"
    echo "  start-apps      Start application instances (requires built images)"
    echo "  test [agents]   Run k6 agent simulation (default: 10 agents)"
    echo "  quick [url]     Run quick standalone test (default: http://localhost:8080)"
    echo "  status          Check status of all services"
    echo "  health          Check health of services"
    echo "  logs [service]  View logs (optional: specific service name)"
    echo "  stop            Stop all services"
    echo "  clean           Clean up everything including volumes"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run-simulation.sh start           # Start infrastructure"
    echo "  ./run-simulation.sh test 20         # Run with 20 agents"
    echo "  ./run-simulation.sh quick           # Quick standalone test"
    echo "  ./run-simulation.sh logs sahool-db  # View DB logs"
    echo ""
}

# Main script logic
case "${1:-help}" in
    start)
        start_infrastructure
        ;;
    start-apps)
        start_apps
        ;;
    test)
        run_test "$2"
        ;;
    quick)
        run_quick_test "$2"
        ;;
    status)
        show_status
        ;;
    health)
        check_health
        ;;
    logs)
        show_logs "$2"
        ;;
    stop)
        stop_services
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
