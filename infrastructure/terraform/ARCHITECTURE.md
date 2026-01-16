# البنية المعمارية لمنصة صحول - المملكة العربية السعودية

# Sahool Platform Architecture - Saudi Arabia

## نظرة عامة معمارية / Architectural Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    منصة صحول - البنية التحتية                          │
│                    Sahool Platform - Infrastructure                     │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────┐    ┌───────────────────────────────┐
│     الرياض / Riyadh           │◄───►│      جدة / Jeddah             │
│     (Primary Region)          │    │     (Secondary Region)        │
│                               │    │                               │
│  ┌─────────────────────────┐  │    │  ┌─────────────────────────┐  │
│  │   VPC 10.0.0.0/16       │  │    │  │   VPC 10.1.0.0/16       │  │
│  │                         │  │    │  │                         │  │
│  │  ┌──────────────────┐   │  │    │  │  ┌──────────────────┐   │  │
│  │  │  EKS Cluster     │   │  │    │  │  │  EKS Cluster     │   │  │
│  │  │  3-10 Nodes      │   │  │    │  │  │  2-8 Nodes       │   │  │
│  │  │  t3.xlarge       │   │  │    │  │  │  t3.large        │   │  │
│  │  └──────────────────┘   │  │    │  │  └──────────────────┘   │  │
│  │                         │  │    │  │                         │  │
│  │  ┌──────────────────┐   │  │    │  │  ┌──────────────────┐   │  │
│  │  │  RDS PostgreSQL  │   │  │    │  │  │  RDS PostgreSQL  │   │  │
│  │  │  + PostGIS       │   │  │    │  │  │  + PostGIS       │   │  │
│  │  │  db.r6g.xlarge   │   │  │    │  │  │  db.r6g.large    │   │  │
│  │  │  500 GB          │   │  │    │  │  │  300 GB          │   │  │
│  │  └──────────────────┘   │  │    │  │  └──────────────────┘   │  │
│  │                         │  │    │  │                         │  │
│  │  ┌──────────────────┐   │  │    │  │  ┌──────────────────┐   │  │
│  │  │  Redis Cache     │   │  │    │  │  │  Redis Cache     │   │  │
│  │  │  3 Nodes         │   │  │    │  │  │  2 Nodes         │   │  │
│  │  │  cache.r6g.large │   │  │    │  │  │  cache.r6g.large │   │  │
│  │  └──────────────────┘   │  │    │  │  └──────────────────┘   │  │
│  │                         │  │    │  │                         │  │
│  │  ┌──────────────────┐   │  │    │  │  ┌──────────────────┐   │  │
│  │  │  S3 Satellite    │   │  │───►│  │  │  S3 Satellite    │   │  │
│  │  │  Imagery         │   │  │    │  │  │  Imagery (Replica)│  │
│  │  └──────────────────┘   │  │    │  │  └──────────────────┘   │  │
│  │                         │  │    │  │                         │  │
│  │  ┌──────────────────┐   │  │    │  │  ┌──────────────────┐   │  │
│  │  │  S3 AI Models    │   │  │    │  │  │  S3 AI Models    │   │  │
│  │  └──────────────────┘   │  │    │  │  └──────────────────┘   │  │
│  └─────────────────────────┘  │    │  └─────────────────────────┘  │
│                               │    │                               │
└───────────────────────────────┘    └───────────────────────────────┘
         │                                      │
         └──────────────VPC Peering─────────────┘
```

## المكونات الرئيسية / Main Components

### 1. الشبكات / Networking

#### VPC (Virtual Private Cloud)

- **الرياض:** 10.0.0.0/16
- **جدة:** 10.1.0.0/16
- **مناطق التوفر:** 3 AZs في كل منطقة
- **الشبكات الفرعية:**
  - عامة (Public): للموازنات وNAT Gateways
  - خاصة (Private): للتطبيقات والخدمات
  - قواعد البيانات: شبكة منعزلة لقواعد البيانات

#### NAT Gateways

- NAT Gateway في كل منطقة توفر
- توفر عالي ومرونة

#### VPC Peering

- اتصال آمن بين الرياض وجدة
- تمكين التواصل بين المناطق

### 2. الحوسبة / Compute

#### Amazon EKS (Elastic Kubernetes Service)

**الرياض (Primary):**

```yaml
Cluster Name: production-sahool-riyadh
Kubernetes Version: 1.28
Node Type: t3.xlarge (4 vCPUs, 16 GB RAM)
Node Count:
  Minimum: 3
  Maximum: 10
  Desired: 5
Features:
  - Auto Scaling
  - Multi-AZ deployment
  - Enhanced logging
  - Secrets encryption with KMS
