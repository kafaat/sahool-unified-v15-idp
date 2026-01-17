"use client";

/**
 * NDVI Tile Layer Component
 * مكون طبقة بيانات NDVI
 *
 * يعرض بيانات NDVI كطبقة ملونة على الخريطة
 * Renders NDVI data as a colored tile overlay on the map
 */

import { useEffect, useRef, useState } from "react";
import type { Map as MaplibreMap } from "maplibre-gl";
import { useNDVIMap } from "@/features/ndvi";
import { logger } from "@/lib/logger";

/**
 * خصائص مكون طبقة NDVI
 * NDVI Tile Layer Props Interface
 */
export interface NdviTileLayerProps {
  /** معرف الحقل - Field ID */
  fieldId: string;

  /** التاريخ المحدد للبيانات التاريخية - Date for historical NDVI data */
  date?: Date;

  /** مستوى الشفافية (0-1) - Opacity level (0-1) */
  opacity?: number;

  /** حالة الظهور - Visibility state */
  visible?: boolean;

  /** مرجع خريطة MapLibre - MapLibre map instance reference */
  map: React.RefObject<MaplibreMap | null>;

  /** دالة تنفذ عند اكتمال التحميل - Callback when layer loads */
  onLoad?: () => void;

  /** دالة تنفذ عند حدوث خطأ - Callback on error */
  onError?: (error: Error) => void;
}

/**
 * تدرج الألوان لقيم NDVI
 * Color gradient mapping for NDVI values
 *
 * Red (منخفض/Low) -> Yellow (متوسط/Medium) -> Green (عالي/High)
 */
const NDVI_COLOR_STOPS = [
  { value: -1.0, color: "#8B4513" }, // تربة جافة / Bare soil (brown)
  { value: 0.0, color: "#FF0000" }, // بدون غطاء نباتي / No vegetation (red)
  { value: 0.2, color: "#FF6600" }, // غطاء نباتي ضعيف جداً / Very poor vegetation (orange-red)
  { value: 0.3, color: "#FFAA00" }, // غطاء نباتي ضعيف / Poor vegetation (orange)
  { value: 0.4, color: "#FFFF00" }, // غطاء نباتي متوسط / Moderate vegetation (yellow)
  { value: 0.5, color: "#AAFF00" }, // غطاء نباتي جيد / Good vegetation (yellow-green)
  { value: 0.6, color: "#55FF00" }, // غطاء نباتي جيد جداً / Very good vegetation (light green)
  { value: 0.7, color: "#00FF00" }, // غطاء نباتي ممتاز / Excellent vegetation (green)
  { value: 0.8, color: "#00CC00" }, // غطاء نباتي كثيف / Dense vegetation (dark green)
  { value: 1.0, color: "#006600" }, // غطاء نباتي كثيف جداً / Very dense vegetation (very dark green)
];

/**
 * معرفات فريدة لطبقة NDVI
 * Unique identifiers for NDVI layer
 */
const LAYER_ID = "ndvi-raster-layer";
const SOURCE_ID = "ndvi-raster-source";

/**
 * مكون طبقة NDVI للخريطة
 * NDVI Tile Layer Component
 *
 * يستخدم Canvas لعرض بيانات NDVI بأداء عالي
 * Uses Canvas for high-performance NDVI data rendering
 */
