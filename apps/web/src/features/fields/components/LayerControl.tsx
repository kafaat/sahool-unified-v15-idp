"use client";

/**
 * SAHOOL Map Layer Control Component
 * مكون التحكم في طبقات الخريطة
 *
 * Features / المميزات:
 * - Toggle buttons for all map layers / أزرار تبديل لجميع طبقات الخريطة
 * - NDVI opacity control / التحكم في شفافية NDVI
 * - Historical NDVI date picker / منتقي التاريخ لـ NDVI التاريخي
 * - Color legend / مفتاح الألوان
 * - Collapsible panel / لوحة قابلة للطي
 * - Keyboard accessible / قابل للوصول عبر لوحة المفاتيح
 * - localStorage preferences / حفظ التفضيلات محلياً
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  Layers,
  ChevronDown,
  ChevronUp,
  Satellite,
  Activity,
  MapPin,
  Cloud,
  Droplets,
  Calendar,
  Info,
  RotateCcw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { clsx } from "clsx";

// ═══════════════════════════════════════════════════════════════════════════
// Types & Interfaces / الأنواع والواجهات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Layer configuration interface / واجهة تكوين الطبقات
 */
export interface LayerSettings {
  /** NDVI satellite imagery layer / طبقة صور الأقمار الصناعية NDVI */
  ndvi: boolean;
  /** Health zones layer / طبقة مناطق الصحة */
  healthZones: boolean;
  /** Task markers layer / طبقة علامات المهام */
  taskMarkers: boolean;
  /** Weather overlay layer / طبقة الطقس */
  weatherOverlay: boolean;
  /** Irrigation zones layer / طبقة مناطق الري */
  irrigationZones: boolean;
}

/**
 * NDVI-specific settings / إعدادات NDVI المحددة
 */
export interface NDVISettings {
  /** Opacity level (0-1) / مستوى الشفافية */
  opacity: number;
  /** Historical date for NDVI data / التاريخ للبيانات التاريخية */
  historicalDate: Date | null;
}

/**
 * Complete layer control state / حالة التحكم الكاملة في الطبقات
 */
export interface LayerControlState {
  layers: LayerSettings;
  ndvi: NDVISettings;
}

/**
 * Component props interface / واجهة خصائص المكون
 */
export interface LayerControlProps {
  /** Initial layer settings / الإعدادات الأولية للطبقات */
  initialLayers?: Partial<LayerSettings>;
  /** Initial NDVI settings / الإعدادات الأولية لـ NDVI */
  initialNDVI?: Partial<NDVISettings>;
  /** Callback when layers change / استدعاء عند تغيير الطبقات */
  onLayersChange?: (layers: LayerSettings) => void;
  /** Callback when NDVI settings change / استدعاء عند تغيير إعدادات NDVI */
  onNDVIChange?: (settings: NDVISettings) => void;
  /** Position on map / الموقع على الخريطة */
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right";
  /** Custom class name / اسم الفئة المخصص */
  className?: string;
  /** Enable localStorage persistence / تفعيل الحفظ المحلي */
  persistPreferences?: boolean;
  /** localStorage key prefix / بادئة مفتاح التخزين المحلي */
  storageKey?: string;
}

/**
 * NDVI color scale definition / تعريف تدرج ألوان NDVI
 */
