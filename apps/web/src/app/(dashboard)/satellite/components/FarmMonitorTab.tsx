'use client';

/**
 * FarmMonitorTab — مراقبة المزارع
 *
 * Select a farm → ALL its fields appear on the full-width satellite map.
 * Click a field → choose a CDSE index → AI analysis panel appears on the right.
 *
 * Flow:
 *  1. Farm selected → full-width map with all field polygons
 *  2. Field clicked on map → CDSE index selector appears (floating overlay)
 *  3. Index selected → Spinner 1: "Fetching Field Info" (CDSE + OpenWeather + OpenMeteo)
 *                    → Spinner 2: "AI Processing / Field AI Analyzing"
 *  4. Results → right panel (Current Status + Recommendations as bullet points)
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Building2, X, ChevronDown, Loader2, Satellite, CloudSun, Brain, AlertCircle } from 'lucide-react';
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

// ── CDSE indices grouped for the selector ────────────────────────────────────

const CDSE_GROUPS = [
  {
    label: 'Vegetation | النباتات',
    indices: ['NDVI', 'EVI', 'NDRE', 'MSAVI', 'GNDVI', 'SAVI', 'LAI'],
  },
  {
    label: 'Water & Moisture | المياه والرطوبة',
    indices: ['NDWI', 'NDMI'],
  },
  {
    label: 'Soil & Land | التربة والأرض',
    indices: ['BSI'],
  },
  {
    label: 'Fire & Burn | الحرائق',
    indices: ['NBR'],
  },
] as const;

const ALL_INDICES = CDSE_GROUPS.flatMap((g) => g.indices);

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

/** Floating CDSE index selector that appears after a field is clicked */
function IndiceSelector({
  field,
  onSelect,
  onClose,
}: {
  field: Field;
  onSelect: (indice: string) => void;
  onClose: () => void;
}) {
  return (
    <div className="absolute inset-0 z-[2000] flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-[380px] max-w-[95vw] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">
              {field.nameAr || field.name}
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">اختر مؤشر CDSE للتحليل بالذكاء الاصطناعي</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        {/* Index groups */}
        <div className="p-4 space-y-3 max-h-[60vh] overflow-y-auto">
          {CDSE_GROUPS.map((group) => (
            <div key={group.label}>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                {group.label}
              </p>
              <div className="flex flex-wrap gap-2">
                {group.indices.map((idx) => (
                  <button
                    key={idx}
                    onClick={() => onSelect(idx)}
                    className="px-3 py-1.5 text-sm font-mono font-medium rounded-lg border border-gray-200 bg-gray-50 hover:bg-green-50 hover:border-green-400 hover:text-green-700 transition-all"
                  >
                    {idx}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/** Sequential loading overlay shown during data fetch + AI analysis */
function AnalysisLoadingOverlay({ step }: { step: LoadingStep }) {
  const steps = [
    {
      id: 'fetching',
      icon: <Satellite className="w-5 h-5" />,
      title: 'Fetching Field Info',
      titleAr: 'جاري جلب بيانات الحقل',
      subtitle: 'CDSE Satellite · OpenWeather · Open-Meteo',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
    {
      id: 'analyzing',
      icon: <Brain className="w-5 h-5" />,
      title: 'Field AI Analyzing',
      titleAr: 'جاري التحليل بالذكاء الاصطناعي',
      subtitle: 'Running parallel agricultural agents with Claude',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
    },
  ];

  const currentStep = steps.findIndex((s) => s.id === step);

  return (
    <div className="absolute inset-0 z-[2000] flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-[380px] max-w-[95vw] p-6">
        <div className="space-y-4">
          {steps.map((s, i) => {
            const isActive = s.id === step;
            const isDone = i < currentStep;
            return (
              <div
                key={s.id}
                className={`flex items-start gap-3 p-3 rounded-xl border transition-all ${
                  isActive
                    ? `${s.bgColor} ${s.borderColor} border`
                    : isDone
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-gray-50 border border-gray-100 opacity-40'
                }`}
              >
                <div
                  className={`mt-0.5 flex-shrink-0 ${
                    isActive ? s.color : isDone ? 'text-green-600' : 'text-gray-400'
                  }`}
                >
                  {isActive ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : isDone ? (
                    <span className="text-green-600 text-lg leading-none">✓</span>
                  ) : (
                    s.icon
                  )}
                </div>
                <div className="min-w-0">
                  <p className={`text-sm font-semibold ${isActive ? s.color : isDone ? 'text-green-700' : 'text-gray-400'}`}>
                    {s.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{s.titleAr}</p>
                  {isActive && (
                    <p className="text-xs text-gray-400 mt-1">{s.subtitle}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
        <p className="text-xs text-center text-gray-400 mt-4">
          Powered by Claude Sonnet · المدعوم بكلود سونيت
        </p>
      </div>
    </div>
  );
}

/** Right panel showing AI analysis results */
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
    <div className="h-full flex flex-col bg-white border-l border-gray-200 overflow-hidden">
      {/* Panel header */}
      <div className="flex items-start justify-between px-4 py-3 border-b border-gray-100 flex-shrink-0 bg-gradient-to-r from-green-50 to-blue-50">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-600 flex-shrink-0" />
            <h2 className="text-sm font-bold text-gray-900 truncate">
              {field.nameAr || field.name}
            </h2>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-semibold bg-green-100 text-green-700">
              {indice}
            </span>
            <span className="text-xs text-gray-400">
              {new Date(result.analyzed_at).toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-white/70 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        {/* Current Status */}
        <section className="px-4 pt-4 pb-3">
          <div className="flex items-center gap-2 mb-3">
            <CloudSun className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <h3 className="text-sm font-bold text-gray-800">Current Status</h3>
            <span className="text-xs text-gray-400">| الوضع الراهن</span>
          </div>
          <ul className="space-y-2">
            {result.current_status.map((bullet, i) => (
              <li key={i} className="flex gap-2 text-sm text-gray-700 leading-relaxed">
                <span className="text-green-500 flex-shrink-0 mt-0.5 font-bold">•</span>
                <span>{bullet}</span>
              </li>
            ))}
            {result.current_status.length === 0 && (
              <li className="text-sm text-gray-400 italic">No status data available</li>
            )}
          </ul>
        </section>

        <div className="mx-4 border-t border-gray-100" />

        {/* Recommendations */}
        <section className="px-4 pt-3 pb-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-4 h-4 text-orange-500 flex-shrink-0" />
            <h3 className="text-sm font-bold text-gray-800">Recommendations</h3>
            <span className="text-xs text-gray-400">| التوصيات</span>
          </div>
          <ul className="space-y-2">
            {result.recommendations.map((rec, i) => {
              const isUrgent = rec.includes('[URGENT]');
              const isHigh = rec.includes('[HIGH]');
              const clean = rec.replace(/\[(URGENT|HIGH|MEDIUM|LOW)\]/g, '').trim();
              return (
                <li key={i} className="flex gap-2 text-sm leading-relaxed">
                  <span
                    className={`flex-shrink-0 mt-0.5 font-bold ${
                      isUrgent ? 'text-red-500' : isHigh ? 'text-orange-500' : 'text-blue-500'
                    }`}
                  >
                    {isUrgent ? '🔴' : isHigh ? '🟠' : '•'}
                  </span>
                  <span className="text-gray-700">
                    {isUrgent && (
                      <span className="inline-block mr-1 px-1.5 py-0.5 text-xs font-bold bg-red-100 text-red-700 rounded">
                        URGENT
                      </span>
                    )}
                    {isHigh && !isUrgent && (
                      <span className="inline-block mr-1 px-1.5 py-0.5 text-xs font-bold bg-orange-100 text-orange-700 rounded">
                        HIGH
                      </span>
                    )}
                    {clean}
                  </span>
                </li>
              );
            })}
            {result.recommendations.length === 0 && (
              <li className="text-sm text-gray-400 italic">No recommendations available</li>
            )}
          </ul>
        </section>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-gray-100 bg-gray-50 flex-shrink-0">
        <p className="text-xs text-center text-gray-400">
          AI analysis by Claude Sonnet · تحليل ذكاء اصطناعي بكلود سونيت
        </p>
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

  const { data: farms = [], isLoading: farmsLoading } = useFarms();
  const { data: farmFields = [], isLoading: fieldsLoading } = useFieldsList(
    selectedFarmId ? { farmId: selectedFarmId } : undefined
  );

  const handleFarmSelect = useCallback((farmId: string | null) => {
    setSelectedFarmId(farmId);
    setActiveDate(null);
    setClickedField(null);
    setSelectedIndice(null);
    setLoadingStep('idle');
    setAnalysisResult(null);
    setAnalysisError(null);
  }, []);

  const handleFieldClick = useCallback((field: Field) => {
    setClickedField(field);
    setSelectedIndice(null);
    setLoadingStep('idle');
    setAnalysisResult(null);
    setAnalysisError(null);
  }, []);

  const handleCloseIndiceSelector = useCallback(() => {
    setClickedField(null);
  }, []);

  const handleCloseAnalysis = useCallback(() => {
    setAnalysisResult(null);
    setClickedField(null);
    setSelectedIndice(null);
    setLoadingStep('idle');
    setAnalysisError(null);
  }, []);

  /** Called when user picks a CDSE index — kicks off the two-phase pipeline */
  const handleIndiceSelect = useCallback(
    async (indice: string) => {
      if (!clickedField) return;

      setSelectedIndice(indice);
      setAnalysisError(null);

      // ── Phase 1: Fetch field AI data ──────────────────────────────────────
      setLoadingStep('fetching');
      let aiData: unknown;
      try {
        const res = await fetch(
          `/api/field-ai-data?fieldId=${clickedField.id}&indice=${indice}`
        );
        const json = await res.json();
        if (!res.ok) throw new Error(json?.error ?? `HTTP ${res.status}`);
        aiData = json?.data ?? json;
      } catch (err) {
        setLoadingStep('idle');
        setAnalysisError(err instanceof Error ? err.message : 'Failed to fetch field data');
        return;
      }

      // ── Phase 2: AI analysis ──────────────────────────────────────────────
      setLoadingStep('analyzing');
      try {
        const res = await fetch('/api/field-analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(aiData),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json?.error ?? json?.detail ?? `HTTP ${res.status}`);
        setAnalysisResult(json as AnalysisResult);
        setLoadingStep('idle');
      } catch (err) {
        setLoadingStep('idle');
        setAnalysisError(err instanceof Error ? err.message : 'AI analysis failed');
      }
    },
    [clickedField]
  );

  const selectedFarm = farms.find((f) => f.id === selectedFarmId);

  const farmCenter = useMemo(() => {
    if (!selectedFarm) return null;
    const lat = selectedFarm.centerLat ?? selectedFarm.coordinates?.lat;
    const lng = selectedFarm.centerLng ?? selectedFarm.coordinates?.lng;
    if (lat == null || lng == null) return null;
    return { lat, lng, zoom: selectedFarm.zoom ?? 14 };
  }, [selectedFarm]);

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

  const showAnalysisPanel = !!analysisResult && loadingStep === 'idle';
  const isLoading = loadingStep === 'fetching' || loadingStep === 'analyzing';

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Top bar */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-400">
            {selectedFarm
              ? `${selectedFarm.nameAr || selectedFarm.name} · ${farmFields.length} حقل`
              : `${farms.length} مزرعة متاحة`}
          </p>
          {showAnalysisPanel && clickedField && (
            <p className="text-xs text-purple-600 font-medium mt-0.5">
              ✦ تحليل AI: {clickedField.nameAr || clickedField.name} · {selectedIndice}
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

      {/* Map + optional right analysis panel */}
      <div className="flex-1 min-h-0 flex overflow-hidden">
        {/* Map area */}
        <div
          className={`relative min-h-0 transition-all duration-300 ${
            showAnalysisPanel ? 'flex-[3]' : 'flex-1'
          }`}
        >
          {!selectedFarmId ? (
            <div className="w-full h-full bg-gray-900 flex items-center justify-center">
              <div className="text-center text-gray-400">
                <div className="text-5xl mb-3">🌾</div>
                <p className="text-sm">اختر مزرعة لعرض حقولها على الخريطة</p>
                <p className="text-xs mt-1 text-gray-500">ثم انقر على حقل للتحليل بالذكاء الاصطناعي</p>
              </div>
            </div>
          ) : fieldsLoading ? (
            <MapSkeleton />
          ) : (
            <div className="relative w-full h-full">
              <GoogleSatelliteMap
                fields={farmFields}
                selectedField={clickedField}
                selectedFieldId={clickedField?.id ?? null}
                flyToTarget={null}
                farmCenter={farmCenter}
                activeLayerId={activeLayerId}
                kpiMap={{}}
                onFieldClick={handleFieldClick}
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

              {/* Layer switcher */}
              <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1001] bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg px-4 py-3 max-w-[95%]">
                <SatelliteLayerSwitcher
                  activeLayerId={activeLayerId}
                  onLayerChange={setActiveLayerId}
                />
                <p className="text-center text-xs text-gray-400 mt-2">
                  {selectedFarm
                    ? `طبقة ${SATELLITE_LAYERS.find(l => l.id === activeLayerId)?.labelAr ?? activeLayerId} — ${selectedFarm.nameAr || selectedFarm.name}`
                    : 'اختر مزرعة'}
                </p>
              </div>

              {/* Hint when no field selected */}
              {!clickedField && !isLoading && !showAnalysisPanel && farmFields.length > 0 && (
                <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1001]">
                  <div className="bg-black/60 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-full">
                    انقر على حقل لبدء التحليل بالذكاء الاصطناعي
                  </div>
                </div>
              )}

              {/* Error display */}
              {analysisError && !isLoading && (
                <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1001] max-w-sm">
                  <div className="bg-red-600 text-white text-xs px-4 py-2 rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                    <span>{analysisError}</span>
                    <button onClick={() => setAnalysisError(null)} className="ml-1 text-white/70 hover:text-white">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}

              {/* CDSE index selector overlay */}
              {clickedField && !selectedIndice && !isLoading && (
                <IndiceSelector
                  field={clickedField}
                  onSelect={handleIndiceSelect}
                  onClose={handleCloseIndiceSelector}
                />
              )}

              {/* Loading overlay */}
              {isLoading && <AnalysisLoadingOverlay step={loadingStep} />}
            </div>
          )}
        </div>

        {/* Right AI analysis panel */}
        {showAnalysisPanel && analysisResult && clickedField && (
          <div className="flex-[2] min-h-0 border-l border-gray-200 min-w-[320px] max-w-[480px]">
            <AnalysisPanel
              result={analysisResult}
              field={clickedField}
              indice={selectedIndice ?? analysisResult.indice}
              onClose={handleCloseAnalysis}
            />
          </div>
        )}
      </div>
    </div>
  );
}
