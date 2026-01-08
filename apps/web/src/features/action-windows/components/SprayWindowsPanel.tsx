'use client';

/**
 * SAHOOL Spray Windows Panel Component
 * مكون لوحة نوافذ الرش
 *
 * Displays 7-day spray forecast with optimal windows and conditions
 */

import React, { useState, useMemo } from 'react';
import { Sprout, Wind, Thermometer, Droplets, Calendar, AlertCircle, RefreshCw, Plus } from 'lucide-react';
import { useSprayWindows } from '../hooks/useActionWindows';
import type { SprayWindow, SprayWindowCriteria } from '../types/action-windows';
import { WindowTimeline } from './WindowTimeline';

interface SprayWindowsPanelProps {
  fieldId: string;
  days?: number;
  criteria?: Partial<SprayWindowCriteria>;
  onCreateTask?: (window: SprayWindow) => void;
  showTimeline?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('ar-EG', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getStatusBadge = (status: SprayWindow['status']) => {
  switch (status) {
    case 'optimal':
      return (
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium border border-green-300">
          مثالي
        </span>
      );
    case 'marginal':
      return (
        <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium border border-yellow-300">
          هامشي
        </span>
      );
    case 'avoid':
      return (
        <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium border border-red-300">
          تجنب
        </span>
      );
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export const SprayWindowsPanel = React.memo<SprayWindowsPanelProps>(({
  fieldId,
  days = 7,
  criteria,
  onCreateTask,
  showTimeline = true,
}) => {
  const [selectedWindow, setSelectedWindow] = useState<SprayWindow | null>(null);
  const { data: windows, isLoading, error, refetch, isRefetching } = useSprayWindows({
    fieldId,
    days,
    criteria,
  });

  // Filter to show only good and marginal windows
  const viableWindows = useMemo(() => {
    return windows?.filter((w) => w.status !== 'avoid') || [];
  }, [windows]);

  // Convert windows to timeline blocks
  const timelineBlocks = useMemo(() => {
    if (!windows) return [];

    return windows.map((window) => ({
      id: window.id,
      startTime: window.startTime,
      endTime: window.endTime,
      status: window.status,
      score: window.score,
      label: `Spray Window - ${window.duration}h`,
      labelAr: `نافذة رش - ${window.duration}س`,
      details: {
        temperature: window.conditions.temperature,
        windSpeed: window.conditions.windSpeed,
        humidity: window.conditions.humidity,
        rainProbability: window.conditions.rainProbability,
      },
      actionable: window.status !== 'avoid',
    }));
  }, [windows]);

  const handleCreateTask = (window: SprayWindow) => {
    onCreateTask?.(window);
    setSelectedWindow(null);
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8" role="status" aria-live="polite">
        <div className="flex flex-col items-center justify-center space-y-4">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin" aria-hidden="true" />
          <p className="text-gray-600" dir="rtl">
            جاري تحميل نوافذ الرش...
          </p>
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="bg-white rounded-xl border border-red-200 p-8" role="alert">
        <div className="flex flex-col items-center justify-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500" aria-hidden="true" />
          <div className="text-center">
            <p className="text-red-700 font-medium mb-2" dir="rtl">
              حدث خطأ أثناء تحميل نوافذ الرش
            </p>
            <p className="text-sm text-red-600 mb-4" dir="ltr">
              {error.message}
            </p>
            <button
              onClick={() => refetch()}
              disabled={isRefetching}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 inline mr-2 ${isRefetching ? 'animate-spin' : ''}`} aria-hidden="true" />
              <span dir="rtl">إعادة المحاولة</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No Windows Available
  if (!windows || windows.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8" role="status">
        <div className="flex flex-col items-center justify-center space-y-4">
          <Sprout className="w-12 h-12 text-gray-400" aria-hidden="true" />
          <div className="text-center">
            <p className="text-gray-700 font-medium mb-2" dir="rtl">
              لا توجد نوافذ رش متاحة
            </p>
            <p className="text-sm text-gray-500" dir="rtl">
              جرب تعديل المعايير أو فحص توقعات الطقس
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3" dir="rtl">
            <div className="p-3 bg-green-100 rounded-lg">
              <Sprout className="w-6 h-6 text-green-700" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">نوافذ الرش</h2>
              <p className="text-sm text-gray-600">توقعات {days} أيام</p>
            </div>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="p-2 text-green-700 hover:bg-green-100 rounded-lg transition-colors"
            aria-label="تحديث نوافذ الرش"
          >
            <RefreshCw className={`w-5 h-5 ${isRefetching ? 'animate-spin' : ''}`} aria-hidden="true" />
          </button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-3 border border-green-200">
            <p className="text-sm text-gray-600 mb-1" dir="rtl">إجمالي النوافذ</p>
            <p className="text-2xl font-bold text-gray-900">{windows.length}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-3 border border-green-300">
            <p className="text-sm text-green-700 mb-1" dir="rtl">مثالي</p>
            <p className="text-2xl font-bold text-green-700">
              {windows.filter((w) => w.status === 'optimal').length}
            </p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-300">
            <p className="text-sm text-yellow-700 mb-1" dir="rtl">هامشي</p>
            <p className="text-2xl font-bold text-yellow-700">
              {windows.filter((w) => w.status === 'marginal').length}
            </p>
          </div>
        </div>
      </div>

      {/* Timeline View */}
      {showTimeline && timelineBlocks.length > 0 && (
        <WindowTimeline
          timeline={timelineBlocks}
          onBlockClick={(block) => {
            const window = windows.find((w) => w.id === block.id);
            if (window) setSelectedWindow(window);
          }}
        />
      )}

      {/* Window Cards List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900" dir="rtl">
          النوافذ المتاحة ({viableWindows.length})
        </h3>

        {viableWindows.length === 0 ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center" dir="rtl">
            <AlertCircle className="w-10 h-10 text-yellow-600 mx-auto mb-3" aria-hidden="true" />
            <p className="text-yellow-800 font-medium">لا توجد نوافذ رش مناسبة في الأيام القادمة</p>
            <p className="text-sm text-yellow-700 mt-2">راقب توقعات الطقس للحصول على ظروف أفضل</p>
          </div>
        ) : (
          viableWindows.map((window) => (
            <div
              key={window.id}
              className={`
                bg-white rounded-lg border-2 p-5 transition-all
                ${selectedWindow?.id === window.id ? 'border-blue-500 shadow-lg' : 'border-gray-200 hover:border-gray-300'}
              `}
              role="article"
            >
              {/* Window Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1" dir="rtl">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-5 h-5 text-gray-500" aria-hidden="true" />
                    <span className="font-semibold text-gray-900">
                      {formatDateTime(window.startTime)}
                    </span>
                    {getStatusBadge(window.status)}
                  </div>
                  <p className="text-sm text-gray-600">
                    المدة: {window.duration} ساعة | النتيجة: {Math.round(window.score)}/100
                  </p>
                </div>

                {onCreateTask && window.status === 'optimal' && (
                  <button
                    onClick={() => handleCreateTask(window)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2"
                    aria-label="إنشاء مهمة رش"
                  >
                    <Plus className="w-4 h-4" aria-hidden="true" />
                    <span dir="rtl">إنشاء مهمة</span>
                  </button>
                )}
              </div>

              {/* Suitability Indicators */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className={`p-3 rounded-lg border ${window.suitability.windSpeed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Wind className="w-4 h-4" aria-hidden="true" />
                    <span className="text-xs font-medium">الرياح</span>
                  </div>
                  <p className="text-sm font-semibold">{window.conditions.windSpeed} km/h</p>
                </div>

                <div className={`p-3 rounded-lg border ${window.suitability.temperature ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Thermometer className="w-4 h-4" aria-hidden="true" />
                    <span className="text-xs font-medium">الحرارة</span>
                  </div>
                  <p className="text-sm font-semibold">{Math.round(window.conditions.temperature)}°C</p>
                </div>

                <div className={`p-3 rounded-lg border ${window.suitability.humidity ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Droplets className="w-4 h-4" aria-hidden="true" />
                    <span className="text-xs font-medium">الرطوبة</span>
                  </div>
                  <p className="text-sm font-semibold">{Math.round(window.conditions.humidity)}%</p>
                </div>

                <div className={`p-3 rounded-lg border ${window.suitability.rain ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Calendar className="w-4 h-4" aria-hidden="true" />
                    <span className="text-xs font-medium">المطر</span>
                  </div>
                  <p className="text-sm font-semibold">{Math.round(window.conditions.rainProbability)}%</p>
                </div>
              </div>

              {/* Warnings */}
              {window.warningsAr.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                  <h4 className="font-medium text-yellow-900 mb-2 text-sm" dir="rtl">تحذيرات:</h4>
                  <ul className="space-y-1">
                    {window.warningsAr.map((warning, idx) => (
                      <li key={idx} className="text-sm text-yellow-800 flex items-start gap-2" dir="rtl">
                        <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" aria-hidden="true" />
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {window.recommendationsAr.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <h4 className="font-medium text-blue-900 mb-2 text-sm" dir="rtl">توصيات:</h4>
                  <ul className="space-y-1">
                    {window.recommendationsAr.map((rec, idx) => (
                      <li key={idx} className="text-sm text-blue-800" dir="rtl">
                        • {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
});

SprayWindowsPanel.displayName = 'SprayWindowsPanel';

export default SprayWindowsPanel;
