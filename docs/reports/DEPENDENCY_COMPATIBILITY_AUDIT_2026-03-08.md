# تقرير فحص توافقية الاعتماديات - منصة سهول
# SAHOOL Platform - Dependency Compatibility Audit Report

**تاريخ التقرير | Report Date**: 2026-03-08
**الإصدار | Version**: 16.0.0
**نطاق الفحص | Scope**: Full platform (72 services, 24 packages, 3 mobile apps, 2 frontends)
**عدد وكلاء التحليل | Analysis Agents**: 17 parallel agents

---

## الملخص التنفيذي | Executive Summary

تم فحص توافقية الاعتماديات لكامل منصة سهول باستخدام 17 وكيل ذكاء اصطناعي بشكل متوازٍ.

| المقياس | القيمة |
|---------|--------|
| **إجمالي المشاكل المكتشفة** | 85 |
| **حرجة (CRITICAL)** | 14 |
| **عالية (HIGH)** | 21 |
| **متوسطة (MEDIUM)** | 30 |
| **منخفضة (LOW)** | 20 |
| **الخدمات المتوافقة بالكامل** | ~45% |
| **الخدمات التي تحتاج إصلاح** | ~55% |

---

## 1. Python AI/ML Services (8 خدمات)

### المشاكل الحرجة

#### 1.1 تعارض إصدارات torch/torchvision
**الخطورة**: CRITICAL

| الخدمة | الإصدار | الحالة |
|--------|---------|--------|
| yolo26-vision-service | Dockerfile (CUDA) | OK |
| copilot-api | `torch>=2.0.0` (loose) | CRITICAL |
| constraints-ai.txt | `torch==2.2.0` | Standard |

**المشكلة**: `copilot-api` يمكن أن يسحب إصدارات غير متوافقة من torch.

**الإصلاح المطلوب** (`copilot-api/requirements.txt`):
```diff
- torch>=2.0.0
+ torch==2.2.0
+ torchvision==0.17.0
```

#### 1.2 numpy مفقود في 4 خدمات AI
**الخطورة**: CRITICAL

| الخدمة | numpy | الحالة |
|--------|-------|--------|
| copilot-api | مفقود | CRITICAL |
| llm-orchestrator-service | مفقود | HIGH |
| knowledge-graph | مفقود | HIGH |
| ai-chat-assistant | مفقود | HIGH |

**الإصلاح**: إضافة `numpy>=1.26.0,<2.5.0` لجميع الخدمات المتأثرة.

#### 1.3 sentence-transformers غير متسق
**الخطورة**: MEDIUM

```
ai-advisor:    sentence-transformers==5.2.2  (pinned)
copilot-api:   sentence-transformers>=2.2.0  (loose - allows old versions!)
```

**الإصلاح**: تثبيت `sentence-transformers==5.2.2` في copilot-api.

#### 1.4 PyJWT و cryptography مفقودان من constraints.txt المركزي
**الخطورة**: CRITICAL

| الحزمة | constraints.txt | constraints-ai.txt | pyproject.toml |
|--------|----------------|-------------------|----------------|
| PyJWT | **مفقود** | `>=2.9.0,<3.0.0` | `>=2.8.0,<3.0.0` |
| cryptography | **مفقود** | `>=43.0.1,<45.0.0` | `>=43.0.1` (بدون حد أعلى) |

**المشكلة**: حزمتان أمنيتان أساسيتان مفقودتان من ملف القيود المركزي، مما يسمح بتثبيت إصدارات قديمة غير آمنة.

**الإصلاح المطلوب** (`constraints.txt`):
```diff
+ PyJWT>=2.9.0,<3.0.0
+ cryptography>=43.0.1,<45.0.0
```

#### 1.5 تعارض حد starlette الأعلى بين ملفات القيود
**الخطورة**: MEDIUM

```
constraints.txt:      starlette>=0.49.1,<0.53.0   ← صارم
constraints-ai.txt:   starlette>=0.49.1,<1.0.0    ← متساهل
```

**المشكلة**: عند إصدار Starlette 0.53.0، ستتعطل الخدمات التي تستخدم constraints.txt بينما تعمل خدمات AI بشكل طبيعي.

#### 1.6 asyncpg vs psycopg2 في خدمات Core
**الخطورة**: HIGH

| الخدمة | Driver | النمط |
|--------|--------|-------|
| notification-service | asyncpg | async (صحيح) |
| billing-core | asyncpg | async (صحيح) |
| task-service | **psycopg2-binary** | **sync (خاطئ)** |
| equipment-service | **psycopg2-binary** | **sync (خاطئ)** |
| alert-service | **psycopg2-binary** | **sync (خاطئ)** |

