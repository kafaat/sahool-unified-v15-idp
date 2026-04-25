/**
 * Unified Spectral Index Colormaps
 * مصدر حقيقة موحّد لخرائط ألوان المؤشرات الطيفية
 *
 * Single source of truth for all six satellite-derived spectral indices
 * (NDVI, NDWI, EVI, SAVI, NDRE, LAI). Color stops, legend items, valid
 * value ranges and bilingual labels follow conventions established by
 * Sentinel Hub Playground / USGS / EOS Crop Monitoring so the same
 * numeric value is rendered identically across:
 *
 *   - the raster tile overlay (`NdviTileLayer.tsx`),
 *   - field-polygon paint expressions (`FieldMap.tsx`, `MapView.tsx`),
 *   - the side-by-side comparison view (`SplitScreenNDVI.tsx`),
 *   - the index switcher chips (`SpectralIndexSwitcher.tsx`).
 *
 * Importers MUST NOT redefine these stops locally. To change a colour,
 * update this file and the entire UI updates in lockstep.
 */
import type { LucideIcon } from 'lucide-react';
import { Droplets, Eye, Flower2, Leaf, Mountain, Sprout } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Identifier for a supported spectral index. */
export type SpectralIndexId = 'ndvi' | 'ndwi' | 'evi' | 'savi' | 'ndre' | 'lai';

export interface ColorStop {
  /** Numeric value at which `color` applies. */
  value: number;
  /** Hex colour (e.g. `#1a9850`). */
  color: string;
}

export interface LegendItem {
  /** Lower bound (inclusive). */
  min: number;
  /** Upper bound (exclusive, except for the last item which is inclusive). */
  max: number;
  /** Representative colour for the band. */
  color: string;
  /** English label. */
  labelEn: string;
  /** Arabic label. */
  labelAr: string;
}

export interface SpectralIndexMetadata {
  id: SpectralIndexId;
  /** Uppercase short code (e.g. `NDVI`). Always Latin. */
  code: string;
  nameEn: string;
  nameAr: string;
  descriptionEn: string;
  descriptionAr: string;
  /** Lucide icon component for the toggle chip. */
  icon: LucideIcon;
  /** Inclusive minimum displayable value. */
  minValue: number;
  /** Inclusive maximum displayable value. */
  maxValue: number;
  /**
   * What this index is best for, shown in tooltips.
   * Bilingual.
   */
  bestForEn: string;
  bestForAr: string;
}

// ---------------------------------------------------------------------------
// Index metadata (chip icons + bilingual descriptions)
// ---------------------------------------------------------------------------

