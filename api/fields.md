# Field Management APIs
# واجهات برمجة تطبيقات إدارة الحقول

## Overview | نظرة عامة

Field Management APIs provide comprehensive tools for managing agricultural fields, including:
- Field registration and boundaries
- Crop profitability analysis
- Cost and revenue tracking
- Historical data and trends
- Regional benchmarks

توفر واجهات إدارة الحقول أدوات شاملة لإدارة الحقول الزراعية، بما في ذلك:
- تسجيل الحقول والحدود
- تحليل ربحية المحاصيل
- تتبع التكاليف والإيرادات
- البيانات التاريخية والاتجاهات
- المقاييس الإقليمية

## Base URL

**Field Management Service:** `http://localhost:8090`

## Authentication | المصادقة

All endpoints require JWT authentication:

```
Authorization: Bearer <access_token>
```

## Endpoints | نقاط النهاية


### POST /fields

**Service:** field-service (Port: 3000)

**Summary:** Update Boundary

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | boundaryupdate | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:3000/fields \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields

**Service:** field-service (Port: 3000)

**Summary:** Update Boundary

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | boundaryupdate | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /fields/check-overlap

**Service:** field-service (Port: 3000)

**Summary:** Check Overlap

#### Example Request

```bash
curl -X POST http://localhost:3000/fields/check-overlap \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}

**Service:** field-service (Port: 3000)

**Summary:** Update Boundary

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | boundaryupdate | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### PATCH /fields/{field_id}

**Service:** field-service (Port: 3000)

**Summary:** Update Boundary

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | boundaryupdate | ✓ | path |  |

#### Example Request

```bash
curl -X PATCH http://localhost:3000/fields/{field_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### DELETE /fields/{field_id}

**Service:** field-service (Port: 3000)

**Summary:** Update Boundary

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | boundaryupdate | ✓ | path |  |

#### Example Request

```bash
curl -X DELETE http://localhost:3000/fields/{field_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/area

**Service:** field-service (Port: 3000)

**Summary:** Calculate Field Area

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/area \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### PUT /fields/{field_id}/boundary

**Service:** field-service (Port: 3000)

**Summary:** Update Boundary

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | boundaryupdate | ✓ | path |  |

#### Example Request

```bash
curl -X PUT http://localhost:3000/fields/{field_id}/boundary \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /fields/{field_id}/crops

**Service:** field-service (Port: 3000)

**Summary:** Start Crop Season

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `season` | cropseasoncreate | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:3000/fields/{field_id}/crops \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /fields/{field_id}/crops/current/close

**Service:** field-service (Port: 3000)

**Summary:** Close Crop Season

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `close_data` | cropseasonclose | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:3000/fields/{field_id}/crops/current/close \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/crops/history

**Service:** field-service (Port: 3000)

**Summary:** Get Crop History

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `field_id` | str | ✓ | path |  |
| `close_data` | cropseasonclose | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/crops/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/export/geojson

**Service:** field-service (Port: 3000)

**Summary:** Export Field Geojson

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `field_id` | str | ✓ | path |  |
| `season` | cropseasoncreate | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/export/geojson \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/export/kml

**Service:** field-service (Port: 3000)

**Summary:** Export Field Kml

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `field_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/export/kml \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /fields/{field_id}/ndvi

**Service:** field-service (Port: 3000)

**Summary:** Add Ndvi Record

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `record` | ndvirecord | ✓ | path |  |
| `field_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:3000/fields/{field_id}/ndvi \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/ndvi/history

**Service:** field-service (Port: 3000)

**Summary:** Add Ndvi Record

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `record` | ndvirecord | ✓ | path |  |
| `field_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/ndvi/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/stats

**Service:** field-service (Port: 3000)

**Summary:** Get Field Stats

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /fields/{field_id}/zones

**Service:** field-service (Port: 3000)

**Summary:** Create Zone

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `zone` | zonecreate | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:3000/fields/{field_id}/zones \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}/zones

**Service:** field-service (Port: 3000)

**Summary:** List Zones

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `zone_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/fields/{field_id}/zones \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /health

**Service:** field-service (Port: 3000)

**Summary:** فحص الصحة - Health check with dependencies

**الملخص:** فحص الصحة - Health check with dependencies

#### Example Request

