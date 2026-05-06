/**
 * Satellite Imagery Page — Types & Configuration
 * صور الأقمار الاصطناعية — الأنواع والإعدادات
 */

// ─── Layer categories & config ─────────────────────────────────────────────

export type LayerGroup = 'rgb' | 'vegetation' | 'water' | 'snow' | 'fire' | 'chlorophyll';

export interface SatelliteLayer {
  id: string;
  label: string;
  labelAr: string;
  group: LayerGroup;
  /** Tailwind ring color class shown when active */
  ringClass: string;
  /** Hex color for map polygon fill (matches schema high-value color) */
  fillColor: string;
}

export const SATELLITE_LAYERS: SatelliteLayer[] = [
  // ── RGB Composites ─────────────────────────────────────────────────────────
  { id: 'TRUE_COLOR',        label: 'True Color',          labelAr: 'اللون الحقيقي',                        group: 'rgb',         ringClass: 'ring-sky-400',     fillColor: '#228B22' },
  { id: 'TRUE_COLOR_L1C',    label: 'True Color L1C',      labelAr: 'اللون الحقيقي L1C',                   group: 'rgb',         ringClass: 'ring-sky-500',     fillColor: '#33A84D' },
  { id: 'TRUE_COLOR_L2A',    label: 'True Color L2A',      labelAr: 'اللون الحقيقي L2A',                   group: 'rgb',         ringClass: 'ring-sky-600',     fillColor: '#33A84D' },
  { id: 'FALSE_COLOR',       label: 'False Color IR',      labelAr: 'ألوان كاذبة بالأشعة تحت الحمراء',     group: 'rgb',         ringClass: 'ring-red-600',     fillColor: '#CC0000' },
  { id: 'SWIR',              label: 'SWIR',                labelAr: 'الأشعة تحت الحمراء القصيرة',           group: 'rgb',         ringClass: 'ring-orange-500',  fillColor: '#CC4400' },
  { id: 'FALSE_COLOR_URBAN', label: 'False Color Urban',   labelAr: 'ألوان كاذبة حضرية',                   group: 'rgb',         ringClass: 'ring-purple-500',  fillColor: '#7755CC' },

  // ── Vegetation ─────────────────────────────────────────────────────────────
  { id: 'NDVI',              label: 'NDVI',                labelAr: 'مؤشر الغطاء النباتي',                  group: 'vegetation',  ringClass: 'ring-green-500',   fillColor: '#1A7A1A' },
  { id: 'EVI',               label: 'EVI',                 labelAr: 'مؤشر النباتات المحسّن',                group: 'vegetation',  ringClass: 'ring-green-400',   fillColor: '#1A7A1A' },
  { id: 'EVI2',              label: 'EVI2',                labelAr: 'EVI ثنائي النطاق',                     group: 'vegetation',  ringClass: 'ring-green-300',   fillColor: '#1A7A1A' },
  { id: 'GNDVI',             label: 'GNDVI',               labelAr: 'NDVI الأخضر',                          group: 'vegetation',  ringClass: 'ring-emerald-500', fillColor: '#228B22' },
  { id: 'KNDVI',             label: 'kNDVI',               labelAr: 'NDVI النواة',                          group: 'vegetation',  ringClass: 'ring-lime-600',    fillColor: '#1A5A1A' },
  { id: 'SAVI',              label: 'SAVI',                labelAr: 'مؤشر معدّل للتربة',                   group: 'vegetation',  ringClass: 'ring-lime-500',    fillColor: '#3A8A3A' },
  { id: 'NDYI',              label: 'NDYI',                labelAr: 'مؤشر الاصفرار',                        group: 'vegetation',  ringClass: 'ring-yellow-400',  fillColor: '#E8C800' },
  { id: 'LAI',               label: 'LAI',                 labelAr: 'مؤشر مساحة الأوراق',                  group: 'vegetation',  ringClass: 'ring-cyan-500',    fillColor: '#1A5A1A' },
  { id: 'FAPAR',             label: 'FAPAR',               labelAr: 'جزء الإشعاع الممتص',                  group: 'vegetation',  ringClass: 'ring-teal-400',    fillColor: '#006600' },
  { id: 'FCOVER',            label: 'FCOVER',              labelAr: 'كسر الغطاء النباتي',                  group: 'vegetation',  ringClass: 'ring-teal-500',    fillColor: '#006600' },
  { id: 'ARVI',              label: 'ARVI',                labelAr: 'مؤشر مقاوم للغلاف الجوي',             group: 'vegetation',  ringClass: 'ring-green-600',   fillColor: '#1A7A1A' },
  { id: 'PSRI',              label: 'PSRI',                labelAr: 'مؤشر شيخوخة النبات',                  group: 'vegetation',  ringClass: 'ring-orange-400',  fillColor: '#DD7700' },

  // ── Water / Moisture ───────────────────────────────────────────────────────
  { id: 'NDWI',              label: 'NDWI',                labelAr: 'مؤشر المياه المعياري',                 group: 'water',       ringClass: 'ring-blue-500',    fillColor: '#0055CC' },
  { id: 'NDMI',              label: 'NDMI',                labelAr: 'مؤشر رطوبة التربة',                   group: 'water',       ringClass: 'ring-blue-400',    fillColor: '#0077BB' },
  { id: 'NDMI_STRESS',       label: 'NDMI Stress',         labelAr: 'إجهاد رطوبة التربة',                  group: 'water',       ringClass: 'ring-blue-600',    fillColor: '#0077BB' },
  { id: 'MSI',               label: 'MSI',                 labelAr: 'مؤشر إجهاد الرطوبة',                  group: 'water',       ringClass: 'ring-indigo-500',  fillColor: '#0077CC' },
  { id: 'NDII',              label: 'NDII',                labelAr: 'مؤشر الأشعة تحت الحمراء',             group: 'water',       ringClass: 'ring-violet-500',  fillColor: '#0066CC' },

  // ── Snow / Ice ─────────────────────────────────────────────────────────────
  { id: 'NDSI',              label: 'NDSI',                labelAr: 'مؤشر الثلج',                           group: 'snow',        ringClass: 'ring-sky-300',     fillColor: '#DDEEFF' },

  // ── Fire / Burn ────────────────────────────────────────────────────────────
  { id: 'NBR',               label: 'NBR',                 labelAr: 'نسبة الحرق المعيّرة',                 group: 'fire',        ringClass: 'ring-red-600',     fillColor: '#1A7A1A' },
  { id: 'BAIS2',             label: 'BAIS2',               labelAr: 'مؤشر المناطق المحروقة',               group: 'fire',        ringClass: 'ring-orange-600',  fillColor: '#AA1100' },

  // ── Chlorophyll ────────────────────────────────────────────────────────────
  { id: 'NDCI',              label: 'NDCI',                labelAr: 'مؤشر الكلوروفيل المعياري',             group: 'chlorophyll', ringClass: 'ring-teal-600',    fillColor: '#00AA44' },
  { id: 'CHL_REDEDGE',       label: 'CHL RedEdge',         labelAr: 'كلوروفيل الحافة الحمراء',             group: 'chlorophyll', ringClass: 'ring-emerald-600', fillColor: '#005500' },
  { id: 'MCARI',             label: 'MCARI',               labelAr: 'مؤشر امتصاص الكلوروفيل',              group: 'chlorophyll', ringClass: 'ring-green-700',   fillColor: '#005500' },
  { id: 'ARI',               label: 'ARI',                 labelAr: 'مؤشر الأنثوسيانين',                   group: 'chlorophyll', ringClass: 'ring-pink-500',    fillColor: '#CC2277' },
  { id: 'MARI',              label: 'mARI',                labelAr: 'مؤشر الأنثوسيانين المعدّل',           group: 'chlorophyll', ringClass: 'ring-pink-600',    fillColor: '#AA1166' },
  { id: 'SIPI1',             label: 'SIPI1',               labelAr: 'مؤشر الصبغة البنيوي',                 group: 'chlorophyll', ringClass: 'ring-amber-500',   fillColor: '#228B22' },
  { id: 'PSSRB1',            label: 'PSSRb1',              labelAr: 'نسبة الكلوروفيل ب',                   group: 'chlorophyll', ringClass: 'ring-lime-700',    fillColor: '#228B22' },
  { id: 'REDEDGE_POSITION',  label: 'RedEdge Position',    labelAr: 'موضع الحافة الحمراء',                 group: 'chlorophyll', ringClass: 'ring-red-400',     fillColor: '#005500' },
];

