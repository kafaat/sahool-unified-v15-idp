# ======================================================================
# تكوين التخزين الخلفي لحالة Terraform
# Terraform Backend Configuration for State Storage
# ======================================================================
# ملاحظة: يجب إنشاء S3 bucket و DynamoDB table يدوياً قبل استخدام هذا التكوين
# Note: S3 bucket and DynamoDB table must be created manually before using this configuration
# ======================================================================

# لتفعيل التخزين الخلفي، قم بإلغاء التعليق على الكود التالي
# To enable backend storage, uncomment the following code:

/*
terraform {
  backend "s3" {
    # اسم S3 bucket لتخزين حالة Terraform
    # S3 bucket name for storing Terraform state
    bucket = "sahool-terraform-state"

    # المفتاح (المسار) داخل الحاوية
    # Key (path) inside the bucket
    key = "multi-region/terraform.tfstate"

    # المنطقة التي يوجد بها الـ bucket
    # Region where the bucket is located
    region = "me-south-1"

    # تفعيل التشفير
    # Enable encryption
    encrypt = true

    # جدول DynamoDB للقفل (لمنع التعديلات المتزامنة)
    # DynamoDB table for locking (to prevent concurrent modifications)
    dynamodb_table = "sahool-terraform-locks"

    # تفعيل versioning
    # Enable versioning
    versioning = true
  }
}
*/

# ======================================================================
# تعليمات إنشاء البنية التحتية للـ Backend
# Instructions for Creating Backend Infrastructure
# ======================================================================
# يجب تنفيذ الأوامر التالية مرة واحدة فقط لإنشاء البنية التحتية للـ backend:
# Execute the following commands only once to create the backend infrastructure:

# 1. إنشاء S3 bucket
#    Create S3 bucket
# aws s3api create-bucket \
#   --bucket sahool-terraform-state \
#   --region me-south-1 \
#   --create-bucket-configuration LocationConstraint=me-south-1

# 2. تفعيل versioning على الـ bucket
#    Enable versioning on the bucket
# aws s3api put-bucket-versioning \
#   --bucket sahool-terraform-state \
#   --versioning-configuration Status=Enabled

# 3. تفعيل التشفير
#    Enable encryption
# aws s3api put-bucket-encryption \
#   --bucket sahool-terraform-state \
#   --server-side-encryption-configuration '{
#     "Rules": [{
#       "ApplyServerSideEncryptionByDefault": {
#         "SSEAlgorithm": "AES256"
#       }
#     }]
#   }'

# 4. حظر الوصول العام
#    Block public access
# aws s3api put-public-access-block \
#   --bucket sahool-terraform-state \
#   --public-access-block-configuration \
#     "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 5. إنشاء جدول DynamoDB للقفل
#    Create DynamoDB table for locking
# aws dynamodb create-table \
#   --table-name sahool-terraform-locks \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
#   --region me-south-1

# ======================================================================
# بعد إنشاء البنية التحتية للـ backend:
# After creating the backend infrastructure:
# ======================================================================
# 1. قم بإلغاء التعليق على كتلة terraform في أعلى هذا الملف
#    Uncomment the terraform block at the top of this file
#
# 2. قم بتشغيل:
#    Run:
#    terraform init -migrate-state
#
# 3. سيتم نقل حالة Terraform إلى S3
#    Terraform state will be migrated to S3
#
# ======================================================================

# ======================================================================
# ملاحظات الأمان / Security Notes
# ======================================================================
# - يجب تفعيل versioning على S3 bucket للحماية من الحذف العرضي
#   Versioning must be enabled on S3 bucket to protect against accidental deletion
#
# - يجب تفعيل التشفير على S3 bucket
#   Encryption must be enabled on S3 bucket
#
# - يجب استخدام DynamoDB للقفل لمنع التعديلات المتزامنة
#   DynamoDB locking must be used to prevent concurrent modifications
#
# - يجب حظر الوصول العام إلى S3 bucket
#   Public access to S3 bucket must be blocked
#
# - يوصى باستخدام IAM roles بدلاً من access keys
#   Using IAM roles instead of access keys is recommended
# ======================================================================
