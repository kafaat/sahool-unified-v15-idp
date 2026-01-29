"use client";

import React, { useState, useMemo } from "react";
import {
  Droplets,
  Search,
  Plus,
  Calendar,
  Clock,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";

type IrrigationStatus = "scheduled" | "in_progress" | "completed" | "cancelled" | "overdue";
type IrrigationType = "drip" | "sprinkler" | "pivot" | "flood" | "manual";

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
}

const mockSchedules: IrrigationSchedule[] = [
  {
    id: "1",
    fieldId: "field-1",
    fieldName: "الحقل الشمالي",
    type: "drip",
    status: "scheduled",
    scheduledAt: "2025-01-25T06:00:00Z",
    duration: 120,
    waterAmount: 500,
  },
  {
    id: "2",
    fieldId: "field-2",
    fieldName: "الحقل الجنوبي",
    type: "pivot",
    status: "in_progress",
    scheduledAt: "2025-01-25T04:00:00Z",
    duration: 180,
    waterAmount: 1200,
  },
  {
    id: "3",
    fieldId: "field-3",
    fieldName: "حقل القمح",
    type: "sprinkler",
    status: "completed",
    scheduledAt: "2025-01-24T18:00:00Z",
    duration: 90,
    waterAmount: 800,
    completedAt: "2025-01-24T19:30:00Z",
  },
  {
    id: "4",
    fieldId: "field-4",
    fieldName: "بستان النخيل",
    type: "flood",
    status: "overdue",
    scheduledAt: "2025-01-24T08:00:00Z",
    duration: 240,
    waterAmount: 2000,
  },
  {
    id: "5",
    fieldId: "field-5",
    fieldName: "الصوب الزراعية",
    type: "drip",
    status: "scheduled",
    scheduledAt: "2025-01-25T16:00:00Z",
    duration: 60,
    waterAmount: 200,
  },
];

const irrigationTypes: Record<IrrigationType, { label: string; labelAr: string }> = {
  drip: { label: "Drip", labelAr: "تنقيط" },
  sprinkler: { label: "Sprinkler", labelAr: "رشاشات" },
  pivot: { label: "Pivot", labelAr: "محوري" },
  flood: { label: "Flood", labelAr: "غمر" },
  manual: { label: "Manual", labelAr: "يدوي" },
};

export default function IrrigationClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<IrrigationStatus | "all">("all");

  const filteredSchedules = useMemo(() => {
    return mockSchedules.filter((schedule) => {
      const matchesSearch =
        !searchTerm ||
        schedule.fieldName.includes(searchTerm);
      const matchesStatus = statusFilter === "all" || schedule.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [searchTerm, statusFilter]);

  const getStatusBadge = (status: IrrigationStatus) => {
    const styles = {
      scheduled: "bg-blue-100 text-blue-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      cancelled: "bg-gray-100 text-gray-800",
      overdue: "bg-red-100 text-red-800",
    };
    const labels = {
      scheduled: "مجدول",
      in_progress: "جاري",
      completed: "مكتمل",
      cancelled: "ملغي",
      overdue: "متأخر",
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

  const totalWaterToday = mockSchedules
    .filter((s) => s.status !== "cancelled")
    .reduce((sum, s) => sum + s.waterAmount, 0);

  const overdueCount = mockSchedules.filter((s) => s.status === "overdue").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة الري</h1>
          <p className="text-gray-500 mt-1">Irrigation Management</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700">
          <Plus className="w-4 h-4" />
          <span>جدولة ري</span>
        </button>
      </div>

      {/* Overdue Alert */}
      {overdueCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              تنبيه: {overdueCount} جدول ري متأخر يتطلب اهتمام
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
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
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">جاري الآن</div>
              <div className="text-xl font-bold text-yellow-600">
                {mockSchedules.filter((s) => s.status === "in_progress").length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مجدول اليوم</div>
              <div className="text-xl font-bold text-green-600">
                {mockSchedules.filter((s) => s.status === "scheduled").length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
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
            placeholder="بحث عن حقل..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as IrrigationStatus | "all")}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="scheduled">مجدول</option>
          <option value="in_progress">جاري</option>
          <option value="completed">مكتمل</option>
          <option value="overdue">متأخر</option>
          <option value="cancelled">ملغي</option>
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
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الموعد</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المدة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">كمية المياه</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredSchedules.map((schedule) => (
                <tr key={schedule.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Droplets className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="font-medium text-gray-900">{schedule.fieldName}</div>
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
                  <td className="px-4 py-3">{getStatusBadge(schedule.status)}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      {schedule.status === "scheduled" && (
                        <button className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium">
                          بدء
                        </button>
                      )}
                      {schedule.status === "in_progress" && (
                        <button className="text-red-600 hover:text-red-700 text-sm font-medium">
                          إيقاف
                        </button>
                      )}
                      <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                        تعديل
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
