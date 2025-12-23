/**
 * Equipment Map Component
 * مكون خريطة المعدات
 */

'use client';

import { useEffect, useRef } from 'react';
import { useEquipment } from '../hooks/useEquipment';
import type { Equipment } from '../types';
import { MapPin, Loader2 } from 'lucide-react';

export function EquipmentMap() {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const { data: equipment, isLoading } = useEquipment();

  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    // Initialize map
    const initMap = async () => {
      // @ts-ignore - Leaflet is loaded via CDN
      const L = window.L;
      if (!L) return;

      // Create map if it doesn't exist
      if (!mapInstanceRef.current) {
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

      // Add equipment markers
      if (equipment && equipment.length > 0) {
        const equipmentWithLocation = equipment.filter((e) => e.location);

        equipmentWithLocation.forEach((item) => {
          if (!item.location) return;

          const statusColors: Record<string, string> = {
            active: 'green',
            maintenance: 'yellow',
            repair: 'orange',
            idle: 'gray',
            retired: 'red',
          };

          const iconHtml = `
            <div style="
              background-color: ${statusColors[item.status] || 'gray'};
              width: 30px;
              height: 30px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>
          `;

          const customIcon = L.divIcon({
            html: iconHtml,
            className: 'custom-equipment-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          });

          const marker = L.marker([item.location.latitude, item.location.longitude], {
            icon: customIcon,
          })
            .addTo(mapInstanceRef.current)
            .bindPopup(
              `
              <div style="direction: rtl; text-align: right;">
                <h3 style="font-weight: bold; margin-bottom: 8px;">${item.nameAr}</h3>
                <p style="margin: 4px 0;">${item.name}</p>
                ${
                  item.location.fieldName
                    ? `<p style="margin: 4px 0; font-size: 0.875rem; color: #666;">الحقل: ${item.location.fieldName}</p>`
                    : ''
                }
                <p style="margin: 4px 0; font-size: 0.875rem;">
                  الحالة: <span style="font-weight: 600;">${getStatusLabel(item.status)}</span>
                </p>
              </div>
            `
            );

          markersRef.current.push(marker);
        });

        // Fit map to show all markers
        if (equipmentWithLocation.length > 0) {
          const bounds = L.latLngBounds(
            equipmentWithLocation.map((e) => [e.location!.latitude, e.location!.longitude])
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
  }, [equipment]);

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
          مواقع المعدات
        </h2>
      </div>
      <div ref={mapRef} className="h-96 w-full" />

      {/* Legend */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-green-500 ml-2"></div>
            <span>نشط</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-yellow-500 ml-2"></div>
            <span>صيانة</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-orange-500 ml-2"></div>
            <span>إصلاح</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-gray-500 ml-2"></div>
            <span>خامل</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded-full bg-red-500 ml-2"></div>
            <span>متوقف</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: 'نشط',
    maintenance: 'صيانة',
    repair: 'إصلاح',
    idle: 'خامل',
    retired: 'متوقف',
  };
  return labels[status] || status;
}
