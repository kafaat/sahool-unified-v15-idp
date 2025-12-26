#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL API Documentation - Quick Start Script
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  🌾 SAHOOL Platform - API Documentation Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
print_status "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 not found, using python3 -m pip"
    PIP_CMD="python3 -m pip"
else
    PIP_CMD="pip3"
fi

# Install dependencies
echo ""
print_info "Installing Python dependencies..."
$PIP_CMD install -q requests pyyaml
print_status "Dependencies installed"

# Check if Docker is installed (optional)
echo ""
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found. You can still generate specs, but won't be able to run the docs server."
    DOCKER_AVAILABLE=false
else
    print_status "Docker found: $(docker --version)"
    DOCKER_AVAILABLE=true
fi

# Check if Docker Compose is installed (optional)
if [ "$DOCKER_AVAILABLE" = true ]; then
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        print_warning "Docker Compose not found. You can still generate specs."
        DOCKER_COMPOSE_AVAILABLE=false
    else
        print_status "Docker Compose found"
        DOCKER_COMPOSE_AVAILABLE=true
    fi
fi

# Prompt user for action
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "What would you like to do?"
echo "════════════════════════════════════════════════════════════════"
echo "1) Generate OpenAPI specs from running services"
echo "2) Start documentation server (requires specs to be generated)"
echo "3) Do both: Generate specs AND start server"
echo "4) Stop documentation server"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        print_info "Generating OpenAPI specifications..."
        echo ""
        python3 openapi-aggregator.py
        echo ""
        print_status "Done! Specifications saved to:"
        print_info "  - openapi-unified.yaml"
        print_info "  - openapi-unified.json"
        echo ""
        print_info "To view the documentation, run: ./quickstart.sh and select option 2"
        ;;

    2)
        if [ "$DOCKER_COMPOSE_AVAILABLE" = false ]; then
            print_error "Docker Compose is required to start the server."
            exit 1
        fi

        if [ ! -f "openapi-unified.yaml" ]; then
            print_error "openapi-unified.yaml not found!"
            print_info "Please run option 1 first to generate the specs."
            exit 1
        fi

        print_info "Starting documentation server..."
        docker-compose -f docker-compose.docs.yml up -d

        echo ""
        print_status "Documentation server started!"
        print_info "Access the documentation at:"
        echo ""
        echo -e "  ${GREEN}http://localhost:8888${NC}"
        echo ""
        print_info "To stop the server, run: ./quickstart.sh and select option 4"
        ;;

    3)
        # Generate specs
        print_info "Step 1/2: Generating OpenAPI specifications..."
        echo ""
        python3 openapi-aggregator.py
        echo ""
        print_status "Specifications generated!"

        # Start server
        if [ "$DOCKER_COMPOSE_AVAILABLE" = false ]; then
            print_error "Docker Compose is required to start the server."
            print_info "Specs have been generated, but cannot start server."
            exit 1
        fi

        echo ""
        print_info "Step 2/2: Starting documentation server..."
        docker-compose -f docker-compose.docs.yml up -d

        echo ""
        print_status "All done! Documentation is ready!"
        print_info "Access the documentation at:"
        echo ""
        echo -e "  ${GREEN}http://localhost:8888${NC}"
        echo ""
        print_info "To stop the server, run: ./quickstart.sh and select option 4"
        ;;

    4)
        if [ "$DOCKER_COMPOSE_AVAILABLE" = false ]; then
            print_error "Docker Compose is required."
            exit 1
        fi

        print_info "Stopping documentation server..."
        docker-compose -f docker-compose.docs.yml down
        print_status "Server stopped"
        ;;

    5)
        print_info "Exiting..."
        exit 0
        ;;

    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════"
