# ======================================================================
# وحدة مجموعة EKS Kubernetes لمنصة صحول
# EKS Kubernetes Cluster Module for Sahool Platform
# ======================================================================
# تنشئ هذه الوحدة مجموعة EKS مع مجموعات عقد متعددة:
# This module creates an EKS cluster with multiple node groups:
# - System: للخدمات الأساسية (CoreDNS, NATS, Kong)
# - Worker: لخدمات التطبيقات (77 microservice)
# - GPU: لخدمات الرؤية الحاسوبية (YOLO26, crop-vision)
# ======================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# ======================================================================
# البيانات المحلية (Local Values)
# ======================================================================
locals {
  name_prefix = "${var.environment}-sahool"

  common_tags = merge(
    var.tags,
    {
      Project     = "sahool"
      Environment = var.environment
      ManagedBy   = "terraform"
      Module      = "eks"
    }
  )
}

# ======================================================================
# مفتاح KMS لتشفير أسرار EKS (KMS Key for EKS Secrets Encryption)
# ======================================================================
resource "aws_kms_key" "eks" {
  description             = "KMS key for EKS cluster ${var.cluster_name} secrets encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-eks-kms"
    }
  )
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.cluster_name}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# ======================================================================
# دور IAM لمجموعة EKS (IAM Role for EKS Cluster)
# ======================================================================
resource "aws_iam_role" "cluster" {
  name = "${var.cluster_name}-cluster-role"

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

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}

resource "aws_iam_role_policy_attachment" "cluster_vpc_resource_controller" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.cluster.name
}

# ======================================================================
# مجموعة أمان EKS (EKS Cluster Security Group)
# ======================================================================
resource "aws_security_group" "cluster" {
  name_prefix = "${var.cluster_name}-cluster-"
  description = "Security group for EKS cluster ${var.cluster_name} control plane"
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.cluster_name}-cluster-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# TODO(security): In production, restrict egress to specific CIDR ranges
# (e.g., VPC CIDR, ECR/S3 endpoints) instead of 0.0.0.0/0.
resource "aws_security_group_rule" "cluster_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.cluster.id
  description       = "Allow all outbound traffic from cluster"
}

resource "aws_security_group_rule" "cluster_ingress_nodes" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.nodes.id
  security_group_id        = aws_security_group.cluster.id
  description              = "Allow HTTPS from worker nodes"
}

# ======================================================================
# مجموعة أمان عقد EKS (EKS Node Security Group)
# ======================================================================
resource "aws_security_group" "nodes" {
  name_prefix = "${var.cluster_name}-nodes-"
  description = "Security group for EKS worker nodes in ${var.cluster_name}"
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name                                        = "${var.cluster_name}-nodes-sg"
      "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# TODO(security): In production, restrict egress to specific CIDR ranges
# (e.g., VPC CIDR, ECR/S3 endpoints, NAT gateway) instead of 0.0.0.0/0.
resource "aws_security_group_rule" "nodes_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.nodes.id
  description       = "Allow all outbound traffic from nodes"
}

resource "aws_security_group_rule" "nodes_ingress_self" {
  type                     = "ingress"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "-1"
  source_security_group_id = aws_security_group.nodes.id
  security_group_id        = aws_security_group.nodes.id
  description              = "Allow node-to-node communication"
}

resource "aws_security_group_rule" "nodes_ingress_cluster" {
  type                     = "ingress"
  from_port                = 1025
  to_port                  = 65535
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.cluster.id
  security_group_id        = aws_security_group.nodes.id
  description              = "Allow communication from cluster control plane"
}

resource "aws_security_group_rule" "nodes_ingress_cluster_https" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.cluster.id
  security_group_id        = aws_security_group.nodes.id
  description              = "Allow HTTPS from cluster control plane"
}

# ======================================================================
# مجموعة EKS Kubernetes (EKS Cluster)
# ======================================================================
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  version  = var.kubernetes_version
  role_arn = aws_iam_role.cluster.arn

  vpc_config {
    subnet_ids              = concat(var.private_subnet_ids, var.public_subnet_ids)
    endpoint_private_access = true
    endpoint_public_access  = var.endpoint_public_access
    public_access_cidrs     = var.public_access_cidrs
    security_group_ids      = [aws_security_group.cluster.id]
  }

  # تسجيل سجلات المجموعة في CloudWatch
  # Cluster logging to CloudWatch
  enabled_cluster_log_types = var.cluster_log_types

  # تشفير الأسرار باستخدام KMS
  # Secrets encryption using KMS
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = var.cluster_name
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_iam_role_policy_attachment.cluster_vpc_resource_controller,
  ]
}

# ======================================================================
# مزود هوية OIDC لـ IRSA (OIDC Identity Provider for IRSA)
# ======================================================================
# مطلوب لتمكين أدوار IAM لحسابات خدمة Kubernetes
# Required to enable IAM Roles for Kubernetes Service Accounts
data "tls_certificate" "eks" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = merge(
    local.common_tags,
    {
      Name = "${var.cluster_name}-oidc-provider"
    }
  )
}

# ======================================================================
# دور IAM لعقد EKS (IAM Role for EKS Nodes)
# ======================================================================
resource "aws_iam_role" "nodes" {
  name = "${var.cluster_name}-node-role"

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

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "nodes_worker_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.nodes.name
}

resource "aws_iam_role_policy_attachment" "nodes_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.nodes.name
}

resource "aws_iam_role_policy_attachment" "nodes_container_registry" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.nodes.name
}

resource "aws_iam_role_policy_attachment" "nodes_ssm_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.nodes.name
}

