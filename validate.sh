#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Validation Script - سكريبت التحقق من منصة سهول
# Validates all recommendations have been implemented
# التحقق من تنفيذ جميع التوصيات
# ═══════════════════════════════════════════════════════════════════════════════

# Disable exit-on-error to allow all validation checks to run and display complete results
# We want to see the full validation summary, not stop at the first failure
set +e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "  ${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  SAHOOL Platform Validation - التحقق من منصة سهول${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Port Conflicts Check - فحص تعارضات المنافذ
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[1/7] Port Conflicts - تعارضات المنافذ${NC}"

CONFLICTS=$(grep -A 5 "ports:" docker-compose.yml | grep -E "^\s+- \"?[0-9]+:[0-9]+\"?" | sed 's/.*"\([0-9]*\):.*/\1/' | sed 's/.*- \([0-9]*\):.*/\1/' | sort -n | uniq -d)

if [ -z "$CONFLICTS" ]; then
    check_pass "No port conflicts detected"
else
    check_fail "Port conflicts found: $CONFLICTS"
fi

# Check specific port 8096 fix
if grep -q "8096:8096" docker-compose.yml; then
    SERVICES=$(awk '/^[[:space:]]*[a-z-]+:/ {service=$1} /8096:8096/ {print service}' docker-compose.yml | wc -l)
    if [ "$SERVICES" -gt 1 ]; then
        check_fail "Port 8096 still has conflicts"
    else
        check_pass "Port 8096 conflict resolved"
    fi
else
    check_pass "Port 8096 not in use (or changed)"
fi

# Check virtual-sensors uses port 8119
if grep -q "virtual-sensors" docker-compose.yml; then
    if grep -A 20 "virtual-sensors:" docker-compose.yml | grep -q "8119:8119"; then
        check_pass "Virtual-sensors correctly using port 8119"
    else
        check_warn "Virtual-sensors port configuration not found or different"
    fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Configuration Files - ملفات التكوين
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[2/7] Configuration Files - ملفات التكوين${NC}"

if [ -f ".env.example" ]; then
    check_pass ".env.example exists"
else
    check_fail ".env.example missing"
fi

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml missing"
fi

if [ -f "Makefile" ]; then
    check_pass "Makefile exists"
else
    check_fail "Makefile missing"
fi

if docker compose config --quiet 2>/dev/null; then
    check_pass "Docker Compose configuration is valid"
else
    check_warn "Docker Compose validation requires .env file"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 3. Kong Gateway Configuration - تكوين بوابة Kong
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[3/7] Kong Gateway - بوابة Kong${NC}"

if [ -f "infra/kong/kong.yml" ]; then
    check_pass "infra/kong/kong.yml exists"
    
    # Check virtual-sensors upstream
    if grep -q "virtual-sensors-upstream" infra/kong/kong.yml; then
        if grep -A 3 "virtual-sensors-upstream" infra/kong/kong.yml | grep -q "virtual-sensors:8119"; then
            check_pass "Kong upstream correctly points to virtual-sensors:8119"
        else
            check_warn "Kong upstream for virtual-sensors may need update"
        fi
    fi
else
    check_fail "infra/kong/kong.yml missing"
fi

if [ -f "infrastructure/gateway/kong/kong.yml" ]; then
    check_pass "infrastructure/gateway/kong/kong.yml exists"
    
    # Check virtual-sensors upstream
    if grep -q "virtual-sensors-upstream" infrastructure/gateway/kong/kong.yml; then
        if grep -A 3 "virtual-sensors-upstream" infrastructure/gateway/kong/kong.yml | grep -q "virtual-sensors:8119"; then
            check_pass "Infrastructure Kong upstream correctly configured"
        else
            check_warn "Infrastructure Kong upstream may need update"
        fi
    fi
else
    check_fail "infrastructure/gateway/kong/kong.yml missing"
fi

# Check astronomical calendar routes
if grep -A 5 "astronomical-calendar-route" infra/kong/kong.yml | grep -q "/api/v1/astronomical"; then
    check_pass "Astronomical calendar route includes /api/v1/astronomical"
fi

