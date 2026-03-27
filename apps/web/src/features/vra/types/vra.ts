/**
 * SAHOOL VRA (Variable Rate Application) Types
 * أنواع التطبيق المتغير المعدل
 *
 * Type definitions for VRA prescription maps and variable rate application features.
 */

// ═══════════════════════════════════════════════════════════════════════════
// Core VRA Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * VRA Application Types
 * أنواع التطبيق المتغير
 */
export type VRAType = 'fertilizer' | 'seed' | 'lime' | 'pesticide' | 'irrigation';

/**
 * Zone Classification Methods
 * طرق تصنيف المناطق
 */
export type VRAMethod = 'ndvi' | 'yield' | 'soil' | 'combined';

/**
 * Zone Level Classification
 * تصنيف مستوى المنطقة
 */
export type ZoneLevel = 'very_low' | 'low' | 'medium' | 'high' | 'very_high';

/**
 * Export Format Types
 * أنواع تنسيق التصدير
 */
export type ExportFormat = 'geojson' | 'csv' | 'shapefile' | 'isoxml';

// ═══════════════════════════════════════════════════════════════════════════
// Request/Response Models
// ═══════════════════════════════════════════════════════════════════════════

/**
 * VRA Prescription Generation Request
 * طلب توليد وصفة التطبيق المتغير
 */
export interface PrescriptionRequest {
  fieldId: string;
  latitude: number;
  longitude: number;
  vraType: VRAType;
  targetRate: number;
  unit: string; // kg/ha, seeds/ha, L/ha, mm/ha
  numZones?: number; // 3 or 5, default 3
  zoneMethod?: VRAMethod; // default 'ndvi'
  minRate?: number;
  maxRate?: number;
  productPricePerUnit?: number;
  notes?: string;
  notesAr?: string;
}

/**
 * Management Zone in Prescription Map
 * منطقة إدارة في خريطة الوصفة
 */
export interface ZoneResult {
  zoneId: number;
  zoneName: string;
  zoneNameAr: string;
  zoneLevel: ZoneLevel;
  ndviMin: number;
  ndviMax: number;
  areaHa: number;
  percentage: number;
  centroid: [number, number]; // [lon, lat]
  polygon?: number[][][]; // GeoJSON Polygon coordinates
  recommendedRate: number;
  unit: string;
  totalProduct: number;
  color: string;
}

/**
 * Complete VRA Prescription Response
 * استجابة وصفة التطبيق المتغير الكاملة
 */
export interface PrescriptionResponse {
  id: string;
  fieldId: string;
  vraType: VRAType;
  createdAt: string;
  targetRate: number;
  minRate: number;
  maxRate: number;
  unit: string;
  numZones: number;
  zoneMethod: VRAMethod;
  zones: ZoneResult[];
  totalAreaHa: number;
  totalProductNeeded: number;
  flatRateProduct: number;
  savingsPercent: number;
  savingsAmount: number;
  costSavings?: number;
  notes?: string;
  notesAr?: string;
  geojsonUrl?: string;
  shapefileUrl?: string;
  isoxmlUrl?: string;
}

/**
 * Prescription Summary for History List
 * ملخص الوصفة لقائمة السجل
 */
export interface PrescriptionSummary {
  id: string;
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  vraType: VRAType;
  createdAt: string;
  targetRate: number;
  unit: string;
  numZones: number;
  totalAreaHa: number;
  savingsPercent: number;
  savingsAmount: number;
  costSavings?: number;
}

/**
 * Prescription History Response
 * استجابة سجل الوصفات
 */
export interface PrescriptionHistoryResponse {
  fieldId: string;
  count: number;
  prescriptions: PrescriptionSummary[];
}

/**
 * Prescription Export Request
 * طلب تصدير الوصفة
 */
export interface PrescriptionExport {
  prescriptionId: string;
  format: ExportFormat;
}

// ═══════════════════════════════════════════════════════════════════════════
// UI State Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * VRA Panel State
 * حالة لوحة التطبيق المتغير
 */
export interface VRAPanelState {
  selectedFieldId?: string;
  vraType: VRAType;
  targetRate: number;
  unit: string;
  numZones: number;
  zoneMethod: VRAMethod;
  minRate?: number;
  maxRate?: number;
  productPrice?: number;
}

/**
 * VRA Form Validation Errors
 * أخطاء التحقق من نموذج التطبيق المتغير
 */
