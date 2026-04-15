/**
 * Vision Service Feature - Types
 * أنواع ميزة الرؤية الحاسوبية
 */

/**
 * Bounding box in pixel coordinates. The yolo26 service returns
 * `{x1, y1, x2, y2}` objects rather than a 4-tuple, but older snapshots of
 * this interface used a tuple — we accept either at runtime. Readers should
 * coerce via toBBoxTuple() in the consumer layer.
 */
export type BBoxTuple = [number, number, number, number];

/**
 * Base detection result. Field names match the yolo26-vision-service
 * schemas (snake_case) with optional camelCase aliases for backward
 * compatibility with older clients.
 * See apps/services/yolo26-vision-service/src/api/schemas.py::DetectionBase
 */
export interface Detection {
  /** Class name in English (backend: class_name_en) */
  class_name_en?: string;
  /** Class name in Arabic (backend: class_name_ar) */
  class_name_ar?: string;
  /** Legacy camelCase aliases (never populated by current backend) */
  class?: string;
  classAr?: string;
  confidence: number;
  /** Backend returns a BoundingBox object {x1,y1,x2,y2}, not a tuple */
  bbox: BBoxTuple | { x1: number; y1: number; x2: number; y2: number };
  scientific_name?: string | null;
}

export interface PestDetection {
  detections: Array<
    Detection & {
      severity: 'low' | 'medium' | 'high' | 'critical';
      life_stage?: string | null;
      /** Backend: recommended_action_en / recommended_action_ar */
      recommended_action_en?: string | null;
      recommended_action_ar?: string | null;
      /** Legacy camelCase aliases (not populated by current backend) */
      species?: string;
      speciesAr?: string;
      recommendation?: string;
      recommendationAr?: string;
    }
  >;
  total_count?: number;
  severity_summary?: Record<string, number>;
  processing_time_ms?: number;
  image_metadata?: Record<string, unknown>;
  visualization_base64?: string | null;
  /** Legacy aliases */
  imageUrl?: string;
  processedAt?: string;
  visualizationBase64?: string;
}

export interface DiseaseDetection {
  detections: Array<
    Detection & {
      severity: 'low' | 'medium' | 'high' | 'critical';
      /** Backend: affected_area_percent */
      affected_area_percent?: number | null;
      spread_risk?: 'low' | 'medium' | 'high' | 'critical';
      /** Backend: recommended_treatment_en / recommended_treatment_ar */
      recommended_treatment_en?: string | null;
      recommended_treatment_ar?: string | null;
      /** Legacy aliases */
      disease?: string;
      diseaseAr?: string;
      affectedArea?: number;
      treatment?: string;
      treatmentAr?: string;
    }
  >;
  total_count?: number;
  overall_health_score?: number;
  severity_summary?: Record<string, number>;
  processing_time_ms?: number;
  visualization_base64?: string | null;
  imageUrl?: string;
  processedAt?: string;
  visualizationBase64?: string;
}

export interface WeedDetection {
  detections: Array<
    Detection & {
      /** Backend: coverage_percent */
      coverage_percent?: number | null;
      growth_stage?: string | null;
      /** Legacy aliases */
      species?: string;
      speciesAr?: string;
      coverage?: number;
    }
  >;
  /** Backend: total_coverage_percent */
  total_coverage_percent?: number;
  /** Legacy alias */
  totalCoverage?: number;
  total_count?: number;
  species_distribution?: Record<string, number>;
  processing_time_ms?: number;
  visualization_base64?: string | null;
  imageUrl?: string;
  processedAt?: string;
  visualizationBase64?: string;
}

export interface PlantCount {
  totalCount: number;
  density: number;
  gridCells: Array<{ x: number; y: number; count: number }>;
  imageUrl?: string;
}

export interface RipenessResult {
  stage: 'unripe' | 'early_ripe' | 'half_ripe' | 'ripe' | 'overripe';
  stageAr: string;
  confidence: number;
  distribution: Record<string, number>;
}

export interface LeafSegmentation {
  leafCount: number;
  totalArea: number;
  lai: number;
  masks: Array<{ id: number; area: number; centroid: [number, number] }>;
  imageUrl?: string;
}

export interface ModelInfo {
  variant: string;
  version: string;
  size: number;
  parameters: number;
  tasks: string[];
  loaded: boolean;
  lastUsed?: string;
}

export interface VisionFilters {
  task?: string;
  dateFrom?: string;
  dateTo?: string;
}

// =============================================================================
// Visualization Types
// أنواع التصور البصري
// =============================================================================

/**
 * Bounding box coordinates (normalized 0-1 or pixel coordinates).
 * إحداثيات مربع الإحاطة
 */
export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

/**
 * Detection visualization data returned when return_visualization=true.
 * بيانات التصور البصري للكشف
 */
export interface DetectionVisualization {
  /** Base64 encoded image with bounding boxes and labels drawn */
  imageBase64: string;
  /** MIME type of the visualization image (e.g. "image/png") */
  mimeType: string;
  /** Width of the visualization image in pixels */
  width: number;
  /** Height of the visualization image in pixels */
  height: number;
  /** Number of detections rendered on the visualization */
  detectionCount: number;
}

/**
 * Severity color mapping for detection overlays.
 * ألوان شدة الإصابة للعرض البصري
 */
export const SEVERITY_COLORS: Record<string, string> = {
  critical: '#FF0000',
  high: '#FF6600',
  medium: '#FFCC00',
  low: '#00CC00',
  none: '#0066FF',
} as const;

/**
 * Severity color mapping with Arabic labels.
 * ألوان شدة الإصابة مع التسميات العربية
 */
export const SEVERITY_LABELS: Record<string, { en: string; ar: string; color: string }> = {
  critical: { en: 'Critical', ar: 'حرج', color: '#FF0000' },
  high: { en: 'High', ar: 'مرتفع', color: '#FF6600' },
  medium: { en: 'Medium', ar: 'متوسط', color: '#FFCC00' },
  low: { en: 'Low', ar: 'منخفض', color: '#00CC00' },
  none: { en: 'None', ar: 'لا يوجد', color: '#0066FF' },
} as const;
