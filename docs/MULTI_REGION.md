# Multi-Region / Multi-Cluster Deployment | النشر متعدد المناطق

## نظرة عامة | Overview

منصة سهول مصممة للنشر في بيئات HCI (Hyper-Converged Infrastructure) متعددة المناطق، مع دعم:
- نشر على عناقيد Kubernetes متعددة
- تكرار البيانات عبر المناطق
- التحويل التلقائي للخدمات (Failover)
- تزامن الإعدادات عبر GitOps

---

## البنية المعمارية | Architecture

```
                    ┌─────────────────────────────────────┐
                    │           Argo CD (Central)         │
                    │         مصدر الحقيقة الوحيد          │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   Region: Tihama    │ │   Region: Highlands │ │  Region: Hadramout  │
│   منطقة: تهامة      │ │   منطقة: المرتفعات  │ │   منطقة: حضرموت     │
│                     │ │                     │ │                     │
│  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │
│  │  k3s Cluster  │  │ │  │  k3s Cluster  │  │ │  │  k3s Cluster  │  │
│  │   (Primary)   │  │ │  │   (Primary)   │  │ │  │   (Primary)   │  │
│  └───────────────┘  │ │  └───────────────┘  │ │  └───────────────┘  │
│                     │ │                     │ │                     │
│  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │
│  │   PostgreSQL  │  │ │  │   PostgreSQL  │  │ │  │   PostgreSQL  │  │
│  │   (Leader)    │◀─┼─┼──│   (Replica)   │──┼─┼─▶│   (Replica)   │  │
│  └───────────────┘  │ │  └───────────────┘  │ │  └───────────────┘  │
│                     │ │                     │ │                     │
│  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │
│  │     Redis     │◀─┼─┼──│     Redis     │──┼─┼─▶│     Redis     │  │
│  │   (Primary)   │  │ │  │   (Replica)   │  │ │  │   (Replica)   │  │
│  └───────────────┘  │ │  └───────────────┘  │ │  └───────────────┘  │
│                     │ │                     │ │                     │
│  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │
│  │  NATS Cluster │◀─┼─┼──│  NATS Cluster │──┼─┼─▶│  NATS Cluster │  │
│  │   (Gateway)   │  │ │  │   (Gateway)   │  │ │  │   (Gateway)   │  │
│  └───────────────┘  │ │  └───────────────┘  │ │  └───────────────┘  │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## المناطق الزراعية اليمنية | Yemen Agricultural Regions

| المنطقة | Region ID | المحافظات | الخصائص |
|---------|-----------|----------|---------|
| **تهامة** | `tihama` | الحديدة، المحويت | ساحلي، زراعة مكثفة |
| **المرتفعات** | `highlands` | صنعاء، إب، تعز، ذمار | جبلي، مدرجات زراعية |
| **حضرموت** | `hadramout` | حضرموت، المهرة، شبوة | صحراوي، نخيل التمور |
| **الجوف** | `jawf` | الجوف، مأرب | شبه صحراوي |

---

## إعداد العناقيد | Cluster Setup

### 1. تسجيل العناقيد في Argo CD

```bash
# إضافة عنقود جديد
argocd cluster add k3s-tihama \
  --name sahool-tihama \
  --kubeconfig /path/to/kubeconfig-tihama

argocd cluster add k3s-highlands \
  --name sahool-highlands \
  --kubeconfig /path/to/kubeconfig-highlands

argocd cluster add k3s-hadramout \
  --name sahool-hadramout \
  --kubeconfig /path/to/kubeconfig-hadramout
```

### 2. تسمية العناقيد (Labels)

```yaml
# تسمية لكل عنقود
apiVersion: v1
kind: Secret
metadata:
  name: sahool-tihama
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
    sahool/enabled: "true"
    sahool/region: "tihama"
    sahool/tier: "production"
    sahool/priority: "primary"
