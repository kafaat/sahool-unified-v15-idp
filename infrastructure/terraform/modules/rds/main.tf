# ======================================================================
# وحدة قاعدة بيانات RDS PostgreSQL لمنصة صحول
# RDS PostgreSQL Database Module for Sahool Platform
# ======================================================================
# تنشئ هذه الوحدة قاعدة بيانات PostgreSQL 16 مع PostGIS 3.4
# This module creates a PostgreSQL 16 database with PostGIS 3.4
# للبيانات الجغرافية والمكانية الزراعية
# For agricultural geospatial data
# ======================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# ======================================================================
# البيانات المحلية (Local Values)
# ======================================================================
locals {
  name_prefix = "${var.environment}-sahool"
  db_identifier = "${local.name_prefix}-db"

  common_tags = merge(
    var.tags,
    {
      Project     = "sahool"
      Environment = var.environment
      ManagedBy   = "terraform"
      Module      = "rds"
    }
  )
}

# ======================================================================
# مفتاح KMS لتشفير RDS (KMS Key for RDS Encryption)
# ======================================================================
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS PostgreSQL encryption - ${local.db_identifier}"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-rds-kms"
    }
  )
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${local.name_prefix}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# ======================================================================
# مجموعة شبكات فرعية لقاعدة البيانات (DB Subnet Group)
# ======================================================================
resource "aws_db_subnet_group" "main" {
  name        = "${local.db_identifier}-subnet-group"
  description = "Database subnet group for Sahool PostgreSQL with PostGIS"
  subnet_ids  = var.database_subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name = "${local.db_identifier}-subnet-group"
    }
  )
}

# ======================================================================
# مجموعة أمان RDS (RDS Security Group)
# ======================================================================
resource "aws_security_group" "rds" {
  name_prefix = "${local.db_identifier}-"
  description = "Security group for RDS PostgreSQL database with PostGIS"
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.db_identifier}-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# السماح بحركة PostgreSQL الواردة من مجموعات الأمان المحددة
# Allow inbound PostgreSQL traffic from specified security groups
resource "aws_security_group_rule" "rds_ingress" {
  count = length(var.allowed_security_group_ids)

  type                     = "ingress"
  from_port                = var.port
  to_port                  = var.port
  protocol                 = "tcp"
  source_security_group_id = var.allowed_security_group_ids[count.index]
  security_group_id        = aws_security_group.rds.id
  description              = "PostgreSQL access from allowed security group ${count.index + 1}"
}

# السماح بحركة PostgreSQL الواردة من نطاقات CIDR محددة
# Allow inbound PostgreSQL traffic from specified CIDR blocks
resource "aws_security_group_rule" "rds_ingress_cidr" {
  count = length(var.allowed_cidr_blocks) > 0 ? 1 : 0

  type              = "ingress"
  from_port         = var.port
  to_port           = var.port
  protocol          = "tcp"
  cidr_blocks       = var.allowed_cidr_blocks
  security_group_id = aws_security_group.rds.id
  description       = "PostgreSQL access from allowed CIDR blocks"
}

# ======================================================================
# مجموعة معلمات RDS PostgreSQL مع PostGIS
# RDS PostgreSQL Parameter Group with PostGIS
# ======================================================================
resource "aws_db_parameter_group" "postgres" {
  name_prefix = "${local.db_identifier}-pg16-"
  family      = "postgres16"
  description = "PostgreSQL 16 parameter group with PostGIS for Sahool platform"

  # تمكين PostGIS والإضافات الجغرافية
  # Enable PostGIS and geospatial extensions
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,auto_explain"
  }

  # تسجيل الاستعلامات البطيئة
  # Log slow queries
  parameter {
    name  = "log_min_duration_statement"
    value = var.log_min_duration_ms
  }

  parameter {
    name  = "log_statement"
    value = "ddl"
  }

  # تحسين أداء PostGIS
  # PostGIS performance tuning
  parameter {
    name  = "work_mem"
    value = var.work_mem_kb
  }

  parameter {
    name  = "maintenance_work_mem"
    value = var.maintenance_work_mem_kb
  }

  parameter {
    name  = "effective_cache_size"
    value = var.effective_cache_size_kb
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1"
  }

  parameter {
    name  = "effective_io_concurrency"
    value = "200"
  }

  # إعدادات WAL للأداء
  # WAL settings for performance
  parameter {
    name  = "wal_buffers"
    value = "65536"
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  # أمان الاتصال
  # Connection security
  parameter {
    name  = "ssl"
    value = "1"
  }

  parameter {
    name  = "password_encryption"
    value = "scram-sha-256"
  }

  # إعدادات pg_stat_statements
  # pg_stat_statements settings
  parameter {
    name  = "pg_stat_statements.max"
    value = "10000"
  }

  parameter {
    name  = "pg_stat_statements.track"
    value = "all"
  }

  tags = local.common_tags

  lifecycle {
    create_before_destroy = true
  }
}

