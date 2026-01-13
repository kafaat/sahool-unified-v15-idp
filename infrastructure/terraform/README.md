# البنية التحتية لمنصة صحول - متعددة المناطق

# Sahool Platform Infrastructure - Multi-Region

البنية التحتية الكاملة لمنصة صحول في المملكة العربية السعودية باستخدام Terraform وAWS.

Complete infrastructure for Sahool platform in Saudi Arabia using Terraform and AWS.

## نظرة عامة / Overview

هذه البنية التحتية تنشئ بيئة كاملة متعددة المناطق في AWS للمملكة العربية السعودية:

This infrastructure creates a complete multi-region environment in AWS for Saudi Arabia:

### المناطق / Regions

1. **الرياض (Riyadh)** - المنطقة الرئيسية / Primary Region
   - موارد أكبر للتعامل مع الحمل الرئيسي
   - Larger resources to handle main workload

2. **جدة (Jeddah)** - المنطقة الثانوية / Secondary Region
   - موارد للنسخ الاحتياطي والتوزيع الجغرافي
   - Resources for backup and geographic distribution

### المكونات الرئيسية / Main Components

#### 1. الشبكة / Networking

- **VPC** مع شبكات فرعية عامة وخاصة في 3 مناطق توفر
- **VPC** with public and private subnets across 3 availability zones
- **NAT Gateways** للوصول الآمن إلى الإنترنت
- **NAT Gateways** for secure internet access
- **VPC Peering** للاتصال بين المناطق
- **VPC Peering** for cross-region connectivity

#### 2. الحوسبة / Compute

- **Amazon EKS** - مجموعات Kubernetes المُدارة
- **Amazon EKS** - Managed Kubernetes clusters
- **Auto Scaling** - توسع تلقائي حسب الحمل
- **Auto Scaling** - Automatic scaling based on load

#### 3. قواعد البيانات / Databases

- **Amazon RDS PostgreSQL 15** مع PostGIS للبيانات الجغرافية
- **Amazon RDS PostgreSQL 15** with PostGIS for geospatial data
- **Multi-AZ** للتوفر العالي
- **Multi-AZ** for high availability
- نسخ احتياطية يومية لمدة 30 يوم
- Daily backups with 30-day retention

#### 4. الذاكرة المؤقتة / Caching

- **Amazon ElastiCache Redis 7.0**
- مجموعة Redis مع تكرار تلقائي
- Redis cluster with automatic failover
- تشفير شامل (في السكون والحركة)
- Full encryption (at rest and in transit)

#### 5. التخزين / Storage

- **Amazon S3** للصور الفضائية (Sentinel، Landsat)
- **Amazon S3** for satellite imagery (Sentinel, Landsat)
- **S3** لنماذج الذكاء الاصطناعي والمخرجات
- **S3** for AI models and outputs
- **S3 Replication** بين المناطق للنسخ الاحتياطي
- **S3 Replication** between regions for backup

#### 6. الأمان / Security

- **KMS** للتشفير الشامل
- **KMS** for comprehensive encryption
- **Security Groups** مُحكمة
- Strict **Security Groups**
- **IAM Roles** مع أقل الصلاحيات
- **IAM Roles** with least privilege

## هيكل المشروع / Project Structure

```
infrastructure/terraform/
├── main.tf                      # التكوين الرئيسي / Main configuration
├── variables.tf                 # المتغيرات العامة / Global variables
├── outputs.tf                   # المخرجات الرئيسية / Main outputs
├── README.md                    # هذا الملف / This file
├── .gitignore                   # تجاهل الملفات الحساسة / Ignore sensitive files
│
├── modules/                     # الوحدات / Modules
│   └── region/                  # وحدة المنطقة / Region module
│       ├── main.tf              # موارد المنطقة / Region resources
│       ├── variables.tf         # متغيرات المنطقة / Region variables
│       └── outputs.tf           # مخرجات المنطقة / Region outputs
│
└── environments/                # البيئات / Environments
    └── production.tfvars        # متغيرات الإنتاج / Production variables
```

## المتطلبات الأساسية / Prerequisites

1. **Terraform** >= 1.5.0

   ```bash
   terraform --version
   ```

2. **AWS CLI** مُثبّت ومُكوّن

   ```bash
   aws --version
   aws configure
   ```

3. **حساب AWS** مع الصلاحيات المناسبة
   - AWS account with appropriate permissions

4. **متغيرات البيئة** المطلوبة:
   ```bash
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_DEFAULT_REGION="me-south-1"
   ```

## الاستخدام / Usage

### 1. التهيئة الأولية / Initial Setup

```bash
# الانتقال إلى مجلد Terraform
# Navigate to Terraform directory
cd infrastructure/terraform/

# تهيئة Terraform وتحميل المزودات
# Initialize Terraform and download providers
terraform init
```

### 2. مراجعة الخطة / Review Plan

```bash
# مراجعة التغييرات قبل التطبيق
# Review changes before applying
terraform plan -var-file="environments/production.tfvars" -var="db_password=YOUR_SECURE_PASSWORD"
```

### 3. النشر / Deploy

```bash
# نشر البنية التحتية
# Deploy infrastructure
terraform apply -var-file="environments/production.tfvars" -var="db_password=YOUR_SECURE_PASSWORD"
```

### 4. الاتصال بمجموعات EKS / Connect to EKS Clusters

