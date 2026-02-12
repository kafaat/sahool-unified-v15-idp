#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Add ARG PYTHON_VERSION to Dockerfiles
# Adds parameterized Python version to services without it
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$PROJECT_ROOT"

echo -e "${BLUE}Adding ARG PYTHON_VERSION to Python Dockerfiles...${NC}\n"

# Counter
UPDATED=0

# Find Python Dockerfiles without ARG PYTHON_VERSION
for dockerfile in apps/services/*/Dockerfile; do
    if grep -q "FROM python:" "$dockerfile" && ! grep -q "ARG PYTHON_VERSION" "$dockerfile"; then
        service_name=$(basename $(dirname "$dockerfile"))
        echo "Processing: $service_name"
        
        # Create backup
        cp "$dockerfile" "${dockerfile}.bak"
        
        # Add ARG before first FROM python: line
        sed -i '/^FROM python:/ {
            i\ARG PYTHON_VERSION=3.11\n
            s/FROM python:3\.11/FROM python:${PYTHON_VERSION}/
            s/FROM python:3\.12/FROM python:${PYTHON_VERSION}/
        }' "$dockerfile"
        
        # Verify the change was made
        if grep -q "ARG PYTHON_VERSION" "$dockerfile"; then
            echo -e "  ${GREEN}✓${NC} Added ARG PYTHON_VERSION"
            ((UPDATED++))
            rm "${dockerfile}.bak"
        else
            echo "  ✗ Failed to add ARG - restoring backup"
            mv "${dockerfile}.bak" "$dockerfile"
        fi
    fi
done

echo -e "\n${GREEN}Updated $UPDATED Dockerfiles${NC}"
