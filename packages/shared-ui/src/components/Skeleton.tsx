"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// Skeleton Component - هيكل التحميل
// Unified skeleton loading placeholder
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from "@sahool/shared-utils";
import { CSSProperties, forwardRef, HTMLAttributes } from "react";

/** Skeleton shape variants */
export type SkeletonVariant = "text" | "circular" | "rectangular";

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  /** Additional CSS classes */
  className?: string;
  /** Shape variant */
  variant?: SkeletonVariant;
  /** Width (CSS value or number for pixels) */
  width?: string | number;
  /** Height (CSS value or number for pixels) */
  height?: string | number;
  /** Whether to animate the skeleton */
  animate?: boolean;
  /** Accessible label for the loading state */
  label?: string;
}

const variantClasses: Record<SkeletonVariant, string> = {
  text: "rounded h-4",
  circular: "rounded-full",
  rectangular: "rounded-lg",
};

/**
 * Skeleton Component
 * هيكل التحميل
 *
 * Displays a placeholder loading animation while content is being fetched.
 *
 * @example
 * <Skeleton variant="text" width="80%" />
 * <Skeleton variant="circular" width={40} height={40} />
 */
export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  (
    {
      className = "",
      variant = "rectangular",
      width,
      height,
      animate = true,
      label = "جاري التحميل...",
      ...props
    },
    ref,
  ) => {
    const style: CSSProperties = {
      width: width ?? (variant === "circular" ? height : "100%"),
      height:
        height ??
        (variant === "text" ? "1rem" : variant === "circular" ? width : "1rem"),
    };

    return (
      <div
        ref={ref}
        className={cn(
          "bg-gray-200",
          animate && "animate-pulse",
          variantClasses[variant],
          className,
        )}
        style={style}
        role="progressbar"
        aria-busy="true"
        aria-label={label}
        aria-valuetext={label}
        {...props}
      />
    );
  },
);

Skeleton.displayName = "Skeleton";

// ═══════════════════════════════════════════════════════════════════════════════
// Compound Components
// ═══════════════════════════════════════════════════════════════════════════════

export interface SkeletonCardProps extends HTMLAttributes<HTMLDivElement> {
  /** Additional CSS classes */
  className?: string;
  /** Number of text lines to show */
  lines?: number;
  /** Whether to show a title skeleton */
  showTitle?: boolean;
}

/**
 * Skeleton Card Component
 * هيكل بطاقة التحميل
 *
 * Pre-configured skeleton for card loading states.
 */
export const SkeletonCard = forwardRef<HTMLDivElement, SkeletonCardProps>(
  ({ className = "", lines = 3, showTitle = true, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-white rounded-lg border border-gray-200 p-4",
          className,
        )}
        role="progressbar"
        aria-busy="true"
        aria-label="جاري تحميل البطاقة..."
        {...props}
      >
        {showTitle && (
          <Skeleton
            variant="rectangular"
            height={20}
            className="mb-3 w-1/2"
            aria-hidden="true"
          />
        )}
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton
            key={i}
            variant="text"
            className="mb-2"
            width={i === lines - 1 ? "75%" : "100%"}
            aria-hidden="true"
          />
        ))}
      </div>
    );
  },
);

SkeletonCard.displayName = "SkeletonCard";

export interface SkeletonTableProps extends HTMLAttributes<HTMLDivElement> {
  /** Number of rows */
  rows?: number;
  /** Number of columns */
  cols?: number;
  /** Whether to show header row */
  showHeader?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Skeleton Table Component
 * هيكل جدول التحميل
 *
 * Pre-configured skeleton for table loading states.
 */
export const SkeletonTable = forwardRef<HTMLDivElement, SkeletonTableProps>(
  ({ rows = 5, cols = 4, showHeader = true, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("space-y-2", className)}
        role="progressbar"
        aria-busy="true"
        aria-label="جاري تحميل الجدول..."
        {...props}
      >
        {/* Header */}
        {showHeader && (
          <div className="flex gap-4 p-3 bg-gray-50 rounded-lg">
            {Array.from({ length: cols }).map((_, i) => (
              <Skeleton key={i} variant="text" className="flex-1" aria-hidden="true" />
            ))}
          </div>
        )}
        {/* Rows */}
        {Array.from({ length: rows }).map((_, rowIdx) => (
          <div key={rowIdx} className="flex gap-4 p-3">
            {Array.from({ length: cols }).map((_, colIdx) => (
              <Skeleton key={colIdx} variant="text" className="flex-1" aria-hidden="true" />
            ))}
          </div>
        ))}
      </div>
    );
  },
);

SkeletonTable.displayName = "SkeletonTable";
