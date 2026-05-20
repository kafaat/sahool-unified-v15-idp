'use client';

/**
 * SatelliteMapPanel — left 60% map with flyTo + KPI badge overlays
 * لوحة خريطة الأقمار الاصطناعية — خريطة Google عالية الدقة مع شارات KPI
 */

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';
import type { Field } from '@/features/fields/types';
import type { FieldKpiSnapshot } from '@/features/fields/api';
import { SatelliteLayerSwitcher } from './SatelliteLayerSwitcher';
import { SatelliteTimeline } from './SatelliteTimeline';
import { useTimeseriesLayers } from '../hooks/useTimeseriesLayers';

// Dynamic import — uses Google Maps API (browser-only)
const GoogleSatelliteMap = dynamic(
  () => import('./GoogleSatelliteMap').then((m) => m.GoogleSatelliteMap),
  { ssr: false, loading: () => <MapSkeleton /> }
);

function MapSkeleton() {
  return (
    <div className="w-full h-full bg-gray-900 animate-pulse flex items-center justify-center rounded-xl">
      <div className="text-center text-gray-400">
        <div className="text-4xl mb-2">🛰️</div>
        <p className="text-sm">جاري تحميل صور الأقمار الاصطناعية...</p>
      </div>
    </div>
  );
}

interface Props {
  fields: Field[];
  /** Full selected-field detail (from useField). Carries polygon/centroid even
   *  when the list API omits heavy geometry. Required for the heatmap overlay. */
  selectedField?: Field | null;
  selectedFieldId: string | null;
  flyToTarget: [number, number] | null;
  activeLayerId: string;
  onLayerChange: (id: string) => void;
  kpi: FieldKpiSnapshot | null | undefined;
  onFieldClick?: (field: Field) => void;
  activeDate: string | null;
  onDateChange: (date: string | null) => void;
  layerOpacity: number;
}

export function SatelliteMapPanel({
  fields,
  selectedField,
  selectedFieldId,
  flyToTarget,
  activeLayerId,
  onLayerChange,
  kpi,
  onFieldClick,
  activeDate,
  onDateChange,
  layerOpacity,
}: Props) {
  // Derive bbox from selected field polygon/centroid for catalog-based date lookup
  const fieldBbox = useMemo((): import('../hooks/useTimeseriesLayers').FieldBbox | undefined => {
    if (!selectedField) return undefined;
    if (selectedField.polygon) {
      const ring = selectedField.polygon.coordinates[0];
      if (ring && ring.length > 0) {
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
    activeLayerId,
    365,
    fieldBbox,
  );
  // Enrich the selected field with full polygon/centroid from the detail query,
  // because the list API may omit heavy geometry. Without polygon the heatmap
  // overlay can never be rendered.
  const enrichedFields = useMemo(() => {
    // Ensure selected field is present even if list API returned it without geometry
    const base = fields.some((f) => f.id === selectedFieldId)
      ? fields
      : selectedField ? [...fields, selectedField] : fields;

    return base.map((f) => {
      if (f.id !== selectedFieldId) return f;
      return {
        ...f,
        polygon:   selectedField?.polygon   ?? f.polygon,
        centroid:  selectedField?.centroid  ?? f.centroid,
        ndviValue: kpi?.ndvi != null ? Number(kpi.ndvi) : f.ndviValue,
      };
    });
  }, [fields, selectedFieldId, kpi, selectedField]);

  // Build kpiMap: { [fieldId]: snapshot } for badge rendering
  const kpiMap = useMemo(() => {
    if (!selectedFieldId || !kpi) return {};
    return { [selectedFieldId]: kpi };
  }, [selectedFieldId, kpi]);

  return (
    <div className="relative flex flex-col h-full min-h-0">
      {/* Map fills the panel */}
      <div className="flex-1 min-h-0 relative">
        <GoogleSatelliteMap
          fields={enrichedFields}
          selectedField={selectedField}
          selectedFieldId={selectedFieldId}
          flyToTarget={flyToTarget}
          activeLayerId={activeLayerId}
          kpiMap={kpiMap}
          onFieldClick={onFieldClick}
          activeDate={activeDate}
          layerOpacity={layerOpacity}
        />
      </div>

      {/* Layer switcher — full-width bar between map and timeline */}
      <SatelliteLayerSwitcher
        activeLayerId={activeLayerId}
        onLayerChange={onLayerChange}
        activeDate={activeDate}
      />

      {/* Timeline slider — shown only when a field is selected */}
      <SatelliteTimeline
        dates={timeseriesDates}
        activeDate={activeDate}
        onDateChange={onDateChange}
        loading={timeseriesLoading}
        hidden={!selectedFieldId}
      />
    </div>
  );
}
