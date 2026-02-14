# تقرير تدقيق شامل لجميع ملفات Docker | Comprehensive Dockerfile Audit Report

**المنصة**: SAHOOL v16.0.0 - National Agricultural Intelligence Platform
**تاريخ التدقيق**: 2026-02-13
**النطاق**: جميع 82 Dockerfile في المستودع (78 خدمة نشطة + 4 بنية تحتية/قوالب)
**المدقق**: Claude AI Audit Agent

---

## الملخص التنفيذي | Executive Summary

تم تدقيق **82 Dockerfile** تغطي 78 خدمة نشطة + 4 ملفات بنية تحتية وقوالب. يشمل التدقيق:
- **3 صور قاعدة** (Python Base, Node.js Base, AI Base)
- **55 خدمة Python** (FastAPI)
- **13 خدمة Node.js** (NestJS)
- **1 خدمة Vision متخصصة** (CUDA/GPU)
- **6 بنية تحتية + قوالب** (PostgreSQL, Test Runner, IDP Template)
- **4 صور Shared/Utility**

### نتيجة التدقيق الإجمالية

| المعيار | النسبة | الحالة |
|---------|--------|--------|
| HEALTHCHECK موجود | 79/82 (96%) | جيد |
| مستخدم غير root | 82/82 (100%) | ممتاز |
| Multi-stage build | 28/82 (34%) | ضعيف |
| Multi-mirror pip fallback | 42/55 (76%) | مقبول |
| Constraints file مستخدم | 6/55 (11%) | ضعيف جداً |
| نسخ shared/ | 48/55 (87%) | جيد |
| اسم مستخدم sahool موحد | 64/82 (78%) | يحتاج تحسين |

---

## القسم 1: صور القاعدة | Base Images

### 1.1 Dockerfile.python.base (`docker/`)

| البند | القيمة | التقييم |
|-------|--------|---------|
| الصورة | `python:3.11-slim` | ⚠️ يجب أن تكون `slim-bookworm` |
| Multi-stage | ✅ 3 مراحل (base → dependencies → production) | جيد |
| HEALTHCHECK | ✅ curl على `/healthz` | جيد |
| مستخدم | ✅ sahool:1000 | جيد |
| pip mirrors | ❌ لا يوجد mirror خارجي، يعتمد على PyPI فقط | يحتاج إصلاح |
| pip.conf | ✅ timeout=300, retries=10, prefer-binary | جيد |
| shared/ | ✅ ينسخ `shared/` إلى `/app/shared/` | جيد |
| constraints | ❌ لا يستخدم constraints.txt | يحتاج إضافة |

**أوجه القصور**:
1. لا يحدد `-bookworm` بالاسم الصريح (قد يتغير في المستقبل)
2. لا يستخدم mirror fallback (مشكلة في المنطقة العربية)
3. لا يستخدم constraints file
4. لا يوجد `PYTHONFAULTHANDLER=1` (موجود في AI base)

---

### 1.2 Dockerfile.node.base (`docker/`)

| البند | القيمة | التقييم |
|-------|--------|---------|
| الصورة | `node:20-slim` | ⚠️ يجب تحديد `bookworm-slim` |
| Multi-stage | ✅ 4 مراحل (base → dependencies → builder → production) | ممتاز |
| HEALTHCHECK | ✅ curl على `/healthz` | جيد |
| مستخدم | ✅ sahool:1000 | جيد |
| npm mirror | ❌ لا يوجد npm mirror | يحتاج إصلاح |
| TypeScript | ✅ يبني TypeScript ثم ينسخ dist فقط | جيد |

**أوجه القصور**:
1. لا يستخدم npm mirror (npmmirror.com)
2. يستخدم `npm ci` بدون `--legacy-peer-deps` (قد يفشل)
3. لا يوجد retry logic لـ npm install

---

### 1.3 Dockerfile.ai-base (`docker/`)

