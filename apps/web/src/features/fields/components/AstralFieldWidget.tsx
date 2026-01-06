'use client';

/**
 * SAHOOL Astral Field Widget Component
 * مكون عنصر التقويم الفلكي للحقل
 *
 * Displays astronomical calendar information in field context including:
 * - Current Hijri date and lunar mansion (المنزلة القمرية)
 * - Moon phase icon and name
 * - Today's farming recommendations
 * - Best 3 days this week for selected activity
 * - Activity selector (planting, irrigation, harvest)
 * - Quick action to create task on best day
 * - Collapsible detailed view
 *
 * Design reference: COMPETITIVE_GAP_ANALYSIS_FIELD_VIEW.md - Astral Agriculture Dashboard
 */

import React, { useState, useMemo } from 'react';
import {
  Moon,
  Calendar,
  Droplet,
  Sprout,
  Scissors,
  ChevronDown,
  ChevronUp,
  Plus,
  Star,
  Sparkles,
  CalendarDays,
} from 'lucide-react';
import { useToday, useBestDays } from '@/features/astronomical';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { Field } from '../types';

// ═══════════════════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════════════════

interface AstralFieldWidgetProps {
  field: Field;
  onCreateTask?: (taskData: {
    title: string;
    title_ar: string;
    description: string;
    description_ar: string;
    due_date: string;
    field_id: string;
    priority: 'high' | 'medium' | 'low';
  }) => void;
  compact?: boolean;
}

type FarmingActivity = 'زراعة' | 'ري' | 'حصاد' | 'تقليم';

