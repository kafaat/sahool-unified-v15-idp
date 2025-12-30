'use client';

/**
 * SAHOOL Field Map Component
 * مكون خريطة الحقل التفاعلية
 *
 * Features:
 * - Interactive Leaflet map
 * - Field polygon display with NDVI coloring
 * - Click to select field
 * - Popup with field details
 * - Health score legend
 */

import React, { useEffect, useRef, useState } from 'react';
import { MapPin, Loader2, Layers } from 'lucide-react';
import DOMPurify from 'dompurify';
import type { Field } from '../types';

// Leaflet type definition for CDN-loaded library
declare global {
  interface Window {
    L?: typeof import('leaflet');
  }
}

interface FieldMapProps {
  field?: Field;
  fields?: Field[];
  height?: string;
  onFieldClick?: (fieldId: string) => void;
  selectedFieldId?: string;
  showLegend?: boolean;
  showControls?: boolean;
}

// NDVI color scale
const getNDVIColor = (ndvi?: number): string => {
  if (ndvi === undefined || ndvi === null) return '#9ca3af'; // gray
  if (ndvi >= 0.7) return '#15803d'; // dark green
  if (ndvi >= 0.5) return '#22c55e'; // green
  if (ndvi >= 0.3) return '#eab308'; // yellow
  if (ndvi >= 0.1) return '#f97316'; // orange
  return '#ef4444'; // red
};

// Health status from NDVI
const getHealthStatus = (ndvi?: number): { label: string; labelAr: string } => {
  if (ndvi === undefined || ndvi === null) return { label: 'Unknown', labelAr: 'غير معروف' };
  if (ndvi >= 0.7) return { label: 'Excellent', labelAr: 'ممتاز' };
  if (ndvi >= 0.5) return { label: 'Good', labelAr: 'جيد' };
  if (ndvi >= 0.3) return { label: 'Fair', labelAr: 'متوسط' };
  if (ndvi >= 0.1) return { label: 'Poor', labelAr: 'ضعيف' };
  return { label: 'Critical', labelAr: 'حرج' };
};

// Yemen center coordinates
const YEMEN_CENTER: [number, number] = [15.5527, 48.5164];
const DEFAULT_ZOOM = 7;