| البند | القيمة | التقييم |
|-------|--------|---------|
| الصورة | `python:3.11-slim-bookworm` | ✅ ممتاز |
| Multi-stage | ✅ 3 مراحل (base → builder → runtime) | ممتاز |
| HEALTHCHECK | ✅ Python urllib | جيد |
| مستخدم | ✅ sahool:1000 | جيد |
| pip mirrors | ✅ Aliyun + Tsinghua + PyPI | ممتاز |
| pip.conf | ✅ شامل مع prefer-binary | ممتاز |
| venv | ✅ يستخدم virtual environment | أفضل ممارسة |
| constraints | ✅ يستخدم `constraints-ai.txt` | ممتاز |
| OCI Labels | ✅ كاملة | جيد |

**هذه الصورة هي المرجع الذهبي (Gold Standard)** - يجب أن تحتذي بها باقي الصور.

---

### 1.4 Dockerfile.walg - PostgreSQL (`config/postgres/`)

| البند | القيمة | التقييم |
|-------|--------|---------|
| الصورة | `postgis/postgis:16-3.4` | ✅ ممتاز |
| WAL-G | ✅ v2.0.1 مع دعم arm64/amd64 | جيد |
| AWS CLI | ✅ للعمليات الاحتياطية | جيد |
| الأمان | ✅ ملكية postgres:postgres | جيد |
| HEALTHCHECK | ❌ غير موجود | يحتاج إضافة |

**أوجه القصور**:
1. لا يوجد HEALTHCHECK (يجب إضافة `pg_isready`)
2. يثبت `unzip` ضمنياً لكن لا يزيله بعد الاستخدام
3. لا يوجد pinning لإصدار AWS CLI

---

## القسم 2: خدمات Python التفصيلية | Python Services Detail

### 2.1 جدول التدقيق الشامل لخدمات Python

