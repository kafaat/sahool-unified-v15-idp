# TaskMarkers Component

مكون علامات المهام على الخريطة

## Overview / نظرة عامة

The `TaskMarkers` component displays tasks as interactive markers on a Leaflet map. It provides visual indicators for task types, priorities, and statuses, with support for clustering and detailed popups.

يعرض مكون `TaskMarkers` المهام كعلامات تفاعلية على خريطة Leaflet. يوفر مؤشرات مرئية لأنواع المهام والأولويات والحالات، مع دعم التجميع والنوافذ المنبثقة التفصيلية.

## Features / الميزات

- ✅ Different icons for different task types (irrigation, inspection, fertilization, etc.)
  - أيقونات مختلفة لأنواع المهام المختلفة (ري، فحص، تسميد، إلخ)
- ✅ Color coding by priority (red=urgent/high, yellow=medium, green=low)
  - ترميز لوني حسب الأولوية (أحمر=عاجل/عالي، أصفر=متوسط، أخضر=منخفض)
- ✅ Popup on click showing detailed task information
  - نافذة منبثقة عند النقر تظهر معلومات مفصلة عن المهمة
- ✅ Support for task clustering when zoomed out (optional)
  - دعم تجميع المهام عند التصغير (اختياري)
- ✅ Navigation to task details page on button click
  - الانتقال إلى صفحة تفاصيل المهمة عند النقر على الزر
- ✅ Task count badge in cluster markers
  - شارة عدد المهام في علامات التجميع
- ✅ Overdue task highlighting
  - تمييز المهام المتأخرة
- ✅ Arabic language support
  - دعم اللغة العربية

## Installation / التثبيت

### Required Dependencies / المكتبات المطلوبة

The component requires the following packages (already installed in the project):

```bash
npm install leaflet react-leaflet @types/leaflet
```

### Optional: Marker Clustering / اختياري: تجميع العلامات

For marker clustering support, you need to install:

```bash
npm install leaflet.markercluster
npm install --save-dev @types/leaflet.markercluster
```

Then, add the clustering CSS to your layout:

```tsx
// app/layout.tsx
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"
/>
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"
/>
```

And include the clustering script:

```tsx
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
```

## Usage / الاستخدام

### Basic Usage / الاستخدام الأساسي

```tsx
import { useRef, useEffect } from 'react';
import { TaskMarkers } from '@/features/fields/components/TaskMarkers';
import { useTasks } from '@/features/tasks/hooks/useTasks';
import { useFields } from '@/features/fields/hooks/useFields';

export function TaskMap() {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { data: tasks = [] } = useTasks();
  const { data: fields = [] } = useFields();

  useEffect(() => {
    if (typeof window === 'undefined' || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) return;

    // Initialize map
    if (!mapRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current).setView([15.5527, 48.5164], 6);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  return (
    <div>
      <div ref={mapContainerRef} className="h-96 w-full" />
      <TaskMarkers tasks={tasks} fields={fields} mapRef={mapRef} />
    </div>
  );
}
```

### Advanced Usage / الاستخدام المتقدم

#### Without Clustering / بدون تجميع

```tsx
<TaskMarkers
  tasks={tasks}
  fields={fields}
  mapRef={mapRef}
  enableClustering={false}
/>
```

#### With Custom Click Handler / مع معالج نقر مخصص

```tsx
<TaskMarkers
  tasks={tasks}
  fields={fields}
  mapRef={mapRef}
  onTaskClick={(taskId) => {
    // Custom logic
    console.log('Task clicked:', taskId);
    // Open modal, sidebar, etc.
  }}
/>
```

#### Filtered Tasks / مهام مصفاة

```tsx
const { data: allTasks = [] } = useTasks();
const urgentTasks = allTasks.filter(
  (task) => task.priority === 'urgent' || task.priority === 'high'
);

<TaskMarkers tasks={urgentTasks} fields={fields} mapRef={mapRef} />;
```

