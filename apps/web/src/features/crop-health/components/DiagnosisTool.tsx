/**
 * Diagnosis Tool Component
 * أداة تشخيص الأمراض
 */

'use client';

import React, { useState, useCallback } from 'react';
import { Upload, X, Camera, FileImage, AlertCircle, Loader2 } from 'lucide-react';
import { useCreateDiagnosis, useUploadDiagnosisImages } from '../hooks/useCropHealth';
import { logger } from '@/lib/logger';

interface DiagnosisToolProps {
  onDiagnosisCreated?: (diagnosisId: string) => void;
}

// Allowed MIME types for crop images (SVG excluded — XSS risk via embedded scripts)
const ALLOWED_IMAGE_MIME_TYPES = new Set<string>([
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/webp',
  'image/heic',
  'image/heif',
]);

// Max single-image size: 10 MB
const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024;
// Max number of images per diagnosis
const MAX_IMAGES_PER_DIAGNOSIS = 5;

export const DiagnosisTool: React.FC<DiagnosisToolProps> = ({ onDiagnosisCreated }) => {
  const [images, setImages] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [cropType, setCropType] = useState('');
  const [fieldId, setFieldId] = useState('');
  const [description, setDescription] = useState('');
  const [descriptionAr, setDescriptionAr] = useState('');
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [symptomsAr, setSymptomsAr] = useState<string[]>([]);
  const [error, setError] = useState<string>('');

  const uploadImages = useUploadDiagnosisImages();
  const createDiagnosis = useCreateDiagnosis();

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length === 0) return;

      // Validate MIME types (SVG and other exotic formats blocked)
      const invalidType = files.find((file) => !ALLOWED_IMAGE_MIME_TYPES.has(file.type));
      if (invalidType) {
        setError('نوع الصورة غير مدعوم. الأنواع المسموح بها: JPEG, PNG, WebP, HEIC');
        // Reset the input so selecting the same file again re-triggers onChange
        e.target.value = '';
        return;
      }

      // Validate size per file (10 MB each)
      const oversized = files.find((file) => file.size > MAX_IMAGE_SIZE_BYTES);
      if (oversized) {
        setError('حجم الصورة يتجاوز الحد الأقصى (10 ميجابايت لكل صورة)');
        e.target.value = '';
        return;
      }

      // Limit to MAX_IMAGES_PER_DIAGNOSIS
      const totalImages = images.length + files.length;
      if (totalImages > MAX_IMAGES_PER_DIAGNOSIS) {
        setError(`الحد الأقصى ${MAX_IMAGES_PER_DIAGNOSIS} صور`);
        e.target.value = '';
        return;
      }

      setError('');
      setImages((prev) => [...prev, ...files]);

      // Create previews (with error handling)
      files.forEach((file) => {
        const reader = new FileReader();
        reader.onload = () => {
          if (typeof reader.result === 'string') {
            setPreviews((prev) => [...prev, reader.result as string]);
          }
        };
        reader.onerror = () => {
          logger.error('FileReader failed to read image preview', reader.error);
        };
        reader.readAsDataURL(file);
      });

      // Reset the input so re-selecting the same file works
      e.target.value = '';
    },
    [images.length]
  );

  const handleRemoveImage = useCallback((index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
    setPreviews((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (images.length === 0) {
      setError('يرجى تحميل صورة واحدة على الأقل');
      return;
    }

    if (!cropType) {
      setError('يرجى اختيار نوع المحصول');
      return;
    }

    try {
      // Upload images first
      const imageUrls = await uploadImages.mutateAsync(images);

      // Create diagnosis request
      const diagnosis = await createDiagnosis.mutateAsync({
        cropType,
        cropTypeAr: cropType, // In real app, this would be mapped
        images: imageUrls,
        fieldId: fieldId || undefined,
        description: description || undefined,
        descriptionAr: descriptionAr || undefined,
        symptoms: symptoms.length > 0 ? symptoms : undefined,
        symptomsAr: symptomsAr.length > 0 ? symptomsAr : undefined,
      });

      // Reset form
      setImages([]);
      setPreviews([]);
      setCropType('');
      setFieldId('');
      setDescription('');
      setDescriptionAr('');
      setSymptoms([]);
      setSymptomsAr([]);

      // Notify parent
      if (onDiagnosisCreated) {
        onDiagnosisCreated(diagnosis.id);
      }
    } catch (err) {
      setError('حدث خطأ أثناء إنشاء التشخيص');
      logger.error(err);
    }
  };

  const isLoading = uploadImages.isPending || createDiagnosis.isPending;

  const cropTypes = [
    { value: 'wheat', label: 'Wheat', labelAr: 'قمح' },
    { value: 'corn', label: 'Corn', labelAr: 'ذرة' },
    { value: 'rice', label: 'Rice', labelAr: 'أرز' },
    { value: 'tomato', label: 'Tomato', labelAr: 'طماطم' },
    { value: 'potato', label: 'Potato', labelAr: 'بطاطس' },
    { value: 'cucumber', label: 'Cucumber', labelAr: 'خيار' },
    { value: 'pepper', label: 'Pepper', labelAr: 'فلفل' },
    { value: 'eggplant', label: 'Eggplant', labelAr: 'باذنجان' },
    { value: 'dates', label: 'Dates', labelAr: 'تمور' },
    { value: 'olive', label: 'Olive', labelAr: 'زيتون' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Camera className="w-6 h-6 text-green-500" />
          تشخيص الأمراض بالذكاء الاصطناعي
        </h2>
        <p className="text-sm text-gray-600 mt-1">AI Crop Disease Diagnosis</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Image Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            صور المحصول المصاب (حتى 5 صور)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {previews.map((preview, index) => (
              <div key={preview} className="relative group">
                <img
                  src={preview}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-32 object-cover rounded-lg border-2 border-gray-200"
                />
                <button
                  type="button"
                  onClick={() => handleRemoveImage(index)}
                  className="absolute top-2 left-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}

            {images.length < 5 && (
              <label className="flex flex-col items-center justify-center h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-green-500 hover:bg-green-50 transition-colors">
                <Upload className="w-8 h-8 text-gray-400 mb-2" />
                <span className="text-sm text-gray-600">تحميل صورة</span>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={isLoading}
                />
              </label>
            )}
          </div>
          <p className="mt-2 text-xs text-gray-500">
            صور واضحة للأوراق أو السيقان المصابة للحصول على تشخيص أفضل
          </p>
        </div>

        {/* Crop Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">نوع المحصول *</label>
          <select
            value={cropType}
            onChange={(e) => setCropType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
            disabled={isLoading}
          >
            <option value="">اختر نوع المحصول</option>
            {cropTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.labelAr} - {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Description (Arabic) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            وصف الأعراض (اختياري)
          </label>
          <textarea
            value={descriptionAr}
            onChange={(e) => setDescriptionAr(e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="صف ما تراه من أعراض على المحصول..."
            disabled={isLoading}
          />
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => {
              setImages([]);
              setPreviews([]);
              setCropType('');
              setDescription('');
              setDescriptionAr('');
              setError('');
            }}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            disabled={isLoading}
          >
            إعادة تعيين
          </button>
          <button
            type="submit"
            disabled={isLoading || images.length === 0 || !cropType}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                جاري التحليل...
              </>
            ) : (
              <>
                <Camera className="w-5 h-5" />
                بدء التشخيص
              </>
            )}
          </button>
        </div>
      </form>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <FileImage className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-medium mb-1">نصائح للحصول على تشخيص دقيق:</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>التقط صوراً واضحة في ضوء جيد</li>
              <li>صور الأوراق أو الأجزاء المصابة عن قرب</li>
              <li>التقط صوراً من زوايا مختلفة</li>
              <li>تأكد من ظهور الأعراض بوضوح في الصورة</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagnosisTool;
