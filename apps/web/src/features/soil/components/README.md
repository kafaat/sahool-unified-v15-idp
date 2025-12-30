# Soil Nutrient Analysis Component

A comprehensive React component for displaying soil nutrient analysis data in the SAHOOL agricultural platform. This component provides features similar to those found in Farmonaut and John Deere platforms, with full Arabic/RTL support for the Yemen market.

## Features

- **NPK Levels Display**: Visual representation of Nitrogen (N), Phosphorus (P), and Potassium (K) levels with color-coded status indicators
- **pH Level Indicator**: Interactive gradient scale showing soil acidity/alkalinity
- **Organic Matter Percentage**: Visual display of organic matter content
- **Soil Moisture & Temperature**: Real-time monitoring of soil conditions
- **Nutrient Deficiency Alerts**: Automatic alerts for nutrients below optimal levels
- **Fertilizer Recommendations**: Actionable recommendations with amounts, methods, and cost estimates
- **Historical Trends**: Track nutrient levels over time
- **Bilingual Support**: Full English and Arabic support with RTL layout
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Production-Ready**: Includes error handling, loading states, and TypeScript types

## Installation

The component is already part of the SAHOOL platform. Import it from the soil features:

```typescript
import { SoilNutrientAnalysis } from '@/features/soil/components';
// or
import SoilNutrientAnalysis from '@/features/soil/components/SoilNutrientAnalysis';
```

## Basic Usage

```typescript
import React from 'react';
import { SoilNutrientAnalysis } from '@/features/soil/components';

export default function MyPage() {
  return (
    <div>
      <SoilNutrientAnalysis language="en" />
    </div>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `SoilNutrient` | Mock data | Soil nutrient data object |
| `onRefresh` | `() => void` | `undefined` | Callback function when refresh button is clicked |
| `loading` | `boolean` | `false` | Shows loading state when true |
| `language` | `'en' \| 'ar'` | `'en'` | Display language (enables RTL for Arabic) |

## Data Structure

### SoilNutrient Interface

```typescript
interface SoilNutrient {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  sampleDate: string; // ISO 8601 format
  location: {
    latitude: number;
    longitude: number;
  };
  nutrients: {
    nitrogen: NutrientLevel;
    phosphorus: NutrientLevel;
    potassium: NutrientLevel;
  };
  ph: {
    current: number;
    optimal: { min: number; max: number };
    status: 'acidic' | 'neutral' | 'alkaline';
  };
  organicMatter: {
    percentage: number;
    status: 'low' | 'moderate' | 'high';
  };
  moisture: {
    percentage: number;
    status: 'low' | 'optimal' | 'high';
  };
  temperature: {
    celsius: number;
  };
}
```

### NutrientLevel Interface

```typescript
interface NutrientLevel {
  current: number;
  optimal: { min: number; max: number };
  unit: string;
  status: 'low' | 'optimal' | 'high';
  trend?: 'up' | 'down' | 'stable';
}
```

### FertilizerRecommendation Interface

```typescript
interface FertilizerRecommendation {
  id: string;
  nutrient: string;
  nutrientAr: string;
  product: string;
  productAr: string;
  amount: number;
  unit: string;
  unitAr: string;
  applicationMethod: string;
  applicationMethodAr: string;
  priority: 'high' | 'medium' | 'low';
  estimatedCost?: number;
  currency?: string;
}
```

## Usage Examples

### Example 1: With Custom Data

```typescript
import React, { useState } from 'react';
import { SoilNutrientAnalysis, type SoilNutrient } from '@/features/soil/components';

export default function MyField() {
  const [data] = useState<SoilNutrient>({
    id: 'soil-001',
    fieldId: 'field-123',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    sampleDate: new Date().toISOString(),
    location: { latitude: 15.5527, longitude: 48.5164 },
    nutrients: {
      nitrogen: {
        current: 45,
        optimal: { min: 40, max: 60 },
        unit: 'ppm',
        status: 'optimal',
        trend: 'up',
      },
      // ... other nutrients
    },
    // ... other fields
  });

  return <SoilNutrientAnalysis data={data} language="en" />;
}
```

### Example 2: With API Integration

```typescript
import React, { useEffect, useState } from 'react';
import { SoilNutrientAnalysis, type SoilNutrient } from '@/features/soil/components';

