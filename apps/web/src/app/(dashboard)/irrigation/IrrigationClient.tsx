'use client';

// TODO: All CRUD operations (handleSave, handleDelete, handleStart, handleStop) only
// modify local state with mock data. Wire up to irrigation API when backend is ready.

import React, { useState, useMemo, useCallback } from 'react';
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
  },
];

const irrigationTypes: Record<IrrigationType, { label: string; labelAr: string }> = {
  drip: { label: 'Drip', labelAr: 'تنقيط' },
  sprinkler: { label: 'Sprinkler', labelAr: 'رشاشات' },
  pivot: { label: 'Pivot', labelAr: 'محوري' },
  flood: { label: 'Flood', labelAr: 'غمر' },
  manual: { label: 'Manual', labelAr: 'يدوي' },
};

const EMPTY_FORM = {
  fieldName: '',
  type: 'drip' as IrrigationType,
  scheduledAt: '',
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
  const { showToast } = useToast();

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

  const overdueCount = schedules.filter((s) => s.status === 'overdue').length;
  const inProgressCount = schedules.filter((s) => s.status === 'in_progress').length;
  const scheduledCount = schedules.filter((s) => s.status === 'scheduled').length;
  void scheduledCount; // Will be used when API integration is wired up

  // CRUD handlers
  const openCreate = useCallback(() => {
    setFormData(EMPTY_FORM);
    setEditingId(null);
    setModalOpen(true);
  }, []);

  const openEdit = useCallback((schedule: IrrigationSchedule) => {
    setFormData({
      fieldName: schedule.fieldName,
      type: schedule.type,
      scheduledAt: schedule.scheduledAt.slice(0, 16),
      duration: schedule.duration,
      waterAmount: schedule.waterAmount,
    });
    setEditingId(schedule.id);
    setModalOpen(true);
  }, []);

  const handleSave = useCallback(() => {
    if (!formData.fieldName.trim()) {
      showToast({
        type: 'warning',
        message: 'Please enter field name',
        messageAr: 'يرجى إدخال اسم الحقل',
      });
      return;
    }

    if (editingId) {
      setSchedules((prev) =>
        prev.map((s) =>
          s.id === editingId
            ? {
                ...s,
                fieldName: formData.fieldName,
                type: formData.type,
                scheduledAt: formData.scheduledAt || s.scheduledAt,
                duration: formData.duration,
                waterAmount: formData.waterAmount,
              }
            : s
        )
      );
      showToast({ type: 'success', message: 'Schedule updated', messageAr: 'تم تحديث الجدول' });
    } else {
      const newSchedule: IrrigationSchedule = {
        id: crypto.randomUUID(),
        fieldId: `field-${Date.now()}`,
        fieldName: formData.fieldName,
        type: formData.type,
        status: 'scheduled',
        scheduledAt: formData.scheduledAt || new Date().toISOString(),
        duration: formData.duration,
        waterAmount: formData.waterAmount,
      };
      setSchedules((prev) => [...prev, newSchedule]);
      showToast({ type: 'success', message: 'Schedule created', messageAr: 'تم إنشاء الجدول' });
    }
    setModalOpen(false);
  }, [formData, editingId, showToast]);

  const handleDelete = useCallback(() => {
    if (!deleteTarget) return;
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
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 animate-shake">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span className="font-medium text-orange-800">
              تنبيه: {overdueCount} جدول ري متأخر يتطلب اهتماماً
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
              className={`w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center ${inProgressCount > 0 ? 'animate-pulse-dot' : ''}`}
            >
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">نشط الآن</div>
              <div className="text-xl font-bold text-green-600">{inProgressCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متأخر</div>
              <div className="text-xl font-bold text-orange-600">{overdueCount}</div>
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
          <option value="scheduled">مجدول</option>
          <option value="in_progress">جاري</option>
          <option value="completed">مكتمل</option>
          <option value="overdue">متأخر</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحقل</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">النوع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  تاريخ الجدولة
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
                        <div className="font-medium text-gray-900">{schedule.fieldName}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {irrigationTypes[schedule.type].labelAr}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(schedule.scheduledAt)}
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
                          title="بدء الري"
                          aria-label={`بدء ري ${schedule.fieldName}`}
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {schedule.status === 'in_progress' && (
                        <button
                          onClick={() => handleStop(schedule.id)}
                          className="p-1.5 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                          title="إيقاف الري"
                          aria-label={`إيقاف ري ${schedule.fieldName}`}
                        >
                          <Pause className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => openEdit(schedule)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="تعديل"
                        aria-label={`تعديل جدول ${schedule.fieldName}`}
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(schedule)}
                        className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="حذف"
                        aria-label={`حذف جدول ${schedule.fieldName}`}
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
                  اسم الحقل <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.fieldName}
                  onChange={(e) => setFormData((p) => ({ ...p, fieldName: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
                  placeholder="مثال: الحقل الشمالي"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نوع الري
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
                <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الجدولة</label>
                <input
                  type="datetime-local"
                  value={formData.scheduledAt}
                  onChange={(e) => setFormData((p) => ({ ...p, scheduledAt: e.target.value }))}
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
              هل أنت متأكد من حذف جدول ري &quot;{deleteTarget.fieldName}&quot;؟
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
