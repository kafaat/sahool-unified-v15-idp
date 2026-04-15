'use client';

/**
 * Crop Protection Client Component
 * مكون حماية المحاصيل — الأمراض والآفات وبرنامج الرش
 */

import React, { useState, useMemo } from 'react';
import {
  Bug,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Wind,
  Thermometer,
  Droplets,
  Clock,
  Leaf,
  Target,
  TrendingUp,
  TrendingDown,
  RefreshCw,
} from 'lucide-react';
import { usePestRecords, useSprayWindows } from '../hooks/useCropProtection';
import type { PestRecord, SprayWindow } from '../api';

// ---------------------------------------------------------------------------
// Types (local UI-only types not covered by the API)
// ---------------------------------------------------------------------------

interface Disease {
  id: string;
  nameAr: string;
  nameEn: string;
  crop: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affectedFields: number;
  lastDetected: string;
  treatmentStatus: 'untreated' | 'in_progress' | 'treated' | 'monitoring';
  affectedAreaPct: number;
}

interface Pest {
  id: string;
  nameAr: string;
  nameEn: string;
  crop: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  threshold: string;
  actionRequired: boolean;
  ipmStrategy: string;
  lastScouting: string;
  populationTrend: 'increasing' | 'stable' | 'decreasing';
}

interface SpraySchedule {
  id: string;
  fieldName: string;
  product: string;
  targetAr: string;
  scheduledDate: string;
  weatherSuitable: boolean;
  windSpeed: number;
  temperature: number;
  humidity: number;
  phi: number;
  costPerHectare: number;
  areaHectares: number;
  status: 'scheduled' | 'completed' | 'postponed' | 'cancelled';
}

// ---------------------------------------------------------------------------
// Helpers — map API data to UI models
// ---------------------------------------------------------------------------

function mapPestRecordsToDiseases(records: PestRecord[]): Disease[] {
  return records.map((r) => ({
    id: r.id,
    nameAr: r.pestType,
    nameEn: r.pestType,
    crop: r.fieldId,
    severity: r.severity,
    affectedFields: 1,
    lastDetected: r.detectedAt,
    treatmentStatus:
      r.status === 'resolved'
        ? 'treated'
        : r.status === 'treated'
          ? 'in_progress'
          : 'untreated',
    affectedAreaPct: Math.round(r.confidence * 100),
  }));
}

function mapPestRecordsToPests(records: PestRecord[]): Pest[] {
  return records.map((r) => ({
    id: r.id,
    nameAr: r.pestType,
    nameEn: r.pestType,
    crop: r.fieldId,
    riskLevel: r.severity,
    threshold: '-',
    actionRequired: r.severity === 'critical' || r.severity === 'high',
    ipmStrategy: '-',
    lastScouting: r.detectedAt,
    populationTrend:
      r.status === 'active' ? 'increasing' : r.status === 'resolved' ? 'decreasing' : 'stable',
  }));
}

function mapSprayWindowsToSchedule(windows: SprayWindow[]): SpraySchedule[] {
  return windows.map((w) => ({
    id: w.id,
    fieldName: w.fieldId,
    product: '-',
    targetAr: '-',
    scheduledDate: w.startTime,
    weatherSuitable: w.suitability !== 'poor',
    windSpeed: w.windSpeed,
    temperature: w.temperature,
    humidity: w.humidity,
    phi: 0,
    costPerHectare: 0,
    areaHectares: 0,
    status: w.suitability === 'optimal' ? 'scheduled' : 'postponed',
  }));
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TABS = [
  { id: 'diseases', label: 'الأمراض', icon: Leaf },
  { id: 'pests', label: 'الآفات', icon: Bug },
  { id: 'spray', label: 'برنامج الرش', icon: Calendar },
] as const;

type TabId = (typeof TABS)[number]['id'];

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
};

const SEVERITY_LABELS: Record<string, string> = {
  critical: 'حرج',
  high: 'مرتفع',
  medium: 'متوسط',
  low: 'منخفض',
};

const TREATMENT_LABELS: Record<string, string> = {
  untreated: 'غير معالج',
  in_progress: 'قيد العلاج',
  treated: 'تم العلاج',
  monitoring: 'مراقبة',
};

const TREATMENT_STYLES: Record<string, string> = {
  untreated: 'bg-red-100 text-red-700',
  in_progress: 'bg-blue-100 text-blue-700',
  treated: 'bg-green-100 text-green-700',
  monitoring: 'bg-purple-100 text-purple-700',
};

const SPRAY_STATUS_LABELS: Record<string, string> = {
  scheduled: 'مجدول',
  completed: 'مكتمل',
  postponed: 'مؤجل',
  cancelled: 'ملغي',
};