# ======================================================================
# قاعدة بيانات RDS PostgreSQL الرئيسية
# Primary RDS PostgreSQL Database
# ======================================================================
resource "aws_db_instance" "primary" {
  identifier = local.db_identifier

  # إعدادات المحرك
  # Engine settings
  engine         = "postgres"
  engine_version = var.engine_version

  # إعدادات المثيل
  # Instance settings
  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type      = var.storage_type
  iops              = var.storage_type == "io1" || var.storage_type == "io2" ? var.iops : null

  # التشفير
  # Encryption
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  # قاعدة البيانات
  # Database
  db_name  = var.db_name
  port     = var.port
  username = var.username
  password = var.password

  # الشبكة والأمان
  # Network and security
  multi_az               = var.multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.postgres.name
  publicly_accessible    = false
  ca_cert_identifier     = "rds-ca-rsa2048-g1"

  # النسخ الاحتياطي
  # Backup
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  copy_tags_to_snapshot  = true
  delete_automated_backups = false

  # الصيانة
  # Maintenance
  maintenance_window        = var.maintenance_window
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  allow_major_version_upgrade = false

  # المراقبة
  # Monitoring
  monitoring_interval          = var.monitoring_interval
  monitoring_role_arn         = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_kms_key_id = var.performance_insights_enabled ? aws_kms_key.rds.arn : null
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_days : null
  enabled_cloudwatch_logs_exports = var.cloudwatch_log_exports

  # مصادقة IAM لقاعدة البيانات
  # IAM Database Authentication
  iam_database_authentication_enabled = var.enable_iam_auth

  # الحماية
  # Protection
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${local.db_identifier}-final-${formatdate("YYYY-MM-DD", timestamp())}" : null

  tags = merge(
    local.common_tags,
    {
      Name    = local.db_identifier
      Engine  = "PostgreSQL 16 with PostGIS"
      Purpose = "Agricultural geospatial database"
    }
  )

  lifecycle {
    ignore_changes = [final_snapshot_identifier]
  }
}

# ======================================================================
# دور IAM لمراقبة RDS المُحسّنة (IAM Role for RDS Enhanced Monitoring)
# ======================================================================
resource "aws_iam_role" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0

  name = "${local.db_identifier}-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
  role       = aws_iam_role.rds_monitoring[0].name
}

# ======================================================================
# نسخة القراءة (Read Replica) - اختيارية
# Read Replica - Optional
# ======================================================================
resource "aws_db_instance" "read_replica" {
  count = var.create_read_replica ? 1 : 0

  identifier          = "${local.db_identifier}-replica"
  replicate_source_db = aws_db_instance.primary.identifier

  instance_class = var.replica_instance_class != "" ? var.replica_instance_class : var.instance_class
  storage_encrypted = true
  kms_key_id       = aws_kms_key.rds.arn

  multi_az            = false
  publicly_accessible = false

  # المراقبة
  # Monitoring
  monitoring_interval          = var.monitoring_interval
  monitoring_role_arn         = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_kms_key_id = var.performance_insights_enabled ? aws_kms_key.rds.arn : null

  tags = merge(
    local.common_tags,
    {
      Name    = "${local.db_identifier}-replica"
      Purpose = "Read replica for query offloading"
    }
  )
}

# ======================================================================
# تنبيهات CloudWatch لقاعدة البيانات (CloudWatch Alarms)
# ======================================================================
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count = var.create_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${local.db_identifier}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization is above 80% for ${local.db_identifier}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.identifier
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "free_storage_low" {
  count = var.create_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${local.db_identifier}-free-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.allocated_storage * 1024 * 1024 * 1024 * 0.1  # 10% of allocated storage
  alarm_description   = "RDS free storage is below 10% for ${local.db_identifier}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.identifier
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "connection_count_high" {
  count = var.create_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${local.db_identifier}-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.max_connections_alarm_threshold
  alarm_description   = "RDS connection count is above threshold for ${local.db_identifier}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.identifier
  }

  tags = local.common_tags
}
