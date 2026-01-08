# WeatherOverlay Component

**مكون تراكب الطقس**

A React component that displays real-time weather information as an overlay on field maps.

---

## Features / الميزات

### Core Features
- ✅ **Real-time Weather Data** - Current temperature, humidity, wind speed & direction
- ✅ **Weather Icons** - Dynamic icons based on conditions (sun, clouds, rain, snow, thunder)
- ✅ **Rainfall Forecast** - 24-hour precipitation forecast
- ✅ **Weather Alerts** - Severe weather warnings with color-coded badges
- ✅ **Collapsible Interface** - Compact and expanded views
- ✅ **Positionable** - Can be placed in any corner of the map
- ✅ **Bilingual** - Arabic and English labels throughout
- ✅ **Auto-refresh** - Periodic updates of weather data
- ✅ **Accessibility** - Full ARIA label support
- ✅ **Loading States** - Graceful loading and error handling

### الميزات الأساسية
- ✅ **بيانات الطقس الفورية** - درجة الحرارة، الرطوبة، سرعة واتجاه الرياح
- ✅ **أيقونات الطقس** - أيقونات ديناميكية بناءً على الحالة (شمس، غيوم، مطر، ثلج، رعد)
- ✅ **توقعات الأمطار** - توقعات هطول الأمطار لمدة 24 ساعة
- ✅ **تنبيهات الطقس** - تحذيرات الطقس الشديد مع شارات ملونة
- ✅ **واجهة قابلة للطي** - عروض مدمجة وموسعة
- ✅ **قابل للوضع** - يمكن وضعه في أي زاوية من الخريطة
- ✅ **ثنائي اللغة** - تسميات عربية وإنجليزية في جميع الأنحاء
- ✅ **تحديث تلقائي** - تحديثات دورية لبيانات الطقس
- ✅ **إمكانية الوصول** - دعم كامل لتسميات ARIA
- ✅ **حالات التحميل** - معالجة أنيقة للتحميل والأخطاء

---

## Installation / التثبيت

The component is already integrated into the SAHOOL fields feature. Import it like this:

```typescript
import { WeatherOverlay } from '@/features/fields/components/WeatherOverlay';
// or
import { WeatherOverlay } from '@/features/fields';
```

---

## API Reference

### Props

```typescript
interface WeatherOverlayProps {
  fieldId: string;
  position?: 'topright' | 'topleft' | 'bottomright' | 'bottomleft';
  expanded?: boolean;
}
```

#### `fieldId` (required)
- **Type:** `string`
- **Description:** The ID of the field for which to display weather data
- **Example:** `"field-123"`

The component will automatically fetch the field's centroid coordinates and use them to retrieve weather data.

#### `position` (optional)
- **Type:** `'topright' | 'topleft' | 'bottomright' | 'bottomleft'`
- **Default:** `'topright'`
- **Description:** Corner position of the overlay on the map
- **Examples:**
  - `'topright'` - Top right corner (default)
  - `'topleft'` - Top left corner
  - `'bottomright'` - Bottom right corner
  - `'bottomleft'` - Bottom left corner

#### `expanded` (optional)
- **Type:** `boolean`
- **Default:** `false`
- **Description:** Whether the overlay starts in expanded or compact mode
- **Example:** `true` - Starts fully expanded

---

## Usage Examples

### Basic Usage

```tsx
import { WeatherOverlay } from '@/features/fields';
import { MapContainer, TileLayer } from 'react-leaflet';

function FieldMap() {
  return (
    <div className="relative h-[600px] w-full">
      <MapContainer center={[15.3694, 44.191]} zoom={13}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <WeatherOverlay fieldId="field-123" />
      </MapContainer>
    </div>
  );
}
```

### Different Positions

```tsx
// Top left
<WeatherOverlay fieldId="field-123" position="topleft" />

// Bottom right
<WeatherOverlay fieldId="field-123" position="bottomright" />

// Bottom left
<WeatherOverlay fieldId="field-123" position="bottomleft" />
```

### Start Expanded

```tsx
<WeatherOverlay fieldId="field-123" expanded={true} />
```

### Full Example with Field Polygon

```tsx
import { WeatherOverlay } from '@/features/fields';
import { useField } from '@/features/fields/hooks/useField';
import { MapContainer, TileLayer, Polygon } from 'react-leaflet';

function FieldMapWithWeather({ fieldId }: { fieldId: string }) {
  const { data: field } = useField(fieldId);

  if (!field) return <div>Loading...</div>;

  const polygonPositions = field.polygon?.coordinates[0].map(
    ([lng, lat]) => [lat, lng] as [number, number]
  ) || [];

  const center = field.centroid?.coordinates
    ? [field.centroid.coordinates[1], field.centroid.coordinates[0]] as [number, number]
    : [15.3694, 44.191] as [number, number];

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer center={center} zoom={14}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {polygonPositions.length > 0 && (
          <Polygon
            positions={polygonPositions}
            pathOptions={{ color: '#10b981', fillOpacity: 0.2 }}
          />
        )}

        <WeatherOverlay fieldId={fieldId} position="topright" />
      </MapContainer>
    </div>
  );
}
```

---

## Component States

### Compact View (Default)
- Shows current temperature with icon
- Alert badge if severe weather warnings exist
- Click to expand

### Expanded View
- Full weather details:
  - Temperature with condition icon and text
  - Humidity percentage
  - Wind speed and direction (Arabic and English)
  - 24-hour rainfall forecast
  - Weather alerts with descriptions
  - Location information
