/**
 * Yield Prediction Dashboard Component
 * لوحة معلومات توقعات المحصول
 *
 * Advanced ML-based yield prediction similar to John Deere Operations Center
 * and Climate FieldView. Provides scenario-based predictions, confidence intervals,
 * accuracy metrics, and historical comparisons.
 */

'use client';

import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Cloud,
  Signal,
  Download,
  RefreshCw,
  AlertCircle,
  Loader2,
  BarChart3,
  Leaf,
  Calendar,
  Award,
  Info,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

/**
 * Prediction scenario type
 * نوع سيناريو التوقع
 */
export type PredictionScenario = 'optimistic' | 'baseline' | 'pessimistic';

/**
 * Confidence level classification
 * تصنيف مستوى الثقة
 */
export type ConfidenceLevel = 'very_high' | 'high' | 'medium' | 'low';

/**
 * Data source for prediction
 * مصدر البيانات للتوقع
 */
export type DataSource = 'satellite' | 'weather' | 'soil' | 'historical' | 'ml_model';

/**
 * Single scenario prediction
 * توقع سيناريو واحد
 */
export interface ScenarioPrediction {
  scenario: PredictionScenario;
  scenarioAr: string;
  predictedYield: number; // kg
  yieldPerHectare: number; // kg/ha
  confidence: number; // percentage 0-100
  confidenceLevel: ConfidenceLevel;
  confidenceLevelAr: string;
  probability: number; // percentage 0-100
  lowerBound: number; // kg
  upperBound: number; // kg
  factors: {
    weather: number; // impact score -10 to 10
    soil: number;
    irrigation: number;
    fertilization: number;
    pestControl: number;
  };
}

/**
 * Complete field prediction with all scenarios
 * توقع كامل للحقل مع جميع السيناريوهات
 */
export interface FieldPrediction {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  area: number; // hectares
  region: string;
  regionAr: string;

  // Scenarios
  scenarios: {
    optimistic: ScenarioPrediction;
    baseline: ScenarioPrediction;
    pessimistic: ScenarioPrediction;
  };

  // Current conditions
  currentConditions: {
    growthStage: string;
    growthStageAr: string;
    healthIndex: number; // 0-100
    ndvi: number; // Normalized Difference Vegetation Index
    soilMoisture: number; // percentage
    temperature: number; // Celsius
    rainfall: number; // mm (last 30 days)
  };

  // Data sources and updates
  dataSources: DataSource[];
  lastSatelliteUpdate: string;
  lastWeatherUpdate: string;
  lastModelUpdate: string;
  nextUpdateIn: number; // hours

  // Metadata
  plantingDate: string;
  expectedHarvestDate: string;
  daysToHarvest: number;
  seasonYear: string;
}

/**
 * Historical prediction record for accuracy tracking
 * سجل التوقع التاريخي لتتبع الدقة
 */
export interface HistoricalPrediction {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  season: string;
  predictionDate: string;
  predictedYield: number; // kg
  actualYield: number; // kg
  accuracy: number; // percentage
  variance: number; // percentage
  scenario: PredictionScenario;
  confidence: number;
}

/**
 * Prediction accuracy metrics
 * مقاييس دقة التوقعات
 */
export interface AccuracyMetrics {
  overallAccuracy: number; // percentage
  averageError: number; // kg
  meanAbsoluteError: number; // kg
  rootMeanSquareError: number; // kg
  r2Score: number; // 0-1
  totalPredictions: number;
  correctPredictions: number; // within 10% variance

  // Breakdown by scenario
  byScenario: {
    optimistic: { accuracy: number; count: number };
    baseline: { accuracy: number; count: number };
    pessimistic: { accuracy: number; count: number };
  };

  // Trends
  improvementTrend: number; // percentage change year over year
  confidenceCalibration: number; // how well confidence matches accuracy
}

/**
 * Farm-level aggregated predictions
 * توقعات مجمعة على مستوى المزرعة
 */
export interface FarmPrediction {
  farmId: string;
  farmName: string;
  farmNameAr: string;
  totalArea: number; // hectares
  totalFields: number;

  // Aggregated scenarios
  scenarios: {
    optimistic: { total: number; average: number; range: [number, number] };
    baseline: { total: number; average: number; range: [number, number] };
    pessimistic: { total: number; average: number; range: [number, number] };
  };

  // Confidence
  averageConfidence: number;
  confidenceRange: [number, number];

