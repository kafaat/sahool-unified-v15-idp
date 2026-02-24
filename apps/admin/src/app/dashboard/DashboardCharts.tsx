"use client";

/**
 * Dashboard Charts Components
 * مكونات الرسوم البيانية للوحة التحكم
 *
 * Separated from the main dashboard page to enable lazy loading of recharts (~120KB).
 * These components are dynamically imported via DashboardCharts.dynamic.tsx.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";

// Chart colors
const CHART_COLORS = {
  primary: "#2E7D32",
  secondary: "#4CAF50",
  accent: "#81C784",
  warning: "#FF9800",
  danger: "#F44336",
  info: "#2196F3",
};

const PIE_COLORS = ["#2E7D32", "#4CAF50", "#81C784", "#A5D6A7", "#C8E6C9"];

// ═══════════════════════════════════════════════════════════════════════════
// Yield Trend Chart
// ═══════════════════════════════════════════════════════════════════════════

interface YieldTrendChartProps {
  data: Array<{ month: string; yield: number; forecast: number }>;
}

export function YieldTrendChart({ data }: YieldTrendChartProps) {
  if (data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <p>لا توجد بيانات متاحة</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data}>
        <defs>
          <linearGradient id="yieldGradient" x1="0" y1="0" x2="0" y2="1">
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
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e0e0e0",
            borderRadius: "8px",
            direction: "rtl",
          }}
        />
        <Area
          type="monotone"
          dataKey="yield"
          stroke={CHART_COLORS.primary}
          fill="url(#yieldGradient)"
          strokeWidth={2}
          name="الإنتاج الفعلي"
        />
        <Line
          type="monotone"
          dataKey="forecast"
          stroke={CHART_COLORS.warning}
          strokeDasharray="5 5"
          strokeWidth={2}
          dot={false}
          name="التوقعات"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Weekly Activity Chart
// ═══════════════════════════════════════════════════════════════════════════

interface WeeklyActivityChartProps {
  data: Array<{
    day: string;
    diagnoses: number;
    irrigations: number;
    alerts: number;
  }>;
}

export function WeeklyActivityChart({ data }: WeeklyActivityChartProps) {
  if (data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <p>لا توجد بيانات متاحة</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="day" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e0e0e0",
            borderRadius: "8px",
            direction: "rtl",
          }}
        />
        <Bar
          dataKey="diagnoses"
          fill={CHART_COLORS.primary}
          radius={[4, 4, 0, 0]}
          name="تشخيصات"
        />
        <Bar
          dataKey="irrigations"
          fill={CHART_COLORS.info}
          radius={[4, 4, 0, 0]}
          name="عمليات ري"
        />
        <Bar
          dataKey="alerts"
          fill={CHART_COLORS.danger}
          radius={[4, 4, 0, 0]}
          name="تنبيهات"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Crop Distribution Chart
// ═══════════════════════════════════════════════════════════════════════════

interface CropDistributionChartProps {
  data: Array<{ name: string; value: number }>;
}

export function CropDistributionChart({ data }: CropDistributionChartProps) {
  if (data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <p>لا توجد بيانات متاحة</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={40}
          outerRadius={70}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent }) =>
            `${name} ${((percent || 0) * 100).toFixed(0)}%`
          }
          labelLine={false}
        >
          {data.map((_entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={PIE_COLORS[index % PIE_COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