export const SPECTRAL_INDEX_METADATA: Record<SpectralIndexId, SpectralIndexMetadata> = {
  ndvi: {
    id: 'ndvi',
    code: 'NDVI',
    nameEn: 'Normalized Difference Vegetation Index',
    nameAr: 'مؤشر الاختلاف الطبيعي للنبات',
    descriptionEn: 'Measures vegetation density and overall canopy health.',
    descriptionAr: 'يقيس كثافة الغطاء النباتي وصحة المظلة بشكل عام.',
    icon: Leaf,
    minValue: -1.0,
    maxValue: 1.0,
    bestForEn: 'General crop health & growth tracking',
    bestForAr: 'تتبع صحة المحصول ونمو النبات بشكل عام',
  },
  ndwi: {
    id: 'ndwi',
    code: 'NDWI',
    nameEn: 'Normalized Difference Water Index',
    nameAr: 'مؤشر الاختلاف الطبيعي للمياه',
    descriptionEn: 'Highlights canopy water content and detects moisture stress.',
    descriptionAr: 'يبرز محتوى الماء في النبات ويكشف الإجهاد المائي.',
    icon: Droplets,
    minValue: -1.0,
    maxValue: 1.0,
    bestForEn: 'Irrigation planning & drought monitoring',
    bestForAr: 'التخطيط للري ومراقبة الجفاف',
  },
  evi: {
    id: 'evi',
    code: 'EVI',
    nameEn: 'Enhanced Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المحسَّن',
    descriptionEn: 'Reduces atmospheric and soil noise; better in dense canopy.',
    descriptionAr: 'يقلّل تأثير الغلاف الجوي والتربة، أفضل في الكثافة العالية.',
    icon: Sprout,
    minValue: -1.0,
    maxValue: 1.0,
    bestForEn: 'Dense canopy biomass estimation',
    bestForAr: 'تقدير الكتلة الحيوية للمظلة الكثيفة',
  },
  savi: {
    id: 'savi',
    code: 'SAVI',
    nameEn: 'Soil Adjusted Vegetation Index',
    nameAr: 'مؤشر النبات المعدَّل للتربة',
    descriptionEn: 'Compensates for bare soil background in sparse vegetation.',
    descriptionAr: 'يعدّل تأثير التربة المكشوفة في الغطاء النباتي المتناثر.',
    icon: Mountain,
    minValue: -1.0,
    maxValue: 1.0,
    bestForEn: 'Early-season & arid-region monitoring',
    bestForAr: 'مراقبة بدايات الموسم والمناطق الجافة',
  },
  ndre: {
    id: 'ndre',
    code: 'NDRE',
    nameEn: 'Normalized Difference Red Edge',
    nameAr: 'مؤشر الحافة الحمراء الطبيعي',
    descriptionEn: 'Sensitive to chlorophyll content and nitrogen status.',
    descriptionAr: 'حساس لمحتوى الكلوروفيل وحالة النيتروجين.',
    icon: Flower2,
    minValue: -1.0,
    maxValue: 1.0,
    bestForEn: 'Nitrogen status & late-season vigor',
    bestForAr: 'حالة النيتروجين وقوّة النمو في أواخر الموسم',
  },
  lai: {
    id: 'lai',
    code: 'LAI',
    nameEn: 'Leaf Area Index',
    nameAr: 'مؤشر مساحة الأوراق',
    descriptionEn: 'Total leaf area per unit ground area (m²/m²).',
    descriptionAr: 'إجمالي مساحة الأوراق لكل وحدة مساحة أرضية (م²/م²).',
    icon: Eye,
    minValue: 0.0,
    maxValue: 8.0,
    bestForEn: 'Canopy coverage & yield modelling',
    bestForAr: 'تغطية المظلة ونمذجة الإنتاجية',
  },
};

/** Ordered list of supported indices, matching toggle order in UI. */
export const SPECTRAL_INDEX_ORDER: readonly SpectralIndexId[] = [
  'ndvi',
  'evi',
  'savi',
  'ndre',
  'ndwi',
  'lai',
] as const;

// ---------------------------------------------------------------------------
// Colour stops — Sentinel Hub / USGS aligned
//
// Vegetation indices (NDVI, EVI, SAVI, NDRE) follow the canonical
// red→orange→yellow→light-green→dark-green ramp used by the Sentinel Hub
// Playground. NDWI uses a brown→blue ramp (water content). LAI uses a
// pale-cream→dark-green ramp scaled for the 0–8 LAI range.
// ---------------------------------------------------------------------------

const NDVI_STOPS: ColorStop[] = [
  { value: -1.0, color: '#0c0c0c' }, // Water / cloud / snow shadow
  { value: 0.0, color: '#a50026' }, // Bare / non-vegetation (deep red)
  { value: 0.1, color: '#d73027' },
  { value: 0.2, color: '#f46d43' },
  { value: 0.3, color: '#fdae61' },
  { value: 0.4, color: '#fee08b' },
  { value: 0.5, color: '#d9ef8b' },
  { value: 0.6, color: '#a6d96a' },
  { value: 0.7, color: '#66bd63' },
  { value: 0.8, color: '#1a9850' },
  { value: 1.0, color: '#006837' }, // Peak vegetation
];

const NDVI_LEGEND: LegendItem[] = [
  { min: -1.0, max: 0.0, color: '#0c0c0c', labelEn: 'Water / Cloud', labelAr: 'مياه / غيوم' },
  { min: 0.0, max: 0.15, color: '#a50026', labelEn: 'Bare soil', labelAr: 'تربة مكشوفة' },
  { min: 0.15, max: 0.3, color: '#f46d43', labelEn: 'Sparse / stressed', labelAr: 'متناثر / مُجهَد' },
  { min: 0.3, max: 0.5, color: '#fee08b', labelEn: 'Moderate', labelAr: 'معتدل' },
  { min: 0.5, max: 0.7, color: '#a6d96a', labelEn: 'Healthy', labelAr: 'صحي' },
  { min: 0.7, max: 1.0, color: '#1a9850', labelEn: 'Very healthy', labelAr: 'صحي جداً' },
];

