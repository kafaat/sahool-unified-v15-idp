'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Droplets,
  Search,
  Plus,
  Calendar,
  Clock,
  TrendingUp,
  AlertTriangle,
  X,
  Play,
  Pause,
  Edit2,
  Trash2,
} from 'lucide-react';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/stores/auth.store';
import { apiClient } from '@/lib/api';
import type { IrrigationScheduleType, IrrigationFrequency as ApiIrrigationFrequency, IrrigationSchedule as ApiIrrigationSchedule } from '@/lib/api/types';

type IrrigationStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'overdue';
type IrrigationType = 'drip' | 'sprinkler' | 'pivot' | 'flood' | 'manual';

interface IrrigationSchedule {
  id: string;
  fieldId: string;
  fieldName: string;
  type: IrrigationType;
  status: IrrigationStatus;
  scheduledAt: string;
  duration: number;
  waterAmount: number;
  completedAt?: string;
  progress?: number;
  schedule?: Record<string, unknown>;
  nextRun?: string;
  createdAt?: string;
  updatedAt?: string;
  name?: string;
  startDate?: string;
  frequency?: string;
}

/** Map API IrrigationSchedule to the local UI interface */
function fromApiSchedule(s: ApiIrrigationSchedule): IrrigationSchedule {
  // Safely map API schedule type (manual/automatic/scheduled) to UI type (drip/sprinkler/pivot/flood/manual)
  const validUiTypes: readonly IrrigationType[] = ['drip', 'sprinkler', 'pivot', 'flood', 'manual'] as const;
  const mappedType: IrrigationType = validUiTypes.includes(s.type as IrrigationType)
    ? (s.type as IrrigationType)
    : 'manual';

  // Safely map API status (active/paused/completed) to UI status (scheduled/in_progress/completed/cancelled/overdue)
  const statusMap: Record<string, IrrigationStatus> = {
    active: 'in_progress',
    paused: 'scheduled',
    completed: 'completed',
  };
  const mappedStatus: IrrigationStatus = statusMap[s.status] ?? 'scheduled';

  return {
    id: s.id,
    fieldId: s.fieldId,
    fieldName: s.fieldName ?? '',
    type: mappedType,
    status: mappedStatus,
    scheduledAt: s.startDate,
    duration: s.duration,
    waterAmount: s.waterAmount,
    schedule: s.schedule as Record<string, unknown> | undefined,
    nextRun: s.nextRun,
    createdAt: s.createdAt,
    updatedAt: s.updatedAt,
    name: s.name,
    startDate: s.startDate,
    frequency: s.frequency,
  };
}

type Field = { id: string; name: string; name_ar?: string };

/**
 * Map the UI irrigation type (drip/sprinkler/pivot/flood/manual) to the API
 * contract type (manual/automatic/scheduled). Drip, sprinkler, pivot, and
 * flood are all scheduled types; manual stays as manual.
 */
function toApiIrrigationType(type: IrrigationType): IrrigationScheduleType {
  if (type === 'manual') return 'manual';
  return 'scheduled';
}

/**
 * Map the UI frequency (daily/weekly/biweekly/custom) to the API contract
 * frequency (daily/weekly/custom). biweekly falls back to 'custom'.
 */
function toApiFrequency(frequency: string): ApiIrrigationFrequency {
  if (frequency === 'daily' || frequency === 'weekly' || frequency === 'custom') {
    return frequency as ApiIrrigationFrequency;
  }
  return 'custom';
}

