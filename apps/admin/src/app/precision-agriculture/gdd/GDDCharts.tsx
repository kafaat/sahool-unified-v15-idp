'use client';

// GDD Chart Components - Lazy-loaded recharts wrappers
// مكونات الرسوم البيانية لدرجات النمو الحرارية

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { formatDate } from '@/lib/utils';

export const CHART_COLORS = {
  primary: '#2E7D32',
  secondary: '#4CAF50',
  accent: '#81C784',
  warning: '#FF9800',
};

// --- GDD Stage Distribution Bar Chart ---
// مخطط توزيع مراحل النمو

interface StageDataItem {
  stage: string;
  count: number;
}

interface GDDStageDistributionChartProps {
  data: StageDataItem[];
}

export function GDDStageDistributionChart({ data }: GDDStageDistributionChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis dataKey="stage" type="category" tick={{ fontSize: 11 }} width={80} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            direction: 'rtl',
          }}
        />
        <Bar dataKey="count" fill={CHART_COLORS.primary} radius={[0, 4, 4, 0]} name="عدد الحقول" />
      </BarChart>
    </ResponsiveContainer>
  );
}

// --- GDD History Line Chart ---
// مخطط تاريخ درجات النمو الحرارية

interface HistoryDataItem {
  date: string;
  gdd: number;
  temp_min: number;
  temp_max: number;
}

interface GDDHistoryChartProps {
  data: HistoryDataItem[];
}

export function GDDHistoryChart({ data }: GDDHistoryChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11 }}
          tickFormatter={(value) =>
            new Date(value).toLocaleDateString('ar-YE', {
              month: 'short',
              day: 'numeric',
            })
          }
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            direction: 'rtl',
          }}
          labelFormatter={(value) => formatDate(value)}
        />
        <Line
          type="monotone"
          dataKey="gdd"
          stroke={CHART_COLORS.primary}
          strokeWidth={2}
          dot={{ fill: CHART_COLORS.primary }}
          name="GDD التراكمي"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
