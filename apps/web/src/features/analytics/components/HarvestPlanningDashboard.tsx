/**
 * Harvest Planning Dashboard Component
 * لوحة معلومات تخطيط الحصاد
 *
 * Advanced harvest planning and optimization similar to John Deere Operations Center
 * and Climate FieldView. Provides harvest readiness tracking, optimal timing,
 * weather integration, equipment management, and yield predictions.
 */

'use client';

import React, { useState } from 'react';
import {
  Calendar,
  Sun,
  Cloud,
  Loader2,
  Check,
  AlertCircle,
  TrendingUp,
  MapPin,
  Leaf,
  RefreshCw,
} from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

/**
 * Field readiness status
 * حالة جاهزية الحقل
 */
export type ReadinessStatus = 'ready' | 'almost_ready' | 'not_ready';

/**
 * Quality grade classification
 * تصنيف درجة الجودة
 */
export type QualityGrade = 'premium' | 'grade_a' | 'grade_b' | 'grade_c';

/**
 * Equipment status
 * حالة المعدات
 */
export type EquipmentStatus = 'available' | 'in_use' | 'maintenance' | 'unavailable';

/**
 * Weather condition
 * حالة الطقس
 */
export interface WeatherForecast {
  date: string;
  dateAr: string;
  tempHigh: number; // Celsius
  tempLow: number;
  precipitation: number; // mm
  humidity: number; // percentage
  windSpeed: number; // km/h
  condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy';
  conditionAr: string;
  harvestSuitability: 'excellent' | 'good' | 'fair' | 'poor';
  harvestSuitabilityAr: string;
}

/**
 * Harvest window - optimal time period for harvesting
 * نافذة الحصاد - الفترة المثلى للحصاد
 */
export interface HarvestWindow {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  startDate: string;
  endDate: string;
  optimalDate: string;
  confidence: number; // percentage
  reason: string;
  reasonAr: string;
}

/**
 * Field harvest readiness details
 * تفاصيل جاهزية الحقل للحصاد
 */
export interface FieldReadiness {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  area: number; // hectares
  location: {
    lat: number;
    lng: number;
    region: string;
    regionAr: string;
  };
  status: ReadinessStatus;
  statusAr: string;
  maturityLevel: number; // percentage 0-100
  moistureContent: number; // percentage
  optimalMoisture: number; // percentage
  daysToOptimal: number;
  predictedYield: number; // kg
  yieldPerHectare: number; // kg/ha
  qualityGrade: QualityGrade;
  qualityGradeAr: string;
  qualityScore: number; // 0-100
  priority: number; // 1-10, higher is more urgent
  lastUpdated: string;
}

/**
 * Equipment availability
 * توفر المعدات
 */
export interface Equipment {
  id: string;
  name: string;
  nameAr: string;
  type: string;
  typeAr: string;
  status: EquipmentStatus;
  statusAr: string;
  capacity: number; // hectares per day
  availableDate?: string;
  assignedField?: string;
  maintenanceDue?: string;
  efficiency: number; // percentage
}

/**
 * Complete harvest plan
 * خطة الحصاد الكاملة
 */
export interface HarvestPlan {
  id: string;
  farmId: string;
  season: string;
  fields: FieldReadiness[];
  harvestWindows: HarvestWindow[];
  equipment: Equipment[];
  weatherForecast: WeatherForecast[];
  totalArea: number;
  totalPredictedYield: number;
  estimatedDuration: number; // days
  createdAt: string;
  updatedAt: string;
}

// ============================================================================
// Mock Data for Demo/Testing
// ============================================================================