const initialMockSchedules: IrrigationSchedule[] = [
  {
    id: '1',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    type: 'drip',
    status: 'scheduled',
    scheduledAt: '2025-01-25T06:00:00Z',
    duration: 120,
    waterAmount: 500,
    schedule: { timeOfDay: '06:00' },
    nextRun: '2025-01-26T06:00:00Z',
    createdAt: '2025-01-20T00:00:00Z',
    updatedAt: '2025-01-25T06:00:00Z',
  },
  {
    id: '2',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    type: 'pivot',
    status: 'in_progress',
    scheduledAt: '2025-01-25T04:00:00Z',
    duration: 180,
    waterAmount: 1200,
    createdAt: '2025-01-18T00:00:00Z',
    updatedAt: '2025-01-25T04:00:00Z',
  },
  {
    id: '3',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    type: 'sprinkler',
    status: 'completed',
    scheduledAt: '2025-01-24T18:00:00Z',
    duration: 90,
    waterAmount: 800,
    completedAt: '2025-01-24T19:30:00Z',
  },
  {
    id: '4',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    type: 'flood',
    status: 'overdue',
    scheduledAt: '2025-01-24T08:00:00Z',
    duration: 240,
    waterAmount: 2000,
    schedule: { interval: 3 },
    createdAt: '2025-01-10T00:00:00Z',
    updatedAt: '2025-01-24T08:00:00Z',
  },
  {
    id: '5',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    type: 'drip',
    status: 'scheduled',
    scheduledAt: '2025-01-25T16:00:00Z',
    duration: 60,
    waterAmount: 200,
    schedule: { timeOfDay: '16:00' },
    nextRun: '2025-01-26T16:00:00Z',
    createdAt: '2025-01-22T00:00:00Z',
    updatedAt: '2025-01-25T16:00:00Z',
  },
];

const irrigationTypes: Record<IrrigationType, { label: string; labelAr: string }> = {
  drip: { label: 'Drip', labelAr: 'تنقيط' },
  sprinkler: { label: 'Sprinkler', labelAr: 'رشاشات' },
  pivot: { label: 'Pivot', labelAr: 'محوري' },
  flood: { label: 'Flood', labelAr: 'غمر' },
  manual: { label: 'Manual', labelAr: 'يدوي' },
};

// Aliases used by the template
const scheduleTypes = irrigationTypes;
type IrrigationFrequency = 'daily' | 'weekly' | 'biweekly' | 'custom';
const frequencies: Record<string, { label: string; labelAr: string }> = {
  daily: { label: 'Daily', labelAr: 'يومي' },
  weekly: { label: 'Weekly', labelAr: 'أسبوعي' },
  biweekly: { label: 'Bi-weekly', labelAr: 'كل أسبوعين' },
  custom: { label: 'Custom', labelAr: 'مخصص' },
};

const EMPTY_FORM = {
  fieldName: '',
  fieldId: '',
  name: '',
  type: 'drip' as IrrigationType,
  scheduledAt: '',
  startDate: '',
  frequency: 'daily' as IrrigationFrequency,
  duration: 60,
  waterAmount: 100,
};

