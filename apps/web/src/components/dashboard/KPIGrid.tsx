/**
 * SAHOOL KPI Grid Component
 * شبكة مؤشرات الأداء الرئيسية
 */

import React from "react";
import { KPI } from "../../types";
import { KPICard } from "./KPICard";

interface KPIGridProps {
  kpis: KPI[];
  onKPIClick?: (kpi: KPI) => void;
  isLoading?: boolean;
}

export const KPIGrid = React.memo<KPIGridProps>(function KPIGrid({
  kpis,
  onKPIClick,
  isLoading,
}) {
  if (isLoading) {
    return (
      <div
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
        aria-busy="true"
        aria-label="جاري تحميل المؤشرات"
      >
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-32 bg-gray-100 rounded-xl animate-pulse"
            aria-label="جاري التحميل"
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      role="region"
      aria-label="شبكة مؤشرات الأداء"
    >
      {kpis.map((kpi) => (
        <KPICard key={kpi.id} kpi={kpi} onClick={() => onKPIClick?.(kpi)} />
      ))}
    </div>
  );
});

export default KPIGrid;
