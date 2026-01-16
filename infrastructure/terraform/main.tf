# ======================================================================
# البنية التحتية الرئيسية لمنصة صحول - متعدد المناطق
# Main Infrastructure for Sahool Platform - Multi-Region
# ======================================================================
# هذا الملف يحدد البنية التحتية الرئيسية لمنصة صحول في المملكة العربية السعودية
# This file defines the main infrastructure for Sahool platform in Saudi Arabia
# المناطق: الرياض (رئيسية) وجدة (ثانوية)
# Regions: Riyadh (primary) and Jeddah (secondary)
# ======================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  # تكوين التخزين الخلفي لحالة Terraform في S3
  # Backend configuration for Terraform state in S3
  backend "s3" {
    bucket         = "sahool-terraform-state"
    key            = "multi-region/terraform.tfstate"
    region         = "me-south-1"
    encrypt        = true
    dynamodb_table = "sahool-terraform-locks"

    # تفعيل التشفير والنسخ الاحتياطي
    # Enable encryption and versioning
    versioning = true
  }
}

# ======================================================================
# إعدادات AWS Provider للمنطقة الرئيسية (البحرين - الأقرب للسعودية)
# AWS Provider configuration for primary region (Bahrain - closest to Saudi Arabia)
# ======================================================================
provider "aws" {
  region = var.primary_region

  default_tags {
    tags = {
      Project     = "Sahool"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Country     = "Saudi Arabia"
      Purpose     = "Precision Agriculture Platform"
    }
  }
}

# مزود AWS للمنطقة الثانوية
# AWS provider for secondary region
provider "aws" {
  alias  = "secondary"
  region = var.secondary_region

  default_tags {
    tags = {
      Project     = "Sahool"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Country     = "Saudi Arabia"
      Purpose     = "Precision Agriculture Platform"
    }
  }
}

# ======================================================================
# التحقق من صحة التكوين متعدد المناطق
# Multi-Region Configuration Validation
# ======================================================================
# التأكد من أن المنطقتين الرئيسية والثانوية مختلفتين
# Ensure primary and secondary regions are different
check "regions_must_be_different" {
  assert {
    condition     = var.primary_region != var.secondary_region
    error_message = "Secondary region (${var.secondary_region}) must be different from primary region (${var.primary_region}) for proper disaster recovery."
  }
}

# ======================================================================
# مصادر البيانات لمناطق التوفر
# Data Sources for Availability Zones
# ======================================================================
# جلب مناطق التوفر للمنطقة الرئيسية
# Fetch availability zones for primary region
data "aws_availability_zones" "primary" {
  state = "available"
}

# جلب مناطق التوفر للمنطقة الثانوية
# Fetch availability zones for secondary region
data "aws_availability_zones" "secondary" {
  provider = aws.secondary
  state    = "available"
}

# ======================================================================
# المنطقة الرئيسية - الرياض (Primary Region - Riyadh)
# ======================================================================
# البنية التحتية الكاملة للمنطقة الرئيسية تشمل:
# - شبكة VPC مع شبكات فرعية عامة وخاصة
# - مجموعة EKS Kubernetes للتطبيقات
# - قاعدة بيانات RDS PostgreSQL مع PostGIS للبيانات الجغرافية
# - ElastiCache Redis للذاكرة المؤقتة
# - S3 للصور الفضائية ومخرجات النماذج
module "riyadh_region" {
  source = "./modules/region"

  # معلومات المنطقة الأساسية
  # Basic region information
  region_name        = "riyadh"
  aws_region         = var.primary_region
  environment        = var.environment
  is_primary         = true

  # تكوين الشبكة
  # Network configuration
  vpc_cidr           = var.riyadh_vpc_cidr
  availability_zones = slice(data.aws_availability_zones.primary.names, 0, 3)

  # تكوين مجموعة EKS
  # EKS cluster configuration
  cluster_name       = "${var.environment}-sahool-riyadh"
  cluster_version    = var.eks_cluster_version
  node_instance_type = var.riyadh_node_instance_type
  min_nodes          = var.riyadh_min_nodes
  max_nodes          = var.riyadh_max_nodes
  desired_nodes      = var.riyadh_desired_nodes

  # تكوين قاعدة البيانات RDS
  # RDS database configuration
  db_instance_class  = var.riyadh_db_instance_class
  db_allocated_storage = var.riyadh_db_allocated_storage
  db_name            = "sahool_riyadh"
  db_username        = var.db_username
  db_password        = var.db_password
  enable_multi_az    = true
  backup_retention_period = 30

  # تكوين Redis
  # Redis configuration
  redis_node_type    = var.riyadh_redis_node_type
  redis_num_cache_nodes = var.riyadh_redis_num_nodes

  # تكوين S3 للصور الفضائية
  # S3 configuration for satellite imagery
  enable_satellite_bucket = true
  satellite_bucket_name   = "sahool-satellite-imagery-riyadh"

  # تكوين S3 للنماذج والمخرجات
  # S3 configuration for models and outputs
  enable_model_bucket = true
  model_bucket_name   = "sahool-ai-models-riyadh"

  # العلامات الإضافية
  # Additional tags
  tags = {
    Region     = "Riyadh"
    RegionType = "Primary"
    City       = "الرياض"
  }
}

# ======================================================================
# المنطقة الثانوية - جدة (Secondary Region - Jeddah)
# ======================================================================
# البنية التحتية للمنطقة الثانوية للتوزيع الجغرافي والتوفر العالي
# Secondary region infrastructure for geographic distribution and high availability
module "jeddah_region" {
  source = "./modules/region"

  providers = {
    aws = aws.secondary
  }

