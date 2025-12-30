/**
 * Yield Factor Analysis Component
 * مكون تحليل عوامل المحصول
 *
 * Comprehensive multi-factor analysis for yield optimization
 * analyzing weather, soil, inputs, and management practices
 */

'use client';

import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  Cloud,
  Droplets,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Info,
  ChevronDown,
  ChevronUp,
  Leaf,
  Calendar,
  Sprout,
  Target,
  BarChart3,
  Activity,
} from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface WeatherFactors {
  rainfall: number; // mm
  temperature: number; // °C
  growingDegreeDays: number; // GDD
  humidity: number; // %
  solarRadiation: number; // MJ/m²
}

interface SoilFactors {
  nitrogen: number; // kg/ha
  phosphorus: number; // kg/ha
  potassium: number; // kg/ha
  pH: number;
  organicMatter: number; // %
  soilMoisture: number; // %
}

interface InputFactors {
  fertilizerNPK: number; // kg/ha
  irrigation: number; // mm
  pesticides: number; // applications
  herbicides: number; // applications
}

interface ManagementFactors {
  plantingDate: string;
  plantingDateScore: number; // 0-100
  varietyQuality: number; // 0-100
  tillageScore: number; // 0-100
  seedRate: number; // kg/ha
  spacing: number; // cm
}

interface FactorCorrelation {
  factorName: string;
  factorNameAr: string;
  correlation: number; // -1 to 1
  impact: 'high' | 'medium' | 'low';
  currentValue: number;
  optimalValue: number;
  unit: string;
}

interface FactorContribution {
  category: string;
  categoryAr: string;
  contribution: number; // percentage
  score: number; // 0-100
  status: 'optimal' | 'good' | 'suboptimal' | 'poor';
}

interface LimitingFactor {
  factor: string;
  factorAr: string;
  category: string;
  categoryAr: string;
  severity: 'critical' | 'moderate' | 'minor';
  currentValue: number;
  targetValue: number;
  unit: string;
  impact: number; // percentage yield loss
}

interface Recommendation {
  id: string;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  category: string;
  categoryAr: string;
  priority: 'high' | 'medium' | 'low';
  expectedImpact: number; // percentage yield increase
  cost: number; // SAR
  roi: number; // return on investment ratio
}

interface FieldFactorData {
  fieldId: string;
  fieldNameAr: string;
  fieldNameEn: string;
  cropTypeAr: string;
  cropTypeEn: string;
  area: number; // hectares
  currentYield: number; // kg/ha
  potentialYield: number; // kg/ha
  yieldGap: number; // percentage
  weather: WeatherFactors;
  soil: SoilFactors;
  inputs: InputFactors;
  management: ManagementFactors;
  correlations: FactorCorrelation[];
  contributions: FactorContribution[];
  limitingFactors: LimitingFactor[];
  recommendations: Recommendation[];
  overallScore: number; // 0-100
}

interface YieldFactorAnalysisProps {
  fieldId?: string;
  comparisonMode?: boolean;
}

// ============================================================================
// Constants
// ============================================================================

const CATEGORY_COLORS = {
  weather: '#3b82f6', // blue
  soil: '#92400e', // brown
  inputs: '#10b981', // green
  management: '#8b5cf6', // purple
};

const STATUS_COLORS = {
  optimal: '#10b981', // green
  good: '#3b82f6', // blue
  suboptimal: '#f59e0b', // amber
  poor: '#ef4444', // red
};

const SEVERITY_COLORS = {
  critical: '#ef4444', // red
  moderate: '#f59e0b', // amber
  minor: '#eab308', // yellow
};

const PRIORITY_COLORS = {
  high: '#ef4444', // red
  medium: '#f59e0b', // amber
  low: '#3b82f6', // blue
};

// ============================================================================
// Mock Data
// ============================================================================

