"use client";

// Sahool Farms Map Component - Fixed for React re-renders
// خريطة المزارع التفاعلية
// Updated: satellite toggle, polygon boundaries, enhanced Arabic UI

import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { getHealthScoreColor } from "@/lib/utils";

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
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false, loading: () => <MapLoadingFallback /> },
) as any;
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false, loading: () => null },
) as any;
const CircleMarker = dynamic(
  () => import("react-leaflet").then((mod) => mod.CircleMarker),
  { ssr: false, loading: () => null },
) as any;
const Polygon = dynamic(
  () => import("react-leaflet").then((mod) => mod.Polygon),
  { ssr: false, loading: () => null },
) as any;
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), {
  ssr: false,
  loading: () => null,
}) as any;
const LayersControl = dynamic(
  () => import("react-leaflet").then((mod) => mod.LayersControl),
  { ssr: false, loading: () => null },
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

/**
 * Get Arabic health status label
 */
const getHealthLabel = (score: number): string => {
  if (score >= 80) return "ممتاز";
  if (score >= 60) return "جيد";
  if (score >= 40) return "متوسط";
  if (score >= 20) return "ضعيف";
  return "حرج";
};

export default function FarmsMap<T extends BaseFarmData = BaseFarmData>({
  farms,
  onFarmClick,
  selectedFarmId,
  showHealthOverlay = true,
  className = "",
}: FarmsMapProps<T>) {
  const [isMounted, setIsMounted] = useState(false);
  const [mapVersion, setMapVersion] = useState(0);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);

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
        if ((containerRef as any)._leaflet_id) {
          delete (containerRef as any)._leaflet_id;
        }
      }
    };
  }, []);

  const getMarkerColor = (healthScore: number): string => {
    if (healthScore >= 80) return "#1B5E20"; // dark green - excellent
    if (healthScore >= 60) return "#4CAF50"; // green - good
    if (healthScore >= 40) return "#FDD835"; // yellow - moderate
    if (healthScore >= 20) return "#FF9800"; // orange - poor
    return "#F44336"; // red - critical
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
    <div
      ref={mapContainerRef}
      className={`relative rounded-lg overflow-hidden ${className}`}
    >
      {/* Map Legend */}
      <div className="absolute top-4 left-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3">
        <h4 className="text-sm font-semibold mb-2 text-gray-700">
          مستوى الصحة
        </h4>
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

      {/* Farm count badge */}
      <div className="absolute top-4 right-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg shadow-lg px-3 py-2">
        <p className="text-xs text-gray-700 font-medium">
          {farms.length} مزرعة
        </p>
      </div>

      <MapContainer
        center={YEMEN_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: "100%", minHeight: "500px", width: "100%" }}
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
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="صور الأقمار الصناعية">
            <TileLayer
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="التضاريس">
            <TileLayer
              attribution='&copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
              url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {/* Farm markers - polygon boundaries where available, circle markers as fallback */}
        {farms.map((farm) => {
          const markerColor = showHealthOverlay
            ? getMarkerColor(farm.healthScore)
            : "#3b82f6";

          // Render polygon boundary if available
          if (farm.boundary && farm.boundary.length > 0) {
            // Convert GeoJSON [lng, lat] to Leaflet [lat, lng]
            const positions = farm.boundary.map((ring) =>
              ring.map(([lng, lat]: number[]) => [lat, lng] as [number, number]),
            );

            return (
              <Polygon
                key={farm.id}
                positions={positions}
                pathOptions={{
                  color: selectedFarmId === farm.id ? "#1e40af" : markerColor,
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
                      {farm.nameAr || farm.name || "مزرعة"}
                    </h3>
                    <div className="space-y-1 text-sm">
                      {farm.governorate && (
                        <p>
                          <span className="text-gray-500">المحافظة:</span>{" "}
                          <span className="font-medium">
                            {farm.governorate}
                          </span>
                        </p>
                      )}
                      <p>
                        <span className="text-gray-500">المساحة:</span>{" "}
                        <span className="font-medium">
                          {farm.area.toFixed(1)} هكتار
                        </span>
                      </p>
                      <p>
                        <span className="text-gray-500">المحاصيل:</span>{" "}
                        <span className="font-medium">
                          {farm.crops.join(", ")}
                        </span>
                      </p>
                      <p>
                        <span className="text-gray-500">مستوى الصحة:</span>{" "}
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
              color={selectedFarmId === farm.id ? "#1e40af" : "#ffffff"}
              weight={selectedFarmId === farm.id ? 3 : 2}
              fillOpacity={0.8}
              eventHandlers={{
                click: () => onFarmClick?.(farm),
              }}
            >
              <Popup>
                <div className="text-right font-arabic">
                  <h3 className="font-bold text-lg mb-2">
                    {farm.nameAr || farm.name || "مزرعة"}
                  </h3>
                  <div className="space-y-1 text-sm">
                    {farm.governorate && (
                      <p>
                        <span className="text-gray-500">المحافظة:</span>{" "}
                        <span className="font-medium">{farm.governorate}</span>
                      </p>
                    )}
                    <p>
                      <span className="text-gray-500">المساحة:</span>{" "}
                      <span className="font-medium">
                        {farm.area.toFixed(1)} هكتار
                      </span>
                    </p>
                    <p>
                      <span className="text-gray-500">المحاصيل:</span>{" "}
                      <span className="font-medium">
                        {farm.crops.join(", ")}
                      </span>
                    </p>
                    <p>
                      <span className="text-gray-500">مستوى الصحة:</span>{" "}
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
