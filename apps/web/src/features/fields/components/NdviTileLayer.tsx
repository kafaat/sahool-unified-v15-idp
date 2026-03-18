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

/** نوع المؤشر النباتي - Vegetation index type */
export type VegetationIndexType = "ndvi" | "ndwi" | "evi" | "savi" | "ndre" | "lai";

/**
 * خصائص مكون طبقة NDVI
 * NDVI Tile Layer Props Interface
 */
export interface NdviTileLayerProps {
  /** معرف الحقل - Field ID */
  fieldId: string;

  /** نوع المؤشر النباتي - Vegetation index type (default: ndvi) */
  indexType?: VegetationIndexType;

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
 * تدرج الألوان حسب نوع المؤشر
 * Color gradient mapping per index type
 */
const INDEX_COLOR_STOPS: Record<VegetationIndexType, Array<{ value: number; color: string }>> = {
  ndvi: [
    { value: -1.0, color: "#8B4513" }, // تربة جافة / Bare soil
    { value: 0.0, color: "#FF0000" },  // بدون غطاء نباتي / No vegetation
    { value: 0.2, color: "#FF6600" },
    { value: 0.3, color: "#FFAA00" },
    { value: 0.4, color: "#FFFF00" },
    { value: 0.5, color: "#AAFF00" },
    { value: 0.6, color: "#55FF00" },
    { value: 0.7, color: "#00FF00" },
    { value: 0.8, color: "#00CC00" },
    { value: 1.0, color: "#006600" },
  ],
  ndwi: [
    { value: -1.0, color: "#8B0000" }, // جفاف شديد / Severe drought
    { value: -0.3, color: "#FF4500" },
    { value: -0.1, color: "#FF8C00" }, // إجهاد مائي / Water stress
    { value: 0.0, color: "#FFD700" },
    { value: 0.1, color: "#87CEEB" },
    { value: 0.2, color: "#4169E1" },  // محتوى مائي كافٍ / Adequate
    { value: 0.4, color: "#0000CD" },
    { value: 1.0, color: "#00008B" },  // مشبّع / Saturated
  ],
  evi: [
    { value: -1.0, color: "#8B4513" },
    { value: 0.0, color: "#FF0000" },
    { value: 0.15, color: "#FF6600" },
    { value: 0.3, color: "#FFFF00" },
    { value: 0.45, color: "#AAFF00" },
    { value: 0.6, color: "#00CC00" },
    { value: 1.0, color: "#006600" },
  ],
  savi: [
    { value: -1.0, color: "#8B4513" }, // تربة عارية / Bare soil
    { value: 0.0, color: "#D2691E" },
    { value: 0.1, color: "#FF6600" },
    { value: 0.25, color: "#FFAA00" },
    { value: 0.4, color: "#FFFF00" },  // غطاء متناثر / Sparse vegetation
    { value: 0.5, color: "#AAFF00" },
    { value: 0.6, color: "#55FF00" },
    { value: 0.8, color: "#00CC00" },
    { value: 1.0, color: "#006600" },
  ],
  ndre: [
    { value: -1.0, color: "#4B0082" },
    { value: 0.0, color: "#FF0000" },  // نقص كلوروفيل / Chlorophyll deficiency
    { value: 0.1, color: "#FF6600" },
    { value: 0.2, color: "#FFAA00" },
    { value: 0.3, color: "#FFFF00" },
    { value: 0.4, color: "#7FFF00" },
    { value: 0.5, color: "#00CC00" },
    { value: 1.0, color: "#006400" },
  ],
  lai: [
    { value: 0.0, color: "#F5DEB3" },  // تربة عارية / Bare
    { value: 1.0, color: "#FFD700" },
    { value: 2.0, color: "#ADFF2F" },
    { value: 3.0, color: "#7CFC00" },
    { value: 4.0, color: "#32CD32" },
    { value: 5.0, color: "#228B22" },
    { value: 6.0, color: "#006400" },
    { value: 8.0, color: "#003300" },
  ],
};


/**
 * معرفات ديناميكية حسب نوع المؤشر
 * Dynamic IDs based on index type
 */
function getLayerId(indexType: VegetationIndexType): string {
  return `${indexType}-raster-layer`;
}
function getSourceId(indexType: VegetationIndexType): string {
  return `${indexType}-raster-source`;
}


/**
 * مكون طبقة NDVI للخريطة
 * NDVI Tile Layer Component
 *
 * يستخدم Canvas لعرض بيانات NDVI بأداء عالي
 * Uses Canvas for high-performance NDVI data rendering
 */
export const NdviTileLayer: React.FC<NdviTileLayerProps> = ({
  fieldId,
  indexType = "ndvi",
  date,
  opacity = 0.7,
  visible = true,
  map,
  onLoad,
  onError,
}) => {
  // تنسيق التاريخ للـ API - Format date for API
  const dateString = date ? date.toISOString().split("T")[0] : undefined;

  // جلب بيانات خريطة المؤشر - Fetch vegetation index map data
  // TODO: useNDVIMap always fetches NDVI data regardless of indexType.
  // When the backend satellite API supports multi-index endpoints, replace with
  // a generic useVegetationIndexMap(fieldId, indexType, dateString) hook.
  const { data: ndviMapData, error } = useNDVIMap(fieldId, dateString);

  // تتبع حالة التحميل - Track loading state
  const [isLayerLoaded, setIsLayerLoaded] = useState(false);
  const prevDataRef = useRef<typeof ndviMapData>(null);

  // Use refs for callback props to avoid re-triggering the effect
  const onLoadRef = useRef(onLoad);
  onLoadRef.current = onLoad;
  const onErrorRef = useRef(onError);
  onErrorRef.current = onError;

  /**
   * إضافة أو تحديث طبقة المؤشر على الخريطة
   * Add or update vegetation index layer on the map
   */
  useEffect(() => {
    const mapInstance = map.current;
    const layerId = getLayerId(indexType);
    const sourceId = getSourceId(indexType);

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
        logger.warn(`No raster URL provided for ${indexType} layer`);
        onErrorRef.current?.(new Error(`No ${indexType.toUpperCase()} data available`));
        return;
      }

      // إزالة الطبقة والمصدر القديم إن وجد
      // Remove existing layer and source if present
      if (mapInstance.getLayer(layerId)) {
        mapInstance.removeLayer(layerId);
      }
      if (mapInstance.getSource(sourceId)) {
        mapInstance.removeSource(sourceId);
      }

      // إضافة مصدر البيانات النقطية
      // Add raster data source
      mapInstance.addSource(sourceId, {
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

      // إضافة طبقة العرض النقطي مع تدرج لوني حسب نوع المؤشر
      // Add raster layer with index-specific color gradient
      mapInstance.addLayer({
        id: layerId,
        type: "raster",
        source: sourceId,
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
              colorScale.colors[0] ?? INDEX_COLOR_STOPS[indexType]?.[0]?.color ?? "#FF0000",
              colorScale.max,
              colorScale.colors[colorScale.colors.length - 1] ?? INDEX_COLOR_STOPS[indexType]?.[INDEX_COLOR_STOPS[indexType]!.length - 1]?.color ?? "#00FF00",
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
      onLoadRef.current?.();

      logger.info(`${indexType.toUpperCase()} tile layer added successfully`, {
        fieldId,
        indexType,
        date: dateString,
      });
    } catch (err) {
      const error =
        err instanceof Error ? err : new Error(`Failed to add ${indexType.toUpperCase()} layer`);
      logger.error(`Error adding ${indexType} tile layer:`, error);
      onErrorRef.current?.(error);
      setIsLayerLoaded(false);
    }

    // تنظيف عند إلغاء التثبيت
    // Cleanup on unmount
    return () => {
      if (mapInstance) {
        try {
          if (mapInstance.getLayer(layerId)) {
            mapInstance.removeLayer(layerId);
          }
          if (mapInstance.getSource(sourceId)) {
            mapInstance.removeSource(sourceId);
          }
        } catch (err) {
          logger.warn(`Error removing ${indexType} layer during cleanup:`, err);
        }
      }
    };
  }, [map, ndviMapData, visible, opacity, fieldId, dateString, indexType]);

  /**
   * تحديث الشفافية عند تغييرها
   * Update opacity when it changes
   */
  useEffect(() => {
    const mapInstance = map.current;
    if (!mapInstance || !isLayerLoaded) return;
    const layerId = getLayerId(indexType);

    try {
      if (mapInstance.getLayer(layerId)) {
        mapInstance.setPaintProperty(layerId, "raster-opacity", opacity);
      }
    } catch (err) {
      logger.warn(`Error updating ${indexType} layer opacity:`, err);
    }
  }, [opacity, map, isLayerLoaded, indexType]);

  /**
   * التحكم في ظهور الطبقة
   * Control layer visibility
   */
  useEffect(() => {
    const mapInstance = map.current;
    if (!mapInstance || !isLayerLoaded) return;
    const layerId = getLayerId(indexType);

    try {
      if (mapInstance.getLayer(layerId)) {
        mapInstance.setLayoutProperty(
          layerId,
          "visibility",
          visible ? "visible" : "none",
        );
      }
    } catch (err) {
      logger.warn(`Error updating ${indexType} layer visibility:`, err);
    }
  }, [visible, map, isLayerLoaded, indexType]);

  /**
   * معالجة الأخطاء
   * Handle errors
   */
  useEffect(() => {
    if (error) {
      const errorObj =
        error instanceof Error ? error : new Error("Failed to load NDVI data");
      logger.error("NDVI data fetch error:", errorObj);
      onErrorRef.current?.(errorObj);
    }
  }, [error]);

  // هذا المكون لا يعرض UI مباشرة
  // This component doesn't render UI directly
  // يقوم بإدارة طبقة الخريطة فقط
  // It only manages the map layer
  return null;
};

/** تسميات المؤشرات - Index labels */
const INDEX_LABELS: Record<VegetationIndexType, { title: string; description: string; lowLabel: string; midLabel: string; highLabel: string }> = {
  ndvi: { title: "مؤشر NDVI", description: "كثافة الغطاء النباتي", lowLabel: "ضعيف", midLabel: "متوسط", highLabel: "كثيف" },
  ndwi: { title: "مؤشر NDWI", description: "محتوى الماء في النبات", lowLabel: "جفاف", midLabel: "متوسط", highLabel: "مشبّع" },
  evi: { title: "مؤشر EVI", description: "الغطاء المحسّن", lowLabel: "ضعيف", midLabel: "متوسط", highLabel: "كثيف" },
  savi: { title: "مؤشر SAVI", description: "الغطاء المعدّل للتربة", lowLabel: "تربة عارية", midLabel: "متناثر", highLabel: "كثيف" },
  ndre: { title: "مؤشر NDRE", description: "تركيز الكلوروفيل", lowLabel: "نقص", midLabel: "متوسط", highLabel: "ممتاز" },
  lai: { title: "مؤشر LAI", description: "مساحة الأوراق (m²/m²)", lowLabel: "0", midLabel: "4", highLabel: "8" },
};

/**
 * مكون مساعد لعرض مفتاح التدرج اللوني
 * Helper component to display vegetation index color legend
 */
export const NdviColorLegend: React.FC<{ className?: string; indexType?: VegetationIndexType }> = ({
  className = "",
  indexType = "ndvi",
}) => {
  const colorStops = INDEX_COLOR_STOPS[indexType];
  const labels = INDEX_LABELS[indexType];

  return (
    <div
      className={`bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 ${className}`}
    >
      <h4 className="text-xs font-bold text-gray-700 mb-2 text-right">
        {labels.title}
      </h4>

      {/* شريط التدرج اللوني - Color gradient bar */}
      <div className="relative h-4 rounded overflow-hidden mb-2">
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(to right, ${colorStops.map(
              (stop) => stop.color,
            ).join(", ")})`,
          }}
        />
      </div>

      {/* تسميات القيم - Value labels */}
      <div className="flex justify-between text-xs text-gray-600">
        <span className="text-left">
          {colorStops[colorStops.length - 1]?.value ?? 1.0}
          <br />
          {labels.highLabel}
        </span>
        <span className="text-center">
          {labels.midLabel}
        </span>
        <span className="text-right">
          {colorStops[0]?.value ?? 0}
          <br />
          {labels.lowLabel}
        </span>
      </div>

      {/* وصف - Description */}
      <div className="mt-2 pt-2 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-right">{labels.description}</p>
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
