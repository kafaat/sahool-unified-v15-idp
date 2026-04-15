/**
 * Vegetation Indices Types & Configuration
 * انواع وتكوين المؤشرات النباتية
 *
 * All 41 vegetation indices supported by the SAHOOL platform,
 * matching the backend VegetationIndex enum in vegetation_indices.py.
 */

// =============================================================================
// Vegetation Index Enum - 41 indices
// =============================================================================

export enum VegetationIndex {
  // Basic (6)
  NDVI = 'ndvi',
  NDWI = 'ndwi',
  EVI = 'evi',
  SAVI = 'savi',
  LAI = 'lai',
  NDMI = 'ndmi',

  // Chlorophyll & Nitrogen (5)
  NDRE = 'ndre',
  CVI = 'cvi',
  MCARI = 'mcari',
  TCARI = 'tcari',
  SIPI = 'sipi',

  // Early Stress Detection (4)
  GNDVI = 'gndvi',
  VARI = 'vari',
  GLI = 'gli',
  GRVI = 'grvi',

  // Soil & Atmosphere Correction (3)
  MSAVI = 'msavi',
  OSAVI = 'osavi',
  ARVI = 'arvi',

  // Pigment & Stress (5)
  PRI = 'pri',
  CRI = 'cri',
  ARI = 'ari',
  PSRI = 'psri',
  REP = 'rep',

  // Extended Spectral (6)
  NBR = 'nbr',
  EVI2 = 'evi2',
  BSI = 'bsi',
  SR = 'sr',
  CCCI = 'ccci',
  MSI = 'msi',

  // Chlorophyll & Red Edge Enhancement (6)
  CI_GREEN = 'ci_green',
  CI_REDEDGE = 'ci_rededge',
  IRECI = 'ireci',
  MTCI = 'mtci',
  RENDVI = 'rendvi',
  WDRVI = 'wdrvi',

  // Water, Drought & Land Cover (6)
  MNDWI = 'mndwi',
  NBR2 = 'nbr2',
  NDBI = 'ndbi',
  DVI = 'dvi',
  GDVI = 'gdvi',
  TSAVI = 'tsavi',
}

// =============================================================================
// Index Categories
// =============================================================================

export type IndexCategory =
  | 'basic'
  | 'chlorophyll'
  | 'stress_detection'
  | 'soil_corrected'
  | 'pigment'
  | 'red_edge'
  | 'water_drought';

export interface IndexCategoryInfo {
  id: IndexCategory;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
}

export const INDEX_CATEGORIES: Record<IndexCategory, IndexCategoryInfo> = {
  basic: {
    id: 'basic',
    name: 'Basic Vegetation',
    nameAr: 'المؤشرات الأساسية',
    description: 'Core vegetation health and water content indices',
    descriptionAr: 'المؤشرات الأساسية لصحة النبات ومحتوى المياه',
  },
  chlorophyll: {
    id: 'chlorophyll',
    name: 'Chlorophyll & Nitrogen',
    nameAr: 'الكلوروفيل والنيتروجين',
    description: 'Chlorophyll content and nitrogen status assessment',
    descriptionAr: 'تقييم محتوى الكلوروفيل وحالة النيتروجين',
  },
  stress_detection: {
    id: 'stress_detection',
    name: 'Early Stress Detection',
    nameAr: 'كشف الإجهاد المبكر',
    description: 'Early detection of crop stress and anomalies',
    descriptionAr: 'الكشف المبكر عن إجهاد المحاصيل والشذوذ',
  },
  soil_corrected: {
    id: 'soil_corrected',
    name: 'Soil & Atmosphere Corrected',
    nameAr: 'تصحيح التربة والغلاف الجوي',
    description: 'Indices corrected for soil background and atmospheric effects',
    descriptionAr: 'مؤشرات مصححة لتأثيرات التربة والغلاف الجوي',
  },
  pigment: {
    id: 'pigment',
    name: 'Pigment & Senescence',
    nameAr: 'الأصباغ والشيخوخة',
    description: 'Carotenoid, anthocyanin, and senescence detection',
    descriptionAr: 'كشف الكاروتينويد والأنثوسيانين والشيخوخة',
  },
  red_edge: {
    id: 'red_edge',
    name: 'Red Edge & Chlorophyll Enhancement',
    nameAr: 'الحافة الحمراء وتعزيز الكلوروفيل',
    description: 'Advanced red-edge band indices for chlorophyll estimation',
    descriptionAr: 'مؤشرات الحافة الحمراء المتقدمة لتقدير الكلوروفيل',
  },
  water_drought: {
    id: 'water_drought',
    name: 'Water, Drought & Land Cover',
    nameAr: 'المياه والجفاف والغطاء الأرضي',
    description: 'Water body detection, drought assessment, and land cover',
    descriptionAr: 'كشف المسطحات المائية وتقييم الجفاف والغطاء الأرضي',
  },
};

