# Service-to-Service Authentication

نظام مصادقة متقدم للتواصل بين الخدمات في منصة SAHOOL، مبني على JWT tokens مع تحكم دقيق في الصلاحيات.

## المزايا الرئيسية

- ✅ **مصادقة آمنة**: استخدام JWT tokens مع claims خاصة للخدمات
- ✅ **تحكم دقيق**: مصفوفة تواصل محددة لكل خدمة (Service Communication Matrix)
- ✅ **دعم كامل**: Python (FastAPI) و TypeScript (NestJS)
- ✅ **سهولة الاستخدام**: Middleware وDecorators جاهزة
- ✅ **TTL قابل للتخصيص**: مدة صلاحية مرنة للـ tokens
- ✅ **رسائل خطأ ثنائية اللغة**: عربي وإنجليزي

## الملفات المُنشأة

### Python (FastAPI)

```
shared/auth/
├── service_auth.py              # ServiceToken class والدوال الأساسية
├── service_middleware.py        # Middleware والـ dependencies
└── service_auth_test_example.py # أمثلة اختبار
```

### TypeScript (NestJS)

```
shared/auth/
├── service_auth.ts              # ServiceToken class والدوال الأساسية
├── service-auth.guard.ts        # Guards والـ decorators
└── service_auth_test_example.ts # أمثلة اختبار
```

### التوثيق

```
shared/auth/
├── SERVICE_AUTH_README.md       # هذا الملف
└── SERVICE_AUTH_EXAMPLES.md     # أمثلة تفصيلية للاستخدام
```

## الاستخدام السريع

### Python (FastAPI)

#### 1. إنشاء Service Token

```python
from shared.auth import create_service_token

# إنشاء token لخدمة farm-service لاستدعاء field-service
token = create_service_token(
    service_name="farm-service",
    target_service="field-service",
    ttl=300,  # 5 دقائق
)

# استخدام الـ token في طلب HTTP
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://field-service/api/fields", headers={"X-Service-Token": token})
```

#### 2. إضافة Middleware للخدمة

```python
from fastapi import FastAPI
from shared.auth import ServiceAuthMiddleware

app = FastAPI()

app.add_middleware(ServiceAuthMiddleware, current_service="field-service", exclude_paths=["/health", "/docs"])
```

#### 3. حماية Endpoints

```python
from fastapi import APIRouter, Depends
from shared.auth import verify_service_request, require_service_auth

router = APIRouter()


# أي خدمة مصادق عليها يمكنها الاستدعاء
@router.get("/internal/data")
async def get_data(service_info: dict = Depends(verify_service_request)):
    return {"data": [...]}


# خدمات محددة فقط
@router.post("/internal/update")
async def update_data(service_info: dict = Depends(require_service_auth(["farm-service"]))):
    return {"status": "updated"}
```

### TypeScript (NestJS)

#### 1. إنشاء Service Token

```typescript
import { createServiceToken } from "./shared/auth/service_auth";
import axios from "axios";

// إنشاء token
const token = createServiceToken("farm-service", "field-service", 300);

// استخدام الـ token
const response = await axios.get("http://field-service/api/fields", {
  headers: { "X-Service-Token": token },
});
```

#### 2. استخدام Guard

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import {
  ServiceAuthGuard,
  AllowedServices,
  ServiceInfo,
} from './shared/auth/service-auth.guard';

@Controller('internal')
export class InternalController {
  @Get('data')
  @UseGuards(ServiceAuthGuard)
  @AllowedServices('farm-service', 'crop-service')
  async getData(@ServiceInfo() serviceInfo) {
    return { data: [...] };
  }
}
```

## قائمة الخدمات المسموح بها

```javascript
const ALLOWED_SERVICES = [
  "idp-service",
  "farm-service",
  "field-service",
  "crop-service",
  "weather-service",
  "advisory-service",
  "analytics-service",
  "equipment-service",
  "precision-ag-service",
  "notification-service",
  "payment-service",
  "user-service",
  "tenant-service",
  "inventory-service",
];
```

## مصفوفة التواصل بين الخدمات

### أمثلة على العلاقات المسموحة:

```
idp-service          → جميع الخدمات ✓
farm-service         → field-service, crop-service, equipment-service ✓
field-service        → crop-service, weather-service, precision-ag-service ✓
notification-service → (تستقبل فقط، لا ترسل) ✓
```

### مثال على علاقة غير مسموحة:

```
notification-service → farm-service ✗ (غير مصرح)
```

لعرض جميع العلاقات المسموحة، راجع `SERVICE_COMMUNICATION_MATRIX` في الملفات.

## متطلبات التثبيت

### Python

```bash
# المكتبات المطلوبة (موجودة بالفعل في معظم الخدمات)
pip install PyJWT fastapi
```

في `requirements.txt`:

```text
PyJWT>=2.8.0
fastapi>=0.100.0
```

### TypeScript

```bash
# المكتبات المطلوبة
npm install jsonwebtoken uuid
npm install -D @types/jsonwebtoken @types/uuid
```

في `package.json`:

```json
{
  "dependencies": {
    "jsonwebtoken": "^9.0.2",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/jsonwebtoken": "^9.0.5",
    "@types/uuid": "^9.0.7"
  }
}
```

## المتغيرات البيئية

```bash
# إعدادات JWT (مشتركة مع نظام مصادقة المستخدمين)
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-api

