'use client';

/**
 * FarmMonitorTab — مراقبة المزارع
 *
 * Select a farm → spinning loading overlay → ALL its fields appear on the
 * FULL-WIDTH satellite map at once (CDSE imagery + historical date timeline).
 *
 * Click a field → CDSE AI analysis results appear as a floating dark panel on the
 * right side of the map (does NOT shrink the map).
 *
 * Flow:
 *  1. Farm selected → full-width map with loading spinner overlay
 *  2. Fields loaded → all field polygons + Sentinel imagery rendered
 *  3. Field clicked on map → two-phase AI pipeline starts
 *     Phase 1: "جاري جلب بيانات الحقل" (CDSE + OpenWeather + OpenMeteo)
 *     Phase 2: "جاري التحليل بالذكاء الاصطناعي" (multi-agent)
 *  4. Results → floating right dark panel (الوضع الراهن + التوصيات)
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  Building2,
  X,
  ChevronDown,
  Loader2,
  Satellite,
  CloudSun,
  Brain,
  AlertCircle,
} from 'lucide-react';
import dynamic from 'next/dynamic';
import { useFarms } from '@/features/farms/hooks/useFarms';
import { useFieldsList } from '@/features/fields/hooks/useFieldsList';
import { SatelliteLayerSwitcher } from './SatelliteLayerSwitcher';
import { SatelliteTimeline } from './SatelliteTimeline';
import { useTimeseriesLayers } from '../hooks/useTimeseriesLayers';
import { SATELLITE_LAYERS } from '../types';
import type { Farm } from '@/features/farms/types';
import type { Field } from '@/features/fields/types';

const GoogleSatelliteMap = dynamic(
  () => import('./GoogleSatelliteMap').then((m) => m.GoogleSatelliteMap),
  { ssr: false, loading: () => <MapSkeleton /> }
);

// ── Types ────────────────────────────────────────────────────────────────────

interface AnalysisResult {
  field_id: string;
  indice: string;
  current_status: string[];
  recommendations: string[];
  analyzed_at: string;
}

type LoadingStep = 'idle' | 'fetching' | 'analyzing';

// ── Sub-components ────────────────────────────────────────────────────────────

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

/** Full-area loading spinner shown while fields are being fetched for a farm */
function FarmLoadingOverlay({ farmName }: { farmName: string }) {
  return (
    <div className="absolute inset-0 z-[3000] flex flex-col items-center justify-center bg-gray-950/75 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <div className="relative flex items-center justify-center w-16 h-16">
          <Loader2 className="w-16 h-16 animate-spin text-green-400" strokeWidth={1.5} />
          <span className="absolute text-2xl">🌾</span>
        </div>
        <div className="text-center">
          <p className="text-white font-semibold text-base">جاري تحميل حقول المزرعة</p>
          <p className="text-green-300 text-sm mt-1">{farmName}</p>
          <p className="text-gray-400 text-xs mt-2">Loading farm fields…</p>
        </div>
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
        <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
    </div>
  );
}

