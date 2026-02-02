# SAHOOL Internal Developer Platform (IDP) Architecture

## نظرة عامة | Overview

منصة المطورين الداخلية (IDP) لسهول هي نظام متكامل يهدف إلى:
- تقليل وقت إعداد المطورين الجدد (دقائق بدلاً من أيام)
- توحيد إنشاء الخدمات (المسارات الذهبية - Golden Paths)
- فرض معايير الأمان والمراقبة (السياسات + القوالب)
- الخدمة الذاتية: إنشاء خدمة ← بناء ← نشر إلى dev/staging/prod عبر GitOps

---

## المكونات الأساسية | Core Components

### 1. Backstage - بوابة المطورين

**الموقع**: `/idp/backstage/`

Backstage هو منصة المطورين مفتوحة المصدر من Spotify، نستخدمها لـ:
- **كتالوج الخدمات**: تسجيل وعرض جميع الخدمات
- **القوالب**: إنشاء خدمات جديدة بسرعة
- **الوثائق**: توثيق موحد لجميع الخدمات
- **المكونات الإضافية**: Kubernetes, GitHub, Prometheus

**التكوين الأساسي** (`app-config.yaml`):
```yaml
app:
  title: SAHOOL Developer Portal
  baseUrl: http://localhost:7007

organization:
  name: SAHOOL

catalog:
  rules:
    - allow: [Component, System, API, Resource, Location, Group, User, Domain]

integrations:
  github:
    - host: github.com
      token: ${GITHUB_TOKEN}

kubernetes:
  serviceLocatorMethod: multiTenant
  clusters:
    - name: sahool-dev
      url: ${K8S_CLUSTER_URL}
      authProvider: serviceAccount
```

**الوصول**:
```bash
kubectl port-forward -n backstage svc/backstage 7007:7007
# ثم افتح: http://localhost:7007
```

---

### 2. GitOps (Argo CD) - التسليم المستمر

**الموقع**: `/gitops/argocd/`

Argo CD هو أداة GitOps للنشر التصريحي على Kubernetes:
- **مزامنة تلقائية**: Git هو مصدر الحقيقة الوحيد
- **التسليم التدريجي**: Canary و Blue-Green deployments
- **إعادة المزامنة الذاتية**: Self-heal عند التغييرات اليدوية
- **دعم عناقيد متعددة**: Multi-cluster deployment

**التطبيقات المنشورة**:
| التطبيق | النوع | الوصف |
|---------|------|-------|
| `sahool` | Application | المنصة الأساسية |
| `cert-manager` | Infrastructure | إدارة شهادات TLS |
| `ingress-nginx` | Infrastructure | وحدة Ingress |
| `external-secrets` | Infrastructure | إدارة الأسرار |
| `argo-rollouts` | Infrastructure | التسليم التدريجي |
| `feature-flags` | Application | فلاغات الميزات (flagd) |
| `backstage` | IDP | بوابة المطورين |

**ApplicationSet للنشر المتعدد**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: sahool-multicluster
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            sahool/enabled: "true"
  template:
    spec:
      source:
        repoURL: ${REPO_URL}
        path: k8s/helm/sahool-kernel
      destination:
        server: '{{server}}'
        namespace: sahool
```

---

### 3. Argo Rollouts - التسليم التدريجي

**الإصدار**: 2.35.0

**استراتيجيات النشر المدعومة**:

#### Canary Deployment
```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 30
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
    analysis:
      templates:
        - templateName: success-rate
      startingStep: 1
```

#### Blue-Green Deployment
```yaml
strategy:
  blueGreen:
    activeService: sahool-active
    previewService: sahool-preview
    autoPromotionEnabled: true
    autoPromotionSeconds: 300
    scaleDownDelaySeconds: 30
```

**لوحة التحكم**:
```bash
kubectl port-forward -n argo-rollouts svc/argo-rollouts-dashboard 3100:3100
# ثم افتح: http://localhost:3100
```

---

### 4. Kyverno - سياسات الحوكمة

**الموقع**: `/governance/policies/kyverno/`

Kyverno هو محرك سياسات Kubernetes الأصلي:
- **التحقق**: Validate resource configurations
- **التعديل**: Mutate resources on creation
- **التوليد**: Generate resources automatically
- **التدقيق**: Audit existing resources

**السياسات المفعلة**:
```yaml
# أمثلة على السياسات
policies:
  - require-labels           # فرض التسميات المطلوبة
  - require-resource-limits  # فرض حدود الموارد
  - disallow-latest-tag      # منع استخدام :latest
  - require-non-root-user    # فرض تشغيل غير root
  - require-probes           # فرض health probes
  - restrict-registries      # تقييد مستودعات الصور
```

---

### 5. Observability Stack - المراقبة

**المكونات**:
| المكون | الإصدار | المنفذ | الغرض |
|--------|---------|--------|-------|
| Prometheus | 2.48.0 | 9090 | جمع المقاييس |
| Grafana | 10.2.0 | 3002 | لوحات التحكم |
| Alertmanager | 0.26.0 | 9093 | إدارة التنبيهات |
| OpenTelemetry | latest | - | التتبع الموزع |

**التكامل مع الخدمات**:
```python
# كل خدمة يجب أن تتضمن:
from prometheus_client import Counter, Histogram