const EVI_STOPS: ColorStop[] = [
  { value: -1.0, color: '#0c0c0c' },
  { value: 0.0, color: '#a50026' },
  { value: 0.15, color: '#f46d43' },
  { value: 0.3, color: '#fee08b' },
  { value: 0.45, color: '#a6d96a' },
  { value: 0.6, color: '#1a9850' },
  { value: 1.0, color: '#006837' },
];

const EVI_LEGEND: LegendItem[] = [
  { min: -1.0, max: 0.0, color: '#0c0c0c', labelEn: 'Water / Cloud', labelAr: 'مياه / غيوم' },
  { min: 0.0, max: 0.15, color: '#a50026', labelEn: 'Bare soil', labelAr: 'تربة مكشوفة' },
  { min: 0.15, max: 0.3, color: '#f46d43', labelEn: 'Sparse vegetation', labelAr: 'نباتات متناثرة' },
  { min: 0.3, max: 0.45, color: '#fee08b', labelEn: 'Moderate', labelAr: 'معتدل' },
  { min: 0.45, max: 0.6, color: '#a6d96a', labelEn: 'Dense', labelAr: 'كثيف' },
  { min: 0.6, max: 1.0, color: '#1a9850', labelEn: 'Very dense', labelAr: 'كثيف جداً' },
];

const SAVI_STOPS: ColorStop[] = [
  { value: -1.0, color: '#0c0c0c' },
  { value: 0.0, color: '#a50026' },
  { value: 0.1, color: '#d73027' },
  { value: 0.2, color: '#f46d43' },
  { value: 0.3, color: '#fdae61' },
  { value: 0.4, color: '#fee08b' },
  { value: 0.5, color: '#d9ef8b' },
  { value: 0.6, color: '#a6d96a' },
  { value: 0.8, color: '#1a9850' },
  { value: 1.0, color: '#006837' },
];

const SAVI_LEGEND: LegendItem[] = [
  { min: -1.0, max: 0.0, color: '#0c0c0c', labelEn: 'Water / Cloud', labelAr: 'مياه / غيوم' },
  { min: 0.0, max: 0.2, color: '#a50026', labelEn: 'Bare soil', labelAr: 'تربة مكشوفة' },
  { min: 0.2, max: 0.4, color: '#f46d43', labelEn: 'Sparse', labelAr: 'متناثر' },
  { min: 0.4, max: 0.6, color: '#fee08b', labelEn: 'Moderate', labelAr: 'معتدل' },
  { min: 0.6, max: 0.8, color: '#a6d96a', labelEn: 'Dense', labelAr: 'كثيف' },
  { min: 0.8, max: 1.0, color: '#1a9850', labelEn: 'Very dense', labelAr: 'كثيف جداً' },
];

const NDRE_STOPS: ColorStop[] = [
  { value: -1.0, color: '#0c0c0c' },
  { value: 0.0, color: '#a50026' },
  { value: 0.1, color: '#f46d43' },
  { value: 0.2, color: '#fdae61' },
  { value: 0.3, color: '#fee08b' },
  { value: 0.4, color: '#d9ef8b' },
  { value: 0.5, color: '#a6d96a' },
  { value: 0.6, color: '#1a9850' },
  { value: 1.0, color: '#006837' },
];

const NDRE_LEGEND: LegendItem[] = [
  { min: -1.0, max: 0.0, color: '#0c0c0c', labelEn: 'Water / Cloud', labelAr: 'مياه / غيوم' },
  { min: 0.0, max: 0.2, color: '#a50026', labelEn: 'Severe N deficit', labelAr: 'نقص شديد في النيتروجين' },
  { min: 0.2, max: 0.3, color: '#fdae61', labelEn: 'Marginal N', labelAr: 'نيتروجين حدّي' },
  { min: 0.3, max: 0.4, color: '#fee08b', labelEn: 'Adequate N', labelAr: 'نيتروجين كافٍ' },
  { min: 0.4, max: 0.6, color: '#a6d96a', labelEn: 'Good N', labelAr: 'نيتروجين جيد' },
  { min: 0.6, max: 1.0, color: '#1a9850', labelEn: 'Excellent N', labelAr: 'نيتروجين ممتاز' },
];

