#!/bin/bash
# ======================================================================
# سكريبت تكوين kubectl للاتصال بمجموعات EKS
# Configure kubectl to connect to EKS clusters
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
REGION="${1:-me-south-1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}تكوين kubectl للاتصال بمجموعات EKS${NC}"
echo -e "${CYAN}Configure kubectl to Connect to EKS Clusters${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo

# الانتقال إلى مجلد Terraform
# Navigate to Terraform directory
cd "$TERRAFORM_DIR"

# التحقق من المتطلبات
# Check prerequisites
echo -e "${BLUE}التحقق من المتطلبات...${NC}"
echo -e "${BLUE}Checking prerequisites...${NC}"

# kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ خطأ: kubectl غير مثبت${NC}"
    echo -e "${RED}❌ Error: kubectl is not installed${NC}"
    echo
    echo -e "${YELLOW}لتثبيت kubectl:${NC}"
    echo -e "${YELLOW}To install kubectl:${NC}"
    echo -e "curl -LO \"https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\""
    echo -e "chmod +x kubectl"
    echo -e "sudo mv kubectl /usr/local/bin/"
    exit 1
fi
echo -e "${GREEN}✓ kubectl $(kubectl version --client --short 2>/dev/null || kubectl version --client)${NC}"

# AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ خطأ: AWS CLI غير مثبت${NC}"
    echo -e "${RED}❌ Error: AWS CLI is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS CLI${NC}"

# التحقق من تكوين AWS
# Check AWS configuration
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ خطأ: AWS CLI غير مُكوّن بشكل صحيح${NC}"
    echo -e "${RED}❌ Error: AWS CLI is not configured properly${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS مُكوّن بشكل صحيح${NC}"
echo -e "${GREEN}✓ AWS configured properly${NC}"
echo

# الحصول على أسماء المجموعات من Terraform
# Get cluster names from Terraform
echo -e "${BLUE}الحصول على معلومات المجموعات من Terraform...${NC}"
echo -e "${BLUE}Getting cluster information from Terraform...${NC}"

RIYADH_CLUSTER=$(terraform output -raw riyadh_eks_cluster_name 2>/dev/null)
JEDDAH_CLUSTER=$(terraform output -raw jeddah_eks_cluster_name 2>/dev/null)

if [ -z "$RIYADH_CLUSTER" ] || [ -z "$JEDDAH_CLUSTER" ]; then
    echo -e "${RED}❌ خطأ: لم يتم العثور على معلومات المجموعات${NC}"
    echo -e "${RED}❌ Error: Cluster information not found${NC}"
    echo -e "${YELLOW}تأكد من نشر البنية التحتية أولاً${NC}"
    echo -e "${YELLOW}Make sure to deploy the infrastructure first${NC}"
    exit 1
fi

echo -e "${GREEN}✓ وُجدت معلومات المجموعات${NC}"
echo -e "${GREEN}✓ Cluster information found${NC}"
echo

# تكوين kubectl للرياض
# Configure kubectl for Riyadh
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}[1/2] تكوين kubectl للرياض...${NC}"
echo -e "${BLUE}[1/2] Configuring kubectl for Riyadh...${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "${CYAN}المجموعة / Cluster:${NC} $RIYADH_CLUSTER"
echo -e "${CYAN}المنطقة / Region:${NC} $REGION"
echo

aws eks update-kubeconfig \
    --region "$REGION" \
    --name "$RIYADH_CLUSTER" \
    --alias "sahool-riyadh"

echo -e "${GREEN}✓ تم تكوين kubectl للرياض${NC}"
echo -e "${GREEN}✓ kubectl configured for Riyadh${NC}"
echo

# تكوين kubectl لجدة
# Configure kubectl for Jeddah
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}[2/2] تكوين kubectl لجدة...${NC}"
echo -e "${BLUE}[2/2] Configuring kubectl for Jeddah...${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "${CYAN}المجموعة / Cluster:${NC} $JEDDAH_CLUSTER"
echo -e "${CYAN}المنطقة / Region:${NC} $REGION"
echo

aws eks update-kubeconfig \
    --region "$REGION" \
    --name "$JEDDAH_CLUSTER" \
    --alias "sahool-jeddah"

echo -e "${GREEN}✓ تم تكوين kubectl لجدة${NC}"
echo -e "${GREEN}✓ kubectl configured for Jeddah${NC}"
echo

# التحقق من الاتصال
# Verify connection
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}التحقق من الاتصال بالمجموعات...${NC}"
echo -e "${BLUE}Verifying connection to clusters...${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo

echo -e "${CYAN}الرياض / Riyadh:${NC}"
kubectl --context=sahool-riyadh get nodes 2>/dev/null || echo -e "${YELLOW}⚠ العقد قد تكون قيد الإنشاء...${NC}"
echo

echo -e "${CYAN}جدة / Jeddah:${NC}"
kubectl --context=sahool-jeddah get nodes 2>/dev/null || echo -e "${YELLOW}⚠ العقد قد تكون قيد الإنشاء...${NC}"
echo

# عرض السياقات المتاحة
# Show available contexts
echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}اكتمل التكوين بنجاح!${NC}"
echo -e "${GREEN}Configuration Complete!${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo

echo -e "${CYAN}السياقات المتاحة / Available Contexts:${NC}"
echo -e "${CYAN}======================================================================${NC}"
kubectl config get-contexts | grep sahool || echo -e "${YELLOW}لم يتم العثور على سياقات${NC}"
echo

echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}استخدام kubectl مع المجموعات / Using kubectl with Clusters:${NC}"
echo -e "${YELLOW}======================================================================${NC}"
echo
echo -e "${BLUE}للتبديل إلى الرياض / Switch to Riyadh:${NC}"
echo -e "  kubectl config use-context sahool-riyadh"
echo
echo -e "${BLUE}للتبديل إلى جدة / Switch to Jeddah:${NC}"
echo -e "  kubectl config use-context sahool-jeddah"
echo
echo -e "${BLUE}استخدام سياق محدد مؤقتاً / Use specific context temporarily:${NC}"
echo -e "  kubectl --context=sahool-riyadh get pods"
echo -e "  kubectl --context=sahool-jeddah get pods"
echo
echo -e "${BLUE}عرض العقد / View nodes:${NC}"
echo -e "  kubectl get nodes"
echo
echo -e "${BLUE}عرض جميع الـ pods / View all pods:${NC}"
echo -e "  kubectl get pods --all-namespaces"
echo
echo -e "${GREEN}======================================================================${NC}"

# تعيين السياق الافتراضي للرياض
# Set default context to Riyadh
kubectl config use-context sahool-riyadh
echo -e "${GREEN}✓ السياق الافتراضي الآن: sahool-riyadh${NC}"
echo -e "${GREEN}✓ Default context is now: sahool-riyadh${NC}"