  // Revenue estimates (optional)
  estimatedRevenue?: {
    optimistic: number;
    baseline: number;
    pessimistic: number;
    currency: string;
    pricePerKg: number;
  };
}

/**
 * Complete prediction dashboard data
 * بيانات لوحة التوقعات الكاملة
 */
export interface PredictionDashboard {
  farmPrediction: FarmPrediction;
  fieldPredictions: FieldPrediction[];
  historicalPredictions: HistoricalPrediction[];
  accuracyMetrics: AccuracyMetrics;
  averageConfidence: number;
  lastUpdated: string;
  nextScheduledUpdate: string;
}

// ============================================================================
// Mock Data for Demo/Testing
// ============================================================================

const mockFieldPredictions: FieldPrediction[] = [
  {
    fieldId: 'field1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    area: 45,
    region: "Sana'a",
    regionAr: 'صنعاء',
    scenarios: {
      optimistic: {
        scenario: 'optimistic',
        scenarioAr: 'متفائل',
        predictedYield: 20250,
        yieldPerHectare: 450,
        confidence: 75,
        confidenceLevel: 'high',
        confidenceLevelAr: 'عالي',
        probability: 25,
        lowerBound: 18900,
        upperBound: 21600,
        factors: {
          weather: 8,
          soil: 7,
          irrigation: 9,
          fertilization: 8,
          pestControl: 7,
        },
      },
      baseline: {
        scenario: 'baseline',
        scenarioAr: 'واقعي',
        predictedYield: 18000,
        yieldPerHectare: 400,
        confidence: 92,
        confidenceLevel: 'very_high',
        confidenceLevelAr: 'عالي جداً',
        probability: 60,
        lowerBound: 17100,
        upperBound: 18900,
        factors: {
          weather: 6,
          soil: 6,
          irrigation: 7,
          fertilization: 6,
          pestControl: 5,
        },
      },
      pessimistic: {
        scenario: 'pessimistic',
        scenarioAr: 'متحفظ',
        predictedYield: 15750,
        yieldPerHectare: 350,
        confidence: 82,
        confidenceLevel: 'high',
        confidenceLevelAr: 'عالي',
        probability: 15,
        lowerBound: 14400,
        upperBound: 17100,
        factors: {
          weather: 3,
          soil: 4,
          irrigation: 4,
          fertilization: 3,
          pestControl: 2,
        },
      },
    },
    currentConditions: {
      growthStage: 'Grain Filling',
      growthStageAr: 'امتلاء الحبوب',
      healthIndex: 88,
      ndvi: 0.72,
      soilMoisture: 65,
      temperature: 24,
      rainfall: 45,
    },
    dataSources: ['satellite', 'weather', 'soil', 'ml_model'],
    lastSatelliteUpdate: '2025-12-30T06:00:00Z',
    lastWeatherUpdate: '2025-12-30T08:00:00Z',
    lastModelUpdate: '2025-12-30T07:30:00Z',
    nextUpdateIn: 4,
    plantingDate: '2025-10-15',
    expectedHarvestDate: '2026-01-20',
    daysToHarvest: 21,
    seasonYear: '2025/2026',
  },
  {
    fieldId: 'field2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    area: 35,
    region: "Sana'a",
    regionAr: 'صنعاء',
    scenarios: {
      optimistic: {
        scenario: 'optimistic',
        scenarioAr: 'متفائل',
        predictedYield: 11550,
        yieldPerHectare: 330,
        confidence: 71,
        confidenceLevel: 'high',
        confidenceLevelAr: 'عالي',
        probability: 20,
        lowerBound: 10850,
        upperBound: 12250,
        factors: {
          weather: 7,
          soil: 6,
          irrigation: 7,
          fertilization: 6,
          pestControl: 5,
        },
      },
      baseline: {
        scenario: 'baseline',
        scenarioAr: 'واقعي',
        predictedYield: 10500,
        yieldPerHectare: 300,
        confidence: 88,
        confidenceLevel: 'very_high',
        confidenceLevelAr: 'عالي جداً',
        probability: 65,
        lowerBound: 10000,
        upperBound: 11000,
        factors: {
          weather: 5,
          soil: 5,
          irrigation: 6,
          fertilization: 5,
          pestControl: 4,
        },
      },
      pessimistic: {
        scenario: 'pessimistic',
        scenarioAr: 'متحفظ',
        predictedYield: 9100,
        yieldPerHectare: 260,
        confidence: 79,
        confidenceLevel: 'high',
        confidenceLevelAr: 'عالي',
        probability: 15,
        lowerBound: 8400,
        upperBound: 9800,
        factors: {
          weather: 2,
          soil: 3,
          irrigation: 3,
          fertilization: 2,
          pestControl: 1,
        },
      },
    },
    currentConditions: {
      growthStage: 'Heading',
      growthStageAr: 'طور السنابل',
      healthIndex: 82,
      ndvi: 0.68,
      soilMoisture: 58,
      temperature: 23,
      rainfall: 38,
    },
    dataSources: ['satellite', 'weather', 'ml_model'],
    lastSatelliteUpdate: '2025-12-30T06:00:00Z',
    lastWeatherUpdate: '2025-12-30T08:00:00Z',
    lastModelUpdate: '2025-12-30T07:30:00Z',
    nextUpdateIn: 4,
    plantingDate: '2025-10-20',
    expectedHarvestDate: '2026-01-25',
    daysToHarvest: 26,
    seasonYear: '2025/2026',
  },
  {
    fieldId: 'field3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    cropType: 'Sorghum',
    cropTypeAr: 'ذرة رفيعة',
    area: 28,
    region: "Sana'a",
    regionAr: 'صنعاء',
    scenarios: {
      optimistic: {
        scenario: 'optimistic',
        scenarioAr: 'متفائل',
        predictedYield: 9520,
        yieldPerHectare: 340,
        confidence: 68,
        confidenceLevel: 'medium',
        confidenceLevelAr: 'متوسط',
        probability: 18,
        lowerBound: 8960,
        upperBound: 10080,
        factors: {
          weather: 6,
          soil: 5,
          irrigation: 6,
          fertilization: 5,
          pestControl: 4,
        },
      },
      baseline: {
        scenario: 'baseline',
        scenarioAr: 'واقعي',
        predictedYield: 8400,
        yieldPerHectare: 300,
        confidence: 85,
        confidenceLevel: 'very_high',
        confidenceLevelAr: 'عالي جداً',
        probability: 70,
        lowerBound: 8000,
        upperBound: 8800,
        factors: {
          weather: 4,
          soil: 4,
          irrigation: 5,
          fertilization: 4,
          pestControl: 3,
        },
      },
      pessimistic: {
        scenario: 'pessimistic',
        scenarioAr: 'متحفظ',
        predictedYield: 7280,
        yieldPerHectare: 260,
        confidence: 76,
        confidenceLevel: 'high',
        confidenceLevelAr: 'عالي',
        probability: 12,
        lowerBound: 6720,
        upperBound: 7840,
        factors: {
          weather: 1,
          soil: 2,
          irrigation: 2,
          fertilization: 1,
          pestControl: 0,
        },
      },
    },
    currentConditions: {
      growthStage: 'Flowering',
      growthStageAr: 'طور الإزهار',
      healthIndex: 79,
      ndvi: 0.65,
      soilMoisture: 55,
      temperature: 25,
      rainfall: 42,
    },
    dataSources: ['satellite', 'weather', 'ml_model'],
    lastSatelliteUpdate: '2025-12-30T06:00:00Z',
    lastWeatherUpdate: '2025-12-30T08:00:00Z',
    lastModelUpdate: '2025-12-30T07:30:00Z',
    nextUpdateIn: 4,
    plantingDate: '2025-10-25',
    expectedHarvestDate: '2026-02-01',
    daysToHarvest: 33,
    seasonYear: '2025/2026',
  },
];

