'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  Satellite,
  Leaf,
  Droplets,
  FlaskConical,
  Bug,
  Calendar,
  AlertTriangle,
  Thermometer,
  Wind,
  CloudRain,
  SprayCan,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  MapPin,
  Target,
  Wheat,
} from 'lucide-react';
import {
  useSatelliteMonitorField,
  useSatelliteMonitorTimeSeries,
  useSatelliteMonitorWeather,
  useSatelliteMonitorZones,
  useSatelliteMonitorDirectionGrid,
  useSatelliteMonitorSoilAnalysis,
  useSatelliteMonitorPestPredictions,
  useSatelliteMonitorIrrigationSchedule,
  useSatelliteMonitorYieldPrediction,
  useSatelliteMonitorHistorical,
  useUpdateField,
} from '@/features/satellite-monitor';
import { MAP_LAYERS } from '@/features/satellite-monitor/api';
import type { MapLayerType, TimePeriod, CropHealthStatus, NutrientLevel } from '@/features/satellite-monitor';
import { useAuth } from '@/stores/auth.store';
import {
  CropHistoryTimeline,
  type CropHistoryEntry,
} from '@/features/fields/components/CropHistoryTimeline';
import {
  FieldAlertsLinkCard,
  type FieldAlertsMetadata,
} from '@/features/fields/components/FieldAlertsLinkCard';
import { StartCropSeasonModal } from '@/features/fields/components/StartCropSeasonModal';
import {
  useStartCropSeason,
  useRecordFieldOperation,
  useCropSeasonsByField,
} from '@/features/fields/hooks/useCropSeasons';

const HEALTH_CONFIG: Record<CropHealthStatus, { color: string; bg: string; labelAr: string }> = {
  healthy: { color: 'text-green-700', bg: 'bg-green-100', labelAr: 'صحي' },
  moderate: { color: 'text-yellow-700', bg: 'bg-yellow-100', labelAr: 'متوسط' },
  stressed: { color: 'text-orange-700', bg: 'bg-orange-100', labelAr: 'مجهد' },
  critical: { color: 'text-red-700', bg: 'bg-red-100', labelAr: 'حرج' },
};

const NUTRIENT_CONFIG: Record<NutrientLevel, { color: string; bg: string; labelAr: string }> = {
  optimal: { color: 'text-green-700', bg: 'bg-green-100', labelAr: 'مثالي' },
  adequate: { color: 'text-blue-700', bg: 'bg-blue-100', labelAr: 'كافٍ' },
  low: { color: 'text-yellow-700', bg: 'bg-yellow-100', labelAr: 'منخفض' },
  deficient: { color: 'text-red-700', bg: 'bg-red-100', labelAr: 'ناقص' },
  excess: { color: 'text-purple-700', bg: 'bg-purple-100', labelAr: 'زائد' },
};

type Tab = 'overview' | 'soil' | 'irrigation' | 'pests' | 'yield' | 'historical';

