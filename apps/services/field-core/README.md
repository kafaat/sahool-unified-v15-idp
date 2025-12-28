# ⚠️ DEPRECATED - Use field-management-service instead

This service has been deprecated and merged into `field-management-service`.
Please update your references to use `field-management-service` on port 3000.

---


# Field Core Service - خدمة الحقول الأساسية

## نظرة عامة | Overview

خدمة إدارة الحقول الأساسية مع دعم PostGIS للاستعلامات الجغرافية ومزامنة الهاتف المحمول.

Core field management service with PostGIS support for geospatial queries and mobile synchronization.

**Port:** 3000
**Version:** 16.0.0
**Stack:** TypeScript, Express, TypeORM, PostGIS

---

## الميزات | Features

### إدارة الحقول | Field Management
| الميزة | Feature | الوصف |
|--------|---------|--------|
| إنشاء الحقول | Field CRUD | إدارة كاملة للحقول |
| الحدود الجغرافية | GeoJSON Boundaries | حدود مضلعة دقيقة |
| الاستعلامات المكانية | Spatial Queries | البحث القريب |
| حساب المساحة | Area Calculation | PostGIS تلقائي |

### مزامنة الهاتف | Mobile Sync (Delta Sync)
| الميزة | Feature | الوصف |
|--------|---------|--------|
| Delta Sync | تزامن تفاضلي | فقط التغييرات الجديدة |
| Batch Upload | رفع مجمع | مزامنة عدة حقول |
| Conflict Resolution | حل التعارضات | ETag + server_version |
| Offline Support | دعم عدم الاتصال | العمل بدون إنترنت |

### تحليل NDVI | NDVI Analysis
| الميزة | Feature | الوصف |
|--------|---------|--------|
| Current NDVI | NDVI الحالي | القيمة الحالية |
| Trend Analysis | تحليل الاتجاه | تحسن/انخفاض/مستقر |
| History | السجل التاريخي | 30 يوم |
| Tenant Summary | ملخص المستأجر | إحصائيات شاملة |

### سجل الحدود | Boundary History
| الميزة | Feature | الوصف |
|--------|---------|--------|
| Version Tracking | تتبع الإصدارات | كل تغيير محفوظ |
| Rollback | استرجاع | العودة لحدود سابقة |
| Change Audit | تدقيق التغييرات | من/متى/لماذا |

---

## API Endpoints

### الحقول | Fields

```http
# قائمة الحقول
GET /api/v1/fields?tenantId=xxx&status=active&cropType=wheat

# حقل بالـ ID (يُرجع ETag)
GET /api/v1/fields/{id}

# إنشاء حقل
POST /api/v1/fields
{
    "name": "حقل القمح الشمالي",
    "tenantId": "tenant_001",
    "cropType": "wheat",
    "coordinates": [[44.1, 15.3], [44.2, 15.3], [44.2, 15.4], [44.1, 15.4]],
    "irrigationType": "drip",
    "soilType": "loam"
}

# تحديث حقل (مع If-Match للتعارضات)
PUT /api/v1/fields/{id}
Headers: If-Match: "etag-value"
{
    "name": "اسم جديد",
    "status": "active"
}

# حذف حقل
DELETE /api/v1/fields/{id}

# الحقول القريبة
GET /api/v1/fields/nearby?lat=15.3694&lng=44.1910&radius=5000
```

### مزامنة الهاتف | Mobile Sync

```http
# Delta Sync - جلب التغييرات منذ آخر مزامنة
GET /api/v1/fields/sync?tenantId=xxx&since=2024-01-01T00:00:00Z

# Batch Upload - رفع عدة حقول
POST /api/v1/fields/sync/batch
{
    "deviceId": "device_123",
    "userId": "user_001",
    "tenantId": "tenant_001",
    "fields": [
        { "id": "field_001", "client_version": 5, "name": "تحديث" },
        { "_isNew": true, "name": "حقل جديد", "cropType": "corn" }
    ]
}

# حالة المزامنة
GET /api/v1/sync/status?deviceId=xxx&tenantId=xxx

# تحديث حالة المزامنة
PUT /api/v1/sync/status
{
    "deviceId": "device_123",
    "userId": "user_001",
    "tenantId": "tenant_001",
    "lastSyncVersion": 100
}
```

### تحليل NDVI