// NDWI: brown (dry) → blue (water saturated). Sentinel Hub convention.
const NDWI_STOPS: ColorStop[] = [
  { value: -1.0, color: '#8c510a' }, // Very dry
  { value: -0.3, color: '#bf812d' },
  { value: -0.1, color: '#dfc27d' },
  { value: 0.0, color: '#f6e8c3' }, // Neutral
  { value: 0.1, color: '#c7eae5' },
  { value: 0.2, color: '#80cdc1' },
  { value: 0.3, color: '#35978f' },
  { value: 0.5, color: '#01665e' },
  { value: 1.0, color: '#003c30' }, // Open water
];

const NDWI_LEGEND: LegendItem[] = [
  { min: -1.0, max: -0.3, color: '#8c510a', labelEn: 'Very dry', labelAr: 'جاف جداً' },
  { min: -0.3, max: 0.0, color: '#dfc27d', labelEn: 'Dry / stressed', labelAr: 'جاف / مُجهَد' },
  { min: 0.0, max: 0.2, color: '#c7eae5', labelEn: 'Adequate moisture', labelAr: 'رطوبة كافية' },
  { min: 0.2, max: 0.4, color: '#80cdc1', labelEn: 'Moist canopy', labelAr: 'مظلة رطبة' },
  { min: 0.4, max: 0.7, color: '#35978f', labelEn: 'Wet / saturated', labelAr: 'رطب / مشبع' },
  { min: 0.7, max: 1.0, color: '#01665e', labelEn: 'Open water', labelAr: 'مسطح مائي' },
];

// LAI: 0..8 m²/m². Pale cream → dark green.
const LAI_STOPS: ColorStop[] = [
  { value: 0.0, color: '#fff7bc' },
  { value: 1.0, color: '#fee391' },
  { value: 2.0, color: '#fec44f' },
  { value: 3.0, color: '#a6d96a' },
  { value: 4.0, color: '#66bd63' },
  { value: 5.0, color: '#1a9850' },
  { value: 6.0, color: '#006837' },
  { value: 8.0, color: '#00441b' },
];

const LAI_LEGEND: LegendItem[] = [
  { min: 0.0, max: 1.0, color: '#fff7bc', labelEn: 'Bare / minimal', labelAr: 'مكشوف / أدنى' },
  { min: 1.0, max: 2.0, color: '#fee391', labelEn: 'Sparse canopy', labelAr: 'مظلة متناثرة' },
  { min: 2.0, max: 3.0, color: '#fec44f', labelEn: 'Low canopy', labelAr: 'مظلة منخفضة' },
  { min: 3.0, max: 4.0, color: '#a6d96a', labelEn: 'Moderate canopy', labelAr: 'مظلة متوسطة' },
  { min: 4.0, max: 5.0, color: '#66bd63', labelEn: 'Good canopy', labelAr: 'مظلة جيدة' },
  { min: 5.0, max: 6.0, color: '#1a9850', labelEn: 'Dense canopy', labelAr: 'مظلة كثيفة' },
  { min: 6.0, max: 8.0, color: '#006837', labelEn: 'Very dense', labelAr: 'كثيفة جداً' },
];

// ---------------------------------------------------------------------------
// Lookup tables (private — exposed via accessor functions)
// ---------------------------------------------------------------------------

const INDEX_STOPS: Record<SpectralIndexId, ColorStop[]> = {
  ndvi: NDVI_STOPS,
  ndwi: NDWI_STOPS,
  evi: EVI_STOPS,
  savi: SAVI_STOPS,
  ndre: NDRE_STOPS,
  lai: LAI_STOPS,
};

const INDEX_LEGEND: Record<SpectralIndexId, LegendItem[]> = {
  ndvi: NDVI_LEGEND,
  ndwi: NDWI_LEGEND,
  evi: EVI_LEGEND,
  savi: SAVI_LEGEND,
  ndre: NDRE_LEGEND,
  lai: LAI_LEGEND,
};

