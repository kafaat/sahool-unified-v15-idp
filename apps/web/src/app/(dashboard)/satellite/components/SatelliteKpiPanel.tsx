'use client';

/**
 * SatelliteKpiPanel — right 40% tabbed KPI panel
 * لوحة KPI — الجزء الأيمن بنظام التبويب (10 أقسام)
 */

import React, { useState } from 'react';
import { RefreshCw, Clock, Satellite } from 'lucide-react';
import type { FieldKpiSnapshot } from '@/features/fields/api';
import type { Field } from '@/features/fields/types';
import {
  VegetationSection,
  WaterSection,
  SoilSection,
  FireSection,
  UrbanSection,
  SnowSection,
  AtmosphereSection,
  WeatherSection,
  AirQualitySection,
  SolarSection,
} from '@/features/fields/components/FieldKPITiles';

type TabId =
  | 'vegetation' | 'water' | 'soil' | 'fire'
  | 'urban' | 'snow' | 'atmosphere'
  | 'weather' | 'airquality' | 'solar';

/** Maps KPI panel tab → default map layer to activate */
const TAB_TO_LAYER: Partial<Record<TabId, string>> = {
  vegetation: 'NDVI',
  water:      'NDWI',
  soil:       'BSI',
  fire:       'NBR',
  urban:      'NDBI',
  snow:       'NDSI',
  atmosphere: 'LST',
};

interface Tab {
  id: TabId;
  icon: string;
  labelAr: string;
  labelEn: string;
}

const TABS: Tab[] = [
  { id: 'vegetation', icon: '🌿', labelAr: 'النباتات',    labelEn: 'Vegetation' },
  { id: 'water',      icon: '💧', labelAr: 'المياه',      labelEn: 'Water' },
  { id: 'soil',       icon: '🪨', labelAr: 'التربة',      labelEn: 'Soil' },
  { id: 'fire',       icon: '🔥', labelAr: 'الحرائق',     labelEn: 'Fire' },
  { id: 'urban',      icon: '🏗️', labelAr: 'العمران',     labelEn: 'Urban' },
  { id: 'snow',       icon: '❄️', labelAr: 'الثلوج',      labelEn: 'Snow' },
  { id: 'atmosphere', icon: '🌡️', labelAr: 'الغلاف الجوي', labelEn: 'Atmosphere' },
  { id: 'weather',    icon: '⛅', labelAr: 'الطقس',       labelEn: 'Weather' },
  { id: 'airquality', icon: '💨', labelAr: 'جودة الهواء', labelEn: 'Air Quality' },
  { id: 'solar',      icon: '☀️', labelAr: 'الإشعاع الشمسي', labelEn: 'Solar' },
];

interface Props {
  field: Field | null | undefined;
  kpi: FieldKpiSnapshot | null | undefined;
  loading: boolean;
  onRefresh: () => void;
  isRefreshing: boolean;
  /** Kept in sync with the map's active layer so the panel reflects what's shown */
  activeLayerId?: string;
  /** Called when a tab is clicked so the map overlay switches to the matching layer */
  onLayerChange?: (layerId: string) => void;
}

export function SatelliteKpiPanel({ field, kpi, loading, onRefresh, isRefreshing, activeLayerId, onLayerChange }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('vegetation');

  /** Switch tab AND sync the map layer */
  const handleTabChange = (tabId: TabId) => {
    setActiveTab(tabId);
    const layerId = TAB_TO_LAYER[tabId];
    if (layerId) onLayerChange?.(layerId);
  };

  const working = loading || isRefreshing;

  if (!field) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-center p-8">
        <Satellite className="w-16 h-16 text-gray-200" />
        <div>
          <p className="font-semibold text-gray-700">اختر حقلاً من القائمة</p>
          <p className="text-xs text-gray-400 mt-1">Select a field to view satellite KPIs</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-gray-100 flex-shrink-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h2 className="font-bold text-gray-900 truncate">{field.nameAr || field.name}</h2>
            <p className="text-xs text-gray-400 truncate">
              {field.cropAr || field.crop || 'لا يوجد محصول'}
              {field.area ? ` · ${field.area} هـ` : ''}
            </p>
          </div>
          <button
            onClick={onRefresh}
            disabled={working}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 disabled:opacity-40 flex-shrink-0 font-medium"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${working ? 'animate-spin' : ''}`} />
            {working ? 'جاري...' : 'تحديث'}
          </button>
        </div>

        {kpi?.fetchedAt && (
          <div className="flex items-center gap-1 mt-1.5 text-xs text-gray-400">
            <Clock className="w-3 h-3" />
            {new Date(kpi.fetchedAt).toLocaleString('ar-SA')}
            {kpi.satelliteSource && <span className="mr-1">· {kpi.satelliteSource}</span>}
          </div>
        )}
      </div>

      {/* Tab bar */}
      <div className="flex gap-0.5 px-2 pt-2 overflow-x-auto flex-shrink-0 scrollbar-none">
        {TABS.map((tab) => {
          const mappedLayer = TAB_TO_LAYER[tab.id];
          const layerIsActive = !!mappedLayer && mappedLayer === activeLayerId;
          return (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              title={`${tab.labelAr} · ${tab.labelEn}${mappedLayer ? ` · ${mappedLayer}` : ''}`}
              className={`relative flex flex-col items-center px-2 py-1.5 rounded-lg text-xs whitespace-nowrap transition-colors flex-shrink-0 ${
                activeTab === tab.id
                  ? 'bg-green-50 text-green-700 font-semibold'
                  : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              <span className="text-base leading-none">{tab.icon}</span>
              <span className="mt-0.5 hidden lg:block">{tab.labelAr}</span>
              {/* dot indicator: this tab's layer is active on the map */}
              {layerIsActive && (
                <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-green-500" />
              )}
            </button>
          );
        })}
      </div>

      {/* Section content */}
      <div className="flex-1 overflow-y-auto p-4 min-h-0">
        {activeTab === 'vegetation' && (
          <VegetationSection kpi={kpi} loading={working} onRefresh={onRefresh} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />
        )}
        {activeTab === 'water'      && <WaterSection      kpi={kpi} loading={working} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />}
        {activeTab === 'soil'       && <SoilSection       kpi={kpi} loading={working} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />}
        {activeTab === 'fire'       && <FireSection       kpi={kpi} loading={working} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />}
        {activeTab === 'urban'      && <UrbanSection      kpi={kpi} loading={working} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />}
        {activeTab === 'snow'       && <SnowSection       kpi={kpi} loading={working} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />}
        {activeTab === 'atmosphere' && <AtmosphereSection kpi={kpi} loading={working} activeLayerId={activeLayerId} onLayerChange={onLayerChange} />}
        {activeTab === 'weather'    && <WeatherSection    kpi={kpi} loading={working} />}
        {activeTab === 'airquality' && <AirQualitySection kpi={kpi} loading={working} />}
        {activeTab === 'solar'      && <SolarSection      kpi={kpi} loading={working} />}
      </div>
    </div>
  );
}
