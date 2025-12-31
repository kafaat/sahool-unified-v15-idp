/**
 * KPI Cards Component
 * بطاقات مؤشرات الأداء الرئيسية
 */

'use client';

import React from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Droplet,
  Sprout,
  DollarSign,
  BarChart,
} from 'lucide-react';
import type { KPIMetric } from '../types';

interface KPICardsProps {
  kpis: KPIMetric[];
}

const iconMap: Record<string, React.ElementType> = {
  water: Droplet,
  crop: Sprout,
  money: DollarSign,
  chart: BarChart,
  trending_up: TrendingUp,
};

const statusColors = {
  good: 'bg-green-50 border-green-200',
  warning: 'bg-yellow-50 border-yellow-200',
  critical: 'bg-red-50 border-red-200',
};

const trendColors = {
  up: 'text-green-600',
  down: 'text-red-600',
  stable: 'text-gray-600',
};

export const KPICards: React.FC<KPICardsProps> = ({ kpis }) => {
  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return TrendingUp;
      case 'down':
        return TrendingDown;
      default:
        return Minus;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {kpis.map((kpi) => {
        const Icon = iconMap[kpi.icon] || BarChart;
        const TrendIcon = getTrendIcon(kpi.trend);
        const statusColor = statusColors[kpi.status];
        const trendColor = trendColors[kpi.trend];

        return (
          <div
            key={kpi.id}
            className={`p-6 rounded-xl border-2 shadow-sm transition-all hover:shadow-md ${statusColor}`}
          >
            <div className="flex items-start justify-between">
              <div className="p-3 bg-white rounded-lg">
                <Icon className="w-6 h-6 text-gray-700" />
              </div>
              <div className={`flex items-center gap-1 ${trendColor}`}>
                <TrendIcon className="w-5 h-5" />
                <span className="text-sm font-medium">
                  {kpi.change > 0 ? '+' : ''}
                  {kpi.change.toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-sm text-gray-600">{kpi.nameAr}</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-bold text-gray-900">
                  {kpi.value.toLocaleString('ar-SA')}
                </span>
                <span className="text-sm text-gray-500">{kpi.unitAr}</span>
              </div>
            </div>

            {kpi.descriptionAr && (
              <p className="mt-3 text-xs text-gray-600 border-t border-gray-200 pt-3">
                {kpi.descriptionAr}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default KPICards;
