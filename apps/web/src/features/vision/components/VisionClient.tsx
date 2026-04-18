'use client';

/**
 * SAHOOL AI Vision Detection Client
 * الكشف البصري بالذكاء الاصطناعي
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Eye,
  Upload,
  Bug,
  Leaf,
  AlertTriangle,
  Clock,
  Zap,
} from 'lucide-react';
import {
  useDetectPest,
  useDetectDisease,
  useDetectWeed,
  useVisionModels,
} from '../hooks/useVision';
import type { PestDetection, DiseaseDetection, WeedDetection } from '../types';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DetectionResult {
  id: string;
  imageId: string;
  fieldName: string;
  detectionType: 'pest' | 'disease' | 'weed';
  detectionTypeAr: string;
  label: string;
  labelAr: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  severityAr?: string;
  date?: string;
  status: 'new' | 'reviewed' | 'treated';
  statusAr: string;
  recommendation: string;
  recommendationAr: string;
}

// ---------------------------------------------------------------------------
// Helpers — map API responses to unified DetectionResult
// ---------------------------------------------------------------------------

const SEVERITY_LABELS_AR: Record<string, string> = {
  low: 'منخفض',
  medium: 'متوسط',
  high: 'عالي',
  critical: 'حرج',
};

/** Read the Arabic label from either backend snake_case or legacy camelCase. */
function pickLabelAr(
  d: { class_name_ar?: string; classAr?: string; speciesAr?: string; diseaseAr?: string },
): string {
  return d.class_name_ar || d.classAr || d.speciesAr || d.diseaseAr || 'غير معروف';
}

/** Read the English label from either backend snake_case or legacy camelCase. */
function pickLabelEn(
  d: { class_name_en?: string; class?: string; species?: string; disease?: string },
): string {
  return d.class_name_en || d.class || d.species || d.disease || 'Unknown';
}

function getDateStr(): string {
  // Mapping is now produced on the client; backend DetectionResponse uses
  // `timestamp` (ISO 8601) but it isn't needed for the list view date column.
  return new Date().toISOString().split('T')[0]!;
}

function mapPestDetection(data: PestDetection): DetectionResult[] {
  return data.detections.map((d, i) => ({
    id: `pest-${i}`,
    imageId: '-',
    fieldName: '-',
    detectionType: 'pest',
    detectionTypeAr: 'آفة',
    label: pickLabelEn(d),
    labelAr: pickLabelAr(d),
    confidence: d.confidence,
    severity: d.severity ?? 'medium',
    severityAr: SEVERITY_LABELS_AR[d.severity ?? 'medium'],
    date: getDateStr(),
    status: 'new',
    statusAr: 'جديد',
    recommendation: d.recommended_action_en ?? d.recommendation ?? '',
    recommendationAr: d.recommended_action_ar ?? d.recommendationAr ?? '',
  }));
}

function mapDiseaseDetection(data: DiseaseDetection): DetectionResult[] {
  return data.detections.map((d, i) => ({
    id: `disease-${i}`,
    imageId: '-',
    fieldName: '-',
    detectionType: 'disease',
    detectionTypeAr: 'مرض',
    label: pickLabelEn(d),
    labelAr: pickLabelAr(d),
    confidence: d.confidence,
    severity: d.severity ?? 'medium',
    severityAr: SEVERITY_LABELS_AR[d.severity ?? 'medium'],
    date: getDateStr(),
    status: 'new',
    statusAr: 'جديد',
    recommendation: d.recommended_treatment_en ?? d.treatment ?? '',
    recommendationAr: d.recommended_treatment_ar ?? d.treatmentAr ?? '',
  }));
}

function mapWeedDetection(data: WeedDetection): DetectionResult[] {
  const totalCoverage = data.total_coverage_percent ?? data.totalCoverage ?? 0;
  const severity: DetectionResult['severity'] =
    totalCoverage > 30 ? 'high' : totalCoverage > 10 ? 'medium' : 'low';
  return data.detections.map((d, i) => {
    const coverage = d.coverage_percent ?? d.coverage ?? 0;
    return {
      id: `weed-${i}`,
      imageId: '-',
      fieldName: '-',
      detectionType: 'weed',
      detectionTypeAr: 'حشائش',
      label: pickLabelEn(d),
      labelAr: pickLabelAr(d),
      confidence: d.confidence,
      severity,
      severityAr: SEVERITY_LABELS_AR[severity],
      date: getDateStr(),
      status: 'new',
      statusAr: 'جديد',
      recommendation: '',
      recommendationAr: `تغطية ${coverage.toFixed(1)}%`,
    };
  });
}

const severityColors: Record<string, string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

const typeIcons: Record<string, React.ReactNode> = {
  pest: <Bug className="w-4 h-4 text-red-500" />,
  disease: <Leaf className="w-4 h-4 text-orange-500" />,
  weed: <AlertTriangle className="w-4 h-4 text-yellow-500" />,
};

const statusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-700',
  reviewed: 'bg-purple-100 text-purple-700',
  treated: 'bg-green-100 text-green-700',
};

// ---------------------------------------------------------------------------
// Loading / Error UI
// ---------------------------------------------------------------------------