interface NDVIColorStop {
  value: number;
  color: string;
  labelAr: string;
  labelEn: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants / الثوابت
// ═══════════════════════════════════════════════════════════════════════════

/**
 * NDVI color gradient scale / تدرج ألوان NDVI
 */
const NDVI_COLOR_SCALE: NDVIColorStop[] = [
  { value: 1.0, color: "#006600", labelAr: "كثيف جداً", labelEn: "Very Dense" },
  { value: 0.8, color: "#00CC00", labelAr: "كثيف", labelEn: "Dense" },
  { value: 0.7, color: "#00FF00", labelAr: "ممتاز", labelEn: "Excellent" },
  { value: 0.6, color: "#55FF00", labelAr: "جيد جداً", labelEn: "Very Good" },
  { value: 0.5, color: "#AAFF00", labelAr: "جيد", labelEn: "Good" },
  { value: 0.4, color: "#FFFF00", labelAr: "متوسط", labelEn: "Moderate" },
  { value: 0.3, color: "#FFAA00", labelAr: "ضعيف", labelEn: "Poor" },
  { value: 0.2, color: "#FF6600", labelAr: "ضعيف جداً", labelEn: "Very Poor" },
  {
    value: 0.0,
    color: "#FF0000",
    labelAr: "بدون غطاء",
    labelEn: "No Vegetation",
  },
  { value: -1.0, color: "#8B4513", labelAr: "تربة جافة", labelEn: "Bare Soil" },
];

/**
 * Default layer settings / الإعدادات الافتراضية للطبقات
 */
const DEFAULT_LAYERS: LayerSettings = {
  ndvi: true,
  healthZones: true,
  taskMarkers: true,
  weatherOverlay: false,
  irrigationZones: true,
};

/**
 * Default NDVI settings / الإعدادات الافتراضية لـ NDVI
 */
const DEFAULT_NDVI: NDVISettings = {
  opacity: 0.7,
  historicalDate: null,
};

/**
 * Layer configuration metadata / بيانات تكوين الطبقات
 */
const LAYER_CONFIG = {
  ndvi: {
    icon: Satellite,
    labelAr: "طبقة NDVI",
    labelEn: "NDVI Layer",
    descriptionAr: "صور الأقمار الصناعية للغطاء النباتي",
    descriptionEn: "Satellite imagery for vegetation",
    color: "text-green-600",
  },
  healthZones: {
    icon: Activity,
    labelAr: "مناطق الصحة",
    labelEn: "Health Zones",
    descriptionAr: "مناطق حالة صحة المحصول",
    descriptionEn: "Crop health status zones",
    color: "text-emerald-600",
  },
  taskMarkers: {
    icon: MapPin,
    labelAr: "علامات المهام",
    labelEn: "Task Markers",
    descriptionAr: "مواقع المهام على الخريطة",
    descriptionEn: "Task locations on map",
    color: "text-blue-600",
  },
  weatherOverlay: {
    icon: Cloud,
    labelAr: "طبقة الطقس",
    labelEn: "Weather Overlay",
    descriptionAr: "بيانات الطقس الحالية",
    descriptionEn: "Current weather data",
    color: "text-sky-600",
  },
  irrigationZones: {
    icon: Droplets,
    labelAr: "مناطق الري",
    labelEn: "Irrigation Zones",
    descriptionAr: "مناطق وخطط الري",
    descriptionEn: "Irrigation areas and plans",
    color: "text-cyan-600",
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Utility Components / المكونات المساعدة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Custom Switch Component / مكون التبديل المخصص
 */
interface SwitchProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  id?: string;
  "aria-label"?: string;
}

const Switch: React.FC<SwitchProps> = ({
  checked,
  onCheckedChange,
  disabled = false,
  id,
  "aria-label": ariaLabel,
}) => {
  return (
    <button
      id={id}
      role="switch"
      aria-checked={checked}
      aria-label={ariaLabel}
      disabled={disabled}
      onClick={() => onCheckedChange(!checked)}
      onKeyDown={(e) => {
        if (e.key === " " || e.key === "Enter") {
          e.preventDefault();
          onCheckedChange(!checked);
        }
      }}
      className={clsx(
        "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2",
        checked ? "bg-green-600" : "bg-gray-300",
        disabled && "opacity-50 cursor-not-allowed",
      )}
    >
      <span
        className={clsx(
          "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
          checked ? "translate-x-6" : "translate-x-1",
        )}
      />
    </button>
  );
};

/**
 * Custom Slider Component / مكون المنزلق المخصص
 */
interface SliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  id?: string;
  "aria-label"?: string;
}

const Slider: React.FC<SliderProps> = ({
  value,
  onChange,
  min = 0,
  max = 1,
  step = 0.01,
  disabled = false,
  id,
  "aria-label": ariaLabel,
}) => {
  return (
    <input
      id={id}
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(parseFloat(e.target.value))}
      disabled={disabled}
      aria-label={ariaLabel}
      className={clsx(
        "w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer",
        "focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2",
        "[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4",
        "[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-green-600",
        "[&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-all",
        "[&::-webkit-slider-thumb]:hover:bg-green-700 [&::-webkit-slider-thumb]:hover:scale-110",
        "[&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full",
        "[&::-moz-range-thumb]:bg-green-600 [&::-moz-range-thumb]:border-0",
        "[&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:transition-all",
        disabled && "opacity-50 cursor-not-allowed",
      )}
    />
  );
};

/**
 * Date Picker Component / مكون منتقي التاريخ
 */
