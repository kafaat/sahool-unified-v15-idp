'use client';

/**
 * SatelliteClient — صور الأقمار الاصطناعية
 * Two tabs:
 *  • Field Monitoring — per-field satellite view with KPI panel (original)
 *  • Farms Monitoring — select a farm, all fields shown at once on a full-width map
 */

import React, { useState } from 'react';
import { AlertTriangle, Satellite, Building2 } from 'lucide-react';
import { useSatellitePage } from './hooks/useSatellitePage';
import { FieldSelectorDropdown } from './components/FieldSelectorDropdown';
import { SatelliteMapPanel } from './components/SatelliteMapPanel';
import { SatelliteKpiPanel } from './components/SatelliteKpiPanel';
import { FarmMonitorTab } from './components/FarmMonitorTab';

type Tab = 'field' | 'farm';

export default function SatelliteClient() {
  const [activeTab, setActiveTab] = useState<Tab>('field');

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

      {/* ── Page header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-gray-900 leading-tight">صور الأقمار الاصطناعية</h1>
          <p className="text-xs text-gray-400">Satellite Analysis | SAHOOL</p>
        </div>

        {/* ── Tab switcher ── */}
        <div className="flex items-center gap-1 bg-gray-100 rounded-xl p-1 flex-shrink-0">
          <button
            onClick={() => setActiveTab('field')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'field'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Satellite className="w-3.5 h-3.5" />
            Field Monitoring
          </button>
          <button
            onClick={() => setActiveTab('farm')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'farm'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            Farms Monitoring
          </button>
        </div>

        {/* Field selector — field tab only */}
        {activeTab === 'field' && (
          <FieldSelectorDropdown
            fields={fields}
            selectedFieldId={selectedFieldId}
            onSelect={handleSelectField}
            loading={fieldsLoading}
          />
        )}
      </div>

      {/* ── KPI error banner (field tab only) ── */}
      {activeTab === 'field' && kpiError && (
        <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 border-b border-orange-100 text-sm text-orange-700 flex-shrink-0">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          فشل تحميل بيانات KPI — تأكد من أن الخدمة تعمل
        </div>
      )}

      {/* ── Tab content ── */}
      {activeTab === 'field' ? (
        /* ── Split-screen: 70% map | 30% KPI ── */
        <div className="flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">
          <div className="
            md:w-[70%] flex-shrink-0
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

          <div className="flex-1 md:w-[30%] overflow-hidden bg-white">
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
      ) : (
        <FarmMonitorTab
          activeLayerId={activeLayerId}
          setActiveLayerId={setActiveLayerId}
        />
      )}
    </div>
  );
}
