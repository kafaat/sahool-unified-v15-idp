# Field Intelligence React Query Hooks

> خطافات React Query لذكاء الحقول

Comprehensive React Query hooks for field intelligence features using TanStack Query v5.

## Overview

This module provides a complete set of hooks for managing field intelligence data including zones, alerts, best days recommendations, date validation, AI recommendations, and task creation from alerts.

## Features

- **Proper Cache Management**: Intelligent query keys for optimal caching
- **Automatic Refetching**: Configurable stale times and refetch intervals
- **Error Handling**: Comprehensive error handling with fallbacks
- **Loading States**: Clear loading state management
- **Optimistic Updates**: Fast UI updates with rollback on error
- **Type Safety**: Full TypeScript support
- **Bilingual**: Arabic and English support throughout

## Installation

The hooks are already available in the fields feature module:

```typescript
import {
  useFieldZones,
  useFieldAlerts,
  useBestDays,
  useValidateDate,
  useFieldRecommendations,
  useCreateTaskFromAlert,
  useFieldIntelligence,
  useDebouncedDateValidation,
} from "@/features/fields";
```

## Available Hooks

### 1. `useFieldZones(fieldId, options?)`

Fetch and cache field zones with health data.

**Parameters:**

- `fieldId: string` - Field identifier
- `options?: HookOptions` - Optional hook configuration

**Returns:** Query result with field zones data

**Cache Configuration:**

