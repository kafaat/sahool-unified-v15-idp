/**
 * Equipment Form Component
 * مكون نموذج المعدات
 */

"use client";

import { useState } from "react";
import { useCreateEquipment, useUpdateEquipment } from "../hooks/useEquipment";
import type {
  Equipment,
  EquipmentFormData,
  EquipmentType,
  EquipmentStatus,
} from "../types";
import { Loader2, Save } from "lucide-react";
import { logger } from "@/lib/logger";

interface EquipmentFormProps {
  equipment?: Equipment;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function EquipmentForm({
  equipment,
  onSuccess,
  onCancel,
}: EquipmentFormProps) {
  const [formData, setFormData] = useState<EquipmentFormData>({
    name: equipment?.name || "",
    nameAr: equipment?.nameAr || "",
    type: equipment?.type || "tractor",
    status: equipment?.status || "active",
    serialNumber: equipment?.serialNumber || "",
    manufacturer: equipment?.manufacturer || "",
    model: equipment?.model || "",
    purchaseDate: equipment?.purchaseDate?.split("T")[0] || "",
    purchasePrice: equipment?.purchasePrice,
    fuelType: equipment?.fuelType || "",
  });

  const createMutation = useCreateEquipment();
  const updateMutation = useUpdateEquipment();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (equipment) {
        await updateMutation.mutateAsync({ id: equipment.id, data: formData });
      } else {
        await createMutation.mutateAsync(formData);
      }
      onSuccess?.();
    } catch (error) {
      logger.error("Failed to save equipment:", error);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">
          {equipment ? "تعديل المعدة" : "إضافة معدة جديدة"}
        </h2>

        {/* Names */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الاسم بالعربية *
            </label>
            <input
              type="text"
              required
              value={formData.nameAr}
              onChange={(e) =>
                setFormData({ ...formData, nameAr: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name (English) *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Type and Status */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              النوع *
            </label>
            <select
              required
              value={formData.type}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  type: e.target.value as EquipmentType,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="tractor">جرار</option>
              <option value="harvester">حصادة</option>
              <option value="irrigation_system">نظام ري</option>
              <option value="sprayer">رشاش</option>
              <option value="planter">آلة زراعة</option>
              <option value="other">أخرى</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الحالة *
            </label>
            <select
              required
              value={formData.status}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  status: e.target.value as EquipmentStatus,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="active">نشط</option>
              <option value="maintenance">صيانة</option>
              <option value="repair">إصلاح</option>
              <option value="idle">خامل</option>
              <option value="retired">متوقف</option>
            </select>
          </div>
        </div>

        {/* Serial Number and Manufacturer */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الرقم التسلسلي *
            </label>
            <input
              type="text"
              required
              value={formData.serialNumber}
              onChange={(e) =>
                setFormData({ ...formData, serialNumber: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الشركة المصنعة
            </label>
            <input
              type="text"
              value={formData.manufacturer}
              onChange={(e) =>
                setFormData({ ...formData, manufacturer: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Model and Fuel Type */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الموديل
            </label>
            <input
              type="text"
              value={formData.model}
              onChange={(e) =>
                setFormData({ ...formData, model: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              نوع الوقود
            </label>
            <input
              type="text"
              value={formData.fuelType}
              onChange={(e) =>
                setFormData({ ...formData, fuelType: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Purchase Date and Price */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              تاريخ الشراء *
            </label>
            <input
              type="date"
              required
              value={formData.purchaseDate}
              onChange={(e) =>
                setFormData({ ...formData, purchaseDate: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              سعر الشراء (ريال)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.purchasePrice || ""}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  purchasePrice: e.target.value
                    ? parseFloat(e.target.value)
                    : undefined,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            إلغاء
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 ml-2 animate-spin" />
              جاري الحفظ...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 ml-2" />
              حفظ
            </>
          )}
        </button>
      </div>
    </form>
  );
}
