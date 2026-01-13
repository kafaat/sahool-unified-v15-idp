"use client";

import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";

interface MapViewProps {
  onFieldSelect?: (fieldId: string | null) => void;
}

// Yemen sample fields (GeoJSON)
const SAMPLE_FIELDS: GeoJSON.FeatureCollection = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      id: "field_001",
      properties: {
        id: "field_001",
        name: "حقل الطماطم - صنعاء",
        crop: "طماطم",
        area: 5.2,
        status: "healthy",
        ndvi: 0.72,
        tasks_count: 3,
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [44.19, 15.37],
            [44.195, 15.37],
            [44.195, 15.375],
            [44.19, 15.375],
            [44.19, 15.37],
          ],
        ],
      },
    },
    {
      type: "Feature",
      id: "field_002",
      properties: {
        id: "field_002",
        name: "حقل البن - إب",
        crop: "بن",
        area: 8.5,
        status: "warning",
        ndvi: 0.45,
        tasks_count: 5,
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [44.16, 13.96],
            [44.17, 13.96],
            [44.17, 13.97],
            [44.16, 13.97],
            [44.16, 13.96],
          ],
        ],
      },
    },
    {
      type: "Feature",
      id: "field_003",
      properties: {
        id: "field_003",
        name: "حقل القات - تعز",
        crop: "قات",
        area: 3.8,
        status: "critical",
        ndvi: 0.28,
        tasks_count: 8,
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [44.02, 13.58],
            [44.03, 13.58],
            [44.03, 13.59],
            [44.02, 13.59],
            [44.02, 13.58],
          ],
        ],
      },
    },
    {
      type: "Feature",
      id: "field_004",
      properties: {
        id: "field_004",
        name: "حقل الموز - الحديدة",
        crop: "موز",
        area: 12.0,
        status: "healthy",
        ndvi: 0.68,
        tasks_count: 2,
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [42.95, 14.8],
            [42.97, 14.8],
            [42.97, 14.82],
            [42.95, 14.82],
            [42.95, 14.8],
          ],
        ],
      },
    },
  ],
};

// Status colors
const STATUS_COLORS: Record<string, string> = {
  healthy: "#10b981",
  warning: "#f59e0b",
  critical: "#ef4444",
};

export default function MapView({ onFieldSelect }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Initialize map centered on Yemen
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "&copy; OpenStreetMap contributors",
          },
        },
        layers: [
          {
            id: "osm",
            type: "raster",
            source: "osm",
          },
        ],
      },
      center: [44.2, 15.0], // Yemen center
      zoom: 6,
    });

    map.current.addControl(new maplibregl.NavigationControl(), "top-left");

    map.current.on("load", () => {
      if (!map.current) return;

      setMapLoaded(true);

      // Add fields source
      map.current.addSource("fields", {
        type: "geojson",
        data: SAMPLE_FIELDS,
      });

      // Add fields fill layer
      map.current.addLayer({
        id: "fields-fill",
        type: "fill",
        source: "fields",
        paint: {
          "fill-color": [
            "match",
            ["get", "status"],
            "healthy",
            STATUS_COLORS.healthy,
            "warning",
            STATUS_COLORS.warning,
            "critical",
            STATUS_COLORS.critical,
            "#9ca3af",
          ],
          "fill-opacity": 0.6,
        },
      });

      // Add fields outline layer
      map.current.addLayer({
        id: "fields-outline",
        type: "line",
        source: "fields",
        paint: {
          "line-color": [
            "match",
            ["get", "status"],
            "healthy",
            STATUS_COLORS.healthy,
            "warning",
            STATUS_COLORS.warning,
            "critical",
            STATUS_COLORS.critical,
            "#6b7280",
          ],
          "line-width": 2,
        },
      });

      // Add labels
      map.current.addLayer({
        id: "fields-label",
        type: "symbol",
        source: "fields",
        layout: {
          "text-field": ["get", "name"],
          "text-size": 12,
          "text-anchor": "center",
        },
        paint: {
          "text-color": "#1f2937",
          "text-halo-color": "#ffffff",
          "text-halo-width": 1,
        },
      });

      // Click handler
      map.current.on("click", "fields-fill", (e) => {
        if (e.features && e.features[0]) {
          const feature = e.features[0];
          const props = feature.properties;
          const fieldId = props?.id;

          setSelectedField(fieldId);
          onFieldSelect?.(fieldId);

          // Show popup
          new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(
              `
              <div class="p-2 text-right" dir="rtl">
                <h4 class="font-bold text-sm">${props?.name || "حقل"}</h4>
                <p class="text-xs text-gray-600">المحصول: ${props?.crop || "-"}</p>
                <p class="text-xs text-gray-600">المساحة: ${props?.area || 0} هكتار</p>
                <p class="text-xs text-gray-600">NDVI: ${props?.ndvi || 0}</p>
                <p class="text-xs text-gray-600">المهام: ${props?.tasks_count || 0}</p>
                <div class="mt-2 flex gap-1">
                  <span class="text-xs px-2 py-0.5 rounded-full bg-${
                    props?.status === "healthy"
                      ? "green"
                      : props?.status === "warning"
                        ? "yellow"
                        : "red"
                  }-100 text-${
                    props?.status === "healthy"
                      ? "green"
                      : props?.status === "warning"
                        ? "yellow"
                        : "red"
                  }-800">
                    ${props?.status === "healthy" ? "صحي" : props?.status === "warning" ? "تحذير" : "حرج"}
                  </span>
                </div>
              </div>
            `,
            )
            .addTo(map.current!);
        }
      });

      // Hover effect
      map.current.on("mouseenter", "fields-fill", () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = "pointer";
        }
      });

      map.current.on("mouseleave", "fields-fill", () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = "";
        }
      });
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [onFieldSelect]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="map-container w-full h-full" />

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3">
        <h4 className="text-xs font-bold text-gray-700 mb-2">الحالة</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span>صحي</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-amber-500"></span>
            <span>تحذير</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span>حرج</span>
          </div>
        </div>
      </div>

      {/* Loading overlay */}
      {!mapLoaded && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-gray-500">جاري تحميل الخريطة...</div>
        </div>
      )}
    </div>
  );
}
