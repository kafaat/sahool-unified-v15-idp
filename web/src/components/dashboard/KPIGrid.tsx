/**
 * SAHOOL KPI Grid Component
 * شبكة مؤشرات الأداء الرئيسية
 */

import React from 'react';
import { KPI } from '../../types';
import { KPICard } from './KPICard';

interface KPIGridProps {
  kpis: KPI[];
  onKPIClick?: (kpi: KPI) => void;
  isLoading?: boolean;
}

export const KPIGrid: React.FC<KPIGridProps> = ({
  kpis,
  onKPIClick,
  isLoading
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-32 bg-gray-100 rounded-xl animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi) => (
        <KPICard
          key={kpi.id}
          kpi={kpi}
          onClick={() => onKPIClick?.(kpi)}
        />
      ))}
    </div>
  );
};

export default KPIGrid;
