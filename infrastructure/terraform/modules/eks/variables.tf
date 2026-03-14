# ======================================================================
# متغيرات وحدة مجموعة EKS Kubernetes
# EKS Kubernetes Cluster Module Variables
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

variable "cluster_name" {
  description = "اسم مجموعة EKS / EKS cluster name"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]*$", var.cluster_name))
    error_message = "Cluster name must start with a letter and contain only alphanumeric characters and hyphens."
  }
}

variable "kubernetes_version" {
  description = "إصدار Kubernetes لمجموعة EKS / Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"

  validation {
    condition     = can(regex("^1\\.(2[5-9]|[3-9][0-9])$", var.kubernetes_version))
    error_message = "Kubernetes version must be 1.25 or later."
  }
}

# ======================================================================
# متغيرات الشبكة (Network Variables)
# ======================================================================
variable "vpc_id" {
  description = "معرّف VPC لنشر مجموعة EKS / VPC ID for deploying the EKS cluster"
  type        = string
}

variable "private_subnet_ids" {
  description = "قائمة معرّفات الشبكات الفرعية الخاصة لعقد EKS / List of private subnet IDs for EKS nodes"
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least 2 private subnets are required."
  }
}

variable "public_subnet_ids" {
  description = "قائمة معرّفات الشبكات الفرعية العامة لموازن التحميل / List of public subnet IDs for load balancers"
  type        = list(string)
  default     = []
}

# ======================================================================
# متغيرات الوصول (Access Variables)
# ======================================================================
variable "endpoint_public_access" {
  description = "تمكين الوصول العام لنقطة نهاية API / Enable public access to API endpoint"
  type        = bool
  default     = true
}

variable "public_access_cidrs" {
  description = "قائمة نطاقات CIDR المسموح بها للوصول العام / List of CIDR blocks allowed for public access. Must be explicitly configured - no default provided for security."
  type        = list(string)
  # SECURITY: No default CIDR provided. You MUST explicitly set allowed CIDRs.
  # Example: ["10.0.0.0/8", "192.168.1.0/24"] or your office/VPN IP ranges.
  # NEVER use ["0.0.0.0/0"] in production.
  default     = []

  validation {
    condition     = !var.endpoint_public_access || length(var.public_access_cidrs) > 0
    error_message = "public_access_cidrs must be explicitly configured with allowed CIDR blocks when endpoint_public_access is true. Do not use 0.0.0.0/0 in production."
  }
}

# ======================================================================
# متغيرات التسجيل (Logging Variables)
# ======================================================================
variable "cluster_log_types" {
  description = "أنواع سجلات المجموعة المُمكّنة / Enabled cluster log types"
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}

variable "cluster_log_retention_days" {
  description = "مدة الاحتفاظ بسجلات المجموعة بالأيام / Cluster log retention period in days"
  type        = number
  default     = 30
}

# ======================================================================
# متغيرات مجموعة عقد النظام (System Node Group Variables)
# ======================================================================
variable "system_node_instance_types" {
  description = "أنواع مثيلات عقد النظام / System node instance types"
  type        = list(string)
  default     = ["t3.large"]
}

variable "system_node_min_size" {
  description = "الحد الأدنى لعدد عقد النظام / Minimum number of system nodes"
  type        = number
  default     = 2

  validation {
    condition     = var.system_node_min_size >= 1
    error_message = "Minimum system nodes must be at least 1."
  }
}

variable "system_node_max_size" {
  description = "الحد الأقصى لعدد عقد النظام / Maximum number of system nodes"
  type        = number
  default     = 4
}

variable "system_node_desired_size" {
  description = "العدد المطلوب من عقد النظام / Desired number of system nodes"
  type        = number
  default     = 2
}

# ======================================================================
# متغيرات مجموعة عقد العمال (Worker Node Group Variables)
# ======================================================================
variable "worker_node_instance_types" {
  description = "أنواع مثيلات عقد العمال / Worker node instance types"
  type        = list(string)
  default     = ["t3.xlarge"]
}

variable "worker_node_min_size" {
  description = "الحد الأدنى لعدد عقد العمال / Minimum number of worker nodes"
  type        = number
  default     = 3

  validation {
    condition     = var.worker_node_min_size >= 1
    error_message = "Minimum worker nodes must be at least 1."
  }
}

variable "worker_node_max_size" {
  description = "الحد الأقصى لعدد عقد العمال / Maximum number of worker nodes"
  type        = number
  default     = 10
}

variable "worker_node_desired_size" {
  description = "العدد المطلوب من عقد العمال / Desired number of worker nodes"
  type        = number
  default     = 5
}

variable "worker_capacity_type" {
  description = "نوع سعة عقد العمال (ON_DEMAND أو SPOT) / Worker node capacity type"
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.worker_capacity_type)
    error_message = "Worker capacity type must be ON_DEMAND or SPOT."
  }
}

# ======================================================================
# متغيرات مجموعة عقد GPU (GPU Node Group Variables)
# ======================================================================
variable "enable_gpu_nodes" {
  description = "تمكين مجموعة عقد GPU لخدمات الرؤية الحاسوبية / Enable GPU node group for vision services"
  type        = bool
  default     = true
}

variable "gpu_node_instance_types" {
  description = "أنواع مثيلات عقد GPU (g4dn للاستدلال, p3 للتدريب) / GPU node instance types"
  type        = list(string)
  default     = ["g4dn.xlarge"]
}

variable "gpu_node_min_size" {
  description = "الحد الأدنى لعدد عقد GPU / Minimum number of GPU nodes"
  type        = number
  default     = 0
}

variable "gpu_node_max_size" {
  description = "الحد الأقصى لعدد عقد GPU / Maximum number of GPU nodes"
  type        = number
  default     = 4
}

variable "gpu_node_desired_size" {
  description = "العدد المطلوب من عقد GPU / Desired number of GPU nodes"
  type        = number
  default     = 1
}

variable "gpu_capacity_type" {
  description = "نوع سعة عقد GPU (ON_DEMAND أو SPOT) / GPU node capacity type"
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.gpu_capacity_type)
    error_message = "GPU capacity type must be ON_DEMAND or SPOT."
  }
}

# ======================================================================
# إضافات EKS (EKS Addons)
# ======================================================================
variable "enable_ebs_csi_driver" {
  description = "تمكين سائق EBS CSI للتخزين الدائم / Enable EBS CSI driver for persistent volumes"
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
