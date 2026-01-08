/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck - Example file for demonstration purposes
'use client';

/**
 * LayerControl Component Usage Examples
 * أمثلة استخدام مكون التحكم في الطبقات
 */

import React, { useRef, useEffect } from 'react';
import { LayerControl, useLayerControl } from './LayerControl';
import type { LayerSettings, NDVISettings } from './LayerControl';
import { MapContainer, TileLayer } from 'react-leaflet';
import type { Map as LeafletMap } from 'leaflet';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Basic Usage / الاستخدام الأساسي
// ═══════════════════════════════════════════════════════════════════════════

export function BasicLayerControlExample() {
  const handleLayersChange = (layers: LayerSettings) => {
    console.log('Layers changed:', layers);
  };

  const handleNDVIChange = (settings: NDVISettings) => {
    console.log('NDVI settings changed:', settings);
  };

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.5527, 48.5164]}
        zoom={13}
        className="h-full w-full rounded-xl"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
      </MapContainer>

      <LayerControl
        position="top-right"
        onLayersChange={handleLayersChange}
        onNDVIChange={handleNDVIChange}
        persistPreferences={true}
      />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: With Initial Settings / مع الإعدادات الأولية
// ═══════════════════════════════════════════════════════════════════════════

export function LayerControlWithInitialSettings() {
  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.5527, 48.5164]}
        zoom={13}
        className="h-full w-full rounded-xl"
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution='&copy; Esri'
        />
      </MapContainer>

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
      />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Using the Hook / استخدام الخطاف
// ═══════════════════════════════════════════════════════════════════════════