```bash
curl -X GET http://localhost:3000/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /healthz

**Service:** field-service (Port: 3000)

**Summary:** فحص الصحة - Kubernetes liveness probe

**الملخص:** فحص الصحة - Kubernetes liveness probe

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field` | fieldcreate | ✓ | path |  |
| `boundary` | is_valid | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/healthz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /readyz

**Service:** field-service (Port: 3000)

**Summary:** فحص الجاهزية - Kubernetes readiness probe

**الملخص:** فحص الجاهزية - Kubernetes readiness probe

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field` | fieldcreate | ✓ | path |  |
| `boundary` | is_valid | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:3000/readyz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### DELETE /zones/{zone_id}

**Service:** field-service (Port: 3000)

**Summary:** Delete Zone

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `limit` | string |  | query |  |
| `zone_id` | str | ✓ | path |  |
| `field_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X DELETE http://localhost:3000/zones/{zone_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /fields

**Service:** field-ops (Port: 8080)

**Summary:** Create Field

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field` | fieldcreate | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:8080/fields \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields

**Service:** field-ops (Port: 8080)

**Summary:** Update Field

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | fieldupdate | ✓ | path |  |
| `field_id` | str | ✓ | path |  |
| `op` | operationcreate | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:8080/fields \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /fields/{field_id}

**Service:** field-ops (Port: 8080)

**Summary:** Get Field

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `tenant_id` | string | ✓ | query |  |
| `skip` | string |  | query |  |
| `limit` | string |  | query |  |
| `field_id` | str | ✓ | path |  |
| `field_id` | str | ✓ | path |  |
| `update` | fieldupdate | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:8080/fields/{field_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### PUT /fields/{field_id}

**Service:** field-ops (Port: 8080)

**Summary:** Update Field

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `update` | fieldupdate | ✓ | path |  |
| `field_id` | str | ✓ | path |  |
| `op` | operationcreate | ✓ | path |  |

#### Example Request

```bash
curl -X PUT http://localhost:8080/fields/{field_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### DELETE /fields/{field_id}

**Service:** field-ops (Port: 8080)

**Summary:** Delete Field

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | str | ✓ | path |  |
| `op` | operationcreate | ✓ | path |  |

#### Example Request

```bash
curl -X DELETE http://localhost:8080/fields/{field_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /healthz

**Service:** field-ops (Port: 8080)

**Summary:** Health

#### Example Request

```bash
curl -X GET http://localhost:8080/healthz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /operations

**Service:** field-ops (Port: 8080)

**Summary:** Create Operation

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | string | ✓ | query |  |
| `op` | operationcreate | ✓ | path |  |
| `operation_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:8080/operations \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /operations

**Service:** field-ops (Port: 8080)

**Summary:** Complete Operation

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `operation_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:8080/operations \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /operations/{operation_id}

**Service:** field-ops (Port: 8080)

**Summary:** Get Operation

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `field_id` | string | ✓ | query |  |
| `skip` | string |  | query |  |
| `limit` | string |  | query |  |
| `operation_id` | str | ✓ | path |  |
| `operation_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:8080/operations/{operation_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /operations/{operation_id}/complete

**Service:** field-ops (Port: 8080)

**Summary:** Complete Operation

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `operation_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X POST http://localhost:8080/operations/{operation_id}/complete \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /readyz

**Service:** field-ops (Port: 8080)

**Summary:** Readiness

#### Example Request

```bash
curl -X GET http://localhost:8080/readyz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /stats/tenant/{tenant_id}

**Service:** field-ops (Port: 8080)

**Summary:** Get Tenant Stats

#### Parameters | المعاملات

| Name | Type | Required | Location | Description |
|------|------|----------|----------|-------------|
| `tenant_id` | str | ✓ | path |  |

#### Example Request

```bash
curl -X GET http://localhost:8080/stats/tenant/{tenant_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /healthz

**Service:** field-core (Port: 8090)

**Summary:** Health

#### Example Request

```bash
curl -X GET http://localhost:8090/healthz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /healthz

**Service:** field-management-service (Port: 8090)

**Summary:** Health

#### Example Request

```bash
curl -X GET http://localhost:8090/healthz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /readyz

**Service:** field-core (Port: 8090)

**Summary:** Readiness

#### Example Request

