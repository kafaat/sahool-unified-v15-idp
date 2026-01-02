#!/bin/bash
# SAHOOL API Documentation Generator
# مولد توثيق واجهة برمجة تطبيقات سحول

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}SAHOOL API Documentation Generator${NC}"
echo -e "${BLUE}مولد توثيق واجهة برمجة تطبيقات سحول${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default paths
SERVICES_DIR="$PROJECT_ROOT/apps/services"
OUTPUT_DIR="$PROJECT_ROOT/docs/api"
GENERATOR_SCRIPT="$PROJECT_ROOT/apps/kernel/common/docs/api_docs_generator.py"

# Parse arguments
SKIP_SCAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-scan)
            SKIP_SCAN=true
            shift
            ;;
        --services-dir)
            SERVICES_DIR="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-scan            Skip service scanning (faster for regeneration)"
            echo "  --services-dir DIR     Path to services directory (default: apps/services)"
            echo "  --output-dir DIR       Path to output directory (default: docs/api)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Generate all documentation"
            echo "  $0 --skip-scan         # Regenerate without scanning"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Verify generator script exists
if [ ! -f "$GENERATOR_SCRIPT" ]; then
    echo -e "${YELLOW}Error: Generator script not found at $GENERATOR_SCRIPT${NC}"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Run generator
echo -e "${GREEN}📝 Generating API documentation...${NC}"
echo ""

if [ "$SKIP_SCAN" = true ]; then
    python "$GENERATOR_SCRIPT" --services-dir "$SERVICES_DIR" --output-dir "$OUTPUT_DIR" --skip-scan
else
    python "$GENERATOR_SCRIPT" --services-dir "$SERVICES_DIR" --output-dir "$OUTPUT_DIR"
fi

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}✅ Documentation generated successfully!${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo -e "${BLUE}Generated files:${NC}"
    echo "  📄 $OUTPUT_DIR/README.md"
    echo "  📄 $OUTPUT_DIR/openapi.json"
    echo "  📄 $OUTPUT_DIR/SAHOOL.postman_collection.json"
    echo "  📄 $OUTPUT_DIR/authentication.md"
    echo "  📄 $OUTPUT_DIR/fields.md"
    echo "  📄 $OUTPUT_DIR/sensors.md"
    echo "  📄 $OUTPUT_DIR/weather.md"
    echo "  📄 $OUTPUT_DIR/ai.md"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Review the generated documentation in $OUTPUT_DIR"
    echo "  2. Import openapi.json into Swagger UI or other tools"
    echo "  3. Import SAHOOL.postman_collection.json into Postman"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Documentation generation failed${NC}"
    exit 1
fi