# مقاييس أساسية
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

---

## القوالب الذهبية | Golden Path Templates

### الموقع: `/idp/templates/`

### 1. Python FastAPI Service

**القالب**: `templates/python-fastapi/template.yaml`

```yaml
metadata:
  name: sahool-python-fastapi
  title: SAHOOL Service (Python FastAPI)
  description: Golden path with OTel + /metrics + GitOps wiring

parameters:
  - name: string (kebab-case)
  - port: integer (default: 8080)
  - layer: [signal-producer, decision, action]
```

**ما يتضمنه**:
- `Dockerfile` مُحسَّن (Python 3.11-slim, non-root)
- `requirements.txt` مع FastAPI 0.126.0
- `src/main.py` مع:
  - Health endpoints (`/healthz`, `/readyz`)
  - Prometheus metrics (`/metrics`)
  - Audit middleware
  - Structured logging (structlog)
  - OpenTelemetry integration
- `catalog-info.yaml` للتسجيل في Backstage

---

### 2. Node.js/Express Service

**القالب**: `templates/node-service/template.yaml`

```yaml
metadata:
  name: sahool-node-service
  title: SAHOOL Service (Node/TS)

parameters:
  - name: string
  - port: integer (default: 8080)
```

**ما يتضمنه**:
- `package.json` مع Express 4.19.2
- `src/index.ts` مع:
  - Health endpoints
  - Prometheus metrics (prom-client)
  - Audit middleware
  - TypeScript support

---

### 3. Flutter Mobile Module

**القالب**: `templates/flutter-mobile/template.yaml`

```yaml
metadata:
  name: sahool-flutter-mobile
  title: SAHOOL Mobile Module (Flutter)
  tags: [flutter, mobile, offline-first, dart]

parameters:
  - name: snake_case (e.g., field_scanner)
  - layer: [feature, core, shared]
  - has_offline_support: boolean
  - has_api_integration: boolean
```

**ما يتضمنه**:
- `pubspec.yaml` مع:
  - flutter_riverpod 2.6.1
  - dio 5.4.0
  - drift 2.24.0 (offline)
  - flutter_secure_storage 9.0.0
- هيكل المجلدات:
  ```
  lib/
  ├── src/
  │   ├── database/
  │   ├── models/
  │   ├── providers/
  │   └── services/
  ```

---

### 4. Data Pipeline

**القالب**: `templates/data-pipeline/template.yaml`

```yaml
metadata:
  name: sahool-data-pipeline
  title: SAHOOL Data Pipeline (Python)
  tags: [python, data-pipeline, etl, streaming]

parameters:
  - name: kebab-case
  - pipeline_type: [batch, streaming, hybrid]
  - schedule: Cron expression
  - input_source: [nats, kafka, postgres, s3, api]
  - output_sink: [nats, postgres, s3, api]
```

**ما يتضمنه**:
- `main.py` مع Pipeline class
- Input/Output source adapters
- Prometheus metrics
- Signal handling للإيقاف الآمن

---

## أداة sahoolctl | CLI Tool

**الموقع**: `/idp/sahoolctl/sahoolctl.py`

أداة سطر أوامر لإنشاء الخدمات مع فرض الحوكمة:

### الأوامر المتاحة

```bash
# إنشاء خدمة جديدة
python3 sahoolctl.py create <name> \
  --template [python-fastapi|node-service|flutter-mobile|data-pipeline] \
  --owner <owner> \
  --team [platform|kernel|frontend|data|devops|agro|iot|mobile] \
  --lifecycle [experimental|internal|production|deprecated|retired] \
  --tier [tier-1|tier-2|tier-3] \
  [--port PORT] \
  [--layer LAYER] \
  [--description DESC]

# التحقق من حوكمة خدمة موجودة
python3 sahoolctl.py validate <path-to-service>

# قائمة القوالب المتاحة
python3 sahoolctl.py templates
```

### مثال على الاستخدام

```bash
python3 sahoolctl.py create ndvi-preprocessor \
  --template python-fastapi \
  --owner "data-team@sahool.io" \
  --team data \
  --lifecycle production \
  --tier tier-2 \
  --port 8150 \
  --layer intelligence
```

### الإخراج المتوقع

```
✅ Created governed service: apps/ndvi-preprocessor
   📁 Service code: apps/ndvi-preprocessor
   📁 Helm values: apps/ndvi-preprocessor/deploy/values.yaml
   📁 Catalog info: apps/ndvi-preprocessor/catalog-info.yaml
   📁 GitOps app: gitops/argocd/applications/ndvi-preprocessor.yaml

📋 Next steps:
   1. git add -A && git commit -m 'Add ndvi-preprocessor service'
   2. git push
   3. ArgoCD will auto-deploy
```

