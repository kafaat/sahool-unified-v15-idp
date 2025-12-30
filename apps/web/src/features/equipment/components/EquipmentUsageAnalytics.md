# Equipment Usage Analytics Component

**مكون تحليلات استخدام المعدات**

## Overview / نظرة عامة

The `EquipmentUsageAnalytics` component provides comprehensive analytics and insights for agricultural equipment, similar to John Deere Operations Center. It tracks operating hours, fuel consumption, utilization rates, costs, and maintenance status.

يوفر مكون `EquipmentUsageAnalytics` تحليلات ورؤى شاملة للمعدات الزراعية، مشابهة لمركز عمليات جون ديري. يتتبع ساعات التشغيل، واستهلاك الوقود، ومعدلات الاستخدام، والتكاليف، وحالة الصيانة.

## Features / الميزات

### 1. Operating Hours Chart / مخطط ساعات التشغيل
- **Daily, Weekly, Monthly views** - عرض يومي، أسبوعي، شهري
- **Interactive bar charts** - مخططات شريطية تفاعلية
- **Statistics summary** - ملخص الإحصائيات (Total, Average, Peak)

### 2. Fuel Consumption Metrics / مقاييس استهلاك الوقود
- **Current fuel level gauge** - مقياس مستوى الوقود الحالي
- **Consumption tracking** - تتبع الاستهلاك (Daily/Weekly/Monthly)
- **Efficiency trends** - اتجاهات الكفاءة (Liters per hour)
- **Cost calculations** - حسابات التكلفة
- **Days remaining estimate** - تقدير الأيام المتبقية

### 3. Equipment Utilization Rate / معدل استخدام المعدات
- **Percentage-based metrics** - مقاييس قائمة على النسبة المئوية
- **Active vs Available hours** - الساعات النشطة مقابل المتاحة
- **Trend indicators** - مؤشرات الاتجاه (Up/Down/Stable)
- **Performance comparison** - مقارنة الأداء

### 4. Cost Per Hour Calculations / حسابات التكلفة في الساعة
- **Real-time cost tracking** - تتبع التكلفة في الوقت الفعلي
- **Arabic currency format** - تنسيق العملة العربية (ريال)
- **Comparative analysis** - تحليل مقارن

### 5. Downtime Analysis / تحليل التوقف
- **Total downtime tracking** - تتبع إجمالي وقت التوقف
- **Breakdown by reasons** - التفصيل حسب الأسباب
- **Visual percentage bars** - أشرطة النسبة المئوية المرئية
- **Last incident details** - تفاصيل آخر حادثة

### 6. Maintenance Status Indicator / مؤشر حالة الصيانة
- **Color-coded status** - حالة مرمزة بالألوان:
  - 🟢 **Good (جيد)** - Maintenance up to date
  - 🟡 **Warning (تحذير)** - Maintenance due soon
  - 🔴 **Critical (حرج)** - Urgent maintenance required
- **Animated indicators** - مؤشرات متحركة
- **Bilingual descriptions** - أوصاف ثنائية اللغة

### 7. Equipment Comparison Table / جدول مقارنة المعدات
- **Side-by-side comparison** - مقارنة جنبًا إلى جنب
- **Multiple metrics** - مقاييس متعددة
- **Performance rankings** - تصنيفات الأداء
- **Summary statistics** - إحصائيات ملخصة

### 8. Arabic RTL Support / دعم العربية من اليمين إلى اليسار
- **Full RTL layout support** - دعم كامل لتخطيط RTL
- **Bilingual labels** - تسميات ثنائية اللغة (Arabic + English)
- **Arabic number formatting** - تنسيق الأرقام العربية
- **Yemen locale (ar-YE)** - اللغة المحلية اليمنية

## Installation / التثبيت

The component is already integrated into the SAHOOL equipment feature. Simply import it:

```typescript
import { EquipmentUsageAnalytics } from '@/features/equipment';
```

## Props / الخصائص

```typescript
interface EquipmentUsageAnalyticsProps {
  equipmentId?: string;           // Optional: Specific equipment ID to display
  showComparison?: boolean;       // Optional: Show comparison table (default: true)
  initialTimeRange?: TimeRange;   // Optional: 'daily' | 'weekly' | 'monthly' (default: 'daily')
}
```

## Usage Examples / أمثلة الاستخدام

### Basic Usage / الاستخدام الأساسي

```tsx
import { EquipmentUsageAnalytics } from '@/features/equipment';

export function EquipmentAnalyticsPage() {
  return (
    <EquipmentUsageAnalytics equipmentId="eq-001" />
  );
}
```

### With Custom Settings / مع إعدادات مخصصة

```tsx
<EquipmentUsageAnalytics
  equipmentId="eq-002"
  showComparison={true}
  initialTimeRange="weekly"
/>
```

### Without Comparison / بدون مقارنة

```tsx
<EquipmentUsageAnalytics
  equipmentId="eq-003"
  showComparison={false}
/>
```

## TypeScript Interfaces / واجهات TypeScript

### EquipmentUsage

```typescript
interface EquipmentUsage {
  equipmentId: string;
  equipmentName: string;
  equipmentNameAr: string;
  type: 'tractor' | 'harvester' | 'irrigation_system' | 'sprayer' | 'planter' | 'other';
  operatingHours: {
    daily: number[];
    weekly: number[];
    monthly: number[];
  };
  fuelConsumption: FuelMetrics;
  utilization: UtilizationData;
  costPerHour: number;
  downtime: DowntimeData;
  maintenanceStatus: MaintenanceStatus;
  location?: string;
  lastUpdated: string;
}
```

### FuelMetrics

