# ======================================================================
# متغيرات البنية التحتية الرئيسية لمنصة صحول
# Main Infrastructure Variables for Sahool Platform
# ======================================================================

# ======================================================================
# المتغيرات العامة (General Variables)
# ======================================================================
variable "environment" {
  description = "البيئة (production, staging, development) / Environment"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "primary_region" {
  description = "المنطقة الرئيسية AWS (البحرين - الأقرب للسعودية) / Primary AWS region"
  type        = string
  default     = "me-south-1"
}

variable "secondary_region" {
  description = "المنطقة الثانوية AWS / Secondary AWS region"
  type        = string
  default     = "me-south-1"
}

variable "eks_cluster_version" {
  description = "إصدار Kubernetes لمجموعات EKS / EKS Kubernetes version"
  type        = string
  default     = "1.28"
}

# ======================================================================
# بيانات اعتماد قاعدة البيانات (Database Credentials)
# ======================================================================
variable "db_username" {
  description = "اسم مستخدم قاعدة البيانات الرئيسية / Master database username"
  type        = string
  sensitive   = true
  default     = "sahool_admin"
}

variable "db_password" {
  description = "كلمة مرور قاعدة البيانات الرئيسية / Master database password"
  type        = string
  sensitive   = true
}

# ======================================================================
# متغيرات منطقة الرياض (Riyadh Region Variables)
# ======================================================================
variable "riyadh_vpc_cidr" {
  description = "CIDR للشبكة الافتراضية في الرياض / VPC CIDR for Riyadh"
  type        = string
  default     = "10.0.0.0/16"
}

variable "riyadh_node_instance_type" {
  description = "نوع مثيل عقد EKS في الرياض / EKS node instance type for Riyadh"
  type        = string
  default     = "t3.xlarge"
}

variable "riyadh_min_nodes" {
  description = "الحد الأدنى لعدد العقد في الرياض / Minimum number of nodes in Riyadh"
  type        = number
  default     = 3
}

variable "riyadh_max_nodes" {
  description = "الحد الأقصى لعدد العقد في الرياض / Maximum number of nodes in Riyadh"
  type        = number
  default     = 10
}

variable "riyadh_desired_nodes" {
  description = "العدد المطلوب من العقد في الرياض / Desired number of nodes in Riyadh"
  type        = number
  default     = 5
}

variable "riyadh_db_instance_class" {
  description = "فئة مثيل RDS في الرياض / RDS instance class for Riyadh"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "riyadh_db_allocated_storage" {
  description = "مساحة التخزين المخصصة لقاعدة البيانات في الرياض (GB) / Allocated storage for database in Riyadh"
  type        = number
  default     = 500
}

variable "riyadh_redis_node_type" {
  description = "نوع عقدة Redis في الرياض / Redis node type for Riyadh"
  type        = string
  default     = "cache.r6g.large"
}

variable "riyadh_redis_num_nodes" {
  description = "عدد عقد Redis في الرياض / Number of Redis nodes in Riyadh"
  type        = number
  default     = 3
}

# ======================================================================
# متغيرات منطقة جدة (Jeddah Region Variables)
# ======================================================================
variable "jeddah_vpc_cidr" {
  description = "CIDR للشبكة الافتراضية في جدة / VPC CIDR for Jeddah"
  type        = string
  default     = "10.1.0.0/16"
}

variable "jeddah_node_instance_type" {
  description = "نوع مثيل عقد EKS في جدة / EKS node instance type for Jeddah"
  type        = string
  default     = "t3.large"
}

variable "jeddah_min_nodes" {
  description = "الحد الأدنى لعدد العقد في جدة / Minimum number of nodes in Jeddah"
  type        = number
  default     = 2
}

variable "jeddah_max_nodes" {
  description = "الحد الأقصى لعدد العقد في جدة / Maximum number of nodes in Jeddah"
  type        = number
  default     = 8
}

variable "jeddah_desired_nodes" {
  description = "العدد المطلوب من العقد في جدة / Desired number of nodes in Jeddah"
  type        = number
  default     = 3
}

variable "jeddah_db_instance_class" {
  description = "فئة مثيل RDS في جدة / RDS instance class for Jeddah"
  type        = string
  default     = "db.r6g.large"
}

variable "jeddah_db_allocated_storage" {
  description = "مساحة التخزين المخصصة لقاعدة البيانات في جدة (GB) / Allocated storage for database in Jeddah"
  type        = number
  default     = 300
}

variable "jeddah_redis_node_type" {
  description = "نوع عقدة Redis في جدة / Redis node type for Jeddah"
  type        = string
  default     = "cache.r6g.large"
}

variable "jeddah_redis_num_nodes" {
  description = "عدد عقد Redis في جدة / Number of Redis nodes in Jeddah"
  type        = number
  default     = 2
}
