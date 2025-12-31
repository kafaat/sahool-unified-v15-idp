/**
 * Alert Rules Component
 * مكون قواعد التنبيهات
 */

'use client';

import { useState } from 'react';
import { useAlertRules, useToggleAlertRule, useDeleteAlertRule } from '../hooks/useActuators';
import type { AlertRule } from '../types';
import { Bell, AlertCircle, Plus, Trash2, Power, Loader2 } from 'lucide-react';

const severityColors = {
  info: 'bg-blue-100 text-blue-800',
  warning: 'bg-yellow-100 text-yellow-800',
  critical: 'bg-red-100 text-red-800',
};

const severityLabels = {
  info: 'معلومة',
  warning: 'تحذير',
  critical: 'حرج',
};

const conditionLabels = {
  above: 'أعلى من',
  below: 'أقل من',
  between: 'بين',
  outside: 'خارج',
};

export function AlertRules() {
  const [showForm, setShowForm] = useState(false);
  const { data: rules, isLoading } = useAlertRules();
  const toggleMutation = useToggleAlertRule();
  const deleteMutation = useDeleteAlertRule();

  const handleToggle = async (ruleId: string, currentEnabled: boolean) => {
    try {
      await toggleMutation.mutateAsync({ id: ruleId, enabled: !currentEnabled });
    } catch (error) {
      console.error('Failed to toggle alert rule:', error);
    }
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm('هل أنت متأكد من حذف هذه القاعدة؟')) return;

    try {
      await deleteMutation.mutateAsync(ruleId);
    } catch (error) {
      console.error('Failed to delete alert rule:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="mr-3 text-gray-600">جاري التحميل...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <Bell className="w-6 h-6 ml-2 text-green-600" />
          قواعد التنبيهات
        </h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 ml-2" />
          إضافة قاعدة
        </button>
      </div>

      {/* Rules List */}
      {rules && rules.length > 0 ? (
        <div className="space-y-4">
          {rules.map((rule) => (
            <AlertRuleCard
              key={rule.id}
              rule={rule}
              onToggle={handleToggle}
              onDelete={handleDelete}
              isLoading={toggleMutation.isPending || deleteMutation.isPending}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">لا توجد قواعد تنبيهات</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 text-green-600 hover:text-green-700 font-medium"
          >
            إنشاء قاعدة جديدة
          </button>
        </div>
      )}
    </div>
  );
}

interface AlertRuleCardProps {
  rule: AlertRule;
  onToggle: (id: string, enabled: boolean) => void;
  onDelete: (id: string) => void;
  isLoading: boolean;
}

function AlertRuleCard({ rule, onToggle, onDelete, isLoading }: AlertRuleCardProps) {
  const getConditionText = (): string => {
    switch (rule.condition) {
      case 'above':
        return `${conditionLabels[rule.condition]} ${rule.threshold}`;
      case 'below':
        return `${conditionLabels[rule.condition]} ${rule.threshold}`;
      case 'between':
        return `${conditionLabels[rule.condition]} ${rule.threshold} و ${rule.thresholdMax}`;
      case 'outside':
        return `${conditionLabels[rule.condition]} ${rule.threshold} و ${rule.thresholdMax}`;
      default:
        return '';
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow p-6 ${!rule.enabled ? 'opacity-60' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{rule.nameAr}</h3>
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                severityColors[rule.severity]
              }`}
            >
              {severityLabels[rule.severity]}
            </span>
            {!rule.enabled && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                معطلة
              </span>
            )}
          </div>

          <p className="text-sm text-gray-600 mb-3">{rule.name}</p>

          <div className="space-y-2 text-sm">
            <div className="flex items-center text-gray-700">
              <span className="font-medium ml-2">المستشعر:</span>
              <span>{rule.sensorName}</span>
            </div>

            <div className="flex items-center text-gray-700">
              <span className="font-medium ml-2">الشرط:</span>
              <span>{getConditionText()}</span>
            </div>

            {rule.actionType && (
              <div className="flex items-center text-gray-700">
                <span className="font-medium ml-2">الإجراء:</span>
                <span>
                  {rule.actionType === 'notification' && 'إرسال إشعار'}
                  {rule.actionType === 'actuator' && 'تفعيل المُشغل'}
                  {rule.actionType === 'both' && 'إشعار + تفعيل المُشغل'}
                </span>
              </div>
            )}

            {rule.actuatorId && rule.actuatorAction && (
              <div className="text-xs text-gray-500">
                إجراء المُشغل:{' '}
                {rule.actuatorAction === 'turn_on' ? 'تشغيل' : 'إيقاف'}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onToggle(rule.id, rule.enabled)}
            disabled={isLoading}
            className={`p-2 rounded-lg transition-colors disabled:opacity-50 ${
              rule.enabled
                ? 'text-green-600 hover:bg-green-50'
                : 'text-gray-400 hover:bg-gray-50'
            }`}
            title={rule.enabled ? 'تعطيل' : 'تفعيل'}
          >
            <Power className="w-5 h-5" />
          </button>

          <button
            onClick={() => onDelete(rule.id)}
            disabled={isLoading}
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
            title="حذف"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
