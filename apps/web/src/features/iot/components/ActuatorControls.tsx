/**
 * Actuator Controls Component
 * مكون التحكم بالمُشغلات
 */

'use client';

import { useActuators, useControlActuator, useSetActuatorMode } from '../hooks/useActuators';
import type { Actuator, ActuatorStatus } from '../types';
import { Power, Loader2, Settings, Zap } from 'lucide-react';
import { logger } from '@/lib/logger';

const statusColors: Record<string, string> = {
  on: 'bg-green-100 text-green-800',
  off: 'bg-gray-100 text-gray-800',
  auto: 'bg-blue-100 text-blue-800',
  online: 'bg-green-100 text-green-800',
  offline: 'bg-gray-100 text-gray-800',
  error: 'bg-red-100 text-red-800',
};

const statusLabels: Record<string, string> = {
  on: 'مُشغّل',
  off: 'مُطفأ',
  auto: 'تلقائي',
  online: 'متصل',
  offline: 'غير متصل',
  error: 'خطأ',
};

const typeLabels = {
  valve: 'صمام',
  pump: 'مضخة',
  fan: 'مروحة',
  heater: 'سخان',
  light: 'إضاءة',
  sprinkler: 'رشاش',
};

const typeIcons = {
  valve: '🚰',
  pump: '⚙️',
  fan: '🌀',
  heater: '🔥',
  light: '💡',
  sprinkler: '💦',
};

export function ActuatorControls() {
  const { data: actuators, isLoading } = useActuators();
  const controlMutation = useControlActuator();
  const setModeMutation = useSetActuatorMode();

  const handleToggle = async (actuatorId: string, currentStatus: ActuatorStatus) => {
    const action = currentStatus === 'on' ? 'off' : 'on';
    // Confirm before toggling physical equipment (irrigation valves, pumps, etc.)
    // to prevent accidental activation.
    const confirmMessage =
      action === 'on'
        ? 'Turn ON actuator? — تشغيل المشغل؟'
        : 'Turn OFF actuator? — إيقاف المشغل؟';
    if (typeof window !== 'undefined' && !window.confirm(confirmMessage)) {
      return;
    }
    try {
      await controlMutation.mutateAsync({
        actuatorId,
        action,
      });
    } catch (error) {
      logger.error('Failed to control actuator:', error);
    }
  };

  const handleModeChange = async (
    actuatorId: string,
    mode: 'manual' | 'automatic' | 'scheduled'
  ) => {
    try {
      await setModeMutation.mutateAsync({ actuatorId, mode });
    } catch (error) {
      logger.error('Failed to set actuator mode:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="ms-3 text-gray-600">جاري التحميل...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <Zap className="w-6 h-6 ml-2 text-green-600" />
          التحكم بالمُشغلات
        </h2>
      </div>

      {actuators && actuators.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {actuators.map((actuator) => (
            <ActuatorControlCard
              key={actuator.id}
              actuator={actuator}
              onToggle={handleToggle}
              onModeChange={handleModeChange}
              isLoading={controlMutation.isPending || setModeMutation.isPending}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">لا توجد مُشغلات</p>
        </div>
      )}
    </div>
  );
}

interface ActuatorControlCardProps {
  actuator: Actuator;
  onToggle: (id: string, status: ActuatorStatus) => void;
  onModeChange: (id: string, mode: 'manual' | 'automatic' | 'scheduled') => void;
  isLoading: boolean;
}

function ActuatorControlCard({
  actuator,
  onToggle,
  onModeChange,
  isLoading,
}: ActuatorControlCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className="text-3xl">{typeIcons[actuator.type]}</div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{actuator.nameAr}</h3>
            <p className="text-sm text-gray-500">{actuator.name}</p>
            <p className="text-xs text-gray-400 mt-1">{typeLabels[actuator.type]}</p>
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[actuator.status]}`}
        >
          {statusLabels[actuator.status]}
        </span>
      </div>

      {/* Control Button */}
      <button
        onClick={() => onToggle(actuator.id, actuator.status)}
        disabled={isLoading || actuator.controlMode !== 'manual'}
        className={`w-full py-3 rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center ${
          actuator.status === 'on'
            ? 'bg-green-600 text-white hover:bg-green-700'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <>
            <Power className="w-5 h-5 ml-2" />
            {actuator.status === 'on' ? 'إيقاف' : 'تشغيل'}
          </>
        )}
      </button>

      {/* Mode Selector */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700 flex items-center">
          <Settings className="w-4 h-4 ml-1" />
          وضع التحكم
        </label>
        <select
          value={actuator.controlMode}
          onChange={(e) =>
            onModeChange(actuator.id, e.target.value as 'manual' | 'automatic' | 'scheduled')
          }
          disabled={isLoading}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm disabled:opacity-50"
        >
          <option value="manual">يدوي</option>
          <option value="automatic">تلقائي</option>
          <option value="scheduled">مجدول</option>
        </select>
      </div>

      {/* Additional Info */}
      <div className="pt-3 border-t border-gray-100 space-y-1 text-sm text-gray-600">
        {actuator.location && (
          <p className="text-xs">{actuator.location.fieldName || 'موقع المُشغل'}</p>
        )}
        {actuator.linkedSensorName && (
          <p className="text-xs">مرتبط بـ: {actuator.linkedSensorName}</p>
        )}
        <p className="text-xs text-gray-400">معرف الجهاز: {actuator.deviceId}</p>
      </div>
    </div>
  );
}
