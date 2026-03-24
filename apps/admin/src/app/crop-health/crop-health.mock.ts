/**
 * Crop Health Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة إدارة صحة المحاصيل
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface CropHealthRecord {
  id: string;
  farmId: string;
  farmName: string;
  farmNameAr: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  crop: string;
  cropAr: string;
  ndvi: number;
  ndviChange: number;
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  issues: string[];
  issuesAr: string[];
  lastInspection: string;
  nextInspection: string;
  recommendations?: string[];
  recommendationsAr?: string[];
}

export const MOCK_RECORDS: CropHealthRecord[] = [
  {
    id: '1',
    farmId: 'F001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    fieldId: 'FLD001',
    fieldName: 'Wheat Field A',
    fieldNameAr: 'حقل القمح أ',
    crop: 'Wheat',
    cropAr: 'قمح',
    ndvi: 0.78,
    ndviChange: 0.05,
    healthStatus: 'excellent',
    issues: [],
    issuesAr: [],
    lastInspection: '2026-01-24',
    nextInspection: '2026-02-07',
  },
  {
    id: '2',
    farmId: 'F002',
    farmName: 'Green Valley',
    farmNameAr: 'الوادي الأخضر',
    fieldId: 'FLD002',
    fieldName: 'Tomato Greenhouse',
    fieldNameAr: 'صوبة الطماطم',
    crop: 'Tomato',
    cropAr: 'طماطم',
    ndvi: 0.65,
    ndviChange: -0.08,
    healthStatus: 'moderate',
    issues: ['Nitrogen deficiency', 'Minor pest damage'],
    issuesAr: ['نقص نيتروجين', 'أضرار آفات طفيفة'],
    lastInspection: '2026-01-23',
    nextInspection: '2026-01-30',
    recommendations: ['Apply nitrogen fertilizer', 'Monitor pest levels'],
    recommendationsAr: ['تطبيق سماد نيتروجين', 'مراقبة مستويات الآفات'],
  },
  {
    id: '3',
    farmId: 'F003',
    farmName: 'Desert Oasis',
    farmNameAr: 'واحة الصحراء',
    fieldId: 'FLD003',
    fieldName: 'Date Palm Grove',
    fieldNameAr: 'بستان النخيل',
    crop: 'Date Palm',
    cropAr: 'نخيل',
    ndvi: 0.72,
    ndviChange: 0.02,
    healthStatus: 'good',
    issues: [],
    issuesAr: [],
    lastInspection: '2026-01-22',
    nextInspection: '2026-02-05',
  },
  {
    id: '4',
    farmId: 'F004',
    farmName: 'Palm Gardens',
    farmNameAr: 'حدائق النخيل',
    fieldId: 'FLD004',
    fieldName: 'Citrus Orchard',
    fieldNameAr: 'بستان الحمضيات',
    crop: 'Citrus',
    cropAr: 'حمضيات',
    ndvi: 0.45,
    ndviChange: -0.15,
    healthStatus: 'poor',
    issues: ['Water stress', 'Leaf yellowing', 'Pest infestation'],
    issuesAr: ['إجهاد مائي', 'اصفرار الأوراق', 'إصابة بالآفات'],
    lastInspection: '2026-01-25',
    nextInspection: '2026-01-28',
    recommendations: ['Increase irrigation', 'Apply fungicide', 'Pest treatment'],
    recommendationsAr: ['زيادة الري', 'تطبيق مبيد فطري', 'معالجة الآفات'],
  },
  {
    id: '5',
    farmId: 'F005',
    farmName: 'Old Farms',
    farmNameAr: 'المزارع القديمة',
    fieldId: 'FLD005',
    fieldName: 'Barley Field',
    fieldNameAr: 'حقل الشعير',
    crop: 'Barley',
    cropAr: 'شعير',
    ndvi: 0.32,
    ndviChange: -0.22,
    healthStatus: 'critical',
    issues: ['Severe drought', 'Disease outbreak', 'Nutrient deficiency'],
    issuesAr: ['جفاف شديد', 'انتشار مرض', 'نقص عناصر غذائية'],
    lastInspection: '2026-01-25',
    nextInspection: '2026-01-26',
    recommendations: ['Emergency irrigation', 'Disease treatment', 'Soil amendment'],
    recommendationsAr: ['ري طارئ', 'علاج المرض', 'تحسين التربة'],
  },
];
