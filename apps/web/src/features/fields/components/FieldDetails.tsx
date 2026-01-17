"use client";

/**
 * SAHOOL Field Details Component
 * مكون تفاصيل الحقل
 */

import React from "react";
import {
  X,
  MapPin,
  Sprout,
  Maximize2,
  Calendar,
  Edit2,
  Trash2,
} from "lucide-react";
import type { Field } from "../types";

interface FieldDetailsProps {
  field: Field;
  onClose?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export const FieldDetails: React.FC<FieldDetailsProps> = ({
  field,
  onClose,
  onEdit,
  onDelete,
}) => {
  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 border-b-2 border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              {field.nameAr || field.name}
            </h2>
            <p className="text-gray-600">{field.name}</p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-white rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Main Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Maximize2 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">المساحة</p>
              <p className="font-semibold text-gray-900">{field.area} هكتار</p>
            </div>
          </div>

          {field.crop && (
            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <div className="p-2 bg-green-100 rounded-lg">
                <Sprout className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">المحصول</p>
                <p className="font-semibold text-gray-900">
                  {field.cropAr || field.crop}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">تاريخ الإضافة</p>
              <p className="font-semibold text-gray-900">
                {field.createdAt
                  ? new Date(field.createdAt).toLocaleDateString("ar-EG")
                  : "N/A"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
            <div className="p-2 bg-cyan-100 rounded-lg">
              <MapPin className="w-5 h-5 text-cyan-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">الموقع</p>
              <p className="font-semibold text-gray-900">
                {field.polygon ? "تم تحديد الموقع" : "لم يتم التحديد"}
              </p>
            </div>
          </div>
        </div>

        {/* Description */}
        {(field.description || field.descriptionAr) && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">الوصف</h3>
            <p className="text-gray-600 leading-relaxed">
              {field.descriptionAr || field.description}
            </p>
          </div>
        )}

        {/* Map Placeholder */}
        {field.polygon && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">الخريطة</h3>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-12 h-12 text-gray-400" />
              <p className="text-gray-500 mr-3">خريطة الحقل</p>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-6 border-t-2 border-gray-200 flex items-center justify-end gap-3">
        {onDelete && (
          <button
            onClick={onDelete}
            className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span>حذف</span>
          </button>
        )}
        {onEdit && (
          <button
            onClick={onEdit}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Edit2 className="w-4 h-4" />
            <span>تعديل</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default FieldDetails;