export const NdviTileLayer: React.FC<NdviTileLayerProps> = ({
  fieldId,
  date,
  opacity = 0.7,
  visible = true,
  map,
  onLoad,
  onError,
}) => {
  // تنسيق التاريخ للـ API - Format date for API
  const dateString = date ? date.toISOString().split("T")[0] : undefined;

  // جلب بيانات خريطة NDVI - Fetch NDVI map data
  const { data: ndviMapData, error } = useNDVIMap(fieldId, dateString);

  // تتبع حالة التحميل - Track loading state
  const [isLayerLoaded, setIsLayerLoaded] = useState(false);
  const prevDataRef = useRef<typeof ndviMapData>(null);

  /**
   * إضافة أو تحديث طبقة NDVI على الخريطة
   * Add or update NDVI layer on the map
   */
  useEffect(() => {
    const mapInstance = map.current;

    // التحقق من وجود الخريطة والبيانات
    // Verify map and data availability
    if (!mapInstance || !ndviMapData || !visible) {
      return;
    }

    // منع التحديثات المتكررة بنفس البيانات
    // Prevent redundant updates with same data
    if (prevDataRef.current === ndviMapData && isLayerLoaded) {
      return;
    }

    prevDataRef.current = ndviMapData;

    try {
      const { rasterUrl, bounds, colorScale } = ndviMapData;

      // التحقق من وجود URL للبيانات
      // Check for raster data URL
      if (!rasterUrl) {
        logger.warn("No raster URL provided for NDVI layer");
        onError?.(new Error("No NDVI data available"));
        return;
      }

      // إزالة الطبقة والمصدر القديم إن وجد
      // Remove existing layer and source if present
      if (mapInstance.getLayer(LAYER_ID)) {
        mapInstance.removeLayer(LAYER_ID);
      }
      if (mapInstance.getSource(SOURCE_ID)) {
        mapInstance.removeSource(SOURCE_ID);
      }

      // إضافة مصدر البيانات النقطية
      // Add raster data source
      mapInstance.addSource(SOURCE_ID, {
        type: "raster",
        tiles: [rasterUrl],
        tileSize: 256,
        bounds: bounds
          ? [
              bounds[0][0], // غرب / west
              bounds[0][1], // جنوب / south
              bounds[1][0], // شرق / east
              bounds[1][1], // شمال / north
            ]
          : undefined,
      });

      // إضافة طبقة العرض النقطي
      // Add raster layer with color gradient
      mapInstance.addLayer({
        id: LAYER_ID,
        type: "raster",
        source: SOURCE_ID,
        paint: {
          // التحكم في الشفافية - Opacity control
          "raster-opacity": opacity,

          // تحسين جودة العرض - Improve rendering quality
          "raster-resampling": "linear",

          // تطبيق التدرج اللوني إذا كان متاحاً
          // Apply color scale if available
          ...(colorScale && {
            "raster-color": [
              "interpolate",
              ["linear"],
              ["raster-value"],
              colorScale.min,
              colorScale.colors[0] || "#FF0000",
              colorScale.max,
              colorScale.colors[colorScale.colors.length - 1] || "#00FF00",
            ],
          }),
        },
      });

      // ضبط حدود الخريطة لتناسب البيانات
      // Fit map bounds to data if bounds are provided
      if (bounds && bounds.length === 2) {
        mapInstance.fitBounds(
          [
            [bounds[0][0], bounds[0][1]], // southwest
            [bounds[1][0], bounds[1][1]], // northeast
          ],
          {
            padding: 50,
            duration: 1000,
          },
        );
      }

      setIsLayerLoaded(true);
      onLoad?.();

      logger.info("NDVI tile layer added successfully", {
        fieldId,
        date: dateString,
      });
    } catch (err) {
      const error =
        err instanceof Error ? err : new Error("Failed to add NDVI layer");
      logger.error("Error adding NDVI tile layer:", error);
      onError?.(error);
      setIsLayerLoaded(false);
    }

    // تنظيف عند إلغاء التثبيت
    // Cleanup on unmount
    return () => {
      if (mapInstance) {
        try {
          if (mapInstance.getLayer(LAYER_ID)) {
            mapInstance.removeLayer(LAYER_ID);
          }
          if (mapInstance.getSource(SOURCE_ID)) {
            mapInstance.removeSource(SOURCE_ID);
          }
        } catch (err) {
          logger.warn("Error removing NDVI layer during cleanup:", err);
        }
      }
    };
  }, [
    map,
    ndviMapData,
    visible,
    opacity,
    fieldId,
    dateString,
    onLoad,
    onError,
    isLayerLoaded,
  ]);

  /**
   * تحديث الشفافية عند تغييرها
   * Update opacity when it changes
   */
  useEffect(() => {
    const mapInstance = map.current;
    if (!mapInstance || !isLayerLoaded) return;

    try {
      if (mapInstance.getLayer(LAYER_ID)) {
        // @ts-expect-error - MapLibre GL types may be incomplete
        mapInstance.setPaintProperty(LAYER_ID, "raster-opacity", opacity);
      }
    } catch (err) {
      logger.warn("Error updating NDVI layer opacity:", err);
    }
  }, [opacity, map, isLayerLoaded]);

  /**
   * التحكم في ظهور الطبقة
   * Control layer visibility
   */
  useEffect(() => {
    const mapInstance = map.current;
    if (!mapInstance || !isLayerLoaded) return;

    try {
      if (mapInstance.getLayer(LAYER_ID)) {
        // @ts-expect-error - MapLibre GL types may be incomplete
        mapInstance.setLayoutProperty(
          LAYER_ID,
          "visibility",
          visible ? "visible" : "none",
        );
      }
    } catch (err) {
      logger.warn("Error updating NDVI layer visibility:", err);
    }
  }, [visible, map, isLayerLoaded]);

  /**
   * معالجة الأخطاء
   * Handle errors
   */
  useEffect(() => {
    if (error) {
      const errorObj =
        error instanceof Error ? error : new Error("Failed to load NDVI data");
      logger.error("NDVI data fetch error:", errorObj);
      onError?.(errorObj);
    }
  }, [error, onError]);

  // هذا المكون لا يعرض UI مباشرة
  // This component doesn't render UI directly
  // يقوم بإدارة طبقة الخريطة فقط
  // It only manages the map layer
  return null;
};

/**
 * مكون مساعد لعرض مفتاح التدرج اللوني
 * Helper component to display NDVI color legend
 */
export const NdviColorLegend: React.FC<{ className?: string }> = ({
  className = "",
}) => {
  return (
    <div
      className={`bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 ${className}`}
    >
      <h4 className="text-xs font-bold text-gray-700 mb-2 text-right">
        مؤشر NDVI
      </h4>

      {/* شريط التدرج اللوني - Color gradient bar */}
      <div className="relative h-4 rounded overflow-hidden mb-2">
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(to right, ${NDVI_COLOR_STOPS.map(
              (stop) => stop.color,
            ).join(", ")})`,
          }}
        />
      </div>

      {/* تسميات القيم - Value labels */}
      <div className="flex justify-between text-xs text-gray-600">
        <span className="text-left">
          1.0
          <br />
          كثيف
        </span>
        <span className="text-center">
          0.5
          <br />
          متوسط
        </span>
        <span className="text-right">
          0.0
          <br />
          ضعيف
        </span>
      </div>

      {/* وصف - Description */}
      <div className="mt-2 pt-2 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-right">كثافة الغطاء النباتي</p>
      </div>
    </div>
  );
};

/**
 * مكون تحميل NDVI
 * NDVI Loading Component
 */
export const NdviLoadingOverlay: React.FC<{
  isLoading: boolean;
  className?: string;
}> = ({ isLoading, className = "" }) => {
  if (!isLoading) return null;

  return (
    <div
      className={`absolute inset-0 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center ${className}`}
    >
      <div className="bg-white rounded-lg shadow-lg p-4 flex items-center gap-3">
        {/* دائرة التحميل - Loading spinner */}
        <div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-green-600" />
        <span className="text-sm text-gray-700">جاري تحميل بيانات NDVI...</span>
      </div>
    </div>
  );
};

export default NdviTileLayer;
