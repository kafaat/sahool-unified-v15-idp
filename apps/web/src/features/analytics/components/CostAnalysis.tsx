/**
 * Cost Analysis Component
 * مكون تحليل التكاليف
 */

'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import {
  DynamicPieChart as PieChart,
  DynamicPie as Pie,
  DynamicCell as Cell,
  DynamicResponsiveContainer as ResponsiveContainer,
  DynamicLegend as Legend,
  DynamicTooltip as Tooltip,
} from '@/components/charts/LazyRecharts.dynamic';
import { useCostAnalysis } from '../hooks/useAnalytics';
import type { AnalyticsFilters } from '../types';

interface CostAnalysisProps {
  filters?: AnalyticsFilters;
}

const COLORS = {
  seeds: '#10b981',
  fertilizers: '#3b82f6',
  pesticides: '#f59e0b',
  irrigation: '#06b6d4',
  labor: '#8b5cf6',
  equipment: '#ec4899',
  other: '#6b7280',
};

export const CostAnalysis: React.FC<CostAnalysisProps> = ({ filters }) => {
  const t = useTranslations('analytics');
  const tCost = useTranslations('costCategories');
  const { data: costData, isLoading } = useCostAnalysis(filters);

  const categoryLabels = {
    seeds: tCost('seeds'),
    fertilizers: tCost('fertilizers'),
    pesticides: tCost('pesticides'),
    irrigation: tCost('irrigation'),
    labor: tCost('labor'),
    equipment: tCost('equipment'),
    other: tCost('other'),
  };

  if (isLoading) {
    return (
      <div
        className="flex items-center justify-center h-64"
        role="status"
        aria-label="جاري التحميل | Loading"
      >
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!costData || costData.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
        <p className="text-gray-600">{t('noCostData')}</p>
      </div>
    );
  }

  // Calculate total breakdown across all fields (null-safe)
  const totalBreakdown = costData.reduce(
    (acc, field) => {
      if (!field.breakdown) return acc;
      Object.keys(field.breakdown).forEach((key) => {
        const category = key as keyof typeof field.breakdown;
        const value = Number(field.breakdown[category]) || 0;
        acc[category] = (acc[category] || 0) + value;
      });
      return acc;
    },
    {} as Record<string, number>
  );

  const pieData = Object.entries(totalBreakdown).map(([category, value]) => ({
    name: categoryLabels[category as keyof typeof categoryLabels] || category,
    value,
    color: COLORS[category as keyof typeof COLORS] || '#6b7280',
  }));

  const totalCost = costData.reduce((sum, field) => sum + (Number(field.totalCost) || 0), 0);
  const safeFieldCount = costData.length || 1;
  const averageCostPerField = totalCost / safeFieldCount;

  return (
    <div className="space-y-6">
      {/* Overview */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('costSummary')}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-600">{t('totalCosts')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {totalCost.toLocaleString('ar-SA')} {t('sar')}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">{t('fieldsCount')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{costData.length}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">{t('averageCostPerField')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {averageCostPerField.toLocaleString('ar-SA', {
                maximumFractionDigits: 0,
              })}{' '}
              {t('sar')}
            </p>
          </div>
        </div>
      </div>

      {/* Pie Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('costDistribution')}</h3>
        <div style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry: { name: string; value: number }) =>
                  totalCost > 0
                    ? `${entry.name}: ${((entry.value / totalCost) * 100).toFixed(1)}%`
                    : entry.name
                }
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry) => (
                  <Cell key={`cell-${entry.name}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {costData.map((field) => (
          <div
            key={field.fieldId}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
          >
            <h4 className="font-semibold text-gray-900 mb-1">{field.fieldNameAr}</h4>
            <p className="text-sm text-gray-600 mb-4">
              {(Number(field.costPerHectare) || 0).toLocaleString('ar-SA')} {t('sar')}/{t('hectare')}
            </p>

            <div className="space-y-2">
              {Object.entries(field.breakdown || {}).map(([category, value]) => {
                const numValue = Number(value) || 0;
                const fieldTotal = Number(field.totalCost) || 0;
                const percentage = fieldTotal > 0 ? (numValue / fieldTotal) * 100 : 0;
                const label = categoryLabels[category as keyof typeof categoryLabels] || category;
                const color = COLORS[category as keyof typeof COLORS] || '#6b7280';

                return (
                  <div key={category} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-700">{label}</span>
                      <span className="font-medium text-gray-900">
                        {numValue.toLocaleString('ar-SA')} {t('sar')}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all"
                        style={{
                          width: `${percentage}%`,
                          backgroundColor: color,
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">{t('total')}</span>
                <span className="text-lg font-bold text-gray-900">
                  {(Number(field.totalCost) || 0).toLocaleString('ar-SA')} {t('sar')}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CostAnalysis;