export const FieldMap: React.FC<FieldMapProps> = ({
  field,
  fields,
  height = '400px',
  onFieldClick,
  selectedFieldId,
  showLegend = true,
  showControls = true,
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const layersRef = useRef<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [mapError, setMapError] = useState<string | null>(null);

  const displayFields = field ? [field] : fields || [];

  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    const initMap = async () => {
      try {
        // Check if Leaflet is loaded
        if (!window.L) {
          // Try to load Leaflet dynamically
          await loadLeaflet();
        }

        if (!window.L) {
          setMapError('فشل في تحميل مكتبة الخرائط');
          setIsLoading(false);
          return;
        }

        const L = window.L;

        // Create map if it doesn't exist
        if (!mapInstanceRef.current && mapRef.current) {
          const map = L.map(mapRef.current, {
            zoomControl: showControls,
          }).setView(YEMEN_CENTER, DEFAULT_ZOOM);

          // Add OpenStreetMap tile layer
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
          }).addTo(map);

          mapInstanceRef.current = map;
        }

        // Clear existing layers
        layersRef.current.forEach((layer) => layer.remove());
        layersRef.current = [];

        // Add field polygons/markers
        if (displayFields.length > 0) {
          const bounds: [number, number][] = [];

          displayFields.forEach((fieldItem) => {
            const color = getNDVIColor(fieldItem.ndviValue);
            const isSelected = selectedFieldId === fieldItem.id;
            const healthStatus = getHealthStatus(fieldItem.ndviValue);

            // If field has polygon, draw it
            if (fieldItem.polygon && fieldItem.polygon.coordinates && fieldItem.polygon.coordinates[0]) {
              // Convert GeoJSON coordinates to Leaflet format [lat, lng]
              const polygonCoords = fieldItem.polygon.coordinates[0];
              const latLngs = polygonCoords.map(
                (coord: number[]) => [coord[1], coord[0]] as [number, number]
              );

              const polygon = L.polygon(latLngs, {
                color: isSelected ? '#1e40af' : '#ffffff',
                weight: isSelected ? 3 : 2,
                fillColor: color,
                fillOpacity: 0.7,
              });

              // Sanitize popup content
              const safeNameAr = DOMPurify.sanitize(String(fieldItem.nameAr || fieldItem.name), { ALLOWED_TAGS: [] });
              const safeCrop = DOMPurify.sanitize(String(fieldItem.cropAr || fieldItem.crop || '-'), { ALLOWED_TAGS: [] });
              const safeArea = DOMPurify.sanitize(String(fieldItem.area?.toFixed(2) || '0'), { ALLOWED_TAGS: [] });
              const safeNdvi = fieldItem.ndviValue !== undefined
                ? DOMPurify.sanitize(String(fieldItem.ndviValue.toFixed(2)), { ALLOWED_TAGS: [] })
                : 'N/A';

              const popupContent = DOMPurify.sanitize(`
                <div style="direction: rtl; text-align: right; min-width: 200px; font-family: system-ui, -apple-system, sans-serif;">
                  <h3 style="margin: 0 0 8px 0; font-weight: bold; font-size: 14px; color: #1f2937;">${safeNameAr}</h3>
                  <div style="font-size: 12px; color: #4b5563;">
                    <p style="margin: 4px 0;">المحصول: <strong>${safeCrop}</strong></p>
                    <p style="margin: 4px 0;">المساحة: <strong>${safeArea} هكتار</strong></p>
                    <p style="margin: 4px 0;">NDVI: <strong style="color: ${color}">${safeNdvi}</strong></p>
                    <p style="margin: 8px 0 0 0;">
                      <span style="display: inline-block; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; background-color: ${color}20; color: ${color};">
                        ${healthStatus.labelAr}
                      </span>
                    </p>
                  </div>
                </div>
              `, {
                ALLOWED_TAGS: ['div', 'h3', 'p', 'strong', 'span'],
                ALLOWED_ATTR: ['style'],
              });

              polygon.bindPopup(popupContent);

              polygon.on('click', () => {
                onFieldClick?.(fieldItem.id);
              });

              polygon.addTo(mapInstanceRef.current);
              layersRef.current.push(polygon);

              // Add to bounds
              latLngs.forEach((ll) => bounds.push(ll));

            } else if (fieldItem.centroid) {
              // If no polygon, use centroid marker
              const lat = fieldItem.centroid.coordinates[1];
              const lng = fieldItem.centroid.coordinates[0];

              const iconHtml = `
                <div style="
                  background-color: ${color};
                  width: ${isSelected ? 36 : 28}px;
                  height: ${isSelected ? 36 : 28}px;
                  border-radius: 50%;
                  border: 3px solid ${isSelected ? '#1e40af' : '#ffffff'};
                  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                  display: flex;
                  align-items: center;
                  justify-content: center;
                ">
                  <span style="font-size: 14px;">🌾</span>
                </div>
              `;

              const customIcon = L.divIcon({
                html: iconHtml,
                className: 'custom-field-marker',
                iconSize: [isSelected ? 36 : 28, isSelected ? 36 : 28],
                iconAnchor: [isSelected ? 18 : 14, isSelected ? 18 : 14],
              });

              const safeNameAr = DOMPurify.sanitize(String(fieldItem.nameAr || fieldItem.name), { ALLOWED_TAGS: [] });
              const safeCrop = DOMPurify.sanitize(String(fieldItem.cropAr || fieldItem.crop || '-'), { ALLOWED_TAGS: [] });
              const safeArea = DOMPurify.sanitize(String(fieldItem.area?.toFixed(2) || '0'), { ALLOWED_TAGS: [] });

              const popupContent = DOMPurify.sanitize(`
                <div style="direction: rtl; text-align: right; min-width: 180px;">
                  <h3 style="margin: 0 0 8px 0; font-weight: bold;">${safeNameAr}</h3>
                  <p style="margin: 4px 0; font-size: 12px;">المحصول: ${safeCrop}</p>
                  <p style="margin: 4px 0; font-size: 12px;">المساحة: ${safeArea} هكتار</p>
                </div>
              `, {
                ALLOWED_TAGS: ['div', 'h3', 'p'],
                ALLOWED_ATTR: ['style'],
              });

              const marker = L.marker([lat, lng], { icon: customIcon })
                .bindPopup(popupContent);

              marker.on('click', () => {
                onFieldClick?.(fieldItem.id);
              });

              marker.addTo(mapInstanceRef.current);
              layersRef.current.push(marker);

              bounds.push([lat, lng]);
            }
          });

          // Fit map to show all fields
          if (bounds.length > 0) {
            const leafletBounds = L.latLngBounds(bounds);
            mapInstanceRef.current.fitBounds(leafletBounds, { padding: [50, 50] });
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing map:', error);
        setMapError('حدث خطأ في تحميل الخريطة');
        setIsLoading(false);
      }
    };

    initMap();

    return () => {
      // Cleanup layers
      layersRef.current.forEach((layer) => layer.remove());
      layersRef.current = [];
    };
  }, [displayFields, selectedFieldId, onFieldClick, showControls]);

  // Cleanup map on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center">
          <Loader2 className="w-10 h-10 animate-spin text-green-600 mb-3" />
          <p className="text-gray-600">جاري تحميل الخريطة...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (mapError) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center text-center p-4">
          <MapPin className="w-12 h-12 text-gray-400 mb-3" />
          <p className="text-gray-600 font-medium">{mapError}</p>
          <p className="text-sm text-gray-500 mt-1">يرجى التحقق من اتصال الإنترنت</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="bg-white rounded-xl border border-gray-200 overflow-hidden relative shadow-sm"
      style={{ height }}
    >
      {/* Map Container */}
      <div ref={mapRef} className="w-full h-full" />

      {/* Legend */}
      {showLegend && (
        <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3 z-[1000]">
          <div className="flex items-center gap-1.5 mb-2">
            <Layers className="w-4 h-4 text-gray-600" />
            <h4 className="text-xs font-bold text-gray-700">مؤشر NDVI</h4>
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#15803d' }}></span>
              <span>ممتاز (≥0.7)</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#22c55e' }}></span>
              <span>جيد (0.5-0.7)</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#eab308' }}></span>
              <span>متوسط (0.3-0.5)</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#f97316' }}></span>
              <span>ضعيف (0.1-0.3)</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#ef4444' }}></span>
              <span>حرج (&lt;0.1)</span>
            </div>
          </div>
        </div>
      )}

      {/* Field count badge */}
      {displayFields.length > 0 && (
        <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-md px-3 py-1.5 z-[1000]">
          <span className="text-sm font-medium text-gray-700">
            {displayFields.length} حقل
          </span>
        </div>
      )}

      {/* Empty state overlay */}
      {displayFields.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50/80 z-[500]">
          <div className="text-center">
            <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600 font-medium">لا توجد حقول للعرض</p>
            <p className="text-sm text-gray-500">أضف حقولاً لعرضها على الخريطة</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to load Leaflet dynamically
async function loadLeaflet(): Promise<void> {
  return new Promise((resolve, reject) => {
    // Check if already loaded
    if (window.L) {
      resolve();
      return;
    }

    // Load CSS
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    cssLink.crossOrigin = '';
    document.head.appendChild(cssLink);

    // Load JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Leaflet'));
    document.head.appendChild(script);
  });
}

export default FieldMap;
