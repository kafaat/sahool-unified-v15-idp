'use client';

/**
 * SatelliteClient — صور الأقمار الاصطناعية
 *
 * Two main tabs:
 *   • مراقبة الحقول  — original per-field satellite view
 *   • مراقبة المزارع — select a farm → show ALL its fields on the map
 */

import React, { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { useSatellitePage } from './hooks/useSatellitePage';
import { FieldSelectorDropdown } from './components/FieldSelectorDropdown';
import { SatelliteMapPanel } from './components/SatelliteMapPanel';
import { SatelliteKpiPanel } from './components/SatelliteKpiPanel';
import { FarmMonitorTab } from './components/FarmMonitorTab';

type MainTab = 'fields' | 'farms';

export default function SatelliteClient() {
  const [mainTab, setMainTab] = useState<MainTab>('fields');

  // Shared layer state — persists when switching tabs
  const [sharedLayerId, setSharedLayerId] = useState<string>('NDVI');

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

  // Keep the field-tab layer in sync with the shared layer
  const handleFieldLayerChange = (id: string) => {
    setActiveLayerId(id);
    setSharedLayerId(id);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] min-h-0 overflow-hidden">

      {/* ── Page header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-gray-900 leading-tight">صور الأقمار الاصطناعية</h1>
          <p className="text-xs text-gray-400">Satellite Analysis | SAHOOL</p>
        </div>

        {/* Main tab switcher */}
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1 flex-shrink-0">
          <button
            onClick={() => setMainTab('fields')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              mainTab === 'fields'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            مراقبة الحقول
          </button>
          <button
            onClick={() => setMainTab('farms')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              mainTab === 'farms'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            مراقبة المزارع
          </button>
        </div>

        {/* Field selector — only shown in field-monitor tab */}
        {mainTab === 'fields' && (
          <FieldSelectorDropdown
            fields={fields}
            selectedFieldId={selectedFieldId}
            onSelect={handleSelectField}
            loading={fieldsLoading}
          />
        )}
      </div>

      {/* ── Tab content ── */}
      {mainTab === 'fields' ? (
        <>
          {kpiError && (
            <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 border-b border-orange-100 text-sm text-orange-700 flex-shrink-0">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              فشل تحميل بيانات KPI — تأكد من أن الخدمة تعمل
            </div>
          )}

          {/* Split-screen: 70% map | 30% KPI */}
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
                onLayerChange={handleFieldLayerChange}
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
                onLayerChange={handleFieldLayerChange}
              />
            </div>
          </div>
        </>
      ) : (
        <FarmMonitorTab
          activeLayerId={sharedLayerId}
          setActiveLayerId={setSharedLayerId}
        />
      )}
    </div>
  );
}