```bash
curl -X GET http://localhost:8090/readyz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /readyz

**Service:** field-management-service (Port: 8090)

**Summary:** Readiness

#### Example Request

```bash
curl -X GET http://localhost:8090/readyz \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/costs/categories

**Service:** field-core (Port: 8090)

**Summary:** List all available cost categories

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/costs/categories \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/costs/categories

**Service:** field-management-service (Port: 8090)

**Summary:** List all available cost categories

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/costs/categories \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/crops/list

**Service:** field-core (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/crops/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/crops/list

**Service:** field-management-service (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/crops/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /v1/profitability/analyze

**Service:** field-core (Port: 8090)

**Summary:** Analyze Profitability

#### Example Request

```bash
curl -X POST http://localhost:8090/v1/profitability/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /v1/profitability/analyze

**Service:** field-management-service (Port: 8090)

**Summary:** Analyze Profitability

#### Example Request

```bash
curl -X POST http://localhost:8090/v1/profitability/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/benchmarks/{crop_code}

**Service:** field-core (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/benchmarks/{crop_code} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/benchmarks/{crop_code}

**Service:** field-management-service (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/benchmarks/{crop_code} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/break-even

**Service:** field-core (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/break-even \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/break-even

**Service:** field-management-service (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/break-even \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/compare

**Service:** field-core (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/compare \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/compare

**Service:** field-management-service (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/compare \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/cost-breakdown/{crop_code}

**Service:** field-core (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/cost-breakdown/{crop_code} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/cost-breakdown/{crop_code}

**Service:** field-management-service (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/cost-breakdown/{crop_code} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/crop/{crop_season_id}

**Service:** field-core (Port: 8090)

**Summary:** Analyze Profitability

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/crop/{crop_season_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/crop/{crop_season_id}

**Service:** field-management-service (Port: 8090)

**Summary:** Analyze Profitability

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/crop/{crop_season_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/history/{field_id}/{crop_code}

**Service:** field-core (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/history/{field_id}/{crop_code} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### GET /v1/profitability/history/{field_id}/{crop_code}

**Service:** field-management-service (Port: 8090)

**Summary:** List all crops with available profitability data.

Returns crop codes, names in both languages, and regional data availability.

#### Example Request

```bash
curl -X GET http://localhost:8090/v1/profitability/history/{field_id}/{crop_code} \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /v1/profitability/season

**Service:** field-core (Port: 8090)

**Summary:** Get Season Summary

#### Example Request

```bash
curl -X POST http://localhost:8090/v1/profitability/season \
  -H "Authorization: Bearer YOUR_TOKEN"
```


### POST /v1/profitability/season

**Service:** field-management-service (Port: 8090)

**Summary:** Get Season Summary

#### Example Request

```bash
curl -X POST http://localhost:8090/v1/profitability/season \
  -H "Authorization: Bearer YOUR_TOKEN"
```


## Data Models | نماذج البيانات

### Field

```typescript
interface Field {
  id: string;
  tenant_id: string;
  name: string;
  name_ar?: string;
  area_hectares: number;
  location: {
    lat: number;
    lon: number;
  };
  boundary?: GeoJSON.Polygon;
  crop_type: string;
  planting_date?: string;
  harvest_date?: string;
  status: 'active' | 'inactive' | 'fallow';
  created_at: string;
  updated_at: string;
}
```

### Crop Profitability

```typescript
interface CropProfitability {
  crop_season_id: string;
  field_id: string;
  crop_code: string;
  crop_name_en: string;
  crop_name_ar: string;
  area_ha: number;
  total_costs: number;
  total_revenue: number;
  net_profit: number;
  profit_margin_pct: number;
  roi_pct: number;
  cost_per_ha: number;
  revenue_per_ha: number;
  cost_breakdown: {
    seeds: number;
    fertilizer: number;
    pesticides: number;
    irrigation: number;
    labor: number;
    machinery: number;
    other: number;
  };
}
```

## Error Codes | رموز الخطأ

| Code | Message | Description |
|------|---------|-------------|
| `field_not_found` | Field not found | The specified field does not exist |
| `invalid_area` | Invalid area | Area must be greater than 0 |
| `invalid_crop_code` | Invalid crop code | The crop code is not recognized |
| `no_benchmark_data` | No benchmark data available | Regional data not available for this crop |

---

*Last updated: 2026-01-02*
