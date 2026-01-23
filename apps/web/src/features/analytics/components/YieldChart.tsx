/**
 * Yield Chart Component
 * مكون رسم بياني للمحصول
 *
 * Performance optimizations:
 * - React.memo prevents re-renders when props don't change
 * - useMemo memoizes chart rendering to prevent expensive recalculations
 */

"use client";

import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { DataPoint, ChartType } from "../types";

interface YieldChartProps {
  data: DataPoint[];
  chartType?: ChartType;
  title?: string;
  titleAr?: string;
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
}

// Memoized tooltip style to prevent object recreation
const TOOLTIP_STYLE = {
  backgroundColor: "#fff",
  border: "1px solid #e5e7eb",
  borderRadius: "8px",
  padding: "8px 12px",
} as const;

const YieldChartComponent: React.FC<YieldChartProps> = ({
  data,
  chartType = "line",
  title,
  titleAr,
  height = 400,
  showLegend = true,
  showGrid = true,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
        <p className="text-gray-600">لا توجد بيانات متاحة</p>
        <p className="text-sm text-gray-500 mt-1">No data available</p>
      </div>
    );
  }

  // Memoize chart rendering to prevent expensive recalculations
  const chartElement = useMemo(() => {
    const commonProps = {
      data,
    };

    switch (chartType) {
      case "bar":
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis
              dataKey="label"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            {showLegend && <Legend />}
            <Bar
              dataKey="value"
              fill="#10b981"
              name="الإنتاج"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        );
      case "area":
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis
              dataKey="label"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            {showLegend && <Legend />}
            <Area
              type="monotone"
              dataKey="value"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.3}
              name="الإنتاج"
            />
          </AreaChart>
        );
      case "line":
      default:
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis
              dataKey="label"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            {showLegend && <Legend />}
            <Line
              type="monotone"
              dataKey="value"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="الإنتاج"
            />
          </LineChart>
        );
    }
  }, [data, chartType, showGrid, showLegend]);

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      {(title || titleAr) && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            {titleAr || title}
          </h3>
          {title && titleAr && (
            <p className="text-sm text-gray-600 mt-1">{title}</p>
          )}
        </div>
      )}

      <div style={{ height: `${height}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartElement}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Memoize component for performance optimization
export const YieldChart = React.memo(YieldChartComponent);
YieldChart.displayName = "YieldChart";

export default YieldChart;