const mockWeatherForecast: WeatherForecast[] = [
  {
    date: '2025-12-31',
    dateAr: '٣١ ديسمبر',
    tempHigh: 28,
    tempLow: 18,
    precipitation: 0,
    humidity: 45,
    windSpeed: 12,
    condition: 'sunny',
    conditionAr: 'مشمس',
    harvestSuitability: 'excellent',
    harvestSuitabilityAr: 'ممتاز',
  },
  {
    date: '2026-01-01',
    dateAr: '١ يناير',
    tempHigh: 27,
    tempLow: 17,
    precipitation: 0,
    humidity: 48,
    windSpeed: 10,
    condition: 'sunny',
    conditionAr: 'مشمس',
    harvestSuitability: 'excellent',
    harvestSuitabilityAr: 'ممتاز',
  },
  {
    date: '2026-01-02',
    dateAr: '٢ يناير',
    tempHigh: 26,
    tempLow: 16,
    precipitation: 2,
    humidity: 55,
    windSpeed: 15,
    condition: 'cloudy',
    conditionAr: 'غائم',
    harvestSuitability: 'good',
    harvestSuitabilityAr: 'جيد',
  },
  {
    date: '2026-01-03',
    dateAr: '٣ يناير',
    tempHigh: 25,
    tempLow: 15,
    precipitation: 8,
    humidity: 65,
    windSpeed: 20,
    condition: 'rainy',
    conditionAr: 'ممطر',
    harvestSuitability: 'poor',
    harvestSuitabilityAr: 'ضعيف',
  },
  {
    date: '2026-01-04',
    dateAr: '٤ يناير',
    tempHigh: 27,
    tempLow: 17,
    precipitation: 1,
    humidity: 50,
    windSpeed: 11,
    condition: 'cloudy',
    conditionAr: 'غائم جزئياً',
    harvestSuitability: 'good',
    harvestSuitabilityAr: 'جيد',
  },
];

const mockEquipment: Equipment[] = [
  {
    id: 'eq1',
    name: 'Combine Harvester CH-2000',
    nameAr: 'حصادة مجمعة CH-2000',
    type: 'Combine Harvester',
    typeAr: 'حصادة مجمعة',
    status: 'available',
    statusAr: 'متاح',
    capacity: 15,
    efficiency: 92,
  },
  {
    id: 'eq2',
    name: 'Combine Harvester CH-1800',
    nameAr: 'حصادة مجمعة CH-1800',
    type: 'Combine Harvester',
    typeAr: 'حصادة مجمعة',
    status: 'in_use',
    statusAr: 'قيد الاستخدام',
    capacity: 12,
    assignedField: 'الحقل الشمالي',
    efficiency: 88,
  },
  {
    id: 'eq3',
    name: 'Grain Trailer GT-500',
    nameAr: 'مقطورة حبوب GT-500',
    type: 'Grain Trailer',
    typeAr: 'مقطورة حبوب',
    status: 'available',
    statusAr: 'متاح',
    capacity: 20,
    efficiency: 95,
  },
  {
    id: 'eq4',
    name: 'Tractor T-400',
    nameAr: 'جرار T-400',
    type: 'Tractor',
    typeAr: 'جرار',
    status: 'maintenance',
    statusAr: 'تحت الصيانة',
    capacity: 8,
    availableDate: '2026-01-05',
    maintenanceDue: '2026-01-04',
    efficiency: 85,
  },
];

const mockFieldsReadiness: FieldReadiness[] = [
  {
    fieldId: 'field1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    area: 45,
    location: {
      lat: 15.5527,
      lng: 48.5164,
      region: 'Sana\'a',
      regionAr: 'صنعاء',
    },
    status: 'ready',
    statusAr: 'جاهز للحصاد',
    maturityLevel: 98,
    moistureContent: 14,
    optimalMoisture: 14,
    daysToOptimal: 0,
    predictedYield: 18000,
    yieldPerHectare: 400,
    qualityGrade: 'premium',
    qualityGradeAr: 'ممتاز',
    qualityScore: 95,
    priority: 10,
    lastUpdated: '2025-12-30T08:00:00Z',
  },
  {
    fieldId: 'field2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    area: 35,
    location: {
      lat: 15.5427,
      lng: 48.5264,
      region: 'Sana\'a',
      regionAr: 'صنعاء',
    },
    status: 'almost_ready',
    statusAr: 'شبه جاهز',
    maturityLevel: 92,
    moistureContent: 16,
    optimalMoisture: 14,
    daysToOptimal: 3,
    predictedYield: 10500,
    yieldPerHectare: 300,
    qualityGrade: 'grade_a',
    qualityGradeAr: 'درجة أولى',
    qualityScore: 88,
    priority: 7,
    lastUpdated: '2025-12-30T08:00:00Z',
  },
  {
    fieldId: 'field3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    cropType: 'Sorghum',
    cropTypeAr: 'ذرة رفيعة',
    area: 28,
    location: {
      lat: 15.5627,
      lng: 48.5364,
      region: 'Sana\'a',
      regionAr: 'صنعاء',
    },
    status: 'almost_ready',
    statusAr: 'شبه جاهز',
    maturityLevel: 89,
    moistureContent: 18,
    optimalMoisture: 15,
    daysToOptimal: 5,
    predictedYield: 8400,
    yieldPerHectare: 300,
    qualityGrade: 'grade_a',
    qualityGradeAr: 'درجة أولى',
    qualityScore: 85,
    priority: 5,
    lastUpdated: '2025-12-30T08:00:00Z',
  },
  {
    fieldId: 'field4',
    fieldName: 'West Field',
    fieldNameAr: 'الحقل الغربي',
    cropType: 'Millet',
    cropTypeAr: 'دخن',
    area: 22,
    location: {
      lat: 15.5327,
      lng: 48.5064,
      region: 'Sana\'a',
      regionAr: 'صنعاء',
    },
    status: 'not_ready',
    statusAr: 'غير جاهز',
    maturityLevel: 75,
    moistureContent: 22,
    optimalMoisture: 14,
    daysToOptimal: 12,
    predictedYield: 6600,
    yieldPerHectare: 300,
    qualityGrade: 'grade_b',
    qualityGradeAr: 'درجة ثانية',
    qualityScore: 72,
    priority: 2,
    lastUpdated: '2025-12-30T08:00:00Z',
  },
];

