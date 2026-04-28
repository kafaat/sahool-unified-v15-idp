/**
 * Phase 2 — Per-Index Semantics Configuration
 * تكوين الدلالات لكل مؤشر طيفي على حدة
 *
 * Critical: NDVI ≠ NDWI ≠ LAI
 * Each index has its own:
 *   - value range
 *   - health zone thresholds
 *   - bilingual health labels
 *   - colormap stops (scientifically correct per-index)
 *   - agronomic interpretation
 *
 * Without this, a user showing NDWI with NDVI health labels
 * will interpret 0.3 as "moderate vegetation" when it actually
 * means "good water content" — a scientifically incorrect reading.
 */

// =============================================================================
// Types
// =============================================================================

export interface ColorStop {
  /** Value at this stop (in index native units) */
  value: number;
  /** CSS color string */
  color: string;
}

export interface HealthZone {
  /** Minimum value for this zone (inclusive) */
  min: number;
  /** Maximum value for this zone (exclusive, last zone = Infinity) */
  max: number;
  /** English label */
  label: string;
  /** Arabic label */
  labelAr: string;
  /** Tailwind / hex badge color */
  color: string;
  /** Agricultural interpretation (en) */
  interpretation: string;
  /** Agricultural interpretation (ar) */
  interpretationAr: string;
}

export interface IndexSemantics {
  /** Spectral index key — must match backend VegetationIndex enum */
  index: string;
  /** Short English display name */
  displayName: string;
  /** Short Arabic display name */
  displayNameAr: string;
  /** What the index measures (en) */
  measures: string;
  /** What the index measures (ar) */
  measuresAr: string;
  /** Unit shown in legend ('' = dimensionless) */
  unit: string;
  /** Full value range [min, max] */
  range: [number, number];
  /** Color map stops (ascending by value) */
  colorStops: ColorStop[];
  /** Health zones (ascending by min) */
  healthZones: HealthZone[];
  /** Agronomic interpretation guidance (en) */
  guidance: string;
  /** Agronomic interpretation guidance (ar) */
  guidanceAr: string;
  /** Recommended growth stages where this index is most informative */
  bestForStages: string[];
}

// =============================================================================
// Per-Index Semantics — production-grade, agronomically correct
// =============================================================================

