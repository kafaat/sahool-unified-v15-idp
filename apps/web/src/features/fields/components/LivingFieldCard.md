# Living Field Card Component

# مكون بطاقة الحقل الحي

## Overview | نظرة عامة

The Living Field Card is a comprehensive React component that displays a real-time health score for agricultural fields. It combines multiple data sources to provide farmers with an at-a-glance view of their field's overall health and actionable recommendations.

بطاقة الحقل الحي هي مكون React شامل يعرض نقاط الصحة في الوقت الفعلي للحقول الزراعية. يجمع مصادر بيانات متعددة لتزويد المزارعين بنظرة سريعة على الصحة العامة لحقلهم والتوصيات القابلة للتنفيذ.

## Features | الميزات

### 1. Overall Score | النقاط الإجمالية

- Large circular progress indicator (0-100)
- Color-coded based on health:
  - 🟢 Green (>70): Excellent
  - 🟡 Yellow (40-70): Moderate
  - 🔴 Red (<40): Poor
- Smooth animated transitions

### 2. Sub-Scores | النقاط الفرعية

Four individual health indicators:

#### Health Score (الصحة) - 35% weight

- Calculated from NDVI satellite data
- Icon: ❤️ Heart
- Indicates crop vegetation health

#### Hydration Score (الترطيب) - 25% weight

- Based on weather data and precipitation
- Icon: 💧 Droplets
- Shows irrigation needs

#### Attention Score (الاهتمام) - 20% weight

- Derived from pending and overdue tasks
- Icon: 👁️ Eye
- Reflects field maintenance activity

#### Astral Score (الفلكي) - 20% weight

- From Yemeni astronomical calendar
- Icon: 🌙 Moon
- Traditional farming timing guidance

### 3. Trend Indicator | مؤشر الاتجاه

- 📈 Improving (يتحسن)
- 📉 Declining (يتراجع)
- ➖ Stable (مستقر)

### 4. Alert System | نظام التنبيهات

- Color-coded severity badges:
  - 🔴 Critical
  - 🟠 High
  - 🟡 Medium
  - ⚪ Low
- Categorized by: health, hydration, attention, astral

### 5. Recommendations | التوصيات

- Expandable section with smooth animation
- Priority-based (high, medium, low)
- Category-specific icons
- Best time suggestions for astral recommendations
- Bilingual (Arabic + English)

### 6. Tooltips | تلميحات الأدوات

- English explanations on hover
- Helps users understand each metric
- Clean, dark-themed tooltips

### 7. Responsive Design | تصميم متجاوب

- Mobile-first approach
- Grid adapts from 2 to 4 columns
- Optimized for all screen sizes

## Installation | التثبيت

The component is already integrated into the Sahool platform. Import it from the fields feature:

```typescript
import { LivingFieldCard } from "@/features/fields";
// or
import { LivingFieldCard } from "@/features/fields/components/LivingFieldCard";
```

## Usage | الاستخدام

### Basic Example

```tsx
import { LivingFieldCard } from "@/features/fields";

function MyFieldDashboard() {
  return <LivingFieldCard fieldId="field-123" />;
}
```

### With Field Names

```tsx
<LivingFieldCard
  fieldId="field-456"
  fieldName="North Wheat Field"
  fieldNameAr="حقل القمح الشمالي"
/>
```

### Multiple Fields Grid

```tsx
function FieldsOverview() {
  const fields = [
    { id: "1", name: "Field A", nameAr: "الحقل أ" },
    { id: "2", name: "Field B", nameAr: "الحقل ب" },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {fields.map((field) => (
        <LivingFieldCard
          key={field.id}
          fieldId={field.id}
          fieldName={field.name}
          fieldNameAr={field.nameAr}
        />
      ))}
    </div>
  );
}
```

## Props | الخصائص

| Prop          | Type     | Required | Description             |
| ------------- | -------- | -------- | ----------------------- |
| `fieldId`     | `string` | ✅ Yes   | Unique field identifier |
| `fieldName`   | `string` | ❌ No    | English field name      |
| `fieldNameAr` | `string` | ❌ No    | Arabic field name       |

## Hook: `useLivingFieldScore`

The component uses the `useLivingFieldScore` hook internally. You can also use it separately:

```tsx
import { useLivingFieldScore } from "@/features/fields";

function CustomComponent({ fieldId }: { fieldId: string }) {
  const score = useLivingFieldScore(fieldId);

  if (score.isLoading) return <div>Loading...</div>;
  if (score.error) return <div>Error: {score.error}</div>;

  return (
    <div>
      <p>Overall Score: {score.overall}</p>
      <p>Health: {score.health}</p>
      <p>Hydration: {score.hydration}</p>
      <p>Attention: {score.attention}</p>
      <p>Astral: {score.astral}</p>
      <p>Trend: {score.trend}</p>
      <p>Alerts: {score.alerts.length}</p>
      <p>Recommendations: {score.recommendations.length}</p>
    </div>
  );
}
```

