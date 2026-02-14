# ======================================================================
# وحدة ElastiCache Redis لمنصة صحول
# ElastiCache Redis Module for Sahool Platform
# ======================================================================
# تنشئ هذه الوحدة مجموعة Redis 7.x مع Sentinel/النسخ المتماثل
# This module creates a Redis 7.x cluster with Sentinel/replication
# للتخزين المؤقت وقوائم الانتظار والجلسات
# For caching, job queues, and sessions
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
  redis_id    = "${local.name_prefix}-redis"

  common_tags = merge(
    var.tags,
    {
      Project     = "sahool"
      Environment = var.environment
      ManagedBy   = "terraform"
      Module      = "elasticache"
    }
  )
}

# ======================================================================
# رمز مصادقة Redis (Redis Auth Token)
# ======================================================================
resource "random_password" "redis_auth" {
  count = var.auth_token == "" ? 1 : 0

  length  = 64
  special = false
}

locals {
  auth_token = var.auth_token != "" ? var.auth_token : random_password.redis_auth[0].result
}

# ======================================================================
# مجموعة شبكات فرعية لـ ElastiCache (ElastiCache Subnet Group)
# ======================================================================
resource "aws_elasticache_subnet_group" "redis" {
  name        = "${local.redis_id}-subnet-group"
  description = "Subnet group for Sahool Redis cluster"
  subnet_ids  = var.subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name = "${local.redis_id}-subnet-group"
    }
  )
}

# ======================================================================
# مجموعة أمان Redis (Redis Security Group)
# ======================================================================
resource "aws_security_group" "redis" {
  name_prefix = "${local.redis_id}-"
  description = "Security group for ElastiCache Redis cluster"
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.redis_id}-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# السماح بحركة Redis الواردة من مجموعات الأمان المحددة
# Allow inbound Redis traffic from specified security groups
resource "aws_security_group_rule" "redis_ingress" {
  count = length(var.allowed_security_group_ids)

  type                     = "ingress"
  from_port                = var.port
  to_port                  = var.port
  protocol                 = "tcp"
  source_security_group_id = var.allowed_security_group_ids[count.index]
  security_group_id        = aws_security_group.redis.id
  description              = "Redis access from allowed security group ${count.index + 1}"
}

# السماح بحركة Redis الواردة من نطاقات CIDR
# Allow inbound Redis traffic from CIDR blocks
resource "aws_security_group_rule" "redis_ingress_cidr" {
  count = length(var.allowed_cidr_blocks) > 0 ? 1 : 0

  type              = "ingress"
  from_port         = var.port
  to_port           = var.port
  protocol          = "tcp"
  cidr_blocks       = var.allowed_cidr_blocks
  security_group_id = aws_security_group.redis.id
  description       = "Redis access from allowed CIDR blocks"
}

# السماح بكل الحركة الصادرة
# Allow all outbound traffic
resource "aws_security_group_rule" "redis_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.redis.id
  description       = "Allow all outbound traffic"
}

# ======================================================================
# مجموعة معلمات Redis (Redis Parameter Group)
# ======================================================================
resource "aws_elasticache_parameter_group" "redis" {
  name        = "${local.redis_id}-params"
  family      = "redis7"
  description = "Redis 7.x parameter group for Sahool platform"

  # تحسينات الأداء
  # Performance tuning
  parameter {
    name  = "maxmemory-policy"
    value = var.maxmemory_policy
  }

  parameter {
    name  = "notify-keyspace-events"
    value = var.notify_keyspace_events
  }

  # تحسينات إدارة الذاكرة
  # Memory management tuning
  parameter {
    name  = "activedefrag"
    value = "yes"
  }

  parameter {
    name  = "lazyfree-lazy-eviction"
    value = "yes"
  }

  parameter {
    name  = "lazyfree-lazy-expire"
    value = "yes"
  }

  # إعدادات انتهاء الصلاحية للجلسات والتخزين المؤقت
  # Expiration settings for sessions and caching
  parameter {
    name  = "timeout"
    value = var.connection_timeout
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }

  tags = local.common_tags
}

# ======================================================================
# مجموعة النسخ المتماثل Redis (Redis Replication Group)
# ======================================================================
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = local.redis_id
  description          = "Redis cluster for Sahool ${var.environment} - sessions, cache, and job queues"

  # إعدادات المحرك
  # Engine settings
  engine               = "redis"
  engine_version       = var.engine_version
  node_type            = var.node_type
  port                 = var.port
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  # إعدادات النسخ المتماثل
  # Replication settings
  num_cache_clusters   = var.num_cache_nodes
  automatic_failover_enabled = var.num_cache_nodes > 1
  multi_az_enabled     = var.num_cache_nodes > 1

  # إعدادات الشبكة والأمان
  # Network and security settings
  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  # التشفير
  # Encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = local.auth_token

  # النسخ الاحتياطي
  # Backup settings
  snapshot_retention_limit = var.snapshot_retention_limit
  snapshot_window         = var.snapshot_window

  # الصيانة
  # Maintenance
  maintenance_window      = var.maintenance_window
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  apply_immediately       = var.environment != "production"

  # الإشعارات
  # Notifications
  notification_topic_arn = var.notification_topic_arn

  tags = merge(
    local.common_tags,
    {
      Name    = local.redis_id
      Purpose = "Caching, sessions, rate-limiting, and job queues"
    }
  )
}

# ======================================================================
# تنبيهات CloudWatch لـ Redis (CloudWatch Alarms)
# ======================================================================
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count = var.create_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${local.redis_id}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "EngineCPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "Redis CPU utilization is above 75% for ${local.redis_id}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  count = var.create_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${local.redis_id}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Redis memory usage is above 80% for ${local.redis_id}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "evictions" {
  count = var.create_cloudwatch_alarms ? 1 : 0

  alarm_name          = "${local.redis_id}-evictions"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Evictions"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Sum"
  threshold           = 100
  alarm_description   = "Redis is evicting keys for ${local.redis_id}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "replication_lag" {
  count = var.create_cloudwatch_alarms && var.num_cache_nodes > 1 ? 1 : 0

  alarm_name          = "${local.redis_id}-replication-lag"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "ReplicationLag"
  namespace           = "AWS/ElastiCache"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1
  alarm_description   = "Redis replication lag is above 1 second for ${local.redis_id}"
  alarm_actions       = var.alarm_sns_topic_arns

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }

  tags = local.common_tags
}
