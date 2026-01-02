# ======================================================================
# مخرجات البنية التحتية الرئيسية لمنصة صحول
# Main Infrastructure Outputs for Sahool Platform
# ======================================================================
# هذا الملف يحتوي على جميع المخرجات الهامة من البنية التحتية متعددة المناطق
# This file contains all important outputs from the multi-region infrastructure
# ======================================================================

# ======================================================================
# معلومات عامة (General Information)
# ======================================================================
output "environment" {
  description = "البيئة الحالية / Current environment"
  value       = var.environment
}

output "primary_region" {
  description = "المنطقة الرئيسية / Primary region"
  value       = var.primary_region
}

output "secondary_region" {
  description = "المنطقة الثانوية / Secondary region"
  value       = var.secondary_region
}

# ======================================================================
# مخرجات منطقة الرياض (Riyadh Region Outputs)
# ======================================================================
output "riyadh_vpc_id" {
  description = "معرّف VPC في الرياض / Riyadh VPC ID"
  value       = module.riyadh_region.vpc_id
}

output "riyadh_vpc_cidr" {
  description = "نطاق CIDR للشبكة في الرياض / Riyadh VPC CIDR"
  value       = module.riyadh_region.vpc_cidr
}

# EKS Cluster - الرياض
output "riyadh_eks_cluster_name" {
  description = "اسم مجموعة EKS في الرياض / Riyadh EKS cluster name"
  value       = module.riyadh_region.eks_cluster_name
}

output "riyadh_eks_cluster_endpoint" {
  description = "نقطة نهاية مجموعة EKS في الرياض / Riyadh EKS cluster endpoint"
  value       = module.riyadh_region.eks_cluster_endpoint
}

output "riyadh_eks_cluster_version" {
  description = "إصدار Kubernetes في الرياض / Riyadh Kubernetes version"
  value       = module.riyadh_region.eks_cluster_version
}

output "riyadh_eks_cluster_certificate_authority" {
  description = "شهادة CA لمجموعة EKS في الرياض / Riyadh EKS cluster CA certificate"
  value       = module.riyadh_region.eks_cluster_certificate_authority
  sensitive   = true
}

# RDS Database - الرياض
output "riyadh_rds_endpoint" {
  description = "نقطة نهاية قاعدة البيانات في الرياض / Riyadh RDS endpoint"
  value       = module.riyadh_region.rds_endpoint
}

output "riyadh_rds_address" {
  description = "عنوان قاعدة البيانات في الرياض / Riyadh RDS address"
  value       = module.riyadh_region.rds_address
}

output "riyadh_rds_port" {
  description = "منفذ قاعدة البيانات في الرياض / Riyadh RDS port"
  value       = module.riyadh_region.rds_port
}

output "riyadh_rds_database_name" {
  description = "اسم قاعدة البيانات في الرياض / Riyadh database name"
  value       = module.riyadh_region.rds_database_name
}

# Redis - الرياض
output "riyadh_redis_endpoint" {
  description = "نقطة نهاية Redis في الرياض / Riyadh Redis endpoint"
  value       = module.riyadh_region.redis_endpoint
}

output "riyadh_redis_port" {
  description = "منفذ Redis في الرياض / Riyadh Redis port"
  value       = module.riyadh_region.redis_port
}

# S3 Buckets - الرياض
output "riyadh_satellite_bucket_name" {
  description = "اسم حاوية الصور الفضائية في الرياض / Riyadh satellite imagery bucket name"
  value       = module.riyadh_region.satellite_bucket_name
}

output "riyadh_model_bucket_name" {
  description = "اسم حاوية النماذج في الرياض / Riyadh AI models bucket name"
  value       = module.riyadh_region.model_bucket_name
}

# ======================================================================
# مخرجات منطقة جدة (Jeddah Region Outputs)
# ======================================================================
output "jeddah_vpc_id" {
  description = "معرّف VPC في جدة / Jeddah VPC ID"
  value       = module.jeddah_region.vpc_id
}

output "jeddah_vpc_cidr" {
  description = "نطاق CIDR للشبكة في جدة / Jeddah VPC CIDR"
  value       = module.jeddah_region.vpc_cidr
}

