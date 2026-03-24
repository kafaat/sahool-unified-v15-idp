/**
 * SAHOOL Vision Service Types
 * أنواع خدمة الرؤية الحاسوبية
 *
 * Type definitions for computer vision services including:
 * - Pest detection (كشف الآفات)
 * - Disease detection (كشف الأمراض)
 * - Weed detection (كشف الأعشاب الضارة)
 * - Plant identification (تحديد النباتات)
 */

// ═══════════════════════════════════════════════════════════════════════════
// Detection Types
// أنواع الكشف
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Types of detections supported by the vision service
 */
export type DetectionType = 'pest' | 'disease' | 'weed' | 'plant';

/**
 * Device type where inference was performed
 */
export type DeviceType = 'cloud' | 'edge' | 'mobile';

/**
 * Bounding box coordinates for detected objects
 */
export interface DetectionBoundingBox {
  xMin: number;
  yMin: number;
  xMax: number;
  yMax: number;
}

/**
 * Vision detection result
 * نتيجة الكشف بالرؤية الحاسوبية
 */
export interface Detection {
  detectionId: string;
  fieldId: string;
  detectionType: DetectionType;
  className: string;
  classNameAr: string;
  confidence: number;
  bbox: DetectionBoundingBox;
  segmentationMask?: number[][];
  modelVersion: string;
  inferenceTimeMs: number;
  deviceType: DeviceType;
  createdAt: Date;
}

/**
 * Extended detection with image metadata
 */
