'use client';

/**
 * SAHOOL Field KPI Tiles
 * بطاقات KPI للحقل — Sentinel Hub + OpenWeather
 */

import React, { useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { useFieldKpiSnapshot, useTriggerKpiRefresh } from '../hooks/useFieldKPIs';
import type { FieldKpiSnapshot } from '../api';

// ─── Vegetation Index thresholds ─────────────────────────────────────────────

type Status = 'good' | 'warning' | 'critical' | 'na';

function ndviStatus(v?: number | null): Status {
  if (v == null) return 'na';
  if (v >= 0.5) return 'good';
  if (v >= 0.3) return 'warning';
  return 'critical';
}

function genericStatus(v?: number | null, good = 0.4, warn = 0.2): Status {
  if (v == null) return 'na';
  if (v >= good) return 'good';
  if (v >= warn) return 'warning';
  return 'critical';
}

const STATUS_DOT: Record<Status, string> = {
  good: 'bg-green-500',
  warning: 'bg-yellow-500',
  critical: 'bg-red-500',
  na: 'bg-gray-300',
};

// ─── Sub-components ───────────────────────────────────────────────────────────

interface KpiTileProps {
  label: string;
  labelAr: string;
  value: React.ReactNode;
  status: Status;
  unit?: string;
}

function KpiTile({ label, labelAr, value, status, unit }: KpiTileProps) {
  const borderColor =
    status === 'good'
      ? 'border-green-400'
      : status === 'warning'
      ? 'border-yellow-400'
      : status === 'critical'
      ? 'border-red-400'
      : 'border-gray-200';

  return (
    <div className={`bg-white rounded-xl border-l-4 ${borderColor} border border-gray-100 p-4 shadow-sm`}>
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="text-xs text-gray-500">{label}</p>
          <p className="text-xs text-gray-400">{labelAr}</p>
        </div>
        <span className={`w-2.5 h-2.5 rounded-full mt-1 ${STATUS_DOT[status]}`} />
      </div>
      <p className="text-xl font-bold text-gray-900">
        {value != null ? (
          <>
            {value}
            {unit && <span className="text-sm font-normal text-gray-500 ml-1">{unit}</span>}
          </>
        ) : (
          <span className="text-gray-400 text-base">—</span>
        )}
      </p>
    </div>
  );
}

function KpiSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm animate-pulse">
      <div className="h-3 bg-gray-200 rounded w-2/3 mb-2" />
      <div className="h-3 bg-gray-100 rounded w-1/2 mb-3" />
      <div className="h-6 bg-gray-200 rounded w-1/3" />
    </div>
  );
}

// ─── Satellite section ────────────────────────────────────────────────────────

function SatelliteSection({
  kpi,
  loading,
  onRefresh,
}: {
  kpi?: FieldKpiSnapshot | null;
  loading: boolean;
  onRefresh: () => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-700">مؤشرات الأقمار الصناعية</h3>
          <p className="text-xs text-gray-400">Sentinel Hub Vegetation Indices</p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 disabled:opacity-50"
          title="تحديث البيانات"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          تحديث
        </button>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {loading ? (
          Array.from({ length: 6 }).map((_, i) => <KpiSkeleton key={i} />)
        ) : (
          <>
            <KpiTile
              label="NDVI"
              labelAr="مؤشر الغطاء النباتي"
              value={kpi?.ndvi != null ? Number(kpi.ndvi).toFixed(3) : null}
              status={ndviStatus(kpi?.ndvi != null ? Number(kpi.ndvi) : null)}
            />
            <KpiTile
              label="EVI"
              labelAr="مؤشر النباتات المحسّن"
              value={kpi?.evi != null ? Number(kpi.evi).toFixed(3) : null}
              status={genericStatus(kpi?.evi != null ? Number(kpi.evi) : null, 0.4, 0.2)}
            />
            <KpiTile
              label="NDWI"
              labelAr="مؤشر محتوى الماء"
              value={kpi?.ndwi != null ? Number(kpi.ndwi).toFixed(3) : null}
              status={genericStatus(kpi?.ndwi != null ? Number(kpi.ndwi) : null, 0.2, 0)}
            />
            <KpiTile
              label="SAVI"
              labelAr="مؤشر الغطاء المعدّل للتربة"
              value={kpi?.savi != null ? Number(kpi.savi).toFixed(3) : null}
              status={genericStatus(kpi?.savi != null ? Number(kpi.savi) : null, 0.35, 0.15)}
            />
            <KpiTile
              label="LAI"
              labelAr="مؤشر مساحة الأوراق"
              value={kpi?.lai != null ? Number(kpi.lai).toFixed(3) : null}
              status={genericStatus(kpi?.lai != null ? Number(kpi.lai) : null, 2, 1)}
            />
            <KpiTile
              label="NDMI"
              labelAr="مؤشر رطوبة النبات"
              value={kpi?.ndmi != null ? Number(kpi.ndmi).toFixed(3) : null}
              status={genericStatus(kpi?.ndmi != null ? Number(kpi.ndmi) : null, 0.1, -0.1)}
            />
          </>
        )}
      </div>
      {kpi?.fetchedAt && !loading && (
        <p className="mt-2 text-xs text-gray-400">
          آخر تحديث: {new Date(kpi.fetchedAt).toLocaleString('ar-SA')}
          {kpi.satelliteSource && ` · ${kpi.satelliteSource}`}
        </p>
      )}
    </div>
  );
}

