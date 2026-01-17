"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// Skeleton Component - هيكل التحميل
// Unified skeleton loading placeholder
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from "@sahool/shared-utils";

export interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular";
  width?: string | number;
  height?: string | number;
  animate?: boolean;
}

export function Skeleton({
  className = "",
  variant = "rectangular",
  width,
  height,
  animate = true,
}: SkeletonProps) {
  const variantClasses = {
    text: "rounded h-4",
    circular: "rounded-full",
    rectangular: "rounded-lg",
  };

  const style: React.CSSProperties = {
    width: width ?? (variant === "circular" ? height : "100%"),
    height:
      height ??
      (variant === "text" ? "1rem" : variant === "circular" ? width : "1rem"),
  };

  return (
    <div
      className={cn(
        "bg-gray-200",
        animate && "animate-pulse",
        variantClasses[variant],
        className,
      )}
      style={style}
    />
  );
}

// Compound components for common use cases
export function SkeletonCard({ className = "" }: { className?: string }) {
  return (
    <div
      className={cn(
        "bg-white rounded-lg border border-gray-200 p-4",
        className,
      )}
    >
      <Skeleton variant="rectangular" height={20} className="mb-3 w-1/2" />
      <Skeleton variant="text" className="mb-2" />
      <Skeleton variant="text" className="mb-2" />
      <Skeleton variant="text" width="75%" />
    </div>
  );
}

export function SkeletonTable({
  rows = 5,
  cols = 4,
}: {
  rows?: number;
  cols?: number;
}) {
  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex gap-4 p-3 bg-gray-50 rounded-lg">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} variant="text" className="flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="flex gap-4 p-3">
          {Array.from({ length: cols }).map((_, colIdx) => (
            <Skeleton key={colIdx} variant="text" className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}
