# AstralFieldWidget Component

## نظرة عامة | Overview

**AstralFieldWidget** هو مكون React متقدم يعرض معلومات التقويم الفلكي اليمني في سياق الحقل، موفراً توصيات زراعية مبنية على المنازل القمرية وأطوار القمر.

**AstralFieldWidget** is an advanced React component that displays Yemeni astronomical calendar information in field context, providing farming recommendations based on lunar mansions and moon phases.

---

## الميزات الرئيسية | Key Features

### 1. عرض التقويم الفلكي | Astronomical Calendar Display

- **التاريخ الهجري** | Current Hijri date with full formatting
- **المنزلة القمرية** | Lunar mansion (منزلة) with constellation details
- **طور القمر** | Moon phase with icon, name, and illumination percentage
- **التقييم الزراعي العام** | Overall farming score for the day

### 2. التوصيات الزراعية | Farming Recommendations

- **اختيار النشاط** | Activity selector (زراعة، ري، حصاد، تقليم)
- **توصية اليوم** | Today's recommendation with suitability score (0-10)
- **أفضل 3 أيام** | Best 3 days this week for selected activity
- **الوقت الأمثل** | Best time of day for the activity

### 3. إنشاء المهام | Task Creation

- **إنشاء سريع** | Quick action to create task on best day
- **بيانات كاملة** | Automatic task data with Arabic and English
- **أولوية ذكية** | Smart priority assignment

### 4. العرض التفصيلي | Detailed View

- **قابل للطي** | Collapsible detailed information
- **تفاصيل المنزلة** | Lunar mansion details with crops and activities
- **أفضل الأيام** | Weekly best days with scores and reasons

---

## الاستخدام | Usage

### استيراد المكون | Import Component

```typescript
import { AstralFieldWidget } from "@/features/fields";
// or
import { AstralFieldWidget } from "@/features/fields/components/AstralFieldWidget";
```

### مثال بسيط | Basic Example

```tsx
import { AstralFieldWidget } from "@/features/fields";
import { useField } from "@/features/fields";

function FieldDetailPage({ fieldId }: { fieldId: string }) {
  const { data: field } = useField(fieldId);

  if (!field) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1>{field.nameAr}</h1>
      <AstralFieldWidget field={field} />
    </div>
  );
}
```

### مثال مع إنشاء المهام | Example with Task Creation

```tsx
import { AstralFieldWidget } from "@/features/fields";
import { useField } from "@/features/fields";
import { useCreateTask } from "@/features/tasks";

function FieldAstralView({ fieldId }: { fieldId: string }) {
  const { data: field } = useField(fieldId);
  const createTask = useCreateTask();

  const handleCreateTask = async (taskData) => {
    try {
      await createTask.mutateAsync(taskData);
      alert("تم إنشاء المهمة بنجاح!");
    } catch (error) {
      console.error("Failed to create task:", error);
    }
  };

  if (!field) return null;

  return (
    <AstralFieldWidget
      field={field}
      onCreateTask={handleCreateTask}
      compact={false}
    />
  );
}
```

### مثال مضغوط | Compact Example

```tsx
// For use in dashboards or sidebars
<AstralFieldWidget
  field={field}
  compact={true}
  onCreateTask={handleCreateTask}
/>
```

---

## واجهة البرمجة | API Reference

### Props

| Prop           | Type                           | Required | Default | Description                                         |
| -------------- | ------------------------------ | -------- | ------- | --------------------------------------------------- |
| `field`        | `Field`                        | ✅ Yes   | -       | Field object containing field details               |
| `onCreateTask` | `(taskData: TaskData) => void` | ❌ No    | -       | Callback function when creating a task              |
| `compact`      | `boolean`                      | ❌ No    | `false` | Whether to show compact view (collapsed by default) |

### Field Type

```typescript
interface Field {
  id: string;
  name: string;
  nameAr: string;
  area: number;
  crop?: string;
  cropAr?: string;
  // ... other field properties
}
```

### TaskData Type

