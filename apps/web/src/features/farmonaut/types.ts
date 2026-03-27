/**
 * Satellite Monitoring - Types
 * أنواع بيانات مراقبة الأقمار الصناعية مراقبة الأقمار الصناعية
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

export interface SatelliteField {
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
  alerts: SatelliteAlert[];
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface SatelliteAlert {
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

export interface SatelliteDashboardStats {
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
  alerts: SatelliteAlert[];
  recommendations: Array<{ text: string; textAr: string; priority: AlertSeverity }>;
}

export interface SatelliteFilters {
  cropType?: string;
  healthStatus?: CropHealthStatus;
  search?: string;
  sortBy?: 'name' | 'ndvi' | 'healthScore' | 'area' | 'lastUpdate';
  sortOrder?: 'asc' | 'desc';
}

// ---------------------------------------------------------------------------
// Error Handling & API Response Types
// ---------------------------------------------------------------------------

export type SatelliteErrorCode =
  | 'NETWORK_ERROR'
  | 'AUTH_REQUIRED'
  | 'FIELD_NOT_FOUND'
  | 'SATELLITE_UNAVAILABLE'
  | 'WEATHER_SERVICE_DOWN'
  | 'AI_SERVICE_TIMEOUT'
  | 'RATE_LIMITED'
  | 'VALIDATION_ERROR'
  | 'CLOUD_COVERAGE_HIGH'
  | 'NO_SATELLITE_DATA'
  | 'PROCESSING_IN_PROGRESS';

export interface SatelliteError {
  code: SatelliteErrorCode;
  message: string;
  messageAr: string;
  retryable: boolean;
  retryAfterMs?: number;
}

export const SATELLITE_ERRORS: Record<SatelliteErrorCode, SatelliteError> = {
  NETWORK_ERROR: { code: 'NETWORK_ERROR', message: 'Network error. Using cached data.', messageAr: 'خطأ في الاتصال. استخدام البيانات المخزنة.', retryable: true, retryAfterMs: 5000 },
  AUTH_REQUIRED: { code: 'AUTH_REQUIRED', message: 'Authentication required.', messageAr: 'يلزم تسجيل الدخول.', retryable: false },
  FIELD_NOT_FOUND: { code: 'FIELD_NOT_FOUND', message: 'Field not found.', messageAr: 'الحقل غير موجود.', retryable: false },
  SATELLITE_UNAVAILABLE: { code: 'SATELLITE_UNAVAILABLE', message: 'Satellite data temporarily unavailable.', messageAr: 'بيانات الأقمار الصناعية غير متاحة مؤقتاً.', retryable: true, retryAfterMs: 30000 },
  WEATHER_SERVICE_DOWN: { code: 'WEATHER_SERVICE_DOWN', message: 'Weather service is unavailable.', messageAr: 'خدمة الطقس غير متاحة.', retryable: true, retryAfterMs: 10000 },
  AI_SERVICE_TIMEOUT: { code: 'AI_SERVICE_TIMEOUT', message: 'AI analysis timed out. Retrying...', messageAr: 'انتهت مهلة تحليل الذكاء الاصطناعي. جاري إعادة المحاولة...', retryable: true, retryAfterMs: 15000 },
  RATE_LIMITED: { code: 'RATE_LIMITED', message: 'Too many requests. Please wait.', messageAr: 'طلبات كثيرة. يرجى الانتظار.', retryable: true, retryAfterMs: 60000 },
  VALIDATION_ERROR: { code: 'VALIDATION_ERROR', message: 'Invalid input data.', messageAr: 'بيانات إدخال غير صالحة.', retryable: false },
  CLOUD_COVERAGE_HIGH: { code: 'CLOUD_COVERAGE_HIGH', message: 'High cloud coverage. Using SAR radar data instead.', messageAr: 'غطاء سحابي كثيف. استخدام بيانات الرادار بدلاً.', retryable: false },
  NO_SATELLITE_DATA: { code: 'NO_SATELLITE_DATA', message: 'No satellite data available for this date.', messageAr: 'لا توجد بيانات أقمار صناعية لهذا التاريخ.', retryable: false },
  PROCESSING_IN_PROGRESS: { code: 'PROCESSING_IN_PROGRESS', message: 'Image processing in progress. Check back in 1-2 hours.', messageAr: 'جاري معالجة الصور. تحقق بعد 1-2 ساعة.', retryable: true, retryAfterMs: 3600000 },
};

// ---------------------------------------------------------------------------
// Service Integration Mapping
// ---------------------------------------------------------------------------

/** Maps satellite monitoring features to SAHOOL backend microservices */
export interface ServiceEndpoint {
  service: string;
  serviceAr: string;
  port: number;
  basePath: string;
  healthCheck: string;
}

export const SATELLITE_SERVICE_MAP: Record<string, ServiceEndpoint> = {
  satellite: { service: 'vegetation-analysis-service', serviceAr: 'خدمة تحليل الغطاء النباتي', port: 8090, basePath: '/api/v1/vegetation', healthCheck: '/healthz' },
  weather: { service: 'weather-service', serviceAr: 'خدمة الطقس', port: 8092, basePath: '/api/v1/weather', healthCheck: '/healthz' },
  advisory: { service: 'advisory-service', serviceAr: 'خدمة الاستشارات', port: 8093, basePath: '/api/v1/advisory', healthCheck: '/healthz' },
  irrigation: { service: 'irrigation-smart', serviceAr: 'خدمة الري الذكي', port: 8094, basePath: '/api/v1/irrigation', healthCheck: '/healthz' },
  soil: { service: 'soil-analysis-service', serviceAr: 'خدمة تحليل التربة', port: 8134, basePath: '/api/v1/soil', healthCheck: '/healthz' },
  pests: { service: 'pest-detection-service', serviceAr: 'خدمة اكتشاف الآفات', port: 8125, basePath: '/api/v1/pest', healthCheck: '/healthz' },
  alerts: { service: 'alert-service', serviceAr: 'خدمة التنبيهات', port: 8113, basePath: '/api/v1/alerts', healthCheck: '/healthz' },
  yield: { service: 'yield-prediction-service', serviceAr: 'خدمة توقع الإنتاجية', port: 8152, basePath: '/api/v1/yield', healthCheck: '/healthz' },
  terrain: { service: 'terrain-core-service', serviceAr: 'خدمة التضاريس', port: 8185, basePath: '/api/v1/terrain', healthCheck: '/healthz' },
  vision: { service: 'yolo26-vision-service', serviceAr: 'خدمة الرؤية الحاسوبية', port: 8150, basePath: '/api/v1/vision', healthCheck: '/healthz' },
  cropIntelligence: { service: 'crop-intelligence-service', serviceAr: 'خدمة ذكاء المحاصيل', port: 8095, basePath: '/api/v1/crop-intelligence', healthCheck: '/healthz' },
};

// ---------------------------------------------------------------------------
// Data Source & Quality Tracking
// ---------------------------------------------------------------------------

export type DataSource = 'live' | 'cache' | 'mock' | 'sar_fallback';

export interface DataMeta {
  source: DataSource;
  fetchedAt: string;
  staleAfterMs: number;
  serviceHealth: 'healthy' | 'degraded' | 'offline';
}

export interface WeatherHourly {
  hour: string;
  temp: number;
  humidity: number;
  windSpeed: number;
  precipitation: number;
  condition: WeatherCondition;
}

export interface WeatherForecastExtended extends WeatherForecast {
  hourly?: WeatherHourly[];
  uvIndex?: number;
  dewPoint?: number;
  pressure?: number;
  sunrise?: string;
  sunset?: string;
}
