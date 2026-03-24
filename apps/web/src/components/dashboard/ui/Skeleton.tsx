import React from "react";
import { clsx } from "clsx";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "rectangular" | "circular";
  width?: string | number;
  height?: string | number;
  /** Animation type */
  animation?: "pulse" | "wave" | "none";
  /** Screen reader label */
  label?: string;
}

export const Skeleton = React.memo<SkeletonProps>(function Skeleton({
  className = "",
  variant = "rectangular",
  width,
  height,
  animation = "pulse",
  label = "جاري التحميل",
}) {
  const variantStyles = {
    text: "h-4 rounded",
    rectangular: "rounded-lg",
    circular: "rounded-full",
  };

  const animationStyles = {
    pulse: "animate-pulse",
    wave: "skeleton-wave",
    none: "",
  };

  const style: React.CSSProperties = {
    width: width || "100%",
    height: height || (variant === "text" ? "1rem" : "100%"),
  };

  return (
    <div
      className={clsx(
        "bg-gray-200",
        variantStyles[variant],
        animationStyles[animation],
        className,
      )}
      style={style}
      role="status"
      aria-busy="true"
      aria-label={label}
    >
      <span className="sr-only">{label}</span>
    </div>
  );
});

/** KPI Card Skeleton - for dashboard metrics */
export const SkeletonCard = React.memo(function SkeletonCard() {
  return (
    <div
      className="bg-white rounded-xl p-4 space-y-3 shadow-sm"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل البطاقة - Loading card"
    >
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton width={80} height={12} variant="text" label="Loading title" />
          <Skeleton width={60} height={24} variant="text" label="Loading value" />
        </div>
        <Skeleton width={40} height={40} variant="circular" label="Loading icon" />
      </div>
      <Skeleton width={100} height={12} variant="text" label="Loading subtitle" />
      <span className="sr-only">جاري تحميل البطاقة - Loading card</span>
    </div>
  );
});

/** Task Item Skeleton */
export const SkeletonTaskItem = React.memo(function SkeletonTaskItem() {
  return (
    <div
      className="bg-white rounded-lg p-3 border-e-4 border-gray-300 space-y-2"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل المهمة - Loading task"
    >
      <div className="flex justify-between items-start">
        <Skeleton width="60%" height={16} variant="text" />
        <Skeleton width={60} height={20} variant="rectangular" />
      </div>
      <Skeleton width="40%" height={12} variant="text" />
      <div className="flex justify-between items-center">
        <Skeleton width={80} height={12} variant="text" />
        <Skeleton width={24} height={24} variant="circular" />
      </div>
      <span className="sr-only">جاري تحميل المهمة - Loading task</span>
    </div>
  );
});

/** Event Item Skeleton */
export const SkeletonEventItem = React.memo(function SkeletonEventItem() {
  return (
    <div
      className="bg-white rounded-lg p-3 border space-y-2"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل الحدث - Loading event"
    >
      <div className="flex items-center gap-2">
        <Skeleton width={24} height={24} variant="circular" />
        <Skeleton width="50%" height={14} variant="text" />
      </div>
      <Skeleton width="80%" height={12} variant="text" />
      <Skeleton width={60} height={10} variant="text" />
      <span className="sr-only">جاري تحميل الحدث - Loading event</span>
    </div>
  );
});

/** Table Row Skeleton */
export const SkeletonTableRow = React.memo(function SkeletonTableRow({
  columns = 4,
}: {
  columns?: number;
}) {
  return (
    <tr
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل الصف - Loading row"
    >
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton
            width={i === 0 ? "80%" : i === columns - 1 ? 60 : "60%"}
            height={16}
            variant="text"
          />
        </td>
      ))}
    </tr>
  );
});

/** Form Field Skeleton */
export const SkeletonFormField = React.memo(function SkeletonFormField() {
  return (
    <div
      className="space-y-2"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل الحقل - Loading field"
    >
      <Skeleton width={100} height={14} variant="text" />
      <Skeleton width="100%" height={44} variant="rectangular" />
      <span className="sr-only">جاري تحميل الحقل - Loading field</span>
    </div>
  );
});