# EKS Cluster - جدة
output "jeddah_eks_cluster_name" {
  description = "اسم مجموعة EKS في جدة / Jeddah EKS cluster name"
  value       = module.jeddah_region.eks_cluster_name
}

output "jeddah_eks_cluster_endpoint" {
  description = "نقطة نهاية مجموعة EKS في جدة / Jeddah EKS cluster endpoint"
  value       = module.jeddah_region.eks_cluster_endpoint
}

output "jeddah_eks_cluster_version" {
  description = "إصدار Kubernetes في جدة / Jeddah Kubernetes version"
  value       = module.jeddah_region.eks_cluster_version
}

output "jeddah_eks_cluster_certificate_authority" {
  description = "شهادة CA لمجموعة EKS في جدة / Jeddah EKS cluster CA certificate"
  value       = module.jeddah_region.eks_cluster_certificate_authority
  sensitive   = true
}

# RDS Database - جدة
output "jeddah_rds_endpoint" {
  description = "نقطة نهاية قاعدة البيانات في جدة / Jeddah RDS endpoint"
  value       = module.jeddah_region.rds_endpoint
}

output "jeddah_rds_address" {
  description = "عنوان قاعدة البيانات في جدة / Jeddah RDS address"
  value       = module.jeddah_region.rds_address
}

output "jeddah_rds_port" {
  description = "منفذ قاعدة البيانات في جدة / Jeddah RDS port"
  value       = module.jeddah_region.rds_port
}

output "jeddah_rds_database_name" {
  description = "اسم قاعدة البيانات في جدة / Jeddah database name"
  value       = module.jeddah_region.rds_database_name
}

# Redis - جدة
output "jeddah_redis_endpoint" {
  description = "نقطة نهاية Redis في جدة / Jeddah Redis endpoint"
  value       = module.jeddah_region.redis_endpoint
}

output "jeddah_redis_port" {
  description = "منفذ Redis في جدة / Jeddah Redis port"
  value       = module.jeddah_region.redis_port
}

# S3 Buckets - جدة
output "jeddah_satellite_bucket_name" {
  description = "اسم حاوية الصور الفضائية في جدة / Jeddah satellite imagery bucket name"
  value       = module.jeddah_region.satellite_bucket_name
}

output "jeddah_model_bucket_name" {
  description = "اسم حاوية النماذج في جدة / Jeddah AI models bucket name"
  value       = module.jeddah_region.model_bucket_name
}

# ======================================================================
# معلومات الاتصال بين المناطق (Cross-Region Connectivity)
# ======================================================================
output "vpc_peering_connection_id" {
  description = "معرّف اتصال VPC Peering بين الرياض وجدة / VPC Peering connection ID between Riyadh and Jeddah"
  value       = aws_vpc_peering_connection.riyadh_jeddah.id
}

output "vpc_peering_status" {
  description = "حالة اتصال VPC Peering / VPC Peering connection status"
  value       = aws_vpc_peering_connection.riyadh_jeddah.accept_status
}

# ======================================================================
# تعليمات الاتصال بمجموعات EKS
# Instructions for Connecting to EKS Clusters
# ======================================================================
output "kubectl_config_riyadh" {
  description = "أمر للاتصال بمجموعة EKS في الرياض / Command to connect to Riyadh EKS cluster"
  value       = "aws eks update-kubeconfig --region ${var.primary_region} --name ${module.riyadh_region.eks_cluster_name}"
}

output "kubectl_config_jeddah" {
  description = "أمر للاتصال بمجموعة EKS في جدة / Command to connect to Jeddah EKS cluster"
  value       = "aws eks update-kubeconfig --region ${var.secondary_region} --name ${module.jeddah_region.eks_cluster_name}"
}

