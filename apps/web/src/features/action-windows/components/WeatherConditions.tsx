"use client";

/**
 * SAHOOL Weather Conditions Display Component
 * مكون عرض الظروف الجوية
 *
 * Displays weather conditions with threshold indicators for action windows
 */

import React from "react";
import {
  Wind,
  Thermometer,
  Droplets,
  CloudRain,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import type {
  WeatherCondition,
  ThresholdIndicator,
} from "../types/action-windows";

interface WeatherConditionsProps {
  conditions: WeatherCondition;
  thresholds?: ThresholdIndicator[];
  compact?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

const getStatusColor = (status: ThresholdIndicator["status"]) => {
  switch (status) {
    case "good":
      return "text-green-600 bg-green-50 border-green-200";
    case "warning":
      return "text-yellow-600 bg-yellow-50 border-yellow-200";
    case "danger":
      return "text-red-600 bg-red-50 border-red-200";
    default:
      return "text-gray-600 bg-gray-50 border-gray-200";
  }
};

const getStatusIcon = (status: ThresholdIndicator["status"]) => {
  switch (status) {
    case "good":
      return <CheckCircle className="w-4 h-4" aria-hidden="true" />;
    case "warning":
    case "danger":
      return <AlertTriangle className="w-4 h-4" aria-hidden="true" />;
    default:
      return null;
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export const WeatherConditions = React.memo<WeatherConditionsProps>(
  ({ conditions, thresholds, compact = false }) => {
    if (compact) {
      return (
        <div className="flex flex-wrap gap-3" dir="rtl">
          {/* Wind Speed */}
          <div className="flex items-center gap-1.5 text-sm">
            <Wind className="w-4 h-4 text-cyan-600" aria-hidden="true" />
            <span className="text-gray-700">{conditions.windSpeed} km/h</span>
          </div>

          {/* Temperature */}
          <div className="flex items-center gap-1.5 text-sm">
            <Thermometer
              className="w-4 h-4 text-orange-600"
              aria-hidden="true"
            />
            <span className="text-gray-700">
              {Math.round(conditions.temperature)}°C
            </span>
          </div>

          {/* Humidity */}
          <div className="flex items-center gap-1.5 text-sm">
            <Droplets className="w-4 h-4 text-blue-600" aria-hidden="true" />
            <span className="text-gray-700">
              {Math.round(conditions.humidity)}%
            </span>
          </div>

          {/* Rain Probability */}
          <div className="flex items-center gap-1.5 text-sm">
            <CloudRain className="w-4 h-4 text-indigo-600" aria-hidden="true" />
            <span className="text-gray-700">
              {Math.round(conditions.rainProbability)}%
            </span>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* Weather Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {/* Wind Speed */}
          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <div className="flex items-center gap-2 mb-2" dir="rtl">
              <Wind className="w-5 h-5 text-cyan-600" aria-hidden="true" />
              <span className="text-sm text-gray-600">سرعة الرياح</span>
            </div>
            <p className="text-2xl font-bold text-gray-900" dir="ltr">
              {conditions.windSpeed}{" "}
              <span className="text-sm font-normal">km/h</span>
            </p>
            <p className="text-xs text-gray-500 mt-1" dir="rtl">
              {conditions.windDirection}
            </p>
          </div>

          {/* Temperature */}
          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <div className="flex items-center gap-2 mb-2" dir="rtl">
              <Thermometer
                className="w-5 h-5 text-orange-600"
                aria-hidden="true"
              />
              <span className="text-sm text-gray-600">درجة الحرارة</span>
            </div>
            <p className="text-2xl font-bold text-gray-900" dir="ltr">
              {Math.round(conditions.temperature)}{" "}
              <span className="text-sm font-normal">°C</span>
            </p>
          </div>

          {/* Humidity */}
          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <div className="flex items-center gap-2 mb-2" dir="rtl">
              <Droplets className="w-5 h-5 text-blue-600" aria-hidden="true" />
              <span className="text-sm text-gray-600">الرطوبة</span>
            </div>
            <p className="text-2xl font-bold text-gray-900" dir="ltr">
              {Math.round(conditions.humidity)}{" "}
              <span className="text-sm font-normal">%</span>
            </p>
          </div>

          {/* Rain Probability */}
          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <div className="flex items-center gap-2 mb-2" dir="rtl">
              <CloudRain
                className="w-5 h-5 text-indigo-600"
                aria-hidden="true"
              />
              <span className="text-sm text-gray-600">احتمال المطر</span>
            </div>
            <p className="text-2xl font-bold text-gray-900" dir="ltr">
              {Math.round(conditions.rainProbability)}{" "}
              <span className="text-sm font-normal">%</span>
            </p>
            {conditions.precipitation > 0 && (
              <p className="text-xs text-blue-600 mt-1" dir="rtl">
                {conditions.precipitation} mm
              </p>
            )}
          </div>
        </div>

        {/* Threshold Indicators */}
        {thresholds && thresholds.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-gray-700" dir="rtl">
              مؤشرات العتبة
            </h4>
            <div className="space-y-2">
              {thresholds.map((threshold, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(threshold.status)}`}
                  role="status"
                  aria-live="polite"
                >
                  <div className="flex items-center gap-2">
                    {getStatusIcon(threshold.status)}
                    <div>
                      <p className="text-sm font-medium" dir="rtl">
                        {threshold.parameterAr}
                      </p>
                      <p className="text-xs" dir="rtl">
                        {threshold.messageAr}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold" dir="ltr">
                      {threshold.currentValue} {threshold.unit}
                    </p>
                    <p className="text-xs opacity-75" dir="rtl">
                      الحد: {threshold.threshold} {threshold.unit}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Additional Details */}
        {(conditions.cloudCover !== undefined ||
          conditions.uvIndex !== undefined) && (
          <div className="flex gap-4 text-sm text-gray-600" dir="rtl">
            {conditions.cloudCover !== undefined && (
              <div>
                <span className="font-medium">الغطاء السحابي:</span>{" "}
                {Math.round(conditions.cloudCover)}%
              </div>
            )}
            {conditions.uvIndex !== undefined && (
              <div>
                <span className="font-medium">مؤشر UV:</span>{" "}
                {conditions.uvIndex}
              </div>
            )}
          </div>
        )}
      </div>
    );
  },
);

WeatherConditions.displayName = "WeatherConditions";

export default WeatherConditions;
