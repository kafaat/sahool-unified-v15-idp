# LayerControl Component

**مكون التحكم في طبقات الخريطة**

A comprehensive, accessible map layer control component for managing multiple map overlays with NDVI-specific controls.

## Features / المميزات

### Core Features

- **5 Layer Toggles**: Control visibility of all map layers
  - NDVI satellite imagery (صور الأقمار الصناعية NDVI)
  - Health zones (مناطق الصحة)
  - Task markers (علامات المهام)
  - Weather overlay (طبقة الطقس)
  - Irrigation zones (مناطق الري)

- **NDVI Controls**:
  - Opacity slider (0-100%) for fine-tuned transparency control
  - Historical date picker for viewing past NDVI data
  - Visual feedback with real-time percentage display

- **Interactive Legend**:
  - Color gradient visualization
  - Detailed NDVI value descriptions in Arabic and English
  - Toggleable display to save screen space

- **Collapsible Panel**:
  - Expand/collapse functionality to maximize map viewing area
  - Smooth animations and transitions
  - Remembers state in localStorage

- **Accessibility**:
  - Full keyboard navigation support
  - ARIA labels and roles for screen readers
  - Focus indicators for all interactive elements
  - Semantic HTML structure

- **Persistence**:
  - Automatic saving to localStorage
  - Preferences restored on page reload
  - Configurable storage keys for multiple instances

- **Bilingual Support**:
  - All labels in Arabic and English
  - RTL-friendly design
  - Culturally appropriate color coding

## Installation / التثبيت

The component is located at:
```
/apps/web/src/features/fields/components/LayerControl.tsx
```

Import the component:
```typescript
import { LayerControl, useLayerControl } from '@/features/fields/components/LayerControl';
import type { LayerSettings, NDVISettings } from '@/features/fields/components/LayerControl';
```

## Usage / الاستخدام

### Basic Usage

```tsx
import { LayerControl } from '@/features/fields/components/LayerControl';

function MyMap() {
  const handleLayersChange = (layers) => {
    console.log('Active layers:', layers);
    // Update your map layers here
  };

  const handleNDVIChange = (settings) => {
    console.log('NDVI settings:', settings);
    // Update NDVI layer opacity and date
  };

  return (
    <div className="relative h-screen">
      {/* Your map component */}
      <MapContainer>
        {/* Map layers */}
      </MapContainer>

      {/* Layer control */}
      <LayerControl
        position="top-right"
        onLayersChange={handleLayersChange}
        onNDVIChange={handleNDVIChange}
        persistPreferences={true}
      />
    </div>
  );
}
```

### With Initial Settings

```tsx
<LayerControl
  position="top-left"
  initialLayers={{
    ndvi: true,
    healthZones: true,
    taskMarkers: false,
    weatherOverlay: true,
    irrigationZones: false,
  }}
  initialNDVI={{
    opacity: 0.5,
    historicalDate: new Date('2025-01-01'),
  }}
  onLayersChange={handleLayersChange}
  onNDVIChange={handleNDVIChange}
/>
```

### Using the Hook

```tsx
import { useLayerControl } from '@/features/fields/components/LayerControl';

function MyComponent() {
  const [state, controls] = useLayerControl({
    layers: {
      ndvi: true,
      healthZones: true,
      taskMarkers: true,
      weatherOverlay: false,
      irrigationZones: true,
    },
    ndvi: {
      opacity: 0.7,
      historicalDate: null,
    },
  });

  // Programmatically control layers
  const handleToggleNDVI = () => {
    controls.toggleLayer('ndvi');
  };

  const handleSetOpacity = (value: number) => {
    controls.updateNDVIOpacity(value);
  };

  return (
    <div>
      {/* Your UI */}
      <button onClick={handleToggleNDVI}>Toggle NDVI</button>
      <input
        type="range"
        min="0"
        max="1"
        step="0.1"
        value={state.ndvi.opacity}
        onChange={(e) => handleSetOpacity(parseFloat(e.target.value))}
      />
    </div>
  );
}
```

## API Reference

### LayerControl Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `initialLayers` | `Partial<LayerSettings>` | `DEFAULT_LAYERS` | Initial layer visibility settings |
| `initialNDVI` | `Partial<NDVISettings>` | `DEFAULT_NDVI` | Initial NDVI configuration |
| `onLayersChange` | `(layers: LayerSettings) => void` | - | Callback when any layer visibility changes |
| `onNDVIChange` | `(settings: NDVISettings) => void` | - | Callback when NDVI settings change |
| `position` | `'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right'` | `'top-right'` | Position on the map |
| `className` | `string` | `''` | Additional CSS classes |
| `persistPreferences` | `boolean` | `true` | Enable/disable localStorage persistence |
| `storageKey` | `string` | `'sahool-map-layers'` | localStorage key prefix |

