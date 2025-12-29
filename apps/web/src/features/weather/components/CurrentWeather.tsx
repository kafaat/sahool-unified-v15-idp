'use client';

/**
 * SAHOOL Current Weather Component
 * مكون الطقس الحالي
 *
 * Enhanced with:
 * - React.memo and useMemo for performance optimization
 * - Extracted MetricCard as a reusable sub-component
 * - Proper ARIA labels and accessibility attributes
 * - Improved error states with retry button
 * - RTL support
 */

import React, { useMemo } from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, Gauge, Eye, Sunrise, RefreshCw } from 'lucide-react';
import { useCurrentWeather } from '../hooks/useWeather';

interface CurrentWeatherProps {
  lat?: number;
  lon?: number;
  enabled?: boolean;
}

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  unit?: string;
  extraInfo?: string;
  ariaLabel: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// MetricCard Sub-component
// ─────────────────────────────────────────────────────────────────────────────

const MetricCard = React.memo<MetricCardProps>(({
  icon,
  label,
  value,
  unit,
  extraInfo,
  ariaLabel
}) => {
  return (
    <div
      className="bg-white/50 backdrop-blur-sm rounded-lg p-4"
      role="region"
      aria-label={ariaLabel}
    >
      <div className="flex items-center gap-2 mb-2" dir="rtl">
        {icon}
        <p className="text-sm text-gray-600">{label}</p>
      </div>
      <p className="text-2xl font-bold text-gray-900" aria-live="polite">
        {value}{unit && <span className="text-sm font-normal ml-1">{unit}</span>}
      </p>
      {extraInfo && (
        <p className="text-xs text-gray-500 mt-1">{extraInfo}</p>
      )}
    </div>
  );
});

MetricCard.displayName = 'MetricCard';

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