const SPRAY_STATUS_STYLES: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  postponed: 'bg-yellow-100 text-yellow-700',
  cancelled: 'bg-red-100 text-red-700',
};

// ---------------------------------------------------------------------------
// Loading / Error UI
// ---------------------------------------------------------------------------

function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 animate-pulse">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gray-200 rounded-xl" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/3" />
              <div className="h-3 bg-gray-200 rounded w-1/4" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ErrorBanner({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
      <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
      <p className="text-red-700 font-medium mb-3">{message}</p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
      >
        <RefreshCw className="w-4 h-4" />
        إعادة المحاولة
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CropProtectionClient() {
  const [activeTab, setActiveTab] = useState<TabId>('diseases');
  const [_searchQuery, _setSearchQuery] = useState('');

  // Fetch data from API
  const {
    data: pestRecords,
    isLoading: pestsLoading,
    isError: pestsError,
    refetch: refetchPests,
  } = usePestRecords();

  const {
    data: sprayWindows,
    isLoading: sprayLoading,
    isError: sprayError,
    refetch: refetchSpray,
  } = useSprayWindows();

  const isLoading = pestsLoading || sprayLoading;
  const isError = pestsError || sprayError;

  // Map API data to UI models
  const diseases = useMemo(
    () => (pestRecords ? mapPestRecordsToDiseases(pestRecords) : []),
    [pestRecords],
  );
  const pests = useMemo(
    () => (pestRecords ? mapPestRecordsToPests(pestRecords) : []),
    [pestRecords],
  );
  const spraySchedule = useMemo(
    () => (sprayWindows ? mapSprayWindowsToSchedule(sprayWindows) : []),
    [sprayWindows],
  );

  const stats = useMemo(
    () => ({
      totalDiseases: diseases.length,
      criticalDiseases: diseases.filter((d) => d.severity === 'critical').length,
      totalPests: pests.length,
      actionRequired: pests.filter((p) => p.actionRequired).length,
      scheduledSprays: spraySchedule.filter((s) => s.status === 'scheduled').length,
      completedSprays: spraySchedule.filter((s) => s.status === 'completed').length,
    }),
    [diseases, pests, spraySchedule],
  );

  const handleRetry = () => {
    refetchPests();
    refetchSpray();
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">حماية المحاصيل</h1>
        <p className="text-sm text-gray-500 mt-1">
          إدارة الأمراض والآفات وبرنامج الرش الوقائي والعلاجي
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-500">أمراض نشطة</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {isLoading ? '...' : stats.totalDiseases}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="text-sm text-gray-500">حرجة</span>
          </div>
          <p className="text-2xl font-bold text-red-600 mt-1">
            {isLoading ? '...' : stats.criticalDiseases}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Bug className="w-5 h-5 text-orange-500" />
            <span className="text-sm text-gray-500">آفات مرصودة</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {isLoading ? '...' : stats.totalPests}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-500">تتطلب إجراء</span>
          </div>
          <p className="text-2xl font-bold text-orange-600 mt-1">
            {isLoading ? '...' : stats.actionRequired}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-gray-500">رش مجدول</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {isLoading ? '...' : stats.scheduledSprays}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-sm text-gray-500">رش مكتمل</span>
          </div>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {isLoading ? '...' : stats.completedSprays}
          </p>
        </div>
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

      {/* Error State */}
      {isError && (
        <ErrorBanner
          message="فشل في تحميل بيانات حماية المحاصيل. يرجى المحاولة مرة أخرى."
          onRetry={handleRetry}
        />
      )}

      {/* Loading State */}
      {isLoading && !isError && <LoadingSkeleton />}

      {/* Diseases Tab */}
      {!isLoading && !isError && activeTab === 'diseases' && (
        <div className="space-y-3">
          {diseases.length === 0 ? (
            <div className="bg-white rounded-xl p-8 text-center text-gray-500">
              لا توجد أمراض مسجلة حالياً
            </div>
          ) : (
            diseases.map((disease) => (
              <div key={disease.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        disease.severity === 'critical'
                          ? 'bg-red-100'
                          : disease.severity === 'high'
                            ? 'bg-orange-100'
                            : 'bg-yellow-100'
                      }`}
                    >
                      <Leaf
                        className={`w-6 h-6 ${
                          disease.severity === 'critical'
                            ? 'text-red-600'
                            : disease.severity === 'high'
                              ? 'text-orange-600'
                              : 'text-yellow-600'
                        }`}
                      />
                    </div>
                    <div>
                      <p className="font-bold text-gray-900">{disease.nameAr}</p>
                      <p className="text-sm text-gray-500">
                        {disease.nameEn} - {disease.crop}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-left text-sm">
                      <p className="text-gray-500">{disease.affectedFields} حقول متأثرة</p>
                      <p className="text-gray-500">{disease.affectedAreaPct}% مساحة مصابة</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${SEVERITY_STYLES[disease.severity]}`}
                    >
                      {SEVERITY_LABELS[disease.severity]}
                    </span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${TREATMENT_STYLES[disease.treatmentStatus]}`}
                    >
                      {TREATMENT_LABELS[disease.treatmentStatus]}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Pests Tab */}
      {!isLoading && !isError && activeTab === 'pests' && (
        <div className="space-y-3">
          {pests.length === 0 ? (
            <div className="bg-white rounded-xl p-8 text-center text-gray-500">
              لا توجد آفات مرصودة حالياً
            </div>
          ) : (
            pests.map((pest) => (
              <div key={pest.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        pest.riskLevel === 'critical'
                          ? 'bg-red-100'
                          : pest.riskLevel === 'high'
                            ? 'bg-orange-100'
                            : 'bg-yellow-100'
                      }`}
                    >
                      <Bug
                        className={`w-6 h-6 ${
                          pest.riskLevel === 'critical'
                            ? 'text-red-600'
                            : pest.riskLevel === 'high'
                              ? 'text-orange-600'
                              : 'text-yellow-600'
                        }`}
                      />
                    </div>
                    <div>
                      <p className="font-bold text-gray-900">{pest.nameAr}</p>
                      <p className="text-sm text-gray-500">
                        {pest.nameEn} - {pest.crop}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1 text-sm">
                      {pest.populationTrend === 'increasing' ? (
                        <TrendingUp className="w-4 h-4 text-red-500" />
                      ) : pest.populationTrend === 'decreasing' ? (
                        <TrendingDown className="w-4 h-4 text-green-500" />
                      ) : (
                        <span className="w-4 h-4 text-gray-400">--</span>
                      )}
                      <span
                        className={
                          pest.populationTrend === 'increasing'
                            ? 'text-red-600'
                            : pest.populationTrend === 'decreasing'
                              ? 'text-green-600'
                              : 'text-gray-500'
                        }
                      >
                        {pest.populationTrend === 'increasing'
                          ? 'متزايد'
                          : pest.populationTrend === 'decreasing'
                            ? 'متناقص'
                            : 'مستقر'}
                      </span>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${SEVERITY_STYLES[pest.riskLevel]}`}
                    >
                      {SEVERITY_LABELS[pest.riskLevel]}
                    </span>
                    {pest.actionRequired && (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                        يتطلب إجراء
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-6 text-sm text-gray-500 border-t pt-3">
                  <span>العتبة: {pest.threshold}</span>
                  <span>الاستراتيجية: {pest.ipmStrategy}</span>
                  <span>آخر فحص: {pest.lastScouting}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Spray Schedule Tab */}
      {!isLoading && !isError && activeTab === 'spray' && (
        <div className="space-y-3">
          {spraySchedule.length === 0 ? (
            <div className="bg-white rounded-xl p-8 text-center text-gray-500">
              لا توجد جداول رش حالياً
            </div>
          ) : (
            spraySchedule.map((spray) => (
              <div key={spray.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-bold text-gray-900">{spray.fieldName}</p>
                    <p className="text-sm text-gray-500">
                      {spray.product} - {spray.targetAr}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-600">{spray.scheduledDate}</span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${SPRAY_STATUS_STYLES[spray.status]}`}
                    >
                      {SPRAY_STATUS_LABELS[spray.status]}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-sm border-t pt-3">
                  <div className="flex items-center gap-1">
                    {spray.weatherSuitable ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                    )}
                    <span className={spray.weatherSuitable ? 'text-green-600' : 'text-red-600'}>
                      {spray.weatherSuitable ? 'طقس مناسب' : 'طقس غير مناسب'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-500">
                    <Wind className="w-4 h-4" />
                    <span>{spray.windSpeed} كم/س</span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-500">
                    <Thermometer className="w-4 h-4" />
                    <span>{spray.temperature} درجة</span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-500">
                    <Droplets className="w-4 h-4" />
                    <span>{spray.humidity}%</span>
                  </div>
                  {spray.phi > 0 && (
                    <div className="flex items-center gap-1 text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>PHI: {spray.phi} يوم</span>
                    </div>
                  )}
                  {spray.costPerHectare > 0 && spray.areaHectares > 0 && (
                    <div className="text-gray-500">
                      التكلفة:{' '}
                      {(spray.costPerHectare * spray.areaHectares).toLocaleString('ar-SA')} ريال
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