```

**جدة (Secondary):**

```yaml
Cluster Name: production-sahool-jeddah
Kubernetes Version: 1.28
Node Type: t3.large (2 vCPUs, 8 GB RAM)
Node Count:
  Minimum: 2
  Maximum: 8
  Desired: 3
Features:
  - Auto Scaling
  - Multi-AZ deployment
  - Enhanced logging
  - Secrets encryption with KMS
```

### 3. قواعد البيانات / Databases

#### Amazon RDS PostgreSQL 15 + PostGIS

**الرياض:**

```yaml
Instance Class: db.r6g.xlarge (4 vCPUs, 32 GB RAM)
Storage: 500 GB (gp3)
Engine: PostgreSQL 15.4
Extensions: PostGIS, pg_stat_statements
Features:
  - Multi-AZ deployment
  - Automated backups (30 days)
  - Encrypted at rest (KMS)
  - Encrypted in transit (SSL/TLS)
  - CloudWatch Logs integration
```

**جدة:**

```yaml
Instance Class: db.r6g.large (2 vCPUs, 16 GB RAM)
Storage: 300 GB (gp3)
Engine: PostgreSQL 15.4
Extensions: PostGIS, pg_stat_statements
Features:
  - Multi-AZ deployment
  - Automated backups (30 days)
  - Encrypted at rest (KMS)
  - Encrypted in transit (SSL/TLS)
  - CloudWatch Logs integration
```

**PostGIS للبيانات الجغرافية:**

- تخزين حدود الحقول الزراعية
- معالجة الصور الفضائية
- تحليل الموقع الجغرافي
- حسابات المسافة والمساحة

### 4. الذاكرة المؤقتة / Caching

#### Amazon ElastiCache Redis 7.0

**الرياض:**

```yaml
Node Type: cache.r6g.large (2 vCPUs, 13.07 GB RAM)
Nodes: 3
Features:
  - Cluster mode enabled
  - Automatic failover
  - Encrypted at rest
  - Encrypted in transit
  - Auth token enabled
```

**جدة:**

```yaml
Node Type: cache.r6g.large (2 vCPUs, 13.07 GB RAM)
Nodes: 2
Features:
  - Cluster mode enabled
  - Automatic failover
  - Encrypted at rest
  - Encrypted in transit
  - Auth token enabled
```

**حالات الاستخدام:**

- ذاكرة مؤقتة للاستعلامات
- جلسات المستخدمين
- قوائم انتظار المهام (Job Queues)
- البيانات المؤقتة للنماذج

### 5. التخزين / Storage

#### Amazon S3

**حاوية الصور الفضائية (Satellite Imagery):**

```yaml
الرياض: sahool-satellite-imagery-riyadh-production
جدة: sahool-satellite-imagery-jeddah-production

Features:
  - Versioning enabled
  - Server-side encryption (KMS)
  - Lifecycle policies:
    * 90 days → Standard-IA
    * 180 days → Glacier
    * 730 days → Deletion
  - Cross-region replication (Riyadh → Jeddah)
```

**حاوية النماذج (AI Models):**

```yaml
الرياض: sahool-ai-models-riyadh-production
جدة: sahool-ai-models-jeddah-production

Features:
  - Versioning enabled
  - Server-side encryption (KMS)
  - Model artifacts storage
  - Training data storage
```

### 6. الأمان / Security

#### التشفير / Encryption

```yaml
At Rest:
  - RDS: KMS encryption
  - S3: KMS encryption
  - EBS: Encrypted volumes
  - ElastiCache: Encrypted data

In Transit:
  - RDS: SSL/TLS
  - ElastiCache: TLS
  - S3: HTTPS
  - EKS: TLS between components
```

#### مجموعات الأمان / Security Groups

```yaml
EKS:
  - Ingress: من Load Balancers
  - Egress: إلى الإنترنت، RDS، Redis

RDS:
  - Ingress: من EKS فقط (port 5432)
  - Egress: محدود

Redis:
  - Ingress: من EKS فقط (port 6379)
  - Egress: محدود
```

#### IAM Roles

```yaml
EKS Cluster Role:
  - AmazonEKSClusterPolicy
  - AmazonEKSVPCResourceController

EKS Node Role:
  - AmazonEKSWorkerNodePolicy
  - AmazonEKS_CNI_Policy
  - AmazonEC2ContainerRegistryReadOnly
  - Custom S3 access policy
```

## تدفق البيانات / Data Flow

### 1. تدفق الطلبات / Request Flow

```
المستخدم → Route 53 → ALB → EKS Pods → RDS/Redis
User → Route 53 → ALB → EKS Pods → RDS/Redis
```

### 2. تدفق الصور الفضائية / Satellite Imagery Flow

```
1. تحميل إلى S3 الرياض
   Upload to S3 Riyadh
   ↓