| # | الخدمة | المنفذ | Multi-Stage | HEALTHCHECK | المستخدم | Mirror Pattern | shared/ | constraints | الحالة |
|---|--------|--------|------------|------------|----------|---------------|---------|------------|--------|
| 1 | advisory-service | 8093 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 2 | agent-registry | 8160 | ❌ | ✅ | sahool | A (multi) | ⚠️ جزئي | ❌ | نشط |
| 3 | agro-advisor | 8105 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | مهمل |
| 4 | agro-rules | - | ❌ | ✅ (pgrep) | sahool | A (multi) | ❌ | ❌ | فارغ |
| 5 | **ai-advisor** | 8112 | ✅ | ✅ | sahool | ✅ Aliyun+Tsinghua | ✅ | ✅ | نشط |
| 6 | ai-agents-core | 8161 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 7 | **ai-agents-service** | 8130 | ✅ | ✅ (curl) | sahool | ✅ Aliyun+Tsinghua | ✅ | ✅ | نشط |
| 8 | ai-chat-assistant | 8230 | ❌ | ✅ | sahool | ❌ لا يوجد | ❌ | ❌ | نشط |
| 9 | alert-service | 8113 | ❌ | ✅ | sahool | B (Aliyun) | ✅ | ❌ | نشط |
| 10 | astronomical-calendar | 8111 | ❌ | ✅ (httpx) | ⚠️ appuser | A (multi) | ✅ | ❌ | نشط |
| 11 | audit-service | 8114 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 12 | billing-core | 8089 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 13 | **code-fix-agent** | 8162 | ✅ | ✅ (httpx) | sahool | B (Aliyun) | ✅ | ❌ | نشط |
| 14 | code-review-service | 8102 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 15 | cooperative-service | 8127 | ❌ | ✅ (curl) | ⚠️ appuser | ❌ Tsinghua فقط | ❌ | ❌ | هيكل |
| 16 | **copilot-api** | 8088 | ✅ | ✅ (curl) | ⚠️ copilot | B (Aliyun) | ✅ | ❌ | نشط |
| 17 | crm-service | 8131 | ❌ | ✅ (curl) | sahool | A (multi) | ✅ | ❌ | نشط |
| 18 | **crop-intelligence-service** | 8095 | ✅ | ✅ | sahool | B (pip.conf) | ⚠️ جزئي | ✅ | نشط |
| 19 | demo-data | - | ❌ | ✅ (pgrep) | ⚠️ appuser | B (Aliyun) | ❌ | ❌ | فارغ |
| 20 | digital-twin-engine | 8253 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 21 | drone-service | 8172 | ❌ | ✅ (curl) | ⚠️ appuser | ❌ Tsinghua فقط | ❌ | ❌ | هيكل |
| 22 | equipment-service | 8101 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 23 | fertigation-engine | 8252 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 24 | field-chat | 8099 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 25 | **field-intelligence** | 8120 | ✅ | ✅ | sahool | B (pip.conf) | ⚠️ جزئي | ✅ | نشط |
| 26 | globalgap-compliance | 8128 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 27 | **ground-vision-service** | 8182 | ✅ | ✅ | ⚠️ appuser | B (Aliyun) | ✅ | ❌ | نشط |
| 28 | hydrology-service | 8165 | ❌ | ✅ | sahool | A (multi) | ⚠️ جزئي | ❌ | نشط |
| 29 | indicators-service | 8091 | ❌ | ✅ | sahool | A (multi) | ⚠️ جزئي | ❌ | نشط |
| 30 | inventory-service | 8116 | ❌ | ✅ | sahool | A (multi) | ✅ (workaround) | ❌ | نشط |
| 31 | iot-gateway | 8106 | ❌ | ✅ (custom) | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 32 | iot-sensor-hub | 8251 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 33 | irrigation-cycle-engine | 8250 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 34 | irrigation-smart | 8094 | ❌ | ✅ | sahool | A (multi) | ⚠️ جزئي | ❌ | نشط |
| 35 | **knowledge-graph** | 8140 | ✅ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 36 | **llm-orchestrator-service** | 8164 | ✅ | ✅ | sahool | B (pip.conf) | ✅ | ✅ | نشط |
| 37 | logistics-service | 8167 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 38 | lowcode-engine | 8132 | ❌ | ✅ (curl) | sahool | A (multi) | ✅ | ❌ | نشط |
| 39 | mcp-server | 8200 | ❌ | ✅ (httpx) | sahool | A (multi) | ✅ (مكرر) | ❌ | هيكل |
| 40 | ndvi-engine | 8107 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | مهمل |
| 41 | ndvi-processor | 8118 | ❌ | ✅ | sahool | A (multi) | ✅ (workaround) | ❌ | نشط |
| 42 | notification-service | 8110 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 43 | pest-detection-service | 8125 | ❌ | ✅ | sahool | ❌ Tsinghua فقط | ✅ | ❌ | نشط |
| 44 | provider-config | 8104 | ❌ | ✅ | sahool | A (multi) | ✅ (workaround) | ❌ | نشط |
| 45 | skills-service | 8121 | ❌ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 46 | soil-analysis-service | 8124 | ❌ | ✅ (curl) | ⚠️ appuser | ❌ Tsinghua فقط | ❌ | ❌ | هيكل |
| 47 | supply-chain-service | 8230 | ✅ | ✅ | ⚠️ appuser | B (Aliyun) | ❌ | ❌ | نشط |
| 48 | task-service | 8103 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 49 | terrain-core-service | 8185 | ❌ | ✅ | sahool | A (multi) | ✅ (workaround) | ❌ | نشط |
| 50 | traceability-service | 8123 | ❌ | ✅ (curl) | ⚠️ appuser | ❌ Tsinghua فقط | ❌ | ❌ | هيكل |
| 51 | ussd-gateway | 8183 | ❌ | ✅ | sahool | A (multi) | ✅ (مكرر) | ❌ | نشط |
| 52 | vegetation-analysis-service | 8090 | ❌ | ✅ | sahool | B (Aliyun) | ✅ (مكرر) | ❌ | نشط |
| 53 | **virtual-sensors** | 8119 | ✅ | ✅ | sahool | B (Aliyun) | ⚠️ جزئي | ❌ | نشط |
| 54 | **weather-core** | 8092 | ✅ | ✅ | sahool | A (multi) | ✅ | ❌ | مهمل |
| 55 | **weather-service** | 8092 | ✅ | ✅ | sahool | A (multi) | ✅ | ❌ | نشط |
| 56 | wechat-service | 8133 | ❌ | ✅ (curl) | sahool | A (multi) | ⚠️ جزئي | ❌ | نشط |
| 57 | **whatsapp-bot-service** | 8240 | ✅ | ✅ (curl) | sahool | B (Aliyun) | ✅ | ❌ | نشط |
| 58 | ws-gateway | 8081 | ❌ | ✅ | sahool | A (multi) | ✅ (workaround) | ❌ | نشط |
| 59 | **yield-engine** | 8098 | ✅ | ✅ | sahool | B (Aliyun) | ⚠️ جزئي | ❌ | مهمل |
| 60 | yield-prediction-service | 8152 | ✅ | ✅ | node | npm mirror | N/A | ❌ | نشط (Node.js) |
| 61 | **edge-orchestrator-service** | 8180 | ✅ | ✅ (curl) | sahool | B (Aliyun) | ❌ | ❌ | نشط |
| 62 | **leveling-optimizer-service** | 8170 | ✅ | ✅ (curl) | ⚠️ appuser | ❌ Tsinghua فقط | ❌ | ❌ | نشط |

