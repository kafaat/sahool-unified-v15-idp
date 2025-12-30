# Disease Risk Forecast Component

## مكون توقعات مخاطر الأمراض

A comprehensive disease risk forecasting component for the SAHOOL agricultural platform, inspired by industry leaders like John Deere and Farmonaut. This component provides 7-14 day disease outbreak probability forecasts based on weather conditions, crop stages, and disease epidemiology models.

---

## Features / المميزات

### Core Features
- ✅ **7-14 Day Forecast**: Flexible forecast periods for short and medium-term planning
- ✅ **Weather-based Risk Calculation**: Incorporates temperature, humidity, rainfall, and other weather factors
- ✅ **4-Level Risk Classification**: Low, Moderate, High, and Critical risk levels
- ✅ **Disease-Specific Predictions**: Individual risk assessments for multiple diseases
- ✅ **Preventive Recommendations**: Actionable advice prioritized by urgency
- ✅ **Crop Stage Vulnerability**: Risk adjustments based on crop growth stage
- ✅ **Interactive Timeline**: Visual, color-coded daily risk calendar
- ✅ **Bilingual Support**: Full Arabic (RTL) and English labeling
- ✅ **Responsive Design**: Mobile-first, works on all screen sizes
- ✅ **Production-Ready**: Loading states, error handling, and data validation

### Disease Models
The component currently models these common crop diseases:
1. **Late Blight** (اللفحة المتأخرة) - *Phytophthora infestans*
2. **Powdery Mildew** (البياض الدقيقي)
3. **Downy Mildew** (البياض الزغبي)
4. **Anthracnose** (أنثراكنوز)

Each disease has specific environmental triggers based on:
- Optimal temperature ranges
- Humidity requirements
- Rainfall patterns
- Crop vulnerability by growth stage

---

## Installation / التثبيت

The component is already integrated into the SAHOOL platform. To use it:

```tsx
import { DiseaseRiskForecast } from '@/features/crop-health';
// or
import { DiseaseRiskForecast } from '@/features/crop-health/components/DiseaseRiskForecast';
```

---

## Basic Usage / الاستخدام الأساسي

### Simple Example

```tsx
import { DiseaseRiskForecast } from '@/features/crop-health';

export default function MyPage() {
  return (
    <div>
      <DiseaseRiskForecast />
    </div>
  );
}
```

### With Custom Props

```tsx
import { DiseaseRiskForecast } from '@/features/crop-health';
import type { CropStage } from '@/features/crop-health';

export default function FieldPage() {
  const cropStage: CropStage = {
    id: 'flowering',
    name: 'Flowering',
    nameAr: 'الإزهار',
    vulnerabilityMultiplier: 1.8,
  };

  return (
    <DiseaseRiskForecast
      fieldId="field-123"
      cropType="Tomato"
      cropTypeAr="طماطم"
      cropStage={cropStage}
      forecastDays={14}
      lat={15.3694}
      lon={44.1910}
      onRefresh={() => console.log('Refreshing...')}
    />
  );
}
```

---

## API Reference / مرجع الواجهة

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `fieldId` | `string?` | `undefined` | Unique identifier for the field |
| `cropType` | `string?` | `'Tomato'` | Crop type in English |
| `cropTypeAr` | `string?` | `'طماطم'` | Crop type in Arabic |
| `cropStage` | `CropStage?` | Flowering stage | Current growth stage of the crop |
| `forecastDays` | `7 \| 14` | `7` | Number of forecast days |
| `lat` | `number?` | `undefined` | Field latitude for weather data |
| `lon` | `number?` | `undefined` | Field longitude for weather data |
| `onRefresh` | `() => void?` | `undefined` | Callback when refresh button clicked |
| `isLoading` | `boolean?` | `false` | External loading state |
| `error` | `string \| null?` | `null` | External error message |

### TypeScript Interfaces

#### `WeatherFactors`
```typescript
interface WeatherFactors {
  temperature: number;      // °C
  humidity: number;         // %
  rainfall: number;         // mm
  windSpeed?: number;       // km/h
  cloudCover?: number;      // %
}
```

