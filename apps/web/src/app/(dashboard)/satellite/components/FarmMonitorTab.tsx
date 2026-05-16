'use client';

/**
 * FarmMonitorTab — مراقبة المزارع
 * Selects a farm → shows all its fields on the satellite map.
 * Clicking a field opens its KPI panel (same as the field-monitor tab).
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Building2, AlertTriangle } from 'lucide-react';
import dynamic from 'next/dynamic';
import { useFarms } from '@/features/farms/hooks/useFarms';
import { useFieldsList } from '@/features/fields/hooks/useFieldsList';
import { useFieldKpiSnapshot, useTriggerKpiRefresh } from '@/features/fields/hooks/useFieldKPIs';
import { useField } from '@/features/fields/hooks/useField';
import { SatelliteKpiPanel } from './SatelliteKpiPanel';
import { SatelliteLayerSwitcher } from './SatelliteLayerSwitcher';
import { SatelliteTimeline } from './SatelliteTimeline';
import { useTimeseriesLayers } from '../hooks/useTimeseriesLayers';
import { SATELLITE_LAYERS } from '../types';
import type { Farm } from '@/features/farms/types';
import type { Field } from '@/features/fields/types';
import type { FieldKpiSnapshot } from '@/features/fields/api';

const GoogleSatelliteMap = dynamic(
  () => import('./GoogleSatelliteMap').then((m) => m.GoogleSatelliteMap),
  { ssr: false, loading: () => <MapSkeleton /> }
);

function MapSkeleton() {
  return (
    <div className="w-full h-full bg-gray-900 animate-pulse flex items-center justify-center">
      <div className="text-center text-gray-400">
        <div className="text-4xl mb-2">🛰️</div>
        <p className="text-sm">جاري تحميل صور الأقمار الاصطناعية...</p>
      </div>
    </div>
  );
}

/** Farm selector dropdown */
function FarmSelectorDropdown({
  farms,
  selectedFarmId,
  onSelect,
  loading,
}: {
  farms: Farm[];
  selectedFarmId: string | null;
  onSelect: (id: string | null) => void;
  loading?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      <Building2 className="w-4 h-4 text-gray-400 flex-shrink-0" />
      <div className="relative flex-1 min-w-[220px]">
        <select
          value={selectedFarmId ?? ''}
          onChange={(e) => onSelect(e.target.value || null)}
          disabled={loading}
          className="w-full appearance-none bg-white border border-gray-200 rounded-lg px-3 py-2 pr-8 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:opacity-50 cursor-pointer shadow-sm"
        >
          <option value="">— اختر مزرعة —</option>
          {farms.map((farm) => (
            <option key={farm.id} value={farm.id}>
              {farm.nameAr || farm.name}
              {farm.fieldsCount ? ` · ${farm.fieldsCount} حقل` : ''}
              {farm.totalAreaHa ? ` · ${farm.totalAreaHa.toFixed(1)} هـ` : ''}
            </option>
          ))}
        </select>
        <svg
          className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

/** Sidebar: list of fields for the selected farm */
function FarmFieldsList({
  fields,
  selectedFieldId,
  kpiMap,
  onSelect,
}: {
  fields: Field[];
  selectedFieldId: string | null;
  kpiMap: Record<string, FieldKpiSnapshot>;
  onSelect: (id: string) => void;
}) {
  if (!fields.length) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 gap-3 text-center p-6 text-gray-400">
        <div className="text-4xl">🌾</div>
        <p className="text-sm">لا توجد حقول في هذه المزرعة</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto divide-y divide-gray-50">
      {fields.map((field) => {
        const kpi = kpiMap[field.id];
        const ndvi = kpi?.ndvi ?? field.ndviValue;
        const ndviColor =
          ndvi == null ? 'bg-gray-200'
          : ndvi >= 0.6 ? 'bg-green-500'
          : ndvi >= 0.4 ? 'bg-lime-400'
          : ndvi >= 0.2 ? 'bg-yellow-400'
          : 'bg-red-400';

        return (
          <button
            key={field.id}
            onClick={() => onSelect(field.id)}
            className={`w-full text-right px-4 py-3 hover:bg-gray-50 transition-colors flex items-center gap-3 ${
              selectedFieldId === field.id ? 'bg-green-50 border-r-2 border-green-500' : ''
            }`}
          >
            <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${ndviColor}`} />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">{field.nameAr || field.name}</div>
              <div className="text-xs text-gray-400 truncate">
                {field.cropAr || field.crop || 'لا يوجد محصول'}
                {field.area ? ` · ${field.area} هـ` : ''}
                {ndvi != null ? ` · NDVI: ${ndvi.toFixed(2)}` : ''}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

interface Props {
  activeLayerId: string;
  setActiveLayerId: (id: string) => void;
}

export function FarmMonitorTab({ activeLayerId, setActiveLayerId }: Props) {
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [activeDate, setActiveDate] = useState<string | null>(null);
  const layerOpacity = 0.85;

  // Farms list
  const { data: farms = [], isLoading: farmsLoading } = useFarms();

  // Fields for selected farm
  const { data: farmFields = [], isLoading: fieldsLoading } = useFieldsList(
    selectedFarmId ? { farmId: selectedFarmId } : undefined
  );

  // Selected field detail (for centroid + polygon)
  const { data: selectedField } = useField(selectedFieldId ?? '');

  // KPI for selected field
  const {
    data: kpi,
    isLoading: kpiLoading,
    error: kpiError,
  } = useFieldKpiSnapshot(selectedFieldId ?? '', !!selectedFieldId);

  const refresh = useTriggerKpiRefresh(selectedFieldId ?? '');

  // Reset field selection when farm changes
  const handleFarmSelect = useCallback((farmId: string | null) => {
    setSelectedFarmId(farmId);
    setSelectedFieldId(null);
    setActiveDate(null);
  }, []);

  const handleFieldClick = useCallback((field: Field) => {
    setSelectedFieldId(field.id);
    setActiveDate(null);
  }, []);

  const handleRefresh = useCallback(() => {
    if (!selectedField?.centroid) return;
    const [lng, lat] = selectedField.centroid.coordinates;
    const polygonCoordinates = selectedField.polygon?.coordinates?.[0]?.map(
      ([pLng, pLat]) => [pLng ?? 0, pLat ?? 0] as [number, number]
    );
    refresh.mutate({ lat, lng, polygonCoordinates });
  }, [selectedField, refresh]);

  // flyToTarget: fly to selected field centroid
  const flyToTarget = useMemo((): [number, number] | null => {
    if (!selectedField?.centroid) return null;
    const [lng, lat] = selectedField.centroid.coordinates;
    return [lat, lng];
  }, [selectedField]);

  // Enrich selected field in the list with full geometry
  const enrichedFields = useMemo(() => {
    if (!farmFields.length) return farmFields;
    return farmFields.map((f) => {
      if (f.id !== selectedFieldId) return f;
      return {
        ...f,
        polygon:   selectedField?.polygon  ?? f.polygon,
        centroid:  selectedField?.centroid ?? f.centroid,
        ndviValue: kpi?.ndvi != null ? Number(kpi.ndvi) : f.ndviValue,
      };
    });
  }, [farmFields, selectedFieldId, selectedField, kpi]);

  // Timeseries dates for timeline
  const fieldBbox = useMemo(() => {
    if (!selectedField) return undefined;
    if (selectedField.polygon) {
      const ring = selectedField.polygon.coordinates[0];
      if (ring?.length) {
        let n = -Infinity, s = Infinity, e = -Infinity, w = Infinity;
        ring.forEach((coord) => {
          const lng = coord[0] as number;
          const lat = coord[1] as number;
          if (lat > n) n = lat; if (lat < s) s = lat;
          if (lng > e) e = lng; if (lng < w) w = lng;
        });
        return { west: w, south: s, east: e, north: n };
      }
    }
    if (selectedField.centroid) {
      const [lng, lat] = selectedField.centroid.coordinates;
      const d = 0.008;
      return { west: lng - d, south: lat - d, east: lng + d, north: lat + d };
    }
    return undefined;
  }, [selectedField]);

  const { data: timeseriesDates = [], isLoading: timeseriesLoading } = useTimeseriesLayers(
    activeLayerId, 365, fieldBbox
  );

  const kpiMap = useMemo(() => {
    if (!selectedFieldId || !kpi) return {};
    return { [selectedFieldId]: kpi };
  }, [selectedFieldId, kpi]);

  const selectedFarm = farms.find((f) => f.id === selectedFarmId);
  const isRefreshing = refresh.isPending;

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Top bar */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-400">
            {selectedFarm
              ? `${selectedFarm.nameAr || selectedFarm.name} · ${farmFields.length} حقل`
              : `${farms.length} مزرعة متاحة — اختر مزرعة لعرض حقولها`}
          </p>
        </div>
        <FarmSelectorDropdown
          farms={farms}
          selectedFarmId={selectedFarmId}
          onSelect={handleFarmSelect}
          loading={farmsLoading}
        />
      </div>

      {kpiError && (
        <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 border-b border-orange-100 text-sm text-orange-700 flex-shrink-0">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          فشل تحميل بيانات KPI — تأكد من أن الخدمة تعمل
        </div>
      )}

      {/* Body: map + side panel */}
      <div className="flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">

        {/* Map — 70% */}
        <div className="md:w-[70%] flex-shrink-0 h-[300px] md:h-auto border-b md:border-b-0 md:border-r border-gray-100 relative">
          {!selectedFarmId ? (
            <div className="w-full h-full bg-gray-900 flex items-center justify-center">
              <div className="text-center text-gray-400">
                <div className="text-5xl mb-3">🌾</div>
                <p className="text-sm">اختر مزرعة لعرض حقولها على الخريطة</p>
              </div>
            </div>
          ) : fieldsLoading ? (
            <MapSkeleton />
          ) : (
            <div className="relative flex flex-col h-full min-h-0">
              <div className="flex-1 min-h-0 relative">
                <GoogleSatelliteMap
                  fields={enrichedFields}
                  selectedField={selectedField}
                  selectedFieldId={selectedFieldId}
                  flyToTarget={flyToTarget}
                  activeLayerId={activeLayerId}
                  kpiMap={kpiMap}
                  onFieldClick={handleFieldClick}
                  activeDate={activeDate}
                  layerOpacity={layerOpacity}
                />
              </div>

              <SatelliteTimeline
                dates={timeseriesDates}
                activeDate={activeDate}
                onDateChange={setActiveDate}
                loading={timeseriesLoading}
                hidden={!selectedFieldId}
              />

              <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1001] bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg px-4 py-3 max-w-[95%]">
                <SatelliteLayerSwitcher
                  activeLayerId={activeLayerId}
                  onLayerChange={setActiveLayerId}
                />
                <p className="text-center text-xs text-gray-400 mt-2">
                  {selectedFieldId
                    ? `طبقة ${SATELLITE_LAYERS.find(l => l.id === activeLayerId)?.labelAr ?? activeLayerId}`
                    : 'انقر على حقل لعرض تفاصيله'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right panel — 30% */}
        <div className="flex-1 md:w-[30%] flex flex-col overflow-hidden bg-white">
          {!selectedFarmId ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-4 text-center p-8 text-gray-400">
              <Building2 className="w-16 h-16 text-gray-200" />
              <div>
                <p className="font-semibold text-gray-700">اختر مزرعة من القائمة</p>
                <p className="text-xs text-gray-400 mt-1">Select a farm to view its fields</p>
              </div>
            </div>
          ) : selectedFieldId ? (
            /* KPI panel for selected field */
            <SatelliteKpiPanel
              field={selectedField}
              kpi={kpi}
              loading={kpiLoading || isRefreshing}
              onRefresh={handleRefresh}
              isRefreshing={isRefreshing}
              activeLayerId={activeLayerId}
              onLayerChange={setActiveLayerId}
            />
          ) : (
            /* Fields list */
            <div className="flex flex-col h-full min-h-0">
              <div className="px-4 py-3 border-b border-gray-100 flex-shrink-0">
                <h3 className="font-bold text-gray-900 text-sm">
                  حقول {selectedFarm?.nameAr || selectedFarm?.name}
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  {farmFields.length} حقل · انقر على حقل لعرض KPI الأقمار الاصطناعية
                </p>
              </div>
              <FarmFieldsList
                fields={farmFields}
                selectedFieldId={selectedFieldId}
                kpiMap={kpiMap}
                onSelect={setSelectedFieldId}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
