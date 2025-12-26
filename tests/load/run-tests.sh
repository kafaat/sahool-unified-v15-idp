#!/bin/bash
# SAHOOL Platform - Load Testing Script
# Run k6 load tests with various scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
FIELD_SERVICE_URL="${FIELD_SERVICE_URL:-http://localhost:8080}"
WEATHER_URL="${WEATHER_URL:-http://localhost:8092}"
BILLING_URL="${BILLING_URL:-http://localhost:8089}"
SATELLITE_URL="${SATELLITE_URL:-http://localhost:8090}"
EQUIPMENT_URL="${EQUIPMENT_URL:-http://localhost:8101}"
TASK_URL="${TASK_URL:-http://localhost:8103}"
CROP_HEALTH_URL="${CROP_HEALTH_URL:-http://localhost:8095}"
ENVIRONMENT="${ENVIRONMENT:-local}"
RESULTS_DIR="${RESULTS_DIR:-./results}"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

# Function to check if k6 is installed
check_k6() {
    if ! command -v k6 &> /dev/null; then
        print_error "k6 is not installed!"
        echo ""
        echo "Install k6:"
        echo "  macOS: brew install k6"
        echo "  Linux: sudo gpg -k && sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 && echo 'deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main' | sudo tee /etc/apt/sources.list.d/k6.list && sudo apt-get update && sudo apt-get install k6"
        echo "  Docker: Use docker-compose.load.yml"
        echo ""
        exit 1
    fi
}

# Function to check if services are running
check_services() {
    print_info "Checking if services are reachable..."

    services=(
        "$FIELD_SERVICE_URL/healthz:Field Service"
        "$WEATHER_URL/healthz:Weather Service"
        "$BILLING_URL/healthz:Billing Service"
    )

    all_healthy=true

    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        if curl -s -f -m 3 "$url" > /dev/null 2>&1; then
            print_success "$name is healthy"
        else
            print_warning "$name is not reachable at $url"
            all_healthy=false
        fi
    done

    if [ "$all_healthy" = false ]; then
        print_warning "Some services are not healthy. Tests may fail."
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to run a specific test
run_test() {
    local test_type=$1
    local test_file=$2
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local results_file="$RESULTS_DIR/${test_type}_${timestamp}"

    print_info "Starting ${test_type} test..."
    echo ""

    # Run k6 with environment variables and save results
    k6 run \
        --out json="${results_file}.json" \
        --summary-export="${results_file}_summary.json" \
        -e BASE_URL="$BASE_URL" \
        -e FIELD_SERVICE_URL="$FIELD_SERVICE_URL" \
        -e WEATHER_URL="$WEATHER_URL" \
        -e BILLING_URL="$BILLING_URL" \
        -e SATELLITE_URL="$SATELLITE_URL" \
        -e EQUIPMENT_URL="$EQUIPMENT_URL" \
        -e TASK_URL="$TASK_URL" \
        -e CROP_HEALTH_URL="$CROP_HEALTH_URL" \
        -e ENVIRONMENT="$ENVIRONMENT" \
        "$test_file"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_success "${test_type} test completed successfully!"
        print_info "Results saved to: ${results_file}.json"
    else
        print_error "${test_type} test failed with exit code $exit_code"
        return $exit_code
    fi

    echo ""

    # Generate HTML report if k6-reporter is available
    if command -v k6-reporter &> /dev/null; then
        print_info "Generating HTML report..."
        k6-reporter "${results_file}.json" --output "${results_file}.html"
        print_success "HTML report: ${results_file}.html"
    fi

    return 0
}

# Function to upload results to InfluxDB (optional)
upload_to_influxdb() {
    if [ -n "$INFLUXDB_URL" ]; then
        print_info "InfluxDB integration detected. Results will be sent to: $INFLUXDB_URL"
        # k6 will automatically send metrics if --out influxdb is specified
        return 0
    fi
    return 1
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "Test Types:"
    echo "  smoke      - Quick smoke test (1 VU, 1 minute)"
    echo "  load       - Standard load test (50 VUs, 10 minutes)"
    echo "  stress     - Stress test (ramp to 200 VUs, 15 minutes)"
    echo "  spike      - Spike test (sudden bursts, 8 minutes)"
    echo "  soak       - Soak test (20 VUs, 2 hours)"
    echo "  all        - Run all tests sequentially"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -c, --check-only        Only check services, don't run tests"
    echo "  -s, --skip-health       Skip health check"
    echo "  --base-url URL          Base API URL (default: http://localhost:8000)"
    echo "  --field-url URL         Field service URL (default: http://localhost:8080)"
    echo "  --weather-url URL       Weather service URL (default: http://localhost:8092)"
    echo "  --billing-url URL       Billing service URL (default: http://localhost:8089)"
    echo "  --influxdb-url URL      InfluxDB URL for metrics storage"
    echo "  --environment ENV       Environment name (default: local)"
    echo ""
    echo "Environment Variables:"
    echo "  BASE_URL               Base API URL"
    echo "  FIELD_SERVICE_URL      Field service URL"
    echo "  WEATHER_URL            Weather service URL"
    echo "  BILLING_URL            Billing service URL"
    echo "  SATELLITE_URL          Satellite service URL"
    echo "  EQUIPMENT_URL          Equipment service URL"
    echo "  TASK_URL               Task service URL"
    echo "  CROP_HEALTH_URL        Crop health AI service URL"
    echo "  INFLUXDB_URL           InfluxDB URL"
    echo "  RESULTS_DIR            Results directory (default: ./results)"
    echo ""
    echo "Examples:"
    echo "  $0 smoke                          # Run smoke test"
    echo "  $0 load --environment staging     # Run load test on staging"
    echo "  $0 all                            # Run all tests"
    echo "  BASE_URL=https://api.sahool.io $0 load  # Custom URL"
}

# Parse command line arguments
SKIP_HEALTH=false
CHECK_ONLY=false
TEST_TYPE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -c|--check-only)
            CHECK_ONLY=true
            shift
            ;;
        -s|--skip-health)
            SKIP_HEALTH=true
            shift
            ;;
        --base-url)
            BASE_URL="$2"
            shift 2
            ;;
        --field-url)
            FIELD_SERVICE_URL="$2"
            shift 2
            ;;
        --weather-url)
            WEATHER_URL="$2"
            shift 2
            ;;
        --billing-url)
            BILLING_URL="$2"
            shift 2
            ;;
        --influxdb-url)
            INFLUXDB_URL="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        smoke|load|stress|spike|soak|all)
            TEST_TYPE="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         SAHOOL Platform - Load Testing Suite                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check k6 installation
