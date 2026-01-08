# 💰 دليل تحسين التكاليف - منصة سهول
# Cost Optimization Guide - Sahool Platform

## 📊 نظرة عامة / Overview

هذا الدليل يقدم استراتيجيات لتحسين تكاليف البنية التحتية مع الحفاظ على الأداء والموثوقية.

---

## 🎯 استراتيجيات التحسين / Optimization Strategies

### 1. Spot Instances / الموارد الفورية

```yaml
# EKS Node Group with Spot Instances
# 70% Spot + 30% On-Demand للموثوقية
nodeGroups:
  - name: sahool-spot-workers
    instanceTypes:
      - m5.large
      - m5.xlarge
      - m5a.large
    capacityType: SPOT
    desiredCapacity: 5
    minSize: 2
    maxSize: 20
    labels:
      workload-type: spot-tolerant
    taints:
      - key: spot-instance
        value: "true"
        effect: PreferNoSchedule
```

**التوفير المتوقع**: 60-70% من تكلفة On-Demand

### 2. Reserved Instances / الموارد المحجوزة

| الخدمة | النوع | المدة | التوفير |
|--------|-------|-------|---------|
| RDS | Reserved | 1 سنة | 35% |
| ElastiCache | Reserved | 1 سنة | 30% |
| EKS | Savings Plan | 1 سنة | 20% |

### 3. Right-Sizing / تحجيم صحيح

```bash
# تحليل استخدام الموارد
kubectl top pods -n sahool --sort-by=cpu
kubectl top pods -n sahool --sort-by=memory

# توصيات VPA (Vertical Pod Autoscaler)
kubectl get vpa -n sahool -o yaml
```

### 4. Auto-Scaling / التوسع التلقائي

```yaml
# Cluster Autoscaler تكوين
autoscaling:
  enabled: true
  # تقليص إلى 0 في غير أوقات الذروة
  minNodes: 0
  maxNodes: 20
  # تأخير التقليص لتجنب التذبذب
  scaleDownDelayAfterAdd: 10m
  scaleDownUnneededTime: 10m
```

---

## ⏰ جدولة التشغيل / Scheduling

### إيقاف بيئة التطوير ليلاً

```yaml
# CronJob لإيقاف Staging ليلاً
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-staging
  namespace: sahool-staging
spec:
  # كل يوم الساعة 10 مساءً (KSA)
  schedule: "0 19 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: kubectl
              image: bitnami/kubectl:latest
              command:
                - /bin/sh
                - -c
                - |
                  kubectl scale deployment --all -n sahool-staging --replicas=0
          restartPolicy: OnFailure
---
# CronJob لإعادة التشغيل صباحاً
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-up-staging
  namespace: sahool-staging
spec:
  # كل يوم الساعة 8 صباحاً (KSA)
  schedule: "0 5 * * 0-4"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: kubectl
              image: bitnami/kubectl:latest
              command:
                - /bin/sh
                - -c
                - |
                  kubectl scale deployment --all -n sahool-staging --replicas=1
          restartPolicy: OnFailure
```

---

## 💾 تحسين التخزين / Storage Optimization

### S3 Lifecycle Policies

```json
{
  "Rules": [
    {
      "ID": "SatelliteImageryLifecycle",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "satellite/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    },
    {
      "ID": "LogsLifecycle",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
```

### EBS Optimization

| التخزين | الاستخدام | التوفير |
|---------|----------|---------|
| gp3 بدلاً من gp2 | جميع الـ PVs | 20% |
| sc1 للأرشيف | البيانات القديمة | 50% |
| حذف Snapshots قديمة | > 90 يوم | متغير |

---

## 📈 المراقبة والتقارير / Monitoring & Reporting

### AWS Cost Explorer Query

```bash
# تقرير التكاليف الشهري
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" "UnblendedCost" \
  --group-by Type=TAG,Key=Project
```

### Kubecost Dashboard

```yaml
# تثبيت Kubecost
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost \
  --create-namespace \
  --set kubecostToken="YOUR_TOKEN"
```

---

## 📋 قائمة التحقق الشهرية / Monthly Checklist

- [ ] مراجعة تقرير AWS Cost Explorer
- [ ] تحليل Kubecost recommendations
- [ ] حذف الموارد غير المستخدمة
- [ ] مراجعة Reserved Instances
- [ ] تحديث حدود Auto-Scaling
- [ ] تنظيف S3 والـ ECR
- [ ] مراجعة EBS Snapshots

---

## 🎯 أهداف التوفير / Savings Targets

| الربع | الهدف | الفعلي | الحالة |
|-------|-------|--------|--------|
| Q1 | 20% | - | - |
| Q2 | 25% | - | - |
| Q3 | 30% | - | - |
| Q4 | 35% | - | - |

---

## 🔧 أدوات مفيدة / Useful Tools

1. **AWS Cost Explorer** - تحليل التكاليف
2. **Kubecost** - تكاليف Kubernetes
3. **Spot.io** - إدارة Spot Instances
4. **Goldilocks** - توصيات VPA
5. **kube-resource-report** - تقارير الموارد