const mockHarvestWindows: HarvestWindow[] = [
  {
    fieldId: 'field1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    startDate: '2025-12-30',
    endDate: '2026-01-05',
    optimalDate: '2025-12-31',
    confidence: 95,
    reason: 'Perfect maturity and weather conditions',
    reasonAr: 'نضج مثالي وظروف جوية ممتازة',
  },
  {
    fieldId: 'field2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    startDate: '2026-01-02',
    endDate: '2026-01-08',
    optimalDate: '2026-01-04',
    confidence: 88,
    reason: 'Needs slight moisture reduction',
    reasonAr: 'يحتاج إلى تقليل طفيف في الرطوبة',
  },
  {
    fieldId: 'field3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    startDate: '2026-01-05',
    endDate: '2026-01-12',
    optimalDate: '2026-01-07',
    confidence: 82,
    reason: 'Allow for further maturation',
    reasonAr: 'السماح بمزيد من النضج',
  },
];

const mockHarvestPlan: HarvestPlan = {
  id: 'hp1',
  farmId: 'farm1',
  season: '2025/2026',
  fields: mockFieldsReadiness,
  harvestWindows: mockHarvestWindows,
  equipment: mockEquipment,
  weatherForecast: mockWeatherForecast,
  totalArea: 130,
  totalPredictedYield: 43500,
  estimatedDuration: 14,
  createdAt: '2025-12-30T08:00:00Z',
  updatedAt: '2025-12-30T08:00:00Z',
};

// ============================================================================
// Helper Functions
// ============================================================================

const getReadinessColor = (status: ReadinessStatus): string => {
  switch (status) {
    case 'ready':
      return 'bg-green-100 border-green-300 text-green-800';
    case 'almost_ready':
      return 'bg-yellow-100 border-yellow-300 text-yellow-800';
    case 'not_ready':
      return 'bg-gray-100 border-gray-300 text-gray-800';
  }
};

const getReadinessIcon = (status: ReadinessStatus) => {
  switch (status) {
    case 'ready':
      return Check;
    case 'almost_ready':
      return Loader2;
    case 'not_ready':
      return AlertCircle;
  }
};

const getQualityColor = (grade: QualityGrade): string => {
  switch (grade) {
    case 'premium':
      return 'text-green-700 bg-green-50';
    case 'grade_a':
      return 'text-blue-700 bg-blue-50';
    case 'grade_b':
      return 'text-yellow-700 bg-yellow-50';
    case 'grade_c':
      return 'text-gray-700 bg-gray-50';
  }
};

const getEquipmentStatusColor = (status: EquipmentStatus): string => {
  switch (status) {
    case 'available':
      return 'bg-green-100 text-green-800';
    case 'in_use':
      return 'bg-blue-100 text-blue-800';
    case 'maintenance':
      return 'bg-yellow-100 text-yellow-800';
    case 'unavailable':
      return 'bg-red-100 text-red-800';
  }
};

