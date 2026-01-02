# ======================================================================
# وحدة البنية التحتية الإقليمية لمنصة صحول
# Regional Infrastructure Module for Sahool Platform
# ======================================================================
# هذه الوحدة تنشئ البنية التحتية الكاملة لمنطقة واحدة بما في ذلك:
# This module creates complete infrastructure for a single region including:
# - VPC مع شبكات فرعية عامة وخاصة
# - EKS Kubernetes Cluster
# - RDS PostgreSQL مع PostGIS
# - ElastiCache Redis
# - S3 Buckets للصور الفضائية والنماذج
# ======================================================================

# ======================================================================
# الشبكة الافتراضية الخاصة (VPC - Virtual Private Cloud)
# ======================================================================
# إنشاء VPC للمنطقة مع دعم DNS
# Create VPC for the region with DNS support
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-sahool-vpc-${var.region_name}"
      Region      = var.region_name
      Environment = var.environment
    }
  )
}

# ======================================================================
# بوابة الإنترنت (Internet Gateway)
# ======================================================================
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-igw-${var.region_name}"
    }
  )
}

# ======================================================================
# الشبكات الفرعية العامة (Public Subnets)
# ======================================================================
# شبكات فرعية عامة في مناطق توفر متعددة للموازنة والتوفر العالي
# Public subnets across multiple availability zones for load balancing and high availability
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name                                           = "${var.environment}-sahool-public-${var.region_name}-${count.index + 1}"
      "kubernetes.io/role/elb"                      = "1"
      "kubernetes.io/cluster/${var.cluster_name}"   = "shared"
    }
  )
}

# ======================================================================
# الشبكات الفرعية الخاصة (Private Subnets)
# ======================================================================
# شبكات فرعية خاصة للتطبيقات وقواعد البيانات
# Private subnets for applications and databases
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name                                           = "${var.environment}-sahool-private-${var.region_name}-${count.index + 1}"
      "kubernetes.io/role/internal-elb"             = "1"
      "kubernetes.io/cluster/${var.cluster_name}"   = "shared"
    }
  )
}

# ======================================================================
# شبكات فرعية لقواعد البيانات (Database Subnets)
# ======================================================================
resource "aws_subnet" "database" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 200)
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-database-${var.region_name}-${count.index + 1}"
      Type = "Database"
    }
  )
}

# ======================================================================
# عناوين IP المرنة لبوابات NAT (Elastic IPs for NAT Gateways)
# ======================================================================
resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-nat-eip-${var.region_name}-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ======================================================================
# بوابات NAT (NAT Gateways)
# ======================================================================
# بوابات NAT لتمكين الشبكات الخاصة من الوصول إلى الإنترنت
# NAT Gateways to enable private subnets to access the internet
resource "aws_nat_gateway" "main" {
  count         = length(var.availability_zones)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-nat-${var.region_name}-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ======================================================================
# جداول التوجيه (Route Tables)
# ======================================================================
# جدول توجيه للشبكات العامة
# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-public-rt-${var.region_name}"
    }
  )
}

# ربط الشبكات العامة بجدول التوجيه
# Associate public subnets with route table
resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# جداول توجيه للشبكات الخاصة (واحد لكل منطقة توفر)
# Route tables for private subnets (one per AZ)
resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-private-rt-${var.region_name}-${count.index + 1}"
    }
  )
}

# ربط الشبكات الخاصة بجداول التوجيه
# Associate private subnets with route tables
resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# ======================================================================
# مجموعة أمان EKS (EKS Security Group)
# ======================================================================
resource "aws_security_group" "eks_cluster" {
  name_prefix = "${var.environment}-sahool-eks-${var.region_name}-"
  description = "Security group for EKS cluster ${var.cluster_name}"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-eks-sg-${var.region_name}"
    }
  )
}

# ======================================================================
# دور IAM لمجموعة EKS (IAM Role for EKS Cluster)
# ======================================================================
resource "aws_iam_role" "eks_cluster" {
  name = "${var.environment}-sahool-eks-cluster-role-${var.region_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster.name
}

# ======================================================================
# مجموعة EKS Kubernetes (EKS Kubernetes Cluster)
# ======================================================================
# مجموعة Kubernetes المُدارة لتشغيل تطبيقات صحول
# Managed Kubernetes cluster for running Sahool applications
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  version  = var.cluster_version
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids              = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    security_group_ids      = [aws_security_group.eks_cluster.id]
  }

  # تمكين تسجيل السجلات
  # Enable logging
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # التشفير للأسرار
  # Encryption for secrets
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }

  tags = merge(
    var.tags,
    {
      Name = var.cluster_name
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]
}

