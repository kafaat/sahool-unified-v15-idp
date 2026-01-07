#!/bin/bash

# SAHOOL Marketplace Service - Test Verification Script
# This script helps verify that tests are properly set up

echo "=========================================="
echo "SAHOOL Marketplace Service Test Verification"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run from marketplace-service directory"
    exit 1
fi

echo "✅ Directory check passed"
echo ""

# Check if test files exist
echo "Checking test files..."
TEST_FILES=(
    "src/__tests__/marketplace.controller.spec.ts"
    "src/__tests__/product.service.spec.ts"
    "src/__tests__/order.service.spec.ts"
    "src/__tests__/payment.service.spec.ts"
)

for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "✅ $file ($lines lines)"
    else
        echo "❌ Missing: $file"
    fi
done
echo ""

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found"
    echo "   Run: npm install"
    echo ""

    read -p "Install dependencies now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing dependencies..."
        npm install
        echo ""
    fi
else
    echo "✅ node_modules exists"
    echo ""
fi

# Check if Jest is available
if command -v npx &> /dev/null; then
    if npx jest --version &> /dev/null; then
        JEST_VERSION=$(npx jest --version 2>/dev/null)
        echo "✅ Jest is available (version: $JEST_VERSION)"
    else
        echo "⚠️  Jest not found. Install dependencies first."
    fi
else
    echo "⚠️  npx not found. Install Node.js first."
fi
echo ""

# Summary
echo "=========================================="
echo "Test Suite Summary"
echo "=========================================="
echo "Total test files: 4"
echo "Total test lines: 3,135+"
echo ""
echo "Test files created:"
echo "  1. marketplace.controller.spec.ts (664 lines) - API endpoints"
echo "  2. product.service.spec.ts (704 lines) - Product CRUD"
echo "  3. order.service.spec.ts (778 lines) - Order management"
echo "  4. payment.service.spec.ts (989 lines) - Payment processing"
echo ""

# Check if tests can be listed
if [ -d "node_modules" ]; then
    echo "=========================================="
    echo "Available Test Commands"
    echo "=========================================="
    echo "npm test                    # Run all tests"
    echo "npm test:watch              # Run tests in watch mode"
    echo "npm test:cov                # Run tests with coverage"
    echo ""
    echo "npm test -- marketplace.controller.spec.ts  # Run specific test"
    echo "npm test -- product.service.spec.ts"
    echo "npm test -- order.service.spec.ts"
    echo "npm test -- payment.service.spec.ts"
    echo ""

    read -p "Run tests now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Running tests..."
        npm test
    fi
else
    echo "=========================================="
    echo "Next Steps"
    echo "=========================================="
    echo "1. Install dependencies: npm install"
    echo "2. Run tests: npm test"
    echo "3. View coverage: npm test:cov"
    echo ""
fi

echo "=========================================="
echo "Documentation"
echo "=========================================="
echo "📖 Test README: src/__tests__/README.md"
echo "📖 Testing Guide: TESTING.md"
echo ""
echo "For more information, see the documentation files."
echo ""
