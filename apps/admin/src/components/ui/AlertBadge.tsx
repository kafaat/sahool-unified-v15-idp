"use client";

// Alert Badge Component
// شارة التنبيه

import { cn, getSeverityColor, getSeverityLabel } from "@/lib/utils";

interface AlertBadgeProps {
  severity: "low" | "medium" | "high" | "critical";
  className?: string;
  locale?: string;
}

export default function AlertBadge({
  severity,
  className = "",
  locale = "ar",
}: AlertBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        getSeverityColor(severity),
        className,
      )}
    >
      {getSeverityLabel(severity, locale)}
    </span>
  );
}