### LayerSettings Interface

```typescript
interface LayerSettings {
  ndvi: boolean;           // NDVI satellite imagery
  healthZones: boolean;    // Health zones
  taskMarkers: boolean;    // Task markers
  weatherOverlay: boolean; // Weather overlay
  irrigationZones: boolean; // Irrigation zones
}
```

### NDVISettings Interface

```typescript
interface NDVISettings {
  opacity: number;              // 0-1 range
  historicalDate: Date | null;  // Date for historical data
}
```

### useLayerControl Hook

Returns: `[state, controls]`

**State:**
```typescript
{
  layers: LayerSettings;
  ndvi: NDVISettings;
}
```

**Controls:**
```typescript
{
  toggleLayer: (layer: keyof LayerSettings) => void;
  updateNDVIOpacity: (opacity: number) => void;
  updateNDVIDate: (date: Date | null) => void;
  resetToDefaults: () => void;
}
```

## Component Architecture / البنية المعمارية

### Internal Components

1. **Switch Component**
   - Custom toggle switch for layer visibility
   - Keyboard accessible (Space/Enter keys)
   - Visual state indicators
   - ARIA attributes for accessibility

2. **Slider Component**
   - Range input for opacity control
   - Smooth transitions and hover effects
   - Real-time value display
   - Keyboard navigation support

3. **DatePicker Component**
   - Native HTML5 date input
   - Max date validation (cannot select future dates)
   - Clear button functionality
   - Localized date display

### Color Legend

The component includes a comprehensive NDVI color scale:

| Value | Color | Arabic | English |
|-------|-------|--------|---------|
| 1.0 | #006600 | كثيف جداً | Very Dense |
| 0.8 | #00CC00 | كثيف | Dense |
| 0.7 | #00FF00 | ممتاز | Excellent |
| 0.6 | #55FF00 | جيد جداً | Very Good |
| 0.5 | #AAFF00 | جيد | Good |
| 0.4 | #FFFF00 | متوسط | Moderate |
| 0.3 | #FFAA00 | ضعيف | Poor |
| 0.2 | #FF6600 | ضعيف جداً | Very Poor |
| 0.0 | #FF0000 | بدون غطاء | No Vegetation |
| -1.0 | #8B4513 | تربة جافة | Bare Soil |

## Keyboard Accessibility / إمكانية الوصول عبر لوحة المفاتيح

| Element | Keys | Action |
|---------|------|--------|
| Switch | `Space`, `Enter` | Toggle layer on/off |
| Slider | `←` `→` | Decrease/increase opacity |
| Date Picker | `Enter` | Open date selector |
| Collapse Button | `Space`, `Enter` | Expand/collapse panel |
| Legend Toggle | `Space`, `Enter` | Show/hide legend |
| Reset Button | `Space`, `Enter` | Reset to defaults |

All interactive elements have:
- Clear focus indicators (ring-2 ring-green-500)
- ARIA labels for screen readers
- Logical tab order

## localStorage Schema

The component stores preferences in two keys:

### Layers Key: `sahool-map-layers-layers`
```json
{
  "ndvi": true,
  "healthZones": true,
  "taskMarkers": true,
  "weatherOverlay": false,
  "irrigationZones": true
}
```

### NDVI Key: `sahool-map-layers-ndvi`
```json
{
  "opacity": 0.7,
  "historicalDate": "2025-01-01T00:00:00.000Z"
}
```

## Styling / التنسيق

The component uses:
- Tailwind CSS utility classes
- `clsx` for conditional class names
- Transparent backdrop with blur effect
- Green color scheme matching SAHOOL branding
- Responsive design (mobile-friendly)

### Customization

You can override styles using the `className` prop:

```tsx
<LayerControl
  className="shadow-2xl border-4"
  position="top-right"
/>
```

## Integration Examples / أمثلة التكامل

### With NdviTileLayer

```tsx
function FieldMap({ fieldId }) {
  const [layers, setLayers] = useState<LayerSettings>(DEFAULT_LAYERS);
  const [ndviSettings, setNdviSettings] = useState<NDVISettings>(DEFAULT_NDVI);

  return (
    <div className="relative h-screen">
      <MapContainer>
        {layers.ndvi && (
          <NdviTileLayer
            fieldId={fieldId}
            opacity={ndviSettings.opacity}
            date={ndviSettings.historicalDate}
            visible={layers.ndvi}
          />
        )}
        {layers.healthZones && <HealthZonesLayer />}
        {layers.taskMarkers && <TaskMarkers />}
        {layers.weatherOverlay && <WeatherOverlay />}
      </MapContainer>

      <LayerControl
        onLayersChange={setLayers}
        onNDVIChange={setNdviSettings}
      />
    </div>
  );
}
```

