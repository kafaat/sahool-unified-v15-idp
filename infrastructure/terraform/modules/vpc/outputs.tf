# ======================================================================
# مخرجات وحدة الشبكة الافتراضية الخاصة
# VPC Module Outputs
# ======================================================================

# ======================================================================
# مخرجات VPC (VPC Outputs)
# ======================================================================
output "vpc_id" {
  description = "معرّف الشبكة الافتراضية / VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "نطاق CIDR للشبكة الافتراضية / VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "vpc_arn" {
  description = "ARN للشبكة الافتراضية / VPC ARN"
  value       = aws_vpc.main.arn
}

# ======================================================================
# مخرجات الشبكات الفرعية (Subnet Outputs)
# ======================================================================
output "public_subnet_ids" {
  description = "قائمة معرّفات الشبكات الفرعية العامة / List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "public_subnet_cidr_blocks" {
  description = "قائمة نطاقات CIDR للشبكات الفرعية العامة / List of public subnet CIDR blocks"
  value       = aws_subnet.public[*].cidr_block
}

output "private_subnet_ids" {
  description = "قائمة معرّفات الشبكات الفرعية الخاصة / List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "private_subnet_cidr_blocks" {
  description = "قائمة نطاقات CIDR للشبكات الفرعية الخاصة / List of private subnet CIDR blocks"
  value       = aws_subnet.private[*].cidr_block
}

output "database_subnet_ids" {
  description = "قائمة معرّفات شبكات قواعد البيانات / List of database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "database_subnet_cidr_blocks" {
  description = "قائمة نطاقات CIDR لشبكات قواعد البيانات / List of database subnet CIDR blocks"
  value       = aws_subnet.database[*].cidr_block
}

# ======================================================================
# مخرجات بوابات NAT (NAT Gateway Outputs)
# ======================================================================
output "nat_gateway_ids" {
  description = "قائمة معرّفات بوابات NAT / List of NAT gateway IDs"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = "قائمة عناوين IP العامة لبوابات NAT / List of NAT gateway public IPs"
  value       = aws_eip.nat[*].public_ip
}

# ======================================================================
# مخرجات جداول التوجيه (Route Table Outputs)
# ======================================================================
output "public_route_table_id" {
  description = "معرّف جدول التوجيه العام / Public route table ID"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "قائمة معرّفات جداول التوجيه الخاصة / List of private route table IDs"
  value       = aws_route_table.private[*].id
}

output "database_route_table_id" {
  description = "معرّف جدول توجيه قواعد البيانات / Database route table ID"
  value       = aws_route_table.database.id
}

# ======================================================================
# مخرجات نقاط نهاية VPC (VPC Endpoint Outputs)
# ======================================================================
output "s3_endpoint_id" {
  description = "معرّف نقطة نهاية S3 / S3 VPC endpoint ID"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.s3[0].id : null
}

output "vpc_endpoint_security_group_id" {
  description = "معرّف مجموعة أمان نقاط نهاية VPC / VPC endpoints security group ID"
  value       = aws_security_group.vpc_endpoints.id
}

# ======================================================================
# مخرجات بوابة الإنترنت (Internet Gateway Outputs)
# ======================================================================
output "internet_gateway_id" {
  description = "معرّف بوابة الإنترنت / Internet gateway ID"
  value       = aws_internet_gateway.main.id
}

# ======================================================================
# مخرجات مجمّعة (Aggregated Outputs)
# ======================================================================
output "subnet_ids" {
  description = "جميع معرّفات الشبكات الفرعية مجمّعة حسب النوع / All subnet IDs grouped by tier"
  value = {
    public   = aws_subnet.public[*].id
    private  = aws_subnet.private[*].id
    database = aws_subnet.database[*].id
  }
}

output "availability_zones" {
  description = "قائمة مناطق التوفر المستخدمة / List of availability zones used"
  value       = var.availability_zones
}
