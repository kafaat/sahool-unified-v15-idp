# LayerControl - Quick Start Guide

**دليل البدء السريع - مكون التحكم في طبقات الخريطة**

Get started with the LayerControl component in 5 minutes!

## 1. Basic Setup (30 seconds)

```tsx
import { LayerControl } from "@/features/fields/components";

function MyMap() {
  return (
    <div className="relative h-screen">
      {/* Your map */}
      <MapContainer center={[15.5527, 48.5164]} zoom={13}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      </MapContainer>

      {/* Add layer control - that's it! */}
      <LayerControl position="top-right" />
    </div>
  );
}
```

## 2. Handle Layer Changes (1 minute)

```tsx
function MyMap() {
  const handleLayersChange = (layers) => {
    console.log("Active layers:", layers);
    // layers = { ndvi: true, healthZones: false, ... }
  };

  const handleNDVIChange = (settings) => {
    console.log("NDVI opacity:", settings.opacity);
    console.log("Historical date:", settings.historicalDate);
  };

  return (
    <div className="relative h-screen">
      <MapContainer>...</MapContainer>
      <LayerControl
        onLayersChange={handleLayersChange}
        onNDVIChange={handleNDVIChange}
      />
    </div>
  );
}
```

## 3. Control Layers Programmatically (2 minutes)

```tsx
import { useLayerControl } from "@/features/fields/components";

function MyMap() {
  const [state, controls] = useLayerControl();

  return (
    <div>
      {/* Your map with conditional layers */}
      <MapContainer>
        {state.layers.ndvi && (
          <NdviTileLayer
            opacity={state.ndvi.opacity}
            date={state.ndvi.historicalDate}
          />
        )}
        {state.layers.healthZones && <HealthZonesLayer />}
        {state.layers.taskMarkers && <TaskMarkers />}
      </MapContainer>

      {/* Layer control */}
      <LayerControl />

      {/* External controls */}
      <button onClick={() => controls.toggleLayer("ndvi")}>Toggle NDVI</button>
      <button onClick={() => controls.updateNDVIOpacity(0.5)}>
        50% Opacity
      </button>
    </div>
  );
}
```

## 4. Full Integration Example (3 minutes)

```tsx
import { useState } from "react";
import {
  LayerControl,
  NdviTileLayer,
  HealthZonesLayer,
} from "@/features/fields/components";

function FieldMap({ fieldId }) {
  const [layers, setLayers] = useState({
    ndvi: true,
    healthZones: true,
    taskMarkers: false,
    weatherOverlay: false,
    irrigationZones: true,
  });

  const [ndviSettings, setNdviSettings] = useState({
    opacity: 0.7,
    historicalDate: null,
  });

  return (
    <div className="relative h-screen">
      <MapContainer center={[15.5527, 48.5164]} zoom={13}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {/* Conditional layers based on toggle state */}
        {layers.ndvi && (
          <NdviTileLayer
            fieldId={fieldId}
            opacity={ndviSettings.opacity}
            date={ndviSettings.historicalDate}
            visible={layers.ndvi}
          />
        )}

        {layers.healthZones && <HealthZonesLayer fieldId={fieldId} />}

        {layers.taskMarkers && <TaskMarkers fieldId={fieldId} />}
      </MapContainer>

      {/* Layer control */}
      <LayerControl
        position="top-right"
        initialLayers={layers}
        initialNDVI={ndviSettings}
        onLayersChange={setLayers}
        onNDVIChange={setNdviSettings}
        persistPreferences={true}
      />
    </div>
  );
}
```

## Features at a Glance

### Toggle Layers

- NDVI satellite imagery ✓
- Health zones ✓
- Task markers ✓
- Weather overlay ✓
- Irrigation zones ✓

### NDVI Controls

- Opacity slider (0-100%)
- Historical date picker
- Real-time updates

### User Experience

- Collapsible panel
- Color legend
- Keyboard accessible
- Saves to localStorage
- Arabic + English labels

## Props Cheat Sheet

| Prop                 | Type                                                           | Default                        | What it does                  |
| -------------------- | -------------------------------------------------------------- | ------------------------------ | ----------------------------- |
| `position`           | `'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right'` | `'top-right'`                  | Where to place the control    |
| `onLayersChange`     | `(layers) => void`                                             | -                              | Called when any layer toggles |
| `onNDVIChange`       | `(settings) => void`                                           | -                              | Called when NDVI changes      |
| `initialLayers`      | `object`                                                       | All on except weather          | Starting layer visibility     |
| `initialNDVI`        | `object`                                                       | `{ opacity: 0.7, date: null }` | Starting NDVI settings        |
| `persistPreferences` | `boolean`                                                      | `true`                         | Save to localStorage          |

## Common Patterns

### Pattern 1: Simple Toggle

```tsx
<LayerControl onLayersChange={(layers) => console.log(layers)} />
```

### Pattern 2: With State

```tsx
const [layers, setLayers] = useState({...});
<LayerControl onLayersChange={setLayers} />
```

### Pattern 3: Programmatic Control

```tsx
const [state, { toggleLayer }] = useLayerControl();
<button onClick={() => toggleLayer("ndvi")}>Toggle</button>;
```

## Keyboard Shortcuts

- `Tab` - Navigate between controls
- `Space/Enter` - Toggle switches and buttons
- `Arrow Keys` - Adjust opacity slider
- `Esc` - Close date picker

## Troubleshooting

**Q: Layers not updating?**
A: Make sure you're passing `onLayersChange` and actually updating your map layers.

**Q: Settings not persisting?**
A: Set `persistPreferences={true}` and ensure localStorage is available.

**Q: Styles broken?**
A: Check that Tailwind CSS is configured and the component path is in `content` array.

## Next Steps

1. See `LayerControl.example.tsx` for more examples
2. Read `LayerControl.README.md` for full documentation
3. Check the TypeScript types for all available options

## Need Help?

- Full docs: `LayerControl.README.md`
- Examples: `LayerControl.example.tsx`
- Types: Check IntelliSense or `LayerControl.tsx`

---

**تم! You're ready to use LayerControl!** 🎉

For advanced features like custom storage keys, multiple instances, or integration with MapLibre GL, see the full README.