**الخدمات المميزة بالخط العريض** = تستخدم multi-stage build

---

## القسم 3: خدمات Node.js التفصيلية | Node.js Services Detail

| # | الخدمة | المنفذ | Multi-Stage | HEALTHCHECK | المستخدم | npm mirror | Prisma | الحالة |
|---|--------|--------|------------|------------|----------|-----------|--------|--------|
| 1 | field-management-service | 3000 | ✅ | ✅ (Node.js) | sahool | ❌ | ✅ | نشط |
| 2 | user-service | 3025 | ✅ | ✅ (curl) | node | ❌ | ✅ | نشط |
| 3 | chat-service | 8000 | ✅ | ✅ (curl) | node | ❌ | ✅ | نشط |
| 4 | community-chat | 8097 | ✅ | ✅ (Node.js) | nodejs:1001 | ❌ | ✅ | مهمل/فارغ |
| 5 | crop-growth-model | 3023 | ✅ | ✅ (curl) | node | ✅ (Taobao) | ❌ | نشط |
| 6 | disaster-assessment | 3020 | ✅ | ✅ (curl) | node | ❌ | ✅ | نشط |
| 7 | iot-service | 8117 | ✅ | ✅ (curl) | nodejs:1001 | ❌ | ✅ | نشط |
| 8 | lai-estimation | 3022 | ✅ | ✅ (curl) | node | ✅ (Taobao) | ❌ | نشط |
| 9 | marketplace-service | 3010 | ✅ | ✅ (fetch) | node | ❌ | ✅ | نشط |
| 10 | research-core | 3015 | ✅ | ✅ (curl) | node | ❌ | ✅ | نشط |
| 11 | yield-prediction | 3021 | ✅ | ✅ (curl) | node | ✅ (Taobao) | ❌ | نشط |
| 12 | admin (Next.js) | 3001 | ✅ (3 مراحل) | ✅ (wget) | nextjs:1001 | ❌ | ❌ | نشط |
| 13 | code-review-agent | - | ✅ | ✅ | agent | ❌ | ❌ | نشط |

**ملاحظة**: جميع خدمات Node.js تستخدم multi-stage build ✅

---

## القسم 4: خدمة YOLO26 Vision المتخصصة

| البند | القيمة | التقييم |
|-------|--------|---------|
| الصورة | `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` | ✅ ممتاز |
| المراحل | **5 مراحل** (base→builder→production→development→cpu-only) | ✅ الأفضل |
| HEALTHCHECK | ✅ curl | ✅ |
| المستخدم | ✅ sahool:1000 | ✅ |
| pip mirrors | ✅ Aliyun + Tsinghua + PyPI | ✅ |
| constraints | ✅ `constraints-ai.txt` | ✅ |
| GPU | ✅ CUDA 12.1 + cuDNN 8 + PyTorch | ✅ |
| CPU variant | ✅ مرحلة cpu-only بديلة | ممتاز |
| Dev stage | ✅ مرحلة development للتطوير | ممتاز |

**هذه هي أفضل Dockerfile في المشروع** - نموذج يُحتذى به.

---

## القسم 5: تحليل أوجه القصور | Deficiency Analysis

### 5.1 مشاكل حرجة (Critical) 🔴

