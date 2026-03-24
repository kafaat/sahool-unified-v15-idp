"use client";

import React, { useState, useMemo, useCallback, useEffect } from "react";
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
} from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { apiClient } from "@/lib/api/client";
import type {
  IrrigationSchedule,
  IrrigationStatus,
  IrrigationScheduleType,
  IrrigationFrequency,
  IrrigationScheduleCreate,
} from "@/lib/api/types";

const initialMockSchedules: IrrigationSchedule[] = [
  {
    id: "1",
    fieldId: "field-1",
    fieldName: "الحقل الشمالي",
    name: "ري صباحي - الحقل الشمالي",
    type: "scheduled",
    status: "active",
    startDate: "2025-01-25T06:00:00Z",
    frequency: "daily",
    duration: 120,
    waterAmount: 500,
    schedule: { timeOfDay: "06:00" },
    nextRun: "2025-01-26T06:00:00Z",
    createdAt: "2025-01-20T00:00:00Z",
    updatedAt: "2025-01-25T06:00:00Z",
  },
  {
    id: "2",
    fieldId: "field-2",
    fieldName: "الحقل الجنوبي",
    name: "ري محوري - الحقل الجنوبي",
    type: "automatic",
    status: "active",
    startDate: "2025-01-25T04:00:00Z",
    frequency: "daily",
    duration: 180,
    waterAmount: 1200,
    createdAt: "2025-01-18T00:00:00Z",
    updatedAt: "2025-01-25T04:00:00Z",
  },
  {
    id: "3",
    fieldId: "field-3",
    fieldName: "حقل القمح",
    name: "ري رشاشات - حقل القمح",
    type: "scheduled",
    status: "completed",
    startDate: "2025-01-24T18:00:00Z",
    endDate: "2025-01-24T19:30:00Z",
    frequency: "weekly",
    duration: 90,
    waterAmount: 800,
    schedule: { daysOfWeek: [0, 3], timeOfDay: "18:00" },
    createdAt: "2025-01-15T00:00:00Z",
    updatedAt: "2025-01-24T19:30:00Z",
  },
  {
    id: "4",
    fieldId: "field-4",
    fieldName: "بستان النخيل",
    name: "ري يدوي - بستان النخيل",
    type: "manual",
    status: "paused",
    startDate: "2025-01-24T08:00:00Z",
    frequency: "custom",
    duration: 240,
    waterAmount: 2000,
    schedule: { interval: 3 },
    createdAt: "2025-01-10T00:00:00Z",
    updatedAt: "2025-01-24T08:00:00Z",
  },
  {
    id: "5",
    fieldId: "field-5",
    fieldName: "الصوب الزراعية",
    name: "ري تنقيط - الصوب الزراعية",
    type: "scheduled",
    status: "active",
    startDate: "2025-01-25T16:00:00Z",
    frequency: "daily",
    duration: 60,
    waterAmount: 200,
    schedule: { timeOfDay: "16:00" },
    nextRun: "2025-01-26T16:00:00Z",
    createdAt: "2025-01-22T00:00:00Z",
    updatedAt: "2025-01-25T16:00:00Z",
  },
];

const scheduleTypes: Record<IrrigationScheduleType, { label: string; labelAr: string }> = {
  manual: { label: "Manual", labelAr: "يدوي" },
  automatic: { label: "Automatic", labelAr: "تلقائي" },
  scheduled: { label: "Scheduled", labelAr: "مجدول" },
};

const frequencies: Record<IrrigationFrequency, { label: string; labelAr: string }> = {
  daily: { label: "Daily", labelAr: "يومي" },
  weekly: { label: "Weekly", labelAr: "أسبوعي" },
  custom: { label: "Custom", labelAr: "مخصص" },
};

const EMPTY_FORM = {
  name: "",
  fieldId: "",
  type: "scheduled" as IrrigationScheduleType,
  startDate: "",
  frequency: "daily" as IrrigationFrequency,
  duration: 60,
  waterAmount: 100,
};