### With MapLibre GL

```tsx
function MapLibreMap() {
  const mapRef = useRef<Map>(null);

  const handleLayersChange = (layers: LayerSettings) => {
    const map = mapRef.current;
    if (!map) return;

    // Toggle NDVI layer
    if (map.getLayer('ndvi-layer')) {
      map.setLayoutProperty(
        'ndvi-layer',
        'visibility',
        layers.ndvi ? 'visible' : 'none'
      );
    }

    // Toggle other layers...
  };

  const handleNDVIChange = (settings: NDVISettings) => {
    const map = mapRef.current;
    if (!map || !map.getLayer('ndvi-layer')) return;

    // Update opacity
    map.setPaintProperty('ndvi-layer', 'raster-opacity', settings.opacity);

    // Reload with historical date if needed
    if (settings.historicalDate) {
      // Fetch and update NDVI data
    }
  };

  return (
    <div className="relative h-screen">
      <div ref={mapRef} className="h-full w-full" />
      <LayerControl
        onLayersChange={handleLayersChange}
        onNDVIChange={handleNDVIChange}
      />
    </div>
  );
}
```

## Performance Considerations / اعتبارات الأداء

- **Debounced Updates**: Consider debouncing rapid opacity changes
- **Memoization**: Callbacks are memoized with `useCallback`
- **Conditional Rendering**: Only renders active layer controls
- **localStorage**: Writes are throttled by React's state batching

### Optimization Example

```tsx
import { debounce } from 'lodash';

const handleNDVIChange = debounce((settings: NDVISettings) => {
  // Update expensive NDVI layer
  updateNDVILayer(settings);
}, 300);

<LayerControl onNDVIChange={handleNDVIChange} />
```

## Testing / الاختبار

### Unit Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LayerControl } from './LayerControl';

test('toggles NDVI layer', () => {
  const handleChange = jest.fn();
  render(<LayerControl onLayersChange={handleChange} />);

  const ndviSwitch = screen.getByLabelText(/Toggle NDVI Layer/i);
  fireEvent.click(ndviSwitch);

  expect(handleChange).toHaveBeenCalledWith(
    expect.objectContaining({ ndvi: false })
  );
});

test('updates opacity slider', () => {
  const handleChange = jest.fn();
  render(<LayerControl onNDVIChange={handleChange} />);

  const slider = screen.getByLabelText(/NDVI layer opacity/i);
  fireEvent.change(slider, { target: { value: '0.5' } });

  expect(handleChange).toHaveBeenCalledWith(
    expect.objectContaining({ opacity: 0.5 })
  );
});
```

### Accessibility Tests

```typescript
import { axe } from 'jest-axe';

test('has no accessibility violations', async () => {
  const { container } = render(<LayerControl />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Browser Support / دعم المتصفحات

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support (touch-optimized)

## Related Components / المكونات ذات الصلة

- `NdviTileLayer` - NDVI data visualization
- `HealthZonesLayer` - Health zone overlays
- `TaskMarkers` - Task location markers
- `WeatherOverlay` - Weather data display
- `InteractiveFieldMap` - Main field map component

## Future Enhancements / التحسينات المستقبلية

- [ ] Animation presets for layer transitions
- [ ] Export/import layer configurations
- [ ] Layer ordering control (z-index)
- [ ] Custom layer definitions
- [ ] Layer groups/categories
- [ ] Preset configurations (e.g., "Monitoring Mode", "Planning Mode")
- [ ] Opacity controls for all layers (not just NDVI)
- [ ] Date range picker for time series analysis

## Troubleshooting / استكشاف الأخطاء

### Layers not updating

Ensure you're passing the callbacks:
```tsx
<LayerControl
  onLayersChange={(layers) => {
    // Actually update your map layers
    updateMapLayers(layers);
  }}
/>
```

### localStorage not working

Check if localStorage is available:
```tsx
if (typeof window !== 'undefined') {
  // Safe to use localStorage
}
```

### Styles not applied

Ensure Tailwind CSS is configured correctly and the component's directory is included in the `content` array of `tailwind.config.js`.

## License / الترخيص

This component is part of the SAHOOL agricultural management system.

## Contributors / المساهمون

- SAHOOL Development Team

## Support / الدعم

For issues or questions, please contact the development team or create an issue in the project repository.

---

**Last Updated**: January 5, 2026
**Version**: 1.0.0