```bash
# الرياض / Riyadh
aws eks update-kubeconfig --region me-south-1 --name production-sahool-riyadh

# جدة / Jeddah
aws eks update-kubeconfig --region me-south-1 --name production-sahool-jeddah

# التحقق من الاتصال / Verify connection
kubectl get nodes
```

### 5. عرض المخرجات / View Outputs

```bash
# عرض جميع المخرجات
# Display all outputs
terraform output

# عرض مخرج معين
# Display specific output
terraform output riyadh_eks_cluster_endpoint
terraform output infrastructure_summary
```

### 6. الحذف (احذر!) / Destroy (Caution!)

```bash
# حذف البنية التحتية بالكامل
# Destroy entire infrastructure
terraform destroy -var-file="environments/production.tfvars" -var="db_password=YOUR_SECURE_PASSWORD"
```

## الأمان / Security

### أفضل الممارسات / Best Practices

1. **كلمات المرور / Passwords**
   - لا تُخزّن كلمات المرور في الملفات
   - Don't store passwords in files
   - استخدم AWS Secrets Manager أو متغيرات البيئة
   - Use AWS Secrets Manager or environment variables

2. **ملفات الحالة / State Files**
   - مُخزّنة في S3 مع التشفير
   - Stored in S3 with encryption
   - لا تُرفع إلى Git
   - Don't commit to Git

3. **الوصول / Access**
   - استخدم IAM Roles بدلاً من المفاتيح
   - Use IAM Roles instead of keys
   - فعّل MFA للحسابات الحساسة
   - Enable MFA for sensitive accounts

### تخزين الأسرار / Secrets Management

```bash
# حفظ كلمة مرور قاعدة البيانات في AWS Secrets Manager
# Store database password in AWS Secrets Manager
aws secretsmanager create-secret \
  --name sahool/production/db-password \
  --secret-string "YOUR_SECURE_PASSWORD" \
  --region me-south-1

# استرجاع كلمة المرور
# Retrieve password
aws secretsmanager get-secret-value \
  --secret-id sahool/production/db-password \
  --region me-south-1 \
  --query SecretString \
  --output text
```

## التكلفة المتوقعة / Estimated Cost

### بيئة الإنتاج / Production Environment

| المكون / Component   | الرياض / Riyadh  | جدة / Jeddah     | الإجمالي / Total |
| -------------------- | ---------------- | ---------------- | ---------------- |
| EKS Cluster          | $75/شهر          | $75/شهر          | $150/شهر         |
| EC2 Nodes            | $600/شهر         | $300/شهر         | $900/شهر         |
| RDS PostgreSQL       | $400/شهر         | $200/شهر         | $600/شهر         |
| ElastiCache Redis    | $200/شهر         | $150/شهر         | $350/شهر         |
| NAT Gateways         | $100/شهر         | $100/شهر         | $200/شهر         |
| S3 & Transfer        | متغير / Variable | متغير / Variable | ~$200/شهر        |
| **الإجمالي / Total** |                  |                  | **~$2,400/شهر**  |

_ملاحظة: التكاليف تقريبية وقد تختلف حسب الاستخدام_
_Note: Costs are approximate and may vary based on usage_

## الصيانة / Maintenance

### التحديثات / Updates

```bash
# تحديث Kubernetes
# Update Kubernetes version
# قم بتعديل eks_cluster_version في production.tfvars
# Edit eks_cluster_version in production.tfvars
terraform plan -var-file="environments/production.tfvars"
terraform apply -var-file="environments/production.tfvars"
```

### النسخ الاحتياطي / Backups

- **RDS**: نسخ احتياطية تلقائية يومية (30 يوم)
- **RDS**: Automatic daily backups (30 days retention)
- **S3**: versioning مُفعّل + Replication بين المناطق
- **S3**: Versioning enabled + Cross-region replication

### المراقبة / Monitoring

```bash
# عرض سجلات EKS
# View EKS logs
kubectl logs -n kube-system -l app=aws-node

# مراقبة استخدام الموارد
# Monitor resource usage
kubectl top nodes
kubectl top pods --all-namespaces
```

## استكشاف الأخطاء / Troubleshooting

### مشاكل شائعة / Common Issues

1. **فشل تهيئة Terraform**

   ```bash
   terraform init -upgrade
   ```

2. **أخطاء الصلاحيات**
   - تحقق من صلاحيات IAM
   - Check IAM permissions

3. **تعذر الاتصال بـ EKS**
   ```bash
   aws eks update-kubeconfig --region me-south-1 --name cluster-name
   ```

## المساهمة / Contributing

لتحسين البنية التحتية:
To improve the infrastructure:

1. أنشئ فرع جديد / Create a new branch
2. قم بإجراء التعديلات / Make your changes
3. اختبر التغييرات / Test changes
4. أنشئ Pull Request / Create Pull Request

## الترخيص / License

هذا المشروع جزء من منصة صحول
This project is part of Sahool platform

## الدعم / Support

للدعم والمساعدة:
For support and assistance:

- راجع الوثائق / Check documentation
- افتح Issue في GitHub / Open GitHub Issue
- تواصل مع الفريق / Contact the team

---

**ملاحظة هامة**: هذه بنية تحتية للإنتاج. تأكد من مراجعة جميع التكوينات قبل النشر.

**Important Note**: This is production infrastructure. Ensure all configurations are reviewed before deployment.
