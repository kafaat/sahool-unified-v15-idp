'use client';

import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import DOMPurify from 'dompurify';
import { apiClient } from '@/lib/api';
import type { Field } from '@/lib/api/types';

interface MapViewProps {
  tenantId?: string;
  onFieldSelect?: (fieldId: string | null) => void;
  fields?: Field[];
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

const MapView = React.memo<MapViewProps>(function MapView({ tenantId, onFieldSelect, fields: propFields }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<InstanceType<typeof maplibregl.Map> | null>(null);
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
        .catch(console.error);
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

    // Click handler
    map.current.on('click', 'fields-fill', (e: any) => {
      if (e.features && e.features[0]) {
        const feature = e.features[0];
        const props = feature.properties;
        const fieldId = props?.id;

        setSelectedField(fieldId);
        onFieldSelect?.(fieldId);

        // Sanitize content to prevent XSS using DOMPurify
        const safeName = DOMPurify.sanitize(String(props?.name || 'حقل'), { ALLOWED_TAGS: [] });
        const safeCrop = DOMPurify.sanitize(String(props?.crop || '-'), { ALLOWED_TAGS: [] });
        const safeArea = DOMPurify.sanitize(String(props?.area || '0'), { ALLOWED_TAGS: [] });
        const safeNdvi = props?.ndvi ? DOMPurify.sanitize(String(props.ndvi.toFixed(2)), { ALLOWED_TAGS: [] }) : 'N/A';
        const statusClass = props?.status === 'healthy' ? 'bg-green-100 text-green-800' :
                           props?.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                           'bg-red-100 text-red-800';
        const statusText = props?.status === 'healthy' ? 'صحي' :
                          props?.status === 'warning' ? 'تحذير' : 'حرج';

        const popupContent = DOMPurify.sanitize(`
          <div class="p-2 text-right" dir="rtl">
            <h4 class="font-bold text-sm">${safeName}</h4>
            <p class="text-xs text-gray-600">المحصول: ${safeCrop}</p>
            <p class="text-xs text-gray-600">المساحة: ${safeArea} هكتار</p>
            <p class="text-xs text-gray-600">NDVI: ${safeNdvi}</p>
            <div class="mt-2">
              <span class="text-xs px-2 py-0.5 rounded-full ${statusClass}">
                ${statusText}
              </span>
            </div>
          </div>
        `, {
          ALLOWED_TAGS: ['div', 'h4', 'p', 'span'],
          ALLOWED_ATTR: ['class', 'dir'],
        });

        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(popupContent)
          .addTo(map.current!);
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
        if (feature?.geometry?.type === 'Polygon' && feature.geometry.coordinates?.[0]) {
          feature.geometry.coordinates[0].forEach(coord => {
            bounds.extend(coord as [number, number]);
          });
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
