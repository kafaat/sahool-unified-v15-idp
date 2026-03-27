'use client';

import React, { useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  MapPin,
  Upload,
  Search,
  Plus,
  FileUp,
  Pencil,
  Save,
  Leaf,
  Calendar,
  Check,
  Loader2,
  AlertTriangle,
  CheckCircle,
  Trash2,
} from 'lucide-react';
import { useCreateField } from '@/features/farmonaut';
import type { BoundaryInputMethod, FieldBoundary } from '@/features/farmonaut';

const CROP_TYPES = [
  { value: 'wheat', label: 'Wheat', labelAr: 'قمح' },
  { value: 'barley', label: 'Barley', labelAr: 'شعير' },
  { value: 'date_palm', label: 'Date Palm', labelAr: 'نخيل' },
  { value: 'tomato', label: 'Tomato', labelAr: 'طماطم' },
  { value: 'cucumber', label: 'Cucumber', labelAr: 'خيار' },
  { value: 'corn', label: 'Corn', labelAr: 'ذرة' },
  { value: 'soybean', label: 'Soybean', labelAr: 'فول الصويا' },
  { value: 'rice', label: 'Rice', labelAr: 'أرز' },
  { value: 'alfalfa', label: 'Alfalfa', labelAr: 'برسيم' },
  { value: 'cotton', label: 'Cotton', labelAr: 'قطن' },
  { value: 'other', label: 'Other', labelAr: 'أخرى' },
];

const BOUNDARY_METHODS: Array<{ method: BoundaryInputMethod; label: string; labelAr: string; icon: React.ComponentType<{ className?: string }> }> = [
  { method: 'draw', label: 'Draw on Map', labelAr: 'رسم على الخريطة', icon: Pencil },
  { method: 'kml', label: 'Upload KML File', labelAr: 'رفع ملف KML', icon: FileUp },
  { method: 'shapefile', label: 'Upload Shapefile', labelAr: 'رفع ملف Shapefile', icon: Upload },
  { method: 'coordinates', label: 'Enter Coordinates', labelAr: 'إدخال الإحداثيات', icon: MapPin },
];

