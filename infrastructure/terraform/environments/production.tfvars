# ======================================================================
# متغيرات بيئة الإنتاج لمنصة صحول - المملكة العربية السعودية
# Production Environment Variables for Sahool Platform - Saudi Arabia
# ======================================================================
# هذا الملف يحدد قيم المتغيرات لبيئة الإنتاج في المملكة
# This file defines variable values for the production environment in Saudi Arabia
# ======================================================================

# ======================================================================
# الإعدادات العامة (General Settings)
# ======================================================================
environment = "production"

# المنطقة الرئيسية: البحرين (الأقرب لمدن السعودية)
# Primary region: Bahrain (closest to Saudi cities)
primary_region   = "me-south-1"
secondary_region = "me-south-1"

# إصدار Kubernetes
# Kubernetes version
eks_cluster_version = "1.28"

# ======================================================================
# بيانات اعتماد قاعدة البيانات (Database Credentials)
# ملاحظة: يجب تخزين كلمة المرور في AWS Secrets Manager أو متغيرات البيئة
# Note: Password should be stored in AWS Secrets Manager or environment variables
# ======================================================================
db_username = "sahool_admin"
# db_password = "CHANGE_ME_IN_SECRETS_MANAGER"  # يتم تعيينها عبر متغير بيئة

# ======================================================================
# إعدادات منطقة الرياض (Riyadh Region Settings)
# ======================================================================
# المنطقة الرئيسية مع موارد أكبر للتعامل مع الحمل الأساسي
# Primary region with larger resources to handle main load

# الشبكة - Network
riyadh_vpc_cidr = "10.0.0.0/16"

# مجموعة EKS - EKS Cluster
# استخدام t3.xlarge للإنتاج (4 vCPUs، 16 GB RAM)
# Using t3.xlarge for production (4 vCPUs, 16 GB RAM)
riyadh_node_instance_type = "t3.xlarge"
riyadh_min_nodes          = 3   # الحد الأدنى للتوفر العالي
riyadh_max_nodes          = 10  # للتوسع التلقائي عند الحاجة
riyadh_desired_nodes      = 5   # العدد الابتدائي المطلوب

# قاعدة البيانات RDS - RDS Database
# استخدام db.r6g.xlarge لأداء جيد (4 vCPUs، 32 GB RAM)
# Using db.r6g.xlarge for good performance (4 vCPUs, 32 GB RAM)
riyadh_db_instance_class     = "db.r6g.xlarge"
riyadh_db_allocated_storage  = 500  # 500 GB للبيانات الجغرافية

# Redis Cache
# استخدام cache.r6g.large (2 vCPUs، 13.07 GB RAM)
# Using cache.r6g.large (2 vCPUs, 13.07 GB RAM)
riyadh_redis_node_type    = "cache.r6g.large"
riyadh_redis_num_nodes    = 3  # للتوفر العالي

# ======================================================================
# إعدادات منطقة جدة (Jeddah Region Settings)
# ======================================================================
# المنطقة الثانوية مع موارد أقل للنسخ الاحتياطي والتوزيع
# Secondary region with smaller resources for backup and distribution

# الشبكة - Network
jeddah_vpc_cidr = "10.1.0.0/16"

# مجموعة EKS - EKS Cluster
# استخدام t3.large للمنطقة الثانوية (2 vCPUs، 8 GB RAM)
# Using t3.large for secondary region (2 vCPUs, 8 GB RAM)
jeddah_node_instance_type = "t3.large"
jeddah_min_nodes          = 2   # الحد الأدنى
jeddah_max_nodes          = 8   # للتوسع عند الحاجة
jeddah_desired_nodes      = 3   # العدد الابتدائي

# قاعدة البيانات RDS - RDS Database
# استخدام db.r6g.large للمنطقة الثانوية (2 vCPUs، 16 GB RAM)
# Using db.r6g.large for secondary region (2 vCPUs, 16 GB RAM)
jeddah_db_instance_class     = "db.r6g.large"
jeddah_db_allocated_storage  = 300  # 300 GB للنسخة الاحتياطية

# Redis Cache
# استخدام cache.r6g.large
# Using cache.r6g.large
jeddah_redis_node_type    = "cache.r6g.large"
jeddah_redis_num_nodes    = 2  # عقدتان للتوفر

# ======================================================================
# ملاحظات التكوين (Configuration Notes)
# ======================================================================
#
# 1. أحجام المثيلات (Instance Sizes):
#    - الرياض (Primary): موارد أكبر للتعامل مع الحمل الرئيسي
#    - جدة (Secondary): موارد أقل للنسخ الاحتياطي والتوزيع الجغرافي
#
# 2. التكلفة المتوقعة الشهرية (Estimated Monthly Cost):
#    - الرياض: ~$1,500 - $2,000 (حسب الاستخدام)
#    - جدة: ~$800 - $1,200 (حسب الاستخدام)
#    - الإجمالي: ~$2,300 - $3,200 شهرياً
#
# 3. التخزين (Storage):
#    - RDS: 500GB (الرياض) + 300GB (جدة) = 800GB إجمالي
#    - S3: حسب الاستخدام (الدفع مقابل ما تستخدمه)
#
# 4. التوفر العالي (High Availability):
#    - Multi-AZ مُفعّل لكل من RDS و Redis
#    - EKS موزّع على 3 مناطق توفر
#    - النسخ المتماثل بين المناطق للصور الفضائية
#
# 5. الأمان (Security):
#    - تشفير شامل لكل البيانات (في حالة السكون والحركة)
#    - مفاتيح KMS منفصلة لكل خدمة
#    - شبكات خاصة للبيانات الحساسة
#    - Multi-AZ للنسخ الاحتياطي
#
# 6. للاستخدام (Usage):
#    terraform plan -var-file="environments/production.tfvars"
#    terraform apply -var-file="environments/production.tfvars"
#
# ======================================================================