// =============================================================================
// Vegetation Index Configuration
// =============================================================================

export interface VegetationIndexConfig {
  /** Machine key matching VegetationIndex enum */
  key: VegetationIndex;
  /** English display name */
  name: string;
  /** Arabic display name */
  nameAr: string;
  /** English description */
  description: string;
  /** Arabic description */
  descriptionAr: string;
  /** Category grouping */
  category: IndexCategory;
  /** Full value range [min, max] */
  range: [number, number];
  /** Healthy/optimal range for crops [min, max] */
  healthyRange: [number, number];
  /** Unit of measurement (empty string for dimensionless) */
  unit: string;
}

// =============================================================================
// INDEX_CONFIGS - complete configuration for all 41 indices
// =============================================================================

export const INDEX_CONFIGS: Record<VegetationIndex, VegetationIndexConfig> = {
  // ── Basic (6) ──────────────────────────────────────────────────────────────
  [VegetationIndex.NDVI]: {
    key: VegetationIndex.NDVI,
    name: 'Normalized Difference Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المعياري',
    description: 'Overall vegetation health and biomass estimation',
    descriptionAr: 'تقييم صحة الغطاء النباتي والكتلة الحيوية',
    category: 'basic',
    range: [-1, 1],
    healthyRange: [0.6, 0.9],
    unit: '',
  },
  [VegetationIndex.NDWI]: {
    key: VegetationIndex.NDWI,
    name: 'Normalized Difference Water Index',
    nameAr: 'مؤشر الماء المعياري',
    description: 'Water content and irrigation monitoring',
    descriptionAr: 'مراقبة محتوى الماء والري',
    category: 'basic',
    range: [-1, 1],
    healthyRange: [0.2, 0.6],
    unit: '',
  },
  [VegetationIndex.EVI]: {
    key: VegetationIndex.EVI,
    name: 'Enhanced Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المحسّن',
    description: 'High biomass areas with reduced atmospheric effects',
    descriptionAr: 'المناطق ذات الكتلة الحيوية العالية مع تقليل التأثيرات الجوية',
    category: 'basic',
    range: [-1, 1],
    healthyRange: [0.3, 0.8],
    unit: '',
  },
  [VegetationIndex.SAVI]: {
    key: VegetationIndex.SAVI,
    name: 'Soil Adjusted Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المعدّل للتربة',
    description: 'Vegetation index corrected for soil background',
    descriptionAr: 'مؤشر نباتي مصحح لخلفية التربة',
    category: 'basic',
    range: [-1, 1],
    healthyRange: [0.4, 0.8],
    unit: '',
  },
  [VegetationIndex.LAI]: {
    key: VegetationIndex.LAI,
    name: 'Leaf Area Index',
    nameAr: 'مؤشر مساحة الورق',
    description: 'Total one-sided area of leaf tissue per ground surface area',
    descriptionAr: 'إجمالي مساحة الأوراق من جانب واحد لكل وحدة مساحة أرضية',
    category: 'basic',
    range: [0, 8],
    healthyRange: [2, 5],
    unit: 'm\u00B2/m\u00B2',
  },
  [VegetationIndex.NDMI]: {
    key: VegetationIndex.NDMI,
    name: 'Normalized Difference Moisture Index',
    nameAr: 'مؤشر الرطوبة المعياري',
    description: 'Crop water stress detection',
    descriptionAr: 'كشف إجهاد المحاصيل المائي',
    category: 'basic',
    range: [-1, 1],
    healthyRange: [0.2, 0.6],
    unit: '',
  },

  // ── Chlorophyll & Nitrogen (5) ─────────────────────────────────────────────
  [VegetationIndex.NDRE]: {
    key: VegetationIndex.NDRE,
    name: 'Normalized Difference Red Edge',
    nameAr: 'الحافة الحمراء المعيارية',
    description: 'Chlorophyll content in mature crops and nitrogen status',
    descriptionAr: 'محتوى الكلوروفيل في المحاصيل الناضجة وحالة النيتروجين',
    category: 'chlorophyll',
    range: [-1, 1],
    healthyRange: [0.3, 0.7],
    unit: '',
  },
  [VegetationIndex.CVI]: {
    key: VegetationIndex.CVI,
    name: 'Chlorophyll Vegetation Index',
    nameAr: 'مؤشر الكلوروفيل النباتي',
    description: 'Chlorophyll content assessment',
    descriptionAr: 'تقييم محتوى الكلوروفيل',
    category: 'chlorophyll',
    range: [0, 10],
    healthyRange: [2, 5],
    unit: '',
  },
  [VegetationIndex.MCARI]: {
    key: VegetationIndex.MCARI,
    name: 'Modified Chlorophyll Absorption Ratio Index',
    nameAr: 'مؤشر نسبة امتصاص الكلوروفيل المعدّل',
    description: 'Chlorophyll concentration in crops',
    descriptionAr: 'تركيز الكلوروفيل في المحاصيل',
    category: 'chlorophyll',
    range: [0, 1.5],
    healthyRange: [0.3, 1.0],
    unit: '',
  },
  [VegetationIndex.TCARI]: {
    key: VegetationIndex.TCARI,
    name: 'Transformed Chlorophyll Absorption Ratio Index',
    nameAr: 'مؤشر نسبة امتصاص الكلوروفيل المحوّل',
    description: 'Chlorophyll content with soil background resistance',
    descriptionAr: 'محتوى الكلوروفيل مع مقاومة خلفية التربة',
    category: 'chlorophyll',
    range: [0, 3],
    healthyRange: [0.5, 1.5],
    unit: '',
  },
  [VegetationIndex.SIPI]: {
    key: VegetationIndex.SIPI,
    name: 'Structure Insensitive Pigment Index',
    nameAr: 'مؤشر الصبغة غير الحساس للبنية',
    description: 'Pigment composition independent of leaf structure',
    descriptionAr: 'تركيب الأصباغ بشكل مستقل عن بنية الأوراق',
    category: 'chlorophyll',
    range: [0, 2],
    healthyRange: [0.8, 1.2],
    unit: '',
  },

  // ── Early Stress Detection (4) ────────────────────────────────────────────
  [VegetationIndex.GNDVI]: {
    key: VegetationIndex.GNDVI,
    name: 'Green Normalized Difference Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المعياري الأخضر',
    description: 'Nitrogen content and early stress detection',
    descriptionAr: 'محتوى النيتروجين والكشف المبكر عن الإجهاد',
    category: 'stress_detection',
    range: [-1, 1],
    healthyRange: [0.5, 0.8],
    unit: '',
  },
  [VegetationIndex.VARI]: {
    key: VegetationIndex.VARI,
    name: 'Visible Atmospherically Resistant Index',
    nameAr: 'المؤشر المرئي المقاوم للغلاف الجوي',
    description: 'Vegetation fraction using visible bands only',
    descriptionAr: 'نسبة الغطاء النباتي باستخدام النطاقات المرئية فقط',
    category: 'stress_detection',
    range: [-1, 1],
    healthyRange: [0.1, 0.5],
    unit: '',
  },
  [VegetationIndex.GLI]: {
    key: VegetationIndex.GLI,
    name: 'Green Leaf Index',
    nameAr: 'مؤشر الأوراق الخضراء',
    description: 'Green vegetation fraction from visible bands',
    descriptionAr: 'نسبة الغطاء النباتي الأخضر من النطاقات المرئية',
    category: 'stress_detection',
    range: [-1, 1],
    healthyRange: [0.1, 0.4],
    unit: '',
  },
  [VegetationIndex.GRVI]: {
    key: VegetationIndex.GRVI,
    name: 'Green-Red Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي الأخضر-الأحمر',
    description: 'Early stress indicator using green and red bands',
    descriptionAr: 'مؤشر إجهاد مبكر باستخدام النطاقين الأخضر والأحمر',
    category: 'stress_detection',
    range: [-1, 1],
    healthyRange: [0.1, 0.5],
    unit: '',
  },

  // ── Soil & Atmosphere Corrected (3) ───────────────────────────────────────
  [VegetationIndex.MSAVI]: {
    key: VegetationIndex.MSAVI,
    name: 'Modified Soil Adjusted Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المعدّل للتربة المحسّن',
    description: 'Self-adjusting soil factor for sparse vegetation',
    descriptionAr: 'عامل تربة ذاتي التعديل للغطاء النباتي المتفرق',
    category: 'soil_corrected',
    range: [-1, 1],
    healthyRange: [0.3, 0.7],
    unit: '',
  },
  [VegetationIndex.OSAVI]: {
    key: VegetationIndex.OSAVI,
    name: 'Optimized Soil Adjusted Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المعدّل للتربة المُحسّن',
    description: 'Optimized soil adjustment for variable density canopy',
    descriptionAr: 'تعديل محسّن للتربة لكثافة الغطاء المتغيرة',
    category: 'soil_corrected',
    range: [-1, 1],
    healthyRange: [0.4, 0.8],
    unit: '',
  },
  [VegetationIndex.ARVI]: {
    key: VegetationIndex.ARVI,
    name: 'Atmospherically Resistant Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المقاوم للغلاف الجوي',
    description: 'Vegetation index resistant to atmospheric effects',
    descriptionAr: 'مؤشر نباتي مقاوم لتأثيرات الغلاف الجوي',
    category: 'soil_corrected',
    range: [-1, 1],
    healthyRange: [0.3, 0.7],
    unit: '',
  },

  // ── Pigment & Senescence (5) ──────────────────────────────────────────────
  [VegetationIndex.PRI]: {
    key: VegetationIndex.PRI,
    name: 'Photochemical Reflectance Index',
    nameAr: 'مؤشر الانعكاس الكيميائي الضوئي',
    description: 'Light use efficiency and xanthophyll cycle activity',
    descriptionAr: 'كفاءة استخدام الضوء ونشاط دورة الزانثوفيل',
    category: 'pigment',
    range: [-1, 1],
    healthyRange: [-0.05, 0.05],
    unit: '',
  },
  [VegetationIndex.CRI]: {
    key: VegetationIndex.CRI,
    name: 'Carotenoid Reflectance Index',
    nameAr: 'مؤشر انعكاس الكاروتينويد',
    description: 'Carotenoid pigment concentration',
    descriptionAr: 'تركيز صبغة الكاروتينويد',
    category: 'pigment',
    range: [0, 15],
    healthyRange: [1, 6],
    unit: '',
  },
  [VegetationIndex.ARI]: {
    key: VegetationIndex.ARI,
    name: 'Anthocyanin Reflectance Index',
    nameAr: 'مؤشر انعكاس الأنثوسيانين',
    description: 'Anthocyanin pigment for stress and maturity detection',
    descriptionAr: 'صبغة الأنثوسيانين لكشف الإجهاد والنضج',
    category: 'pigment',
    range: [0, 10],
    healthyRange: [0.5, 3],
    unit: '',
  },
  [VegetationIndex.PSRI]: {
    key: VegetationIndex.PSRI,
    name: 'Plant Senescence Reflectance Index',
    nameAr: 'مؤشر انعكاس شيخوخة النبات',
    description: 'Onset and progression of plant senescence',
    descriptionAr: 'بداية وتطور شيخوخة النبات',
    category: 'pigment',
    range: [-1, 1],
    healthyRange: [-0.1, 0.1],
    unit: '',
  },
  [VegetationIndex.REP]: {
    key: VegetationIndex.REP,
    name: 'Red Edge Position',
    nameAr: 'موقع الحافة الحمراء',
    description: 'Spectral position of red edge inflection point',
    descriptionAr: 'الموقع الطيفي لنقطة انعطاف الحافة الحمراء',
    category: 'pigment',
    range: [690, 740],
    healthyRange: [715, 730],
    unit: 'nm',
  },

  // ── Extended Spectral (6) ─────────────────────────────────────────────────
  [VegetationIndex.NBR]: {
    key: VegetationIndex.NBR,
    name: 'Normalized Burn Ratio',
    nameAr: 'نسبة الحرق المعيارية',
    description: 'Fire/drought severity and post-fire recovery',
    descriptionAr: 'شدة الحريق/الجفاف والتعافي بعد الحريق',
    category: 'water_drought',
    range: [-1, 1],
    healthyRange: [0.2, 0.7],
    unit: '',
  },
  [VegetationIndex.EVI2]: {
    key: VegetationIndex.EVI2,
    name: 'Two-Band Enhanced Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المحسّن ثنائي النطاق',
    description: 'EVI approximation without blue band (Landsat compatible)',
    descriptionAr: 'تقريب مؤشر EVI بدون النطاق الأزرق (متوافق مع لاندسات)',
    category: 'basic',
    range: [-1, 1],
    healthyRange: [0.3, 0.8],
    unit: '',
  },
  [VegetationIndex.BSI]: {
    key: VegetationIndex.BSI,
    name: 'Bare Soil Index',
    nameAr: 'مؤشر التربة العارية',
    description: 'Bare soil identification and land degradation',
    descriptionAr: 'تحديد التربة العارية وتدهور الأراضي',
    category: 'soil_corrected',
    range: [-1, 1],
    healthyRange: [-0.3, 0.1],
    unit: '',
  },
  [VegetationIndex.SR]: {
    key: VegetationIndex.SR,
    name: 'Simple Ratio',
    nameAr: 'النسبة البسيطة',
    description: 'Simple NIR/Red ratio for vegetation density',
    descriptionAr: 'نسبة بسيطة بين الأشعة تحت الحمراء القريبة والحمراء لكثافة الغطاء النباتي',
    category: 'basic',
    range: [0, 30],
    healthyRange: [3, 12],
    unit: '',
  },
  [VegetationIndex.CCCI]: {
    key: VegetationIndex.CCCI,
    name: 'Canopy Chlorophyll Content Index',
    nameAr: 'مؤشر محتوى الكلوروفيل في الغطاء',
    description: 'Canopy-level chlorophyll estimation',
    descriptionAr: 'تقدير الكلوروفيل على مستوى الغطاء',
    category: 'chlorophyll',
    range: [-1, 1],
    healthyRange: [0.3, 0.7],
    unit: '',
  },
  [VegetationIndex.MSI]: {
    key: VegetationIndex.MSI,
    name: 'Moisture Stress Index',
    nameAr: 'مؤشر إجهاد الرطوبة',
    description: 'Leaf water content and moisture stress',
    descriptionAr: 'محتوى ماء الأوراق وإجهاد الرطوبة',
    category: 'water_drought',
    range: [0, 4],
    healthyRange: [0.4, 1.0],
    unit: '',
  },

  // ── Red Edge & Chlorophyll Enhancement (6) ────────────────────────────────
  [VegetationIndex.CI_GREEN]: {
    key: VegetationIndex.CI_GREEN,
    name: 'Chlorophyll Index Green',
    nameAr: 'مؤشر الكلوروفيل الأخضر',
    description: 'Chlorophyll content using green band (Gitelson 2003)',
    descriptionAr: 'محتوى الكلوروفيل باستخدام النطاق الأخضر',
    category: 'red_edge',
    range: [0, 15],
    healthyRange: [2, 8],
    unit: '',
  },
  [VegetationIndex.CI_REDEDGE]: {
    key: VegetationIndex.CI_REDEDGE,
    name: 'Chlorophyll Index Red Edge',
    nameAr: 'مؤشر الكلوروفيل للحافة الحمراء',
    description: 'Chlorophyll content using red edge band (Gitelson 2003)',
    descriptionAr: 'محتوى الكلوروفيل باستخدام نطاق الحافة الحمراء',
    category: 'red_edge',
    range: [0, 10],
    healthyRange: [1, 5],
    unit: '',
  },
  [VegetationIndex.IRECI]: {
    key: VegetationIndex.IRECI,
    name: 'Inverted Red Edge Chlorophyll Index',
    nameAr: 'مؤشر الكلوروفيل المقلوب للحافة الحمراء',
    description: 'Chlorophyll estimation via inverted red edge (Frampton 2013)',
    descriptionAr: 'تقدير الكلوروفيل عبر الحافة الحمراء المقلوبة',
    category: 'red_edge',
    range: [0, 8],
    healthyRange: [1, 4],
    unit: '',
  },
  [VegetationIndex.MTCI]: {
    key: VegetationIndex.MTCI,
    name: 'MERIS Terrestrial Chlorophyll Index',
    nameAr: 'مؤشر الكلوروفيل الأرضي لـ MERIS',
    description: 'Chlorophyll content estimation (Dash & Curran 2004)',
    descriptionAr: 'تقدير محتوى الكلوروفيل',
    category: 'red_edge',
    range: [0, 10],
    healthyRange: [1, 5],
    unit: '',
  },
  [VegetationIndex.RENDVI]: {
    key: VegetationIndex.RENDVI,
    name: 'Red Edge NDVI',
    nameAr: 'مؤشر NDVI للحافة الحمراء',
    description: 'NDVI using red edge bands for chlorophyll sensitivity',
    descriptionAr: 'مؤشر NDVI باستخدام نطاقات الحافة الحمراء لحساسية الكلوروفيل',
    category: 'red_edge',
    range: [-1, 1],
    healthyRange: [0.2, 0.6],
    unit: '',
  },
  [VegetationIndex.WDRVI]: {
    key: VegetationIndex.WDRVI,
    name: 'Wide Dynamic Range Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي واسع النطاق الديناميكي',
    description: 'Linearized NDVI for high biomass areas (Gitelson 2004)',
    descriptionAr: 'مؤشر NDVI الخطي للمناطق ذات الكتلة الحيوية العالية',
    category: 'red_edge',
    range: [-1, 1],
    healthyRange: [0.1, 0.6],
    unit: '',
  },

  // ── Water, Drought & Land Cover (6) ───────────────────────────────────────
  [VegetationIndex.MNDWI]: {
    key: VegetationIndex.MNDWI,
    name: 'Modified Normalized Difference Water Index',
    nameAr: 'مؤشر الماء المعياري المعدّل',
    description: 'Water body detection reducing built-up noise (Xu 2006)',
    descriptionAr: 'كشف المسطحات المائية مع تقليل ضوضاء المباني',
    category: 'water_drought',
    range: [-1, 1],
    healthyRange: [-0.3, 0.3],
    unit: '',
  },
  [VegetationIndex.NBR2]: {
    key: VegetationIndex.NBR2,
    name: 'Normalized Burn Ratio 2',
    nameAr: 'نسبة الحرق المعيارية 2',
    description: 'Burn severity using SWIR bands',
    descriptionAr: 'شدة الحرق باستخدام نطاقات SWIR',
    category: 'water_drought',
    range: [-1, 1],
    healthyRange: [0.1, 0.5],
    unit: '',
  },
  [VegetationIndex.NDBI]: {
    key: VegetationIndex.NDBI,
    name: 'Normalized Difference Built-up Index',
    nameAr: 'مؤشر المناطق المبنية المعياري',
    description: 'Urban and built-up area identification (Zha 2003)',
    descriptionAr: 'تحديد المناطق الحضرية والمبنية',
    category: 'water_drought',
    range: [-1, 1],
    healthyRange: [-0.3, 0.0],
    unit: '',
  },
  [VegetationIndex.DVI]: {
    key: VegetationIndex.DVI,
    name: 'Difference Vegetation Index',
    nameAr: 'مؤشر الفرق النباتي',
    description: 'Simple difference of NIR and Red bands (Richardson 1977)',
    descriptionAr: 'الفرق البسيط بين نطاقي الأشعة تحت الحمراء القريبة والحمراء',
    category: 'water_drought',
    range: [-1, 1],
    healthyRange: [0.2, 0.6],
    unit: '',
  },
  [VegetationIndex.GDVI]: {
    key: VegetationIndex.GDVI,
    name: 'Green Difference Vegetation Index',
    nameAr: 'مؤشر الفرق النباتي الأخضر',
    description: 'Difference of NIR and Green bands for vegetation',
    descriptionAr: 'الفرق بين نطاقي الأشعة تحت الحمراء القريبة والأخضر للغطاء النباتي',
    category: 'water_drought',
    range: [-1, 1],
    healthyRange: [0.2, 0.6],
    unit: '',
  },
  [VegetationIndex.TSAVI]: {
    key: VegetationIndex.TSAVI,
    name: 'Transformed Soil Adjusted Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المعدّل للتربة المحوّل',
    description: 'Soil-adjusted index using soil line parameters (Baret & Guyot 1991)',
    descriptionAr: 'مؤشر معدّل للتربة باستخدام معاملات خط التربة',
    category: 'soil_corrected',
    range: [-1, 1],
    healthyRange: [0.2, 0.6],
    unit: '',
  },
};