const getWeatherIcon = (condition: WeatherForecast['condition']) => {
  switch (condition) {
    case 'sunny':
      return Sun;
    case 'cloudy':
    case 'rainy':
    case 'stormy':
      return Cloud;
  }
};

const getSuitabilityColor = (suitability: WeatherForecast['harvestSuitability']): string => {
  switch (suitability) {
    case 'excellent':
      return 'bg-green-100 text-green-800';
    case 'good':
      return 'bg-blue-100 text-blue-800';
    case 'fair':
      return 'bg-yellow-100 text-yellow-800';
    case 'poor':
      return 'bg-red-100 text-red-800';
  }
};

// ============================================================================
// Main Component
// ============================================================================

export const HarvestPlanningDashboard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error] = useState<string | null>(null);
  const [harvestPlan] = useState<HarvestPlan>(mockHarvestPlan);
  const [selectedField, setSelectedField] = useState<string | null>(null);

  // Simulate refresh action
  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 1500);
  };

  // Loading state
  if (isLoading && !harvestPlan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto" />
          <p className="mt-4 text-gray-600">جاري تحميل خطة الحصاد...</p>
          <p className="text-sm text-gray-500">Loading harvest plan...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-red-200 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto" />
          <h3 className="mt-4 text-lg font-semibold text-gray-900 text-center">
            حدث خطأ
          </h3>
          <p className="mt-2 text-sm text-gray-600 text-center">{error}</p>
          <button
            onClick={handleRefresh}
            className="mt-6 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  const readyFields = harvestPlan.fields.filter(f => f.status === 'ready');
  const almostReadyFields = harvestPlan.fields.filter(f => f.status === 'almost_ready');
  const notReadyFields = harvestPlan.fields.filter(f => f.status === 'not_ready');

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                تخطيط الحصاد
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Harvest Planning Dashboard
              </p>
            </div>

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
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" data-testid="summary-cards">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <Leaf className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">إجمالي المساحة</p>
                <p className="text-2xl font-bold text-gray-900">
                  {harvestPlan.totalArea.toLocaleString('ar-SA')}
                </p>
                <p className="text-xs text-gray-500">هكتار</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">المحصول المتوقع</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(harvestPlan.totalPredictedYield / 1000).toLocaleString('ar-SA', { maximumFractionDigits: 1 })}
                </p>
                <p className="text-xs text-gray-500">طن</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <Check className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">حقول جاهزة</p>
                <p className="text-2xl font-bold text-green-600">
                  {readyFields.length.toLocaleString('ar-SA')}
                </p>
                <p className="text-xs text-gray-500">من {harvestPlan.fields.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Calendar className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">المدة المتوقعة</p>
                <p className="text-2xl font-bold text-gray-900">
                  {harvestPlan.estimatedDuration.toLocaleString('ar-SA')}
                </p>
                <p className="text-xs text-gray-500">يوم</p>
              </div>
            </div>
          </div>
        </div>

        {/* Field Readiness Indicators */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            جاهزية الحقول
            <span className="text-sm font-normal text-gray-500 mr-2">Field Readiness</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {harvestPlan.fields
              .sort((a, b) => b.priority - a.priority)
              .map((field) => {
                const ReadinessIcon = getReadinessIcon(field.status);
                return (
                  <div
                    key={field.fieldId}
                    className={`p-6 rounded-xl shadow-sm border-2 cursor-pointer transition-all hover:shadow-md ${
                      getReadinessColor(field.status)
                    } ${selectedField === field.fieldId ? 'ring-2 ring-green-500' : ''}`}
                    onClick={() => setSelectedField(field.fieldId)}
                    data-testid={`field-card-${field.fieldId}`}
                  >
                    {/* Field Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          <h3 className="font-bold text-lg">{field.fieldNameAr}</h3>
                        </div>
                        <p className="text-sm mt-1">{field.cropTypeAr}</p>
                      </div>
                      <ReadinessIcon className="w-6 h-6" />
                    </div>

                    {/* Status Badge */}
                    <div className="mb-4">
                      <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-white bg-opacity-80">
                        {field.statusAr}
                      </span>
                    </div>

                    {/* Metrics */}
                    <div className="space-y-3">
                      {/* Maturity Progress */}
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>مستوى النضج</span>
                          <span className="font-semibold">{field.maturityLevel}%</span>
                        </div>
                        <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
                          <div
                            className="bg-current rounded-full h-2 transition-all"
                            style={{ width: `${field.maturityLevel}%` }}
                          />
                        </div>
                      </div>

                      {/* Key Metrics */}
                      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-current border-opacity-20">
                        <div>
                          <p className="text-xs opacity-75">المساحة</p>
                          <p className="font-semibold">{field.area} هكتار</p>
                        </div>
                        <div>
                          <p className="text-xs opacity-75">الأولوية</p>
                          <p className="font-semibold">{field.priority}/10</p>
                        </div>
                        <div>
                          <p className="text-xs opacity-75">المحصول المتوقع</p>
                          <p className="font-semibold">{(field.predictedYield / 1000).toFixed(1)} طن</p>
                        </div>
                        <div>
                          <p className="text-xs opacity-75">الجودة</p>
                          <p className="font-semibold text-xs">{field.qualityGradeAr}</p>
                        </div>
                      </div>

                      {/* Days to Optimal */}
                      {field.daysToOptimal > 0 && (
                        <div className="pt-3 border-t border-current border-opacity-20">
                          <p className="text-sm">
                            <Calendar className="w-4 h-4 inline ml-1" />
                            <span className="font-semibold">{field.daysToOptimal}</span> يوم حتى الوقت الأمثل
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Harvest Windows Calendar */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            نوافذ الحصاد المثلى
            <span className="text-sm font-normal text-gray-500 mr-2">Optimal Harvest Windows</span>
          </h2>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="space-y-4">
              {harvestPlan.harvestWindows.map((window) => (
                <div
                  key={window.fieldId}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                  data-testid={`harvest-window-${window.fieldId}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-900">{window.fieldNameAr}</h4>
                      <p className="text-sm text-gray-600 mt-1">{window.reasonAr}</p>
                    </div>
                    <div className="text-left">
                      <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                        ثقة {window.confidence}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-500" />
                      <div>
                        <p className="text-xs text-gray-600">فترة الحصاد</p>
                        <p className="font-semibold text-sm">
                          {new Date(window.startDate).toLocaleDateString('ar-SA')} - {new Date(window.endDate).toLocaleDateString('ar-SA')}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-600" />
                      <div>
                        <p className="text-xs text-gray-600">التاريخ الأمثل</p>
                        <p className="font-semibold text-sm text-green-600">
                          {new Date(window.optimalDate).toLocaleDateString('ar-SA')}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-600" />
                      <div>
                        <p className="text-xs text-gray-600">الأيام المتبقية</p>
                        <p className="font-semibold text-sm">
                          {Math.max(0, Math.ceil((new Date(window.optimalDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)))} يوم
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Weather Forecast Integration */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            توقعات الطقس للحصاد
            <span className="text-sm font-normal text-gray-500 mr-2">Weather Forecast for Harvest</span>
          </h2>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {harvestPlan.weatherForecast.map((forecast) => {
                const WeatherIcon = getWeatherIcon(forecast.condition);
                return (
                  <div
                    key={forecast.date}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200 text-center"
                    data-testid={`weather-${forecast.date}`}
                  >
                    <p className="text-sm font-semibold text-gray-900">{forecast.dateAr}</p>
                    <WeatherIcon className="w-10 h-10 mx-auto my-3 text-yellow-500" />
                    <p className="text-xs text-gray-600 mb-2">{forecast.conditionAr}</p>

                    <div className="mb-3">
                      <p className="text-2xl font-bold text-gray-900">
                        {forecast.tempHigh}°
                      </p>
                      <p className="text-sm text-gray-500">{forecast.tempLow}°</p>
                    </div>

                    <div className="space-y-1 text-xs text-gray-600">
                      <p>💧 {forecast.humidity}%</p>
                      <p>🌧️ {forecast.precipitation} مم</p>
                      <p>💨 {forecast.windSpeed} كم/س</p>
                    </div>

                    <div className="mt-3">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${getSuitabilityColor(forecast.harvestSuitability)}`}>
                        {forecast.harvestSuitabilityAr}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Two Column Layout: Equipment & Quality Predictions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Equipment Availability */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              توفر المعدات
              <span className="text-sm font-normal text-gray-500 mr-2">Equipment Availability</span>
            </h2>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="space-y-4">
                {harvestPlan.equipment.map((equipment) => (
                  <div
                    key={equipment.id}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                    data-testid={`equipment-${equipment.id}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{equipment.nameAr}</h4>
                        <p className="text-sm text-gray-600">{equipment.typeAr}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getEquipmentStatusColor(equipment.status)}`}>
                        {equipment.statusAr}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-gray-600">السعة</p>
                        <p className="font-semibold text-sm">{equipment.capacity} هكتار/يوم</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">الكفاءة</p>
                        <p className="font-semibold text-sm">{equipment.efficiency}%</p>
                      </div>
                    </div>

                    {equipment.assignedField && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs text-gray-600">
                          مخصص لـ: <span className="font-semibold">{equipment.assignedField}</span>
                        </p>
                      </div>
                    )}

                    {equipment.availableDate && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs text-gray-600">
                          متاح في: <span className="font-semibold">{new Date(equipment.availableDate).toLocaleDateString('ar-SA')}</span>
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quality Grade Predictions */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              توقعات جودة المحصول
              <span className="text-sm font-normal text-gray-500 mr-2">Quality Grade Predictions</span>
            </h2>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="space-y-4">
                {harvestPlan.fields
                  .sort((a, b) => b.qualityScore - a.qualityScore)
                  .map((field) => (
                    <div
                      key={field.fieldId}
                      className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                      data-testid={`quality-${field.fieldId}`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-gray-900">{field.fieldNameAr}</h4>
                          <p className="text-sm text-gray-600">{field.cropTypeAr}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getQualityColor(field.qualityGrade)}`}>
                          {field.qualityGradeAr}
                        </span>
                      </div>

                      {/* Quality Score Progress */}
                      <div className="mb-3">
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">درجة الجودة</span>
                          <span className="font-semibold">{field.qualityScore}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 rounded-full h-2 transition-all"
                            style={{ width: `${field.qualityScore}%` }}
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs text-gray-600">الإنتاجية</p>
                          <p className="font-semibold text-sm">{field.yieldPerHectare} كجم/هكتار</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600">الرطوبة</p>
                          <p className="font-semibold text-sm">{field.moistureContent}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>

        {/* Harvest Priority Ranking */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            ترتيب أولوية الحصاد
            <span className="text-sm font-normal text-gray-500 mr-2">Harvest Priority Ranking</span>
          </h2>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="priority-table">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      الأولوية
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      الحقل
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      المحصول
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      الحالة
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      النضج
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      الأيام المتبقية
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                      المحصول المتوقع
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {harvestPlan.fields
                    .sort((a, b) => b.priority - a.priority)
                    .map((field, index) => (
                      <tr
                        key={field.fieldId}
                        className="hover:bg-gray-50 transition-colors"
                        data-testid={`priority-row-${field.fieldId}`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-800 font-bold text-sm">
                            {index + 1}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-semibold text-gray-900">{field.fieldNameAr}</div>
                          <div className="text-sm text-gray-500">{field.area} هكتار</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {field.cropTypeAr}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                            field.status === 'ready' ? 'bg-green-100 text-green-800' :
                            field.status === 'almost_ready' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {field.statusAr}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 w-16 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-green-600 rounded-full h-2"
                                style={{ width: `${field.maturityLevel}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-900 w-12">
                              {field.maturityLevel}%
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-semibold text-gray-900">
                            {field.daysToOptimal === 0 ? (
                              <span className="text-green-600">الآن</span>
                            ) : (
                              `${field.daysToOptimal} يوم`
                            )}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-semibold text-gray-900">
                            {(field.predictedYield / 1000).toFixed(1)} طن
                          </div>
                          <div className="text-sm text-gray-500">
                            {field.yieldPerHectare} كجم/هكتار
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Summary Statistics */}
        <div className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-xl border border-green-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">ملخص خطة الحصاد</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">الحقول الجاهزة</p>
              <p className="text-3xl font-bold text-green-600">{readyFields.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">الحقول شبه الجاهزة</p>
              <p className="text-3xl font-bold text-yellow-600">{almostReadyFields.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">الحقول غير الجاهزة</p>
              <p className="text-3xl font-bold text-gray-600">{notReadyFields.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">متوسط الجودة</p>
              <p className="text-3xl font-bold text-blue-600">
                {(harvestPlan.fields.reduce((sum, f) => sum + f.qualityScore, 0) / harvestPlan.fields.length).toFixed(0)}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HarvestPlanningDashboard;
