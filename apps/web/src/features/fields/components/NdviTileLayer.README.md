# NDVI Tile Layer Component

## Overview / نظرة عامة

The `NdviTileLayer` component renders NDVI (Normalized Difference Vegetation Index) data as a colored tile overlay on MapLibre GL maps. It provides real-time visualization of vegetation health with historical data support.

مكون `NdviTileLayer` يعرض بيانات مؤشر الغطاء النباتي NDVI كطبقة ملونة على الخريطة مع دعم البيانات التاريخية.

## Features / المميزات

- ✅ **Real-time NDVI visualization** / تصور NDVI في الوقت الفعلي
- ✅ **Historical data support** / دعم البيانات التاريخية
- ✅ **Color gradient from red (low) to green (high)** / تدرج لوني من الأحمر (منخفض) إلى الأخضر (عالي)
- ✅ **Adjustable opacity** / تحكم في الشفافية
- ✅ **Loading states** / حالات التحميل
- ✅ **Error handling** / معالجة الأخطاء
- ✅ **Canvas-based rendering for performance** / عرض قائم على Canvas للأداء العالي
- ✅ **Automatic map bounds fitting** / تعديل حدود الخريطة تلقائياً

## Installation / التثبيت

The component is already included in the fields feature. Just import it:

```typescript
import { NdviTileLayer, NdviColorLegend } from '@/features/fields/components';
```

## Props / الخصائص

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `fieldId` | `string` | ✅ | - | معرف الحقل / Field ID |
| `map` | `RefObject<Map \| null>` | ✅ | - | مرجع خريطة MapLibre / MapLibre map reference |
| `date` | `Date` | ❌ | `undefined` | التاريخ للبيانات التاريخية / Date for historical data |
| `opacity` | `number` | ❌ | `0.7` | مستوى الشفافية (0-1) / Opacity level (0-1) |
| `visible` | `boolean` | ❌ | `true` | حالة الظهور / Visibility state |
| `onLoad` | `() => void` | ❌ | - | دالة تنفذ عند التحميل / Callback on load |
| `onError` | `(error: Error) => void` | ❌ | - | دالة تنفذ عند الخطأ / Callback on error |

## Basic Usage / الاستخدام الأساسي

```typescript
import { useRef, useEffect, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { NdviTileLayer, NdviColorLegend } from '@/features/fields/components';

function MyMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: { /* ... */ },
      center: [44.2, 15.0],
      zoom: 10,
    });

    map.current.on('load', () => setMapLoaded(true));

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  return (
    <div className="relative w-full h-screen">
      <div ref={mapContainer} className="w-full h-full" />

      {mapLoaded && (
        <>
          <NdviTileLayer
            fieldId="field-123"
            map={map}
          />
          <NdviColorLegend className="absolute bottom-4 right-4" />
        </>
      )}
    </div>
  );
}
```

## Advanced Usage / الاستخدام المتقدم

### With Date Selection / مع اختيار التاريخ

```typescript
const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);

<NdviTileLayer
  fieldId="field-123"
  date={selectedDate}
  map={map}
/>
```

### With Opacity Control / مع التحكم في الشفافية

```typescript
const [opacity, setOpacity] = useState(0.7);

<>
  <NdviTileLayer
    fieldId="field-123"
    opacity={opacity}
    map={map}
  />

  <input
    type="range"
    min="0"
    max="100"
    value={opacity * 100}
    onChange={(e) => setOpacity(Number(e.target.value) / 100)}
  />
</>
```

### With Visibility Toggle / مع تبديل الظهور

```typescript
const [visible, setVisible] = useState(true);

<>
  <NdviTileLayer
    fieldId="field-123"
    visible={visible}
    map={map}
  />

  <button onClick={() => setVisible(!visible)}>
    {visible ? 'إخفاء' : 'إظهار'}
  </button>
</>
```

### With Loading and Error Handling / مع معالجة التحميل والأخطاء