# ======================================================================
# دور IAM لعقد EKS (IAM Role for EKS Nodes)
# ======================================================================
resource "aws_iam_role" "eks_nodes" {
  name = "${var.environment}-sahool-eks-node-role-${var.region_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}

# سياسة إضافية للوصول إلى S3
# Additional policy for S3 access
resource "aws_iam_role_policy" "eks_s3_access" {
  name = "${var.environment}-sahool-eks-s3-access-${var.region_name}"
  role = aws_iam_role.eks_nodes.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.satellite_imagery[0].arn}/*",
          aws_s3_bucket.satellite_imagery[0].arn,
          "${aws_s3_bucket.ai_models[0].arn}/*",
          aws_s3_bucket.ai_models[0].arn
        ]
      }
    ]
  })
}

# ======================================================================
# مجموعة عقد EKS (EKS Node Group)
# ======================================================================
# مجموعة من خوادم العمل لتشغيل الحاويات
# Group of worker nodes for running containers
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.private[*].id

  instance_types = [var.node_instance_type]

  scaling_config {
    desired_size = var.desired_nodes
    max_size     = var.max_nodes
    min_size     = var.min_nodes
  }

  update_config {
    max_unavailable = 1
  }

  # تسميات للعقد
  # Labels for nodes
  labels = {
    environment = var.environment
    region      = var.region_name
    workload    = "general"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.cluster_name}-node-group"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
}

# ======================================================================
# مفتاح KMS للتشفير (KMS Key for Encryption)
# ======================================================================
resource "aws_kms_key" "eks" {
  description             = "KMS key for EKS cluster ${var.cluster_name} secrets encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-eks-kms-${var.region_name}"
    }
  )
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.environment}-sahool-eks-${var.region_name}"
  target_key_id = aws_kms_key.eks.key_id
}

# ======================================================================
# مجموعة أمان RDS (RDS Security Group)
# ======================================================================
resource "aws_security_group" "rds" {
  name_prefix = "${var.environment}-sahool-rds-${var.region_name}-"
  description = "Security group for RDS PostgreSQL database"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "PostgreSQL access from EKS cluster"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-rds-sg-${var.region_name}"
    }
  )
}

# ======================================================================
# مجموعة شبكات فرعية لقاعدة البيانات (DB Subnet Group)
# ======================================================================
resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-sahool-db-subnet-${var.region_name}"
  subnet_ids = aws_subnet.database[*].id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-db-subnet-group-${var.region_name}"
    }
  )
}

# ======================================================================
# مجموعة معلمات RDS PostgreSQL مع PostGIS
# RDS PostgreSQL Parameter Group with PostGIS
# ======================================================================
resource "aws_db_parameter_group" "postgres" {
  name_prefix = "${var.environment}-sahool-postgres-${var.region_name}-"
  family      = "postgres15"
  description = "PostgreSQL parameter group with PostGIS for Sahool"

  # تمكين PostGIS للبيانات الجغرافية
  # Enable PostGIS for geospatial data
  parameter {
    name  = "shared_preload_libraries"
    value = "postgis,pg_stat_statements"
  }

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  tags = var.tags
}

# ======================================================================
# قاعدة بيانات RDS PostgreSQL
# RDS PostgreSQL Database
# ======================================================================
# قاعدة بيانات PostgreSQL مع PostGIS للبيانات الجغرافية
# PostgreSQL database with PostGIS for geospatial data
resource "aws_db_instance" "postgres" {
  identifier     = "${var.environment}-sahool-db-${var.region_name}"
  engine         = "postgres"
  engine_version = "15.4"

  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  # التوفر العالي
  # High availability
  multi_az               = var.enable_multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.postgres.name

  # النسخ الاحتياطي والصيانة
  # Backup and maintenance
  backup_retention_period = var.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  # تمكين النسخ الاحتياطية التلقائية
  # Enable automated backups
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # الحماية من الحذف
  # Deletion protection
  deletion_protection = var.environment == "production" ? true : false
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.environment}-sahool-db-${var.region_name}-final-snapshot" : null

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-db-${var.region_name}"
    }
  )
}

# مفتاح KMS لتشفير RDS
# KMS key for RDS encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption in ${var.region_name}"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-rds-kms-${var.region_name}"
    }
  )
}

# ======================================================================
# مجموعة أمان ElastiCache Redis (Redis Security Group)
# ======================================================================
resource "aws_security_group" "redis" {
  name_prefix = "${var.environment}-sahool-redis-${var.region_name}-"
  description = "Security group for ElastiCache Redis"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Redis access from EKS cluster"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-redis-sg-${var.region_name}"
    }
  )
}

# ======================================================================
# مجموعة شبكات فرعية لـ ElastiCache
# ElastiCache Subnet Group
# ======================================================================
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.environment}-sahool-redis-subnet-${var.region_name}"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-redis-subnet-group-${var.region_name}"
    }
  )
}

# ======================================================================
# ElastiCache Redis Cluster
# ======================================================================
# Redis للذاكرة المؤقتة وقوائم الانتظار
# Redis for caching and job queues
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.environment}-sahool-redis-${var.region_name}"
  replication_group_description = "Redis cluster for Sahool ${var.region_name}"

  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.redis_node_type
  num_cache_clusters   = var.redis_num_cache_nodes
  port                 = 6379

  # التكوين الأمني
  # Security configuration
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled   = true

  # النسخ الاحتياطي
  # Backup configuration
  snapshot_retention_limit = 5
  snapshot_window         = "03:00-05:00"
  maintenance_window      = "sun:05:00-sun:07:00"

  # التوفر العالي
  # High availability
  automatic_failover_enabled = var.redis_num_cache_nodes > 1

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-redis-${var.region_name}"
    }
  )
}

# ======================================================================
# S3 Bucket للصور الفضائية (Satellite Imagery)
# ======================================================================
# حاوية S3 لتخزين الصور الفضائية من Sentinel وLandsat
# S3 bucket for storing satellite imagery from Sentinel and Landsat
resource "aws_s3_bucket" "satellite_imagery" {
  count  = var.enable_satellite_bucket ? 1 : 0
  bucket = "${var.satellite_bucket_name}-${var.environment}"

  tags = merge(
    var.tags,
    {
      Name    = "${var.satellite_bucket_name}-${var.environment}"
      Purpose = "Satellite Imagery Storage"
    }
  )
}

# تمكين versioning للصور الفضائية
# Enable versioning for satellite imagery
resource "aws_s3_bucket_versioning" "satellite_imagery" {
  count  = var.enable_satellite_bucket ? 1 : 0
  bucket = aws_s3_bucket.satellite_imagery[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

# تشفير الصور الفضائية
# Encryption for satellite imagery
resource "aws_s3_bucket_server_side_encryption_configuration" "satellite_imagery" {
  count  = var.enable_satellite_bucket ? 1 : 0
  bucket = aws_s3_bucket.satellite_imagery[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# سياسة دورة الحياة للصور الفضائية
# Lifecycle policy for satellite imagery
resource "aws_s3_bucket_lifecycle_configuration" "satellite_imagery" {
  count  = var.enable_satellite_bucket ? 1 : 0
  bucket = aws_s3_bucket.satellite_imagery[0].id

  rule {
    id     = "archive-old-imagery"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }

    expiration {
      days = 730
    }
  }
}

# ======================================================================
# S3 Bucket لنماذج الذكاء الاصطناعي ومخرجاتها
# S3 Bucket for AI Models and Outputs
# ======================================================================
resource "aws_s3_bucket" "ai_models" {
  count  = var.enable_model_bucket ? 1 : 0
  bucket = "${var.model_bucket_name}-${var.environment}"

  tags = merge(
    var.tags,
    {
      Name    = "${var.model_bucket_name}-${var.environment}"
      Purpose = "AI Models and Outputs Storage"
    }
  )
}

# تمكين versioning للنماذج
# Enable versioning for models
resource "aws_s3_bucket_versioning" "ai_models" {
  count  = var.enable_model_bucket ? 1 : 0
  bucket = aws_s3_bucket.ai_models[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

# تشفير النماذج
# Encryption for models
resource "aws_s3_bucket_server_side_encryption_configuration" "ai_models" {
  count  = var.enable_model_bucket ? 1 : 0
  bucket = aws_s3_bucket.ai_models[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# مفتاح KMS لتشفير S3
# KMS key for S3 encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 encryption in ${var.region_name}"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-sahool-s3-kms-${var.region_name}"
    }
  )
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.environment}-sahool-s3-${var.region_name}"
  target_key_id = aws_kms_key.s3.key_id
}