export interface VRAFormErrors {
  fieldId?: string;
  vraType?: string;
  targetRate?: string;
  unit?: string;
  numZones?: string;
  zoneMethod?: string;
  minRate?: string;
  maxRate?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// VRA Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * VRA Type Configuration
 * تكوين نوع التطبيق المتغير
 */
export interface VRATypeConfig {
  type: VRAType;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  defaultUnit: string;
  strategy: string;
  strategyAr: string;
  icon?: string;
}

/**
 * Zone Method Configuration
 * تكوين طريقة المنطقة
 */
export interface ZoneMethodConfig {
  method: VRAMethod;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants and Configurations
// ═══════════════════════════════════════════════════════════════════════════

/**
 * VRA Type Configurations
 * تكوينات أنواع التطبيق المتغير
 */
export const VRA_TYPES: Record<VRAType, VRATypeConfig> = {
  fertilizer: {
    type: 'fertilizer',
    name: 'Fertilizer',
    nameAr: 'تسميد',
    description: 'Variable nitrogen/fertilizer application based on crop vigor',
    descriptionAr: 'تطبيق النيتروجين/الأسمدة المتغير بناءً على قوة المحصول',
    defaultUnit: 'kg/ha',
    strategy: 'More to low-vigor areas, less to high-vigor areas',
    strategyAr: 'المزيد للمناطق منخفضة النشاط، والأقل للمناطق عالية النشاط',
  },
  seed: {
    type: 'seed',
    name: 'Seed',
    nameAr: 'بذار',
    description: 'Variable seeding rates based on field potential',
    descriptionAr: 'معدلات البذر المتغيرة بناءً على إمكانات الحقل',
    defaultUnit: 'seeds/ha',
    strategy: 'More seeds to high-potential areas',
    strategyAr: 'المزيد من البذور للمناطق ذات الإمكانات العالية',
  },
  lime: {
    type: 'lime',
    name: 'Lime',
    nameAr: 'جير',
    description: 'Variable lime application for pH correction',
    descriptionAr: 'تطبيق الجير المتغير لتصحيح الحموضة',
    defaultUnit: 'kg/ha',
    strategy: 'More lime to acidic (low NDVI) areas',
    strategyAr: 'المزيد من الجير للمناطق الحمضية (NDVI منخفض)',
  },
  pesticide: {
    type: 'pesticide',
    name: 'Pesticide',
    nameAr: 'مبيدات',
    description: 'Variable pesticide application targeting problem areas',
    descriptionAr: 'تطبيق المبيدات المتغير لاستهداف المناطق المشكلة',
    defaultUnit: 'L/ha',
    strategy: 'Target high-vigor areas where pests thrive',
    strategyAr: 'استهداف المناطق عالية النشاط حيث تزدهر الآفات',
  },
  irrigation: {
    type: 'irrigation',
    name: 'Irrigation',
    nameAr: 'ري',
    description: 'Variable water application based on stress indicators',
    descriptionAr: 'تطبيق الماء المتغير بناءً على مؤشرات الإجهاد',
    defaultUnit: 'mm/ha',
    strategy: 'More water to stressed (low NDVI) areas',
    strategyAr: 'المزيد من الماء للمناطق المجهدة (NDVI منخفض)',
  },
};

/**
 * Zone Method Configurations
 * تكوينات طرق المناطق
 */
export const ZONE_METHODS: Record<VRAMethod, ZoneMethodConfig> = {
  ndvi: {
    method: 'ndvi',
    name: 'NDVI-Based',
    nameAr: 'بناءً على NDVI',
    description: 'Zones based on vegetation index from satellite imagery',
    descriptionAr: 'مناطق بناءً على مؤشر الغطاء النباتي من صور الأقمار الصناعية',
  },
  yield: {
    method: 'yield',
    name: 'Yield-Based',
    nameAr: 'بناءً على الإنتاج',
    description: 'Zones based on historical yield data',
    descriptionAr: 'مناطق بناءً على بيانات الإنتاج التاريخية',
  },
  soil: {
    method: 'soil',
    name: 'Soil-Based',
    nameAr: 'بناءً على التربة',
    description: 'Zones based on soil analysis and properties',
    descriptionAr: 'مناطق بناءً على تحليل التربة وخصائصها',
  },
  combined: {
    method: 'combined',
    name: 'Combined',
    nameAr: 'مجمع',
    description: 'Multi-factor zone classification combining NDVI, yield, and soil',
    descriptionAr: 'تصنيف المناطق متعدد العوامل يجمع بين NDVI والإنتاج والتربة',
  },
};

/**
 * Zone Level Names
 * أسماء مستويات المناطق
 */
export const ZONE_LEVEL_NAMES: Record<ZoneLevel, { name: string; nameAr: string }> = {
  very_low: { name: 'Very Low', nameAr: 'منخفض جداً' },
  low: { name: 'Low', nameAr: 'منخفض' },
  medium: { name: 'Medium', nameAr: 'متوسط' },
  high: { name: 'High', nameAr: 'عالي' },
  very_high: { name: 'Very High', nameAr: 'عالي جداً' },
};

/**
 * Default Zone Colors
 * ألوان المناطق الافتراضية
 */
export const ZONE_COLORS: Record<ZoneLevel, string> = {
  very_low: '#d62728', // Red
  low: '#ff7f0e', // Orange
  medium: '#ffdd00', // Yellow
  high: '#98df8a', // Light green
  very_high: '#2ca02c', // Dark green
};

/**
 * Number of Zones Options
 * خيارات عدد المناطق
 */
export const ZONE_COUNT_OPTIONS = [3, 5] as const;

/**
 * Export Format Labels
 * تسميات تنسيقات التصدير
 */
export const EXPORT_FORMAT_LABELS: Record<ExportFormat, { name: string; nameAr: string }> = {
  geojson: { name: 'GeoJSON', nameAr: 'GeoJSON' },
  csv: { name: 'CSV', nameAr: 'CSV' },
  shapefile: { name: 'Shapefile', nameAr: 'Shapefile' },
  isoxml: { name: 'ISO-XML', nameAr: 'ISO-XML' },
};
