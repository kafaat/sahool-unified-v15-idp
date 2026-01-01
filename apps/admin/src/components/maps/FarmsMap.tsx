'use client';

// Sahool Farms Map Component
// خريطة المزارع التفاعلية

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { getHealthScoreColor } from '@/lib/utils';

// Minimal interface for map farms - compatible with both Farm and MapFarm types
export interface BaseFarmData {
  id: string;
  name?: string;
  nameAr?: string;
  coordinates: { lat: number; lng: number };
  healthScore: number;
  area: number;
  crops: string[];
  governorate?: string;
  status?: string;
}

// Dynamic import for Leaflet (SSR not supported)
// Using type assertions to preserve react-leaflet prop types
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
) as any;
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
) as any;
const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
) as any;
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
) as any;
const CircleMarker = dynamic(
  () => import('react-leaflet').then((mod) => mod.CircleMarker),
  { ssr: false }
) as any;

interface FarmsMapProps<T extends BaseFarmData = BaseFarmData> {
  farms: T[];
  onFarmClick?: (farm: T) => void;
  selectedFarmId?: string;
  showHealthOverlay?: boolean;
  className?: string;
}

// Yemen center coordinates
const YEMEN_CENTER: [number, number] = [15.5527, 48.5164];
const DEFAULT_ZOOM = 6;

export default function FarmsMap<T extends BaseFarmData = BaseFarmData>({
  farms,
  onFarmClick,
  selectedFarmId,
  showHealthOverlay = true,
  className = '',
}: FarmsMapProps<T>) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const getMarkerColor = (healthScore: number): string => {
    if (healthScore >= 80) return '#22c55e'; // green
    if (healthScore >= 60) return '#eab308'; // yellow
    if (healthScore >= 40) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  if (!isMounted) {
    return (
      <div className={`bg-gray-100 animate-pulse rounded-lg ${className}`}>
        <div className="flex items-center justify-center h-full min-h-[400px]">
          <p className="text-gray-500">جاري تحميل الخريطة...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative rounded-lg overflow-hidden ${className}`}>
      {/* Map Legend */}
      <div className="absolute top-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-3">
        <h4 className="text-sm font-semibold mb-2 text-gray-700">مستوى الصحة</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            <span>ممتاز (80%+)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
            <span>جيد (60-79%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-orange-500"></span>
            <span>متوسط (40-59%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span>ضعيف (&lt;40%)</span>
          </div>
        </div>
      </div>

      <MapContainer
        center={YEMEN_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', minHeight: '500px', width: '100%' }}
        scrollWheelZoom={true}
      >
        {/* Base tile layer - OpenStreetMap */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Farm markers */}
        {farms.map((farm) => (
          <CircleMarker
            key={farm.id}
            center={[farm.coordinates.lat, farm.coordinates.lng]}
            radius={selectedFarmId === farm.id ? 12 : 8}
            fillColor={showHealthOverlay ? getMarkerColor(farm.healthScore) : '#3b82f6'}
            color={selectedFarmId === farm.id ? '#1e40af' : '#ffffff'}
            weight={selectedFarmId === farm.id ? 3 : 2}
            fillOpacity={0.8}
            eventHandlers={{
              click: () => onFarmClick?.(farm),
            }}
          >
            <Popup>
              <div className="text-right font-arabic" dir="rtl">
                <h3 className="font-bold text-lg mb-2">{farm.nameAr || farm.name || 'مزرعة'}</h3>
                <div className="space-y-1 text-sm">
                  {farm.governorate && (
                    <p>
                      <span className="text-gray-500">المحافظة:</span>{' '}
                      <span className="font-medium">{farm.governorate}</span>
                    </p>
                  )}
                  <p>
                    <span className="text-gray-500">المساحة:</span>{' '}
                    <span className="font-medium">{farm.area.toFixed(1)} هكتار</span>
                  </p>
                  <p>
                    <span className="text-gray-500">المحاصيل:</span>{' '}
                    <span className="font-medium">{farm.crops.join(', ')}</span>
                  </p>
                  <p>
                    <span className="text-gray-500">مستوى الصحة:</span>{' '}
                    <span className={`font-bold px-2 py-0.5 rounded ${getHealthScoreColor(farm.healthScore)}`}>
                      {farm.healthScore}%
                    </span>
                  </p>
                </div>
                <button
                  onClick={() => onFarmClick?.(farm)}
                  className="mt-3 w-full bg-sahool-600 text-white py-1 px-3 rounded text-sm hover:bg-sahool-700 transition-colors"
                >
                  عرض التفاصيل
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
