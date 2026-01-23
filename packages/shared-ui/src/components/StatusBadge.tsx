"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// StatusBadge Component - شارة الحالة
// Unified status badge for displaying status indicators
// ═══════════════════════════════════════════════════════════════════════════════

import { cn, getStatusColor, getStatusLabel } from "@sahool/shared-utils";
import { forwardRef, HTMLAttributes } from "react";

/** Badge size options */
export type BadgeSize = "sm" | "md" | "lg";

/** Locale options */
export type Locale = "ar" | "en";

export interface StatusBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** Status value to display */
  status: string;
  /** Additional CSS classes */
  className?: string;
  /** Display language */
  locale?: Locale;
  /** Badge size */
  size?: BadgeSize;
  /** Whether this badge represents a live status */
  isLive?: boolean;
}

const sizeClasses: Record<BadgeSize, string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-0.5 text-sm",
  lg: "px-3 py-1 text-base",
};

/**
 * Status Badge Component
 * شارة الحالة
 *
 * Displays a status indicator with localized label and semantic colors.
 *
 * @example
 * <StatusBadge status="active" locale="en" />
 * <StatusBadge status="pending" locale="ar" size="lg" />
 */
export const StatusBadge = forwardRef<HTMLSpanElement, StatusBadgeProps>(
  (
    {
      status,
      className = "",
      locale = "ar",
      size = "sm",
      isLive = false,
      ...props
    },
    ref,
  ) => {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full font-medium",
          sizeClasses[size],
          getStatusColor(status),
          className,
        )}
        role="status"
        aria-live={isLive ? "polite" : undefined}
        {...props}
      >
        {getStatusLabel(status, locale)}
      </span>
    );
  },
);

StatusBadge.displayName = "StatusBadge";
