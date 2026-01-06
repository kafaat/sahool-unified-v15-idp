# AlertsPanel Component

**مكون لوحة تنبيهات الحقل**

A comprehensive React component for displaying and managing field alerts with real-time updates, filtering, and task creation capabilities.

## Features / المميزات

### Core Features
- ✅ **List of active alerts** - عرض قائمة التنبيهات النشطة
- ✅ **Four alert types** - أربعة أنواع من التنبيهات:
  - `ndvi_drop` - انخفاض NDVI
  - `weather_warning` - تحذير جوي
  - `soil_moisture` - رطوبة التربة
  - `task_overdue` - مهمة متأخرة
- ✅ **Severity levels** - مستويات الخطورة:
  - `critical` (red) - حرج (أحمر)
  - `warning` (yellow) - تحذير (أصفر)
  - `info` (blue) - معلومة (أزرق)
- ✅ **Expandable alert details** - تفاصيل قابلة للتوسيع
- ✅ **Action buttons** - أزرار الإجراءات:
  - Dismiss - إغلاق
  - Create Task - إنشاء مهمة
  - View Details - عرض التفاصيل
- ✅ **Pre-filled task creation** - إنشاء مهمة مع بيانات مملوءة مسبقاً
- ✅ **Real-time updates** - تحديثات فورية (WebSocket أو Polling)
- ✅ **Empty state** - حالة فارغة عند عدم وجود تنبيهات
- ✅ **Filter by type** - تصفية حسب النوع
- ✅ **Arabic labels** - تسميات عربية

## Installation / التثبيت

The component is already part of the fields feature. No additional installation required.

```bash
# Dependencies are already included in package.json
npm install
```

## Usage / الاستخدام

### Basic Usage

```tsx
import { AlertsPanel } from '@/features/fields/components/AlertsPanel';

function MyFieldPage() {
  const fieldId = 'field-123';
  const [alerts, setAlerts] = useState<FieldAlert[]>([]);

  const handleDismiss = async (alertId: string) => {
    // Call API to dismiss alert
    await api.dismissAlert(alertId);
    // Update local state
    setAlerts(prev => prev.map(a =>
      a.id === alertId ? { ...a, acknowledged: true } : a
    ));
  };

  const handleCreateTask = async (data: TaskFormData) => {
    // Call API to create task
    await api.createTask(data);
  };

  const handleViewDetails = (alert: FieldAlert) => {
    // Navigate to alert details or open modal
    router.push(`/alerts/${alert.id}`);
  };

  return (
    <AlertsPanel
      fieldId={fieldId}
      alerts={alerts}
      onDismiss={handleDismiss}
      onCreateTask={handleCreateTask}
      onViewDetails={handleViewDetails}
    />
  );
}
```

### With WebSocket (Real-time Updates)

```tsx
<AlertsPanel
  fieldId={fieldId}
  alerts={alerts}
  onDismiss={handleDismiss}
  onCreateTask={handleCreateTask}
  onViewDetails={handleViewDetails}
  enableWebSocket={true}
  wsUrl="ws://localhost:3001/field-alerts"
/>
```

### With Polling

```tsx
<AlertsPanel
  fieldId={fieldId}
  alerts={alerts}
  onDismiss={handleDismiss}
  onCreateTask={handleCreateTask}
  onViewDetails={handleViewDetails}
  enableWebSocket={false}
  pollingInterval={30000} // 30 seconds
/>
```

## Props / الخصائص

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `fieldId` | `string` | ✅ | - | معرّف الحقل - Field ID |
| `alerts` | `FieldAlert[]` | ❌ | `[]` | قائمة التنبيهات - List of alerts |
| `onDismiss` | `(alertId: string) => void \| Promise<void>` | ❌ | - | دالة إغلاق التنبيه - Dismiss handler |
| `onCreateTask` | `(data: TaskFormData) => void \| Promise<void>` | ❌ | - | دالة إنشاء مهمة - Task creation handler |
| `onViewDetails` | `(alert: FieldAlert) => void` | ❌ | - | دالة عرض التفاصيل - View details handler |
| `enableWebSocket` | `boolean` | ❌ | `false` | تفعيل WebSocket - Enable WebSocket |
| `wsUrl` | `string` | ❌ | - | عنوان WebSocket - WebSocket URL |
| `pollingInterval` | `number` | ❌ | `30000` | فترة التحديث (ms) - Polling interval |
| `className` | `string` | ❌ | `''` | CSS classes إضافية - Additional CSS classes |

## Types / الأنواع

### FieldAlert

```typescript
interface FieldAlert {
  id: string;                    // معرّف فريد
  fieldId: string;               // معرّف الحقل
  type: AlertType;               // نوع التنبيه
  severity: AlertSeverity;       // مستوى الخطورة
  title: string;                 // العنوان
  message: string;               // الرسالة
  data: Record<string, any>;     // بيانات إضافية
  createdAt: Date;               // تاريخ الإنشاء
  acknowledged: boolean;          // تم الاطلاع عليه
}
```

