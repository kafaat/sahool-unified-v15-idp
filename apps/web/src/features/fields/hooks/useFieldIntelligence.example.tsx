/**
 * SAHOOL Field Intelligence Hooks - Usage Examples
 * أمثلة استخدام خطافات ذكاء الحقول
 *
 * This file demonstrates how to use the field intelligence hooks
 * in your React components for various use cases.
 */

'use client';

import React, { useState } from 'react';
import {
  useFieldZones,
  useFieldAlerts,
  useBestDays,
  useValidateDate,
  useFieldRecommendations,
  useCreateTaskFromAlert,
  useFieldIntelligence,
  useDebouncedDateValidation,
  type TaskFromAlertData,
} from './useFieldIntelligence';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Basic Field Zones Display
// مثال 1: عرض مناطق الحقل الأساسي
// ═══════════════════════════════════════════════════════════════════════════

export function FieldZonesExample({ fieldId }: { fieldId: string }) {
  const { data: zones, isLoading, isError, error } = useFieldZones(fieldId);

  if (isLoading) {
    return <div>جاري تحميل المناطق... / Loading zones...</div>;
  }

  if (isError) {
    return <div>خطأ: {error?.message} / Error: {error?.message}</div>;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Field Zones / مناطق الحقل</h2>
      {zones?.map((zone) => (
        <div key={zone.id} className="border p-4 rounded">
          <h3 className="font-semibold">{zone.name}</h3>
          <p>NDVI: {zone.ndviValue.toFixed(2)}</p>
          <p>Health: {zone.status}</p>
          <p>Area: {zone.area} hectares</p>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Real-time Field Alerts with Auto-refresh
// مثال 2: تنبيهات الحقل في الوقت الفعلي مع التحديث التلقائي
// ═══════════════════════════════════════════════════════════════════════════

export function FieldAlertsExample({ fieldId }: { fieldId: string }) {
  const { data: alerts, isLoading, refetch } = useFieldAlerts(fieldId);
  const createTask = useCreateTaskFromAlert();

  const handleCreateTask = (alertId: string) => {
    const taskData: TaskFromAlertData = {
      title: 'Task from Alert',
      titleAr: 'مهمة من تنبيه',
      priority: 'high',
    };

    createTask.mutate({
      alertId,
      taskData,
    }, {
      onSuccess: (task) => {
        console.log('Task created:', task);
        alert(`Task ${task.id} created successfully!`);
      },
      onError: (error) => {
        console.error('Failed to create task:', error);
        alert('Failed to create task');
      },
    });
  };

  if (isLoading) {
    return <div>جاري تحميل التنبيهات... / Loading alerts...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Field Alerts / تنبيهات الحقل</h2>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          تحديث / Refresh
        </button>
      </div>

      {alerts?.length === 0 && (
        <p className="text-gray-500">No active alerts / لا توجد تنبيهات نشطة</p>
      )}

      {alerts?.map((alert) => (
        <div
          key={alert.id}
          className={`border p-4 rounded ${
            alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
            alert.severity === 'warning' ? 'border-yellow-500 bg-yellow-50' :
            'border-blue-500 bg-blue-50'
          }`}
        >
          <h3 className="font-semibold">{alert.titleAr} / {alert.title}</h3>
          <p>{alert.messageAr}</p>
          <p className="text-sm text-gray-600">Severity: {alert.severity}</p>
          <button
            onClick={() => handleCreateTask(alert.id)}
            disabled={createTask.isPending}
            className="mt-2 px-3 py-1 bg-green-500 text-white rounded text-sm"
          >
            {createTask.isPending ? 'جاري الإنشاء...' : 'إنشاء مهمة / Create Task'}
          </button>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Best Days for Activity Planning
// مثال 3: أفضل الأيام للتخطيط للنشاط
// ═══════════════════════════════════════════════════════════════════════════

export function BestDaysExample() {
  const [activity, setActivity] = useState('زراعة');
  const [days, setDays] = useState(30);

  const { data: bestDays, isLoading } = useBestDays(activity, {
    days,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Best Days Finder / محدد أفضل الأيام</h2>

      <div className="space-y-2">
        <div>
          <label className="block text-sm font-medium">
            Activity / النشاط:
          </label>
          <select
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            className="mt-1 block w-full rounded border p-2"
          >
            <option value="زراعة">زراعة / Planting</option>
            <option value="حصاد">حصاد / Harvesting</option>
            <option value="ري">ري / Irrigation</option>
            <option value="تسميد">تسميد / Fertilizing</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium">
            Days to Search / عدد الأيام:
          </label>
          <input
            type="number"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            min={7}
            max={90}
            className="mt-1 block w-full rounded border p-2"
          />
        </div>
      </div>

      {isLoading && <p>جاري البحث... / Searching...</p>}

      {bestDays && (
        <div className="space-y-2">
          <h3 className="font-semibold">
            أفضل {bestDays.length} أيام / Best {bestDays.length} Days:
          </h3>
          {bestDays.map((day) => (
            <div key={day.date} className="border p-3 rounded bg-green-50">
              <p className="font-medium">{day.date}</p>
              <p className="text-sm">Suitability: {day.suitabilityAr}</p>
              <p className="text-sm">Score: {day.score}/100</p>
              {day.reasonsAr && day.reasonsAr.length > 0 && (
                <p className="text-sm text-gray-600">{day.reasonsAr[0]}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Date Validation for Activity Planning
// مثال 4: التحقق من صحة التاريخ للتخطيط للنشاط
// ═══════════════════════════════════════════════════════════════════════════

export function DateValidationExample() {
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0] as string
  );
  const [activity, setActivity] = useState('زراعة');

  const { data: validation, isLoading } = useValidateDate(
    selectedDate || '',
    activity,
    { enabled: !!selectedDate }
  );

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Date Validator / محقق التاريخ</h2>

      <div className="space-y-2">
        <div>
          <label className="block text-sm font-medium">
            Date / التاريخ:
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="mt-1 block w-full rounded border p-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium">
            Activity / النشاط:
          </label>
          <select
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            className="mt-1 block w-full rounded border p-2"
          >
            <option value="زراعة">زراعة / Planting</option>
            <option value="حصاد">حصاد / Harvesting</option>
            <option value="ري">ري / Irrigation</option>
          </select>
        </div>
      </div>

      {isLoading && <p>جاري التحقق... / Validating...</p>}

      {validation && (
        <div
          className={`border p-4 rounded ${
            validation.suitable && validation.score > 70
              ? 'bg-green-50 border-green-500'
              : validation.score > 40
              ? 'bg-yellow-50 border-yellow-500'
              : 'bg-red-50 border-red-500'
          }`}
        >
          <h3 className="font-semibold">
            {validation.suitable ? '✓ تاريخ صالح / Valid Date' : '✗ تاريخ غير مثالي / Suboptimal Date'}
          </h3>
          <p className="mt-2">Score: {validation.score}/100</p>
          <p className="mt-2">Rating: {validation.ratingAr}</p>
          {validation.reasonsAr && validation.reasonsAr.length > 0 && (
            <div className="mt-2">
              <p className="font-medium text-sm">Reasons:</p>
              <ul className="list-disc list-inside text-sm">
                {validation.reasonsAr.map((reason, i) => (
                  <li key={i}>{reason}</li>
                ))}
              </ul>
            </div>
          )}

          {validation.warnings && validation.warnings.length > 0 && (
            <div className="mt-3">
              <p className="font-medium text-sm">Warnings:</p>
              <ul className="list-disc list-inside text-sm">
                {validation.warningsAr?.map((warning, i) => (
                  <li key={i}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Field Recommendations Display
// مثال 5: عرض توصيات الحقل
// ═══════════════════════════════════════════════════════════════════════════

export function FieldRecommendationsExample({ fieldId }: { fieldId: string }) {
  const { data: recommendations, isLoading, refetch } = useFieldRecommendations(fieldId);

  if (isLoading) {
    return <div>جاري تحميل التوصيات... / Loading recommendations...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">
          Field Recommendations / توصيات الحقل
        </h2>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-500 text-white rounded text-sm"
        >
          تحديث / Refresh
        </button>
      </div>

      {recommendations?.length === 0 && (
        <p className="text-gray-500">
          No recommendations available / لا توجد توصيات متاحة
        </p>
      )}

      {recommendations?.map((rec) => (
        <div
          key={rec.id}
          className={`border p-4 rounded ${
            rec.priority === 'urgent' ? 'border-red-500 bg-red-50' :
            rec.priority === 'high' ? 'border-orange-500 bg-orange-50' :
            rec.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
            'border-blue-500 bg-blue-50'
          }`}
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold">{rec.titleAr}</h3>
              <p className="text-sm text-gray-600">{rec.title}</p>
            </div>
            <span
              className={`px-2 py-1 text-xs rounded ${
                rec.priority === 'urgent' ? 'bg-red-200 text-red-800' :
                rec.priority === 'high' ? 'bg-orange-200 text-orange-800' :
                rec.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                'bg-blue-200 text-blue-800'
              }`}
            >
              {rec.priority}
            </span>
          </div>

          <p className="mt-2">{rec.descriptionAr}</p>

          {rec.actionItems && rec.actionItems.length > 0 && (
            <div className="mt-3">
              <p className="font-medium text-sm">Action Items:</p>
              <ul className="list-disc list-inside text-sm space-y-1">
                {rec.actionItems.map((item, idx) => (
                  <li key={idx} className={item.required ? 'font-semibold' : ''}>
                    {item.actionAr} {item.required && '(مطلوب)'}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {rec.expectedBenefitAr && (
            <p className="mt-2 text-sm text-green-700">
              <strong>Expected Benefit:</strong> {rec.expectedBenefitAr}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 6: Composite Hook - Complete Field Intelligence Dashboard
// مثال 6: خطاف مركب - لوحة معلومات ذكاء الحقل الكاملة
// ═══════════════════════════════════════════════════════════════════════════

export function FieldIntelligenceDashboard({ fieldId }: { fieldId: string }) {
  const intelligence = useFieldIntelligence(fieldId);

  if (intelligence.isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">جاري تحميل بيانات الذكاء... / Loading intelligence data...</p>
        </div>
      </div>
    );
  }

  if (intelligence.isError) {
    return (
      <div className="border border-red-500 bg-red-50 p-4 rounded">
        <p className="text-red-700">
          خطأ في تحميل البيانات / Error loading data
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">
        Field Intelligence Dashboard / لوحة معلومات ذكاء الحقل
      </h1>

      {/* Zones Section */}
      <section className="border rounded p-4">
        <h2 className="text-lg font-semibold mb-3">
          Zones ({intelligence.zones.data?.length || 0}) / المناطق
        </h2>
        {intelligence.zones.isLoading && <p>Loading zones...</p>}
        {intelligence.zones.data?.map((zone) => (
          <div key={zone.id} className="mb-2 p-2 bg-gray-50 rounded">
            <p className="font-medium">{zone.name}</p>
            <p className="text-sm">NDVI: {zone.ndviValue.toFixed(2)} - {zone.status}</p>
          </div>
        ))}
      </section>

      {/* Alerts Section */}
      <section className="border rounded p-4">
        <h2 className="text-lg font-semibold mb-3">
          Active Alerts ({intelligence.alerts.data?.length || 0}) / التنبيهات النشطة
        </h2>
        {intelligence.alerts.isLoading && <p>Loading alerts...</p>}
        {intelligence.alerts.data?.length === 0 && (
          <p className="text-gray-500">No active alerts</p>
        )}
        {intelligence.alerts.data?.map((alert) => (
          <div
            key={alert.id}
            className={`mb-2 p-3 rounded ${
              alert.severity === 'critical' ? 'bg-red-100' :
              alert.severity === 'warning' ? 'bg-yellow-100' :
              'bg-blue-100'
            }`}
          >
            <p className="font-medium">{alert.titleAr}</p>
            <p className="text-sm">{alert.messageAr}</p>
            <button
              onClick={() => intelligence.createTask.mutate({
                alertId: alert.id,
                taskData: {
                  title: `Task for: ${alert.title}`,
                  titleAr: `مهمة لـ: ${alert.titleAr}`,
                  priority: alert.severity === 'critical' ? 'urgent' : 'high',
                },
              })}
              disabled={intelligence.createTask.isPending}
              className="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Create Task / إنشاء مهمة
            </button>
          </div>
        ))}
      </section>

      {/* Recommendations Section */}
      <section className="border rounded p-4">
        <h2 className="text-lg font-semibold mb-3">
          Recommendations ({intelligence.recommendations.data?.length || 0}) / التوصيات
        </h2>
        {intelligence.recommendations.isLoading && <p>Loading recommendations...</p>}
        {intelligence.recommendations.data?.length === 0 && (
          <p className="text-gray-500">No recommendations available</p>
        )}
        {intelligence.recommendations.data?.map((rec) => (
          <div key={rec.id} className="mb-2 p-3 bg-green-50 rounded">
            <p className="font-medium">{rec.titleAr}</p>
            <p className="text-sm text-gray-600">{rec.descriptionAr}</p>
            <span className="text-xs px-2 py-1 bg-green-200 rounded mt-1 inline-block">
              {rec.priority}
            </span>
          </div>
        ))}
      </section>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 7: Debounced Date Validation (for forms)
// مثال 7: التحقق من التاريخ مع التأخير (للنماذج)
// ═══════════════════════════════════════════════════════════════════════════

export function DebouncedDateValidationForm() {
  const [date, setDate] = useState('');
  const [activity] = useState('زراعة');

  // This will automatically debounce API calls
  const validation = useDebouncedDateValidation(date, activity);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">
        Form with Date Validation / نموذج مع التحقق من التاريخ
      </h2>

      <div>
        <label className="block text-sm font-medium mb-1">
          Select Date / اختر التاريخ:
        </label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-full rounded border p-2"
        />
      </div>

      {validation.isValidating && (
        <p className="text-sm text-gray-500">جاري التحقق... / Validating...</p>
      )}

      {validation.data && date && (
        <div
          className={`p-3 rounded text-sm ${
            validation.isSuitable && (validation.score || 0) > 70
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          <p>Suitability Score: {validation.score}/100</p>
          <p>Rating: {validation.rating}</p>
          {validation.warnings && validation.warnings.length > 0 && (
            <ul className="mt-2 list-disc list-inside">
              {validation.warnings.map((warning, i) => (
                <li key={i}>{warning}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Export all examples
// ═══════════════════════════════════════════════════════════════════════════

export default {
  FieldZonesExample,
  FieldAlertsExample,
  BestDaysExample,
  DateValidationExample,
  FieldRecommendationsExample,
  FieldIntelligenceDashboard,
  DebouncedDateValidationForm,
};