#### `CropStage`
```typescript
interface CropStage {
  id: string;
  name: string;            // English name
  nameAr: string;          // Arabic name
  vulnerabilityMultiplier: number;  // 0.5 - 2.0 (affects risk calculation)
}
```

#### `RiskLevel`
```typescript
type RiskLevel = 'low' | 'moderate' | 'high' | 'critical';
```

#### `DiseaseRisk`
```typescript
interface DiseaseRisk {
  disease: {
    id: string;
    name: string;
    nameAr: string;
    type: string;
    typeAr: string;
  };
  probability: number;      // 0-100%
  riskLevel: RiskLevel;
  contributingFactors: {
    temperature: number;    // impact score 0-100
    humidity: number;       // impact score 0-100
    rainfall: number;       // impact score 0-100
  };
}
```

#### `RiskForecast`
```typescript
interface RiskForecast {
  date: string;
  dayNumber: number;
  weather: WeatherFactors;
  overallRiskLevel: RiskLevel;
  riskScore: number;        // 0-100
  diseases: DiseaseRisk[];
  recommendations: {
    action: string;
    actionAr: string;
    priority: 'low' | 'medium' | 'high';
  }[];
}
```

---

## Crop Stages / مراحل المحصول

### Default Crop Stages

| Stage ID | Name (EN) | Name (AR) | Vulnerability |
|----------|-----------|-----------|---------------|
| `seedling` | Seedling | الشتلة | 1.5× |
| `vegetative` | Vegetative Growth | النمو الخضري | 1.2× |
| `flowering` | Flowering | الإزهار | 1.8× |
| `fruiting` | Fruiting | الإثمار | 1.4× |
| `maturity` | Maturity | النضج | 1.0× |

**Vulnerability Multiplier**: Higher values mean the crop is more susceptible to diseases at that stage.

---

## Risk Calculation Algorithm

### Overview
The component uses a weather-based epidemiological model to calculate disease risk. Each disease has optimal environmental conditions that promote growth and infection.

### Calculation Steps

1. **Temperature Factor** (0-100)
   - Calculate based on distance from optimal range
   - Disease-specific optimal temperatures

2. **Humidity Factor** (0-100)
   - Higher humidity generally increases fungal disease risk
   - Some diseases prefer specific humidity ranges

3. **Rainfall Factor** (0-100)
   - Rainfall creates conditions for spore dispersal
   - Leaf wetness promotes infection

4. **Crop Stage Adjustment**
   - Base probability × vulnerability multiplier
   - Accounts for crop's susceptibility at different stages

5. **Final Risk Score**
   - Average of all contributing factors
   - Adjusted by crop stage vulnerability
   - Classified into Low/Moderate/High/Critical

### Example: Late Blight Calculation

```typescript
// Optimal conditions: 15-25°C, 90%+ humidity, rainfall
const tempScore = temperature >= 15 && temperature <= 25
  ? 100
  : Math.max(0, 100 - Math.abs(temperature - 20) * 5);

const humidityScore = humidity >= 90
  ? 100
  : humidity * 1.1;

const rainfallScore = rainfall > 5
  ? 100
  : rainfall * 15;

const baseProb = (tempScore + humidityScore + rainfallScore) / 3;
const finalProb = baseProb * cropStage.vulnerabilityMultiplier;
```

---

## Customization / التخصيص

### Custom Crop Stages

```tsx
const customStage: CropStage = {
  id: 'custom-stage',
  name: 'Post-Harvest',
  nameAr: 'ما بعد الحصاد',
  vulnerabilityMultiplier: 0.8, // Lower risk
};

<DiseaseRiskForecast cropStage={customStage} />
```

### Styling

The component uses Tailwind CSS and follows the SAHOOL design system. All colors and styles can be customized by modifying the `RISK_CONFIG` object in the source file.

---

## Integration Examples / أمثلة التكامل

### 1. Dashboard Integration

```tsx
import { DiseaseRiskForecast } from '@/features/crop-health';

export default function CropHealthDashboard() {
  return (
    <div className="space-y-6">
      <h1>Crop Health Overview</h1>
      <DiseaseRiskForecast forecastDays={7} />
      {/* Other dashboard components */}
    </div>
  );
}
```

### 2. Field Details Page

