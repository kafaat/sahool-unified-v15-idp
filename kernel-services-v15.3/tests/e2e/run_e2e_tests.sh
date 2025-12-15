#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SAHOOL Kernel Services v15.3 - E2E Test Runner
# تشغيل اختبارات E2E للخدمات
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "🧪 SAHOOL Kernel Services E2E Tests"
echo "════════════════════════════════════"

# Default URLs (can be overridden via environment)
export SATELLITE_URL=${SATELLITE_URL:-"http://localhost:8090"}
export INDICATORS_URL=${INDICATORS_URL:-"http://localhost:8091"}
export WEATHER_URL=${WEATHER_URL:-"http://localhost:8092"}
export FERTILIZER_URL=${FERTILIZER_URL:-"http://localhost:8093"}
export IRRIGATION_URL=${IRRIGATION_URL:-"http://localhost:8094"}

# Check if services are running
check_service() {
    local name=$1
    local url=$2
    if curl -s -o /dev/null -w "%{http_code}" "$url/healthz" | grep -q "200"; then
        echo "✅ $name is running"
        return 0
    else
        echo "❌ $name is not responding at $url"
        return 1
    fi
}

echo ""
echo "📡 Checking service availability..."
echo "─────────────────────────────────────"

SERVICES_OK=true
check_service "Satellite Service" "$SATELLITE_URL" || SERVICES_OK=false
check_service "Indicators Service" "$INDICATORS_URL" || SERVICES_OK=false
check_service "Weather Service" "$WEATHER_URL" || SERVICES_OK=false
check_service "Fertilizer Service" "$FERTILIZER_URL" || SERVICES_OK=false
check_service "Irrigation Service" "$IRRIGATION_URL" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    echo ""
    echo "⚠️  Some services are not running."
    echo "   Start services with: docker-compose up -d"
    echo "   Or run from kernel-services-v15.3/: docker-compose up -d"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Running E2E Tests..."
echo "─────────────────────────────────────"

# Run pytest with coverage
cd "$(dirname "$0")"

# Install dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install pytest pytest-asyncio httpx
fi

# Run tests
python -m pytest \
    -v \
    --tb=short \
    -x \
    --color=yes \
    "$@"

TEST_EXIT_CODE=$?

echo ""
echo "─────────────────────────────────────"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All E2E tests passed!"
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
fi

exit $TEST_EXIT_CODE