| المشكلة | عدد الخدمات المتأثرة | الخدمات |
|---------|---------------------|---------|
| **لا يوجد pip mirror (يفشل في المنطقة العربية)** | 4 | ai-chat-assistant, cooperative-service, drone-service, soil-analysis-service |
| **mirror واحد فقط (Tsinghua) - نقطة فشل واحدة** | 5 | cooperative-service, drone-service, pest-detection-service, soil-analysis-service, traceability-service, leveling-optimizer-service |
| **لا ينسخ shared/ (يفشل عند التشغيل)** | 8 | ai-chat-assistant, cooperative-service, drone-service, soil-analysis-service, traceability-service, supply-chain-service, edge-orchestrator-service, leveling-optimizer-service |
| **تعارض منافذ** | 2 | ai-chat-assistant و supply-chain-service كلاهما على المنفذ 8230 |

### 5.2 مشاكل متوسطة (Medium) 🟡

| المشكلة | عدد الخدمات المتأثرة | التأثير |
|---------|---------------------|---------|
| **لا يستخدم multi-stage build** | 37/55 Python (67%) | حجم صورة أكبر، أمان أقل |
| **لا يستخدم constraints file** | 49/55 Python (89%) | إصدارات غير مثبتة، مشاكل توافق |
| **مستخدم غير sahool** | 12 خدمة | عدم اتساق، مشاكل صلاحيات |
| **نسخ shared/ مكرر (root + apps/services/)** | 15 خدمة | زيادة حجم الصورة بلا فائدة |
| **لا يوجد npm mirror** | 10/13 Node.js | فشل البناء في المنطقة |
| **يستخدم `node` بدل `sahool`** | 8/13 Node.js | عدم اتساق مع المعيار |

### 5.3 مشاكل منخفضة (Low) 🟢

| المشكلة | عدد الخدمات المتأثرة | التأثير |
|---------|---------------------|---------|
| **HEALTHCHECK بطرق مختلفة** | كل الخدمات | عدم اتساق (curl vs urllib vs httpx vs pgrep) |
| **CMD بأنماط مختلفة** | كل الخدمات | `uvicorn` vs `python -m uvicorn` vs `sh -c` |
| **PORT متغير vs ثابت** | كل الخدمات | `${PORT:-8XXX}` vs hardcoded |
| **Alpine vs Bookworm** | Node.js | صور مختلفة لنفس النوع |

---

## القسم 6: توزيع أنماط pip Mirror

```
Pattern A (Multi-Mirror Fallback): ███████████████████████████████████████████░ 42 خدمة (76%)
PyPI → Aliyun → Tencent (الأفضل)

Pattern B (Aliyun/Tsinghua فقط):   ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 8 خدمات (15%)
mirror واحد (مقبول)

Pattern C (لا يوجد mirror):         ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 4 خدمات (7%)
⛔ خطر فشل البناء

Pattern D (Tsinghua فقط):           ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 5 خدمات (9%)
⚠️ نقطة فشل واحدة
```

---

## القسم 7: توزيع المستخدمين

```
sahool:1000   ████████████████████████████████████████████████████████████████ 64 خدمة (78%)
node (builtin) ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 8 خدمات (10%)
appuser:1000  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 8 خدمات (10%)
أخرى          ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2 خدمة (2%)
```

الخدمات التي تستخدم مستخدم غير `sahool`:
- `appuser`: astronomical-calendar, cooperative-service, demo-data, drone-service, ground-vision-service, soil-analysis-service, supply-chain-service, traceability-service, leveling-optimizer-service
- `copilot`: copilot-api
- `node`: user-service, chat-service, crop-growth-model, disaster-assessment, lai-estimation, marketplace-service, research-core, yield-prediction
- `nodejs`: community-chat, iot-service
- `nextjs`: admin
- `agent`: code-review-agent

---

## القسم 8: مقارنة كيف يجب أن تكون vs الواقع

### 8.1 Dockerfile المثالي لخدمة Python (المعيار)

