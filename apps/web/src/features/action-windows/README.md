# Action Windows Feature
# ميزة نوافذ العمل

A comprehensive weather-based action windows system for optimal agricultural timing decisions.

## Overview

The Action Windows feature provides farmers with intelligent recommendations for spray applications, irrigation scheduling, and other agricultural activities based on real-time weather conditions and forecasts.

## Features

### 1. Spray Windows (نوافذ الرش)
- **7-day forecast** of optimal spray timing
- **Real-time weather monitoring** (wind speed, temperature, humidity, rain probability)
- **Color-coded status** indicators (Optimal, Marginal, Avoid)
- **Intelligent scoring system** (0-100) based on multiple weather parameters
- **One-click task creation** for optimal windows
- **Visual timeline** with color-coded blocks
- **Customizable criteria** for wind speed, temperature, humidity, rain probability

### 2. Irrigation Windows (نوافذ الري)
- **Smart irrigation scheduling** based on soil moisture and weather
- **ET (Evapotranspiration) calculations** (ET₀, ETc, Kc)
- **Soil moisture monitoring** (current, target, deficit)
- **Priority-based recommendations** (Urgent, High, Medium, Low)
- **Water amount calculations** in mm
- **Duration estimates** in hours
- **Morning and evening time preferences**
- **One-click task creation** for urgent/high priority windows

### 3. Action Recommendations (توصيات العمل)
- **AI-driven recommendations** for various agricultural activities
- **Priority-based sorting** (Urgent → High → Medium → Low)
- **Comprehensive reasoning** for each recommendation
- **Benefits and warnings** for each action
- **Confidence scores** (0-100)
- **One-click task creation**

### 4. Visual Timeline (الجدول الزمني)
- **Interactive timeline visualization** of all windows
- **Color-coded blocks** for easy identification
- **Click-to-select** for detailed information
- **Summary statistics** (total, optimal, marginal, avoid)
- **Responsive design** for all screen sizes

## File Structure

```
/apps/web/src/features/action-windows/
├── types/
│   └── action-windows.ts          # TypeScript type definitions
├── api/
│   └── action-windows-api.ts      # API client for backend communication
├── hooks/
│   └── useActionWindows.ts        # React Query hooks
├── components/
│   ├── SprayWindowsPanel.tsx      # Spray windows UI
│   ├── IrrigationWindowsPanel.tsx # Irrigation windows UI
│   ├── WindowTimeline.tsx         # Timeline visualization
│   ├── WeatherConditions.tsx      # Weather display component
│   ├── ActionRecommendation.tsx   # Recommendation cards
│   ├── ActionWindowsDemo.tsx      # Demo/example component
│   └── index.ts                   # Component exports
├── utils/
│   └── window-calculator.ts       # Calculation logic
├── index.ts                       # Feature exports
└── README.md                      # This file
```

## Installation & Usage

### Basic Usage

```tsx
import { SprayWindowsPanel, IrrigationWindowsPanel } from '@/features/action-windows';

function MyFieldPage({ fieldId }: { fieldId: string }) {
  return (
    <div>
      {/* Spray Windows */}
      <SprayWindowsPanel
        fieldId={fieldId}
        days={7}
        onCreateTask={(window) => {
          console.log('Create spray task:', window);
        }}
        showTimeline={true}
      />

      {/* Irrigation Windows */}
      <IrrigationWindowsPanel
        fieldId={fieldId}
        days={7}
        onCreateTask={(window) => {
          console.log('Create irrigation task:', window);
        }}
        showTimeline={true}
      />
    </div>
  );
}
```

### Using Hooks

```tsx
import {
  useSprayWindows,
  useIrrigationWindows,
  useActionRecommendations
} from '@/features/action-windows';

function MyComponent({ fieldId }: { fieldId: string }) {
  const { data: sprayWindows, isLoading } = useSprayWindows({
    fieldId,
    days: 7,
    criteria: {
      windSpeedMax: 12,  // Custom criteria
      temperatureMax: 28
    }
  });

  const { data: irrigationWindows } = useIrrigationWindows({
    fieldId,
    days: 7
  });

  const { data: recommendations } = useActionRecommendations({
    fieldId,
    actionTypes: ['spray', 'irrigate'],
    days: 7
  });

  // ... use the data
}
```

### One-Click Task Creation

```tsx
import { SprayWindowsPanel } from '@/features/action-windows';
import { useCreateTask } from '@/features/tasks/hooks/useTasks';
import type { TaskFormData } from '@/features/tasks/types';

function SprayWindowsWithTasks({ fieldId }: { fieldId: string }) {
  const createTask = useCreateTask();

  const handleCreateTask = async (window: SprayWindow) => {
    const taskData: TaskFormData = {
      title: `Spray Application`,
      title_ar: `رش المبيدات`,
      description: `Optimal spray conditions: Wind ${window.conditions.windSpeed} km/h, Temp ${window.conditions.temperature}°C`,
      description_ar: `ظروف رش مثالية: رياح ${window.conditions.windSpeed} كم/س، حرارة ${window.conditions.temperature}°م`,
      due_date: window.startTime,
      priority: window.score >= 90 ? 'high' : 'medium',
      field_id: fieldId,
      status: 'open',
    };

    await createTask.mutateAsync(taskData);
  };

  return (
    <SprayWindowsPanel
      fieldId={fieldId}
      onCreateTask={handleCreateTask}
    />
  );
}
```

### Complete Demo Example

```tsx
import { ActionWindowsDemo } from '@/features/action-windows/components/ActionWindowsDemo';

function FieldDetailsPage({ fieldId, fieldName }: { fieldId: string; fieldName: string }) {
  return (
    <ActionWindowsDemo
      fieldId={fieldId}
      fieldName={fieldName}
      fieldNameAr="حقل القمح"
      days={7}
    />
  );
}
```