  # معلومات المنطقة الأساسية
  # Basic region information
  region_name        = "jeddah"
  aws_region         = var.secondary_region
  environment        = var.environment
  is_primary         = false

  # تكوين الشبكة
  # Network configuration
  vpc_cidr           = var.jeddah_vpc_cidr
  availability_zones = slice(data.aws_availability_zones.secondary.names, 0, 3)

  # تكوين مجموعة EKS
  # EKS cluster configuration
  cluster_name       = "${var.environment}-sahool-jeddah"
  cluster_version    = var.eks_cluster_version
  node_instance_type = var.jeddah_node_instance_type
  min_nodes          = var.jeddah_min_nodes
  max_nodes          = var.jeddah_max_nodes
  desired_nodes      = var.jeddah_desired_nodes

  # تكوين قاعدة البيانات RDS (نسخة للقراءة من الرياض)
  # RDS database configuration (read replica from Riyadh)
  db_instance_class  = var.jeddah_db_instance_class
  db_allocated_storage = var.jeddah_db_allocated_storage
  db_name            = "sahool_jeddah"
  db_username        = var.db_username
  db_password        = var.db_password
  enable_multi_az    = true
  backup_retention_period = 30

  # تكوين Redis
  # Redis configuration
  redis_node_type    = var.jeddah_redis_node_type
  redis_num_cache_nodes = var.jeddah_redis_num_nodes

  # تكوين S3 للصور الفضائية
  # S3 configuration for satellite imagery
  enable_satellite_bucket = true
  satellite_bucket_name   = "sahool-satellite-imagery-jeddah"

  # تكوين S3 للنماذج والمخرجات
  # S3 configuration for models and outputs
  enable_model_bucket = true
  model_bucket_name   = "sahool-ai-models-jeddah"

  # العلامات الإضافية
  # Additional tags
  tags = {
    Region     = "Jeddah"
    RegionType = "Secondary"
    City       = "جدة"
  }
}

# ======================================================================
# التواصل بين المناطق (Cross-Region Connectivity)
# ======================================================================
# VPC Peering بين الرياض وجدة لتمكين الاتصال الآمن
# VPC Peering between Riyadh and Jeddah for secure connectivity
resource "aws_vpc_peering_connection" "riyadh_jeddah" {
  vpc_id        = module.riyadh_region.vpc_id
  peer_vpc_id   = module.jeddah_region.vpc_id
  peer_region   = var.secondary_region
  auto_accept   = false

  tags = {
    Name        = "sahool-riyadh-jeddah-peering"
    Purpose     = "Cross-region connectivity"
    Environment = var.environment
  }
}

# قبول طلب VPC Peering من المنطقة الثانوية
# Accept VPC peering request from secondary region
resource "aws_vpc_peering_connection_accepter" "jeddah" {
  provider                  = aws.secondary
  vpc_peering_connection_id = aws_vpc_peering_connection.riyadh_jeddah.id
  auto_accept               = true

  tags = {
    Name        = "sahool-jeddah-accepts-riyadh"
    Environment = var.environment
  }
}

# ======================================================================
# مسارات VPC Peering (VPC Peering Routes)
# ======================================================================
# مسارات من الرياض إلى جدة عبر VPC Peering
# Routes from Riyadh to Jeddah via VPC Peering
resource "aws_route" "riyadh_to_jeddah" {
  count                     = length(module.riyadh_region.private_route_table_ids)
  route_table_id            = module.riyadh_region.private_route_table_ids[count.index]
  destination_cidr_block    = var.jeddah_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.riyadh_jeddah.id

  depends_on = [aws_vpc_peering_connection_accepter.jeddah]
}

# مسارات من جدة إلى الرياض عبر VPC Peering
# Routes from Jeddah to Riyadh via VPC Peering
resource "aws_route" "jeddah_to_riyadh" {
  provider                  = aws.secondary
  count                     = length(module.jeddah_region.private_route_table_ids)
  route_table_id            = module.jeddah_region.private_route_table_ids[count.index]
  destination_cidr_block    = var.riyadh_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.riyadh_jeddah.id

  depends_on = [aws_vpc_peering_connection_accepter.jeddah]
}

# ======================================================================
# S3 Replication للصور الفضائية بين المناطق
# S3 Replication for satellite imagery between regions
# ======================================================================
# نسخ تلقائي للصور الفضائية من الرياض إلى جدة للنسخ الاحتياطي
# Automatic replication of satellite imagery from Riyadh to Jeddah for backup
resource "aws_s3_bucket_replication_configuration" "satellite_replication" {
  depends_on = [module.riyadh_region, module.jeddah_region]

  bucket = module.riyadh_region.satellite_bucket_id
  role   = aws_iam_role.replication.arn

  rule {
    id     = "replicate-satellite-imagery"
    status = "Enabled"

    destination {
      bucket        = module.jeddah_region.satellite_bucket_arn
      storage_class = "STANDARD_IA"

      # التشفير في المنطقة الثانوية
      # Encryption in secondary region
      encryption_configuration {
        replica_kms_key_id = module.jeddah_region.kms_key_arn
      }
    }
  }
}

# دور IAM للنسخ المتماثل
# IAM role for replication
resource "aws_iam_role" "replication" {
  name = "sahool-s3-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "replication" {
  role = aws_iam_role.replication.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          module.riyadh_region.satellite_bucket_arn
        ]
      },
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Effect = "Allow"
        Resource = [
          "${module.riyadh_region.satellite_bucket_arn}/*"
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Effect = "Allow"
        Resource = [
          "${module.jeddah_region.satellite_bucket_arn}/*"
        ]
      }
    ]
  })
}