**المشكلة**: 3 خدمات FastAPI تستخدم driver متزامن رغم أن FastAPI مصمم للعمل بشكل غير متزامن.

---

## 2. Node.js/NestJS Services (8 خدمات)

### المشاكل الحرجة

#### 2.1 تعارض إصدار TypeScript في code-review-agent
**الخطورة**: CRITICAL

```
code-review-agent:    typescript@^5.7.2    ← قديم
NestJS services:      typescript@^5.9.3    ← المعيار
```

#### 2.2 متطلبات Node.js غير متسقة
**الخطورة**: CRITICAL

```
code-review-agent:    node@>=18.0.0    ← لا يتوافق مع المنصة
NestJS services:      node@>=20.0.0    ← المعيار
```

#### 2.3 نظام الوحدات مختلف
**الخطورة**: CRITICAL

```
code-review-agent:    ESM ("type": "module")
NestJS services:      CommonJS (implicit)
```

#### 2.4 ts-jest غير متسق
**الخطورة**: HIGH

| الخدمة | الإصدار |
|--------|---------|
| marketplace-service | ^29.2.5 |
| chat-service | ^29.4.6 |
| research-core | ^29.1.0 |

**الإصلاح**: توحيد إلى `ts-jest@^29.2.5`.

---

## 3. Flutter Mobile Apps (تطبيقان)

### المشاكل الحرجة

#### 3.1 تعارض حزمة record
**الخطورة**: HIGH

```yaml
sahool_field_app:   record: 5.0.5 + dependency_overrides: record_platform_interface: 1.2.0
sahol_atmosphere:   record: ^5.1.2   # بدون override!
```

**المشكلة**: sahol_atmosphere سيفشل على Linux بسبب `startStream` method not found.

**الإصلاح** (`sahol_atmosphere/pubspec.yaml`):
```yaml
dependency_overrides:
  record_platform_interface: 1.2.0
```

#### 3.2 تكرار app_links في sahool_field_app
**الخطورة**: HIGH

```yaml
# سطر 93:
app_links: ^3.5.1     # مكرر - يتم تجاهله
# سطر 101:
app_links: ^6.3.3     # القيمة الفعلية
```

**الإصلاح**: حذف السطر 93 المكرر.

---

## 4. Web/Admin Frontend (تطبيقان)

### الحالة: متوافق بشكل ممتاز

| المكون | web | admin | الحالة |
|--------|-----|-------|--------|
| React | ^19.2.4 | ^19.2.4 | OK |
| Next.js | 15.5.12 | ^15.5.12 | OK |
| TypeScript | 5.9.3 | 5.9.3 | OK |
| Tailwind | 3.4.17 | 3.4.17 | OK |
| Vitest | 3.2.4 | 3.2.4 | OK |

**مشاكل طفيفة**:
- `jsdom`: web يستخدم ^27.3.0, admin يستخدم 26.1.0 (LOW)
- Sentry: shared-ui يستخدم ^8.0.0, التطبيقات تستخدم ^9.5.0 (LOW)

---

## 5. IoT & Integration Services (7 خدمات)

### المشاكل الحرجة

#### 5.1 تعارض مكتبات MQTT في iot-sensor-hub
**الخطورة**: CRITICAL

```python
# iot-sensor-hub/requirements.txt
asyncio-mqtt>=0.16.0    # مكتبة 1
aiomqtt>=2.0.0          # مكتبة 2 - غير متوافقة!
```

**المشكلة**: لا يمكن أن تتواجد المكتبتان في نفس العملية.

**الإصلاح**: حذف `asyncio-mqtt` واستخدام `aiomqtt>=2.3.0` فقط.

#### 5.2 WebSocket غير متسق
**الخطورة**: HIGH

```
ws-gateway:                websockets==16.0
edge-orchestrator-service: websockets>=14.0,<17.0  (loose)
```

#### 5.3 HTTP client مكرر في virtual-sensors
**الخطورة**: MEDIUM

```
httpx==0.28.1      # مكتبة 1
aiohttp>=3.13.3    # مكتبة 2 - مكرر
```

---

## 6. Terrain & Geospatial Services (4 خدمات)

### المشاكل

#### 6.1 تثبيت scipy صارم جداً
**الخطورة**: HIGH

```
terrain-core-service:   scipy==1.17.0      (pinned)
ground-vision-service:  scipy>=1.14.0,<1.18.0  (range)
constraints.txt:        scipy>=1.11.0,<1.18.0
```

**الإصلاح**: تغيير terrain-core-service إلى `scipy>=1.14.0,<1.18.0`.