```

---

## ApplicationSet للنشر المتعدد | Multi-Cluster ApplicationSet

### الموقع: `/gitops/argocd/applicationsets/multi-cluster.yaml`

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: sahool-multicluster
  namespace: argocd
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            sahool/enabled: "true"
        values:
          region: '{{metadata.labels.sahool/region}}'
          tier: '{{metadata.labels.sahool/tier}}'
  template:
    metadata:
      name: 'sahool-{{name}}'
      labels:
        region: '{{values.region}}'
    spec:
      project: sahool
      source:
        repoURL: '${REPO_URL}'
        targetRevision: HEAD
        path: k8s/helm/sahool-kernel
        helm:
          valueFiles:
            - values.yaml
            - 'values-{{values.region}}.yaml'
          parameters:
            - name: global.region
              value: '{{values.region}}'
            - name: global.cluster
              value: '{{name}}'
      destination:
        server: '{{server}}'
        namespace: sahool
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

---

## ملفات القيم حسب المنطقة | Region-Specific Values

### values-tihama.yaml

```yaml
global:
  region: tihama
  timezone: Asia/Aden
  language: ar

# خدمات محددة للمنطقة
irrigation:
  enabled: true
  mode: intensive
  defaultSchedule: "0 5,17 * * *"  # صباحاً ومساءً

weather:
  stations:
    - hodeidah-central
    - zabid-agricultural
    - bajil-coastal

crops:
  primary:
    - cotton
    - sorghum
    - mango
    - banana

postgresql:
  replication:
    role: primary
    replicaCount: 2

redis:
  sentinel:
    enabled: true
    masterSet: tihama-master
```

### values-highlands.yaml

```yaml
global:
  region: highlands
  timezone: Asia/Aden
  language: ar

irrigation:
  enabled: true
  mode: terraced
  defaultSchedule: "0 6 * * *"

weather:
  stations:
    - sanaa-central
    - ibb-agricultural
    - taiz-highland

crops:
  primary:
    - wheat
    - barley
    - qat
    - coffee
    - grapes

postgresql:
  replication:
    role: replica
    primaryHost: postgresql.tihama.sahool.local

redis:
  sentinel:
    enabled: true
    masterSet: tihama-master
```

### values-hadramout.yaml

```yaml
global:
  region: hadramout
  timezone: Asia/Aden
  language: ar

irrigation:
  enabled: true
  mode: drip
  defaultSchedule: "0 4 * * *"

weather:
  stations:
    - mukalla-central
    - seiyun-valley
    - tarim-oasis

crops:
  primary:
    - dates
    - palm
    - tobacco

postgresql:
  replication:
    role: replica
    primaryHost: postgresql.tihama.sahool.local

redis:
  sentinel:
    enabled: true
    masterSet: tihama-master
```

---

## تكرار قاعدة البيانات | Database Replication

### PostgreSQL Cross-Region Replication

```yaml
# Primary (Tihama)
postgresql:
  architecture: replication
  primary:
    resources:
      requests:
        memory: 2Gi
        cpu: 1000m
    persistence:
      size: 100Gi

  readReplicas:
    replicaCount: 2
    resources:
      requests:
        memory: 1Gi
        cpu: 500m

  replication:
    synchronousCommit: "on"
    numSynchronousReplicas: 1

  # Cross-region replicas
  externalReplicas:
    - host: postgresql.highlands.sahool.local
      port: 5432
      async: true
    - host: postgresql.hadramout.sahool.local
      port: 5432
      async: true
```

### Patroni Configuration

```yaml
# patroni-config.yaml
scope: sahool-postgres-cluster
name: postgresql-tihama-0

bootstrap:
  dcs:
    synchronous_mode: true
    synchronous_node_count: 1
    postgresql:
      use_pg_rewind: true
      parameters:
        max_wal_senders: 10
        wal_keep_size: 1GB
        hot_standby: "on"
        wal_log_hints: "on"

  initdb:
    - encoding: UTF8
    - data-checksums

standby_cluster:
  host: postgresql.tihama.sahool.local
  port: 5432
  create_replica_methods:
    - basebackup
