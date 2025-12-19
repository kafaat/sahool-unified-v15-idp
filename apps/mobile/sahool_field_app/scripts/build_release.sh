#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL App - Release Build Script
# سكريبت بناء النسخة الإنتاجية لتطبيق سهول
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}        SAHOOL App - Release Build Script                      ${NC}"
echo -e "${GREEN}        سهول - بناء النسخة الإنتاجية                            ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Navigate to app directory
cd "$(dirname "$0")/.."
APP_DIR=$(pwd)

echo -e "${BLUE}📁 Working directory: $APP_DIR${NC}"
echo ""

# Step 1: Check for icons
echo -e "${YELLOW}[1/6] Checking app icons...${NC}"
if [ ! -f "assets/icon/app_icon.png" ]; then
    echo -e "${YELLOW}⚠️  Icons not found. Generating placeholder icons...${NC}"
    python3 scripts/generate_icons.py || {
        echo -e "${RED}❌ Failed to generate icons. Install Pillow: pip install Pillow${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✅ Icons ready${NC}"
echo ""

# Step 2: Clean previous builds
echo -e "${YELLOW}[2/6] Cleaning previous builds...${NC}"
flutter clean
echo -e "${GREEN}✅ Clean complete${NC}"
echo ""

# Step 3: Get dependencies
echo -e "${YELLOW}[3/6] Getting dependencies...${NC}"
flutter pub get
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Generate launcher icons
echo -e "${YELLOW}[4/6] Generating launcher icons...${NC}"
dart run flutter_launcher_icons || {
    echo -e "${RED}⚠️  Launcher icons generation failed (non-critical)${NC}"
}
echo ""

# Step 5: Generate splash screen
echo -e "${YELLOW}[5/6] Generating splash screen...${NC}"
dart run flutter_native_splash:create || {
    echo -e "${RED}⚠️  Splash screen generation failed (non-critical)${NC}"
}
echo ""

# Step 6: Build release APK
echo -e "${YELLOW}[6/6] Building release APK...${NC}"
echo -e "${BLUE}This may take several minutes...${NC}"
flutter build apk --release --obfuscate --split-debug-info=./build/app/outputs/symbols

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ BUILD SUCCESSFUL!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Show APK location
APK_PATH="build/app/outputs/flutter-apk/app-release.apk"
if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo -e "${GREEN}📦 APK Location: ${BLUE}$APP_DIR/$APK_PATH${NC}"
    echo -e "${GREEN}📊 APK Size: ${BLUE}$APK_SIZE${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  1. Transfer APK to your phone"
    echo -e "  2. Make sure Docker services are running"
    echo -e "  3. Connect phone to same WiFi as computer"
    echo -e "  4. Install and test the app"
else
    echo -e "${RED}❌ APK not found at expected location${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
