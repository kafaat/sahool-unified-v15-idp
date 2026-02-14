# ======================================================================
# مخرجات وحدة قاعدة بيانات RDS PostgreSQL
# RDS PostgreSQL Database Module Outputs
# ======================================================================

# ======================================================================
# مخرجات المثيل الرئيسي (Primary Instance Outputs)
# ======================================================================
output "endpoint" {
  description = "نقطة نهاية قاعدة البيانات الرئيسية (host:port) / Primary database endpoint"
  value       = aws_db_instance.primary.endpoint
}

output "address" {
  description = "عنوان قاعدة البيانات الرئيسية (host) / Primary database address"
  value       = aws_db_instance.primary.address
}

output "port" {
  description = "منفذ قاعدة البيانات / Database port"
  value       = aws_db_instance.primary.port
}

output "db_name" {
  description = "اسم قاعدة البيانات / Database name"
  value       = aws_db_instance.primary.db_name
}

output "identifier" {
  description = "معرّف مثيل RDS / RDS instance identifier"
  value       = aws_db_instance.primary.identifier
}

output "arn" {
  description = "ARN لمثيل RDS / RDS instance ARN"
  value       = aws_db_instance.primary.arn
}

output "resource_id" {
  description = "معرّف مورد RDS / RDS resource ID"
  value       = aws_db_instance.primary.resource_id
}

output "engine_version_actual" {
  description = "إصدار المحرك الفعلي / Actual engine version"
  value       = aws_db_instance.primary.engine_version_actual
}

# ======================================================================
# مخرجات سلسلة الاتصال (Connection String Outputs)
# ======================================================================
output "connection_string" {
  description = "سلسلة اتصال PostgreSQL (بدون كلمة المرور) / PostgreSQL connection string (without password)"
  value       = "postgresql://${var.username}@${aws_db_instance.primary.address}:${aws_db_instance.primary.port}/${var.db_name}?sslmode=require"
  sensitive   = true
}

# ======================================================================
# مخرجات النسخة المتماثلة (Read Replica Outputs)
# ======================================================================
output "replica_endpoint" {
  description = "نقطة نهاية نسخة القراءة / Read replica endpoint"
  value       = var.create_read_replica ? aws_db_instance.read_replica[0].endpoint : null
}

output "replica_address" {
  description = "عنوان نسخة القراءة / Read replica address"
  value       = var.create_read_replica ? aws_db_instance.read_replica[0].address : null
}

# ======================================================================
# مخرجات الأمان (Security Outputs)
# ======================================================================
output "security_group_id" {
  description = "معرّف مجموعة أمان RDS / RDS security group ID"
  value       = aws_security_group.rds.id
}

output "kms_key_arn" {
  description = "ARN لمفتاح KMS لتشفير RDS / KMS key ARN for RDS encryption"
  value       = aws_kms_key.rds.arn
}

output "kms_key_id" {
  description = "معرّف مفتاح KMS لتشفير RDS / KMS key ID for RDS encryption"
  value       = aws_kms_key.rds.key_id
}

# ======================================================================
# مخرجات مجموعة الشبكات الفرعية (Subnet Group Outputs)
# ======================================================================
output "db_subnet_group_name" {
  description = "اسم مجموعة شبكات قاعدة البيانات / Database subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "db_subnet_group_arn" {
  description = "ARN لمجموعة شبكات قاعدة البيانات / Database subnet group ARN"
  value       = aws_db_subnet_group.main.arn
}

# ======================================================================
# مخرجات المراقبة (Monitoring Outputs)
# ======================================================================
output "monitoring_role_arn" {
  description = "ARN لدور IAM لمراقبة RDS المُحسّنة / Enhanced monitoring IAM role ARN"
  value       = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null
}