```typescript
interface TaskData {
  title: string; // English title
  title_ar: string; // Arabic title
  description: string; // English description
  description_ar: string; // Arabic description
  due_date: string; // ISO date string (YYYY-MM-DD)
  field_id: string; // Field ID
  priority: "high" | "medium" | "low"; // Task priority
}
```

---

## التصميم والأقسام | Design & Sections

### 1. القسم العلوي | Header Section

```
┌─────────────────────────────────────────────────────┐
│ 🌙 التقويم الفلكي اليمني              [▼ Expand]  │
│    توصيات زراعية حسب المنازل القمرية               │
└─────────────────────────────────────────────────────┘
```

### 2. التاريخ والمنزلة | Date & Mansion

```
┌──────────────────────┬──────────────────────┐
│ 📅 التاريخ الهجري   │ ⭐ المنزلة القمرية │
│ 15 جمادى الآخرة     │ البطين              │
│ 1446 هـ             │ برج الحمل            │
└──────────────────────┴──────────────────────┘
```

### 3. طور القمر | Moon Phase

```
┌─────────────────────────────────────────────────────┐
│ 🌕 بدر                                     [مناسب] │
│ الإضاءة: 98% • العمر: 14 يوم                       │
└─────────────────────────────────────────────────────┘
```

### 4. اختيار النشاط | Activity Selector

```
┌───────┬───────┬───────┬───────┐
│ 🌱زراعة│ 💧 ري │✂️ حصاد│✨ تقليم│
└───────┴───────┴───────┴───────┘
```

### 5. توصية اليوم | Today's Recommendation

```
┌─────────────────────────────────────────────────────┐
│ توصية اليوم للزراعة                                │
│ ┌─────┐                                             │
│ │ 9   │ ممتاز                                       │
│ │ /10 │ المنزلة مناسبة جداً للزراعة                │
│ └─────┘ أفضل وقت: الصباح الباكر                    │
└─────────────────────────────────────────────────────┘
```

### 6. أفضل 3 أيام | Best 3 Days

```
┌─────────────────────────────────────────────────────┐
│ 📅 أفضل 3 أيام هذا الأسبوع للزراعة                │
│                                                     │
│ #1 | الثلاثاء 7 يناير        [9/10] 🌙 🌟        │
│    | المنزلة مثالية للزراعة                        │
│                                                     │
│ #2 | الخميس 9 يناير         [8/10] 🌙 🌟         │
│    | طور القمر مناسب                               │
│                                                     │
│ #3 | السبت 11 يناير         [7/10] 🌙 🌟         │
│    | وقت جيد للزراعة                               │
└─────────────────────────────────────────────────────┘
```

### 7. زر الإنشاء السريع | Quick Create Button

```
┌─────────────────────────────────────────────────────┐
│ [+ إنشاء مهمة في أفضل يوم (الثلاثاء 7 يناير)]     │
└─────────────────────────────────────────────────────┘
```

---

## البيانات الفلكية | Astronomical Data

### مصدر البيانات | Data Source

```
API Endpoint: /api/v1/astronomical/today
API Endpoint: /api/v1/astronomical/best-days?activity=زراعة&days=7
```

### الخطافات المستخدمة | Hooks Used

```typescript
import { useToday, useBestDays } from "@/features/astronomical";

const { data: todayData } = useToday();
const { data: bestDaysData } = useBestDays("زراعة", { days: 7 });
```

---

## الأنشطة المدعومة | Supported Activities

| Activity   | Arabic | Icon | Description              |
| ---------- | ------ | ---- | ------------------------ |
| Planting   | زراعة  | 🌱   | Planting seeds and crops |
| Irrigation | ري     | 💧   | Watering and irrigation  |
| Harvest    | حصاد   | ✂️   | Harvesting crops         |
| Pruning    | تقليم  | ✨   | Pruning and trimming     |

---

## التقييمات | Scoring System

### مقياس الملاءمة | Suitability Score

