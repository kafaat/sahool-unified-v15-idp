/**
 * Sensor Map Component
 * مكون خريطة المستشعرات
 */

'use client';

import { useEffect, useRef } from 'react';
import { useSensors } from '../hooks/useSensors';
import { MapPin, Loader2 } from 'lucide-react';

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

/**
 * Escape HTML special characters to prevent XSS when injecting
 * user-controlled sensor data into Leaflet popup HTML templates.
 * هروب أحرف HTML لمنع هجمات XSS عند إدراج بيانات المستشعرات
 */
function escapeHtml(value: unknown): string {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function SensorMap() {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const { data: sensors, isLoading } = useSensors();

  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    // Initialize map
    const initMap = async () => {
      // Access Leaflet from window (loaded via CDN in layout)
      const L = (window as typeof window & { L?: any }).L;
      if (!L) return;

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
            online: '#16a34a',
            inactive: '#6b7280',
            offline: '#6b7280',
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

          // Sanitize all user-controlled fields before injecting into HTML
          // to prevent stored XSS via sensor name/field name/unit values.
          const safeNameAr = escapeHtml(sensor.nameAr);
          const safeName = escapeHtml(sensor.name);
          const safeTypeLabel = escapeHtml(
            (typeLabels as Record<string, string>)[sensor.type] ?? sensor.type
          );
          const safeFieldName = escapeHtml(sensor.location.fieldName);
          const readingValue = sensor.lastReading?.value;
          const safeReadingValue = escapeHtml(
            typeof readingValue === 'number' && Number.isFinite(readingValue)
              ? readingValue.toFixed(1)
              : '-'
          );
          const safeReadingUnit = escapeHtml(sensor.lastReading?.unit ?? '');
          const safeReadingTime = sensor.lastReading
            ? escapeHtml(new Date(sensor.lastReading.timestamp).toLocaleString('ar-YE'))
            : '';
          const safeBattery = escapeHtml(sensor.battery);

          const marker = L.marker([sensor.location.latitude, sensor.location.longitude], {
            icon: customIcon,
          })
            .addTo(mapInstanceRef.current)
            .bindPopup(
              `
              <div style="direction: rtl; text-align: right; min-width: 200px;">
                <h3 style="font-weight: bold; margin-bottom: 8px;">${safeNameAr}</h3>
                <p style="margin: 4px 0; font-size: 0.875rem;">${safeName}</p>
                <p style="margin: 4px 0; font-size: 0.875rem; color: #666;">
                  النوع: ${safeTypeLabel}
                </p>
                ${
                  sensor.location.fieldName
                    // nosemgrep: javascript.lang.security.audit.xss.direct-response-write.html-in-template-string,html-in-template-string -- intentional HTML template; user data escaped via esc()
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
                  sensor.battery !== undefined
                    // nosemgrep: javascript.lang.security.audit.xss.direct-response-write.html-in-template-string,html-in-template-string -- intentional HTML template; user data escaped via esc()
                    ? `<p style="margin: 4px 0; font-size: 0.75rem; color: #666;">البطارية: ${safeBattery}%</p>`
                    : ''
                }
              </div>
            `
            );

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
      // Cleanup map instance to prevent "Map container is already initialized" on re-mount
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [sensors]);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="ms-3 text-gray-600">جاري تحميل الخريطة...</span>
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