const getWeatherIcon = (condition?: string) => {
  if (!condition) return <Cloud className="w-16 h-16" aria-hidden="true" />;

  const lower = condition.toLowerCase();
  if (lower.includes('rain')) return <CloudRain className="w-16 h-16 text-blue-500" aria-hidden="true" />;
  if (lower.includes('clear') || lower.includes('sunny')) return <Sun className="w-16 h-16 text-yellow-500" aria-hidden="true" />;
  return <Cloud className="w-16 h-16 text-gray-400" aria-hidden="true" />;
};

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export const CurrentWeather = React.memo<CurrentWeatherProps>(({ lat, lon, enabled }) => {
  const { data: weather, isLoading, error, refetch, isRefetching } = useCurrentWeather({ lat, lon, enabled });

  // Memoize weather icon to avoid recalculation
  const weatherIcon = useMemo(() => getWeatherIcon(weather?.condition), [weather?.condition]);

  // Memoize formatted timestamp
  const formattedTimestamp = useMemo(() => {
    if (!weather?.timestamp) return null;
    return new Date(weather.timestamp).toLocaleString('ar-EG', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, [weather?.timestamp]);

  // Memoize metric cards data
  const metricCards = useMemo(() => {
    if (!weather) return [];

    const cards = [
      {
        icon: <Droplets className="w-5 h-5 text-blue-600" aria-hidden="true" />,
        label: 'الرطوبة',
        value: weather.humidity,
        unit: '%',
        ariaLabel: `الرطوبة ${weather.humidity} بالمئة`,
      },
      {
        icon: <Wind className="w-5 h-5 text-cyan-600" aria-hidden="true" />,
        label: 'الرياح',
        value: weather.windSpeed,
        unit: ' km/h',
        extraInfo: weather.windDirection,
        ariaLabel: `سرعة الرياح ${weather.windSpeed} كيلومتر في الساعة${weather.windDirection ? ` اتجاه ${weather.windDirection}` : ''}`,
      },
    ];

    if (weather.pressure) {
      cards.push({
        icon: <Gauge className="w-5 h-5 text-purple-600" aria-hidden="true" />,
        label: 'الضغط',
        value: weather.pressure,
        unit: 'hPa',
        ariaLabel: `الضغط الجوي ${weather.pressure} هيكتوباسكال`,
      });
    }

    if (weather.visibility) {
      cards.push({
        icon: <Eye className="w-5 h-5 text-green-600" aria-hidden="true" />,
        label: 'الرؤية',
        value: weather.visibility,
        unit: 'km',
        ariaLabel: `مدى الرؤية ${weather.visibility} كيلومتر`,
      });
    }

    if (weather.uvIndex !== undefined) {
      cards.push({
        icon: <Sunrise className="w-5 h-5 text-orange-600" aria-hidden="true" />,
        label: 'مؤشر UV',
        value: weather.uvIndex,
        unit: '',
        ariaLabel: `مؤشر الأشعة فوق البنفسجية ${weather.uvIndex}`,
      });
    }

    return cards;
  }, [weather]);

  // Loading State
  if (isLoading) {
    return (
      <div
        className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-8"
        role="status"
        aria-live="polite"
        aria-busy="true"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6" dir="rtl">
          <h2 className="text-2xl font-bold text-gray-900">
            الطقس الحالي
          </h2>
          <span className="text-sm text-gray-600" dir="ltr">
            Current Weather
          </span>
        </div>
        <div className="h-64 flex items-center justify-center">
          <div className="animate-pulse text-gray-400" dir="rtl">
            جاري تحميل بيانات الطقس...
          </div>
        </div>
      </div>
    );
  }

  // Error State with Retry Button
  if (error) {
    return (
      <div
        className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl border-2 border-red-200 p-8"
        role="alert"
        aria-live="assertive"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6" dir="rtl">
          <h2 className="text-2xl font-bold text-gray-900">
            الطقس الحالي
          </h2>
          <span className="text-sm text-gray-600" dir="ltr">
            Current Weather
          </span>
        </div>
        <div className="text-center py-8">
          <Cloud className="w-16 h-16 mx-auto mb-4 text-red-300" aria-hidden="true" />
          <p className="text-gray-700 mb-2" dir="rtl">
            عذراً، حدث خطأ أثناء تحميل بيانات الطقس
          </p>
          <p className="text-sm text-gray-500 mb-4" dir="ltr">
            Sorry, an error occurred while loading weather data
          </p>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="إعادة المحاولة لتحميل بيانات الطقس"
          >
            <RefreshCw
              className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
            <span dir="rtl">{isRefetching ? 'جاري المحاولة...' : 'إعادة المحاولة'}</span>
          </button>
        </div>
      </div>
    );
  }

  // No Data State
  if (!weather) {
    return (
      <div
        className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-8"
        role="status"
        aria-live="polite"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6" dir="rtl">
          <h2 className="text-2xl font-bold text-gray-900">
            الطقس الحالي
          </h2>
          <span className="text-sm text-gray-600" dir="ltr">
            Current Weather
          </span>
        </div>
        <div className="text-center py-8 text-gray-500">
          <Cloud className="w-16 h-16 mx-auto mb-4 opacity-20" aria-hidden="true" />
          <p dir="rtl">بيانات الطقس غير متوفرة</p>
          <p className="text-sm mt-2" dir="ltr">Weather data not available</p>
        </div>
      </div>
    );
  }

  // Main Weather Display
  return (
    <div
      className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-8"
      role="region"
      aria-label="معلومات الطقس الحالي"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6" dir="rtl">
        <h2 className="text-2xl font-bold text-gray-900">
          الطقس الحالي
        </h2>
        <span className="text-sm text-gray-600" dir="ltr">
          Current Weather
        </span>
      </div>

      {/* Main Weather Display */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-6" dir="rtl">
          {weatherIcon}
          <div>
            <p
              className="text-6xl font-bold text-gray-900"
              aria-label={`درجة الحرارة ${Math.round(weather.temperature)} درجة مئوية`}
            >
              {Math.round(weather.temperature)}°C
            </p>
            <p className="text-xl text-gray-600 mt-2" dir="rtl">
              {weather.conditionAr || weather.condition}
            </p>
            {weather.location && (
              <p className="text-sm text-gray-500 mt-1" dir="rtl">
                {weather.location}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Weather Details Grid */}
      <div
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
        role="list"
        aria-label="تفاصيل الطقس"
      >
        {metricCards.map((card, index) => (
          <MetricCard
            key={`metric-${index}`}
            icon={card.icon}
            label={card.label}
            value={card.value}
            unit={card.unit}
            extraInfo={card.extraInfo}
            ariaLabel={card.ariaLabel}
          />
        ))}
      </div>

      {/* Timestamp */}
      {formattedTimestamp && (
        <div
          className="mt-6 text-center text-sm text-gray-500"
          dir="rtl"
          role="status"
          aria-live="polite"
          aria-label={`آخر تحديث ${formattedTimestamp}`}
        >
          آخر تحديث: {formattedTimestamp}
        </div>
      )}
    </div>
  );
});

CurrentWeather.displayName = 'CurrentWeather';

export default CurrentWeather;
