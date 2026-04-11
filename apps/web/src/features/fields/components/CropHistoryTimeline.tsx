'use client';

/**
 * CropHistoryTimeline
 * جدول زمني لأرشفة تاريخ محاصيل الحقل
 *
 * Renders the per-field crop-rotation history as a vertical timeline
 * (newest first). The history is stored as a JSON array inside the
 * existing `Field.metadata.cropHistory` JSONB column on the backend —
 * no migration or new endpoint is required.
 *
 * Metadata shape (new — additive-only, forward-compatible):
 *
 *   field.metadata.cropHistory: CropHistoryEntry[]
 *
 *   interface CropHistoryEntry {
 *     cropType: string;        // canonical slug (wheat, barley, ...)
 *     cropTypeAr?: string;     // Arabic label for display
 *     season?: string;         // winter | summer | year-round | ...
 *     startDate: string;       // ISO 8601 — when this crop was planted
 *     endDate?: string;        // ISO 8601 — set when the crop rotates out
 *     isCurrent?: boolean;     // true for the most recent still-planted entry
 *     yieldKgHa?: number;      // optional post-harvest measurement
 *     notes?: string;          // optional free-text note
 *   }
 *
 * If `metadata.cropHistory` is missing or empty, the component falls
 * back to a single synthetic entry built from the live `cropType` +
 * `createdAt` so an existing field always has at least one row — the
 * "historical database" is never empty even for pre-existing records.
 */

