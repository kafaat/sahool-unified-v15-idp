'use client';

import React, { useState } from 'react';
import {
  Leaf,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Check,
  RefreshCw,
  Droplets,
  Thermometer,
} from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface NutrientLevel {
  current: number;
  optimal: { min: number; max: number };
  unit: string;
  status: 'low' | 'optimal' | 'high';
  trend?: 'up' | 'down' | 'stable';
}

interface SoilNutrient {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  sampleDate: string;
  location: {
    latitude: number;
    longitude: number;
  };
  nutrients: {
    nitrogen: NutrientLevel;
    phosphorus: NutrientLevel;
    potassium: NutrientLevel;
  };
  ph: {
    current: number;
    optimal: { min: number; max: number };
    status: 'acidic' | 'neutral' | 'alkaline';
  };
  organicMatter: {
    percentage: number;
    status: 'low' | 'moderate' | 'high';
  };
  moisture: {
    percentage: number;
    status: 'low' | 'optimal' | 'high';
  };
  temperature: {
    celsius: number;
  };
}

interface FertilizerRecommendation {
  id: string;
  nutrient: string;
  nutrientAr: string;
  product: string;
  productAr: string;
  amount: number;
  unit: string;
  unitAr: string;
  applicationMethod: string;
  applicationMethodAr: string;
  priority: 'high' | 'medium' | 'low';
  estimatedCost?: number;
  currency?: string;
}

interface HistoricalDataPoint {
  date: string;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  ph: number;
}

interface SoilNutrientAnalysisProps {
  data?: SoilNutrient;
  onRefresh?: () => void;
  loading?: boolean;
  language?: 'en' | 'ar';
}

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_SOIL_DATA: SoilNutrient = {
  id: 'soil-001',
  fieldId: 'field-123',
  fieldName: 'North Field - Plot A',
  fieldNameAr: 'الحقل الشمالي - قطعة أ',
  sampleDate: '2025-12-28T10:30:00Z',
  location: {
    latitude: 15.5527,
    longitude: 48.5164,
  },
  nutrients: {
    nitrogen: {
      current: 45,
      optimal: { min: 40, max: 60 },
      unit: 'ppm',
      status: 'optimal',
      trend: 'up',
    },
    phosphorus: {
      current: 15,
      optimal: { min: 20, max: 40 },
      unit: 'ppm',
      status: 'low',
      trend: 'down',
    },
    potassium: {
      current: 185,
      optimal: { min: 100, max: 200 },
      unit: 'ppm',
      status: 'optimal',
      trend: 'stable',
    },
  },
  ph: {
    current: 7.2,
    optimal: { min: 6.0, max: 7.5 },
    status: 'neutral',
  },
  organicMatter: {
    percentage: 3.8,
    status: 'moderate',
  },
  moisture: {
    percentage: 22,
    status: 'optimal',
  },
  temperature: {
    celsius: 24,
  },
};

const MOCK_FERTILIZER_RECOMMENDATIONS: FertilizerRecommendation[] = [
  {
    id: 'rec-001',
    nutrient: 'Phosphorus',
    nutrientAr: 'الفوسفور',
    product: 'Triple Superphosphate (TSP)',
    productAr: 'سوبر فوسفات ثلاثي',
    amount: 50,
    unit: 'kg/hectare',
    unitAr: 'كجم/هكتار',
    applicationMethod: 'Broadcast and incorporate before planting',
    applicationMethodAr: 'نثر وخلط قبل الزراعة',
    priority: 'high',
    estimatedCost: 2500,
    currency: 'YER',
  },
  {
    id: 'rec-002',
    nutrient: 'Nitrogen',
    nutrientAr: 'النيتروجين',
    product: 'Urea (46-0-0)',
    productAr: 'يوريا',
    amount: 30,
    unit: 'kg/hectare',
    unitAr: 'كجم/هكتار',
    applicationMethod: 'Split application: 50% at planting, 50% at growth stage',
    applicationMethodAr: 'تطبيق مقسم: ٥٠٪ عند الزراعة، ٥٠٪ في مرحلة النمو',
    priority: 'medium',
    estimatedCost: 1800,
    currency: 'YER',
  },
];

