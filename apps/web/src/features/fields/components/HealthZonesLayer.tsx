"use client";

/**
 * SAHOOL Health Zones Layer Component
 * مكون طبقة مناطق الصحة
 *
 * يعرض مناطق الحقل كمضلعات ملونة بناءً على صحة NDVI
 * Displays field zones as colored polygons based on NDVI health
 *
 * Features:
 * - Color coding based on NDVI values
 * - Zone selection highlighting
 * - Interactive tooltips with zone information
 * - Click handling for zone details
 * - Arabic RTL support
 * - Error handling and fallback states
 */

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { AlertCircle } from "lucide-react";
import type { LeafletMouseEvent } from "leaflet";

// ═══════════════════════════════════════════════════════════════════════════
// Types - الأنواع
// ═══════════════════════════════════════════════════════════════════════════

/**
 * منطقة الحقل مع بيانات الصحة
 * Field zone with health data
 */
export interface FieldZone {
  id: string;
  name: string;
  boundary: [number, number][]; // Array of [lat, lng] coordinates
  ndviValue: number;
  healthStatus: "excellent" | "good" | "moderate" | "poor" | "critical";
  area: number; // in hectares
}

interface HealthZonesLayerProps {
  zones: FieldZone[];
  selectedZoneId?: string;
  onZoneClick?: (zone: FieldZone) => void;
  showLabels?: boolean;
  showTooltips?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Dynamic Imports - التحميل الديناميكي
// ═══════════════════════════════════════════════════════════════════════════

/**
 * تحميل مكونات react-leaflet بشكل ديناميكي لتجنب مشاكل SSR
 * Dynamically import react-leaflet components to avoid SSR issues
 */
const Polygon = dynamic(
  () => import("react-leaflet").then((mod) => mod.Polygon),
  { ssr: false },
) as any;

const Tooltip = dynamic(
  () => import("react-leaflet").then((mod) => mod.Tooltip),
  { ssr: false },
) as any;

const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), {
  ssr: false,
}) as any;

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions - دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * الحصول على اللون بناءً على قيمة NDVI
 * Get color based on NDVI value
 *
 * Color coding:
 * - Green (>0.6): Excellent health - صحة ممتازة
 * - Yellow (0.4-0.6): Moderate health - صحة متوسطة
 * - Red (<0.4): Poor health - صحة ضعيفة
 */
const getNDVIColor = (ndviValue: number): string => {
  if (ndviValue > 0.6) return "#22c55e"; // Green - أخضر
  if (ndviValue >= 0.4) return "#eab308"; // Yellow - أصفر
  return "#ef4444"; // Red - أحمر
};

/**
 * الحصول على لون الحدود بناءً على قيمة NDVI (ظل أغمق)
 * Get border color based on NDVI value (darker shade)
 */
const getNDVIBorderColor = (ndviValue: number): string => {
  if (ndviValue > 0.6) return "#16a34a"; // Dark green - أخضر داكن
  if (ndviValue >= 0.4) return "#ca8a04"; // Dark yellow - أصفر داكن
  return "#dc2626"; // Dark red - أحمر داكن
};

/**
 * الحصول على النص العربي لحالة الصحة
 * Get Arabic text for health status
 */
const getHealthStatusArabic = (status: FieldZone["healthStatus"]): string => {
  const statusMap = {
    excellent: "ممتازة",
    good: "جيدة",
    moderate: "متوسطة",
    poor: "ضعيفة",
    critical: "حرجة",
  };
  return statusMap[status] || "غير معروفة";
};

/**
 * التحقق من صحة إحداثيات المنطقة
 * Validate zone boundary coordinates
 */