- Click chevron to collapse

### Loading State
- Shows "جاري تحميل الطقس..." (Loading weather...)
- Animated pulse effect

### Error State
- Shows "بيانات الطقس غير متوفرة" (Weather data unavailable)
- Graceful degradation

---

## Weather Data

The component displays:

### Current Conditions
- **Temperature (°C)** - Current temperature in Celsius
- **Condition** - Weather condition (Clear, Cloudy, Rainy, etc.)
  - Arabic: صافي، غائم، ممطر، إلخ
- **Weather Icon** - Dynamic icon based on condition

### Metrics
- **Humidity (%)** - Relative humidity percentage
- **Wind** - Speed (km/h) and direction
  - Direction in Arabic: شمال، جنوب، شرق، غرب، إلخ
- **Rainfall Forecast (mm)** - Next 24 hours precipitation

### Alerts
- **Type** - Alert category
- **Severity** - Critical, Warning, Info
- **Title & Description** - In Arabic and English
- **Badge Color** - Red (critical), Yellow (warning), Blue (info)

---

## Weather Icons

The component uses different icons based on conditions:

| Condition | Icon | Color |
|-----------|------|-------|
| Clear/Sunny | ☀️ Sun | Yellow |
| Cloudy | ☁️ Cloud | Gray |
| Rainy | 🌧️ CloudRain | Blue |
| Drizzle | 🌦️ CloudDrizzle | Light Blue |
| Thunder | ⛈️ CloudLightning | Yellow |
| Snow | 🌨️ CloudSnow | Light Blue |

---

## Data Sources

### Weather API
The component fetches weather data from:
- **Current Weather:** `GET /api/v1/weather/current?lat={lat}&lon={lon}`
- **Forecast:** `GET /api/v1/weather/forecast?lat={lat}&lon={lon}&days=1`
- **Alerts:** `GET /api/v1/weather/alerts?lat={lat}&lon={lon}`

### Field Data
Field coordinates are fetched via:
- **Hook:** `useField(fieldId)`
- **Location:** Field centroid coordinates (`field.centroid.coordinates`)

---

## Styling

The component uses:
- **Gradient Background:** Blue to cyan gradient with 90% opacity
- **Backdrop Blur:** For glassmorphism effect
- **Shadow:** Large shadow for elevation
- **Transitions:** Smooth animations on expand/collapse
- **Responsive:** Adapts to different screen sizes
- **RTL Support:** Right-to-left layout for Arabic text

### CSS Classes
```css
/* Container */
.absolute .z-[1000] .max-w-[320px]

/* Background */
.bg-gradient-to-br .from-blue-500/90 .to-cyan-600/90
.backdrop-blur-md .rounded-lg .shadow-lg

/* Metrics */
.bg-white/10 .backdrop-blur-sm .rounded-lg .p-3
```

---

## Performance

### Optimization Features
- **React.memo** - Prevents unnecessary re-renders
- **useMemo** - Memoizes calculations and derived data
- **Query Caching** - React Query caches API responses
- **Auto-refresh** - Configurable intervals (10-15 minutes)
- **Conditional Fetching** - Only fetches when field coordinates exist

### Cache Configuration
- **Current Weather:** 5 min stale time, 10 min refetch interval
- **Forecast:** 30 min stale time
- **Alerts:** 10 min stale time, 15 min refetch interval

---

## Accessibility

### ARIA Support
- `aria-label` - Descriptive labels for all interactive elements
- `aria-expanded` - Indicates expanded/collapsed state
- `aria-live` - Announces dynamic content changes
- `aria-busy` - Indicates loading state
- `role="alert"` - For weather alerts
- `role="region"` - For content sections
- `role="status"` - For status updates

### Keyboard Navigation
- Fully keyboard accessible
- Tab navigation support
- Enter/Space to toggle expansion

---

## Browser Support

- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ✅ Requires JavaScript enabled
- ✅ Requires CSS Grid and Flexbox support

---

## Dependencies

### Required
- `react` >= 18.0.0
- `@tanstack/react-query` - Data fetching and caching
- `lucide-react` - Icon library
- `clsx` - Utility for conditional classes

### Internal Dependencies
- `@/features/fields/hooks/useField` - Field data hook
- `@/features/weather/hooks/useWeather` - Weather data hooks
- `@/features/weather/types` - Weather type definitions
- `@/components/ui/badge` - Badge component

---

## Troubleshooting

### Weather data not showing
1. Check that the field has valid centroid coordinates
2. Verify API endpoints are accessible
3. Check console for API errors
4. Ensure `NEXT_PUBLIC_API_URL` is set

### Position not correct
- Make sure map container has `position: relative`
- Check z-index conflicts with other overlays
- Verify CSS is loaded correctly

### Icons not displaying
- Ensure `lucide-react` is installed
- Check that icon imports are correct
- Verify no CSS conflicts

---

## Future Enhancements

Potential improvements:
- [ ] Historical weather data trends
- [ ] Multiple day forecasts
- [ ] Hourly forecast graph
- [ ] Weather radar integration
- [ ] Custom threshold alerts
- [ ] Export weather data
- [ ] Comparison with other fields
- [ ] Weather-based recommendations

---

## License

Part of the SAHOOL agricultural management platform.

---

## Support

For issues or questions:
1. Check the example file: `WeatherOverlay.example.tsx`
2. Review the component source: `WeatherOverlay.tsx`
3. Contact the development team

---

**Created:** 2026-01-05
**Version:** 1.0.0
**Author:** SAHOOL Development Team
