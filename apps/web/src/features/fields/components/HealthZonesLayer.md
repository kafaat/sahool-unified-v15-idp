# HealthZonesLayer Component

**مكون طبقة مناطق الصحة**

## Overview - نظرة عامة

A React component for displaying field health zones on a map using react-leaflet. The zones are colored based on NDVI (Normalized Difference Vegetation Index) values to visualize crop health status.

مكون React لعرض مناطق صحة الحقل على الخريطة باستخدام react-leaflet. يتم تلوين المناطق بناءً على قيم NDVI (مؤشر الاختلاف النباتي الطبيعي) لتصور حالة صحة المحاصيل.

## Features - الميزات

✅ **NDVI-based color coding** - ترميز الألوان بناءً على NDVI

- Green (>0.6): Excellent health
- Yellow (0.4-0.6): Moderate health
- Red (<0.4): Poor health

✅ **Interactive zones** - مناطق تفاعلية

- Click handling for zone details
- Selection highlighting
- Hover effects

✅ **Rich tooltips** - تلميحات غنية

- Zone name and NDVI value
- Health status in Arabic
- Area information

✅ **Comprehensive popups** - نوافذ منبثقة شاملة

- Full zone details
- Color-coded health status
- Action button for more details

✅ **Error handling** - معالجة الأخطاء

- Validation of zone boundaries
- NDVI value validation
- Development mode error display

✅ **RTL support** - دعم RTL

- Full Arabic language support
- Right-to-left layout

## Installation - التثبيت

The component is part of the fields feature and is already exported:

```typescript
import { HealthZonesLayer, type FieldZone } from "@/features/fields";
```

## Props - الخصائص

| Prop             | Type                        | Required | Default | Description                     |
| ---------------- | --------------------------- | -------- | ------- | ------------------------------- |
| `zones`          | `FieldZone[]`               | ✅ Yes   | -       | Array of field zones to display |
| `selectedZoneId` | `string`                    | No       | -       | ID of currently selected zone   |
| `onZoneClick`    | `(zone: FieldZone) => void` | No       | -       | Callback when zone is clicked   |
| `showLabels`     | `boolean`                   | No       | `true`  | Show zone labels on map         |
| `showTooltips`   | `boolean`                   | No       | `true`  | Show tooltips on hover          |

## FieldZone Type - نوع FieldZone

```typescript
interface FieldZone {
  id: string; // Unique identifier
  name: string; // Zone name (supports Arabic)
  boundary: [number, number][]; // Array of [lat, lng] coordinates
  ndviValue: number; // NDVI value (-1 to 1)
  healthStatus: "excellent" | "good" | "moderate" | "poor" | "critical";
  area: number; // Area in hectares
}
```

## Basic Usage - الاستخدام الأساسي

```tsx
"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { HealthZonesLayer, type FieldZone } from "@/features/fields";

// Dynamic imports to avoid SSR issues
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false },
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false },
);

export default function MyMap() {
  const [selectedZone, setSelectedZone] = useState<string>();

  const zones: FieldZone[] = [
    {
      id: "zone-1",
      name: "المنطقة الشمالية",
      boundary: [
        [15.5527, 48.5164],
        [15.5537, 48.5174],
        [15.5527, 48.5184],
      ],
      ndviValue: 0.75,
      healthStatus: "excellent",
      area: 2.5,
    },
    // ... more zones
  ];

  return (
    <MapContainer center={[15.5517, 48.5184]} zoom={14}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      <HealthZonesLayer
        zones={zones}
        selectedZoneId={selectedZone}
        onZoneClick={(zone) => setSelectedZone(zone.id)}
      />
    </MapContainer>
  );
}
```

## Advanced Usage - الاستخدام المتقدم

### With API Data - مع بيانات API

```tsx
import { useFieldNDVI } from "@/features/ndvi";
import { HealthZonesLayer } from "@/features/fields";

export default function FieldHealthMap({ fieldId }: { fieldId: string }) {
  const { data: ndviData, isLoading } = useFieldNDVI(fieldId);
  const [selectedZone, setSelectedZone] = useState<string>();

  if (isLoading) return <div>Loading...</div>;

  // Transform API data to FieldZone format
  const zones: FieldZone[] =
    ndviData?.zones.map((zone) => ({
      id: zone.id,
      name: zone.nameAr || zone.name,
      boundary: zone.coordinates,
      ndviValue: zone.ndvi,
      healthStatus: getHealthStatus(zone.ndvi),
      area: zone.areaHectares,
    })) || [];

  const handleZoneClick = (zone: FieldZone) => {
    setSelectedZone(zone.id);
    // Open details modal, navigate, etc.
    router.push(`/fields/${fieldId}/zones/${zone.id}`);
  };

  return (
    <MapContainer center={[15.5517, 48.5184]} zoom={14}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      <HealthZonesLayer
        zones={zones}
        selectedZoneId={selectedZone}
        onZoneClick={handleZoneClick}
        showLabels={true}
        showTooltips={true}
      />
    </MapContainer>
  );
}

function getHealthStatus(ndvi: number): FieldZone["healthStatus"] {
  if (ndvi > 0.7) return "excellent";
  if (ndvi > 0.6) return "good";
  if (ndvi > 0.4) return "moderate";
  if (ndvi > 0.2) return "poor";
  return "critical";
}
```

