"use client";

// Satellite NDVI Trend Chart Component
// مكون مخطط اتجاه NDVI الفضائي

import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { formatDate } from "@/lib/utils";

export const CHART_COLORS = {
  primary: "#2E7D32",
  secondary: "#4CAF50",
  accent: "#81C784",
  warning: "#FF9800",
  danger: "#F44336",
  info: "#2196F3",
};

interface NDVITrendDataPoint {
  date: string;
  ndvi: number;
  fieldId: string;
  fieldName: string;
}

interface NDVITrendChartProps {
  data: NDVITrendDataPoint[];
}

export function NDVITrendChart({ data }: NDVITrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data}>
        <defs>
          <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="5%"
              stopColor={CHART_COLORS.primary}
              stopOpacity={0.3}
            />
            <stop
              offset="95%"
              stopColor={CHART_COLORS.primary}
              stopOpacity={0}
            />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11 }}
          tickFormatter={(value) =>
            new Date(value).toLocaleDateString("ar-YE", {
              month: "short",
              day: "numeric",
            })
          }
        />
        <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e0e0e0",
            borderRadius: "8px",
            direction: "rtl",
          }}
          labelFormatter={(value) => formatDate(value)}
        />
        <Area
          type="monotone"
          dataKey="ndvi"
          stroke={CHART_COLORS.primary}
          fill="url(#ndviGradient)"
          strokeWidth={2}
          name="NDVI"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