export const INDEX_SEMANTICS: Record<string, IndexSemantics> = {

  // ───────────────────────────────────────────────────────────────────────────
  ndvi: {
    index: 'ndvi',
    displayName: 'NDVI',
    displayNameAr: 'مؤشر الغطاء النباتي',
    measures: 'Vegetation density & biomass',
    measuresAr: 'كثافة الغطاء النباتي والكتلة الحيوية',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#8B4513' }, // bare soil
      { value: 0.0,  color: '#CC3300' }, // no vegetation
      { value: 0.15, color: '#FF6600' },
      { value: 0.25, color: '#FFA500' },
      { value: 0.35, color: '#FFDD00' },
      { value: 0.45, color: '#AAEE00' },
      { value: 0.55, color: '#55CC00' },
      { value: 0.70, color: '#00AA00' },
      { value: 0.85, color: '#006600' }, // dense healthy vegetation
    ],
    healthZones: [
      {
        min: -1, max: 0.1,
        label: 'Bare / No crop',
        labelAr: 'تربة عارية / لا محصول',
        color: '#8B4513',
        interpretation: 'No crop detected or harvested field',
        interpretationAr: 'لا يوجد محصول أو الحقل محصود',
      },
      {
        min: 0.1, max: 0.2,
        label: 'Critical',
        labelAr: 'حرج',
        color: '#DC2626',
        interpretation: 'Severe stress or early germination',
        interpretationAr: 'إجهاد حاد أو إنبات مبكر',
      },
      {
        min: 0.2, max: 0.35,
        label: 'Poor',
        labelAr: 'ضعيف',
        color: '#EA580C',
        interpretation: 'Moderate stress; check irrigation and nutrition',
        interpretationAr: 'إجهاد معتدل؛ تحقق من الري والتغذية',
      },
      {
        min: 0.35, max: 0.5,
        label: 'Moderate',
        labelAr: 'متوسط',
        color: '#CA8A04',
        interpretation: 'Below optimal; monitor closely',
        interpretationAr: 'دون المستوى الأمثل؛ راقب عن كثب',
      },
      {
        min: 0.5, max: 0.65,
        label: 'Good',
        labelAr: 'جيد',
        color: '#16A34A',
        interpretation: 'Healthy crop; normal agronomic management',
        interpretationAr: 'محصول صحي؛ إدارة زراعية طبيعية',
      },
      {
        min: 0.65, max: 1.01,
        label: 'Excellent',
        labelAr: 'ممتاز',
        color: '#15803D',
        interpretation: 'Dense healthy canopy; optimal growth',
        interpretationAr: 'مظلة كثيفة وصحية؛ نمو أمثل',
      },
    ],
    guidance: 'NDVI measures overall vegetation density. Values above 0.5 indicate a healthy growing crop. Values below 0.3 during active growth signal stress requiring investigation.',
    guidanceAr: 'يقيس NDVI كثافة الغطاء النباتي. القيم فوق 0.5 تدل على محصول صحي نامٍ. القيم دون 0.3 خلال النمو النشط تشير إلى إجهاد يستلزم التحقيق.',
    bestForStages: ['tillering', 'stem_elongation', 'booting', 'vegetative'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  ndwi: {
    index: 'ndwi',
    displayName: 'NDWI',
    displayNameAr: 'مؤشر المياه',
    measures: 'Canopy water content & irrigation status',
    measuresAr: 'محتوى الماء في المظلة وحالة الري',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#8B2500' }, // severe drought
      { value: -0.2, color: '#C25A00' },
      { value: -0.1, color: '#E8A02E' },
      { value: 0.0,  color: '#F5E26A' }, // neutral
      { value: 0.1,  color: '#A8D6E8' },
      { value: 0.25, color: '#4BA3C3' },
      { value: 0.5,  color: '#1565A0' }, // high water content
    ],
    healthZones: [
      {
        min: -1, max: -0.1,
        label: 'Drought / Dry Stress',
        labelAr: 'جفاف / إجهاد جفاف',
        color: '#DC2626',
        interpretation: 'Severe water deficit in canopy; immediate irrigation required',
        interpretationAr: 'عجز مائي حاد في المظلة؛ الري الفوري مطلوب',
      },
      {
        min: -0.1, max: 0.1,
        label: 'Low Water Content',
        labelAr: 'محتوى ماء منخفض',
        color: '#EA580C',
        interpretation: 'Below optimal water; schedule irrigation soon',
        interpretationAr: 'ماء أقل من الأمثل؛ جدول الري قريبًا',
      },
      {
        min: 0.1, max: 0.25,
        label: 'Adequate',
        labelAr: 'كافٍ',
        color: '#16A34A',
        interpretation: 'Adequate canopy water content; maintain current irrigation',
        interpretationAr: 'محتوى ماء كافٍ في المظلة؛ حافظ على الري الحالي',
      },
      {
        min: 0.25, max: 1.01,
        label: 'High Water Content',
        labelAr: 'محتوى ماء مرتفع',
        color: '#2563EB',
        interpretation: 'High water; check for over-irrigation or waterlogging',
        interpretationAr: 'ماء مرتفع؛ تحقق من الإفراط في الري أو التشبع',
      },
    ],
    guidance: 'NDWI measures leaf water content, NOT vegetation density. Do NOT compare NDWI values with NDVI thresholds. Values above 0.1 indicate adequate irrigation; values below -0.1 indicate drought stress.',
    guidanceAr: 'يقيس NDWI محتوى الماء في الأوراق وليس كثافة النبات. لا تقارن قيم NDWI بعتبات NDVI. القيم فوق 0.1 تدل على ري كافٍ؛ القيم دون -0.1 تدل على إجهاد جفاف.',
    bestForStages: ['flowering', 'fruit_dev', 'ripening', 'stem_elongation'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  evi: {
    index: 'evi',
    displayName: 'EVI',
    displayNameAr: 'مؤشر الغطاء المحسّن',
    measures: 'Vegetation with reduced atmospheric & soil influence',
    measuresAr: 'الغطاء النباتي مع تقليل تأثيرات التربة والغلاف الجوي',
    unit: '',
    range: [-0.2, 1],
    colorStops: [
      { value: -0.2, color: '#8B4513' },
      { value: 0.0,  color: '#CC3300' },
      { value: 0.1,  color: '#FF7700' },
      { value: 0.2,  color: '#FFCC00' },
      { value: 0.35, color: '#99DD00' },
      { value: 0.5,  color: '#22BB00' },
      { value: 0.7,  color: '#006600' },
    ],
    healthZones: [
      {
        min: -0.2, max: 0.1,
        label: 'Bare / Stressed',
        labelAr: 'عارٍ / متضايق',
        color: '#DC2626',
        interpretation: 'Little or no canopy; bare soil dominates',
        interpretationAr: 'مظلة قليلة أو معدومة؛ التربة العارية مهيمنة',
      },
      {
        min: 0.1, max: 0.25,
        label: 'Sparse',
        labelAr: 'متفرق',
        color: '#EA580C',
        interpretation: 'Sparse canopy; consider causes (drought, disease, pests)',
        interpretationAr: 'مظلة متفرقة؛ ابحث عن الأسباب (جفاف، مرض، آفات)',
      },
      {
        min: 0.25, max: 0.45,
        label: 'Moderate',
        labelAr: 'متوسط',
        color: '#CA8A04',
        interpretation: 'Moderate canopy; below seasonal average',
        interpretationAr: 'مظلة متوسطة؛ دون المتوسط الموسمي',
      },
      {
        min: 0.45, max: 1.01,
        label: 'Dense / Healthy',
        labelAr: 'كثيف / صحي',
        color: '#15803D',
        interpretation: 'Dense healthy canopy; optimal growth',
        interpretationAr: 'مظلة كثيفة وصحية؛ نمو أمثل',
      },
    ],
    guidance: 'EVI is more sensitive than NDVI in high-biomass regions and reduces soil and atmospheric noise. Use EVI over NDVI when crop canopy is very dense (LAI > 3) or in arid areas with bright soils.',
    guidanceAr: 'EVI أكثر حساسية من NDVI في المناطق ذات الكتلة الحيوية العالية ويقلل ضوضاء التربة والغلاف الجوي. استخدم EVI عوضًا عن NDVI عندما تكون المظلة كثيفة جدًا (LAI > 3) أو في المناطق الجافة ذات التربة الفاتحة.',
    bestForStages: ['tillering', 'stem_elongation', 'booting', 'vegetative'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  savi: {
    index: 'savi',
    displayName: 'SAVI',
    displayNameAr: 'مؤشر التربة المعدّل',
    measures: 'Vegetation adjusted for soil background',
    measuresAr: 'الغطاء النباتي مع تعديل خلفية التربة',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#8B4513' },
      { value: 0.0,  color: '#CC3300' },
      { value: 0.1,  color: '#FF7700' },
      { value: 0.25, color: '#FFCC00' },
      { value: 0.4,  color: '#99DD00' },
      { value: 0.6,  color: '#22BB00' },
      { value: 0.8,  color: '#006600' },
    ],
    healthZones: [
      {
        min: -1, max: 0.1,
        label: 'Bare / No crop',
        labelAr: 'تربة عارية / لا محصول',
        color: '#DC2626',
        interpretation: 'Dominated by exposed soil; pre-emergence or harvested',
        interpretationAr: 'تهيمن عليه التربة المكشوفة؛ قبل الإنبات أو محصود',
      },
      {
        min: 0.1, max: 0.3,
        label: 'Sparse',
        labelAr: 'متفرق',
        color: '#EA580C',
        interpretation: 'Early growth or stressed sparse canopy',
        interpretationAr: 'نمو مبكر أو مظلة متفرقة متضايقة',
      },
      {
        min: 0.3, max: 0.5,
        label: 'Moderate',
        labelAr: 'متوسط',
        color: '#CA8A04',
        interpretation: 'Developing crop; soil still visible between rows',
        interpretationAr: 'محصول في طور النمو؛ التربة لا تزال مرئية بين الصفوف',
      },
      {
        min: 0.5, max: 1.01,
        label: 'Good to Dense',
        labelAr: 'جيد إلى كثيف',
        color: '#15803D',
        interpretation: 'Full or near-full canopy closure; healthy growth',
        interpretationAr: 'إغلاق كامل أو شبه كامل للمظلة؛ نمو صحي',
      },
    ],
    guidance: 'SAVI is optimised for sparse vegetation in semi-arid soils (L factor = 0.5). Use SAVI instead of NDVI during early growth stages when soil background is bright and dominant.',
    guidanceAr: 'صُمِّم SAVI للغطاء النباتي المتفرق في التربة شبه الجافة (معامل L = 0.5). استخدم SAVI بدلاً من NDVI في المراحل المبكرة من النمو عندما تكون التربة فاتحة ومهيمنة.',
    bestForStages: ['germination', 'emergence', 'leaf_dev'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  ndre: {
    index: 'ndre',
    displayName: 'NDRE',
    displayNameAr: 'مؤشر الحافة الحمراء',
    measures: 'Chlorophyll content & nitrogen status',
    measuresAr: 'محتوى الكلوروفيل وحالة النيتروجين',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#7C3AED' }, // very low chlorophyll (purple)
      { value: 0.0,  color: '#A855F7' },
      { value: 0.1,  color: '#EC4899' },
      { value: 0.2,  color: '#F97316' },
      { value: 0.3,  color: '#EAB308' },
      { value: 0.45, color: '#84CC16' },
      { value: 0.6,  color: '#16A34A' }, // high chlorophyll (dark green)
    ],
    healthZones: [
      {
        min: -1, max: 0.1,
        label: 'Severe N Deficiency',
        labelAr: 'نقص نيتروجين حاد',
        color: '#DC2626',
        interpretation: 'Severe chlorophyll deficiency; urgent nitrogen application needed',
        interpretationAr: 'نقص حاد في الكلوروفيل؛ التسميد النيتروجيني العاجل ضروري',
      },
      {
        min: 0.1, max: 0.2,
        label: 'N Deficient',
        labelAr: 'ناقص نيتروجين',
        color: '#EA580C',
        interpretation: 'Below-optimal chlorophyll; apply nitrogen fertiliser',
        interpretationAr: 'كلوروفيل دون الأمثل؛ أضف سماد نيتروجيني',
      },
      {
        min: 0.2, max: 0.35,
        label: 'Adequate',
        labelAr: 'كافٍ',
        color: '#CA8A04',
        interpretation: 'Adequate chlorophyll; monitor for subtle decline',
        interpretationAr: 'كلوروفيل كافٍ؛ راقب الانخفاض الطفيف',
      },
      {
        min: 0.35, max: 1.01,
        label: 'Good N Status',
        labelAr: 'حالة نيتروجين جيدة',
        color: '#15803D',
        interpretation: 'Good nitrogen and chlorophyll status; no action needed',
        interpretationAr: 'حالة نيتروجين وكلوروفيل جيدة؛ لا حاجة لأي إجراء',
      },
    ],
    guidance: 'NDRE uses the red-edge band (705–745 nm) to detect chlorophyll concentration before NDVI shows symptoms. NDRE saturates later than NDVI in dense canopies, making it the preferred index for nitrogen management in wheat and date palms.',
    guidanceAr: 'يستخدم NDRE نطاق الحافة الحمراء (705–745 نانومتر) للكشف عن تركيز الكلوروفيل قبل ظهور الأعراض في NDVI. يتشبع NDRE لاحقاً من NDVI في المظلات الكثيفة، مما يجعله المؤشر المفضل لإدارة النيتروجين في القمح ونخيل التمر.',
    bestForStages: ['tillering', 'stem_elongation', 'booting', 'flowering'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  lai: {
    index: 'lai',
    displayName: 'LAI',
    displayNameAr: 'مؤشر مساحة الورقة',
    measures: 'Leaf Area Index (m²/m²)',
    measuresAr: 'مؤشر مساحة الورقة (م²/م²)',
    unit: 'm²/m²',
    range: [0, 8],
    colorStops: [
      { value: 0.0, color: '#FFFDE7' }, // bare
      { value: 0.5, color: '#DCEDC8' },
      { value: 1.0, color: '#AED581' },
      { value: 2.0, color: '#7CB342' },
      { value: 3.0, color: '#558B2F' },
      { value: 5.0, color: '#2E7D32' },
      { value: 8.0, color: '#1B5E20' }, // very dense
    ],
    healthZones: [
      {
        min: 0, max: 0.5,
        label: 'Bare / Germinating',
        labelAr: 'عارٍ / إنبات',
        color: '#78716C',
        interpretation: 'Pre-emergence or very early stage; no canopy intercept',
        interpretationAr: 'قبل الإنبات أو مرحلة مبكرة جدًا؛ لا اعتراض مظلة',
      },
      {
        min: 0.5, max: 1.5,
        label: 'Sparse Canopy',
        labelAr: 'مظلة متفرقة',
        color: '#EA580C',
        interpretation: 'Low leaf area; crop establishing or stressed',
        interpretationAr: 'مساحة أوراق منخفضة؛ المحصول في طور التأسيس أو متضايق',
      },
      {
        min: 1.5, max: 3.0,
        label: 'Developing',
        labelAr: 'في طور النمو',
        color: '#CA8A04',
        interpretation: 'Crop developing well; monitor irrigation and nutrition',
        interpretationAr: 'المحصول ينمو جيدًا؛ راقب الري والتغذية',
      },
      {
        min: 3.0, max: 5.0,
        label: 'Full Canopy',
        labelAr: 'مظلة كاملة',
        color: '#16A34A',
        interpretation: 'Full canopy closure; optimal light interception',
        interpretationAr: 'إغلاق مظلة كامل؛ اعتراض ضوء أمثل',
      },
      {
        min: 5.0, max: Infinity,
        label: 'Very Dense',
        labelAr: 'كثيف جدًا',
        color: '#15803D',
        interpretation: 'Very dense canopy; typical for forestry or mature palm',
        interpretationAr: 'مظلة كثيفة جدًا؛ نموذجية للغابات أو النخيل الناضج',
      },
    ],
    guidance: 'LAI (Leaf Area Index) is NOT dimensionless — it measures m² of leaf per m² of ground. A wheat crop at peak needs LAI ~4–6. Date palms reach LAI 2–4. Do NOT compare LAI values with NDVI values — they have completely different scales.',
    guidanceAr: 'LAI (مؤشر مساحة الورقة) ليس بلا أبعاد — يقيس م² من الأوراق لكل م² من الأرض. يحتاج محصول القمح عند الذروة إلى LAI ~4–6. يصل نخيل التمر إلى LAI 2–4. لا تقارن قيم LAI بقيم NDVI — لهما مقاييس مختلفة تمامًا.',
    bestForStages: ['tillering', 'stem_elongation', 'booting', 'leaf_dev'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  gndvi: {
    index: 'gndvi',
    displayName: 'GNDVI',
    displayNameAr: 'مؤشر الأخضر للنبات',
    measures: 'Early nitrogen stress & canopy greenness',
    measuresAr: 'الإجهاد النيتروجيني المبكر وخضرة المظلة',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#8B4513' },
      { value: 0.0,  color: '#CC3300' },
      { value: 0.2,  color: '#FFA500' },
      { value: 0.35, color: '#CCEE00' },
      { value: 0.5,  color: '#44BB00' },
      { value: 0.7,  color: '#005500' },
    ],
    healthZones: [
      {
        min: -1, max: 0.2,
        label: 'Stressed / Deficient',
        labelAr: 'متضايق / ناقص',
        color: '#DC2626',
        interpretation: 'Nitrogen or chlorophyll deficiency; early intervention recommended',
        interpretationAr: 'نقص نيتروجين أو كلوروفيل؛ التدخل المبكر موصى به',
      },
      {
        min: 0.2, max: 0.4,
        label: 'Suboptimal',
        labelAr: 'دون الأمثل',
        color: '#CA8A04',
        interpretation: 'Below optimal greenness; likely N stress',
        interpretationAr: 'خضرة دون الأمثل؛ على الأرجح إجهاد نيتروجيني',
      },
      {
        min: 0.4, max: 1.01,
        label: 'Healthy',
        labelAr: 'صحي',
        color: '#15803D',
        interpretation: 'Good canopy greenness and nitrogen status',
        interpretationAr: 'خضرة مظلة جيدة وحالة نيتروجين جيدة',
      },
    ],
    guidance: 'GNDVI uses the green band instead of red, making it more sensitive to chlorophyll concentration and N status in early growth stages. GNDVI detects N deficiency 7–10 days earlier than NDVI.',
    guidanceAr: 'يستخدم GNDVI النطاق الأخضر بدلاً من الأحمر، مما يجعله أكثر حساسية لتركيز الكلوروفيل وحالة N في مراحل النمو المبكرة. يكشف GNDVI عن نقص N قبل 7–10 أيام من NDVI.',
    bestForStages: ['emergence', 'leaf_dev', 'tillering'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  ndmi: {
    index: 'ndmi',
    displayName: 'NDMI',
    displayNameAr: 'مؤشر رطوبة النبات',
    measures: 'Crop moisture & drought stress',
    measuresAr: 'رطوبة المحصول وإجهاد الجفاف',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#7C2D12' }, // extreme drought
      { value: -0.3, color: '#B45309' },
      { value: -0.1, color: '#D97706' },
      { value: 0.0,  color: '#FDE68A' },
      { value: 0.1,  color: '#6EE7B7' },
      { value: 0.3,  color: '#0D9488' },
      { value: 0.6,  color: '#0E7490' }, // high moisture
    ],
    healthZones: [
      {
        min: -1, max: -0.1,
        label: 'Drought Stress',
        labelAr: 'إجهاد جفاف',
        color: '#DC2626',
        interpretation: 'Severe crop moisture deficit; urgent irrigation required',
        interpretationAr: 'عجز حاد في رطوبة المحصول؛ الري العاجل ضروري',
      },
      {
        min: -0.1, max: 0.1,
        label: 'Moisture Deficit',
        labelAr: 'عجز رطوبة',
        color: '#D97706',
        interpretation: 'Below-optimal moisture; schedule irrigation',
        interpretationAr: 'رطوبة دون الأمثل؛ جدول الري',
      },
      {
        min: 0.1, max: 0.4,
        label: 'Well Watered',
        labelAr: 'مروي جيدًا',
        color: '#16A34A',
        interpretation: 'Good crop moisture content; maintain irrigation schedule',
        interpretationAr: 'محتوى رطوبة المحصول جيد؛ حافظ على جدول الري',
      },
      {
        min: 0.4, max: 1.01,
        label: 'High Moisture',
        labelAr: 'رطوبة مرتفعة',
        color: '#0E7490',
        interpretation: 'High moisture; monitor for waterlogging or over-irrigation',
        interpretationAr: 'رطوبة مرتفعة؛ راقب التشبع أو الإفراط في الري',
      },
    ],
    guidance: 'NDMI uses NIR and SWIR bands to measure moisture in the leaf structure itself, not just the canopy water (unlike NDWI). Use NDMI to detect drought stress 5–7 days before NDWI shows symptoms.',
    guidanceAr: 'يستخدم NDMI نطاقي NIR وSWIR لقياس الرطوبة في بنية الأوراق نفسها، وليس فقط ماء المظلة (على عكس NDWI). استخدم NDMI للكشف عن إجهاد الجفاف قبل 5–7 أيام من ظهور الأعراض في NDWI.',
    bestForStages: ['stem_elongation', 'flowering', 'fruit_dev'],
  },

  // ───────────────────────────────────────────────────────────────────────────
  msavi: {
    index: 'msavi',
    displayName: 'MSAVI',
    displayNameAr: 'مؤشر التربة المعدّل الديناميكي',
    measures: 'Vegetation in sparse / arid fields (dynamic soil factor)',
    measuresAr: 'الغطاء النباتي في الحقول المتفرقة / الجافة (معامل تربة ديناميكي)',
    unit: '',
    range: [-1, 1],
    colorStops: [
      { value: -1.0, color: '#8B4513' },
      { value: 0.0,  color: '#CC3300' },
      { value: 0.15, color: '#FF7700' },
      { value: 0.3,  color: '#FFCC00' },
      { value: 0.5,  color: '#99DD00' },
      { value: 0.7,  color: '#006600' },
    ],
    healthZones: [
      {
        min: -1, max: 0.15,
        label: 'Bare / Very Sparse',
        labelAr: 'عارٍ / متفرق جدًا',
        color: '#DC2626',
        interpretation: 'Soil dominated; minimal vegetation present',
        interpretationAr: 'تهيمن التربة؛ غطاء نباتي ضئيل',
      },
      {
        min: 0.15, max: 0.35,
        label: 'Sparse',
        labelAr: 'متفرق',
        color: '#EA580C',
        interpretation: 'Early crop establishment in arid soil',
        interpretationAr: 'تأسيس مبكر للمحصول في تربة جافة',
      },
      {
        min: 0.35, max: 0.6,
        label: 'Developing',
        labelAr: 'في طور النمو',
        color: '#CA8A04',
        interpretation: 'Crop developing; MSAVI more accurate than NDVI here',
        interpretationAr: 'المحصول ينمو؛ MSAVI أدق من NDVI هنا',
      },
      {
        min: 0.6, max: 1.01,
        label: 'Dense / Healthy',
        labelAr: 'كثيف / صحي',
        color: '#15803D',
        interpretation: 'Full canopy; MSAVI converges with NDVI at high LAI',
        interpretationAr: 'مظلة كاملة؛ يتقارب MSAVI مع NDVI عند LAI مرتفع',
      },
    ],
    guidance: 'MSAVI uses a dynamic soil-line factor instead of the fixed L=0.5 in SAVI. It is the most accurate index for early-stage crops in bright arid soils where NDVI and SAVI tend to overestimate stress.',
    guidanceAr: 'يستخدم MSAVI معامل خط تربة ديناميكيًا بدلاً من L=0.5 الثابت في SAVI. إنه المؤشر الأدق لمراحل المحاصيل المبكرة في التربة الجافة الفاتحة حيث يميل NDVI وSAVI إلى المبالغة في تقدير الإجهاد.',
    bestForStages: ['germination', 'emergence', 'leaf_dev'],
  },
};

// =============================================================================
// Helper utilities
// =============================================================================

/**
 * Get semantics for an index, falling back to NDVI semantics if not found.
 * هذا fallback آمن — يمنع crash عند تمرير مؤشر غير معرّف.
 */
export function getIndexSemantics(index: string): IndexSemantics {
  return INDEX_SEMANTICS[index.toLowerCase()] ?? INDEX_SEMANTICS.ndvi;
}

/**
 * Given an index value, find the matching health zone.
 * إيجاد منطقة الصحة المطابقة لقيمة مؤشر معينة.
 */
export function getHealthZone(index: string, value: number): HealthZone | null {
  const semantics = getIndexSemantics(index);
  return (
    semantics.healthZones.find((zone) => value >= zone.min && value < zone.max) ??
    semantics.healthZones[semantics.healthZones.length - 1] ??
    null
  );
}

/**
 * Interpolate a CSS hex color from color stops for a given value.
 * استيفاء لون CSS من محطات الألوان لقيمة معينة.
 */
export function interpolateColor(index: string, value: number): string {
  const { colorStops } = getIndexSemantics(index);
  if (!colorStops.length) return '#888888';

  if (value <= colorStops[0].value) return colorStops[0].color;
  if (value >= colorStops[colorStops.length - 1].value) return colorStops[colorStops.length - 1].color;

  for (let i = 0; i < colorStops.length - 1; i++) {
    const lo = colorStops[i];
    const hi = colorStops[i + 1];
    if (value >= lo.value && value <= hi.value) {
      const t = (value - lo.value) / (hi.value - lo.value);
      return _blendHex(lo.color, hi.color, t);
    }
  }
  return colorStops[0].color;
}

/** Blend two hex colors by t ∈ [0,1] */
function _blendHex(a: string, b: string, t: number): string {
  const pa = _parseHex(a);
  const pb = _parseHex(b);
  const r = Math.round(pa[0] + (pb[0] - pa[0]) * t);
  const g = Math.round(pa[1] + (pb[1] - pa[1]) * t);
  const bl = Math.round(pa[2] + (pb[2] - pa[2]) * t);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${bl.toString(16).padStart(2, '0')}`;
}

function _parseHex(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

/**
 * List of indices supported by the index-map raster endpoint.
 * قائمة المؤشرات المدعومة لنقطة نهاية خريطة الراستر.
 */
export const MAP_SUPPORTED_INDICES = Object.keys(INDEX_SEMANTICS) as (keyof typeof INDEX_SEMANTICS)[];
