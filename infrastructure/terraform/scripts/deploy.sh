#!/bin/bash
# ======================================================================
# سكريبت نشر البنية التحتية لمنصة صحول
# Sahool Platform Infrastructure Deployment Script
# ======================================================================

set -e  # إيقاف السكريبت عند حدوث خطأ / Exit on error

# الألوان للمخرجات / Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# المتغيرات / Variables
ENVIRONMENT="${1:-production}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}نشر البنية التحتية لمنصة صحول${NC}"
echo -e "${CYAN}Sahool Platform Infrastructure Deployment${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo -e "${BLUE}البيئة / Environment:${NC} $ENVIRONMENT"
echo -e "${BLUE}المجلد / Directory:${NC} $TERRAFORM_DIR"
echo -e "${CYAN}======================================================================${NC}"
echo

# الانتقال إلى مجلد Terraform
# Navigate to Terraform directory
cd "$TERRAFORM_DIR"

# التحقق من المتطلبات
# Check prerequisites
echo -e "${BLUE}التحقق من المتطلبات...${NC}"
echo -e "${BLUE}Checking prerequisites...${NC}"

# Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ خطأ: Terraform غير مثبت${NC}"
    echo -e "${RED}❌ Error: Terraform is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Terraform $(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)${NC}"

# AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ خطأ: AWS CLI غير مثبت${NC}"
    echo -e "${RED}❌ Error: AWS CLI is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS CLI $(aws --version | cut -d' ' -f1)${NC}"

# التحقق من تكوين AWS
# Check AWS configuration
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ خطأ: AWS CLI غير مُكوّن بشكل صحيح${NC}"
    echo -e "${RED}❌ Error: AWS CLI is not configured properly${NC}"
    exit 1
fi
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: $ACCOUNT_ID${NC}"
echo

# التحقق من ملف المتغيرات
# Check variables file
VARS_FILE="environments/${ENVIRONMENT}.tfvars"
if [ ! -f "$VARS_FILE" ]; then
    echo -e "${RED}❌ خطأ: ملف المتغيرات غير موجود: $VARS_FILE${NC}"
    echo -e "${RED}❌ Error: Variables file not found: $VARS_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ ملف المتغيرات: $VARS_FILE${NC}"
echo -e "${GREEN}✓ Variables file: $VARS_FILE${NC}"
echo

# طلب كلمة مرور قاعدة البيانات
# Request database password
if [ -z "$TF_VAR_db_password" ]; then
    echo -e "${YELLOW}⚠ كلمة مرور قاعدة البيانات غير محددة${NC}"
    echo -e "${YELLOW}⚠ Database password not set${NC}"
    read -sp "أدخل كلمة مرور قاعدة البيانات / Enter database password: " DB_PASSWORD
    echo
    export TF_VAR_db_password="$DB_PASSWORD"
fi

# تهيئة Terraform
# Initialize Terraform
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}[1/4] تهيئة Terraform...${NC}"
echo -e "${BLUE}[1/4] Initializing Terraform...${NC}"
echo -e "${BLUE}======================================================================${NC}"
terraform init -upgrade
echo -e "${GREEN}✓ تمت التهيئة بنجاح${NC}"
echo -e "${GREEN}✓ Initialization successful${NC}"
echo

# التحقق من التنسيق
# Validate configuration
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}[2/4] التحقق من التنسيق...${NC}"
echo -e "${BLUE}[2/4] Validating configuration...${NC}"
echo -e "${BLUE}======================================================================${NC}"
terraform validate
echo -e "${GREEN}✓ التنسيق صحيح${NC}"
echo -e "${GREEN}✓ Configuration is valid${NC}"
echo

# عرض خطة التنفيذ
# Show execution plan
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}[3/4] عرض خطة التنفيذ...${NC}"
echo -e "${BLUE}[3/4] Showing execution plan...${NC}"
echo -e "${BLUE}======================================================================${NC}"
terraform plan -var-file="$VARS_FILE" -out=tfplan
echo

# تأكيد التطبيق
# Confirm application
echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}هل تريد تطبيق هذه التغييرات؟${NC}"
echo -e "${YELLOW}Do you want to apply these changes?${NC}"
echo -e "${YELLOW}======================================================================${NC}"
read -p "أدخل 'yes' للمتابعة / Enter 'yes' to continue: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}تم الإلغاء${NC}"
    echo -e "${RED}Cancelled${NC}"
    rm -f tfplan
    exit 0
fi

# تطبيق التغييرات
# Apply changes
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}[4/4] تطبيق التغييرات...${NC}"
echo -e "${BLUE}[4/4] Applying changes...${NC}"
echo -e "${BLUE}======================================================================${NC}"
terraform apply tfplan
rm -f tfplan
echo

# عرض المخرجات المهمة
# Display important outputs
echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}نجح النشر!${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo

echo -e "${CYAN}مجموعات EKS / EKS Clusters:${NC}"
echo -e "${CYAN}======================================================================${NC}"
RIYADH_CLUSTER=$(terraform output -raw riyadh_eks_cluster_name 2>/dev/null || echo "N/A")
JEDDAH_CLUSTER=$(terraform output -raw jeddah_eks_cluster_name 2>/dev/null || echo "N/A")
echo -e "${BLUE}الرياض / Riyadh:${NC} $RIYADH_CLUSTER"
echo -e "${BLUE}جدة / Jeddah:${NC} $JEDDAH_CLUSTER"
echo

echo -e "${CYAN}قواعد البيانات / Databases:${NC}"
echo -e "${CYAN}======================================================================${NC}"
RIYADH_DB=$(terraform output -raw riyadh_rds_endpoint 2>/dev/null || echo "N/A")
JEDDAH_DB=$(terraform output -raw jeddah_rds_endpoint 2>/dev/null || echo "N/A")
echo -e "${BLUE}الرياض / Riyadh:${NC} $RIYADH_DB"
echo -e "${BLUE}جدة / Jeddah:${NC} $JEDDAH_DB"
echo

echo -e "${CYAN}حاويات S3 / S3 Buckets:${NC}"
echo -e "${CYAN}======================================================================${NC}"
RIYADH_BUCKET=$(terraform output -raw riyadh_satellite_bucket_name 2>/dev/null || echo "N/A")
JEDDAH_BUCKET=$(terraform output -raw jeddah_satellite_bucket_name 2>/dev/null || echo "N/A")
echo -e "${BLUE}الرياض / Riyadh:${NC} $RIYADH_BUCKET"
echo -e "${BLUE}جدة / Jeddah:${NC} $JEDDAH_BUCKET"
echo

echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}الخطوات التالية / Next Steps:${NC}"
echo -e "${YELLOW}======================================================================${NC}"
echo -e "1. تكوين kubectl للاتصال بمجموعات EKS"
echo -e "   Configure kubectl to connect to EKS clusters"
echo -e "   ${CYAN}./scripts/configure-kubectl.sh${NC}"
echo
echo -e "2. نشر التطبيقات على Kubernetes"
echo -e "   Deploy applications to Kubernetes"
echo
echo -e "3. تكوين المراقبة والتنبيهات"
echo -e "   Configure monitoring and alerts"
echo -e "${GREEN}======================================================================${NC}"
