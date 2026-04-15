'use client';

import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import maplibregl, { type MapLayerMouseEvent } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { apiClient } from '@/lib/api';
import type { Field } from '@/lib/api/types';
import { logger } from '@/lib/logger';

interface MapViewProps {
  tenantId?: string;
  onFieldSelect?: (fieldId: string | null) => void;
  fields?: Field[];
}

interface PopupData {
  name: string;
  crop: string;
  area: number | string;
  ndvi: number | null;
  status: FieldStatus;
}

// ---------------------------------------------------------------------------
// Field status classification + colors
// ---------------------------------------------------------------------------
// Status categories are only used for the popup badge and legend. The actual
// polygon fill colour is computed as a continuous gradient over the raw NDVI
// value (see the `interpolate` expression in the `fields-fill` layer below),
// so two fields with NDVI = 0.42 and 0.58 no longer share the same fill.
//
// `no-data` is a distinct state — previously, missing NDVI values silently
// fell through to `warning` (amber), which made every field in a freshly-
// loaded tenant look "one colour for all" and masked real issues.

const STATUS_COLORS = {
  healthy: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
  'no-data': '#9ca3af',
} as const;

type FieldStatus = keyof typeof STATUS_COLORS;

function getFieldStatus(ndviValue?: number | null): FieldStatus {
  // Treat undefined / null / NaN as a distinct "no data" state rather than
  // silently bucketing them into "warning". Note: a real NDVI reading of 0
  // (bare soil) IS valid data and must be classified as "critical".
  if (ndviValue === undefined || ndviValue === null || Number.isNaN(ndviValue)) {
    return 'no-data';
  }
  if (ndviValue >= 0.6) return 'healthy';
  if (ndviValue >= 0.4) return 'warning';
  return 'critical';
}

// Secure popup content component using React instead of raw HTML
const PopupContent: React.FC<PopupData> = ({ name, crop, area, ndvi, status }) => {
  const statusClasses: Record<FieldStatus, string> = {
    healthy: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    critical: 'bg-red-100 text-red-800',
    'no-data': 'bg-gray-100 text-gray-700',
  };

  const statusLabels: Record<FieldStatus, string> = {
    healthy: 'صحي',
    warning: 'تحذير',
    critical: 'حرج',
    'no-data': 'لا توجد بيانات',
  };

  return (
    <div className="p-2 text-right">
      <h4 className="font-bold text-sm">{name || 'حقل'}</h4>
      <p className="text-xs text-gray-600">المحصول: {crop || '-'}</p>
      <p className="text-xs text-gray-600">المساحة: {area || '0'} هكتار</p>
      <p className="text-xs text-gray-600">
        NDVI: {ndvi !== null && ndvi !== undefined ? ndvi.toFixed(2) : 'N/A'}
      </p>
      <div className="mt-2">
        <span className={`text-xs px-2 py-0.5 rounded-full ${statusClasses[status]}`}>
          {statusLabels[status]}
        </span>
      </div>
    </div>
  );
};

