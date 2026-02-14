# ======================================================================
# متغيرات وحدة ElastiCache Redis
# ElastiCache Redis Module Variables
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
  description = "معرّف VPC لنشر مجموعة Redis / VPC ID for deploying the Redis cluster"
  type        = string
}

variable "subnet_ids" {
  description = "قائمة معرّفات الشبكات الفرعية لمجموعة Redis / List of subnet IDs for the Redis cluster"
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "At least 2 subnets are required for high availability."
  }
}

variable "allowed_security_group_ids" {
  description = "قائمة معرّفات مجموعات الأمان المسموح بها / List of allowed security group IDs"
  type        = list(string)
  default     = []
}

variable "allowed_cidr_blocks" {
  description = "قائمة نطاقات CIDR المسموح بها / List of allowed CIDR blocks"
  type        = list(string)
  default     = []
}

# ======================================================================
# متغيرات المحرك (Engine Variables)
# ======================================================================
variable "engine_version" {
  description = "إصدار محرك Redis / Redis engine version"
  type        = string
  default     = "7.1"
}

variable "node_type" {
  description = "نوع عقدة ElastiCache / ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"

  validation {
    condition     = can(regex("^cache\\.", var.node_type))
    error_message = "Node type must start with 'cache.' prefix."
  }
}

variable "port" {
  description = "منفذ Redis / Redis port"
  type        = number
  default     = 6379
}

variable "num_cache_nodes" {
  description = "عدد عقد التخزين المؤقت (1 = بدون نسخ متماثل، 2+ = مع نسخ متماثل) / Number of cache nodes"
  type        = number
  default     = 3

  validation {
    condition     = var.num_cache_nodes >= 1 && var.num_cache_nodes <= 6
    error_message = "Number of cache nodes must be between 1 and 6."
  }
}

# ======================================================================
# متغيرات المصادقة (Authentication Variables)
# ======================================================================
variable "auth_token" {
  description = "رمز مصادقة Redis (فارغ لتوليد تلقائي) / Redis auth token (empty to auto-generate)"
  type        = string
  sensitive   = true
  default     = ""
}

# ======================================================================
# متغيرات معلمات Redis (Redis Parameter Variables)
# ======================================================================
variable "maxmemory_policy" {
  description = "سياسة إدارة الذاكرة عند الامتلاء / Memory management policy when full"
  type        = string
  default     = "allkeys-lru"

  validation {
    condition = contains([
      "volatile-lru", "allkeys-lru", "volatile-lfu", "allkeys-lfu",
      "volatile-random", "allkeys-random", "volatile-ttl", "noeviction"
    ], var.maxmemory_policy)
    error_message = "Must be a valid Redis maxmemory-policy."
  }
}

variable "notify_keyspace_events" {
  description = "أحداث مساحة المفاتيح للإشعارات / Keyspace notification events"
  type        = string
  default     = "Ex"
}

variable "connection_timeout" {
  description = "مهلة اتصال Redis بالثواني (0 = بدون مهلة) / Redis connection timeout in seconds (0 = no timeout)"
  type        = string
  default     = "300"
}

# ======================================================================
# متغيرات النسخ الاحتياطي (Backup Variables)
# ======================================================================
variable "snapshot_retention_limit" {
  description = "عدد اللقطات اليومية المحتفظ بها / Number of daily snapshots retained"
  type        = number
  default     = 5

  validation {
    condition     = var.snapshot_retention_limit >= 0 && var.snapshot_retention_limit <= 35
    error_message = "Snapshot retention must be between 0 and 35."
  }
}

variable "snapshot_window" {
  description = "نافذة اللقطة اليومية (UTC) / Daily snapshot window (UTC)"
  type        = string
  default     = "03:00-05:00"
}

# ======================================================================
# متغيرات الصيانة (Maintenance Variables)
# ======================================================================
variable "maintenance_window" {
  description = "نافذة الصيانة الأسبوعية (UTC) / Weekly maintenance window (UTC)"
  type        = string
  default     = "sun:05:00-sun:07:00"
}

variable "auto_minor_version_upgrade" {
  description = "تمكين الترقية التلقائية للإصدارات الثانوية / Enable automatic minor version upgrades"
  type        = bool
  default     = true
}

# ======================================================================
# متغيرات الإشعارات (Notification Variables)
# ======================================================================
variable "notification_topic_arn" {
  description = "ARN لموضوع SNS للإشعارات / SNS topic ARN for notifications"
  type        = string
  default     = null
}

# ======================================================================
# متغيرات التنبيهات (Alarm Variables)
# ======================================================================
variable "create_cloudwatch_alarms" {
  description = "إنشاء تنبيهات CloudWatch لـ Redis / Create CloudWatch alarms for Redis"
  type        = bool
  default     = true
}

variable "alarm_sns_topic_arns" {
  description = "قائمة ARNs لمواضيع SNS لإرسال التنبيهات / List of SNS topic ARNs for sending alarms"
  type        = list(string)
  default     = []
}

# ======================================================================
# العلامات (Tags)
# ======================================================================
variable "tags" {
  description = "علامات إضافية للموارد / Additional tags for resources"
  type        = map(string)
  default     = {}
}
