/**
 * Vision Service Feature - Types
 * أنواع ميزة الرؤية الحاسوبية
 */

export interface Detection {
  class: string;
  classAr: string;
  confidence: number;
  bbox: [number, number, number, number];
}

export interface PestDetection {
  detections: Array<
    Detection & {
      species: string;
      speciesAr: string;
      severity: 'low' | 'medium' | 'high' | 'critical';
      recommendation: string;
      recommendationAr: string;
    }
  >;
  imageUrl?: string;
  processedAt: string;
  visualization_base64?: string;
}

export interface DiseaseDetection {
  detections: Array<
    Detection & {
      disease: string;
      diseaseAr: string;
      affectedArea: number;
      treatment: string;
      treatmentAr: string;
    }
  >;
  imageUrl?: string;
  processedAt: string;
  visualization_base64?: string;
}

export interface WeedDetection {
  detections: Array<
    Detection & {
      species: string;
      speciesAr: string;
      coverage: number;
    }
  >;
  totalCoverage: number;
  imageUrl?: string;
  processedAt: string;
  visualization_base64?: string;
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
