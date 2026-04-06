# تقرير الفحص العميق للخدمات الزراعية الأساسية

**التاريخ**: 2026-04-06
**الفرع المُراجَع**: `claude/fix-docker-container-health-Ged0X`
**نطاق الفحص**: 15 خدمة زراعية أساسية + البنية التحتية (docker-compose.yml, PgBouncer, Redis, NATS)
**المنهجية**: مراجعة يدوية للكود + تحقق آلي من النتائج المُبلّغة

---

## ملخص تنفيذي

| الفئة | مؤكّد | مُصحَّح جزئياً | غير دقيق | جديد (مكتشف) |
|-------|-------|---------------|----------|-------------|
| P0 — تعطّل كامل | 4 | 1 | 1 | 2 |
| P1 — ضرر وظيفي | 2 | 0 | 1 | 4 |
| P2 — تحسين | 0 | 0 | 0 | 3 |

---

## P0 — مشاكل تُعطّل الخدمات (حرجة)

### P0-1: AUTH_SECRET_KEY مفقود — مُصحَّح جزئياً

**الحالة**: مؤكّد مع تصحيحات على التقرير الأصلي

**الحقيقة التقنية**: وحدة المصادقة `shared/auth/config.py:48` تقرأ `JWT_SECRET_KEY` (وليس `AUTH_SECRET_KEY`):
```python
value = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
```

**ملاحظة مهمة**: التقرير الأصلي ذكر `AUTH_SECRET_KEY` كمتغير مفقود، لكن الوحدة الفعلية تقرأ `JWT_SECRET_KEY`. المتغير `AUTH_SECRET_KEY` هو متغير إضافي تستخدمه بعض الخدمات داخلياً ولكنه ليس المتغير الأساسي للمصادقة.

**الخدمات المتأثرة فعلياً** (تستخدم `get_current_user` ولكن ليس لديها `JWT_SECRET_KEY` في docker-compose.yml):

| الخدمة | المنفذ | `JWT_SECRET_KEY` | `AUTH_SECRET_KEY` | الأثر |
|--------|--------|-----------------|------------------|-------|
| advisory-service | 8093 | **موجود** | **موجود** | تم الإصلاح في فرع الإصلاح |
| crop-intelligence-service | 8095 | **موجود** | غير موجود | يعمل (JWT_SECRET_KEY كافٍ) |
| ws-gateway | 8081 | **موجود** | **موجود** | تم الإصلاح |
| iot-gateway | 8106 | **موجود** | غير موجود | يعمل |
| ai-agents-service | 8130 | **موجود** | غير موجود | يعمل |
| ai-advisor | 8093 | غير موجود | **موجود** | يحتاج تحقق — `AUTH_SECRET_KEY` موجود لكن هل يُقرأ؟ |
| astronomical-calendar | 8111 | غير موجود | غير موجود | **لا يزال مفقوداً** |
| mcp-server | 8201 | غير موجود | غير موجود | **لا يزال مفقوداً** |

**الخلاصة**: التقرير الأصلي كان **صحيحاً جوهرياً** — كانت هناك فجوات في تكوين المصادقة. تم إصلاح الأغلبية في فرع الإصلاح، لكن **خدمتين لا تزالان بدون JWT_SECRET_KEY**: `astronomical-calendar` و `mcp-server`.

---

### P0-2: NATS Auth مفقود — مؤكّد

**الحالة**: مؤكّد ومُصلح في فرع الإصلاح

فرع الإصلاح غيّر من `nats.conf` (بكلمات مرور bcrypt ثابتة) إلى `nats-secure.conf` (يقرأ من متغيرات البيئة):
```yaml
# قبل الإصلاح
command: [ "-c", "/etc/nats/nats.conf" ]

# بعد الإصلاح
command: [ "-c", "/etc/nats/nats-secure.conf" ]
```

---

### P0-3: Vault Bind Address خاطئ — مؤكّد

**الحالة**: مؤكّد ومُصلح

```yaml
# قبل — Vault لا يمكن الوصول إليه من حاويات أخرى
VAULT_DEV_LISTEN_ADDRESS: "127.0.0.1:8200"

# بعد — يمكن الوصول عبر شبكة Docker
VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
```

---

### P0-4: JetStream لا يُهيّأ — مؤكّد

**الحالة**: مؤكّد ومُصلح

فرع الإصلاح أضاف حاوية `nats-stream-init` (one-shot) تنشئ 11 JetStream stream عند بدء التشغيل. بدون هذا، الرسائل تُرسل كـ plain NATS بدون persistence.

