"use client";

/**
 * Analytics Chart Component
 * مكون الرسوم البيانية التحليلية
 */

import { useMemo } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from "recharts";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export type ChartType = "area" | "bar" | "line" | "pie" | "donut";

export interface ChartDataPoint {
  name: string;
  nameAr?: string;
  [key: string]: string | number | undefined;
}

export interface ChartSeries {
  dataKey: string;
  name: string;
  nameAr?: string;
  color?: string;
  type?: "monotone" | "linear" | "step";
}

interface AnalyticsChartProps {
  type: ChartType;
  data: ChartDataPoint[];
  series: ChartSeries[];
  title?: string;
  titleAr?: string;
  subtitle?: string;
  subtitleAr?: string;
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  showTooltip?: boolean;
  stacked?: boolean;
  gradient?: boolean;
  className?: string;
  // Stats
  currentValue?: number;
  previousValue?: number;
  valuePrefix?: string;
  valueSuffix?: string;
  // Pie chart specific
  innerRadius?: number;
  outerRadius?: number;
  showLabels?: boolean;
}

// Default color palette
const defaultColors = [
  "#10B981", // Sahool green
  "#3B82F6", // Blue
  "#F59E0B", // Yellow
  "#EF4444", // Red
  "#8B5CF6", // Purple
  "#EC4899", // Pink
  "#06B6D4", // Cyan
  "#84CC16", // Lime
];