const MOCK_HISTORICAL_DATA: HistoricalDataPoint[] = [
  { date: '2025-09-01', nitrogen: 38, phosphorus: 22, potassium: 175, ph: 7.0 },
  { date: '2025-10-01', nitrogen: 42, phosphorus: 20, potassium: 180, ph: 7.1 },
  { date: '2025-11-01', nitrogen: 44, phosphorus: 18, potassium: 182, ph: 7.1 },
  { date: '2025-12-01', nitrogen: 45, phosphorus: 15, potassium: 185, ph: 7.2 },
];

// ============================================================================
// Helper Functions
// ============================================================================

const getNutrientStatusColor = (status: 'low' | 'optimal' | 'high'): string => {
  switch (status) {
    case 'low':
      return 'bg-red-500';
    case 'optimal':
      return 'bg-green-500';
    case 'high':
      return 'bg-yellow-500';
    default:
      return 'bg-gray-500';
  }
};

const getNutrientStatusBgColor = (
  status: 'low' | 'optimal' | 'high'
): string => {
  switch (status) {
    case 'low':
      return 'bg-red-50 border-red-200';
    case 'optimal':
      return 'bg-green-50 border-green-200';
    case 'high':
      return 'bg-yellow-50 border-yellow-200';
    default:
      return 'bg-gray-50 border-gray-200';
  }
};

const getNutrientStatusTextColor = (
  status: 'low' | 'optimal' | 'high'
): string => {
  switch (status) {
    case 'low':
      return 'text-red-700';
    case 'optimal':
      return 'text-green-700';
    case 'high':
      return 'text-yellow-700';
    default:
      return 'text-gray-700';
  }
};

const getTrendIcon = (trend?: 'up' | 'down' | 'stable') => {
  if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-600" />;
  if (trend === 'down')
    return <TrendingDown className="w-4 h-4 text-red-600" />;
  return null;
};

const getPriorityColor = (priority: 'high' | 'medium' | 'low'): string => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-300';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    case 'low':
      return 'bg-blue-100 text-blue-800 border-blue-300';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300';
  }
};

