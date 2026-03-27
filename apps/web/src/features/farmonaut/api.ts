/**
 * Farmonaut Satellite Monitoring - API Layer
 * طبقة API لمراقبة الأقمار الصناعية فارمونوت
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { API_PREFIX } from '@sahool/shared-types/contracts';
import type {
  FarmonautField,
  FarmonautDashboardStats,
  FarmonautAlert,
  NDVITimeSeriesPoint,
  WeatherForecast,
  FieldZone,
  FieldReport,
  FarmonautFilters,
  ReportFormat,
  TimePeriod,
  DirectionGridAnalysis,
  DirectionZoneData,
  SoilAnalysis,
  PestPrediction,
  IrrigationSchedule,
  YieldPrediction,
  FieldSetupData,
  HistoricalSnapshot,
  MapLayerType,
  HybridColorMeaning,
} from './types';

const api = createApiClient({ timeout: 15000 });

// ---------------------------------------------------------------------------
// Mock Data - used when API is unavailable (offline-first)
// ---------------------------------------------------------------------------

const MOCK_FIELDS: FarmonautField[] = [
  {
    id: 'fm-001',
    fieldId: 'field-001',
    name: 'Al-Rashid Wheat Field',
    nameAr: 'حقل القمح الراشد',
    cropType: 'wheat',
    cropTypeAr: 'قمح',
    growthStage: 'Tillering',
    growthStageAr: 'التفريع',
    area: 15.5,
    center: { lat: 24.7136, lng: 46.6753 },
    boundary: [
      { lat: 24.71, lng: 46.67 },
      { lat: 24.71, lng: 46.68 },
      { lat: 24.72, lng: 46.68 },
      { lat: 24.72, lng: 46.67 },
    ],
    lastImageDate: '2026-03-25',
    satelliteSource: 'Sentinel-2',
    cloudCoverage: 5,
    ndvi: 0.78,
    ndviChange: 0.05,
    ndwi: 0.32,
    evi: 0.65,
    savi: 0.58,
    soilMoisture: 45,
    healthStatus: 'healthy',
    healthScore: 92,
    waterStressLevel: 12,
    alerts: [],
    metadata: {},
    createdAt: '2025-10-01T00:00:00Z',
    updatedAt: '2026-03-25T10:00:00Z',
  },
  {
    id: 'fm-002',
    fieldId: 'field-002',
    name: 'Southern Barley Field',
    nameAr: 'حقل الشعير الجنوبي',
    cropType: 'barley',
    cropTypeAr: 'شعير',
    growthStage: 'Heading',
    growthStageAr: 'طرد السنابل',
    area: 12.3,
    center: { lat: 24.72, lng: 46.68 },
    boundary: [
      { lat: 24.715, lng: 46.675 },
      { lat: 24.715, lng: 46.685 },
      { lat: 24.725, lng: 46.685 },
      { lat: 24.725, lng: 46.675 },
    ],
    lastImageDate: '2026-03-25',
    satelliteSource: 'Sentinel-2',
    cloudCoverage: 8,
    ndvi: 0.62,
    ndviChange: -0.03,
    ndwi: 0.18,
    evi: 0.52,
    savi: 0.45,
    soilMoisture: 35,
    healthStatus: 'moderate',
    healthScore: 72,
    waterStressLevel: 35,
    alerts: [],
    metadata: {},
    createdAt: '2025-10-01T00:00:00Z',
    updatedAt: '2026-03-25T10:00:00Z',
  },
  {
    id: 'fm-003',
    fieldId: 'field-003',
    name: 'Northern Tomato Plot',
    nameAr: 'قطعة الطماطم الشمالية',
    cropType: 'tomato',
    cropTypeAr: 'طماطم',
    growthStage: 'Fruiting',
    growthStageAr: 'الإثمار',
    area: 8.7,
    center: { lat: 24.705, lng: 46.67 },
    boundary: [
      { lat: 24.70, lng: 46.665 },
      { lat: 24.70, lng: 46.675 },
      { lat: 24.71, lng: 46.675 },
      { lat: 24.71, lng: 46.665 },
    ],
    lastImageDate: '2026-03-24',
    satelliteSource: 'Sentinel-2',
    cloudCoverage: 12,
    ndvi: 0.41,
    ndviChange: -0.09,
    ndwi: -0.05,
    evi: 0.35,
    savi: 0.30,
    soilMoisture: 22,
    healthStatus: 'stressed',
    healthScore: 48,
    waterStressLevel: 65,
    alerts: [
      {
        id: 'alert-001',
        fieldId: 'field-003',
        fieldName: 'Northern Tomato Plot',
        fieldNameAr: 'قطعة الطماطم الشمالية',
        type: 'water_stress',
        typeAr: 'إجهاد مائي',
        severity: 'warning',
        title: 'Water Stress Detected',
        titleAr: 'تم اكتشاف إجهاد مائي',
        description: 'NDWI values indicate significant water stress in the field.',
        descriptionAr: 'تشير قيم NDWI إلى إجهاد مائي كبير في الحقل.',
        recommendation: 'Increase irrigation frequency. Apply 25mm water within 24 hours.',
        recommendationAr: 'زيادة وتيرة الري. تطبيق 25 مم من المياه خلال 24 ساعة.',
        detectedAt: '2026-03-24T08:00:00Z',
        isResolved: false,
      },
      {
        id: 'alert-002',
        fieldId: 'field-003',
        fieldName: 'Northern Tomato Plot',
        fieldNameAr: 'قطعة الطماطم الشمالية',
        type: 'disease',
        typeAr: 'مرض',
        severity: 'advisory',
        title: 'Possible Leaf Blight Risk',
        titleAr: 'خطر محتمل لآفة الأوراق',
        description: 'Declining NDVI trend with moderate humidity suggests disease risk.',
        descriptionAr: 'انخفاض اتجاه NDVI مع رطوبة معتدلة يشير إلى خطر الأمراض.',
        recommendation: 'Scout field for disease symptoms. Consider preventive fungicide.',
        recommendationAr: 'استكشاف الحقل لأعراض المرض. النظر في استخدام مبيد فطري وقائي.',
        detectedAt: '2026-03-24T10:00:00Z',
        isResolved: false,
      },
    ],
    metadata: {},
    createdAt: '2025-11-15T00:00:00Z',
    updatedAt: '2026-03-24T10:00:00Z',
  },
  {
    id: 'fm-004',
    fieldId: 'field-004',
    name: 'Date Palm Grove',
    nameAr: 'بستان النخيل',
    cropType: 'date_palm',
    cropTypeAr: 'نخيل',
    growthStage: 'Pollination',
    growthStageAr: 'التلقيح',
    area: 22.0,
    center: { lat: 24.73, lng: 46.69 },
    boundary: [
      { lat: 24.725, lng: 46.685 },
      { lat: 24.725, lng: 46.695 },
      { lat: 24.735, lng: 46.695 },
      { lat: 24.735, lng: 46.685 },
    ],
    lastImageDate: '2026-03-25',
    satelliteSource: 'Sentinel-2',
    cloudCoverage: 3,
    ndvi: 0.72,
    ndviChange: 0.02,
    ndwi: 0.28,
    evi: 0.60,
    savi: 0.55,
    soilMoisture: 40,
    healthStatus: 'healthy',
    healthScore: 85,
    waterStressLevel: 18,
    alerts: [],
    metadata: {},
    createdAt: '2025-09-01T00:00:00Z',
    updatedAt: '2026-03-25T10:00:00Z',
  },
  {
    id: 'fm-005',
    fieldId: 'field-005',
    name: 'Eastern Cucumber Field',
    nameAr: 'حقل الخيار الشرقي',
    cropType: 'cucumber',
    cropTypeAr: 'خيار',
    growthStage: 'Vegetative',
    growthStageAr: 'النمو الخضري',
    area: 5.2,
    center: { lat: 24.695, lng: 46.695 },
    boundary: [
      { lat: 24.69, lng: 46.69 },
      { lat: 24.69, lng: 46.70 },
      { lat: 24.70, lng: 46.70 },
      { lat: 24.70, lng: 46.69 },
    ],
    lastImageDate: '2026-03-23',
    satelliteSource: 'Sentinel-2',
    cloudCoverage: 15,
    ndvi: 0.28,
    ndviChange: -0.12,
    ndwi: -0.10,
    evi: 0.22,
    savi: 0.20,
    soilMoisture: 18,
    healthStatus: 'critical',
    healthScore: 30,
    waterStressLevel: 82,
    alerts: [
      {
        id: 'alert-003',
        fieldId: 'field-005',
        fieldName: 'Eastern Cucumber Field',
        fieldNameAr: 'حقل الخيار الشرقي',
        type: 'water_stress',
        typeAr: 'إجهاد مائي',
        severity: 'critical',
        title: 'Severe Water Stress',
        titleAr: 'إجهاد مائي حاد',
        description: 'Critical water deficit detected. Immediate irrigation required.',
        descriptionAr: 'تم اكتشاف عجز مائي حرج. يلزم الري الفوري.',
        recommendation: 'Emergency irrigation: Apply 40mm immediately. Check irrigation system.',
        recommendationAr: 'ري طارئ: تطبيق 40 مم فوراً. فحص نظام الري.',
        detectedAt: '2026-03-23T06:00:00Z',
        isResolved: false,
      },
      {
        id: 'alert-004',
        fieldId: 'field-005',
        fieldName: 'Eastern Cucumber Field',
        fieldNameAr: 'حقل الخيار الشرقي',
        type: 'pest',
        typeAr: 'آفة',
        severity: 'warning',
        title: 'Aphid Infestation Risk',
        titleAr: 'خطر إصابة بالمن',
        description: 'Stressed crops are vulnerable to aphid infestations.',
        descriptionAr: 'المحاصيل المجهدة عرضة للإصابة بالمن.',
        recommendation: 'Monitor for aphids. Apply neem oil as preventive measure.',
        recommendationAr: 'مراقبة المن. تطبيق زيت النيم كإجراء وقائي.',
        detectedAt: '2026-03-23T10:00:00Z',
        isResolved: false,
      },
    ],
    metadata: {},
    createdAt: '2026-01-10T00:00:00Z',
    updatedAt: '2026-03-23T10:00:00Z',
  },
];

const MOCK_STATS: FarmonautDashboardStats = {
  totalFields: 5,
  totalArea: 63.7,
  averageNdvi: 0.56,
  ndviTrend: 'stable',
  averageHealthScore: 65,
  fieldsHealthy: 2,
  fieldsStressed: 2,
  fieldsCritical: 1,
  activeAlerts: 4,
  lastSatellitePass: '2026-03-25T09:30:00Z',
  waterStressFields: 2,
  nextSatellitePass: '2026-03-27T09:45:00Z',
};

const MOCK_TIMESERIES: NDVITimeSeriesPoint[] = [
  { date: '2026-01-01', ndvi: 0.35, evi: 0.28, ndwi: 0.15, cloudCoverage: 10, source: 'Sentinel-2' },
  { date: '2026-01-15', ndvi: 0.42, evi: 0.34, ndwi: 0.20, cloudCoverage: 5, source: 'Sentinel-2' },
  { date: '2026-02-01', ndvi: 0.50, evi: 0.42, ndwi: 0.25, cloudCoverage: 8, source: 'Sentinel-2' },
  { date: '2026-02-15', ndvi: 0.58, evi: 0.48, ndwi: 0.30, cloudCoverage: 12, source: 'Sentinel-2' },
  { date: '2026-03-01', ndvi: 0.68, evi: 0.56, ndwi: 0.28, cloudCoverage: 3, source: 'Sentinel-2' },
  { date: '2026-03-10', ndvi: 0.73, evi: 0.60, ndwi: 0.30, cloudCoverage: 7, source: 'Sentinel-2' },
  { date: '2026-03-20', ndvi: 0.76, evi: 0.63, ndwi: 0.32, cloudCoverage: 5, source: 'Sentinel-2' },
  { date: '2026-03-25', ndvi: 0.78, evi: 0.65, ndwi: 0.32, cloudCoverage: 5, source: 'Sentinel-2' },
];

const MOCK_WEATHER: WeatherForecast[] = [
  { date: '2026-03-27', condition: 'sunny', conditionAr: 'مشمس', tempMin: 18, tempMax: 32, humidity: 25, windSpeed: 12, precipitation: 0, sprayWindow: true },
  { date: '2026-03-28', condition: 'sunny', conditionAr: 'مشمس', tempMin: 19, tempMax: 34, humidity: 22, windSpeed: 8, precipitation: 0, sprayWindow: true },
  { date: '2026-03-29', condition: 'partly_cloudy', conditionAr: 'غائم جزئياً', tempMin: 20, tempMax: 33, humidity: 30, windSpeed: 15, precipitation: 0, sprayWindow: true },
  { date: '2026-03-30', condition: 'cloudy', conditionAr: 'غائم', tempMin: 17, tempMax: 28, humidity: 45, windSpeed: 20, precipitation: 5, sprayWindow: false },
  { date: '2026-03-31', condition: 'rainy', conditionAr: 'ماطر', tempMin: 15, tempMax: 24, humidity: 65, windSpeed: 25, precipitation: 15, sprayWindow: false },
  { date: '2026-04-01', condition: 'partly_cloudy', conditionAr: 'غائم جزئياً', tempMin: 16, tempMax: 27, humidity: 40, windSpeed: 10, precipitation: 2, sprayWindow: true },
  { date: '2026-04-02', condition: 'sunny', conditionAr: 'مشمس', tempMin: 18, tempMax: 31, humidity: 28, windSpeed: 8, precipitation: 0, sprayWindow: true },
];

const MOCK_ZONES: FieldZone[] = [
  { id: 'z1', zoneName: 'Zone A - North', zoneNameAr: 'المنطقة أ - شمال', area: 4.2, ndvi: 0.82, healthStatus: 'healthy', recommendation: 'Maintain current practices', recommendationAr: 'الحفاظ على الممارسات الحالية', color: '#22c55e' },
  { id: 'z2', zoneName: 'Zone B - Center', zoneNameAr: 'المنطقة ب - وسط', area: 6.1, ndvi: 0.75, healthStatus: 'healthy', recommendation: 'Monitor nitrogen levels', recommendationAr: 'مراقبة مستويات النيتروجين', color: '#4ade80' },
  { id: 'z3', zoneName: 'Zone C - South', zoneNameAr: 'المنطقة ج - جنوب', area: 3.5, ndvi: 0.55, healthStatus: 'moderate', recommendation: 'Increase irrigation by 15%', recommendationAr: 'زيادة الري بنسبة 15%', color: '#eab308' },
  { id: 'z4', zoneName: 'Zone D - Edge', zoneNameAr: 'المنطقة د - الحافة', area: 1.7, ndvi: 0.38, healthStatus: 'stressed', recommendation: 'Apply foliar fertilizer', recommendationAr: 'تطبيق سماد ورقي', color: '#f97316' },
];

// ---------------------------------------------------------------------------
// API Functions
// ---------------------------------------------------------------------------

export const farmonautApi = {
  getFields: async (filters?: FarmonautFilters): Promise<FarmonautField[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      if (filters?.healthStatus) params.set('health_status', filters.healthStatus);
      if (filters?.search) params.set('search', filters.search);
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.sortOrder) params.set('sort_order', filters.sortOrder);

      const response = await api.get(`${API_PREFIX}/farmonaut/fields?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;

      logger.warn('Farmonaut API returned unexpected format, using mock data');
      return MOCK_FIELDS;
    } catch (error) {
      logger.warn('Failed to fetch farmonaut fields, using mock data:', error);
      return MOCK_FIELDS;
    }
  },

  getFieldById: async (id: string): Promise<FarmonautField> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch farmonaut field ${id}, using mock data:`, error);
      const mock = MOCK_FIELDS.find((f) => f.id === id || f.fieldId === id);
      if (mock) return mock;
      return MOCK_FIELDS[0];
    }
  },

  getStats: async (): Promise<FarmonautDashboardStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch farmonaut stats, using mock data:', error);
      return MOCK_STATS;
    }
  },

  getAlerts: async (fieldId?: string): Promise<FarmonautAlert[]> => {
    try {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${API_PREFIX}/farmonaut/alerts${params}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch alerts, using mock data:', error);
      const allAlerts = MOCK_FIELDS.flatMap((f) => f.alerts);
      return fieldId ? allAlerts.filter((a) => a.fieldId === fieldId) : allAlerts;
    }
  },

  getTimeSeries: async (
    fieldId: string,
    period: TimePeriod
  ): Promise<NDVITimeSeriesPoint[]> => {
    try {
      const response = await api.get(
        `${API_PREFIX}/farmonaut/fields/${fieldId}/timeseries?period=${period}`
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch timeseries for ${fieldId}, using mock data:`, error);
      return MOCK_TIMESERIES;
    }
  },

  getWeatherForecast: async (fieldId: string): Promise<WeatherForecast[]> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${fieldId}/weather`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch weather for ${fieldId}, using mock data:`, error);
      return MOCK_WEATHER;
    }
  },

  getFieldZones: async (fieldId: string): Promise<FieldZone[]> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${fieldId}/zones`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch zones for ${fieldId}, using mock data:`, error);
      return MOCK_ZONES;
    }
  },

  generateReport: async (
    fieldId: string,
    period: TimePeriod,
    format: ReportFormat
  ): Promise<FieldReport> => {
    try {
      const response = await api.post(`${API_PREFIX}/farmonaut/fields/${fieldId}/report`, {
        period,
        format,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to generate report for ${fieldId}:`, error);
      throw error;
    }
  },

  resolveAlert: async (alertId: string): Promise<void> => {
    try {
      await api.patch(`${API_PREFIX}/farmonaut/alerts/${alertId}/resolve`);
    } catch (error) {
      logger.error(`Failed to resolve alert ${alertId}:`, error);
      throw error;
    }
  },

  getDirectionGrid: async (fieldId: string, layerType: MapLayerType): Promise<DirectionGridAnalysis> => {
    try {
      const response = await api.get(
        `${API_PREFIX}/farmonaut/fields/${fieldId}/direction-grid?layer=${layerType}`
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch direction grid for ${fieldId}, using mock data:`, error);
      return MOCK_DIRECTION_GRID;
    }
  },

  getSoilAnalysis: async (fieldId: string): Promise<SoilAnalysis> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${fieldId}/soil`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch soil analysis for ${fieldId}, using mock data:`, error);
      return MOCK_SOIL_ANALYSIS;
    }
  },

  getPestPredictions: async (fieldId: string): Promise<PestPrediction[]> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${fieldId}/pest-predictions`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch pest predictions for ${fieldId}, using mock data:`, error);
      return MOCK_PEST_PREDICTIONS;
    }
  },

  getIrrigationSchedule: async (fieldId: string): Promise<IrrigationSchedule> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${fieldId}/irrigation-schedule`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch irrigation schedule for ${fieldId}, using mock data:`, error);
      return MOCK_IRRIGATION_SCHEDULE;
    }
  },

  getYieldPrediction: async (fieldId: string): Promise<YieldPrediction> => {
    try {
      const response = await api.get(`${API_PREFIX}/farmonaut/fields/${fieldId}/yield-prediction`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch yield prediction for ${fieldId}, using mock data:`, error);
      return MOCK_YIELD_PREDICTION;
    }
  },

  getHistoricalData: async (
    fieldId: string,
    startDate: string,
    endDate: string,
    layerType: MapLayerType
  ): Promise<HistoricalSnapshot[]> => {
    try {
      const params = new URLSearchParams({ start: startDate, end: endDate, layer: layerType });
      const response = await api.get(
        `${API_PREFIX}/farmonaut/fields/${fieldId}/historical?${params.toString()}`
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch historical data for ${fieldId}, using mock data:`, error);
      return MOCK_HISTORICAL;
    }
  },

  createField: async (data: FieldSetupData): Promise<FarmonautField> => {
    const response = await api.post(`${API_PREFIX}/farmonaut/fields`, data);
    return response.data.data || response.data;
  },

  updateField: async (fieldId: string, data: Partial<FieldSetupData>): Promise<FarmonautField> => {
    const response = await api.patch(`${API_PREFIX}/farmonaut/fields/${fieldId}`, data);
    return response.data.data || response.data;
  },
};

// ---------------------------------------------------------------------------
// Hybrid Index Color Definitions
// ---------------------------------------------------------------------------
export const HYBRID_COLORS: HybridColorMeaning[] = [
  { color: 'green', hex: '#22c55e', meaning: 'Good crop health & good irrigation', meaningAr: 'صحة محصول جيدة وري جيد' },
  { color: 'orange', hex: '#f97316', meaning: 'Crop health needs attention', meaningAr: 'صحة المحصول تتطلب انتباه' },
  { color: 'purple', hex: '#a855f7', meaning: 'Irrigation needs attention', meaningAr: 'الري يتطلب انتباه' },
  { color: 'red', hex: '#ef4444', meaning: 'Both health & irrigation need attention / Cloud / No crop', meaningAr: 'الصحة والري يتطلبان انتباه / غطاء سحابي / لا محصول' },
  { color: 'white', hex: '#f8fafc', meaning: 'Cloud cover blocking view', meaningAr: 'غطاء سحابي يحجب الرؤية' },
];

// ---------------------------------------------------------------------------
// Map Layer Configuration
// ---------------------------------------------------------------------------
export interface MapLayerConfig {
  type: MapLayerType;
  label: string;
  labelAr: string;
  group: string;
  groupAr: string;
  description: string;
  descriptionAr: string;
  colorStops: Array<{ value: number; color: string; label: string; labelAr: string }>;
}

export const MAP_LAYERS: MapLayerConfig[] = [
  // ── Basic Analysis ──
  {
    type: 'hybrid',
    label: 'Hybrid Index',
    labelAr: 'المؤشر الهجين',
    group: 'Basic Analysis',
    groupAr: 'التحليل الأساسي',
    description: 'Combined crop health + irrigation status for beginners',
    descriptionAr: 'صحة المحصول والري في صورة واحدة - للمبتدئين',
    colorStops: [
      { value: 0, color: '#ef4444', label: 'Critical', labelAr: 'حرج / لا محصول' },
      { value: 0.3, color: '#f97316', label: 'Crop Attention', labelAr: 'انتباه للمحصول' },
      { value: 0.5, color: '#a855f7', label: 'Irrigation Attention', labelAr: 'انتباه للري' },
      { value: 0.7, color: '#22c55e', label: 'Good', labelAr: 'جيد' },
      { value: 1.0, color: '#f8fafc', label: 'Cloud', labelAr: 'غطاء سحابي' },
    ],
  },
  // ── Colorblind Visualization ──
  {
    type: 'colorblind',
    label: 'Colorblind Visualization',
    labelAr: 'تصور لعمى الألوان',
    group: 'Basic Analysis',
    groupAr: 'التحليل الأساسي',
    description: 'Colorblind-friendly field visualization',
    descriptionAr: 'تصور ملائم لمن يعانون من عمى الألوان',
    colorStops: [
      { value: 0, color: '#0077BB', label: 'Low', labelAr: 'منخفض' },
      { value: 0.5, color: '#EE7733', label: 'Medium', labelAr: 'متوسط' },
      { value: 1.0, color: '#009988', label: 'High', labelAr: 'مرتفع' },
    ],
  },
  // ── Colored Satellite Image ──
  {
    type: 'tci',
    label: 'TCI - True Color',
    labelAr: 'صورة الألوان الحقيقية',
    group: 'Satellite Image',
    groupAr: 'صورة القمر الصناعي',
    description: 'True Color Image from satellite',
    descriptionAr: 'صورة الألوان الحقيقية من القمر الصناعي',
    colorStops: [
      { value: 0, color: '#6b7280', label: 'Natural colors', labelAr: 'ألوان طبيعية' },
    ],
  },
  {
    type: 'etci',
    label: 'ETCI - Enhanced True Color',
    labelAr: 'صورة الألوان المحسنة',
    group: 'Satellite Image',
    groupAr: 'صورة القمر الصناعي',
    description: 'Enhanced True Color Image with better contrast',
    descriptionAr: 'صورة ألوان محسنة بتباين أفضل',
    colorStops: [
      { value: 0, color: '#6b7280', label: 'Enhanced colors', labelAr: 'ألوان محسنة' },
    ],
  },
  // ── Crop Health (Early Growth) ──
  {
    type: 'ndvi',
    label: 'NDVI',
    labelAr: 'مؤشر الغطاء النباتي',
    group: 'Crop Health (Early)',
    groupAr: 'صحة المحصول (مبكر)',
    description: 'Vegetation health - best for early growth stages',
    descriptionAr: 'صحة النبات - الأفضل في المراحل المبكرة',
    colorStops: [
      { value: 0, color: '#dc2626', label: 'No vegetation', labelAr: 'لا غطاء نباتي' },
      { value: 0.2, color: '#f97316', label: 'Sparse', labelAr: 'متناثر' },
      { value: 0.4, color: '#eab308', label: 'Moderate', labelAr: 'متوسط' },
      { value: 0.6, color: '#22c55e', label: 'Dense', labelAr: 'كثيف' },
      { value: 0.8, color: '#15803d', label: 'Very dense', labelAr: 'كثيف جداً' },
    ],
  },
  {
    type: 'evi',
    label: 'EVI',
    labelAr: 'مؤشر الغطاء المحسن',
    group: 'Crop Health (Early)',
    groupAr: 'صحة المحصول (مبكر)',
    description: 'Enhanced vegetation index with atmospheric correction',
    descriptionAr: 'مؤشر الغطاء النباتي مع تصحيح جوي',
    colorStops: [
      { value: 0, color: '#dc2626', label: 'Poor', labelAr: 'ضعيف' },
      { value: 0.2, color: '#f97316', label: 'Low', labelAr: 'منخفض' },
      { value: 0.4, color: '#eab308', label: 'Moderate', labelAr: 'متوسط' },
      { value: 0.6, color: '#22c55e', label: 'Good', labelAr: 'جيد' },
    ],
  },
  {
    type: 'savi',
    label: 'SAVI',
    labelAr: 'مؤشر الغطاء المعدل للتربة',
    group: 'Crop Health (Early)',
    groupAr: 'صحة المحصول (مبكر)',
    description: 'Soil-adjusted vegetation index - best for arid environments',
    descriptionAr: 'مؤشر نباتي معدل للتربة - مناسب للبيئة الجافة',
    colorStops: [
      { value: 0, color: '#dc2626', label: 'Poor', labelAr: 'ضعيف' },
      { value: 0.2, color: '#f97316', label: 'Low', labelAr: 'منخفض' },
      { value: 0.4, color: '#eab308', label: 'Moderate', labelAr: 'متوسط' },
      { value: 0.6, color: '#22c55e', label: 'Good', labelAr: 'جيد' },
    ],
  },
  // ── Crop Health (Late Growth) ──
  {
    type: 'ndre',
    label: 'NDRE',
    labelAr: 'مؤشر الحافة الحمراء',
    group: 'Crop Health (Late)',
    groupAr: 'صحة المحصول (متأخر)',
    description: 'Best for dense canopy crops (soybean, corn) & late growth stages',
    descriptionAr: 'الأفضل للمحاصيل الكثيفة (فول الصويا، الذرة) والمراحل المتأخرة',
    colorStops: [
      { value: 0, color: '#dc2626', label: 'Poor', labelAr: 'ضعيف' },
      { value: 0.15, color: '#f97316', label: 'Low', labelAr: 'منخفض' },
      { value: 0.3, color: '#eab308', label: 'Moderate', labelAr: 'متوسط' },
      { value: 0.5, color: '#22c55e', label: 'Good', labelAr: 'جيد' },
    ],
  },
  {
    type: 'ndwi',
    label: 'NDWI',
    labelAr: 'مؤشر نقص المياه',
    group: 'Water & Irrigation',
    groupAr: 'المياه والري',
    description: 'Identifies areas with water deficit',
    descriptionAr: 'يحدد المناطق التي تعاني من نقص المياه',
    colorStops: [
      { value: -0.3, color: '#dc2626', label: 'Severe deficit', labelAr: 'عجز شديد' },
      { value: -0.1, color: '#f97316', label: 'Deficit', labelAr: 'عجز' },
      { value: 0.1, color: '#eab308', label: 'Adequate', labelAr: 'كافٍ' },
      { value: 0.3, color: '#3b82f6', label: 'Good', labelAr: 'جيد' },
      { value: 0.5, color: '#1d4ed8', label: 'Saturated', labelAr: 'مشبع' },
    ],
  },
  {
    type: 'evapotranspiration',
    label: 'Evapotranspiration',
    labelAr: 'النتح التبخري',
    group: 'Water & Irrigation',
    groupAr: 'المياه والري',
    description: 'Water evaporation rate from plants and soil',
    descriptionAr: 'معدل تبخر المياه من النبات والتربة',
    colorStops: [
      { value: 0, color: '#dbeafe', label: 'Low', labelAr: 'منخفض' },
      { value: 3, color: '#60a5fa', label: 'Moderate', labelAr: 'متوسط' },
      { value: 5, color: '#2563eb', label: 'High', labelAr: 'مرتفع' },
      { value: 8, color: '#1e3a8a', label: 'Very high', labelAr: 'مرتفع جداً' },
    ],
  },
  {
    type: 'ndmi',
    label: 'NDMI',
    labelAr: 'مؤشر رطوبة التربة',
    group: 'Water & Irrigation',
    groupAr: 'المياه والري',
    description: 'Soil moisture content',
    descriptionAr: 'محتوى رطوبة التربة',
    colorStops: [
      { value: -0.2, color: '#dc2626', label: 'Dry', labelAr: 'جاف' },
      { value: 0, color: '#f97316', label: 'Low moisture', labelAr: 'رطوبة منخفضة' },
      { value: 0.2, color: '#60a5fa', label: 'Moderate', labelAr: 'متوسط' },
      { value: 0.4, color: '#2563eb', label: 'Moist', labelAr: 'رطب' },
    ],
  },
  // ── Soil Health ──
  {
    type: 'soc',
    label: 'Soil Organic Carbon',
    labelAr: 'الكربون العضوي للتربة',
    group: 'Soil Health',
    groupAr: 'صحة التربة',
    description: 'Carbon content - low areas ideal for soil sampling (pre-sowing & post-harvest)',
    descriptionAr: 'محتوى الكربون - المناطق المنخفضة مثالية لأخذ عينات التربة (قبل البذر وبعد الحصاد)',
    colorStops: [
      { value: 0.5, color: '#fef3c7', label: 'Very low', labelAr: 'منخفض جداً' },
      { value: 1.0, color: '#d97706', label: 'Low', labelAr: 'منخفض' },
      { value: 2.0, color: '#92400e', label: 'Moderate', labelAr: 'متوسط' },
      { value: 3.0, color: '#451a03', label: 'High', labelAr: 'مرتفع' },
    ],
  },
  // ── Advanced Analysis ──
  {
    type: 'erosion',
    label: 'Soil Erosion',
    labelAr: 'تآكل التربة',
    group: 'Advanced Analysis',
    groupAr: 'تحليل متقدم',
    description: 'Soil erosion risk assessment',
    descriptionAr: 'تقييم مخاطر تآكل التربة',
    colorStops: [
      { value: 0, color: '#22c55e', label: 'Low risk', labelAr: 'مخاطر منخفضة' },
      { value: 30, color: '#eab308', label: 'Moderate', labelAr: 'متوسط' },
      { value: 60, color: '#f97316', label: 'High', labelAr: 'مرتفع' },
      { value: 90, color: '#dc2626', label: 'Severe', labelAr: 'شديد' },
    ],
  },
  // ── Topography ──
  {
    type: 'dem',
    label: 'Digital Elevation Model',
    labelAr: 'نموذج الارتفاع الرقمي',
    group: 'Topography',
    groupAr: 'التضاريس',
    description: 'Farm topography - detect water pooling areas',
    descriptionAr: 'تضاريس المزرعة - كشف مناطق تجمع المياه',
    colorStops: [
      { value: 0, color: '#2563eb', label: 'Low', labelAr: 'منخفض' },
      { value: 50, color: '#22c55e', label: 'Medium', labelAr: 'متوسط' },
      { value: 100, color: '#92400e', label: 'High', labelAr: 'مرتفع' },
    ],
  },
  {
    type: 'sar_rvi',
    label: 'SAR - Crop Health (RVI)',
    labelAr: 'رادار - صحة المحصول',
    group: 'Radar (SAR)',
    groupAr: 'الرادار',
    description: 'Radar vegetation index - works through clouds',
    descriptionAr: 'مؤشر الغطاء النباتي بالرادار - يعمل عبر السحب',
    colorStops: [
      { value: 0, color: '#6b7280', label: 'No vegetation', labelAr: 'لا غطاء' },
      { value: 0.3, color: '#9ca3af', label: 'Sparse', labelAr: 'متناثر' },
      { value: 0.6, color: '#4ade80', label: 'Moderate', labelAr: 'متوسط' },
      { value: 0.9, color: '#15803d', label: 'Dense', labelAr: 'كثيف' },
    ],
  },
  {
    type: 'sar_rsm',
    label: 'SAR - Soil Moisture (RSM)',
    labelAr: 'رادار - رطوبة التربة',
    group: 'Radar (SAR)',
    groupAr: 'الرادار',
    description: 'Radar soil moisture - works through clouds',
    descriptionAr: 'رطوبة التربة بالرادار - يعمل عبر السحب',
    colorStops: [
      { value: 0, color: '#fecaca', label: 'Dry', labelAr: 'جاف' },
      { value: 20, color: '#fde68a', label: 'Low', labelAr: 'منخفض' },
      { value: 40, color: '#93c5fd', label: 'Moderate', labelAr: 'متوسط' },
      { value: 60, color: '#1d4ed8', label: 'Wet', labelAr: 'رطب' },
    ],
  },
];

// ---------------------------------------------------------------------------
// Additional Mock Data
// ---------------------------------------------------------------------------

const MOCK_DIRECTION_GRID: DirectionGridAnalysis = {
  fieldId: 'field-001',
  analysisDate: '2026-03-25',
  layerType: 'ndvi',
  zones: [
    { zone: 'NW', label: 'North-West', labelAr: 'شمال غرب', ndvi: 0.82, healthStatus: 'healthy', irrigationNeeded: false, recommendation: 'Maintain current practices', recommendationAr: 'الحفاظ على الممارسات الحالية' },
    { zone: 'N', label: 'North', labelAr: 'شمال', ndvi: 0.78, healthStatus: 'healthy', irrigationNeeded: false, recommendation: 'Good condition', recommendationAr: 'حالة جيدة' },
    { zone: 'NE', label: 'North-East', labelAr: 'شمال شرق', ndvi: 0.75, healthStatus: 'healthy', irrigationNeeded: false, recommendation: 'Monitor next week', recommendationAr: 'مراقبة الأسبوع القادم' },
    { zone: 'W', label: 'West', labelAr: 'غرب', ndvi: 0.68, healthStatus: 'moderate', irrigationNeeded: true, recommendation: 'Increase irrigation by 10%', recommendationAr: 'زيادة الري بنسبة 10%' },
    { zone: 'C', label: 'Center', labelAr: 'وسط', ndvi: 0.80, healthStatus: 'healthy', irrigationNeeded: false, recommendation: 'Optimal condition', recommendationAr: 'حالة مثالية' },
    { zone: 'E', label: 'East', labelAr: 'شرق', ndvi: 0.72, healthStatus: 'moderate', irrigationNeeded: false, recommendation: 'Check nitrogen levels', recommendationAr: 'فحص مستويات النيتروجين' },
    { zone: 'SW', label: 'South-West', labelAr: 'جنوب غرب', ndvi: 0.55, healthStatus: 'stressed', irrigationNeeded: true, recommendation: 'Urgent: Apply 20mm irrigation', recommendationAr: 'عاجل: تطبيق 20 مم ري' },
    { zone: 'S', label: 'South', labelAr: 'جنوب', ndvi: 0.60, healthStatus: 'moderate', irrigationNeeded: true, recommendation: 'Increase irrigation', recommendationAr: 'زيادة الري' },
    { zone: 'SE', label: 'South-East', labelAr: 'جنوب شرق', ndvi: 0.65, healthStatus: 'moderate', irrigationNeeded: false, recommendation: 'Apply foliar fertilizer', recommendationAr: 'تطبيق سماد ورقي' },
  ],
};

const MOCK_SOIL_ANALYSIS: SoilAnalysis = {
  fieldId: 'field-001',
  analysisDate: '2026-03-20',
  nutrients: [
    { name: 'Nitrogen', nameAr: 'النيتروجين', symbol: 'N', value: 18, unit: 'ppm', optimalRange: { min: 25, max: 50 }, level: 'low', recommendation: 'Apply Urea 46% at 46 kg/ha', recommendationAr: 'تطبيق يوريا 46% بمعدل 46 كجم/هكتار' },
    { name: 'Phosphorus', nameAr: 'الفوسفور', symbol: 'P', value: 28, unit: 'ppm', optimalRange: { min: 20, max: 40 }, level: 'optimal', recommendation: 'Adequate levels', recommendationAr: 'مستويات كافية' },
    { name: 'Potassium', nameAr: 'البوتاسيوم', symbol: 'K', value: 155, unit: 'ppm', optimalRange: { min: 120, max: 200 }, level: 'optimal', recommendation: 'Adequate levels', recommendationAr: 'مستويات كافية' },
    { name: 'Zinc', nameAr: 'الزنك', symbol: 'Zn', value: 0.8, unit: 'ppm', optimalRange: { min: 1.0, max: 5.0 }, level: 'deficient', recommendation: 'Apply zinc sulfate 10 kg/ha', recommendationAr: 'تطبيق كبريتات الزنك 10 كجم/هكتار' },
    { name: 'Sulfur', nameAr: 'الكبريت', symbol: 'S', value: 12, unit: 'ppm', optimalRange: { min: 10, max: 30 }, level: 'adequate', recommendation: 'Monitor levels', recommendationAr: 'مراقبة المستويات' },
  ],
  ph: { value: 7.2, optimal: { min: 6.0, max: 7.5 }, level: 'optimal' },
  salinity: { value: 2.1, unit: 'dS/m', level: 'adequate' },
  organicCarbon: { value: 1.5, unit: '%', level: 'low' },
  overallHealth: 'moderate',
  fertilizerRecommendations: [
    { product: 'Urea 46%', productAr: 'يوريا 46%', quantity: 46, unit: 'kg/ha', timing: 'Immediately - top dressing', timingAr: 'فوراً - تسميد سطحي' },
    { product: 'Zinc Sulfate', productAr: 'كبريتات الزنك', quantity: 10, unit: 'kg/ha', timing: 'Within 1 week - foliar spray', timingAr: 'خلال أسبوع - رش ورقي' },
  ],
};

const MOCK_PEST_PREDICTIONS: PestPrediction[] = [
  { id: 'pp-001', fieldId: 'field-001', pestName: 'Wheat Rust', pestNameAr: 'صدأ القمح', riskLevel: 'warning', probability: 35, detectionSource: 'weather_pattern', preventiveAction: 'Apply preventive fungicide within 5 days', preventiveActionAr: 'تطبيق مبيد فطري وقائي خلال 5 أيام', estimatedDate: '2026-04-01' },
  { id: 'pp-002', fieldId: 'field-001', pestName: 'Aphids', pestNameAr: 'المن', riskLevel: 'advisory', probability: 20, detectionSource: 'ndvi_anomaly', preventiveAction: 'Scout field edges, apply neem oil if detected', preventiveActionAr: 'استكشاف حواف الحقل، تطبيق زيت النيم عند الاكتشاف', estimatedDate: '2026-04-05' },
];

const MOCK_IRRIGATION_SCHEDULE: IrrigationSchedule = {
  fieldId: 'field-001',
  nextIrrigation: '2026-03-28T06:00:00Z',
  amountMm: 25,
  durationHours: 4,
  factors: {
    weatherData: { temp: 32, humidity: 25, windSpeed: 12 },
    soilMoisture: 45,
    cropWaterNeed: 5.5,
    evapotranspiration: 6.2,
  },
  zones: [
    { zone: 'NW', priority: 'normal', amountMm: 20 },
    { zone: 'N', priority: 'normal', amountMm: 20 },
    { zone: 'NE', priority: 'normal', amountMm: 22 },
    { zone: 'W', priority: 'urgent', amountMm: 30 },
    { zone: 'C', priority: 'skip', amountMm: 15 },
    { zone: 'E', priority: 'normal', amountMm: 25 },
    { zone: 'SW', priority: 'urgent', amountMm: 35 },
    { zone: 'S', priority: 'urgent', amountMm: 30 },
    { zone: 'SE', priority: 'normal', amountMm: 25 },
  ],
};

const MOCK_YIELD_PREDICTION: YieldPrediction = {
  fieldId: 'field-001',
  cropType: 'wheat',
  cropTypeAr: 'قمح',
  predictedHeight: 85,
  heightUnit: 'cm',
  expectedYield: 69.75,
  yieldUnit: 'ton',
  yieldPerHectare: 4.5,
  plannedHarvestDate: '2026-05-15',
  confidencePercent: 82,
  trend: 'above_average',
};

const MOCK_HISTORICAL: HistoricalSnapshot[] = [
  { date: '2025-01-15', layerType: 'ndvi', averageValue: 0.15, source: 'Sentinel-2', cloudCoverage: 5 },
  { date: '2025-03-15', layerType: 'ndvi', averageValue: 0.55, source: 'Sentinel-2', cloudCoverage: 8 },
  { date: '2025-05-15', layerType: 'ndvi', averageValue: 0.72, source: 'Sentinel-2', cloudCoverage: 3 },
  { date: '2025-07-15', layerType: 'ndvi', averageValue: 0.10, source: 'Sentinel-2', cloudCoverage: 0 },
  { date: '2025-09-15', layerType: 'ndvi', averageValue: 0.12, source: 'Sentinel-2', cloudCoverage: 2 },
  { date: '2025-11-15', layerType: 'ndvi', averageValue: 0.30, source: 'Sentinel-2', cloudCoverage: 10 },
  { date: '2026-01-15', layerType: 'ndvi', averageValue: 0.42, source: 'Sentinel-2', cloudCoverage: 5 },
  { date: '2026-03-25', layerType: 'ndvi', averageValue: 0.78, source: 'Sentinel-2', cloudCoverage: 5 },
];