```dockerfile
# المعيار الذهبي - بناءً على ai-advisor و yolo26-vision-service
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# --- Builder Stage ---
FROM base AS builder
USER sahool
WORKDIR /home/sahool
ENV VIRTUAL_ENV=/home/sahool/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# pip.conf مع mirrors متعددة
RUN mkdir -p ~/.pip && cat > ~/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               pypi.org
               files.pythonhosted.org
[install]
prefer-binary = true
EOF

COPY --chown=sahool:sahool constraints.txt /tmp/
COPY --chown=sahool:sahool requirements.txt .
RUN pip install --no-cache-dir -c /tmp/constraints.txt -r requirements.txt

# --- Production Stage ---
FROM base AS production
ARG SERVICE_NAME=service-name
ARG SERVICE_VERSION=16.0.0
LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}" \
      org.opencontainers.image.version="${SERVICE_VERSION}" \
      org.opencontainers.image.vendor="KAFAAT"

COPY --from=builder --chown=sahool:sahool /home/sahool/venv /home/sahool/venv
ENV VIRTUAL_ENV=/home/sahool/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/app
WORKDIR /app

COPY --chown=sahool:sahool shared/ /app/shared/
COPY --chown=sahool:sahool src/ /app/src/

USER sahool
EXPOSE 8XXX

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8XXX/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8XXX"]
```

### 8.2 فجوة المطابقة مع المعيار

| المعيار | يجب | الواقع | الفجوة |
|---------|------|--------|--------|
| Multi-stage build | ✅ لكل خدمة | 18/55 (33%) | **67% لا يستخدمه** |
| Virtual environment | ✅ لكل خدمة | ~10/55 (18%) | **82% لا يستخدمه** |
| constraints.txt | ✅ لكل خدمة | 6/55 (11%) | **89% لا يستخدمه** |
| Multi-mirror pip | ✅ لكل خدمة | 42/55 (76%) | 24% يحتاج إصلاح |
| sahool:1000 user | ✅ لكل خدمة | 64/82 (78%) | 22% يحتاج توحيد |
| OCI Labels | ✅ لكل خدمة | ~15/82 (18%) | **82% بدون labels** |
| EXPOSE + ENV PORT | ✅ لكل خدمة | ~50/82 (61%) | 39% بدون ENV PORT |

---

## القسم 9: الخدمات حسب حالة الاكتمال

### 9.1 خدمات ممتازة (A+ Grade) - نموذج يُحتذى

| الخدمة | السبب |
|--------|-------|
| yolo26-vision-service | 5 مراحل، constraints، GPU+CPU، dev stage |
| ai-advisor | multi-stage، venv، constraints، bilingual labels |
| ai-agents-service | multi-stage، constraints، curl health |
| weather-service | multi-stage، venv، pip.conf، dual shared |
| llm-orchestrator-service | multi-stage، constraints-ai.txt، pip.conf |

### 9.2 خدمات جيدة (B Grade) - تحتاج تحسينات بسيطة

| الخدمة | ما ينقصها |
|--------|----------|
| field-management-service | npm mirror |
| knowledge-graph | constraints file |
| whatsapp-bot-service | Aliyun فقط |
| copilot-api | مستخدم copilot بدل sahool |
| virtual-sensors | shared/ جزئي |

### 9.3 خدمات مقبولة (C Grade) - تحتاج عمل

| الخدمة | المشاكل |
|--------|--------|
| advisory-service, alert-service, billing-core, equipment-service, etc. | لا multi-stage، لا constraints |
| vegetation-analysis-service | Aliyun فقط، لا multi-stage |

### 9.4 خدمات ضعيفة (D Grade) - تحتاج إعادة بناء

| الخدمة | المشاكل الحرجة |
|--------|---------------|
| ai-chat-assistant | لا mirror، لا shared/، تعارض منفذ 8230 |
| cooperative-service | Tsinghua فقط، appuser، لا shared/ |
| drone-service | Tsinghua فقط، appuser، لا shared/ |
| soil-analysis-service | Tsinghua فقط، appuser، لا shared/، curl |
| traceability-service | Tsinghua فقط، appuser، لا shared/ |
| leveling-optimizer-service | Tsinghua فقط، appuser/appgroup، لا shared/ |
| supply-chain-service | Aliyun فقط، appuser، لا shared/، تعارض منفذ 8230 |

### 9.5 خدمات فارغة/مهملة (لا تحتاج تدقيق)

