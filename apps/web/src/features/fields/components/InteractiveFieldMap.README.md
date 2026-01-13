# InteractiveFieldMap Component

## خريطة الحقول التفاعلية

A comprehensive, feature-rich interactive map component for displaying agricultural fields with support for multiple data layers and user interactions.

مكون خريطة تفاعلي شامل وغني بالمميزات لعرض الحقول الزراعية مع دعم طبقات بيانات متعددة والتفاعلات المستخدمة.

---

## Features / المميزات

### ✅ Core Features / المميزات الأساسية

- **Field Boundary Display** / **عرض حدود الحقول**: Display field polygons with customizable styling
- **NDVI Layer Overlay** / **طبقة NDVI**: Color-coded NDVI visualization with automatic color mapping
- **Health Zones** / **مناطق الصحة**: Circular zones showing field health status
- **Task Markers** / **علامات المهام**: Interactive markers for field tasks with priority-based colors
- **Weather Overlay** / **طبقة الطقس**: Real-time weather information display
- **Layer Controls** / **التحكم في الطبقات**: Toggle individual layers on/off
- **Zoom Controls** / **أدوات التكبير**: Standard map zoom functionality
- **Interactive Popups** / **النوافذ المنبثقة التفاعلية**: Detailed information on click
- **Event Handlers** / **معالجات الأحداث**: Callbacks for user interactions
- **RTL Support** / **دعم RTL**: Full Arabic language support

### 🎨 Styling / التنسيق

- Built with **Tailwind CSS** / مبني باستخدام Tailwind CSS
- Responsive design / تصميم متجاوب
- Custom markers and icons / علامات وأيقونات مخصصة
- Smooth transitions and animations / انتقالات ورسوم متحركة سلسة

### 🔧 Technical / تقني

- **TypeScript** with full type safety / TypeScript مع أمان كامل للأنواع
- **React Leaflet 4.2.1** integration / تكامل مع React Leaflet
- **Functional Component** with hooks / مكون وظيفي مع الخطافات
- Optimized with `useMemo` and `useCallback` / محسّن باستخدام useMemo و useCallback
- Clean code architecture / معمارية كود نظيفة

---

## Installation / التثبيت

The component is already part of the fields feature module. Dependencies are:

المكون جزء بالفعل من وحدة ميزة الحقول. التبعيات هي:

```json
{
  "leaflet": "1.9.4",
  "react-leaflet": "4.2.1",
  "@types/leaflet": "1.9.21",
  "lucide-react": "0.468.0"
}
```

---

## Usage / الاستخدام

### Basic Usage / الاستخدام الأساسي

```tsx
import { InteractiveFieldMap } from "@/features/fields/components";

function MyComponent() {
  const field = {
    id: "field-1",
    name: "My Field",
    nameAr: "حقلي",
    area: 5.0,
    polygon: {
      type: "Polygon",
      coordinates: [
        [
          [44.2, 15.3],
          [44.21, 15.3],
          [44.21, 15.31],
          [44.2, 15.31],
          [44.2, 15.3],
        ],
      ],
    },
    ndviValue: 0.65,
    healthScore: 85,
    status: "active",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  return (
    <InteractiveFieldMap
      field={field}
      height="600px"
      onFieldClick={(field) => console.log("Clicked:", field)}
    />
  );
}
```

### Advanced Usage with All Features / الاستخدام المتقدم مع جميع المميزات

```tsx
import { InteractiveFieldMap } from "@/features/fields/components";
import type { HealthZone, MapTask } from "@/features/fields/components";

function AdvancedMap() {
  const fields = [
    /* array of fields */
  ];
  const tasks: MapTask[] = [
    /* array of tasks with location */
  ];
  const healthZones: HealthZone[] = [
    /* array of health zones */
  ];
  const weather = {
    /* weather data */
  };

  return (
    <InteractiveFieldMap
      fields={fields}
      tasks={tasks}
      healthZones={healthZones}
      weather={weather}
      height="800px"
      zoom={15}
      center={[15.5527, 48.5164]}
      enableLayerControl={true}
      onFieldClick={(field) => handleFieldClick(field)}
      onTaskClick={(task) => handleTaskClick(task)}
      onHealthZoneClick={(zone) => handleZoneClick(zone)}
      onMapClick={(lat, lng) => console.log("Map clicked at:", lat, lng)}
    />
  );
}
```

---

## Props / الخصائص

### InteractiveFieldMapProps