/** Loading states rendered inside the floating dark analysis panel */
function AnalysisLoadingPanel({ step }: { step: LoadingStep }) {
  const steps = [
    {
      id: 'fetching',
      icon: <Satellite className="w-5 h-5" />,
      titleAr: 'جاري جلب بيانات الحقل',
      subtitle: 'CDSE · OpenWeather · Open-Meteo',
      activeColor: 'text-blue-400',
      activeBg: 'bg-blue-950/60',
      activeBorder: 'border-blue-700',
      doneBg: 'bg-green-950/60',
      doneBorder: 'border-green-700',
    },
    {
      id: 'analyzing',
      icon: <Brain className="w-5 h-5" />,
      titleAr: 'جاري التحليل بالذكاء الاصطناعي',
      subtitle: 'تشغيل وكلاء الذكاء الاصطناعي الزراعي المتوازيين',
      activeColor: 'text-purple-400',
      activeBg: 'bg-purple-950/60',
      activeBorder: 'border-purple-700',
      doneBg: 'bg-green-950/60',
      doneBorder: 'border-green-700',
    },
  ];

  const currentStep = steps.findIndex((s) => s.id === step);

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full space-y-4">
        {steps.map((s, i) => {
          const isActive = s.id === step;
          const isDone = i < currentStep;
          return (
            <div
              key={s.id}
              className={`flex items-start gap-3 p-3 rounded-xl border transition-all ${
                isActive
                  ? `${s.activeBg} ${s.activeBorder} border`
                  : isDone
                  ? `${s.doneBg} ${s.doneBorder} border`
                  : 'bg-gray-800/40 border border-gray-700/40 opacity-40'
              }`}
            >
              <div
                className={`mt-0.5 flex-shrink-0 ${
                  isActive ? s.activeColor : isDone ? 'text-green-400' : 'text-gray-600'
                }`}
              >
                {isActive ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : isDone ? (
                  <span className="text-green-400 text-lg leading-none">✓</span>
                ) : (
                  s.icon
                )}
              </div>
              <div className="min-w-0">
                <p className={`text-sm font-semibold ${isActive ? s.activeColor : isDone ? 'text-green-400' : 'text-gray-600'}`}>
                  {s.titleAr}
                </p>
                {isActive && (
                  <p className="text-xs text-gray-500 mt-1">{s.subtitle}</p>
                )}
              </div>
            </div>
          );
        })}
        <p className="text-xs text-center text-gray-600 mt-2">
          مدعوم بالذكاء الاصطناعي · Qwen 3.5
        </p>
      </div>
    </div>
  );
}

