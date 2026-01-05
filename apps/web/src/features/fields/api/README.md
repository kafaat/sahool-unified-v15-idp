# Field Intelligence API

**واجهة برمجة التطبيقات لذكاء الحقل**

This module provides comprehensive API client functions for field intelligence features in the SAHOOL platform. It integrates data from multiple sources (NDVI, sensors, weather, astronomical data) to provide actionable insights for field management.

## Features

- **Living Field Score**: Comprehensive field health scoring based on multiple factors
- **Field Zones**: Analysis of field zones with health metrics and recommendations
- **Alert Management**: Active alerts and ability to convert them to tasks
- **Best Days Prediction**: AI-powered recommendations for optimal farming activity timing
- **Date Validation**: Verify if a specific date is suitable for farming activities
- **AI Recommendations**: Get prioritized recommendations for field management

## API Functions

### 1. `fetchLivingFieldScore(fieldId)`

Calculates a comprehensive score for field health based on NDVI, irrigation, tasks, and astronomical data.

**Parameters:**
- `fieldId` (string): The field identifier

**Returns:**
```typescript
{
  success: boolean;
  data?: {
    fieldId: string;
    overall: number;          // 0-100
    health: number;           // 0-100
    hydration: number;        // 0-100
    attention: number;        // 0-100
    astral: number;           // 0-100
    trend: 'improving' | 'stable' | 'declining';
    components: {
      ndvi: { value, category, contribution };
      soilMoisture: { value, status, contribution };
      taskCompletion: { completedTasks, totalTasks, overdueTasks };
      astronomical: { moonPhase, farmingScore };
    };
  };
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { fetchLivingFieldScore } from '@/features/fields';

const response = await fetchLivingFieldScore('field-123');
if (response.success) {
  console.log('Overall Score:', response.data.overall);
  console.log('Trend:', response.data.trend);
}
```

### 2. `fetchFieldZones(fieldId)`

Retrieves field zones with health data, NDVI values, and recommendations.

**Parameters:**
- `fieldId` (string): The field identifier

**Returns:**
```typescript
{
  success: boolean;
  data?: FieldZone[];
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { fetchFieldZones } from '@/features/fields';

const response = await fetchFieldZones('field-123');
if (response.success) {
  response.data?.forEach(zone => {
    console.log(`Zone ${zone.name}: Health ${zone.healthScore}`);
  });
}
```

### 3. `fetchFieldAlerts(fieldId)`

Gets all active alerts for a specific field.

**Parameters:**
- `fieldId` (string): The field identifier

**Returns:**
```typescript
{
  success: boolean;
  data?: FieldAlert[];
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { fetchFieldAlerts } from '@/features/fields';

const response = await fetchFieldAlerts('field-123');
if (response.success) {
  const criticalAlerts = response.data?.filter(a => a.severity === 'critical');
  console.log(`Critical alerts: ${criticalAlerts?.length}`);
}
```

### 4. `createTaskFromAlert(alertId, taskData)`

Converts an alert into an actionable task.

**Parameters:**
- `alertId` (string): The alert identifier
- `taskData` (TaskFromAlertData): Task creation data
  ```typescript
  {
    title: string;
    titleAr: string;
    description?: string;
    descriptionAr?: string;
    priority: 'urgent' | 'high' | 'medium' | 'low';
    dueDate?: string;
    assigneeId?: string;
  }
  ```

**Returns:**
```typescript
{
  success: boolean;
  data?: CreatedTask;
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { createTaskFromAlert } from '@/features/fields';

const response = await createTaskFromAlert('alert-456', {
  title: 'Fix Irrigation System',
  titleAr: 'إصلاح نظام الري',
  priority: 'urgent',
  dueDate: '2026-01-10',
});
```

### 5. `fetchBestDays(activity, days)`

Analyzes weather and astronomical conditions to find optimal days for farming activities.

**Parameters:**
- `activity` (string): Activity type (e.g., 'planting', 'irrigation', 'harvesting')
- `days` (number): Number of days to analyze (1-30, default: 14)

**Returns:**
```typescript
{
  success: boolean;
  data?: BestDay[];
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { fetchBestDays } from '@/features/fields';

const response = await fetchBestDays('planting', 7);
if (response.success) {
  const bestDay = response.data?.[0];
  console.log(`Best day: ${bestDay?.date} (${bestDay?.suitability})`);
}
```

### 6. `validateTaskDate(date, activity)`

Checks if a specific date is suitable for a farming activity.

**Parameters:**
- `date` (string): ISO 8601 date string
- `activity` (string): Activity type