import React from 'react';
import Link from 'next/link';
import {
  Wheat,
  Calendar,
  TrendingUp,
  Droplets,
  Sprout,
  PlusCircle,
  Tractor,
  Layers,
  Clock,
  DollarSign,
  Wrench,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Public shape
// ---------------------------------------------------------------------------

export interface CropHistoryEntry {
  cropType: string;
  cropTypeAr?: string;
  /** Season classification (winter/summer/year-round/spring/autumn). */
  season?: string;
  /** Sowing date — ISO 8601. Drives crop phenology / growth-stage modelling. */
  startDate: string;
  /** Closing date when the crop is rotated out. */
  endDate?: string;
  isCurrent?: boolean;
  /** Post-harvest measured yield in kg/ha. */
  yieldKgHa?: number;
  notes?: string;

  // ── Stage-2 "Start Crop Season" rich fields ────────────────────────────
  // Captured via <StartCropSeasonModal>. All optional so the existing
  // minimal entries (legacy fields created before this feature landed)
  // still render correctly — the timeline just hides the rows whose
  // value is absent.

  /**
   * Tillage / plowing date — ISO 8601. Records when primary tillage
   * (disc, plow, chisel) was performed on the field. Comes BEFORE
   * `landPreparationDate` in the typical workflow.
   */
  plowingDate?: string;
  /**
   * Plowing operation duration in hours. Feeds the total "field
   * operation hours" metric and, when an equipment record is linked,
   * lets the equipment-management page accrue wear/maintenance cycles.
   */
  plowingDurationHours?: number;
  /**
   * Plowing operation cost in local currency (SAR). Sum of fuel +
   * labour + equipment rental. Surfaces in per-season totals.
   */
  plowingCost?: number;
  /**
   * Equipment id from the equipment-management feature
   * (`useEquipment()`). Linking a tractor/plow here lets the timeline
   * render a clickable chip that deep-links to `/equipment/[id]` and
   * enables per-equipment cost roll-ups across seasons.
   */
  plowingEquipmentId?: string;
  /** Cached equipment display name at link-time (fallback label). */
  plowingEquipmentName?: string;
  /** Cached Arabic equipment display name at link-time. */
  plowingEquipmentNameAr?: string;

  /**
   * Land-preparation completion date — ISO 8601. Records when the
   * seedbed was finalised (harrowing, levelling, bed-making). Comes
   * AFTER plowing and BEFORE sowing (`startDate`).
   */
  landPreparationDate?: string;
  /** Land-preparation duration in hours. */
  landPreparationDurationHours?: number;
  /** Land-preparation cost in local currency (SAR). */
  landPreparationCost?: number;
  /** Equipment id used for land preparation (harrow / leveller / ...). */
  landPreparationEquipmentId?: string;
  /** Cached equipment display name for land-prep equipment. */
  landPreparationEquipmentName?: string;
  /** Cached Arabic display name for land-prep equipment. */
  landPreparationEquipmentNameAr?: string;
  /** Seed variety / cultivar, e.g. "Sakha 95", "Pioneer P1415". */
  seedVariety?: string;
  /** Arabic label for seed variety. */
  seedVarietyAr?: string;
  /** Planting density in kg/ha (or seeds/m² converted). */
  plantingDensityKgHa?: number;
  /** Irrigation method slug — drip | sprinkler | flood | pivot | manual. */
  irrigationType?: string;
  /** Arabic label for irrigation method. */
  irrigationTypeAr?: string;
  /** Expected harvest date — ISO 8601. Used by yield-prediction models. */
  estimatedHarvestDate?: string;
}

export interface CropHistoryTimelineProps {
  /** Current crop slug shown as the live / "is_current" entry fallback. */
  currentCropType: string;
  /** Arabic label for the current crop (optional, for display only). */
  currentCropTypeAr?: string;
  /** ISO timestamp — when the field was first created (fallback start date). */
  fieldCreatedAt?: string;
  /**
   * Raw metadata blob from the backend. Only the `cropHistory` key is
   * read; any other metadata keys are ignored.
   */
  metadata?: Record<string, unknown> | null;
  /** Hide the header. Useful when embedding inside a larger card. */
  hideHeader?: boolean;
  /**
   * Optional callback. When provided, a "بدء موسم جديد" button is
   * rendered in the header so the user can open a `<StartCropSeasonModal>`.
   * The parent is responsible for actually opening the modal / calling
   * the mutation — this component only raises the click.
   */
  onStartSeason?: () => void;
}

// ---------------------------------------------------------------------------
// Arabic localisation helpers
// ---------------------------------------------------------------------------

const CROP_LABELS_AR: Record<string, string> = {
  wheat: 'قمح',
  barley: 'شعير',
  date_palm: 'نخيل',
  tomato: 'طماطم',
  cucumber: 'خيار',
  corn: 'ذرة',
  soybean: 'فول الصويا',
  rice: 'أرز',
  alfalfa: 'برسيم',
  cotton: 'قطن',
  potato: 'بطاطس',
  onion: 'بصل',
  other: 'أخرى',
};

const SEASON_LABELS_AR: Record<string, string> = {
  winter: 'شتوي',
  summer: 'صيفي',
  'year-round': 'طوال العام',
  spring: 'ربيعي',
  autumn: 'خريفي',
};

function toArabicCropLabel(slug: string, fallback?: string): string {
  if (fallback && fallback.trim()) return fallback;
  return CROP_LABELS_AR[slug] ?? slug;
}

function formatDateAr(iso: string | undefined): string {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('ar-SA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

// ---------------------------------------------------------------------------
// Metadata reader (tolerant to malformed / legacy shapes)
// ---------------------------------------------------------------------------

function readCropHistoryFromMetadata(
  metadata: Record<string, unknown> | null | undefined,
): CropHistoryEntry[] {
  if (!metadata) return [];
  const raw = (metadata as Record<string, unknown>).cropHistory;
  if (!Array.isArray(raw)) return [];

  const entries: CropHistoryEntry[] = [];
  const str = (v: unknown): string | undefined =>
    typeof v === 'string' && v.trim() ? v : undefined;
  const num = (v: unknown): number | undefined =>
    typeof v === 'number' && Number.isFinite(v) ? v : undefined;

  for (const item of raw) {
    if (!item || typeof item !== 'object') continue;
    const obj = item as Record<string, unknown>;
    const cropType = str(obj.cropType);
    const startDate = str(obj.startDate);
    if (!cropType || !startDate) continue;
    entries.push({
      cropType,
      cropTypeAr: str(obj.cropTypeAr),
      season: str(obj.season),
      startDate,
      endDate: str(obj.endDate),
      isCurrent: obj.isCurrent === true,
      yieldKgHa: num(obj.yieldKgHa),
      notes: str(obj.notes),
      plowingDate: str(obj.plowingDate),
      plowingDurationHours: num(obj.plowingDurationHours),
      plowingCost: num(obj.plowingCost),
      plowingEquipmentId: str(obj.plowingEquipmentId),
      plowingEquipmentName: str(obj.plowingEquipmentName),
      plowingEquipmentNameAr: str(obj.plowingEquipmentNameAr),
      landPreparationDate: str(obj.landPreparationDate),
      landPreparationDurationHours: num(obj.landPreparationDurationHours),
      landPreparationCost: num(obj.landPreparationCost),
      landPreparationEquipmentId: str(obj.landPreparationEquipmentId),
      landPreparationEquipmentName: str(obj.landPreparationEquipmentName),
      landPreparationEquipmentNameAr: str(obj.landPreparationEquipmentNameAr),
      seedVariety: str(obj.seedVariety),
      seedVarietyAr: str(obj.seedVarietyAr),
      plantingDensityKgHa: num(obj.plantingDensityKgHa),
      irrigationType: str(obj.irrigationType),
      irrigationTypeAr: str(obj.irrigationTypeAr),
      estimatedHarvestDate: str(obj.estimatedHarvestDate),
    });
  }

  // Sort by startDate descending (newest first) so the timeline reads
  // top → bottom = now → past, which matches the standard "recent
  // activity first" UX expectation in Arabic dashboards.
  return entries.sort((a, b) => b.startDate.localeCompare(a.startDate));
}

// ---------------------------------------------------------------------------
// Public helper: build a fresh history entry from a new field's inputs
// ---------------------------------------------------------------------------

/**
 * Returns the initial `cropHistory` array for a brand-new field.
 *
 * Intended use: call this from the "Add Field" flow, assign the result
 * to `metadata.cropHistory` before POSTing the create request, and the
 * backend will persist the seeded history inside the existing JSONB
 * column without any migration.
 */
export function buildInitialCropHistory(args: {
  cropType: string;
  cropTypeAr?: string;
  plantingDate?: string | null;
  season?: string;
}): CropHistoryEntry[] {
  const startDate =
    args.plantingDate && args.plantingDate.trim()
      ? new Date(args.plantingDate).toISOString()
      : new Date().toISOString();

  return [
    {
      cropType: args.cropType,
      cropTypeAr: args.cropTypeAr ?? CROP_LABELS_AR[args.cropType],
      season: args.season,
      startDate,
      isCurrent: true,
    },
  ];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const IRRIGATION_LABELS_AR: Record<string, string> = {
  drip: 'تنقيط',
  sprinkler: 'رشاشات',
  flood: 'غمر',
  pivot: 'محوري',
  manual: 'يدوي',
  other: 'أخرى',
};

export const CropHistoryTimeline: React.FC<CropHistoryTimelineProps> = ({
  currentCropType,
  currentCropTypeAr,
  fieldCreatedAt,
  metadata,
  hideHeader = false,
  onStartSeason,
}) => {
  const persistedEntries = readCropHistoryFromMetadata(metadata);

  // Fallback: synthesise a single entry from the live crop type so
  // fields created before this feature landed still render a non-empty
  // timeline. The fallback is only used when `cropHistory` is absent.
  const entries: CropHistoryEntry[] =
    persistedEntries.length > 0
      ? persistedEntries
      : [
          {
            cropType: currentCropType,
            cropTypeAr: currentCropTypeAr,
            startDate: fieldCreatedAt ?? new Date().toISOString(),
            isCurrent: true,
          },
        ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4" dir="rtl">
      {!hideHeader && (
        <div className="mb-4 flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <Wheat className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-gray-900">تاريخ المحاصيل</h3>
            <span className="text-xs text-gray-500">
              ({entries.length} {entries.length === 1 ? 'إدخال' : 'إدخالات'})
            </span>
          </div>
          {onStartSeason && (
            <button
              type="button"
              onClick={onStartSeason}
              className="inline-flex items-center gap-1 text-xs font-medium bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-md transition-colors"
            >
              <PlusCircle className="w-3.5 h-3.5" aria-hidden="true" />
              بدء موسم جديد
            </button>
          )}
        </div>
      )}

      {entries.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">
          لا توجد سجلات تاريخية
        </p>
      ) : (
        <ol className="relative border-r-2 border-gray-200 pr-4 space-y-4">
          {entries.map((entry, idx) => {
            const isCurrent = !!entry.isCurrent && !entry.endDate;
            const cropAr = toArabicCropLabel(entry.cropType, entry.cropTypeAr);
            const seasonAr = entry.season
              ? SEASON_LABELS_AR[entry.season] ?? entry.season
              : null;
            return (
              <li key={`${entry.cropType}-${entry.startDate}-${idx}`} className="relative">
                {/* Timeline dot */}
                <span
                  className={`absolute -right-[26px] top-1 flex h-4 w-4 items-center justify-center rounded-full border-2 border-white shadow ${
                    isCurrent ? 'bg-green-500' : 'bg-gray-400'
                  }`}
                  aria-hidden="true"
                />
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-gray-900">{cropAr}</span>
                      {isCurrent && (
                        <span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">
                          الحالي
                        </span>
                      )}
                      {seasonAr && (
                        <span className="text-[10px] bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                          {seasonAr}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 text-xs text-gray-600 flex items-center gap-1">
                      <Calendar className="w-3 h-3" aria-hidden="true" />
                      <span>
                        تاريخ البذار: <strong>{formatDateAr(entry.startDate)}</strong>
                        {entry.endDate && ` — ${formatDateAr(entry.endDate)}`}
                      </span>
                    </div>
                    {entry.plowingDate && (
                      <div className="mt-2 rounded-md border border-yellow-200 bg-yellow-50/60 p-2 space-y-1">
                        <div className="text-xs text-gray-800 flex items-center gap-1">
                          <Tractor className="w-3 h-3 text-yellow-700" aria-hidden="true" />
                          <span>
                            تاريخ الحراثة:{' '}
                            <strong>{formatDateAr(entry.plowingDate)}</strong>
                          </span>
                        </div>
                        {entry.plowingEquipmentId && (
                          <div className="text-[11px] text-gray-700 flex items-center gap-1">
                            <Wrench className="w-3 h-3 text-gray-500" aria-hidden="true" />
                            <span>المعدة:</span>
                            <Link
                              href={`/equipment/${entry.plowingEquipmentId}`}
                              className="font-medium text-blue-700 hover:text-blue-900 hover:underline"
                            >
                              {entry.plowingEquipmentNameAr ??
                                entry.plowingEquipmentName ??
                                entry.plowingEquipmentId}
                            </Link>
                          </div>
                        )}
                        {typeof entry.plowingDurationHours === 'number' && (
                          <div className="text-[11px] text-gray-700 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-gray-500" aria-hidden="true" />
                            <span>
                              المدة:{' '}
                              <strong>
                                {entry.plowingDurationHours.toLocaleString('ar-SA')}
                              </strong>{' '}
                              ساعة
                            </span>
                          </div>
                        )}
                        {typeof entry.plowingCost === 'number' && (
                          <div className="text-[11px] text-gray-700 flex items-center gap-1">
                            <DollarSign className="w-3 h-3 text-gray-500" aria-hidden="true" />
                            <span>
                              التكلفة:{' '}
                              <strong>
                                {entry.plowingCost.toLocaleString('ar-SA')}
                              </strong>{' '}
                              ريال
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                    {entry.landPreparationDate && (
                      <div className="mt-2 rounded-md border border-stone-200 bg-stone-50/60 p-2 space-y-1">
                        <div className="text-xs text-gray-800 flex items-center gap-1">
                          <Layers className="w-3 h-3 text-stone-600" aria-hidden="true" />
                          <span>
                            تهيئة الأرض:{' '}
                            <strong>{formatDateAr(entry.landPreparationDate)}</strong>
                          </span>
                        </div>
                        {entry.landPreparationEquipmentId && (
                          <div className="text-[11px] text-gray-700 flex items-center gap-1">
                            <Wrench className="w-3 h-3 text-gray-500" aria-hidden="true" />
                            <span>المعدة:</span>
                            <Link
                              href={`/equipment/${entry.landPreparationEquipmentId}`}
                              className="font-medium text-blue-700 hover:text-blue-900 hover:underline"
                            >
                              {entry.landPreparationEquipmentNameAr ??
                                entry.landPreparationEquipmentName ??
                                entry.landPreparationEquipmentId}
                            </Link>
                          </div>
                        )}
                        {typeof entry.landPreparationDurationHours === 'number' && (
                          <div className="text-[11px] text-gray-700 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-gray-500" aria-hidden="true" />
                            <span>
                              المدة:{' '}
                              <strong>
                                {entry.landPreparationDurationHours.toLocaleString('ar-SA')}
                              </strong>{' '}
                              ساعة
                            </span>
                          </div>
                        )}
                        {typeof entry.landPreparationCost === 'number' && (
                          <div className="text-[11px] text-gray-700 flex items-center gap-1">
                            <DollarSign className="w-3 h-3 text-gray-500" aria-hidden="true" />
                            <span>
                              التكلفة:{' '}
                              <strong>
                                {entry.landPreparationCost.toLocaleString('ar-SA')}
                              </strong>{' '}
                              ريال
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                    {/* Per-entry rollup: total land-prep operation cost + hours */}
                    {(() => {
                      const plowCost = entry.plowingCost ?? 0;
                      const prepCost = entry.landPreparationCost ?? 0;
                      const plowHrs = entry.plowingDurationHours ?? 0;
                      const prepHrs = entry.landPreparationDurationHours ?? 0;
                      const totalCost = plowCost + prepCost;
                      const totalHrs = plowHrs + prepHrs;
                      if (totalCost === 0 && totalHrs === 0) return null;
                      return (
                        <div className="mt-2 pt-2 border-t border-dashed border-gray-200 text-[11px] text-gray-800 flex flex-wrap items-center gap-x-3 gap-y-1">
                          <span className="font-semibold">الإجمالي قبل البذار:</span>
                          {totalHrs > 0 && (
                            <span className="inline-flex items-center gap-1">
                              <Clock className="w-3 h-3 text-gray-500" aria-hidden="true" />
                              <strong>{totalHrs.toLocaleString('ar-SA')}</strong> ساعة
                            </span>
                          )}
                          {totalCost > 0 && (
                            <span className="inline-flex items-center gap-1">
                              <DollarSign className="w-3 h-3 text-gray-500" aria-hidden="true" />
                              <strong>{totalCost.toLocaleString('ar-SA')}</strong> ريال
                            </span>
                          )}
                        </div>
                      );
                    })()}
                    {/* Rich Stage-2 details (only render when present) */}
                    {(entry.seedVariety || entry.seedVarietyAr) && (
                      <div className="mt-1 text-xs text-gray-700 flex items-center gap-1">
                        <Sprout className="w-3 h-3 text-green-600" aria-hidden="true" />
                        <span>
                          الصنف:{' '}
                          <strong>
                            {entry.seedVarietyAr ?? entry.seedVariety}
                          </strong>
                        </span>
                      </div>
                    )}
                    {typeof entry.plantingDensityKgHa === 'number' && (
                      <div className="mt-1 text-xs text-gray-700 flex items-center gap-1">
                        <Wheat className="w-3 h-3 text-amber-600" aria-hidden="true" />
                        <span>
                          كثافة البذر:{' '}
                          <strong>
                            {entry.plantingDensityKgHa.toLocaleString('ar-SA')}
                          </strong>{' '}
                          كجم/هكتار
                        </span>
                      </div>
                    )}
                    {(entry.irrigationType || entry.irrigationTypeAr) && (
                      <div className="mt-1 text-xs text-gray-700 flex items-center gap-1">
                        <Droplets className="w-3 h-3 text-blue-600" aria-hidden="true" />
                        <span>
                          نظام الري:{' '}
                          <strong>
                            {entry.irrigationTypeAr ??
                              IRRIGATION_LABELS_AR[entry.irrigationType ?? ''] ??
                              entry.irrigationType}
                          </strong>
                        </span>
                      </div>
                    )}
                    {entry.estimatedHarvestDate && (
                      <div className="mt-1 text-xs text-gray-700 flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-purple-600" aria-hidden="true" />
                        <span>
                          الحصاد المتوقع:{' '}
                          <strong>{formatDateAr(entry.estimatedHarvestDate)}</strong>
                        </span>
                      </div>
                    )}
                    {typeof entry.yieldKgHa === 'number' && (
                      <div className="mt-1 text-xs text-gray-700 flex items-center gap-1">
                        <TrendingUp className="w-3 h-3 text-emerald-600" aria-hidden="true" />
                        <span>
                          الإنتاجية:{' '}
                          <strong>{entry.yieldKgHa.toLocaleString('ar-SA')}</strong>{' '}
                          كجم/هكتار
                        </span>
                      </div>
                    )}
                    {entry.notes && (
                      <p className="mt-1 text-xs text-gray-500 leading-relaxed">
                        {entry.notes}
                      </p>
                    )}
                  </div>
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
};

export default CropHistoryTimeline;