/** Floating dark-mode AI analysis results panel (overlaid on the map, right side) */
function AnalysisPanel({
  result,
  field,
  indice,
  onClose,
}: {
  result: AnalysisResult;
  field: Field;
  indice: string;
  onClose: () => void;
}) {
  return (
    <div className="h-full flex flex-col bg-black overflow-hidden" dir="rtl">
      {/* Panel header */}
      <div className="flex items-start justify-between px-4 py-3 border-b border-gray-700 flex-shrink-0 bg-gradient-to-l from-green-950 to-blue-950">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400 flex-shrink-0" />
            <h2 className="text-sm font-extrabold text-white truncate">
              {field.nameAr || field.name}
            </h2>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-green-900 text-green-300 border border-green-700">
              {indice}
            </span>
            <span className="text-xs text-gray-400">
              {new Date(result.analyzed_at).toLocaleTimeString('ar-SA', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors flex-shrink-0 mr-auto ml-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
        {/* Current Status — الوضع الراهن */}
        <section className="px-4 pt-4 pb-3">
          <div className="flex items-center gap-2 mb-3">
            <CloudSun className="w-4 h-4 text-blue-400 flex-shrink-0" />
            <h3 className="text-sm font-extrabold text-white tracking-wide">الوضع الراهن</h3>
          </div>
          <ul className="space-y-2.5">
            {result.current_status.map((bullet, i) => (
              <li key={i} className="flex gap-2 text-sm text-white leading-relaxed">
                <span className="text-green-400 flex-shrink-0 mt-0.5 font-bold">•</span>
                <span>{bullet}</span>
              </li>
            ))}
            {result.current_status.length === 0 && (
              <li className="text-sm text-gray-500 italic">لا توجد بيانات متاحة</li>
            )}
          </ul>
        </section>

        <div className="mx-4 border-t border-gray-700" />

        {/* Recommendations — التوصيات */}
        <section className="px-4 pt-3 pb-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <h3 className="text-sm font-extrabold text-white tracking-wide">التوصيات</h3>
          </div>
          <ul className="space-y-2.5">
            {result.recommendations.map((rec, i) => {
              const isUrgent = rec.includes('[عاجل]') || rec.includes('[URGENT]');
              const isHigh = rec.includes('[عالٍ]') || rec.includes('[HIGH]');
              const clean = rec
                .replace(/\[(عاجل|عالٍ|متوسط|منخفض|URGENT|HIGH|MEDIUM|LOW)\]/g, '')
                .trim();
              return (
                <li key={i} className="flex gap-2 text-sm leading-relaxed">
                  <span className={`flex-shrink-0 mt-0.5 font-bold ${isUrgent ? 'text-red-400' : isHigh ? 'text-amber-400' : 'text-blue-400'}`}>
                    {isUrgent ? '🔴' : isHigh ? '🟠' : '•'}
                  </span>
                  <span className="text-white">
                    {isUrgent && (
                      <span className="inline-block ml-1 mb-0.5 px-1.5 py-0.5 text-xs font-bold bg-red-900 text-red-300 border border-red-700 rounded">
                        عاجل
                      </span>
                    )}
                    {isHigh && !isUrgent && (
                      <span className="inline-block ml-1 mb-0.5 px-1.5 py-0.5 text-xs font-bold bg-amber-900 text-amber-300 border border-amber-700 rounded">
                        عالٍ
                      </span>
                    )}
                    {clean}
                  </span>
                </li>
              );
            })}
            {result.recommendations.length === 0 && (
              <li className="text-sm text-gray-500 italic">لا توجد توصيات متاحة</li>
            )}
          </ul>
        </section>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-gray-700 bg-gray-950 flex-shrink-0">
        <p className="text-xs text-center text-gray-500">
          تحليل ذكاء اصطناعي زراعي · Qwen 3.5 via OpenRouter
        </p>
      </div>
    </div>
  );
}

/** Brief panel when no satellite imagery is available — no AI call made */
function NoSatellitePanel({
  field,
  indice,
  onClose,
}: {
  field: Field;
  indice: string;
  onClose: () => void;
}) {
  return (
    <div className="h-full flex flex-col bg-black overflow-hidden" dir="rtl">
      <div className="flex items-start justify-between px-4 py-3 border-b border-gray-700 flex-shrink-0 bg-gradient-to-l from-gray-900 to-gray-950">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Satellite className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <h2 className="text-sm font-extrabold text-white truncate">
              {field.nameAr || field.name}
            </h2>
          </div>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-gray-800 text-gray-400 border border-gray-700 mt-1">
            {indice}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors flex-shrink-0 mr-auto ml-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center px-6 text-center gap-4">
        <div className="w-14 h-14 rounded-full bg-gray-800/80 flex items-center justify-center">
          <Satellite className="w-7 h-7 text-gray-500" />
        </div>
        <p className="text-sm text-gray-300 leading-relaxed">
          لا تتوفر صور أقمار اصطناعية لهذا الحقل حاليًا
        </p>
        <p className="text-xs text-gray-600">جرّب مؤشرًا آخر أو أعد المحاولة لاحقًا</p>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

interface Props {
  activeLayerId: string;
  setActiveLayerId: (id: string) => void;
}

export function FarmMonitorTab({ activeLayerId, setActiveLayerId }: Props) {
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);
  const [activeDate, setActiveDate] = useState<string | null>(null);

  // Field click → AI analysis state
  const [clickedField, setClickedField] = useState<Field | null>(null);
  const [selectedIndice, setSelectedIndice] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState<LoadingStep>('idle');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [noSatellite, setNoSatellite] = useState(false);

  const { data: farms = [], isLoading: farmsLoading } = useFarms();
  const { data: farmFields = [], isLoading: fieldsLoading } = useFieldsList(
    selectedFarmId ? { farmId: selectedFarmId } : undefined
  );

  const handleFarmSelect = useCallback(
    (farmId: string | null) => {
      setSelectedFarmId(farmId);
      setActiveDate(null);
      setClickedField(null);
      setSelectedIndice(null);
      setLoadingStep('idle');
      setAnalysisResult(null);
      setAnalysisError(null);
      setNoSatellite(false);
      if (farmId) setActiveLayerId('NDVI');
    },
    [setActiveLayerId]
  );

  /** Two-phase AI pipeline: fetch field data → multi-agent analysis */
  const runAnalysis = useCallback(async (field: Field, indice: string) => {
    setClickedField(field);
    setSelectedIndice(indice);
    setAnalysisError(null);
    setAnalysisResult(null);
    setNoSatellite(false);

    // Phase 1: Fetch field AI data (CDSE + OpenWeather + OpenMeteo)
    setLoadingStep('fetching');
    let aiData: unknown;
    try {
      const res = await fetch(`/api/field-ai-data?fieldId=${field.id}&indice=${indice}`);
      const json = await res.json();
      if (!res.ok) {
        const msg = typeof json?.error === 'string'
          ? json.error
          : typeof json?.message === 'string'
          ? json.message
          : `HTTP ${res.status}`;
        throw new Error(msg);
      }
      aiData = json?.data ?? json;
    } catch (err) {
      setLoadingStep('idle');
      setAnalysisError(err instanceof Error ? err.message : 'فشل جلب بيانات الحقل');
      return;
    }

    // Guard: if no satellite value found across all fallbacks, skip AI and show brief message
    const cdseValue = (aiData as any)?.cdse?.value;
    if (cdseValue === null || cdseValue === undefined) {
      setNoSatellite(true);
      setLoadingStep('idle');
      return;
    }

    // Phase 2: multi-agent AI analysis (3 agents in parallel)
    setLoadingStep('analyzing');
    try {
      const res = await fetch('/api/field-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(aiData),
      });
      const json = await res.json();
      if (!res.ok) {
        const msg = typeof json?.error === 'string'
          ? json.error
          : typeof json?.detail === 'string'
          ? json.detail
          : typeof json?.message === 'string'
          ? json.message
          : `HTTP ${res.status}`;
        throw new Error(msg);
      }
      setAnalysisResult(json as AnalysisResult);
      setLoadingStep('idle');
    } catch (err) {
      setLoadingStep('idle');
      setAnalysisError(err instanceof Error ? err.message : 'فشل التحليل بالذكاء الاصطناعي');
    }
  }, []);

  /** Field click → analyze with the current active CDSE index */
  const handleFieldClick = useCallback(
    (field: Field) => {
      runAnalysis(field, activeLayerId);
    },
    [runAnalysis, activeLayerId]
  );

  const handleCloseAnalysis = useCallback(() => {
    setAnalysisResult(null);
    setClickedField(null);
    setSelectedIndice(null);
    setLoadingStep('idle');
    setAnalysisError(null);
    setNoSatellite(false);
  }, []);

  const selectedFarm = farms.find((f) => f.id === selectedFarmId);

  const farmBbox = useMemo(() => {
    if (!farmFields.length) return undefined;
    let n = -Infinity, s = Infinity, e = -Infinity, w = Infinity;
    let found = false;
    farmFields.forEach((f) => {
      const ring = f.polygon?.coordinates?.[0];
      if (ring?.length) {
        ring.forEach((coord) => {
          const lng = coord[0] as number,
            lat = coord[1] as number;
          if (lat > n) n = lat;
          if (lat < s) s = lat;
          if (lng > e) e = lng;
          if (lng < w) w = lng;
        });
        found = true;
      } else if (f.centroid) {
        const lng = f.centroid.coordinates[0] as number;
        const lat = f.centroid.coordinates[1] as number;
        const d = 0.008;
        if (lat + d > n) n = lat + d;
        if (lat - d < s) s = lat - d;
        if (lng + d > e) e = lng + d;
        if (lng - d < w) w = lng - d;
        found = true;
      }
    });
    return found ? { west: w, south: s, east: e, north: n } : undefined;
  }, [farmFields]);

  // Primary: use the farm's stored centerLat/centerLng/zoom.
  // Fallback: derive center from the farm's registered bbox, then from computed field extents.
  // Always use the stored zoom — never fitBounds.
  const farmCenter = useMemo(() => {
    if (!selectedFarm) return null;
    const lat = selectedFarm.centerLat ?? selectedFarm.coordinates?.lat;
    const lng = selectedFarm.centerLng ?? selectedFarm.coordinates?.lng;
    const zoom = selectedFarm.zoom ?? 14;
    if (lat != null && lng != null) {
      return { lat: Number(lat), lng: Number(lng), zoom };
    }
    // Derive center from registered bbox first, then from computed field extents
    const bboxSrc = selectedFarm.bbox
      ? { west: selectedFarm.bbox[0], south: selectedFarm.bbox[1], east: selectedFarm.bbox[2], north: selectedFarm.bbox[3] }
      : farmBbox;
    if (bboxSrc) {
      return {
        lat: (bboxSrc.north + bboxSrc.south) / 2,
        lng: (bboxSrc.east + bboxSrc.west) / 2,
        zoom,
      };
    }
    return null;
  }, [selectedFarm, farmBbox]);

  const { data: timeseriesDates = [], isLoading: timeseriesLoading } = useTimeseriesLayers(
    activeLayerId,
    365,
    farmBbox
  );

  const isAnalyzing = loadingStep === 'fetching' || loadingStep === 'analyzing';
  const hasResult = !!analysisResult && loadingStep === 'idle';
  const showSidePanel = !!clickedField && (isAnalyzing || hasResult || !!analysisError || noSatellite);

  // Trigger Leaflet invalidateSize after panel visibility changes
  useEffect(() => {
    const timer = setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 320);
    return () => clearTimeout(timer);
  }, [showSidePanel, selectedFarmId]);

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* ── Top bar: farm selector ── */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-400">
            {selectedFarm
              ? `${selectedFarm.nameAr || selectedFarm.name} · ${farmFields.length} حقل`
              : `${farms.length} مزرعة متاحة`}
          </p>
          {(isAnalyzing || hasResult) && clickedField && (
            <p className="text-xs text-purple-600 font-medium mt-0.5">
              ✦ {isAnalyzing ? 'جاري التحليل…' : 'تحليل AI'}:{' '}
              {clickedField.nameAr || clickedField.name} · {selectedIndice}
            </p>
          )}
        </div>
        <FarmSelectorDropdown
          farms={farms}
          selectedFarmId={selectedFarmId}
          onSelect={handleFarmSelect}
          loading={farmsLoading}
        />
      </div>

      {/* ── Map + floating analysis panel (full-width map always) ── */}
      <div className="flex-1 min-h-0 relative overflow-hidden">

        {/* ── Empty state when no farm is selected ── */}
        {!selectedFarmId ? (
          <div className="w-full h-full bg-gray-900 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <div className="text-5xl mb-3">🌾</div>
              <p className="text-sm">اختر مزرعة لعرض حقولها على الخريطة</p>
              <p className="text-xs mt-1 text-gray-500">ثم انقر على حقل للتحليل بالذكاء الاصطناعي</p>
            </div>
          </div>
        ) : (
          <>
            {/* ── Full-width map ── */}
            <div className="absolute inset-0">
              {fieldsLoading ? (
                <MapSkeleton />
              ) : (
                <GoogleSatelliteMap
                  fields={farmFields}
                  selectedField={null}
                  selectedFieldId={null}
                  flyToTarget={null}
                  farmCenter={farmCenter}
                  farmId={selectedFarmId}
                  activeLayerId={activeLayerId}
                  kpiMap={{}}
                  onFieldClick={handleFieldClick}
                  activeDate={activeDate}
                  layerOpacity={0.85}
                  showAllFieldsImagery={!!selectedFarmId}
                />
              )}
            </div>

            {/* ── Farm loading overlay (while fields are fetching) ── */}
            {fieldsLoading && selectedFarm && (
              <FarmLoadingOverlay farmName={selectedFarm.nameAr || selectedFarm.name} />
            )}

            {/* ── Timeline slider (bottom of map, above layer switcher) ── */}
            {!fieldsLoading && (
              <SatelliteTimeline
                dates={timeseriesDates}
                activeDate={activeDate}
                onDateChange={setActiveDate}
                loading={timeseriesLoading}
                hidden={!farmFields.length}
              />
            )}

            {/* ── Layer switcher (centered bottom) ── */}
            {!fieldsLoading && (
              <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1001] bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg px-4 py-3 max-w-[95%]">
                <SatelliteLayerSwitcher
                  activeLayerId={activeLayerId}
                  onLayerChange={setActiveLayerId}
                />
                <p className="text-center text-xs text-gray-400 mt-2">
                  {selectedFarm
                    ? `طبقة ${SATELLITE_LAYERS.find((l) => l.id === activeLayerId)?.labelAr ?? activeLayerId} — ${selectedFarm.nameAr || selectedFarm.name}`
                    : 'اختر مزرعة'}
                </p>
              </div>
            )}

            {/* ── Click-a-field hint ── */}
            {!fieldsLoading && !clickedField && !isAnalyzing && !hasResult && !noSatellite && farmFields.length > 0 && (
              <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1001]">
                <div className="bg-black/60 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-full">
                  انقر على حقل لبدء التحليل بالذكاء الاصطناعي
                </div>
              </div>
            )}

            {/* ── Floating dark AI analysis panel (right side, does not shrink map) ── */}
            {showSidePanel && (
              <div className="absolute top-0 right-0 bottom-0 z-[1500] w-[380px] max-w-[45%] shadow-2xl flex flex-col border-l border-gray-800 bg-gray-950/97 backdrop-blur-md">
                {/* Error banner */}
                {analysisError && !isAnalyzing && (
                  <div className="m-4 p-3 bg-red-950/80 border border-red-800 rounded-xl flex items-start gap-2 flex-shrink-0">
                    <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-semibold text-red-300">فشل التحليل</p>
                      <p className="text-xs text-red-400 mt-0.5">{analysisError}</p>
                    </div>
                    <button
                      onClick={handleCloseAnalysis}
                      className="text-red-600 hover:text-red-400 transition-colors"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}

                {/* Loading steps */}
                {isAnalyzing && clickedField && (
                  <>
                    <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 flex-shrink-0 bg-gradient-to-l from-purple-950/60 to-blue-950/60">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                        <span className="text-sm font-semibold text-white">
                          {clickedField.nameAr || clickedField.name}
                        </span>
                      </div>
                      <button
                        onClick={handleCloseAnalysis}
                        className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <AnalysisLoadingPanel step={loadingStep} />
                  </>
                )}

                {/* No satellite imagery available */}
                {noSatellite && clickedField && (
                  <NoSatellitePanel
                    field={clickedField}
                    indice={selectedIndice ?? activeLayerId}
                    onClose={handleCloseAnalysis}
                  />
                )}

                {/* Results */}
                {hasResult && analysisResult && clickedField && (
                  <AnalysisPanel
                    result={analysisResult}
                    field={clickedField}
                    indice={selectedIndice ?? analysisResult.indice}
                    onClose={handleCloseAnalysis}
                  />
                )}

                {/* Error-only close button at bottom */}
                {analysisError && !isAnalyzing && (
                  <div className="p-4 flex-shrink-0">
                    <button
                      onClick={handleCloseAnalysis}
                      className="w-full py-2 text-sm text-gray-500 hover:text-gray-300 border border-gray-800 rounded-lg hover:bg-gray-800/50 transition-colors"
                    >
                      إغلاق
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