function LoadingSkeleton() {
  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex items-center gap-4 animate-pulse">
            <div className="w-10 h-10 bg-gray-200 rounded" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/3" />
              <div className="h-3 bg-gray-200 rounded w-1/4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function VisionClient() {
  const [filter, setFilter] = useState<'all' | 'pest' | 'disease' | 'weed'>('all');
  const [results, setResults] = useState<DetectionResult[]>([]);
  const [partialFailure, setPartialFailure] = useState<string | null>(null);

  // Mutation hooks for detection
  const pestMutation = useDetectPest();
  const diseaseMutation = useDetectDisease();
  const weedMutation = useDetectWeed();

  // Query hook for models (to show service status)
  const { data: models, isLoading: modelsLoading } = useVisionModels();

  const isProcessing = pestMutation.isPending || diseaseMutation.isPending || weedMutation.isPending;
  const hasError = pestMutation.isError || diseaseMutation.isError || weedMutation.isError;

  const handleUpload = useCallback(async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      setPartialFailure(null);

      // Run all 3 detections in parallel
      const settled = await Promise.allSettled([
        pestMutation.mutateAsync({ image: file }),
        diseaseMutation.mutateAsync({ image: file }),
        weedMutation.mutateAsync({ image: file }),
      ]);
      const [pestResult, diseaseResult, weedResult] = settled;

      const newResults: DetectionResult[] = [];
      if (pestResult.status === 'fulfilled') {
        newResults.push(...mapPestDetection(pestResult.value));
      }
      if (diseaseResult.status === 'fulfilled') {
        newResults.push(...mapDiseaseDetection(diseaseResult.value));
      }
      if (weedResult.status === 'fulfilled') {
        newResults.push(...mapWeedDetection(weedResult.value));
      }

      const failed = settled.filter((r) => r.status === 'rejected').length;
      if (failed > 0 && failed < settled.length) {
        // Partial failure — surface it so the user knows some detections were
        // skipped. The standard error banner (`hasError`) handles full failure.
        setPartialFailure(
          `تعذر إتمام ${failed} من ${settled.length} كشوفات. | ${failed} of ${settled.length} detections failed.`,
        );
      }

      setResults((prev) => [...newResults, ...prev]);
    };
    input.click();
  }, [pestMutation, diseaseMutation, weedMutation]);

  const filtered = filter === 'all' ? results : results.filter((r) => r.detectionType === filter);

  const stats = useMemo(
    () => ({
      total: results.length,
      critical: results.filter((r) => r.severity === 'critical').length,
      pending: results.filter((r) => r.status === 'new').length,
      avgConfidence:
        results.length > 0
          ? Math.round((results.reduce((s, r) => s + r.confidence, 0) / results.length) * 100)
          : 0,
    }),
    [results],
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الكشف البصري بالذكاء الاصطناعي</h1>
            <p className="text-gray-600 mt-1">AI Vision Detection</p>
            {models && models.length > 0 && (
              <p className="text-xs text-gray-400 mt-1">
                {models.filter((m) => m.loaded).length} / {models.length} نماذج محملة
              </p>
            )}
          </div>
          <button
            onClick={handleUpload}
            disabled={isProcessing}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                <span>جاري التحليل...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>رفع صورة للتحليل</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {hasError && !partialFailure && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-700 text-sm">
            فشل في معالجة بعض الصور. يرجى المحاولة مرة أخرى.
          </p>
        </div>
      )}

      {/* Partial Failure Banner (bilingual) */}
      {partialFailure && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
          <p className="text-amber-800 text-sm">{partialFailure}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Eye className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">إجمالي الكشوفات</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <p className="text-sm text-gray-600">حالات حرجة</p>
          </div>
          <p className="text-3xl font-bold text-red-600">{stats.critical}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-orange-600" />
            <p className="text-sm text-gray-600">بانتظار المراجعة</p>
          </div>
          <p className="text-3xl font-bold text-orange-600">{stats.pending}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">متوسط الدقة</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{stats.avgConfidence}%</p>
        </div>
      </div>

      {/* Models Loading */}
      {modelsLoading && <LoadingSkeleton />}

      {/* Filter + Table */}
      <div className="bg-white rounded-xl border-2 border-gray-200">
        <div className="flex items-center gap-3 p-6 border-b border-gray-200">
          <span className="text-sm font-medium text-gray-600">تصفية:</span>
          {(['all', 'pest', 'disease', 'weed'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {f === 'all' ? 'الكل' : f === 'pest' ? 'آفات' : f === 'disease' ? 'أمراض' : 'حشائش'}
            </button>
          ))}
        </div>

        <div className="p-6">
          {filtered.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Eye className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="font-medium">لا توجد كشوفات بعد</p>
              <p className="text-sm mt-1">ارفع صورة لبدء التحليل</p>
            </div>
          ) : (
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">النوع</th>
                  <th className="pb-3 pr-4 font-medium">الكشف</th>
                  <th className="pb-3 pr-4 font-medium">الحقل</th>
                  <th className="pb-3 pr-4 font-medium">الدقة</th>
                  <th className="pb-3 pr-4 font-medium">الخطورة</th>
                  <th className="pb-3 pr-4 font-medium">الحالة</th>
                  <th className="pb-3 pr-4 font-medium">التوصية</th>
                  <th className="pb-3 font-medium">التاريخ</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((result) => (
                  <tr key={result.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4">
                      <div className="flex items-center gap-2">
                        {typeIcons[result.detectionType]}
                        <span className="text-sm">{result.detectionTypeAr}</span>
                      </div>
                    </td>
                    <td className="py-4 pr-4">
                      <p className="font-semibold text-gray-900 text-sm">{result.labelAr}</p>
                      <p className="text-xs text-gray-500">{result.label}</p>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{result.fieldName}</td>
                    <td className="py-4 pr-4 text-sm font-medium text-gray-900">
                      {Math.round(result.confidence * 100)}%
                    </td>
                    <td className="py-4 pr-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${severityColors[result.severity]}`}
                      >
                        {result.severityAr}
                      </span>
                    </td>
                    <td className="py-4 pr-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[result.status]}`}
                      >
                        {result.statusAr}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-600 max-w-[200px] truncate">
                      {result.recommendationAr}
                    </td>
                    <td className="py-4 text-sm text-gray-700">{result.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
