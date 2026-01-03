#!/bin/bash
# SAHOOL Documentation Generator - نظام التوثيق الآلي
# Generates comprehensive documentation for all apps and services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DOCS_OUTPUT="$ROOT_DIR/docs/generated"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SAHOOL Unified Documentation Generator${NC}"
echo -e "${BLUE}   نظام التوثيق الموحد لمنصة سهول${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Create output directories
mkdir -p "$DOCS_OUTPUT/web"
mkdir -p "$DOCS_OUTPUT/admin"
mkdir -p "$DOCS_OUTPUT/mobile"
mkdir -p "$DOCS_OUTPUT/api"

# Function to generate TypeDoc for TypeScript apps
generate_typedoc() {
    local app_name=$1
    local app_path=$2

    echo -e "\n${YELLOW}📚 Generating TypeDoc for $app_name...${NC}"

    if [ -f "$app_path/typedoc.json" ]; then
        cd "$app_path"
        if command -v npx &> /dev/null; then
            npx typedoc --options typedoc.json 2>/dev/null || {
                echo -e "${YELLOW}  ⚠️  TypeDoc not installed, skipping $app_name${NC}"
                return 0
            }
            echo -e "${GREEN}  ✓ $app_name documentation generated${NC}"
        else
            echo -e "${RED}  ✗ npx not found, skipping TypeDoc${NC}"
        fi
        cd "$ROOT_DIR"
    else
        echo -e "${YELLOW}  ⚠️  No typedoc.json found for $app_name${NC}"
    fi
}

# Function to generate Dart documentation
generate_dartdoc() {
    echo -e "\n${YELLOW}📱 Generating Dart documentation for Mobile App...${NC}"

    if [ -d "$ROOT_DIR/apps/mobile" ]; then
        cd "$ROOT_DIR/apps/mobile"
        if command -v dart &> /dev/null; then
            dart doc . --output="$DOCS_OUTPUT/mobile" 2>/dev/null || {
                echo -e "${YELLOW}  ⚠️  dart doc failed, trying dartdoc...${NC}"
                dartdoc --output="$DOCS_OUTPUT/mobile" 2>/dev/null || {
                    echo -e "${YELLOW}  ⚠️  Dart documentation skipped${NC}"
                    return 0
                }
            }
            echo -e "${GREEN}  ✓ Mobile app documentation generated${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Dart not installed, skipping mobile docs${NC}"
        fi
        cd "$ROOT_DIR"
    fi
}

# Function to aggregate OpenAPI specs
aggregate_openapi() {
    echo -e "\n${YELLOW}🔌 Aggregating OpenAPI specifications...${NC}"

    if [ -f "$ROOT_DIR/docs/api/openapi-aggregator.py" ]; then
        if command -v python3 &> /dev/null; then
            python3 "$ROOT_DIR/docs/api/openapi-aggregator.py" 2>/dev/null || {
                echo -e "${YELLOW}  ⚠️  OpenAPI aggregation skipped (dependencies missing)${NC}"
                return 0
            }
            echo -e "${GREEN}  ✓ OpenAPI specs aggregated${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Python3 not installed, skipping OpenAPI aggregation${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠️  OpenAPI aggregator not found${NC}"
    fi
}

# Function to generate service documentation index
generate_service_index() {
    echo -e "\n${YELLOW}📋 Generating service documentation index...${NC}"

    local index_file="$DOCS_OUTPUT/api/services-index.md"

    cat > "$index_file" << 'EOF'
# SAHOOL Services Documentation Index
# فهرس توثيق خدمات سهول

Generated automatically by SAHOOL Documentation System.

## Core Services - الخدمات الأساسية

| Service | Port | Description |
|---------|------|-------------|
EOF

    # Find all services and add to index
    for service_dir in "$ROOT_DIR/services"/*/ "$ROOT_DIR/services"/*/*/; do
        if [ -d "$service_dir" ]; then
            service_name=$(basename "$service_dir")
            if [ -f "$service_dir/Dockerfile" ]; then
                # Try to extract port from Dockerfile
                port=$(grep -E "EXPOSE\s+[0-9]+" "$service_dir/Dockerfile" 2>/dev/null | head -1 | grep -oE "[0-9]+" || echo "N/A")
                # Try to get description from README
                desc=""
                if [ -f "$service_dir/README.md" ]; then
                    desc=$(head -3 "$service_dir/README.md" | tail -1 | sed 's/#//g' | xargs)
                fi
                echo "| $service_name | $port | $desc |" >> "$index_file"
            fi
        fi
    done

    echo -e "${GREEN}  ✓ Service index generated${NC}"
}

# Function to generate documentation summary
generate_summary() {
    echo -e "\n${YELLOW}📊 Generating documentation summary...${NC}"

    local summary_file="$DOCS_OUTPUT/README.md"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cat > "$summary_file" << EOF
# SAHOOL Platform Documentation
# توثيق منصة سهول الموحدة

**Generated:** $timestamp

## Quick Links - روابط سريعة

- [Web App Documentation](./web/index.html)
- [Admin Dashboard Documentation](./admin/index.html)
- [Mobile App Documentation](./mobile/index.html)
- [API Services Index](./api/services-index.md)

## Documentation Structure

\`\`\`
docs/generated/
├── web/           # Web app TypeDoc documentation
├── admin/         # Admin dashboard TypeDoc documentation
├── mobile/        # Mobile app Dart documentation
└── api/           # Aggregated API documentation
    └── services-index.md
\`\`\`

## Generating Documentation

Run from the project root:

\`\`\`bash
# Generate all documentation
npm run docs

# Or run the script directly
./scripts/generate-docs.sh
\`\`\`

## Requirements

- Node.js 18+ with npx
- TypeDoc (installed via npm)
- Dart SDK (for mobile docs)
- Python 3 (for OpenAPI aggregation)

---

*SAHOOL Agricultural Platform - منصة سهول الزراعية*
EOF

    echo -e "${GREEN}  ✓ Documentation summary generated${NC}"
}

# Main execution
echo -e "\n${BLUE}Starting documentation generation...${NC}"

# Generate TypeDoc for web and admin apps
generate_typedoc "Web App" "$ROOT_DIR/apps/web"
generate_typedoc "Admin Dashboard" "$ROOT_DIR/apps/admin"

# Generate Dart documentation for mobile
generate_dartdoc

# Aggregate OpenAPI specs
aggregate_openapi

# Generate service index
generate_service_index

# Generate summary
generate_summary

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Documentation generation complete!${NC}"
echo -e "${BLUE}  Output: $DOCS_OUTPUT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