export const GROUP_LABELS: Record<LayerGroup, { en: string; ar: string; icon: string }> = {
  rgb:         { en: 'RGB',         ar: 'صور ملونة',    icon: '🎨' },
  vegetation:  { en: 'Vegetation',  ar: 'النباتات',     icon: '🌿' },
  water:       { en: 'Water',       ar: 'المياه',       icon: '💧' },
  snow:        { en: 'Snow',        ar: 'الثلوج',       icon: '❄️' },
  fire:        { en: 'Fire',        ar: 'الحرائق',      icon: '🔥' },
  chlorophyll: { en: 'Chlorophyll', ar: 'الكلوروفيل',   icon: '🔬' },
};

// ─── NDVI → fill color for polygons ────────────────────────────────────────

/** Interpolate NDVI value to a hex fill color (red → yellow → green) */
export function ndviToFillColor(ndvi: number | null | undefined): string {
  if (ndvi == null) return '#94a3b8'; // gray for no data
  if (ndvi >= 0.6) return '#16a34a';  // dark green
  if (ndvi >= 0.4) return '#4ade80';  // light green
  if (ndvi >= 0.2) return '#facc15';  // yellow
  if (ndvi >= 0.0) return '#fb923c';  // orange
  return '#ef4444';                    // red
}

export function ndviToHealthDot(ndvi: number | null | undefined): string {
  if (ndvi == null) return 'bg-gray-300';
  if (ndvi >= 0.5) return 'bg-green-500';
  if (ndvi >= 0.3) return 'bg-yellow-400';
  if (ndvi >= 0.1) return 'bg-orange-400';
  return 'bg-red-500';
}

