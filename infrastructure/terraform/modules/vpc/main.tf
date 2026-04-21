# ======================================================================
# وحدة الشبكة الافتراضية الخاصة لمنصة صحول
# VPC Module for Sahool Platform
# ======================================================================
# تنشئ هذه الوحدة شبكة VPC كاملة مع شبكات فرعية عامة وخاصة وقواعد بيانات
# This module creates a complete VPC with public, private, and database subnets
# بالإضافة إلى بوابات NAT وجداول التوجيه ونقاط نهاية VPC
# Including NAT gateways, route tables, and VPC endpoints
# ======================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ======================================================================
# البيانات المحلية (Local Values)
# ======================================================================
locals {
  name_prefix = "${var.environment}-sahool-${var.region_name}"

  common_tags = merge(
    var.tags,
    {
      Project     = "sahool"
      Environment = var.environment
      ManagedBy   = "terraform"
      Module      = "vpc"
      Region      = var.region_name
    }
  )
}

# ======================================================================
# الشبكة الافتراضية الخاصة (VPC)
# ======================================================================
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  # تمكين IPv6 اختيارياً
  # Optionally enable IPv6
  assign_generated_ipv6_cidr_block = var.enable_ipv6

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-vpc"
    }
  )
}

# ======================================================================
# بوابة الإنترنت (Internet Gateway)
# ======================================================================
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-igw"
    }
  )
}

# ======================================================================
# الشبكات الفرعية العامة (Public Subnets)
# ======================================================================
# شبكات فرعية عامة لموازنات التحميل وبوابات NAT
# Public subnets for load balancers and NAT gateways
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.cidr_block, var.subnet_newbits, count.index)
  availability_zone       = var.availability_zones[count.index]
  # Public IPs assigned explicitly via ELB/NAT, not automatically
  map_public_ip_on_launch = false

  tags = merge(
    local.common_tags,
    {
      Name                                = "${local.name_prefix}-public-${var.availability_zones[count.index]}"
      Tier                                = "Public"
      "kubernetes.io/role/elb"            = "1"
      "kubernetes.io/cluster/${var.eks_cluster_name}" = var.eks_cluster_name != "" ? "shared" : ""
    }
  )
}

# ======================================================================
# الشبكات الفرعية الخاصة (Private Subnets)
# ======================================================================
# شبكات فرعية خاصة لتطبيقات EKS والخدمات
# Private subnets for EKS applications and services
resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, var.subnet_newbits, count.index + length(var.availability_zones))
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    local.common_tags,
    {
      Name                                         = "${local.name_prefix}-private-${var.availability_zones[count.index]}"
      Tier                                         = "Private"
      "kubernetes.io/role/internal-elb"            = "1"
      "kubernetes.io/cluster/${var.eks_cluster_name}" = var.eks_cluster_name != "" ? "shared" : ""
    }
  )
}

# ======================================================================
# شبكات فرعية لقواعد البيانات (Database Subnets)
# ======================================================================
# شبكات معزولة لقواعد البيانات RDS وElastiCache
# Isolated subnets for RDS databases and ElastiCache
resource "aws_subnet" "database" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, var.subnet_newbits, count.index + 2 * length(var.availability_zones))
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-database-${var.availability_zones[count.index]}"
      Tier = "Database"
    }
  )
}

# ======================================================================
# عناوين IP المرنة لبوابات NAT (Elastic IPs for NAT Gateways)
# ======================================================================
resource "aws_eip" "nat" {
  count = var.single_nat_gateway ? 1 : length(var.availability_zones)

  domain = "vpc"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-nat-eip-${count.index + 1}"
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
  count = var.single_nat_gateway ? 1 : length(var.availability_zones)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-nat-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ======================================================================
# جداول التوجيه العامة (Public Route Tables)
# ======================================================================
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-public-rt"
    }
  )
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ======================================================================
# جداول التوجيه الخاصة (Private Route Tables)
# ======================================================================
# جدول توجيه لكل منطقة توفر مع بوابة NAT خاصة بها
# Route table per AZ with its own NAT gateway
resource "aws_route_table" "private" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-private-rt-${var.availability_zones[count.index]}"
    }
  )
}

resource "aws_route" "private_nat" {
  count = length(var.availability_zones)

  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# ======================================================================
# جداول التوجيه لقواعد البيانات (Database Route Tables)
# ======================================================================
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-database-rt"
    }
  )
}

