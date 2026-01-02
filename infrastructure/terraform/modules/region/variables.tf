# ======================================================================
# متغيرات وحدة البنية التحتية الإقليمية
# Regional Infrastructure Module Variables
# ======================================================================

# ======================================================================
# المتغيرات الأساسية (Basic Variables)
# ======================================================================
variable "region_name" {
  description = "اسم المنطقة (مثل: riyadh, jeddah) / Region name (e.g., riyadh, jeddah)"
  type        = string

  validation {
    condition     = can(regex("^[a-z]+$", var.region_name))
    error_message = "Region name must contain only lowercase letters."
  }
}

variable "aws_region" {
  description = "منطقة AWS (مثل: me-south-1) / AWS region (e.g., me-south-1)"
  type        = string
}

variable "environment" {
  description = "البيئة (production, staging, development) / Environment"
  type        = string

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "is_primary" {
  description = "هل هذه المنطقة الرئيسية؟ / Is this the primary region?"
  type        = bool
  default     = false
}

# ======================================================================
# متغيرات الشبكة (Network Variables)
# ======================================================================
variable "vpc_cidr" {
  description = "نطاق CIDR للشبكة الافتراضية / CIDR block for VPC"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "قائمة مناطق التوفر / List of availability zones"
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 availability zones are required for high availability."
  }
}

# ======================================================================
# متغيرات EKS Cluster
# ======================================================================
variable "cluster_name" {
  description = "اسم مجموعة EKS / EKS cluster name"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]*$", var.cluster_name))
    error_message = "Cluster name must start with a letter and contain only alphanumeric characters and hyphens."
  }
}

variable "cluster_version" {
  description = "إصدار Kubernetes للمجموعة / Kubernetes version for the cluster"
  type        = string
  default     = "1.28"
}

variable "node_instance_type" {
  description = "نوع مثيل عقد EKS / EKS node instance type"
  type        = string
  default     = "t3.large"

  validation {
    condition     = can(regex("^[a-z][0-9][a-z]?\\.[a-z]+$", var.node_instance_type))
    error_message = "Instance type must be a valid EC2 instance type (e.g., t3.large, m5.xlarge)."
  }
}

variable "min_nodes" {
  description = "الحد الأدنى لعدد العقد / Minimum number of nodes"
  type        = number
  default     = 2

  validation {
    condition     = var.min_nodes >= 1
    error_message = "Minimum nodes must be at least 1."
  }
}

variable "max_nodes" {
  description = "الحد الأقصى لعدد العقد / Maximum number of nodes"
  type        = number
  default     = 10

  validation {
    condition     = var.max_nodes >= 1
    error_message = "Maximum nodes must be at least 1."
  }
}

variable "desired_nodes" {
  description = "العدد المطلوب من العقد / Desired number of nodes"
  type        = number
  default     = 3

  validation {
    condition     = var.desired_nodes >= 1
    error_message = "Desired nodes must be at least 1."
  }
}

# ======================================================================
# متغيرات قاعدة البيانات RDS (RDS Database Variables)
# ======================================================================
variable "db_instance_class" {
  description = "فئة مثيل قاعدة البيانات / Database instance class"
  type        = string
  default     = "db.r6g.large"

  validation {
    condition     = can(regex("^db\\.[a-z][0-9][a-z]?\\.[a-z]+$", var.db_instance_class))
    error_message = "DB instance class must be a valid RDS instance type (e.g., db.r6g.large)."
  }
}

variable "db_allocated_storage" {
  description = "مساحة التخزين المخصصة لقاعدة البيانات بالجيجابايت / Allocated storage for database in GB"
  type        = number
  default     = 100

  validation {
    condition     = var.db_allocated_storage >= 20
    error_message = "Allocated storage must be at least 20 GB."
  }
}

variable "db_name" {
  description = "اسم قاعدة البيانات / Database name"
  type        = string
  default     = "sahool"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_name))
    error_message = "Database name must start with a letter and contain only alphanumeric characters and underscores."
  }
}

variable "db_username" {
  description = "اسم مستخدم قاعدة البيانات / Database username"
  type        = string
  sensitive   = true

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_username))
    error_message = "Database username must start with a letter and contain only alphanumeric characters and underscores."
  }
}

variable "db_password" {
  description = "كلمة مرور قاعدة البيانات / Database password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters long."
  }
}

variable "enable_multi_az" {
  description = "تمكين النشر متعدد المناطق للتوفر العالي / Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "فترة الاحتفاظ بالنسخ الاحتياطية بالأيام / Backup retention period in days"
  type        = number
  default     = 7

  validation {
    condition     = var.backup_retention_period >= 0 && var.backup_retention_period <= 35
    error_message = "Backup retention period must be between 0 and 35 days."
  }
}

# ======================================================================
# متغيرات Redis (Redis Variables)
# ======================================================================
variable "redis_node_type" {
  description = "نوع عقدة Redis / Redis node type"
  type        = string
  default     = "cache.r6g.large"

  validation {
    condition     = can(regex("^cache\\.[a-z][0-9][a-z]?\\.[a-z]+$", var.redis_node_type))
    error_message = "Redis node type must be a valid ElastiCache node type (e.g., cache.r6g.large)."
  }
}

variable "redis_num_cache_nodes" {
  description = "عدد عقد Redis / Number of Redis cache nodes"
  type        = number
  default     = 2

  validation {
    condition     = var.redis_num_cache_nodes >= 1 && var.redis_num_cache_nodes <= 6
    error_message = "Number of Redis nodes must be between 1 and 6."
  }
}

# ======================================================================
# متغيرات S3 (S3 Variables)
# ======================================================================
variable "enable_satellite_bucket" {
  description = "تمكين حاوية S3 للصور الفضائية / Enable S3 bucket for satellite imagery"
  type        = bool
  default     = true
}

variable "satellite_bucket_name" {
  description = "اسم حاوية S3 للصور الفضائية / S3 bucket name for satellite imagery"
  type        = string
  default     = "sahool-satellite-imagery"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.satellite_bucket_name))
    error_message = "S3 bucket name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "enable_model_bucket" {
  description = "تمكين حاوية S3 لنماذج الذكاء الاصطناعي / Enable S3 bucket for AI models"
  type        = bool
  default     = true
}

variable "model_bucket_name" {
  description = "اسم حاوية S3 لنماذج الذكاء الاصطناعي / S3 bucket name for AI models"
  type        = string
  default     = "sahool-ai-models"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.model_bucket_name))
    error_message = "S3 bucket name must contain only lowercase letters, numbers, and hyphens."
  }
}

# ======================================================================
# العلامات (Tags)
# ======================================================================
variable "tags" {
  description = "علامات إضافية للموارد / Additional tags for resources"
  type        = map(string)
  default     = {}
}