// ---------------------------------------------------------------------------
// Public accessors
// ---------------------------------------------------------------------------

/** Return the colour stops for an index (frozen copy — do not mutate). */
export function getIndexColorStops(index: SpectralIndexId): readonly ColorStop[] {
  return INDEX_STOPS[index];
}

/** Return the legend bands for an index (frozen copy — do not mutate). */
export function getIndexLegend(index: SpectralIndexId): readonly LegendItem[] {
  return INDEX_LEGEND[index];
}

/** Return the metadata block for an index. */
export function getIndexMetadata(index: SpectralIndexId): SpectralIndexMetadata {
  return SPECTRAL_INDEX_METADATA[index];
}

/**
 * Return the linearly-interpolated colour for a given numeric value.
 * Values outside `[minValue, maxValue]` are clamped to the nearest end.
 */
export function getIndexColor(index: SpectralIndexId, value: number): string {
  const stops = INDEX_STOPS[index];
  const meta = SPECTRAL_INDEX_METADATA[index];
  const clamped = Math.min(Math.max(value, meta.minValue), meta.maxValue);

  if (clamped <= stops[0]!.value) return stops[0]!.color;
  const last = stops[stops.length - 1]!;
  if (clamped >= last.value) return last.color;

  for (let i = 0; i < stops.length - 1; i++) {
    const lo = stops[i]!;
    const hi = stops[i + 1]!;
    if (clamped >= lo.value && clamped <= hi.value) {
      const t = (clamped - lo.value) / (hi.value - lo.value);
      return lerpHex(lo.color, hi.color, t);
    }
  }
  return last.color;
}

/**
 * Return the legend band a value falls into. Useful for category labels
 * shown next to the numeric value (e.g. "0.62 — Healthy / صحي").
 */
export function getIndexBand(index: SpectralIndexId, value: number): LegendItem {
  const legend = INDEX_LEGEND[index];
  for (const band of legend) {
    if (value >= band.min && value < band.max) return band;
  }
  // Inclusive on the upper end of the final band.
  return legend[legend.length - 1]!;
}

/** Bilingual health/category label for a value. */
export function getIndexHealthLabel(
  index: SpectralIndexId,
  value: number,
  language: 'en' | 'ar' = 'en',
): string {
  const band = getIndexBand(index, value);
  return language === 'ar' ? band.labelAr : band.labelEn;
}

/**
 * Build a MapLibre `interpolate` expression for the given index.
 *
 * Returned shape: `['interpolate', ['linear'], ['get', valueProp], v0, c0, v1, c1, ...]`
 * Caller must wrap with their preferred outer expression (e.g. `case` for
 * no-data handling).
 */
export function buildInterpolateExpression(
  index: SpectralIndexId,
  valueProperty: string | unknown[] = 'value',
): unknown[] {
  const stops = INDEX_STOPS[index];
  const expr: unknown[] = [
    'interpolate',
    ['linear'],
    typeof valueProperty === 'string' ? ['to-number', ['get', valueProperty]] : valueProperty,
  ];
  for (const stop of stops) {
    expr.push(stop.value, stop.color);
  }
  return expr;
}

/**
 * Build a CSS `linear-gradient(to right, …)` value for legend bars.
 */
export function buildCssGradient(index: SpectralIndexId): string {
  const stops = INDEX_STOPS[index];
  return `linear-gradient(to right, ${stops.map((s) => s.color).join(', ')})`;
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function lerpHex(a: string, b: string, t: number): string {
  const ar = parseInt(a.slice(1, 3), 16);
  const ag = parseInt(a.slice(3, 5), 16);
  const ab = parseInt(a.slice(5, 7), 16);
  const br = parseInt(b.slice(1, 3), 16);
  const bg = parseInt(b.slice(3, 5), 16);
  const bb = parseInt(b.slice(5, 7), 16);
  const r = Math.round(ar + (br - ar) * t);
  const g = Math.round(ag + (bg - ag) * t);
  const bl = Math.round(ab + (bb - ab) * t);
  return `#${[r, g, bl].map((v) => v.toString(16).padStart(2, '0')).join('')}`;
}
