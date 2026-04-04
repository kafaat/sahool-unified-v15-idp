'use client';

// Map Layers Panel — لوحة طبقات الخريطة
// Toggle visibility of multiple data layers: NDVI, soil moisture, elevation, etc.

import React, { useState, useMemo } from 'react';
import {
  Layers,
  ChevronRight,
  ChevronDown,
  ChevronLeft,
  Eye,
  EyeOff,
  Leaf,
  Droplets,
  Thermometer,
  Mountain,
  MapPin,
  Tractor,
  FlaskConical,
  Spline,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface MapLayer {
  id: string;
  name: string;
  nameAr: string;
  icon: string;
  category: 'vegetation' | 'soil' | 'water' | 'terrain' | 'weather' | 'scouting';
  enabled: boolean;
  opacity: number; // 0-100
  colorScale?: 'ndvi' | 'moisture' | 'temperature' | 'elevation';
}

export interface MapLayersPanelProps {
  layers: MapLayer[];
  onToggleLayer: (layerId: string) => void;
  onOpacityChange: (layerId: string, opacity: number) => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CATEGORY_META: Record<
  MapLayer['category'],
  { label: string; labelAr: string }
> = {
  vegetation: { label: 'Vegetation', labelAr: 'الغطاء النباتي' },
  soil: { label: 'Soil', labelAr: 'التربة' },
  water: { label: 'Water', labelAr: 'المياه' },
  terrain: { label: 'Terrain', labelAr: 'التضاريس' },
  weather: { label: 'Weather', labelAr: 'الطقس' },
  scouting: { label: 'Scouting', labelAr: 'الاستكشاف' },
};

const CATEGORY_ORDER: MapLayer['category'][] = [
  'vegetation',
  'soil',
  'water',
  'terrain',
  'weather',
  'scouting',
];

const ICON_MAP: Record<string, React.ElementType> = {
  leaf: Leaf,
  droplets: Droplets,
  thermometer: Thermometer,
  mountain: Mountain,
  spline: Spline,
  'map-pin': MapPin,
  tractor: Tractor,
  'flask-conical': FlaskConical,
};

const COLOR_SCALE_GRADIENTS: Record<string, string> = {
  ndvi: 'from-red-600 via-yellow-400 to-green-600',
  moisture: 'from-amber-300 via-sky-400 to-blue-700',
  temperature: 'from-blue-500 via-yellow-400 to-red-600',
  elevation: 'from-green-700 via-amber-400 to-stone-100',
};

// ---------------------------------------------------------------------------
// Default layers factory
// ---------------------------------------------------------------------------

export function getDefaultLayers(): MapLayer[] {
  return [
    {
      id: 'ndvi',
      name: 'NDVI',
      nameAr: 'مؤشر الغطاء النباتي',
      icon: 'leaf',
      category: 'vegetation',
      enabled: true,
      opacity: 80,
      colorScale: 'ndvi',
    },
    {
      id: 'soil-moisture',
      name: 'Soil Moisture',
      nameAr: 'رطوبة التربة',
      icon: 'droplets',
      category: 'soil',
      enabled: false,
      opacity: 70,
      colorScale: 'moisture',
    },
    {
      id: 'temperature',
      name: 'Temperature',
      nameAr: 'درجة الحرارة',
      icon: 'thermometer',
      category: 'weather',
      enabled: false,
      opacity: 60,
      colorScale: 'temperature',
    },
    {
      id: 'elevation',
      name: 'Elevation',
      nameAr: 'الارتفاع',
      icon: 'mountain',
      category: 'terrain',
      enabled: false,
      opacity: 70,
      colorScale: 'elevation',
    },
    {
      id: 'contour-lines',
      name: 'Contour Lines',
      nameAr: 'خطوط الكنتور',
      icon: 'spline',
      category: 'terrain',
      enabled: false,
      opacity: 50,
    },
    {
      id: 'scouting-notes',
      name: 'Scouting Notes',
      nameAr: 'ملاحظات الاستكشاف',
      icon: 'map-pin',
      category: 'scouting',
      enabled: false,
      opacity: 100,
    },
    {
      id: 'equipment-tracks',
      name: 'Equipment Tracks',
      nameAr: 'مسارات المعدات',
      icon: 'tractor',
      category: 'scouting',
      enabled: false,
      opacity: 60,
    },
    {
      id: 'vra-prescription',
      name: 'VRA Prescription',
      nameAr: 'وصفة التطبيق المتغير',
      icon: 'flask-conical',
      category: 'soil',
      enabled: false,
      opacity: 70,
    },
  ];
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function LayerIcon({ iconName, className }: { iconName: string; className?: string }) {
  const IconComponent = ICON_MAP[iconName] ?? Layers;
  return <IconComponent className={className} />;
}

function ColorScaleBar({ colorScale }: { colorScale: string }) {
  const gradient = COLOR_SCALE_GRADIENTS[colorScale];
  if (!gradient) return null;

  return (
    <div
      className={`h-1.5 w-full rounded-full bg-gradient-to-r ${gradient} mt-1`}
      title={colorScale}
    />
  );
}

interface LayerRowProps {
  layer: MapLayer;
  onToggle: () => void;
  onOpacityChange: (opacity: number) => void;
}

function LayerRow({ layer, onToggle, onOpacityChange }: LayerRowProps) {
  const [showOpacity, setShowOpacity] = useState(false);

  return (
    <div
      className={`rounded-lg border px-3 py-2 transition-colors ${
        layer.enabled
          ? 'border-emerald-200 bg-emerald-50/60 dark:border-emerald-800 dark:bg-emerald-950/30'
          : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800'
      }`}
    >
      <div className="flex items-center gap-2">
        {/* Toggle */}
        <button
          type="button"
          onClick={onToggle}
          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 ${
            layer.enabled ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
          }`}
          role="switch"
          aria-checked={layer.enabled}
          aria-label={`Toggle ${layer.name}`}
        >
          <span
            className={`pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform ${
              layer.enabled ? 'translate-x-4' : 'translate-x-0'
            }`}
          />
        </button>

        {/* Icon */}
        <LayerIcon
          iconName={layer.icon}
          className={`h-4 w-4 shrink-0 ${
            layer.enabled
              ? 'text-emerald-600 dark:text-emerald-400'
              : 'text-gray-400 dark:text-gray-500'
          }`}
        />

        {/* Labels */}
        <div className="min-w-0 flex-1">
          <p
            className={`text-sm font-medium leading-tight ${
              layer.enabled
                ? 'text-gray-900 dark:text-gray-100'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            {layer.name}
          </p>
          <p
            className={`text-xs leading-tight ${
              layer.enabled
                ? 'text-gray-600 dark:text-gray-300'
                : 'text-gray-400 dark:text-gray-500'
            }`}
            dir="rtl"
          >
            {layer.nameAr}
          </p>
        </div>

        {/* Visibility indicator & opacity toggle */}
        <button
          type="button"
          onClick={() => setShowOpacity((v) => !v)}
          className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          aria-label={`Adjust opacity for ${layer.name}`}
        >
          {layer.enabled ? (
            <Eye className="h-3.5 w-3.5" />
          ) : (
            <EyeOff className="h-3.5 w-3.5" />
          )}
        </button>
      </div>

      {/* Opacity slider */}
      {showOpacity && (
        <div className="mt-2 flex items-center gap-2">
          <input
            type="range"
            min={0}
            max={100}
            value={layer.opacity}
            onChange={(e) => onOpacityChange(Number(e.target.value))}
            className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-gray-200 accent-emerald-500 dark:bg-gray-600"
            aria-label={`Opacity for ${layer.name}`}
          />
          <span className="w-8 text-right text-xs tabular-nums text-gray-500 dark:text-gray-400">
            {layer.opacity}%
          </span>
        </div>
      )}

      {/* Color scale bar */}
      {layer.enabled && layer.colorScale && (
        <ColorScaleBar colorScale={layer.colorScale} />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function MapLayersPanel({
  layers,
  onToggleLayer,
  onOpacityChange,
}: MapLayersPanelProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [collapsedCategories, setCollapsedCategories] = useState<Set<string>>(
    () => new Set()
  );

  const toggleCategory = (category: string) => {
    setCollapsedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  const layersByCategory = useMemo(() => {
    const grouped = new Map<MapLayer['category'], MapLayer[]>();
    for (const layer of layers) {
      const arr = grouped.get(layer.category) ?? [];
      arr.push(layer);
      grouped.set(layer.category, arr);
    }
    return grouped;
  }, [layers]);

  const enabledCount = useMemo(
    () => layers.filter((l) => l.enabled).length,
    [layers]
  );

  // Collapsed tab
  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed right-0 top-1/3 z-30 flex items-center gap-1.5 rounded-l-lg border border-r-0 border-gray-200 bg-white px-2 py-3 shadow-lg transition-colors hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-750"
        aria-label="Open map layers panel"
      >
        <ChevronLeft className="h-4 w-4 text-gray-600 dark:text-gray-300" />
        <Layers className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
        {enabledCount > 0 && (
          <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-emerald-500 px-1 text-xs font-semibold text-white">
            {enabledCount}
          </span>
        )}
      </button>
    );
  }

  return (
    <div className="fixed right-0 top-16 z-30 flex h-[calc(100vh-4rem)] w-72 flex-col border-l border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <Layers className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
          <div>
            <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Map Layers
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400" dir="rtl">
              طبقات الخريطة
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {enabledCount > 0 && (
            <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
              {enabledCount} active
            </span>
          )}
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
            aria-label="Close map layers panel"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Layer list */}
      <div className="flex-1 overflow-y-auto px-3 py-2">
        {CATEGORY_ORDER.map((category) => {
          const categoryLayers = layersByCategory.get(category);
          if (!categoryLayers || categoryLayers.length === 0) return null;

          const meta = CATEGORY_META[category];
          const isCollapsed = collapsedCategories.has(category);
          const activeLayers = categoryLayers.filter((l) => l.enabled).length;

          return (
            <div key={category} className="mb-3">
              {/* Category header */}
              <button
                type="button"
                onClick={() => toggleCategory(category)}
                className="flex w-full items-center gap-1.5 rounded-md px-1 py-1.5 text-left hover:bg-gray-50 dark:hover:bg-gray-750"
              >
                {isCollapsed ? (
                  <ChevronRight className="h-3.5 w-3.5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-3.5 w-3.5 text-gray-400" />
                )}
                <span className="flex-1 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  {meta.label}
                  <span className="mx-1 text-gray-300 dark:text-gray-600">|</span>
                  <span dir="rtl">{meta.labelAr}</span>
                </span>
                {activeLayers > 0 && (
                  <span className="rounded-full bg-emerald-100 px-1.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
                    {activeLayers}
                  </span>
                )}
              </button>

              {/* Category layers */}
              {!isCollapsed && (
                <div className="mt-1 flex flex-col gap-1.5">
                  {categoryLayers.map((layer) => (
                    <LayerRow
                      key={layer.id}
                      layer={layer}
                      onToggle={() => onToggleLayer(layer.id)}
                      onOpacityChange={(opacity) =>
                        onOpacityChange(layer.id, opacity)
                      }
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 px-4 py-2 dark:border-gray-700">
        <p className="text-center text-[10px] text-gray-400 dark:text-gray-500">
          {layers.length} layers available &middot; {enabledCount} enabled
        </p>
      </div>
    </div>
  );
}
