/**
 * SAHOOL Scouting Feature Types
 * أنواع ميزة الكشافة الحقلية
 *
 * Field scouting data types for observing and recording field conditions,
 * pests, diseases, and other issues during field inspections.
 */

import type { GeoPoint } from '@/features/fields/types';

// Re-export GeoPoint for convenience
export type { GeoPoint };

// ═══════════════════════════════════════════════════════════════════════════
// Observation Categories
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Observation Category Types
 * Based on mobile scouting app categories
 */
export type ObservationCategory =
  | 'pest'           // حشرات - Insect pests
  | 'disease'        // فطريات/أمراض - Fungal/bacterial diseases
  | 'weed'           // أعشاب ضارة - Weeds
  | 'nutrient'       // نقص غذائي - Nutrient deficiency
  | 'water'          // جفاف/ري - Water stress/irrigation
  | 'other';         // أخرى - Other issues

/**
 * Severity Level (1-5 scale)
 */
export type Severity = 1 | 2 | 3 | 4 | 5;

/**
 * Session Status
 */
export type SessionStatus = 'active' | 'completed' | 'cancelled';

// ═══════════════════════════════════════════════════════════════════════════
// Photo Annotation Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Annotation Shape Type
 */
export type AnnotationType = 'circle' | 'arrow' | 'text' | 'rectangle';

/**
 * Photo Annotation Interface
 * For drawing on photos to highlight problem areas
 */
export interface PhotoAnnotation {
  id: string;
  type: AnnotationType;
  color: string;

  // Position and size (relative to image dimensions 0-1)
  x: number;
  y: number;
  width?: number;
  height?: number;

  // For arrows
  startX?: number;
  startY?: number;
  endX?: number;
  endY?: number;

  // For text
  text?: string;
  fontSize?: number;

  createdAt: string;
}

/**
 * Annotated Photo Interface
 */
export interface AnnotatedPhoto {
  id: string;
  url: string;
  thumbnailUrl?: string;
  annotations: PhotoAnnotation[];
  uploadedAt: string;
  fileSize?: number;
  mimeType?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Observation Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field Observation Interface
 * Individual observation point during scouting
 */
export interface Observation {
  id: string;
  sessionId: string;
  fieldId: string;

  // Location
  location: GeoPoint;
  locationName?: string;
  locationNameAr?: string;

  // Classification
  category: ObservationCategory;
  subcategory?: string;
  subcategoryAr?: string;
  severity: Severity;

  // Content
  notes: string;
  notesAr?: string;

  // Photos
  photos: AnnotatedPhoto[];

  // Task creation
  taskCreated?: boolean;
  taskId?: string;

  // Metadata
  observedBy?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Observation Form Data
 * For creating/editing observations
 */
export interface ObservationFormData {
  location: GeoPoint;
  locationName?: string;
  locationNameAr?: string;
  category: ObservationCategory;
  subcategory?: string;
  subcategoryAr?: string;
  severity: Severity;
  notes: string;
  notesAr?: string;
  photos?: File[];
  createTask?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Scouting Session Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Scouting Session Interface
 * A single field inspection session
 */
export interface ScoutingSession {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;

  // Session info
  status: SessionStatus;
  startTime: string;
  endTime?: string;
  duration?: number; // in minutes

  // Scout info
  scoutId: string;
  scoutName?: string;

  // Observations
  observationsCount: number;
  observations?: Observation[];

  // Summary stats
  categoryCounts?: Record<ObservationCategory, number>;
  severityDistribution?: Record<Severity, number>;
  averageSeverity?: number;

  // Metadata
  weather?: {
    temperature?: number;
    humidity?: number;
    conditions?: string;
  };
  notes?: string;
  notesAr?: string;

