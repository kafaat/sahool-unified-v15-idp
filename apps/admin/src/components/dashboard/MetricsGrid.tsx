"use client";

// Metrics Grid Component
// شبكة المقاييس

import { memo } from "react";
import StatCard from "@/components/ui/StatCard";
import { LucideIcon } from "lucide-react";

export interface Metric {
  id?: string;
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  suffix?: string;
  iconColor?: string;
}

interface MetricsGridProps {
  metrics: Metric[];
  columns?: 2 | 3 | 4 | 5 | 6;
  className?: string;
}

// Static grid column classes - defined outside component to prevent recreation
const GRID_COLS: Record<number, string> = {
  2: "grid-cols-1 md:grid-cols-2",
  3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
  4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
  5: "grid-cols-1 md:grid-cols-2 lg:grid-cols-5",
  6: "grid-cols-1 md:grid-cols-3 lg:grid-cols-6",
};

function MetricsGrid({
  metrics,
  columns = 4,
  className = "",
}: MetricsGridProps) {
  return (
    <div className={`grid ${GRID_COLS[columns]} gap-6 ${className}`}>
      {metrics.map((metric) => (
        <StatCard
          key={metric.id || metric.title}
          title={metric.title}
          value={metric.value}
          icon={metric.icon}
          trend={metric.trend}
          suffix={metric.suffix}
          iconColor={metric.iconColor}
        />
      ))}
    </div>
  );
}

// Memoized export to prevent unnecessary re-renders
export default memo(MetricsGrid);