export function LayerControlWithHook() {
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

  useEffect(() => {
    console.log('Current layer state:', state);
  }, [state]);

  return (
    <div className="space-y-4">
      <div className="relative h-[600px] w-full">
        <MapContainer
          center={[15.5527, 48.5164]}
          zoom={13}
          className="h-full w-full rounded-xl"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
        </MapContainer>

        <LayerControl
          position="top-right"
          onLayersChange={(layers) => {
            // You can use controls to update state programmatically
            console.log('Layers updated:', layers);
          }}
          onNDVIChange={(ndvi) => {
            console.log('NDVI updated:', ndvi);
          }}
        />
      </div>

      {/* External controls / عناصر تحكم خارجية */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => controls.toggleLayer('ndvi')}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Toggle NDVI
        </button>
        <button
          onClick={() => controls.updateNDVIOpacity(0.5)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Set Opacity to 50%
        </button>
        <button
          onClick={() => controls.updateNDVIDate(new Date())}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Set Today&apos;s Date
        </button>
        <button
          onClick={() => controls.resetToDefaults()}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          Reset to Defaults
        </button>
      </div>

      {/* State display / عرض الحالة */}
      <div className="p-4 bg-gray-100 rounded-lg">
        <h3 className="font-bold mb-2">Current State:</h3>
        <pre className="text-sm overflow-auto">
          {JSON.stringify(state, null, 2)}
        </pre>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: All Positions / جميع المواقع
// ═══════════════════════════════════════════════════════════════════════════

export function LayerControlPositionsExample() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {(['top-left', 'top-right', 'bottom-left', 'bottom-right'] as const).map(
        (position) => (
          <div key={position} className="relative h-[400px] w-full border-2 border-gray-200 rounded-xl">
            <MapContainer
              center={[15.5527, 48.5164]}
              zoom={10}
              className="h-full w-full rounded-xl"
              zoomControl={false}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap'
              />
            </MapContainer>

            <LayerControl position={position} />

            <div className="absolute bottom-2 left-2 bg-white/90 px-3 py-1 rounded-lg text-sm font-semibold">
              {position}
            </div>
          </div>
        )
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Integration with Map Layers / التكامل مع طبقات الخريطة
// ═══════════════════════════════════════════════════════════════════════════

export function IntegratedMapExample() {
  const mapRef = useRef<LeafletMap | null>(null);
  const [layerState, controls] = useLayerControl();

  // Simulate layer visibility control
  useEffect(() => {
    if (!mapRef.current) return;

    console.log('Update map layers based on:', layerState);
    // Here you would actually control your map layers
    // For example, toggle NDVI layer visibility:
    // if (layerState.layers.ndvi) {
    //   showNDVILayer(mapRef.current, layerState.ndvi.opacity);
    // } else {
    //   hideNDVILayer(mapRef.current);
    // }
  }, [layerState]);

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.5527, 48.5164]}
        zoom={13}
        className="h-full w-full rounded-xl"
        ref={mapRef}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {/* Conditionally render layers based on state */}
        {layerState.layers.ndvi && (
          <div>
            {/* Your NDVI layer component here */}
            {/* <NdviTileLayer opacity={layerState.ndvi.opacity} ... /> */}
          </div>
        )}

        {layerState.layers.healthZones && (
          <div>
            {/* Your health zones layer here */}
            {/* <HealthZonesLayer ... /> */}
          </div>
        )}

        {layerState.layers.taskMarkers && (
          <div>
            {/* Your task markers here */}
            {/* <TaskMarkers ... /> */}
          </div>
        )}

        {layerState.layers.weatherOverlay && (
          <div>
            {/* Your weather overlay here */}
            {/* <WeatherOverlay ... /> */}
          </div>
        )}

        {layerState.layers.irrigationZones && (
          <div>
            {/* Your irrigation zones here */}
          </div>
        )}
      </MapContainer>

      <LayerControl
        position="top-right"
        onLayersChange={(layers) => {
          console.log('Layers changed:', layers);
        }}
        onNDVIChange={(ndvi) => {
          console.log('NDVI changed:', ndvi);
        }}
        persistPreferences={true}
        storageKey="sahool-field-map-layers"
      />

      {/* Status indicator */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3">
        <h4 className="text-sm font-bold mb-2">Active Layers:</h4>
        <ul className="text-xs space-y-1">
          {Object.entries(layerState.layers)
            .filter(([_, enabled]) => enabled)
            .map(([layer]) => (
              <li key={layer} className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="capitalize">{layer}</span>
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 6: Without Persistence / بدون حفظ دائم
// ═══════════════════════════════════════════════════════════════════════════

export function LayerControlWithoutPersistence() {
  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.5527, 48.5164]}
        zoom={13}
        className="h-full w-full rounded-xl"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
      </MapContainer>

      <LayerControl
        position="top-right"
        persistPreferences={false}
        onLayersChange={(layers) => {
          // Handle layer changes without localStorage
          console.log('Layers (not persisted):', layers);
        }}
      />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Demo Component / مكون العرض التوضيحي
// ═══════════════════════════════════════════════════════════════════════════

export default function LayerControlDemo() {
  const [activeExample, setActiveExample] = React.useState(0);

  const examples = [
    { name: 'Basic Usage', component: BasicLayerControlExample },
    { name: 'With Initial Settings', component: LayerControlWithInitialSettings },
    { name: 'Using Hook', component: LayerControlWithHook },
    { name: 'All Positions', component: LayerControlPositionsExample },
    { name: 'Integrated Map', component: IntegratedMapExample },
    { name: 'Without Persistence', component: LayerControlWithoutPersistence },
  ];

  const ActiveComponent = examples[activeExample].component;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            LayerControl Component Examples
          </h1>
          <p className="text-gray-600 mb-4">
            أمثلة مكون التحكم في طبقات الخريطة
          </p>

          {/* Example selector */}
          <div className="flex gap-2 flex-wrap">
            {examples.map((example, index) => (
              <button
                key={example.name}
                onClick={() => setActiveExample(index)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeExample === index
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {example.name}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {examples[activeExample].name}
          </h2>
          <ActiveComponent />
        </div>
      </div>
    </div>
  );
}
