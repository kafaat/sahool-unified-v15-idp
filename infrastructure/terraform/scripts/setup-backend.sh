#!/bin/bash
# ======================================================================
# سكريبت إعداد البنية التحتية للـ Backend
# Backend Infrastructure Setup Script
# ======================================================================
# هذا السكريبت ينشئ S3 bucket و DynamoDB table لتخزين حالة Terraform
# This script creates S3 bucket and DynamoDB table for storing Terraform state
# ======================================================================

set -e  # إيقاف السكريبت عند حدوث خطأ / Exit on error

# الألوان للمخرجات / Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# المتغيرات / Variables
BUCKET_NAME="sahool-terraform-state"
DYNAMODB_TABLE="sahool-terraform-locks"
REGION="me-south-1"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}إعداد البنية التحتية لـ Terraform Backend${NC}"
echo -e "${BLUE}Setting up Terraform Backend Infrastructure${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo

# التحقق من تثبيت AWS CLI
# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}خطأ: AWS CLI غير مثبت${NC}"
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# التحقق من تكوين AWS CLI
# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}خطأ: AWS CLI غير مُكوّن بشكل صحيح${NC}"
    echo -e "${RED}Error: AWS CLI is not configured properly${NC}"
    echo -e "${YELLOW}قم بتشغيل: aws configure${NC}"
    echo -e "${YELLOW}Run: aws configure${NC}"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI مُكوّن بشكل صحيح${NC}"
echo -e "${GREEN}✓ AWS CLI is configured properly${NC}"
echo

# 1. إنشاء S3 bucket
# 1. Create S3 bucket
echo -e "${BLUE}[1/5] إنشاء S3 bucket...${NC}"
echo -e "${BLUE}[1/5] Creating S3 bucket...${NC}"
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo -e "${YELLOW}⚠ S3 bucket موجود بالفعل${NC}"
    echo -e "${YELLOW}⚠ S3 bucket already exists${NC}"
else
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION"
    echo -e "${GREEN}✓ تم إنشاء S3 bucket بنجاح${NC}"
    echo -e "${GREEN}✓ S3 bucket created successfully${NC}"
fi
echo

# 2. تفعيل versioning
# 2. Enable versioning
echo -e "${BLUE}[2/5] تفعيل versioning...${NC}"
echo -e "${BLUE}[2/5] Enabling versioning...${NC}"
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled
echo -e "${GREEN}✓ تم تفعيل versioning${NC}"
echo -e "${GREEN}✓ Versioning enabled${NC}"
echo

# 3. تفعيل التشفير
# 3. Enable encryption
echo -e "${BLUE}[3/5] تفعيل التشفير...${NC}"
echo -e "${BLUE}[3/5] Enabling encryption...${NC}"
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
echo -e "${GREEN}✓ تم تفعيل التشفير${NC}"
echo -e "${GREEN}✓ Encryption enabled${NC}"
echo

# 4. حظر الوصول العام
# 4. Block public access
echo -e "${BLUE}[4/5] حظر الوصول العام...${NC}"
echo -e "${BLUE}[4/5] Blocking public access...${NC}"
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
echo -e "${GREEN}✓ تم حظر الوصول العام${NC}"
echo -e "${GREEN}✓ Public access blocked${NC}"
echo

# 5. إنشاء جدول DynamoDB
# 5. Create DynamoDB table
echo -e "${BLUE}[5/5] إنشاء جدول DynamoDB...${NC}"
echo -e "${BLUE}[5/5] Creating DynamoDB table...${NC}"
if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" --region "$REGION" 2>/dev/null; then
    echo -e "${YELLOW}⚠ جدول DynamoDB موجود بالفعل${NC}"
    echo -e "${YELLOW}⚠ DynamoDB table already exists${NC}"
else
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region "$REGION" \
        > /dev/null
    echo -e "${GREEN}✓ تم إنشاء جدول DynamoDB بنجاح${NC}"
    echo -e "${GREEN}✓ DynamoDB table created successfully${NC}"

    # انتظار جاهزية الجدول
    # Wait for table to be ready
    echo -e "${YELLOW}انتظار جاهزية الجدول...${NC}"
    echo -e "${YELLOW}Waiting for table to be ready...${NC}"
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE" --region "$REGION"
    echo -e "${GREEN}✓ الجدول جاهز${NC}"
    echo -e "${GREEN}✓ Table is ready${NC}"
fi
echo

# ملخص
# Summary
echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}تم إعداد البنية التحتية للـ Backend بنجاح!${NC}"
echo -e "${GREEN}Backend Infrastructure Setup Complete!${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo
echo -e "${BLUE}S3 Bucket:${NC} $BUCKET_NAME"
echo -e "${BLUE}DynamoDB Table:${NC} $DYNAMODB_TABLE"
echo -e "${BLUE}Region:${NC} $REGION"
echo
echo -e "${YELLOW}الخطوات التالية:${NC}"
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. قم بإلغاء التعليق على كتلة backend في main.tf"
echo -e "   Uncomment the backend block in main.tf"
echo -e "2. قم بتشغيل: terraform init -migrate-state"
echo -e "   Run: terraform init -migrate-state"
echo -e "${GREEN}======================================================================${NC}"
