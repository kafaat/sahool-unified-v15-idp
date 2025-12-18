# 🌾 SAHOOL Platform (v8.3 Enhanced)

منصة **سهول** الزراعية الذكية — نسخة تشغيل محلية *Production-like* عبر Docker Compose.

## ✅ ما الذي أصلحته في هذا الأرشيف؟
النسخة المرفوعة كانت **هيكل/سكافولد** وبداخلها ملفات كثيرة تحتوي `...` أو أسطر مقطوعة (غير قابلة للبناء).
قمتُ بتحويلها إلى مشروع **قابل للتشغيل فعليًا** مع:

- `docker-compose.yml` جاهز
- مفاتيح JWT (RS256) مولّدة داخل `infrastructure/secrets/`
- `.env.example` + `.env`
- استبدال ملفات الخدمات الأساسية بكود TypeScript فعلي (بدون `...`)
- Endpointات عملية (Auth + Gateway + Signals + Advisor + Tasks + Alerts)

> ملاحظة: هذا الإصلاح يجعل المشروع يعمل كبنية **MVP تشغيلية** (يمكن البناء عليها لدمج كل خدمات Sahool الكبيرة لاحقًا).

---

## 🧱 الخدمات الموجودة
- Platform Core:
  - `api-gateway` (port **3000**)
  - `auth-service` (port **3001**)
- Signal Producers:
  - `weather-signal` (3010)
  - `ndvi-signal` (3011)
  - `astronomical-calendar-signal` (3013)
- Decision Services:
  - `crop-advisor` (3020)
- Execution Services:
  - `task-manager` (3030)
  - `alert-dispatcher` (3031)
- Infra:
  - Postgres (5432)
  - Redis (6379)

---

## ▶️ التشغيل
```bash
cd sahool-platform
cp .env.example .env
docker compose up --build
```

### اختبار سريع (Flow كامل)
1) سجّل مستخدم:
```bash
curl -sX POST http://localhost:3001/v1/auth/register   -H "content-type: application/json"   -d '{"email":"test@sahool.local","name":"Test","password":"Password123","tenantId":"default"}'
```

2) خذ الـ token ثم اختبر Gateway:
```bash
TOKEN="ضع_التوكن_هنا"

curl -s http://localhost:3000/health

curl -s http://localhost:3000/api/v1/weather/v1/weather/today   -H "authorization: Bearer $TOKEN"
```

3) اطلب توصية زراعية:
```bash
curl -sX POST http://localhost:3000/api/v1/advisor/v1/advice   -H "authorization: Bearer $TOKEN"   -H "content-type: application/json"   -d '{"fieldId":"field_123","crop":"wheat"}'
```

4) أنشئ مهمة:
```bash
curl -sX POST http://localhost:3000/api/v1/tasks/v1/tasks   -H "authorization: Bearer $TOKEN"   -H "content-type: application/json"   -d '{"title":"فحص الري","fieldId":"field_123","priority":"high"}'
```

---

## 🔒 أمان (مهم)
- غيّر `PASSWORD_PEPPER` في `.env` قبل أي تشغيل حقيقي.
- لا ترفع مفاتيح `infrastructure/secrets/` إلى GitHub في الإنتاج.

---

## 📄 License
MIT (يمكنك وضع ملف LICENSE لاحقًا حسب تفضيلك).

---

## ✅ Unified Enterprise Package (v15.2 + v8.3)

This repository is a merged output:
- **v8.3** provides runnable services + `docker-compose.yml`.
- **v15.2** adds governance, security utilities, observability configs, and Kubernetes/Helm assets.

See `MERGE_REPORT.md` for merge details.

### Quick run (Docker)
```bash
cp .env.example .env
docker compose up --build
```

### Governance audit (v15.2 tool)
```bash
python3 platform/tools/audit/audit.py --help
```


## Kernel v14.1 merged
This package includes kernel v14.1 assets under:
- `platform/kernel-v14.1-docs/`
- `platform/astral/data/seeds/` (also loaded via `infrastructure/postgres/init/10-astral-seeds.sql`)
- `platform-core/kernel-services/`
- Kernel compose references: `docker/docker-compose.kernel.yml`
