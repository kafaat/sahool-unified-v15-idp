/**
 * Comparison Chart Component
 * مكون مخطط المقارنة
 */

'use client';

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useComparison } from '../hooks/useAnalytics';
import type { AnalyticsFilters, ComparisonType, MetricType } from '../types';

interface ComparisonChartProps {
  type: ComparisonType;
  metric: MetricType;
  filters?: AnalyticsFilters;
}

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

export const ComparisonChart: React.FC<ComparisonChartProps> = ({ type, metric, filters }) => {
  const [chartType, setChartType] = useState<'line' | 'bar'>('bar');
  const { data: comparison, isLoading } = useComparison(type, metric, filters);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!comparison || comparison.items.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
        <p className="text-gray-600">لا توجد بيانات مقارنة متاحة</p>
        <p className="text-sm text-gray-500 mt-1">No comparison data available</p>
      </div>
    );
  }

  // Prepare chart data - combine all time series
  const allDates = new Set<string>();
  comparison.items.forEach((item) => {
    item.data.forEach((point) => allDates.add(point.date));
  });

  const chartData = Array.from(allDates)
    .sort()
    .map((date) => {
      const dataPoint: Record<string, unknown> = { date };
      comparison.items.forEach((item) => {
        const point = item.data.find((p) => p.date === date);
        dataPoint[item.nameAr] = point?.value || 0;
      });
      return dataPoint;
    });

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            المقارنة
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {type === 'fields' && 'مقارنة بين الحقول'}
            {type === 'seasons' && 'مقارنة بين المواسم'}
            {type === 'crops' && 'مقارنة بين المحاصيل'}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setChartType('bar')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              chartType === 'bar'
                ? 'bg-green-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            أعمدة
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              chartType === 'line'
                ? 'bg-green-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            خطوط
          </button>
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: '400px' }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'bar' ? (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              {comparison.items.map((item, index) => (
                <Bar
                  key={item.id}
                  dataKey={item.nameAr}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </BarChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              {comparison.items.map((item, index) => (
                <Line
                  key={item.id}
                  type="monotone"
                  dataKey={item.nameAr}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-6">
        {comparison.items.map((item, index) => (
          <div
            key={item.id}
            className="p-4 rounded-lg border-2"
            style={{ borderColor: COLORS[index % COLORS.length] }}
          >
            <p className="text-sm text-gray-600">{item.nameAr}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {item.value.toLocaleString('ar-SA')}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComparisonChart;