export interface DetectionWithImage extends Detection {
  imageId: string;
  imageUrl: string;
  imageThumbnailUrl?: string;
  imageWidth: number;
  imageHeight: number;
  capturedAt: Date;
  geoLocation?: {
    latitude: number;
    longitude: number;
    accuracy?: number;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Pest Classification Types
// أنواع تصنيف الآفات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Pest classes detected by the vision service
 * فئات الآفات المكتشفة
 */
export type PestClass =
  | 'locust' // جراد
  | 'aphid' // من
  | 'whitefly' // ذبابة بيضاء
  | 'thrips' // تربس
  | 'spider_mite' // عنكبوت أحمر
  | 'leafhopper' // نطاط الأوراق
  | 'armyworm' // دودة الحشد
  | 'cutworm' // دودة قاطعة
  | 'stem_borer' // حفار الساق
  | 'fruit_fly' // ذبابة الفاكهة
  | 'weevil' // سوسة
  | 'bollworm' // دودة اللوز
  | 'red_palm_weevil' // سوسة النخيل الحمراء
  | 'dubas_bug' // حشرة الدوباس
  | 'scale_insect' // حشرة قشرية
  | 'mealybug' // البق الدقيقي
  | 'grasshopper' // جندب
  | 'unknown_pest'; // آفة غير معروفة

/**
 * Pest detection with specific metadata
 */
export interface PestDetection extends Detection {
  detectionType: 'pest';
  pestClass: PestClass;
  pestClassAr: string;
  lifeCycleStage?: 'egg' | 'larva' | 'nymph' | 'pupa' | 'adult';
  lifeCycleStageAr?: string;
  estimatedPopulationDensity?: 'low' | 'medium' | 'high' | 'severe';
  estimatedPopulationDensityAr?: string;
  actionThresholdReached: boolean;
  recommendedAction?: string;
  recommendedActionAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Disease Classification Types
// أنواع تصنيف الأمراض
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Disease classes detected by the vision service
 * فئات الأمراض المكتشفة
 */
export type DiseaseClass =
  | 'rust' // صدأ
  | 'powdery_mildew' // بياض دقيقي
  | 'downy_mildew' // بياض زغبي
  | 'blight' // لفحة
  | 'leaf_spot' // تبقع الأوراق
  | 'anthracnose' // أنثراكنوز
  | 'fusarium_wilt' // ذبول فيوزاريوم
  | 'verticillium_wilt' // ذبول فيرتيسيليوم
  | 'root_rot' // تعفن الجذور
  | 'bacterial_blight' // لفحة بكتيرية
  | 'viral_mosaic' // موزاييك فيروسي
  | 'smut' // تفحم
  | 'ergot' // أرغوت
  | 'scab' // جرب
  | 'canker' // تقرح
  | 'damping_off' // سقوط البادرات
  | 'black_rot' // عفن أسود
  | 'gray_mold' // عفن رمادي
  | 'nutrient_deficiency' // نقص عناصر غذائية
  | 'unknown_disease'; // مرض غير معروف

/**
 * Disease severity level
 */
export type DiseaseSeverity = 'trace' | 'light' | 'moderate' | 'severe' | 'very_severe';

/**
 * Disease detection with specific metadata
 */
export interface DiseaseDetection extends Detection {
  detectionType: 'disease';
  diseaseClass: DiseaseClass;
  diseaseClassAr: string;
  severity: DiseaseSeverity;
  severityAr: string;
  severityPercent: number;
  affectedPlantPart: 'leaf' | 'stem' | 'root' | 'fruit' | 'flower' | 'whole_plant';
  affectedPlantPartAr: string;
  spreadRisk: 'low' | 'medium' | 'high';
  spreadRiskAr: string;
  isTreatable: boolean;
  recommendedTreatment?: string;
  recommendedTreatmentAr?: string;
  quarantineRequired: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Weed Classification Types
// أنواع تصنيف الأعشاب الضارة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Weed classes detected by the vision service
 * فئات الأعشاب الضارة المكتشفة
 */
export type WeedClass =
  | 'broadleaf' // عريضة الأوراق
  | 'grass_weed' // حشائش نجيلية
  | 'sedge' // سعد
  | 'thistle' // شوك
  | 'bindweed' // لبلاب
  | 'pigweed' // رجلة
  | 'lambsquarters' // قطف
  | 'purslane' // بقلة
  | 'nutsedge' // سعد مثلث
  | 'barnyard_grass' // دنيبة
  | 'crabgrass' // نجم
  | 'wild_oat' // شوفان بري
  | 'dodder' // حامول
  | 'broomrape' // هالوك
  | 'unknown_weed'; // عشب ضار غير معروف

/**
 * Weed detection with specific metadata
 */
export interface WeedDetection extends Detection {
  detectionType: 'weed';
  weedClass: WeedClass;
  weedClassAr: string;
  growthStage: 'seedling' | 'vegetative' | 'flowering' | 'seeding';
  growthStageAr: string;
  coveragePercent: number;
  competitionLevel: 'low' | 'medium' | 'high';
  competitionLevelAr: string;
  isParasitic: boolean;
  resistanceProfile?: string[];
  recommendedHerbicide?: string;
  recommendedHerbicideAr?: string;
  mechanicalControlSuitable: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Plant Identification Types
// أنواع تحديد النباتات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Plant identification detection
 */
export interface PlantDetection extends Detection {
  detectionType: 'plant';
  scientificName: string;
  commonName: string;
  commonNameAr: string;
  family: string;
  familyAr: string;
  growthHabit: 'annual' | 'biennial' | 'perennial';
  growthHabitAr: string;
  isAgronomicCrop: boolean;
  varietyMatch?: string;
  varietyConfidence?: number;
  healthStatus: 'healthy' | 'stressed' | 'diseased' | 'damaged';
  healthStatusAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Vision Service Request/Response Types
// أنواع طلبات واستجابات خدمة الرؤية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Detection request payload
 */
export interface DetectionRequest {
  imageBase64?: string;
  imageUrl?: string;
  fieldId?: string;
  detectionTypes?: DetectionType[];
  confidenceThreshold?: number;
  maxDetections?: number;
  includeSegmentation?: boolean;
  modelVersion?: string;
  deviceType?: DeviceType;
  metadata?: Record<string, unknown>;
}

/**
 * Batch detection request
 */
export interface BatchDetectionRequest {
  images: Array<{
    imageBase64?: string;
    imageUrl?: string;
    imageId: string;
  }>;
  fieldId?: string;
  detectionTypes?: DetectionType[];
  confidenceThreshold?: number;
}

/**
 * Detection response
 */
export interface DetectionResponse {
  success: boolean;
  requestId: string;
  detections: Detection[];
  totalDetections: number;
  processingTimeMs: number;
  modelVersion: string;
  deviceType: DeviceType;
  warnings?: string[];
  warningsAr?: string[];
}

/**
 * Detection summary for a field
 */
export interface FieldDetectionSummary {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  totalScans: number;
  lastScanDate: string;
  detectionCounts: {
    pest: number;
    disease: number;
    weed: number;
    plant: number;
  };
  topPests: Array<{
    pestClass: PestClass;
    count: number;
    lastDetected: string;
  }>;
  topDiseases: Array<{
    diseaseClass: DiseaseClass;
    count: number;
    avgSeverity: DiseaseSeverity;
    lastDetected: string;
  }>;
  healthScore: number;
  healthScoreAr: string;
  alertLevel: 'none' | 'low' | 'medium' | 'high' | 'critical';
  alertLevelAr: string;
  recommendations: string[];
  recommendationsAr: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Model Types
// أنواع النماذج
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Vision model metadata
 */
export interface VisionModel {
  modelId: string;
  modelName: string;
  modelNameAr: string;
  version: string;
  detectionTypes: DetectionType[];
  supportedCrops?: string[];
  inputSize: {
    width: number;
    height: number;
  };
  architecture: string;
  accuracy: number;
  inferenceTimeMs: number;
  sizeBytes: number;
  isEdgeCompatible: boolean;
  isMobileCompatible: boolean;
  lastUpdated: string;
  releaseNotes?: string;
  releaseNotesAr?: string;
}

/**
 * Model deployment status
 */
export interface ModelDeploymentStatus {
  modelId: string;
  deployedTo: DeviceType[];
  cloudVersion: string;
  edgeVersion?: string;
  mobileVersion?: string;
  lastSync: string;
  syncStatus: 'synced' | 'syncing' | 'pending' | 'failed';
}