// ─── KPI badge config ───────────────────────────────────────────────────────

export interface BadgeConfig {
  key: string;           // keyof FieldKpiSnapshot
  label: string;
  labelAr: string;
  icon: string;
  unit?: string;
  format: (v: number) => string;
  color: (v: number) => string;
}

export const BADGE_CONFIGS: BadgeConfig[] = [
  {
    key: 'ndvi',
    label: 'NDVI',
    labelAr: 'مؤشر النباتات',
    icon: '🌿',
    format: (v) => v.toFixed(2),
    color: (v) => v >= 0.5 ? '#16a34a' : v >= 0.3 ? '#ca8a04' : '#dc2626',
  },
  {
    key: 'temperature',
    label: 'Temp',
    labelAr: 'الحرارة',
    icon: '🌡️',
    unit: '°C',
    format: (v) => v.toFixed(1),
    color: (v) => v > 38 || v < 5 ? '#dc2626' : v > 32 ? '#ca8a04' : '#16a34a',
  },
  {
    key: 'aqi',
    label: 'AQI',
    labelAr: 'جودة الهواء',
    icon: '💨',
    format: (v) => v.toFixed(0),
    color: (v) => v <= 2 ? '#16a34a' : v <= 3 ? '#ca8a04' : '#dc2626',
  },
  {
    key: 'ndwi',
    label: 'NDWI',
    labelAr: 'مؤشر المياه',
    icon: '💧',
    format: (v) => v.toFixed(2),
    color: (v) => v >= 0.2 ? '#2563eb' : v >= 0 ? '#ca8a04' : '#dc2626',
  },
];