const MapView = React.memo<MapViewProps>(function MapView({
  tenantId,
  onFieldSelect,
  fields: propFields,
}) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<InstanceType<typeof maplibregl.Map> | null>(null);
  const popupRef = useRef<InstanceType<typeof maplibregl.Popup> | null>(null);
  const popupRootRef = useRef<ReturnType<typeof createRoot> | null>(null);
  const [, setSelectedField] = useState<string | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [fields, setFields] = useState<Field[]>(propFields || []);
  const [activeBaseLayer, setActiveBaseLayer] = useState<'osm' | 'satellite'>('osm');

  // Fetch fields if not provided
  useEffect(() => {
    if (propFields) {
      setFields(propFields);
      return;
    }

    if (tenantId) {
      apiClient
        .getFields(tenantId)
        .then((response) => {
          if (response.success && response.data) {
            setFields(response.data);
          }
        })
        .catch(logger.error);
    }
  }, [tenantId, propFields]);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Initialize map centered on Yemen with both OSM and Satellite sources
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors',
          },
          satellite: {
            type: 'raster',
            tiles: [
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            ],
            tileSize: 256,
            attribution: '&copy; Esri, Maxar, Earthstar Geographics',
          },
        },
        layers: [
          {
            id: 'osm',
            type: 'raster',
            source: 'osm',
          },
          {
            id: 'satellite',
            type: 'raster',
            source: 'satellite',
            layout: {
              visibility: 'none',
            },
          },
        ],
      },
      center: [44.2, 15.0], // Yemen center
      zoom: 6,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-left');

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    return () => {
      // Clean up React root first
      if (popupRootRef.current) {
        popupRootRef.current.unmount();
        popupRootRef.current = null;
      }
      // Clean up popup
      if (popupRef.current) {
        popupRef.current.remove();
        popupRef.current = null;
      }
      // Clean up map
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Handle base layer switching
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    if (activeBaseLayer === 'satellite') {
      map.current.setLayoutProperty('osm', 'visibility', 'none');
      map.current.setLayoutProperty('satellite', 'visibility', 'visible');
    } else {
      map.current.setLayoutProperty('osm', 'visibility', 'visible');
      map.current.setLayoutProperty('satellite', 'visibility', 'none');
    }
  }, [activeBaseLayer, mapLoaded]);

  // Update fields on map when data changes
  useEffect(() => {
    if (!map.current || !mapLoaded || fields.length === 0) return;

    const geojsonData: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: fields
        .filter((field) => field.boundary)
        .map((field) => {
          // IMPORTANT: use `??` not `||` so that a valid NDVI of 0 (bare
          // soil) is preserved instead of being treated as "no data". The
          // previous `field.ndvi_value || field.ndvi_current` lost zeros.
          const ndviRaw = field.ndvi_value ?? field.ndvi_current;
          const ndvi =
            typeof ndviRaw === 'number' && Number.isFinite(ndviRaw) ? ndviRaw : null;
          return {
            type: 'Feature' as const,
            id: field.id,
            properties: {
              id: field.id,
              name: field.name,
              crop: field.crop_type || field.crop,
              area: field.area_hectares || field.area,
              status: getFieldStatus(ndvi ?? undefined),
              // Store `ndvi` separately from `hasNdvi` so the MapLibre
              // expression can branch on presence without mistaking a
              // real 0.0 reading for "missing".
              ndvi: ndvi ?? -999, // sentinel; hasNdvi flag disambiguates
              hasNdvi: ndvi !== null,
            },
            geometry: field.boundary || field.polygon || field.geometry!,
          };
        }),
    };

    // Remove existing layers and source
    if (map.current.getSource('fields')) {
      map.current.removeLayer('fields-label');
      map.current.removeLayer('fields-outline');
      map.current.removeLayer('fields-fill');
      map.current.removeSource('fields');
    }

    // Add fields source
    map.current.addSource('fields', {
      type: 'geojson',
      data: geojsonData,
    });

    // Add fields fill layer.
    //
    // Previously this used a 3-bucket `match` expression over the pre-computed
    // `status` property (healthy/warning/critical/fallback-gray). That had two
    // problems that together produced the "one colour for all fields" symptom:
    //
    //   1. Every field with NDVI in 0.4-0.59 mapped to the same warning amber,
    //      and every field with NDVI in 0.6-1.0 mapped to the same healthy
    //      green — so any tenant whose fields clustered inside one of these
    //      wide bands looked uniformly coloured.
    //   2. The old status helper treated `undefined` / `null` NDVI as
    //      `warning` instead of `no-data`, so a freshly-loaded tenant whose
    //      fields had not yet been scored was painted entirely amber.
    //
    // The new paint expression:
    //   - checks `hasNdvi` first and paints `no-data` fields in neutral gray
    //     (STATUS_COLORS['no-data']) so the user can visually distinguish
    //     "no reading yet" from "stressed";
    //   - then interpolates the raw NDVI value through a 7-stop gradient
    //     (0.0 → dark red, up to 0.8+ → dark green) matching the NDVI scale
    //     used by NdviTileLayer / NDVI_COLORS in lib/chart-colors.ts.
    //
    // The same expression is reused for the outline colour so the polygon
    // stroke stays in sync with the fill.
    // MapLibre `case` + `interpolate` expression as a plain array.
    // The paint-property types for MapLibre's `addLayer` differ between
    // minor versions, so we build the expression as `unknown` and let
    // MapLibre's runtime expression parser validate it.
    const ndviFillExpression: unknown = [
      'case',
      ['!', ['to-boolean', ['get', 'hasNdvi']]],
      STATUS_COLORS['no-data'],
      [
        'interpolate',
        ['linear'],
        ['to-number', ['get', 'ndvi']],
        0.0,
        '#8B0000', // Bare soil / critical (dark red)
        0.2,
        '#d73027', // Very low vegetation (red)
        0.3,
        '#f46d43', // Sparse (orange)
        0.4,
        '#fdae61', // Moderate-low (amber)
        0.5,
        '#fee08b', // Moderate (yellow)
        0.6,
        '#a6d96a', // Healthy (light green)
        0.7,
        '#66bd63', // Very healthy (green)
        0.8,
        '#1a9850', // Excellent (dark green)
      ],
    ];

    // Add fields fill layer
    map.current.addLayer({
      id: 'fields-fill',
      type: 'fill',
      source: 'fields',
      paint: {

        'fill-color': ndviFillExpression as any,
        'fill-opacity': 0.6,
      },
    });

    // Add fields outline layer
    map.current.addLayer({
      id: 'fields-outline',
      type: 'line',
      source: 'fields',
      paint: {

        'line-color': ndviFillExpression as any,
        'line-width': 2,
      },
    });

    // Add labels
    map.current.addLayer({
      id: 'fields-label',
      type: 'symbol',
      source: 'fields',
      layout: {
        'text-field': ['get', 'name'],
        'text-size': 12,
        'text-anchor': 'center',
      },
      paint: {
        'text-color': '#1f2937',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1,
      },
    });

    // Click handler - using React createRoot for secure popup rendering
    map.current.on('click', 'fields-fill', (e: MapLayerMouseEvent) => {
      if (e.features && e.features[0]) {
        const feature = e.features[0];
        const props = feature.properties;
        const fieldId = props?.id;

        setSelectedField(fieldId);
        onFieldSelect?.(fieldId);

        // Clean up existing popup and React root
        if (popupRef.current) {
          popupRef.current.remove();
        }
        if (popupRootRef.current) {
          popupRootRef.current.unmount();
          popupRootRef.current = null;
        }

        // Create popup with placeholder for React content
        const popupId = `popup-${Date.now()}`;
        popupRef.current = new maplibregl.Popup({
          closeButton: true,
          closeOnClick: false,
        })
          .setLngLat(e.lngLat)
          .setHTML(`<div id="${popupId}" class="sahool-popup-content"></div>`)
          .addTo(map.current!);

        // Mount React component to the popup container after it's in the DOM
        requestAnimationFrame(() => {
          const popupContainer = document.getElementById(popupId);
          if (popupContainer) {
            popupRootRef.current = createRoot(popupContainer);
            popupRootRef.current.render(
              <PopupContent
                name={props?.name || 'حقل'}
                crop={props?.crop || '-'}
                area={props?.area || '0'}
                ndvi={props?.ndvi ?? null}
                status={props?.status || 'warning'}
              />
            );
          }
        });

        // Track popup for cleanup - cleanup happens when new popup is created
        // or when component unmounts
      }
    });

    // Hover effect
    map.current.on('mouseenter', 'fields-fill', () => {
      if (map.current) {
        map.current.getCanvas().style.cursor = 'pointer';
      }
    });

    map.current.on('mouseleave', 'fields-fill', () => {
      if (map.current) {
        map.current.getCanvas().style.cursor = '';
      }
    });

    // Fit bounds to fields
    if (geojsonData.features.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      geojsonData.features.forEach((feature) => {
        if (feature.geometry.type === 'Polygon' && feature.geometry.coordinates) {
          const outerRing = feature.geometry.coordinates[0];
          if (outerRing) {
            outerRing.forEach((coord) => {
              bounds.extend(coord as [number, number]);
            });
          }
        }
      });
      map.current.fitBounds(bounds, { padding: 50 });
    }
  }, [mapLoaded, fields, onFieldSelect]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Base Layer Toggle */}
      <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-1.5 flex gap-1">
        <button
          type="button"
          onClick={() => setActiveBaseLayer('osm')}
          className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
            activeBaseLayer === 'osm'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          aria-label="عرض خريطة الشوارع"
          aria-pressed={activeBaseLayer === 'osm'}
        >
          خريطة
        </button>
        <button
          type="button"
          onClick={() => setActiveBaseLayer('satellite')}
          className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
            activeBaseLayer === 'satellite'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          aria-label="عرض صور القمر الصناعي"
          aria-pressed={activeBaseLayer === 'satellite'}
        >
          قمر صناعي
        </button>
      </div>

      {/* Legend — continuous NDVI gradient + no-data swatch */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 w-44">
        <h4 className="text-xs font-bold text-gray-700 mb-2">مؤشر NDVI</h4>
        {/* Continuous gradient bar matching the `interpolate` stops used
            by the `fields-fill` layer. */}
        <div
          className="relative h-3 rounded overflow-hidden mb-1"
          style={{
            background:
              'linear-gradient(to right, #8B0000 0%, #d73027 25%, #f46d43 37.5%, #fdae61 50%, #fee08b 62.5%, #a6d96a 75%, #66bd63 87.5%, #1a9850 100%)',
          }}
        />
        <div className="flex justify-between text-[10px] text-gray-600 mb-2">
          <span>0.0</span>
          <span>0.4</span>
          <span>0.8+</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: STATUS_COLORS['no-data'] }}
          ></span>
          <span>لا توجد بيانات</span>
        </div>
      </div>

      {/* Loading overlay */}
      {!mapLoaded && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-gray-500">جاري تحميل الخريطة...</div>
        </div>
      )}
    </div>
  );
});

export { MapView };
export default MapView;
