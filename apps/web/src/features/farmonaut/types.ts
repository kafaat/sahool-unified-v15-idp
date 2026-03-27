/**
 * Farmonaut Satellite Monitoring - Types
 * أنواع بيانات مراقبة الأقمار الصناعية فارمونوت
 */

export type CropHealthStatus = 'healthy' | 'moderate' | 'stressed' | 'critical';
export type AlertSeverity = 'critical' | 'warning' | 'advisory' | 'info';
export type WeatherCondition = 'sunny' | 'partly_cloudy' | 'cloudy' | 'rainy' | 'stormy' | 'windy';
export type ReportFormat = 'pdf' | 'csv' | 'json';
export type TimePeriod = '7d' | '30d' | '90d' | '6m' | '1y';

// ---------------------------------------------------------------------------
// Map Layer Types (10 indices from Farmonaut)
// ---------------------------------------------------------------------------
export type MapLayerType =
  | 'hybrid'            // Hybrid Index - combined crop health + irrigation
  | 'colorblind'        // Colorblind-friendly visualization
  | 'tci'               // True Color Image (colored satellite image)
  | 'etci'              // Enhanced True Color Image
  | 'ndvi'              // Normalized Difference Vegetation Index
  | 'evi'               // Enhanced Vegetation Index
  | 'savi'              // Soil Adjusted Vegetation Index
  | 'ndre'              // Normalized Difference Red Edge (late growth)
  | 'ndwi'              // Normalized Difference Water Index
  | 'ndmi'              // Normalized Difference Moisture Index
  | 'evapotranspiration' // Evapotranspiration rate
  | 'soc'               // Soil Organic Carbon
  | 'erosion'           // Soil Erosion analysis
  | 'dem'               // Digital Elevation Model (Topography)
  | 'sar_rvi'           // SAR Radar Vegetation Index
  | 'sar_rsm';          // SAR Radar Soil Moisture

// Hybrid Index color meanings
export type HybridColor = 'green' | 'orange' | 'purple' | 'red' | 'white';

export interface HybridColorMeaning {
  color: HybridColor;
  hex: string;
  meaning: string;
  meaningAr: string;
}

// 9-Direction Grid for field analysis reports
export type DirectionZone = 'NW' | 'N' | 'NE' | 'W' | 'C' | 'E' | 'SW' | 'S' | 'SE';

export interface DirectionZoneData {
  zone: DirectionZone;
  label: string;
  labelAr: string;
  ndvi: number;
  healthStatus: CropHealthStatus;
  irrigationNeeded: boolean;
  recommendation: string;
  recommendationAr: string;
}

export interface DirectionGridAnalysis {
  fieldId: string;
  analysisDate: string;
  layerType: MapLayerType;
  zones: DirectionZoneData[];
}

// ---------------------------------------------------------------------------
// JEEVN AI Advisory Types
// ---------------------------------------------------------------------------
export type NutrientLevel = 'optimal' | 'adequate' | 'low' | 'deficient' | 'excess';

export interface SoilNutrient {
  name: string;
  nameAr: string;
  symbol: string;
  value: number;
  unit: string;
  optimalRange: { min: number; max: number };
  level: NutrientLevel;
  recommendation: string;
  recommendationAr: string;
}

export interface SoilAnalysis {
  fieldId: string;
  analysisDate: string;
  nutrients: SoilNutrient[];
  ph: { value: number; optimal: { min: number; max: number }; level: NutrientLevel };
  salinity: { value: number; unit: string; level: NutrientLevel };
  organicCarbon: { value: number; unit: string; level: NutrientLevel };
  overallHealth: CropHealthStatus;
  fertilizerRecommendations: Array<{
    product: string;
    productAr: string;
    quantity: number;
    unit: string;
    timing: string;
    timingAr: string;
  }>;
}

export interface PestPrediction {
  id: string;
  fieldId: string;
  pestName: string;
  pestNameAr: string;
  riskLevel: AlertSeverity;
  probability: number;
  detectionSource: 'satellite' | 'weather_pattern' | 'historical' | 'ndvi_anomaly';
  preventiveAction: string;
  preventiveActionAr: string;
  estimatedDate: string;
}

export interface IrrigationSchedule {
  fieldId: string;
  nextIrrigation: string;
  amountMm: number;
  durationHours: number;
  factors: {
    weatherData: { temp: number; humidity: number; windSpeed: number };
    soilMoisture: number;
    cropWaterNeed: number;
    evapotranspiration: number;
  };
  zones: Array<{
    zone: DirectionZone;
    priority: 'urgent' | 'normal' | 'skip';
    amountMm: number;
  }>;
}

