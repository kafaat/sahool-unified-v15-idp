#!/bin/bash
# =============================================================================
# SAHOOL Docker Log Analyzer
# Analyzes docker-compose logs using Ollama + DeepSeek Coder
# Supports 20+ concurrent agents for parallel analysis
# =============================================================================

set -e

# Default configuration
LINES=100
PARALLEL=20
ONLY_ERRORS=false
OUTPUT_FILE=""
SERVICES=""
OLLAMA_URL="http://localhost:11434"
MODEL="deepseek-coder:6.7b"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo ""
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${CYAN}================================================================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${MAGENTA}--- $1 ---${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

# Usage
usage() {
    cat << EOF
SAHOOL Docker Log Analyzer - Analyzes logs using Ollama + DeepSeek Coder

Usage: $0 [OPTIONS]

Options:
    -s, --services SERVICES   Comma-separated list of services to analyze
    -l, --lines NUM           Number of log lines per service (default: 100)
    -p, --parallel NUM        Number of concurrent analysis agents (default: 20)
    -e, --only-errors         Only analyze services with errors
    -o, --output FILE         Save analysis report to file
    -h, --help                Show this help message

Examples:
    $0
    $0 -s "postgres,redis,field-ops" -l 200
    $0 -e -p 24 -o analysis.md
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--services)
            SERVICES="$2"
            shift 2
            ;;
        -l|--lines)
            LINES="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -e|--only-errors)
            ONLY_ERRORS=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Check Ollama connection