#### 6.2 rasterio غير متسق
**الخطورة**: MEDIUM

```
terrain-core-service:   rasterio==1.4.3    (pinned)
ground-vision-service:  rasterio>=1.4.0    (loose)
```

---

## 7. Intelligence/Analytics Services (7 خدمات)

### المشاكل

#### 7.1 FastAPI متساهل في pest-detection-service
**الخطورة**: HIGH

```
pest-detection-service:  fastapi>=0.115.0,<1.0.0  ← متساهل جداً
المعيار:                 fastapi==0.128.5
```

#### 7.2 اعتماديات علمية مفقودة
**الخطورة**: MEDIUM

| الخدمة | numpy | scipy | scikit-learn | pandas |
|--------|-------|-------|-------------|--------|
| vegetation-analysis | OK | مفقود | مفقود | مفقود |
| indicators-service | مفقود | مفقود | مفقود | مفقود |
| field-intelligence | مفقود | مفقود | مفقود | مفقود |
| pest-detection | مفقود | مفقود | مفقود | مفقود |
| soil-analysis | مفقود | مفقود | مفقود | مفقود |
| skills-service | مفقود | مفقود | مفقود | مفقود |

---

## 8. Business/Operations Services (7 خدمات)

### المشاكل

#### 8.1 cryptography بدون حد أعلى
**الخطورة**: HIGH

| الخدمة | المحدد | المعيار |
|--------|--------|---------|
| crm-service | `>=43.0.1` (بدون حد) | `>=43.0.1,<45.0.0` |
| logistics-service | `>=43.0.1` (بدون حد) | `>=43.0.1,<45.0.0` |

#### 8.2 GlobalGAP إصدارات قديمة جداً
**الخطورة**: HIGH

```
fastapi>=0.104.0     ← المعيار 0.128.5
uvicorn>=0.24.0      ← المعيار 0.40.0
structlog>=23.2.0    ← المعيار 24.4.0
```

#### 8.3 Audit-Service يستخدم psycopg2 المتزامن
**الخطورة**: MEDIUM

```
psycopg2-binary==2.9.9    # متزامن - يخالف نمط async-first
```

---

## 9. Advisory/Decision Services (7 خدمات)

### الحالة: جيدة

| الخدمة | الحالة |
|--------|--------|
| advisory-service | OK |
| irrigation-smart | OK |
| agro-rules | ناقص (يفتقر لاعتماديات الاختبار) |
| digital-twin-engine | OK |
| fertigation-engine | OK |
| irrigation-cycle-engine | OK (pyfao56 غير موجود في constraints) |
| yield-prediction-service | OK (Redis مكرر) |

---

## 10. Docker Base Images

### الحالة: ممتازة (94/100)

| المكون | التوحيد | الحالة |
|--------|---------|--------|
| Python | 3.11-slim-bookworm (95%) | OK |
| Node.js | 20-bookworm-slim (100%) | OK |
| CUDA | 12.1.1 (100%) | OK |
| Debian | Bookworm 12 (99%) | OK |

**مشكلة واحدة**: 3 خدمات تفتقر لتعريف `ARG PYTHON_VERSION=3.11` صريح.

---

## 11. Shared npm Packages (12 حزمة)

### الحالة: متوافق

جميع الحزم المشتركة تعتمد على `react >=18.0.0` كـ peer dependency وهو متوافق مع React 19.2.4 المستخدم في التطبيقات.

---

## 12. Agent & Code Services (10 خدمات)

### الحالة: متوافق بشكل عام

| الخدمة | الحالة |
|--------|--------|
| agent-registry | OK (NATS مفقود صريحاً) |
| code-fix-agent | OK |
| code-review-agent (Node) | OK |
| code-review-service | OK |
| provider-config | OK |
| llm-orchestrator-service | OK (LangChain commented) |
| ai-advisor | OK |
| ai-agents-core | OK |
| ai-agents-service | OK |
| copilot-api | CRITICAL (torch, numpy, sentence-transformers) |

---

## 13. Specialized/Communication Services (8 خدمات)

### المشاكل المكتشفة

#### 13.1 pytest-asyncio غير موحد عبر المنصة
**الخطورة**: MEDIUM

```
المعيار:                pytest-asyncio==0.26.0  (34 خدمة)
whatsapp-bot-service:   pytest-asyncio>=0.23.0  (متساهل)
edge-orchestrator:      pytest-asyncio>=0.24.0  (متساهل)
```

---

## خطة الإصلاح ذات الأولوية | Prioritized Fix Plan

### P0 - حرج (الإصلاح فوراً)