// ─── Weather section ──────────────────────────────────────────────────────────

function WeatherSection({
  kpi,
  loading,
}: {
  kpi?: FieldKpiSnapshot | null;
  loading: boolean;
}) {
  return (
    <div>
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-gray-700">بيانات الطقس</h3>
        <p className="text-xs text-gray-400">OpenWeather Current Conditions</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => <KpiSkeleton key={i} />)
        ) : (
          <>
            <KpiTile
              label="Temperature"
              labelAr="درجة الحرارة"
              value={kpi?.temperature != null ? Number(kpi.temperature).toFixed(1) : null}
              unit="°C"
              status={kpi?.temperature != null ? 'good' : 'na'}
            />
            <KpiTile
              label="Humidity"
              labelAr="الرطوبة"
              value={kpi?.humidity != null ? Number(kpi.humidity).toFixed(0) : null}
              unit="%"
              status={kpi?.humidity != null ? 'good' : 'na'}
            />
            <KpiTile
              label="Wind Speed"
              labelAr="سرعة الرياح"
              value={kpi?.windSpeed != null ? Number(kpi.windSpeed).toFixed(1) : null}
              unit="km/h"
              status={kpi?.windSpeed != null ? 'good' : 'na'}
            />
            <KpiTile
              label="Precipitation"
              labelAr="هطول الأمطار"
              value={kpi?.precipitation != null ? Number(kpi.precipitation).toFixed(1) : null}
              unit="mm"
              status={kpi?.precipitation != null ? 'good' : 'na'}
            />
            <KpiTile
              label="UV Index"
              labelAr="مؤشر الأشعة فوق البنفسجية"
              value={kpi?.uvIndex != null ? Number(kpi.uvIndex).toFixed(1) : null}
              status={
                kpi?.uvIndex == null
                  ? 'na'
                  : Number(kpi.uvIndex) <= 5
                  ? 'good'
                  : Number(kpi.uvIndex) <= 8
                  ? 'warning'
                  : 'critical'
              }
            />
          </>
        )}
      </div>
      {kpi?.weatherConditionAr && !loading && (
        <p className="mt-2 text-xs text-gray-500">
          الحالة: {kpi.weatherConditionAr}
          {kpi.weatherSource && ` · ${kpi.weatherSource}`}
        </p>
      )}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface FieldKPITilesProps {
  fieldId: string;
  centroidLat?: number;
  centroidLng?: number;
}

export function FieldKPITiles({ fieldId, centroidLat, centroidLng }: FieldKPITilesProps) {
  const { data: kpi, isLoading } = useFieldKpiSnapshot(fieldId);
  const refresh = useTriggerKpiRefresh(fieldId);

  // Auto-trigger when no snapshot and centroid is available
  useEffect(() => {
    if (!isLoading && kpi === null && centroidLat != null && centroidLng != null && !refresh.isPending) {
      refresh.mutate({ lat: centroidLat, lng: centroidLng });
    }
  }, [isLoading, kpi, centroidLat, centroidLng]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleRefresh = () => {
    if (centroidLat != null && centroidLng != null) {
      refresh.mutate({ lat: centroidLat, lng: centroidLng });
    }
  };

  const isWorking = isLoading || refresh.isPending;

  return (
    <div className="space-y-6">
      <SatelliteSection kpi={kpi} loading={isWorking} onRefresh={handleRefresh} />
      <WeatherSection kpi={kpi} loading={isWorking} />
    </div>
  );
}

export default FieldKPITiles;
