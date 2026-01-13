"use client";

/**
 * SAHOOL Weather Overlay Component
 * مكون تراكب الطقس
 *
 * Displays weather conditions over the field map with:
 * - Current weather conditions
 * - Temperature, humidity, wind direction
 * - Weather icons
 * - Rainfall forecast
 * - Severe weather alerts
 * - Collapsible panel
 */

import React, { useState, useMemo } from "react";
import {
  Cloud,
  CloudRain,
  Sun,
  Wind,
  Droplets,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  CloudDrizzle,
  CloudSnow,
  CloudLightning,
  Thermometer,
} from "lucide-react";
import { useField } from "../hooks/useField";
import {
  useCurrentWeather,
  useWeatherForecast,
  useWeatherAlerts,
} from "@/features/weather/hooks/useWeather";
import { Badge } from "@/components/ui/badge";
import type { WeatherData, WeatherAlert } from "@/features/weather/types";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface WeatherOverlayProps {
  fieldId: string;
  position?: "topright" | "topleft" | "bottomright" | "bottomleft";
  expanded?: boolean;
}

type Position = "topright" | "topleft" | "bottomright" | "bottomleft";

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get weather icon based on condition
 * الحصول على أيقونة الطقس بناءً على الحالة
 */
const getWeatherIcon = (condition?: string, size: number = 24) => {
  if (!condition)
    return <Cloud className={`w-${size} h-${size}`} aria-hidden="true" />;

  const lower = condition.toLowerCase();
  const iconClass = `w-${size} h-${size}`;

  if (lower.includes("rain") || lower.includes("ممطر")) {
    return (
      <CloudRain className={`${iconClass} text-blue-500`} aria-hidden="true" />
    );
  }
  if (lower.includes("drizzle") || lower.includes("رذاذ")) {
    return (
      <CloudDrizzle
        className={`${iconClass} text-blue-400`}
        aria-hidden="true"
      />
    );
  }
  if (lower.includes("thunder") || lower.includes("رعد")) {
    return (
      <CloudLightning
        className={`${iconClass} text-yellow-500`}
        aria-hidden="true"
      />
    );
  }
  if (lower.includes("snow") || lower.includes("ثلج")) {
    return (
      <CloudSnow className={`${iconClass} text-blue-300`} aria-hidden="true" />
    );
  }
  if (
    lower.includes("clear") ||
    lower.includes("sunny") ||
    lower.includes("صافي") ||
    lower.includes("مشمس")
  ) {
    return (
      <Sun className={`${iconClass} text-yellow-500`} aria-hidden="true" />
    );
  }
  if (lower.includes("cloud") || lower.includes("غائم")) {
    return (
      <Cloud className={`${iconClass} text-gray-400`} aria-hidden="true" />
    );
  }

  return <Cloud className={`${iconClass} text-gray-400`} aria-hidden="true" />;
};

/**
 * Get wind direction in Arabic
 * الحصول على اتجاه الرياح بالعربية
 */
const getWindDirectionAr = (direction: string): string => {
  const directionMap: Record<string, string> = {
    N: "شمال",
    NE: "شمال شرق",
    E: "شرق",
    SE: "جنوب شرق",
    S: "جنوب",
    SW: "جنوب غرب",
    W: "غرب",
    NW: "شمال غرب",
  };
  return directionMap[direction] || direction;
};

/**
 * Get position classes for overlay
 * الحصول على فئات الموقع للتراكب
 */
const getPositionClasses = (position: Position): string => {
  const positionMap: Record<Position, string> = {
    topright: "top-4 right-4",
    topleft: "top-4 left-4",
    bottomright: "bottom-4 right-4",
    bottomleft: "bottom-4 left-4",
  };
  return positionMap[position];
};

/**
 * Get severity badge variant
 * الحصول على نوع شارة الخطورة
 */
const getSeverityVariant = (
  severity: string,
): "default" | "warning" | "danger" => {
  if (severity === "critical" || severity === "severe") return "danger";
  if (severity === "warning" || severity === "moderate") return "warning";
  return "default";
};

// ═══════════════════════════════════════════════════════════════════════════
// Sub-Components
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Compact weather display (collapsed state)
 * عرض الطقس المدمج (الحالة المطوية)
 */
interface CompactWeatherProps {
  weather: WeatherData;
  alertsCount: number;
  onExpand: () => void;
}