### With Custom Styling - مع تنسيق مخصص

```tsx
// Add custom CSS for tooltips
// أضف CSS مخصص للتلميحات

<style jsx global>{`
  .leaflet-tooltip.custom-tooltip {
    background: rgba(0, 0, 0, 0.9);
    border: none;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    padding: 8px 12px;
  }

  .leaflet-tooltip.custom-tooltip::before {
    border-top-color: rgba(0, 0, 0, 0.9);
  }
`}</style>
```

## Color Coding Reference - مرجع ترميز الألوان

| NDVI Range | Color               | Health Status | Arabic |
| ---------- | ------------------- | ------------- | ------ |
| > 0.6      | 🟢 Green (#22c55e)  | Excellent     | ممتازة |
| 0.4 - 0.6  | 🟡 Yellow (#eab308) | Moderate      | متوسطة |
| < 0.4      | 🔴 Red (#ef4444)    | Poor          | ضعيفة  |

## Validation Rules - قواعد التحقق

The component validates zones and logs errors in development mode:

1. **Zone ID**: Must be present and unique
2. **Boundary**: Must have at least 3 coordinate pairs
3. **Coordinates**: Must be valid [lat, lng] pairs
   - Latitude: -90 to 90
   - Longitude: -180 to 180
4. **NDVI Value**: Must be between -1 and 1

## Error Handling - معالجة الأخطاء

```tsx
// Invalid zones are silently skipped
// يتم تخطي المناطق غير الصالحة بصمت

// In development mode, errors are displayed
// في وضع التطوير، يتم عرض الأخطاء

const invalidZone = {
  id: "invalid",
  name: "Invalid Zone",
  boundary: [[200, 300]], // ❌ Invalid coordinates
  ndviValue: 2.5, // ❌ Out of range
  healthStatus: "good",
  area: 1.0,
};

// Component will show error in dev mode but won't crash
// سيعرض المكون الخطأ في وضع التطوير ولكن لن يتعطل
```

## Performance Considerations - اعتبارات الأداء

- ✅ Uses dynamic imports to avoid SSR issues
- ✅ Only re-renders when props change
- ✅ Efficient event handling with callbacks
- ✅ Validates data once on mount and when zones change
- ⚠️ For large numbers of zones (>100), consider:
  - Implementing zone clustering
  - Using canvas-based rendering
  - Implementing viewport-based filtering

## Browser Compatibility - توافق المتصفح

- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile browsers (iOS Safari, Chrome Android)
- ⚠️ Requires JavaScript enabled
- ⚠️ Requires modern ES6+ support

## Dependencies - الاعتماديات

- `react` (>= 18.0.0)
- `react-leaflet` (>= 4.2.1)
- `leaflet` (>= 1.9.4)
- `lucide-react` (for icons)
- `next` (for dynamic imports)

## Accessibility - إمكانية الوصول

- ✅ Keyboard navigation supported by Leaflet
- ✅ Screen reader friendly zone names
- ✅ High contrast colors for health status
- ✅ Focus indicators on interactive elements

## Example Files - ملفات الأمثلة

See the complete working example:

- `/apps/web/src/features/fields/examples/HealthZonesLayerExample.tsx`

## Troubleshooting - استكشاف الأخطاء

### Zones not displaying

- ✓ Check that coordinates are in [lat, lng] format
- ✓ Verify NDVI values are between -1 and 1
- ✓ Ensure at least 3 coordinate pairs per zone
- ✓ Check browser console for validation errors

### SSR Errors

- ✓ Use dynamic imports for all react-leaflet components
- ✓ Ensure 'use client' directive is present
- ✓ Check that isMounted state is properly handled

### Styling Issues

- ✓ Import Leaflet CSS in your layout
- ✓ Check z-index values for overlapping elements
- ✓ Verify Tailwind classes are not being purged

## Contributing - المساهمة

When modifying this component:

1. Maintain TypeScript type safety
2. Add Arabic translations for new text
3. Update this documentation
4. Add tests for new features
5. Follow the existing code style

## License - الترخيص

Part of the SAHOOL agricultural platform.

---

**Created by**: Claude Code
**Last Updated**: 2026-01-05
**Version**: 1.0.0
