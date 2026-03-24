/**
 * Crop Health Feature - Mock Data (Development Fallback)
 * بيانات وهمية لصحة المحصول
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { HealthSummary, HealthRecord, Disease, DiseaseAlert } from './types';

export const MOCK_HEALTH_SUMMARY: HealthSummary = {
  totalFields: 5,
  healthyFields: 3,
  atRiskFields: 1,
  diseasedFields: 1,
  criticalFields: 0,
  avgHealthScore: 78,
  recentDiagnoses: 3,
  pendingTreatments: 2,
  topDiseases: [
    {
      disease: {
        id: 'disease-1',
        name: 'Wheat Rust',
        nameAr: 'صدأ القمح',
        category: 'fungal',
        description: 'A common fungal disease affecting wheat crops',
        descriptionAr: 'مرض فطري شائع يصيب محاصيل القمح',
        symptoms: ['Orange-red pustules on leaves', 'Yellow spots'],
        symptomsAr: ['بثور برتقالية حمراء على الأوراق', 'بقع صفراء'],
        causes: ['Fungal spores', 'High humidity'],
        causesAr: ['جراثيم فطرية', 'رطوبة عالية'],
        affectedCrops: ['Wheat', 'Barley'],
        affectedCropsAr: ['قمح', 'شعير'],
        severity: 'medium',
        prevalence: 35,
      },
      affectedFields: 2,
    },
  ],
};

export const MOCK_HEALTH_RECORDS: HealthRecord[] = [
  {
    id: 'record-1',
    fieldId: '1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    date: new Date().toISOString(),
    healthScore: 85,
    status: 'healthy',
    observations: 'Crop is growing well with no visible issues',
    observationsAr: 'المحصول ينمو بشكل جيد دون مشاكل ظاهرة',
  },
  {
    id: 'record-2',
    fieldId: '2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    cropType: 'Corn',
    cropTypeAr: 'ذرة',
    date: new Date().toISOString(),
    healthScore: 65,
    status: 'at_risk',
    observations: 'Some yellowing observed on lower leaves',
    observationsAr: 'لوحظ اصفرار في الأوراق السفلية',
    issues: [
      {
        type: 'Nutrient Deficiency',
        typeAr: 'نقص المغذيات',
        severity: 'low',
        description: 'Possible nitrogen deficiency',
        descriptionAr: 'احتمال نقص النيتروجين',
      },
    ],
  },
];

export const MOCK_DISEASES: Disease[] = [
  {
    id: 'disease-1',
    name: 'Wheat Rust',
    nameAr: 'صدأ القمح',
    category: 'fungal',
    description: 'A common fungal disease affecting wheat crops',
    descriptionAr: 'مرض فطري شائع يصيب محاصيل القمح',
    symptoms: ['Orange-red pustules on leaves', 'Yellow spots', 'Leaf wilting'],
    symptomsAr: ['بثور برتقالية حمراء على الأوراق', 'بقع صفراء', 'ذبول الأوراق'],
    causes: ['Fungal spores', 'High humidity', 'Poor air circulation'],
    causesAr: ['جراثيم فطرية', 'رطوبة عالية', 'دوران هواء ضعيف'],
    affectedCrops: ['Wheat', 'Barley'],
    affectedCropsAr: ['قمح', 'شعير'],
    severity: 'medium',
    prevalence: 35,
  },
  {
    id: 'disease-2',
    name: 'Corn Blight',
    nameAr: 'لفحة الذرة',
    category: 'fungal',
    description: 'Fungal disease causing leaf lesions in corn',
    descriptionAr: 'مرض فطري يسبب آفات على أوراق الذرة',
    symptoms: ['Brown lesions on leaves', 'Stunted growth', 'Reduced yield'],
    symptomsAr: ['آفات بنية على الأوراق', 'توقف النمو', 'انخفاض الإنتاج'],
    causes: ['Fungal infection', 'Warm humid weather', 'Plant stress'],
    causesAr: ['عدوى فطرية', 'طقس دافئ رطب', 'إجهاد النبات'],
    affectedCrops: ['Corn', 'Sorghum'],
    affectedCropsAr: ['ذرة', 'ذرة رفيعة'],
    severity: 'high',
    prevalence: 42,
  },
];

export const MOCK_DISEASE_ALERTS: DiseaseAlert[] = [
  {
    id: 'alert-1',
    disease: MOCK_DISEASES[0]!,
    severity: 'medium',
    affectedFields: ['North Field', 'East Field'],
    affectedFieldsAr: ['الحقل الشمالي', 'الحقل الشرقي'],
    region: 'Northern Region',
    regionAr: 'المنطقة الشمالية',
    message: 'Wheat rust detected in your area. Monitor crops closely.',
    messageAr: 'تم رصد صدأ القمح في منطقتك. راقب المحاصيل عن كثب.',
    recommendations: ['Apply fungicide', 'Improve air circulation', 'Monitor daily'],
    recommendationsAr: ['استخدم مبيد فطري', 'حسّن دوران الهواء', 'راقب يومياً'],
    issuedAt: new Date().toISOString(),
    source: 'ai_detection',
  },
];