export default function IrrigationClient() {
  const [schedules, setSchedules] = useState<IrrigationSchedule[]>(initialMockSchedules);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<IrrigationStatus | "all">("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [deleteTarget, setDeleteTarget] = useState<IrrigationSchedule | null>(null);
  const { showToast } = useToast();

  // Load schedules from API on mount
  useEffect(() => {
    async function loadSchedules() {
      try {
        const response = await apiClient.getIrrigationSchedules();
        if (response.success && response.data) {
          setSchedules(response.data);
        }
      } catch {
        // API unavailable - keep mock data for offline-first UX
      }
    }
    loadSchedules();
  }, []);

  const filteredSchedules = useMemo(() => {
    return schedules.filter((schedule) => {
      const matchesSearch =
        !searchTerm ||
        (schedule.fieldName ?? "").includes(searchTerm) ||
        schedule.name.includes(searchTerm);
      const matchesStatus = statusFilter === "all" || schedule.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [schedules, searchTerm, statusFilter]);

  const getStatusBadge = (status: IrrigationStatus) => {
    const styles: Record<IrrigationStatus, string> = {
      active: "bg-green-100 text-green-800",
      paused: "bg-orange-100 text-orange-800",
      completed: "bg-gray-100 text-gray-800",
    };
    const labels: Record<IrrigationStatus, string> = {
      active: "نشط",
      paused: "متوقف",
      completed: "مكتمل",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("ar-SA", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const totalWaterToday = schedules
    .filter((s) => s.status !== "completed")
    .reduce((sum, s) => sum + s.waterAmount, 0);

  const pausedCount = schedules.filter((s) => s.status === "paused").length;
  const activeCount = schedules.filter((s) => s.status === "active").length;

  // CRUD handlers
  const openCreate = useCallback(() => {
    setFormData(EMPTY_FORM);
    setEditingId(null);
    setModalOpen(true);
  }, []);

  const openEdit = useCallback((schedule: IrrigationSchedule) => {
    setFormData({
      name: schedule.name,
      fieldId: schedule.fieldId,
      type: schedule.type,
      startDate: schedule.startDate.slice(0, 16),
      frequency: schedule.frequency,
      duration: schedule.duration,
      waterAmount: schedule.waterAmount,
    });
    setEditingId(schedule.id);
    setModalOpen(true);
  }, []);

  const handleSave = useCallback(async () => {
    if (!formData.name.trim()) {
      showToast({ type: "warning", message: "Please enter schedule name", messageAr: "يرجى إدخال اسم الجدول" });
      return;
    }

    try {
      // Normalize datetime-local value to ISO 8601 with timezone
      const startDateISO = formData.startDate
        ? new Date(formData.startDate).toISOString()
        : new Date().toISOString();

      if (editingId) {
        const response = await apiClient.updateIrrigationSchedule(editingId, {
          name: formData.name,
          fieldId: formData.fieldId,
          type: formData.type,
          startDate: startDateISO,
          frequency: formData.frequency,
          duration: formData.duration,
          waterAmount: formData.waterAmount,
        });
        if (response.success && response.data) {
          setSchedules((prev) => prev.map((s) => (s.id === editingId ? response.data! : s)));
        } else {
          // Optimistic update if API returns no data
          setSchedules((prev) =>
            prev.map((s) =>
              s.id === editingId
                ? { ...s, name: formData.name, type: formData.type, startDate: startDateISO, frequency: formData.frequency, duration: formData.duration, waterAmount: formData.waterAmount }
                : s
            )
          );
        }
        showToast({ type: "success", message: "Schedule updated", messageAr: "تم تحديث الجدول" });
      } else {
        const payload: IrrigationScheduleCreate = {
          fieldId: formData.fieldId || `field-${Date.now()}`,
          name: formData.name,
          type: formData.type,
          startDate: startDateISO,
          frequency: formData.frequency,
          duration: formData.duration,
          waterAmount: formData.waterAmount,
        };
        const response = await apiClient.createIrrigationSchedule(payload);
        if (response.success && response.data) {
          setSchedules((prev) => [...prev, response.data!]);
        } else {
          // Optimistic fallback
          const newSchedule: IrrigationSchedule = {
            id: crypto.randomUUID(),
            ...payload,
            status: "active",
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
          setSchedules((prev) => [...prev, newSchedule]);
        }
        showToast({ type: "success", message: "Schedule created", messageAr: "تم إنشاء الجدول" });
      }
    } catch {
      showToast({ type: "error", message: "Operation failed", messageAr: "فشلت العملية" });
    }
    setModalOpen(false);
  }, [formData, editingId, showToast]);

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    try {
      await apiClient.deleteIrrigationSchedule(deleteTarget.id);
    } catch {
      // Optimistic delete even on API failure (offline-first)
    }
    setSchedules((prev) => prev.filter((s) => s.id !== deleteTarget.id));
    showToast({ type: "success", message: "Schedule deleted", messageAr: "تم حذف الجدول" });
    setDeleteTarget(null);
  }, [deleteTarget, showToast]);

  const handleStart = useCallback(async (id: string) => {
    setSchedules((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: "active" as IrrigationStatus } : s))
    );
    try {
      await apiClient.startIrrigationSchedule(id);
    } catch {
      // Optimistic update already applied
    }
    showToast({ type: "info", message: "Irrigation started", messageAr: "بدأ الري" });
  }, [showToast]);

  const handleStop = useCallback(async (id: string) => {
    setSchedules((prev) =>
      prev.map((s) =>
        s.id === id
          ? { ...s, status: "paused" as IrrigationStatus }
          : s
      )
    );
    try {
      await apiClient.stopIrrigationSchedule(id);
    } catch {
      // Optimistic update already applied
    }
    showToast({ type: "success", message: "Irrigation paused", messageAr: "تم إيقاف الري مؤقتاً" });
  }, [showToast]);

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

      {/* Paused Alert */}
      {pausedCount > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 animate-shake">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span className="font-medium text-orange-800">
              تنبيه: {pausedCount} جدول ري متوقف يتطلب اهتمام
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
              <div className="text-xl font-bold text-blue-600">{totalWaterToday.toLocaleString()} م³</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center ${activeCount > 0 ? "animate-pulse-dot" : ""}`}>
              <Clock className="w-5 h-5 text-green-600" />
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
              <div className="text-xl font-bold text-orange-600">{pausedCount}</div>
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
          onChange={(e) => setStatusFilter(e.target.value as IrrigationStatus | "all")}
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
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">تاريخ البدء</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المدة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">كمية المياه</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredSchedules.map((schedule, index) => (
                <tr
                  key={schedule.id}
                  className="hover:bg-gray-50 transition-colors animate-slide-in-up"
                  style={{ animationDelay: `${index * 40}ms`, animationFillMode: "both" }}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Droplets className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{schedule.name}</div>
                        {schedule.fieldName && (
                          <div className="text-xs text-gray-500">{schedule.fieldName}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {scheduleTypes[schedule.type].labelAr}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {frequencies[schedule.frequency].labelAr}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(schedule.startDate)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">{schedule.duration} دقيقة</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{schedule.waterAmount} م³</td>
                  <td className="px-4 py-3">
                    {getStatusBadge(schedule.status)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      {schedule.status === "paused" && (
                        <button
                          onClick={() => handleStart(schedule.id)}
                          className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="استئناف الري"
                          aria-label={`استئناف ري ${schedule.name}`}
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {schedule.status === "active" && (
                        <button
                          onClick={() => handleStop(schedule.id)}
                          className="p-1.5 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                          title="إيقاف الري مؤقتاً"
                          aria-label={`إيقاف ري ${schedule.name}`}
                        >
                          <Pause className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => openEdit(schedule)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="تعديل"
                        aria-label={`تعديل جدول ${schedule.name}`}
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(schedule)}
                        className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="حذف"
                        aria-label={`حذف جدول ${schedule.name}`}
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
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setModalOpen(false)} />
          <div className="relative bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 animate-scale-in">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                {editingId ? "تعديل جدول الري" : "جدولة ري جديدة"}
              </h2>
              <button onClick={() => setModalOpen(false)} className="p-1.5 hover:bg-gray-100 rounded-lg" aria-label="إغلاق">
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
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">نوع الجدولة</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData((p) => ({ ...p, type: e.target.value as IrrigationScheduleType }))}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  >
                    {Object.entries(scheduleTypes).map(([key, val]) => (
                      <option key={key} value={key}>{val.labelAr}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">التكرار</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData((p) => ({ ...p, frequency: e.target.value as IrrigationFrequency }))}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  >
                    {Object.entries(frequencies).map(([key, val]) => (
                      <option key={key} value={key}>{val.labelAr}</option>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">المدة (دقيقة)</label>
                  <input
                    type="number"
                    min={1}
                    value={formData.duration}
                    onChange={(e) => setFormData((p) => ({ ...p, duration: Number(e.target.value) }))}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">كمية المياه (م³)</label>
                  <input
                    type="number"
                    min={1}
                    value={formData.waterAmount}
                    onChange={(e) => setFormData((p) => ({ ...p, waterAmount: Number(e.target.value) }))}
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
                {editingId ? "حفظ التعديلات" : "جدولة"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {deleteTarget && (
        <div className="fixed inset-0 z-[9998] flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setDeleteTarget(null)} />
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
