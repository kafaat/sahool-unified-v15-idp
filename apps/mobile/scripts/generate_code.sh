#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SAHOOL Mobile App - Code Generation Script
# سكريبت توليد الكود لتطبيق سهول الموبايل
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        SAHOOL Mobile App - Code Generation                      ║"
echo "║        توليد الكود لتطبيق سهول الموبايل                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter is not installed${NC}"
    echo "Please install Flutter from https://flutter.dev"
    exit 1
fi

# Navigate to mobile app directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo ""
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
flutter pub get

echo ""
echo -e "${YELLOW}🔧 Generating code with build_runner...${NC}"
echo "This may take a few minutes..."

# Run build_runner
flutter pub run build_runner build --delete-conflicting-outputs

echo ""
echo -e "${YELLOW}🌐 Generating localization files...${NC}"
flutter gen-l10n

echo ""
echo -e "${GREEN}✅ Code generation complete!${NC}"
echo ""
echo "Generated files:"
echo "  - *.freezed.dart (Freezed models)"
echo "  - *.g.dart (JSON serialization)"
echo "  - lib/generated/l10n/ (Localization)"
echo ""
echo "You can now run the app with:"
echo "  flutter run"
