#!/bin/bash
# Script to update all TypeScript/NestJS services with Pino JSON logging

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# TypeScript services to update
SERVICES=(
    "user-service"
    "marketplace-service"
    "crop-growth-model"
    "disaster-assessment"
    "iot-service"
    "lai-estimation"
    "research-core"
    "yield-prediction"
    "yield-prediction-service"
)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Updating TypeScript Services with Pino${NC}"
echo -e "${BLUE}========================================${NC}"
echo

for service in "${SERVICES[@]}"; do
    echo -e "${YELLOW}📦 Processing: $service${NC}"

    if [ ! -d "$service" ]; then
        echo -e "  ⚠️  Directory not found, skipping"
        continue
    fi

    cd "$service"

    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo -e "  ⚠️  No package.json found, skipping"
        cd ..
        continue
    fi

    # Add Pino dependencies if not present
    if ! grep -q "nestjs-pino" package.json; then
        echo -e "  ➕ Adding Pino dependencies..."

        # Use npm to add dependencies (will update package.json)
        # Or manually edit package.json
        cat package.json | \
        jq '.dependencies["nestjs-pino"] = "^4.1.0" | .dependencies["pino-http"] = "^10.3.0" | .dependencies["pino-pretty"] = "^13.0.0"' \
        > package.json.tmp && mv package.json.tmp package.json

        echo -e "  ${GREEN}✓${NC} Dependencies added to package.json"
    else
        echo -e "  ${GREEN}✓${NC} Pino dependencies already present"
    fi

    # Check if app.module.ts exists and needs update
    if [ -f "src/app.module.ts" ]; then
        if ! grep -q "nestjs-pino" "src/app.module.ts"; then
            echo -e "  📝 app.module.ts needs manual update"
            echo -e "     Add: import { LoggerModule } from 'nestjs-pino';"
            echo -e "     Add: import { createPinoLoggerConfig } from '../../shared/logging/pino-logger.config';"
            echo -e "     Add to imports: LoggerModule.forRoot(createPinoLoggerConfig('$service')),"
        else
            echo -e "  ${GREEN}✓${NC} app.module.ts already configured"
        fi
    fi

    # Check if main.ts exists and needs update
    if [ -f "src/main.ts" ]; then
        if ! grep -q "nestjs-pino" "src/main.ts"; then
            echo -e "  📝 main.ts needs manual update"
            echo -e "     Add: import { Logger } from 'nestjs-pino';"
            echo -e "     Update NestFactory.create to: { logger: false, bufferLogs: true }"
            echo -e "     Add: app.useLogger(app.get(Logger));"
        else
            echo -e "  ${GREEN}✓${NC} main.ts already configured"
        fi
    fi

    cd ..
    echo
done

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Update complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo
echo "Next steps:"
echo "1. Review the manual update notes above"
echo "2. For each service, run: cd {service} && npm install"
echo "3. Test each service to ensure logging works"
echo "4. Verify JSON logs are generated in production mode"
echo
echo "For detailed instructions, see:"
echo "  $SCRIPT_DIR/LOGGING_IMPLEMENTATION_REPORT.md"