check_ollama() {
    if curl -s --max-time 5 "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if deepseek-coder model is available
check_model() {
    local models=$(curl -s "$OLLAMA_URL/api/tags" 2>/dev/null | grep -o '"name":"[^"]*"' | grep -c "deepseek-coder" || echo "0")
    if [[ "$models" -gt 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Pull deepseek-coder model
install_model() {
    print_warning "Downloading deepseek-coder:6.7b model..."
    curl -X POST "$OLLAMA_URL/api/pull" \
        -H "Content-Type: application/json" \
        -d '{"name":"deepseek-coder:6.7b"}' \
        --max-time 3600 \
        --progress-bar
    echo ""
    print_success "Model downloaded successfully!"
}

# Get docker-compose services
get_services() {
    docker compose ps --services 2>/dev/null || docker-compose ps --services 2>/dev/null
}

# Get logs for a service
get_logs() {
    local service=$1
    docker compose logs --tail=$LINES "$service" 2>&1 || docker-compose logs --tail=$LINES "$service" 2>&1
}

# Check if logs contain errors
has_errors() {
    local logs="$1"
    local patterns=("error" "Error" "ERROR" "failed" "Failed" "FAILED" "exception" "Exception" \
                    "fatal" "Fatal" "FATAL" "panic" "Panic" "refused" "timeout" "denied")

    for pattern in "${patterns[@]}"; do
        if echo "$logs" | grep -qi "$pattern"; then
            return 0
        fi
    done
    return 1
}

# Analyze logs with Ollama
analyze_logs() {
    local service=$1
    local logs=$2

    local prompt="You are a Docker and DevOps expert analyzing logs from the '$service' container.
Analyze the following logs and provide:
1. ERRORS FOUND: List each error with line reference
2. ROOT CAUSE: Explain why each error occurred
3. FIXES: Specific commands or code changes to fix each issue
4. PRIORITY: Critical/High/Medium/Low for each issue

If no errors are found, state: \"SERVICE HEALTHY - No issues detected\"

Format your response as:
## $service Analysis

### Errors Found
- [Error 1 description]
- [Error 2 description]

### Root Cause Analysis
1. [Cause for Error 1]
2. [Cause for Error 2]

### Suggested Fixes
1. [Fix for Error 1 with command/code]
2. [Fix for Error 2 with command/code]

### Priority
- Error 1: [Priority Level]
- Error 2: [Priority Level]

LOGS:
$logs"

    # Escape special characters for JSON
    local escaped_prompt=$(echo "$prompt" | jq -Rs .)

    local body="{\"model\":\"$MODEL\",\"prompt\":$escaped_prompt,\"stream\":false,\"options\":{\"temperature\":0.3,\"num_predict\":2048}}"

    local response=$(curl -s -X POST "$OLLAMA_URL/api/generate" \
        -H "Content-Type: application/json" \
        -d "$body" \
        --max-time 180 2>/dev/null)

    echo "$response" | jq -r '.response // "Analysis failed"' 2>/dev/null || echo "Analysis failed"
}

# Parallel analysis function
analyze_service() {
    local service=$1
    local logs=$2
    local temp_file=$3

    local analysis=$(analyze_logs "$service" "$logs")
    echo "$analysis" > "$temp_file"
}

# Main execution
print_header "SAHOOL Docker Log Analyzer"
echo -e "${GRAY}Powered by Ollama + DeepSeek Coder${NC}"
echo ""

# Check dependencies
if ! command -v jq &> /dev/null; then
    print_error "ERROR: jq is required but not installed"
    print_warning "Install with: apt-get install jq (Ubuntu) or brew install jq (Mac)"
    exit 1
fi

# Check Ollama
print_warning "Checking Ollama connection..."
if ! check_ollama; then
    print_error "ERROR: Ollama is not running or not accessible at $OLLAMA_URL"
    print_warning "Start Ollama with: docker compose up -d ollama"
    exit 1
fi
print_success "Ollama is running"

# Check model
print_warning "Checking deepseek-coder model..."
if ! check_model; then
    print_warning "Model not found. Installing deepseek-coder:6.7b..."
    install_model
fi
print_success "deepseek-coder model is ready"

# Get services
all_services=$(get_services)
if [[ -z "$all_services" ]]; then
    print_error "ERROR: No docker-compose services found"
    exit 1
fi

service_count=$(echo "$all_services" | wc -l)
print_info "Found $service_count services"

# Filter services if specified
if [[ -n "$SERVICES" ]]; then
    target_services=$(echo "$SERVICES" | tr ',' '\n')
else
    target_services="$all_services"
fi

echo ""
print_section "Collecting Logs"

# Create temp directory for results
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Collect logs and prepare for analysis
declare -A service_logs
declare -A service_has_errors
services_to_analyze=()

while IFS= read -r service; do
    [[ -z "$service" ]] && continue

    printf "  Collecting logs from: %s" "$service"
    logs=$(get_logs "$service")

    if has_errors "$logs"; then
        echo -e " ${RED}[ERRORS FOUND]${NC}"
        service_has_errors[$service]=true
    else
        if [[ "$ONLY_ERRORS" == "true" ]]; then
            echo -e " ${GRAY}[SKIP - No errors]${NC}"
            continue
        fi
        echo -e " ${GREEN}[OK]${NC}"
        service_has_errors[$service]=false
    fi

    # Save logs to temp file
    echo "$logs" > "$TEMP_DIR/${service}.logs"
    services_to_analyze+=("$service")
done <<< "$target_services"

if [[ ${#services_to_analyze[@]} -eq 0 ]]; then
    print_warning "No services to analyze."
    exit 0
fi

print_section "Analyzing Logs with DeepSeek Coder ($PARALLEL concurrent agents)"
echo ""

# Parallel analysis using background jobs
active_jobs=0
job_pids=()

for service in "${services_to_analyze[@]}"; do
    logs=$(cat "$TEMP_DIR/${service}.logs")
    result_file="$TEMP_DIR/${service}.result"

    # Start background job
    (
        analysis=$(analyze_logs "$service" "$logs")
        echo "$analysis" > "$result_file"
    ) &

    job_pids+=($!)
    active_jobs=$((active_jobs + 1))

    printf "  Analyzing: %s" "$service"

    # Throttle parallel jobs
    if [[ $active_jobs -ge $PARALLEL ]]; then
        wait -n 2>/dev/null || true
        active_jobs=$((active_jobs - 1))
    fi

    echo -e " ${YELLOW}[IN PROGRESS]${NC}"
done

# Wait for all jobs to complete
echo ""
print_warning "Waiting for all analyses to complete..."
for pid in "${job_pids[@]}"; do
    wait $pid 2>/dev/null || true
done
print_success "All analyses complete!"

# Generate report
print_header "Analysis Report"

report="# SAHOOL Docker Log Analysis Report
Generated: $(date '+%Y-%m-%d %H:%M:%S')
Services Analyzed: ${#services_to_analyze[@]}

"

# Collect error and healthy services
error_services=()
healthy_services=()

for service in "${services_to_analyze[@]}"; do
    if [[ "${service_has_errors[$service]}" == "true" ]]; then
        error_services+=("$service")
    else
        healthy_services+=("$service")
    fi
done

# Services with errors first
if [[ ${#error_services[@]} -gt 0 ]]; then
    report+="
## Services with Errors (${#error_services[@]})
"
    print_section "Services with Errors"

    for service in "${error_services[@]}"; do
        result_file="$TEMP_DIR/${service}.result"
        if [[ -f "$result_file" ]]; then
            analysis=$(cat "$result_file")
            echo ""
            echo -e "${RED}### $service${NC}"
            echo "$analysis"

            report+="
### $service
$analysis

---
"
        fi
    done
fi

# Healthy services
if [[ ${#healthy_services[@]} -gt 0 ]]; then
    report+="
## Healthy Services (${#healthy_services[@]})
"
    print_section "Healthy Services"

    for service in "${healthy_services[@]}"; do
        result_file="$TEMP_DIR/${service}.result"
        if [[ -f "$result_file" ]]; then
            analysis=$(cat "$result_file")
            echo ""
            echo -e "${GREEN}### $service${NC}"
            echo "$analysis"

            report+="
### $service
$analysis

---
"
        fi
    done
fi

# Summary
summary="
## Summary
- Total Services Analyzed: ${#services_to_analyze[@]}
- Services with Errors: ${#error_services[@]}
- Healthy Services: ${#healthy_services[@]}
- Analysis Engine: Ollama + DeepSeek Coder 6.7B
- Concurrent Agents Used: $PARALLEL
"

report+="$summary"

print_header "Summary"
print_info "Total Services Analyzed: ${#services_to_analyze[@]}"
if [[ ${#error_services[@]} -gt 0 ]]; then
    print_error "Services with Errors: ${#error_services[@]}"
else
    print_success "Services with Errors: 0"
fi
print_success "Healthy Services: ${#healthy_services[@]}"

# Save to file if specified
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$report" > "$OUTPUT_FILE"
    echo ""
    print_warning "Report saved to: $OUTPUT_FILE"
fi

echo ""
print_success "Analysis complete!"
