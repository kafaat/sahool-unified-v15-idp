"use client";

// Statistics Card Component
// بطاقة الإحصائيات

import { cn, formatNumber } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  suffix?: string;
  className?: string;
  iconColor?: string;
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  suffix = "",
  className = "",
  iconColor = "text-sahool-600",
}: StatCardProps) {
  const displayValue = typeof value === "number" ? formatNumber(value) : value;

  return (
    <div
      className={cn(
        "bg-white rounded-xl shadow-sm border border-gray-100 p-6 transition-all hover:shadow-md",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">
            {displayValue}
            {suffix && (
              <span className="text-lg text-gray-500 mr-1">{suffix}</span>
            )}
          </p>
          {trend && (
            <p
              className={cn(
                "text-sm mt-2 flex items-center gap-1",
                trend.isPositive ? "text-green-600" : "text-red-600",
              )}
            >
              <span>{trend.isPositive ? "↑" : "↓"}</span>
              <span>{Math.abs(trend.value)}%</span>
              <span className="text-gray-500">من الأسبوع الماضي</span>
            </p>
          )}
        </div>
        <div
          className={cn(
            "p-3 rounded-xl bg-opacity-10",
            iconColor.replace("text-", "bg-"),
          )}
        >
          <Icon className={cn("w-6 h-6", iconColor)} />
        </div>
      </div>
    </div>
  );
}
