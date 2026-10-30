# 💰 SAHOOL Billing Core Service

# خدمة الفوترة الأساسية

## نظرة عامة | Overview

خدمة الفوترة الأساسية هي المسؤولة عن إدارة الاشتراكات والفواتير والمدفوعات لمنصة سهول.

The Billing Core Service manages subscriptions, invoices, and payments for the SAHOOL platform.

**Version:** 15.4.0
**Port:** 8089
**Status:** Production Ready

---

## المميزات | Features

### 1. إدارة الخطط | Plan Management

- 4 خطط تسعير (Free, Starter, Professional, Enterprise)
- حدود استخدام قابلة للتخصيص
- تسعير متعدد العملات (USD, YER)

### 2. إدارة الاشتراكات | Subscription Management

- دورة حياة كاملة للاشتراك
- ترقية/تخفيض تلقائي
- فترات تجريبية
- إلغاء مع أو بدون استرداد

### 3. الفواتير | Invoicing

- توليد فواتير تلقائي
- بنود تفصيلية
- ضرائب قابلة للتخصيص
- تحويل العملات

### 4. المدفوعات | Payments

- تكامل مع Stripe
- تسجيل المدفوعات
- تتبع الحالة
- استرداد المدفوعات

### 5. تتبع الاستخدام | Usage Tracking

- مراقبة الاستخدام الفوري
- إنفاذ الحصص
- تنبيهات عند قرب الحد

---

## API Endpoints

### Health Check

```http
GET /healthz
```

### Plans | الخطط

```http
GET  /v1/plans                    # قائمة الخطط
GET  /v1/plans/{plan_id}          # تفاصيل خطة
POST /v1/plans                    # إنشاء خطة (admin)
```

### Tenants | المستأجرين

```http
POST  /v1/tenants                          # تسجيل مستأجر جديد
GET   /v1/tenants/{tenant_id}              # معلومات المستأجر
GET   /v1/tenants/{tenant_id}/subscription # تفاصيل الاشتراك
PATCH /v1/tenants/{tenant_id}/subscription # تحديث الاشتراك
POST  /v1/tenants/{tenant_id}/cancel       # إلغاء الاشتراك
```

### Usage | الاستخدام

```http
POST /v1/tenants/{tenant_id}/usage    # تسجيل استخدام
GET  /v1/tenants/{tenant_id}/quota    # حالة الحصة
GET  /v1/enforce                      # التحقق من الحدود
```

### Invoices | الفواتير

```http
GET  /v1/tenants/{tenant_id}/invoices         # قائمة الفواتير
GET  /v1/invoices/{invoice_id}                # تفاصيل فاتورة
POST /v1/tenants/{tenant_id}/invoices/generate # توليد فاتورة
```

### Payments | المدفوعات

```http
POST /v1/payments                       # تسجيل دفعة
GET  /v1/tenants/{tenant_id}/payments   # سجل المدفوعات
```

### Reports | التقارير

```http
GET /v1/reports/revenue       # تقرير الإيرادات
GET /v1/reports/subscriptions # تقرير الاشتراكات
```

---

## خطط التسعير | Pricing Plans

| الخطة        | السعر/شهر | الحقول | المستخدمين | تحليل AI | API |
| ------------ | --------- | ------ | ---------- | -------- | --- |
| Free         | $0        | 1      | 1          | 10/شهر   | ❌  |
| Starter      | $29       | 5      | 3          | 100/شهر  | ✅  |
| Professional | $99       | 25     | 10         | 500/شهر  | ✅  |
| Enterprise   | $299      | ∞      | ∞          | ∞        | ✅  |

---

## الاستخدام | Usage

### Python Client

```python
from shared.integration import get_service_client, ServiceName

# إنشاء العميل
billing = get_service_client(ServiceName.BILLING)

# الحصول على اشتراك
response = await billing.get("/v1/tenants/tenant-123/subscription")
if response.success:
    subscription = response.data

# تسجيل استخدام
await billing.post("/v1/tenants/tenant-123/usage", json={"usage_type": "ai_analysis", "amount": 1})
```

### cURL Examples

```bash
# الحصول على الخطط
curl http://localhost:8089/v1/plans

# تسجيل مستأجر
curl -X POST http://localhost:8089/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"email": "farm@example.com", "name": "My Farm", "plan_id": "starter"}'

# التحقق من الحصة
curl http://localhost:8089/v1/tenants/tenant-123/quota
```

---

## متغيرات البيئة | Environment Variables

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sahool_billing
DB_USER=sahool
DB_PASSWORD=secret

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Service
SERVICE_PORT=8089
LOG_LEVEL=INFO
```

---

## البنية | Architecture

```
billing-core/
├── src/
│   └── main.py          # FastAPI application
├── requirements.txt      # Dependencies
└── README.md            # This file
```

### Data Models

```
Tenant
├── id (UUID)
├── email
├── name
├── plan_id
├── subscription_status
├── usage (Dict)
└── invoices[]

Invoice
├── id (UUID)
├── tenant_id
├── amount
├── status
├── line_items[]
└── created_at

Payment
├── id (UUID)
├── tenant_id
├── invoice_id
├── amount
├── status
└── payment_method
```

---

## التكامل | Integration

### مع الخدمات الأخرى

```python
# في أي خدمة أخرى
from shared.integration import check_quota, record_usage

# التحقق من الحصة قبل العملية
quota = await check_quota(tenant_id, "ai_analysis")
if quota and quota["remaining"] > 0:
    # تنفيذ العملية
    result = await perform_ai_analysis()
    # تسجيل الاستخدام
    await record_usage(tenant_id, "ai_analysis", 1)
```

---

## Changelog

### v15.4.0 (December 2025)

- إعادة كتابة كاملة للخدمة
- إضافة 4 خطط تسعير
- تكامل Stripe
- نظام فواتير متكامل
- تتبع الاستخدام وإنفاذ الحصص
- تقارير الإيرادات والاشتراكات

### v15.3.0

- الإصدار الأولي (محدود)