const mockHistoricalPredictions: HistoricalPrediction[] = [
  {
    id: 'hp1',
    fieldId: 'field1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    season: '2024/2025',
    predictionDate: '2024-12-30',
    predictedYield: 17500,
    actualYield: 17800,
    accuracy: 98.3,
    variance: 1.7,
    scenario: 'baseline',
    confidence: 90,
  },
  {
    id: 'hp2',
    fieldId: 'field1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    season: '2023/2024',
    predictionDate: '2023-12-30',
    predictedYield: 16800,
    actualYield: 16200,
    accuracy: 96.4,
    variance: -3.6,
    scenario: 'baseline',
    confidence: 88,
  },
  {
    id: 'hp3',
    fieldId: 'field2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    season: '2024/2025',
    predictionDate: '2024-12-30',
    predictedYield: 10200,
    actualYield: 10450,
    accuracy: 97.6,
    variance: 2.4,
    scenario: 'baseline',
    confidence: 86,
  },
  {
    id: 'hp4',
    fieldId: 'field2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    season: '2023/2024',
    predictionDate: '2023-12-30',
    predictedYield: 9800,
    actualYield: 9200,
    accuracy: 93.9,
    variance: -6.1,
    scenario: 'baseline',
    confidence: 84,
  },
  {
    id: 'hp5',
    fieldId: 'field3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    season: '2024/2025',
    predictionDate: '2024-12-30',
    predictedYield: 8100,
    actualYield: 8300,
    accuracy: 97.6,
    variance: 2.4,
    scenario: 'baseline',
    confidence: 83,
  },
  {
    id: 'hp6',
    fieldId: 'field3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    season: '2023/2024',
    predictionDate: '2023-12-30',
    predictedYield: 7900,
    actualYield: 7500,
    accuracy: 94.9,
    variance: -5.1,
    scenario: 'baseline',
    confidence: 81,
  },
];