// =============================================================================
// Helper: indices by category
// =============================================================================

export function getIndicesByCategory(category: IndexCategory): VegetationIndexConfig[] {
  return Object.values(INDEX_CONFIGS).filter((cfg) => cfg.category === category);
}

export function getAllCategories(): IndexCategory[] {
  return Object.keys(INDEX_CATEGORIES) as IndexCategory[];
}

// =============================================================================
// API Response Interfaces
// =============================================================================

/** Single index value within a response */
export interface IndexValue {
  name: string;
  value: number;
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  interpretation: string;
  interpretationAr: string;
  confidence: number;
}

/** Response from GET /api/v1/indices/{fieldId} */
export interface IndicesResult {
  fieldId: string;
  fieldName?: string;
  date: string;
  source: 'sentinel-2' | 'landsat' | 'modis';
  cloudCoverage: number;
  indices: Record<string, IndexValue>;
}

/** Response from GET /api/v1/indices/{fieldId}/{indexName} */
export interface SingleIndexResult {
  fieldId: string;
  indexName: string;
  date: string;
  value: number;
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  interpretation: string;
  interpretationAr: string;
  confidence: number;
  thresholds: Record<string, number>;
}

/** Response from GET /api/v1/indices/interpret */
export interface IndicesInterpretation {
  fieldId: string;
  date: string;
  overallHealth: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  overallHealthAr: string;
  summary: string;
  summaryAr: string;
  indices: Record<string, IndexValue>;
  recommendations: Array<{
    type: string;
    priority: 'critical' | 'warning' | 'advisory' | 'informational';
    message: string;
    messageAr: string;
  }>;
}

/** Single time-series data point for any index */
export interface IndexTimeSeriesPoint {
  date: string;
  value: number;
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
}

/** Response from GET /api/v1/indices/{fieldId}/{indexName}/timeseries */
export interface IndexTimeSeries {
  fieldId: string;
  indexName: string;
  data: IndexTimeSeriesPoint[];
  trend: 'improving' | 'stable' | 'declining';
  anomalies: Array<{
    date: string;
    type: 'sudden_drop' | 'unusual_peak';
    severity: 'low' | 'medium' | 'high';
  }>;
}
