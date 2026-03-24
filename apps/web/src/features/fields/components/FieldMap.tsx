"use client";

/**
 * SAHOOL Field Map Component
 * مكون خريطة الحقل
 *
 * Interactive map using React-Leaflet for displaying field boundaries,
 * NDVI coloring, and field details popups.
 */

import React, { useMemo, useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polygon,
  Popup,
  LayersControl,
  ZoomControl,
  CircleMarker,
} from "react-leaflet";
import type { LatLngTuple, LatLngExpression } from "leaflet";
import type { Field, GeoPolygon } from "../types";
import {
  INTERACTION_COLORS,
} from "@/lib/chart-colors";

interface FieldMapProps {
  field?: Field;
  fields?: Field[];
  height?: string;
  onFieldClick?: (fieldId: string) => void;
}

// Yemen center coordinates
const YEMEN_CENTER: LatLngTuple = [15.5527, 48.5164];

/**
 * Get NDVI-based color for field display
 * Uses the same color scale as HealthZonesLayer for cross-component consistency
 */
export const getNDVIColor = (ndvi?: number): string => {
  if (ndvi === undefined || ndvi === null) return "#9ca3af"; // Gray - no data
  if (ndvi >= 0.7) return "#1B5E20"; // Dark green - excellent
  if (ndvi >= 0.5) return "#4CAF50"; // Green - good
  if (ndvi >= 0.3) return "#FDD835"; // Yellow - moderate
  if (ndvi >= 0.15) return "#FF9800"; // Orange - poor
  return "#F44336"; // Red - critical
};

/**
 * Get Arabic health status label
 */
export const getHealthLabel = (ndvi?: number): string => {
  if (ndvi === undefined || ndvi === null) return "غير معروف";
  if (ndvi >= 0.7) return "ممتاز";
  if (ndvi >= 0.5) return "جيد";
  if (ndvi >= 0.3) return "متوسط";
  if (ndvi >= 0.15) return "ضعيف";
  return "حرج";
};

/**
 * Convert GeoPolygon coordinates to Leaflet LatLng format
 * GeoJSON uses [lng, lat], Leaflet uses [lat, lng]
 */
const geoPolygonToLatLng = (polygon: GeoPolygon): LatLngExpression[][] => {
  return polygon.coordinates.map((ring) =>
    ring.map(([lng, lat]) => [lat, lng] as LatLngTuple),
  );
};

