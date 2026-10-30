# 🔧 SAHOOL Shared Libraries

# المكتبات المشتركة لمنصة سهول

## نظرة عامة | Overview

هذا المجلد يحتوي على المكتبات والأدوات المشتركة التي تستخدمها جميع خدمات سهول.

This folder contains shared libraries and tools used by all SAHOOL services.

---

## المكونات | Components

### 1. 🗄️ Database Layer | طبقة قاعدة البيانات

```
shared/database/
├── __init__.py      # Exports
├── config.py        # Database configuration
├── session.py       # Session management
├── base.py          # Base models & mixins
└── repository.py    # Repository pattern
```

### 2. 🔐 Authentication Layer | طبقة المصادقة

```
shared/auth/
├── __init__.py      # Exports
├── config.py        # Auth configuration
├── jwt.py           # JWT token handling
├── password.py      # Password hashing
├── models.py        # User, Role, Permission
├── rbac.py          # Role-Based Access Control
└── dependencies.py  # FastAPI dependencies
```

### 3. 🔗 Integration Layer | طبقة التكامل

```
shared/integration/
├── __init__.py         # Exports
├── client.py           # Service client
├── circuit_breaker.py  # Circuit breaker pattern
└── discovery.py        # Service discovery
```

### 4. ⚖️ Compliance Layer | طبقة الامتثال

```
shared/compliance/
├── __init__.py         # Exports
└── routes_gdpr.py      # GDPR compliance endpoints
```

### 5. 📌 Versions | الإصدارات

```
shared/versions.py      # Unified library versions
```

---

## 🗄️ Database Layer | طبقة قاعدة البيانات

### الاستخدام | Usage

```python
from shared.database import (
    get_db,
    Base,
    TimestampMixin,
    TenantMixin,
    BaseRepository,
)

# إنشاء نموذج
class Farm(Base, TimestampMixin, TenantMixin):
    __tablename__ = "farms"

    name = Column(String(255))
    area_hectares = Column(Float)

# Repository
class FarmRepository(BaseRepository[Farm]):
    def __init__(self, db: Session):
        super().__init__(Farm, db)

    def get_by_tenant(self, tenant_id: str):
        return self.get_by_tenant_id(tenant_id)

# استخدام في FastAPI
@app.get("/farms")
async def get_farms(db: Session = Depends(get_db)):
    repo = FarmRepository(db)
    return repo.get_all()
```

### Mixins المتاحة

| Mixin             | الوصف                   |
| ----------------- | ----------------------- |
| `TimestampMixin`  | created_at, updated_at  |
| `TenantMixin`     | tenant_id للعزل         |
| `UUIDMixin`       | UUID primary key        |
| `AuditMixin`      | created_by, updated_by  |
| `SoftDeleteMixin` | deleted_at للحذف الناعم |

---

## 🔐 Authentication Layer | طبقة المصادقة

### إنشاء توكن | Creating Tokens

```python
from shared.auth import create_access_token, create_refresh_token

# توكن وصول
token = create_access_token(
    user_id="user-123",
    email="user@example.com",
    tenant_id="tenant-456",
    roles=["farm_manager"],
)

# توكن تحديث
refresh = create_refresh_token(user_id="user-123")
```

### حماية Endpoints

```python
from shared.auth import (
    get_current_user,
    get_current_active_user,
    require_roles,
    require_permissions,
)

# مستخدم مصادق
@app.get("/profile")
async def get_profile(user: User = Depends(get_current_active_user)):
    return {"user": user.email}

# يتطلب دور معين
@app.post("/farms")
async def create_farm(
    user: User = Depends(require_roles(["farm_manager", "tenant_admin"]))
):
    pass

# يتطلب صلاحية معينة
@app.delete("/farms/{id}")
async def delete_farm(
    user: User = Depends(require_permissions(["farm:delete"]))
):
    pass
```

### الأدوار المعرفة | Predefined Roles

