'use client';

/**
 * FarmMonitorTab — مراقبة المزارع
 *
 * Select a farm → ALL its fields appear on the full-width satellite map
 * immediately, each with its own Sentinel-2 imagery, no side panel.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Building2 } from 'lucide-react';
import dynamic from 'next/dynamic';
import { useFarms } from '@/features/farms/hooks/useFarms';
import { useFieldsList } from '@/features/fields/hooks/useFieldsList';
import { SatelliteLayerSwitcher } from './SatelliteLayerSwitcher';
import { SatelliteTimeline } from './SatelliteTimeline';
import { useTimeseriesLayers } from '../hooks/useTimeseriesLayers';
import { SATELLITE_LAYERS } from '../types';
import type { Farm } from '@/features/farms/types';

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
      <div className="relative min-w-[220px]">
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
        <svg className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

interface Props {
  activeLayerId: string;
  setActiveLayerId: (id: string) => void;
}

export function FarmMonitorTab({ activeLayerId, setActiveLayerId }: Props) {
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);
  const [activeDate, setActiveDate] = useState<string | null>(null);

  const { data: farms = [], isLoading: farmsLoading } = useFarms();
  const { data: farmFields = [], isLoading: fieldsLoading } = useFieldsList(
    selectedFarmId ? { farmId: selectedFarmId } : undefined
  );

  const handleFarmSelect = useCallback((farmId: string | null) => {
    setSelectedFarmId(farmId);
    setActiveDate(null);
  }, []);

  const selectedFarm = farms.find((f) => f.id === selectedFarmId);

  // farmCenter: fit all field polygons or fall back to stored center+zoom
  const farmCenter = useMemo(() => {
    if (!selectedFarm) return null;
    const lat = selectedFarm.centerLat ?? selectedFarm.coordinates?.lat;
    const lng = selectedFarm.centerLng ?? selectedFarm.coordinates?.lng;
    if (lat == null || lng == null) return null;
    return { lat, lng, zoom: selectedFarm.zoom ?? 14 };
  }, [selectedFarm]);

  // Timeline: use union bbox of all farm fields
  const farmBbox = useMemo(() => {
    if (!farmFields.length) return undefined;
    let n = -Infinity, s = Infinity, e = -Infinity, w = Infinity;
    let found = false;
    farmFields.forEach((f) => {
      const ring = f.polygon?.coordinates?.[0];
      if (ring?.length) {
        ring.forEach((coord) => {
          const lng = coord[0] as number, lat = coord[1] as number;
          if (lat > n) n = lat; if (lat < s) s = lat;
          if (lng > e) e = lng; if (lng < w) w = lng;
        });
        found = true;
      } else if (f.centroid) {
        const lng = f.centroid.coordinates[0] as number;
        const lat = f.centroid.coordinates[1] as number;
        const d = 0.008;
        if (lat + d > n) n = lat + d; if (lat - d < s) s = lat - d;
        if (lng + d > e) e = lng + d; if (lng - d < w) w = lng - d;
        found = true;
      }
    });
    return found ? { west: w, south: s, east: e, north: n } : undefined;
  }, [farmFields]);

  const { data: timeseriesDates = [], isLoading: timeseriesLoading } = useTimeseriesLayers(
    activeLayerId, 365, farmBbox
  );

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Top bar — farm selector only */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-400">
            {selectedFarm
              ? `${selectedFarm.nameAr || selectedFarm.name} · ${farmFields.length} حقل`
              : `${farms.length} مزرعة متاحة`}
          </p>
        </div>
        <FarmSelectorDropdown
          farms={farms}
          selectedFarmId={selectedFarmId}
          onSelect={handleFarmSelect}
          loading={farmsLoading}
        />
      </div>

      {/* Full-width map */}
      <div className="flex-1 min-h-0 relative">
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
          <div className="relative w-full h-full">
            <GoogleSatelliteMap
              fields={farmFields}
              selectedField={null}
              selectedFieldId={null}
              flyToTarget={null}
              farmCenter={farmCenter}
              activeLayerId={activeLayerId}
              kpiMap={{}}
              onFieldClick={undefined}
              activeDate={activeDate}
              layerOpacity={0.85}
              showAllFieldsImagery={true}
            />

            {/* Timeline slider */}
            <SatelliteTimeline
              dates={timeseriesDates}
              activeDate={activeDate}
              onDateChange={setActiveDate}
              loading={timeseriesLoading}
              hidden={!farmFields.length}
            />

            {/* Layer switcher — same position as field-monitor tab */}
            <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1001] bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg px-4 py-3 max-w-[95%]">
              <SatelliteLayerSwitcher
                activeLayerId={activeLayerId}
                onLayerChange={setActiveLayerId}
              />
              <p className="text-center text-xs text-gray-400 mt-2">
                {selectedFarm
                  ? `طبقة ${SATELLITE_LAYERS.find(l => l.id === activeLayerId)?.labelAr ?? activeLayerId} — جميع حقول ${selectedFarm.nameAr || selectedFarm.name}`
                  : 'اختر مزرعة لعرض صور الأقمار الاصطناعية'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
