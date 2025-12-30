# Harvest Planning Dashboard
# لوحة معلومات تخطيط الحصاد

A comprehensive harvest planning and optimization dashboard component for the SAHOOL agricultural platform, inspired by industry-leading solutions like John Deere Operations Center and Climate FieldView.

## Features / الميزات

### 1. Field Harvest Readiness Indicators
**مؤشرات جاهزية الحقول للحصاد**

- **Ready (جاهز)**: Fields at optimal maturity with ideal conditions
- **Almost Ready (شبه جاهز)**: Fields approaching optimal harvest window
- **Not Ready (غير جاهز)**: Fields requiring more time to mature

Each field displays:
- Maturity level progress (0-100%)
- Moisture content vs optimal
- Days until optimal harvest
- Priority ranking (1-10)
- Predicted yield
- Quality grade assessment

### 2. Optimal Harvest Window Calendar View
**عرض تقويم نوافذ الحصاد المثلى**

- Start and end dates for harvest period
- Optimal harvest date with confidence percentage
- Reasoning for recommended timing (Arabic & English)
- Days remaining countdown

### 3. Weather Forecast Integration
**تكامل توقعات الطقس**

5-day weather forecast showing:
- Temperature (high/low)
- Precipitation
- Humidity
- Wind speed
- Weather condition icons
- Harvest suitability rating (excellent/good/fair/poor)

### 4. Equipment Availability Status
**حالة توفر المعدات**

Track all harvest equipment:
- **Available (متاح)**: Ready for immediate use
- **In Use (قيد الاستخدام)**: Currently assigned to field
- **Maintenance (تحت الصيانة)**: Undergoing maintenance
- **Unavailable (غير متاح)**: Out of service

Equipment details include:
- Capacity (hectares per day)
- Efficiency rating
- Assigned field (if in use)
- Availability date (if in maintenance)

### 5. Predicted Yield Summary by Field
**ملخص المحصول المتوقع حسب الحقل**

- Total predicted yield in tons
- Yield per hectare
- Comparison with expected yield
- Field area
- Crop type

### 6. Quality Grade Predictions
**توقعات درجة الجودة**

Quality grading system:
- **Premium (ممتاز)**: 90-100% quality score
- **Grade A (درجة أولى)**: 80-89% quality score
- **Grade B (درجة ثانية)**: 70-79% quality score
- **Grade C (درجة ثالثة)**: Below 70%

Factors affecting quality:
- Moisture content
- Maturity level
- Weather conditions
- Harvest timing

### 7. Harvest Priority Ranking
**ترتيب أولوية الحصاد**

Interactive table showing:
- Priority order (1-n)
- Field name and area
- Crop type
- Readiness status
- Maturity percentage
- Days to optimal harvest
- Predicted yield

### 8. Arabic RTL Support
**دعم اللغة العربية من اليمين إلى اليسار**

- Full RTL layout support
- Bilingual labels (Arabic primary, English secondary)
- Arabic number formatting
- Culturally appropriate design for Yemen market

## Installation / التثبيت

The component is already integrated into the SAHOOL platform analytics feature.

### Dependencies
```json
{
  "react": "^19.0.0",
  "lucide-react": "^0.468.0",
  "tailwindcss": "^3.4.17"
}
```

## Usage / الاستخدام

### Basic Usage

```tsx
import { HarvestPlanningDashboard } from '@/features/analytics';

export default function HarvestPage() {
  return <HarvestPlanningDashboard />;
}
```

### In Next.js App Router

Create a file: `app/harvest-planning/page.tsx`

```tsx
import { HarvestPlanningDashboard } from '@/features/analytics';

export default function HarvestPlanningPage() {
  return (
    <div className="min-h-screen">
      <HarvestPlanningDashboard />
    </div>
  );
}
```

### With Navigation

```tsx
import { HarvestPlanningDashboard } from '@/features/analytics';

export default function FarmDashboard() {
  const [view, setView] = useState('overview');

  return (
    <div>
      <nav>
        <button onClick={() => setView('overview')}>Overview</button>
        <button onClick={() => setView('harvest')}>Harvest Planning</button>
      </nav>

      {view === 'harvest' && <HarvestPlanningDashboard />}
    </div>
  );
}
```

## TypeScript Interfaces / واجهات TypeScript

### Main Interfaces

```typescript
import type {
  HarvestPlan,
  FieldReadiness,
  HarvestWindow,
  WeatherForecast,
  Equipment,
  ReadinessStatus,
  QualityGrade,
  EquipmentStatus,
} from '@/features/analytics';
```

### Field Readiness
```typescript
interface FieldReadiness {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  area: number; // hectares
  status: ReadinessStatus;
  maturityLevel: number; // 0-100
  moistureContent: number; // percentage
  optimalMoisture: number;
  daysToOptimal: number;
  predictedYield: number; // kg
  yieldPerHectare: number;
  qualityGrade: QualityGrade;
  qualityScore: number; // 0-100
  priority: number; // 1-10
}
```