const formatDate = (dateString: string, language: 'en' | 'ar'): string => {
  const date = new Date(dateString);
  if (language === 'ar') {
    return date.toLocaleDateString('ar-YE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const calculateNutrientPercentage = (
  current: number,
  optimal: { min: number; max: number }
): number => {
  const range = optimal.max - optimal.min;
  const position = current - optimal.min;
  return Math.min(Math.max((position / range) * 100, 0), 100);
};

// ============================================================================
// Component
// ============================================================================

const SoilNutrientAnalysis: React.FC<SoilNutrientAnalysisProps> = ({
  data = MOCK_SOIL_DATA,
  onRefresh,
  loading = false,
  language = 'en',
}) => {
  const [showHistorical, setShowHistorical] = useState(false);
  const isRTL = language === 'ar';

  // Error handling for missing data
  if (!data && !loading) {
    return (
      <div
        className={`p-6 bg-red-50 border border-red-200 rounded-lg ${
          isRTL ? 'text-right' : 'text-left'
        }`}
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        <div className="flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span className="font-semibold">
            {language === 'ar'
              ? 'خطأ: لا توجد بيانات متاحة'
              : 'Error: No data available'}
          </span>
        </div>
        <p className="mt-2 text-sm text-red-600">
          {language === 'ar'
            ? 'يرجى التحقق من اتصال الاستشعار أو تحديث البيانات.'
            : 'Please check sensor connection or refresh the data.'}
        </p>
      </div>
    );
  }

  const translations = {
    title: language === 'ar' ? 'تحليل مغذيات التربة' : 'Soil Nutrient Analysis',
    field: language === 'ar' ? 'الحقل' : 'Field',
    sampleDate: language === 'ar' ? 'تاريخ العينة' : 'Sample Date',
    refresh: language === 'ar' ? 'تحديث' : 'Refresh',
    npkLevels: language === 'ar' ? 'مستويات NPK' : 'NPK Levels',
    nitrogen: language === 'ar' ? 'النيتروجين' : 'Nitrogen',
    phosphorus: language === 'ar' ? 'الفوسفور' : 'Phosphorus',
    potassium: language === 'ar' ? 'البوتاسيوم' : 'Potassium',
    current: language === 'ar' ? 'الحالي' : 'Current',
    optimal: language === 'ar' ? 'الأمثل' : 'Optimal',
    status: language === 'ar' ? 'الحالة' : 'Status',
    low: language === 'ar' ? 'منخفض' : 'Low',
    high: language === 'ar' ? 'مرتفع' : 'High',
    phLevel: language === 'ar' ? 'مستوى الحموضة (pH)' : 'pH Level',
    acidic: language === 'ar' ? 'حمضي' : 'Acidic',
    neutral: language === 'ar' ? 'محايد' : 'Neutral',
    alkaline: language === 'ar' ? 'قلوي' : 'Alkaline',
    organicMatter: language === 'ar' ? 'المادة العضوية' : 'Organic Matter',
    moisture: language === 'ar' ? 'الرطوبة' : 'Soil Moisture',
    temperature: language === 'ar' ? 'درجة الحرارة' : 'Temperature',
    moderate: language === 'ar' ? 'معتدل' : 'Moderate',
    deficiencyAlerts:
      language === 'ar' ? 'تنبيهات النقص' : 'Deficiency Alerts',
    noDeficiencies:
      language === 'ar'
        ? 'لا توجد أوجه نقص حرجة'
        : 'No critical deficiencies',
    fertilizerRecommendations:
      language === 'ar' ? 'توصيات الأسمدة' : 'Fertilizer Recommendations',
    amount: language === 'ar' ? 'الكمية' : 'Amount',
    method: language === 'ar' ? 'طريقة التطبيق' : 'Application Method',
    estimatedCost: language === 'ar' ? 'التكلفة المقدرة' : 'Estimated Cost',
    priority: language === 'ar' ? 'الأولوية' : 'Priority',
    priorityHigh: language === 'ar' ? 'عالية' : 'High',
    priorityMedium: language === 'ar' ? 'متوسطة' : 'Medium',
    priorityLow: language === 'ar' ? 'منخفضة' : 'Low',
    historicalTrends:
      language === 'ar' ? 'الاتجاهات التاريخية' : 'Historical Trends',
    showHistorical:
      language === 'ar' ? 'عرض البيانات التاريخية' : 'Show Historical Data',
    hideHistorical:
      language === 'ar' ? 'إخفاء البيانات التاريخية' : 'Hide Historical Data',
  };

  return (
    <div
      className={`w-full space-y-6 ${isRTL ? 'text-right' : 'text-left'}`}
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <Leaf className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">
                {translations.title}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {translations.field}:{' '}
                {language === 'ar' ? data.fieldNameAr : data.fieldName}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              <span className="font-semibold">{translations.sampleDate}:</span>{' '}
              {formatDate(data.sampleDate, language)}
            </div>
            <button
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <RefreshCw
                className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
              />
              <span>{translations.refresh}</span>
            </button>
          </div>
        </div>
      </div>

      {/* NPK Levels */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Leaf className="w-5 h-5 text-green-600" />
          {translations.npkLevels}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Nitrogen */}
          <NutrientCard
            name={translations.nitrogen}
            nameShort="N"
            data={data.nutrients.nitrogen}
            translations={translations}
            isRTL={isRTL}
          />
          {/* Phosphorus */}
          <NutrientCard
            name={translations.phosphorus}
            nameShort="P"
            data={data.nutrients.phosphorus}
            translations={translations}
            isRTL={isRTL}
          />
          {/* Potassium */}
          <NutrientCard
            name={translations.potassium}
            nameShort="K"
            data={data.nutrients.potassium}
            translations={translations}
            isRTL={isRTL}
          />
        </div>
      </div>

      {/* pH Level, Organic Matter, Moisture, Temperature */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* pH Level */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Droplets className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-gray-800">
              {translations.phLevel}
            </h4>
          </div>
          <div className="space-y-3">
            <div className="text-3xl font-bold text-gray-900">
              {data.ph.current.toFixed(1)}
            </div>
            <div className="relative h-3 bg-gradient-to-r from-red-500 via-green-500 to-blue-500 rounded-full">
              <div
                className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white border-2 border-gray-800 rounded-full shadow-md"
                style={{
                  left: `${((data.ph.current - 4) / 10) * 100}%`,
                }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-600">
              <span>4.0</span>
              <span>7.0</span>
              <span>14.0</span>
            </div>
            <div
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                data.ph.status === 'neutral'
                  ? 'bg-green-100 text-green-700'
                  : data.ph.status === 'acidic'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-blue-100 text-blue-700'
              }`}
            >
              {data.ph.status === 'neutral'
                ? translations.neutral
                : data.ph.status === 'acidic'
                ? translations.acidic
                : translations.alkaline}
            </div>
            <div className="text-xs text-gray-500">
              {translations.optimal}: {data.ph.optimal.min.toFixed(1)} -{' '}
              {data.ph.optimal.max.toFixed(1)}
            </div>
          </div>
        </div>

        {/* Organic Matter */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Leaf className="w-5 h-5 text-amber-600" />
            <h4 className="font-semibold text-gray-800">
              {translations.organicMatter}
            </h4>
          </div>
          <div className="space-y-3">
            <div className="text-3xl font-bold text-gray-900">
              {data.organicMatter.percentage.toFixed(1)}%
            </div>
            <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="absolute top-0 left-0 h-full bg-amber-500 rounded-full transition-all"
                style={{ width: `${data.organicMatter.percentage * 10}%` }}
              />
            </div>
            <div
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                data.organicMatter.status === 'moderate'
                  ? 'bg-green-100 text-green-700'
                  : data.organicMatter.status === 'low'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-blue-100 text-blue-700'
              }`}
            >
              {data.organicMatter.status === 'moderate'
                ? translations.moderate
                : data.organicMatter.status === 'low'
                ? translations.low
                : translations.high}
            </div>
          </div>
        </div>

        {/* Soil Moisture */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Droplets className="w-5 h-5 text-cyan-600" />
            <h4 className="font-semibold text-gray-800">
              {translations.moisture}
            </h4>
          </div>
          <div className="space-y-3">
            <div className="text-3xl font-bold text-gray-900">
              {data.moisture.percentage}%
            </div>
            <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="absolute top-0 left-0 h-full bg-cyan-500 rounded-full transition-all"
                style={{ width: `${data.moisture.percentage}%` }}
              />
            </div>
            <div
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                data.moisture.status === 'optimal'
                  ? 'bg-green-100 text-green-700'
                  : data.moisture.status === 'low'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-blue-100 text-blue-700'
              }`}
            >
              {data.moisture.status === 'optimal'
                ? translations.optimal
                : data.moisture.status === 'low'
                ? translations.low
                : translations.high}
            </div>
          </div>
        </div>

        {/* Temperature */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Thermometer className="w-5 h-5 text-orange-600" />
            <h4 className="font-semibold text-gray-800">
              {translations.temperature}
            </h4>
          </div>
          <div className="space-y-3">
            <div className="text-3xl font-bold text-gray-900">
              {data.temperature.celsius}°C
            </div>
            <div className="relative h-3 bg-gradient-to-r from-blue-400 via-green-400 to-red-500 rounded-full">
              <div
                className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white border-2 border-gray-800 rounded-full shadow-md"
                style={{
                  left: `${((data.temperature.celsius - 0) / 50) * 100}%`,
                }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-600">
              <span>0°C</span>
              <span>25°C</span>
              <span>50°C</span>
            </div>
          </div>
        </div>
      </div>

      {/* Deficiency Alerts */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          {translations.deficiencyAlerts}
        </h3>
        <div className="space-y-3">
          {data.nutrients.phosphorus.status === 'low' && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-semibold text-red-800">
                  {translations.phosphorus}{' '}
                  {language === 'ar' ? 'منخفض' : 'Deficiency'}
                </p>
                <p className="text-sm text-red-700 mt-1">
                  {language === 'ar'
                    ? `المستوى الحالي (${data.nutrients.phosphorus.current} ${data.nutrients.phosphorus.unit}) أقل من النطاق الأمثل. قد يؤثر ذلك على نمو الجذور وتطور النبات.`
                    : `Current level (${data.nutrients.phosphorus.current} ${data.nutrients.phosphorus.unit}) is below optimal range. This may affect root development and plant growth.`}
                </p>
              </div>
            </div>
          )}
          {data.nutrients.nitrogen.status === 'optimal' &&
            data.nutrients.potassium.status === 'optimal' &&
            data.nutrients.phosphorus.status === 'optimal' && (
              <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="font-semibold text-green-800">
                    {translations.noDeficiencies}
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    {language === 'ar'
                      ? 'جميع مستويات العناصر الغذائية ضمن النطاقات المثلى.'
                      : 'All nutrient levels are within optimal ranges.'}
                  </p>
                </div>
              </div>
            )}
        </div>
      </div>

      {/* Fertilizer Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Leaf className="w-5 h-5 text-green-600" />
          {translations.fertilizerRecommendations}
        </h3>
        <div className="space-y-4">
          {MOCK_FERTILIZER_RECOMMENDATIONS.map((rec) => (
            <div
              key={rec.id}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold text-gray-800">
                      {language === 'ar' ? rec.productAr : rec.product}
                    </h4>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded border ${getPriorityColor(
                        rec.priority
                      )}`}
                    >
                      {rec.priority === 'high'
                        ? translations.priorityHigh
                        : rec.priority === 'medium'
                        ? translations.priorityMedium
                        : translations.priorityLow}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">
                      {language === 'ar' ? rec.nutrientAr : rec.nutrient}
                    </span>
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">
                    {translations.amount}:
                  </span>{' '}
                  <span className="text-gray-900">
                    {rec.amount} {language === 'ar' ? rec.unitAr : rec.unit}
                  </span>
                </div>
                {rec.estimatedCost && (
                  <div>
                    <span className="font-medium text-gray-700">
                      {translations.estimatedCost}:
                    </span>{' '}
                    <span className="text-gray-900">
                      {rec.estimatedCost.toLocaleString()} {rec.currency}
                    </span>
                  </div>
                )}
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{translations.method}:</span>{' '}
                  {language === 'ar'
                    ? rec.applicationMethodAr
                    : rec.applicationMethod}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Historical Trends */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            {translations.historicalTrends}
          </h3>
          <button
            onClick={() => setShowHistorical(!showHistorical)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showHistorical
              ? translations.hideHistorical
              : translations.showHistorical}
          </button>
        </div>
        {showHistorical && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">
                    {language === 'ar' ? 'التاريخ' : 'Date'}
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">
                    N (ppm)
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">
                    P (ppm)
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">
                    K (ppm)
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">
                    pH
                  </th>
                </tr>
              </thead>
              <tbody>
                {MOCK_HISTORICAL_DATA.map((point, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="px-4 py-3 text-gray-900">
                      {formatDate(point.date, language)}
                    </td>
                    <td className="px-4 py-3 text-gray-900">
                      {point.nitrogen}
                    </td>
                    <td className="px-4 py-3 text-gray-900">
                      {point.phosphorus}
                    </td>
                    <td className="px-4 py-3 text-gray-900">
                      {point.potassium}
                    </td>
                    <td className="px-4 py-3 text-gray-900">
                      {point.ph.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Nutrient Card Component
// ============================================================================

interface NutrientCardProps {
  name: string;
  nameShort: string;
  data: NutrientLevel;
  translations: Record<string, string>;
  isRTL: boolean;
}

const NutrientCard: React.FC<NutrientCardProps> = ({
  name,
  nameShort,
  data,
  translations,
  isRTL,
}) => {
  const percentage = calculateNutrientPercentage(data.current, data.optimal);

  return (
    <div
      className={`p-4 border rounded-lg ${getNutrientStatusBgColor(
        data.status
      )}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className={`w-10 h-10 rounded-full ${getNutrientStatusColor(
              data.status
            )} flex items-center justify-center text-white font-bold`}
          >
            {nameShort}
          </div>
          <h4 className="font-semibold text-gray-800">{name}</h4>
        </div>
        {data.trend && getTrendIcon(data.trend)}
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-baseline">
          <span className="text-2xl font-bold text-gray-900">
            {data.current}
          </span>
          <span className="text-sm text-gray-600">{data.unit}</span>
        </div>

        {/* Progress Bar */}
        <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`absolute top-0 ${
              isRTL ? 'right-0' : 'left-0'
            } h-full ${getNutrientStatusColor(
              data.status
            )} rounded-full transition-all`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-gray-600">
          <span>
            {translations.optimal}: {data.optimal.min}
          </span>
          <span>{data.optimal.max}</span>
        </div>

        <div className="pt-2">
          <span
            className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getNutrientStatusTextColor(
              data.status
            )} ${getNutrientStatusBgColor(data.status)}`}
          >
            {data.status === 'optimal' && (
              <Check className="w-3 h-3" />
            )}
            {data.status === 'low' && <AlertCircle className="w-3 h-3" />}
            {data.status === 'optimal'
              ? translations.optimal
              : data.status === 'low'
              ? translations.low
              : translations.high}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SoilNutrientAnalysis;
export type {
  SoilNutrient,
  NutrientLevel,
  FertilizerRecommendation,
  HistoricalDataPoint,
  SoilNutrientAnalysisProps,
};