| الدور            | الوصف         | الصلاحيات             |
| ---------------- | ------------- | --------------------- |
| `super_admin`    | مدير النظام   | كل شيء                |
| `tenant_admin`   | مدير المستأجر | كل شيء في المستأجر    |
| `farm_manager`   | مدير المزرعة  | إدارة المزارع والحقول |
| `field_operator` | مشغل الحقل    | عمليات الحقل          |
| `agronomist`     | مهندس زراعي   | تحليل المحاصيل        |
| `viewer`         | مشاهد         | قراءة فقط             |

---

## 🔗 Integration Layer | طبقة التكامل

### Service Client

```python
from shared.integration import get_service_client, ServiceName

# إنشاء عميل
weather = get_service_client(ServiceName.WEATHER)

# طلب GET
response = await weather.get("/v1/current/sanaa")
if response.success:
    print(response.data)

# طلب POST
response = await weather.post("/v1/analyze", json={"data": "..."})
```

### دوال مساعدة | Helper Functions

```python
from shared.integration import (
    get_current_weather,
    get_weather_forecast,
    get_tenant_subscription,
    record_usage,
    check_quota,
    send_notification,
)

# الطقس
weather = await get_current_weather("sanaa")

# الاشتراك والاستخدام
subscription = await get_tenant_subscription("tenant-123")
await record_usage("tenant-123", "ai_analysis", 1)

# الإشعارات
await send_notification("tenant-123", "تنبيه", "رطوبة عالية")
```

### Circuit Breaker

```python
from shared.integration import CircuitBreaker, get_circuit_breaker

breaker = get_circuit_breaker("weather-api")

async def fetch_weather():
    return await api_call()

# مع fallback
result = await breaker.call(
    fetch_weather,
    fallback=lambda: {"temp": 25}  # قيمة افتراضية
)
```

### Service Discovery

```python
from shared.integration import get_service_discovery

discovery = get_service_discovery()
await discovery.start_health_checks()

# فحص صحة خدمة
health = discovery.get_service_health("weather-service")

# ملخص
summary = discovery.get_summary()
print(f"Healthy: {summary['healthy']}/{summary['total_services']}")
```

---

## 📌 Unified Versions | الإصدارات الموحدة

```python
from shared.versions import VERSIONS, SERVICE_PORTS, get_service_url

# إصدار مكتبة
print(VERSIONS["fastapi"])  # "0.128.5"

# منفذ خدمة
print(SERVICE_PORTS["weather-service"])  # 8092

# URL خدمة
url = get_service_url("billing-core")  # "http://localhost:8089"
```

---

## التثبيت | Installation

```bash
# في كل خدمة، أضف للـ PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/apps/services"

# أو في requirements.txt
-e ../shared
```

---

## ⚖️ Compliance Layer | طبقة الامتثال

### GDPR Endpoints

```python
from shared.compliance import gdpr_router

# إضافة مسارات GDPR
app.include_router(gdpr_router)
```

### المسارات المتاحة | Available Endpoints

| المسار                                     | الوصف              | GDPR Article   |
| ------------------------------------------ | ------------------ | -------------- |
| `POST /gdpr/export`                        | طلب تصدير البيانات | Article 15, 20 |
| `POST /gdpr/delete`                        | طلب حذف البيانات   | Article 17     |
| `GET /gdpr/consent/{user_id}`              | عرض الموافقات      | -              |
| `POST /gdpr/consent`                       | تسجيل موافقة       | -              |
| `DELETE /gdpr/consent/{user_id}/{purpose}` | إلغاء موافقة       | -              |
| `GET /gdpr/audit/{user_id}`                | سجل التدقيق        | Article 15     |
| `GET /gdpr/status`                         | حالة الامتثال      | -              |

---

## أفضل الممارسات | Best Practices

1. **استخدم Repository Pattern** لجميع عمليات قاعدة البيانات
2. **استخدم Mixins** لتجنب تكرار الكود
3. **استخدم Circuit Breaker** للاتصال بين الخدمات
4. **تحقق من الصلاحيات** قبل كل عملية حساسة
5. **سجل الاستخدام** لكل عملية مدفوعة
6. **استخدم GDPR routes** لجميع طلبات الامتثال
