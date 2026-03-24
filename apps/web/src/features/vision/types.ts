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