export const FieldMap: React.FC<FieldMapProps> = ({
  field,
  fields,
  height = "400px",
  onFieldClick,
}) => {
  const [isMounted, setIsMounted] = useState(false);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const displayFields = useMemo(() => {
    return field ? [field] : fields || [];
  }, [field, fields]);

  // Calculate map center from field data
  const mapCenter = useMemo((): LatLngTuple => {
    if (displayFields.length === 0) return YEMEN_CENTER;

    const firstField = displayFields[0];
    if (firstField?.centroid) {
      const [lng, lat] = firstField.centroid.coordinates;
      return [lat, lng];
    }
    if (firstField?.polygon && firstField.polygon.coordinates.length > 0) {
      const firstRing = firstField.polygon.coordinates[0];
      if (firstRing && firstRing.length > 0) {
        const coords = firstRing[0];
        if (coords && coords.length >= 2) {
          return [coords[1] ?? 15.5527, coords[0] ?? 48.5164];
        }
      }
    }
    return YEMEN_CENTER;
  }, [displayFields]);

  const mapZoom = useMemo(() => {
    if (displayFields.length === 1 && displayFields[0]?.polygon) return 14;
    if (displayFields.length > 0) return 10;
    return 6;
  }, [displayFields]);

  // SSR guard - render loading state on server
  if (!isMounted) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative animate-pulse"
        style={{ height }}
      >
        <div className="w-full h-full flex flex-col items-center justify-center">
          <p className="text-gray-500">جاري تحميل الخريطة...</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative"
      style={{ height }}
    >
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        zoomControl={false}
        className="w-full h-full"
        style={{ height: "100%", width: "100%" }}
      >
        {/* Base Map Layers */}
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
        </LayersControl>

        <ZoomControl position="topleft" />

        {/* Render field polygons or circle markers */}
        {displayFields.map((fieldItem) => {
          const color = getNDVIColor(fieldItem.ndviValue);

          if (fieldItem.polygon) {
            const positions = geoPolygonToLatLng(fieldItem.polygon);
            const isSelected = selectedFieldId === fieldItem.id;
            return (
              <Polygon
                key={fieldItem.id}
                positions={positions}
                pathOptions={{
                  color: isSelected ? INTERACTION_COLORS.selectedBorder : color,
                  fillColor: color,
                  fillOpacity: isSelected ? 0.55 : 0.35,
                  weight: isSelected ? 4 : 2,
                }}
                eventHandlers={{
                  click: () => {
                    setSelectedFieldId((prev) => (prev === fieldItem.id ? null : fieldItem.id));
                    onFieldClick?.(fieldItem.id);
                  },
                  mouseover: (e) => {
                    const layer = e.target;
                    if (!isSelected) {
                      layer.setStyle({ fillOpacity: 0.5, weight: 3 });
                    }
                  },
                  mouseout: (e) => {
                    const layer = e.target;
                    if (!isSelected) {
                      layer.setStyle({ fillOpacity: 0.35, weight: 2 });
                    }
                  },
                }}
                {...({} as any)}
              >
                <Popup>
                  <div className="p-3 min-w-[220px]">
                    <h3 className="font-bold text-gray-900 mb-1 text-base">
                      {fieldItem.nameAr || fieldItem.name}
                    </h3>
                    {fieldItem.name && fieldItem.nameAr && (
                      <p className="text-xs text-gray-500 mb-3">{fieldItem.name}</p>
                    )}
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">المساحة:</span>
                        <span className="font-semibold">
                          {fieldItem.area} هكتار
                        </span>
                      </div>
                      {fieldItem.crop && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">المحصول:</span>
                          <span className="font-semibold">
                            {fieldItem.cropAr || fieldItem.crop}
                          </span>
                        </div>
                      )}
                      {fieldItem.ndviValue !== undefined && (
                        <>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-600">NDVI:</span>
                            <span className="font-semibold">
                              {fieldItem.ndviValue.toFixed(2)}
                            </span>
                          </div>
                          {/* NDVI visual bar */}
                          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${Math.max(0, Math.min(100, fieldItem.ndviValue * 100))}%`,
                                backgroundColor: color,
                              }}
                            />
                          </div>
                        </>
                      )}
                      <div className="flex justify-between items-center pt-1">
                        <span className="text-gray-600">الحالة:</span>
                        <span
                          className="font-semibold px-2 py-0.5 rounded-full text-xs"
                          style={{
                            backgroundColor: `${color}20`,
                            color: color,
                          }}
                        >
                          {getHealthLabel(fieldItem.ndviValue)}
                        </span>
                      </div>
                    </div>
                  </div>
                </Popup>
              </Polygon>
            );
          }

          // Fallback to circle marker at centroid
          if (fieldItem.centroid) {
            const [lng, lat] = fieldItem.centroid.coordinates;
            return (
              <CircleMarker
                key={fieldItem.id}
                center={[lat, lng] as LatLngTuple}
                radius={8}
                pathOptions={{
                  fillColor: color,
                  color: INTERACTION_COLORS.markerBorder,
                  weight: 2,
                  fillOpacity: 0.8,
                }}
                eventHandlers={{
                  click: () => onFieldClick?.(fieldItem.id),
                }}
                {...({} as any)}
              >
                <Popup>
                  <div className="p-2 min-w-[180px]">
                    <h3 className="font-bold text-gray-900 mb-1">
                      {fieldItem.nameAr || fieldItem.name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      المساحة: {fieldItem.area} هكتار
                    </p>
                    {fieldItem.crop && (
                      <p className="text-sm text-gray-600">
                        المحصول: {fieldItem.cropAr || fieldItem.crop}
                      </p>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          }

          return null;
        })}
      </MapContainer>

      {/* NDVI Legend */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 z-[1000]">
        <h4 className="text-xs font-bold text-gray-700 mb-2">حالة الحقول</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span>صحي (NDVI &gt; 0.6)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-amber-500"></span>
            <span>متوسط (0.4 - 0.6)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-orange-500"></span>
            <span>مجهد (0.2 - 0.4)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span>حرج (&lt; 0.2)</span>
          </div>
        </div>
      </div>

      {/* Field count overlay */}
      {displayFields.length > 0 && (
        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg px-3 py-2 z-[1000]">
          <p className="text-xs text-gray-700 font-medium">
            {displayFields.length} حقل على الخريطة
          </p>
        </div>
      )}
    </div>
  );
};

export default FieldMap;