# ======================================================================
# قالب الإطلاق مع IMDSv2 (Launch Template with IMDSv2 enforcement)
# ======================================================================
# فرض استخدام IMDSv2 لمنع هجمات SSRF على بيانات الاعتماد
# Enforce IMDSv2 to prevent SSRF attacks on instance credentials
resource "aws_launch_template" "eks_nodes" {
  name_prefix = "${var.cluster_name}-node-"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  tag_specifications {
    resource_type = "instance"
    tags = merge(
      local.common_tags,
      {
        Name = "${var.cluster_name}-node"
      }
    )
  }
}

# ======================================================================
# مجموعة عقد النظام (System Node Group)
# ======================================================================
# عقد النظام لتشغيل الخدمات الأساسية مثل CoreDNS وKong وNATS
# System nodes for running core services like CoreDNS, Kong, and NATS
resource "aws_eks_node_group" "system" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-system"
  node_role_arn   = aws_iam_role.nodes.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = var.system_node_instance_types
  capacity_type  = "ON_DEMAND"

  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = "$Latest"
  }

  scaling_config {
    desired_size = var.system_node_desired_size
    max_size     = var.system_node_max_size
    min_size     = var.system_node_min_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    role        = "system"
    environment = var.environment
    workload    = "system"
  }

  taint {
    key    = "CriticalAddonsOnly"
    value  = "true"
    effect = "PREFER_NO_SCHEDULE"
  }

  tags = merge(
    local.common_tags,
    {
      Name     = "${var.cluster_name}-system-nodes"
      NodeType = "system"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.nodes_worker_policy,
    aws_iam_role_policy_attachment.nodes_cni_policy,
    aws_iam_role_policy_attachment.nodes_container_registry,
  ]
}

# ======================================================================
# مجموعة عقد العمال (Worker Node Group)
# ======================================================================
# عقد العمال لتشغيل خدمات التطبيقات الرئيسية
# Worker nodes for running main application services
resource "aws_eks_node_group" "worker" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-worker"
  node_role_arn   = aws_iam_role.nodes.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = var.worker_node_instance_types
  capacity_type  = var.worker_capacity_type

  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = "$Latest"
  }

  scaling_config {
    desired_size = var.worker_node_desired_size
    max_size     = var.worker_node_max_size
    min_size     = var.worker_node_min_size
  }

  update_config {
    max_unavailable_percentage = 25
  }

  labels = {
    role        = "worker"
    environment = var.environment
    workload    = "application"
  }

  tags = merge(
    local.common_tags,
    {
      Name     = "${var.cluster_name}-worker-nodes"
      NodeType = "worker"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.nodes_worker_policy,
    aws_iam_role_policy_attachment.nodes_cni_policy,
    aws_iam_role_policy_attachment.nodes_container_registry,
  ]
}

# ======================================================================
# مجموعة عقد GPU (GPU Node Group)
# ======================================================================
# عقد GPU لخدمات الرؤية الحاسوبية مثل YOLO26 وكشف الأمراض
# GPU nodes for computer vision services like YOLO26 and disease detection
resource "aws_eks_node_group" "gpu" {
  count = var.enable_gpu_nodes ? 1 : 0

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-gpu"
  node_role_arn   = aws_iam_role.nodes.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = var.gpu_node_instance_types
  capacity_type  = var.gpu_capacity_type

  ami_type = "AL2_x86_64_GPU"

  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = "$Latest"
  }

  scaling_config {
    desired_size = var.gpu_node_desired_size
    max_size     = var.gpu_node_max_size
    min_size     = var.gpu_node_min_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    role                              = "gpu"
    environment                       = var.environment
    workload                          = "gpu"
    "nvidia.com/gpu.present"          = "true"
    "sahool.io/vision-service"        = "true"
  }

  taint {
    key    = "nvidia.com/gpu"
    value  = "true"
    effect = "NO_SCHEDULE"
  }

  tags = merge(
    local.common_tags,
    {
      Name     = "${var.cluster_name}-gpu-nodes"
      NodeType = "gpu"
      Purpose  = "Vision services (YOLO26, crop-vision, pest-detection)"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.nodes_worker_policy,
    aws_iam_role_policy_attachment.nodes_cni_policy,
    aws_iam_role_policy_attachment.nodes_container_registry,
  ]
}

# ======================================================================
# مجموعة سجلات CloudWatch لمجموعة EKS
# CloudWatch Log Group for EKS Cluster
# ======================================================================
resource "aws_cloudwatch_log_group" "eks" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = var.cluster_log_retention_days

  tags = merge(
    local.common_tags,
    {
      Name = "${var.cluster_name}-logs"
    }
  )
}

# ======================================================================
# إضافات EKS (EKS Addons)
# ======================================================================
resource "aws_eks_addon" "vpc_cni" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "vpc-cni"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.common_tags
}

resource "aws_eks_addon" "coredns" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "coredns"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.common_tags

  depends_on = [aws_eks_node_group.system]
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "kube-proxy"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.common_tags
}

resource "aws_eks_addon" "ebs_csi_driver" {
  count = var.enable_ebs_csi_driver ? 1 : 0

  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "aws-ebs-csi-driver"
  resolve_conflicts_on_update = "OVERWRITE"
  service_account_role_arn    = aws_iam_role.ebs_csi[0].arn

  tags = local.common_tags
}

# ======================================================================
# دور IAM لسائق EBS CSI (IAM Role for EBS CSI Driver)
# ======================================================================
resource "aws_iam_role" "ebs_csi" {
  count = var.enable_ebs_csi_driver ? 1 : 0

  name = "${var.cluster_name}-ebs-csi-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}:aud" = "sts.amazonaws.com"
            "${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:kube-system:ebs-csi-controller-sa"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ebs_csi" {
  count = var.enable_ebs_csi_driver ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  role       = aws_iam_role.ebs_csi[0].name
}
