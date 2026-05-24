'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { MapPin } from 'lucide-react';
import { useFarms } from '@/features/farms';
import { YEMEN_GOVERNORATES } from '@/data/yemen-locations';
import type { WizardData } from '../useWizardState';
import type { GeoPolygon } from '../../../types';

// Dynamic import — no SSR for Leaflet
const LeafletFieldDrawer = dynamic(
  () => import('@/components/maps/LeafletFieldDrawer'),
  {
    ssr: false,
    loading: () => (
      <div className="flex-1 bg-gray-100 animate-pulse flex items-center justify-center text-gray-400">
        <MapPin className="w-8 h-8 animate-bounce" />
      </div>
    ),
  }
);

interface Step1Props {
  data: WizardData;
  update: <K extends keyof WizardData>(key: K, value: WizardData[K]) => void;
  error?: string | null;
}

export function Step1Location({ data, update, error }: Step1Props) {
  const { data: farms = [] } = useFarms();
  const [mapFlyTo, setMapFlyTo] = useState<[number, number] | null>(null);
  const [mapFlyZoom, setMapFlyZoom] = useState(11);

  const handleFarmChange = (farmId: string) => {
    update('farmId', farmId);
    if (!farmId) { setMapFlyTo(null); return; }

    const farm = farms.find((f) => f.id === farmId);
    if (!farm) { setMapFlyTo(null); return; }

    if (farm.centerLat != null && farm.centerLng != null) {
      setMapFlyTo([farm.centerLat, farm.centerLng]);
      setMapFlyZoom(farm.zoom ?? 12);
      return;
    }
    if (farm.bbox) {
      const [minLng, minLat, maxLng, maxLat] = farm.bbox;
      setMapFlyTo([(minLat + maxLat) / 2, (minLng + maxLng) / 2]);
      setMapFlyZoom(farm.zoom ?? 12);
      return;
    }
    if (farm.coordinates) {
      setMapFlyTo([farm.coordinates.lat, farm.coordinates.lng]);
      setMapFlyZoom(12);
      return;
    }
    const locationAr = farm.locationAr ?? '';
    if (locationAr) {
      for (const gov of YEMEN_GOVERNORATES) {
        const dist = gov.districts.find((d) => locationAr.includes(d.nameAr));
        if (dist) { setMapFlyTo(dist.center); setMapFlyZoom(11); return; }
        if (locationAr.includes(gov.nameAr)) { setMapFlyTo(gov.center); setMapFlyZoom(9); return; }
      }
    }
    setMapFlyTo(null);
  };

  const handleBoundaryChange = (geojson: GeoPolygon | null) => {
    if (geojson) {
      const coords = geojson.coordinates[0] ?? [];
      const area = computeAreaHectares(coords);
      update('polygon', geojson);
      update('area', area);
    } else {
      update('polygon', null);
      update('area', 0);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Farm selector — compact bar at top */}
      <div className="px-4 py-3 bg-white border-b border-gray-200 flex items-center gap-3">
        <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
          المزرعة:
        </label>
        <select
          value={data.farmId}
          onChange={(e) => handleFarmChange(e.target.value)}
          className="flex-1 max-w-xs px-3 py-1.5 border-2 border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500 bg-white"
          dir="rtl"
        >
          <option value="">— اختر المزرعة —</option>
          {farms.map((farm) => (
            <option key={farm.id} value={farm.id}>
              {farm.nameAr || farm.name}
            </option>
          ))}
        </select>

        {data.area > 0 && (
          <span className="text-sm font-medium text-green-600 bg-green-50 border border-green-200 px-3 py-1 rounded-full whitespace-nowrap">
            {data.area.toFixed(2)} هكتار
          </span>
        )}

        {error && (
          <span className="text-sm text-red-600 flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
            {error}
          </span>
        )}
      </div>

      {/* Full-height map */}
      <div className="flex-1 min-h-0">
        <LeafletFieldDrawer
          onBoundaryChange={handleBoundaryChange}
          initialCenter={[15.5527, 48.5164]}
          initialZoom={7}
          height="100%"
          externalFlyTo={mapFlyTo}
          externalFlyZoom={mapFlyZoom}
          initialPolygon={data.polygon}
        />
      </div>
    </div>
  );
}

/** Haversine-based area calculation in hectares (same formula as FieldForm) */
function computeAreaHectares(coords: number[][]): number {
  if (coords.length < 3) return 0;
  const R = 6371000; // metres
  let area = 0;
  const n = coords.length;
  for (let i = 0; i < n; i++) {
    const c1 = coords[i] as number[];
    const c2 = coords[(i + 1) % n] as number[];
    const lng1 = c1[0] as number;
    const lat1 = c1[1] as number;
    const lng2 = c2[0] as number;
    const lat2 = c2[1] as number;
    const phi1 = (lat1 * Math.PI) / 180;
    const phi2 = (lat2 * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    area += (dLng * (2 + Math.sin(phi1) + Math.sin(phi2)));
  }
  area = Math.abs((area * R * R) / 2);
  return area / 10000; // m² → ha
}
