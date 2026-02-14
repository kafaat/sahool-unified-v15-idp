# ======================================================================
# مخرجات وحدة مجموعة EKS Kubernetes
# EKS Kubernetes Cluster Module Outputs
# ======================================================================

# ======================================================================
# مخرجات المجموعة (Cluster Outputs)
# ======================================================================
output "cluster_id" {
  description = "معرّف مجموعة EKS / EKS cluster ID"
  value       = aws_eks_cluster.main.id
}

output "cluster_name" {
  description = "اسم مجموعة EKS / EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "نقطة نهاية مجموعة EKS / EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_version" {
  description = "إصدار Kubernetes لمجموعة EKS / EKS cluster Kubernetes version"
  value       = aws_eks_cluster.main.version
}

output "cluster_arn" {
  description = "ARN لمجموعة EKS / EKS cluster ARN"
  value       = aws_eks_cluster.main.arn
}

output "cluster_certificate_authority_data" {
  description = "بيانات شهادة CA لمجموعة EKS / EKS cluster CA certificate data"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "cluster_platform_version" {
  description = "إصدار منصة EKS / EKS platform version"
  value       = aws_eks_cluster.main.platform_version
}

# ======================================================================
# مخرجات OIDC (OIDC Outputs)
# ======================================================================
output "oidc_provider_arn" {
  description = "ARN لمزود هوية OIDC / OIDC identity provider ARN"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "oidc_provider_url" {
  description = "رابط مزود هوية OIDC / OIDC identity provider URL"
  value       = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

output "oidc_provider_id" {
  description = "معرّف مزود هوية OIDC (بدون بروتوكول) / OIDC provider ID (without protocol)"
  value       = replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")
}

# ======================================================================
# مخرجات مجموعات الأمان (Security Group Outputs)
# ======================================================================
output "cluster_security_group_id" {
  description = "معرّف مجموعة أمان مجموعة EKS / EKS cluster security group ID"
  value       = aws_security_group.cluster.id
}

output "node_security_group_id" {
  description = "معرّف مجموعة أمان عقد EKS / EKS node security group ID"
  value       = aws_security_group.nodes.id
}

# ======================================================================
# مخرجات أدوار IAM (IAM Role Outputs)
# ======================================================================
output "cluster_role_arn" {
  description = "ARN لدور IAM لمجموعة EKS / EKS cluster IAM role ARN"
  value       = aws_iam_role.cluster.arn
}

output "node_role_arn" {
  description = "ARN لدور IAM لعقد EKS / EKS node IAM role ARN"
  value       = aws_iam_role.nodes.arn
}

output "node_role_name" {
  description = "اسم دور IAM لعقد EKS / EKS node IAM role name"
  value       = aws_iam_role.nodes.name
}

# ======================================================================
# مخرجات مجموعات العقد (Node Group Outputs)
# ======================================================================
output "system_node_group_id" {
  description = "معرّف مجموعة عقد النظام / System node group ID"
  value       = aws_eks_node_group.system.id
}

output "worker_node_group_id" {
  description = "معرّف مجموعة عقد العمال / Worker node group ID"
  value       = aws_eks_node_group.worker.id
}

output "gpu_node_group_id" {
  description = "معرّف مجموعة عقد GPU / GPU node group ID"
  value       = var.enable_gpu_nodes ? aws_eks_node_group.gpu[0].id : null
}

# ======================================================================
# مخرجات التشفير (Encryption Outputs)
# ======================================================================
output "kms_key_arn" {
  description = "ARN لمفتاح KMS لتشفير أسرار EKS / KMS key ARN for EKS secrets encryption"
  value       = aws_kms_key.eks.arn
}

output "kms_key_id" {
  description = "معرّف مفتاح KMS لتشفير أسرار EKS / KMS key ID for EKS secrets encryption"
  value       = aws_kms_key.eks.key_id
}

# ======================================================================
# مخرجات الاتصال (Connection Outputs)
# ======================================================================
output "kubeconfig_command" {
  description = "أمر تحديث kubeconfig للاتصال بالمجموعة / Command to update kubeconfig for cluster connection"
  value       = "aws eks update-kubeconfig --region ${data.aws_region.current.name} --name ${aws_eks_cluster.main.name}"
}

# بيانات المنطقة الحالية
# Current region data
data "aws_region" "current" {}
