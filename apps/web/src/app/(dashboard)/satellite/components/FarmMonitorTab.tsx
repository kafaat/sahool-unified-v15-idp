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
  Brain,
  AlertCircle,
} from 'lucide-react';
import dynamic from 'next/dynamic';
import { useFarms } from '@/features/farms/hooks/useFarms';
import { useFieldsList } from '@/features/fields/hooks/useFieldsList';
import { SatelliteLayerSwitcher } from './SatelliteLayerSwitcher';
import { SatelliteTimeline } from './SatelliteTimeline';
import { useTimeseriesLayers } from '../hooks/useTimeseriesLayers';
import type { Farm } from '@/features/farms/types';
import type { Field } from '@/features/fields/types';

const GoogleSatelliteMap = dynamic(
  () => import('./GoogleSatelliteMap').then((m) => m.GoogleSatelliteMap),
  { ssr: false, loading: () => <MapSkeleton /> }
);

// ── Types ────────────────────────────────────────────────────────────────────

interface SectionContent {
  title: string;
  title_en: string;
  status: 'good' | 'moderate' | 'warning' | 'critical';
  status_color: 'green' | 'yellow' | 'orange' | 'red';
  summary: string;
  details: string[];
  metrics?: Record<string, unknown> | null;
  confidence: number;
}

interface AnalysisSections {
  health_overview: SectionContent;
  vegetation_health: SectionContent;
  water_stress: SectionContent;
  growth_stage: SectionContent;
  nutrient_status: SectionContent;
  pest_disease_risk: SectionContent;
  irrigation_recommendation: SectionContent;
  weather_impact: SectionContent;
  yield_prediction: SectionContent;
  soil_health: SectionContent;
  historical_trends: SectionContent;
  action_plan: SectionContent;
  economic_impact: SectionContent;
}

interface ImageryPayload {
  true_color: string | null;
  ndvi_heatmap: string | null;
  ndmi_heatmap: string | null;
  ndre_heatmap: string | null;
}

