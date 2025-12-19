/**
 * SAHOOL KPI Card Component
 * بطاقة مؤشر الأداء الرئيسي
 */

import React from 'react';
import { KPI } from '../../types';

interface KPICardProps {
  kpi: KPI;
  onClick?: () => void;
}

const statusColors: Record<string, string> = {
  good: 'bg-green-50 border-green-200 text-green-700',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  critical: 'bg-red-50 border-red-200 text-red-700',
};

const trendIcons: Record<string, string> = {
  up: '↗',
  down: '↘',
  stable: '→',
};

const trendColors: Record<string, string> = {
  up: 'text-green-500',
  down: 'text-red-500',
  stable: 'text-gray-500',
};

const iconMap: Record<string, string> = {
  leaf: '🌿',
  water: '💧',
  sun: '☀️',
  alert: '⚠️',
};

export const KPICard: React.FC<KPICardProps> = ({ kpi, onClick }) => {
  return (
    <div
      className={`
        p-4 rounded-xl border-2 cursor-pointer
        transition-all duration-200 hover:shadow-lg hover:scale-[1.02]
        ${statusColors[kpi.status]}
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
    >
      <div className="flex items-start justify-between">
        <div className="p-2 rounded-lg bg-white/50 text-2xl">
          {iconMap[kpi.icon] || '📊'}
        </div>
        <div className={`flex items-center gap-1 ${trendColors[kpi.trend]}`}>
          <span>{trendIcons[kpi.trend]}</span>
          <span className="text-sm font-medium">
            {kpi.trendValue > 0 ? '+' : ''}{kpi.trendValue}%
          </span>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm text-gray-600">{kpi.labelAr}</p>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-3xl font-bold">{kpi.value}</span>
          <span className="text-sm text-gray-500">{kpi.unit}</span>
        </div>
      </div>
    </div>
  );
};

export default KPICard;