const isValidBoundary = (boundary: [number, number][]): boolean => {
  if (!boundary || !Array.isArray(boundary) || boundary.length < 3) {
    return false;
  }

  return boundary.every(
    (coord) =>
      Array.isArray(coord) &&
      coord.length === 2 &&
      typeof coord[0] === "number" &&
      typeof coord[1] === "number" &&
      !isNaN(coord[0]) &&
      !isNaN(coord[1]) &&
      coord[0] >= -90 &&
      coord[0] <= 90 &&
      coord[1] >= -180 &&
      coord[1] <= 180,
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Main Component - المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

export const HealthZonesLayer: React.FC<HealthZonesLayerProps> = ({
  zones,
  selectedZoneId,
  onZoneClick,
  showLabels = true,
  showTooltips = true,
}) => {
  const [isMounted, setIsMounted] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  // ─────────────────────────────────────────────────────────────────────────
  // Effects - التأثيرات
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * تعيين حالة التحميل لتجنب مشاكل التطابق بين الخادم والعميل
   * Set mounted state to avoid server-client mismatch
   */
  useEffect(() => {
    setIsMounted(true);
  }, []);

  /**
   * التحقق من صحة المناطق وتسجيل الأخطاء
   * Validate zones and log errors
   */
  useEffect(() => {
    if (!zones || zones.length === 0) return;

    const validationErrors: string[] = [];

    zones.forEach((zone, index) => {
      // التحقق من وجود المعرف
      // Validate zone ID
      if (!zone.id) {
        validationErrors.push(`المنطقة ${index + 1} تفتقد المعرف (ID)`);
      }

      // التحقق من صحة الحدود
      // Validate boundary
      if (!isValidBoundary(zone.boundary)) {
        validationErrors.push(
          `المنطقة "${zone.name || zone.id}" تحتوي على إحداثيات غير صالحة`,
        );
      }

      // التحقق من قيمة NDVI
      // Validate NDVI value
      if (
        typeof zone.ndviValue !== "number" ||
        zone.ndviValue < -1 ||
        zone.ndviValue > 1
      ) {
        validationErrors.push(
          `المنطقة "${zone.name || zone.id}" تحتوي على قيمة NDVI غير صالحة: ${zone.ndviValue}`,
        );
      }
    });

    setErrors(validationErrors);

    // طباعة الأخطاء في وضع التطوير
    // Log errors in development mode
    if (validationErrors.length > 0 && process.env.NODE_ENV === "development") {
      console.error("HealthZonesLayer validation errors:", validationErrors);
    }
  }, [zones]);

  // ─────────────────────────────────────────────────────────────────────────
  // Early Returns - العودة المبكرة
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * عدم عرض شيء قبل التحميل (تجنب مشاكل SSR)
   * Don't render anything before mount (avoid SSR issues)
   */
  if (!isMounted) {
    return null;
  }

  /**
   * عرض رسالة خطأ إذا لم تكن هناك مناطق
   * Show error message if no zones
   */
  if (!zones || zones.length === 0) {
    return null; // Silent fail - parent component should handle this
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Event Handlers - معالجات الأحداث
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * معالج النقر على المنطقة
   * Handle zone click event
   */
  const handleZoneClick = (zone: FieldZone) => {
    try {
      if (onZoneClick) {
        onZoneClick(zone);
      }
    } catch (error) {
      console.error("Error handling zone click:", error);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Render - العرض
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <>
      {/* عرض الأخطاء في وضع التطوير - Show errors in development */}
      {errors.length > 0 && process.env.NODE_ENV === "development" && (
        <div className="absolute top-4 right-4 z-[1000] bg-red-50 border border-red-200 rounded-lg p-3 max-w-sm">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-red-900 mb-1">
                أخطاء التحقق من المناطق
              </h4>
              <ul className="text-xs text-red-700 space-y-1">
                {errors.slice(0, 3).map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
                {errors.length > 3 && (
                  <li>... و {errors.length - 3} خطأ إضافي</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* رسم المناطق - Render zones */}
      {zones.map((zone) => {
        // تخطي المناطق غير الصالحة
        // Skip invalid zones
        if (!isValidBoundary(zone.boundary)) {
          return null;
        }

        const isSelected = selectedZoneId === zone.id;
        const fillColor = getNDVIColor(zone.ndviValue);
        const borderColor = getNDVIBorderColor(zone.ndviValue);

        return (
          <Polygon
            key={zone.id}
            positions={zone.boundary}
            pathOptions={{
              // الألوان والتعبئة - Colors and fill
              fillColor: fillColor,
              fillOpacity: isSelected ? 0.7 : 0.5,
              color: isSelected ? "#1e40af" : borderColor,
              weight: isSelected ? 4 : 2,
              opacity: 1,
            }}
            eventHandlers={{
              click: () => handleZoneClick(zone),
              mouseover: (e: LeafletMouseEvent) => {
                // تمييز عند المرور - Highlight on hover
                const layer = e.target;
                if (!isSelected) {
                  layer.setStyle({
                    fillOpacity: 0.7,
                    weight: 3,
                  });
                }
              },
              mouseout: (e: LeafletMouseEvent) => {
                // إعادة التعيين عند المغادرة - Reset on mouse out
                const layer = e.target;
                if (!isSelected) {
                  layer.setStyle({
                    fillOpacity: 0.5,
                    weight: 2,
                  });
                }
              },
            }}
          >
            {/* Tooltip - تلميح الأدوات */}
            {showTooltips && (
              <Tooltip
                direction="top"
                offset={[0, -10]}
                opacity={0.9}
                permanent={showLabels && isSelected}
                className="custom-tooltip"
              >
                <div className="text-right font-arabic" dir="rtl">
                  <div className="font-bold text-sm mb-1">{zone.name}</div>
                  <div className="text-xs space-y-0.5">
                    <div>
                      <span className="text-gray-600">NDVI:</span>{" "}
                      <span className="font-semibold">
                        {zone.ndviValue.toFixed(3)}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">الحالة:</span>{" "}
                      <span className="font-semibold">
                        {getHealthStatusArabic(zone.healthStatus)}
                      </span>
                    </div>
                  </div>
                </div>
              </Tooltip>
            )}

            {/* Popup - النافذة المنبثقة */}
            <Popup>
              <div className="text-right font-arabic min-w-[200px]" dir="rtl">
                <h3 className="font-bold text-base mb-3 text-gray-900 border-b border-gray-200 pb-2">
                  {zone.name}
                </h3>

                <div className="space-y-2 text-sm">
                  {/* قيمة NDVI - NDVI Value */}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">قيمة NDVI:</span>
                    <span className="font-bold text-gray-900">
                      {zone.ndviValue.toFixed(3)}
                    </span>
                  </div>

                  {/* حالة الصحة - Health Status */}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">الحالة الصحية:</span>
                    <span
                      className="font-bold px-2 py-0.5 rounded text-white"
                      style={{ backgroundColor: fillColor }}
                    >
                      {getHealthStatusArabic(zone.healthStatus)}
                    </span>
                  </div>

                  {/* المساحة - Area */}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">المساحة:</span>
                    <span className="font-semibold text-gray-900">
                      {zone.area.toFixed(2)} هكتار
                    </span>
                  </div>

                  {/* المعرف - ID */}
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-500">المعرف:</span>
                    <span className="text-gray-500 font-mono">{zone.id}</span>
                  </div>
                </div>

                {/* زر التفاصيل - Details Button */}
                {onZoneClick && (
                  <button
                    onClick={() => handleZoneClick(zone)}
                    className="mt-3 w-full bg-green-600 text-white py-2 px-3 rounded-lg text-sm font-semibold hover:bg-green-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  >
                    عرض التفاصيل الكاملة
                  </button>
                )}
              </div>
            </Popup>
          </Polygon>
        );
      })}
    </>
  );
};

export default HealthZonesLayer;