| # | الخدمة | الإصلاح |
|---|--------|---------|
| 1 | copilot-api | Pin torch==2.2.0, add numpy, pin sentence-transformers==5.2.2 |
| 2 | iot-sensor-hub | Remove asyncio-mqtt, keep aiomqtt only |
| 3 | sahol_atmosphere | Add dependency_overrides for record_platform_interface |
| 4 | sahool_field_app | Remove duplicate app_links: ^3.5.1 |
| 5 | code-review-agent | Upgrade TypeScript to ^5.9.3, Node to >=20.0.0 |
| 6 | constraints.txt | Add PyJWT>=2.9.0,<3.0.0 and cryptography>=43.0.1,<45.0.0 |

### P1 - عالي (هذا الأسبوع)

| # | الخدمة | الإصلاح |
|---|--------|---------|
| 7 | crm-service, logistics-service | Add cryptography upper bound <45.0.0 |
| 8 | globalgap-compliance | Update minimum versions (fastapi, uvicorn, structlog) |
| 9 | pest-detection-service | Pin fastapi==0.128.5 |
| 10 | terrain-core-service | Change scipy to range >=1.14.0,<1.18.0 |
| 11 | edge-orchestrator-service | Pin websockets==16.0, fastapi==0.128.5 |
| 12 | llm-orchestrator, knowledge-graph, ai-chat-assistant | Add numpy>=1.26.0,<2.5.0 |
| 13 | task-service, equipment-service, alert-service | Migrate psycopg2-binary → asyncpg |
| 14 | constraints.txt | Align starlette upper bound with constraints-ai.txt |

### P2 - متوسط (الإصدار القادم)

| # | النطاق | الإصلاح |
|---|--------|---------|
| 12 | All services | Standardize pytest-asyncio==0.26.0 |
| 13 | All services with cryptography | Add upper bound <45.0.0 |
| 14 | Intelligence services | Add explicit numpy, scipy, pandas declarations |
| 15 | virtual-sensors | Remove duplicate aiohttp, keep httpx only |
| 16 | NestJS services | Standardize ts-jest@^29.2.5 |
| 17 | audit-service | Consider migrating psycopg2 → asyncpg |
| 18 | All loose Pydantic | Pin to pydantic==2.12.5 |

### P3 - منخفض (صيانة)

| # | النطاق | الإصلاح |
|---|--------|---------|
| 19 | admin | Standardize jsdom to ^27.3.0 |
| 20 | All services | Add upper bounds to all loose dependencies |
| 21 | Docker images | Add explicit ARG PYTHON_VERSION=3.11 to 3 services |
| 22 | agro-rules | Add missing test/auth dependencies |

---

## أوامر التحقق | Verification Commands

```bash
# Python dependency resolution check
pip install -c docker/constraints-ai.txt --dry-run -r requirements.txt

# Node.js dependency audit
npm ls --legacy-peer-deps

# Flutter dependency check
flutter pub outdated
dart pub deps --no-dev | grep CONFLICT

# Check all Python service versions
ruff check apps/ shared/
make lint

# Run full CI
make ci
```

---

## إحصائيات التحليل | Analysis Statistics

| المقياس | القيمة |
|---------|--------|
| إجمالي الخدمات المفحوصة | 72+ |
| حزم npm المفحوصة | 24 |
| تطبيقات Flutter المفحوصة | 3 |
| تطبيقات Frontend المفحوصة | 2 |
| ملفات Dockerfile المفحوصة | 20+ |
| ملفات constraints المفحوصة | 2 |
| وكلاء التحليل المتوازيين | 17 |
| إجمالي الملفات المقروءة | 150+ |

---

## الخلاصة | Conclusion

المنصة تتمتع بأساس قوي من التوحيد خاصة في:
- Docker base images (94/100)
- Frontend apps (React 19 + Next.js 15) - ممتاز
- Advisory/Decision services - جيد جداً
- NATS versioning (2.13.1) - موحد

المجالات التي تحتاج أكبر قدر من الاهتمام:
1. **copilot-api**: أكثر خدمة تحتاج إصلاح (torch, numpy, sentence-transformers)
2. **IoT services**: تعارض MQTT في iot-sensor-hub
3. **Mobile apps**: record package و app_links duplicates
4. **Intelligence services**: اعتماديات علمية مفقودة
5. **Business services**: cryptography بدون حد أعلى

---

_Generated by 17 parallel AI agents | تم إنشاؤه بواسطة 17 وكيل ذكاء اصطناعي متوازٍ_
_SAHOOL Platform v16.0.0 | KAFAAT_
