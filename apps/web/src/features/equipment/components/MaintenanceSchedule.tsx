/**
 * Maintenance Schedule Component
 * مكون جدول الصيانة
 */

'use client';

import { useState } from 'react';
import { useMaintenanceRecords, useCompleteMaintenance } from '../hooks/useEquipment';
import type { MaintenanceRecord, MaintenanceStatus } from '../types';
import { Calendar, CheckCircle, AlertCircle, Loader2, Plus } from 'lucide-react';

interface MaintenanceScheduleProps {
  equipmentId?: string;
  limit?: number;
}

const statusColors: Record<MaintenanceStatus, string> = {
  scheduled: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
};

const statusLabels: Record<MaintenanceStatus, string> = {
  scheduled: 'مجدولة',
  in_progress: 'قيد التنفيذ',
  completed: 'مكتملة',
  overdue: 'متأخرة',
};

const typeLabels = {
  routine: 'دورية',
  repair: 'إصلاح',
  inspection: 'فحص',
  emergency: 'طارئة',
};

export function MaintenanceSchedule({ equipmentId, limit }: MaintenanceScheduleProps) {
  const [showForm, setShowForm] = useState(false);
  const { data: records, isLoading, error } = useMaintenanceRecords(equipmentId);
  const completeMutation = useCompleteMaintenance();

  const handleComplete = async (recordId: string) => {
    try {
      await completeMutation.mutateAsync({ id: recordId });
    } catch (error) {
      console.error('Failed to complete maintenance:', error);
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

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        حدث خطأ أثناء تحميل جدول الصيانة
      </div>
    );
  }

  const upcomingRecords = records?.filter(
    (r) => r.status === 'scheduled' && new Date(r.scheduledDate) >= new Date()
  ).slice(0, limit);
  const overdueRecords = records?.filter(
    (r) => r.status === 'scheduled' && new Date(r.scheduledDate) < new Date()
  ).slice(0, limit);
  const completedRecords = records?.filter((r) => r.status === 'completed').slice(0, limit || 5);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">جدول الصيانة</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 ml-2" />
          جدولة صيانة
        </button>
      </div>

      {/* Overdue Alerts */}
      {overdueRecords && overdueRecords.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <AlertCircle className="w-5 h-5 text-red-600 ml-2" />
            <h3 className="font-semibold text-red-800">صيانة متأخرة</h3>
          </div>
          <p className="text-sm text-red-700">
            لديك {overdueRecords.length} عملية صيانة متأخرة تحتاج إلى اهتمام فوري
          </p>
        </div>
      )}

      {/* Upcoming Maintenance */}
      {upcomingRecords && upcomingRecords.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <Calendar className="w-5 h-5 ml-2 text-blue-600" />
              الصيانة القادمة
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {upcomingRecords.map((record) => (
              <MaintenanceRecordItem
                key={record.id}
                record={record}
                onComplete={handleComplete}
                isCompleting={completeMutation.isPending}
              />
            ))}
          </div>
        </div>
      )}

      {/* Overdue Maintenance */}
      {overdueRecords && overdueRecords.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <AlertCircle className="w-5 h-5 ml-2 text-red-600" />
              الصيانة المتأخرة
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {overdueRecords.map((record) => (
              <MaintenanceRecordItem
                key={record.id}
                record={record}
                isOverdue
                onComplete={handleComplete}
                isCompleting={completeMutation.isPending}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Maintenance */}
      {completedRecords && completedRecords.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <CheckCircle className="w-5 h-5 ml-2 text-green-600" />
              الصيانة المكتملة
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {completedRecords.slice(0, 5).map((record) => (
              <MaintenanceRecordItem key={record.id} record={record} />
            ))}
          </div>
        </div>
      )}

      {records && records.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">لا توجد سجلات صيانة</p>
        </div>
      )}
    </div>
  );
}

interface MaintenanceRecordItemProps {
  record: MaintenanceRecord;
  isOverdue?: boolean;
  onComplete?: (id: string) => void;
  isCompleting?: boolean;
}

function MaintenanceRecordItem({
  record,
  isOverdue,
  onComplete,
  isCompleting,
}: MaintenanceRecordItemProps) {
  const canComplete = record.status !== 'completed' && onComplete;

  return (
    <div className={`p-4 ${isOverdue ? 'bg-red-50' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-medium text-gray-900">{record.descriptionAr}</h4>
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                statusColors[record.status]
              }`}
            >
              {statusLabels[record.status]}
            </span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
              {typeLabels[record.type]}
            </span>
          </div>

          <p className="text-sm text-gray-600 mb-2">{record.description}</p>

          <div className="flex flex-wrap gap-4 text-sm text-gray-500">
            <span className="flex items-center">
              <Calendar className="w-4 h-4 ml-1" />
              {new Date(record.scheduledDate).toLocaleDateString('ar-YE')}
            </span>

            {record.completedDate && (
              <span className="flex items-center text-green-600">
                <CheckCircle className="w-4 h-4 ml-1" />
                أُكملت في {new Date(record.completedDate).toLocaleDateString('ar-YE')}
              </span>
            )}

            {record.cost && (
              <span className="font-medium">التكلفة: {record.cost.toLocaleString('ar-YE')} ريال</span>
            )}
          </div>

          {record.equipmentName && (
            <p className="text-xs text-gray-500 mt-2">المعدة: {record.equipmentName}</p>
          )}
        </div>

        {canComplete && (
          <button
            onClick={() => onComplete(record.id)}
            disabled={isCompleting}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 text-sm flex items-center"
          >
            {isCompleting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <CheckCircle className="w-4 h-4 ml-1" />
                إكمال
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
