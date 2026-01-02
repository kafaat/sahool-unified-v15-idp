# ======================================================================
# مخرجات وحدة البنية التحتية الإقليمية
# Regional Infrastructure Module Outputs
# ======================================================================

# ======================================================================
# مخرجات الشبكة (Network Outputs)
# ======================================================================
output "vpc_id" {
  description = "معرّف الشبكة الافتراضية / VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "نطاق CIDR للشبكة الافتراضية / VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "معرّفات الشبكات الفرعية العامة / Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "معرّفات الشبكات الفرعية الخاصة / Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "معرّفات شبكات قواعد البيانات / Database subnet IDs"
  value       = aws_subnet.database[*].id
}

# ======================================================================
# مخرجات EKS Cluster
# ======================================================================
output "eks_cluster_id" {
  description = "معرّف مجموعة EKS / EKS cluster ID"
  value       = aws_eks_cluster.main.id
}

output "eks_cluster_name" {
  description = "اسم مجموعة EKS / EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "نقطة نهاية مجموعة EKS / EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "eks_cluster_version" {
  description = "إصدار مجموعة EKS / EKS cluster version"
  value       = aws_eks_cluster.main.version
}

output "eks_cluster_certificate_authority" {
  description = "شهادة CA لمجموعة EKS / EKS cluster certificate authority"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "eks_cluster_security_group_id" {
  description = "معرّف مجموعة أمان EKS / EKS cluster security group ID"
  value       = aws_security_group.eks_cluster.id
}

output "eks_node_group_id" {
  description = "معرّف مجموعة عقد EKS / EKS node group ID"
  value       = aws_eks_node_group.main.id
}

output "eks_node_role_arn" {
  description = "ARN لدور عقد EKS / EKS node role ARN"
  value       = aws_iam_role.eks_nodes.arn
}

# ======================================================================
# مخرجات قاعدة البيانات RDS (RDS Outputs)
# ======================================================================
output "rds_endpoint" {
  description = "نقطة نهاية قاعدة البيانات RDS / RDS database endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "عنوان قاعدة البيانات RDS / RDS database address"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "منفذ قاعدة البيانات RDS / RDS database port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "اسم قاعدة البيانات / Database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_instance_id" {
  description = "معرّف مثيل RDS / RDS instance ID"
  value       = aws_db_instance.postgres.id
}

output "rds_arn" {
  description = "ARN لمثيل RDS / RDS instance ARN"
  value       = aws_db_instance.postgres.arn
}

output "rds_security_group_id" {
  description = "معرّف مجموعة أمان RDS / RDS security group ID"
  value       = aws_security_group.rds.id
}

# ======================================================================
# مخرجات Redis (Redis Outputs)
# ======================================================================
output "redis_endpoint" {
  description = "نقطة نهاية مجموعة Redis / Redis cluster endpoint"
  value       = aws_elasticache_replication_group.redis.configuration_endpoint_address
}

output "redis_port" {
  description = "منفذ Redis / Redis port"
  value       = aws_elasticache_replication_group.redis.port
}

output "redis_id" {
  description = "معرّف مجموعة Redis / Redis cluster ID"
  value       = aws_elasticache_replication_group.redis.id
}

output "redis_arn" {
  description = "ARN لمجموعة Redis / Redis cluster ARN"
  value       = aws_elasticache_replication_group.redis.arn
}

output "redis_security_group_id" {
  description = "معرّف مجموعة أمان Redis / Redis security group ID"
  value       = aws_security_group.redis.id
}

# ======================================================================
# مخرجات S3 (S3 Outputs)
# ======================================================================
output "satellite_bucket_id" {
  description = "معرّف حاوية S3 للصور الفضائية / Satellite imagery S3 bucket ID"
  value       = var.enable_satellite_bucket ? aws_s3_bucket.satellite_imagery[0].id : null
}

output "satellite_bucket_arn" {
  description = "ARN لحاوية S3 للصور الفضائية / Satellite imagery S3 bucket ARN"
  value       = var.enable_satellite_bucket ? aws_s3_bucket.satellite_imagery[0].arn : null
}

output "satellite_bucket_name" {
  description = "اسم حاوية S3 للصور الفضائية / Satellite imagery S3 bucket name"
  value       = var.enable_satellite_bucket ? aws_s3_bucket.satellite_imagery[0].bucket : null
}

output "model_bucket_id" {
  description = "معرّف حاوية S3 للنماذج / AI models S3 bucket ID"
  value       = var.enable_model_bucket ? aws_s3_bucket.ai_models[0].id : null
}

output "model_bucket_arn" {
  description = "ARN لحاوية S3 للنماذج / AI models S3 bucket ARN"
  value       = var.enable_model_bucket ? aws_s3_bucket.ai_models[0].arn : null
}

output "model_bucket_name" {
  description = "اسم حاوية S3 للنماذج / AI models S3 bucket name"
  value       = var.enable_model_bucket ? aws_s3_bucket.ai_models[0].bucket : null
}

# ======================================================================
# مخرجات التشفير (Encryption Outputs)
# ======================================================================
output "kms_key_arn" {
  description = "ARN لمفتاح KMS للتشفير / KMS key ARN for encryption"
  value       = aws_kms_key.s3.arn
}

output "eks_kms_key_arn" {
  description = "ARN لمفتاح KMS لـ EKS / EKS KMS key ARN"
  value       = aws_kms_key.eks.arn
}

output "rds_kms_key_arn" {
  description = "ARN لمفتاح KMS لـ RDS / RDS KMS key ARN"
  value       = aws_kms_key.rds.arn
}

# ======================================================================
# مخرجات عامة (General Outputs)
# ======================================================================
output "region_name" {
  description = "اسم المنطقة / Region name"
  value       = var.region_name
}

output "aws_region" {
  description = "منطقة AWS / AWS region"
  value       = var.aws_region
}

output "environment" {
  description = "البيئة / Environment"
  value       = var.environment
}

output "is_primary" {
  description = "هل هذه المنطقة الرئيسية / Is this the primary region"
  value       = var.is_primary
}