```

---

## تكرار Redis | Redis Replication

### Redis Sentinel Cross-Region

```yaml
# redis-sentinel.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-sentinel-config
data:
  sentinel.conf: |
    sentinel monitor tihama-master redis-primary.tihama.sahool.local 6379 2
    sentinel down-after-milliseconds tihama-master 5000
    sentinel failover-timeout tihama-master 10000
    sentinel parallel-syncs tihama-master 1

    # Cross-region monitoring
    sentinel known-replica tihama-master redis.highlands.sahool.local 6379
    sentinel known-replica tihama-master redis.hadramout.sahool.local 6379
```

---

## تزامن NATS | NATS Synchronization

### NATS Super-Cluster with Gateways

```conf
# nats-gateway.conf (Tihama)
gateway {
  name: sahool-tihama
  listen: 0.0.0.0:7222

  tls {
    cert_file: "/etc/nats/certs/server.crt"
    key_file: "/etc/nats/certs/server.key"
    ca_file: "/etc/nats/certs/ca.crt"
  }

  gateways: [
    {
      name: sahool-highlands
      urls: [
        "nats://nats.highlands.sahool.local:7222"
      ]
    },
    {
      name: sahool-hadramout
      urls: [
        "nats://nats.hadramout.sahool.local:7222"
      ]
    }
  ]
}
```

---

## استراتيجية التحويل | Failover Strategy

### DNS-based Failover

```yaml
# ExternalDNS configuration
apiVersion: externaldns.k8s.io/v1alpha1
kind: DNSEndpoint
metadata:
  name: sahool-api-geo
spec:
  endpoints:
    - dnsName: api.sahool.io
      recordType: A
      targets:
        - 10.0.1.100  # Tihama
        - 10.0.2.100  # Highlands
        - 10.0.3.100  # Hadramout
      setIdentifier: tihama
      recordTTL: 60
      providerSpecific:
        - name: aws/geolocation-country-code
          value: YE
        - name: aws/health-check-id
          value: tihama-health-check
```

### Health Check Configuration

```yaml
# Health check for each region
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sahool-healthcheck
  annotations:
    nginx.ingress.kubernetes.io/health-check-path: /healthz
    nginx.ingress.kubernetes.io/health-check-interval: 10s
spec:
  rules:
    - host: health.tihama.sahool.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: kong-proxy
                port:
                  number: 80
```

---

## المراقبة عبر المناطق | Cross-Region Monitoring

### Prometheus Federation

```yaml
# prometheus-federation.yaml
scrape_configs:
  - job_name: 'federate-tihama'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job=~"sahool.*"}'
    static_configs:
      - targets:
          - 'prometheus.tihama.sahool.local:9090'
        labels:
          region: 'tihama'

  - job_name: 'federate-highlands'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job=~"sahool.*"}'
    static_configs:
      - targets:
          - 'prometheus.highlands.sahool.local:9090'
        labels:
          region: 'highlands'

  - job_name: 'federate-hadramout'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job=~"sahool.*"}'
    static_configs:
      - targets:
          - 'prometheus.hadramout.sahool.local:9090'
        labels:
          region: 'hadramout'
```

### Grafana Multi-Region Dashboard

```json
{
  "title": "SAHOOL Multi-Region Overview",
  "panels": [
    {
      "title": "Requests by Region",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[5m])) by (region)",
          "legendFormat": "{{region}}"
        }
      ]
    },
    {
      "title": "Replication Lag",
      "targets": [
        {
          "expr": "pg_replication_lag_seconds",
          "legendFormat": "{{region}}"
        }
      ]
    },
    {
      "title": "Service Health by Region",
      "targets": [
        {
          "expr": "up{job=~'sahool.*'}",
          "legendFormat": "{{region}}/{{service}}"
        }
      ]
    }
  ]
}
```

---

## Terraform للبنية التحتية | Infrastructure as Code

### الموقع: `/infrastructure/terraform/`

```hcl
# main.tf
module "region_tihama" {
  source = "./modules/region"

  region_name    = "tihama"
  region_id      = "ye-tihama-1"
  is_primary     = true

