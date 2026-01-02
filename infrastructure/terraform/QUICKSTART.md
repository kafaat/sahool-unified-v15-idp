# دليل البدء السريع / Quick Start Guide
# البنية التحتية لمنصة صحول - السعودية

## نظرة سريعة / Quick Overview

هذا دليل سريع لنشر البنية التحتية لمنصة صحول في المملكة العربية السعودية.

This is a quick guide to deploy Sahool platform infrastructure in Saudi Arabia.

## 📋 المتطلبات / Prerequisites

```bash
# تحقق من تثبيت الأدوات المطلوبة / Check required tools are installed
terraform --version   # يجب أن يكون >= 1.5.0 / Should be >= 1.5.0
aws --version        # AWS CLI
kubectl version      # Kubernetes CLI (اختياري للآن / optional for now)
```

## 🚀 البدء السريع / Quick Start

### الخطوة 1: تكوين AWS
```bash
# تكوين بيانات الاعتماد / Configure AWS credentials
aws configure

# أو استخدام متغيرات البيئة / Or use environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="me-south-1"
```

### الخطوة 2: إعداد Backend (اختياري)
```bash
# إنشاء S3 bucket و DynamoDB للحالة / Create S3 and DynamoDB for state
cd infrastructure/terraform
./scripts/setup-backend.sh
```

### الخطوة 3: تكوين المتغيرات
```bash
# نسخ ملف المثال / Copy example file
cp terraform.tfvars.example terraform.tfvars

# تعديل القيم حسب الحاجة / Edit values as needed
nano terraform.tfvars
```

### الخطوة 4: النشر
```bash
# استخدام السكريبت الآلي / Use automated script
./scripts/deploy.sh production

# أو النشر يدوياً / Or deploy manually
terraform init
terraform plan -var-file="environments/production.tfvars" -var="db_password=YOUR_PASSWORD"
terraform apply -var-file="environments/production.tfvars" -var="db_password=YOUR_PASSWORD"
```

### الخطوة 5: تكوين kubectl
```bash
# تكوين kubectl للاتصال بمجموعات EKS / Configure kubectl for EKS
./scripts/configure-kubectl.sh

# التحقق من الاتصال / Verify connection
kubectl get nodes
```

## 📦 ما الذي سيتم إنشاؤه؟ / What Will Be Created?

### منطقة الرياض (Primary)
- ✅ VPC مع 3 Availability Zones
- ✅ EKS Cluster مع 3-10 عقد
- ✅ RDS PostgreSQL 15 + PostGIS (db.r6g.xlarge)
- ✅ ElastiCache Redis 7.0 (3 عقد)
- ✅ S3 Buckets للصور الفضائية والنماذج

### منطقة جدة (Secondary)
- ✅ VPC مع 3 Availability Zones
- ✅ EKS Cluster مع 2-8 عقد
- ✅ RDS PostgreSQL 15 + PostGIS (db.r6g.large)
- ✅ ElastiCache Redis 7.0 (2 عقد)
- ✅ S3 Buckets للصور الفضائية والنماذج

### الاتصال بين المناطق
- ✅ VPC Peering بين الرياض وجدة
- ✅ S3 Replication من الرياض إلى جدة

## 💰 التكلفة المتوقعة / Estimated Cost

| المنطقة / Region | التكلفة الشهرية / Monthly Cost |
|------------------|--------------------------------|
| الرياض (Riyadh) | ~$1,500 - $2,000 |
| جدة (Jeddah) | ~$800 - $1,200 |
| **الإجمالي / Total** | **~$2,300 - $3,200** |

## 🔐 الأمان / Security

### تخزين كلمة مرور قاعدة البيانات / Store Database Password

```bash
# استخدام متغير بيئة / Use environment variable
export TF_VAR_db_password="your-secure-password"

# أو AWS Secrets Manager / Or AWS Secrets Manager
aws secretsmanager create-secret \
  --name sahool/production/db-password \
  --secret-string "your-secure-password" \
  --region me-south-1
```

## 📊 عرض المعلومات / View Information

```bash
# عرض جميع المخرجات / Display all outputs
terraform output

# عرض ملخص البنية التحتية / Display infrastructure summary
terraform output infrastructure_summary

# عرض تعليمات النشر / Display deployment instructions
terraform output deployment_instructions
```

## 🔧 الأوامر المفيدة / Useful Commands

### Terraform
```bash
# تنسيق الملفات / Format files
terraform fmt -recursive

# التحقق من الصحة / Validate configuration
terraform validate

# عرض الحالة / Show state
terraform show

# عرض قائمة الموارد / List resources
terraform state list
```

### kubectl
```bash
# التبديل بين المجموعات / Switch between clusters
kubectl config use-context sahool-riyadh
kubectl config use-context sahool-jeddah

# عرض العقد / View nodes
kubectl get nodes

# عرض جميع الموارد / View all resources
kubectl get all --all-namespaces

# عرض استخدام الموارد / View resource usage
kubectl top nodes
kubectl top pods --all-namespaces
```

### AWS CLI
```bash
# عرض معلومات EKS / View EKS information
aws eks list-clusters --region me-south-1
aws eks describe-cluster --name production-sahool-riyadh --region me-south-1

# عرض معلومات RDS / View RDS information
aws rds describe-db-instances --region me-south-1

# عرض S3 buckets / View S3 buckets
aws s3 ls
```

## 🗑️ الحذف / Cleanup

```bash
# ⚠️ تحذير: هذا سيحذف جميع الموارد!
# ⚠️ Warning: This will delete all resources!

terraform destroy -var-file="environments/production.tfvars" -var="db_password=YOUR_PASSWORD"
```

## 🐛 استكشاف الأخطاء / Troubleshooting

### مشكلة: فشل تهيئة Terraform
```bash
# الحل / Solution
terraform init -upgrade
```

### مشكلة: أخطاء الصلاحيات
```bash
# تحقق من صلاحيات IAM / Check IAM permissions
aws sts get-caller-identity
```

### مشكلة: تعذر الاتصال بـ EKS
```bash
# إعادة تكوين kubectl / Reconfigure kubectl
aws eks update-kubeconfig --region me-south-1 --name production-sahool-riyadh
```

### مشكلة: خطأ في lock state
```bash
# إزالة القفل يدوياً (احذر!) / Remove lock manually (caution!)
terraform force-unlock LOCK_ID
```

## 📚 موارد إضافية / Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Amazon EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [PostgreSQL + PostGIS Documentation](https://postgis.net/documentation/)

## 📞 الدعم / Support

للمساعدة والدعم:
For help and support:

1. راجع ملف [README.md](./README.md) للوثائق الكاملة
2. افتح issue في GitHub
3. تواصل مع فريق صحول

## ✅ قائمة التحقق / Checklist

- [ ] تثبيت Terraform >= 1.5.0
- [ ] تثبيت AWS CLI
- [ ] تكوين بيانات اعتماد AWS
- [ ] إنشاء ملف terraform.tfvars
- [ ] تعيين كلمة مرور قاعدة البيانات
- [ ] إنشاء S3 backend (اختياري)
- [ ] تشغيل terraform plan
- [ ] مراجعة التكاليف المتوقعة
- [ ] تشغيل terraform apply
- [ ] تكوين kubectl
- [ ] التحقق من الاتصال بـ EKS
- [ ] نشر التطبيقات

---

**تم الإنشاء بواسطة / Created by:** فريق صحول / Sahool Team
**التاريخ / Date:** 2026-01-02