interface DatePickerProps {
  value: Date | null;
  onChange: (date: Date | null) => void;
  disabled?: boolean;
  id?: string;
  "aria-label"?: string;
  maxDate?: Date;
}

const DatePicker: React.FC<DatePickerProps> = ({
  value,
  onChange,
  disabled = false,
  id,
  "aria-label": ariaLabel,
  maxDate = new Date(),
}) => {
  const formatDateForInput = (date: Date | null): string => {
    if (!date) return "";
    return date.toISOString().split("T")[0] ?? "";
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const dateValue = e.target.value;
    onChange(dateValue ? new Date(dateValue) : null);
  };

  return (
    <input
      id={id}
      type="date"
      value={formatDateForInput(value)}
      onChange={handleChange}
      disabled={disabled}
      max={formatDateForInput(maxDate)}
      aria-label={ariaLabel}
      className={clsx(
        "w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
        "focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        "text-gray-700 bg-white",
      )}
    />
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Main Component / المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Map Layer Control Component / مكون التحكم في طبقات الخريطة
 */
export const LayerControl: React.FC<LayerControlProps> = ({
  initialLayers = {},
  initialNDVI = {},
  onLayersChange,
  onNDVIChange,
  position = "top-right",
  className = "",
  persistPreferences = true,
  storageKey = "sahool-map-layers",
}) => {
  // ─────────────────────────────────────────────────────────────────────────
  // State Management / إدارة الحالة
  // ─────────────────────────────────────────────────────────────────────────

  const [isExpanded, setIsExpanded] = useState(true);
  const [showLegend, setShowLegend] = useState(false);
  const [layers, setLayers] = useState<LayerSettings>(() => {
    if (persistPreferences && typeof window !== "undefined") {
      const saved = localStorage.getItem(`${storageKey}-layers`);
      if (saved) {
        try {
          return { ...DEFAULT_LAYERS, ...JSON.parse(saved), ...initialLayers };
        } catch (e) {
          console.warn("Failed to parse saved layer settings:", e);
        }
      }
    }
    return { ...DEFAULT_LAYERS, ...initialLayers };
  });

  const [ndviSettings, setNdviSettings] = useState<NDVISettings>(() => {
    if (persistPreferences && typeof window !== "undefined") {
      const saved = localStorage.getItem(`${storageKey}-ndvi`);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          return {
            ...DEFAULT_NDVI,
            ...parsed,
            historicalDate: parsed.historicalDate
              ? new Date(parsed.historicalDate)
              : null,
            ...initialNDVI,
          };
        } catch (e) {
          console.warn("Failed to parse saved NDVI settings:", e);
        }
      }
    }
    return { ...DEFAULT_NDVI, ...initialNDVI };
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Effects / التأثيرات
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Persist layers to localStorage / حفظ الطبقات في التخزين المحلي
   */
  useEffect(() => {
    if (persistPreferences && typeof window !== "undefined") {
      localStorage.setItem(`${storageKey}-layers`, JSON.stringify(layers));
    }
    onLayersChange?.(layers);
  }, [layers, persistPreferences, storageKey, onLayersChange]);

  /**
   * Persist NDVI settings to localStorage / حفظ إعدادات NDVI في التخزين المحلي
   */
  useEffect(() => {
    if (persistPreferences && typeof window !== "undefined") {
      localStorage.setItem(`${storageKey}-ndvi`, JSON.stringify(ndviSettings));
    }
    onNDVIChange?.(ndviSettings);
  }, [ndviSettings, persistPreferences, storageKey, onNDVIChange]);

  // ─────────────────────────────────────────────────────────────────────────
  // Event Handlers / معالجات الأحداث
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Toggle layer visibility / تبديل رؤية الطبقة
   */
  const toggleLayer = useCallback((layerKey: keyof LayerSettings) => {
    setLayers((prev) => ({
      ...prev,
      [layerKey]: !prev[layerKey],
    }));
  }, []);

  /**
   * Update NDVI opacity / تحديث شفافية NDVI
   */
  const updateOpacity = useCallback((opacity: number) => {
    setNdviSettings((prev) => ({
      ...prev,
      opacity,
    }));
  }, []);

  /**
   * Update historical date / تحديث التاريخ التاريخي
   */
  const updateHistoricalDate = useCallback((date: Date | null) => {
    setNdviSettings((prev) => ({
      ...prev,
      historicalDate: date,
    }));
  }, []);

  /**
   * Reset to defaults / إعادة تعيين إلى الإعدادات الافتراضية
   */
  const resetToDefaults = useCallback(() => {
    setLayers(DEFAULT_LAYERS);
    setNdviSettings(DEFAULT_NDVI);
    if (persistPreferences && typeof window !== "undefined") {
      localStorage.removeItem(`${storageKey}-layers`);
      localStorage.removeItem(`${storageKey}-ndvi`);
    }
  }, [persistPreferences, storageKey]);

  // ─────────────────────────────────────────────────────────────────────────
  // Position Styling / تنسيق الموقع
  // ─────────────────────────────────────────────────────────────────────────

  const positionClasses = {
    "top-left": "top-4 left-4",
    "top-right": "top-4 right-4",
    "bottom-left": "bottom-4 left-4",
    "bottom-right": "bottom-4 right-4",
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Render / العرض
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div
      className={clsx(
        "absolute z-[1000] max-w-sm",
        positionClasses[position],
        className,
      )}
    >
      <Card className="shadow-xl border-2 border-gray-200 bg-white/95 backdrop-blur-sm">
        {/* Header / الرأس */}
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Layers className="w-5 h-5 text-green-600" />
              <span className="font-bold text-gray-900">طبقات الخريطة</span>
              <span className="text-sm font-normal text-gray-500">
                Map Layers
              </span>
            </CardTitle>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowLegend(!showLegend)}
                title={
                  showLegend
                    ? "إخفاء المفتاح / Hide Legend"
                    : "عرض المفتاح / Show Legend"
                }
                aria-label={showLegend ? "Hide legend" : "Show legend"}
                className="p-1 rounded hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <Info className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                aria-label={isExpanded ? "Collapse panel" : "Expand panel"}
                aria-expanded={isExpanded}
                className="p-1 rounded hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-gray-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-600" />
                )}
              </button>
            </div>
          </div>
        </CardHeader>

        {/* Content / المحتوى */}
        {isExpanded && (
          <CardContent className="space-y-4">
            {/* Layer Toggles / مفاتيح التبديل للطبقات */}
            <div className="space-y-3">
              {(Object.keys(LAYER_CONFIG) as Array<keyof LayerSettings>).map(
                (layerKey) => {
                  const config = LAYER_CONFIG[layerKey];
                  const IconComponent = config.icon;

                  return (
                    <div
                      key={layerKey}
                      className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <IconComponent
                          className={clsx("w-5 h-5", config.color)}
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-gray-900">
                              {config.labelAr}
                            </span>
                            <span className="text-xs text-gray-500">
                              {config.labelEn}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500">
                            {config.descriptionAr}
                          </p>
                        </div>
                      </div>
                      <Switch
                        id={`layer-${layerKey}`}
                        checked={layers[layerKey]}
                        onCheckedChange={() => toggleLayer(layerKey)}
                        aria-label={`Toggle ${config.labelEn} layer`}
                      />
                    </div>
                  );
                },
              )}
            </div>

            {/* NDVI Controls / التحكم في NDVI */}
            {layers.ndvi && (
              <div className="border-t pt-4 space-y-4">
                <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                  <Satellite className="w-4 h-4 text-green-600" />
                  <span>إعدادات NDVI</span>
                  <span className="text-xs font-normal text-gray-500">
                    NDVI Settings
                  </span>
                </h4>

                {/* Opacity Slider / منزلق الشفافية */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label
                      htmlFor="ndvi-opacity"
                      className="text-sm text-gray-700 font-medium"
                    >
                      الشفافية <span className="text-gray-500">Opacity</span>
                    </label>
                    <span className="text-sm font-semibold text-green-600">
                      {Math.round(ndviSettings.opacity * 100)}%
                    </span>
                  </div>
                  <Slider
                    id="ndvi-opacity"
                    value={ndviSettings.opacity}
                    onChange={updateOpacity}
                    min={0}
                    max={1}
                    step={0.05}
                    aria-label="NDVI layer opacity"
                  />
                </div>

                {/* Historical Date Picker / منتقي التاريخ التاريخي */}
                <div className="space-y-2">
                  <label
                    htmlFor="ndvi-date"
                    className="text-sm text-gray-700 font-medium flex items-center gap-2"
                  >
                    <Calendar className="w-4 h-4" />
                    <span>تاريخ تاريخي</span>
                    <span className="text-gray-500">Historical Date</span>
                  </label>
                  <DatePicker
                    id="ndvi-date"
                    value={ndviSettings.historicalDate}
                    onChange={updateHistoricalDate}
                    aria-label="Select historical NDVI date"
                  />
                  {ndviSettings.historicalDate && (
                    <p className="text-xs text-gray-500">
                      عرض بيانات{" "}
                      {ndviSettings.historicalDate.toLocaleDateString("ar-EG")}
                      {" / "}
                      Showing data from{" "}
                      {ndviSettings.historicalDate.toLocaleDateString("en-US")}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* NDVI Legend / مفتاح NDVI */}
            {showLegend && layers.ndvi && (
              <div className="border-t pt-4 space-y-3">
                <h4 className="text-sm font-bold text-gray-900">
                  مفتاح ألوان NDVI{" "}
                  <span className="text-gray-500">/ Color Legend</span>
                </h4>

                {/* Color Gradient Bar / شريط التدرج اللوني */}
                <div className="relative h-6 rounded-lg overflow-hidden border border-gray-200">
                  <div
                    className="absolute inset-0"
                    style={{
                      background: `linear-gradient(to right, ${NDVI_COLOR_SCALE.map(
                        (stop) => stop.color,
                      ).join(", ")})`,
                    }}
                  />
                </div>

                {/* Value Labels / تسميات القيم */}
                <div className="flex justify-between text-xs">
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">-1.0</div>
                    <div className="text-gray-600">Bare Soil</div>
                    <div className="text-gray-600">تربة جافة</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-gray-900">0.5</div>
                    <div className="text-gray-600">Moderate</div>
                    <div className="text-gray-600">متوسط</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">1.0</div>
                    <div className="text-gray-600">Dense</div>
                    <div className="text-gray-600">كثيف</div>
                  </div>
                </div>

                {/* Detailed Legend Items / عناصر المفتاح المفصلة */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {NDVI_COLOR_SCALE.filter((_, i) => i % 2 === 0).map(
                    (stop) => (
                      <div key={stop.value} className="flex items-center gap-2">
                        <div
                          className="w-4 h-4 rounded border border-gray-300 flex-shrink-0"
                          style={{ backgroundColor: stop.color }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 truncate">
                            {stop.labelAr}
                          </div>
                          <div className="text-gray-500 truncate">
                            {stop.labelEn}
                          </div>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>
            )}

            {/* Reset Button / زر إعادة التعيين */}
            <div className="border-t pt-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={resetToDefaults}
                className="w-full"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                <span>إعادة تعيين الإعدادات</span>
                <span className="text-gray-500 mr-2">/ Reset</span>
              </Button>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
};

/**
 * Hook for managing layer control state / خطاف لإدارة حالة التحكم في الطبقات
 */
export function useLayerControl(initialState?: Partial<LayerControlState>): [
  LayerControlState,
  {
    toggleLayer: (layer: keyof LayerSettings) => void;
    updateNDVIOpacity: (opacity: number) => void;
    updateNDVIDate: (date: Date | null) => void;
    resetToDefaults: () => void;
  },
] {
  const [state, setState] = useState<LayerControlState>({
    layers: { ...DEFAULT_LAYERS, ...initialState?.layers },
    ndvi: { ...DEFAULT_NDVI, ...initialState?.ndvi },
  });

  const toggleLayer = useCallback((layer: keyof LayerSettings) => {
    setState((prev) => ({
      ...prev,
      layers: {
        ...prev.layers,
        [layer]: !prev.layers[layer],
      },
    }));
  }, []);

  const updateNDVIOpacity = useCallback((opacity: number) => {
    setState((prev) => ({
      ...prev,
      ndvi: {
        ...prev.ndvi,
        opacity,
      },
    }));
  }, []);

  const updateNDVIDate = useCallback((date: Date | null) => {
    setState((prev) => ({
      ...prev,
      ndvi: {
        ...prev.ndvi,
        historicalDate: date,
      },
    }));
  }, []);

  const resetToDefaults = useCallback(() => {
    setState({
      layers: DEFAULT_LAYERS,
      ndvi: DEFAULT_NDVI,
    });
  }, []);

  return [
    state,
    {
      toggleLayer,
      updateNDVIOpacity,
      updateNDVIDate,
      resetToDefaults,
    },
  ];
}

export default LayerControl;