# ======================================================================
# معلومات الاتصال بقواعد البيانات
# Database Connection Information
# ======================================================================
output "database_connection_info" {
  description = "معلومات الاتصال بقواعد البيانات / Database connection information"
  value = {
    riyadh = {
      host     = module.riyadh_region.rds_address
      port     = module.riyadh_region.rds_port
      database = module.riyadh_region.rds_database_name
      # ملاحظة: اسم المستخدم وكلمة المرور يتم تخزينهما في AWS Secrets Manager
      # Note: Username and password are stored in AWS Secrets Manager
    }
    jeddah = {
      host     = module.jeddah_region.rds_address
      port     = module.jeddah_region.rds_port
      database = module.jeddah_region.rds_database_name
    }
  }
  sensitive = true
}

# ======================================================================
# جميع أسماء حاويات S3 (All S3 Bucket Names)
# ======================================================================
output "all_s3_buckets" {
  description = "قائمة بجميع حاويات S3 / List of all S3 buckets"
  value = {
    riyadh = {
      satellite_imagery = module.riyadh_region.satellite_bucket_name
      ai_models        = module.riyadh_region.model_bucket_name
    }
    jeddah = {
      satellite_imagery = module.jeddah_region.satellite_bucket_name
      ai_models        = module.jeddah_region.model_bucket_name
    }
  }
}

# ======================================================================
# ملخص البنية التحتية (Infrastructure Summary)
# ======================================================================
output "infrastructure_summary" {
  description = "ملخص البنية التحتية الكاملة / Complete infrastructure summary"
  value = {
    environment = var.environment
    regions = {
      riyadh = {
        name               = "الرياض (Primary)"
        vpc_cidr          = module.riyadh_region.vpc_cidr
        eks_cluster       = module.riyadh_region.eks_cluster_name
        eks_endpoint      = module.riyadh_region.eks_cluster_endpoint
        database_endpoint = module.riyadh_region.rds_endpoint
        redis_endpoint    = module.riyadh_region.redis_endpoint
      }
      jeddah = {
        name               = "جدة (Secondary)"
        vpc_cidr          = module.jeddah_region.vpc_cidr
        eks_cluster       = module.jeddah_region.eks_cluster_name
        eks_endpoint      = module.jeddah_region.eks_cluster_endpoint
        database_endpoint = module.jeddah_region.rds_endpoint
        redis_endpoint    = module.jeddah_region.redis_endpoint
      }
    }
    cross_region = {
      vpc_peering_id     = aws_vpc_peering_connection.riyadh_jeddah.id
      s3_replication     = "Enabled from Riyadh to Jeddah"
    }
  }
}

# ======================================================================
# تعليمات النشر (Deployment Instructions)
# ======================================================================
output "deployment_instructions" {
  description = "تعليمات النشر والاستخدام / Deployment and usage instructions"
  value = <<-EOT
    ===================================================================
    مرحباً بك في البنية التحتية لمنصة صحول - المملكة العربية السعودية
    Welcome to Sahool Platform Infrastructure - Saudi Arabia
    ===================================================================

    المناطق المنشورة / Deployed Regions:
    ----------------------------------
    1. الرياض (Primary)   - ${module.riyadh_region.eks_cluster_name}
    2. جدة (Secondary)    - ${module.jeddah_region.eks_cluster_name}

    للاتصال بمجموعات Kubernetes:
    To connect to Kubernetes clusters:
    ----------------------------------
    الرياض: aws eks update-kubeconfig --region ${var.primary_region} --name ${module.riyadh_region.eks_cluster_name}
    جدة:   aws eks update-kubeconfig --region ${var.secondary_region} --name ${module.jeddah_region.eks_cluster_name}

    قواعد البيانات / Databases:
    ---------------------------
    الرياض: ${module.riyadh_region.rds_endpoint}
    جدة:   ${module.jeddah_region.rds_endpoint}

    حاويات S3 للصور الفضائية / Satellite Imagery S3 Buckets:
    ------------------------------------------------------
    الرياض: ${module.riyadh_region.satellite_bucket_name}
    جدة:   ${module.jeddah_region.satellite_bucket_name}

    ملاحظة: النسخ المتماثل التلقائي مُفعّل من الرياض إلى جدة
    Note: Automatic replication enabled from Riyadh to Jeddah

    ===================================================================
  EOT
}
