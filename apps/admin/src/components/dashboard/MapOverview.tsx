"use client";

// Map Overview Component
// نظرة عامة على الخريطة

import { useState } from "react";
import dynamic from "next/dynamic";
import { MapPin, Layers, Eye, EyeOff } from "lucide-react";
import Link from "next/link";

// Dynamic import for map (no SSR)
const InteractiveMap = dynamic(() => import("@/components/maps/FarmsMap"), {
  ssr: false,
  loading: () => (
    <div className="h-full bg-gray-100 animate-pulse flex items-center justify-center">
      <p className="text-gray-500">جاري تحميل الخريطة...</p>
    </div>
  ),
});

export interface MapFarm {
  id: string;
  name?: string;
  nameAr?: string;
  coordinates: { lat: number; lng: number };
  healthScore: number;
  area: number;
  crops: string[];
  status?: string;
  // Optional properties for Farm type compatibility
  governorate?: string;
  ownerId?: string;
  lastUpdated?: string;
  createdAt?: string;
}

interface MapOverviewProps {
  farms: MapFarm[];
  height?: string;
  showHealthOverlay?: boolean;
  showControls?: boolean;
  onFarmClick?: (farm: MapFarm) => void;
  selectedFarmId?: string;
  className?: string;
}

export default function MapOverview({
  farms,
  height = "500px",
  showHealthOverlay = true,
  showControls = true,
  onFarmClick,
  selectedFarmId,
  className = "",
}: MapOverviewProps) {
  const [overlayEnabled, setOverlayEnabled] = useState(showHealthOverlay);
  const [mapView, setMapView] = useState<"satellite" | "standard">("standard");

  const healthyFarms = farms.filter((f) => f.healthScore >= 70).length;
  const warningFarms = farms.filter(
    (f) => f.healthScore >= 50 && f.healthScore < 70,
  ).length;
  const criticalFarms = farms.filter((f) => f.healthScore < 50).length;

  return (
    <div
      className={`bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-sahool-600" />
          <h2 className="font-bold text-gray-900">خريطة المزارع</h2>
        </div>

        {showControls && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setOverlayEnabled(!overlayEnabled)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 ${
                overlayEnabled
                  ? "bg-sahool-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
              title={overlayEnabled ? "إخفاء طبقة الصحة" : "عرض طبقة الصحة"}
            >
              {overlayEnabled ? (
                <Eye className="w-3 h-3" />
              ) : (
                <EyeOff className="w-3 h-3" />
              )}
              طبقة الصحة
            </button>

            <select
              value={mapView}
              onChange={(e) =>
                setMapView(e.target.value as "satellite" | "standard")
              }
              className="px-3 py-1.5 text-xs font-medium border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            >
              <option value="standard">خريطة عادية</option>
              <option value="satellite">صور الأقمار</option>
            </select>

            <Link
              href="/farms"
              className="px-3 py-1.5 text-xs font-medium text-sahool-600 hover:text-sahool-700"
            >
              عرض الكل ←
            </Link>
          </div>
        )}
      </div>

      {/* Health Statistics Bar */}
      {overlayEnabled && (
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-100">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-600">
                صحي:{" "}
                <span className="font-medium text-gray-900">
                  {healthyFarms}
                </span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-gray-600">
                تحذير:{" "}
                <span className="font-medium text-gray-900">
                  {warningFarms}
                </span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-gray-600">
                حرج:{" "}
                <span className="font-medium text-gray-900">
                  {criticalFarms}
                </span>
              </span>
            </div>
            <div className="mr-auto text-gray-500">
              إجمالي المزارع:{" "}
              <span className="font-medium text-gray-900">{farms.length}</span>
            </div>
          </div>
        </div>
      )}

      {/* Map */}
      <div style={{ height }}>
        <InteractiveMap
          farms={farms}
          onFarmClick={onFarmClick}
          selectedFarmId={selectedFarmId}
          showHealthOverlay={overlayEnabled}
        />
      </div>

      {/* Legend */}
      {overlayEnabled && (
        <div className="p-3 bg-gray-50 border-t border-gray-100">
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Layers className="w-3 h-3" />
            <span>الألوان تمثل مستوى صحة المحصول:</span>
            <span className="text-green-600 font-medium">أخضر (70-100)</span>
            <span>•</span>
            <span className="text-yellow-600 font-medium">أصفر (50-69)</span>
            <span>•</span>
            <span className="text-red-600 font-medium">أحمر (&lt;50)</span>
          </div>
        </div>
      )}
    </div>
  );
}