check_k6

# Display configuration
print_info "Configuration:"
echo "  Environment:     $ENVIRONMENT"
echo "  Base URL:        $BASE_URL"
echo "  Field Service:   $FIELD_SERVICE_URL"
echo "  Weather Service: $WEATHER_URL"
echo "  Billing Service: $BILLING_URL"
echo "  Results Dir:     $RESULTS_DIR"
echo ""

# Check services health
if [ "$SKIP_HEALTH" = false ]; then
    check_services
    echo ""
fi

if [ "$CHECK_ONLY" = true ]; then
    print_success "Health check complete. Exiting."
    exit 0
fi

# Validate test type
if [ -z "$TEST_TYPE" ]; then
    print_error "No test type specified!"
    show_usage
    exit 1
fi

# Run tests
cd "$(dirname "$0")"

case $TEST_TYPE in
    smoke)
        run_test "smoke" "scenarios/smoke.js"
        ;;
    load)
        run_test "load" "scenarios/load.js"
        ;;
    stress)
        print_warning "Stress test will push the system to its limits!"
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_test "stress" "scenarios/stress.js"
        fi
        ;;
    spike)
        run_test "spike" "scenarios/spike.js"
        ;;
    soak)
        print_warning "Soak test will run for 2 hours!"
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_test "soak" "scenarios/soak.js"
        fi
        ;;
    all)
        print_info "Running all load tests sequentially..."
        echo ""

        run_test "smoke" "scenarios/smoke.js" || exit 1
        sleep 10

        run_test "load" "scenarios/load.js" || exit 1
        sleep 10

        print_warning "Next: Stress test. This will push the system hard."
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_test "stress" "scenarios/stress.js" || exit 1
            sleep 10
        fi

        run_test "spike" "scenarios/spike.js" || exit 1
        sleep 10

        print_warning "Final test: Soak test (2 hours)."
        read -p "Run soak test? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_test "soak" "scenarios/soak.js" || exit 1
        fi

        print_success "All tests completed!"
        ;;
    *)
        print_error "Unknown test type: $TEST_TYPE"
        show_usage
        exit 1
        ;;
esac

echo ""
print_success "Load testing complete!"
print_info "Results are saved in: $RESULTS_DIR"
echo ""