## API Reference

### Types

#### `SprayWindow`
```typescript
interface SprayWindow {
  id: string;
  fieldId: string;
  startTime: string;
  endTime: string;
  duration: number; // hours
  status: 'optimal' | 'marginal' | 'avoid';
  score: number; // 0-100
  conditions: WeatherCondition;
  suitability: {
    windSpeed: boolean;
    temperature: boolean;
    humidity: boolean;
    rain: boolean;
    overall: boolean;
  };
  warnings: string[];
  warningsAr: string[];
  recommendations: string[];
  recommendationsAr: string[];
}
```

#### `IrrigationWindow`
```typescript
interface IrrigationWindow {
  id: string;
  fieldId: string;
  date: string;
  startTime: string;
  endTime: string;
  status: 'optimal' | 'marginal' | 'avoid';
  priority: 'urgent' | 'high' | 'medium' | 'low';
  waterAmount: number; // mm
  duration: number; // hours
  soilMoisture: {
    current: number; // %
    target: number; // %
    deficit: number; // mm
    status: 'critical' | 'low' | 'optimal' | 'high';
    statusAr: string;
  };
  et: {
    et0: number; // mm/day
    etc: number; // mm/day
    kc: number; // Crop coefficient
  };
  weather: WeatherCondition;
  recommendations: string[];
  recommendationsAr: string[];
  reason: string;
  reasonAr: string;
}
```

### Hooks

#### `useSprayWindows(options)`
Fetch spray windows for a field.

**Options:**
- `fieldId: string` - Required field ID
- `days?: number` - Number of days to forecast (default: 7)
- `criteria?: Partial<SprayWindowCriteria>` - Custom spray criteria
- `enabled?: boolean` - Enable/disable query (default: true)

**Returns:** React Query result with `SprayWindow[]`

#### `useIrrigationWindows(options)`
Fetch irrigation windows for a field.

**Options:**
- `fieldId: string` - Required field ID
- `days?: number` - Number of days to forecast (default: 7)
- `enabled?: boolean` - Enable/disable query (default: true)

**Returns:** React Query result with `IrrigationWindow[]`

#### `useActionRecommendations(options)`
Fetch action recommendations for a field.

**Options:**
- `fieldId: string` - Required field ID
- `actionTypes?: ActionType[]` - Filter by action types
- `days?: number` - Number of days to forecast (default: 7)
- `enabled?: boolean` - Enable/disable query (default: true)

**Returns:** React Query result with `ActionRecommendation[]`

### Utility Functions

#### `calculateSprayWindow(weather, criteria?)`
Calculate if weather conditions are suitable for spraying.

**Parameters:**
- `weather: WeatherCondition` - Current weather conditions
- `criteria?: Partial<SprayWindowCriteria>` - Custom criteria

**Returns:** `WindowCalculationResult` with status, score, warnings, and recommendations

#### `calculateIrrigationNeed(soilMoisture, et, fieldAreaHectares?)`
Calculate irrigation needs based on soil moisture and ET.

**Parameters:**
- `soilMoisture: SoilMoistureData` - Current soil moisture data
- `et: ETData` - Evapotranspiration data
- `fieldAreaHectares?: number` - Field area in hectares

**Returns:** `IrrigationNeed` with urgency, amount, duration, and reasoning

#### `getOptimalWindow(conditions, actionType, criteria?)`
Find the optimal window from a list of weather conditions.

**Parameters:**
- `conditions: WeatherCondition[]` - Array of weather conditions
- `actionType: 'spray' | 'irrigate'` - Type of action
- `criteria?: Partial<SprayWindowCriteria>` - Custom criteria

**Returns:** `WeatherCondition | null` - The optimal condition or null

## Default Spray Criteria

```typescript
{
  windSpeedMax: 15,        // km/h
  windSpeedMin: 3,         // km/h
  temperatureMin: 10,      // °C
  temperatureMax: 30,      // °C
  humidityMin: 50,         // %
  humidityMax: 90,         // %
  rainProbabilityMax: 20,  // %
  minDuration: 2,          // hours
}
```

## Scoring System

### Spray Windows Score (0-100)
- **Wind Speed:** 25 points (3-15 km/h)
- **Temperature:** 25 points (10-30°C)
- **Humidity:** 25 points (50-90%)
- **Rain:** 25 points (<20% probability)

**Status:**
- **Optimal:** ≥75 points
- **Marginal:** 50-74 points
- **Avoid:** <50 points

### Irrigation Priority
Based on soil moisture stress level:
- **Critical:** Stress level < 0.3
- **High:** Stress level < 0.5
- **Medium:** Stress level < 0.7
- **Low:** Current < Target
- **None:** Current ≥ Target

## Bilingual Support

All components, messages, and recommendations are available in:
- **English** (primary)
- **Arabic** (عربي)

Field names with `_ar` suffix contain Arabic translations.

## Backend Integration

The feature attempts to fetch data from the backend API at:
- `/api/v1/action-windows/spray`
- `/api/v1/action-windows/irrigation`
- `/api/v1/action-windows/recommendations`

If the backend is unavailable, it falls back to client-side calculations using weather forecast data.

## Testing

```bash
# Run tests (when available)
npm test action-windows
```

## Contributing

When contributing to this feature:
1. Follow the existing code patterns
2. Add both English and Arabic translations
3. Update TypeScript types
4. Add tests for new functionality
5. Update this README

## License

Part of the SAHOOL platform.

---

**Created:** 2026-01-06
**Last Updated:** 2026-01-06
**Version:** 1.0.0