const mockFieldData: FieldFactorData[] = [
  {
    fieldId: '1',
    fieldNameAr: 'الحقل الشمالي',
    fieldNameEn: 'North Field',
    cropTypeAr: 'قمح',
    cropTypeEn: 'Wheat',
    area: 30,
    currentYield: 4200,
    potentialYield: 6000,
    yieldGap: 30,
    overallScore: 72,
    weather: {
      rainfall: 320,
      temperature: 22,
      growingDegreeDays: 2100,
      humidity: 45,
      solarRadiation: 18.5,
    },
    soil: {
      nitrogen: 85,
      phosphorus: 28,
      potassium: 180,
      pH: 7.2,
      organicMatter: 2.8,
      soilMoisture: 65,
    },
    inputs: {
      fertilizerNPK: 250,
      irrigation: 450,
      pesticides: 3,
      herbicides: 2,
    },
    management: {
      plantingDate: '2024-11-15',
      plantingDateScore: 85,
      varietyQuality: 90,
      tillageScore: 75,
      seedRate: 120,
      spacing: 15,
    },
    correlations: [
      {
        factorName: 'Nitrogen',
        factorNameAr: 'النيتروجين',
        correlation: 0.85,
        impact: 'high',
        currentValue: 85,
        optimalValue: 120,
        unit: 'kg/ha',
      },
      {
        factorName: 'Irrigation',
        factorNameAr: 'الري',
        correlation: 0.78,
        impact: 'high',
        currentValue: 450,
        optimalValue: 550,
        unit: 'mm',
      },
      {
        factorName: 'Growing Degree Days',
        factorNameAr: 'أيام النمو الحرارية',
        correlation: 0.72,
        impact: 'high',
        currentValue: 2100,
        optimalValue: 2400,
        unit: 'GDD',
      },
      {
        factorName: 'Organic Matter',
        factorNameAr: 'المادة العضوية',
        correlation: 0.68,
        impact: 'medium',
        currentValue: 2.8,
        optimalValue: 3.5,
        unit: '%',
      },
      {
        factorName: 'Planting Date',
        factorNameAr: 'تاريخ الزراعة',
        correlation: 0.65,
        impact: 'medium',
        currentValue: 85,
        optimalValue: 95,
        unit: 'score',
      },
      {
        factorName: 'pH Level',
        factorNameAr: 'درجة الحموضة',
        correlation: 0.58,
        impact: 'medium',
        currentValue: 7.2,
        optimalValue: 6.8,
        unit: 'pH',
      },
      {
        factorName: 'Phosphorus',
        factorNameAr: 'الفوسفور',
        correlation: 0.52,
        impact: 'medium',
        currentValue: 28,
        optimalValue: 35,
        unit: 'kg/ha',
      },
      {
        factorName: 'Rainfall',
        factorNameAr: 'الأمطار',
        correlation: 0.45,
        impact: 'low',
        currentValue: 320,
        optimalValue: 400,
        unit: 'mm',
      },
    ],
    contributions: [
      {
        category: 'soil',
        categoryAr: 'التربة',
        contribution: 35,
        score: 68,
        status: 'good',
      },
      {
        category: 'weather',
        categoryAr: 'الطقس',
        contribution: 30,
        score: 72,
        status: 'good',
      },
      {
        category: 'inputs',
        categoryAr: 'المدخلات',
        contribution: 20,
        score: 65,
        status: 'suboptimal',
      },
      {
        category: 'management',
        categoryAr: 'الإدارة',
        contribution: 15,
        score: 82,
        status: 'optimal',
      },
    ],
    limitingFactors: [
      {
        factor: 'Nitrogen Deficiency',
        factorAr: 'نقص النيتروجين',
        category: 'soil',
        categoryAr: 'التربة',
        severity: 'critical',
        currentValue: 85,
        targetValue: 120,
        unit: 'kg/ha',
        impact: 15,
      },
      {
        factor: 'Insufficient Irrigation',
        factorAr: 'ري غير كافي',
        category: 'inputs',
        categoryAr: 'المدخلات',
        severity: 'moderate',
        currentValue: 450,
        targetValue: 550,
        unit: 'mm',
        impact: 10,
      },
      {
        factor: 'Low Organic Matter',
        factorAr: 'مادة عضوية منخفضة',
        category: 'soil',
        categoryAr: 'التربة',
        severity: 'moderate',
        currentValue: 2.8,
        targetValue: 3.5,
        unit: '%',
        impact: 8,
      },
    ],
    recommendations: [
      {
        id: 'rec-1',
        title: 'Increase Nitrogen Application',
        titleAr: 'زيادة إضافة النيتروجين',
        description: 'Apply additional 35 kg/ha of nitrogen fertilizer in split doses during tillering and jointing stages',
        descriptionAr: 'إضافة 35 كجم/هكتار من سماد النيتروجين على دفعات خلال مرحلتي التفريع والاستطالة',
        category: 'inputs',
        categoryAr: 'المدخلات',
        priority: 'high',
        expectedImpact: 12,
        cost: 1200,
        roi: 8.5,
      },
      {
        id: 'rec-2',
        title: 'Optimize Irrigation Schedule',
        titleAr: 'تحسين جدول الري',
        description: 'Add 2-3 additional irrigation cycles during critical growth stages, especially grain filling',
        descriptionAr: 'إضافة 2-3 دورات ري إضافية خلال مراحل النمو الحرجة، خاصة امتلاء الحبوب',
        category: 'inputs',
        categoryAr: 'المدخلات',
        priority: 'high',
        expectedImpact: 8,
        cost: 800,
        roi: 10.2,
      },
      {
        id: 'rec-3',
        title: 'Enhance Soil Organic Matter',
        titleAr: 'تحسين المادة العضوية في التربة',
        description: 'Incorporate compost or cover crops to increase organic matter content by 0.5-1%',
        descriptionAr: 'إضافة السماد العضوي أو المحاصيل الغطائية لزيادة المادة العضوية بنسبة 0.5-1%',
        category: 'soil',
        categoryAr: 'التربة',
        priority: 'medium',
        expectedImpact: 6,
        cost: 1500,
        roi: 4.8,
      },
      {
        id: 'rec-4',
        title: 'Adjust pH Level',
        titleAr: 'تعديل درجة الحموضة',
        description: 'Apply sulfur-based amendments to lower pH from 7.2 to optimal 6.8',
        descriptionAr: 'إضافة محسنات تحتوي على الكبريت لتخفيض الحموضة من 7.2 إلى 6.8 المثالية',
        category: 'soil',
        categoryAr: 'التربة',
        priority: 'medium',
        expectedImpact: 4,
        cost: 600,
        roi: 6.0,
      },
      {
        id: 'rec-5',
        title: 'Phosphorus Top Dressing',
        titleAr: 'إضافة الفوسفور السطحي',
        description: 'Apply 10-15 kg/ha of phosphorus during early growth stages',
        descriptionAr: 'إضافة 10-15 كجم/هكتار من الفوسفور خلال مراحل النمو المبكرة',
        category: 'inputs',
        categoryAr: 'المدخلات',
        priority: 'low',
        expectedImpact: 3,
        cost: 400,
        roi: 5.5,
      },
    ],
  },
  {
    fieldId: '2',
    fieldNameAr: 'الحقل الجنوبي',
    fieldNameEn: 'South Field',
    cropTypeAr: 'ذرة',
    cropTypeEn: 'Corn',
    area: 25,
    currentYield: 8500,
    potentialYield: 10500,
    yieldGap: 19,
    overallScore: 81,
    weather: {
      rainfall: 380,
      temperature: 24,
      growingDegreeDays: 2850,
      humidity: 52,
      solarRadiation: 20.2,
    },
    soil: {
      nitrogen: 110,
      phosphorus: 38,
      potassium: 220,
      pH: 6.8,
      organicMatter: 3.2,
      soilMoisture: 72,
    },
    inputs: {
      fertilizerNPK: 320,
      irrigation: 580,
      pesticides: 4,
      herbicides: 3,
    },
    management: {
      plantingDate: '2024-03-20',
      plantingDateScore: 92,
      varietyQuality: 88,
      tillageScore: 80,
      seedRate: 28,
      spacing: 75,
    },
    correlations: [
      {
        factorName: 'Temperature',
        factorNameAr: 'درجة الحرارة',
        correlation: 0.82,
        impact: 'high',
        currentValue: 24,
        optimalValue: 26,
        unit: '°C',
      },
      {
        factorName: 'Nitrogen',
        factorNameAr: 'النيتروجين',
        correlation: 0.75,
        impact: 'high',
        currentValue: 110,
        optimalValue: 140,
        unit: 'kg/ha',
      },
      {
        factorName: 'Irrigation',
        factorNameAr: 'الري',
        correlation: 0.70,
        impact: 'high',
        currentValue: 580,
        optimalValue: 650,
        unit: 'mm',
      },
      {
        factorName: 'Potassium',
        factorNameAr: 'البوتاسيوم',
        correlation: 0.65,
        impact: 'medium',
        currentValue: 220,
        optimalValue: 250,
        unit: 'kg/ha',
      },
      {
        factorName: 'Planting Date',
        factorNameAr: 'تاريخ الزراعة',
        correlation: 0.62,
        impact: 'medium',
        currentValue: 92,
        optimalValue: 95,
        unit: 'score',
      },
      {
        factorName: 'Organic Matter',
        factorNameAr: 'المادة العضوية',
        correlation: 0.58,
        impact: 'medium',
        currentValue: 3.2,
        optimalValue: 3.5,
        unit: '%',
      },
    ],
    contributions: [
      {
        category: 'weather',
        categoryAr: 'الطقس',
        contribution: 32,
        score: 85,
        status: 'optimal',
      },
      {
        category: 'soil',
        categoryAr: 'التربة',
        contribution: 28,
        score: 78,
        status: 'good',
      },
      {
        category: 'inputs',
        categoryAr: 'المدخلات',
        contribution: 25,
        score: 75,
        status: 'good',
      },
      {
        category: 'management',
        categoryAr: 'الإدارة',
        contribution: 15,
        score: 88,
        status: 'optimal',
      },
    ],
    limitingFactors: [
      {
        factor: 'Nitrogen Below Optimal',
        factorAr: 'النيتروجين أقل من المثالي',
        category: 'soil',
        categoryAr: 'التربة',
        severity: 'moderate',
        currentValue: 110,
        targetValue: 140,
        unit: 'kg/ha',
        impact: 8,
      },
      {
        factor: 'Irrigation Deficit',
        factorAr: 'عجز في الري',
        category: 'inputs',
        categoryAr: 'المدخلات',
        severity: 'moderate',
        currentValue: 580,
        targetValue: 650,
        unit: 'mm',
        impact: 7,
      },
      {
        factor: 'Potassium Deficiency',
        factorAr: 'نقص البوتاسيوم',
        category: 'soil',
        categoryAr: 'التربة',
        severity: 'minor',
        currentValue: 220,
        targetValue: 250,
        unit: 'kg/ha',
        impact: 4,
      },
    ],
    recommendations: [
      {
        id: 'rec-6',
        title: 'Boost Nitrogen Levels',
        titleAr: 'تعزيز مستويات النيتروجين',
        description: 'Apply additional 30 kg/ha nitrogen, split between V6 and V12 growth stages',
        descriptionAr: 'إضافة 30 كجم/هكتار نيتروجين، مقسمة بين مرحلتي V6 و V12',
        category: 'inputs',
        categoryAr: 'المدخلات',
        priority: 'high',
        expectedImpact: 6,
        cost: 1000,
        roi: 7.2,
      },
      {
        id: 'rec-7',
        title: 'Extend Irrigation',
        titleAr: 'توسيع الري',
        description: 'Add irrigation during silking and grain fill stages for maximum kernel development',
        descriptionAr: 'إضافة الري خلال مراحل التحرير وامتلاء الحبوب لتطوير الحبوب بشكل أقصى',
        category: 'inputs',
        categoryAr: 'المدخلات',
        priority: 'high',
        expectedImpact: 5,
        cost: 900,
        roi: 6.8,
      },
      {
        id: 'rec-8',
        title: 'Potassium Supplementation',
        titleAr: 'إضافة البوتاسيوم',
        description: 'Apply 30 kg/ha potassium to improve stress tolerance and grain quality',
        descriptionAr: 'إضافة 30 كجم/هكتار بوتاسيوم لتحسين مقاومة الإجهاد وجودة الحبوب',
        category: 'inputs',
        categoryAr: 'المدخلات',
        priority: 'medium',
        expectedImpact: 3,
        cost: 500,
        roi: 5.0,
      },
    ],
  },
];