# اسم الخدمة الحالية (اختياري - للتعريف التلقائي)
SERVICE_NAME=farm-service
```

## الاختبار

### Python

```bash
cd shared/auth
python service_auth_test_example.py
```

### TypeScript

```bash
cd shared/auth
ts-node service_auth_test_example.ts
# أو
npm test  # إذا أضفت script في package.json
```

## أمثلة الاستخدام الكاملة

للحصول على أمثلة تفصيلية وشاملة، راجع:

- 📖 [SERVICE_AUTH_EXAMPLES.md](./SERVICE_AUTH_EXAMPLES.md)

يحتوي على:

- أمثلة كاملة لـ FastAPI
- أمثلة كاملة لـ NestJS
- أمثلة معالجة الأخطاء
- أمثلة الاختبار
- دليل الترحيل (Migration Guide)

## الأمان

### أفضل الممارسات

1. ✅ **استخدم TTL قصير**: 5-10 دقائق كحد أقصى
2. ✅ **أنشئ token جديد لكل طلب**: لا تعيد استخدام tokens
3. ✅ **تحقق من target_service**: تأكد أن الـ token للخدمة الصحيحة
4. ✅ **استخدم HTTPS**: في بيئة الإنتاج
5. ✅ **سجّل جميع المكالمات**: للمراقبة والتدقيق
6. ✅ **حدّث المصفوفة بانتظام**: حافظ على `SERVICE_COMMUNICATION_MATRIX` محدثة

### تحذيرات

⚠️ **لا تضع tokens في logs**
⚠️ **لا تشارك JWT_SECRET بين البيئات**
⚠️ **لا تسمح بعلاقات غير ضرورية** في المصفوفة

## إضافة خدمة جديدة

1. أضف اسم الخدمة إلى `ALLOWED_SERVICES`:

```python
# في service_auth.py
ALLOWED_SERVICES = [
    # ... الخدمات الموجودة
    "new-service",
]
```

2. حدد علاقات التواصل في `SERVICE_COMMUNICATION_MATRIX`:

```python
SERVICE_COMMUNICATION_MATRIX = {
    # ... العلاقات الموجودة
    "new-service": [
        "field-service",
        "crop-service",
    ],
}
```

3. كرر نفس الخطوات في `service_auth.ts`

## استكشاف الأخطاء

### خطأ: "Invalid service name"

**السبب**: اسم الخدمة غير موجود في `ALLOWED_SERVICES`
**الحل**: أضف الخدمة إلى القائمة

### خطأ: "Service is not authorized to call the target service"

**السبب**: العلاقة غير موجودة في `SERVICE_COMMUNICATION_MATRIX`
**الحل**: أضف العلاقة المطلوبة أو راجع التصميم

### خطأ: "Invalid service authentication token"

**الأسباب المحتملة**:

- Token منتهي الصلاحية
- JWT_SECRET مختلف بين الخدمات
- Token تم التلاعب به

**الحل**: تأكد من مطابقة الإعدادات بين جميع الخدمات

### خطأ: "Authentication token has expired"

**السبب**: انتهت صلاحية الـ token
**الحل**: أنشئ token جديد (استخدم TTL أطول إذا لزم الأمر)

## الدعم والمساهمة

للإبلاغ عن مشاكل أو طلب ميزات جديدة:

1. تحقق من [SERVICE_AUTH_EXAMPLES.md](./SERVICE_AUTH_EXAMPLES.md) للحلول الشائعة
2. قم بتشغيل ملفات الاختبار للتأكد من عمل النظام
3. تواصل مع فريق التطوير

## رخصة الاستخدام

هذا النظام جزء من منصة SAHOOL ومخصص للاستخدام الداخلي.

---

**تم الإنشاء**: 2025-12-27
**الإصدار**: 1.0.0
**الحالة**: ✅ جاهز للإنتاج
