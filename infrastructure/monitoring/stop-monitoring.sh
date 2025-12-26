#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Monitoring Stack Shutdown Script
# سكريبت إيقاف مجموعة المراقبة
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      SAHOOL Platform - Monitoring Stack Shutdown              ║${NC}"
echo -e "${BLUE}║      إيقاف مجموعة المراقبة لمنصة سهول                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse command line arguments
REMOVE_VOLUMES=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --remove-volumes)
            REMOVE_VOLUMES=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./stop-monitoring.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --remove-volumes    Remove data volumes (WARNING: deletes all metrics)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "الاستخدام: ./stop-monitoring.sh [الخيارات]"
            echo ""
            echo "الخيارات:"
            echo "  --remove-volumes    حذف وحدات البيانات (تحذير: يحذف جميع المقاييس)"
            echo "  -h, --help          عرض هذه الرسالة"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Stop services
echo -e "${BLUE}🛑 Stopping monitoring services...${NC}"
echo -e "${BLUE}🛑 جاري إيقاف خدمات المراقبة...${NC}"

if [ "$REMOVE_VOLUMES" = true ]; then
    echo -e "${RED}⚠️  WARNING: This will delete all monitoring data!${NC}"
    echo -e "${RED}⚠️  تحذير: سيتم حذف جميع بيانات المراقبة!${NC}"
    echo -e "${YELLOW}Press Ctrl+C to cancel, or wait 5 seconds to continue...${NC}"
    echo -e "${YELLOW}اضغط Ctrl+C للإلغاء، أو انتظر 5 ثوانٍ للمتابعة...${NC}"
    sleep 5

    docker-compose -f docker-compose.monitoring.yml down -v
    echo -e "${GREEN}✅ Services stopped and volumes removed${NC}"
    echo -e "${GREEN}✅ تم إيقاف الخدمات وحذف وحدات التخزين${NC}"
else
    docker-compose -f docker-compose.monitoring.yml down
    echo -e "${GREEN}✅ Services stopped (data preserved)${NC}"
    echo -e "${GREEN}✅ تم إيقاف الخدمات (تم الحفاظ على البيانات)${NC}"
fi

echo ""
echo -e "${BLUE}📊 Monitoring Stack Status:${NC}"
docker-compose -f docker-compose.monitoring.yml ps
echo ""

if [ "$REMOVE_VOLUMES" = false ]; then
    echo -e "${YELLOW}💡 Tip: Use './stop-monitoring.sh --remove-volumes' to also delete data${NC}"
    echo -e "${YELLOW}💡 نصيحة: استخدم './stop-monitoring.sh --remove-volumes' لحذف البيانات أيضاً${NC}"
fi

echo ""
echo -e "${GREEN}✨ Monitoring stack stopped successfully!${NC}"
echo -e "${GREEN}✨ تم إيقاف مجموعة المراقبة بنجاح!${NC}"