// Custom tooltip component
function CustomTooltip({
  active,
  payload,
  label,
  isRtl = true,
}: TooltipProps<number, string> & { isRtl?: boolean }) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl border border-gray-200 dark:border-gray-700 p-3 min-w-[150px]">
      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
        {label}
      </p>
      <div className="space-y-1">
        {payload.map((entry, index) => (
          <div
            key={index}
            className="flex items-center justify-between gap-4 text-sm"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-600 dark:text-gray-400">
                {entry.name}
              </span>
            </div>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {typeof entry.value === "number"
                ? entry.value.toLocaleString(isRtl ? "ar-YE" : "en-US")
                : entry.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AnalyticsChart({
  type,
  data,
  series,
  title,
  titleAr,
  subtitle,
  subtitleAr,
  height = 300,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  stacked = false,
  gradient = true,
  className = "",
  currentValue,
  previousValue,
  valuePrefix = "",
  valueSuffix = "",
  innerRadius = 60,
  outerRadius = 80,
  showLabels = false,
}: AnalyticsChartProps) {
  // Calculate trend
  const trend = useMemo(() => {
    if (currentValue === undefined || previousValue === undefined) return null;
    if (previousValue === 0) return { direction: "up", percentage: 100 };

    const change = ((currentValue - previousValue) / previousValue) * 100;
    return {
      direction: change > 0 ? "up" : change < 0 ? "down" : "neutral",
      percentage: Math.abs(change),
    };
  }, [currentValue, previousValue]);

  // Prepare series with colors
  const preparedSeries = useMemo(() => {
    return series.map((s, index) => ({
      ...s,
      color: s.color || defaultColors[index % defaultColors.length] || "#10B981",
    }));
  }, [series]);

  // Render gradient definitions
  const renderGradients = () => (
    <defs>
      {preparedSeries.map((s, index) => (
        <linearGradient
          key={`gradient-${index}`}
          id={`gradient-${s.dataKey}`}
          x1="0"
          y1="0"
          x2="0"
          y2="1"
        >
          <stop offset="5%" stopColor={s.color} stopOpacity={0.3} />
          <stop offset="95%" stopColor={s.color} stopOpacity={0} />
        </linearGradient>
      ))}
    </defs>
  );

  // Render chart based on type
  const renderChart = () => {
    switch (type) {
      case "area":
        return (
          <AreaChart data={data}>
            {gradient && renderGradients()}
            {showGrid && (
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            )}
            <XAxis
              dataKey="nameAr"
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={{ stroke: "#E5E7EB" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) =>
                value.toLocaleString("ar-YE", { notation: "compact" })
              }
            />
            {showTooltip && (
              <Tooltip content={<CustomTooltip />} />
            )}
            {showLegend && (
              <Legend
                wrapperStyle={{ paddingTop: 20 }}
                formatter={(value) => (
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {value}
                  </span>
                )}
              />
            )}
            {preparedSeries.map((s) => (
              <Area
                key={s.dataKey}
                type={s.type || "monotone"}
                dataKey={s.dataKey}
                name={s.nameAr || s.name}
                stroke={s.color}
                fill={gradient ? `url(#gradient-${s.dataKey})` : s.color}
                fillOpacity={gradient ? 1 : 0.3}
                strokeWidth={2}
                stackId={stacked ? "stack" : undefined}
              />
            ))}
          </AreaChart>
        );

      case "bar":
        return (
          <BarChart data={data}>
            {showGrid && (
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            )}
            <XAxis
              dataKey="nameAr"
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={{ stroke: "#E5E7EB" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) =>
                value.toLocaleString("ar-YE", { notation: "compact" })
              }
            />
            {showTooltip && (
              <Tooltip content={<CustomTooltip />} />
            )}
            {showLegend && (
              <Legend
                wrapperStyle={{ paddingTop: 20 }}
                formatter={(value) => (
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {value}
                  </span>
                )}
              />
            )}
            {preparedSeries.map((s) => (
              <Bar
                key={s.dataKey}
                dataKey={s.dataKey}
                name={s.nameAr || s.name}
                fill={s.color}
                radius={[4, 4, 0, 0]}
                stackId={stacked ? "stack" : undefined}
              />
            ))}
          </BarChart>
        );

      case "line":
        return (
          <LineChart data={data}>
            {showGrid && (
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            )}
            <XAxis
              dataKey="nameAr"
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={{ stroke: "#E5E7EB" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) =>
                value.toLocaleString("ar-YE", { notation: "compact" })
              }
            />
            {showTooltip && (
              <Tooltip content={<CustomTooltip />} />
            )}
            {showLegend && (
              <Legend
                wrapperStyle={{ paddingTop: 20 }}
                formatter={(value) => (
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {value}
                  </span>
                )}
              />
            )}
            {preparedSeries.map((s) => (
              <Line
                key={s.dataKey}
                type={s.type || "monotone"}
                dataKey={s.dataKey}
                name={s.nameAr || s.name}
                stroke={s.color}
                strokeWidth={2}
                dot={{ fill: s.color, strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            ))}
          </LineChart>
        );

      case "pie":
      case "donut":
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={type === "donut" ? innerRadius : 0}
              outerRadius={outerRadius}
              paddingAngle={2}
              dataKey={preparedSeries[0]?.dataKey || "value"}
              nameKey="nameAr"
              label={
                showLabels
                  ? ({ name, percent }: { name: string; percent: number }) =>
                      `${name} (${(percent * 100).toFixed(0)}%)`
                  : false
              }
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={defaultColors[index % defaultColors.length] ?? "#10B981"}
                />
              ))}
            </Pie>
            {showTooltip && (
              <Tooltip content={<CustomTooltip />} />
            )}
            {showLegend && (
              <Legend
                layout="vertical"
                align="right"
                verticalAlign="middle"
                formatter={(value) => (
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {value}
                  </span>
                )}
              />
            )}
          </PieChart>
        );

      default:
        // Fallback to empty area chart
        return <AreaChart data={data}><Area dataKey="value" /></AreaChart>;
    }
  };

  return (
    <div
      className={cn(
        "bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700",
        className
      )}
    >
      {/* Header */}
      {(title || titleAr || currentValue !== undefined) && (
        <div className="flex items-start justify-between mb-6">
          <div>
            {(title || titleAr) && (
              <>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {titleAr || title}
                </h3>
                {(subtitle || subtitleAr) && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {subtitleAr || subtitle}
                  </p>
                )}
              </>
            )}
          </div>

          {currentValue !== undefined && (
            <div className="text-left">
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {valuePrefix}
                {currentValue.toLocaleString("ar-YE")}
                {valueSuffix}
              </div>
              {trend && (
                <div
                  className={cn(
                    "flex items-center gap-1 text-sm mt-1",
                    trend.direction === "up" && "text-green-600 dark:text-green-400",
                    trend.direction === "down" && "text-red-600 dark:text-red-400",
                    trend.direction === "neutral" && "text-gray-500 dark:text-gray-400"
                  )}
                >
                  {trend.direction === "up" && <TrendingUp className="w-4 h-4" />}
                  {trend.direction === "down" && <TrendingDown className="w-4 h-4" />}
                  {trend.direction === "neutral" && <Minus className="w-4 h-4" />}
                  <span>{trend.percentage.toFixed(1)}%</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
}

// Mini sparkline chart for compact displays
export function SparklineChart({
  data,
  dataKey,
  color = "#10B981",
  height = 40,
  className = "",
}: {
  data: ChartDataPoint[];
  dataKey: string;
  color?: string;
  height?: number;
  className?: string;
}) {
  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`sparkline-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            fill={`url(#sparkline-${dataKey})`}
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