## Props / الخصائص

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tasks` | `Task[]` | Yes | - | Array of tasks to display on the map |
| `fields` | `Field[]` | Yes | - | Array of fields (used to get task locations) |
| `mapRef` | `React.RefObject<any>` | Yes | - | Reference to the Leaflet map instance |
| `enableClustering` | `boolean` | No | `true` | Enable/disable marker clustering |
| `onTaskClick` | `(taskId: string) => void` | No | Navigate to `/dashboard/tasks/{id}` | Custom handler for task marker clicks |

## Task Types / أنواع المهام

The component supports the following task types with corresponding icons:

| Type | Icon | Arabic Label |
|------|------|--------------|
| `irrigation` | 💧 | ري |
| `inspection` | 🔍 | فحص |
| `fertilization` | 🌱 | تسميد |
| `planting` | 🌾 | زراعة |
| `harvesting` | 🌽 | حصاد |
| `pest_control` | 🐛 | مكافحة آفات |
| `maintenance` | 🔧 | صيانة |
| `other` | 📋 | أخرى |

## Priority Colors / ألوان الأولوية

| Priority | Color | Hex |
|----------|-------|-----|
| `urgent` | Red | `#dc2626` |
| `high` | Red | `#ef4444` |
| `medium` | Yellow | `#eab308` |
| `low` | Green | `#22c55e` |

## Status Labels / تسميات الحالة

| Status | Arabic Label |
|--------|--------------|
| `open` | مفتوح |
| `pending` | معلق |
| `in_progress` | قيد التنفيذ |
| `completed` | مكتمل |
| `cancelled` | ملغي |

## Popup Content / محتوى النافذة المنبثقة

The task popup displays:
- Task title (Arabic and English)
- Task type with icon
- Task status
- Priority badge with color coding
- Due date (with overdue warning if applicable)
- Field name
- Task description (if available)
- "View Task Details" button

## Clustering Behavior / سلوك التجميع

When clustering is enabled and multiple tasks are at nearby locations:
- Markers are grouped into clusters
- Cluster color represents the highest priority task in the group
- Cluster badge shows the count of tasks
- Clicking a cluster zooms in or spiderfies the markers
- Max cluster radius is 50 pixels

## Browser Compatibility / التوافق مع المتصفحات

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Considerations / اعتبارات الأداء

- The component efficiently handles up to 1000+ task markers
- Clustering significantly improves performance with large datasets
- Markers are cleaned up on component unmount
- Event listeners are properly removed to prevent memory leaks

## Troubleshooting / استكشاف الأخطاء

### Leaflet not loaded

**Problem:** Console warning "Leaflet is not loaded"

**Solution:** Make sure Leaflet is loaded via CDN in your layout:

```tsx
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

### Tasks not appearing

**Problem:** No markers on the map

**Checklist:**
1. Verify tasks have `field_id` property
2. Verify fields have `centroid` property with valid coordinates
3. Check that map is properly initialized before TaskMarkers mounts
4. Inspect browser console for errors

### Clustering not working

**Problem:** Markers not clustering

**Solutions:**
1. Install `leaflet.markercluster` package
2. Include clustering CSS and JS in layout
3. Verify `enableClustering={true}` (or omit for default behavior)

## Examples / الأمثلة

See `TaskMarkers.example.tsx` for comprehensive usage examples including:
- Basic map with all tasks
- Map without clustering
- Filtered high-priority tasks
- Custom click handlers
- Field-specific task views

## Related Components / المكونات ذات الصلة

- `FieldMap` - Base field map component
- `EquipmentMap` - Equipment location map
- `SensorMap` - Sensor location map
- `TaskCard` - Individual task display card
- `TasksList` - List view of tasks

## Contributing / المساهمة

When extending this component, please:
1. Maintain RTL (right-to-left) support for Arabic
2. Follow existing color coding conventions
3. Test with large datasets (100+ tasks)
4. Update this documentation
5. Add unit tests for new features

## License / الترخيص

Part of the SAHOOL Agricultural Platform
© 2025 SAHOOL - All Rights Reserved