```http
# NDVI للحقل
GET /api/v1/fields/{id}/ndvi

Response:
{
    "current": { "value": 0.72, "category": "healthy" },
    "statistics": { "average": 0.68, "trend": 0.05, "trendDirection": "improving" },
    "history": [...]
}

# تحديث NDVI
PUT /api/v1/fields/{id}/ndvi
{
    "value": 0.75,
    "source": "satellite"
}

# ملخص NDVI للمستأجر
GET /api/v1/ndvi/summary?tenantId=xxx
```

### سجل الحدود

```http
# سجل تغييرات الحدود
GET /api/v1/fields/{id}/boundary-history

# استرجاع حدود سابقة
POST /api/v1/fields/{id}/boundary-history/rollback
{
    "historyId": "history_001",
    "userId": "user_001",
    "reason": "خطأ في الرسم"
}
```

---

## Optimistic Locking (ETag)

```
1. GET /api/v1/fields/{id}
   Response Headers: ETag: "field_001-v5"
   Response Body: { ..., "etag": "field_001-v5", "server_version": 5 }

2. PUT /api/v1/fields/{id}
   Request Headers: If-Match: "field_001-v5"

3a. Success (200): { ..., "etag": "field_001-v6" }

3b. Conflict (409):
    {
        "success": false,
        "error": "Conflict",
        "serverData": { ... },
        "currentEtag": "field_001-v7"
    }
```

---

## نماذج البيانات | Data Models

### Field
```json
{
    "id": "field_001",
    "tenantId": "tenant_001",
    "name": "حقل القمح الشمالي",
    "cropType": "wheat",
    "status": "active",
    "boundary": {
        "type": "Polygon",
        "coordinates": [[[44.1, 15.3], [44.2, 15.3], [44.2, 15.4], [44.1, 15.4], [44.1, 15.3]]]
    },
    "centroid": {
        "type": "Point",
        "coordinates": [44.15, 15.35]
    },
    "areaHectares": 120.5,
    "ndviValue": 0.72,
    "healthScore": 0.85,
    "version": 5,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-02-15T10:30:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=3000

# قاعدة البيانات (PostGIS)
DATABASE_URL=postgresql://user:pass@host:5432/sahool_fields

# أو بالتفصيل
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sahool_fields
DB_USER=sahool
DB_PASSWORD=secret
```

---

## Health Check

```http
GET /healthz
Response: { "status": "healthy", "service": "field-core" }

GET /readyz
Response: { "status": "ready", "database": "connected" }
```

---

---

## تحليل الربحية | Profitability Analysis

### نظرة عامة | Overview

تحليل شامل لربحية المحاصيل لمساعدة المزارعين على فهم أي المحاصيل أكثر ربحية. مستوحى من LiteFarm.

Comprehensive crop profitability analysis to help farmers understand which crops are most profitable. Inspired by LiteFarm.

**Port:** 8090 (Python Service)
**Features:**
- تحليل ربحية المحصول الفردي | Individual Crop Analysis
- ملخص الموسم مع الترتيب | Season Summary with Rankings
- تحليل التعادل | Break-even Analysis
- المعايير الإقليمية | Regional Benchmarks
- الاتجاهات التاريخية | Historical Trends
- مقارنة المحاصيل | Crop Comparison
- تفصيل التكاليف | Cost Breakdown
- دعم العربية والإنجليزية | Arabic & English Support

### المحاصيل المدعومة | Supported Crops

| المحصول | Crop | الإنتاجية (كجم/هكتار) | السعر (ريال/كجم) |
|---------|------|----------------------|------------------|
| قمح | Wheat | 2,800 | 550 |
| طماطم | Tomato | 25,000 | 280 |
| ذرة رفيعة | Sorghum | 2,200 | 400 |
| بطاطس | Potato | 18,000 | 350 |
| بصل | Onion | 22,000 | 300 |
| بن | Coffee | 800 | 8,500 |
| قات | Qat | 3,500 | 3,500 |
| شعير | Barley | 2,500 | 480 |
| ذرة شامية | Maize | 3,200 | 520 |
| خيار | Cucumber | 20,000 | 250 |
| بطيخ | Watermelon | 30,000 | 180 |
| مانجو | Mango | 12,000 | 800 |

### فئات التكاليف | Cost Categories

- بذور | Seeds
- أسمدة | Fertilizer
- مبيدات | Pesticides
- ري | Irrigation
- عمالة | Labor
- آلات | Machinery
- أرض | Land
- تسويق | Marketing
- أخرى | Other

### المقاييس المحسوبة | Calculated Metrics