| Prop                 | Type                                 | Required | Default         | Description                                |
| -------------------- | ------------------------------------ | -------- | --------------- | ------------------------------------------ |
| `fields`             | `Field[]`                            | No       | `[]`            | Array of fields to display                 |
| `field`              | `Field`                              | No       | -               | Single field (alternative to fields array) |
| `tasks`              | `MapTask[]`                          | No       | `[]`            | Tasks with location data                   |
| `healthZones`        | `HealthZone[]`                       | No       | `[]`            | Health zones to visualize                  |
| `weather`            | `WeatherData`                        | No       | -               | Weather data for overlay                   |
| `height`             | `string`                             | No       | `'600px'`       | Map container height                       |
| `center`             | `LatLngTuple`                        | No       | Auto-calculated | Initial map center [lat, lng]              |
| `zoom`               | `number`                             | No       | `13`            | Initial zoom level                         |
| `enableLayerControl` | `boolean`                            | No       | `true`          | Show layer control panel                   |
| `onFieldClick`       | `(field: Field) => void`             | No       | -               | Callback when field is clicked             |
| `onTaskClick`        | `(task: MapTask) => void`            | No       | -               | Callback when task is clicked              |
| `onHealthZoneClick`  | `(zone: HealthZone) => void`         | No       | -               | Callback when zone is clicked              |
| `onMapClick`         | `(lat: number, lng: number) => void` | No       | -               | Callback when map is clicked               |
| `className`          | `string`                             | No       | `''`            | Additional CSS classes                     |

---

## Type Definitions / تعريفات الأنواع

### HealthZone

```typescript
interface HealthZone {
  id: string;
  fieldId: string;
  center: GeoPoint; // Center coordinates / الإحداثيات المركزية
  radius: number; // Radius in meters / نصف القطر بالأمتار
  healthScore: number; // 0-100
  ndviValue?: number; // Optional NDVI value
  status: "healthy" | "moderate" | "stressed" | "critical";
  color: string; // Hex color code
}
```

### MapTask

```typescript
interface MapTask extends Task {
  location?: GeoPoint; // Task location on map / موقع المهمة على الخريطة
}
```

### LayerConfig

```typescript
interface LayerConfig {
  fields: boolean; // Show field boundaries
  ndvi: boolean; // Show NDVI coloring
  healthZones: boolean; // Show health zones
  tasks: boolean; // Show task markers
  weather: boolean; // Show weather overlay
}
```

---

## Features in Detail / تفاصيل المميزات

### 1. Field Boundaries / حدود الحقول

Fields are displayed as polygons on the map. The color is determined by:

- NDVI value (if NDVI layer is active)
- Default blue color (if NDVI is inactive)

تُعرض الحقول كمضلعات على الخريطة. يتم تحديد اللون بواسطة:

- قيمة NDVI (إذا كانت طبقة NDVI نشطة)
- اللون الأزرق الافتراضي (إذا كان NDVI غير نشط)

**Click Behavior**: Clicking a field shows a popup with details and triggers `onFieldClick` callback.

### 2. NDVI Layer / طبقة NDVI

NDVI (Normalized Difference Vegetation Index) values are color-coded:

قيم NDVI (مؤشر الاختلاف الطبيعي للنباتات) مرمزة بالألوان:

- **> 0.6**: 🟢 Healthy Green / أخضر صحي
- **0.4 - 0.6**: 🟢 Light Green / أخضر فاتح
- **0.2 - 0.4**: 🟡 Yellow / أصفر
- **0.0 - 0.2**: 🟠 Orange / برتقالي
- **< 0.0**: 🔴 Red / أحمر

A legend is automatically displayed at the bottom-left when NDVI layer is active.

### 3. Health Zones / مناطق الصحة

Circular zones representing areas with specific health characteristics:

- Radius in meters
- Color-coded by health score or custom color
- Clickable with popup details

مناطق دائرية تمثل مناطق ذات خصائص صحية محددة:

- نصف القطر بالأمتار
- مرمزة بالألوان حسب درجة الصحة أو لون مخصص
- قابلة للنقر مع تفاصيل منبثقة

### 4. Task Markers / علامات المهام

Tasks are displayed as circular markers with:

- **Color** based on priority and status
- **Icon**: ✓ for completed, ! for others
- **Priority colors**:
  - Urgent: 🔴 Red
  - High: 🟠 Orange
  - Medium: 🟡 Yellow
  - Low: 🔵 Blue

### 5. Weather Overlay / طبقة الطقس

Displays current weather conditions in a panel:

- Temperature / درجة الحرارة
- Humidity / الرطوبة
- Wind speed / سرعة الرياح
- Condition description / وصف الحالة

### 6. Layer Control / التحكم في الطبقات

Interactive panel to toggle each layer:

- Click the layers icon (top-left)
- Check/uncheck individual layers
- Changes apply immediately

لوحة تفاعلية لتبديل كل طبقة:

- انقر على أيقونة الطبقات (أعلى اليسار)
- حدد/ألغِ تحديد الطبقات الفردية
- تُطبق التغييرات فوراً

---

## Color Schemes / أنظمة الألوان

### NDVI Colors

```typescript
const getNDVIColor = (ndvi: number): string => {
  if (ndvi >= 0.6) return "#00ff00"; // Healthy
  if (ndvi >= 0.4) return "#90ee90"; // Good
  if (ndvi >= 0.2) return "#ffff00"; // Moderate
  if (ndvi >= 0.0) return "#ffa500"; // Poor
  return "#ff0000"; // Critical
};
```

### Health Score Colors

```typescript
const getHealthColor = (score: number): string => {
  if (score >= 80) return "#22c55e"; // Green
  if (score >= 60) return "#eab308"; // Yellow
  if (score >= 40) return "#f97316"; // Orange
  return "#ef4444"; // Red
};
```

### Task Priority Colors

```typescript
const getTaskColor = (priority: Priority, status: TaskStatus): string => {
  if (status === "completed") return "#22c55e";
  if (status === "cancelled") return "#6b7280";

  switch (priority) {
    case "urgent":
      return "#dc2626";
    case "high":
      return "#f97316";
    case "medium":
      return "#eab308";
    case "low":
      return "#3b82f6";
  }
};
```

---

## Event Handlers / معالجات الأحداث

### onFieldClick

```typescript
onFieldClick={(field: Field) => {
  // Handle field selection
  setSelectedField(field);
  // Show field details
  showFieldDetails(field.id);
  // Navigate to field page
  router.push(`/fields/${field.id}`);
}}
```

### onTaskClick

```typescript
onTaskClick={(task: MapTask) => {
  // Open task modal
  openTaskModal(task);
  // Update task status
  updateTaskStatus(task.id);
}}
```

### onHealthZoneClick

```typescript
onHealthZoneClick={(zone: HealthZone) => {
  // Show zone analysis
  showZoneAnalysis(zone);
  // Trigger zone actions
  handleZoneAction(zone.status);
}}
```

### onMapClick

```typescript
onMapClick={(lat: number, lng: number) => {
  // Create new task at location
  createTaskAtLocation(lat, lng);
  // Add measurement point
  addMeasurementPoint({ lat, lng });
}}
```

---

## Best Practices / أفضل الممارسات

### 1. Performance / الأداء

```typescript
// ✅ DO: Memoize data
const processedFields = useMemo(() => fields.map(processField), [fields]);

// ❌ DON'T: Process data on every render
const processedFields = fields.map(processField);
```

### 2. Event Handlers / معالجات الأحداث

```typescript
// ✅ DO: Use useCallback for handlers
const handleFieldClick = useCallback((field: Field) => {
  console.log(field);
}, []);

// ❌ DON'T: Define inline functions
onFieldClick={(field) => console.log(field)}
```

### 3. Data Validation / التحقق من البيانات

```typescript
// ✅ DO: Validate polygon data
const validFields = fields.filter(f =>
  f.polygon &&
  f.polygon.coordinates.length > 0
);

// Then use in map
<InteractiveFieldMap fields={validFields} />
```

---

## Accessibility / إمكانية الوصول

- Semantic HTML structure
- ARIA labels for controls
- Keyboard navigation support
- Screen reader friendly
- RTL support for Arabic

---

## Browser Support / دعم المتصفحات

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive

---

## Troubleshooting / استكشاف الأخطاء

### Map doesn't appear

```typescript
// Ensure container has height
<div style={{ height: '600px' }}>
  <InteractiveFieldMap ... />
</div>
```

### Markers not showing

```typescript
// Ensure tasks have location property
const tasks = tasks.map((task) => ({
  ...task,
  location: {
    type: "Point",
    coordinates: [lng, lat], // Note: [lng, lat] order
  },
}));
```

### NDVI colors not updating

```typescript
// Ensure ndviValue is set on fields
const fields = fields.map((f) => ({
  ...f,
  ndviValue: calculateNDVI(f),
}));
```

---

## Related Components / المكونات ذات الصلة

- `FieldMap` - Simple field map (legacy)
- `NdviTileLayer` - NDVI tile layer component
- `WeatherOverlay` - Weather overlay component
- `HealthZonesLayer` - Health zones layer component

---

## License / الترخيص

Part of the SAHOOL Agricultural Platform
© 2024 SAHOOL. All rights reserved.

---

## Support / الدعم

For questions or issues, contact the development team or refer to the main project documentation.

للأسئلة أو المشاكل، اتصل بفريق التطوير أو راجع وثائق المشروع الرئيسية.