/** Chart Skeleton */
export const SkeletonChart = React.memo(function SkeletonChart({
  height = 200,
}: {
  height?: number;
}) {
  return (
    <div
      className="bg-white rounded-xl p-4 space-y-4"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل الرسم البياني - Loading chart"
    >
      <div className="flex items-center justify-between">
        <Skeleton width={120} height={20} variant="text" />
        <div className="flex gap-2">
          <Skeleton width={60} height={28} variant="rectangular" />
          <Skeleton width={60} height={28} variant="rectangular" />
        </div>
      </div>
      <Skeleton width="100%" height={height} variant="rectangular" />
      <div className="flex justify-center gap-4">
        <Skeleton width={80} height={12} variant="text" />
        <Skeleton width={80} height={12} variant="text" />
        <Skeleton width={80} height={12} variant="text" />
      </div>
      <span className="sr-only">جاري تحميل الرسم البياني - Loading chart</span>
    </div>
  );
});

/** Map Skeleton */
export const SkeletonMap = React.memo(function SkeletonMap({
  height = 300,
}: {
  height?: number;
}) {
  return (
    <div
      className="bg-white rounded-xl overflow-hidden relative"
      style={{ height }}
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل الخريطة - Loading map"
    >
      <Skeleton width="100%" height="100%" variant="rectangular" animation="wave" />
      <div className="absolute bottom-4 start-4 bg-white rounded-lg p-2 shadow-md">
        <div className="flex gap-1">
          <Skeleton width={28} height={28} variant="rectangular" />
          <Skeleton width={28} height={28} variant="rectangular" />
        </div>
      </div>
      <span className="sr-only">جاري تحميل الخريطة - Loading map</span>
    </div>
  );
});

/** Alert/Notification Skeleton */
export const SkeletonAlert = React.memo(function SkeletonAlert() {
  return (
    <div
      className="bg-white rounded-lg p-4 border-s-4 border-gray-300 space-y-2"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل التنبيه - Loading alert"
    >
      <div className="flex items-center gap-3">
        <Skeleton width={20} height={20} variant="circular" />
        <Skeleton width="70%" height={16} variant="text" />
      </div>
      <Skeleton width="90%" height={14} variant="text" />
      <div className="flex gap-2 mt-2">
        <Skeleton width={80} height={32} variant="rectangular" />
        <Skeleton width={80} height={32} variant="rectangular" />
      </div>
      <span className="sr-only">جاري تحميل التنبيه - Loading alert</span>
    </div>
  );
});

/** Page Header Skeleton */
export const SkeletonPageHeader = React.memo(function SkeletonPageHeader() {
  return (
    <div
      className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل العنوان - Loading header"
    >
      <div className="space-y-2">
        <Skeleton width={200} height={28} variant="text" />
        <Skeleton width={300} height={16} variant="text" />
      </div>
      <div className="flex gap-2">
        <Skeleton width={100} height={40} variant="rectangular" />
        <Skeleton width={120} height={40} variant="rectangular" />
      </div>
      <span className="sr-only">جاري تحميل العنوان - Loading header</span>
    </div>
  );
});

/** Dashboard Grid Skeleton - Complete dashboard loading state */
export const SkeletonDashboard = React.memo(function SkeletonDashboard() {
  return (
    <div
      className="space-y-6"
      role="status"
      aria-busy="true"
      aria-label="جاري تحميل لوحة المعلومات - Loading dashboard"
    >
      <SkeletonPageHeader />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SkeletonChart height={280} />
        </div>
        <div className="space-y-4">
          <SkeletonAlert />
          <SkeletonAlert />
        </div>
      </div>

      {/* Tasks and Events */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-4 space-y-3">
          <Skeleton width={120} height={20} variant="text" />
          <SkeletonTaskItem />
          <SkeletonTaskItem />
          <SkeletonTaskItem />
        </div>
        <div className="bg-white rounded-xl p-4 space-y-3">
          <Skeleton width={120} height={20} variant="text" />
          <SkeletonEventItem />
          <SkeletonEventItem />
          <SkeletonEventItem />
        </div>
      </div>

      <span className="sr-only">جاري تحميل لوحة المعلومات - Loading dashboard</span>
    </div>
  );
});
