'use client';

// Sahool Farms Map Component - Fixed for React re-renders
// خريطة المزارع التفاعلية
// Updated: satellite toggle, polygon boundaries, enhanced Arabic UI

import { useEffect, useState, useRef } from 'react';
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
  boundary?: number[][][]; // GeoJSON polygon coordinates [[[lng,lat],...]]
}

// Loading fallback component for map imports
const MapLoadingFallback = () => (
  <div className="h-full bg-gray-100 animate-pulse flex items-center justify-center min-h-[100px]">
    <p className="text-gray-500 text-sm">جاري تحميل...</p>
  </div>
);

// Dynamic import for Leaflet (SSR not supported)
// react-leaflet components have complex generic types that are incompatible with
// next/dynamic's return type. The `as any` is intentional and widely accepted.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const MapContainer = dynamic(() => import('react-leaflet').then((mod) => mod.MapContainer), {
  ssr: false,
  loading: () => <MapLoadingFallback />,
}) as any; // eslint-disable-line @typescript-eslint/no-explicit-any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const TileLayer = dynamic(() => import('react-leaflet').then((mod) => mod.TileLayer), {
  ssr: false,
  loading: () => null,
}) as any; // eslint-disable-line @typescript-eslint/no-explicit-any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CircleMarker = dynamic(() => import('react-leaflet').then((mod) => mod.CircleMarker), {
  ssr: false,
  loading: () => null,
}) as any; // eslint-disable-line @typescript-eslint/no-explicit-any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Polygon = dynamic(() => import('react-leaflet').then((mod) => mod.Polygon), {
  ssr: false,
  loading: () => null,
}) as any; // eslint-disable-line @typescript-eslint/no-explicit-any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Popup = dynamic(() => import('react-leaflet').then((mod) => mod.Popup), {
  ssr: false,
  loading: () => null,
}) as any; // eslint-disable-line @typescript-eslint/no-explicit-any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const LayersControl = dynamic(() => import('react-leaflet').then((mod) => mod.LayersControl), {
  ssr: false,
  loading: () => null,
}) as any; // eslint-disable-line @typescript-eslint/no-explicit-any

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

/**
 * Get Arabic health status label
 */
const getHealthLabel = (score: number): string => {
  if (score >= 90) return 'ممتاز';
  if (score >= 80) return 'صحي جداً';
  if (score >= 65) return 'صحي';
  if (score >= 50) return 'معتدل';
  if (score >= 40) return 'مجهد';
  if (score >= 25) return 'مجهد جداً';
  if (score >= 15) return 'حرج';
  return 'تربة عارية';
};

