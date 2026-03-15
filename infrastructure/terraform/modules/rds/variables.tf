# ======================================================================
# متغيرات وحدة قاعدة بيانات RDS PostgreSQL
# RDS PostgreSQL Database Module Variables
# ======================================================================

# ======================================================================
# المتغيرات الأساسية (Basic Variables)
# ======================================================================
variable "environment" {
  description = "البيئة (production, staging, development) / Environment"
  type        = string

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

# ======================================================================
# متغيرات الشبكة (Network Variables)
# ======================================================================
variable "vpc_id" {
  description = "معرّف VPC لنشر قاعدة البيانات / VPC ID for deploying the database"
  type        = string
}

variable "database_subnet_ids" {
  description = "قائمة معرّفات شبكات قواعد البيانات / List of database subnet IDs"
  type        = list(string)

  validation {
    condition     = length(var.database_subnet_ids) >= 2
    error_message = "At least 2 database subnets are required for Multi-AZ."
  }
}

variable "allowed_security_group_ids" {
  description = "قائمة معرّفات مجموعات الأمان المسموح بها للوصول / List of security group IDs allowed to access the database"
  type        = list(string)
  default     = []
}

variable "allowed_cidr_blocks" {
  description = "قائمة نطاقات CIDR المسموح بها للوصول / List of CIDR blocks allowed to access the database"
  type        = list(string)
  default     = []
}

# ======================================================================
# متغيرات المحرك (Engine Variables)
# ======================================================================
variable "engine_version" {
  description = "إصدار محرك PostgreSQL / PostgreSQL engine version"
  type        = string
  default     = "16.4"

  validation {
    condition     = can(regex("^16\\.", var.engine_version))
    error_message = "Engine version must be PostgreSQL 16.x for PostGIS 3.4 support."
  }
}

# ======================================================================
# متغيرات المثيل (Instance Variables)
# ======================================================================
variable "instance_class" {
  description = "فئة مثيل RDS / RDS instance class"
  type        = string
  default     = "db.r6g.xlarge"

  validation {
    condition     = can(regex("^db\\.", var.instance_class))
    error_message = "Instance class must start with 'db.' prefix."
  }
}

variable "allocated_storage" {
  description = "مساحة التخزين المخصصة بالجيجابايت / Allocated storage in GB"
  type        = number
  default     = 100

  validation {
    condition     = var.allocated_storage >= 20
    error_message = "Allocated storage must be at least 20 GB."
  }
}

variable "max_allocated_storage" {
  description = "الحد الأقصى للتخزين التلقائي بالجيجابايت (0 لتعطيل التوسع التلقائي) / Maximum auto-scaling storage in GB (0 to disable)"
  type        = number
  default     = 1000
}

variable "storage_type" {
  description = "نوع التخزين (gp3, io1, io2) / Storage type"
  type        = string
  default     = "gp3"

  validation {
    condition     = contains(["gp3", "io1", "io2"], var.storage_type)
    error_message = "Storage type must be gp3, io1, or io2."
  }
}

variable "iops" {
  description = "عدد عمليات الإدخال/الإخراج في الثانية (لـ io1/io2 فقط) / Provisioned IOPS (for io1/io2 only)"
  type        = number
  default     = 3000
}

# ======================================================================
# متغيرات قاعدة البيانات (Database Variables)
# ======================================================================
variable "db_name" {
  description = "اسم قاعدة البيانات الافتراضية / Default database name"
  type        = string
  default     = "sahool"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_name))
    error_message = "Database name must start with a letter and contain only alphanumeric characters and underscores."
  }
}

variable "port" {
  description = "منفذ PostgreSQL / PostgreSQL port"
  type        = number
  default     = 5432
}

variable "username" {
  description = "اسم المستخدم الرئيسي / Master username"
  type        = string
  sensitive   = true
  default     = "sahool_admin"
}

variable "password" {
  description = "كلمة المرور الرئيسية / Master password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.password) >= 16
    error_message = "Database password must be at least 16 characters for security."
  }
}

