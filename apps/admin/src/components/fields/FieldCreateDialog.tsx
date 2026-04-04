'use client';

/**
 * Field Create Dialog Component
 * حوار إنشاء حقل جديد
 *
 * Modal dialog for creating a new agricultural field with map-based boundary drawing.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { cn } from '@/lib/utils';
import { useToast } from '@/components/ui/Toast';
import { apiClient } from '@/lib/api';
import {
  X,
  MapPin,
  Loader2,
  Wheat,
  Droplets,
  Plus,
  AlertCircle,
} from 'lucide-react';

// Dynamic import for DrawableMap (SSR disabled - Leaflet requires browser APIs)
const DrawableMap = dynamic(() => import('../maps/DrawableMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full bg-gray-100 dark:bg-gray-700 animate-pulse flex items-center justify-center rounded-lg">
      <p className="text-gray-500 dark:text-gray-400 text-sm">جاري تحميل الخريطة...</p>
    </div>
  ),
});

// ─── Types ───────────────────────────────────────────────────────────────────

interface FieldCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (field: Record<string, unknown>) => void;
}

interface BoundaryData {
  coordinates: number[][][]; // GeoJSON polygon coordinates [[[lng, lat], ...]]
  area: number; // Area in hectares
  bbox: [number, number, number, number]; // [minLng, minLat, maxLng, maxLat]
}

type CropType =
  | 'wheat'
  | 'barley'
  | 'date_palm'
  | 'tomato'
  | 'cucumber'
  | 'corn'
  | 'rice'
  | 'other';

type IrrigationType = 'drip' | 'sprinkler' | 'flood' | 'pivot' | 'rain_fed';

// ─── Constants ───────────────────────────────────────────────────────────────

const CROP_OPTIONS: { value: CropType; labelAr: string; labelEn: string }[] = [
  { value: 'wheat', labelAr: 'قمح', labelEn: 'Wheat' },
  { value: 'barley', labelAr: 'شعير', labelEn: 'Barley' },
  { value: 'date_palm', labelAr: 'نخيل', labelEn: 'Date Palm' },
  { value: 'tomato', labelAr: 'طماطم', labelEn: 'Tomato' },
  { value: 'cucumber', labelAr: 'خيار', labelEn: 'Cucumber' },
  { value: 'corn', labelAr: 'ذرة', labelEn: 'Corn' },
  { value: 'rice', labelAr: 'أرز', labelEn: 'Rice' },
  { value: 'other', labelAr: 'أخرى', labelEn: 'Other' },
];

const IRRIGATION_OPTIONS: { value: IrrigationType; labelAr: string; labelEn: string }[] = [
  { value: 'drip', labelAr: 'تنقيط', labelEn: 'Drip' },
  { value: 'sprinkler', labelAr: 'رشاش', labelEn: 'Sprinkler' },
  { value: 'flood', labelAr: 'غمر', labelEn: 'Flood' },
  { value: 'pivot', labelAr: 'محوري', labelEn: 'Pivot' },
  { value: 'rain_fed', labelAr: 'بعلي', labelEn: 'Rain-fed' },
];

// ─── Component ───────────────────────────────────────────────────────────────

export default function FieldCreateDialog({
  open,
  onClose,
  onSuccess,
}: FieldCreateDialogProps) {
  const { toast } = useToast();
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Form state
  const [fieldName, setFieldName] = useState('');
  const [fieldNameAr, setFieldNameAr] = useState('');
  const [cropType, setCropType] = useState<CropType | ''>('');
  const [irrigationType, setIrrigationType] = useState<IrrigationType | ''>('');
  const [boundary, setBoundary] = useState<BoundaryData | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Focus management
  useEffect(() => {
    if (open) {
      previousFocusRef.current = document.activeElement as HTMLElement | null;
    } else if (previousFocusRef.current) {
      previousFocusRef.current.focus();
      previousFocusRef.current = null;
    }
  }, [open]);

  // Keyboard handling (Escape to close)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!open) return;
      if (e.key === 'Escape' && !isSubmitting) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, isSubmitting, onClose]);

  // Ref for accumulating boundary data from DrawableMap callbacks
  const boundaryRef = useRef<Partial<BoundaryData>>({});

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      setFieldName('');
      setFieldNameAr('');
      setCropType('');
      setIrrigationType('');
      setBoundary(null);
      setError(null);
      boundaryRef.current = {};
    }
  }, [open]);

  const handleBboxSelect = useCallback((bbox: [number, number, number, number]) => {
    boundaryRef.current.bbox = bbox;
    if (boundaryRef.current.coordinates) {
      // Calculate approximate area from bbox
      const [minLng, minLat, maxLng, maxLat] = bbox;
      const latMid = (minLat + maxLat) / 2;
      const cosLat = Math.cos((latMid * Math.PI) / 180);
      const widthKm = Math.abs(maxLng - minLng) * 111.32 * cosLat;
      const heightKm = Math.abs(maxLat - minLat) * 111.32;
      const areaHa = (widthKm * heightKm) * 100;
      setBoundary({
        coordinates: boundaryRef.current.coordinates,
        bbox,
        area: Math.round(areaHa * 100) / 100,
      });
    }
  }, []);

  const handleBoundaryDraw = useCallback((coordinates: number[][][]) => {
    boundaryRef.current.coordinates = coordinates;
    if (boundaryRef.current.bbox) {
      handleBboxSelect(boundaryRef.current.bbox);
    }
  }, [handleBboxSelect]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);

      // Validation
      if (!fieldName.trim()) {
        setError('اسم الحقل مطلوب - Field name is required');
        return;
      }
      if (!cropType) {
        setError('نوع المحصول مطلوب - Crop type is required');
        return;
      }
      if (!irrigationType) {
        setError('نوع الري مطلوب - Irrigation type is required');
        return;
      }
      if (!boundary) {
        setError('يرجى رسم حدود الحقل على الخريطة - Please draw field boundary on the map');
        return;
      }

      setIsSubmitting(true);

      try {
        // Extract flat 2D coordinates from GeoJSON 3D boundary
        // Backend expects: coordinates as [[lng,lat], ...] (2D) AND/OR boundary as GeoJSON
        const flatCoords = boundary.coordinates[0]; // First ring of GeoJSON polygon

        const response = await apiClient.post('/api/v1/fields', {
          name: fieldName.trim(),
          nameAr: fieldNameAr.trim() || undefined,
          cropType,
          irrigationType,
          // tenantId: extracted from JWT by backend controller, but DTO requires a value
          coordinates: flatCoords,
          boundary: {
            type: 'Polygon',
            coordinates: boundary.coordinates,
          },
        });

        toast.success(
          'Field created successfully',
          'تم إنشاء الحقل بنجاح'
        );

        onSuccess(response.data);
        onClose();
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { messageAr?: string; message?: string } } };
        const message =
          axiosErr?.response?.data?.messageAr ||
          axiosErr?.response?.data?.message ||
          'حدث خطأ أثناء إنشاء الحقل - An error occurred while creating the field';
        setError(message);
        toast.error(
          'Failed to create field',
          'فشل في إنشاء الحقل'
        );
      } finally {
        setIsSubmitting(false);
      }
    },
    [fieldName, fieldNameAr, cropType, irrigationType, boundary, onSuccess, onClose, toast]
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[9998] flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="field-create-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-fade-in"
        onClick={() => !isSubmitting && onClose()}
      />

      {/* Dialog */}
      <div
        ref={dialogRef}
        dir="rtl"
        className={cn(
          'relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl',
          'w-[95vw] max-w-4xl max-h-[90vh] mx-4',
          'flex flex-col animate-scale-in overflow-hidden'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <Plus className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h2
                id="field-create-title"
                className="text-lg font-semibold text-gray-900 dark:text-gray-100"
              >
                إنشاء حقل جديد
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Create New Field
              </p>
            </div>
          </div>
          <button
            onClick={() => !isSubmitting && onClose()}
            disabled={isSubmitting}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition disabled:opacity-50"
            aria-label="إغلاق"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-5">
            {/* Error Alert */}
            {error && (
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}

            {/* Form Fields Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Field Name (English) */}
              <div>
                <label
                  htmlFor="field-name"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  اسم الحقل (إنجليزي) <span className="text-red-500">*</span>
                </label>
                <input
                  id="field-name"
                  type="text"
                  dir="ltr"
                  value={fieldName}
                  onChange={(e) => setFieldName(e.target.value)}
                  placeholder="Field Name"
                  required
                  disabled={isSubmitting}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg border text-sm',
                    'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                    'disabled:opacity-50 disabled:cursor-not-allowed',
                    'transition'
                  )}
                />
              </div>

              {/* Field Name (Arabic) */}
              <div>
                <label
                  htmlFor="field-name-ar"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  اسم الحقل (عربي)
                </label>
                <input
                  id="field-name-ar"
                  type="text"
                  dir="rtl"
                  value={fieldNameAr}
                  onChange={(e) => setFieldNameAr(e.target.value)}
                  placeholder="اسم الحقل"
                  disabled={isSubmitting}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg border text-sm',
                    'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                    'disabled:opacity-50 disabled:cursor-not-allowed',
                    'transition'
                  )}
                />
              </div>

              {/* Crop Type */}
              <div>
                <label
                  htmlFor="crop-type"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  <span className="inline-flex items-center gap-1.5">
                    <Wheat className="w-4 h-4" />
                    نوع المحصول <span className="text-red-500">*</span>
                  </span>
                </label>
                <select
                  id="crop-type"
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value as CropType)}
                  required
                  disabled={isSubmitting}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg border text-sm',
                    'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'disabled:opacity-50 disabled:cursor-not-allowed',
                    'transition'
                  )}
                >
                  <option value="">-- اختر نوع المحصول --</option>
                  {CROP_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.labelAr} - {opt.labelEn}
                    </option>
                  ))}
                </select>
              </div>

              {/* Irrigation Type */}
              <div>
                <label
                  htmlFor="irrigation-type"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  <span className="inline-flex items-center gap-1.5">
                    <Droplets className="w-4 h-4" />
                    نوع الري <span className="text-red-500">*</span>
                  </span>
                </label>
                <select
                  id="irrigation-type"
                  value={irrigationType}
                  onChange={(e) => setIrrigationType(e.target.value as IrrigationType)}
                  required
                  disabled={isSubmitting}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg border text-sm',
                    'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'disabled:opacity-50 disabled:cursor-not-allowed',
                    'transition'
                  )}
                >
                  <option value="">-- اختر نوع الري --</option>
                  {IRRIGATION_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.labelAr} - {opt.labelEn}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Map Section */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                <span className="inline-flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  حدود الحقل <span className="text-red-500">*</span>
                </span>
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                ارسم حدود الحقل على الخريطة باستخدام أدوات الرسم
                <span className="mx-1">|</span>
                <span dir="ltr">Draw the field boundary on the map using the drawing tools</span>
              </p>
              <div className="h-[400px] rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
                <DrawableMap
                  onBboxSelect={handleBboxSelect}
                  onBoundaryDraw={handleBoundaryDraw}
                  height="400px"
                />
              </div>
            </div>

            {/* Boundary Info (shown after drawing) */}
            {boundary && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Calculated Area */}
                <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                  <p className="text-xs text-green-600 dark:text-green-400 font-medium mb-1">
                    المساحة المحسوبة | Calculated Area
                  </p>
                  <p className="text-lg font-bold text-green-800 dark:text-green-200" dir="ltr">
                    {boundary.area.toFixed(2)} ha
                  </p>
                </div>

                {/* Bounding Box */}
                <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                  <p className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">
                    الإحداثيات المحيطة | Bounding Box
                  </p>
                  <div className="text-xs text-blue-800 dark:text-blue-200 font-mono space-y-0.5" dir="ltr">
                    <p>Min: {boundary.bbox[0].toFixed(5)}, {boundary.bbox[1].toFixed(5)}</p>
                    <p>Max: {boundary.bbox[2].toFixed(5)}, {boundary.bbox[3].toFixed(5)}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className={cn(
                'px-5 py-2.5 text-sm font-medium rounded-lg transition',
                'text-gray-700 dark:text-gray-300',
                'bg-gray-100 dark:bg-gray-700',
                'hover:bg-gray-200 dark:hover:bg-gray-600',
                'focus:ring-2 focus:ring-gray-400 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={cn(
                'px-5 py-2.5 text-sm font-medium text-white rounded-lg transition',
                'bg-green-600 hover:bg-green-700',
                'focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'flex items-center gap-2'
              )}
            >
              {isSubmitting && (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              {isSubmitting ? 'جاري الإنشاء...' : 'إنشاء الحقل'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