export default function FieldAnalysis({ fieldId }: { fieldId: string }) {
  const [data, setData] = useState<SoilNutrient | undefined>();
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/soil-analysis/${fieldId}`);
      const soilData = await response.json();
      setData(soilData);
    } catch (error) {
      console.error('Error fetching soil data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fieldId]);

  return (
    <SoilNutrientAnalysis
      data={data}
      onRefresh={fetchData}
      loading={loading}
      language="en"
    />
  );
}
```

### Example 3: Arabic/RTL Version

```typescript
import React from 'react';
import { SoilNutrientAnalysis } from '@/features/soil/components';

export default function ArabicSoilAnalysis() {
  return (
    <div dir="rtl">
      <SoilNutrientAnalysis language="ar" />
    </div>
  );
}
```

## Color Coding

The component uses intuitive color coding for nutrient status:

- **Red**: Low levels (requires attention)
- **Green**: Optimal levels (healthy)
- **Yellow**: High levels (may need adjustment)

## Icons Used

The component uses the following Lucide React icons:

- `Leaf`: NPK levels and organic matter
- `AlertCircle`: Deficiency alerts
- `TrendingUp`: Positive trends
- `TrendingDown`: Negative trends
- `Check`: Optimal status
- `RefreshCw`: Refresh button
- `Droplets`: Moisture and pH
- `Thermometer`: Temperature

## Responsive Design

The component is fully responsive and adapts to different screen sizes:

- **Desktop**: Full layout with all features visible
- **Tablet**: Grid layout adjusts to 2 columns
- **Mobile**: Single column layout for easy scrolling

## Accessibility

- Semantic HTML structure
- Color-blind friendly color combinations
- ARIA labels for icons and interactive elements
- Keyboard navigation support

## Customization

### Styling

The component uses Tailwind CSS classes. You can customize the appearance by:

1. Modifying the Tailwind configuration
2. Adding custom CSS classes
3. Using Tailwind's JIT mode for dynamic styles

### Language Support

To add additional languages, extend the `translations` object in the component and add the language type to the `language` prop.

## API Integration Guide

To integrate with your backend API:

1. Create an API endpoint that returns data matching the `SoilNutrient` interface
2. Use the `onRefresh` prop to handle data updates
3. Manage loading states with the `loading` prop
4. Handle errors with try-catch blocks and display error states

Example API response format:

```json
{
  "id": "soil-001",
  "fieldId": "field-123",
  "fieldName": "North Field",
  "fieldNameAr": "الحقل الشمالي",
  "sampleDate": "2025-12-28T10:30:00Z",
  "location": {
    "latitude": 15.5527,
    "longitude": 48.5164
  },
  "nutrients": {
    "nitrogen": {
      "current": 45,
      "optimal": { "min": 40, "max": 60 },
      "unit": "ppm",
      "status": "optimal",
      "trend": "up"
    },
    "phosphorus": {
      "current": 15,
      "optimal": { "min": 20, "max": 40 },
      "unit": "ppm",
      "status": "low",
      "trend": "down"
    },
    "potassium": {
      "current": 185,
      "optimal": { "min": 100, "max": 200 },
      "unit": "ppm",
      "status": "optimal",
      "trend": "stable"
    }
  },
  "ph": {
    "current": 7.2,
    "optimal": { "min": 6.0, "max": 7.5 },
    "status": "neutral"
  },
  "organicMatter": {
    "percentage": 3.8,
    "status": "moderate"
  },
  "moisture": {
    "percentage": 22,
    "status": "optimal"
  },
  "temperature": {
    "celsius": 24
  }
}
```

## Performance Considerations

- The component uses React hooks for state management
- Historical data is only rendered when requested (lazy loading)
- Avoid passing new object references on every render to prevent unnecessary re-renders
- Use memoization for expensive calculations if needed

## Troubleshooting

### Icons not displaying

Make sure `lucide-react` is installed:

```bash
npm install lucide-react
# or
yarn add lucide-react
```

### Tailwind classes not working

Ensure your Tailwind configuration includes the component path:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './apps/web/src/**/*.{js,ts,jsx,tsx}',
  ],
  // ... rest of config
};
```

### RTL not working properly

Make sure you're setting the `dir` attribute on a parent element when using Arabic:

```typescript
<div dir="rtl">
  <SoilNutrientAnalysis language="ar" />
</div>
```

## License

This component is part of the SAHOOL platform and follows the project's license.

## Support

For issues, questions, or contributions, please contact the SAHOOL development team.
