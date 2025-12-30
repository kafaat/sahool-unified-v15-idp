'use client';

/**
 * SAHOOL Field Form Component
 * مكون نموذج الحقل
 */

import React, { useState } from 'react';
import { Save, X } from 'lucide-react';
import type { Field, FieldFormData } from '../types';

interface FieldFormProps {
  field?: Field;
  onSubmit: (data: FieldFormData) => void | Promise<void>;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

export const FieldForm: React.FC<FieldFormProps> = ({
  field,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [formData, setFormData] = useState<FieldFormData>({
    name: field?.name || '',
    nameAr: field?.nameAr || '',
    area: field?.area || 0,
    crop: field?.crop || '',
    cropAr: field?.cropAr || '',
    description: field?.description || '',
    descriptionAr: field?.descriptionAr || '',
    farmId: field?.farmId || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  const handleChange = (field: keyof FieldFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {field ? 'تعديل الحقل' : 'إضافة حقل جديد'}
      </h2>

      <div className="space-y-6">
        {/* Name (Arabic) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الاسم (بالعربية) *
          </label>
          <input
            type="text"
            required
            value={formData.nameAr}
            onChange={(e) => handleChange('nameAr', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="أدخل اسم الحقل"
          />
        </div>

        {/* Name (English) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Name (English) *
          </label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Enter field name"
            dir="ltr"
          />
        </div>

        {/* Area */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            المساحة (هكتار) *
          </label>
          <input
            type="number"
            required
            min="0"
            step="0.1"
            value={formData.area}
            onChange={(e) => handleChange('area', parseFloat(e.target.value))}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="0.0"
          />
        </div>

        {/* Crop (Arabic) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            المحصول (بالعربية)
          </label>
          <input
            type="text"
            value={formData.cropAr}
            onChange={(e) => handleChange('cropAr', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="نوع المحصول"
          />
        </div>

        {/* Crop (English) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Crop (English)
          </label>
          <input
            type="text"
            value={formData.crop}
            onChange={(e) => handleChange('crop', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Crop type"
            dir="ltr"
          />
        </div>

        {/* Description (Arabic) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الوصف (بالعربية)
          </label>
          <textarea
            value={formData.descriptionAr}
            onChange={(e) => handleChange('descriptionAr', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="وصف الحقل"
          />
        </div>

        {/* Description (English) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description (English)
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Field description"
            dir="ltr"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 mt-8 pt-6 border-t-2 border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center gap-2 px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            <X className="w-4 h-4" />
            <span>إلغاء</span>
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4" />
          <span>{isSubmitting ? 'جاري الحفظ...' : 'حفظ'}</span>
        </button>
      </div>
    </form>
  );
};

export default FieldForm;