// ============================================================================
// Component
// ============================================================================

export const YieldFactorAnalysis: React.FC<YieldFactorAnalysisProps> = ({
  fieldId,
  comparisonMode = false,
}) => {
  const [selectedField, setSelectedField] = useState<string>(mockFieldData[0]?.fieldId ?? '');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    correlations: true,
    contributions: true,
    limiting: true,
    recommendations: true,
    sensitivity: false,
    comparison: false,
  });

  // Filter data based on props
  const displayData = fieldId
    ? mockFieldData.filter((f) => f.fieldId === fieldId)
    : mockFieldData;

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Empty state
  if (!displayData || displayData.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
        <p className="text-gray-600">لا توجد بيانات تحليل العوامل متاحة</p>
        <p className="text-sm text-gray-500 mt-1">No factor analysis data available</p>
      </div>
    );
  }

  const currentFieldData = displayData.find((f) => f.fieldId === selectedField) ?? displayData[0];

  if (!currentFieldData) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
        <p className="text-gray-600">لا توجد بيانات تحليل العوامل متاحة</p>
        <p className="text-sm text-gray-500 mt-1">No factor analysis data available</p>
      </div>
    );
  }

  // Prepare sensitivity analysis data
  const sensitivityData = currentFieldData.correlations.map((corr) => ({
    factor: corr.factorNameAr,
    sensitivity: Math.abs(corr.correlation * 100),
    current: ((corr.currentValue / corr.optimalValue) * 100),
  }));

  // Prepare comparison data
  const comparisonData = displayData.map((field) => ({
    name: field.fieldNameAr,
    weather: field.contributions.find((c) => c.category === 'weather')?.score || 0,
    soil: field.contributions.find((c) => c.category === 'soil')?.score || 0,
    inputs: field.contributions.find((c) => c.category === 'inputs')?.score || 0,
    management: field.contributions.find((c) => c.category === 'management')?.score || 0,
    overall: field.overallScore,
  }));

  return (
    <div className="space-y-6" data-testid="yield-factor-analysis">
      {/* Header & Field Selector */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 p-6 rounded-xl shadow-lg text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3">
              <BarChart3 className="w-8 h-8" />
              <span>تحليل عوامل المحصول المتقدم</span>
            </h2>
            <p className="text-green-100 mt-1 text-sm">
              Advanced Yield Factor Analysis
            </p>
          </div>
          {displayData.length > 1 && (
            <select
              data-testid="field-selector"
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
              className="bg-white text-gray-900 px-4 py-2 rounded-lg font-medium shadow-md focus:outline-none focus:ring-2 focus:ring-green-300"
            >
              {displayData.map((field) => (
                <option key={field.fieldId} value={field.fieldId}>
                  {field.fieldNameAr} - {field.cropTypeAr}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm border-2 border-blue-200" data-testid="current-yield-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">المحصول الحالي</p>
              <p className="text-xs text-gray-500">Current Yield</p>
            </div>
            <Leaf className="w-8 h-8 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {currentFieldData.currentYield.toLocaleString('ar-SA')}
          </p>
          <p className="text-sm text-gray-600 mt-1">كجم/هكتار</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border-2 border-green-200" data-testid="potential-yield-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">الإنتاجية المحتملة</p>
              <p className="text-xs text-gray-500">Potential Yield</p>
            </div>
            <Target className="w-8 h-8 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {currentFieldData.potentialYield.toLocaleString('ar-SA')}
          </p>
          <p className="text-sm text-gray-600 mt-1">كجم/هكتار</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border-2 border-amber-200" data-testid="yield-gap-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">فجوة المحصول</p>
              <p className="text-xs text-gray-500">Yield Gap</p>
            </div>
            <TrendingUp className="w-8 h-8 text-amber-500" />
          </div>
          <p className="text-3xl font-bold text-amber-600 mt-2">
            {currentFieldData.yieldGap}%
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {(currentFieldData.potentialYield - currentFieldData.currentYield).toLocaleString('ar-SA')} كجم
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border-2 border-purple-200" data-testid="overall-score-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">النتيجة الإجمالية</p>
              <p className="text-xs text-gray-500">Overall Score</p>
            </div>
            <Activity className="w-8 h-8 text-purple-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {currentFieldData.overallScore}/100
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className="bg-purple-500 h-2 rounded-full transition-all"
              style={{ width: `${currentFieldData.overallScore}%` }}
            />
          </div>
        </div>
      </div>

      {/* Factor Contributions */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('contributions')}
          className="w-full flex items-center justify-between text-left"
          data-testid="contributions-toggle"
        >
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-600" />
            <span>مساهمة العوامل في المحصول</span>
            <span className="text-sm text-gray-500 font-normal">Factor Contribution Breakdown</span>
          </h3>
          {expandedSections.contributions ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>

        {expandedSections.contributions && (
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pie Chart */}
            <div data-testid="contribution-pie-chart">
              <h4 className="text-sm font-medium text-gray-700 mb-4 text-center">
                توزيع المساهمة (Contribution Distribution)
              </h4>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={currentFieldData.contributions}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: { categoryAr: string; contribution: number }) => `${entry.categoryAr}: ${entry.contribution}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="contribution"
                  >
                    {currentFieldData.contributions.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CATEGORY_COLORS[entry.category as keyof typeof CATEGORY_COLORS]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Bar Chart */}
            <div data-testid="contribution-bar-chart">
              <h4 className="text-sm font-medium text-gray-700 mb-4 text-center">
                نقاط الأداء (Performance Scores)
              </h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={currentFieldData.contributions} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis type="category" dataKey="categoryAr" width={80} />
                  <Tooltip />
                  <Bar dataKey="score" name="النقاط">
                    {currentFieldData.contributions.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={STATUS_COLORS[entry.status as keyof typeof STATUS_COLORS]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {expandedSections.contributions && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {currentFieldData.contributions.map((contrib, index) => {
              const Icon =
                contrib.category === 'weather'
                  ? Cloud
                  : contrib.category === 'soil'
                  ? Leaf
                  : contrib.category === 'inputs'
                  ? Droplets
                  : Calendar;

              return (
                <div
                  key={index}
                  className="p-4 rounded-lg border-2"
                  style={{
                    backgroundColor: `${CATEGORY_COLORS[contrib.category as keyof typeof CATEGORY_COLORS]}10`,
                    borderColor: CATEGORY_COLORS[contrib.category as keyof typeof CATEGORY_COLORS],
                  }}
                  data-testid={`contribution-card-${contrib.category}`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Icon
                      className="w-5 h-5"
                      style={{ color: CATEGORY_COLORS[contrib.category as keyof typeof CATEGORY_COLORS] }}
                    />
                    <h4 className="font-semibold text-gray-900">{contrib.categoryAr}</h4>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{contrib.contribution}%</p>
                  <p className="text-sm text-gray-600 mt-1">نقاط: {contrib.score}/100</p>
                  <div className="mt-2 flex items-center gap-2">
                    <div
                      className="px-2 py-1 rounded text-xs font-medium"
                      style={{
                        backgroundColor: STATUS_COLORS[contrib.status as keyof typeof STATUS_COLORS],
                        color: 'white',
                      }}
                    >
                      {contrib.status === 'optimal' && 'مثالي'}
                      {contrib.status === 'good' && 'جيد'}
                      {contrib.status === 'suboptimal' && 'دون المثالي'}
                      {contrib.status === 'poor' && 'ضعيف'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Correlation Analysis */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('correlations')}
          className="w-full flex items-center justify-between text-left"
          data-testid="correlations-toggle"
        >
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <span>تحليل الارتباط متعدد العوامل</span>
            <span className="text-sm text-gray-500 font-normal">Multi-Factor Correlation</span>
          </h3>
          {expandedSections.correlations ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>

        {expandedSections.correlations && (
          <div className="mt-6">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={currentFieldData.correlations}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="factorNameAr" angle={-45} textAnchor="end" height={100} />
                <YAxis domain={[0, 1]} />
                <Tooltip
                  content={({ active, payload }: { active?: boolean; payload?: Array<{ payload: FactorCorrelation }> }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0]?.payload;
                      if (!data) return null;
                      return (
                        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
                          <p className="font-semibold text-gray-900">{data.factorNameAr}</p>
                          <p className="text-sm text-gray-600">{data.factorName}</p>
                          <p className="text-sm mt-2">
                            <span className="font-medium">الارتباط:</span> {data.correlation.toFixed(2)}
                          </p>
                          <p className="text-sm">
                            <span className="font-medium">القيمة الحالية:</span> {data.currentValue} {data.unit}
                          </p>
                          <p className="text-sm">
                            <span className="font-medium">القيمة المثلى:</span> {data.optimalValue} {data.unit}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Bar dataKey="correlation" name="معامل الارتباط" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentFieldData.correlations.slice(0, 6).map((corr, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg border-2 border-gray-200 hover:border-blue-400 transition-colors"
                  data-testid={`correlation-card-${index}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900 text-sm">{corr.factorNameAr}</h4>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium text-white ${
                        corr.impact === 'high'
                          ? 'bg-red-500'
                          : corr.impact === 'medium'
                          ? 'bg-amber-500'
                          : 'bg-blue-500'
                      }`}
                    >
                      {corr.impact === 'high' && 'عالي'}
                      {corr.impact === 'medium' && 'متوسط'}
                      {corr.impact === 'low' && 'منخفض'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2">{corr.factorName}</p>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">الارتباط:</span>
                      <span className="font-semibold text-gray-900">{corr.correlation.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">الحالي:</span>
                      <span className="font-semibold text-gray-900">
                        {corr.currentValue} {corr.unit}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">المثالي:</span>
                      <span className="font-semibold text-green-600">
                        {corr.optimalValue} {corr.unit}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${Math.abs(corr.correlation) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Sensitivity Analysis */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('sensitivity')}
          className="w-full flex items-center justify-between text-left"
          data-testid="sensitivity-toggle"
        >
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            <span>تحليل الحساسية</span>
            <span className="text-sm text-gray-500 font-normal">Sensitivity Analysis</span>
          </h3>
          {expandedSections.sensitivity ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>

        {expandedSections.sensitivity && (
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar Chart */}
            <div data-testid="sensitivity-radar-chart">
              <h4 className="text-sm font-medium text-gray-700 mb-4 text-center">
                حساسية العوامل (Factor Sensitivity)
              </h4>
              <ResponsiveContainer width="100%" height={350}>
                <RadarChart data={sensitivityData.slice(0, 6)}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="factor" />
                  <PolarRadiusAxis domain={[0, 100]} />
                  <Radar
                    name="الحساسية"
                    dataKey="sensitivity"
                    stroke="#8b5cf6"
                    fill="#8b5cf6"
                    fillOpacity={0.6}
                  />
                  <Radar
                    name="الحالة الحالية"
                    dataKey="current"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.3}
                  />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Scatter Plot */}
            <div data-testid="sensitivity-scatter-chart">
              <h4 className="text-sm font-medium text-gray-700 mb-4 text-center">
                الحساسية مقابل الحالة (Sensitivity vs Current State)
              </h4>
              <ResponsiveContainer width="100%" height={350}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="current"
                    name="الحالة الحالية"
                    domain={[0, 120]}
                    label={{ value: 'Current State (%)', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="sensitivity"
                    name="الحساسية"
                    domain={[0, 100]}
                    label={{ value: 'Sensitivity', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter name="العوامل" data={sensitivityData} fill="#8b5cf6" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* Limiting Factors */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('limiting')}
          className="w-full flex items-center justify-between text-left"
          data-testid="limiting-factors-toggle"
        >
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span>العوامل المحددة للمحصول</span>
            <span className="text-sm text-gray-500 font-normal">Limiting Factors</span>
          </h3>
          {expandedSections.limiting ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>

        {expandedSections.limiting && (
          <div className="mt-6 space-y-4">
            {currentFieldData.limitingFactors.map((factor, index) => (
              <div
                key={index}
                className={`p-5 rounded-lg border-l-4 ${
                  factor.severity === 'critical'
                    ? 'bg-red-50 border-red-500'
                    : factor.severity === 'moderate'
                    ? 'bg-amber-50 border-amber-500'
                    : 'bg-yellow-50 border-yellow-500'
                }`}
                data-testid={`limiting-factor-${index}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <AlertTriangle
                        className={`w-5 h-5 ${
                          factor.severity === 'critical'
                            ? 'text-red-600'
                            : factor.severity === 'moderate'
                            ? 'text-amber-600'
                            : 'text-yellow-600'
                        }`}
                      />
                      <h4 className="font-semibold text-gray-900">{factor.factorAr}</h4>
                      <span
                        className="px-3 py-1 rounded-full text-xs font-medium text-white"
                        style={{ backgroundColor: SEVERITY_COLORS[factor.severity] }}
                      >
                        {factor.severity === 'critical' && 'حرج'}
                        {factor.severity === 'moderate' && 'متوسط'}
                        {factor.severity === 'minor' && 'طفيف'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{factor.factor}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">الفئة</p>
                        <p className="font-semibold text-gray-900">{factor.categoryAr}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">القيمة الحالية</p>
                        <p className="font-semibold text-gray-900">
                          {factor.currentValue} {factor.unit}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">القيمة المستهدفة</p>
                        <p className="font-semibold text-green-600">
                          {factor.targetValue} {factor.unit}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">التأثير على المحصول</p>
                        <p className="font-semibold text-red-600">-{factor.impact}%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('recommendations')}
          className="w-full flex items-center justify-between text-left"
          data-testid="recommendations-toggle"
        >
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Info className="w-5 h-5 text-yellow-600" />
            <span>التوصيات والتحسينات</span>
            <span className="text-sm text-gray-500 font-normal">Recommendations & Optimization</span>
          </h3>
          {expandedSections.recommendations ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>

        {expandedSections.recommendations && (
          <div className="mt-6 space-y-4">
            {currentFieldData.recommendations.map((rec, index) => (
              <div
                key={rec.id}
                className="p-5 rounded-lg border-2 border-gray-200 hover:border-green-400 transition-colors"
                data-testid={`recommendation-${index}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className="px-3 py-1 rounded-full text-xs font-medium text-white"
                        style={{ backgroundColor: PRIORITY_COLORS[rec.priority] }}
                      >
                        {rec.priority === 'high' && 'أولوية عالية'}
                        {rec.priority === 'medium' && 'أولوية متوسطة'}
                        {rec.priority === 'low' && 'أولوية منخفضة'}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {rec.categoryAr}
                      </span>
                    </div>
                    <h4 className="font-semibold text-gray-900 text-lg">{rec.titleAr}</h4>
                    <p className="text-sm text-gray-600 mt-1">{rec.title}</p>
                  </div>
                  <Info className="w-6 h-6 text-yellow-500 flex-shrink-0" />
                </div>

                <p className="text-gray-700 mb-3">{rec.descriptionAr}</p>
                <p className="text-sm text-gray-600 mb-4">{rec.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="text-xs text-gray-600">التأثير المتوقع</p>
                      <p className="font-semibold text-green-600">+{rec.expectedImpact}%</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Sprout className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="text-xs text-gray-600">التكلفة</p>
                      <p className="font-semibold text-gray-900">
                        {rec.cost.toLocaleString('ar-SA')} ريال
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="text-xs text-gray-600">العائد على الاستثمار</p>
                      <p className="font-semibold text-purple-600">{rec.roi.toFixed(1)}x</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Summary */}
            <div className="mt-6 p-5 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border-2 border-green-200">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Target className="w-5 h-5 text-green-600" />
                <span>ملخص التوصيات (Recommendations Summary)</span>
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">إجمالي التأثير المتوقع</p>
                  <p className="text-2xl font-bold text-green-600">
                    +
                    {currentFieldData.recommendations
                      .reduce((sum, rec) => sum + rec.expectedImpact, 0)
                      .toFixed(1)}
                    %
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">إجمالي التكلفة</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {currentFieldData.recommendations
                      .reduce((sum, rec) => sum + rec.cost, 0)
                      .toLocaleString('ar-SA')}{' '}
                    ريال
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">متوسط العائد</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {(
                      currentFieldData.recommendations.reduce((sum, rec) => sum + rec.roi, 0) /
                      currentFieldData.recommendations.length
                    ).toFixed(1)}
                    x
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Comparison Mode */}
      {comparisonMode && displayData.length > 1 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <button
            onClick={() => toggleSection('comparison')}
            className="w-full flex items-center justify-between text-left"
            data-testid="comparison-toggle"
          >
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-600" />
              <span>المقارنة بين الحقول</span>
              <span className="text-sm text-gray-500 font-normal">Field Comparison</span>
            </h3>
            {expandedSections.comparison ? (
              <ChevronUp className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            )}
          </button>

          {expandedSections.comparison && (
            <div className="mt-6">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="weather" name="الطقس" fill={CATEGORY_COLORS.weather} />
                  <Bar dataKey="soil" name="التربة" fill={CATEGORY_COLORS.soil} />
                  <Bar dataKey="inputs" name="المدخلات" fill={CATEGORY_COLORS.inputs} />
                  <Bar dataKey="management" name="الإدارة" fill={CATEGORY_COLORS.management} />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {displayData.map((field) => (
                  <div
                    key={field.fieldId}
                    className="p-4 rounded-lg border-2 border-gray-200 hover:border-indigo-400 transition-colors"
                    data-testid={`comparison-card-${field.fieldId}`}
                  >
                    <h4 className="font-semibold text-gray-900 mb-2">{field.fieldNameAr}</h4>
                    <p className="text-sm text-gray-600 mb-3">{field.cropTypeAr}</p>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">النتيجة الإجمالية:</span>
                        <span className="font-semibold text-gray-900">{field.overallScore}/100</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">فجوة المحصول:</span>
                        <span className="font-semibold text-amber-600">{field.yieldGap}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">عوامل محددة:</span>
                        <span className="font-semibold text-red-600">
                          {field.limitingFactors.length}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default YieldFactorAnalysis;