export default function FarmsMap<T extends BaseFarmData = BaseFarmData>({
  farms,
  onFarmClick,
  selectedFarmId,
  showHealthOverlay = true,
  className = '',
}: FarmsMapProps<T>) {
  const [isMounted, setIsMounted] = useState(false);
  const [mapVersion, setMapVersion] = useState(0);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<import('leaflet').Map | null>(null);

  useEffect(() => {
    setIsMounted(true);
    // Increment version to force new map instance on mount
    setMapVersion((v) => v + 1);

    // Capture ref value for cleanup (React lint rule)
    const containerRef = mapContainerRef.current;

    // Cleanup function to remove any existing Leaflet instances
    return () => {
      // Clean up the map instance if it exists
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove();
          mapInstanceRef.current = null;
        } catch {
          // Ignore errors during cleanup
        }
      }

      // Force cleanup of Leaflet's internal tracker
      if (containerRef) {
        // Remove any Leaflet-specific properties to prevent "Map container already initialized"
        // Leaflet stores _leaflet_id on the DOM element which is not part of HTMLElement types
        const leafletEl = containerRef as HTMLElement & { _leaflet_id?: number };
        if (leafletEl._leaflet_id) {
          delete leafletEl._leaflet_id;
        }
      }
    };
  }, []);

  const getMarkerColor = (healthScore: number): string => {
    if (healthScore >= 90) return '#004d00'; // very dark green - excellent
    if (healthScore >= 80) return '#1B5E20'; // dark green - very healthy
    if (healthScore >= 65) return '#4CAF50'; // green - healthy
    if (healthScore >= 50) return '#8BC34A'; // light green - moderate
    if (healthScore >= 40) return '#FDD835'; // yellow - stressed
    if (healthScore >= 25) return '#FF9800'; // orange - very stressed
    if (healthScore >= 15) return '#F44336'; // red - critical
    return '#8B0000'; // dark red - bare soil/dead
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
    <div ref={mapContainerRef} className={`relative rounded-lg overflow-hidden ${className}`}>
      {/* Map Legend */}
      <div className="absolute top-4 left-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3">
        <h4 className="text-sm font-semibold mb-2 text-gray-700">مستوى الصحة</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#004d00' }}></span>
            <span>ممتاز (90%+)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#1B5E20' }}></span>
            <span>صحي جداً (80-89%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#4CAF50' }}></span>
            <span>صحي (65-79%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#8BC34A' }}></span>
            <span>معتدل (50-64%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#FDD835' }}></span>
            <span>مجهد (40-49%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#FF9800' }}></span>
            <span>مجهد جداً (25-39%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#F44336' }}></span>
            <span>حرج (15-24%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#8B0000' }}></span>
            <span>تربة عارية (&lt;15%)</span>
          </div>
        </div>
      </div>

      {/* Farm count badge */}
      <div className="absolute top-4 right-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg shadow-lg px-3 py-2">
        <p className="text-xs text-gray-700 font-medium">{farms.length} مزرعة</p>
      </div>

      <MapContainer
        center={YEMEN_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', minHeight: '500px', width: '100%' }}
        scrollWheelZoom={true}
        // Force new instance on every mount using version counter
        key={`map-${mapVersion}`}
        ref={(map: any) => {
          if (map) {
            mapInstanceRef.current = map;
          }
        }}
      >
        {/* Base Layers with satellite option */}
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="خريطة الشوارع">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              errorTileUrl="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mN88P/BfwAJhAPk3KErzgAAAABJRU5ErkJggg=="
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="صور الأقمار الصناعية">
            <TileLayer
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              errorTileUrl="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mN88P/BfwAJhAPk3KErzgAAAABJRU5ErkJggg=="
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="التضاريس">
            <TileLayer
              attribution='&copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
              url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
              errorTileUrl="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mN88P/BfwAJhAPk3KErzgAAAABJRU5ErkJggg=="
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {/* Farm markers - polygon boundaries where available, circle markers as fallback */}
        {farms.map((farm) => {
          const markerColor = showHealthOverlay ? getMarkerColor(farm.healthScore) : '#3b82f6';

          // Render polygon boundary if available
          if (farm.boundary && farm.boundary.length > 0) {
            // Convert GeoJSON [lng, lat] to Leaflet [lat, lng]
            const positions = farm.boundary.map((ring) =>
              ring.map(([lng, lat]: number[]) => [lat, lng] as [number, number])
            );

            return (
              <Polygon
                key={farm.id}
                positions={positions}
                pathOptions={{
                  color: selectedFarmId === farm.id ? '#1e40af' : markerColor,
                  fillColor: markerColor,
                  fillOpacity: selectedFarmId === farm.id ? 0.5 : 0.3,
                  weight: selectedFarmId === farm.id ? 3 : 2,
                }}
                eventHandlers={{
                  click: () => onFarmClick?.(farm),
                }}
              >
                <Popup>
                  <div className="text-right font-arabic">
                    <h3 className="font-bold text-lg mb-2">
                      {farm.nameAr || farm.name || 'مزرعة'}
                    </h3>
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
                        <span
                          className={`font-bold px-2 py-0.5 rounded ${getHealthScoreColor(farm.healthScore)}`}
                        >
                          {farm.healthScore}% - {getHealthLabel(farm.healthScore)}
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
              </Polygon>
            );
          }

          // Fallback to circle marker
          return (
            <CircleMarker
              key={farm.id}
              center={[farm.coordinates.lat, farm.coordinates.lng]}
              radius={selectedFarmId === farm.id ? 12 : 8}
              fillColor={markerColor}
              color={selectedFarmId === farm.id ? '#1e40af' : '#ffffff'}
              weight={selectedFarmId === farm.id ? 3 : 2}
              fillOpacity={0.8}
              eventHandlers={{
                click: () => onFarmClick?.(farm),
              }}
            >
              <Popup>
                <div className="text-right font-arabic">
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
                      <span
                        className={`font-bold px-2 py-0.5 rounded ${getHealthScoreColor(farm.healthScore)}`}
                      >
                        {farm.healthScore}% - {getHealthLabel(farm.healthScore)}
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
          );
        })}
      </MapContainer>
    </div>
  );
}
