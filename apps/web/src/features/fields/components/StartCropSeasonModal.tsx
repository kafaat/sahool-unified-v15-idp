'use client';

/**
 * StartCropSeasonModal
 * نافذة بدء موسم محصولي جديد (المرحلة الثانية)
 *
 * A dedicated "Stage 2" capture form for starting a new cropping
 * season on an existing field. Kept intentionally separate from the
 * minimal "Add Field" flow so the user can create a bare field first
 * (geographic/identity only) and fill in the agronomic detail later,
 * per the best-practice pattern followed by advanced farm-management
 * systems:
 *
 *   1. Crop phenology accuracy — a real sowing date lets the satellite
 *      pipeline compare the field against crop-specific growth stages
 *      (Zadoks, BBCH) instead of generic NDVI thresholds.
 *   2. Seasonality — multiple seasons on the same field stay
 *      separable (last season: corn; current: wheat) so the
 *      historical timeline never collapses distinct plantings into
 *      one amorphous "crop type" column.
 *   3. Prescriptive analytics — seed variety, planting density, and
 *      irrigation method unlock per-season recommendations that a
 *      pure visual-monitoring view cannot produce.
 *
 * This modal does NOT talk to the backend directly. It builds a
 * `CropHistoryEntry` and hands it to the parent via `onSubmit`; the
 * parent is responsible for merging it into `field.metadata.cropHistory`
 * and PATCHing the field. All data stays inside the existing JSONB
 * column — no migration or new endpoint is required.
 */

import React, { useState, useMemo } from 'react';
import {
  X,
  Save,
  Sprout,
  Droplets,
  Wheat,
  Calendar,
  Tractor,
  Layers,
  Clock,
  DollarSign,
  Wrench,
} from 'lucide-react';
import type { CropHistoryEntry } from './CropHistoryTimeline';
import { useEquipment } from '@/features/equipment/hooks/useEquipment';
import type { Equipment } from '@/features/equipment/types';

// ---------------------------------------------------------------------------
// Option lists (bilingual)
// ---------------------------------------------------------------------------

interface Option {
  value: string;
  label: string;
  labelAr: string;
}

const CROP_OPTIONS: Option[] = [
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
  { value: 'potato', label: 'Potato', labelAr: 'بطاطس' },
  { value: 'onion', label: 'Onion', labelAr: 'بصل' },
  { value: 'other', label: 'Other', labelAr: 'أخرى' },
];

const SEASON_OPTIONS: Option[] = [
  { value: 'winter', label: 'Winter', labelAr: 'شتوي' },
  { value: 'spring', label: 'Spring', labelAr: 'ربيعي' },
  { value: 'summer', label: 'Summer', labelAr: 'صيفي' },
  { value: 'autumn', label: 'Autumn', labelAr: 'خريفي' },
  { value: 'year-round', label: 'Year-round', labelAr: 'طوال العام' },
];

