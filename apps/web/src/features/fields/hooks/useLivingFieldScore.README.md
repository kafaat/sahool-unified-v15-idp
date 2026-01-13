# Living Field Score Hook

**خطاف حساب درجة الحقل الحي**

A comprehensive React hook that calculates a "Living Field Score" by combining data from multiple agricultural monitoring sources to provide actionable insights about field health and management.

## Overview

The `useLivingFieldScore` hook integrates data from:

- **NDVI** (Normalized Difference Vegetation Index) - Satellite imagery for crop health
- **Soil Moisture Sensors** - IoT sensors monitoring irrigation needs
- **Weather Data** - Current and forecasted weather conditions
- **Task Management** - Pending and completed farm activities
- **Astronomical Calendar** - Traditional Yemeni farming almanac

## Features

✅ **Multi-source Data Integration**: Combines NDVI, sensors, weather, tasks, and astronomical data
✅ **Comprehensive Scoring**: 5 scores (overall, health, hydration, attention, astral)
✅ **Intelligent Alerts**: Context-aware alerts with Arabic translations
✅ **Smart Recommendations**: Actionable farming recommendations based on conditions
✅ **Trend Analysis**: Tracks if field conditions are improving, stable, or declining
✅ **Performance Optimized**: Memoized calculations for efficient re-renders
✅ **Bilingual Support**: Full English and Arabic support

## Installation

The hook is part of the fields feature and can be imported directly:

```typescript
import { useLivingFieldScore } from "@/features/fields";
```

## Basic Usage

```typescript
import { useLivingFieldScore } from '@/features/fields';

function FieldDashboard({ fieldId }: { fieldId: string }) {
  const { data, isLoading, isError } = useLivingFieldScore(fieldId);

  if (isLoading) return <div>Loading...</div>;
  if (isError || !data) return <div>Error</div>;

  return (
    <div>
      <h2>Field Health Score: {data.overall}/100</h2>
      <p>Trend: {data.trend}</p>
      <p>Alerts: {data.alerts.length}</p>
      <p>Recommendations: {data.recommendations.length}</p>
    </div>
  );
}
```

## API Reference

### Hook Signature

```typescript
function useLivingFieldScore(
  fieldId: string,
  options?: UseLivingFieldScoreOptions,
): {
  data: LivingFieldScore | undefined;
  isLoading: boolean;
  isError: boolean;
};
```

### Parameters

#### `fieldId` (required)

- **Type**: `string`
- **Description**: The unique identifier of the field to analyze

#### `options` (optional)

- **Type**: `UseLivingFieldScoreOptions`
- **Properties**:
  - `enabled?: boolean` - Enable/disable the hook (default: `true`)
  - `includeAlerts?: boolean` - Generate alerts (default: `true`)
  - `includeRecommendations?: boolean` - Generate recommendations (default: `true`)

### Return Value

```typescript
interface LivingFieldScore {
  overall: number; // 0-100: Weighted average of all scores
  health: number; // 0-100: Crop health from NDVI
  hydration: number; // 0-100: Soil moisture and irrigation
  attention: number; // 0-100: Task completion and urgency
  astral: number; // 0-100: Astronomical favorability
  trend: "improving" | "stable" | "declining";
  alerts: FieldAlert[]; // Active alerts requiring attention
  recommendations: Recommendation[]; // Actionable recommendations
  lastUpdated: Date; // Timestamp of calculation
}
```

## Score Components

### 1. Overall Score (0-100)

**Weighted average of all component scores:**

- Health: 35%
- Hydration: 35%
- Attention: 20%
- Astral: 10%

**Interpretation:**

- 70-100: Excellent ✅ (Green)
- 40-69: Moderate ⚠️ (Yellow)
- 0-39: Poor ❌ (Red)

### 2. Health Score

**Based on NDVI satellite data**

Measures crop vegetation health:

- **Excellent (95)**: NDVI ≥ 0.7
- **Good (80)**: NDVI ≥ 0.5
- **Moderate (60)**: NDVI ≥ 0.3
- **Poor (35)**: NDVI ≥ 0.15
- **Critical (15)**: NDVI < 0.15

### 3. Hydration Score

**Based on soil moisture sensors and weather**

Optimal soil moisture: 30-60%

- **90**: Within optimal range
- **60**: Slightly low (20-30%)
- **30**: Over-irrigated (>80%)
- **20**: Critical low (<20%)

Adjusted for weather conditions:

- Temperature > 35°C + Humidity < 30% → -15 points
- Humidity 50-70% → +5 points

### 4. Attention Score

**Based on task completion and urgency**

Starts at 100, deductions for:

- **5+ overdue tasks**: -50 points
- **2-4 overdue tasks**: -25 points
- **1 overdue task**: -10 points
- **10+ pending tasks**: -20 points
- **6-9 pending tasks**: -10 points

Bonus:

- **Completion rate > 80%**: +10 points

### 5. Astral Score

**Based on Yemeni agricultural astronomical calendar**

Uses:

- Moon phases (farming_good indicator)
- Lunar mansions (farming_score 0-10)
- Overall farming score from calendar

Favorable conditions increase score up to 100.

## Alerts

### Alert Structure

```typescript
interface FieldAlert {
  id: string;
  severity: "info" | "warning" | "critical" | "emergency";
  category:
    | "crop_health"
    | "weather"
    | "irrigation"
    | "pest"
    | "disease"
    | "market"
    | "system";
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  timestamp: string;
  threshold?: number;
  currentValue?: number;
}
```

