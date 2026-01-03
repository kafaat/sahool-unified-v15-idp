'use client';

import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import maplibregl, { type MapMouseEvent } from 'maplibre-gl';
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
  status: 'healthy' | 'warning' | 'critical';
}

// Status colors for NDVI/health
const STATUS_COLORS: Record<string, string> = {
  healthy: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
};

function getFieldStatus(ndviValue?: number): 'healthy' | 'warning' | 'critical' {
  if (!ndviValue) return 'warning';
  if (ndviValue >= 0.6) return 'healthy';
  if (ndviValue >= 0.4) return 'warning';
  return 'critical';
}

// Secure popup content component using React instead of raw HTML
const PopupContent: React.FC<PopupData> = ({ name, crop, area, ndvi, status }) => {
  const statusClasses = {
    healthy: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    critical: 'bg-red-100 text-red-800',
  };

  const statusLabels = {
    healthy: 'صحي',
    warning: 'تحذير',
    critical: 'حرج',
  };

  return (
    <div className="p-2 text-right" dir="rtl">
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

const MapView = React.memo<MapViewProps>(function MapView({ tenantId, onFieldSelect, fields: propFields }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<InstanceType<typeof maplibregl.Map> | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);
  const popupRootRef = useRef<ReturnType<typeof createRoot> | null>(null);
  const [, setSelectedField] = useState<string | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [fields, setFields] = useState<Field[]>(propFields || []);

  // Fetch fields if not provided
  useEffect(() => {
    if (propFields) {
      setFields(propFields);
      return;
    }

    if (tenantId) {
      apiClient.getFields(tenantId)
        .then(response => {
          if (response.success && response.data) {
            setFields(response.data);
          }
        })
        .catch(logger.error);
    }
  }, [tenantId, propFields]);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Initialize map centered on Yemen
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
        },
        layers: [
          {
            id: 'osm',
            type: 'raster',
            source: 'osm',
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
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Update fields on map when data changes
  useEffect(() => {
    if (!map.current || !mapLoaded || fields.length === 0) return;

    const geojsonData: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: fields
        .filter(field => field.boundary)
        .map(field => ({
          type: 'Feature' as const,
          id: field.id,
          properties: {
            id: field.id,
            name: field.name,
            crop: field.crop_type || field.crop,
            area: field.area_hectares || field.area,
            status: getFieldStatus(field.ndvi_value || field.ndvi_current),
            ndvi: field.ndvi_value || field.ndvi_current,
          },
          geometry: field.boundary || field.polygon || field.geometry!,
        })),
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

    // Add fields fill layer
    map.current.addLayer({
      id: 'fields-fill',
      type: 'fill',
      source: 'fields',
      paint: {
        'fill-color': [
          'match',
          ['get', 'status'],
          'healthy', STATUS_COLORS.healthy,
          'warning', STATUS_COLORS.warning,
          'critical', STATUS_COLORS.critical,
          '#9ca3af',
        ],
        'fill-opacity': 0.6,
      },
    });

    // Add fields outline layer
    map.current.addLayer({
      id: 'fields-outline',
      type: 'line',
      source: 'fields',
      paint: {
        'line-color': [
          'match',
          ['get', 'status'],
          'healthy', STATUS_COLORS.healthy,
          'warning', STATUS_COLORS.warning,
          'critical', STATUS_COLORS.critical,
          '#6b7280',
        ],
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
    map.current.on('click', 'fields-fill', (e: MapMouseEvent) => {
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

        // Create popup container
        const popupContainer = document.createElement('div');

        // Create new popup with the container element
        popupRef.current = new maplibregl.Popup({
          closeButton: true,
          closeOnClick: false,
        })
          .setLngLat(e.lngLat)
          .setHTML(popupContainer.outerHTML)
          .addTo(map.current!);

        // Get the actual popup element from the DOM
        const popupElement = popupRef.current.getElement();
        const contentContainer = popupElement?.querySelector('.maplibregl-popup-content > div');

        if (contentContainer) {
          // Create React root and render the secure PopupContent component
          popupRootRef.current = createRoot(contentContainer);
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

        // Clean up React root when popup is closed
        popupRef.current.on('close', () => {
          if (popupRootRef.current) {
            popupRootRef.current.unmount();
            popupRootRef.current = null;
          }
          popupRef.current = null;
        });
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
      geojsonData.features.forEach(feature => {
        if (feature.geometry.type === 'Polygon' && feature.geometry.coordinates) {
          const outerRing = feature.geometry.coordinates[0];
          if (outerRing) {
            outerRing.forEach(coord => {
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

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3">
        <h4 className="text-xs font-bold text-gray-700 mb-2">الحالة</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span>صحي (NDVI &gt; 0.6)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-amber-500"></span>
            <span>تحذير (0.4 - 0.6)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span>حرج (&lt; 0.4)</span>
          </div>
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
