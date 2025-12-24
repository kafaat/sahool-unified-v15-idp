# @sahool/api-client

عميل API موحد لمنصة سهول الزراعية

## التثبيت | Installation

```bash
npm install @sahool/api-client
# or
pnpm add @sahool/api-client
```

## الاستخدام | Usage

### التهيئة الأساسية | Basic Setup

```typescript
import { createApiClient } from '@sahool/api-client';

const client = createApiClient({
  baseUrl: 'http://localhost:8000',
  tenantId: 'your-tenant-id',
  token: 'your-auth-token', // optional
});
```

### الحقول | Fields

```typescript
// جلب جميع الحقول
const fields = await client.getFields();

// جلب حقل محدد
const field = await client.getField('field_001');

// إنشاء حقل جديد
const newField = await client.createField({
  name: 'حقل الطماطم',
  cropType: 'tomato',
  areaHectares: 5.2,
  boundary: { type: 'Polygon', coordinates: [...] }
});
```

### المهام | Tasks

```typescript
// جلب المهام
const tasks = await client.getTasks({ fieldId: 'field_001' });

// إنشاء مهمة
const task = await client.createTask({
  title: 'ري الحقل',
  fieldId: 'field_001',
  priority: 'high',
  dueDate: new Date().toISOString(),
});

// تحديث حالة المهمة
await client.updateTaskStatus('task_001', 'completed');
```

### تحليل NDVI

```typescript
// جلب ملخص NDVI
const summary = await client.getNDVISummary('tenant_001');

// جلب تحليل حقل محدد
const analysis = await client.getFieldNDVI('field_001');
```

### الطقس | Weather

```typescript
// الطقس الحالي
const current = await client.getCurrentWeather(15.37, 44.19);

// التنبؤات
const forecast = await client.getWeatherForecast(15.37, 44.19, 7);
```

### التنبيهات | Alerts

```typescript
// جلب التنبيهات
const alerts = await client.getAlerts({ status: 'active' });

// تأكيد تنبيه
await client.acknowledgeAlert('alert_001');
```

## الأنواع | Types

```typescript
import type {
  Field,
  Task,
  Alert,
  NDVIAnalysis,
  WeatherData,
  ApiResponse,
} from '@sahool/api-client/types';
```

## التكوين | Configuration

| الخيار | النوع | الوصف |
|--------|------|-------|
| `baseUrl` | `string` | عنوان API الأساسي |
| `tenantId` | `string` | معرف المستأجر |
| `token` | `string?` | رمز المصادقة |
| `timeout` | `number?` | مهلة الطلب (ms) |
| `retries` | `number?` | عدد المحاولات |

## معالجة الأخطاء | Error Handling

```typescript
import { ApiError } from '@sahool/api-client';

try {
  const field = await client.getField('invalid_id');
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error: ${error.status} - ${error.message}`);
  }
}
```

## خريطة المنافذ | Port Map

| الخدمة | المنفذ | الوصف |
|--------|--------|-------|
| Kong Gateway | 8000 | البوابة الرئيسية |
| WebSocket | 8081 | الأحداث المباشرة |
| satellite-service | 8090 | تحليل الأقمار الصناعية |
| indicators-service | 8091 | المؤشرات الزراعية |
| weather-advanced | 8092 | الطقس المتقدم |
| fertilizer-advisor | 8093 | مستشار التسميد |
| irrigation-smart | 8094 | الري الذكي |
| crop-health-ai | 8095 | صحة المحاصيل |
| virtual-sensors | 8096 | المستشعرات الافتراضية |
| yield-engine | 8098 | محرك الإنتاجية |
| notification-service | 8110 | الإشعارات |

## الترخيص | License

MIT © SAHOOL Team
