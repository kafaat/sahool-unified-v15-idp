'use client';

/**
 * SAHOOL Action Windows Demo Component
 * مكون عرض توضيحي لنوافذ العمل
 *
 * Example usage of Action Windows feature with one-click task creation
 */

import React, { useState } from 'react';
import { SprayWindowsPanel } from './SprayWindowsPanel';
import { IrrigationWindowsPanel } from './IrrigationWindowsPanel';
import { ActionRecommendation } from './ActionRecommendation';
import { useActionRecommendations } from '../hooks/useActionWindows';
import { useCreateTask } from '@/features/tasks/hooks/useTasks';
import type { SprayWindow, IrrigationWindow, ActionRecommendation as ActionRec } from '../types/action-windows';
import type { TaskFormData } from '@/features/tasks/types';
import { CheckCircle2, AlertCircle } from 'lucide-react';

interface ActionWindowsDemoProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  days?: number;
}

/**
 * Demo component showing how to integrate Action Windows with Task creation
 *
 * Features:
 * - Spray windows with one-click task creation
 * - Irrigation windows with one-click task creation
 * - Action recommendations with one-click task creation
 * - Success/Error feedback
 */
export const ActionWindowsDemo: React.FC<ActionWindowsDemoProps> = ({
  fieldId,
  fieldName = 'Field',
  fieldNameAr = 'الحقل',
  days = 7,
}) => {
  const [activeTab, setActiveTab] = useState<'spray' | 'irrigation' | 'recommendations'>('spray');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const createTaskMutation = useCreateTask();
  const { data: recommendations } = useActionRecommendations({ fieldId, days });

  // ─────────────────────────────────────────────────────────────────────────────
  // Task Creation Handlers
  // ─────────────────────────────────────────────────────────────────────────────

  /**
   * Create a spray task from a spray window
   */
  const handleCreateSprayTask = async (window: SprayWindow) => {
    const taskData: TaskFormData = {
      title: `Spray Application - ${fieldName}`,
      title_ar: `رش المبيدات - ${fieldNameAr}`,
      description: `Optimal spray window available\n\nConditions:\n- Wind: ${window.conditions.windSpeed} km/h\n- Temperature: ${window.conditions.temperature}°C\n- Humidity: ${window.conditions.humidity}%\n- Rain Probability: ${window.conditions.rainProbability}%\n\nScore: ${window.score}/100\n\nRecommendations:\n${window.recommendations.join('\n')}`,
      description_ar: `نافذة رش مثالية متاحة\n\nالظروف:\n- الرياح: ${window.conditions.windSpeed} كم/س\n- الحرارة: ${window.conditions.temperature}°م\n- الرطوبة: ${window.conditions.humidity}%\n- احتمال المطر: ${window.conditions.rainProbability}%\n\nالنتيجة: ${window.score}/100\n\nالتوصيات:\n${window.recommendationsAr.join('\n')}`,
      due_date: window.startTime,
      priority: window.score >= 90 ? 'high' : 'medium',
      field_id: fieldId,
      status: 'open',
    };

    try {
      await createTaskMutation.mutateAsync(taskData);
      setSuccessMessage(`تم إنشاء مهمة الرش بنجاح لـ ${formatDate(window.startTime)}`);
      setErrorMessage('');
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (error) {
      setErrorMessage('فشل إنشاء مهمة الرش. حاول مرة أخرى.');
      setSuccessMessage('');
      console.error('Failed to create spray task:', error);
    }
  };

  /**
   * Create an irrigation task from an irrigation window
   */
  const handleCreateIrrigationTask = async (window: IrrigationWindow) => {
    const taskData: TaskFormData = {
      title: `Irrigation - ${window.waterAmount}mm - ${fieldName}`,
      title_ar: `ري - ${window.waterAmount}ملم - ${fieldNameAr}`,
      description: `${window.reason}\n\nDetails:\n- Soil Moisture: ${window.soilMoisture.current.toFixed(1)}% (Target: ${window.soilMoisture.target.toFixed(1)}%)\n- Water Deficit: ${window.soilMoisture.deficit.toFixed(1)}mm\n- Water Amount: ${window.waterAmount}mm\n- Duration: ${window.duration} hours\n- ET₀: ${window.et.et0.toFixed(2)} mm/day\n- ETc: ${window.et.etc.toFixed(2)} mm/day\n\nRecommendations:\n${window.recommendations.join('\n')}`,
      description_ar: `${window.reasonAr}\n\nالتفاصيل:\n- رطوبة التربة: ${window.soilMoisture.current.toFixed(1)}% (المستهدف: ${window.soilMoisture.target.toFixed(1)}%)\n- عجز الماء: ${window.soilMoisture.deficit.toFixed(1)}ملم\n- كمية الماء: ${window.waterAmount}ملم\n- المدة: ${window.duration} ساعة\n- ET₀: ${window.et.et0.toFixed(2)} ملم/يوم\n- ETc: ${window.et.etc.toFixed(2)} ملم/يوم\n\nالتوصيات:\n${window.recommendationsAr.join('\n')}`,
      due_date: window.startTime,
      priority: window.priority === 'urgent' || window.priority === 'high' ? 'high' : 'medium',
      field_id: fieldId,
      status: 'open',
    };

    try {
      await createTaskMutation.mutateAsync(taskData);
      setSuccessMessage(`تم إنشاء مهمة الري بنجاح لـ ${formatDate(window.date)}`);
      setErrorMessage('');
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (error) {
      setErrorMessage('فشل إنشاء مهمة الري. حاول مرة أخرى.');
      setSuccessMessage('');
      console.error('Failed to create irrigation task:', error);
    }
  };

  /**
   * Create a task from an action recommendation
   */
  const handleCreateRecommendationTask = async (recommendation: ActionRec) => {
    const taskData: TaskFormData = {
      title: recommendation.title,
      title_ar: recommendation.titleAr,
      description: `${recommendation.description}\n\nReason:\n${recommendation.reason}\n\nBenefits:\n${recommendation.benefits.join('\n')}\n${recommendation.warnings ? `\nWarnings:\n${recommendation.warnings.join('\n')}` : ''}`,
      description_ar: `${recommendation.descriptionAr}\n\nالسبب:\n${recommendation.reasonAr}\n\nالفوائد:\n${recommendation.benefitsAr.join('\n')}\n${recommendation.warningsAr ? `\nتحذيرات:\n${recommendation.warningsAr.join('\n')}` : ''}`,
      due_date: recommendation.window.startTime,
      priority: recommendation.priority === 'urgent' || recommendation.priority === 'high' ? 'high' : 'medium',
      field_id: fieldId,
      status: 'open',
    };

    try {
      await createTaskMutation.mutateAsync(taskData);
      setSuccessMessage(`تم إنشاء المهمة بنجاح: ${recommendation.titleAr}`);
      setErrorMessage('');
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (error) {
      setErrorMessage('فشل إنشاء المهمة. حاول مرة أخرى.');
      setSuccessMessage('');
      console.error('Failed to create recommendation task:', error);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper Functions
  // ─────────────────────────────────────────────────────────────────────────────

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Success/Error Messages */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3" role="alert">
          <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <p className="text-green-800 font-medium" dir="rtl">{successMessage}</p>
        </div>
      )}

      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3" role="alert">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-red-800 font-medium" dir="rtl">{errorMessage}</p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg border border-gray-200 p-1">
        <div className="grid grid-cols-3 gap-1">
          <button
            onClick={() => setActiveTab('spray')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'spray'
                ? 'bg-blue-600 text-white'
                : 'bg-transparent text-gray-700 hover:bg-gray-100'
            }`}
            dir="rtl"
          >
            نوافذ الرش
          </button>
          <button
            onClick={() => setActiveTab('irrigation')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'irrigation'
                ? 'bg-blue-600 text-white'
                : 'bg-transparent text-gray-700 hover:bg-gray-100'
            }`}
            dir="rtl"
          >
            نوافذ الري
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'recommendations'
                ? 'bg-blue-600 text-white'
                : 'bg-transparent text-gray-700 hover:bg-gray-100'
            }`}
            dir="rtl"
          >
            التوصيات
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'spray' && (
          <SprayWindowsPanel
            fieldId={fieldId}
            days={days}
            onCreateTask={handleCreateSprayTask}
            showTimeline={true}
          />
        )}

        {activeTab === 'irrigation' && (
          <IrrigationWindowsPanel
            fieldId={fieldId}
            days={days}
            onCreateTask={handleCreateIrrigationTask}
            showTimeline={true}
          />
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-4">
            {recommendations && recommendations.length > 0 ? (
              recommendations.map((recommendation) => (
                <ActionRecommendation
                  key={recommendation.id}
                  recommendation={recommendation}
                  onCreateTask={() => handleCreateRecommendationTask(recommendation)}
                />
              ))
            ) : (
              <div className="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
                <p className="text-gray-600" dir="rtl">لا توجد توصيات متاحة</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Usage Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6" dir="rtl">
        <h3 className="font-semibold text-blue-900 mb-3">كيفية الاستخدام:</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• اختر علامة التبويب (الرش، الري، أو التوصيات)</li>
          <li>• استعرض النوافذ المتاحة مع تفاصيلها الكاملة</li>
          <li>• انقر على "إنشاء مهمة" للنوافذ المثالية</li>
          <li>• سيتم إنشاء المهمة تلقائياً مع جميع التفاصيل</li>
          <li>• تابع المهام من قسم المهام في التطبيق</li>
        </ul>
      </div>
    </div>
  );
};

export default ActionWindowsDemo;