## Data Sources | مصادر البيانات

The Living Field Score aggregates data from multiple APIs:

1. **NDVI Service** (`/api/v1/ndvi`)
   - Satellite vegetation health data
   - Historical trend analysis

2. **Tasks Service** (`/api/v1/tasks`)
   - Pending and overdue tasks
   - Completion history

3. **Astronomical Calendar** (`/api/v1/astronomical`)
   - Yemeni traditional farming calendar
   - Moon phases and mansions
   - Activity suitability scores

4. **Weather Service** (`/api/v1/weather`)
   - Current conditions
   - Precipitation data
   - Humidity levels

## Score Calculation | حساب النقاط

### Overall Score Formula

```
overall = (health × 0.35) + (hydration × 0.25) + (attention × 0.20) + (astral × 0.20)
```

### Health Score (0-100)

Based on NDVI values:

- 0.8-1.0 → 90-100 (Excellent)
- 0.6-0.8 → 70-90 (Good)
- 0.4-0.6 → 50-70 (Fair)
- 0.2-0.4 → 30-50 (Poor)
- 0.0-0.2 → 0-30 (Very Poor)

### Hydration Score (0-100)

- 70% based on current humidity
- 30% bonus from recent precipitation

### Attention Score (0-100)

- Base: 50
- -15 points per overdue task
- -10 to -20 points for too many pending tasks
- +10 points per recently completed task

### Astral Score (0-100)

- Average of all farming activity suitability scores (0-10 scale)
- Converted to 0-100 scale

## Alerts Generation | توليد التنبيهات

Alerts are automatically generated based on thresholds:

| Score Range    | Alert Severity | Category  |
| -------------- | -------------- | --------- |
| Health < 40    | Critical       | Health    |
| Health 40-70   | Medium         | Health    |
| Hydration < 40 | High           | Hydration |
| Attention < 40 | Medium         | Attention |

## Recommendations Logic | منطق التوصيات

1. **Health < 70**: Inspect crop health
2. **Hydration < 50**: Check irrigation system
3. **Attention < 50**: Complete pending tasks
4. **Astral score ≥ 7**: Favorable astronomical conditions

## Styling | التصميم

The component uses:

- **Tailwind CSS** for utility classes
- **shadcn/ui** components (Card, Badge)
- **lucide-react** for icons
- Custom SVG for circular progress

### Color Scheme

```css
Green (Excellent): #10b981, #dcfce7, #15803d
Yellow (Moderate): #eab308, #fef9c3, #a16207
Red (Poor): #ef4444, #fee2e2, #b91c1c
```

## Animations | الحركات

1. **Loading State**: Pulse animation
2. **Progress Circles**: 1-second ease-out transition
3. **Recommendations**: 300ms slide-down expansion
4. **Tooltips**: 200ms fade-in/out
5. **Hover Effects**: Scale and shadow transitions

## Accessibility | إمكانية الوصول

- Semantic HTML structure
- ARIA labels for screen readers
- Keyboard navigation support (tab, enter)
- High contrast color schemes
- Tooltip explanations for all metrics

## Performance | الأداء

- React.memo optimization (where applicable)
- Debounced hover states
- Lazy data loading with React Query
- Minimal re-renders with useMemo

## Error Handling | معالجة الأخطاء

The component gracefully handles:

- Loading states with skeleton UI
- API errors with user-friendly messages
- Missing data with fallback values
- Network failures with retry logic

## Browser Support | دعم المتصفحات

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Related Components | المكونات ذات الصلة

- `FieldCard` - Basic field information card
- `FieldDetails` - Detailed field view
- `AstralFieldWidget` - Standalone astronomical widget
- `HealthZonesLayer` - Map layer for health zones

## Testing | الاختبار

```tsx
import { render, screen } from "@testing-library/react";
import { LivingFieldCard } from "./LivingFieldCard";

describe("LivingFieldCard", () => {
  it("renders field name", () => {
    render(<LivingFieldCard fieldId="test-1" fieldNameAr="حقل الاختبار" />);
    expect(screen.getByText("حقل الاختبار")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    // Mock loading hook
    render(<LivingFieldCard fieldId="test-1" />);
    expect(screen.getByText("جاري التحميل...")).toBeInTheDocument();
  });
});
```

## Future Enhancements | التحسينات المستقبلية

- [ ] Historical score chart (last 30 days)
- [ ] Comparison with neighboring fields
- [ ] Export score report as PDF
- [ ] Push notifications for critical alerts
- [ ] AI-powered predictive insights
- [ ] Integration with IoT sensors
- [ ] Voice command support

## License | الترخيص

Copyright © 2026 Sahool Agricultural Platform