interface ActivityConfig {
  value: FarmingActivity;
  label: string;
  labelEn: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

const ACTIVITY_OPTIONS: ActivityConfig[] = [
  {
    value: 'زراعة',
    label: 'زراعة',
    labelEn: 'Planting',
    icon: Sprout,
    color: 'text-green-600',
  },
  {
    value: 'ري',
    label: 'ري',
    labelEn: 'Irrigation',
    icon: Droplet,
    color: 'text-blue-600',
  },
  {
    value: 'حصاد',
    label: 'حصاد',
    labelEn: 'Harvest',
    icon: Scissors,
    color: 'text-amber-600',
  },
  {
    value: 'تقليم',
    label: 'تقليم',
    labelEn: 'Pruning',
    icon: Sparkles,
    color: 'text-purple-600',
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get color based on suitability score
 */
function getScoreColor(score: number): string {
  if (score >= 8) return 'text-green-600 bg-green-50';
  if (score >= 6) return 'text-amber-600 bg-amber-50';
  return 'text-red-600 bg-red-50';
}

/**
 * Get suitability text based on score
 */
function getSuitabilityText(score: number): { ar: string; en: string } {
  if (score >= 9) return { ar: 'ممتاز', en: 'Excellent' };
  if (score >= 8) return { ar: 'جيد جداً', en: 'Very Good' };
  if (score >= 6) return { ar: 'جيد', en: 'Good' };
  if (score >= 5) return { ar: 'متوسط', en: 'Fair' };
  return { ar: 'غير مناسب', en: 'Not Suitable' };
}

/**
 * Format date for display
 */
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ar-EG', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}

/**
 * Get day name in Arabic
 */
function getArabicDayName(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ar-EG', { weekday: 'long' });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════════════════════

export function AstralFieldWidget({
  field,
  onCreateTask,
  compact = false,
}: AstralFieldWidgetProps) {
  // State
  const [isExpanded, setIsExpanded] = useState(!compact);
  const [selectedActivity, setSelectedActivity] = useState<FarmingActivity>('زراعة');

  // Data fetching
  const { data: todayData, isLoading: isTodayLoading } = useToday();
  const { data: bestDaysData, isLoading: isBestDaysLoading } = useBestDays(
    selectedActivity,
    { days: 7 } // This week
  );

  // Computed values
  const todayRecommendation = useMemo(() => {
    if (!todayData?.recommendations) return null;
    return todayData.recommendations.find((rec) => rec.activity === selectedActivity);
  }, [todayData, selectedActivity]);

  const best3Days = useMemo(() => {
    if (!bestDaysData?.best_days) return [];
    return bestDaysData.best_days.slice(0, 3);
  }, [bestDaysData]);

  const selectedActivityConfig = useMemo(
    () => ACTIVITY_OPTIONS.find((opt) => opt.value === selectedActivity)!,
    [selectedActivity]
  );

  // Handlers
  const handleCreateTaskOnBestDay = () => {
    if (!best3Days[0] || !onCreateTask) return;

    const bestDay = best3Days[0];
    const activity = selectedActivityConfig;

    const taskData = {
      title: `${activity.labelEn} on ${formatDate(bestDay.date)}`,
      title_ar: `${activity.label} في ${getArabicDayName(bestDay.date)}`,
      description: `Best day for ${activity.labelEn.toLowerCase()} based on astronomical calendar.\n\nReason: ${bestDay.reason}`,
      description_ar: `أفضل يوم للـ${activity.label} بناءً على التقويم الفلكي.\n\nالسبب: ${bestDay.reason}`,
      due_date: bestDay.date,
      field_id: field.id,
      priority: 'medium' as const,
    };

    onCreateTask(taskData);
  };

  // Loading state
  if (isTodayLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
            <span className="mr-3 text-gray-600">جاري تحميل البيانات الفلكية...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!todayData) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center py-8 text-gray-500">
            لا تتوفر بيانات فلكية حالياً
          </div>
        </CardContent>
      </Card>
    );
  }

  // Render
  return (
    <Card variant="bordered" className="overflow-hidden">
      {/* Header */}
      <CardHeader className="bg-gradient-to-l from-indigo-50 to-purple-50 pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Moon className="w-5 h-5 text-purple-600" aria-hidden="true" />
            </div>
            <div>
              <CardTitle className="text-lg">التقويم الفلكي اليمني</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                توصيات زراعية حسب المنازل القمرية
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1"
            aria-label={isExpanded ? 'إخفاء التفاصيل' : 'عرض التفاصيل'}
          >
            {isExpanded ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        {/* Hijri Date & Lunar Mansion */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Hijri Date */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <Calendar className="w-5 h-5 text-gray-600 flex-shrink-0" />
            <div>
              <div className="text-xs text-gray-500 mb-1">التاريخ الهجري</div>
              <div className="font-semibold text-gray-900">
                {todayData.date_hijri.day} {todayData.date_hijri.month_name} {todayData.date_hijri.year}
              </div>
              <div className="text-xs text-gray-600 mt-0.5">
                {todayData.date_hijri.weekday}
              </div>
            </div>
          </div>

          {/* Lunar Mansion */}
          <div className="flex items-center gap-3 p-3 bg-indigo-50 rounded-lg">
            <Star className="w-5 h-5 text-indigo-600 flex-shrink-0" />
            <div>
              <div className="text-xs text-indigo-600 mb-1">المنزلة القمرية</div>
              <div className="font-semibold text-gray-900">
                {todayData.lunar_mansion.name}
              </div>
              <div className="text-xs text-gray-600 mt-0.5">
                {todayData.lunar_mansion.constellation}
              </div>
            </div>
          </div>
        </div>

        {/* Moon Phase */}
        <div className="flex items-center gap-4 p-4 bg-gradient-to-l from-blue-50 to-indigo-50 rounded-lg mb-6">
          <div className="text-4xl" aria-label={todayData.moon_phase.name}>
            {todayData.moon_phase.icon}
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 mb-1">
              {todayData.moon_phase.name}
            </div>
            <div className="text-sm text-gray-600">
              الإضاءة: {Math.round(todayData.moon_phase.illumination * 100)}% •{' '}
              العمر: {todayData.moon_phase.age_days} يوم
            </div>
          </div>
          {todayData.moon_phase.farming_good && (
            <div className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
              مناسب للزراعة
            </div>
          )}
        </div>

        {/* Activity Selector */}
        <div className="mb-6">
          <div className="text-sm font-medium text-gray-700 mb-3">
            اختر النشاط الزراعي
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {ACTIVITY_OPTIONS.map((activity) => {
              const Icon = activity.icon;
              const isSelected = selectedActivity === activity.value;

              return (
                <button
                  key={activity.value}
                  onClick={() => setSelectedActivity(activity.value)}
                  className={`
                    flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg
                    border-2 transition-all duration-200
                    ${
                      isSelected
                        ? 'border-sahool-green-600 bg-sahool-green-50 shadow-sm'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }
                  `}
                  aria-pressed={isSelected}
                >
                  <Icon
                    className={`w-4 h-4 ${isSelected ? 'text-sahool-green-600' : 'text-gray-500'}`}
                  />
                  <span
                    className={`text-sm font-medium ${
                      isSelected ? 'text-sahool-green-900' : 'text-gray-700'
                    }`}
                  >
                    {activity.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Today's Recommendation */}
        {todayRecommendation && (
          <div className="mb-6">
            <div className="text-sm font-medium text-gray-700 mb-3">
              توصية اليوم لـ{selectedActivityConfig.label}
            </div>
            <div
              className={`
              flex items-start gap-4 p-4 rounded-lg border-2
              ${getScoreColor(todayRecommendation.suitability_score)}
            `}
            >
              <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm">
                  <span className="text-xl font-bold">
                    {todayRecommendation.suitability_score}
                  </span>
                  <span className="text-xs text-gray-600">/10</span>
                </div>
              </div>
              <div className="flex-1">
                <div className="font-semibold mb-1">
                  {getSuitabilityText(todayRecommendation.suitability_score).ar}
                </div>
                <div className="text-sm text-gray-700 mb-2">
                  {todayRecommendation.reason}
                </div>
                {todayRecommendation.best_time && (
                  <div className="text-xs text-gray-600">
                    أفضل وقت: {todayRecommendation.best_time}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Expanded Details */}
        {isExpanded && (
          <div className="space-y-6 pt-6 border-t border-gray-200">
            {/* Best 3 Days This Week */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <CalendarDays className="w-5 h-5 text-sahool-green-600" />
                <h4 className="font-semibold text-gray-900">
                  أفضل 3 أيام هذا الأسبوع لـ{selectedActivityConfig.label}
                </h4>
              </div>

              {isBestDaysLoading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-sahool-green-600 mx-auto" />
                </div>
              ) : best3Days.length > 0 ? (
                <div className="space-y-3">
                  {best3Days.map((day, index) => (
                    <div
                      key={day.date}
                      className={`
                        flex items-center gap-4 p-4 rounded-lg border-2
                        ${index === 0 ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'}
                      `}
                    >
                      <div className="flex-shrink-0 text-center">
                        <div
                          className={`
                          w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                          ${index === 0 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-700'}
                        `}
                        >
                          #{index + 1}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="font-semibold text-gray-900">
                            {getArabicDayName(day.date)}
                          </div>
                          <div className="text-sm text-gray-600">
                            {formatDate(day.date)}
                          </div>
                          <div
                            className={`
                            px-2 py-0.5 rounded text-xs font-medium
                            ${getScoreColor(day.score)}
                          `}
                          >
                            {day.score}/10
                          </div>
                        </div>
                        <div className="text-sm text-gray-700 mb-1">
                          {day.reason}
                        </div>
                        <div className="flex items-center gap-3 text-xs text-gray-600">
                          <span>🌙 {day.moon_phase}</span>
                          <span>⭐ {day.lunar_mansion}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-gray-500">
                  لا توجد أيام مناسبة هذا الأسبوع
                </div>
              )}
            </div>

            {/* Quick Action: Create Task */}
            {best3Days.length > 0 && best3Days[0] && onCreateTask && (
              <div className="pt-4 border-t border-gray-200">
                <Button
                  onClick={handleCreateTaskOnBestDay}
                  variant="primary"
                  className="w-full"
                  size="md"
                >
                  <Plus className="w-4 h-4 ml-2" />
                  إنشاء مهمة في أفضل يوم ({formatDate(best3Days[0].date)})
                </Button>
              </div>
            )}

            {/* Lunar Mansion Details */}
            <div className="pt-4 border-t border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">
                تفاصيل المنزلة القمرية - {todayData.lunar_mansion.name}
              </h4>
              <div className="space-y-3">
                <div className="text-sm text-gray-700">
                  {todayData.lunar_mansion.description}
                </div>

                {todayData.lunar_mansion.crops.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-gray-600 mb-2">
                      المحاصيل المناسبة:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {todayData.lunar_mansion.crops.map((crop) => (
                        <span
                          key={crop}
                          className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full"
                        >
                          {crop}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {todayData.lunar_mansion.activities.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-gray-600 mb-2">
                      الأنشطة الموصى بها:
                    </div>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {todayData.lunar_mansion.activities.map((activity) => (
                        <li key={activity} className="flex items-center gap-2">
                          <span className="text-green-600">✓</span>
                          {activity}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {todayData.lunar_mansion.avoid.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-gray-600 mb-2">
                      يُنصح بتجنب:
                    </div>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {todayData.lunar_mansion.avoid.map((item) => (
                        <li key={item} className="flex items-center gap-2">
                          <span className="text-red-600">✗</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Overall Farming Score */}
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between p-4 bg-gradient-to-l from-purple-50 to-indigo-50 rounded-lg">
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">
                    التقييم الزراعي العام لليوم
                  </div>
                  <div className="text-xs text-gray-600">
                    بناءً على المنزلة القمرية وطور القمر والموسم
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-3xl font-bold text-purple-600">
                    {todayData.overall_farming_score}
                  </div>
                  <div className="text-sm text-gray-600">/10</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

AstralFieldWidget.displayName = 'AstralFieldWidget';

export default AstralFieldWidget;