### AlertType

```typescript
type AlertType =
  | 'ndvi_drop'         // انخفاض NDVI
  | 'weather_warning'   // تحذير جوي
  | 'soil_moisture'     // رطوبة التربة
  | 'task_overdue';     // مهمة متأخرة
```

### AlertSeverity

```typescript
type AlertSeverity =
  | 'critical'  // حرج (أحمر)
  | 'warning'   // تحذير (أصفر)
  | 'info';     // معلومة (أزرق)
```

## Examples / أمثلة

See [AlertsPanel.example.tsx](./AlertsPanel.example.tsx) for complete working examples including:
- WebSocket integration
- Polling integration
- Minimal setup

## Component Structure / هيكل المكون

```
AlertsPanel/
├── Header (Statistics & Filters)
│   ├── Alert Count Badge
│   ├── Filter Buttons
│   └── Show/Hide Acknowledged Toggle
├── Alerts List
│   ├── AlertItem 1
│   │   ├── Icon & Title
│   │   ├── Severity Badge
│   │   ├── Message
│   │   ├── Metadata
│   │   └── Actions (Expandable)
│   │       ├── Alert Data
│   │       └── Action Buttons
│   ├── AlertItem 2
│   └── ...
└── Task Creation Modal
```

## Styling / التنسيق

The component uses Tailwind CSS classes and follows the Sahool design system:

- **Colors**: Uses theme colors (sahool-green, etc.)
- **Spacing**: Consistent padding and margins
- **Typography**: Arabic-first with English fallbacks
- **Responsive**: Mobile-friendly with breakpoints

## Real-time Updates / التحديثات الفورية

### WebSocket Events

The component listens for these WebSocket message types:

```typescript
// New alert
{
  type: 'field_alert',
  fieldId: 'field-123',
  data: FieldAlert
}

// Alert dismissed
{
  type: 'alert_dismissed',
  fieldId: 'field-123',
  alertId: 'alert-456'
}
```

### Polling

When WebSocket is disabled, the component can use polling to fetch updates periodically. Implement the fetching logic in the `useEffect` hook.

## Accessibility / إمكانية الوصول

- ✅ Semantic HTML structure
- ✅ ARIA labels and roles
- ✅ Keyboard navigation support
- ✅ Focus management
- ✅ Screen reader friendly

## Performance Considerations / الأداء

- **Memoization**: Uses `useMemo` for filtered alerts and statistics
- **Callbacks**: Uses `useCallback` to prevent unnecessary re-renders
- **Lazy Loading**: Expands details only when needed
- **Efficient Updates**: Only updates affected alerts

## Customization / التخصيص

### Custom Alert Types

Add new alert types by extending the configuration:

```typescript
const ALERT_TYPE_CONFIG = {
  // ... existing types
  custom_type: {
    icon: CustomIcon,
    label: 'Custom Type',
    labelAr: 'نوع مخصص',
    color: 'text-purple-600',
  },
};
```

### Custom Severity Levels

Extend severity configuration:

```typescript
const SEVERITY_CONFIG = {
  // ... existing levels
  urgent: {
    variant: 'danger',
    label: 'Urgent',
    labelAr: 'عاجل',
  },
};
```

## Testing / الاختبار

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AlertsPanel } from './AlertsPanel';

test('renders alerts correctly', () => {
  const alerts = [/* mock alerts */];
  render(<AlertsPanel fieldId="field-123" alerts={alerts} />);

  expect(screen.getByText('تنبيهات الحقل')).toBeInTheDocument();
});

test('dismisses alert on button click', async () => {
  const onDismiss = jest.fn();
  render(
    <AlertsPanel
      fieldId="field-123"
      alerts={alerts}
      onDismiss={onDismiss}
    />
  );

  fireEvent.click(screen.getByText('إغلاق'));
  expect(onDismiss).toHaveBeenCalled();
});
```

## Dependencies / التبعيات

- `react` (v19.0.0)
- `lucide-react` (icons)
- `@/components/ui/*` (UI components)
- `@/features/tasks/components/TaskForm`
- `@/hooks/useWebSocket`

## Browser Support / دعم المتصفحات

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers

## Known Issues / المشكلات المعروفة

None at this time.

## Future Enhancements / تحسينات مستقبلية

- [ ] Alert grouping by type
- [ ] Bulk actions (dismiss multiple)
- [ ] Export alerts to CSV/PDF
- [ ] Alert history view
- [ ] Custom notification sounds
- [ ] Priority sorting
- [ ] Search/filter by keywords

## License / الترخيص

Part of the Sahool Agricultural Platform - Proprietary

## Support / الدعم

For questions or issues, contact the development team.

---

**Created by**: Sahool Development Team
**Last Updated**: 2024-01-05
