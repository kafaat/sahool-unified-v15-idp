# Feature Flags & Experiments | فلاغات الميزات والتجارب

## نظرة عامة | Overview

نظام فلاغات الميزات في منصة سهول يعتمد على:
- **OpenFeature SDK**: واجهة موحدة للتطبيقات
- **flagd**: مزود فلاغات خفيف الوزن
- **GitOps**: تكوين الفلاغات عبر Git

---

## البنية المعمارية | Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Application   │────▶│  OpenFeature    │────▶│     flagd       │
│   (Service)     │     │     SDK         │     │   (Provider)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   ConfigMap     │
                                                │  (flags.json)   │
                                                └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │     GitOps      │
                                                │   (Argo CD)     │
                                                └─────────────────┘
```

---

## التثبيت | Installation

### 1. نشر flagd

**الموقع**: `/gitops/feature-flags/flagd/`

```bash
# تطبيق manifests
kubectl apply -f gitops/feature-flags/flagd/

# أو عبر ArgoCD
argocd app create feature-flags \
  --repo ${REPO_URL} \
  --path gitops/feature-flags/flagd \
  --dest-namespace feature-flags \
  --dest-server https://kubernetes.default.svc
```

### 2. Kubernetes Manifests

**namespace.yaml**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: feature-flags
  labels:
    app.kubernetes.io/name: feature-flags
```

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flagd
  namespace: feature-flags
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flagd
  template:
    metadata:
      labels:
        app: flagd
    spec:
      containers:
        - name: flagd
          image: ghcr.io/open-feature/flagd:v0.11.1
          args:
            - start
            - --uri
            - file:/etc/flagd/flags.json
          ports:
            - containerPort: 8013
              name: grpc
          volumeMounts:
            - name: flags-config
              mountPath: /etc/flagd
      volumes:
        - name: flags-config
          configMap:
            name: flagd-config
```

**service.yaml**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: flagd
  namespace: feature-flags
spec:
  selector:
    app: flagd
  ports:
    - port: 8013
      targetPort: 8013
      name: grpc
```

---

## تكوين الفلاغات | Flag Configuration

### ملف التكوين (flags.json)

**الموقع**: `/gitops/feature-flags/flagd/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flagd-config
  namespace: feature-flags
data:
  flags.json: |
    {
      "$schema": "https://flagd.dev/schema/v0/flags.json",
      "flags": {
        "ndvi.newPipeline": {
          "state": "ENABLED",
          "variants": {
            "on": true,
            "off": false
          },
          "defaultVariant": "off",
          "targeting": {
            "if": [
              {"in": ["beta", {"var": "tenant_tier"}]},
              "on",
              "off"
            ]
          }
        },
        "advisor.promptV2": {
          "state": "ENABLED",
          "variants": {
            "v1": "v1",
            "v2": "v2"
          },
          "defaultVariant": "v1",
          "targeting": {
            "fractional": [
              ["v1", 70],
              ["v2", 30]
            ]
          }
        },
        "irrigation.smartScheduling": {
          "state": "ENABLED",
          "variants": {
            "enabled": true,
            "disabled": false
          },
          "defaultVariant": "disabled",
          "targeting": {
            "if": [
              {"in": [{"var": "region"}, ["tihama", "hadramout"]]},
              "enabled",
              "disabled"
            ]
          }
        },
        "marketplace.newUI": {
          "state": "ENABLED",
          "variants": {
            "enabled": true,
            "disabled": false
          },
          "defaultVariant": "disabled",
          "targeting": {
            "if": [
              {">=": [{"var": "user_score"}, 80]},
              "enabled",
              "disabled"
            ]
          }
        },
        "ai.ragEnabled": {
          "state": "ENABLED",
          "variants": {
            "on": true,
            "off": false
          },
          "defaultVariant": "off",
          "targeting": {
            "if": [
              {"==": [{"var": "subscription"}, "enterprise"]},
              "on",
              "off"
            ]
          }
        }
      }
    }
```

---

## استخدام SDK | SDK Usage

### Python (FastAPI)

```python
from openfeature import api
from openfeature.contrib.provider.flagd import FlagdProvider

# تهيئة المزود
api.set_provider(FlagdProvider(
    host="flagd.feature-flags.svc.cluster.local",
    port=8013
))

# الحصول على العميل
client = api.get_client()

# استخدام الفلاغ
@app.get("/ndvi/process")
async def process_ndvi(tenant_id: str, tenant_tier: str):
    # سياق التقييم
    context = EvaluationContext(
        targeting_key=tenant_id,
        attributes={
            "tenant_tier": tenant_tier
        }
    )

    # تقييم الفلاغ
    use_new_pipeline = client.get_boolean_value(
        "ndvi.newPipeline",
        default_value=False,
        context=context
    )

    if use_new_pipeline:
        return await process_with_new_pipeline()
    else:
        return await process_with_legacy_pipeline()
```

