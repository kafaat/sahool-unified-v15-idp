/**
 * Yield Chart Component
 * مكون رسم بياني للمحصول
 */

'use client';

import React from 'react';
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
} from 'recharts';
import type { DataPoint, ChartType } from '../types';

interface YieldChartProps {
  data: DataPoint[];
  chartType?: ChartType;
  title?: string;
  titleAr?: string;
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
}

export const YieldChart: React.FC<YieldChartProps> = ({
  data,
  chartType = 'line',
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
          {chartType === 'line' && (
            <LineChart data={data}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis
                dataKey="label"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '8px 12px',
                }}
              />
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
          )}

          {chartType === 'bar' && (
            <BarChart data={data}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis
                dataKey="label"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '8px 12px',
                }}
              />
              {showLegend && <Legend />}
              <Bar dataKey="value" fill="#10b981" name="الإنتاج" radius={[8, 8, 0, 0]} />
            </BarChart>
          )}

          {chartType === 'area' && (
            <AreaChart data={data}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis
                dataKey="label"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '8px 12px',
                }}
              />
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
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default YieldChart;
