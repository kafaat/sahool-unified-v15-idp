'use client';

/**
 * NDVI Tile Layer Component
 * مكون طبقة بيانات NDVI
 *
 * يعرض بيانات NDVI كطبقة ملونة على الخريطة
 * Renders NDVI data as a colored tile overlay on the map
 */

import { useEffect, useRef, useState } from 'react';
import type { Map as MaplibreMap } from 'maplibre-gl';
<<<<<<< HEAD
import { useNDVIMap } from '@/features/ndvi';
import {
  buildCssGradient,
  getIndexColorStops,
  getIndexLegend,
  getIndexMetadata,
  type SpectralIndexId,
} from '@/features/ndvi/lib/spectral-colormaps';
=======
import { useIndexMap } from '@/features/ndvi';
>>>>>>> origin/main
import { logger } from '@/lib/logger';

/**
 * نوع المؤشر النباتي - Vegetation index type
 *
 * Alias of {@link SpectralIndexId}. The unified module is the source of
 * truth; this alias is preserved for backward compatibility with existing
 * imports of `VegetationIndexType`.
 */
export type VegetationIndexType = SpectralIndexId;

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
 * تدرج الألوان حسب نوع المؤشر — يُستورد من المصدر الموحّد
 * Color stops live in {@link ../../ndvi/lib/spectral-colormaps}.
 * All callers MUST go through `getIndexColorStops()` so a single
 * source-of-truth governs every rendering surface (raster overlay,
 * polygon paint, legend chip, comparison view).
 */

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
  indexType = 'ndvi',
  date,
  opacity = 0.7,
  visible = true,
  map,
  onLoad,
  onError,
}) => {
  // تنسيق التاريخ للـ API - Format date for API
  const dateString = date ? date.toISOString().split('T')[0] : undefined;

  // جلب بيانات الطبقة النقطية للمؤشر المحدد
  // Fetch tile data for whichever index is currently selected. The unified
  // `useIndexMap` hook (vs the old NDVI-only one) returns `{rasterUrl,
  // bounds, colorScale}` for all 6 mappable indices — NDVI, NDRE, NDWI,
  // EVI, SAVI, LAI — so switching indices no longer re-mounts the layer
  // or strands us on a stale NDVI tile.
  const { data: ndviMapData, error } = useIndexMap(fieldId, indexType, { date: dateString });

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
        type: 'raster',
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

      const stops = getIndexColorStops(indexType);
      // إضافة طبقة العرض النقطي مع تدرج لوني حسب نوع المؤشر
      // Add raster layer with index-specific color gradient
      mapInstance.addLayer({
        id: layerId,
        type: 'raster',
        source: sourceId,
        paint: {
          // التحكم في الشفافية - Opacity control
          'raster-opacity': opacity,

          // تحسين جودة العرض - Improve rendering quality
          'raster-resampling': 'linear',

          // تطبيق التدرج اللوني إذا كان متاحاً
          // Apply color scale if available
          ...(colorScale && {
            'raster-color': [
              'interpolate',
              ['linear'],
              ['raster-value'],
              colorScale.min,
              colorScale.colors[0] ?? stops[0]?.color ?? '#a50026',
              colorScale.max,
              colorScale.colors[colorScale.colors.length - 1] ??
                stops[stops.length - 1]?.color ??
                '#1a9850',
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
          }
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
    // isLayerLoaded is intentionally excluded: it's a guard against redundant
    // updates, not a reactive dependency. Including it causes an infinite loop
    // since this very effect is the one that sets it.
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        mapInstance.setPaintProperty(layerId, 'raster-opacity', opacity);
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
        mapInstance.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
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
      const errorObj = error instanceof Error ? error : new Error('Failed to load NDVI data');
      logger.error('NDVI data fetch error:', errorObj);
      onErrorRef.current?.(errorObj);
    }
  }, [error]);

  // هذا المكون لا يعرض UI مباشرة
  // This component doesn't render UI directly
  // يقوم بإدارة طبقة الخريطة فقط
  // It only manages the map layer
  return null;
};

/**
 * مكون مساعد لعرض مفتاح التدرج اللوني
 * Helper component to display vegetation index color legend.
 *
 * Renders the bilingual legend bands and a continuous gradient bar driven
 * by the unified colormap module so the legend never drifts from the
 * actual map paint.
 */
export const NdviColorLegend: React.FC<{
  className?: string;
  indexType?: VegetationIndexType;
  /** Display language for legend band labels. Defaults to Arabic. */
  language?: 'en' | 'ar';
}> = ({ className = '', indexType = 'ndvi', language = 'ar' }) => {
  const meta = getIndexMetadata(indexType);
  const legend = getIndexLegend(indexType);
  const stops = getIndexColorStops(indexType);
  const isArabic = language === 'ar';
  const dir = isArabic ? 'rtl' : 'ltr';

  return (
    <div
      className={`bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 ${className}`}
      dir={dir}
    >
      <h4 className="text-xs font-bold text-gray-700 mb-1">
        {isArabic ? `مؤشر ${meta.code}` : meta.code} &mdash; {isArabic ? meta.nameAr : meta.nameEn}
      </h4>

      {/* شريط التدرج اللوني - Color gradient bar */}
      <div
        className="relative h-4 rounded overflow-hidden mb-2"
        role="img"
        aria-label={isArabic ? `تدرّج ألوان ${meta.code}` : `${meta.code} colour ramp`}
      >
        <div className="absolute inset-0" style={{ background: buildCssGradient(indexType) }} />
      </div>

      {/* تسميات النطاقات - Band labels */}
      <ul className="grid grid-cols-1 gap-1 text-xs text-gray-600">
        {legend.map((band) => (
          <li
            key={`${meta.code}-${band.min}-${band.max}`}
            className="flex items-center gap-2"
          >
            <span
              className="inline-block h-3 w-4 rounded-sm border border-gray-200"
              style={{ backgroundColor: band.color }}
              aria-hidden="true"
            />
            <span className="font-mono text-[10px] text-gray-500" dir="ltr">
              {band.min.toFixed(band.min >= 1 || band.min <= -1 ? 0 : 1)}–
              {band.max.toFixed(band.max >= 1 || band.max <= -1 ? 0 : 1)}
            </span>
            <span className="truncate">{isArabic ? band.labelAr : band.labelEn}</span>
          </li>
        ))}
      </ul>

      {/* القيم الطرفية - Range endpoints */}
      <div className="mt-2 flex justify-between border-t border-gray-200 pt-1 font-mono text-[10px] text-gray-400" dir="ltr">
        <span>{stops[0]?.value ?? meta.minValue}</span>
        <span>{stops[stops.length - 1]?.value ?? meta.maxValue}</span>
      </div>

      {/* وصف - Description */}
      <p className="mt-1 text-xs text-gray-500">
        {isArabic ? meta.descriptionAr : meta.descriptionEn}
      </p>
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
}> = ({ isLoading, className = '' }) => {
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