const mockAccuracyMetrics: AccuracyMetrics = {
  overallAccuracy: 96.5,
  averageError: 285,
  meanAbsoluteError: 312,
  rootMeanSquareError: 398,
  r2Score: 0.94,
  totalPredictions: 24,
  correctPredictions: 21,
  byScenario: {
    optimistic: { accuracy: 82.3, count: 8 },
    baseline: { accuracy: 96.5, count: 12 },
    pessimistic: { accuracy: 91.2, count: 4 },
  },
  improvementTrend: 4.2,
  confidenceCalibration: 0.92,
};

const mockFarmPrediction: FarmPrediction = {
  farmId: 'farm1',
  farmName: 'Al-Khair Farm',
  farmNameAr: 'مزرعة الخير',
  totalArea: 108,
  totalFields: 3,
  scenarios: {
    optimistic: {
      total: 41320,
      average: 382.6,
      range: [330, 450],
    },
    baseline: {
      total: 36900,
      average: 341.7,
      range: [300, 400],
    },
    pessimistic: {
      total: 32130,
      average: 297.5,
      range: [260, 350],
    },
  },
  averageConfidence: 88.3,
  confidenceRange: [85, 92],
  estimatedRevenue: {
    optimistic: 20660000,
    baseline: 18450000,
    pessimistic: 16065000,
    currency: 'YER',
    pricePerKg: 500,
  },
};

const mockDashboard: PredictionDashboard = {
  farmPrediction: mockFarmPrediction,
  fieldPredictions: mockFieldPredictions,
  historicalPredictions: mockHistoricalPredictions,
  accuracyMetrics: mockAccuracyMetrics,
  averageConfidence: 88.3,
  lastUpdated: '2025-12-30T08:00:00Z',
  nextScheduledUpdate: '2025-12-30T12:00:00Z',
};

// ============================================================================
// Helper Functions
// ============================================================================

const _getConfidenceColor = (level: ConfidenceLevel): string => {
  switch (level) {
    case 'very_high':
      return 'bg-green-100 text-green-800 border-green-300';
    case 'high':
      return 'bg-blue-100 text-blue-800 border-blue-300';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    case 'low':
      return 'bg-red-100 text-red-800 border-red-300';
  }
};
void _getConfidenceColor;

const getConfidenceBadgeColor = (confidence: number): string => {
  if (confidence >= 90) return 'bg-green-100 text-green-800';
  if (confidence >= 75) return 'bg-blue-100 text-blue-800';
  if (confidence >= 60) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};

const getScenarioColor = (scenario: PredictionScenario): string => {
  switch (scenario) {
    case 'optimistic':
      return 'text-green-600';
    case 'baseline':
      return 'text-blue-600';
    case 'pessimistic':
      return 'text-orange-600';
  }
};

const getScenarioIcon = (scenario: PredictionScenario) => {
  switch (scenario) {
    case 'optimistic':
      return TrendingUp;
    case 'baseline':
      return Target;
    case 'pessimistic':
      return TrendingDown;
  }
};

const formatNumber = (num: number, locale: string = 'ar-SA'): string => {
  return num.toLocaleString(locale);
};

const formatCurrency = (num: number, currency: string = 'YER'): string => {
  return `${formatNumber(num)} ${currency}`;
};

