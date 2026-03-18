"use client";

// Satellite Map Component
// خريطة البيانات الفضائية
// Updated: supports actual satellite imagery tiles with layer switching

import { useEffect, useRef, useState } from "react";

interface SatelliteMapProps {
  fields: Array<{
    id: string;
    farmName: string;
    fieldName: string;
    location: { lat: number; lng: number };
    ndvi: {
      current: number;
      average: number;
      trend: "up" | "down" | "stable";
    };
  }>;
  selectedFieldId: string | null;
  onFieldClick?: (fieldId: string) => void;
}

// Tile layer definitions
const TILE_LAYERS = {
  satellite: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "© Esri, Maxar, Earthstar Geographics",
    label: "صور فضائية",
  },
  osm: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "© OpenStreetMap contributors",
    label: "خريطة الشوارع",
  },
  terrain: {
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: "© OpenTopoMap contributors",
    label: "التضاريس",
  },
} as const;

type LayerType = keyof typeof TILE_LAYERS;

export default function SatelliteMap({
  fields,
  selectedFieldId,
  onFieldClick,
}: SatelliteMapProps) {
  const mapRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);
  const markersRef = useRef<Map<string, any>>(new Map());
  const [isClient, setIsClient] = useState(false);
  const [activeLayer, setActiveLayer] = useState<LayerType>("satellite");

  // Use ref for callback prop to avoid rebuilding all markers on parent re-render
  const onFieldClickRef = useRef(onFieldClick);
  onFieldClickRef.current = onFieldClick;

  useEffect(() => {
    setIsClient(true);
    // Load Leaflet CSS dynamically
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    link.integrity = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=";
    link.crossOrigin = "";
    document.head.appendChild(link);
    return () => {
      document.head.removeChild(link);
    };
  }, []);

  // Handle tile layer switching
  useEffect(() => {
    if (!mapRef.current || !tileLayerRef.current) return;

    const L = (window as any).L;
    if (!L) return;

    // Remove current tile layer
    mapRef.current.removeLayer(tileLayerRef.current);

    // Add new tile layer
    const layerConfig = TILE_LAYERS[activeLayer];
    tileLayerRef.current = L.tileLayer(layerConfig.url, {
      attribution: layerConfig.attribution,
      maxZoom: 18,
    }).addTo(mapRef.current);
  }, [activeLayer]);

  // Initialize map once
  useEffect(() => {
    if (!isClient) return;

    const initMap = async () => {
      if (mapRef.current) return; // Already initialized

      const L = (await import("leaflet")).default;
      const map = L.map("satellite-map", {
        center: [15.5527, 48.5164], // Yemen center
        zoom: 7,
        zoomControl: true,
      });

      const layerConfig = TILE_LAYERS[activeLayer];
      tileLayerRef.current = L.tileLayer(layerConfig.url, {
        attribution: layerConfig.attribution,
        maxZoom: 18,
      }).addTo(map);

      mapRef.current = map;
    };

    initMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isClient]);

  // Update markers when fields/selection change (without recreating the map)
  useEffect(() => {
    if (!isClient || !mapRef.current) return;

    const updateMarkers = async () => {
      const L = (await import("leaflet")).default;
      const map = mapRef.current;
      if (!map) return;

      // Clear existing markers
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current.clear();

      // Add field markers with NDVI coloring
      fields.forEach((field) => {
        const ndvi = field.ndvi.current;
        const color = getNDVIColor(ndvi);

        const marker = L.circleMarker(
          [field.location.lat, field.location.lng],
          {
            radius: selectedFieldId === field.id ? 12 : 8,
            fillColor: color,
            color: selectedFieldId === field.id ? "#1e40af" : "#fff",
            weight: selectedFieldId === field.id ? 3 : 2,
            opacity: 1,
            fillOpacity: 0.8,
          },
        );

        // SECURITY: Use DOM methods to prevent XSS from user data
        const popupContent = document.createElement("div");
        popupContent.style.cssText =
          "direction: rtl; text-align: right; min-width: 220px;";

        const title = document.createElement("h3");
        title.style.cssText = "margin: 0 0 8px 0; font-weight: bold;";
        title.textContent = field.farmName; // textContent prevents XSS

        const subtitle = document.createElement("p");
        subtitle.style.cssText = "margin: 0 0 4px 0; color: #666;";
        subtitle.textContent = field.fieldName;

        const hr = document.createElement("hr");
        hr.style.cssText =
          "margin: 8px 0; border: none; border-top: 1px solid #eee;";

        const trendText =
          field.ndvi.trend === "up"
            ? "↑ صاعد"
            : field.ndvi.trend === "down"
              ? "↓ هابط"
              : "→ ثابت";

        popupContent.appendChild(title);
        popupContent.appendChild(subtitle);
        popupContent.appendChild(hr);

        // Current NDVI row
        const currentRow = document.createElement("div");
        currentRow.style.cssText =
          "display: flex; justify-content: space-between; margin-bottom: 4px;";
        const currentLabel = document.createElement("span");
        currentLabel.textContent = "NDVI الحالي:";
        const currentValue = document.createElement("strong");
        currentValue.style.color = color;
        currentValue.textContent = ndvi.toFixed(2);
        currentRow.appendChild(currentLabel);
        currentRow.appendChild(currentValue);
        popupContent.appendChild(currentRow);

        // Average row
        const avgRow = document.createElement("div");
        avgRow.style.cssText =
          "display: flex; justify-content: space-between; margin-bottom: 4px;";
        const avgLabel = document.createElement("span");
        avgLabel.textContent = "المتوسط:";
        const avgValue = document.createElement("strong");
        avgValue.textContent = field.ndvi.average.toFixed(2);
        avgRow.appendChild(avgLabel);
        avgRow.appendChild(avgValue);
        popupContent.appendChild(avgRow);

        // Trend row
        const trendRow = document.createElement("div");
        trendRow.style.cssText =
          "display: flex; justify-content: space-between; margin-bottom: 4px;";
        const trendLabel = document.createElement("span");
        trendLabel.textContent = "الاتجاه:";
        const trendValue = document.createElement("strong");
        trendValue.textContent = trendText;
        trendRow.appendChild(trendLabel);
        trendRow.appendChild(trendValue);
        popupContent.appendChild(trendRow);

        // Health status row
        const healthLabel = getHealthLabel(ndvi);
        const statusRow = document.createElement("div");
        statusRow.style.cssText =
          "display: flex; justify-content: space-between; margin-top: 4px;";
        const statusLabel = document.createElement("span");
        statusLabel.textContent = "الحالة:";
        const statusValue = document.createElement("strong");
        statusValue.style.cssText = `color: ${color}; padding: 2px 8px; border-radius: 9999px; background: ${color}20; font-size: 12px;`;
        statusValue.textContent = healthLabel;
        statusRow.appendChild(statusLabel);
        statusRow.appendChild(statusValue);
        popupContent.appendChild(statusRow);

        marker.bindPopup(popupContent);

        marker.on("click", () => {
          onFieldClickRef.current?.(field.id);
        });

        marker.addTo(map);
        markersRef.current.set(field.id, marker);
      });

      // Fit bounds to show all fields
      if (fields.length > 0) {
        const bounds = L.latLngBounds(
          fields.map(
            (f) => [f.location.lat, f.location.lng] as [number, number],
          ),
        );
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    };

    updateMarkers();
  }, [isClient, fields, selectedFieldId]);

  if (!isClient) {
    return (
      <div
        id="satellite-map"
        className="w-full h-full bg-gray-100 animate-pulse"
        role="region"
        aria-label="جاري تحميل خريطة البيانات الفضائية - Loading Satellite Map"
      />
    );
  }

  return (
    <div className="relative w-full h-full">
      <div
        id="satellite-map"
        className="w-full h-full"
        role="region"
        aria-label="خريطة البيانات الفضائية - Satellite Map"
      />

      {/* Layer Switcher */}
      <div className="absolute top-4 right-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-2">
        <div className="flex gap-1">
          {(Object.keys(TILE_LAYERS) as LayerType[]).map((layerKey) => (
            <button
              key={layerKey}
              onClick={() => setActiveLayer(layerKey)}
              className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                activeLayer === layerKey
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {TILE_LAYERS[layerKey].label}
            </button>
          ))}
        </div>
      </div>

      {/* NDVI Legend */}
      <div className="absolute bottom-4 right-4 z-[1000] bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3">
        <h4 className="text-xs font-bold text-gray-700 mb-2">
          مؤشر الغطاء النباتي
        </h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#1B5E20" }}
            ></span>
            <span>{"ممتاز (NDVI > 0.7)"}</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#4CAF50" }}
            ></span>
            <span>جيد (0.5 - 0.7)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#FDD835" }}
            ></span>
            <span>متوسط (0.3 - 0.5)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#FF9800" }}
            ></span>
            <span>ضعيف (0.15 - 0.3)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: "#F44336" }}
            ></span>
            <span>{"حرج (< 0.15)"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function getNDVIColor(ndvi: number): string {
  if (ndvi >= 0.7) return "#1B5E20"; // Dark green - excellent
  if (ndvi >= 0.5) return "#4CAF50"; // Green - good
  if (ndvi >= 0.3) return "#FDD835"; // Yellow - moderate
  if (ndvi >= 0.15) return "#FF9800"; // Orange - poor
  return "#F44336"; // Red - critical
}

export function getHealthLabel(ndvi: number): string {
  if (ndvi >= 0.7) return "ممتاز";
  if (ndvi >= 0.5) return "جيد";
  if (ndvi >= 0.3) return "متوسط";
  if (ndvi >= 0.15) return "ضعيف";
  return "حرج";
}