## Mock Data / البيانات التجريبية

The component includes comprehensive mock data for:
- 4 fields with varying readiness levels
- 5-day weather forecast
- 4 pieces of equipment
- 3 optimal harvest windows

This allows for immediate testing and demonstration without requiring API integration.

## API Integration / تكامل واجهة برمجة التطبيقات

### Connecting to Real Data

To replace mock data with real API data, create a custom hook:

```typescript
// hooks/useHarvestPlan.ts
import { useState, useEffect } from 'react';
import type { HarvestPlan } from '@/features/analytics';

export function useHarvestPlan(farmId: string) {
  const [data, setData] = useState<HarvestPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/harvest-plans/${farmId}`)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [farmId]);

  return { data, loading, error };
}
```

Then modify the component to use the hook instead of mock data.

## Customization / التخصيص

### Color Scheme

The component uses Tailwind CSS utility classes. Customize colors by modifying:

```tsx
// Ready status (green)
className="bg-green-100 border-green-300 text-green-800"

// Almost ready status (yellow)
className="bg-yellow-100 border-yellow-300 text-yellow-800"

// Not ready status (gray)
className="bg-gray-100 border-gray-300 text-gray-800"
```

### Icons

Uses lucide-react icons. Available icons in component:
- `Calendar` - Harvest timing
- `Sun` - Sunny weather
- `Cloud` - Cloudy/rainy weather
- `Loader2` - Loading/almost ready
- `Check` - Ready status
- `AlertCircle` - Not ready/warnings
- `TrendingUp` - Yield trends
- `MapPin` - Field location
- `Leaf` - Crop/field indicator
- `RefreshCw` - Refresh action

### Responsive Breakpoints

```tsx
// Mobile-first responsive grid
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"

// Responsive column layout
className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4"
```

## Testing / الاختبار

### E2E Test Selectors

The component includes data-testid attributes for testing:

```tsx
// Summary cards
data-testid="summary-cards"

// Field cards
data-testid="field-card-{fieldId}"

// Harvest windows
data-testid="harvest-window-{fieldId}"

// Weather forecast
data-testid="weather-{date}"

// Equipment
data-testid="equipment-{equipmentId}"

// Quality predictions
data-testid="quality-{fieldId}"

// Priority table
data-testid="priority-table"
data-testid="priority-row-{fieldId}"

// Refresh button
data-testid="refresh-button"
```

### Test Example

```typescript
import { render, screen } from '@testing-library/react';
import { HarvestPlanningDashboard } from './HarvestPlanningDashboard';

test('renders harvest planning dashboard', () => {
  render(<HarvestPlanningDashboard />);

  // Check header
  expect(screen.getByText('تخطيط الحصاد')).toBeInTheDocument();

  // Check summary cards
  expect(screen.getByTestId('summary-cards')).toBeInTheDocument();

  // Check priority table
  expect(screen.getByTestId('priority-table')).toBeInTheDocument();
});
```

## Performance / الأداء

### Optimization Features

- Efficient state management with React hooks
- Memoized calculations
- Responsive images and icons
- Lazy loading ready (component uses 'use client' directive)
- Minimal re-renders with proper React patterns

## Accessibility / إمكانية الوصول

- Semantic HTML structure
- Keyboard navigation support
- ARIA labels for screen readers
- High contrast color combinations
- Responsive touch targets (mobile-friendly)
- RTL layout for Arabic users

## Browser Support / دعم المتصفحات

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 14+, Chrome Mobile

## Comparison with Industry Solutions

### John Deere Operations Center
✅ Field readiness tracking
✅ Equipment management
✅ Weather integration
✅ Yield predictions
✅ Priority ranking

### Climate FieldView
✅ Field-level analytics
✅ Quality assessments
✅ Harvest timing recommendations
✅ Weather-based planning
✅ Multi-field comparison

### SAHOOL Unique Features
- Arabic-first interface with full RTL support
- Yemen-specific weather data
- Localized crop types and terminology
- Regional farming practices integration
- Mobile-optimized for field use

## Future Enhancements / التحسينات المستقبلية

Potential additions:
- [ ] Export harvest plan to PDF/Excel
- [ ] Integration with IoT soil sensors
- [ ] Historical yield comparison
- [ ] Automated equipment scheduling
- [ ] Mobile app version
- [ ] Real-time notifications
- [ ] Integration with commodity market prices
- [ ] Labor scheduling module
- [ ] Crop rotation planning
- [ ] Multi-farm management

## Support / الدعم

For issues or questions:
- Check the example file: `HarvestPlanningDashboard.example.tsx`
- Review type definitions in `analytics/types.ts`
- Contact the development team

## License / الترخيص

Part of the SAHOOL unified agricultural platform.
Proprietary - All rights reserved.

---

**Created for SAHOOL Agricultural Platform**
**تم إنشاؤه لمنصة سحول الزراعية**

Version: 1.0.0
Last Updated: 2025-12-30