  createdAt: string;
  updatedAt: string;
}

/**
 * Session Summary Stats
 */
export interface SessionSummary {
  totalObservations: number;
  byCategory: Record<ObservationCategory, number>;
  bySeverity: Record<Severity, number>;
  averageSeverity: number;
  criticalIssues: number; // severity >= 4
  tasksCreated: number;
  photosTaken: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Scouting History Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Scouting History Filter
 */
export interface ScoutingHistoryFilter {
  fieldId?: string;
  scoutId?: string;
  category?: ObservationCategory;
  minSeverity?: Severity;
  startDate?: string;
  endDate?: string;
  status?: SessionStatus;
}

/**
 * Scouting Statistics
 * Aggregated stats across multiple sessions
 */
export interface ScoutingStatistics {
  totalSessions: number;
  totalObservations: number;
  averageObservationsPerSession: number;
  mostCommonCategory: ObservationCategory;
  mostCommonSeverity: Severity;
  sessionsThisWeek: number;
  sessionsThisMonth: number;
  trendData: Array<{
    date: string;
    observationCount: number;
    averageSeverity: number;
  }>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Report Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Scouting Report Configuration
 */
export interface ScoutingReportConfig {
  sessionId: string;
  includePhotos: boolean;
  includeMap: boolean;
  includeStatistics: boolean;
  includeRecommendations: boolean;
  language: 'en' | 'ar' | 'both';
  format: 'pdf' | 'excel' | 'json';
}

/**
 * Report Section
 */
export interface ReportSection {
  title: string;
  titleAr: string;
  content: string | Record<string, any>;
  order: number;
}

/**
 * Scouting Report
 */
export interface ScoutingReport {
  id: string;
  sessionId: string;
  generatedAt: string;
  generatedBy: string;
  config: ScoutingReportConfig;
  sections: ReportSection[];
  downloadUrl?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Category Metadata
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Category Option for UI
 */
export interface CategoryOption {
  value: ObservationCategory;
  label: string;
  labelAr: string;
  icon: string;
  color: string;
  subcategories?: Array<{
    value: string;
    label: string;
    labelAr: string;
    description?: string;
    descriptionAr?: string;
  }>;
}

/**
 * Predefined category options
 */
export const CATEGORY_OPTIONS: CategoryOption[] = [
  {
    value: 'pest',
    label: 'Pest',
    labelAr: 'حشرات',
    icon: 'Bug',
    color: '#ef4444',
    subcategories: [
      { value: 'aphid', label: 'Aphids', labelAr: 'من', description: 'Small sap-sucking insects', descriptionAr: 'حشرات صغيرة ماصة' },
      { value: 'caterpillar', label: 'Caterpillars', labelAr: 'دودة', description: 'Larvae on leaves', descriptionAr: 'يرقات على الأوراق' },
      { value: 'locust', label: 'Locust', labelAr: 'جراد', description: 'Desert locust', descriptionAr: 'جراد صحراوي' },
      { value: 'whitefly', label: 'Whitefly', labelAr: 'ذبابة بيضاء', description: 'White flying insects', descriptionAr: 'حشرات بيضاء طائرة' },
      { value: 'other_pest', label: 'Other', labelAr: 'أخرى', description: 'Other pests', descriptionAr: 'حشرات أخرى' },
    ],
  },
  {
    value: 'disease',
    label: 'Disease',
    labelAr: 'فطريات/أمراض',
    icon: 'Activity',
    color: '#a855f7',
    subcategories: [
      { value: 'rust', label: 'Rust', labelAr: 'صدأ', description: 'Orange/brown spots', descriptionAr: 'بقع برتقالية/بنية' },
      { value: 'powdery_mildew', label: 'Powdery Mildew', labelAr: 'بياض دقيقي', description: 'White powdery layer', descriptionAr: 'طبقة بيضاء' },
      { value: 'blight', label: 'Blight', labelAr: 'لفحة', description: 'Rapid browning/death', descriptionAr: 'احمرار/موت سريع' },
      { value: 'rot', label: 'Rot', labelAr: 'تعفن', description: 'Root/stem rot', descriptionAr: 'تعفن الجذور/الساق' },
      { value: 'other_disease', label: 'Other', labelAr: 'أخرى', description: 'Other diseases', descriptionAr: 'أمراض أخرى' },
    ],
  },
  {
    value: 'weed',
    label: 'Weed',
    labelAr: 'أعشاب ضارة',
    icon: 'Sprout',
    color: '#22c55e',
    subcategories: [
      { value: 'broadleaf', label: 'Broadleaf', labelAr: 'عريضة الأوراق', description: 'Broadleaf weeds', descriptionAr: 'أعشاب عريضة الأوراق' },
      { value: 'grassy', label: 'Grassy', labelAr: 'نجيلية', description: 'Grass-like weeds', descriptionAr: 'أعشاب نجيلية' },
      { value: 'sedge', label: 'Sedge', labelAr: 'سعدية', description: 'Sedge weeds', descriptionAr: 'أعشاب سعدية' },
      { value: 'other_weed', label: 'Other', labelAr: 'أخرى', description: 'Other weeds', descriptionAr: 'أعشاب أخرى' },
    ],
  },
  {
    value: 'nutrient',
    label: 'Nutrient Deficiency',
    labelAr: 'نقص غذائي',
    icon: 'Leaf',
    color: '#f59e0b',
    subcategories: [
      { value: 'nitrogen', label: 'Nitrogen', labelAr: 'نيتروجين', description: 'General yellowing', descriptionAr: 'اصفرار عام' },
      { value: 'phosphorus', label: 'Phosphorus', labelAr: 'فسفور', description: 'Purple/dark leaves', descriptionAr: 'أوراق بنفسجية/داكنة' },
      { value: 'potassium', label: 'Potassium', labelAr: 'بوتاسيوم', description: 'Brown edges', descriptionAr: 'حواف بنية' },
      { value: 'iron', label: 'Iron', labelAr: 'حديد', description: 'Yellowing between veins', descriptionAr: 'اصفرار بين العروق' },
      { value: 'other_nutrient', label: 'Other', labelAr: 'أخرى', description: 'Other deficiencies', descriptionAr: 'نقص آخر' },
    ],
  },
  {
    value: 'water',
    label: 'Water Stress',
    labelAr: 'جفاف/ري',
    icon: 'Droplets',
    color: '#3b82f6',
    subcategories: [
      { value: 'drought', label: 'Drought Stress', labelAr: 'إجهاد جفاف', description: 'Wilting leaves', descriptionAr: 'أوراق ذابلة' },
      { value: 'overwatering', label: 'Overwatering', labelAr: 'ري زائد', description: 'Waterlogged soil', descriptionAr: 'تربة مشبعة بالماء' },
      { value: 'irrigation_issue', label: 'Irrigation Issue', labelAr: 'مشكلة ري', description: 'Irrigation system problem', descriptionAr: 'مشكلة في نظام الري' },
      { value: 'other_water', label: 'Other', labelAr: 'أخرى', description: 'Other water issues', descriptionAr: 'مشاكل مياه أخرى' },
    ],
  },
  {
    value: 'other',
    label: 'Other',
    labelAr: 'أخرى',
    icon: 'AlertCircle',
    color: '#64748b',
    subcategories: [
      { value: 'mechanical_damage', label: 'Mechanical Damage', labelAr: 'ضرر ميكانيكي', description: 'Equipment/animal damage', descriptionAr: 'ضرر من المعدات/الحيوانات' },
      { value: 'weather_damage', label: 'Weather Damage', labelAr: 'ضرر جوي', description: 'Hail/wind/frost damage', descriptionAr: 'ضرر من البرد/الرياح/الصقيع' },
      { value: 'soil_issue', label: 'Soil Issue', labelAr: 'مشكلة تربة', description: 'Soil compaction/salinity', descriptionAr: 'انضغاط/ملوحة التربة' },
      { value: 'other_other', label: 'Other', labelAr: 'أخرى', description: 'Other issues', descriptionAr: 'مشاكل أخرى' },
    ],
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ApiScoutingResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    messageAr: string;
    code?: string;
  };
  message?: string;
  message_ar?: string;
}

export interface ApiSessionResponse extends ApiScoutingResponse<ScoutingSession> {}
export interface ApiSessionsListResponse extends ApiScoutingResponse<ScoutingSession[]> {}
export interface ApiObservationResponse extends ApiScoutingResponse<Observation> {}
export interface ApiObservationsListResponse extends ApiScoutingResponse<Observation[]> {}
export interface ApiStatisticsResponse extends ApiScoutingResponse<ScoutingStatistics> {}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Severity Label Helper
 */
export const SEVERITY_LABELS = {
  1: { en: 'Very Low', ar: 'منخفض جداً', color: '#10b981' },
  2: { en: 'Low', ar: 'منخفض', color: '#84cc16' },
  3: { en: 'Moderate', ar: 'متوسط', color: '#f59e0b' },
  4: { en: 'High', ar: 'عالي', color: '#f97316' },
  5: { en: 'Critical', ar: 'حرج', color: '#ef4444' },
} as const;
