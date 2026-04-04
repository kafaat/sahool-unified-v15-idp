'use client';

/**
 * Field Create Dialog — انشاء حقل جديد
 * Modal dialog for creating new fields with form inputs (name, crop type,
 * irrigation type) and an embedded drawable map for boundary drawing.
 * Extracts GeoJSON boundary and submits to API.
 */

import React, { useState, useCallback, useRef } from 'react';
import { clsx } from 'clsx';
import {
  X,
  MapPin,
  Wheat,
  Droplets,
  PenTool,
  Trash2,
  Loader2,
  Check,
  AlertCircle,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FieldBoundary {
  type: 'Polygon';
  coordinates: [number, number][][];
}

export interface FieldCreateData {
  name: string;
  nameAr: string;
  cropType: string;
  irrigationType: string;
  areaHectares?: number;
  boundary?: FieldBoundary;
}

export interface FieldCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: FieldCreateData) => Promise<void> | void;
  className?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CROP_OPTIONS = [
  { value: '', labelAr: 'اختر المحصول', label: 'Select crop' },
  { value: 'wheat', labelAr: 'قمح', label: 'Wheat' },
  { value: 'barley', labelAr: 'شعير', label: 'Barley' },
  { value: 'sorghum', labelAr: 'ذرة رفيعة', label: 'Sorghum' },
  { value: 'tomato', labelAr: 'طماطم', label: 'Tomato' },
  { value: 'onion', labelAr: 'بصل', label: 'Onion' },
  { value: 'cucumber', labelAr: 'خيار', label: 'Cucumber' },
  { value: 'date_palm', labelAr: 'نخيل', label: 'Date Palm' },
  { value: 'coffee', labelAr: 'بن', label: 'Coffee' },
  { value: 'banana', labelAr: 'موز', label: 'Banana' },
  { value: 'mango', labelAr: 'مانجو', label: 'Mango' },
  { value: 'sesame', labelAr: 'سمسم', label: 'Sesame' },
  { value: 'qat', labelAr: 'قات', label: 'Qat' },
] as const;

const IRRIGATION_OPTIONS = [
  { value: '', labelAr: 'اختر نوع الري', label: 'Select irrigation' },
  { value: 'drip', labelAr: 'تنقيط', label: 'Drip' },
  { value: 'sprinkler', labelAr: 'رشاش', label: 'Sprinkler' },
  { value: 'pivot', labelAr: 'محوري', label: 'Center Pivot' },
  { value: 'flood', labelAr: 'غمر', label: 'Flood' },
  { value: 'furrow', labelAr: 'اخدود', label: 'Furrow' },
  { value: 'rainfed', labelAr: 'بعلي (مطري)', label: 'Rainfed' },
] as const;

// ---------------------------------------------------------------------------
// DrawableMap (placeholder for map integration)
// ---------------------------------------------------------------------------

interface DrawableMapProps {
  points: [number, number][];
  onPointsChange: (points: [number, number][]) => void;
  isDrawing: boolean;
}

