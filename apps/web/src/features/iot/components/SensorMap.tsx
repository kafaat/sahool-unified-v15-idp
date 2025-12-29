/**
 * Sensor Map Component
 * مكون خريطة المستشعرات
 */

'use client';

import { useEffect, useRef } from 'react';
import DOMPurify from 'dompurify';
import { useSensors } from '../hooks/useSensors';
import { MapPin, Loader2 } from 'lucide-react';

// Leaflet type definition for CDN-loaded library
declare global {
  interface Window {
    L?: typeof import('leaflet');
  }
}

const typeLabels = {
  soil_moisture: 'رطوبة التربة',
  temperature: 'درجة الحرارة',
  humidity: 'الرطوبة',
  ph: 'الحموضة',
  light: 'الإضاءة',
  pressure: 'الضغط',
  rain: 'المطر',
  wind: 'الرياح',
};

export function SensorMap() {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const { data: sensors, isLoading } = useSensors();

  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    // Initialize map
    const initMap = async () => {
      // Check if Leaflet is loaded
      if (typeof window === 'undefined' || !window.L) {
        console.warn('Leaflet library not loaded');
        return;
      }
      const L = window.L;

      // Create map if it doesn't exist
      if (!mapInstanceRef.current && mapRef.current) {
        const map = L.map(mapRef.current).setView([15.5527, 48.5164], 6); // Center of Yemen

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
          maxZoom: 19,
        }).addTo(map);

        mapInstanceRef.current = map;
      }

      // Clear existing markers
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = [];

      // Add sensor markers
      if (sensors && sensors.length > 0) {
        const sensorsWithLocation = sensors.filter((s) => s.location);

        sensorsWithLocation.forEach((sensor) => {
          if (!sensor.location) return;

          const statusColors: Record<string, string> = {
            active: '#16a34a',
            inactive: '#6b7280',
            error: '#dc2626',
            maintenance: '#eab308',
          };

          const iconHtml = `
            <div style="
              background-color: ${statusColors[sensor.status] || '#6b7280'};
              width: 32px;
              height: 32px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 16px;
            ">
              📡
            </div>
          `;

          const customIcon = L.divIcon({
            html: iconHtml,
            className: 'custom-sensor-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
          });

          // Sanitize popup content
          const safeNameAr = DOMPurify.sanitize(String(sensor.nameAr), { ALLOWED_TAGS: [] });
          const safeName = DOMPurify.sanitize(String(sensor.name), { ALLOWED_TAGS: [] });
          const safeType = DOMPurify.sanitize(typeLabels[sensor.type], { ALLOWED_TAGS: [] });
          const safeFieldName = sensor.location.fieldName ? DOMPurify.sanitize(String(sensor.location.fieldName), { ALLOWED_TAGS: [] }) : '';
          const safeReadingValue = sensor.lastReading ? DOMPurify.sanitize(String(sensor.lastReading.value.toFixed(1)), { ALLOWED_TAGS: [] }) : '';
          const safeReadingUnit = sensor.lastReading ? DOMPurify.sanitize(String(sensor.lastReading.unit), { ALLOWED_TAGS: [] }) : '';
          const safeReadingTime = sensor.lastReading ? DOMPurify.sanitize(new Date(sensor.lastReading.timestamp).toLocaleString('ar-YE'), { ALLOWED_TAGS: [] }) : '';
          const safeBattery = sensor.battery !== undefined ? DOMPurify.sanitize(String(sensor.battery), { ALLOWED_TAGS: [] }) : '';

          const popupContent = DOMPurify.sanitize(
            `
            <div style="direction: rtl; text-align: right; min-width: 200px;">
              <h3 style="font-weight: bold; margin-bottom: 8px;">${safeNameAr}</h3>
              <p style="margin: 4px 0; font-size: 0.875rem;">${safeName}</p>
              <p style="margin: 4px 0; font-size: 0.875rem; color: #666;">
                النوع: ${safeType}
              </p>
              ${
                safeFieldName
                  ? `<p style="margin: 4px 0; font-size: 0.875rem; color: #666;">الحقل: ${safeFieldName}</p>`
                  : ''
              }
              ${
                sensor.lastReading
                  ? `
                <div style="margin-top: 8px; padding: 8px; background: #f0fdf4; border-radius: 4px;">
                  <p style="margin: 0; font-weight: 600; color: #16a34a;">
                    ${safeReadingValue} ${safeReadingUnit}
                  </p>
                  <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: #666;">
                    ${safeReadingTime}
                  </p>
                </div>
              `
                  : ''
              }
              ${
                safeBattery
                  ? `<p style="margin: 4px 0; font-size: 0.75rem; color: #666;">البطارية: ${safeBattery}%</p>`
                  : ''
              }
            </div>
          `,
            {
              ALLOWED_TAGS: ['div', 'h3', 'p'],
              ALLOWED_ATTR: ['style'],
            }
          );

          const marker = L.marker([sensor.location.latitude, sensor.location.longitude], {
            icon: customIcon,
          })
            .addTo(mapInstanceRef.current)
            .bindPopup(popupContent);

          markersRef.current.push(marker);
        });

        // Fit map to show all markers
        if (sensorsWithLocation.length > 0) {
          const bounds = L.latLngBounds(
            sensorsWithLocation.map((s) => [s.location!.latitude, s.location!.longitude])
          );
          mapInstanceRef.current.fitBounds(bounds, { padding: [50, 50] });
        }
      }
    };

    initMap();

    return () => {
      // Cleanup markers
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = [];
    };
  }, [sensors]);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="mr-3 text-gray-600">جاري تحميل الخريطة...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <MapPin className="w-5 h-5 ml-2 text-green-600" />
          مواقع المستشعرات
        </h2>
      </div>
      <div ref={mapRef} className="h-96 w-full" />

      {/* Legend */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-green-600 ml-2"></div>
            <span>نشط</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-gray-600 ml-2"></div>
            <span>غير نشط</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-red-600 ml-2"></div>
            <span>خطأ</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-yellow-600 ml-2"></div>
            <span>صيانة</span>
          </div>
        </div>
      </div>
    </div>
  );
}
