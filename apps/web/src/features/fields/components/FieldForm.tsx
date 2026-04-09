'use client';

/**
 * SAHOOL Field Form Component
 * مكون نموذج الحقل
 */

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Save, X, MapPin, Info } from 'lucide-react';
import type { Field, FieldFormData, GeoPolygon } from '../types';

// Dynamic import – no SSR for Google Maps
const GoogleMapsFieldDrawer = dynamic(
  () => import('@/components/maps/GoogleMapsFieldDrawer'),
  { ssr: false, loading: () => <div className="h-[calc(100vh-320px)] min-h-[400px] bg-gray-100 rounded-lg animate-pulse" /> }
);

interface FieldFormProps {
  field?: Field;
  onSubmit: (data: FieldFormData) => void | Promise<void>;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

const MAX_NAME_LENGTH = 255;
const MIN_NAME_LENGTH = 2;

export const FieldForm: React.FC<FieldFormProps> = ({
  field,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [tab, setTab] = useState<'info' | 'boundary'>('info');
  const [formData, setFormData] = useState<FieldFormData>({
    name: field?.name || '',
    nameAr: field?.nameAr || '',
    area: field?.area || 0,
    crop: field?.crop || '',
    cropAr: field?.cropAr || '',
    description: field?.description || '',
    descriptionAr: field?.descriptionAr || '',
    farmId: field?.farmId || '',
    polygon: field?.polygon,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    const trimmedNameAr = formData.nameAr.trim();
    if (!trimmedNameAr) {
      newErrors.nameAr = 'اسم الحقل بالعربية مطلوب';
    } else if (trimmedNameAr.length < MIN_NAME_LENGTH) {
      newErrors.nameAr = `الاسم قصير جداً (الحد الأدنى ${MIN_NAME_LENGTH} أحرف)`;
    } else if (trimmedNameAr.length > MAX_NAME_LENGTH) {
      newErrors.nameAr = `الاسم طويل جداً (الحد الأقصى ${MAX_NAME_LENGTH} حرف)`;
    }

    const trimmedName = formData.name.trim();
    if (!trimmedName) {
      newErrors.name = 'Field name in English is required';
    } else if (trimmedName.length < MIN_NAME_LENGTH) {
      newErrors.name = `Name too short (minimum ${MIN_NAME_LENGTH} characters)`;
    } else if (trimmedName.length > MAX_NAME_LENGTH) {
      newErrors.name = `Name too long (maximum ${MAX_NAME_LENGTH} characters)`;
    }

    // Polygon must have at least 3 vertices (4 coords including closing point)
    const coords = formData.polygon?.coordinates?.[0];
    if (!coords || coords.length < 4) {
      newErrors.polygon = 'يجب رسم حدود الحقل (3 نقاط على الأقل)';
    }

    setErrors(newErrors);

    // Switch to the tab that has the first error
    if (newErrors.polygon && !newErrors.nameAr && !newErrors.name) {
      setTab('boundary');
    } else if ((newErrors.nameAr || newErrors.name) && !newErrors.polygon) {
      setTab('info');
    }

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await onSubmit({
      ...formData,
      name: formData.name.trim(),
      nameAr: formData.nameAr.trim(),
    });
  };

  const handleChange = <K extends keyof FieldFormData>(key: K, value: FieldFormData[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    if (errors[key as string]) {
      setErrors((prev) => { const e = { ...prev }; delete e[key as string]; return e; });
    }
  };

  const handleBoundaryChange = (geojson: GeoPolygon | null) => {
    if (geojson) {
      // Compute area from polygon using Haversine
      const coords = geojson.coordinates[0] ?? [];
      const area = computeAreaHectares(coords);
      setFormData((prev) => ({ ...prev, polygon: geojson, area }));
      setErrors((prev) => { const e = { ...prev }; delete e.polygon; return e; });
    } else {
      setFormData((prev) => ({ ...prev, polygon: undefined, area: 0 }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border-2 border-gray-200 flex flex-col h-full">
      <div className="px-6 pt-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {field ? 'تعديل الحقل' : 'إضافة حقل جديد'}
        </h2>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 border-b border-gray-200">
          <button
            type="button"
            onClick={() => setTab('info')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              tab === 'info'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Info className="w-4 h-4" />
            المعلومات الأساسية
          </button>
          <button
            type="button"
            onClick={() => setTab('boundary')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              tab === 'boundary'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            } ${errors.polygon ? 'text-red-500' : ''}`}
          >
            <MapPin className="w-4 h-4" />
            حدود الحقل
            {errors.polygon && <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />}
          </button>
        </div>
      </div>

      {/* Tab: Basic Info */}
      {tab === 'info' && (
        <div className="px-6 space-y-6">
          {/* Name (Arabic) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">الاسم (بالعربية) *</label>
            <input
              type="text"
              required
              maxLength={MAX_NAME_LENGTH}
              value={formData.nameAr}
              onChange={(e) => handleChange('nameAr', e.target.value)}
              className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none focus:border-blue-500 ${errors.nameAr ? 'border-red-400' : 'border-gray-200'}`}
              placeholder="أدخل اسم الحقل"
            />
            {errors.nameAr && <p className="mt-1 text-sm text-red-600">{errors.nameAr}</p>}
          </div>

          {/* Name (English) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name (English) *</label>
            <input
              type="text"
              required
              maxLength={MAX_NAME_LENGTH}
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none focus:border-blue-500 ${errors.name ? 'border-red-400' : 'border-gray-200'}`}
              placeholder="Enter field name"
              dir="ltr"
            />
            {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
          </div>

          {/* Area — read-only, computed from polygon */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">المساحة المحسوبة</label>
            <div className={`w-full px-4 py-2 border-2 rounded-lg bg-gray-50 text-gray-600 ${formData.area > 0 ? 'border-green-300' : 'border-gray-200'}`}>
              {formData.area > 0
                ? `${formData.area.toFixed(2)} هكتار`
                : 'ستُحسب تلقائياً عند رسم الحدود'}
            </div>
          </div>

          {/* Crop (Arabic) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">المحصول (بالعربية)</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-2">Crop (English)</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-2">الوصف (بالعربية)</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-2">Description (English)</label>
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
      )}

      {/* Tab: Boundary */}
      {tab === 'boundary' && (
        <div className="px-6 flex flex-col flex-1 min-h-0">
          <GoogleMapsFieldDrawer
            height="calc(100vh - 320px)"
            initialCenter={[15.5527, 48.5164]}
            initialZoom={7}
            initialPolygon={formData.polygon}
            onBoundaryChange={handleBoundaryChange}
          />
          {formData.area > 0 && (
            <p className="mt-3 text-sm font-medium text-green-700">
              المساحة المحسوبة: {formData.area.toFixed(2)} هكتار
            </p>
          )}
          {errors.polygon && (
            <p className="mt-2 text-sm text-red-600">{errors.polygon}</p>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 mt-8 mx-6 mb-6 pt-6 border-t-2 border-gray-200">
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

// ─── Haversine area helper (runs client-side) ───────────────────────────────

function toRad(deg: number) {
  return (deg * Math.PI) / 180;
}

function computeAreaHectares(coords: number[][]): number {
  if (coords.length < 4) return 0;
  // Spherical excess formula (Gauss's area formula on a sphere)
  const R = 6371000; // Earth radius in meters
  let area = 0;
  for (let i = 0; i < coords.length - 1; i++) {
    const c1 = coords[i] as [number, number];
    const c2 = coords[(i + 1) % coords.length] as [number, number];
    area += toRad(c2[0] - c1[0]) * (2 + Math.sin(toRad(c1[1])) + Math.sin(toRad(c2[1])));
  }
  area = Math.abs((area * R * R) / 2);
  return area / 10000; // m² → hectares
}
