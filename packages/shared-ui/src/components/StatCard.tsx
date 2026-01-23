"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// StatCard Component - بطاقة الإحصائيات
// Unified statistics card for displaying KPIs and metrics
// ═══════════════════════════════════════════════════════════════════════════════

import { cn, formatNumber } from "@sahool/shared-utils";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { forwardRef, HTMLAttributes } from "react";

/** Stat card color variants */
export type StatCardColor = "default" | "primary" | "success" | "warning" | "danger";

export interface StatCardProps extends HTMLAttributes<HTMLDivElement> {
  /** Title/label of the statistic */
  title: string;
  /** The statistic value (number will be formatted) */
  value: number | string;
  /** Icon displayed next to the value */
  icon?: LucideIcon;
  /** Percentage change (positive/negative) */
  trend?: number;
  /** Label for the trend (e.g., "vs last month") */
  trendLabel?: string;
  /** Display locale for number formatting */
  locale?: "ar" | "en";
  /** Additional CSS classes */
  className?: string;
  /** Color theme for the icon background */
  color?: StatCardColor;
  /** Accessible description of the trend */
  trendDescription?: string;
}

const colorClasses = {
  default: "bg-gray-100 text-gray-600",
  primary: "bg-sahool-100 text-sahool-600",
  success: "bg-green-100 text-green-600",
  warning: "bg-yellow-100 text-yellow-600",
  danger: "bg-red-100 text-red-600",
};

/**
 * Stat Card Component
 * بطاقة الإحصائيات
 *
 * Displays a KPI or metric with optional trend indicator and icon.
 *
 * @example
 * <StatCard
 *   title="Total Revenue"
 *   value={125000}
 *   trend={12.5}
 *   trendLabel="vs last month"
 *   icon={DollarSign}
 *   color="success"
 * />
 */
export const StatCard = forwardRef<HTMLDivElement, StatCardProps>(
  (
    {
      title,
      value,
      icon: Icon,
      trend,
      trendLabel,
      locale = "ar",
      className = "",
      color = "default",
      trendDescription,
      ...props
    },
    ref,
  ) => {
    const TrendIcon =
      trend === undefined
        ? null
        : trend > 0
          ? TrendingUp
          : trend < 0
            ? TrendingDown
            : Minus;

    const trendColor =
      trend === undefined
        ? ""
        : trend > 0
          ? "text-green-600"
          : trend < 0
            ? "text-red-600"
            : "text-gray-500";

    const displayValue =
      typeof value === "number" ? formatNumber(value, locale) : value;

    // Generate accessible trend description
    const accessibleTrendDesc =
      trendDescription ||
      (trend !== undefined
        ? `${trend > 0 ? "Increased" : trend < 0 ? "Decreased" : "No change"} ${Math.abs(trend)}%${trendLabel ? ` ${trendLabel}` : ""}`
        : undefined);

    return (
      <div
        ref={ref}
        className={cn(
          "bg-white rounded-lg border border-gray-200 p-4 shadow-sm",
          className,
        )}
        {...props}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm text-gray-500 mb-1">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{displayValue}</p>

            {trend !== undefined && (
              <div
                className={cn("flex items-center gap-1 mt-2 text-sm", trendColor)}
                aria-label={accessibleTrendDesc}
              >
                {TrendIcon && <TrendIcon size={14} aria-hidden="true" />}
                <span>
                  {trend > 0 ? "+" : ""}
                  {trend}%
                </span>
                {trendLabel && (
                  <span className="text-gray-400">{trendLabel}</span>
                )}
              </div>
            )}
          </div>

          {Icon && (
            <div className={cn("p-3 rounded-lg", colorClasses[color])}>
              <Icon size={24} aria-hidden="true" />
            </div>
          )}
        </div>
      </div>
    );
  },
);

StatCard.displayName = "StatCard";