if grep -A 5 "astronomical-calendar-route" infra/kong/kong.yml | grep -q "/api/v1/calendar"; then
    check_pass "Astronomical calendar route includes /api/v1/calendar"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 4. Service Code Updates - تحديثات كود الخدمات
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[4/7] Service Code - كود الخدمات${NC}"

# Check virtual-sensors service code
if [ -f "apps/services/virtual-sensors/src/main.py" ]; then
    check_pass "Virtual-sensors service code exists"
    
    if grep -q 'os.getenv("PORT"' apps/services/virtual-sensors/src/main.py; then
        check_pass "Virtual-sensors uses PORT environment variable"
    else
        check_warn "Virtual-sensors may not be using PORT env var"
    fi
fi

# Check astronomical calendar service
if [ -f "apps/services/astronomical-calendar/src/main.py" ]; then
    check_pass "Astronomical calendar service exists"
    
    if grep -q "WEATHER_SERVICE_URL" apps/services/astronomical-calendar/src/main.py; then
        check_pass "Astronomical calendar uses WEATHER_SERVICE_URL env var"
    fi
fi

# Check mobile app configurations
if [ -f "apps/mobile/lib/core/http/api_client.dart" ]; then
    check_pass "Mobile API client exists"
    
    if grep -q "EnvConfig" apps/mobile/lib/core/http/api_client.dart; then
        check_pass "Mobile app uses EnvConfig"
    fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 5. Documentation - التوثيق
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[5/7] Documentation - التوثيق${NC}"

if [ -f "MERGE_CONFLICT_RESOLUTION.md" ]; then
    check_pass "MERGE_CONFLICT_RESOLUTION.md exists"
else
    check_fail "MERGE_CONFLICT_RESOLUTION.md missing"
fi

if [ -f "PROJECT_REVIEW_REPORT.md" ]; then
    check_pass "PROJECT_REVIEW_REPORT.md exists"
else
    check_fail "PROJECT_REVIEW_REPORT.md missing"
fi

if [ -f "SETUP_GUIDE.md" ]; then
    check_pass "SETUP_GUIDE.md exists"
else
    check_warn "SETUP_GUIDE.md not found"
fi

if [ -f "README.md" ]; then
    check_pass "README.md exists"
else
    check_warn "README.md missing"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 6. Build System - نظام البناء
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[6/7] Build System - نظام البناء${NC}"

# Check Makefile commands
if grep -q "^test:" Makefile; then
    check_pass "Makefile has test command"
fi

if grep -q "^build:" Makefile; then
    check_pass "Makefile has build command"
fi

if grep -q "^health:" Makefile; then
    check_pass "Makefile has health command"
fi

if grep -q "^dev:" Makefile; then
    check_pass "Makefile has dev command"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 7. Security - الأمان
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[7/7] Security - الأمان${NC}"

# Check .gitignore for .env
if grep -q "^\.env$" .gitignore; then
    check_pass ".env is in .gitignore"
else
    check_fail ".env not in .gitignore - SECURITY RISK!"
fi

# Check for committed .env file
if [ -f ".env" ]; then
    if git ls-files --error-unmatch .env 2>/dev/null; then
        check_fail ".env file is tracked by git - REMOVE IT!"
    else
        check_warn ".env file exists locally (OK if not committed)"
    fi
fi

# Check .env.example doesn't have real credentials
if [ -f ".env.example" ]; then
    if grep -q "change_this" .env.example; then
        check_pass ".env.example has placeholder credentials"
    else
        check_warn ".env.example may contain real credentials"
    fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Summary - الملخص
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Validation Summary - ملخص التحقق${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "  ${GREEN}✓ Passed:${NC}   $PASSED"
echo -e "  ${YELLOW}⚠ Warnings:${NC} $WARNINGS"
echo -e "  ${RED}✗ Failed:${NC}   $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ All Critical Checks Passed!${NC}"
    echo -e "${GREEN}  ✅ تم اجتياز جميع الفحوصات الحرجة!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ Some Checks Failed - Please Review${NC}"
    echo -e "${RED}  ✗ فشلت بعض الفحوصات - يرجى المراجعة${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
