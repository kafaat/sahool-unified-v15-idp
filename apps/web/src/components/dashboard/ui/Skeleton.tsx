"use client";

import React from "react";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "rectangular" | "circular";
  width?: string | number;
  height?: string | number;
}

export const Skeleton = React.memo<SkeletonProps>(function Skeleton({
  className = "",
  variant = "rectangular",
  width,
  height,
}) {
  const variantStyles = {
    text: "h-4 rounded",
    rectangular: "rounded-lg",
    circular: "rounded-full",
  };

  const style: React.CSSProperties = {
    width: width || "100%",
    height: height || (variant === "text" ? "1rem" : "100%"),
  };

  return (
    <div
      className={`animate-pulse bg-gray-200 ${variantStyles[variant]} ${className}`}
      style={style}
      aria-busy="true"
      aria-label="جاري التحميل"
    />
  );
});

export const SkeletonCard = React.memo(function SkeletonCard() {
  return (
    <div
      className="bg-white rounded-xl p-4 space-y-3 shadow-sm"
      aria-busy="true"
      aria-label="جاري تحميل البطاقة"
    >
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton width={80} height={12} variant="text" />
          <Skeleton width={60} height={24} variant="text" />
        </div>
        <Skeleton width={40} height={40} variant="circular" />
      </div>
      <Skeleton width={100} height={12} variant="text" />
    </div>
  );
});

export const SkeletonTaskItem = React.memo(function SkeletonTaskItem() {
  return (
    <div
      className="bg-white rounded-lg p-3 border-r-4 border-gray-300 space-y-2"
      aria-busy="true"
      aria-label="جاري تحميل المهمة"
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
    </div>
  );
});

export const SkeletonEventItem = React.memo(function SkeletonEventItem() {
  return (
    <div
      className="bg-white rounded-lg p-3 border space-y-2"
      aria-busy="true"
      aria-label="جاري تحميل الحدث"
    >
      <div className="flex items-center gap-2">
        <Skeleton width={24} height={24} variant="circular" />
        <Skeleton width="50%" height={14} variant="text" />
      </div>
      <Skeleton width="80%" height={12} variant="text" />
      <Skeleton width={60} height={10} variant="text" />
    </div>
  );
});
