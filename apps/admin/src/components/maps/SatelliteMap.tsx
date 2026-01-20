"use client";

// Satellite Map Component
// خريطة البيانات الفضائية

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

export default function SatelliteMap({
  fields,
  selectedFieldId,
  onFieldClick,
}: SatelliteMapProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markersRef = useRef<Map<string, any>>(new Map());
  const [isClient, setIsClient] = useState(false);

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

  useEffect(() => {
    if (!isClient) return;

    // Dynamic import of Leaflet
    const initMap = async () => {
      const L = (await import("leaflet")).default;

      if (!mapRef.current) {
        // Initialize map
        const map = L.map("satellite-map", {
          center: [15.5527, 48.5164], // Yemen center
          zoom: 7,
          zoomControl: true,
        });

        // Add tile layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
          maxZoom: 18,
        }).addTo(map);

        mapRef.current = map;
      }

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
            color: "#fff",
            weight: selectedFieldId === field.id ? 3 : 2,
            opacity: 1,
            fillOpacity: 0.8,
          },
        );

        // SECURITY: Use DOM methods to prevent XSS from user data
        const popupContent = document.createElement("div");
        popupContent.style.cssText = "direction: rtl; text-align: right; min-width: 200px;";

        const title = document.createElement("h3");
        title.style.cssText = "margin: 0 0 8px 0; font-weight: bold;";
        title.textContent = field.farmName; // textContent prevents XSS

        const subtitle = document.createElement("p");
        subtitle.style.cssText = "margin: 0 0 4px 0; color: #666;";
        subtitle.textContent = field.fieldName;

        const hr = document.createElement("hr");
        hr.style.cssText = "margin: 8px 0; border: none; border-top: 1px solid #eee;";

        const trendText = field.ndvi.trend === "up" ? "↑ صاعد" : field.ndvi.trend === "down" ? "↓ هابط" : "→ ثابت";

        // SECURITY: Use DOM methods instead of innerHTML to prevent XSS
        popupContent.appendChild(title);
        popupContent.appendChild(subtitle);
        popupContent.appendChild(hr);

        // Current NDVI row
        const currentRow = document.createElement("div");
        currentRow.style.cssText = "display: flex; justify-content: space-between; margin-bottom: 4px;";
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
        avgRow.style.cssText = "display: flex; justify-content: space-between; margin-bottom: 4px;";
        const avgLabel = document.createElement("span");
        avgLabel.textContent = "المتوسط:";
        const avgValue = document.createElement("strong");
        avgValue.textContent = field.ndvi.average.toFixed(2);
        avgRow.appendChild(avgLabel);
        avgRow.appendChild(avgValue);
        popupContent.appendChild(avgRow);

        // Trend row
        const trendRow = document.createElement("div");
        trendRow.style.cssText = "display: flex; justify-content: space-between;";
        const trendLabel = document.createElement("span");
        trendLabel.textContent = "الاتجاه:";
        const trendValue = document.createElement("strong");
        trendValue.textContent = trendText;
        trendRow.appendChild(trendLabel);
        trendRow.appendChild(trendValue);
        popupContent.appendChild(trendRow);

        marker.bindPopup(popupContent);

        marker.on("click", () => {
          if (onFieldClick) {
            onFieldClick(field.id);
          }
        });

        marker.addTo(mapRef.current!);
        markersRef.current.set(field.id, marker);
      });

      // Fit bounds to show all fields
      if (fields.length > 0) {
        const bounds = L.latLngBounds(
          fields.map(
            (f) => [f.location.lat, f.location.lng] as [number, number],
          ),
        );
        mapRef.current?.fitBounds(bounds, { padding: [50, 50] });
      }
    };

    initMap();

    return () => {
      // Cleanup on unmount
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [isClient, fields, selectedFieldId, onFieldClick]);

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
    <div
      id="satellite-map"
      className="w-full h-full"
      role="region"
      aria-label="خريطة البيانات الفضائية - Satellite Map"
    />
  );
}

function getNDVIColor(ndvi: number): string {
  if (ndvi >= 0.7) return "#2E7D32"; // Dark green
  if (ndvi >= 0.5) return "#4CAF50"; // Green
  if (ndvi >= 0.3) return "#FDD835"; // Yellow
  return "#F44336"; // Red
}