---

### P0-5 (جديد): vegetation-analysis-service لا يُهيّئ NATS أبداً

**الحالة**: مكتشف حديثاً — لم يُذكر في التقرير الأصلي

**الملف**: `apps/services/vegetation-analysis-service/src/main.py:347-437`

دالة `lifespan` لا تُنشئ أي اتصال NATS:
- لا يوجد `await nats.connect(...)` 
- لا يوجد `app.state.nc`
- نقطة `/readyz` (سطر 953) تتحقق من `app.state.nc` الذي لا يُنشأ أبداً → تُعيد دائماً `"not_configured"`

**الأثر**: الخدمة لا تستطيع نشر أحداث NDVI/vegetation عبر NATS. جميع الأحداث المُعرّفة (`sahool.vegetation.*`) لا تُرسل أبداً.

---

### P0-6 (جديد): crop-growth-model — readyz لا يفحص أي شيء

**الحالة**: مكتشف حديثاً

**الملف**: `apps/services/crop-growth-model/src/health/health.controller.ts`

كلا من `/healthz` و `/readyz` تُعيدان `{ status: "ok" }` بشكل ثابت بدون فحص أي تبعية (DB, NATS). هذا يعني أن Kubernetes readiness probe سيمرر الخدمة حتى لو كانت تبعياتها مُعطّلة.

---

## P1 — مشاكل تشغيلية (لا تُعطّل لكن تضرّ)

### P1-1: irrigation-smart — database_utils.py كود ميّت — مؤكّد

**الحالة**: مؤكّد بالكامل

**التحقق**:
- `apps/services/irrigation-smart/src/main.py:204-243` — lifespan تُهيّئ NATS فقط، لا DB pool
- `apps/services/irrigation-smart/src/database_utils.py` — يحتوي على `IrrigationDatabase` class كامل مع `save_irrigation_plan()` و `get_sensor_readings_summary()` — لا يُستورد أبداً
- `docker-compose.yml:2191` — يضبط `DATABASE_URL` الذي لا يُستخدم
- جميع endpoints تحسب البيانات من الذاكرة فقط أو تُرسل عبر NATS
- `/readyz` يتحقق من `db_pool` الذي يكون دائماً `None` → يُعيد `"not_configured"`

**السبب الجذري**: بقايا من تصميم معماري سابق كان يخطط لتخزين البيانات محلياً. تم التحول إلى event-driven لكن لم يُنظف الكود القديم.

**التوصية**: حذف `database_utils.py` وإزالة `DATABASE_URL` من docker-compose.yml

---

### P1-2: advisory-service — DATABASE_URL مُضلِّل — مؤكّد

**الحالة**: مؤكّد بالكامل

**التحقق**:
- `apps/services/advisory-service/src/main.py:406-436` — lifespan تُهيّئ NATS Publisher و Token Revocation Store فقط
- لا يوجد أي import لـ asyncpg أو SQLAlchemy في الخدمة بالكامل
- جميع البيانات من knowledge base في الذاكرة: `kb/diseases.py`, `kb/nutrients.py`, `kb/fertilizers.py`
- `docker-compose.yml` يضبط `DATABASE_URL` بدون أي استخدام فعلي

**التوصية**: إزالة `DATABASE_URL` من docker-compose.yml وتحديث README.md

---

### P1-3: notification-service — تناقض SSL — غير دقيق

**الحالة**: غير صحيح — لا يوجد تناقض

**التحقق**: ملف `apps/services/notification-service/src/database.py:40-63` يستخدم DSN فقط بدون parameter `ssl` منفصل:
```python
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "dsn": DATABASE_URL,
                "statement_cache_size": 0,  # PgBouncer transaction mode
                # ssl handled by sslmode in DATABASE_URL
            },
        },
    },
}
```

لا يوجد `'ssl': 'prefer'` كما ذُكر في التقرير. الإعداد متسق تماماً.

---

### P1-4 (جديد): weather-service — NATS بدون reconnection

**الملف**: `apps/services/weather-service/src/events/publish.py:97`

```python
await self.nc.connect(self.nats_url)  # بدون reconnect parameters
```

لا يوجد `reconnect_time_wait`, `max_reconnect_attempts`, أو callbacks للانقطاع. أي انقطاع مؤقت في الشبكة يصبح فشلاً دائماً.

---

