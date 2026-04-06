'use client';

/**
 * Terrain Analysis Client Component
 * مكون تحليل التضاريس
 */

import React, { useState } from 'react';
import {
  Mountain,
  CheckCircle,
  Clock,
  TrendingUp,
  Droplets,
  ArrowUpDown,
  Loader2,
  AlertTriangle,
  Play,
} from 'lucide-react';
import {
  useAnalyzeDEM,
  useAnalyzeSlope,
  useOptimizeLeveling,
  useAnalyzeDrainage,
} from '@/features/terrain/hooks/useTerrain';
import type { DEMAnalysis, SlopeAnalysis, LevelingPlan, DrainageAnalysis } from '@/features/terrain/types';

// ---------------------------------------------------------------------------
// Types & Static Data
// ---------------------------------------------------------------------------

const TABS = [
  { id: 'dem', label: 'تحليل DEM', icon: Mountain },
  { id: 'slope', label: 'الانحدار', icon: TrendingUp },
  { id: 'leveling', label: 'التسوية', icon: ArrowUpDown },
  { id: 'hydrology', label: 'الهيدرولوجيا', icon: Droplets },
] as const;

type TabId = (typeof TABS)[number]['id'];

const STAT_COLORS: Record<string, { bg: string; icon: string }> = {
  green: { bg: 'bg-green-100', icon: 'text-green-600' },
  yellow: { bg: 'bg-yellow-100', icon: 'text-yellow-600' },
  blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
  purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function TerrainClient() {
  const [activeTab, setActiveTab] = useState<TabId>('dem');
  const [fieldId, setFieldId] = useState('');

  // Mutations from terrain API hooks
  const analyzeDEM = useAnalyzeDEM();
  const analyzeSlope = useAnalyzeSlope();
  const optimizeLeveling = useOptimizeLeveling();
  const analyzeDrainage = useAnalyzeDrainage();
  // Results from mutations
  const demResult: DEMAnalysis | undefined = analyzeDEM.data;
  const slopeResult: SlopeAnalysis | undefined = analyzeSlope.data;
  const levelingResult: LevelingPlan | undefined = optimizeLeveling.data;
  const drainageResult: DrainageAnalysis | undefined = analyzeDrainage.data;

  const isAnyLoading =
    analyzeDEM.isPending || analyzeSlope.isPending || optimizeLeveling.isPending || analyzeDrainage.isPending;

  const handleRunAnalysis = () => {
    if (!fieldId.trim()) return;
    if (activeTab === 'dem') {
      analyzeDEM.mutate({ fieldId });
    } else if (activeTab === 'slope') {
      analyzeSlope.mutate(fieldId);
    } else if (activeTab === 'leveling') {
      optimizeLeveling.mutate({ fieldId });
    } else if (activeTab === 'hydrology') {
      analyzeDrainage.mutate(fieldId);
    }
  };

  const STATS = [
    { label: 'تحليلات DEM', value: demResult ? 1 : 0, icon: Mountain, color: 'green' },
    { label: 'تحليلات الانحدار', value: slopeResult ? 1 : 0, icon: TrendingUp, color: 'yellow' },
    { label: 'خطط التسوية', value: levelingResult ? 1 : 0, icon: ArrowUpDown, color: 'blue' },
    { label: 'تحليلات الصرف', value: drainageResult ? 1 : 0, icon: Droplets, color: 'purple' },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">تحليل التضاريس</h1>
        <p className="text-sm text-gray-500 mt-1">
          معالجة نموذج الارتفاع الرقمي وتحليل الانحدار وتحسين التسوية
        </p>
      </div>

      {/* Field ID Input & Run Button */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              معرّف الحقل (Field ID)
            </label>
            <input
              type="text"
              value={fieldId}
              onChange={(e) => setFieldId(e.target.value)}
              placeholder="أدخل معرّف الحقل لبدء التحليل..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
            />
          </div>
          <button
            onClick={handleRunAnalysis}
            disabled={!fieldId.trim() || isAnyLoading}
            className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isAnyLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            تشغيل التحليل
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS.map((s) => {
          const Icon = s.icon;
          const colors = (STAT_COLORS[s.color] ?? STAT_COLORS.blue)!;
          return (
            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${colors.icon}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{s.value}</p>
                  <p className="text-sm text-gray-500">{s.label}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-green-700 shadow-sm font-medium'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Error display for any mutation */}
      {(analyzeDEM.isError || analyzeSlope.isError || optimizeLeveling.isError || analyzeDrainage.isError) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              فشل في التحليل:{' '}
              {(analyzeDEM.error ?? analyzeSlope.error ?? optimizeLeveling.error ?? analyzeDrainage.error) instanceof Error
                ? (analyzeDEM.error ?? analyzeSlope.error ?? optimizeLeveling.error ?? analyzeDrainage.error)?.message
                : 'خطأ غير معروف'}
            </span>
          </div>
        </div>
      )}

      {/* DEM Tab */}
      {activeTab === 'dem' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          {analyzeDEM.isPending ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
              <p className="text-gray-600 font-medium">جاري تحليل نموذج الارتفاع الرقمي...</p>
              <p className="text-sm text-gray-400 mt-1">Processing DEM analysis...</p>
            </div>
          ) : demResult ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">نتائج تحليل DEM</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">أقل ارتفاع</p>
                  <p className="text-2xl font-bold text-gray-900">{demResult.minElevation} م</p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">أعلى ارتفاع</p>
                  <p className="text-2xl font-bold text-gray-900">{demResult.maxElevation} م</p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">متوسط الارتفاع</p>
                  <p className="text-2xl font-bold text-gray-900">{demResult.meanElevation} م</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>الدقة: {demResult.resolution} م | تم التحليل: {new Date(demResult.processedAt).toLocaleDateString('ar-SA')}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <Mountain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                تحليل نموذج الارتفاع الرقمي
              </h3>
              <p className="text-gray-500 text-sm mb-4">
                أدخل معرّف الحقل واضغط "تشغيل التحليل" لبدء معالجة DEM
              </p>
              <p className="text-xs text-gray-400">
                Enter a field ID and click "Run Analysis" to process DEM data
              </p>
            </div>
          )}
        </div>
      )}

      {/* Slope Tab */}
      {activeTab === 'slope' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          {analyzeSlope.isPending ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
              <p className="text-gray-600 font-medium">جاري تحليل الانحدار...</p>
              <p className="text-sm text-gray-400 mt-1">Processing slope analysis...</p>
            </div>
          ) : slopeResult ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">نتائج تحليل الانحدار</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">أقل انحدار</p>
                  <p className="text-2xl font-bold text-gray-900">{slopeResult.minSlope}%</p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">أعلى انحدار</p>
                  <p className="text-2xl font-bold text-gray-900">{slopeResult.maxSlope}%</p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">متوسط الانحدار</p>
                  <p className="text-2xl font-bold text-gray-900">{slopeResult.meanSlope}%</p>
                </div>
              </div>
              {slopeResult.slopeClasses && slopeResult.slopeClasses.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-700">فئات الانحدار:</h4>
                  {slopeResult.slopeClasses.map((cls) => (
                    <div key={cls.range} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">
                        {cls.rangeAr ?? cls.range}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-green-500"
                            style={{ width: `${cls.percentage}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700 w-12 text-left">
                          {cls.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">تحليل الانحدار</h3>
              <p className="text-gray-500 text-sm mb-4">
                أدخل معرّف الحقل واضغط "تشغيل التحليل" لبدء تحليل الانحدار
              </p>
              <p className="text-xs text-gray-400">
                Enter a field ID and click "Run Analysis" to process slope data
              </p>
            </div>
          )}
        </div>
      )}

      {/* Leveling Tab */}
      {activeTab === 'leveling' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          {optimizeLeveling.isPending ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
              <p className="text-gray-600 font-medium">جاري تحسين التسوية...</p>
              <p className="text-sm text-gray-400 mt-1">Optimizing leveling plan...</p>
            </div>
          ) : levelingResult ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">خطة التسوية المثلى</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">حجم القطع (م3)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {levelingResult.cutVolume.toLocaleString('ar-SA')}
                  </p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">حجم الردم (م3)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {levelingResult.fillVolume.toLocaleString('ar-SA')}
                  </p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">صافي الحجم (م3)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {levelingResult.netVolume.toLocaleString('ar-SA')}
                  </p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">الانحدار المثالي</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {levelingResult.optimalSlope}%
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>المدة المقدرة: {levelingResult.estimatedDuration} يوم</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <ArrowUpDown className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">تحسين التسوية</h3>
              <p className="text-gray-500 text-sm mb-4">
                أدخل معرّف الحقل واضغط "تشغيل التحليل" لحساب خطة التسوية المثلى
              </p>
              <p className="text-xs text-gray-400">
                Enter a field ID and click "Run Analysis" to calculate optimal leveling
              </p>
            </div>
          )}
        </div>
      )}

      {/* Hydrology Tab */}
      {activeTab === 'hydrology' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          {analyzeDrainage.isPending ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
              <p className="text-gray-600 font-medium">جاري تحليل الهيدرولوجيا والصرف...</p>
              <p className="text-sm text-gray-400 mt-1">Processing hydrology analysis...</p>
            </div>
          ) : drainageResult ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">نتائج تحليل الصرف</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">كثافة الصرف</p>
                  <p className="text-2xl font-bold text-gray-900">{drainageResult.drainageDensity}</p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">القنوات الرئيسية</p>
                  <p className="text-2xl font-bold text-gray-900">{drainageResult.mainChannels}</p>
                </div>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <p className="text-sm text-gray-500">مناطق مشكلة</p>
                  <p className="text-2xl font-bold text-red-600">{drainageResult.problemAreas.length}</p>
                </div>
              </div>
              {drainageResult.recommendationsAr && drainageResult.recommendationsAr.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">التوصيات:</h4>
                  <ul className="space-y-1">
                    {drainageResult.recommendationsAr.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Droplets className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                تحليل الهيدرولوجيا والصرف
              </h3>
              <p className="text-gray-500 text-sm mb-4">
                أدخل معرّف الحقل واضغط "تشغيل التحليل" لتحليل الصرف والمياه
              </p>
              <p className="text-xs text-gray-400">
                Enter a field ID and click "Run Analysis" for drainage and hydrology analysis
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
