"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// SeverityBadge Component - شارة الخطورة
// Unified severity badge for displaying severity levels
// ═══════════════════════════════════════════════════════════════════════════════

import { cn, getSeverityColor, getSeverityLabel } from "@sahool/shared-utils";
import { AlertTriangle, AlertCircle, AlertOctagon, Info, LucideIcon } from "lucide-react";
import { forwardRef, HTMLAttributes } from "react";

/** Severity level options */
export type SeverityLevel = "low" | "medium" | "high" | "critical";

/** Badge size options */
export type SeverityBadgeSize = "sm" | "md" | "lg";

export interface SeverityBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** Severity level to display */
  severity: SeverityLevel;
  /** Additional CSS classes */
  className?: string;
  /** Display language */
  locale?: "ar" | "en";
  /** Whether to show the severity icon */
  showIcon?: boolean;
  /** Badge size */
  size?: SeverityBadgeSize;
  /** Custom icon override */
  icon?: LucideIcon;
}

const sizeClasses: Record<SeverityBadgeSize, string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-0.5 text-sm",
  lg: "px-3 py-1 text-base",
};

const iconSizes: Record<SeverityBadgeSize, number> = {
  sm: 12,
  md: 14,
  lg: 16,
};

const SeverityIcon: Record<SeverityLevel, LucideIcon> = {
  low: Info,
  medium: AlertTriangle,
  high: AlertCircle,
  critical: AlertOctagon,
};

/**
 * Severity Badge Component
 * شارة الخطورة
 *
 * Displays a severity indicator with icon and localized label.
 *
 * @example
 * <SeverityBadge severity="high" locale="en" />
 * <SeverityBadge severity="critical" showIcon={false} />
 */
export const SeverityBadge = forwardRef<HTMLSpanElement, SeverityBadgeProps>(
  (
    {
      severity,
      className = "",
      locale = "ar",
      showIcon = true,
      size = "sm",
      icon,
      ...props
    },
    ref,
  ) => {
    const Icon = icon || SeverityIcon[severity];

    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center gap-1 rounded-full font-medium",
          sizeClasses[size],
          getSeverityColor(severity),
          className,
        )}
        role="status"
        aria-label={`${getSeverityLabel(severity, "en")} severity`}
        {...props}
      >
        {showIcon && <Icon size={iconSizes[size]} aria-hidden="true" />}
        {getSeverityLabel(severity, locale)}
      </span>
    );
  },
);

SeverityBadge.displayName = "SeverityBadge";