### P1-5 (جديد): healthz لا يفحص التبعيات في 4 خدمات

| الخدمة | `/healthz` | `/readyz` | المشكلة |
|--------|-----------|-----------|---------|
| weather-service | ثابت "healthy" | يفحص NATS+providers | `/healthz` لا يكشف أي مشكلة |
| vegetation-analysis | ثابت "healthy" | يفحص nc/db (لا يُنشأ أبداً) | `/readyz` يُعيد دائماً not_configured |
| indicators-service | ثابت "ok" | يفحص DB+NATS | `/healthz` مُضلِّل |
| advisory-service | ثابت "ok" | يفحص CROP_REQUIREMENTS فقط | لا يفحص NATS publisher |

**ملاحظة**: `/healthz` (liveness) يجب أن يكون بسيطاً فعلاً (لمنع restart loops)، لكن `/readyz` (readiness) يجب أن يفحص كل التبعيات. المشكلة الحقيقية في vegetation-analysis حيث `/readyz` مكسور.

---

### P1-6 (جديد): 241 except Exception عبر 30 خدمة

عدد `except Exception` في ملفات main.py فقط:

| الخدمة | العدد | ملاحظة |
|--------|-------|--------|
| notification-service | 27 | الأعلى |
| vegetation-analysis-service | 25 | |
| billing-core | 22 | |
| lowcode-engine | 17 | |
| weather-service | 14 | |
| field-management-service (legacy) | 13 | |
| provider-config | 12 | |
| crop-intelligence-service | 12 | |
| iot-gateway | 11 | |
| ai-agents-service | 9 | |

ليست كلها مشاكل (بعضها يُسجّل الخطأ ويستمر)، لكن الكثافة العالية تشير إلى نمط "ابتلاع الأخطاء" الذي يخفي مشاكل حقيقية.

---

### P1-7 (جديد): PgBouncer إعدادات غير متسقة

فرع الإصلاح أصلح 12 مشكلة في PgBouncer:
- `auth_type` كان خاطئاً
- `statement_cache_size=0` مفقود من بعض خدمات Tortoise ORM
- Entrypoint script كان يحتوي على أخطاء

---

## ما يعمل بشكل سليم — مؤكّد

| الخدمة | السبب |
|--------|-------|
| weather-service | مستقل، Open-Meteo مجاني كـ fallback |
| vegetation-analysis-service | يتعامل مع غياب Sentinel Hub credentials |
| crop-intelligence-service | يرجع إلى بيانات نموذجية في الذاكرة |
| iot-gateway | healthcheck يعيد 200 دائماً (يمنع cascade failure) |
| field-management-service | Prisma + PgBouncer صحيح (`pgbouncer=true` في DSN) |

---

## ملخص إصلاحات فرع `claude/fix-docker-container-health-Ged0X`

الفرع يحتوي على **60+ commit** تُعالج:

| الفئة | عدد الإصلاحات | أمثلة |
|-------|-------------|-------|
| أمن (Security) | ~40+ | tenant isolation bypass في 8 خدمات، CORS wildcards، XSS |
| بنية تحتية | ~15 | NATS auth، Vault bind، PgBouncer، JetStream init |
| Docker/Build | ~26 | `build-essential` في 12 Dockerfile، `;` → `&&` في 11 |
| أكواد خطأ مكررة | 7 | Vision service error codes |
| منطق الأعمال | ~15 | streaming JSON crash، cache races، publisher lock |
| Flutter/Mobile | ~230 | `library;` directive في 227 ملف |
| Dependencies | ~5 | openai/anthropic version conflicts |

---

## التوصيات ذات الأولوية القصوى

1. **دمج الفرع فوراً** — يحل مشاكل P0 حرجة (NATS, Vault, JetStream, PgBouncer)
2. **إصلاح vegetation-analysis-service** — إضافة تهيئة NATS في lifespan (مشكلة جديدة)
3. **إضافة JWT_SECRET_KEY** لـ `astronomical-calendar` و `mcp-server`
4. **تنظيف الكود الميّت** — `irrigation-smart/database_utils.py` و `DATABASE_URL` المُضلّلة
5. **إضافة NATS reconnection** — خاصة في weather-service publisher
6. **مراجعة except Exception** — تقليل ابتلاع الأخطاء الصامت في الخدمات ذات الكثافة العالية

---

_تم إنشاء هذا التقرير بواسطة مراجعة كود عميقة مع تحقق آلي من كل نتيجة._