**Returns:**
```typescript
{
  success: boolean;
  data?: {
    suitable: boolean;
    score: number;
    rating: 'excellent' | 'good' | 'moderate' | 'poor' | 'unsuitable';
    reasons: string[];
    reasonsAr: string[];
    alternatives?: Array<{ date, score, reason }>;
    warnings?: string[];
  };
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { validateTaskDate } from '@/features/fields';

const response = await validateTaskDate('2026-01-15', 'irrigation');
if (response.success && response.data) {
  if (response.data.suitable) {
    console.log('Date is suitable:', response.data.rating);
  } else {
    console.log('Better alternatives:', response.data.alternatives);
  }
}
```

### 7. `fetchFieldRecommendations(fieldId)`

Retrieves AI-powered recommendations for field management.

**Parameters:**
- `fieldId` (string): The field identifier

**Returns:**
```typescript
{
  success: boolean;
  data?: FieldRecommendation[];
  error?: string;
  error_ar?: string;
}
```

**Usage Example:**
```typescript
import { fetchFieldRecommendations } from '@/features/fields';

const response = await fetchFieldRecommendations('field-123');
if (response.success) {
  const urgentRecs = response.data?.filter(r => r.priority === 'urgent');
  urgentRecs?.forEach(rec => {
    console.log(`${rec.title}: ${rec.description}`);
  });
}
```

## TanStack Query Integration

All API functions are designed to work seamlessly with TanStack Query. Use the provided query keys for optimal caching and invalidation:

```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchLivingFieldScore, fieldIntelligenceKeys } from '@/features/fields';

function MyComponent({ fieldId }: { fieldId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: fieldIntelligenceKeys.score(fieldId),
    queryFn: () => fetchLivingFieldScore(fieldId),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // ... rest of component
}
```

## Query Keys

The module exports a `fieldIntelligenceKeys` object for TanStack Query:

```typescript
fieldIntelligenceKeys = {
  all: ['field-intelligence'],
  score: (fieldId) => ['field-intelligence', 'score', fieldId],
  zones: (fieldId) => ['field-intelligence', 'zones', fieldId],
  alerts: (fieldId) => ['field-intelligence', 'alerts', fieldId],
  recommendations: (fieldId) => ['field-intelligence', 'recommendations', fieldId],
  bestDays: (activity, days) => ['field-intelligence', 'best-days', activity, days],
  dateValidation: (date, activity) => ['field-intelligence', 'validate-date', date, activity],
}
```

## Error Handling

All API functions return bilingual error messages (English and Arabic) and handle errors gracefully:

```typescript
const response = await fetchLivingFieldScore('field-123');

if (!response.success) {
  // English error
  console.error(response.error);

  // Arabic error
  console.error(response.error_ar);

  // Display to user based on their language preference
  const message = locale === 'ar' ? response.error_ar : response.error;
  toast.error(message);
}
```

## Error Messages

The module exports `INTELLIGENCE_ERROR_MESSAGES` constant with all error messages:

```typescript
import { INTELLIGENCE_ERROR_MESSAGES } from '@/features/fields';

console.log(INTELLIGENCE_ERROR_MESSAGES.SCORE_FETCH_FAILED.en);
// "Failed to fetch living field score"

console.log(INTELLIGENCE_ERROR_MESSAGES.SCORE_FETCH_FAILED.ar);
// "فشل في جلب درجة الحقل الحي"
```

## API Endpoints

The functions call the following API endpoints:

- `GET /api/v1/fields/{fieldId}/intelligence/score` - Living Field Score
- `GET /api/v1/fields/{fieldId}/intelligence/zones` - Field Zones
- `GET /api/v1/fields/{fieldId}/intelligence/alerts` - Field Alerts
- `POST /api/v1/intelligence/alerts/{alertId}/create-task` - Create Task from Alert
- `GET /api/v1/intelligence/best-days` - Best Days for Activity
- `POST /api/v1/intelligence/validate-date` - Validate Task Date
- `GET /api/v1/fields/{fieldId}/intelligence/recommendations` - AI Recommendations

## Type Safety

All functions are fully typed with TypeScript. Import types for full IntelliSense support:

```typescript
import type {
  LivingFieldScore,
  FieldZone,
  FieldAlert,
  BestDay,
  DateValidation,
  FieldRecommendation,
  TaskFromAlertData,
} from '@/features/fields';
```

## Best Practices

1. **Use TanStack Query**: Leverage the query keys for automatic caching and refetching
2. **Handle Errors**: Always check `response.success` before accessing data
3. **Validate Inputs**: Functions validate inputs and return appropriate errors
4. **Stale Time**: Set appropriate `staleTime` based on data volatility
5. **Bilingual Support**: Use `error_ar` for Arabic users, `error` for English

## License

Copyright © 2026 SAHOOL - Smart Agricultural Platform