```typescript
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<Error | null>(null);

<>
  <NdviTileLayer
    fieldId="field-123"
    map={map}
    onLoad={() => {
      setIsLoading(false);
      console.log('NDVI loaded');
    }}
    onError={(err) => {
      setIsLoading(false);
      setError(err);
    }}
  />

  {isLoading && <NdviLoadingOverlay isLoading={true} />}
  {error && <div>Error: {error.message}</div>}
</>
```

## Helper Components / المكونات المساعدة

### NdviColorLegend

Displays a color legend showing NDVI value ranges.

```typescript
<NdviColorLegend className="absolute bottom-4 right-4" />
```

### NdviLoadingOverlay

Shows a loading overlay while NDVI data is being fetched.

```typescript
<NdviLoadingOverlay isLoading={isLoading} />
```

## Color Scale / مقياس الألوان

The component uses the following color scale for NDVI values:

| NDVI Value | Color | Description (AR) | Description (EN) |
|------------|-------|------------------|------------------|
| -1.0 to 0.0 | Brown to Red | تربة جافة / بدون غطاء | Bare soil / No vegetation |
| 0.0 to 0.2 | Red to Orange-Red | غطاء ضعيف جداً | Very poor vegetation |
| 0.2 to 0.4 | Orange to Yellow | غطاء ضعيف إلى متوسط | Poor to moderate vegetation |
| 0.4 to 0.6 | Yellow to Yellow-Green | غطاء متوسط إلى جيد | Moderate to good vegetation |
| 0.6 to 0.8 | Light Green to Green | غطاء جيد جداً إلى ممتاز | Very good to excellent vegetation |
| 0.8 to 1.0 | Green to Dark Green | غطاء كثيف جداً | Very dense vegetation |

## API Integration / التكامل مع API

The component automatically fetches NDVI data using the `useNDVIMap` hook from the NDVI feature:

```typescript
import { useNDVIMap } from '@/features/ndvi';

const { data, isLoading, error } = useNDVIMap(fieldId, dateString);
```

The expected API response format:

```typescript
interface NDVIMapData {
  fieldId: string;
  date: string;
  rasterUrl: string;  // URL template for tiles: https://example.com/{z}/{x}/{y}.png
  bounds: [[number, number], [number, number]];  // [[west, south], [east, north]]
  colorScale: {
    min: number;
    max: number;
    colors: string[];
  };
}
```

## Performance Considerations / اعتبارات الأداء

1. **Canvas Rendering**: The component uses MapLibre GL's built-in Canvas rendering for optimal performance
2. **Lazy Loading**: The layer is only added when the map is loaded and data is available
3. **Efficient Updates**: The component prevents redundant updates by comparing data references
4. **Memory Management**: Proper cleanup ensures no memory leaks when the component unmounts

## Best Practices / أفضل الممارسات

1. **Always provide a map ref**: Ensure the map reference is valid before rendering
2. **Handle errors gracefully**: Use the `onError` callback to show user-friendly error messages
3. **Show loading states**: Use `NdviLoadingOverlay` or custom loading indicators
4. **Add a legend**: Always include `NdviColorLegend` for user reference
5. **Control opacity**: Allow users to adjust opacity for better visualization
6. **Date validation**: Ensure selected dates have available NDVI data

## Troubleshooting / حل المشاكل

### Layer not appearing / الطبقة لا تظهر

- Check that `mapLoaded` is `true` before rendering the component
- Verify the `fieldId` is valid
- Check browser console for errors
- Ensure the API returns valid `rasterUrl` and `bounds`

### Data not loading / البيانات لا تحمل

- Check network requests in browser DevTools
- Verify API endpoint is accessible
- Check authentication token is valid
- Ensure the field has NDVI data for the selected date

### Performance issues / مشاكل في الأداء

- Reduce opacity to lighten rendering load
- Avoid rendering multiple NDVI layers simultaneously
- Use date range limits to prevent excessive API calls
- Ensure tile server can handle the request load

## Examples / أمثلة

See `NdviTileLayerExample.tsx` for complete working examples:

- Basic usage
- Date selection
- Opacity control
- Multiple fields
- Temporal comparison

## License

Part of the Sahool Agricultural Platform