interface FieldAnalysisResponse {
  field_id: string;
  analyzed_at: string;
  cached: boolean;
  health_score: number;
  health_class: 'healthy' | 'moderate' | 'stressed' | 'critical';
  health_confidence: number;
  imagery?: ImageryPayload | null;
  sections?: AnalysisSections | null;
  indices_summary: Record<string, number | null>;
  satellite_date?: string | null;
  cloud_cover_pct?: number | null;
  data_sources?: string[];
  indice: string;
  // legacy compat
  current_status?: string[];
  recommendations?: string[];
  farmer?: unknown;
  specialist?: unknown;
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
  analysis,
  imagery,
  field,
  onClose,
}: {
  analysis: FieldAnalysisResponse;
  imagery?: ImageryPayload | null;
  field: Field;
  onClose: () => void;
}) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['health_overview', 'vegetation_health', 'water_stress', 'growth_stage', 'nutrient_status'])
  );

  const toggleSection = (key: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case 'good': return '\u2705';
      case 'moderate': return '\uD83D\uDFE1';
      case 'warning': return '\uD83D\uDFE0';
      case 'critical': return '\uD83D\uDD34';
      default: return '\u26AA';
    }
  };

  const healthColor = analysis.health_score >= 70 ? '#22c55e' : analysis.health_score >= 40 ? '#eab308' : '#ef4444';

  const sectionOrder: Array<[string, SectionContent | undefined]> = analysis.sections ? [
    ['health_overview', analysis.sections.health_overview],
    ['vegetation_health', analysis.sections.vegetation_health],
    ['water_stress', analysis.sections.water_stress],
    ['growth_stage', analysis.sections.growth_stage],
    ['nutrient_status', analysis.sections.nutrient_status],
    ['pest_disease_risk', analysis.sections.pest_disease_risk],
    ['irrigation_recommendation', analysis.sections.irrigation_recommendation],
    ['weather_impact', analysis.sections.weather_impact],
    ['yield_prediction', analysis.sections.yield_prediction],
    ['soil_health', analysis.sections.soil_health],
    ['historical_trends', analysis.sections.historical_trends],
    ['action_plan', analysis.sections.action_plan],
    ['economic_impact', analysis.sections.economic_impact],
  ] : [];

  return (
    <div className="h-full flex flex-col bg-gray-900 overflow-hidden" dir="rtl">
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
              {analysis.indice}
            </span>
            <span className="text-xs text-gray-300">
              {new Date(analysis.analyzed_at).toLocaleTimeString('ar-SA', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors flex-shrink-0 mr-auto ml-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
        <div className="flex flex-col gap-3 p-3">
          {/* Imagery Gallery */}
          {imagery && (imagery.true_color || imagery.ndvi_heatmap || imagery.ndmi_heatmap || imagery.ndre_heatmap) && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {[
                { key: 'true_color', label: '\u0627\u0644\u0623\u0644\u0648\u0627\u0646 \u0627\u0644\u062D\u0642\u064A\u0642\u064A\u0629', src: imagery.true_color },
                { key: 'ndvi_heatmap', label: 'NDVI', src: imagery.ndvi_heatmap },
                { key: 'ndmi_heatmap', label: 'NDMI', src: imagery.ndmi_heatmap },
                { key: 'ndre_heatmap', label: 'NDRE', src: imagery.ndre_heatmap },
              ].filter(img => img.src).map(img => (
                <div key={img.key} className="flex-shrink-0 w-40">
                  <img src={`data:image/png;base64,${img.src}`} alt={img.label} className="w-full h-28 object-cover rounded-lg" />
                  <p className="text-xs text-center text-gray-400 mt-1">{img.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Health Score Badge */}
          <div className="flex items-center gap-4 bg-gray-800 rounded-xl p-4">
            <div className="relative w-16 h-16 flex items-center justify-center">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                <path d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none" stroke="#4b5563" strokeWidth="3" />
                <path d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none" stroke={healthColor} strokeWidth="3"
                  strokeDasharray={`${analysis.health_score}, 100`} />
              </svg>
              <span className="absolute text-lg font-bold" style={{ color: healthColor }}>{analysis.health_score}</span>
            </div>
            <div className="flex-1">
              <p className="text-white font-semibold text-sm">
                {analysis.health_class === 'healthy' ? '\u0635\u062D\u064A' : analysis.health_class === 'moderate' ? '\u0645\u062A\u0648\u0633\u0637' : analysis.health_class === 'stressed' ? '\u0645\u062C\u0647\u062F' : '\u062D\u0631\u062C'}
              </p>
              <p className="text-gray-200 text-xs">{'\u062B\u0642\u0629'}: {Math.round(analysis.health_confidence * 100)}% | {analysis.indice}</p>
              {analysis.satellite_date && <p className="text-gray-300 text-xs">{'\u062A\u0627\u0631\u064A\u062E \u0627\u0644\u0635\u0648\u0631\u0629'}: {analysis.satellite_date}</p>}
            </div>
            {analysis.cached && <span className="text-xs bg-blue-900/40 text-blue-300 px-2 py-0.5 rounded">{'\u0645\u062E\u0632\u0651\u0646'}</span>}
          </div>

          {/* 13 Sections */}
          {sectionOrder.map(([key, section]) => {
            if (!section) return null;
            const isExpanded = expandedSections.has(key);
            return (
              <div key={key} className="bg-gray-800 rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleSection(key)}
                  className="w-full flex items-center gap-2 p-3 text-right hover:bg-gray-700 transition-colors"
                >
                  <span className="text-sm">{statusIcon(section.status)}</span>
                  <span className="flex-1 text-sm font-medium text-white">{section.title}</span>
                  <span className="text-xs text-gray-300">{section.title_en}</span>
                  <span className="text-gray-300 text-xs">{isExpanded ? '\u25B2' : '\u25BC'}</span>
                </button>
                {isExpanded && (
                  <div className="px-3 pb-3 border-t border-gray-600">
                    <p className="text-white text-sm mt-2 leading-relaxed">{section.summary}</p>
                    {section.details.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {section.details.map((detail, i) => (
                          <li key={i} className="text-gray-200 text-xs flex gap-2">
                            <span className="text-gray-400 mt-0.5">{'\u2022'}</span>
                            <span>{detail}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {section.confidence > 0 && (
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 h-1 bg-gray-600 rounded-full overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${section.confidence * 100}%`, backgroundColor: section.confidence > 0.7 ? '#22c55e' : section.confidence > 0.4 ? '#eab308' : '#ef4444' }} />
                        </div>
                        <span className="text-xs text-gray-300">{Math.round(section.confidence * 100)}%</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Fallback for legacy response (old farmer/specialist format or when sections is null) */}
          {!analysis.sections && (() => {
            // Extract content from old farmer/specialist format if present
            const farmer = analysis.farmer as Record<string, unknown> | null | undefined;
            const specialist = analysis.specialist as Record<string, unknown> | null | undefined;
            const farmerAr = (farmer?.ar ?? farmer) as Record<string, unknown> | null | undefined;
            const specialistAr = (specialist?.ar ?? specialist) as Record<string, unknown> | null | undefined;

            const observations = (
              (farmerAr?.observations as string[]) ??
              (specialistAr?.observations as string[]) ??
              analysis.current_status ??
              []
            ).filter(Boolean);

            const actions = (
              (farmerAr?.actions as Array<Record<string, string>>) ??
              (specialistAr?.actions as Array<Record<string, string>>) ??
              []
            );

            const recommendations = (analysis.recommendations ?? []).filter(Boolean);

            const summary = (
              (farmerAr?.summary as string) ??
              (specialistAr?.summary as string) ??
              ''
            );

            const statusLabel = (
              (farmerAr?.status_label as string) ??
              (specialistAr?.status_label as string) ??
              ''
            );

            const hasContent = observations.length > 0 || recommendations.length > 0 || summary || actions.length > 0;

            if (!hasContent) return null;

            return (
              <div className="bg-gray-800 rounded-lg p-3 space-y-3">
                {statusLabel && (
                  <span className="inline-block px-2 py-0.5 rounded-full text-xs font-bold bg-yellow-900/40 text-yellow-300 border border-yellow-700/50">
                    {statusLabel}
                  </span>
                )}
                {summary && (
                  <p className="text-white text-sm leading-relaxed">{summary}</p>
                )}
                {observations.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-white mb-2">الملاحظات</p>
                    {observations.map((s, i) => (
                      <p key={i} className="text-gray-200 text-xs mb-1.5 flex gap-2">
                        <span className="text-green-400 mt-0.5">{'\u2022'}</span>
                        <span>{s}</span>
                      </p>
                    ))}
                  </div>
                )}
                {actions.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-white mb-2">الإجراءات</p>
                    {actions.map((a, i) => (
                      <p key={i} className="text-gray-200 text-xs mb-1.5 flex gap-2">
                        <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${a.priority === 'urgent' ? 'bg-red-900/40 text-red-300' : a.priority === 'this_week' ? 'bg-yellow-900/40 text-yellow-300' : 'bg-blue-900/40 text-blue-300'}`}>
                          {a.priority === 'urgent' ? 'عاجل' : a.priority === 'this_week' ? 'هذا الأسبوع' : 'هذا الشهر'}
                        </span>
                        <span>{a.text}</span>
                      </p>
                    ))}
                  </div>
                )}
                {recommendations.length > 0 && actions.length === 0 && (
                  <div>
                    <p className="text-sm font-medium text-white mb-2">التوصيات</p>
                    {recommendations.map((r, i) => (
                      <p key={i} className="text-gray-200 text-xs mb-1.5 flex gap-2">
                        <span className="text-green-400 mt-0.5">{'\u2022'}</span>
                        <span>{r}</span>
                      </p>
                    ))}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-gray-700 bg-gray-900 flex-shrink-0">
        <p className="text-xs text-center text-gray-300">
          {'\u062A\u062D\u0644\u064A\u0644 \u0630\u0643\u0627\u0621 \u0627\u0635\u0637\u0646\u0627\u0639\u064A \u0632\u0631\u0627\u0639\u064A'} {'\u00B7'} Claude Sonnet via OpenRouter
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
  const [analysisResult, setAnalysisResult] = useState<FieldAnalysisResponse | null>(null);
  const [analysisImagery, setAnalysisImagery] = useState<ImageryPayload | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

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
      setAnalysisImagery(null);
      setAnalysisError(null);
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
    setAnalysisImagery(null);

    // Phase 1: Fetch field AI data (CDSE + OpenWeather + OpenMeteo)
    setLoadingStep('fetching');
    let aiData: unknown;
    try {
      // Extract lat/lng from field centroid (GeoJSON: coordinates=[lng, lat])
      const fieldLat = field.centroid?.coordinates?.[1] ?? (field as unknown as Record<string, number>).lat ?? 0;
      const fieldLng = field.centroid?.coordinates?.[0] ?? (field as unknown as Record<string, number>).lng ?? 0;
      const res = await fetch(`/api/field-ai-data?fieldId=${field.id}&indice=${indice}&lat=${fieldLat}&lng=${fieldLng}`);
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
      // Extract imagery from Phase 1 response if available
      const rawData = aiData as Record<string, unknown>;
      if (rawData?.imagery) {
        setAnalysisImagery(rawData.imagery as ImageryPayload);
      }
    } catch (err) {
      setLoadingStep('idle');
      setAnalysisError(err instanceof Error ? err.message : 'فشل جلب بيانات الحقل');
      return;
    }

    // Phase 2: multi-agent AI analysis
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
      const result = json as FieldAnalysisResponse;
      // Merge imagery from Phase 2 response if present
      if (result.imagery) {
        setAnalysisImagery(result.imagery);
      }
      setAnalysisResult(result);
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
    setAnalysisImagery(null);
    setClickedField(null);
    setSelectedIndice(null);
    setLoadingStep('idle');
    setAnalysisError(null);
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
  // Fallback: derive center from field polygon bbox after fields load.
  const farmCenter = useMemo(() => {
    if (!selectedFarm) return null;
    const lat = selectedFarm.centerLat ?? selectedFarm.coordinates?.lat;
    const lng = selectedFarm.centerLng ?? selectedFarm.coordinates?.lng;
    if (lat != null && lng != null) {
      return { lat: Number(lat), lng: Number(lng), zoom: selectedFarm.zoom ?? 14 };
    }
    if (farmBbox) {
      return {
        lat: (farmBbox.north + farmBbox.south) / 2,
        lng: (farmBbox.east + farmBbox.west) / 2,
        zoom: 14,
        bbox: farmBbox,
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
  const showSidePanel = !!clickedField && (isAnalyzing || hasResult || !!analysisError);

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
                  farmBbox={farmBbox ?? null}
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

            {/* ── Layer switcher — full-width bottom bar ── */}
            {!fieldsLoading && (
              <div className="absolute bottom-0 left-0 right-0 z-[1001]">
                <SatelliteLayerSwitcher
                  activeLayerId={activeLayerId}
                  onLayerChange={setActiveLayerId}
                  activeDate={activeDate}
                />
              </div>
            )}

            {/* ── Click-a-field hint ── */}
            {!fieldsLoading && !clickedField && !isAnalyzing && !hasResult && farmFields.length > 0 && (
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

                {/* Results */}
                {hasResult && analysisResult && clickedField && (
                  <AnalysisPanel
                    analysis={analysisResult}
                    imagery={analysisImagery}
                    field={clickedField}
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
