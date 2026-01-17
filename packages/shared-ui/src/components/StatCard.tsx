"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// StatCard Component - بطاقة الإحصائيات
// Unified statistics card for displaying KPIs and metrics
// ═══════════════════════════════════════════════════════════════════════════════

import { cn, formatNumber } from "@sahool/shared-utils";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";

export interface StatCardProps {
  title: string;
  value: number | string;
  icon?: LucideIcon;
  trend?: number;
  trendLabel?: string;
  locale?: "ar" | "en";
  className?: string;
  color?: "default" | "primary" | "success" | "warning" | "danger";
}

const colorClasses = {
  default: "bg-gray-100 text-gray-600",
  primary: "bg-sahool-100 text-sahool-600",
  success: "bg-green-100 text-green-600",
  warning: "bg-yellow-100 text-yellow-600",
  danger: "bg-red-100 text-red-600",
};

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendLabel,
  locale = "ar",
  className = "",
  color = "default",
}: StatCardProps) {
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

  return (
    <div
      className={cn(
        "bg-white rounded-lg border border-gray-200 p-4 shadow-sm",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{displayValue}</p>

          {trend !== undefined && (
            <div
              className={cn("flex items-center gap-1 mt-2 text-sm", trendColor)}
            >
              {TrendIcon && <TrendIcon size={14} />}
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
            <Icon size={24} />
          </div>
        )}
      </div>
    </div>
  );
}
