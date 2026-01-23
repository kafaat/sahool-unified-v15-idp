"use client";

import { cn } from "@sahool/shared-utils";
import { forwardRef, HTMLAttributes } from "react";

/** Spinner size options */
export type SpinnerSize = "sm" | "md" | "lg" | "xl";

/** Spinner color options */
export type SpinnerColor = "primary" | "secondary" | "white";

export interface LoadingSpinnerProps extends HTMLAttributes<HTMLDivElement> {
  /** Size of the spinner */
  size?: SpinnerSize;
  /** Color variant of the spinner */
  color?: SpinnerColor;
  /** Additional CSS classes */
  className?: string;
  /** Visible label text (also used for screen readers) */
  label?: string;
  /** Screen reader only text (overrides label for a11y) */
  srLabel?: string;
}

const sizeClasses: Record<SpinnerSize, string> = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-[3px]",
  xl: "h-16 w-16 border-4",
};

const colorClasses: Record<SpinnerColor, string> = {
  primary: "border-sahool-600 border-t-transparent",
  secondary: "border-gray-600 border-t-transparent",
  white: "border-white border-t-transparent",
};

/**
 * Loading Spinner Component
 * مكون مؤشر التحميل
 *
 * Displays an accessible loading indicator with optional label.
 *
 * @example
 * <LoadingSpinner size="lg" label="Loading data..." />
 */
export const LoadingSpinner = forwardRef<HTMLDivElement, LoadingSpinnerProps>(
  (
    {
      size = "md",
      color = "primary",
      className,
      label,
      srLabel,
      ...props
    },
    ref,
  ) => {
    const accessibleLabel = srLabel || label || "جاري التحميل...";

    return (
      <div
        ref={ref}
        className={cn("inline-flex flex-col items-center gap-2", className)}
        role="status"
        aria-label={accessibleLabel}
        {...props}
      >
        <div
          className={cn(
            "animate-spin rounded-full",
            sizeClasses[size],
            colorClasses[color],
          )}
          aria-hidden="true"
        />
        {label && (
          <span className="text-sm text-gray-600" aria-hidden="true">
            {label}
          </span>
        )}
      </div>
    );
  },
);

LoadingSpinner.displayName = "LoadingSpinner";