const exportToCSV = (data: PredictionDashboard) => {
  const headers = [
    'Field Name',
    'اسم الحقل',
    'Crop Type',
    'نوع المحصول',
    'Area (ha)',
    'Optimistic (kg)',
    'Baseline (kg)',
    'Pessimistic (kg)',
    'Confidence (%)',
    'Days to Harvest',
  ];

  const rows = data.fieldPredictions.map((field) => [
    field.fieldName,
    field.fieldNameAr,
    field.cropType,
    field.cropTypeAr,
    field.area,
    field.scenarios.optimistic.predictedYield,
    field.scenarios.baseline.predictedYield,
    field.scenarios.pessimistic.predictedYield,
    field.scenarios.baseline.confidence,
    field.daysToHarvest,
  ]);

  const csvContent = [headers, ...rows].map((row) => row.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', `yield_predictions_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// ============================================================================
// Main Component
// ============================================================================

export const YieldPredictionDashboard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error] = useState<string | null>(null);
  const [dashboard] = useState<PredictionDashboard>(mockDashboard);
  const [selectedScenario, setSelectedScenario] = useState<PredictionScenario>('baseline');
  const [selectedField, setSelectedField] = useState<string | null>(null);

  // Simulate refresh action
  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 1500);
  };

  // Handle export
  const handleExport = () => {
    exportToCSV(dashboard);
  };

  // Loading state
  if (isLoading && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="text-center" data-testid="loading-state">
          <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto" />
          <p className="mt-4 text-gray-600">جاري تحميل توقعات المحصول...</p>
          <p className="text-sm text-gray-500">Loading yield predictions...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-red-200 max-w-md" data-testid="error-state">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto" />
          <h3 className="mt-4 text-lg font-semibold text-gray-900 text-center">
            حدث خطأ
          </h3>
          <p className="mt-2 text-sm text-gray-600 text-center">{error}</p>
          <button
            onClick={handleRefresh}
            className="mt-6 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            data-testid="retry-button"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!dashboard.fieldPredictions || dashboard.fieldPredictions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 max-w-md text-center" data-testid="empty-state">
          <Activity className="w-12 h-12 text-gray-400 mx-auto" />
          <h3 className="mt-4 text-lg font-semibold text-gray-900">
            لا توجد توقعات متاحة
          </h3>
          <p className="mt-2 text-sm text-gray-600">
            No predictions available
          </p>
        </div>
      </div>
    );
  }

  // Prepare chart data for historical comparison
  const historicalChartData = mockHistoricalPredictions.map((pred) => ({
    season: pred.season,
    predicted: pred.predictedYield,
    actual: pred.actualYield,
    fieldNameAr: pred.fieldNameAr,
  }));

  // Prepare scenario comparison data
  const scenarioChartData = dashboard.fieldPredictions.map((field) => ({
    name: field.fieldNameAr,
    optimistic: field.scenarios.optimistic.predictedYield,
    baseline: field.scenarios.baseline.predictedYield,
    pessimistic: field.scenarios.pessimistic.predictedYield,
  }));

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                توقعات المحصول الذكية
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                ML-Based Yield Prediction Dashboard
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                data-testid="export-button"
              >
                <Download className="w-5 h-5" />
                <span>تصدير</span>
              </button>
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="refresh-button"
              >
                <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>تحديث</span>
              </button>
            </div>
          </div>

          {/* Last Update Info */}
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Signal className="w-4 h-4" />
              <span>آخر تحديث للقمر الصناعي: منذ {dashboard.fieldPredictions[0]?.nextUpdateIn} ساعات</span>
            </div>
            <div className="flex items-center gap-2">
              <Cloud className="w-4 h-4" />
              <span>آخر تحديث للطقس: منذ ساعة واحدة</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Farm-Level Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" data-testid="summary-cards">
          <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl shadow-sm border border-green-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-green-600 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-green-700">السيناريو المتفائل</p>
                <p className="text-xs text-green-600">Optimistic</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-green-900">
              {formatNumber(dashboard.farmPrediction.scenarios.optimistic.total / 1000, 'ar-SA')}
            </p>
            <p className="text-sm text-green-700">طن</p>
            <div className="mt-2 text-xs text-green-600">
              احتمالية: {dashboard.fieldPredictions[0]?.scenarios.optimistic.probability}%
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl shadow-sm border border-blue-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-blue-600 rounded-lg">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-blue-700">السيناريو الواقعي</p>
                <p className="text-xs text-blue-600">Baseline</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-blue-900">
              {formatNumber(dashboard.farmPrediction.scenarios.baseline.total / 1000, 'ar-SA')}
            </p>
            <p className="text-sm text-blue-700">طن</p>
            <div className="mt-2 text-xs text-blue-600">
              ثقة: {dashboard.averageConfidence.toFixed(1)}%
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl shadow-sm border border-orange-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-orange-600 rounded-lg">
                <TrendingDown className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-orange-700">السيناريو المتحفظ</p>
                <p className="text-xs text-orange-600">Pessimistic</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-orange-900">
              {formatNumber(dashboard.farmPrediction.scenarios.pessimistic.total / 1000, 'ar-SA')}
            </p>
            <p className="text-sm text-orange-700">طن</p>
            <div className="mt-2 text-xs text-orange-600">
              احتمالية: {dashboard.fieldPredictions[0]?.scenarios.pessimistic.probability}%
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl shadow-sm border border-purple-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-purple-600 rounded-lg">
                <Award className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-purple-700">دقة التوقعات</p>
                <p className="text-xs text-purple-600">Prediction Accuracy</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-purple-900">
              {dashboard.accuracyMetrics.overallAccuracy.toFixed(1)}%
            </p>
            <p className="text-sm text-purple-700">معدل الدقة</p>
            <div className="mt-2 text-xs text-purple-600">
              تحسن: +{dashboard.accuracyMetrics.improvementTrend.toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Scenario Selector */}
        <div className="mb-8">
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <h3 className="text-lg font-semibold text-gray-900">
                اختر السيناريو
                <span className="text-sm font-normal text-gray-500 mr-2">Select Scenario</span>
              </h3>
              <div className="flex gap-2" data-testid="scenario-selector">
                {(['optimistic', 'baseline', 'pessimistic'] as PredictionScenario[]).map((scenario) => {
                  const Icon = getScenarioIcon(scenario);
                  const scenarioLabels = {
                    optimistic: 'متفائل',
                    baseline: 'واقعي',
                    pessimistic: 'متحفظ',
                  };
                  return (
                    <button
                      key={scenario}
                      onClick={() => setSelectedScenario(scenario)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                        selectedScenario === scenario
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                      data-testid={`scenario-${scenario}`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{scenarioLabels[scenario]}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Scenario Comparison Chart */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            مقارنة السيناريوهات
            <span className="text-sm font-normal text-gray-500 mr-2">Scenario Comparison</span>
          </h2>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div style={{ height: '400px' }} data-testid="scenario-comparison-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scenarioChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: number) => `${formatNumber(value)} كجم`}
                    labelStyle={{ direction: 'rtl' }}
                  />
                  <Legend />
                  <Bar dataKey="optimistic" fill="#10b981" name="متفائل" />
                  <Bar dataKey="baseline" fill="#3b82f6" name="واقعي" />
                  <Bar dataKey="pessimistic" fill="#f97316" name="متحفظ" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Field-Level Predictions */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            توقعات الحقول التفصيلية
            <span className="text-sm font-normal text-gray-500 mr-2">Field-Level Predictions</span>
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {dashboard.fieldPredictions.map((field) => {
              const selectedPrediction = field.scenarios[selectedScenario];
              return (
                <div
                  key={field.fieldId}
                  className={`bg-white p-6 rounded-xl shadow-sm border-2 transition-all hover:shadow-md cursor-pointer ${
                    selectedField === field.fieldId
                      ? 'border-green-500 ring-2 ring-green-200'
                      : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedField(field.fieldId)}
                  data-testid={`field-prediction-${field.fieldId}`}
                >
                  {/* Field Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Leaf className="w-5 h-5 text-green-600" />
                        <h3 className="font-bold text-lg text-gray-900">{field.fieldNameAr}</h3>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{field.cropTypeAr}</p>
                      <p className="text-xs text-gray-500 mt-1">{field.area} هكتار</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceBadgeColor(
                        selectedPrediction.confidence
                      )}`}
                    >
                      ثقة {selectedPrediction.confidence}%
                    </span>
                  </div>

                  {/* Main Prediction */}
                  <div className="mb-4 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">التوقع ({selectedPrediction.scenarioAr})</p>
                    <p className={`text-3xl font-bold ${getScenarioColor(selectedScenario)}`}>
                      {formatNumber(selectedPrediction.predictedYield / 1000)} طن
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {formatNumber(selectedPrediction.yieldPerHectare)} كجم/هكتار
                    </p>

                    {/* Confidence Interval */}
                    <div className="mt-3 pt-3 border-t border-gray-300">
                      <p className="text-xs text-gray-600 mb-2">نطاق الثقة 95%</p>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-700">
                          {formatNumber(selectedPrediction.lowerBound / 1000)} طن
                        </span>
                        <span className="text-gray-500">-</span>
                        <span className="text-gray-700">
                          {formatNumber(selectedPrediction.upperBound / 1000)} طن
                        </span>
                      </div>
                      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            selectedScenario === 'optimistic'
                              ? 'bg-green-600'
                              : selectedScenario === 'baseline'
                              ? 'bg-blue-600'
                              : 'bg-orange-600'
                          }`}
                          style={{ width: `${selectedPrediction.confidence}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Current Conditions */}
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-700 mb-2">الظروف الحالية</p>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <p className="text-gray-600">مرحلة النمو</p>
                        <p className="font-semibold text-gray-900">{field.currentConditions.growthStageAr}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">مؤشر الصحة</p>
                        <p className="font-semibold text-gray-900">{field.currentConditions.healthIndex}%</p>
                      </div>
                      <div>
                        <p className="text-gray-600">NDVI</p>
                        <p className="font-semibold text-gray-900">{field.currentConditions.ndvi.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">رطوبة التربة</p>
                        <p className="font-semibold text-gray-900">{field.currentConditions.soilMoisture}%</p>
                      </div>
                    </div>
                  </div>

                  {/* Impact Factors */}
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-700 mb-2">عوامل التأثير</p>
                    <div className="space-y-2">
                      {Object.entries(selectedPrediction.factors).map(([factor, score]) => {
                        const factorLabels: Record<string, string> = {
                          weather: 'الطقس',
                          soil: 'التربة',
                          irrigation: 'الري',
                          fertilization: 'التسميد',
                          pestControl: 'مكافحة الآفات',
                        };
                        const percentage = ((score + 10) / 20) * 100; // Convert -10 to 10 scale to 0-100%
                        return (
                          <div key={factor}>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">{factorLabels[factor]}</span>
                              <span className={`font-semibold ${score >= 5 ? 'text-green-600' : score >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                                {score > 0 ? '+' : ''}{score}
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                              <div
                                className={`h-1.5 rounded-full ${
                                  score >= 5 ? 'bg-green-600' : score >= 0 ? 'bg-blue-600' : 'bg-orange-600'
                                }`}
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Harvest Info */}
                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1 text-gray-600">
                        <Calendar className="w-3 h-3" />
                        <span>الحصاد بعد</span>
                      </div>
                      <span className="font-semibold text-gray-900">{field.daysToHarvest} يوم</span>
                    </div>
                  </div>

                  {/* Data Sources */}
                  <div className="mt-3 flex items-center gap-2 flex-wrap">
                    {field.dataSources.includes('satellite') && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                        <Signal className="w-3 h-3" />
                        قمر صناعي
                      </span>
                    )}
                    {field.dataSources.includes('weather') && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-sky-50 text-sky-700 rounded text-xs">
                        <Cloud className="w-3 h-3" />
                        طقس
                      </span>
                    )}
                    {field.dataSources.includes('ml_model') && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs">
                        <Activity className="w-3 h-3" />
                        ML
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Historical Predictions vs Actual */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            مقارنة التوقعات التاريخية مع الفعلي
            <span className="text-sm font-normal text-gray-500 mr-2">Historical Predictions vs Actual</span>
          </h2>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div style={{ height: '400px' }} data-testid="historical-comparison-chart">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={historicalChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="season" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: number) => `${formatNumber(value)} كجم`}
                    labelStyle={{ direction: 'rtl' }}
                  />
                  <Legend />
                  <Bar dataKey="predicted" fill="#94a3b8" name="المتوقع" />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="#10b981"
                    strokeWidth={3}
                    name="الفعلي"
                    dot={{ r: 5 }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Accuracy Breakdown */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              {mockHistoricalPredictions.slice(0, 3).map((pred) => (
                <div key={pred.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-sm font-semibold text-gray-900">{pred.fieldNameAr}</p>
                  <p className="text-xs text-gray-600 mb-2">{pred.season}</p>
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-xs text-gray-600">الدقة</p>
                      <p className="text-lg font-bold text-green-600">{pred.accuracy.toFixed(1)}%</p>
                    </div>
                    <div className="text-left">
                      <p className="text-xs text-gray-600">الانحراف</p>
                      <p
                        className={`text-lg font-bold ${
                          pred.variance > 0 ? 'text-green-600' : 'text-orange-600'
                        }`}
                      >
                        {pred.variance > 0 ? '+' : ''}
                        {pred.variance.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Prediction Accuracy Metrics */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            مقاييس دقة التوقعات
            <span className="text-sm font-normal text-gray-500 mr-2">Prediction Accuracy Metrics</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Overall Accuracy */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-3 bg-green-100 rounded-lg">
                  <Target className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">الدقة الإجمالية</p>
                  <p className="text-xs text-gray-500">Overall Accuracy</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {dashboard.accuracyMetrics.overallAccuracy.toFixed(1)}%
              </p>
              <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 rounded-full h-2"
                  style={{ width: `${dashboard.accuracyMetrics.overallAccuracy}%` }}
                />
              </div>
            </div>

            {/* R² Score */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">معامل التحديد</p>
                  <p className="text-xs text-gray-500">R² Score</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {dashboard.accuracyMetrics.r2Score.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600 mt-1">من 1.00</p>
            </div>

            {/* Average Error */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <Activity className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">متوسط الخطأ</p>
                  <p className="text-xs text-gray-500">Average Error</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {formatNumber(dashboard.accuracyMetrics.averageError)}
              </p>
              <p className="text-sm text-gray-600 mt-1">كجم</p>
            </div>

            {/* Improvement Trend */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">اتجاه التحسن</p>
                  <p className="text-xs text-gray-500">Improvement Trend</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-green-600">
                +{dashboard.accuracyMetrics.improvementTrend.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600 mt-1">سنوياً</p>
            </div>
          </div>

          {/* Scenario Breakdown */}
          <div className="mt-6 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              الدقة حسب السيناريو
              <span className="text-sm font-normal text-gray-500 mr-2">Accuracy by Scenario</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(dashboard.accuracyMetrics.byScenario).map(([scenario, data]) => {
                const scenarioLabels = {
                  optimistic: { ar: 'متفائل', color: 'green' },
                  baseline: { ar: 'واقعي', color: 'blue' },
                  pessimistic: { ar: 'متحفظ', color: 'orange' },
                };
                const label = scenarioLabels[scenario as PredictionScenario];
                return (
                  <div
                    key={scenario}
                    className={`p-4 bg-${label.color}-50 rounded-lg border border-${label.color}-200`}
                  >
                    <p className="text-sm font-semibold text-gray-900 mb-2">{label.ar}</p>
                    <p className={`text-2xl font-bold text-${label.color}-600`}>
                      {data.accuracy.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {formatNumber(data.count)} توقعات
                    </p>
                    <div className="mt-3 w-full bg-white rounded-full h-2">
                      <div
                        className={`bg-${label.color}-600 rounded-full h-2`}
                        style={{ width: `${data.accuracy}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Revenue Estimates (if available) */}
        {dashboard.farmPrediction.estimatedRevenue && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              تقديرات الإيرادات
              <span className="text-sm font-normal text-gray-500 mr-2">Revenue Estimates</span>
            </h2>

            <div className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-xl border border-green-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {(['optimistic', 'baseline', 'pessimistic'] as PredictionScenario[]).map((scenario) => {
                  const scenarioLabels = {
                    optimistic: { ar: 'متفائل', color: 'green' },
                    baseline: { ar: 'واقعي', color: 'blue' },
                    pessimistic: { ar: 'متحفظ', color: 'orange' },
                  };
                  const label = scenarioLabels[scenario];
                  const revenue = dashboard.farmPrediction.estimatedRevenue![scenario];

                  return (
                    <div key={scenario}>
                      <p className="text-sm text-gray-700 mb-1">{label.ar}</p>
                      <p className={`text-2xl font-bold text-${label.color}-700`}>
                        {formatCurrency(revenue, dashboard.farmPrediction.estimatedRevenue!.currency)}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        سعر: {formatNumber(dashboard.farmPrediction.estimatedRevenue!.pricePerKg)} {dashboard.farmPrediction.estimatedRevenue!.currency}/كجم
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Info Footer */}
        <div className="bg-blue-50 p-6 rounded-xl border border-blue-200">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">حول التوقعات</h4>
              <p className="text-sm text-blue-800">
                يتم تحديث التوقعات تلقائياً كل 6 ساعات باستخدام بيانات الأقمار الصناعية والطقس في الوقت الفعلي.
                النماذج الذكية تأخذ في الاعتبار العديد من العوامل بما في ذلك صحة المحصول، رطوبة التربة، الظروف
                الجوية، والبيانات التاريخية لتوفير توقعات دقيقة.
              </p>
              <p className="text-xs text-blue-700 mt-2">
                Predictions are automatically updated every 6 hours using real-time satellite and weather data.
                ML models consider multiple factors including crop health, soil moisture, weather conditions,
                and historical data to provide accurate forecasts.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YieldPredictionDashboard;