```typescript
interface FuelMetrics {
  currentLevel: number;           // Percentage (0-100)
  consumption: {
    daily: number;                // Liters
    weekly: number;
    monthly: number;
  };
  efficiency: {
    litersPerHour: number;
    trend: 'up' | 'down' | 'stable';
    changePercentage: number;
  };
  totalCost: number;             // In YER (Yemeni Rial)
  estimatedDaysRemaining: number;
}
```

### UtilizationData

```typescript
interface UtilizationData {
  rate: number;                  // Percentage (0-100)
  activeHours: number;
  totalAvailableHours: number;
  trend: 'up' | 'down' | 'stable';
  changePercentage: number;
}
```

### DowntimeData

```typescript
interface DowntimeData {
  totalHours: number;
  reasons: Array<{
    reason: string;
    reasonAr: string;
    hours: number;
    percentage: number;
  }>;
  lastIncident: {
    date: string;
    reason: string;
    reasonAr: string;
    duration: number;
  };
}
```

### MaintenanceStatus

```typescript
type MaintenanceStatus = 'good' | 'warning' | 'critical';
```

## Mock Data / البيانات التجريبية

The component includes comprehensive mock data for three pieces of equipment:

1. **John Deere 8R Series Tractor** (جرار جون ديري)
2. **Case IH Axial-Flow Harvester** (حصادة كيس IH)
3. **Valley Pivot Irrigation System** (نظام الري المحوري)

This mock data demonstrates all features and can be replaced with real API data.

## Styling / التصميم

The component uses **Tailwind CSS** with responsive design:

- **Mobile-first approach** - نهج الجوال أولاً
- **Grid layouts** - تخطيطات الشبكة
- **Responsive breakpoints** - نقاط التوقف المستجيبة (md, lg)
- **Color-coded metrics** - مقاييس مرمزة بالألوان
- **Smooth transitions** - انتقالات سلسة

### Color Scheme / نظام الألوان

- **Blue** - Operating hours, Utilization
- **Green** - Fuel efficiency, Good status
- **Orange** - Costs, Downtime
- **Yellow** - Warning status
- **Red** - Critical status, Alerts

## Icons / الأيقونات

Uses **lucide-react** icons (verified to work):

- `Clock` - Operating hours
- `TrendingUp` - Upward trends
- `TrendingDown` - Downward trends
- `AlertCircle` - Warnings and critical status
- `Check` - Good status
- `RefreshCw` - Refresh button
- `Settings` - Maintenance warning
- `MapPin` - Location

## States / الحالات

### Loading State / حالة التحميل

Component handles loading state with animated spinner:

```tsx
{isLoading && (
  <RefreshCw className="w-5 h-5 animate-spin" />
)}
```

### Error State / حالة الخطأ

Displays bilingual error message when equipment not found:

```tsx
<div className="bg-red-50 border border-red-200 rounded-lg p-6">
  <AlertCircle className="w-12 h-12 text-red-600" />
  <p className="text-red-800">معدات غير موجودة</p>
  <p className="text-red-600">Equipment not found</p>
</div>
```

## Responsive Design / التصميم المستجيب

- **Mobile (< 768px)**: Single column layout
- **Tablet (768px+)**: 2-column grid
- **Desktop (1024px+)**: 4-column grid for metrics

## Integration with API / التكامل مع API

To integrate with real API data, update the component to use a custom hook:

```typescript
// In hooks/useEquipment.ts
export function useEquipmentUsageAnalytics(equipmentId: string) {
  return useQuery({
    queryKey: equipmentKeys.usage(equipmentId),
    queryFn: () => equipmentApi.getUsageAnalytics(equipmentId),
  });
}

// In api.ts
getUsageAnalytics: async (equipmentId: string) => {
  const res = await fetch(`${API_BASE_URL}/equipment/${equipmentId}/analytics`);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}
```

## Performance Optimization / تحسين الأداء

The component uses React optimization techniques:

- **useMemo** for expensive calculations
- **Conditional rendering** for large lists
- **Efficient re-renders** with proper dependencies
- **Lazy loading** support (can be wrapped in Suspense)

## Accessibility / إمكانية الوصول

- **data-testid** attributes for testing
- **Semantic HTML** structure
- **Keyboard navigation** support
- **Screen reader friendly** labels
- **Color contrast** meets WCAG standards

## Testing / الاختبار

Test IDs included for easy testing:

```typescript
// Equipment Analytics
data-testid="equipment-usage-analytics"
data-testid="analytics-title-ar"
data-testid="analytics-title-en"
data-testid="equipment-selector"
data-testid="time-range-daily"
data-testid="refresh-button"

// Metrics
data-testid="metric-card-utilization-rate"
data-testid="metric-card-fuel-efficiency"
data-testid="maintenance-status-card"

// Charts & Tables
data-testid="operating-hours-chart"
data-testid="fuel-consumption-metrics"
data-testid="downtime-analysis"
data-testid="equipment-comparison-table"
```

## Browser Support / دعم المتصفحات

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Future Enhancements / التحسينات المستقبلية

Potential features for future versions:

1. **Export to PDF/Excel** - تصدير إلى PDF/Excel
2. **Custom date range selection** - اختيار نطاق تاريخ مخصص
3. **Real-time updates** - تحديثات في الوقت الفعلي
4. **Alerts and notifications** - التنبيهات والإشعارات
5. **Advanced filtering** - تصفية متقدمة
6. **Machine learning predictions** - تنبؤات التعلم الآلي

## License / الترخيص

Part of the SAHOOL Unified Platform - Yemen Agricultural Management System

## Support / الدعم

For questions or issues, contact the SAHOOL development team.

---

**Created with ❤️ for Yemen's Agricultural Future**
**صُنع بحب لمستقبل اليمن الزراعي**
