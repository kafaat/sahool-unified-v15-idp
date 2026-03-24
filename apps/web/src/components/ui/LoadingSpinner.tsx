/**
 * Loading Spinner Component
 * مكون تحميل
 */

import React from "react";

interface LoadingSpinnerProps {
  /** Size of the spinner / حجم دائرة التحميل */
  size?: "sm" | "md" | "lg" | "xl";
  /** Show loading text / عرض نص التحميل */
  showText?: boolean;
  /** Custom loading text / نص تحميل مخصص */
  text?: string;
  /** Custom text in Arabic / نص مخصص بالعربية */
  textAr?: string;
  /** Custom height / ارتفاع مخصص */
  height?: string;
  /** Custom class name / اسم الفئة المخصص */
  className?: string;
}

const sizeClasses = {
  sm: "h-6 w-6 border-2",
  md: "h-10 w-10 border-2",
  lg: "h-12 w-12 border-b-2",
  xl: "h-16 w-16 border-b-3",
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "md",
  showText = true,
  text = "Loading...",
  textAr = "جاري التحميل...",
  height = "200px",
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center ${className}`}
      style={{ height }}
    >
      <div
        className={`animate-spin rounded-full border-green-500 ${sizeClasses[size]}`}
        role="status"
        aria-label="Loading"
      />
      {showText && (
        <div className="mt-4 text-center">
          <p className="text-gray-600 font-medium">{textAr}</p>
          <p className="text-sm text-gray-500 mt-1">{text}</p>
        </div>
      )}
    </div>
  );
};

/**
 * Chart Loading Spinner - optimized for chart components
 * مكون تحميل للرسوم البيانية
 */
export const ChartLoadingSpinner: React.FC<{ height?: string }> = ({
  height = "400px",
}) => {
  return (
    <div
      className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center justify-center"
      style={{ height }}
      role="status"
      aria-label="جاري تحميل الرسم البياني - Loading chart"
    >
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto" />
        <p className="text-gray-600 mt-4">جاري تحميل الرسم البياني...</p>
        <p className="text-sm text-gray-500 mt-1">Loading chart...</p>
      </div>
    </div>
  );
};

/**
 * Map Loading Spinner - optimized for map components
 * مكون تحميل للخرائط
 */
export const MapLoadingSpinner: React.FC<{ height?: string }> = ({
  height = "500px",
}) => {
  return (
    <div
      className="bg-gray-100 flex items-center justify-center rounded-xl"
      style={{ height }}
      role="status"
      aria-label="جاري تحميل الخريطة - Loading map"
    >
      <div className="text-center">
        <span className="text-4xl mb-3 block">🗺️</span>
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-500 mx-auto mb-3" />
        <p className="text-gray-600 font-medium">جاري تحميل الخريطة...</p>
        <p className="text-sm text-gray-500 mt-1">Loading map...</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