### TypeScript (Node.js/NestJS)

```typescript
import { OpenFeature } from '@openfeature/server-sdk';
import { FlagdProvider } from '@openfeature/flagd-provider';

// تهيئة المزود
OpenFeature.setProvider(new FlagdProvider({
  host: 'flagd.feature-flags.svc.cluster.local',
  port: 8013,
}));

// الحصول على العميل
const client = OpenFeature.getClient();

// استخدام الفلاغ
async function getAdvisorPrompt(userId: string, subscription: string) {
  const context = {
    targetingKey: userId,
    subscription,
  };

  const promptVersion = await client.getStringValue(
    'advisor.promptV2',
    'v1',
    context
  );

  return promptVersion === 'v2'
    ? getPromptV2()
    : getPromptV1();
}
```

### Dart (Flutter)

```dart
import 'package:openfeature/openfeature.dart';

class FeatureFlagService {
  late OpenFeatureClient _client;

  Future<void> initialize() async {
    final provider = FlagdProvider(
      host: 'api.sahool.io',
      port: 8013,
    );

    await OpenFeature.instance.setProvider(provider);
    _client = OpenFeature.instance.getClient();
  }

  Future<bool> isNewUIEnabled(String userId, int userScore) async {
    final context = EvaluationContext(
      targetingKey: userId,
      attributes: {
        'user_score': userScore,
      },
    );

    return await _client.getBooleanValue(
      'marketplace.newUI',
      defaultValue: false,
      context: context,
    );
  }
}
```

---

## أنواع الفلاغات | Flag Types

### 1. Boolean Flags (فلاغات منطقية)

```json
{
  "feature.enabled": {
    "state": "ENABLED",
    "variants": {
      "on": true,
      "off": false
    },
    "defaultVariant": "off"
  }
}
```

### 2. String Flags (فلاغات نصية)

```json
{
  "ui.theme": {
    "state": "ENABLED",
    "variants": {
      "light": "light",
      "dark": "dark",
      "system": "system"
    },
    "defaultVariant": "system"
  }
}
```

### 3. Number Flags (فلاغات رقمية)

```json
{
  "rate.limit": {
    "state": "ENABLED",
    "variants": {
      "low": 10,
      "medium": 50,
      "high": 100
    },
    "defaultVariant": "medium"
  }
}
```

### 4. Object Flags (فلاغات كائنات)

```json
{
  "experiment.config": {
    "state": "ENABLED",
    "variants": {
      "control": {
        "buttonColor": "blue",
        "showBanner": false
      },
      "treatment": {
        "buttonColor": "green",
        "showBanner": true
      }
    },
    "defaultVariant": "control"
  }
}
```

---

## قواعد الاستهداف | Targeting Rules

### 1. استهداف بالنسبة المئوية (Percentage Rollout)

```json
{
  "targeting": {
    "fractional": [
      ["control", 80],
      ["treatment", 20]
    ]
  }
}
```

### 2. استهداف بالسمات (Attribute Targeting)

```json
{
  "targeting": {
    "if": [
      {"==": [{"var": "subscription"}, "enterprise"]},
      "enabled",
      "disabled"
    ]
  }
}
```

### 3. استهداف بالقائمة (List Targeting)

```json
{
  "targeting": {
    "if": [
      {"in": [{"var": "user_id"}, ["user-1", "user-2", "user-3"]]},
      "enabled",
      "disabled"
    ]
  }
}
```

### 4. استهداف مركب (Combined Targeting)

```json
{
  "targeting": {
    "if": [
      {"and": [
        {"==": [{"var": "subscription"}, "enterprise"]},
        {">=": [{"var": "user_score"}, 50]}
      ]},
      "enabled",
      {"if": [
        {"in": [{"var": "region"}, ["beta-regions"]]},
        "enabled",
        "disabled"
      ]}
    ]
  }
}
```

---

## التجارب (A/B Testing) | Experiments

### تصميم التجربة

```json
{
  "experiment.checkout_flow": {
    "state": "ENABLED",
    "variants": {
      "control": {
        "name": "Current Flow",
        "steps": 3,
        "showProgress": false
      },
      "variant_a": {
        "name": "Simplified Flow",
        "steps": 2,
        "showProgress": true
      },
      "variant_b": {
        "name": "Guided Flow",
        "steps": 4,
        "showProgress": true
      }
    },
    "defaultVariant": "control",
    "targeting": {
      "fractional": [
        ["control", 34],
        ["variant_a", 33],
        ["variant_b", 33]
      ]
    }
  }
}
```

### تتبع التجربة