export default function FieldDetailClient({ fieldId }: { fieldId: string }) {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [timeSeriesPeriod] = useState<TimePeriod>('90d');
  const [historicalLayer, setHistoricalLayer] = useState<MapLayerType>('ndvi');
  const [historicalStartDate, setHistoricalStartDate] = useState('2017-01-01');
  const [historicalEndDate, setHistoricalEndDate] = useState('2026-03-27');

  const { data: field, isLoading } = useSatelliteMonitorField(fieldId);
  // Auth identity (used by FieldAlertsLinkCard to show "alerts go to Y").
  const { user } = useAuth();
  // Mutation for PATCHing field metadata when the user toggles alerts
  // or edits the per-field phone override. The mutation only touches
  // `metadata` so we avoid clobbering other server-owned columns.
  const updateField = useUpdateField();
  const handleAlertsChange = (next: FieldAlertsMetadata) => {
    if (!field) return;
    const mergedMetadata = {
      ...(field.metadata ?? {}),
      alerts: next,
    };
    updateField.mutate({
      fieldId,
      data: { metadata: mergedMetadata },
    });
  };

  // ── Stage-2 "Start Crop Season" state ────────────────────────────────
  const [seasonModalOpen, setSeasonModalOpen] = useState(false);

  // Load crop seasons from the first-class backend table (falls back to
  // the legacy `field.metadata.cropHistory[]` shape below when the
  // backend has no rows yet, preserving history from pre-migration
  // fields).
  const { data: cropSeasonsData } = useCropSeasonsByField(fieldId);
  const startCropSeason = useStartCropSeason(fieldId);
  const recordOperation = useRecordFieldOperation(fieldId);

  /**
   * Start a new crop season on this field via the real API.
   *
   * The backend transactionally closes any previously active season, so
   * the client no longer has to orchestrate "mark old as isCurrent=false".
   * After the season is created we fire-and-forget record the plowing
   * and land-preparation operations (if the user filled them in the
   * modal), linked to the new cropSeasonId so the rollup endpoint can
   * compute totals by season.
   */
  const handleStartSeason = async (newEntry: CropHistoryEntry) => {
    if (!field) return;
    try {
      const created = await startCropSeason.mutateAsync({
        cropType: newEntry.cropType,
        cropTypeAr: newEntry.cropTypeAr,
        season: newEntry.season as
          | 'winter'
          | 'spring'
          | 'summer'
          | 'autumn'
          | 'year-round'
          | undefined,
        sowingDate: newEntry.startDate,
        expectedHarvestDate: newEntry.estimatedHarvestDate,
        seedVariety: newEntry.seedVariety,
        seedVarietyAr: newEntry.seedVarietyAr,
        plantingDensityKgHa: newEntry.plantingDensityKgHa,
        irrigationType: newEntry.irrigationType,
        notes: newEntry.notes,
      });

      // Record plowing as a FieldOperation if the modal captured it.
      if (newEntry.plowingDate) {
        try {
          await recordOperation.mutateAsync({
            operationType: 'plowing',
            performedAt: newEntry.plowingDate,
            durationHours: newEntry.plowingDurationHours,
            costAmount: newEntry.plowingCost,
            costCurrency: 'SAR',
            cropSeasonId: created.id,
            equipmentId: newEntry.plowingEquipmentId,
            equipmentName: newEntry.plowingEquipmentName,
            equipmentNameAr: newEntry.plowingEquipmentNameAr,
          });
        } catch (err) {
          // Non-fatal: the season is already created; surface in console
          // for debugging but don't block the modal from closing.
          // eslint-disable-next-line no-console
          console.error('Failed to record plowing operation', err);
        }
      }

      // Record land preparation as a FieldOperation if captured.
      if (newEntry.landPreparationDate) {
        try {
          await recordOperation.mutateAsync({
            operationType: 'land_preparation',
            performedAt: newEntry.landPreparationDate,
            durationHours: newEntry.landPreparationDurationHours,
            costAmount: newEntry.landPreparationCost,
            costCurrency: 'SAR',
            cropSeasonId: created.id,
            equipmentId: newEntry.landPreparationEquipmentId,
            equipmentName: newEntry.landPreparationEquipmentName,
            equipmentNameAr: newEntry.landPreparationEquipmentNameAr,
          });
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Failed to record land-preparation operation', err);
        }
      }

      setSeasonModalOpen(false);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to start crop season', err);
    }
  };

  /**
   * True when the field already has an active (unclosed) crop season.
   * Preference order:
   *   1. Real backend row from `useCropSeasonsByField`.
   *   2. Legacy `field.metadata.cropHistory[]` fallback so fields
   *      created before the migration still render correctly.
   */
  const hasActiveSeason: boolean = (() => {
    const backendRows = cropSeasonsData?.items ?? [];
    if (backendRows.some((r) => r.isCurrent)) return true;
    const raw = (field?.metadata as Record<string, unknown> | undefined)
      ?.cropHistory;
    if (!Array.isArray(raw)) return false;
    return raw.some(
      (e) =>
        e &&
        typeof e === 'object' &&
        (e as Record<string, unknown>).isCurrent === true &&
        !(e as Record<string, unknown>).endDate,
    );
  })();
  const { data: timeSeries = [] } = useSatelliteMonitorTimeSeries(fieldId, timeSeriesPeriod);
  const { data: weather = [] } = useSatelliteMonitorWeather(fieldId);
  const { data: zones = [] } = useSatelliteMonitorZones(fieldId);
  const { data: directionGrid } = useSatelliteMonitorDirectionGrid(fieldId, 'ndvi');
  const { data: soilAnalysis } = useSatelliteMonitorSoilAnalysis(fieldId);
  const { data: pestPredictions = [] } = useSatelliteMonitorPestPredictions(fieldId);
  const { data: irrigationSchedule } = useSatelliteMonitorIrrigationSchedule(fieldId);
  const { data: yieldPrediction } = useSatelliteMonitorYieldPrediction(fieldId);
  const { data: historicalData = [] } = useSatelliteMonitorHistorical(fieldId, historicalLayer, historicalStartDate, historicalEndDate);

  if (isLoading || !field) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
      </div>
    );
  }

  const health = HEALTH_CONFIG[field.healthStatus];

  const TABS: Array<{ key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }> = [
    { key: 'overview', label: 'نظرة عامة', icon: BarChart3 },
    { key: 'soil', label: 'تحليل التربة الذكي', icon: FlaskConical },
    { key: 'irrigation', label: 'إدارة الري', icon: Droplets },
    { key: 'pests', label: 'الآفات والأمراض', icon: Bug },
    { key: 'yield', label: 'توقع الإنتاجية', icon: Wheat },
    { key: 'historical', label: 'البيانات التاريخية', icon: Calendar },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/satellite-monitor" className="hover:text-green-600">مراقبة الأقمار الصناعية</Link>
        <ArrowRight className="w-3 h-3" />
        <span className="text-gray-900 font-medium">{field.nameAr}</span>
      </div>

      {/* Field Header */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{field.nameAr}</h1>
            <p className="text-gray-500 text-sm">{field.name}</p>
            <div className="flex flex-wrap items-center gap-4 mt-3 text-sm">
              <span className="flex items-center gap-1 text-gray-600">
                <Leaf className="w-4 h-4" /> {field.cropTypeAr} - {field.growthStageAr}
              </span>
              <span className="flex items-center gap-1 text-gray-600">
                <MapPin className="w-4 h-4" /> {field.area} هكتار
              </span>
              <span className="flex items-center gap-1 text-gray-600">
                <Satellite className="w-4 h-4" /> {field.satelliteSource} - {field.lastImageDate}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${health.color} ${health.bg}`}>
              {health.labelAr} ({field.healthScore}%)
            </span>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">{field.ndvi.toFixed(2)}</div>
              <div className="text-xs text-gray-500">NDVI</div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mt-6 pt-4 border-t">
          <QuickStat label="NDVI" value={field.ndvi.toFixed(2)} change={field.ndviChange} />
          <QuickStat label="NDWI" value={field.ndwi.toFixed(2)} />
          <QuickStat label="EVI" value={field.evi.toFixed(2)} />
          <QuickStat label="رطوبة التربة" value={`${field.soilMoisture}%`} />
          <QuickStat label="الإجهاد المائي" value={`${field.waterStressLevel}%`} alert={field.waterStressLevel > 50} />
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="flex border-b overflow-x-auto">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === key
                  ? 'border-green-600 text-green-700 bg-green-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* ========= OVERVIEW TAB ========= */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/*
                Crop history archive + alerts binding — both read from
                Field.metadata JSONB (no backend migration required).
                Stacks as two columns on wide screens and a single
                column on mobile.
              */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <CropHistoryTimeline
                  currentCropType={field.cropType}
                  currentCropTypeAr={field.cropTypeAr}
                  fieldCreatedAt={field.createdAt}
                  metadata={field.metadata}
                  onStartSeason={() => setSeasonModalOpen(true)}
                />
                <FieldAlertsLinkCard
                  user={user}
                  metadata={field.metadata}
                  onChange={handleAlertsChange}
                />
              </div>

              {/* Zone Analysis */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">تحليل المناطق</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {zones.map((zone) => {
                    const zh = HEALTH_CONFIG[zone.healthStatus];
                    return (
                      <div key={zone.id} className={`p-3 rounded-lg border ${zh.bg}`}>
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-medium text-sm">{zone.zoneNameAr}</span>
                          <span className={`text-lg font-bold ${zh.color}`}>{zone.ndvi.toFixed(2)}</span>
                        </div>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${zh.color} ${zh.bg}`}>{zh.labelAr}</span>
                        <p className="text-xs text-gray-600 mt-2">{zone.recommendationAr}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 9-Direction Grid */}
              {directionGrid && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">شبكة الاتجاهات التسعة</h3>
                  <div className="grid grid-cols-3 gap-2 max-w-sm mx-auto">
                    {(['NW', 'N', 'NE', 'W', 'C', 'E', 'SW', 'S', 'SE'] as const).map((zone) => {
                      const zd = directionGrid.zones.find((z) => z.zone === zone);
                      if (!zd) return <div key={zone} className="p-2 bg-gray-50 rounded" />;
                      const zh = HEALTH_CONFIG[zd.healthStatus];
                      return (
                        <div key={zone} className={`p-2 rounded-lg border text-center ${zh.bg}`} title={zd.recommendationAr}>
                          <div className="text-[10px] text-gray-500">{zd.labelAr}</div>
                          <div className={`text-sm font-bold ${zh.color}`}>{zd.ndvi.toFixed(2)}</div>
                          {zd.irrigationNeeded && <Droplets className="w-3 h-3 text-blue-500 mx-auto" />}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Time Series */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">المسار الزمني NDVI</h3>
                <div className="flex items-end gap-1 h-32">
                  {timeSeries.map((p, i) => {
                    const h = Math.max(p.ndvi * 100, 5);
                    const c = p.ndvi >= 0.6 ? 'bg-green-500' : p.ndvi >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center">
                        <span className="text-[8px] text-gray-400">{p.ndvi.toFixed(2)}</span>
                        <div className={`w-full rounded-t ${c}`} style={{ height: `${h}%` }} />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Alerts */}
              {field.alerts.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">التنبيهات النشطة ({field.alerts.length})</h3>
                  <div className="space-y-2">
                    {field.alerts.map((alert) => (
                      <div key={alert.id} className="p-3 rounded-lg border bg-orange-50 border-orange-200">
                        <div className="flex items-center gap-2 mb-1">
                          <AlertTriangle className="w-4 h-4 text-orange-600" />
                          <span className="font-medium text-sm">{alert.titleAr}</span>
                        </div>
                        <p className="text-xs text-gray-600">{alert.descriptionAr}</p>
                        <p className="text-xs text-green-700 mt-1 font-medium">{alert.recommendationAr}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ========= SOIL ANALYSIS TAB (AI) ========= */}
          {activeTab === 'soil' && soilAnalysis && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-gray-900">تحليل التربة الذكي - AI</h3>
                <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full">AI</span>
              </div>

              {/* Nutrient Levels */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">مستويات العناصر الغذائية</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {soilAnalysis.nutrients.map((nutrient) => {
                    const nc = NUTRIENT_CONFIG[nutrient.level];
                    const pct = Math.min((nutrient.value / nutrient.optimalRange.max) * 100, 120);
                    return (
                      <div key={nutrient.symbol} className="p-4 rounded-lg border">
                        <div className="flex justify-between items-center mb-2">
                          <div>
                            <span className="font-bold text-lg text-gray-900">{nutrient.symbol}</span>
                            <span className="text-xs text-gray-500 mr-2">{nutrient.nameAr}</span>
                          </div>
                          <span className={`px-2 py-0.5 text-xs rounded-full ${nc.color} ${nc.bg}`}>{nc.labelAr}</span>
                        </div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-bold">{nutrient.value} {nutrient.unit}</span>
                          <span className="text-[10px] text-gray-400">
                            (المثالي: {nutrient.optimalRange.min}-{nutrient.optimalRange.max})
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 relative">
                          <div
                            className={`h-2 rounded-full ${nutrient.level === 'optimal' || nutrient.level === 'adequate' ? 'bg-green-500' : nutrient.level === 'low' ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${Math.min(pct, 100)}%` }}
                          />
                          {/* Optimal range indicator */}
                          <div
                            className="absolute top-0 h-2 border-l-2 border-r-2 border-green-600 opacity-30"
                            style={{
                              left: `${(nutrient.optimalRange.min / nutrient.optimalRange.max) * 100}%`,
                              width: `${100 - (nutrient.optimalRange.min / nutrient.optimalRange.max) * 100}%`,
                            }}
                          />
                        </div>
                        {nutrient.level !== 'optimal' && nutrient.level !== 'adequate' && (
                          <p className="text-xs text-amber-700 mt-2 bg-amber-50 p-1.5 rounded">{nutrient.recommendationAr}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* pH, Salinity, SOC */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg border">
                  <div className="text-xs text-gray-500 mb-1">درجة الحموضة (pH)</div>
                  <div className="text-2xl font-bold">{soilAnalysis.ph.value}</div>
                  <span className={`text-xs ${NUTRIENT_CONFIG[soilAnalysis.ph.level].color}`}>
                    المثالي: {soilAnalysis.ph.optimal.min} - {soilAnalysis.ph.optimal.max}
                  </span>
                </div>
                <div className="p-4 rounded-lg border">
                  <div className="text-xs text-gray-500 mb-1">الملوحة</div>
                  <div className="text-2xl font-bold">{soilAnalysis.salinity.value} <span className="text-sm">{soilAnalysis.salinity.unit}</span></div>
                  <span className={`text-xs ${NUTRIENT_CONFIG[soilAnalysis.salinity.level].color}`}>
                    {NUTRIENT_CONFIG[soilAnalysis.salinity.level].labelAr}
                  </span>
                </div>
                <div className="p-4 rounded-lg border">
                  <div className="text-xs text-gray-500 mb-1">الكربون العضوي (SOC)</div>
                  <div className="text-2xl font-bold">{soilAnalysis.organicCarbon.value}<span className="text-sm">{soilAnalysis.organicCarbon.unit}</span></div>
                  <span className={`text-xs ${NUTRIENT_CONFIG[soilAnalysis.organicCarbon.level].color}`}>
                    {NUTRIENT_CONFIG[soilAnalysis.organicCarbon.level].labelAr}
                  </span>
                </div>
              </div>

              {/* Fertilizer Recommendations */}
              {soilAnalysis.fertilizerRecommendations.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">توصيات التسميد</h4>
                  <div className="space-y-2">
                    {soilAnalysis.fertilizerRecommendations.map((rec, i) => (
                      <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-200">
                        <div>
                          <span className="font-medium text-green-800">{rec.productAr}</span>
                          <span className="text-sm text-gray-600 mr-2">- {rec.quantity} {rec.unit}</span>
                        </div>
                        <span className="text-xs text-green-700 bg-green-100 px-2 py-1 rounded">{rec.timingAr}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ========= IRRIGATION TAB ========= */}
          {activeTab === 'irrigation' && irrigationSchedule && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-2">
                <Droplets className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-gray-900">إدارة الري الذكية - AI</h3>
              </div>

              {/* Next Irrigation */}
              <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-blue-800">الري القادم</h4>
                  <span className="text-lg font-bold text-blue-700">
                    {new Date(irrigationSchedule.nextIrrigation).toLocaleDateString('ar-SA', { weekday: 'long', month: 'short', day: 'numeric' })}
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-xs text-gray-500">الكمية</div>
                    <div className="font-bold text-blue-700">{irrigationSchedule.amountMm} مم</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">المدة</div>
                    <div className="font-bold">{irrigationSchedule.durationHours} ساعات</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">النتح التبخري</div>
                    <div className="font-bold">{irrigationSchedule.factors.evapotranspiration} مم/يوم</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">رطوبة التربة الحالية</div>
                    <div className="font-bold">{irrigationSchedule.factors.soilMoisture}%</div>
                  </div>
                </div>
              </div>

              {/* Factors */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">عوامل الحساب</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-lg border text-center">
                    <Thermometer className="w-5 h-5 text-red-500 mx-auto mb-1" />
                    <div className="text-xs text-gray-500">الحرارة</div>
                    <div className="font-bold">{irrigationSchedule.factors.weatherData.temp}°C</div>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <Droplets className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                    <div className="text-xs text-gray-500">الرطوبة</div>
                    <div className="font-bold">{irrigationSchedule.factors.weatherData.humidity}%</div>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <Wind className="w-5 h-5 text-gray-500 mx-auto mb-1" />
                    <div className="text-xs text-gray-500">الرياح</div>
                    <div className="font-bold">{irrigationSchedule.factors.weatherData.windSpeed} كم/س</div>
                  </div>
                  <div className="p-3 rounded-lg border text-center">
                    <Leaf className="w-5 h-5 text-green-500 mx-auto mb-1" />
                    <div className="text-xs text-gray-500">حاجة المحصول</div>
                    <div className="font-bold">{irrigationSchedule.factors.cropWaterNeed} مم</div>
                  </div>
                </div>
              </div>

              {/* Zone Priorities */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">أولويات المناطق</h4>
                <div className="grid grid-cols-3 gap-2 max-w-sm mx-auto">
                  {irrigationSchedule.zones.map((z) => (
                    <div
                      key={z.zone}
                      className={`p-2 rounded-lg text-center text-sm ${
                        z.priority === 'urgent' ? 'bg-red-100 border-red-300 border' :
                        z.priority === 'skip' ? 'bg-gray-100 border-gray-200 border' :
                        'bg-blue-50 border-blue-200 border'
                      }`}
                    >
                      <div className="text-xs text-gray-500">{z.zone}</div>
                      <div className="font-bold">{z.amountMm} مم</div>
                      <div className={`text-[10px] font-medium ${
                        z.priority === 'urgent' ? 'text-red-700' :
                        z.priority === 'skip' ? 'text-gray-500' :
                        'text-blue-700'
                      }`}>
                        {z.priority === 'urgent' ? 'عاجل' : z.priority === 'skip' ? 'تخطي' : 'عادي'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Weather */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">توقعات الطقس ونوافذ الرش</h4>
                <div className="grid grid-cols-7 gap-2">
                  {weather.slice(0, 7).map((day) => (
                    <div key={day.date} className="p-2 rounded-lg border text-center text-xs">
                      <div className="text-gray-500">{new Date(day.date).toLocaleDateString('ar-SA', { weekday: 'short' })}</div>
                      <div className="text-lg my-1">{day.condition === 'sunny' ? '☀️' : day.condition === 'rainy' ? '🌧️' : '⛅'}</div>
                      <div className="font-medium">{day.tempMax}°</div>
                      <div className="text-gray-400">{day.tempMin}°</div>
                      {day.sprayWindow ? (
                        <SprayCan className="w-3 h-3 text-green-500 mx-auto mt-1" />
                      ) : (
                        <CloudRain className="w-3 h-3 text-red-400 mx-auto mt-1" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ========= PESTS TAB ========= */}
          {activeTab === 'pests' && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-2">
                <Bug className="w-5 h-5 text-red-600" />
                <h3 className="font-semibold text-gray-900">التنبؤ بالآفات والأمراض - AI</h3>
              </div>

              {pestPredictions.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <Bug className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>لا توجد تنبؤات بآفات حالياً</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {pestPredictions.map((pred) => (
                    <div key={pred.id} className={`p-4 rounded-lg border ${
                      pred.riskLevel === 'critical' ? 'bg-red-50 border-red-200' :
                      pred.riskLevel === 'warning' ? 'bg-orange-50 border-orange-200' :
                      'bg-yellow-50 border-yellow-200'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{pred.pestNameAr}</span>
                          <span className="text-xs text-gray-500">({pred.pestName})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${pred.probability > 50 ? 'bg-red-500' : pred.probability > 25 ? 'bg-orange-500' : 'bg-yellow-500'}`}
                              style={{ width: `${pred.probability}%` }}
                            />
                          </div>
                          <span className="text-sm font-bold">{pred.probability}%</span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 mb-2">
                        المصدر: {pred.detectionSource === 'satellite' ? 'صور الأقمار الصناعية' :
                          pred.detectionSource === 'weather_pattern' ? 'أنماط الطقس' :
                          pred.detectionSource === 'ndvi_anomaly' ? 'شذوذ NDVI' : 'بيانات تاريخية'}
                        {' | '}التاريخ المتوقع: {pred.estimatedDate}
                      </div>
                      <div className="p-2 bg-white/60 rounded text-sm">
                        <span className="font-medium text-gray-700">الإجراء الوقائي: </span>
                        {pred.preventiveActionAr}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ========= YIELD TAB ========= */}
          {activeTab === 'yield' && yieldPrediction && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-2">
                <Wheat className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-gray-900">توقع الإنتاجية والحصاد - AI</h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg border text-center">
                  <div className="text-xs text-gray-500 mb-1">ارتفاع المحصول المتوقع</div>
                  <div className="text-3xl font-bold text-green-700">{yieldPrediction.predictedHeight}</div>
                  <div className="text-sm text-gray-500">{yieldPrediction.heightUnit}</div>
                </div>
                <div className="p-4 rounded-lg border text-center">
                  <div className="text-xs text-gray-500 mb-1">العائد المتوقع / هكتار</div>
                  <div className="text-3xl font-bold text-amber-700">{yieldPrediction.yieldPerHectare}</div>
                  <div className="text-sm text-gray-500">طن/هكتار</div>
                </div>
                <div className="p-4 rounded-lg border text-center">
                  <div className="text-xs text-gray-500 mb-1">الإنتاج الكلي المتوقع</div>
                  <div className="text-3xl font-bold text-blue-700">{yieldPrediction.expectedYield.toFixed(1)}</div>
                  <div className="text-sm text-gray-500">{yieldPrediction.yieldUnit}</div>
                </div>
                <div className="p-4 rounded-lg border text-center">
                  <div className="text-xs text-gray-500 mb-1">موعد الحصاد المخطط</div>
                  <div className="text-xl font-bold text-purple-700">
                    {new Date(yieldPrediction.plannedHarvestDate).toLocaleDateString('ar-SA', { month: 'long', day: 'numeric' })}
                  </div>
                  <div className="text-sm text-gray-500">{yieldPrediction.plannedHarvestDate}</div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 border">
                <div>
                  <span className="text-sm text-gray-600">دقة التنبؤ: </span>
                  <span className="font-bold text-lg">{yieldPrediction.confidencePercent}%</span>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  yieldPrediction.trend === 'above_average' ? 'bg-green-100 text-green-700' :
                  yieldPrediction.trend === 'below_average' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {yieldPrediction.trend === 'above_average' ? 'فوق المتوسط' :
                   yieldPrediction.trend === 'below_average' ? 'تحت المتوسط' : 'متوسط'}
                </span>
              </div>
            </div>
          )}

          {/* ========= HISTORICAL TAB ========= */}
          {activeTab === 'historical' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-semibold text-gray-900">البيانات التاريخية منذ 2017</h3>
                </div>
                <p className="text-xs text-gray-400">Historical Data & Timelapse</p>
              </div>

              {/* Date Range + Layer Selector */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">من تاريخ (From)</label>
                  <input
                    type="date"
                    value={historicalStartDate}
                    min="2017-01-01"
                    onChange={(e) => setHistoricalStartDate(e.target.value)}
                    className="w-full px-3 py-1.5 border rounded text-sm focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">إلى تاريخ (To)</label>
                  <input
                    type="date"
                    value={historicalEndDate}
                    onChange={(e) => setHistoricalEndDate(e.target.value)}
                    className="w-full px-3 py-1.5 border rounded text-sm focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">المؤشر (Index)</label>
                  <select
                    value={historicalLayer}
                    onChange={(e) => setHistoricalLayer(e.target.value as MapLayerType)}
                    className="w-full px-3 py-1.5 border rounded text-sm focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="ndvi">NDVI - مؤشر الغطاء النباتي</option>
                    <option value="ndre">NDRE - الحافة الحمراء</option>
                    <option value="ndwi">NDWI - نقص المياه</option>
                    <option value="evi">EVI - الغطاء المحسن</option>
                    <option value="savi">SAVI - معدل للتربة</option>
                    <option value="ndmi">NDMI - رطوبة التربة</option>
                    <option value="sar_rvi">SAR RVI - رادار (عبر السحب)</option>
                  </select>
                </div>
              </div>

              {/* Quick Date Presets */}
              <div className="flex flex-wrap gap-2">
                {[
                  { label: 'هذا الموسم', from: '2025-10-01', to: '2026-03-27' },
                  { label: 'الموسم الماضي', from: '2024-10-01', to: '2025-06-01' },
                  { label: 'سنة كاملة', from: '2025-03-27', to: '2026-03-27' },
                  { label: 'منذ 2017', from: '2017-01-01', to: '2026-03-27' },
                ].map((preset) => (
                  <button
                    key={preset.label}
                    onClick={() => { setHistoricalStartDate(preset.from); setHistoricalEndDate(preset.to); }}
                    className="px-3 py-1 text-xs rounded-full border border-indigo-200 text-indigo-700 hover:bg-indigo-100"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>

              {historicalData.length > 0 ? (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">المسار الزمني - {MAP_LAYERS.find(l => l.type === historicalLayer)?.labelAr}</h4>
                  <div className="flex items-end gap-1 h-40">
                    {historicalData.map((snap, idx) => {
                      const h = Math.max(snap.averageValue * 100, 5);
                      const c = snap.averageValue >= 0.6 ? 'bg-green-500' : snap.averageValue >= 0.3 ? 'bg-yellow-500' : snap.averageValue >= 0.15 ? 'bg-orange-500' : 'bg-gray-300';
                      return (
                        <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                          <span className="text-[8px] text-gray-400">{snap.averageValue.toFixed(2)}</span>
                          <div className={`w-full rounded-t ${c}`} style={{ height: `${h}%` }} title={`${snap.date}: ${snap.averageValue.toFixed(2)}`} />
                          <span className="text-[7px] text-gray-400 whitespace-nowrap">{snap.date.slice(0, 7)}</span>
                        </div>
                      );
                    })}
                  </div>
                  <p className="text-xs text-gray-400 text-center mt-4">
                    يمكنك طلب بيانات تاريخية من 2017 لإنشاء فاصل زمني (Timelapse) ومقارنة المؤشرات
                  </p>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Calendar className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>لا توجد بيانات تاريخية متاحة</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/*
        Stage-2 "Start new crop season" modal — rendered at the root
        so it can overlay the whole detail view regardless of which
        tab is currently active.
      */}
      <StartCropSeasonModal
        open={seasonModalOpen}
        onClose={() => setSeasonModalOpen(false)}
        onSubmit={handleStartSeason}
        hasActiveSeason={hasActiveSeason}
        initialCropType={field.cropType}
      />
    </div>
  );
}

function QuickStat({ label, value, change, alert }: { label: string; value: string; change?: number; alert?: boolean }) {
  return (
    <div className={`p-3 rounded-lg ${alert ? 'bg-red-50' : 'bg-gray-50'}`}>
      <div className="text-xs text-gray-500">{label}</div>
      <div className={`text-lg font-bold ${alert ? 'text-red-600' : 'text-gray-900'}`}>
        {value}
        {change !== undefined && (
          <span className={`text-xs mr-1 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {change > 0 ? (
              <ArrowUpRight className="w-3 h-3 inline" />
            ) : change < 0 ? (
              <ArrowDownRight className="w-3 h-3 inline" />
            ) : null}
            {change > 0 ? '+' : ''}{change.toFixed(2)}
          </span>
        )}
      </div>
    </div>
  );
}
