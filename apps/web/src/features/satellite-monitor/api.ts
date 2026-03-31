/**
 * Satellite Monitoring - API Layer
 * طبقة API لمراقبة الأقمار الصناعية
 *
 * Backend Service Integration Map (from Component Unification Plan PR #1344):
 * ──────────────────────────────────────────────────────────────────────────
 * getFields/Stats      → copilot-api:8088 → field-management-service:3000
 * getTimeSeries        → vegetation-analysis-service:8090 /v1/timeseries/{fieldId}
 * getWeatherForecast   → weather-service:8092 POST /weather/forecast (days=8)
 * getSoilAnalysis      → soil-analysis-service:8134 POST /interpret
 * getPestPredictions   → crop-intelligence-service:8095 POST /api/v1/pests/assess
 * getIrrigationSchedule→ irrigation-smart:8094 POST /v1/calculate
 * getYieldPrediction   → crop-intelligence-service:8095 POST /api/v1/yield/predict
 * getDirectionGrid     → crop-intelligence-service:8095 GET /api/v1/fields/{id}/diagnosis
 * getHistoricalData    → vegetation-analysis-service:8090 /v1/ndvi-timeseries/analyze/{id}
 * getFieldZones        → terrain-core-service:8185 POST /api/v1/terrain/analyze
 *
 * SAR Fallback Logic (TODO — P1):
 * if cloudCoverage > 30% → GET vegetation-analysis:8090/v1/soil-moisture/{fieldId}
 * Uses Water Cloud Model calibrated for Yemen (A=15.0, B=8.5, C=-0.3)
 *
 * Copilot Integration (PR #1344):
 * All queries can also go through copilot-api:8088 POST /api/v1/chat
 * IntentRouter automatically routes to the correct expert service
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { API_PREFIX } from '@sahool/shared-types/contracts';
import type {
  SatelliteField,
  SatelliteDashboardStats,
  SatelliteAlert,
  NDVITimeSeriesPoint,
  WeatherForecast,
  FieldZone,
  FieldReport,
  SatelliteFilters,
  ReportFormat,
  TimePeriod,
  DirectionGridAnalysis,
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
// API Functions
// ---------------------------------------------------------------------------

export const satelliteMonitorApi = {
  getFields: async (filters?: SatelliteFilters): Promise<SatelliteField[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields`, async () => {
      const params = new URLSearchParams();
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      if (filters?.healthStatus) params.set('health_status', filters.healthStatus);
      if (filters?.search) params.set('search', filters.search);
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.sortOrder) params.set('sort_order', filters.sortOrder);
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getFieldById: async (id: string): Promise<SatelliteField> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${id}`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${id}`);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<SatelliteDashboardStats> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/stats`);
      return response.data.data || response.data;
    });
  },

  getAlerts: async (fieldId?: string): Promise<SatelliteAlert[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/alerts`, async () => {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${API_PREFIX}/satellite-monitor/alerts${params}`);
      return response.data.data || response.data;
    });
  },

  getTimeSeries: async (fieldId: string, period: TimePeriod): Promise<NDVITimeSeriesPoint[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/timeseries`, async () => {
      const response = await api.get(
        `${API_PREFIX}/satellite-monitor/fields/${fieldId}/timeseries?period=${period}`
      );
      return response.data.data || response.data;
    });
  },

  getWeatherForecast: async (fieldId: string): Promise<WeatherForecast[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/weather`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/weather`);
      return response.data.data || response.data;
    });
  },

  getFieldZones: async (fieldId: string): Promise<FieldZone[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/zones`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/zones`);
      return response.data.data || response.data;
    });
  },

  generateReport: async (fieldId: string, period: TimePeriod, format: ReportFormat): Promise<FieldReport> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/report`, async () => {
      const response = await api.post(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/report`, {
        period,
        format,
      });
      return response.data.data || response.data;
    });
  },

  resolveAlert: async (alertId: string): Promise<void> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/alerts/${alertId}/resolve`, async () => {
      await api.patch(`${API_PREFIX}/satellite-monitor/alerts/${alertId}/resolve`);
    });
  },

  getDirectionGrid: async (fieldId: string, layerType: MapLayerType): Promise<DirectionGridAnalysis> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/direction-grid`, async () => {
      const response = await api.get(
        `${API_PREFIX}/satellite-monitor/fields/${fieldId}/direction-grid?layer=${layerType}`
      );
      return response.data.data || response.data;
    });
  },

  getSoilAnalysis: async (fieldId: string): Promise<SoilAnalysis> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/soil`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/soil`);
      return response.data.data || response.data;
    });
  },

  getPestPredictions: async (fieldId: string): Promise<PestPrediction[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/pest-predictions`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/pest-predictions`);
      return response.data.data || response.data;
    });
  },

  getIrrigationSchedule: async (fieldId: string): Promise<IrrigationSchedule> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/irrigation-schedule`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/irrigation-schedule`);
      return response.data.data || response.data;
    });
  },

  getYieldPrediction: async (fieldId: string): Promise<YieldPrediction> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/yield-prediction`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/yield-prediction`);
      return response.data.data || response.data;
    });
  },

  getHistoricalData: async (fieldId: string, startDate: string, endDate: string, layerType: MapLayerType): Promise<HistoricalSnapshot[]> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}/historical`, async () => {
      const params = new URLSearchParams({ start: startDate, end: endDate, layer: layerType });
      const response = await api.get(
        `${API_PREFIX}/satellite-monitor/fields/${fieldId}/historical?${params.toString()}`
      );
      return response.data.data || response.data;
    });
  },

  createField: async (data: FieldSetupData): Promise<SatelliteField> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields`, async () => {
      const response = await api.post(`${API_PREFIX}/satellite-monitor/fields`, data);
      return response.data.data || response.data;
    });
  },

  updateField: async (fieldId: string, data: Partial<FieldSetupData>): Promise<SatelliteField> => {
    return safeFetch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}`, async () => {
      const response = await api.patch(`${API_PREFIX}/satellite-monitor/fields/${fieldId}`, data);
      return response.data.data || response.data;
    });
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
