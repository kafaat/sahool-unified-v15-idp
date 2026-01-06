'use client';

/**
 * Observation Form Component
 * مكون نموذج الملاحظة
 *
 * Form for creating/editing field observations with:
 * - Location (auto-filled from map click)
 * - Category and subcategory selection
 * - Severity slider
 * - Photo upload with drag & drop
 * - Notes
 * - Optional task creation
 */

import React, { useState, useCallback, useRef } from 'react';
import { useLocale } from 'next-intl';
import {
  Bug,
  Activity,
  Sprout,
  Leaf,
  Droplets,
  AlertCircle,
  Upload,
  X,
  CheckCircle,
  Image as ImageIcon,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import type {
  ObservationFormData,
  ObservationCategory,
  Severity,
  GeoPoint,
} from '../types/scouting';
import { CATEGORY_OPTIONS, SEVERITY_LABELS } from '../types/scouting';
import { clsx } from 'clsx';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ObservationFormProps {
  location: GeoPoint;
  onSubmit: (data: ObservationFormData) => void | Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
  initialData?: Partial<ObservationFormData>;
}

interface PhotoPreview {
  file: File;
  url: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Icon Map
// ═══════════════════════════════════════════════════════════════════════════

const ICON_MAP = {
  Bug,
  Activity,
  Sprout,
  Leaf,
  Droplets,
  AlertCircle,
};

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const ObservationForm: React.FC<ObservationFormProps> = ({
  location,
  onSubmit,
  onCancel,
  isSubmitting = false,
  initialData,
}) => {
  const locale = useLocale();
  const isArabic = locale === 'ar';
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form state
  const [category, setCategory] = useState<ObservationCategory | null>(
    initialData?.category || null
  );
  const [subcategory, setSubcategory] = useState<string | null>(
    initialData?.subcategory || null
  );
  const [severity, setSeverity] = useState<Severity>(initialData?.severity || 3);
  const [notes, setNotes] = useState(initialData?.notes || '');
  const [photos, setPhotos] = useState<PhotoPreview[]>([]);
  const [createTask, setCreateTask] = useState(initialData?.createTask || false);
  const [isDragging, setIsDragging] = useState(false);

  // Get selected category option
  const selectedCategoryOption = CATEGORY_OPTIONS.find((opt) => opt.value === category);
  const subcategoryOptions = selectedCategoryOption?.subcategories || [];

  // Validation
  const canSubmit = category && severity && notes.trim().length > 0;

  // ─────────────────────────────────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────────────────────────────────

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || isSubmitting) return;

    const selectedSubcategory = subcategoryOptions.find((opt) => opt.value === subcategory);

    const formData: ObservationFormData = {
      location,
      category: category!,
      subcategory: subcategory || undefined,
      subcategoryAr: selectedSubcategory?.labelAr,
      severity,
      notes,
      notesAr: notes, // In production, you might want separate Arabic notes
      photos: photos.map((p) => p.file),
      createTask,
    };

    await onSubmit(formData);
  };

  const handlePhotoSelect = useCallback((files: FileList | null) => {
    if (!files) return;

    const newPhotos: PhotoPreview[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.type.startsWith('image/')) {
        newPhotos.push({
          file,
          url: URL.createObjectURL(file),
        });
      }
    }

    setPhotos((prev) => [...prev, ...newPhotos]);
  }, []);

  const handleRemovePhoto = useCallback((index: number) => {
    setPhotos((prev) => {
      const updated = [...prev];
      URL.revokeObjectURL(updated[index].url);
      updated.splice(index, 1);
      return updated;
    });
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handlePhotoSelect(e.dataTransfer.files);
    },
    [handlePhotoSelect]
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-sahool-green-600" />
          {isArabic ? 'ملاحظة جديدة' : 'New Observation'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Step 1: Category Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              {isArabic ? '1. نوع المشكلة' : '1. Issue Category'}
              <span className="text-red-500 ml-1">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {CATEGORY_OPTIONS.map((option) => {
                const IconComponent = ICON_MAP[option.icon as keyof typeof ICON_MAP];
                const isSelected = category === option.value;

                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => {
                      setCategory(option.value);
                      setSubcategory(null);
                    }}
                    className={clsx(
                      'p-4 rounded-lg border-2 transition-all duration-200 text-left',
                      'hover:border-sahool-green-500 hover:shadow-md',
                      isSelected
                        ? 'border-sahool-green-600 bg-sahool-green-50 shadow-md'
                        : 'border-gray-200 bg-white'
                    )}
                    style={{
                      borderColor: isSelected ? option.color : undefined,
                      backgroundColor: isSelected ? `${option.color}15` : undefined,
                    }}
                  >
                    <div className="flex items-center gap-3">
                      {IconComponent && (
                        <IconComponent
                          className="w-6 h-6"
                          style={{ color: isSelected ? option.color : '#9ca3af' }}
                        />
                      )}
                      <div className="flex-1">
                        <p
                          className="font-semibold text-sm"
                          style={{ color: isSelected ? option.color : '#1f2937' }}
                        >
                          {isArabic ? option.labelAr : option.label}
                        </p>
                      </div>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5" style={{ color: option.color }} />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Step 2: Subcategory Selection */}
          {category && subcategoryOptions.length > 0 && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                {isArabic ? '2. تفاصيل المشكلة' : '2. Issue Details'}
              </label>
              <div className="flex flex-wrap gap-2">
                {subcategoryOptions.map((option) => {
                  const isSelected = subcategory === option.value;
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setSubcategory(option.value)}
                      className={clsx(
                        'px-4 py-2 rounded-full border text-sm font-medium transition-all',
                        isSelected
                          ? 'border-sahool-green-600 bg-sahool-green-600 text-white'
                          : 'border-gray-300 bg-white text-gray-700 hover:border-sahool-green-400'
                      )}
                    >
                      <div className="text-center">
                        <div>{isArabic ? option.labelAr : option.label}</div>
                        {option.description && (
                          <div className="text-xs opacity-80">
                            {isArabic ? option.descriptionAr : option.description}
                          </div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Step 3: Severity */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              {isArabic ? '3. شدة المشكلة' : '3. Severity Level'}
              <span className="text-red-500 ml-1">*</span>
            </label>
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-gray-600">
                  {isArabic ? SEVERITY_LABELS[1].ar : SEVERITY_LABELS[1].en}
                </span>
                <div
                  className="px-4 py-2 rounded-full font-bold text-sm"
                  style={{
                    backgroundColor: `${SEVERITY_LABELS[severity].color}20`,
                    color: SEVERITY_LABELS[severity].color,
                  }}
                >
                  {isArabic ? SEVERITY_LABELS[severity].ar : SEVERITY_LABELS[severity].en}
                </div>
                <span className="text-xs text-gray-600">
                  {isArabic ? SEVERITY_LABELS[5].ar : SEVERITY_LABELS[5].en}
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                step="1"
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value) as Severity)}
                className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, ${SEVERITY_LABELS[1].color}, ${SEVERITY_LABELS[3].color}, ${SEVERITY_LABELS[5].color})`,
                }}
              />
              <div className="flex justify-between mt-2">
                {[1, 2, 3, 4, 5].map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setSeverity(val as Severity)}
                    className={clsx(
                      'w-8 h-8 rounded-full text-xs font-bold transition-all',
                      severity === val
                        ? 'ring-4 ring-offset-2'
                        : 'opacity-50 hover:opacity-100'
                    )}
                    style={{
                      backgroundColor: SEVERITY_LABELS[val as Severity].color,
                      color: 'white',
                      ringColor: SEVERITY_LABELS[val as Severity].color,
                    }}
                  >
                    {val}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Step 4: Photo Upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              {isArabic ? '4. الصور (اختياري)' : '4. Photos (Optional)'}
            </label>
            <div
              className={clsx(
                'border-2 border-dashed rounded-lg p-6 text-center transition-all',
                isDragging
                  ? 'border-sahool-green-500 bg-sahool-green-50'
                  : 'border-gray-300 hover:border-gray-400'
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={(e) => handlePhotoSelect(e.target.files)}
              />
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-2" />
              <p className="text-sm text-gray-600 mb-2">
                {isArabic
                  ? 'اسحب الصور هنا أو انقر للتحميل'
                  : 'Drag photos here or click to upload'}
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
              >
                <ImageIcon className="w-4 h-4 mr-2" />
                {isArabic ? 'اختر الصور' : 'Choose Photos'}
              </Button>
            </div>

            {/* Photo Previews */}
            {photos.length > 0 && (
              <div className="grid grid-cols-3 gap-3 mt-4">
                {photos.map((photo, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={photo.url}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-24 object-cover rounded-lg border border-gray-200"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemovePhoto(index)}
                      className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Step 5: Notes */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              {isArabic ? '5. ملاحظات' : '5. Notes'}
              <span className="text-red-500 ml-1">*</span>
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              placeholder={
                isArabic
                  ? 'اكتب ملاحظاتك حول المشكلة...'
                  : 'Write your notes about the issue...'
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Step 6: Create Task Checkbox */}
          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
            <input
              type="checkbox"
              id="createTask"
              checked={createTask}
              onChange={(e) => setCreateTask(e.target.checked)}
              className="w-5 h-5 text-sahool-green-600 rounded focus:ring-sahool-green-500"
            />
            <label htmlFor="createTask" className="text-sm font-medium text-gray-700 cursor-pointer">
              {isArabic ? 'إنشاء مهمة للمتابعة' : 'Create follow-up task'}
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
              className="flex-1"
            >
              {isArabic ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button
              type="submit"
              disabled={!canSubmit || isSubmitting}
              className="flex-1"
            >
              {isSubmitting
                ? isArabic
                  ? 'جاري الحفظ...'
                  : 'Saving...'
                : isArabic
                ? 'حفظ الملاحظة'
                : 'Save Observation'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default ObservationForm;