# ======================================================================
# متغيرات التوفر العالي (High Availability Variables)
# ======================================================================
variable "multi_az" {
  description = "تمكين النشر متعدد المناطق / Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

# ======================================================================
# متغيرات النسخ الاحتياطي (Backup Variables)
# ======================================================================
variable "backup_retention_period" {
  description = "فترة الاحتفاظ بالنسخ الاحتياطية بالأيام / Backup retention period in days"
  type        = number
  default     = 30

  validation {
    condition     = var.backup_retention_period >= 1 && var.backup_retention_period <= 35
    error_message = "Backup retention must be between 1 and 35 days."
  }
}

variable "backup_window" {
  description = "نافذة النسخ الاحتياطي اليومية (UTC) / Daily backup window (UTC)"
  type        = string
  default     = "03:00-04:00"
}

# ======================================================================
# متغيرات الصيانة (Maintenance Variables)
# ======================================================================
variable "maintenance_window" {
  description = "نافذة الصيانة الأسبوعية (UTC) / Weekly maintenance window (UTC)"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "auto_minor_version_upgrade" {
  description = "تمكين الترقية التلقائية للإصدارات الثانوية / Enable automatic minor version upgrades"
  type        = bool
  default     = true
}

# ======================================================================
# متغيرات المراقبة (Monitoring Variables)
# ======================================================================
variable "monitoring_interval" {
  description = "فترة المراقبة المُحسّنة بالثواني (0 لتعطيل) / Enhanced monitoring interval in seconds (0 to disable)"
  type        = number
  default     = 60

  validation {
    condition     = contains([0, 1, 5, 10, 15, 30, 60], var.monitoring_interval)
    error_message = "Monitoring interval must be 0, 1, 5, 10, 15, 30, or 60."
  }
}

variable "performance_insights_enabled" {
  description = "تمكين تحليل الأداء / Enable Performance Insights"
  type        = bool
  default     = true
}

variable "performance_insights_retention_days" {
  description = "مدة الاحتفاظ ببيانات تحليل الأداء بالأيام / Performance Insights retention in days"
  type        = number
  default     = 7

  validation {
    condition     = contains([7, 31, 62, 93, 124, 155, 186, 217, 248, 279, 310, 341, 372, 403, 434, 465, 496, 527, 558, 589, 620, 651, 682, 713, 731], var.performance_insights_retention_days)
    error_message = "Performance Insights retention must be 7 (free tier) or a valid paid tier value."
  }
}

variable "cloudwatch_log_exports" {
  description = "قائمة سجلات PostgreSQL للتصدير إلى CloudWatch / List of PostgreSQL logs to export to CloudWatch"
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

# ======================================================================
# متغيرات الحماية (Protection Variables)
# ======================================================================
variable "deletion_protection" {
  description = "تمكين الحماية من الحذف / Enable deletion protection"
  type        = bool
  default     = true
}

# ======================================================================
# متغيرات معلمات PostgreSQL (PostgreSQL Parameter Variables)
# ======================================================================
variable "log_min_duration_ms" {
  description = "الحد الأدنى لمدة الاستعلام للتسجيل بالميلي ثانية / Minimum query duration for logging in ms"
  type        = string
  default     = "1000"
}

variable "work_mem_kb" {
  description = "ذاكرة العمل لكل عملية فرز بالكيلوبايت / Work memory per sort operation in KB"
  type        = string
  default     = "65536"
}

variable "maintenance_work_mem_kb" {
  description = "ذاكرة العمل لعمليات الصيانة بالكيلوبايت / Maintenance work memory in KB"
  type        = string
  default     = "524288"
}

variable "effective_cache_size_kb" {
  description = "تقدير حجم ذاكرة التخزين المؤقت الفعالة بالكيلوبايت / Effective cache size estimate in KB"
  type        = string
  default     = "6291456"
}

# ======================================================================
# متغيرات النسخة المتماثلة (Read Replica Variables)
# ======================================================================
variable "create_read_replica" {
  description = "إنشاء نسخة قراءة / Create a read replica"
  type        = bool
  default     = false
}

variable "replica_instance_class" {
  description = "فئة مثيل نسخة القراءة (فارغ لاستخدام نفس الفئة الرئيسية) / Read replica instance class (empty for same as primary)"
  type        = string
  default     = ""
}

# ======================================================================
# متغيرات التشفير (Encryption Variables)
# ======================================================================
variable "kms_deletion_window_days" {
  description = "فترة انتظار حذف مفتاح KMS بالأيام / KMS key deletion window in days"
  type        = number
  default     = 10
}

# ======================================================================
# متغيرات التنبيهات (Alarm Variables)
# ======================================================================
variable "create_cloudwatch_alarms" {
  description = "إنشاء تنبيهات CloudWatch لقاعدة البيانات / Create CloudWatch alarms for the database"
  type        = bool
  default     = true
}

variable "alarm_sns_topic_arns" {
  description = "قائمة ARNs لمواضيع SNS لإرسال التنبيهات / List of SNS topic ARNs for sending alarms"
  type        = list(string)
  default     = []
}

variable "max_connections_alarm_threshold" {
  description = "حد التنبيه لعدد الاتصالات / Connection count alarm threshold"
  type        = number
  default     = 200
}

# ======================================================================
# متغيرات مصادقة IAM (IAM Authentication Variables)
# ======================================================================
variable "enable_iam_auth" {
  description = "تمكين مصادقة IAM لقاعدة البيانات / Enable IAM database authentication"
  type        = bool
  default     = true
}

# ======================================================================
# العلامات (Tags)
# ======================================================================
variable "tags" {
  description = "علامات إضافية للموارد / Additional tags for resources"
  type        = map(string)
  default     = {}
}
