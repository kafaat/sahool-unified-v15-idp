# ======================================================================
# متغيرات وحدة الشبكة الافتراضية الخاصة
# VPC Module Variables
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

variable "region_name" {
  description = "اسم المنطقة المنطقي (مثل: riyadh, jeddah) / Logical region name (e.g., riyadh, jeddah)"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*$", var.region_name))
    error_message = "Region name must start with a letter and contain only lowercase letters, numbers, and hyphens."
  }
}

variable "aws_region" {
  description = "منطقة AWS (مثل: me-south-1) / AWS region (e.g., me-south-1)"
  type        = string
  default     = "me-south-1"
}

# ======================================================================
# متغيرات الشبكة (Network Variables)
# ======================================================================
variable "cidr_block" {
  description = "نطاق CIDR الرئيسي للشبكة الافتراضية / Primary CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "CIDR block must be a valid IPv4 CIDR notation."
  }
}

variable "availability_zones" {
  description = "قائمة مناطق التوفر لتوزيع الموارد / List of availability zones for resource distribution"
  type        = list(string)
  default     = ["me-south-1a", "me-south-1b", "me-south-1c"]

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 availability zones are required for high availability."
  }
}

variable "subnet_newbits" {
  description = "عدد البتات الإضافية لحساب CIDR الشبكات الفرعية / Number of additional bits for subnet CIDR calculation"
  type        = number
  default     = 4

  validation {
    condition     = var.subnet_newbits >= 2 && var.subnet_newbits <= 12
    error_message = "Subnet newbits must be between 2 and 12."
  }
}

variable "enable_ipv6" {
  description = "تمكين IPv6 في الشبكة الافتراضية / Enable IPv6 in VPC"
  type        = bool
  default     = false
}

# ======================================================================
# متغيرات NAT Gateway
# ======================================================================
variable "single_nat_gateway" {
  description = "استخدام بوابة NAT واحدة بدلاً من واحدة لكل منطقة توفر (توفير التكلفة) / Use single NAT gateway instead of one per AZ (cost saving)"
  type        = bool
  default     = false
}

# ======================================================================
# متغيرات نقاط نهاية VPC (VPC Endpoints)
# ======================================================================
variable "enable_vpc_endpoints" {
  description = "تمكين نقاط نهاية VPC لخدمات AWS (S3, ECR, STS, Logs) / Enable VPC endpoints for AWS services"
  type        = bool
  default     = true
}

# ======================================================================
# متغيرات سجلات التدفق (Flow Logs)
# ======================================================================
variable "enable_flow_logs" {
  description = "تمكين سجلات تدفق VPC للمراقبة الأمنية / Enable VPC flow logs for security monitoring"
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "مدة الاحتفاظ بسجلات التدفق بالأيام / Flow logs retention period in days"
  type        = number
  default     = 30

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653], var.flow_logs_retention_days)
    error_message = "Flow logs retention must be a valid CloudWatch retention value."
  }
}

# ======================================================================
# متغيرات Kubernetes (Kubernetes Variables)
# ======================================================================
variable "eks_cluster_name" {
  description = "اسم مجموعة EKS لوضع علامات على الشبكات الفرعية / EKS cluster name for subnet tagging"
  type        = string
  default     = ""
}

# ======================================================================
# العلامات (Tags)
# ======================================================================
variable "tags" {
  description = "علامات إضافية للموارد / Additional tags for resources"
  type        = map(string)
  default     = {}
}
