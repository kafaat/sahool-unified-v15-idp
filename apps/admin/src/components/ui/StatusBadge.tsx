// Status Badge Component
// شارة الحالة

import { cn, getStatusColor, getStatusLabel } from "@/lib/utils";

export interface StatusBadgeProps {
  status: string;
  className?: string;
  locale?: "ar" | "en";
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-0.5 text-sm",
  lg: "px-3 py-1 text-base",
};

export function StatusBadge({
  status,
  className = "",
  locale = "ar",
  size = "sm",
}: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full font-medium",
        sizeClasses[size],
        getStatusColor(status),
        className,
      )}
    >
      {getStatusLabel(status, locale)}
    </span>
  );
}

export default StatusBadge;