- Stale Time: 5 minutes (zones don't change frequently)
- Retry: 2 attempts with 1 second delay

**Example:**

```typescript
function FieldZonesView({ fieldId }: { fieldId: string }) {
  const { data: zones, isLoading, isError, error } = useFieldZones(fieldId);

  if (isLoading) return <div>Loading zones...</div>;
  if (isError) return <div>Error: {error.message}</div>;

  return (
    <div>
      {zones?.map((zone) => (
        <div key={zone.id}>
          <h3>{zone.name}</h3>
          <p>NDVI: {zone.ndviValue.toFixed(2)}</p>
          <p>Health: {zone.status}</p>
          <p>Area: {zone.area} hectares</p>
        </div>
      ))}
    </div>
  );
}
```

### 2. `useFieldAlerts(fieldId, options?)`

Fetch field alerts with automatic real-time updates.

**Parameters:**

- `fieldId: string` - Field identifier
- `options?: HookOptions` - Optional hook configuration

**Returns:** Query result with active field alerts

**Cache Configuration:**

- Stale Time: 30 seconds (alerts change frequently)
- Refetch Interval: 60 seconds (auto-refresh)
- Retry: 2 attempts with 500ms delay

**Example:**

```typescript
function FieldAlertsPanel({ fieldId }: { fieldId: string }) {
  const { data: alerts, refetch } = useFieldAlerts(fieldId);

  return (
    <div>
      <button onClick={() => refetch()}>Refresh</button>
      {alerts?.map((alert) => (
        <div key={alert.id} className={`alert-${alert.severity}`}>
          <h4>{alert.titleAr}</h4>
          <p>{alert.messageAr}</p>
        </div>
      ))}
    </div>
  );
}
```

### 3. `useBestDays(activity, options?)`

Find best days for farming activities based on weather and astronomical conditions.

**Parameters:**

- `activity: string` - Activity type (e.g., 'planting', 'harvesting', 'irrigation')
- `options?: BestDaysOptions` - Query options including days count

**Returns:** Query result with best days ranked by suitability

**Cache Configuration:**

- Stale Time: 24 hours (best days are stable)
- Retry: 2 attempts with 1 second delay

**Example:**

```typescript
function BestDaysFinder() {
  const [activity, setActivity] = useState('planting');
  const { data: bestDays } = useBestDays(activity, { days: 14 });

  return (
    <div>
      <select value={activity} onChange={(e) => setActivity(e.target.value)}>
        <option value="planting">Planting</option>
        <option value="harvesting">Harvesting</option>
        <option value="irrigation">Irrigation</option>
      </select>

      {bestDays?.map((day) => (
        <div key={day.date}>
          <p>{day.date}</p>
          <p>Score: {day.score}/100</p>
          <p>{day.suitabilityAr}</p>
        </div>
      ))}
    </div>
  );
}
```

### 4. `useValidateDate(date, activity, options?)`

Validate if a date is suitable for a farming activity.

**Parameters:**

- `date: string` - Date to validate (ISO format)
- `activity: string` - Farming activity type
- `options?: HookOptions` - Optional hook configuration

**Returns:** Query result with validation data including score and alternatives

**Cache Configuration:**

- Stale Time: 1 hour (validation is stable per date)
- Retry: 1 attempt with 500ms delay

**Example:**

```typescript
function DateValidationForm() {
  const [date, setDate] = useState('2026-01-15');
  const [activity] = useState('planting');

  const { data: validation, isLoading } = useValidateDate(date, activity);

  return (
    <div>
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />

      {validation && (
        <div className={validation.suitable ? 'success' : 'warning'}>
          <p>Score: {validation.score}/100</p>
          <p>Rating: {validation.ratingAr}</p>
          {validation.reasonsAr?.map((reason, i) => (
            <p key={i}>{reason}</p>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 5. `useFieldRecommendations(fieldId, options?)`

Fetch AI-powered recommendations for a field.

**Parameters:**

- `fieldId: string` - Field identifier
- `options?: HookOptions` - Optional hook configuration

**Returns:** Query result with prioritized recommendations

**Cache Configuration:**

- Stale Time: 2 minutes (recommendations should be fresh)
- Retry: 2 attempts with 1 second delay

**Example:**

```typescript
function RecommendationsPanel({ fieldId }: { fieldId: string }) {
  const { data: recommendations } = useFieldRecommendations(fieldId);

  return (
    <div>
      {recommendations?.map((rec) => (
        <div key={rec.id} className={`priority-${rec.priority}`}>
          <h3>{rec.titleAr}</h3>
          <p>{rec.descriptionAr}</p>
          <ul>
            {rec.actionItems.map((item, i) => (
              <li key={i}>{item.actionAr}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
```

### 6. `useCreateTaskFromAlert()`

Create a task from an alert with optimistic updates.

**Returns:** Mutation result with task creation handler

**Features:**

- Optimistic updates for instant UI feedback
- Automatic rollback on error
- Query invalidation for affected data

**Example:**

```typescript
function AlertActionButton({ alert }: { alert: FieldAlert }) {
  const createTask = useCreateTaskFromAlert();

  const handleCreateTask = () => {
    createTask.mutate({
      alertId: alert.id,
      taskData: {
        title: `Task for: ${alert.title}`,
        titleAr: `مهمة لـ: ${alert.titleAr}`,
        priority: alert.severity === 'critical' ? 'urgent' : 'high',
      },
    }, {
      onSuccess: (task) => {
        alert(`Task ${task.id} created successfully!`);
      },
      onError: (error) => {
        alert('Failed to create task');
      },
    });
  };

  return (
    <button
      onClick={handleCreateTask}
      disabled={createTask.isPending}
    >
      {createTask.isPending ? 'Creating...' : 'Create Task'}
    </button>
  );
}
```

### 7. `useFieldIntelligence(fieldId, options?)` (Composite Hook)

Get all field intelligence data in a single hook.

**Parameters:**

- `fieldId: string` - Field identifier
- `options?: HookOptions` - Optional hook configuration

**Returns:** Combined intelligence data (zones, alerts, recommendations, createTask)

**Example:**

```typescript
function FieldIntelligenceDashboard({ fieldId }: { fieldId: string }) {
  const intelligence = useFieldIntelligence(fieldId);

  if (intelligence.isLoading) {
    return <div>Loading intelligence data...</div>;
  }

  return (
    <div>
      {/* Zones */}
      <section>
        <h2>Zones ({intelligence.zones.data?.length || 0})</h2>
        {intelligence.zones.data?.map((zone) => (
          <div key={zone.id}>{zone.name}</div>
        ))}
      </section>

      {/* Alerts */}
      <section>
        <h2>Alerts ({intelligence.alerts.data?.length || 0})</h2>
        {intelligence.alerts.data?.map((alert) => (
          <div key={alert.id}>
            <p>{alert.titleAr}</p>
            <button
              onClick={() => intelligence.createTask.mutate({
                alertId: alert.id,
                taskData: {
                  title: alert.title,
                  titleAr: alert.titleAr,
                  priority: 'high',
                },
              })}
            >
              Create Task
            </button>
          </div>
        ))}
      </section>

      {/* Recommendations */}
      <section>
        <h2>Recommendations ({intelligence.recommendations.data?.length || 0})</h2>
        {intelligence.recommendations.data?.map((rec) => (
          <div key={rec.id}>{rec.titleAr}</div>
        ))}
      </section>
    </div>
  );
}
```

### 8. `useDebouncedDateValidation(date, activity, options?)`

Validate date with built-in debouncing for forms.

**Parameters:**

- `date: string` - Date to validate
- `activity: string` - Farming activity
- `options?: HookOptions` - Optional hook configuration

**Returns:** Validation result with convenience properties

**Example:**

```typescript
function DateInputWithValidation() {
  const [date, setDate] = useState('');
  const validation = useDebouncedDateValidation(date, 'planting');

  return (
    <div>
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />

      {validation.isValidating && <p>Validating...</p>}

      {validation.data && (
        <div>
          <p>Score: {validation.score}/100</p>
          <p>Rating: {validation.rating}</p>
        </div>
      )}
    </div>
  );
}
```

## Query Keys

All hooks use centralized query keys from `fieldIntelligenceKeys`:

```typescript
import { fieldIntelligenceKeys } from "@/features/fields";

// Manual cache invalidation
queryClient.invalidateQueries({
  queryKey: fieldIntelligenceKeys.zones(fieldId),
});

// Manual cache updates
queryClient.setQueryData(fieldIntelligenceKeys.alerts(fieldId), newAlerts);
```

## Type Definitions

### BestDaysOptions

```typescript
interface BestDaysOptions {
  days?: number; // Number of days to search (1-30)
  enabled?: boolean; // Enable/disable query
}
```

### HookOptions

```typescript
interface HookOptions {
  enabled?: boolean; // Enable/disable query
}
```

### TaskFromAlertData

```typescript
interface TaskFromAlertData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  priority: "urgent" | "high" | "medium" | "low";
  dueDate?: string;
  assigneeId?: string;
}
```

## Best Practices

### 1. Use Composite Hook for Dashboards

When building field dashboards that need multiple intelligence features, use `useFieldIntelligence` instead of individual hooks:

```typescript
// ✅ Good: Single hook for all data
const intelligence = useFieldIntelligence(fieldId);

// ❌ Avoid: Multiple individual hooks
const zones = useFieldZones(fieldId);
const alerts = useFieldAlerts(fieldId);
const recommendations = useFieldRecommendations(fieldId);
```

### 2. Handle Loading and Error States

Always handle loading and error states for better UX:

```typescript
const { data, isLoading, isError, error } = useFieldZones(fieldId);

if (isLoading) return <Spinner />;
if (isError) return <ErrorMessage error={error} />;
if (!data || data.length === 0) return <EmptyState />;

return <ZonesList zones={data} />;
```

### 3. Use Enabled Flag for Conditional Queries

Disable queries when data is not needed:

```typescript
const { data } = useFieldZones(fieldId, {
  enabled: !!fieldId && isVisible,
});
```

### 4. Leverage Automatic Refetching

Alerts automatically refetch every minute. Use this for real-time displays:

```typescript
const { data: alerts } = useFieldAlerts(fieldId);
// Automatically stays up-to-date!
```

### 5. Use Debounced Validation in Forms

For form inputs, use the debounced validation hook:

```typescript
const validation = useDebouncedDateValidation(formDate, activity);
// Avoids excessive API calls while typing
```

## Error Handling

All hooks include comprehensive error handling:

```typescript
try {
  const { data } = useFieldZones(fieldId);
  // Use data
} catch (error) {
  // Error is automatically logged
  // Fallback data is returned
}
```

## Performance Considerations

### Cache Times

| Hook                      | Stale Time | Refetch Interval | Rationale                         |
| ------------------------- | ---------- | ---------------- | --------------------------------- |
| `useFieldZones`           | 5 minutes  | None             | Zones change infrequently         |
| `useFieldAlerts`          | 30 seconds | 60 seconds       | Real-time monitoring needed       |
| `useBestDays`             | 24 hours   | None             | Astronomical data is stable       |
| `useValidateDate`         | 1 hour     | None             | Validation results are stable     |
| `useFieldRecommendations` | 2 minutes  | None             | AI recommendations need freshness |

### Optimization Tips

1. **Use Query Keys for Prefetching:**

   ```typescript
   queryClient.prefetchQuery({
     queryKey: fieldIntelligenceKeys.zones(fieldId),
     queryFn: () => fetchFieldZones(fieldId),
   });
   ```

2. **Selective Refetching:**

   ```typescript
   const { data, refetch } = useFieldAlerts(fieldId);
   // Only refetch when user explicitly requests
   ```

3. **Disable Auto-Refetch When Not Visible:**
   ```typescript
   const { data } = useFieldAlerts(fieldId, {
     enabled: isTabActive,
   });
   ```

## Testing

Example test using React Testing Library:

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useFieldZones } from './useFieldIntelligence';

test('useFieldZones fetches and returns zones', async () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  const { result } = renderHook(() => useFieldZones('field-123'), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));

  expect(result.current.data).toHaveLength(3);
  expect(result.current.data[0]).toHaveProperty('name');
  expect(result.current.data[0]).toHaveProperty('ndviValue');
});
```

## Related Documentation

- [TanStack Query v5 Documentation](https://tanstack.com/query/latest/docs/framework/react/overview)
- [Field Intelligence API Documentation](../api/field-intelligence-api.ts)
- [Usage Examples](./useFieldIntelligence.example.tsx)

## Support

For issues or questions:

1. Check the [example file](./useFieldIntelligence.example.tsx) for usage patterns
2. Review the [API documentation](../api/field-intelligence-api.ts)
3. Contact the development team

## License

Part of the SAHOOL Unified Platform - © 2024-2026
