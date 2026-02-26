"use client";

// Profitability Charts - Extracted recharts components
// مخططات الربحية - مكونات recharts المستخرجة

import {
  BarChart,
  Bar,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Area,
  AreaChart,
} from "recharts";

export const CHART_COLORS = {
  primary: "#2E7D32",
  secondary: "#4CAF50",
  accent: "#81C784",
  warning: "#FF9800",
  danger: "#F44336",
  info: "#2196F3",
};

export const PIE_COLORS = [
  "#2E7D32",
  "#4CAF50",
  "#81C784",
  "#A5D6A7",
  "#C8E6C9",
  "#E8F5E9",
];

// --- MonthlyTrendChart ---

interface MonthlyTrendChartProps {
  data: Array<{
    month: string;
    revenue: number;
    costs: number;
    profit: number;
  }>;
}

export function MonthlyTrendChart({ data }: MonthlyTrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data}>
        <defs>
          <linearGradient
            id="revenueGradient"
            x1="0"
            y1="0"
            x2="0"
            y2="1"
          >
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
          <linearGradient id="costsGradient" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="5%"
              stopColor={CHART_COLORS.danger}
              stopOpacity={0.3}
            />
            <stop
              offset="95%"
              stopColor={CHART_COLORS.danger}
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
        <Legend />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke={CHART_COLORS.primary}
          fill="url(#revenueGradient)"
          strokeWidth={2}
          name="الإيرادات"
        />
        <Area
          type="monotone"
          dataKey="costs"
          stroke={CHART_COLORS.danger}
          fill="url(#costsGradient)"
          strokeWidth={2}
          name="التكاليف"
        />
        <Line
          type="monotone"
          dataKey="profit"
          stroke={CHART_COLORS.info}
          strokeWidth={3}
          dot={{ fill: CHART_COLORS.info, r: 4 }}
          name="الربح الصافي"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// --- CropProfitabilityChart ---

interface CropProfitabilityChartProps {
  data: Array<{
    crop: string;
    cropAr: string;
    revenue: number;
    costs: number;
    profit: number;
    margin: number;
    area: number;
  }>;
}

export function CropProfitabilityChart({ data }: CropProfitabilityChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis
          dataKey="cropAr"
          type="category"
          tick={{ fontSize: 11 }}
          width={80}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e0e0e0",
            borderRadius: "8px",
            direction: "rtl",
          }}
        />
        <Legend />
        <Bar
          dataKey="revenue"
          fill={CHART_COLORS.primary}
          name="الإيرادات"
          radius={[0, 4, 4, 0]}
        />
        <Bar
          dataKey="costs"
          fill={CHART_COLORS.danger}
          name="التكاليف"
          radius={[0, 4, 4, 0]}
        />
        <Bar
          dataKey="profit"
          fill={CHART_COLORS.info}
          name="الربح"
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

// --- CostBreakdownChart ---

interface CostBreakdownChartProps {
  data: Array<{
    category: string;
    categoryAr: string;
    amount: number;
    percentage: number;
  }>;
}

export function CostBreakdownChart({ data }: CostBreakdownChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          dataKey="amount"
          nameKey="categoryAr"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label={({ categoryAr, percentage }: { categoryAr: string; percentage: number }) =>
            `${categoryAr} ${percentage.toFixed(0)}%`
          }
          labelLine={true}
        >
          {data.map((_entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={PIE_COLORS[index % PIE_COLORS.length] ?? "#2E7D32"}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e0e0e0",
            borderRadius: "8px",
            direction: "rtl",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
