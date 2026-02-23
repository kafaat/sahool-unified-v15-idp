"use client";

// Spray Charts - Product Usage & Cost Distribution
// مخططات الرش - استخدام المنتجات وتوزيع التكاليف

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

export const CHART_COLORS = {
  primary: "#2E7D32",
  secondary: "#4CAF50",
  accent: "#81C784",
  warning: "#FF9800",
};

export const PIE_COLORS = ["#2E7D32", "#4CAF50", "#81C784", "#A5D6A7"];

export interface ProductUsageItem {
  type: string;
  quantity: number;
  cost: number;
}

interface ProductUsageChartProps {
  data: ProductUsageItem[];
  productTypeLabels: Record<string, string>;
}

interface CostDistributionChartProps {
  data: ProductUsageItem[];
  productTypeLabels: Record<string, string>;
}

export function ProductUsageChart({
  data,
  productTypeLabels,
}: ProductUsageChartProps) {
  return (
    <div className="lg:col-span-2">
      <h3 className="font-bold text-gray-900 mb-4">استخدام المنتجات</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="type"
              tick={{ fontSize: 11 }}
              tickFormatter={(value) => productTypeLabels[value] || value}
            />
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
              dataKey="quantity"
              fill={CHART_COLORS.primary}
              radius={[4, 4, 0, 0]}
              name="الكمية (لتر)"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function CostDistributionChart({
  data,
  productTypeLabels,
}: CostDistributionChartProps) {
  return (
    <div>
      <h3 className="font-bold text-gray-900 mb-4">توزيع التكاليف</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="cost"
              nameKey="type"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ type, percent }) =>
                `${productTypeLabels[type]} ${((percent || 0) * 100).toFixed(0)}%`
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
      </div>
    </div>
  );
}