```tsx
import { DiseaseRiskForecast } from '@/features/crop-health';
import { useField } from '@/features/fields';

export default function FieldDetailsPage({ fieldId }: { fieldId: string }) {
  const { data: field } = useField(fieldId);

  if (!field) return <div>Loading...</div>;

  return (
    <div>
      <h1>{field.name}</h1>
      <DiseaseRiskForecast
        fieldId={field.id}
        cropType={field.cropType}
        cropTypeAr={field.cropTypeAr}
        cropStage={field.currentStage}
        lat={field.location.lat}
        lon={field.location.lon}
      />
    </div>
  );
}
```

### 3. With Real Weather API

```tsx
import { DiseaseRiskForecast } from '@/features/crop-health';
import { useWeatherForecast } from '@/features/weather';

export default function WeatherIntegratedForecast() {
  const { data, isLoading, error, refetch } = useWeatherForecast({
    lat: 15.3694,
    lon: 44.1910,
    days: 7,
  });

  return (
    <DiseaseRiskForecast
      lat={15.3694}
      lon={44.1910}
      isLoading={isLoading}
      error={error?.message || null}
      onRefresh={refetch}
    />
  );
}
```

---

## Testing / الاختبار

The component includes test IDs for automated testing:

```tsx
// Test IDs
data-testid="disease-risk-forecast"     // Main container
data-testid="disease-risk-loading"      // Loading state
data-testid="disease-risk-error"        // Error state
data-testid="refresh-button"            // Refresh button
data-testid="timeline-day-{index}"      // Timeline day buttons
```

### Example Test

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { DiseaseRiskForecast } from './DiseaseRiskForecast';

test('renders disease risk forecast', () => {
  render(<DiseaseRiskForecast />);
  expect(screen.getByTestId('disease-risk-forecast')).toBeInTheDocument();
});

test('calls onRefresh when refresh button clicked', () => {
  const mockRefresh = jest.fn();
  render(<DiseaseRiskForecast onRefresh={mockRefresh} />);

  fireEvent.click(screen.getByTestId('refresh-button'));
  expect(mockRefresh).toHaveBeenCalled();
});
```

---

## Performance Considerations / الأداء

### Optimization Features

1. **useMemo Hook**: Forecast data is memoized to prevent unnecessary recalculations
2. **Efficient Re-renders**: Only updates when props change
3. **Lightweight Icons**: Uses lucide-react's tree-shakeable icons
4. **Responsive Images**: No heavy images, all UI is CSS-based

### Best Practices

- Use the component within a parent that handles data fetching
- Implement proper loading and error states
- Cache forecast data when possible
- Consider using React Query or SWR for API integration

---

## Browser Support / دعم المتصفحات

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## Accessibility / إمكانية الوصول

- ✅ Keyboard navigation support
- ✅ Screen reader friendly
- ✅ Semantic HTML
- ✅ ARIA labels where appropriate
- ✅ Color contrast compliance (WCAG 2.1 AA)
- ✅ RTL language support

---

## Future Enhancements / تحسينات مستقبلية

### Planned Features
- [ ] Historical accuracy tracking
- [ ] More disease models (bacterial, viral)
- [ ] Pest risk integration
- [ ] Machine learning predictions
- [ ] Push notifications for critical alerts
- [ ] Export to PDF/Excel
- [ ] Integration with spray scheduling
- [ ] Multi-field comparison view

### Contributing
To add new disease models, modify the `calculateDiseaseRisk` function with:
1. Disease-specific environmental triggers
2. Optimal condition ranges
3. Contributing factor calculations
4. Risk level thresholds

---

## License / الترخيص

This component is part of the SAHOOL platform and is proprietary software.

---

## Support / الدعم

For issues or questions:
- Documentation: This README
- Examples: `DiseaseRiskForecast.example.tsx`
- Component: `DiseaseRiskForecast.tsx`

---

## Credits / الشكر والتقدير

Inspired by:
- John Deere Operations Center
- Farmonaut Satellite Farming
- International disease prediction models from agricultural research institutions

---

**Last Updated**: December 30, 2024
**Version**: 1.0.0
**Author**: SAHOOL Development Team
