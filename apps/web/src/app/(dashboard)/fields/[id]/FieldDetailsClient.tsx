"use client";

/**
 * Field Details Client Component
 * مكون تفاصيل الحقل
 */

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowRight,
  MapPin,
  Sprout,
  Maximize2,
  Calendar,
  Edit2,
  Trash2,
  Droplets,
  Sun,
  Thermometer,
  Wind,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useField, useDeleteField } from "@/features/fields/hooks/useFields";
import { FieldForm } from "@/features/fields/components/FieldForm";
import { Modal } from "@/components/ui/modal";
import type { FieldFormData } from "@/features/fields/types";
import { logger } from "@/lib/logger";

interface FieldDetailsClientProps {
  fieldId: string;
}

export default function FieldDetailsClient({
  fieldId,
}: FieldDetailsClientProps) {
  const router = useRouter();
  const { data: field, isLoading, error, refetch } = useField(fieldId);
  const deleteField = useDeleteField();
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDelete = async () => {
    try {
      await deleteField.mutateAsync(fieldId);
      router.push("/fields");
    } catch (err) {
      logger.error("Failed to delete field:", err);
    }
  };

  const handleEditSubmit = async (_data: FieldFormData) => {
    // TODO: Implement update when backend is ready
    logger.log("Update field data:", _data);
    setShowEditModal(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">جاري تحميل بيانات الحقل...</p>
          <p className="text-sm text-gray-500">Loading field data...</p>
        </div>
      </div>
    );
  }

  if (error || !field) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center bg-white rounded-xl border-2 border-red-200 p-8 max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            لم يتم العثور على الحقل
          </h2>
          <p className="text-gray-600 mb-6">
            Field not found or an error occurred
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => refetch()}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              <RefreshCw className="w-4 h-4" />
              إعادة المحاولة
            </button>
            <Link
              href="/fields"
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <ArrowRight className="w-4 h-4" />
              العودة للحقول
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Calculate health status
  const healthScore = field.healthScore ?? field.ndviValue ?? 0;
  const healthStatus =
    healthScore >= 0.7
      ? "excellent"
      : healthScore >= 0.5
        ? "good"
        : healthScore >= 0.3
          ? "fair"
          : "poor";
  const healthConfig = {
    excellent: {
      label: "ممتاز",
      labelEn: "Excellent",
      color: "text-green-600",
      bg: "bg-green-100",
      icon: CheckCircle,
    },
    good: {
      label: "جيد",
      labelEn: "Good",
      color: "text-blue-600",
      bg: "bg-blue-100",
      icon: CheckCircle,
    },
    fair: {
      label: "متوسط",
      labelEn: "Fair",
      color: "text-yellow-600",
      bg: "bg-yellow-100",
      icon: AlertTriangle,
    },
    poor: {
      label: "ضعيف",
      labelEn: "Poor",
      color: "text-red-600",
      bg: "bg-red-100",
      icon: AlertTriangle,
    },
  };
  const currentHealth = healthConfig[healthStatus];
  const HealthIcon = currentHealth.icon;

  return (
    <div className="space-y-6" dir="rtl">
      {/* Breadcrumb & Actions */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3 text-sm">
            <Link href="/fields" className="text-gray-500 hover:text-gray-700">
              الحقول
            </Link>
            <span className="text-gray-400">/</span>
            <span className="text-gray-900 font-medium">
              {field.nameAr || field.name}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowEditModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Edit2 className="w-4 h-4" />
              <span>تعديل</span>
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-red-200"
            >
              <Trash2 className="w-4 h-4" />
              <span>حذف</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="bg-gradient-to-l from-green-50 to-blue-50 rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {field.nameAr || field.name}
            </h1>
            <p className="text-gray-600 text-lg">{field.name}</p>
            {field.descriptionAr && (
              <p className="text-gray-500 mt-2">{field.descriptionAr}</p>
            )}
          </div>
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-full ${currentHealth.bg}`}
          >
            <HealthIcon className={`w-5 h-5 ${currentHealth.color}`} />
            <span className={`font-semibold ${currentHealth.color}`}>
              {currentHealth.label}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Maximize2 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">المساحة</p>
              <p className="text-xl font-bold text-gray-900">
                {field.area} <span className="text-sm font-normal">هكتار</span>
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <Sprout className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">المحصول</p>
              <p className="text-xl font-bold text-gray-900">
                {field.cropAr || field.crop || "غير محدد"}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">مؤشر NDVI</p>
              <p className="text-xl font-bold text-gray-900">
                {field.ndviValue?.toFixed(2) || "N/A"}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-cyan-100 rounded-lg">
              <MapPin className="w-6 h-6 text-cyan-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">الموقع</p>
              <p className="text-xl font-bold text-gray-900">
                {field.polygon ? "محدد" : "غير محدد"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content - 2/3 */}
        <div className="lg:col-span-2 space-y-6">
          {/* Map Section */}
          <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-green-600" />
                خريطة الحقل
              </h2>
            </div>
            <div className="h-72 bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
              {field.polygon ? (
                <div className="text-center">
                  <MapPin className="w-16 h-16 text-green-400 mx-auto mb-3" />
                  <p className="text-gray-600">الخريطة التفاعلية</p>
                  <p className="text-sm text-gray-500">Interactive Map View</p>
                </div>
              ) : (
                <div className="text-center">
                  <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">لم يتم تحديد حدود الحقل</p>
                  <button className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                    رسم حدود الحقل
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Health Metrics */}
          <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                مؤشرات صحة المحصول
              </h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* NDVI Progress */}
                <div className="text-center">
                  <div className="relative w-24 h-24 mx-auto mb-3">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        fill="none"
                        stroke="#22c55e"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${(field.ndviValue || 0) * 251} 251`}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xl font-bold text-gray-900">
                        {((field.ndviValue || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm font-medium text-gray-900">مؤشر NDVI</p>
                  <p className="text-xs text-gray-500">Vegetation Index</p>
                </div>

                {/* Health Score */}
                <div className="text-center">
                  <div className="relative w-24 h-24 mx-auto mb-3">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${healthScore * 251} 251`}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xl font-bold text-gray-900">
                        {(healthScore * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm font-medium text-gray-900">
                    صحة المحصول
                  </p>
                  <p className="text-xs text-gray-500">Crop Health</p>
                </div>

                {/* Growth Stage */}
                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
                    <Sprout className="w-10 h-10 text-green-600" />
                  </div>
                  <p className="text-sm font-medium text-gray-900">
                    مرحلة النمو
                  </p>
                  <p className="text-xs text-gray-500">Growing Stage</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar - 1/3 */}
        <div className="space-y-6">
          {/* Field Info Card */}
          <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900">معلومات الحقل</h2>
            </div>
            <div className="p-4 space-y-4">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">تاريخ الإنشاء</p>
                  <p className="text-sm font-medium">
                    {field.createdAt
                      ? new Date(field.createdAt).toLocaleDateString("ar-SA")
                      : "N/A"}
                  </p>
                </div>
              </div>

              {field.plantingDate && (
                <div className="flex items-center gap-3">
                  <Sprout className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">تاريخ الزراعة</p>
                    <p className="text-sm font-medium">
                      {new Date(field.plantingDate).toLocaleDateString("ar-SA")}
                    </p>
                  </div>
                </div>
              )}

              {field.expectedHarvest && (
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">موعد الحصاد المتوقع</p>
                    <p className="text-sm font-medium">
                      {new Date(field.expectedHarvest).toLocaleDateString(
                        "ar-SA",
                      )}
                    </p>
                  </div>
                </div>
              )}

              {field.soilType && (
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-amber-200" />
                  <div>
                    <p className="text-xs text-gray-500">نوع التربة</p>
                    <p className="text-sm font-medium">{field.soilType}</p>
                  </div>
                </div>
              )}

              {field.irrigationType && (
                <div className="flex items-center gap-3">
                  <Droplets className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">نظام الري</p>
                    <p className="text-sm font-medium">
                      {field.irrigationType}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Weather Card */}
          <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Sun className="w-5 h-5 text-yellow-500" />
                الطقس الحالي
              </h2>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <Thermometer className="w-6 h-6 text-orange-500 mx-auto mb-1" />
                  <p className="text-lg font-bold text-gray-900">28°C</p>
                  <p className="text-xs text-gray-500">درجة الحرارة</p>
                </div>
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <Droplets className="w-6 h-6 text-blue-500 mx-auto mb-1" />
                  <p className="text-lg font-bold text-gray-900">65%</p>
                  <p className="text-xs text-gray-500">الرطوبة</p>
                </div>
                <div className="text-center p-3 bg-cyan-50 rounded-lg">
                  <Wind className="w-6 h-6 text-cyan-500 mx-auto mb-1" />
                  <p className="text-lg font-bold text-gray-900">12 كم/س</p>
                  <p className="text-xs text-gray-500">سرعة الرياح</p>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <Sun className="w-6 h-6 text-yellow-500 mx-auto mb-1" />
                  <p className="text-lg font-bold text-gray-900">مشمس</p>
                  <p className="text-xs text-gray-500">الحالة</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900">إجراءات سريعة</h2>
            </div>
            <div className="p-4 space-y-2">
              <button className="w-full flex items-center gap-3 p-3 text-right hover:bg-gray-50 rounded-lg transition-colors">
                <Activity className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">تحليل صحة المحصول</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-right hover:bg-gray-50 rounded-lg transition-colors">
                <Droplets className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium">جدولة الري</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-right hover:bg-gray-50 rounded-lg transition-colors">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                <span className="text-sm font-medium">تقرير الإنتاجية</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        titleAr="تعديل الحقل"
        title="Edit Field"
      >
        <FieldForm
          field={field}
          onSubmit={handleEditSubmit}
          onCancel={() => setShowEditModal(false)}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        titleAr="تأكيد الحذف"
        title="Confirm Delete"
      >
        <div className="p-6 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trash2 className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            هل أنت متأكد من حذف هذا الحقل؟
          </h3>
          <p className="text-gray-600 mb-6">
            سيتم حذف جميع البيانات المرتبطة بهذا الحقل ولا يمكن التراجع عن هذا
            الإجراء.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              إلغاء
            </button>
            <button
              onClick={handleDelete}
              disabled={deleteField.isPending}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
            >
              {deleteField.isPending && (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              حذف الحقل
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