const CompactWeather = React.memo<CompactWeatherProps>(
  ({ weather, alertsCount, onExpand }) => {
    return (
      <button
        onClick={onExpand}
        className="w-full flex items-center justify-between gap-3 hover:bg-white/10 rounded-lg p-2 transition-colors"
        aria-label="توسيع معلومات الطقس"
        aria-expanded="false"
      >
        <div className="flex items-center gap-2">
          {getWeatherIcon(weather.condition, 6)}
          <span className="text-2xl font-bold text-white">
            {Math.round(weather.temperature)}°
          </span>
        </div>
        <div className="flex items-center gap-2">
          {alertsCount > 0 && (
            <Badge variant="danger" size="sm" className="animate-pulse">
              {alertsCount}
            </Badge>
          )}
          <ChevronDown className="w-4 h-4 text-white" aria-hidden="true" />
        </div>
      </button>
    );
  },
);

CompactWeather.displayName = "CompactWeather";

/**
 * Expanded weather display
 * عرض الطقس الموسع
 */
interface ExpandedWeatherProps {
  weather: WeatherData;
  alerts: WeatherAlert[];
  rainfallForecast: number;
  onCollapse: () => void;
}

const ExpandedWeather = React.memo<ExpandedWeatherProps>(
  ({ weather, alerts, rainfallForecast, onCollapse }) => {
    const activeAlerts = useMemo(
      () => alerts.filter((a) => a.isActive),
      [alerts],
    );

    return (
      <div className="space-y-4">
        {/* Header with collapse button */}
        <div className="flex items-center justify-between" dir="rtl">
          <h3 className="text-lg font-bold text-white">الطقس الحالي</h3>
          <button
            onClick={onCollapse}
            className="p-1 hover:bg-white/10 rounded transition-colors"
            aria-label="طي معلومات الطقس"
            aria-expanded="true"
          >
            <ChevronUp className="w-4 h-4 text-white" aria-hidden="true" />
          </button>
        </div>

        {/* Main weather info */}
        <div className="flex items-center gap-4">
          {getWeatherIcon(weather.condition, 12)}
          <div dir="rtl">
            <p className="text-4xl font-bold text-white">
              {Math.round(weather.temperature)}°C
            </p>
            <p className="text-sm text-white/80 mt-1">
              {weather.conditionAr || weather.condition}
            </p>
          </div>
        </div>

        {/* Weather metrics grid */}
        <div className="grid grid-cols-2 gap-3">
          {/* Temperature */}
          <div
            className="bg-white/10 backdrop-blur-sm rounded-lg p-3"
            dir="rtl"
          >
            <div className="flex items-center gap-2 mb-1">
              <Thermometer
                className="w-4 h-4 text-white/80"
                aria-hidden="true"
              />
              <p className="text-xs text-white/80">الحرارة</p>
            </div>
            <p className="text-lg font-bold text-white">
              {Math.round(weather.temperature)}°C
            </p>
          </div>

          {/* Humidity */}
          <div
            className="bg-white/10 backdrop-blur-sm rounded-lg p-3"
            dir="rtl"
          >
            <div className="flex items-center gap-2 mb-1">
              <Droplets className="w-4 h-4 text-white/80" aria-hidden="true" />
              <p className="text-xs text-white/80">الرطوبة</p>
            </div>
            <p className="text-lg font-bold text-white">{weather.humidity}%</p>
          </div>

          {/* Wind */}
          <div
            className="bg-white/10 backdrop-blur-sm rounded-lg p-3"
            dir="rtl"
          >
            <div className="flex items-center gap-2 mb-1">
              <Wind className="w-4 h-4 text-white/80" aria-hidden="true" />
              <p className="text-xs text-white/80">الرياح</p>
            </div>
            <p className="text-lg font-bold text-white">
              {weather.windSpeed} km/h
            </p>
            <p className="text-xs text-white/70">
              {getWindDirectionAr(weather.windDirection)}
            </p>
          </div>

          {/* Rainfall forecast */}
          <div
            className="bg-white/10 backdrop-blur-sm rounded-lg p-3"
            dir="rtl"
          >
            <div className="flex items-center gap-2 mb-1">
              <CloudRain className="w-4 h-4 text-white/80" aria-hidden="true" />
              <p className="text-xs text-white/80">الأمطار المتوقعة</p>
            </div>
            <p className="text-lg font-bold text-white">
              {rainfallForecast.toFixed(1)} mm
            </p>
            <p className="text-xs text-white/70">24 ساعة</p>
          </div>
        </div>

        {/* Weather alerts */}
        {activeAlerts.length > 0 && (
          <div className="space-y-2" dir="rtl">
            <div className="flex items-center gap-2">
              <AlertTriangle
                className="w-4 h-4 text-yellow-300"
                aria-hidden="true"
              />
              <p className="text-sm font-semibold text-white">تنبيهات الطقس</p>
            </div>
            <div className="space-y-2">
              {activeAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-3 border-l-4 border-yellow-400"
                  role="alert"
                  aria-live="polite"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-white">
                        {alert.titleAr || alert.title}
                      </p>
                      {alert.descriptionAr && (
                        <p className="text-xs text-white/80 mt-1">
                          {alert.descriptionAr}
                        </p>
                      )}
                    </div>
                    <Badge
                      variant={getSeverityVariant(alert.severity)}
                      size="sm"
                    >
                      {alert.severity}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Location info */}
        {weather.location && (
          <div className="text-center pt-3 border-t border-white/20" dir="rtl">
            <p className="text-xs text-white/70">{weather.location}</p>
          </div>
        )}
      </div>
    );
  },
);

ExpandedWeather.displayName = "ExpandedWeather";

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════════════════

export const WeatherOverlay = React.memo<WeatherOverlayProps>(
  ({ fieldId, position = "topright", expanded: expandedProp }) => {
    // State
    const [isExpanded, setIsExpanded] = useState(expandedProp ?? false);

    // Fetch field data to get coordinates
    const { data: field } = useField(fieldId);

    // Extract coordinates from field centroid
    const coordinates = useMemo(() => {
      if (!field?.centroid?.coordinates) return undefined;
      const [lon, lat] = field.centroid.coordinates;
      return { lat, lon };
    }, [field]);

    // Fetch weather data
    const {
      data: weather,
      isLoading: weatherLoading,
      error: weatherError,
    } = useCurrentWeather({
      lat: coordinates?.lat,
      lon: coordinates?.lon,
      enabled: !!coordinates,
    });

    const { data: forecast } = useWeatherForecast({
      lat: coordinates?.lat,
      lon: coordinates?.lon,
      days: 1,
      enabled: !!coordinates,
    });

    const { data: alerts = [] } = useWeatherAlerts({
      lat: coordinates?.lat,
      lon: coordinates?.lon,
      enabled: !!coordinates,
    });

    // Calculate total rainfall forecast for next 24 hours
    const rainfallForecast = useMemo(() => {
      if (!forecast || forecast.length === 0) return 0;
      return forecast[0]?.precipitation || 0;
    }, [forecast]);

    // Count active alerts
    const activeAlertsCount = useMemo(() => {
      return alerts.filter((a) => a.isActive).length;
    }, [alerts]);

    // Handlers
    const handleExpand = () => setIsExpanded(true);
    const handleCollapse = () => setIsExpanded(false);

    // Loading state
    if (weatherLoading) {
      return (
        <div
          className={`absolute ${getPositionClasses(position)} z-[1000]`}
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <div className="bg-gradient-to-br from-blue-500/90 to-cyan-600/90 backdrop-blur-md rounded-lg shadow-lg p-4 min-w-[200px]">
            <div
              className="animate-pulse text-white text-sm text-center"
              dir="rtl"
            >
              جاري تحميل الطقس...
            </div>
          </div>
        </div>
      );
    }

    // Error state
    if (weatherError || !weather) {
      return (
        <div
          className={`absolute ${getPositionClasses(position)} z-[1000]`}
          role="alert"
        >
          <div className="bg-gradient-to-br from-gray-500/90 to-gray-600/90 backdrop-blur-md rounded-lg shadow-lg p-4 min-w-[200px]">
            <div
              className="flex items-center gap-2 text-white text-sm"
              dir="rtl"
            >
              <Cloud className="w-4 h-4 opacity-50" aria-hidden="true" />
              <span>بيانات الطقس غير متوفرة</span>
            </div>
          </div>
        </div>
      );
    }

    // Main render
    return (
      <div
        className={`absolute ${getPositionClasses(position)} z-[1000] max-w-[320px]`}
        role="region"
        aria-label="معلومات الطقس للحقل"
      >
        <div className="bg-gradient-to-br from-blue-500/90 to-cyan-600/90 backdrop-blur-md rounded-lg shadow-lg p-4 transition-all duration-300">
          {isExpanded ? (
            <ExpandedWeather
              weather={weather}
              alerts={alerts}
              rainfallForecast={rainfallForecast}
              onCollapse={handleCollapse}
            />
          ) : (
            <CompactWeather
              weather={weather}
              alertsCount={activeAlertsCount}
              onExpand={handleExpand}
            />
          )}
        </div>

        {/* Alert badge for severe weather (visible when collapsed) */}
        {!isExpanded && activeAlertsCount > 0 && (
          <div className="absolute -top-2 -right-2" aria-hidden="true">
            <Badge
              variant="danger"
              size="sm"
              className="animate-pulse shadow-lg"
            >
              <AlertTriangle className="w-3 h-3 mr-1" />
              {activeAlertsCount}
            </Badge>
          </div>
        )}
      </div>
    );
  },
);

WeatherOverlay.displayName = "WeatherOverlay";

export default WeatherOverlay;