---

## بيئات النشر | Deployment Environments

### هيكل البيئات

```
gitops/environments/
├── preview/           # PR Preview environments
│   └── values.yaml
├── staging/           # بيئة التحضير
│   └── values.yaml
└── production/        # بيئة الإنتاج
    └── values.yaml
```

### PR Preview Environments

**ApplicationSet للمعاينات**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: sahool-pr-previews
spec:
  generators:
    - pullRequest:
        github:
          owner: ${GITHUB_OWNER}
          repo: ${GITHUB_REPO}
        requeueAfterSeconds: 180
  template:
    metadata:
      name: 'sahool-pr-{{number}}'
    spec:
      source:
        path: gitops/environments/preview
        helm:
          parameters:
            - name: global.environment
              value: 'pr-{{number}}'
      destination:
        namespace: 'pr-{{number}}-sahool'
```

**URL المعاينة**: `https://pr-{number}.preview.sahool.io`

---

## نظام الكتالوج | Catalog System

### تسجيل الخدمات

كل خدمة يجب أن تحتوي على `catalog-info.yaml`:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: ndvi-processor
  description: NDVI Processing Service
  tags:
    - python
    - fastapi
    - intelligence
  annotations:
    github.com/project-slug: kafaat/sahool-unified-v15-idp
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: group:data-team
  system: sahool-platform
  dependsOn:
    - resource:postgresql
    - component:vegetation-analysis-service
  providesApis:
    - ndvi-api
```

### نظام SAHOOL

```yaml
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: sahool-platform
  description: SAHOOL Smart Agriculture Platform
spec:
  owner: group:sahool-platform
  domain: agriculture
```

---

## الأمان والتدقيق | Security & Audit

### إعدادات التدقيق في Backstage

```yaml
audit:
  enabled: true
  retentionDays: 90
  alertChannels:
    - type: webhook
    - type: log
  categories:
    - authentication
    - authorization
    - configuration
    - catalog
    - kubernetes
```

### إعدادات الأمان

```yaml
security:
  sessionTimeoutMinutes: 30
  mfaRequired: false
  auditAdminActions: true
  rateLimit:
    enabled: true
    maxRequestsPerMinute: 100
```

---

## Kubernetes Deployment | نشر Kubernetes

### ملفات النشر

**الموقع**: `/idp/backstage/k8s/`

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: backstage

# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backstage
  namespace: backstage
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: backstage
          image: ghcr.io/backstage/backstage:latest
          ports:
            - containerPort: 7007
          volumeMounts:
            - name: app-config
              mountPath: /app/app-config.yaml
              subPath: app-config.yaml

# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backstage
  namespace: backstage
spec:
  type: ClusterIP
  ports:
    - port: 7007
      targetPort: 7007
```

---

## متغيرات البيئة | Environment Variables

```bash
# GitHub Integration
GITHUB_TOKEN=xxx

# Kubernetes Configuration
K8S_CLUSTER_URL=https://k8s-api:6443
K8S_SA_TOKEN=xxx
K8S_CA_DATA=xxx

# Audit Webhook
AUDIT_WEBHOOK_URL=https://audit-service/webhook

# Security
SECURITY_MFA_REQUIRED=false
```

---

## سير العمل الكامل | Complete Workflow

```
1. المطور يريد إنشاء خدمة جديدة
   ↓
2. يستخدم sahoolctl أو Backstage Templates
   ↓
3. يتم توليد الهيكل + catalog-info.yaml + ArgoCD app
   ↓
4. git push → GitHub Actions CI
   ↓
5. CI: Lint → Test → Build Docker → Push to Registry
   ↓
6. ArgoCD يكتشف التغيير ويبدأ المزامنة
   ↓
7. Argo Rollouts ينفذ Canary/Blue-Green
   ↓
8. التحقق التلقائي (Analysis Templates)
   ↓
9. النشر الكامل أو الـ Rollback التلقائي
```

---

## الأوامر المفيدة | Useful Commands

```bash
# الوصول إلى Backstage
kubectl port-forward -n backstage svc/backstage 7007:7007

# الوصول إلى ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8080:443

# الوصول إلى Argo Rollouts Dashboard
kubectl port-forward -n argo-rollouts svc/argo-rollouts-dashboard 3100:3100

# عرض حالة التطبيقات
argocd app list
argocd app get sahool

# عرض حالة Rollout
kubectl argo rollouts get rollout sahool-api -n sahool

# ترقية Canary يدوياً
kubectl argo rollouts promote sahool-api -n sahool

# الرجوع للإصدار السابق
kubectl argo rollouts undo sahool-api -n sahool
```

---

## المراجع | References

- [Backstage Documentation](https://backstage.io/docs)
- [Argo CD Documentation](https://argo-cd.readthedocs.io)
- [Argo Rollouts Documentation](https://argoproj.github.io/argo-rollouts)
- [Kyverno Documentation](https://kyverno.io/docs)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs)

---

_Last Updated: January 2026_