const IRRIGATION_OPTIONS: Option[] = [
  { value: 'drip', label: 'Drip', labelAr: 'تنقيط' },
  { value: 'sprinkler', label: 'Sprinkler', labelAr: 'رشاشات' },
  { value: 'flood', label: 'Flood', labelAr: 'غمر' },
  { value: 'pivot', label: 'Center pivot', labelAr: 'محوري' },
  { value: 'manual', label: 'Manual', labelAr: 'يدوي' },
  { value: 'other', label: 'Other', labelAr: 'أخرى' },
];

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface StartCropSeasonModalProps {
  /** Controls visibility. The caller owns the open/close state. */
  open: boolean;
  onClose: () => void;
  /**
   * Called with a fully-built `CropHistoryEntry` when the user saves.
   * The parent is expected to:
   *   1. mark any currently-active entry as `isCurrent: false` + set
   *      its `endDate` to today
   *   2. append this new entry to `metadata.cropHistory`
   *   3. PATCH the field via `useUpdateField`
   */
  onSubmit: (entry: CropHistoryEntry) => void;
  /**
   * Whether a previous season is already active. When true, the modal
   * shows a warning banner explaining that starting a new season will
   * close the existing one.
   */
  hasActiveSeason?: boolean;
  /**
   * Pre-fill crop type from the parent field (e.g., the current
   * planned crop) so the user does not have to reselect it when
   * they are just formalising a pre-existing crop.
   */
  initialCropType?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const today = () => new Date().toISOString().slice(0, 10);

function clampPositive(raw: string): string {
  const n = Number(raw);
  if (!Number.isFinite(n) || n < 0) return '';
  return raw;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const StartCropSeasonModal: React.FC<StartCropSeasonModalProps> = ({
  open,
  onClose,
  onSubmit,
  hasActiveSeason = false,
  initialCropType = '',
}) => {
  const [cropType, setCropType] = useState<string>(initialCropType);
  const [season, setSeason] = useState<string>('');
  const [plowingDate, setPlowingDate] = useState<string>('');
  const [plowingEquipmentId, setPlowingEquipmentId] = useState<string>('');
  const [plowingDurationHours, setPlowingDurationHours] = useState<string>('');
  const [plowingCost, setPlowingCost] = useState<string>('');
  const [landPreparationDate, setLandPreparationDate] = useState<string>('');
  const [landPreparationEquipmentId, setLandPreparationEquipmentId] =
    useState<string>('');
  const [landPreparationDurationHours, setLandPreparationDurationHours] =
    useState<string>('');
  const [landPreparationCost, setLandPreparationCost] = useState<string>('');
  const [startDate, setStartDate] = useState<string>(today());
  const [estimatedHarvestDate, setEstimatedHarvestDate] = useState<string>('');
  const [seedVariety, setSeedVariety] = useState<string>('');
  const [plantingDensityKgHa, setPlantingDensityKgHa] = useState<string>('');
  const [irrigationType, setIrrigationType] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // Pull active equipment list from the existing equipment feature so the
  // user can link a specific tractor / plow / harrow to each operation.
  // The hook is a plain react-query fetch — no backend change needed.
  const { data: equipmentList } = useEquipment();
  const tillageCandidates = useMemo<Equipment[]>(() => {
    if (!equipmentList) return [];
    return equipmentList.filter(
      (e) =>
        (e.type === 'tractor' ||
          e.type === 'planter' ||
          e.type === 'other') &&
        e.status !== 'retired',
    );
  }, [equipmentList]);

  const cropLabelAr = useMemo(
    () => CROP_OPTIONS.find((c) => c.value === cropType)?.labelAr,
    [cropType],
  );
  const irrigationLabelAr = useMemo(
    () => IRRIGATION_OPTIONS.find((c) => c.value === irrigationType)?.labelAr,
    [irrigationType],
  );

  // Live preview of the total pre-sowing operation cost + hours so the
  // user can see the rollup before saving (same formula used by the
  // timeline when rendering existing entries).
  const totalCost = useMemo(() => {
    const p = Number(plowingCost);
    const l = Number(landPreparationCost);
    return (Number.isFinite(p) ? p : 0) + (Number.isFinite(l) ? l : 0);
  }, [plowingCost, landPreparationCost]);
  const totalHours = useMemo(() => {
    const p = Number(plowingDurationHours);
    const l = Number(landPreparationDurationHours);
    return (Number.isFinite(p) ? p : 0) + (Number.isFinite(l) ? l : 0);
  }, [plowingDurationHours, landPreparationDurationHours]);

  if (!open) return null;

  const handleSave = () => {
    setError(null);
    if (!cropType) {
      setError('يرجى اختيار نوع المحصول');
      return;
    }
    if (!startDate) {
      setError('يرجى إدخال تاريخ البذر');
      return;
    }
    const startMs = new Date(startDate).getTime();
    if (Number.isNaN(startMs)) {
      setError('تاريخ البذر غير صالح');
      return;
    }
    // Optional: plowing → land preparation → sowing must be in order.
    let plowingMs: number | null = null;
    if (plowingDate) {
      plowingMs = new Date(plowingDate).getTime();
      if (Number.isNaN(plowingMs)) {
        setError('تاريخ الحراثة غير صالح');
        return;
      }
      if (plowingMs > startMs) {
        setError('تاريخ الحراثة يجب أن يكون قبل تاريخ البذر');
        return;
      }
    }
    let landPrepMs: number | null = null;
    if (landPreparationDate) {
      landPrepMs = new Date(landPreparationDate).getTime();
      if (Number.isNaN(landPrepMs)) {
        setError('تاريخ تهيئة الأرض غير صالح');
        return;
      }
      if (landPrepMs > startMs) {
        setError('تاريخ تهيئة الأرض يجب أن يكون قبل تاريخ البذر');
        return;
      }
      if (plowingMs !== null && landPrepMs < plowingMs) {
        setError('تاريخ تهيئة الأرض يجب أن يكون بعد تاريخ الحراثة');
        return;
      }
    }
    if (estimatedHarvestDate) {
      const harvestMs = new Date(estimatedHarvestDate).getTime();
      if (Number.isNaN(harvestMs) || harvestMs < startMs) {
        setError('تاريخ الحصاد المتوقع يجب أن يكون بعد تاريخ البذر');
        return;
      }
    }

    const density =
      plantingDensityKgHa.trim() && Number.isFinite(Number(plantingDensityKgHa))
        ? Number(plantingDensityKgHa)
        : undefined;

    // Resolve the chosen equipment objects so we can snapshot the
    // display names at save-time (timeline fallback if the equipment
    // is later renamed or deleted).
    const plowingEq = plowingEquipmentId
      ? tillageCandidates.find((e) => e.id === plowingEquipmentId)
      : undefined;
    const landPrepEq = landPreparationEquipmentId
      ? tillageCandidates.find((e) => e.id === landPreparationEquipmentId)
      : undefined;

    const parsePositive = (raw: string): number | undefined => {
      if (!raw.trim()) return undefined;
      const n = Number(raw);
      return Number.isFinite(n) && n >= 0 ? n : undefined;
    };

    const entry: CropHistoryEntry = {
      cropType,
      cropTypeAr: cropLabelAr,
      season: season || undefined,
      plowingDate: plowingDate
        ? new Date(plowingDate).toISOString()
        : undefined,
      plowingDurationHours: parsePositive(plowingDurationHours),
      plowingCost: parsePositive(plowingCost),
      plowingEquipmentId: plowingEq?.id,
      plowingEquipmentName: plowingEq?.name,
      plowingEquipmentNameAr: plowingEq?.nameAr,
      landPreparationDate: landPreparationDate
        ? new Date(landPreparationDate).toISOString()
        : undefined,
      landPreparationDurationHours: parsePositive(landPreparationDurationHours),
      landPreparationCost: parsePositive(landPreparationCost),
      landPreparationEquipmentId: landPrepEq?.id,
      landPreparationEquipmentName: landPrepEq?.name,
      landPreparationEquipmentNameAr: landPrepEq?.nameAr,
      startDate: new Date(startDate).toISOString(),
      estimatedHarvestDate: estimatedHarvestDate
        ? new Date(estimatedHarvestDate).toISOString()
        : undefined,
      seedVariety: seedVariety.trim() || undefined,
      plantingDensityKgHa: density,
      irrigationType: irrigationType || undefined,
      irrigationTypeAr: irrigationLabelAr,
      notes: notes.trim() || undefined,
      isCurrent: true,
    };

    onSubmit(entry);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="start-season-title"
      dir="rtl"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4 bg-gradient-to-l from-emerald-50 to-white">
          <div className="flex items-center gap-2">
            <Sprout className="w-5 h-5 text-emerald-600" />
            <h2 id="start-season-title" className="text-base font-bold text-gray-900">
              بدء موسم محصولي جديد
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
            aria-label="إغلاق النافذة"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto p-5 space-y-4">
          {hasActiveSeason && (
            <div className="rounded-md bg-amber-50 border border-amber-200 p-3 text-xs text-amber-800 leading-relaxed">
              ⚠️ هناك موسم محصولي نشط لهذا الحقل حالياً. عند الحفظ، سيتم
              إنهاء الموسم الحالي تلقائياً (endDate = اليوم) وبدء هذا الموسم
              كالموسم الحالي الجديد.
            </div>
          )}

          {/* Row 1: crop + season */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">
                <Wheat className="w-3 h-3 inline ml-1" />
                نوع المحصول <span className="text-red-500">*</span>
              </label>
              <select
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">— اختر —</option>
                {CROP_OPTIONS.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.labelAr}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">
                الموسم الزراعي
              </label>
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">— اختر (اختياري) —</option>
                {SEASON_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.labelAr}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Section: Plowing (date + equipment + duration + cost) */}
          <fieldset className="rounded-md border border-yellow-200 bg-yellow-50/30 p-3">
            <legend className="text-xs font-semibold text-gray-800 px-2 flex items-center gap-1">
              <Tractor className="w-3.5 h-3.5 text-yellow-700" />
              عملية الحراثة
            </legend>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  تاريخ الحراثة
                </label>
                <input
                  type="date"
                  value={plowingDate}
                  onChange={(e) => setPlowingDate(e.target.value)}
                  max={startDate || today()}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  dir="ltr"
                />
                <p className="mt-1 text-[10px] text-gray-500">
                  الحراثة الأولية (قلب التربة، تكسير الطبقات)
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  <Wrench className="w-3 h-3 inline ml-1" />
                  المعدة المستخدمة
                </label>
                <select
                  value={plowingEquipmentId}
                  onChange={(e) => setPlowingEquipmentId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="">— اختر من قائمة المعدات —</option>
                  {tillageCandidates.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.nameAr || e.name}
                      {e.manufacturer ? ` — ${e.manufacturer}` : ''}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-[10px] text-gray-500">
                  مربوطة بصفحة إدارة المعدات
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  <Clock className="w-3 h-3 inline ml-1" />
                  مدة الحراثة (ساعة)
                </label>
                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  max="1000"
                  step="0.1"
                  value={plowingDurationHours}
                  onChange={(e) =>
                    setPlowingDurationHours(clampPositive(e.target.value))
                  }
                  placeholder="مثال: 6"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  dir="ltr"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  <DollarSign className="w-3 h-3 inline ml-1" />
                  تكلفة الحراثة (ريال)
                </label>
                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  step="1"
                  value={plowingCost}
                  onChange={(e) => setPlowingCost(clampPositive(e.target.value))}
                  placeholder="مثال: 1200"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  dir="ltr"
                />
              </div>
            </div>
          </fieldset>

          {/* Section: Land Preparation (date + equipment + duration + cost) */}
          <fieldset className="rounded-md border border-stone-200 bg-stone-50/30 p-3">
            <legend className="text-xs font-semibold text-gray-800 px-2 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-stone-600" />
              عملية تهيئة الأرض
            </legend>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  تاريخ تهيئة الأرض
                </label>
                <input
                  type="date"
                  value={landPreparationDate}
                  onChange={(e) => setLandPreparationDate(e.target.value)}
                  min={plowingDate || undefined}
                  max={startDate || today()}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  dir="ltr"
                />
                <p className="mt-1 text-[10px] text-gray-500">
                  تسوية وتهيئة مهد البذرة قبل الزراعة
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  <Wrench className="w-3 h-3 inline ml-1" />
                  المعدة المستخدمة
                </label>
                <select
                  value={landPreparationEquipmentId}
                  onChange={(e) => setLandPreparationEquipmentId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="">— اختر من قائمة المعدات —</option>
                  {tillageCandidates.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.nameAr || e.name}
                      {e.manufacturer ? ` — ${e.manufacturer}` : ''}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-[10px] text-gray-500">
                  مربوطة بصفحة إدارة المعدات
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  <Clock className="w-3 h-3 inline ml-1" />
                  مدة التهيئة (ساعة)
                </label>
                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  max="1000"
                  step="0.1"
                  value={landPreparationDurationHours}
                  onChange={(e) =>
                    setLandPreparationDurationHours(clampPositive(e.target.value))
                  }
                  placeholder="مثال: 4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  dir="ltr"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">
                  <DollarSign className="w-3 h-3 inline ml-1" />
                  تكلفة التهيئة (ريال)
                </label>
                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  step="1"
                  value={landPreparationCost}
                  onChange={(e) =>
                    setLandPreparationCost(clampPositive(e.target.value))
                  }
                  placeholder="مثال: 800"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  dir="ltr"
                />
              </div>
            </div>
          </fieldset>

          {/* Live rollup of pre-sowing operation totals */}
          {(totalCost > 0 || totalHours > 0) && (
            <div className="rounded-md bg-emerald-50 border border-emerald-200 p-3 text-xs text-emerald-900 flex flex-wrap items-center gap-x-4 gap-y-1">
              <span className="font-semibold">الإجمالي قبل البذار:</span>
              {totalHours > 0 && (
                <span className="inline-flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <strong>{totalHours.toLocaleString('ar-SA')}</strong> ساعة
                </span>
              )}
              {totalCost > 0 && (
                <span className="inline-flex items-center gap-1">
                  <DollarSign className="w-3.5 h-3.5" />
                  <strong>{totalCost.toLocaleString('ar-SA')}</strong> ريال
                </span>
              )}
            </div>
          )}

          {/* Row 2b: sowing + expected harvest */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">
                <Calendar className="w-3 h-3 inline ml-1" />
                تاريخ البذار <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                min={landPreparationDate || plowingDate || undefined}
                max={today()}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                dir="ltr"
              />
              <p className="mt-1 text-[10px] text-gray-500">
                يحدّد مرحلة النمو المتوقعة (Crop Phenology)
              </p>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">
                تاريخ الحصاد المتوقع
              </label>
              <input
                type="date"
                value={estimatedHarvestDate}
                onChange={(e) => setEstimatedHarvestDate(e.target.value)}
                min={startDate || undefined}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                dir="ltr"
              />
            </div>
          </div>

          {/* Row 3: seed variety + density */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">
                <Sprout className="w-3 h-3 inline ml-1" />
                الصنف / البذور
              </label>
              <input
                type="text"
                value={seedVariety}
                onChange={(e) => setSeedVariety(e.target.value.slice(0, 100))}
                maxLength={100}
                placeholder="مثال: Sakha 95"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">
                كثافة البذر (كجم/هكتار)
              </label>
              <input
                type="number"
                inputMode="decimal"
                min="0"
                max="10000"
                step="0.1"
                value={plantingDensityKgHa}
                onChange={(e) =>
                  setPlantingDensityKgHa(clampPositive(e.target.value))
                }
                placeholder="مثال: 120"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                dir="ltr"
              />
            </div>
          </div>

          {/* Row 4: irrigation */}
          <div>
            <label className="text-xs font-medium text-gray-700 mb-1 block">
              <Droplets className="w-3 h-3 inline ml-1" />
              نظام الري
            </label>
            <select
              value={irrigationType}
              onChange={(e) => setIrrigationType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">— اختر (اختياري) —</option>
              {IRRIGATION_OPTIONS.map((i) => (
                <option key={i.value} value={i.value}>
                  {i.labelAr}
                </option>
              ))}
            </select>
          </div>

          {/* Notes */}
          <div>
            <label className="text-xs font-medium text-gray-700 mb-1 block">
              ملاحظات
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value.slice(0, 500))}
              rows={3}
              maxLength={500}
              placeholder="أي ملاحظات إضافية عن هذا الموسم..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
            />
            <p className="mt-1 text-[10px] text-gray-400 text-left">
              {notes.length} / 500
            </p>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-xs text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-5 py-3 bg-gray-50 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            إلغاء
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 rounded-md transition-colors inline-flex items-center gap-1.5"
          >
            <Save className="w-4 h-4" />
            حفظ الموسم
          </button>
        </div>
      </div>
    </div>
  );
};

export default StartCropSeasonModal;