export default function AddFieldClient() {
  const router = useRouter();
  const createField = useCreateField();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [boundaryMethod, setBoundaryMethod] = useState<BoundaryInputMethod>('draw');
  const [boundaryPoints, setBoundaryPoints] = useState<FieldBoundary[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    nameAr: '',
    cropType: '',
    sowingDate: '',
    address: '',
    lat: '',
    lng: '',
  });

  // Validate step before advancing
  const validateStep = (currentStep: number): boolean => {
    const errors: string[] = [];
    if (currentStep === 1) {
      if (!formData.lat && !formData.lng && !formData.address) {
        errors.push('يرجى تحديد الموقع بالعنوان أو الإحداثيات');
      }
      if (formData.lat && (parseFloat(formData.lat) < -90 || parseFloat(formData.lat) > 90)) {
        errors.push('خط العرض يجب أن يكون بين -90 و 90');
      }
      if (formData.lng && (parseFloat(formData.lng) < -180 || parseFloat(formData.lng) > 180)) {
        errors.push('خط الطول يجب أن يكون بين -180 و 180');
      }
    }
    if (currentStep === 2) {
      if (boundaryMethod === 'coordinates' && boundaryPoints.length < 3) {
        errors.push('يجب إدخال 3 نقاط على الأقل لتحديد الحدود');
      }
      if ((boundaryMethod === 'kml' || boundaryMethod === 'shapefile') && !uploadedFile) {
        errors.push('يرجى رفع ملف الحدود');
      }
    }
    setValidationErrors(errors);
    return errors.length === 0;
  };

  const goToStep = (target: 1 | 2 | 3) => {
    if (target > step && !validateStep(step)) return;
    setValidationErrors([]);
    setStep(target);
  };

  // Add/remove boundary points for manual coordinate entry
  const addBoundaryPoint = () => {
    setBoundaryPoints([...boundaryPoints, { lat: 0, lng: 0 }]);
  };
  const removeBoundaryPoint = (index: number) => {
    setBoundaryPoints(boundaryPoints.filter((_, i) => i !== index));
  };
  const updateBoundaryPoint = (index: number, field: 'lat' | 'lng', value: string) => {
    const updated = [...boundaryPoints];
    updated[index] = { ...updated[index], [field]: parseFloat(value) || 0 };
    setBoundaryPoints(updated);
  };

  // Handle file upload for KML/Shapefile
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setUploadedFile(file);
  };

  // Submit field creation
  const handleSubmit = useCallback(async () => {
    if (!validateStep(3)) return;
    if (!formData.nameAr || !formData.cropType) {
      setValidationErrors(['يرجى ملء اسم الحقل ونوع المحصول']);
      return;
    }
    try {
      await createField.mutateAsync({
        name: formData.name || formData.nameAr,
        nameAr: formData.nameAr,
        cropType: formData.cropType,
        sowingDate: formData.sowingDate,
        boundary: boundaryPoints.length > 0 ? boundaryPoints : [
          { lat: parseFloat(formData.lat) || 0, lng: parseFloat(formData.lng) || 0 },
        ],
        boundaryMethod,
        address: formData.address || undefined,
        coordinates: formData.lat && formData.lng
          ? { lat: parseFloat(formData.lat), lng: parseFloat(formData.lng) }
          : undefined,
      });
    } catch {
      // Error handled by mutation
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData, boundaryPoints, boundaryMethod, createField]);

  // Success state
  if (createField.isSuccess) {
    return (
      <div className="max-w-lg mx-auto mt-16 text-center space-y-4">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
        <h2 className="text-2xl font-bold text-gray-900">تم إرسال الحقل للمعالجة</h2>
        <p className="text-gray-500">ستصل أول صورة قمر صناعي خلال 3-5 أيام</p>
        <p className="text-sm text-gray-400">Field submitted for pre-processing. First image in 3-5 days.</p>
        <Link href="/farmonaut" className="inline-block px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm mt-4">
          العودة للوحة التحكم
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/farmonaut" className="hover:text-green-600">مراقبة فارمونوت</Link>
        <ArrowRight className="w-3 h-3" />
        <span className="text-gray-900 font-medium">إضافة حقل جديد</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold text-gray-900">إضافة حقل جديد</h1>
        <p className="text-gray-500 text-sm mt-1">Add a New Field for Satellite Monitoring</p>
      </div>

      {/* Steps Indicator */}
      <div className="flex items-center gap-4">
        {[
          { num: 1, label: 'تحديد الموقع', labelEn: 'Location' },
          { num: 2, label: 'رسم الحدود', labelEn: 'Boundaries' },
          { num: 3, label: 'معلومات المحصول', labelEn: 'Crop Info' },
        ].map(({ num, label, labelEn }) => (
          <div key={num} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              step === num ? 'bg-green-600 text-white' :
              step > num ? 'bg-green-100 text-green-700' :
              'bg-gray-200 text-gray-500'
            }`}>
              {step > num ? <Check className="w-4 h-4" /> : num}
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900">{label}</div>
              <div className="text-[10px] text-gray-400">{labelEn}</div>
            </div>
            {num < 3 && <div className="w-12 h-0.5 bg-gray-200 mx-2" />}
          </div>
        ))}
      </div>

      {/* Step 1: Location */}
      {step === 1 && (
        <div className="bg-white rounded-lg border p-6 space-y-6">
          <h2 className="font-semibold text-gray-900">تحديد موقع المزرعة</h2>

          {/* Search by Address */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">البحث بالعنوان</label>
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="ابحث عن موقع مزرعتك..."
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>
              <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                بحث
              </button>
            </div>
          </div>

          {/* Or GPS Coordinates */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t" /></div>
            <div className="relative flex justify-center"><span className="bg-white px-3 text-sm text-gray-500">أو إدخال الإحداثيات</span></div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">خط العرض (Latitude)</label>
              <input
                type="number"
                step="0.0001"
                placeholder="24.7136"
                value={formData.lat}
                onChange={(e) => setFormData({ ...formData, lat: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">خط الطول (Longitude)</label>
              <input
                type="number"
                step="0.0001"
                placeholder="46.6753"
                value={formData.lng}
                onChange={(e) => setFormData({ ...formData, lng: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
          </div>

          {/* Map placeholder */}
          <div className="aspect-video bg-gradient-to-br from-blue-50 via-green-50 to-green-100 rounded-lg border-2 border-dashed border-green-300 flex items-center justify-center">
            <div className="text-center">
              <MapPin className="w-12 h-12 text-green-500 mx-auto mb-2" />
              <p className="text-green-700 font-medium">خريطة تفاعلية</p>
              <p className="text-green-600 text-sm">حدد موقع مزرعتك على الخريطة</p>
            </div>
          </div>

          {validationErrors.length > 0 && step === 1 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              {validationErrors.map((err, i) => (
                <p key={i} className="text-red-600 text-sm flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> {err}
                </p>
              ))}
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={() => goToStep(2)}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
            >
              التالي: رسم الحدود
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Boundaries */}
      {step === 2 && (
        <div className="bg-white rounded-lg border p-6 space-y-6">
          <h2 className="font-semibold text-gray-900">تحديد حدود الحقل</h2>

          {/* Boundary Method Selection */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {BOUNDARY_METHODS.map(({ method, labelAr, icon: Icon }) => (
              <button
                key={method}
                onClick={() => setBoundaryMethod(method)}
                className={`p-4 rounded-lg border text-center transition-all ${
                  boundaryMethod === method
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm font-medium">{labelAr}</span>
              </button>
            ))}
          </div>

          {/* Method-specific content */}
          {boundaryMethod === 'draw' && (
            <div className="aspect-video bg-gradient-to-br from-green-50 via-green-100 to-green-200 rounded-lg border-2 border-green-300 flex items-center justify-center">
              <div className="text-center">
                <Pencil className="w-12 h-12 text-green-600 mx-auto mb-2" />
                <p className="text-green-800 font-medium">انقر على الخريطة لتحديد نقاط الحدود</p>
                <p className="text-green-600 text-sm mt-1">سيتم ربط النقاط تلقائياً لإنشاء المضلع</p>
              </div>
            </div>
          )}

          {(boundaryMethod === 'kml' || boundaryMethod === 'shapefile') && (
            <div className="p-8 border-2 border-dashed border-gray-300 rounded-lg text-center">
              {uploadedFile ? (
                <>
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                  <p className="font-medium text-green-700">{uploadedFile.name}</p>
                  <p className="text-sm text-gray-500 mt-1">{(uploadedFile.size / 1024).toFixed(1)} KB</p>
                  <button
                    onClick={() => setUploadedFile(null)}
                    className="mt-3 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 text-sm"
                  >
                    إزالة الملف
                  </button>
                </>
              ) : (
                <>
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="font-medium text-gray-700">
                    {boundaryMethod === 'kml' ? 'ارفع ملف KML (.kml, .kmz)' : 'ارفع ملف Shapefile (.shp, .geojson)'}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">اسحب الملف هنا أو انقر للاختيار</p>
                  <label className="mt-4 inline-block px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm cursor-pointer">
                    اختيار ملف
                    <input
                      type="file"
                      className="hidden"
                      accept={boundaryMethod === 'kml' ? '.kml,.kmz' : '.shp,.geojson,.json'}
                      onChange={handleFileUpload}
                    />
                  </label>
                </>
              )}
            </div>
          )}

          {boundaryMethod === 'coordinates' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600">أدخل إحداثيات نقاط الحدود (خط عرض، خط طول) لكل نقطة (3 نقاط على الأقل):</p>
              {boundaryPoints.map((point, idx) => (
                <div key={idx} className="grid grid-cols-4 gap-3 items-center">
                  <span className="text-sm text-gray-500">النقطة {idx + 1}:</span>
                  <input
                    type="number"
                    step="0.0001"
                    placeholder="خط العرض"
                    value={point.lat || ''}
                    onChange={(e) => updateBoundaryPoint(idx, 'lat', e.target.value)}
                    className="px-3 py-2 border rounded-lg text-sm"
                  />
                  <input
                    type="number"
                    step="0.0001"
                    placeholder="خط الطول"
                    value={point.lng || ''}
                    onChange={(e) => updateBoundaryPoint(idx, 'lng', e.target.value)}
                    className="px-3 py-2 border rounded-lg text-sm"
                  />
                  <button
                    onClick={() => removeBoundaryPoint(idx)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded"
                    title="حذف النقطة"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <button
                onClick={addBoundaryPoint}
                className="flex items-center gap-1 text-sm text-green-600 hover:text-green-700"
              >
                <Plus className="w-4 h-4" /> إضافة نقطة
              </button>
              {boundaryPoints.length > 0 && (
                <p className="text-xs text-gray-400">{boundaryPoints.length} نقاط محددة (الحد الأدنى: 3)</p>
              )}
            </div>
          )}

          {validationErrors.length > 0 && step === 2 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              {validationErrors.map((err, i) => (
                <p key={i} className="text-red-600 text-sm flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> {err}
                </p>
              ))}
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(1)} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm">
              السابق
            </button>
            <button onClick={() => goToStep(3)} className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
              التالي: معلومات المحصول
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Crop Info */}
      {step === 3 && (
        <div className="bg-white rounded-lg border p-6 space-y-6">
          <h2 className="font-semibold text-gray-900">معلومات المحصول</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">اسم الحقل (عربي)</label>
              <input
                type="text"
                placeholder="مثال: حقل القمح الشمالي"
                value={formData.nameAr}
                onChange={(e) => setFormData({ ...formData, nameAr: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Field Name (English)</label>
              <input
                type="text"
                placeholder="e.g. Northern Wheat Field"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">نوع المحصول</label>
              <select
                value={formData.cropType}
                onChange={(e) => setFormData({ ...formData, cropType: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
              >
                <option value="">اختر نوع المحصول...</option>
                {CROP_TYPES.map((c) => (
                  <option key={c.value} value={c.value}>{c.labelAr} ({c.label})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ البذر</label>
              <input
                type="date"
                value={formData.sowingDate}
                onChange={(e) => setFormData({ ...formData, sowingDate: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800">
            <p className="font-medium mb-1">ملاحظة:</p>
            <p>سيتم إرسال الحقل للمعالجة المسبقة. ستصل أول صورة قمر صناعي خلال 3-5 أيام.</p>
            <p className="text-xs text-blue-600 mt-1">Submit for pre-processing. First satellite image within 3-5 days.</p>
          </div>

          {validationErrors.length > 0 && step === 3 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              {validationErrors.map((err, i) => (
                <p key={i} className="text-red-600 text-sm flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> {err}
                </p>
              ))}
            </div>
          )}

          {createField.isError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> فشل في إنشاء الحقل. يرجى المحاولة مرة أخرى.
              </p>
              <p className="text-red-500 text-xs mt-1">Failed to create field. Please try again.</p>
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(2)} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm">
              السابق
            </button>
            <button
              onClick={handleSubmit}
              disabled={createField.isPending}
              className="inline-flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {createField.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {createField.isPending ? 'جاري الإرسال...' : 'إرسال للمعالجة المسبقة'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