  kubernetes = {
    version = "1.28"
    nodes   = 3
  }

  postgresql = {
    instance_type = "db.r6g.large"
    storage_gb    = 100
    multi_az      = true
  }

  redis = {
    node_type      = "cache.r6g.large"
    num_cache_nodes = 3
  }
}

module "region_highlands" {
  source = "./modules/region"

  region_name    = "highlands"
  region_id      = "ye-highlands-1"
  is_primary     = false

  primary_region = module.region_tihama

  # Same configuration...
}

module "region_hadramout" {
  source = "./modules/region"

  region_name    = "hadramout"
  region_id      = "ye-hadramout-1"
  is_primary     = false

  primary_region = module.region_tihama

  # Same configuration...
}
```

---

## HCI Conventions | اتفاقيات البنية التحتية

### k3s on Bare Metal

```bash
# تثبيت k3s على العقدة الأساسية
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --disable traefik \
  --disable servicelb \
  --node-label region=tihama \
  --node-label role=control-plane

# إضافة عقد عاملة
curl -sfL https://get.k3s.io | K3S_URL=https://master:6443 \
  K3S_TOKEN=xxxxx sh -s - agent \
  --node-label region=tihama \
  --node-label role=worker
```

### MetalLB للـ Load Balancing

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: sahool-pool
  namespace: metallb-system
spec:
  addresses:
    - 10.0.1.100-10.0.1.110  # Tihama
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: sahool-l2
  namespace: metallb-system
spec:
  ipAddressPools:
    - sahool-pool
```

### Longhorn للتخزين

```yaml
apiVersion: longhorn.io/v1beta2
kind: Setting
metadata:
  name: default-replica-count
  namespace: longhorn-system
value: "3"
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-sahool
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "2880"
  fromBackup: ""
  fsType: ext4
reclaimPolicy: Retain
volumeBindingMode: Immediate
```

---

## اختبار التحويل | Failover Testing

### سكربت الاختبار

```bash
#!/bin/bash
# test-failover.sh

REGIONS=("tihama" "highlands" "hadramout")
PRIMARY="tihama"

echo "Testing failover from $PRIMARY..."

# 1. إيقاف المنطقة الأساسية
kubectl --context sahool-$PRIMARY scale deployment --all --replicas=0 -n sahool

# 2. التحقق من التحويل التلقائي
sleep 30
for region in "${REGIONS[@]}"; do
  if [ "$region" != "$PRIMARY" ]; then
    echo "Checking $region..."
    kubectl --context sahool-$region get pods -n sahool

    # التحقق من صحة الخدمات
    curl -s https://api.$region.sahool.local/healthz
  fi
done

# 3. استعادة المنطقة الأساسية
kubectl --context sahool-$PRIMARY scale deployment --all --replicas=2 -n sahool

echo "Failover test complete."
```

---

## الأوامر المفيدة | Useful Commands

```bash
# عرض حالة جميع العناقيد
argocd cluster list

# مزامنة تطبيق لجميع المناطق
argocd app sync sahool-tihama sahool-highlands sahool-hadramout

# عرض حالة التكرار
kubectl exec -it postgresql-0 -n sahool -- \
  psql -U postgres -c "SELECT * FROM pg_stat_replication;"

# التحقق من NATS Gateways
nats server info --server nats.tihama.sahool.local:4222

# عرض مقاييس عبر المناطق
curl -s prometheus.central.sahool.local:9090/api/v1/query \
  -d 'query=up{job=~"sahool.*"}' | jq '.data.result[] | {region: .metric.region, status: .value[1]}'
```

---

## المراجع | References

- [Argo CD ApplicationSets](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/)
- [PostgreSQL Streaming Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [NATS Super-Cluster](https://docs.nats.io/running-a-nats-service/configuration/gateways)
- [k3s Documentation](https://docs.k3s.io/)
- [Longhorn Storage](https://longhorn.io/docs/)
- [MetalLB](https://metallb.universe.tf/)

---

_Last Updated: January 2026_