| الخدمة | الحالة |
|--------|--------|
| agro-rules | فارغ (worker فقط) |
| demo-data | فارغ |
| community-chat | فارغ/مهمل |
| agro-advisor | مهمل → advisory-service |
| ndvi-engine | مهمل → vegetation-analysis-service |
| weather-core | مهمل → weather-service |
| yield-engine | مهمل → yield-prediction-service |

---

## القسم 10: قالب IDP و Dockerfile.test

### 10.1 IDP Template (`idp/templates/python-fastapi/skeleton/Dockerfile`)

| البند | التقييم |
|-------|---------|
| الصورة | `python:3.11-slim` (يجب bookworm) |
| Multi-stage | ❌ |
| HEALTHCHECK | ❌ غير موجود |
| مستخدم | ✅ sahool |
| pip mirror | ❌ لا يوجد |
| CMD | `python -m src.main` (يجب uvicorn) |

**⛔ هذا القالب يُنشئ خدمات ناقصة** - يجب تحديثه ليطابق المعيار الذهبي.

### 10.2 Dockerfile.test (الجذر)

| البند | التقييم |
|-------|---------|
| الصورة | `python:3.11-slim` |
| HEALTHCHECK | ❌ (طبيعي لحاوية اختبار) |
| مستخدم | ✅ sahool |
| pip mirror | ❌ لا يوجد |
| محتوى | ✅ ينسخ tests/, apps/, packages/, shared/ |

---

## القسم 11: التوصيات | Recommendations

### 11.1 إجراءات فورية (Sprint 1 - أسبوع)

1. **إصلاح تعارض المنافذ**: ai-chat-assistant (8230) و supply-chain-service (8230) - يجب تغيير أحدهما
2. **إضافة shared/ للخدمات المفقودة**: 8 خدمات تحتاج COPY shared/
3. **إصلاح pip mirrors للخدمات بدون mirror**: 4 خدمات
4. **توحيد المستخدم إلى sahool:1000**: 12 خدمة تحتاج تغيير

### 11.2 إجراءات متوسطة المدى (Sprint 2-3)

5. **تحويل إلى multi-stage build**: 37 خدمة Python
6. **إضافة constraints.txt**: 49 خدمة Python
7. **إضافة npm mirror**: 10 خدمات Node.js
8. **توحيد HEALTHCHECK** إلى Python urllib (بدون curl dependency)
9. **تحديث IDP Template** ليطابق المعيار الذهبي

### 11.3 إجراءات طويلة المدى (Sprint 4+)

10. **إضافة OCI Labels** لجميع الخدمات
11. **إضافة virtual environment** لجميع خدمات Python
12. **إضافة HEALTHCHECK لـ Dockerfile.walg** (`pg_isready`)
13. **توحيد CMD pattern** إلى `["uvicorn", ...]` (بدون `sh -c`)
14. **إزالة Dockerfiles المهملة** أو تعليمها بوضوح

---

## القسم 12: إحصائيات ختامية

```
┌────────────────────────────────────────────────────────┐
│           SAHOOL Dockerfile Audit Summary               │
├────────────────────────────────────────────────────────┤
│ إجمالي الملفات المدققة:        82                      │
│ خدمات نشطة:                    67                      │
│ خدمات مهملة:                   7                       │
│ خدمات فارغة/هيكلية:            8                       │
│                                                        │
│ تطابق كامل مع المعيار:         5  (6%)   ████          │
│ تطابق جيد:                     12 (15%)  ████████      │
│ تطابق مقبول:                   38 (46%)  █████████████ │
│ تحتاج إعادة بناء:              7  (9%)   ████          │
│ فارغة/مهملة (لا تحتاج تدقيق):  20 (24%)  ██████████   │
│                                                        │
│ المشاكل الحرجة:                4                       │
│ المشاكل المتوسطة:              12                      │
│ المشاكل المنخفضة:              8                       │
└────────────────────────────────────────────────────────┘
```

---

_تقرير تدقيق مُنشأ بواسطة Claude AI Audit Agent_
_تاريخ: 2026-02-13_
_المراجعة التالية المقترحة: 2026-03-15_
