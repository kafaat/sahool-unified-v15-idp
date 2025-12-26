#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Monitoring Stack Startup Script
# سكريبت بدء تشغيل مجموعة المراقبة
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         SAHOOL Platform - Monitoring Stack Setup              ║${NC}"
echo -e "${BLUE}║         مجموعة المراقبة لمنصة سهول الزراعية                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    echo -e "${YELLOW}⚠️  ملف .env غير موجود. جاري الإنشاء من .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ Please edit .env file with your actual credentials before continuing!${NC}"
    echo -e "${RED}❌ الرجاء تحرير ملف .env بمعلومات الاعتماد الفعلية قبل المتابعة!${NC}"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
echo -e "${BLUE}🔍 Checking required environment variables...${NC}"
echo -e "${BLUE}🔍 فحص متغيرات البيئة المطلوبة...${NC}"

REQUIRED_VARS=("GRAFANA_ADMIN_PASSWORD" "POSTGRES_PASSWORD" "REDIS_PASSWORD")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" == "change_me_secure_password" ] || [[ "${!var}" == *"your_"* ]]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing or invalid required variables:${NC}"
    echo -e "${RED}❌ متغيرات مطلوبة مفقودة أو غير صالحة:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "${RED}   - $var${NC}"
    done
    echo ""
    echo -e "${YELLOW}Please update .env file with actual values.${NC}"
    echo -e "${YELLOW}الرجاء تحديث ملف .env بالقيم الفعلية.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All required variables are set${NC}"
echo -e "${GREEN}✅ جميع المتغيرات المطلوبة معينة${NC}"
echo ""

# Check if SAHOOL network exists
echo -e "${BLUE}🔍 Checking for SAHOOL network...${NC}"
echo -e "${BLUE}🔍 فحص شبكة سهول...${NC}"

if ! docker network ls | grep -q "sahool-network"; then
    echo -e "${YELLOW}⚠️  SAHOOL network not found. Creating...${NC}"
    echo -e "${YELLOW}⚠️  شبكة سهول غير موجودة. جاري الإنشاء...${NC}"
    docker network create sahool-network
    echo -e "${GREEN}✅ Network created${NC}"
else
    echo -e "${GREEN}✅ Network exists${NC}"
fi
echo ""

# Pull latest images
echo -e "${BLUE}📥 Pulling latest Docker images...${NC}"
echo -e "${BLUE}📥 جاري تحميل أحدث صور Docker...${NC}"
docker-compose -f docker-compose.monitoring.yml pull
echo ""

# Start monitoring stack
echo -e "${BLUE}🚀 Starting monitoring stack...${NC}"
echo -e "${BLUE}🚀 جاري تشغيل مجموعة المراقبة...${NC}"
docker-compose -f docker-compose.monitoring.yml up -d
echo ""

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
echo -e "${BLUE}⏳ انتظار الخدمات لتصبح جاهزة...${NC}"
sleep 10

# Check service status
echo -e "${BLUE}🔍 Checking service status...${NC}"
echo -e "${BLUE}🔍 فحص حالة الخدمات...${NC}"
docker-compose -f docker-compose.monitoring.yml ps
echo ""

# Display access information
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Monitoring Stack Started!                     ║${NC}"
echo -e "${GREEN}║                  تم تشغيل مجموعة المراقبة!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Access URLs:${NC}"
echo -e "${BLUE}📊 روابط الوصول:${NC}"
echo ""
echo -e "  ${GREEN}Prometheus:${NC}    http://localhost:9090"
echo -e "  ${GREEN}Grafana:${NC}       http://localhost:3002"
echo -e "  ${GREEN}Alertmanager:${NC}  http://localhost:9093"
echo ""
echo -e "${BLUE}🔐 Grafana Credentials:${NC}"
echo -e "  ${GREEN}Username:${NC} ${GRAFANA_ADMIN_USER:-admin}"
echo -e "  ${GREEN}Password:${NC} (see .env file)"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "${YELLOW}📝 الخطوات التالية:${NC}"
echo -e "  1. Open Grafana: http://localhost:3002"
echo -e "  2. Login with your credentials"
echo -e "  3. Navigate to Dashboards → SAHOOL Platform Overview"
echo -e "  4. Configure alert notifications in Alertmanager"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo -e "  See README.md for detailed configuration and usage"
echo -e "  راجع README.md للحصول على إعدادات مفصلة والاستخدام"
echo ""
echo -e "${GREEN}✨ Happy Monitoring! / مراقبة سعيدة!${NC}"