2. نسخ متماثل تلقائي إلى S3 جدة
   Automatic replication to S3 Jeddah
   ↓
3. معالجة بواسطة نماذج الذكاء الاصطناعي
   Processing by AI models
   ↓
4. تخزين النتائج في RDS
   Store results in RDS
```

### 3. النسخ الاحتياطي / Backup Flow

```
RDS Riyadh → Automated Snapshots (30 days)
           → Manual Snapshots (on-demand)

S3 Riyadh → Cross-region replication → S3 Jeddah
          → Glacier Archive (180 days)
```

## التوسع / Scalability

### التوسع الأفقي / Horizontal Scaling

- **EKS:** توسع تلقائي من 3-10 عقد (الرياض)
- **EKS:** توسع تلقائي من 2-8 عقد (جدة)
- **RDS:** Read Replicas (يمكن إضافتها)

### التوسع الرأسي / Vertical Scaling

- **EKS Nodes:** يمكن تغيير نوع المثيل
- **RDS:** يمكن ترقية فئة المثيل
- **Redis:** يمكن ترقية نوع العقدة

## التوفر العالي / High Availability

### استراتيجيات التوفر / Availability Strategies

1. **Multi-AZ Deployment** في كل خدمة
2. **منطقتين جغرافيتين** (الرياض، جدة)
3. **نسخ متماثل** للبيانات الحرجة
4. **Automatic Failover** لـ RDS و Redis
5. **Load Balancing** للتطبيقات

### أوقات التعافي المستهدفة / Recovery Time Objectives

```yaml
RTO (Recovery Time Objective):
  - EKS Pods: < 5 minutes
  - RDS Failover: < 2 minutes
  - Redis Failover: < 1 minute
  - Cross-region: < 15 minutes

RPO (Recovery Point Objective):
  - RDS: 5 minutes (automated backups)
  - S3: Real-time replication
```

## المراقبة / Monitoring

### CloudWatch Metrics

```yaml
EKS:
  - CPU Utilization
  - Memory Utilization
  - Pod count
  - Node status

RDS:
  - CPU Utilization
  - Database Connections
  - Read/Write IOPS
  - Storage usage

Redis:
  - CPU Utilization
  - Memory Utilization
  - Cache Hit Rate
  - Evictions
```

### CloudWatch Logs

```yaml
EKS:
  - API server logs
  - Audit logs
  - Controller Manager logs
  - Scheduler logs

RDS:
  - PostgreSQL logs
  - Slow query logs
  - Error logs
```

## التكلفة التقديرية / Cost Estimation

### التكلفة الشهرية (بالدولار) / Monthly Cost (USD)

| المكون / Component    | الرياض / Riyadh  | جدة / Jeddah     | الإجمالي / Total |
| --------------------- | ---------------- | ---------------- | ---------------- |
| EKS Control Plane     | $75              | $75              | $150             |
| EC2 Nodes             | $600             | $300             | $900             |
| RDS PostgreSQL        | $400             | $200             | $600             |
| ElastiCache Redis     | $200             | $150             | $350             |
| NAT Gateways          | $100             | $100             | $200             |
| S3 Storage & Transfer | متغير / Variable | متغير / Variable | ~$200            |
| Data Transfer         | ~$50             | ~$50             | ~$100            |
| **الإجمالي / Total**  | **~$1,425**      | **~$875**        | **~$2,500**      |

_ملاحظة: التكاليف تقريبية وتعتمد على الاستخدام الفعلي_

### خيارات توفير التكلفة / Cost Optimization Options

1. **Reserved Instances** لـ RDS و ElastiCache (توفير ~40%)
2. **Savings Plans** لـ EC2 (توفير ~30%)
3. **S3 Intelligent-Tiering** للصور القديمة
4. **Spot Instances** لمهام المعالجة غير الحرجة

## أفضل الممارسات المطبقة / Best Practices Applied

### الأمان / Security

✅ تشفير شامل للبيانات
✅ مفاتيح KMS منفصلة لكل خدمة
✅ شبكات خاصة معزولة
✅ مجموعات أمان محكمة
✅ IAM Roles بصلاحيات محدودة

### الموثوقية / Reliability

✅ Multi-AZ deployment
✅ نسخ احتياطية تلقائية
✅ Automatic failover
✅ Health checks
✅ منطقتين للـ DR

### الأداء / Performance

✅ ذاكرة مؤقتة (Redis)
✅ توسع تلقائي
✅ Read replicas (قابل للإضافة)
✅ أحجام مثيلات محسّنة

### الكفاءة / Efficiency

✅ موارد محسّنة حسب الحمل
✅ توسع تلقائي
✅ سياسات دورة حياة S3
✅ مراقبة التكلفة

---

**التحديث الأخير / Last Updated:** 2026-01-02
**الإصدار / Version:** 1.0.0