export default function IrrigationClient() {
  const [schedules, setSchedules] = useState(initialMockSchedules);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<IrrigationStatus | 'all'>('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [deleteTarget, setDeleteTarget] = useState<IrrigationSchedule | null>(null);
  const [fields, setFields] = useState<Field[]>([]);
  const { showToast } = useToast();
  const { user } = useAuth();
  const tenantId = user?.tenant_id;

  // Load available fields for the field selector (skip until tenant is known)
  useEffect(() => {
    if (!tenantId) return;
    const tid = tenantId;
    let cancelled = false;
    async function loadFields() {
      try {
        const response = await apiClient.getFields(tid, { limit: 200 });
        if (!cancelled && response.success && response.data) {
          setFields(response.data);
        }
      } catch {
        // Fields will remain empty; the selector will show no options
      }
    }
    loadFields();
    return () => {
      cancelled = true;
    };
  }, [tenantId]);

  // Load schedules from API on mount
  useEffect(() => {
    let cancelled = false;
    async function loadSchedules() {
      try {
        const response = await apiClient.getIrrigationSchedules();
        if (!cancelled && response.success && response.data) {
          setSchedules(response.data.map(fromApiSchedule));
        }
      } catch {
        // API unavailable - keep mock data for offline-first UX
      }
    }
    loadSchedules();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredSchedules = useMemo(() => {
    return schedules.filter((schedule) => {
      const matchesSearch = !searchTerm || schedule.fieldName.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || schedule.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [schedules, searchTerm, statusFilter]);

  const getStatusBadge = (status: IrrigationStatus) => {
    const styles = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800',
      overdue: 'bg-red-100 text-red-800',
    };
    const labels = {
      scheduled: 'مجدول',
      in_progress: 'جاري',
      completed: 'مكتمل',
      cancelled: 'ملغي',
      overdue: 'متأخر',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ar-SA', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const totalWaterToday = schedules
    .filter((s) => s.status !== 'cancelled')
    .reduce((sum, s) => sum + s.waterAmount, 0);

  const activeCount = schedules.filter((s) => s.status === 'in_progress').length;
  const cancelledCount = schedules.filter((s) => s.status === 'cancelled').length;
  const overdueCount = schedules.filter((s) => s.status === 'overdue').length;

  // CRUD handlers
  const openCreate = useCallback(() => {
    setFormData(EMPTY_FORM);
    setEditingId(null);
    setModalOpen(true);
  }, []);

  const openEdit = useCallback((schedule: IrrigationSchedule) => {
    setFormData({
      fieldName: schedule.fieldName || '',
      fieldId: schedule.fieldId || '',
      name: schedule.name || '',
      type: schedule.type,
      scheduledAt: schedule.scheduledAt || '',
      startDate: (schedule.startDate || '').slice(0, 16),
      frequency: (schedule.frequency || 'daily') as IrrigationFrequency,
      duration: schedule.duration,
      waterAmount: schedule.waterAmount,
    });
    setEditingId(schedule.id);
    setModalOpen(true);
  }, []);

  const handleSave = useCallback(async () => {
    if (!formData.fieldName.trim()) {
      showToast({
        type: 'warning',
        message: 'Please enter field name',
        messageAr: 'يرجى إدخال اسم الحقل',
      });
      return;
    }

    if (!formData.fieldId) {
      showToast({
        type: 'warning',
        message: 'Please select a field',
        messageAr: 'يرجى اختيار الحقل',
      });
      return;
    }

    if (editingId) {
      // Preserve the existing schedule's fieldId as fallback
      const existingSchedule = schedules.find((s) => s.id === editingId);
      try {
        const response = await apiClient.updateIrrigationSchedule(editingId, {
          fieldId: formData.fieldId || existingSchedule?.fieldId || '',
          name: formData.name,
          type: toApiIrrigationType(formData.type),
          startDate: formData.startDate || formData.scheduledAt,
          frequency: toApiFrequency(formData.frequency),
          duration: formData.duration,
          waterAmount: formData.waterAmount,
        });
        if (response.success && response.data) {
          // Map server-returned API data into the UI schedule shape
          const mapped = fromApiSchedule(response.data);
          setSchedules((prev) =>
            prev.map((s) => (s.id === editingId ? mapped : s))
          );
        } else {
          // Optimistic update on non-critical error
          setSchedules((prev) =>
            prev.map((s) =>
              s.id === editingId
                ? {
                    ...s,
                    fieldName: formData.fieldName,
                    name: formData.name,
                    type: formData.type,
                    scheduledAt: formData.startDate || formData.scheduledAt || s.scheduledAt,
                    startDate: formData.startDate || formData.scheduledAt,
                    frequency: formData.frequency,
                    duration: formData.duration,
                    waterAmount: formData.waterAmount,
                  }
                : s
            )
          );
        }
      } catch {
        // Optimistic update for offline-first UX
        setSchedules((prev) =>
          prev.map((s) =>
            s.id === editingId
              ? {
                  ...s,
                  fieldName: formData.fieldName,
                  name: formData.name,
                  type: formData.type,
                  scheduledAt: formData.startDate || formData.scheduledAt || s.scheduledAt,
                  startDate: formData.startDate || formData.scheduledAt,
                  frequency: formData.frequency,
                  duration: formData.duration,
                  waterAmount: formData.waterAmount,
                }
              : s
          )
        );
      }
      showToast({ type: 'success', message: 'Schedule updated', messageAr: 'تم تحديث الجدول' });
    } else {
      try {
        const response = await apiClient.createIrrigationSchedule({
          fieldId: formData.fieldId,
          name: formData.name || formData.fieldName,
          type: toApiIrrigationType(formData.type),
          startDate: formData.startDate || formData.scheduledAt || new Date().toISOString(),
          frequency: toApiFrequency(formData.frequency),
          duration: formData.duration,
          waterAmount: formData.waterAmount,
        });
        if (response.success && response.data) {
          setSchedules((prev) => [...prev, fromApiSchedule(response.data)]);
        } else {
          // Optimistic insert for offline-first UX
          const newSchedule: IrrigationSchedule = {
            id: crypto.randomUUID(),
            fieldId: formData.fieldId,
            fieldName: formData.fieldName,
            type: formData.type,
            status: 'scheduled',
            scheduledAt: formData.scheduledAt || new Date().toISOString(),
            duration: formData.duration,
            waterAmount: formData.waterAmount,
          };
          setSchedules((prev) => [...prev, newSchedule]);
        }
      } catch {
        // Optimistic insert for offline-first UX
        const newSchedule: IrrigationSchedule = {
          id: crypto.randomUUID(),
          fieldId: formData.fieldId,
          fieldName: formData.fieldName,
          type: formData.type,
          status: 'scheduled',
          scheduledAt: formData.scheduledAt || new Date().toISOString(),
          duration: formData.duration,
          waterAmount: formData.waterAmount,
        };
        setSchedules((prev) => [...prev, newSchedule]);
      }
      showToast({ type: 'success', message: 'Schedule created', messageAr: 'تم إنشاء الجدول' });
    }
    setModalOpen(false);
  }, [formData, editingId, showToast]);

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    try {
      const response = await apiClient.deleteIrrigationSchedule(deleteTarget.id);
      if (!response.success) {
        showToast({
          type: 'error',
          message: 'Failed to delete schedule',
          messageAr: 'فشل حذف الجدول',
        });
        setDeleteTarget(null);
        return;
      }
    } catch {
      // Network failure - optimistic delete for offline-first
    }
    setSchedules((prev) => prev.filter((s) => s.id !== deleteTarget.id));
    showToast({ type: 'success', message: 'Schedule deleted', messageAr: 'تم حذف الجدول' });
    setDeleteTarget(null);
  }, [deleteTarget, showToast]);

  const handleStart = useCallback(
    (id: string) => {
      setSchedules((prev) =>
        prev.map((s) =>
          s.id === id ? { ...s, status: 'in_progress' as IrrigationStatus, progress: 0 } : s
        )
      );
      showToast({ type: 'info', message: 'Irrigation started', messageAr: 'بدأ الري' });
    },
    [showToast]
  );

  const handleStop = useCallback(
    (id: string) => {
      setSchedules((prev) =>
        prev.map((s) =>
          s.id === id
            ? {
                ...s,
                status: 'completed' as IrrigationStatus,
                completedAt: new Date().toISOString(),
              }
            : s
        )
      );
      showToast({ type: 'success', message: 'Irrigation completed', messageAr: 'تم إكمال الري' });
    },
    [showToast]
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة الري</h1>
          <p className="text-gray-500 mt-1">Irrigation Management</p>
        </div>
        <button
          onClick={openCreate}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>جدولة ري</span>
        </button>
      </div>

      {/* Overdue Alert */}
      {overdueCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 animate-shake">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              تنبيه: {overdueCount} جدول ري متأخر يتطلب اهتماماً
            </span>
          </div>
        </div>
      )}

      {/* Paused Alert */}
      {cancelledCount > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 animate-shake">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span className="font-medium text-orange-800">
              تنبيه: {cancelledCount} جدول ري متوقف يتطلب اهتماماً
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Droplets className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">استهلاك اليوم</div>
              <div className="text-xl font-bold text-blue-600">
                {totalWaterToday.toLocaleString()} م³
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center ${activeCount > 0 ? 'animate-pulse-dot' : ''}`}
            >
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">نشط الآن</div>
              <div className="text-xl font-bold text-green-600">{activeCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوقف</div>
              <div className="text-xl font-bold text-orange-600">{cancelledCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-sahool-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">كفاءة الري</div>
              <div className="text-xl font-bold text-sahool-green-600">87%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن حقل أو جدول..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
            aria-label="بحث في جداول الري"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as IrrigationStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          aria-label="تصفية حسب الحالة"
        >
          <option value="all">جميع الحالات</option>
          <option value="active">نشط</option>
          <option value="paused">متوقف</option>
          <option value="completed">مكتمل</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الاسم</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">النوع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">التكرار</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  تاريخ البدء
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المدة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  كمية المياه
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredSchedules.map((schedule, index) => (
                <tr
                  key={schedule.id}
                  className="hover:bg-gray-50 transition-colors animate-slide-in-up"
                  style={{ animationDelay: `${index * 40}ms`, animationFillMode: 'both' }}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Droplets className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{schedule.name || schedule.fieldName}</div>
                        {schedule.name && (
                          <div className="text-xs text-gray-500">{schedule.fieldName}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {scheduleTypes[schedule.type].labelAr}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {schedule.frequency ? frequencies[schedule.frequency]?.labelAr ?? schedule.frequency : '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {schedule.startDate ? formatDate(schedule.startDate) : formatDate(schedule.scheduledAt)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">{schedule.duration} دقيقة</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{schedule.waterAmount} م³</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col gap-1">
                      {getStatusBadge(schedule.status)}
                      {schedule.status === 'in_progress' && schedule.progress !== undefined && (
                        <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-yellow-500 rounded-full transition-all duration-1000 animate-progress-fill"
                            style={
                              {
                                '--progress-width': `${schedule.progress}%`,
                                width: `${schedule.progress}%`,
                              } as React.CSSProperties
                            }
                          />
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      {schedule.status === 'scheduled' && (
                        <button
                          onClick={() => handleStart(schedule.id)}
                          className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="استئناف الري"
                          aria-label={`استئناف ري ${schedule.name || schedule.fieldName}`}
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {schedule.status === 'in_progress' && (
                        <button
                          onClick={() => handleStop(schedule.id)}
                          className="p-1.5 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                          title="إيقاف الري مؤقتاً"
                          aria-label={`إيقاف ري ${schedule.name || schedule.fieldName}`}
                        >
                          <Pause className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => openEdit(schedule)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="تعديل"
                        aria-label={`تعديل جدول ${schedule.name || schedule.fieldName}`}
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(schedule)}
                        className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="حذف"
                        aria-label={`حذف جدول ${schedule.name || schedule.fieldName}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-[9998] flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setModalOpen(false)}
          />
          <div className="relative bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 animate-scale-in">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                {editingId ? 'تعديل جدول الري' : 'جدولة ري جديد'}
              </h2>
              <button
                onClick={() => setModalOpen(false)}
                className="p-1.5 hover:bg-gray-100 rounded-lg"
                aria-label="إغلاق"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  اسم الجدول <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
                  placeholder="مثال: ري صباحي - الحقل الشمالي"
                />
              </div>
              {!editingId && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الحقل <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={formData.fieldId}
                    onChange={(e) => setFormData((p) => ({ ...p, fieldId: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                    required
                  >
                    <option value="">اختر الحقل...</option>
                    {fields.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.name_ar || f.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    نوع الجدولة
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) =>
                      setFormData((p) => ({ ...p, type: e.target.value as IrrigationType }))
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  >
                    {Object.entries(irrigationTypes).map(([key, val]) => (
                      <option key={key} value={key}>
                        {val.labelAr}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">التكرار</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) =>
                      setFormData((p) => ({
                        ...p,
                        frequency: e.target.value as IrrigationFrequency,
                      }))
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  >
                    {Object.entries(frequencies).map(([key, val]) => (
                      <option key={key} value={key}>
                        {val.labelAr}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ البدء</label>
                <input
                  type="datetime-local"
                  value={formData.startDate}
                  onChange={(e) => setFormData((p) => ({ ...p, startDate: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    المدة (دقيقة)
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={formData.duration}
                    onChange={(e) =>
                      setFormData((p) => ({ ...p, duration: Number(e.target.value) }))
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    كمية المياه (م³)
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={formData.waterAmount}
                    onChange={(e) =>
                      setFormData((p) => ({ ...p, waterAmount: Number(e.target.value) }))
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-3 px-6 py-4 border-t border-gray-200">
              <button
                onClick={() => setModalOpen(false)}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
              >
                إلغاء
              </button>
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 transition"
              >
                {editingId ? 'حفظ التعديلات' : 'جدولة'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {deleteTarget && (
        <div className="fixed inset-0 z-[9998] flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setDeleteTarget(null)}
          />
          <div className="relative bg-white rounded-xl shadow-2xl max-w-sm w-full mx-4 p-6 animate-scale-in text-center">
            <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Trash2 className="w-7 h-7 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">حذف جدول الري</h3>
            <p className="text-sm text-gray-600 mb-6">
              هل أنت متأكد من حذف جدول ري &quot;{deleteTarget.name}&quot;؟
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteTarget(null)}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
              >
                إلغاء
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition"
              >
                حذف
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