function DrawableMap({ points, onPointsChange, isDrawing }: DrawableMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);

  const handleMapClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!isDrawing || !mapRef.current) return;

      const rect = mapRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Map pixel coordinates to approximate geo coordinates
      // Default center: Yemen (15.5, 44.2) with ~0.01 degree per 10px
      const lng = 44.2 + ((x - rect.width / 2) / rect.width) * 0.5;
      const lat = 15.5 - ((y - rect.height / 2) / rect.height) * 0.5;

      onPointsChange([...points, [lng, lat]]);
    },
    [isDrawing, points, onPointsChange],
  );

  return (
    <div
      ref={mapRef}
      onClick={handleMapClick}
      className={clsx(
        'relative w-full h-64 rounded-xl overflow-hidden border-2',
        isDrawing
          ? 'border-green-400 dark:border-green-600 cursor-crosshair'
          : 'border-gray-200 dark:border-gray-700 cursor-default',
        'bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50',
        'dark:from-gray-800 dark:via-gray-750 dark:to-gray-700',
      )}
    >
      {/* Map placeholder background */}
      <div className="absolute inset-0 opacity-10">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" className="text-gray-400" />
        </svg>
      </div>

      {/* Center label */}
      {points.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="h-8 w-8 mx-auto text-gray-400 dark:text-gray-500 mb-2" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {isDrawing ? 'اضغط لرسم حدود الحقل' : 'فعل وضع الرسم اولا'}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              {isDrawing ? 'Click to draw field boundary' : 'Enable drawing mode first'}
            </p>
          </div>
        </div>
      )}

      {/* Drawn points visualization */}
      {points.length > 0 && (
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {/* Lines between points */}
          {points.length > 1 && (
            <polyline
              points={points
                .map(([lng, lat]) => {
                  const x = ((lng - 43.95) / 0.5) * 100;
                  const y = ((15.75 - lat) / 0.5) * 100;
                  return `${x}%,${y}%`;
                })
                .join(' ')}
              fill="none"
              stroke="#22c55e"
              strokeWidth="2"
              strokeDasharray="4 2"
            />
          )}
          {/* Close polygon line */}
          {points.length > 2 && (
            <line
              x1={`${((points[points.length - 1]![0] - 43.95) / 0.5) * 100}%`}
              y1={`${((15.75 - points[points.length - 1]![1]) / 0.5) * 100}%`}
              x2={`${((points[0]![0] - 43.95) / 0.5) * 100}%`}
              y2={`${((15.75 - points[0]![1]) / 0.5) * 100}%`}
              stroke="#22c55e"
              strokeWidth="2"
              strokeDasharray="4 2"
              opacity="0.5"
            />
          )}
          {/* Point markers */}
          {points.map(([lng, lat], i) => {
            const cx = ((lng - 43.95) / 0.5) * 100;
            const cy = ((15.75 - lat) / 0.5) * 100;
            return (
              <circle
                key={i}
                cx={`${cx}%`}
                cy={`${cy}%`}
                r="5"
                fill="#22c55e"
                stroke="white"
                strokeWidth="2"
              />
            );
          })}
        </svg>
      )}

      {/* Point count badge */}
      {points.length > 0 && (
        <div className="absolute top-2 right-2 bg-white dark:bg-gray-800 rounded-lg px-2 py-1 shadow-sm border border-gray-200 dark:border-gray-600">
          <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
            {points.length} نقطة
          </span>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function FieldCreateDialog({
  open,
  onClose,
  onSubmit,
  className,
}: FieldCreateDialogProps) {
  const [name, setName] = useState('');
  const [nameAr, setNameAr] = useState('');
  const [cropType, setCropType] = useState('');
  const [irrigationType, setIrrigationType] = useState('');
  const [areaHectares, setAreaHectares] = useState('');
  const [boundaryPoints, setBoundaryPoints] = useState<[number, number][]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = useCallback(() => {
    setName('');
    setNameAr('');
    setCropType('');
    setIrrigationType('');
    setAreaHectares('');
    setBoundaryPoints([]);
    setIsDrawing(false);
    setError(null);
  }, []);

  const handleClose = useCallback(() => {
    if (submitting) return;
    resetForm();
    onClose();
  }, [onClose, resetForm, submitting]);

  const buildGeoJSON = useCallback((): FieldBoundary | undefined => {
    if (boundaryPoints.length < 3) return undefined;
    // Close the polygon ring
    const ring: [number, number][] = [...boundaryPoints, boundaryPoints[0]!];
    return {
      type: 'Polygon',
      coordinates: [ring],
    };
  }, [boundaryPoints]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);

      if (!nameAr.trim()) {
        setError('الرجاء ادخال اسم الحقل بالعربية');
        return;
      }
      if (!cropType) {
        setError('الرجاء اختيار المحصول');
        return;
      }
      if (!irrigationType) {
        setError('الرجاء اختيار نوع الري');
        return;
      }

      const data: FieldCreateData = {
        name: name.trim() || nameAr.trim(),
        nameAr: nameAr.trim(),
        cropType,
        irrigationType,
        areaHectares: areaHectares ? parseFloat(areaHectares) : undefined,
        boundary: buildGeoJSON(),
      };

      try {
        setSubmitting(true);
        await onSubmit(data);
        resetForm();
        onClose();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'حدث خطأ اثناء الحفظ');
      } finally {
        setSubmitting(false);
      }
    },
    [name, nameAr, cropType, irrigationType, areaHectares, buildGeoJSON, onSubmit, resetForm, onClose],
  );

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div
        dir="rtl"
        className={clsx(
          'relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl',
          'bg-white dark:bg-gray-900 shadow-2xl border border-gray-200 dark:border-gray-700',
          'mx-4',
          className,
        )}
      >
        {/* ---- Header ---- */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 rounded-t-2xl">
          <div className="flex items-center gap-2">
            <MapPin className="h-5 w-5 text-green-600 dark:text-green-400" />
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              انشاء حقل جديد
            </h2>
            <span className="text-sm text-gray-400 dark:text-gray-500">Create Field</span>
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={submitting}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
            aria-label="اغلاق"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* ---- Form ---- */}
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-5">
          {/* Error message */}
          {error && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800">
              <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          )}

          {/* Field name */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="field-name-ar"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
              >
                اسم الحقل (عربي) <span className="text-red-500">*</span>
              </label>
              <input
                id="field-name-ar"
                type="text"
                dir="rtl"
                value={nameAr}
                onChange={(e) => setNameAr(e.target.value)}
                placeholder="مثال: حقل القمح الشمالي"
                className={clsx(
                  'w-full px-3.5 py-2.5 rounded-xl border text-sm',
                  'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                  'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                )}
              />
            </div>
            <div>
              <label
                htmlFor="field-name-en"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
              >
                Field Name (English)
              </label>
              <input
                id="field-name-en"
                type="text"
                dir="ltr"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. North Wheat Field"
                className={clsx(
                  'w-full px-3.5 py-2.5 rounded-xl border text-sm',
                  'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                  'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                )}
              />
            </div>
          </div>

          {/* Crop + Irrigation */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="field-crop"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
              >
                <Wheat className="h-3.5 w-3.5 inline ml-1" />
                المحصول <span className="text-red-500">*</span>
              </label>
              <select
                id="field-crop"
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                className={clsx(
                  'w-full px-3.5 py-2.5 rounded-xl border text-sm appearance-none',
                  'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                )}
              >
                {CROP_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.labelAr} {opt.value ? `- ${opt.label}` : ''}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label
                htmlFor="field-irrigation"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
              >
                <Droplets className="h-3.5 w-3.5 inline ml-1" />
                نوع الري <span className="text-red-500">*</span>
              </label>
              <select
                id="field-irrigation"
                value={irrigationType}
                onChange={(e) => setIrrigationType(e.target.value)}
                className={clsx(
                  'w-full px-3.5 py-2.5 rounded-xl border text-sm appearance-none',
                  'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                )}
              >
                {IRRIGATION_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.labelAr} {opt.value ? `- ${opt.label}` : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Area */}
          <div className="max-w-xs">
            <label
              htmlFor="field-area"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
            >
              المساحة (هكتار)
            </label>
            <input
              id="field-area"
              type="number"
              step="0.1"
              min="0"
              dir="ltr"
              value={areaHectares}
              onChange={(e) => setAreaHectares(e.target.value)}
              placeholder="0.0"
              className={clsx(
                'w-full px-3.5 py-2.5 rounded-xl border text-sm',
                'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                'border-gray-300 dark:border-gray-600',
                'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                'placeholder:text-gray-400 dark:placeholder:text-gray-500',
              )}
            />
          </div>

          {/* ---- Map section ---- */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                <MapPin className="h-3.5 w-3.5 inline ml-1" />
                حدود الحقل | Field Boundary
              </label>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setIsDrawing(!isDrawing)}
                  className={clsx(
                    'inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition',
                    isDrawing
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700',
                  )}
                >
                  <PenTool className="w-3.5 h-3.5" />
                  {isDrawing ? 'الرسم مفعل' : 'رسم الحدود'}
                </button>
                {boundaryPoints.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setBoundaryPoints([])}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-lg text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 hover:bg-red-100 dark:hover:bg-red-900/30 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    مسح
                  </button>
                )}
              </div>
            </div>

            <DrawableMap
              points={boundaryPoints}
              onPointsChange={setBoundaryPoints}
              isDrawing={isDrawing}
            />

            {boundaryPoints.length > 0 && boundaryPoints.length < 3 && (
              <p className="mt-1.5 text-xs text-amber-600 dark:text-amber-400">
                يجب رسم 3 نقاط على الاقل لتكوين حدود الحقل
              </p>
            )}
            {boundaryPoints.length >= 3 && (
              <p className="mt-1.5 text-xs text-green-600 dark:text-green-400">
                <Check className="h-3 w-3 inline ml-0.5" />
                تم رسم {boundaryPoints.length} نقطة - الحدود جاهزة
              </p>
            )}
          </div>

          {/* ---- GeoJSON preview ---- */}
          {boundaryPoints.length >= 3 && (
            <details className="group">
              <summary className="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300 transition">
                عرض GeoJSON | View GeoJSON
              </summary>
              <pre
                dir="ltr"
                className="mt-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-mono text-gray-600 dark:text-gray-400 overflow-x-auto max-h-32"
              >
                {JSON.stringify(buildGeoJSON(), null, 2)}
              </pre>
            </details>
          )}

          {/* ---- Actions ---- */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              className={clsx(
                'px-5 py-2.5 text-sm font-medium rounded-xl transition',
                'text-gray-700 dark:text-gray-300',
                'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700',
                'disabled:opacity-50 disabled:cursor-not-allowed',
              )}
            >
              الغاء
            </button>
            <button
              type="submit"
              disabled={submitting}
              className={clsx(
                'inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white rounded-xl transition',
                'bg-green-600 hover:bg-green-700',
                'focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed',
              )}
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  جاري الحفظ...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  انشاء الحقل
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
