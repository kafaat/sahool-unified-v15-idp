'use client';

/**
 * SatelliteClient — صور الأقمار الاصطناعية
 * Split-screen: 60% interactive map | 40% KPI panel (10 tabbed sections)
 *
 * Layout:
 *   Desktop: flex-row  (map left 60%, KPI panel right 40%)
 *   Mobile:  flex-col  (map full-width 300px, KPI panel scrollable)
 */

import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { useSatellitePage } from './hooks/useSatellitePage';
import { FieldSelectorDropdown } from './components/FieldSelectorDropdown';
import { SatelliteMapPanel } from './components/SatelliteMapPanel';
import { SatelliteKpiPanel } from './components/SatelliteKpiPanel';

export default function SatelliteClient() {
  const {
    fields,
    fieldsLoading,
    selectedFieldId,
    selectedField,
    handleSelectField,
    flyToTarget,
    activeLayerId,
    setActiveLayerId,
    activeDate,
    setActiveDate,
    layerOpacity,
    kpi,
    kpiLoading,
    kpiError,
    handleRefresh,
    isRefreshing,
  } = useSatellitePage();

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] min-h-0 overflow-hidden">

      {/* ── Top bar ── */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-gray-900 leading-tight">صور الأقمار الاصطناعية</h1>
          <p className="text-xs text-gray-400">Satellite Imagery · KPI Intelligence · {fields.length} حقل</p>
        </div>
        <FieldSelectorDropdown
          fields={fields}
          selectedFieldId={selectedFieldId}
          onSelect={handleSelectField}
          loading={fieldsLoading}
        />
      </div>

      {/* ── KPI fetch error notice ── */}
      {kpiError && (
        <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 border-b border-orange-100 text-sm text-orange-700 flex-shrink-0">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          فشل تحميل بيانات KPI — تأكد من أن الخدمة تعمل
        </div>
      )}

      {/* ── Split-screen body ── */}
      <div className="flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">

        {/* Map panel — 60% on desktop, fixed height on mobile */}
        <div className="
          md:w-[60%] flex-shrink-0
          h-[300px] md:h-auto
          border-b md:border-b-0 md:border-r border-gray-100
          relative
        ">
          <SatelliteMapPanel
            fields={fields}
            selectedField={selectedField}
            selectedFieldId={selectedFieldId}
            flyToTarget={flyToTarget}
            activeLayerId={activeLayerId}
            onLayerChange={setActiveLayerId}
            kpi={kpi}
            onFieldClick={(f) => handleSelectField(f.id)}
            activeDate={activeDate}
            onDateChange={setActiveDate}
            layerOpacity={layerOpacity}
          />
        </div>

        {/* KPI panel — 40% on desktop, full width below map on mobile */}
        <div className="flex-1 md:w-[40%] overflow-hidden bg-white">
          <SatelliteKpiPanel
            field={selectedField}
            kpi={kpi}
            loading={kpiLoading}
            onRefresh={handleRefresh}
            isRefreshing={isRefreshing}
            activeLayerId={activeLayerId}
            onLayerChange={setActiveLayerId}
          />
        </div>
      </div>
    </div>
  );
}