```
إجمالي الربح = الإيرادات - التكاليف المباشرة
Gross Profit = Revenue - Direct Costs

هامش الربح الإجمالي % = إجمالي الربح / الإيرادات × 100
Gross Margin % = Gross Profit / Revenue × 100

صافي الربح = إجمالي الربح - التكاليف العامة
Net Profit = Gross Profit - Overhead

العائد على الاستثمار % = صافي الربح / إجمالي التكاليف × 100
ROI % = Net Profit / Total Costs × 100

إنتاجية التعادل = إجمالي التكاليف / السعر للوحدة
Break-even Yield = Total Costs / Price per Unit

الربح لكل هكتار = صافي الربح / المساحة
Profit per Hectare = Net Profit / Area
```

### Profitability API Endpoints

```http
# تحليل محصول | Analyze Crop
POST /v1/profitability/analyze
{
    "field_id": "field-001",
    "crop_season_id": "season-2025-1",
    "crop_code": "wheat",
    "area_ha": 2.5,
    "costs": [
        {
            "category": "seeds",
            "description": "بذور قمح ممتازة",
            "amount": 200000,
            "unit": "YER",
            "quantity": 75
        }
    ],
    "revenues": [
        {
            "description": "حصاد القمح",
            "quantity": 7500,
            "unit": "kg",
            "unit_price": 550
        }
    ]
}

# ملخص الموسم | Season Summary
POST /v1/profitability/season
{
    "farmer_id": "farmer-001",
    "season_year": "2025",
    "crops": [
        {"field_id": "field-001", "crop_code": "wheat", "area_ha": 2.5},
        {"field_id": "field-002", "crop_code": "tomato", "area_ha": 1.0}
    ]
}

# مقارنة المحاصيل | Compare Crops
GET /v1/profitability/compare?crops=wheat,tomato,potato&area_ha=1&region=sanaa

# حساب التعادل | Break-even Calculation
GET /v1/profitability/break-even?crop_code=wheat&area_ha=2.5&total_costs=670000&expected_price=550

# المعايير الإقليمية | Regional Benchmarks
GET /v1/profitability/benchmarks/wheat?region=sanaa

# تفصيل التكاليف | Cost Breakdown
GET /v1/profitability/cost-breakdown/wheat?area_ha=2.5

# البيانات التاريخية | Historical Data
GET /v1/profitability/history/field-001/wheat?years=5

# قائمة المحاصيل | List Crops
GET /v1/crops/list

# فئات التكاليف | Cost Categories
GET /v1/costs/categories
```

### Running Python Profitability Service

```bash
# Development
cd apps/services/field-core
pip install -r requirements.txt
python src/main.py

# Docker
docker build -f Dockerfile.python -t sahool-field-profitability .
docker run -p 8090:8090 sahool-field-profitability

# Docker Compose
services:
  field-profitability:
    build:
      context: ./apps/services/field-core
      dockerfile: Dockerfile.python
    ports:
      - "8090:8090"
    environment:
      - PORT=8090
      - DATABASE_URL=postgresql://user:pass@db:5432/sahool
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run profitability tests
pytest tests/test_profitability.py -v

# Run API integration tests
pytest tests/test_api.py -v

# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### أمثلة الاستخدام | Usage Examples

#### تحليل محصول مع البيانات الإقليمية
```bash
curl "http://localhost:8090/v1/profitability/crop/season-2025-1?\
field_id=field-123&\
crop_code=wheat&\
area_ha=2.5"
```

#### تحليل مع التكاليف والإيرادات المخصصة
```bash
curl -X POST "http://localhost:8090/v1/profitability/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-123",
    "crop_season_id": "season-2025-1",
    "crop_code": "wheat",
    "area_ha": 2.5,
    "costs": [
      {
        "category": "seeds",
        "description": "بذور قمح - صنف ممتاز",
        "amount": 200000,
        "unit": "YER",
        "quantity": 75,
        "unit_cost": 2666.67
      }
    ],
    "revenues": [
      {
        "description": "حصاد القمح - درجة ممتازة",
        "quantity": 7500,
        "unit": "kg",
        "unit_price": 550,
        "grade": "premium"
      }
    ]
  }'
```

#### مقارنة المحاصيل للتخطيط
```bash
curl "http://localhost:8090/v1/profitability/compare?\
crops=wheat,tomato,potato,coffee&\
area_ha=5&\
region=sanaa"
```

### Integration with SAHOOL Platform

The profitability service integrates with:
- **Field Service** - Field and crop season data
- **Field Ops** - Operation costs and harvest data
- **Market Service** - Real-time crop prices
- **Advisory Services** - Recommendations based on profitability

---

## الترخيص | License

Proprietary - KAFAAT © 2024