### Alert Triggers

#### Health Alerts

- **Critical**: Health < 30
- **Warning**: Health < 50

#### Hydration Alerts

- **Critical Low**: Soil moisture < 20%
- **Warning High**: Soil moisture > 80%

#### Task Alerts

- **Critical**: 5+ overdue tasks
- **Warning**: 2-4 overdue tasks

### Example Alerts

```typescript
// Critical crop health
{
  severity: 'critical',
  category: 'crop_health',
  title: 'Critical Crop Health',
  titleAr: 'صحة المحصول حرجة',
  message: 'Crop health is critically low. Immediate action required.',
  messageAr: 'صحة المحصول منخفضة بشكل حرج. مطلوب إجراء فوري.'
}

// Low soil moisture
{
  severity: 'critical',
  category: 'irrigation',
  title: 'Critical Low Soil Moisture',
  titleAr: 'رطوبة التربة منخفضة للغاية',
  message: 'Soil moisture is critically low at 15.3%. Immediate irrigation required.',
  messageAr: 'رطوبة التربة منخفضة جداً عند 15.3٪. مطلوب ري فوري.'
}
```

## Recommendations

### Recommendation Structure

```typescript
interface Recommendation {
  id: string;
  type:
    | "irrigation"
    | "fertilizer"
    | "pest_control"
    | "harvest"
    | "planting"
    | "general";
  priority: "low" | "medium" | "high" | "urgent";
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  actionItems: string[];
  expectedBenefit?: string;
  expectedBenefitAr?: string;
}
```

### Recommendation Triggers

#### Health Recommendations

- **Priority: Urgent** (health < 30)
  - Conduct soil nutrient analysis
  - Check for pest or disease signs
  - Review irrigation schedule
  - Consider targeted fertilization

#### Irrigation Recommendations

- **Increase Irrigation** (hydration < 40)
  - Schedule immediate irrigation
  - Check irrigation system functionality
  - Monitor soil moisture sensors
  - Adjust irrigation frequency

- **Reduce Irrigation** (hydration > 80)
  - Pause irrigation temporarily
  - Improve field drainage
  - Monitor for signs of waterlogging

#### Task Recommendations

- **Complete Pending Tasks** (attention < 60)
  - Review overdue tasks
  - Prioritize urgent activities
  - Assign tasks to team members

#### Weather-based Recommendations

- **Heat Stress Mitigation** (temp > 35°C, humidity < 30%)
  - Increase irrigation frequency
  - Consider shade netting
  - Monitor crops for stress signs
  - Apply mulch to retain moisture

## Thresholds Configuration

```typescript
const THRESHOLDS = {
  NDVI: {
    EXCELLENT: 0.7,
    GOOD: 0.5,
    MODERATE: 0.3,
    POOR: 0.15,
  },
  SOIL_MOISTURE: {
    OPTIMAL_MIN: 30,
    OPTIMAL_MAX: 60,
    CRITICAL_LOW: 20,
    CRITICAL_HIGH: 80,
  },
  TASKS: {
    OVERDUE_CRITICAL: 5,
    OVERDUE_WARNING: 2,
    PENDING_WARNING: 10,
  },
  ASTRAL: {
    EXCELLENT: 80,
    GOOD: 60,
    MODERATE: 40,
  },
};
```

## Advanced Usage

### Disabling Alerts/Recommendations

For performance optimization, you can disable alerts or recommendations:

```typescript
const { data } = useLivingFieldScore(fieldId, {
  includeAlerts: false,
  includeRecommendations: false,
});
```

### Conditional Enabling

```typescript
const [enabled, setEnabled] = useState(false);

const { data } = useLivingFieldScore(fieldId, {
  enabled,
});

// Enable when needed
setEnabled(true);
```

## Performance Considerations

1. **Memoization**: All calculations are memoized using `useMemo`
2. **Stale Time**: Data is cached for appropriate durations:
   - NDVI: 15 minutes
   - Weather: 5 minutes
   - Sensors: 30 seconds
   - Tasks: 2 minutes
   - Astronomical: 30 minutes

3. **Lazy Loading**: Only fetch what you need using options

## Data Dependencies

The hook internally uses these data sources:

```typescript
// NDVI data
useFieldNDVI(fieldId);

// Weather data
useCurrentWeather();

// Astronomical calendar
useAstronomicalToday();

// Tasks
useTasksByField(fieldId);

// Soil moisture sensors
useSensors({ fieldId, type: "soil_moisture" });
```

## Error Handling

The hook gracefully handles missing data:

- Missing NDVI: Returns neutral score (50)
- No sensors: Uses weather data only
- No tasks: Assumes perfect attention (100)
- Missing weather: Uses sensor data only

## Components

### Pre-built Component

Use the `LivingFieldCard` component for a complete UI:

```typescript
import { LivingFieldCard } from '@/features/fields';

<LivingFieldCard
  fieldId="field-123"
  fieldName="North Field"
  fieldNameAr="الحقل الشمالي"
/>
```

## Internationalization

All alerts and recommendations include both English and Arabic text:

- `title` / `titleAr`
- `message` / `messageAr`
- `description` / `descriptionAr`

## Examples

See `useLivingFieldScore.example.ts` for complete working examples including:

1. Basic usage
2. With options
3. Display alerts
4. Display recommendations
5. Trend indicator
6. Score color coding
7. Conditional rendering
8. Last updated timestamp

## License

Part of the SAHOOL agricultural platform.
