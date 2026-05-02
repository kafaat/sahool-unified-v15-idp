'use client';

/**
 * Field Create Dialog — انشاء حقل جديد
 *
 * Modal dialog for creating new fields, following the UX pattern used by
 * leading agricultural platforms (John Deere Operations Center, Climate
 * FieldView, Granular):
 *
 *   1. The user draws the field boundary on a real interactive map FIRST
 *      (using the shared DrawableMap with Leaflet).
 *   2. Once a polygon is drawn, the details form (single name, crop,
 *      irrigation type, optional area) becomes available.
 *   3. The form submits a GeoJSON polygon plus metadata.
 *
 * Notes:
 * - The name input is bilingual (one field, RTL-aware placeholder).
 *   Internally we still expose `name` (English) and `nameAr` (Arabic) on
 *   `FieldCreateData` for API back-compat: when only one is provided, the
 *   other is mirrored from it.
 * - The DrawableMap is loaded dynamically (Leaflet is browser-only) and
 *   emits a `GeoJSON.Polygon | null` via `onBoundaryChange`.
 */

import React, { useState, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { clsx } from 'clsx';
import {
  X,
  MapPin,
  Wheat,
  Droplets,
  Loader2,
  Check,
  AlertCircle,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// DrawableMap is browser-only (Leaflet). Load on demand to keep the modal
// SSR-safe and avoid pulling Leaflet into the initial bundle.
// ---------------------------------------------------------------------------
const DrawableMap = dynamic(() => import('@/components/maps/DrawableMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-80 rounded-xl bg-gray-100 dark:bg-gray-800 animate-pulse flex items-center justify-center">
      <p className="text-sm text-gray-500 dark:text-gray-400">جاري تحميل الخريطة...</p>
    </div>
  ),
});

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FieldBoundary {
  type: 'Polygon';
  coordinates: [number, number][][];
}

export interface FieldCreateData {
  /** English (or Latin-script) name. Mirrors `nameAr` if the user entered Arabic only. */
  name: string;
  /** Arabic name. Mirrors `name` if the user entered English only. */
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
// Geometry helpers
// ---------------------------------------------------------------------------

/**
 * Approximate polygon area in hectares.
 *
 * Algorithm: shoelace formula applied to coordinates projected onto a local
 * equirectangular (plate-carrée) plane centred on the polygon's mean
 * latitude. Conversion uses 1° latitude ≈ 111_320 m and 1° longitude ≈
 * 111_320 · cos(meanLat) m.
 *
 * @param polygon - GeoJSON Polygon with rings in `[longitude, latitude]`
 *   order (decimal degrees, WGS84). The first ring is treated as the outer
 *   boundary; inner rings (holes) are ignored.
 * @returns Area in hectares, or `null` if the polygon is invalid (no rings,
 *   <4 points, or a missing coordinate).
 *
 * Accuracy notes:
 *   - Designed for fields up to ~1000 ha in Yemen's latitude band
 *     (~13–18°N), where the equirectangular distortion is < 0.5%.
 *   - Degrades at high latitudes (use a proper ellipsoidal calculation —
 *     e.g. `@turf/area` — for fields outside ±60°).
 *   - Does not account for terrain (planar projection only).
 */
function approxAreaHectares(polygon: GeoJSON.Polygon | null): number | null {
  if (!polygon || polygon.coordinates.length === 0) return null;
  const ring = polygon.coordinates[0];
  if (!ring || ring.length < 4) return null;

  // Convert lat/lng to local-meter coordinates (equirectangular).
  // 1 degree latitude ≈ 111_320 m, 1 degree longitude ≈ 111_320 * cos(lat) m.
  let latSum = 0;
  for (const pt of ring) {
    const lat = pt[1];
    if (lat === undefined) return null;
    latSum += lat;
  }
  const meanLat = latSum / ring.length;
  const cosLat = Math.cos((meanLat * Math.PI) / 180);

  const pts: Array<readonly [number, number]> = [];
  for (const pt of ring) {
    const lng = pt[0];
    const lat = pt[1];
    if (lng === undefined || lat === undefined) return null;
    pts.push([lng * 111_320 * cosLat, lat * 111_320] as const);
  }

  let area = 0;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const pi = pts[i]!;
    const pj = pts[j]!;
    area += (pj[0] + pi[0]) * (pj[1] - pi[1]);
  }
  const sqMeters = Math.abs(area) / 2;
  return sqMeters / 10_000; // 1 ha = 10_000 m²
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
  // Single bilingual name input — RTL-aware. Stored as Arabic by default,
  // mirrored to `name` (English) at submit time if the latter is empty.
  const [name, setName] = useState('');
  const [cropType, setCropType] = useState('');
  const [irrigationType, setIrrigationType] = useState('');
  const [areaHectares, setAreaHectares] = useState('');
  const [boundary, setBoundary] = useState<GeoJSON.Polygon | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const computedArea = useMemo(() => approxAreaHectares(boundary), [boundary]);

  const resetForm = useCallback(() => {
    setName('');
    setCropType('');
    setIrrigationType('');
    setAreaHectares('');
    setBoundary(null);
    setError(null);
  }, []);

  const handleClose = useCallback(() => {
    if (submitting) return;
    resetForm();
    onClose();
  }, [onClose, resetForm, submitting]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);

      if (!boundary) {
        setError('الرجاء رسم حدود الحقل على الخريطة أولاً | Please draw the field boundary on the map first');
        return;
      }
      if (!name.trim()) {
        setError('الرجاء ادخال اسم الحقل | Please enter the field name');
        return;
      }
      if (!cropType) {
        setError('الرجاء اختيار المحصول | Please select a crop');
        return;
      }
      if (!irrigationType) {
        setError('الرجاء اختيار نوع الري | Please select an irrigation type');
        return;
      }

      const trimmed = name.trim();
      // Single bilingual input: mirror the value into both `name` and
      // `nameAr` so the API receives a populated label regardless of
      // which language the user typed in. The backend can detect the
      // script and route the value to the appropriate display field.

      // Normalize boundary coordinates to the [number, number] tuple shape
      // expected by the API contract (drops any altitude component if present).
      const coords: [number, number][][] = boundary.coordinates.map((ring) =>
        ring.map(([lng, lat]) => [lng, lat] as [number, number]),
      );

      // Bind through the FieldBoundary interface so any future required
      // properties (e.g. a `crs` field) cause a compile error here instead
      // of silently being omitted from the API payload.
      const fieldBoundary: FieldBoundary = { type: 'Polygon', coordinates: coords };

      const data: FieldCreateData = {
        name: trimmed,
        nameAr: trimmed,
        cropType,
        irrigationType,
        areaHectares: areaHectares
          ? parseFloat(areaHectares)
          : computedArea
          ? Math.round(computedArea * 100) / 100
          : undefined,
        boundary: fieldBoundary,
      };

      try {
        setSubmitting(true);
        await onSubmit(data);
        resetForm();
        onClose();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'حدث خطأ اثناء الحفظ | Error while saving');
      } finally {
        setSubmitting(false);
      }
    },
    [name, cropType, irrigationType, areaHectares, boundary, computedArea, onSubmit, resetForm, onClose],
  );

  if (!open) return null;

  const detailsEnabled = boundary !== null;

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
          'relative w-full max-w-3xl max-h-[92vh] overflow-y-auto rounded-2xl',
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
            <span className="text-sm text-gray-400 dark:text-gray-500">| Create Field</span>
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={submitting}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition disabled:opacity-50"
            aria-label="اغلاق"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* ---- Form ---- */}
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-6">
          {/* Error message */}
          {error && (
            <div
              role="alert"
              className="flex items-start gap-2 px-4 py-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800"
            >
              <AlertCircle className="h-4 w-4 mt-0.5 text-red-600 dark:text-red-400 shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          )}

          {/* ===========================================================
              STEP 1 — Draw the boundary on the map (always first)
              ───────────────────────────────────────────────────────────
              This matches the UX of John Deere Operations Center and
              Climate FieldView: the spatial extent is selected before
              any metadata, so the form always reflects a real polygon.
              =========================================================== */}
          <section aria-labelledby="step-1-label">
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-600 text-white text-xs font-bold">
                1
              </span>
              <h3
                id="step-1-label"
                className="text-sm font-semibold text-gray-900 dark:text-gray-100"
              >
                ارسم حدود الحقل على الخريطة
                <span className="ms-2 text-gray-400 font-normal">| Draw field boundary</span>
              </h3>
            </div>

            <DrawableMap
              onBoundaryChange={setBoundary}
              height="380px"
              initialCenter={[15.5527, 48.5164]}
              initialZoom={6}
            />

            {boundary && computedArea !== null && (
              <p className="mt-2 text-xs text-green-700 dark:text-green-400 flex items-center gap-1">
                <Check className="h-3.5 w-3.5" />
                تم رسم الحدود — المساحة التقريبية: {computedArea.toFixed(2)} هكتار
                <span className="text-gray-400">| ≈ {computedArea.toFixed(2)} ha</span>
              </p>
            )}
            {!boundary && (
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                استخدم أدوات الرسم لتحديد المضلع أو المستطيل، ثم انتقل لإدخال التفاصيل أدناه.
                <span className="block text-gray-400">
                  Use the drawing tools to outline a polygon or rectangle, then continue below.
                </span>
              </p>
            )}
          </section>

          {/* ===========================================================
              STEP 2 — Details (enabled only after the boundary exists)
              =========================================================== */}
          <section
            aria-labelledby="step-2-label"
            aria-disabled={!detailsEnabled}
            className={clsx(
              'rounded-xl border p-4 transition',
              detailsEnabled
                ? 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900'
                : 'border-dashed border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/40 opacity-60',
            )}
          >
            <div className="flex items-center gap-2 mb-4">
              <span
                className={clsx(
                  'inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold',
                  detailsEnabled
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-300 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
                )}
              >
                2
              </span>
              <h3
                id="step-2-label"
                className="text-sm font-semibold text-gray-900 dark:text-gray-100"
              >
                تفاصيل الحقل
                <span className="ms-2 text-gray-400 font-normal">| Field details</span>
              </h3>
            </div>

            <fieldset
              disabled={!detailsEnabled}
              className="space-y-4 disabled:opacity-60"
            >
              {/* Single bilingual name field — replaces the two duplicate
                  Arabic/English inputs that the previous design exposed. */}
              <div>
                <label
                  htmlFor="field-name"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  اسم الحقل
                  <span className="ms-2 text-gray-400 font-normal">| Field name</span>
                  <span className="text-red-500 ms-1">*</span>
                </label>
                <input
                  id="field-name"
                  type="text"
                  // dir="auto" lets the browser pick LTR/RTL per the first
                  // strong directional character. Note: pure-Arabic and
                  // pure-Latin input render correctly; mixed-script input
                  // (e.g. "Field 5 الشمالي") will follow the leading
                  // character's direction. The aria-describedby below makes
                  // this behaviour explicit for screen-reader users.
                  dir="auto"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="مثال: حقل القمح الشمالي / North Wheat Field"
                  autoComplete="off"
                  aria-describedby="field-name-help"
                  className={clsx(
                    'w-full px-3.5 py-2.5 rounded-xl border text-sm',
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                  )}
                />
                <p
                  id="field-name-help"
                  className="mt-1 text-xs text-gray-500 dark:text-gray-400"
                >
                  يمكن إدخال الاسم بالعربية أو الإنجليزية
                  <span className="ms-1 text-gray-400">
                    | Enter the name in Arabic or English
                  </span>
                </p>
              </div>

              {/* Crop + Irrigation */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="field-crop"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                  >
                    <Wheat className="h-3.5 w-3.5 inline ms-1" />
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
                    <Droplets className="h-3.5 w-3.5 inline ms-1" />
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

              {/* Area — pre-filled from the polygon if the user does not override */}
              <div className="max-w-xs">
                <label
                  htmlFor="field-area"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  المساحة (هكتار) <span className="text-gray-400 font-normal">| Area (ha)</span>
                </label>
                <input
                  id="field-area"
                  type="number"
                  step="0.01"
                  min="0"
                  dir="ltr"
                  value={areaHectares}
                  onChange={(e) => setAreaHectares(e.target.value)}
                  placeholder={
                    computedArea !== null ? computedArea.toFixed(2) : '0.0'
                  }
                  className={clsx(
                    'w-full px-3.5 py-2.5 rounded-xl border text-sm',
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                  )}
                />
                {computedArea !== null && !areaHectares && (
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    سيتم استخدام المساحة المحسوبة من الحدود إذا تُركت فارغة
                    <span className="block text-gray-400">
                      Computed area from boundary will be used if left empty
                    </span>
                  </p>
                )}
              </div>
            </fieldset>
          </section>

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
              disabled={submitting || !detailsEnabled}
              className={clsx(
                'inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white rounded-xl transition',
                'bg-green-600 hover:bg-green-700',
                'focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed',
              )}
              title={
                !detailsEnabled
                  ? 'ارسم الحدود أولاً | Draw the boundary first'
                  : undefined
              }
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
