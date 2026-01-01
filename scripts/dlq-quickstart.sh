#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAHOOL DLQ Quick Start Script
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Quick start script for Dead Letter Queue management.
#
# Usage:
#   ./scripts/dlq-quickstart.sh [command]
#
# Commands:
#   start    - Start DLQ management service
#   stop     - Stop DLQ management service
#   stats    - View DLQ statistics
#   messages - List DLQ messages
#   replay   - Replay failed messages
#   help     - Show this help
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
DLQ_SERVICE_URL="${DLQ_SERVICE_URL:-http://localhost:8090}"
DOCKER_COMPOSE_FILE="docker/docker-compose.dlq.yml"

# ──────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  $1"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# ──────────────────────────────────────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────────────────────────────────────

cmd_start() {
    print_header "Starting DLQ Management Service"

    # Check if docker-compose file exists
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "Docker compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    # Start services
    echo "Starting DLQ services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    # Wait for service to be ready
    echo "Waiting for service to be ready..."
    sleep 5

    # Check health
    if curl -sf "${DLQ_SERVICE_URL}/health" > /dev/null; then
        print_success "DLQ Management Service started successfully"
        echo ""
        echo "API Documentation: ${DLQ_SERVICE_URL}/docs"
        echo "Statistics:        ${DLQ_SERVICE_URL}/dlq/stats"
        echo "Messages:          ${DLQ_SERVICE_URL}/dlq/messages"
    else
        print_warning "Service started but health check failed"
        echo "Check logs with: docker-compose -f $DOCKER_COMPOSE_FILE logs dlq-service"
    fi
}

cmd_stop() {
    print_header "Stopping DLQ Management Service"

    docker-compose -f "$DOCKER_COMPOSE_FILE" down

    print_success "DLQ services stopped"
}

cmd_stats() {
    print_header "DLQ Statistics"

    response=$(curl -s "${DLQ_SERVICE_URL}/dlq/stats")

    if [ $? -eq 0 ]; then
        echo "$response" | python3 -m json.tool
    else
        print_error "Failed to fetch statistics"
        print_warning "Make sure the DLQ service is running: ./scripts/dlq-quickstart.sh start"
    fi
}

cmd_messages() {
    print_header "DLQ Messages"

    page="${1:-1}"
    page_size="${2:-10}"

    echo "Fetching page $page (size: $page_size)..."
    echo ""

    response=$(curl -s "${DLQ_SERVICE_URL}/dlq/messages?page=${page}&page_size=${page_size}")

    if [ $? -eq 0 ]; then
        echo "$response" | python3 -m json.tool
    else
        print_error "Failed to fetch messages"
    fi
}

cmd_replay() {
    print_header "Replay DLQ Messages"

    if [ -z "$1" ]; then
        print_error "Usage: ./scripts/dlq-quickstart.sh replay <seq1> [seq2] [seq3] ..."
        exit 1
    fi

    # Build message_seqs array
    seqs="["
    for seq in "$@"; do
        seqs="${seqs}${seq},"
    done
    seqs="${seqs%,}]"  # Remove trailing comma and close array

    payload="{\"message_seqs\": ${seqs}, \"delete_after_replay\": true}"

    echo "Replaying messages: $seqs"
    echo ""

    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "${DLQ_SERVICE_URL}/dlq/replay/bulk")

    if [ $? -eq 0 ]; then
        echo "$response" | python3 -m json.tool

        # Extract success count
        success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success_count', 0))")
        failure=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('failure_count', 0))")

        echo ""
        if [ "$failure" -eq 0 ]; then
            print_success "Successfully replayed $success message(s)"
        else
            print_warning "Replayed $success, failed $failure"
        fi
    else
        print_error "Failed to replay messages"
    fi
}

cmd_help() {
    cat << EOF

SAHOOL DLQ Quick Start Script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USAGE:
    ./scripts/dlq-quickstart.sh [command] [options]

COMMANDS:
    start                   Start DLQ management service
    stop                    Stop DLQ management service
    stats                   View DLQ statistics
    messages [page] [size]  List DLQ messages (default: page 1, size 10)
    replay <seq> [seq...]   Replay message(s) by sequence number
    help                    Show this help

EXAMPLES:
    # Start the service
    ./scripts/dlq-quickstart.sh start

    # View statistics
    ./scripts/dlq-quickstart.sh stats

    # List first page of messages
    ./scripts/dlq-quickstart.sh messages

    # List page 2 with 20 messages
    ./scripts/dlq-quickstart.sh messages 2 20

    # Replay a single message
    ./scripts/dlq-quickstart.sh replay 123

    # Replay multiple messages
    ./scripts/dlq-quickstart.sh replay 123 124 125

    # Stop the service
    ./scripts/dlq-quickstart.sh stop

CONFIGURATION:
    DLQ_SERVICE_URL    URL of DLQ service (default: http://localhost:8090)

    Example:
        DLQ_SERVICE_URL=http://production:8090 ./scripts/dlq-quickstart.sh stats

DOCUMENTATION:
    See shared/events/DLQ_README.md for complete documentation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
}

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

command="${1:-help}"

case "$command" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    stats)
        cmd_stats
        ;;
    messages)
        shift
        cmd_messages "$@"
        ;;
    replay)
        shift
        cmd_replay "$@"
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $command"
        echo "Run './scripts/dlq-quickstart.sh help' for usage"
        exit 1
        ;;
esac
