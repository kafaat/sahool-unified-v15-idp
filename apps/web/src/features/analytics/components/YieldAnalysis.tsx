/**
 * Yield Analysis Component
 * مكون تحليل المحصول
 */

'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertTriangle } from 'lucide-react';
import { useYieldAnalysis } from '../hooks/useAnalytics';
import type { AnalyticsFilters } from '../types';

interface YieldAnalysisProps {
  filters?: AnalyticsFilters;
}

export const YieldAnalysis: React.FC<YieldAnalysisProps> = ({ filters }) => {
  const t = useTranslations('analytics');
  const [chartType, setChartType] = useState<'line' | 'bar'>('bar');
  const { data: yieldData, isLoading } = useYieldAnalysis(filters);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!yieldData || yieldData.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
        <p className="text-gray-600">{t('noYieldData')}</p>
      </div>
    );
  }

  // Prepare chart data
  const chartData = yieldData.map((field) => ({
    name: field.fieldNameAr,
    actual: field.totalYield,
    expected: field.expectedYield,
    yieldPerHectare: field.yieldPerHectare,
  }));

  return (
    <div className="space-y-6">
      {/* Chart Type Toggle */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {t('yieldAnalysis')}
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setChartType('bar')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                chartType === 'bar'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('bars')}
            </button>
            <button
              onClick={() => setChartType('line')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                chartType === 'line'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('lines')}
            </button>
          </div>
        </div>

        <div className="mt-6" style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'bar' ? (
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="actual" fill="#10b981" name={t('actualYield')} />
                <Bar dataKey="expected" fill="#94a3b8" name={t('expectedYield')} />
              </BarChart>
            ) : (
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke="#10b981"
                  strokeWidth={2}
                  name={t('actualYield')}
                />
                <Line
                  type="monotone"
                  dataKey="expected"
                  stroke="#94a3b8"
                  strokeWidth={2}
                  name={t('expectedYield')}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {yieldData.map((field) => {
          const variance = field.variance;
          const isUnderperforming = variance < -10;
          const isOverperforming = variance > 10;

          return (
            <div
              key={field.fieldId}
              className={`p-6 rounded-xl shadow-sm border-2 ${
                isUnderperforming
                  ? 'bg-red-50 border-red-200'
                  : isOverperforming
                  ? 'bg-green-50 border-green-200'
                  : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold text-gray-900">{field.fieldNameAr}</h4>
                  <p className="text-sm text-gray-600 mt-1">{field.cropTypeAr}</p>
                </div>
                {isUnderperforming && (
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                )}
                {isOverperforming && (
                  <TrendingUp className="w-5 h-5 text-green-500" />
                )}
              </div>

              <div className="mt-4 space-y-3">
                <div>
                  <p className="text-sm text-gray-600">{t('actualYield')}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {field.totalYield.toLocaleString('ar-SA')} {t('kg')}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">{t('productivity')} ({t('kgPerHectare')})</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {field.yieldPerHectare.toLocaleString('ar-SA')}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">{t('varianceFromExpected')}</p>
                  <p
                    className={`text-lg font-semibold ${
                      variance > 0 ? 'text-green-600' : variance < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}
                  >
                    {variance > 0 ? '+' : ''}
                    {variance.toFixed(1)}%
                  </p>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    {t('totalArea')}: {field.area.toLocaleString('ar-SA')} {t('hectare')}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {t('season')}: {field.season}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default YieldAnalysis;