resource "aws_route_table_association" "database" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database.id
}

# ======================================================================
# قوائم التحكم بالشبكة (Network ACLs)
# ======================================================================
# قائمة تحكم مخصصة لشبكات قواعد البيانات لعزل إضافي
# Custom NACL for database subnets for additional isolation
resource "aws_network_acl" "database" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.database[*].id

  # السماح بحركة PostgreSQL الواردة من الشبكات الخاصة
  # Allow inbound PostgreSQL traffic from private subnets
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.cidr_block
    from_port  = 5432
    to_port    = 5432
  }

  # السماح بحركة Redis الواردة من الشبكات الخاصة
  # Allow inbound Redis traffic from private subnets
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.cidr_block
    from_port  = 6379
    to_port    = 6379
  }

  # السماح بحركة الرد المرتجعة (Ephemeral ports)
  # Allow return traffic (ephemeral ports)
  ingress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = var.cidr_block
    from_port  = 1024
    to_port    = 65535
  }

  # السماح بكل الحركة الصادرة داخل VPC
  # Allow all outbound traffic within VPC
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.cidr_block
    from_port  = 0
    to_port    = 65535
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-database-nacl"
    }
  )
}

# ======================================================================
# نقاط نهاية VPC (VPC Endpoints)
# ======================================================================
# نقطة نهاية S3 لتجنب حركة المرور عبر الإنترنت
# S3 endpoint to avoid internet traffic for S3 access
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  route_table_ids = concat(
    [aws_route_table.public.id],
    aws_route_table.private[*].id,
    [aws_route_table.database.id]
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-s3-endpoint"
    }
  )
}

# نقطة نهاية DynamoDB
# DynamoDB endpoint (for Terraform state locking)
resource "aws_vpc_endpoint" "dynamodb" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.dynamodb"

  route_table_ids = concat(
    aws_route_table.private[*].id
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-dynamodb-endpoint"
    }
  )
}

# نقطة نهاية ECR API لسحب صور Docker
# ECR API endpoint for pulling Docker images
resource "aws_vpc_endpoint" "ecr_api" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecr-api-endpoint"
    }
  )
}

# نقطة نهاية ECR Docker لسحب طبقات الصور
# ECR Docker endpoint for pulling image layers
resource "aws_vpc_endpoint" "ecr_dkr" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecr-dkr-endpoint"
    }
  )
}

# نقطة نهاية STS لمصادقة IRSA في EKS
# STS endpoint for EKS IRSA authentication
resource "aws_vpc_endpoint" "sts" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.sts"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-sts-endpoint"
    }
  )
}

# نقطة نهاية CloudWatch Logs
# CloudWatch Logs endpoint
resource "aws_vpc_endpoint" "logs" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-logs-endpoint"
    }
  )
}

# ======================================================================
# مجموعة أمان نقاط نهاية VPC (VPC Endpoints Security Group)
# ======================================================================
resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "${local.name_prefix}-vpc-endpoints-"
  description = "Security group for VPC interface endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.cidr_block]
    description = "HTTPS from VPC CIDR"
  }

  # Egress restricted to the VPC CIDR — interface endpoints terminate
  # AWS-service traffic inside the VPC, so no public-internet egress is
  # required. Eliminates the previous `0.0.0.0/0` data-exfil path
  # (STABILIZATION_PLAN_v16.1 PR4 — "VPC endpoint egress restriction").
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.cidr_block]
    description = "VPC-internal traffic only"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-vpc-endpoints-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# ======================================================================
# سجل تدفق VPC (VPC Flow Logs)
# ======================================================================
resource "aws_flow_log" "main" {
  count = var.enable_flow_logs ? 1 : 0

  vpc_id               = aws_vpc.main.id
  traffic_type         = "ALL"
  iam_role_arn         = aws_iam_role.flow_logs[0].arn
  log_destination      = aws_cloudwatch_log_group.flow_logs[0].arn
  log_destination_type = "cloud-watch-logs"
  max_aggregation_interval = 60

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-flow-logs"
    }
  )
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name              = "/aws/vpc/flow-logs/${local.name_prefix}"
  retention_in_days = var.flow_logs_retention_days

  tags = local.common_tags
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name = "${local.name_prefix}-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name = "${local.name_prefix}-flow-logs-policy"
  role = aws_iam_role.flow_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