export interface YieldPrediction {
  fieldId: string;
  cropType: string;
  cropTypeAr: string;
  predictedHeight: number;
  heightUnit: string;
  expectedYield: number;
  yieldUnit: string;
  yieldPerHectare: number;
  plannedHarvestDate: string;
  confidencePercent: number;
  trend: 'above_average' | 'average' | 'below_average';
}

// ---------------------------------------------------------------------------
// Field Setup / Creation
// ---------------------------------------------------------------------------
export type BoundaryInputMethod = 'draw' | 'kml' | 'shapefile' | 'coordinates';

export interface FieldSetupData {
  name: string;
  nameAr: string;
  cropType: string;
  sowingDate: string;
  boundary: FieldBoundary[];
  boundaryMethod: BoundaryInputMethod;
  address?: string;
  coordinates?: { lat: number; lng: number };
}

// ---------------------------------------------------------------------------
// Historical / Timelapse
// ---------------------------------------------------------------------------
export interface HistoricalDataRequest {
  fieldId: string;
  startDate: string; // from 2017
  endDate: string;
  layerType: MapLayerType;
  interval: 'weekly' | 'biweekly' | 'monthly';
}

export interface HistoricalSnapshot {
  date: string;
  layerType: MapLayerType;
  averageValue: number;
  source: string;
  cloudCoverage: number;
}

export interface FieldBoundary {
  lat: number;
  lng: number;
}

export interface FarmonautField {
  id: string;
  fieldId: string;
  name: string;
  nameAr: string;
  cropType: string;
  cropTypeAr: string;
  growthStage: string;
  growthStageAr: string;
  area: number;
  center: { lat: number; lng: number };
  boundary: FieldBoundary[];
  lastImageDate: string;
  satelliteSource: string;
  cloudCoverage: number;
  ndvi: number;
  ndviChange: number;
  ndwi: number;
  evi: number;
  savi: number;
  soilMoisture: number;
  healthStatus: CropHealthStatus;
  healthScore: number;
  waterStressLevel: number;
  alerts: FarmonautAlert[];
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface FarmonautAlert {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  type: 'pest' | 'disease' | 'water_stress' | 'nutrient' | 'weather' | 'growth';
  typeAr: string;
  severity: AlertSeverity;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  recommendation: string;
  recommendationAr: string;
  detectedAt: string;
  isResolved: boolean;
}

export interface NDVITimeSeriesPoint {
  date: string;
  ndvi: number;
  evi?: number;
  ndwi?: number;
  cloudCoverage: number;
  source: string;
}

export interface WeatherForecast {
  date: string;
  condition: WeatherCondition;
  conditionAr: string;
  tempMin: number;
  tempMax: number;
  humidity: number;
  windSpeed: number;
  precipitation: number;
  sprayWindow: boolean;
}

export interface FieldZone {
  id: string;
  zoneName: string;
  zoneNameAr: string;
  area: number;
  ndvi: number;
  healthStatus: CropHealthStatus;
  recommendation: string;
  recommendationAr: string;
  color: string;
}

export interface FarmonautDashboardStats {
  totalFields: number;
  totalArea: number;
  averageNdvi: number;
  ndviTrend: 'up' | 'down' | 'stable';
  averageHealthScore: number;
  fieldsHealthy: number;
  fieldsStressed: number;
  fieldsCritical: number;
  activeAlerts: number;
  lastSatellitePass: string;
  waterStressFields: number;
  nextSatellitePass: string;
}

export interface FieldReport {
  id: string;
  fieldId: string;
  title: string;
  titleAr: string;
  generatedAt: string;
  period: { from: string; to: string };
  summary: string;
  summaryAr: string;
  ndviSummary: {
    average: number;
    min: number;
    max: number;
    trend: 'up' | 'down' | 'stable';
  };
  healthHistory: Array<{ date: string; score: number; status: CropHealthStatus }>;
  alerts: FarmonautAlert[];
  recommendations: Array<{ text: string; textAr: string; priority: AlertSeverity }>;
}

export interface FarmonautFilters {
  cropType?: string;
  healthStatus?: CropHealthStatus;
  search?: string;
  sortBy?: 'name' | 'ndvi' | 'healthScore' | 'area' | 'lastUpdate';
  sortOrder?: 'asc' | 'desc';
}