```python
import structlog
from openfeature import api

logger = structlog.get_logger()

async def checkout(user_id: str, cart: Cart):
    context = EvaluationContext(targeting_key=user_id)

    # الحصول على متغير التجربة
    variant = client.get_object_value(
        "experiment.checkout_flow",
        default_value={"name": "control", "steps": 3},
        context=context
    )

    # تسجيل التعيين
    logger.info(
        "experiment_assignment",
        experiment="checkout_flow",
        variant=variant["name"],
        user_id=user_id
    )

    # تنفيذ التجربة
    result = await execute_checkout(cart, variant)

    # تسجيل النتيجة
    logger.info(
        "experiment_outcome",
        experiment="checkout_flow",
        variant=variant["name"],
        user_id=user_id,
        success=result.success,
        conversion_value=result.total
    )

    return result
```

---

## التكامل مع Argo Rollouts | Integration with Rollouts

### Analysis Template

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: feature-flag-analysis
spec:
  args:
    - name: flag-name
    - name: expected-variant
  metrics:
    - name: flag-evaluation
      provider:
        web:
          url: "http://flagd.feature-flags:8013/schema.v1.Service/ResolveBoolean"
          method: POST
          body: |
            {
              "flagKey": "{{args.flag-name}}",
              "context": {}
            }
      successCondition: result.variant == "{{args.expected-variant}}"
```

### Rollout with Feature Flag

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: ndvi-processor
spec:
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: {duration: 5m}
        - analysis:
            templates:
              - templateName: feature-flag-analysis
            args:
              - name: flag-name
                value: ndvi.newPipeline
              - name: expected-variant
                value: "on"
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100
```

---

## إدارة الفلاغات | Flag Management

### دورة حياة الفلاغ

```
1. DISABLED (معطل)
   ↓ تفعيل للاختبار
2. ENABLED (مفعل - نسبة صغيرة)
   ↓ توسيع تدريجي
3. ENABLED (مفعل - 100%)
   ↓ تثبيت في الكود
4. REMOVED (إزالة الفلاغ)
```

### أفضل الممارسات

1. **تسمية الفلاغات**:
   ```
   {domain}.{feature}

   مثال:
   - ndvi.newPipeline
   - advisor.promptV2
   - marketplace.newUI
   ```

2. **توثيق الفلاغات**:
   ```json
   {
     "myFlag": {
       "_meta": {
         "description": "وصف الميزة",
         "owner": "team-name",
         "created": "2026-01-15",
         "expires": "2026-06-15"
       }
     }
   }
   ```

3. **تنظيف الفلاغات**:
   - مراجعة أسبوعية للفلاغات المنتهية
   - إزالة الفلاغات بعد 100% rollout
   - أرشفة تكوينات الفلاغات القديمة

---

## المراقبة والتتبع | Monitoring

### Prometheus Metrics

```yaml
# مقاييس flagd
flagd_impressions_total{flag_key, variant}
flagd_reasons_total{flag_key, reason}
flagd_evaluation_duration_seconds{flag_key}
```

### Grafana Dashboard

```json
{
  "title": "Feature Flags",
  "panels": [
    {
      "title": "Flag Evaluations",
      "targets": [
        {
          "expr": "sum(rate(flagd_impressions_total[5m])) by (flag_key, variant)"
        }
      ]
    },
    {
      "title": "Evaluation Latency",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, flagd_evaluation_duration_seconds)"
        }
      ]
    }
  ]
}
```

---

## البدائل المتقدمة | Advanced Alternatives

إذا كنت بحاجة لميزات أكثر تقدماً:

| المنصة | الميزات | التكلفة |
|--------|---------|---------|
| **Unleash** | Self-hosted, SDKs, UI | مجاني/مدفوع |
| **LaunchDarkly** | Enterprise, Analytics | مدفوع |
| **Split.io** | Experimentation | مدفوع |
| **Flagsmith** | Open-source, UI | مجاني/مدفوع |

---

## الأوامر المفيدة | Useful Commands

```bash
# التحقق من حالة flagd
kubectl get pods -n feature-flags

# عرض السجلات
kubectl logs -n feature-flags -l app=flagd

# تحديث التكوين
kubectl apply -f gitops/feature-flags/flagd/configmap.yaml

# إعادة تحميل التكوين (بدون إعادة تشغيل)
kubectl rollout restart deployment/flagd -n feature-flags

# اختبار الفلاغ
grpcurl -plaintext flagd.feature-flags:8013 \
  schema.v1.Service/ResolveBoolean \
  -d '{"flagKey": "ndvi.newPipeline", "context": {}}'
```

---

## المراجع | References

- [OpenFeature Documentation](https://openfeature.dev/docs)
- [flagd Documentation](https://flagd.dev/docs)
- [JSON Logic](https://jsonlogic.com/)
- [Feature Flag Best Practices](https://martinfowler.com/articles/feature-toggles.html)

---

_Last Updated: January 2026_