| Score | Arabic    | English      | Color    |
| ----- | --------- | ------------ | -------- |
| 9-10  | ممتاز     | Excellent    | 🟢 Green |
| 8     | جيد جداً  | Very Good    | 🟢 Green |
| 6-7   | جيد       | Good         | 🟡 Amber |
| 5     | متوسط     | Fair         | 🟡 Amber |
| 0-4   | غير مناسب | Not Suitable | 🔴 Red   |

---

## التخصيص | Customization

### تخصيص الألوان | Custom Colors

```tsx
// Customize in tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        "sahool-green": {
          50: "#f0fdf4",
          600: "#16a34a",
          900: "#14532d",
        },
      },
    },
  },
};
```

### تخصيص الأيقونات | Custom Icons

```tsx
import { CustomMoonIcon } from "@/components/icons";

// In component:
<CustomMoonIcon className="w-5 h-5" />;
```

---

## إمكانية الوصول | Accessibility

### مزايا إمكانية الوصول | Accessibility Features

- ✅ ARIA labels for all interactive elements
- ✅ Keyboard navigation support
- ✅ Screen reader friendly
- ✅ RTL (Right-to-Left) support for Arabic
- ✅ Color contrast compliance (WCAG 2.1 AA)
- ✅ Focus indicators

### الملاحة بلوحة المفاتيح | Keyboard Navigation

| Key               | Action                    |
| ----------------- | ------------------------- |
| `Tab`             | Navigate between elements |
| `Enter` / `Space` | Toggle expand/collapse    |
| `Escape`          | Close details             |

---

## الأداء | Performance

### التحسينات | Optimizations

- ✅ React.memo for performance
- ✅ useMemo for computed values
- ✅ Lazy loading for detailed view
- ✅ Optimized re-renders
- ✅ Cached API responses (30 min staleTime)

### حجم الحزمة | Bundle Size

```
Component size: ~8KB (gzipped)
Dependencies: lucide-react, @tanstack/react-query
```

---

## الاختبار | Testing

### مثال اختبار | Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { AstralFieldWidget } from './AstralFieldWidget';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

describe('AstralFieldWidget', () => {
  it('renders astronomical data', () => {
    const mockField = {
      id: '1',
      name: 'Test Field',
      nameAr: 'حقل تجريبي',
      area: 5,
    };

    render(
      <QueryClientProvider client={queryClient}>
        <AstralFieldWidget field={mockField} />
      </QueryClientProvider>
    );

    expect(screen.getByText('التقويم الفلكي اليمني')).toBeInTheDocument();
  });

  it('creates task on best day', async () => {
    const handleCreateTask = jest.fn();

    // Test implementation...
  });
});
```

---

## الأخطاء الشائعة | Common Issues

### 1. API URL غير محدد | API URL not set

```
Solution: Set NEXT_PUBLIC_API_URL in .env
NEXT_PUBLIC_API_URL=https://api.sahool.app
```

### 2. البيانات لا تظهر | Data not loading

```
Check:
- API is running
- Network connectivity
- Browser console for errors
```

### 3. الأيقونات لا تظهر | Icons not displaying

```
Solution: Install lucide-react
npm install lucide-react
```

---

## المراجع | References

- [Competitive Gap Analysis](../../../../docs/reports/COMPETITIVE_GAP_ANALYSIS_FIELD_VIEW.md)
- [Astronomical Calendar Service](../../../../docs/ASTRONOMICAL_CALENDAR_SERVICE.md)
- [Task Astronomical Integration](../../../../docs/reports/TASK_ASTRONOMICAL_INTEGRATION_RECOMMENDATIONS.md)

---

## الترخيص | License

Part of SAHOOL Unified Platform v15-IDP
© 2026 SAHOOL Team

---

## الدعم | Support

For issues or questions:

- 📧 Email: support@sahool.app
- 📝 GitHub Issues: [github.com/sahool/issues](https://github.com/sahool/issues)
- 📚 Documentation: [docs.sahool.app](https://docs.sahool.app)

---

**إعداد | Prepared by**: Claude AI Assistant
**التاريخ | Date**: 2026-01-05
**الإصدار | Version**: v15-IDP
