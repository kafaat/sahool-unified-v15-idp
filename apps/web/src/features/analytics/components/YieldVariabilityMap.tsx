/**
 * Yield Variability Map Component
 * خريطة تباين المحصول
 *
 * Advanced spatial yield variability analysis similar to Climate FieldView and Farmonaut.
 * Provides field zone segmentation, yield heatmaps, management zone recommendations,
 * and variable rate application suggestions.
 */

'use client';

import React, { useState } from 'react';
import {
  Map,
  MapPin,
  TrendingUp,
  TrendingDown,
  Minus,
  Droplets,
  Leaf,
  ChevronRight,
  BarChart3,
  Layers,
  Zap,
  AlertCircle,
  Check,
  Info,
  RefreshCw,
  Download,
  Filter,
} from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

/**
 * Yield zone classification
 * تصنيف منطقة المحصول
 */
export type YieldZoneType = 'high' | 'medium' | 'low' | 'very_low';

/**
 * Soil type classification
 * تصنيف نوع التربة
 */
export type SoilType = 'clay' | 'loam' | 'sand' | 'silt' | 'clay_loam';

/**
 * Management zone recommendation type
 * نوع توصية منطقة الإدارة
 */
export type RecommendationType = 'fertilizer' | 'irrigation' | 'soil_amendment' | 'seed_density';

/**
 * Individual yield zone within a field
 * منطقة محصول فردية داخل الحقل
 */
export interface YieldZone {
  id: string;
  zoneType: YieldZoneType;
  zoneTypeAr: string;
  area: number; // hectares
  averageYield: number; // kg/ha
  soilType: SoilType;
  soilTypeAr: string;
  soilPH: number;
  organicMatter: number; // percentage
  nitrogenLevel: number; // kg/ha
  phosphorusLevel: number; // kg/ha
  potassiumLevel: number; // kg/ha
  moistureRetention: number; // percentage
  gridCells: number[]; // Grid cell indices for visualization
  color: string;
}

/**
 * Variable rate application recommendation
 * توصية التطبيق بمعدل متغير
 */
export interface VariableRateRecommendation {
  id: string;
  zoneId: string;
  type: RecommendationType;
  typeAr: string;
  product: string;
  productAr: string;
  currentRate: number;
  recommendedRate: number;
  unit: string;
  unitAr: string;
  expectedYieldIncrease: number; // percentage
  costPerHectare: number;
  potentialRevenue: number;
  roi: number; // percentage
  priority: 'high' | 'medium' | 'low';
  priorityAr: string;
  reason: string;
  reasonAr: string;
}

/**
 * Soil-yield correlation data
 * بيانات الارتباط بين التربة والمحصول
 */
export interface SoilYieldCorrelation {
  factor: string;
  factorAr: string;
  correlation: number; // -1 to 1
  impact: 'positive' | 'negative' | 'neutral';
  impactAr: string;
  description: string;
  descriptionAr: string;
}

/**
 * Complete field yield variability analysis
 * تحليل تباين المحصول الكامل للحقل
 */
export interface FieldYieldVariability {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  totalArea: number;
  season: string;
  zones: YieldZone[];
  recommendations: VariableRateRecommendation[];
  correlations: SoilYieldCorrelation[];
  statistics: {
    averageYield: number;
    maxYield: number;
    minYield: number;
    yieldVariability: number; // coefficient of variation
    potentialYieldIncrease: number; // kg
    estimatedAdditionalRevenue: number;
  };
  gridSize: number; // e.g., 10 for 10x10 grid
  lastUpdated: string;
}

// ============================================================================
// Mock Data for Demo/Testing
// ============================================================================

const mockFieldData: FieldYieldVariability[] = [
  {
    fieldId: 'field1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    totalArea: 45,
    season: '2025/2026',
    gridSize: 10,
    zones: [
      {
        id: 'zone1',
        zoneType: 'high',
        zoneTypeAr: 'عالي الإنتاجية',
        area: 12.5,
        averageYield: 520,
        soilType: 'loam',
        soilTypeAr: 'طمي',
        soilPH: 6.8,
        organicMatter: 3.5,
        nitrogenLevel: 180,
        phosphorusLevel: 45,
        potassiumLevel: 220,
        moistureRetention: 75,
        gridCells: [0, 1, 2, 10, 11, 12, 20, 21, 22, 30, 31, 32],
        color: '#22c55e',
      },
      {
        id: 'zone2',
        zoneType: 'medium',
        zoneTypeAr: 'متوسط الإنتاجية',
        area: 18.5,
        averageYield: 380,
        soilType: 'clay_loam',
        soilTypeAr: 'طمي طيني',
        soilPH: 7.1,
        organicMatter: 2.8,
        nitrogenLevel: 140,
        phosphorusLevel: 35,
        potassiumLevel: 180,
        moistureRetention: 68,
        gridCells: [3, 4, 5, 13, 14, 15, 23, 24, 25, 33, 34, 35, 40, 41, 42, 50, 51, 52],
        color: '#eab308',
      },
      {
        id: 'zone3',
        zoneType: 'low',
        zoneTypeAr: 'منخفض الإنتاجية',
        area: 10.0,
        averageYield: 280,
        soilType: 'sand',
        soilTypeAr: 'رملي',
        soilPH: 7.5,
        organicMatter: 1.8,
        nitrogenLevel: 95,
        phosphorusLevel: 22,
        potassiumLevel: 135,
        moistureRetention: 45,
        gridCells: [6, 7, 16, 17, 26, 27, 36, 37, 43, 44, 53, 54],
        color: '#f97316',
      },
      {
        id: 'zone4',
        zoneType: 'very_low',
        zoneTypeAr: 'منخفض جداً',
        area: 4.0,
        averageYield: 190,
        soilType: 'sand',
        soilTypeAr: 'رملي',
        soilPH: 8.0,
        organicMatter: 1.2,
        nitrogenLevel: 65,
        phosphorusLevel: 15,
        potassiumLevel: 95,
        moistureRetention: 35,
        gridCells: [8, 9, 18, 19, 28, 29],
        color: '#ef4444',
      },
    ],
    recommendations: [
      {
        id: 'rec1',
        zoneId: 'zone3',
        type: 'fertilizer',
        typeAr: 'سماد',
        product: 'Nitrogen Fertilizer (NPK 20-10-10)',
        productAr: 'سماد نيتروجين (NPK 20-10-10)',
        currentRate: 120,
        recommendedRate: 180,
        unit: 'kg/ha',
        unitAr: 'كجم/هكتار',
        expectedYieldIncrease: 22,
        costPerHectare: 1200,
        potentialRevenue: 3500,
        roi: 192,
        priority: 'high',
        priorityAr: 'عالية',
        reason: 'Low nitrogen levels limiting yield potential',
        reasonAr: 'مستويات النيتروجين المنخفضة تحد من إمكانات المحصول',
      },
      {
        id: 'rec2',
        zoneId: 'zone4',
        type: 'soil_amendment',
        typeAr: 'تعديل التربة',
        product: 'Organic Compost',
        productAr: 'سماد عضوي',
        currentRate: 0,
        recommendedRate: 8000,
        unit: 'kg/ha',
        unitAr: 'كجم/هكتار',
        expectedYieldIncrease: 35,
        costPerHectare: 2500,
        potentialRevenue: 6800,
        roi: 172,
        priority: 'high',
        priorityAr: 'عالية',
        reason: 'Very low organic matter affecting soil structure',
        reasonAr: 'المادة العضوية المنخفضة جداً تؤثر على بنية التربة',
      },
      {
        id: 'rec3',
        zoneId: 'zone3',
        type: 'irrigation',
        typeAr: 'ري',
        product: 'Drip Irrigation System',
        productAr: 'نظام الري بالتنقيط',
        currentRate: 450,
        recommendedRate: 650,
        unit: 'mm/season',
        unitAr: 'مم/موسم',
        expectedYieldIncrease: 18,
        costPerHectare: 800,
        potentialRevenue: 2900,
        roi: 263,
        priority: 'medium',
        priorityAr: 'متوسطة',
        reason: 'Poor moisture retention in sandy soil',
        reasonAr: 'ضعف الاحتفاظ بالرطوبة في التربة الرملية',
      },
      {
        id: 'rec4',
        zoneId: 'zone2',
        type: 'fertilizer',
        typeAr: 'سماد',
        product: 'Phosphorus Fertilizer',
        productAr: 'سماد فوسفور',
        currentRate: 60,
        recommendedRate: 85,
        unit: 'kg/ha',
        unitAr: 'كجم/هكتار',
        expectedYieldIncrease: 12,
        costPerHectare: 600,
        potentialRevenue: 1800,
        roi: 200,
        priority: 'medium',
        priorityAr: 'متوسطة',
        reason: 'Moderate phosphorus deficiency detected',
        reasonAr: 'نقص فوسفور متوسط تم اكتشافه',
      },
      {
        id: 'rec5',
        zoneId: 'zone1',
        type: 'seed_density',
        typeAr: 'كثافة البذور',
        product: 'High-Yield Wheat Variety',
        productAr: 'صنف قمح عالي الإنتاج',
        currentRate: 180,
        recommendedRate: 220,
        unit: 'kg/ha',
        unitAr: 'كجم/هكتار',
        expectedYieldIncrease: 8,
        costPerHectare: 400,
        potentialRevenue: 1600,
        roi: 300,
        priority: 'low',
        priorityAr: 'منخفضة',
        reason: 'Optimal conditions allow for higher plant density',
        reasonAr: 'الظروف المثالية تسمح بكثافة نباتية أعلى',
      },
    ],
    correlations: [
      {
        factor: 'Organic Matter',
        factorAr: 'المادة العضوية',
        correlation: 0.85,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'Strong positive correlation with yield',
        descriptionAr: 'ارتباط إيجابي قوي مع المحصول',
      },
      {
        factor: 'Nitrogen Level',
        factorAr: 'مستوى النيتروجين',
        correlation: 0.78,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'High correlation - key limiting factor',
        descriptionAr: 'ارتباط عالي - عامل محدد رئيسي',
      },
      {
        factor: 'Moisture Retention',
        factorAr: 'الاحتفاظ بالرطوبة',
        correlation: 0.72,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'Significant impact on yield stability',
        descriptionAr: 'تأثير كبير على استقرار المحصول',
      },
      {
        factor: 'Soil pH',
        factorAr: 'حموضة التربة',
        correlation: -0.45,
        impact: 'negative',
        impactAr: 'سلبي',
        description: 'High pH reducing nutrient availability',
        descriptionAr: 'الحموضة العالية تقلل من توفر العناصر الغذائية',
      },
      {
        factor: 'Phosphorus Level',
        factorAr: 'مستوى الفوسفور',
        correlation: 0.65,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'Moderate correlation with root development',
        descriptionAr: 'ارتباط متوسط مع نمو الجذور',
      },
    ],
    statistics: {
      averageYield: 380,
      maxYield: 520,
      minYield: 190,
      yieldVariability: 28.5,
      potentialYieldIncrease: 4500,
      estimatedAdditionalRevenue: 22500,
    },
    lastUpdated: '2025-12-30T08:00:00Z',
  },
  {
    fieldId: 'field2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    totalArea: 35,
    season: '2025/2026',
    gridSize: 10,
    zones: [
      {
        id: 'zone5',
        zoneType: 'high',
        zoneTypeAr: 'عالي الإنتاجية',
        area: 10.0,
        averageYield: 420,
        soilType: 'clay_loam',
        soilTypeAr: 'طمي طيني',
        soilPH: 6.9,
        organicMatter: 3.2,
        nitrogenLevel: 165,
        phosphorusLevel: 42,
        potassiumLevel: 200,
        moistureRetention: 72,
        gridCells: [0, 1, 10, 11, 20, 21, 30, 31, 40, 41],
        color: '#22c55e',
      },
      {
        id: 'zone6',
        zoneType: 'medium',
        zoneTypeAr: 'متوسط الإنتاجية',
        area: 15.5,
        averageYield: 320,
        soilType: 'loam',
        soilTypeAr: 'طمي',
        soilPH: 7.0,
        organicMatter: 2.5,
        nitrogenLevel: 130,
        phosphorusLevel: 32,
        potassiumLevel: 170,
        moistureRetention: 65,
        gridCells: [2, 3, 4, 12, 13, 14, 22, 23, 24, 32, 33, 34, 42, 43, 44, 50, 51, 52],
        color: '#eab308',
      },
      {
        id: 'zone7',
        zoneType: 'low',
        zoneTypeAr: 'منخفض الإنتاجية',
        area: 9.5,
        averageYield: 240,
        soilType: 'silt',
        soilTypeAr: 'غريني',
        soilPH: 7.4,
        organicMatter: 2.0,
        nitrogenLevel: 100,
        phosphorusLevel: 25,
        potassiumLevel: 140,
        moistureRetention: 55,
        gridCells: [5, 6, 15, 16, 25, 26, 35, 36, 45, 46, 53, 54],
        color: '#f97316',
      },
    ],
    recommendations: [
      {
        id: 'rec6',
        zoneId: 'zone7',
        type: 'fertilizer',
        typeAr: 'سماد',
        product: 'Balanced NPK (15-15-15)',
        productAr: 'NPK متوازن (15-15-15)',
        currentRate: 100,
        recommendedRate: 150,
        unit: 'kg/ha',
        unitAr: 'كجم/هكتار',
        expectedYieldIncrease: 20,
        costPerHectare: 950,
        potentialRevenue: 2800,
        roi: 195,
        priority: 'high',
        priorityAr: 'عالية',
        reason: 'Multiple nutrient deficiencies detected',
        reasonAr: 'تم اكتشاف نقص في عدة عناصر غذائية',
      },
      {
        id: 'rec7',
        zoneId: 'zone6',
        type: 'irrigation',
        typeAr: 'ري',
        product: 'Optimized Irrigation Schedule',
        productAr: 'جدول ري محسّن',
        currentRate: 400,
        recommendedRate: 520,
        unit: 'mm/season',
        unitAr: 'مم/موسم',
        expectedYieldIncrease: 15,
        costPerHectare: 650,
        potentialRevenue: 2200,
        roi: 238,
        priority: 'medium',
        priorityAr: 'متوسطة',
        reason: 'Water stress during critical growth stages',
        reasonAr: 'إجهاد مائي خلال مراحل النمو الحرجة',
      },
    ],
    correlations: [
      {
        factor: 'Nitrogen Level',
        factorAr: 'مستوى النيتروجين',
        correlation: 0.82,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'Primary yield driver for barley',
        descriptionAr: 'المحرك الرئيسي للمحصول للشعير',
      },
      {
        factor: 'Moisture Retention',
        factorAr: 'الاحتفاظ بالرطوبة',
        correlation: 0.68,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'Critical for grain filling stage',
        descriptionAr: 'حاسم لمرحلة امتلاء الحبوب',
      },
      {
        factor: 'Organic Matter',
        factorAr: 'المادة العضوية',
        correlation: 0.75,
        impact: 'positive',
        impactAr: 'إيجابي',
        description: 'Improves soil structure and fertility',
        descriptionAr: 'يحسن بنية التربة والخصوبة',
      },
    ],
    statistics: {
      averageYield: 320,
      maxYield: 420,
      minYield: 240,
      yieldVariability: 24.2,
      potentialYieldIncrease: 3200,
      estimatedAdditionalRevenue: 16000,
    },
    lastUpdated: '2025-12-30T08:00:00Z',
  },
];

// ============================================================================
// Helper Functions
// ============================================================================

const _getZoneColor = (zoneType: YieldZoneType): string => {
  switch (zoneType) {
    case 'high':
      return '#22c55e';
    case 'medium':
      return '#eab308';
    case 'low':
      return '#f97316';
    case 'very_low':
      return '#ef4444';
  }
};
void _getZoneColor;

const getZoneIcon = (zoneType: YieldZoneType) => {
  switch (zoneType) {
    case 'high':
      return TrendingUp;
    case 'medium':
      return Minus;
    case 'low':
    case 'very_low':
      return TrendingDown;
  }
};

const getPriorityColor = (priority: 'high' | 'medium' | 'low'): string => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-blue-100 text-blue-800 border-blue-200';
  }
};

const getCorrelationColor = (correlation: number): string => {
  const abs = Math.abs(correlation);
  if (abs >= 0.7) return 'text-green-700 bg-green-50';
  if (abs >= 0.5) return 'text-yellow-700 bg-yellow-50';
  return 'text-gray-700 bg-gray-50';
};

// ============================================================================
// Sub-Components
// ============================================================================

interface GridVisualizationProps {
  field: FieldYieldVariability;
  selectedZone: string | null;
  onZoneSelect: (zoneId: string) => void;
}

const GridVisualization: React.FC<GridVisualizationProps> = ({
  field,
  selectedZone,
  onZoneSelect,
}) => {
  const gridSize = field.gridSize;
  const totalCells = gridSize * gridSize;

  // Create a map of cell index to zone
  const cellZoneMap: Map<number, YieldZone> = new Map();
  field.zones.forEach((zone) => {
    zone.gridCells.forEach((cellIndex) => {
      cellZoneMap.set(cellIndex, zone);
    });
  });

  return (
    <div className="bg-gray-100 p-4 rounded-lg border-2 border-gray-300" data-testid="grid-visualization">
      <div
        className="grid gap-1"
        style={{
          gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))`,
        }}
      >
        {Array.from({ length: totalCells }).map((_, index) => {
          const zone = cellZoneMap.get(index);
          const isSelected = zone && selectedZone === zone.id;

          return (
            <button
              key={index}
              onClick={() => zone && onZoneSelect(zone.id)}
              className={`aspect-square rounded transition-all ${
                zone
                  ? `hover:opacity-80 ${isSelected ? 'ring-2 ring-blue-500 scale-110 z-10' : ''}`
                  : 'bg-gray-200'
              }`}
              style={{
                backgroundColor: zone ? zone.color : '#e5e7eb',
              }}
              data-testid={zone ? `grid-cell-${zone.id}` : `grid-cell-empty-${index}`}
              title={zone ? `${zone.zoneTypeAr} - ${zone.averageYield} كجم/هكتار` : 'غير مصنف'}
            />
          );
        })}
      </div>
    </div>
  );
};

// ============================================================================
// Main Component
// ============================================================================

export const YieldVariabilityMap: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error] = useState<string | null>(null);
  const [selectedFieldId, setSelectedFieldId] = useState<string>(mockFieldData[0]?.fieldId ?? '');
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [showCorrelations, setShowCorrelations] = useState(true);

  const selectedField = mockFieldData.find((f) => f.fieldId === selectedFieldId);

  // Simulate refresh action
  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 1500);
  };

  // Loading state
  if (isLoading && !selectedField) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="text-center" data-testid="loading-state">
          <RefreshCw className="w-12 h-12 animate-spin text-green-600 mx-auto" />
          <p className="mt-4 text-gray-600">جاري تحميل خريطة تباين المحصول...</p>
          <p className="text-sm text-gray-500">Loading yield variability map...</p>
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
          <h3 className="mt-4 text-lg font-semibold text-gray-900 text-center">حدث خطأ</h3>
          <p className="mt-2 text-sm text-gray-600 text-center">{error}</p>
          <button
            onClick={handleRefresh}
            className="mt-6 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            data-testid="error-retry-button"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!selectedField) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" dir="rtl">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 max-w-md text-center" data-testid="empty-state">
          <Map className="w-12 h-12 text-gray-400 mx-auto" />
          <h3 className="mt-4 text-lg font-semibold text-gray-900">لا توجد بيانات متاحة</h3>
          <p className="mt-2 text-sm text-gray-600">No yield variability data available</p>
        </div>
      </div>
    );
  }

  const selectedZoneData = selectedField.zones.find((z) => z.id === selectedZone);

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">خريطة تباين المحصول</h1>
              <p className="mt-1 text-sm text-gray-500">Yield Variability Map</p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                data-testid="refresh-button"
              >
                <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>تحديث</span>
              </button>

              <button
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                data-testid="download-button"
              >
                <Download className="w-5 h-5" />
                <span>تصدير التقرير</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Field Selector */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            اختر الحقل / Select Field
          </label>
          <select
            value={selectedFieldId}
            onChange={(e) => {
              setSelectedFieldId(e.target.value);
              setSelectedZone(null);
            }}
            className="w-full md:w-auto px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            data-testid="field-selector"
          >
            {mockFieldData.map((field) => (
              <option key={field.fieldId} value={field.fieldId}>
                {field.fieldNameAr} - {field.cropTypeAr} ({field.totalArea} هكتار)
              </option>
            ))}
          </select>
        </div>

        {/* Summary Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" data-testid="summary-cards">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">متوسط المحصول</p>
                <p className="text-2xl font-bold text-gray-900">
                  {selectedField.statistics.averageYield.toLocaleString('ar-SA')}
                </p>
                <p className="text-xs text-gray-500">كجم/هكتار</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">أعلى محصول</p>
                <p className="text-2xl font-bold text-green-600">
                  {selectedField.statistics.maxYield.toLocaleString('ar-SA')}
                </p>
                <p className="text-xs text-gray-500">كجم/هكتار</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-orange-100 rounded-lg">
                <TrendingDown className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">أدنى محصول</p>
                <p className="text-2xl font-bold text-orange-600">
                  {selectedField.statistics.minYield.toLocaleString('ar-SA')}
                </p>
                <p className="text-xs text-gray-500">كجم/هكتار</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Layers className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">معامل التباين</p>
                <p className="text-2xl font-bold text-purple-600">
                  {selectedField.statistics.yieldVariability.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500">CV</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Map Visualization & Zone Legend */}
          <div className="lg:col-span-2 space-y-6">
            {/* Grid Visualization */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  خريطة المناطق
                  <span className="text-sm font-normal text-gray-500 mr-2">Zone Map</span>
                </h2>
                <button className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                  <Filter className="w-4 h-4" />
                  <span>تصفية</span>
                </button>
              </div>

              <GridVisualization
                field={selectedField}
                selectedZone={selectedZone}
                onZoneSelect={setSelectedZone}
              />

              <p className="text-xs text-gray-500 mt-4 text-center">
                انقر على أي منطقة لعرض التفاصيل / Click any zone to view details
              </p>
            </div>

            {/* Zone Legend & Statistics */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                مناطق الإنتاجية
                <span className="text-sm font-normal text-gray-500 mr-2">Yield Zones</span>
              </h3>

              <div className="space-y-4" data-testid="zone-legend">
                {selectedField.zones.map((zone) => {
                  const ZoneIcon = getZoneIcon(zone.zoneType);
                  const isSelected = selectedZone === zone.id;

                  return (
                    <div
                      key={zone.id}
                      onClick={() => setSelectedZone(zone.id)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                      }`}
                      data-testid={`zone-legend-${zone.id}`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-6 h-6 rounded-full"
                            style={{ backgroundColor: zone.color }}
                          />
                          <div>
                            <h4 className="font-semibold text-gray-900">{zone.zoneTypeAr}</h4>
                            <p className="text-sm text-gray-600">{zone.soilTypeAr}</p>
                          </div>
                        </div>
                        <ZoneIcon className="w-5 h-5 text-gray-600" />
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <p className="text-xs text-gray-600">المساحة</p>
                          <p className="font-semibold text-sm">
                            {zone.area.toFixed(1)} هكتار
                          </p>
                          <p className="text-xs text-gray-500">
                            {((zone.area / selectedField.totalArea) * 100).toFixed(1)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600">الإنتاجية</p>
                          <p className="font-semibold text-sm">
                            {zone.averageYield.toLocaleString('ar-SA')}
                          </p>
                          <p className="text-xs text-gray-500">كجم/هكتار</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600">المحصول الكلي</p>
                          <p className="font-semibold text-sm">
                            {((zone.averageYield * zone.area) / 1000).toFixed(1)}
                          </p>
                          <p className="text-xs text-gray-500">طن</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Zone Details & Soil Data */}
          <div className="space-y-6">
            {/* Selected Zone Details */}
            {selectedZoneData ? (
              <div className="bg-white p-6 rounded-xl shadow-sm border-2 border-blue-500" data-testid="zone-details">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900">تفاصيل المنطقة</h3>
                  <button
                    onClick={() => setSelectedZone(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  <div
                    className="p-3 rounded-lg"
                    style={{ backgroundColor: `${selectedZoneData.color}20` }}
                  >
                    <h4 className="font-semibold text-lg text-gray-900">
                      {selectedZoneData.zoneTypeAr}
                    </h4>
                    <p className="text-sm text-gray-600">{selectedZoneData.soilTypeAr}</p>
                  </div>

                  {/* Soil Metrics */}
                  <div className="space-y-3">
                    <h5 className="font-semibold text-gray-900 flex items-center gap-2">
                      <Droplets className="w-4 h-4" />
                      خصائص التربة
                    </h5>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">حموضة التربة</p>
                        <p className="text-lg font-bold text-gray-900">
                          {selectedZoneData.soilPH.toFixed(1)}
                        </p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">المادة العضوية</p>
                        <p className="text-lg font-bold text-gray-900">
                          {selectedZoneData.organicMatter.toFixed(1)}%
                        </p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">نيتروجين</p>
                        <p className="text-lg font-bold text-gray-900">
                          {selectedZoneData.nitrogenLevel}
                        </p>
                        <p className="text-xs text-gray-500">كجم/هكتار</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">فوسفور</p>
                        <p className="text-lg font-bold text-gray-900">
                          {selectedZoneData.phosphorusLevel}
                        </p>
                        <p className="text-xs text-gray-500">كجم/هكتار</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">بوتاسيوم</p>
                        <p className="text-lg font-bold text-gray-900">
                          {selectedZoneData.potassiumLevel}
                        </p>
                        <p className="text-xs text-gray-500">كجم/هكتار</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">احتفاظ رطوبة</p>
                        <p className="text-lg font-bold text-gray-900">
                          {selectedZoneData.moistureRetention}%
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Zone-specific Recommendations */}
                  <div className="pt-4 border-t border-gray-200">
                    <h5 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-yellow-600" />
                      توصيات خاصة بالمنطقة
                    </h5>
                    {selectedField.recommendations
                      .filter((rec) => rec.zoneId === selectedZoneData.id)
                      .map((rec) => (
                        <div
                          key={rec.id}
                          className={`p-3 rounded-lg border mb-2 ${getPriorityColor(rec.priority)}`}
                        >
                          <p className="font-semibold text-sm">{rec.productAr}</p>
                          <p className="text-xs mt-1">{rec.reasonAr}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs font-semibold">
                              +{rec.expectedYieldIncrease}% زيادة متوقعة
                            </span>
                            <span className="text-xs">ROI: {rec.roi}%</span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center" data-testid="no-zone-selected">
                <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">انقر على منطقة لعرض التفاصيل</p>
                <p className="text-sm text-gray-500">Click a zone to view details</p>
              </div>
            )}

            {/* Potential Improvement Card */}
            <div className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-xl border border-green-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                الإمكانات التحسينية
              </h3>

              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">زيادة محصول محتملة</p>
                  <p className="text-3xl font-bold text-green-600">
                    {(selectedField.statistics.potentialYieldIncrease / 1000).toFixed(1)}
                  </p>
                  <p className="text-xs text-gray-500">طن إضافي</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">إيرادات إضافية متوقعة</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {selectedField.statistics.estimatedAdditionalRevenue.toLocaleString('ar-SA')}
                  </p>
                  <p className="text-xs text-gray-500">ريال سعودي</p>
                </div>

                <div className="pt-3 border-t border-green-200">
                  <p className="text-xs text-gray-600">
                    باستخدام التوصيات أدناه
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Variable Rate Application Recommendations */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              توصيات التطبيق بمعدل متغير
              <span className="text-sm font-normal text-gray-500 mr-2">
                Variable Rate Application Recommendations
              </span>
            </h2>
            <button
              onClick={() => setShowRecommendations(!showRecommendations)}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              data-testid="toggle-recommendations"
            >
              <ChevronRight
                className={`w-4 h-4 transition-transform ${showRecommendations ? 'rotate-90' : ''}`}
              />
              <span>{showRecommendations ? 'إخفاء' : 'عرض'}</span>
            </button>
          </div>

          {showRecommendations && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="recommendations-grid">
              {selectedField.recommendations
                .sort((a, b) => {
                  const priorityOrder = { high: 3, medium: 2, low: 1 };
                  return priorityOrder[b.priority] - priorityOrder[a.priority];
                })
                .map((rec) => {
                  const zone = selectedField.zones.find((z) => z.id === rec.zoneId);

                  return (
                    <div
                      key={rec.id}
                      className={`p-6 rounded-xl shadow-sm border-2 ${getPriorityColor(rec.priority)}`}
                      data-testid={`recommendation-${rec.id}`}
                    >
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Leaf className="w-5 h-5" />
                            <h3 className="font-bold text-gray-900">{rec.typeAr}</h3>
                          </div>
                          <p className="text-sm text-gray-700 font-semibold">{rec.productAr}</p>
                        </div>
                        <span className="px-2 py-1 bg-white bg-opacity-70 rounded text-xs font-bold">
                          {rec.priorityAr}
                        </span>
                      </div>

                      {/* Zone Info */}
                      {zone && (
                        <div className="mb-4 p-2 bg-white bg-opacity-50 rounded-lg flex items-center gap-2">
                          <div
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: zone.color }}
                          />
                          <span className="text-sm font-semibold">{zone.zoneTypeAr}</span>
                        </div>
                      )}

                      {/* Rates Comparison */}
                      <div className="mb-4 p-3 bg-white bg-opacity-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-600">المعدل الحالي</span>
                          <span className="font-semibold">
                            {rec.currentRate} {rec.unitAr}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">المعدل الموصى</span>
                          <span className="font-bold text-green-700">
                            {rec.recommendedRate} {rec.unitAr}
                          </span>
                        </div>
                      </div>

                      {/* Impact Metrics */}
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="p-3 bg-white bg-opacity-50 rounded-lg text-center">
                          <p className="text-xs text-gray-600 mb-1">زيادة المحصول</p>
                          <p className="text-xl font-bold text-green-700">
                            +{rec.expectedYieldIncrease}%
                          </p>
                        </div>
                        <div className="p-3 bg-white bg-opacity-50 rounded-lg text-center">
                          <p className="text-xs text-gray-600 mb-1">عائد الاستثمار</p>
                          <p className="text-xl font-bold text-blue-700">{rec.roi}%</p>
                        </div>
                      </div>

                      {/* Financial Info */}
                      <div className="pt-3 border-t border-current border-opacity-20 space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">التكلفة/هكتار:</span>
                          <span className="font-semibold">
                            {rec.costPerHectare.toLocaleString('ar-SA')} ر.س
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">الإيراد المحتمل:</span>
                          <span className="font-bold text-green-700">
                            {rec.potentialRevenue.toLocaleString('ar-SA')} ر.س
                          </span>
                        </div>
                      </div>

                      {/* Reason */}
                      <div className="mt-4 pt-3 border-t border-current border-opacity-20">
                        <p className="text-xs text-gray-700">
                          <Info className="w-3 h-3 inline ml-1" />
                          {rec.reasonAr}
                        </p>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </div>

        {/* Soil-Yield Correlation Analysis */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              تحليل الارتباط: التربة والمحصول
              <span className="text-sm font-normal text-gray-500 mr-2">
                Soil-Yield Correlation Analysis
              </span>
            </h2>
            <button
              onClick={() => setShowCorrelations(!showCorrelations)}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              data-testid="toggle-correlations"
            >
              <ChevronRight
                className={`w-4 h-4 transition-transform ${showCorrelations ? 'rotate-90' : ''}`}
              />
              <span>{showCorrelations ? 'إخفاء' : 'عرض'}</span>
            </button>
          </div>

          {showCorrelations && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="space-y-4" data-testid="correlations-list">
                {selectedField.correlations.map((correlation) => {
                  const absCorrelation = Math.abs(correlation.correlation);
                  const barWidth = absCorrelation * 100;

                  return (
                    <div
                      key={correlation.factor}
                      className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                      data-testid={`correlation-${correlation.factor}`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">{correlation.factorAr}</h4>
                          <p className="text-sm text-gray-600 mt-1">{correlation.descriptionAr}</p>
                        </div>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold ${getCorrelationColor(correlation.correlation)}`}
                        >
                          {correlation.correlation > 0 ? '+' : ''}
                          {correlation.correlation.toFixed(2)}
                        </span>
                      </div>

                      {/* Correlation Bar */}
                      <div className="relative">
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all ${
                              correlation.impact === 'positive'
                                ? 'bg-green-600'
                                : correlation.impact === 'negative'
                                ? 'bg-red-600'
                                : 'bg-gray-400'
                            }`}
                            style={{ width: `${barWidth}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>ضعيف</span>
                          <span>متوسط</span>
                          <span>قوي</span>
                        </div>
                      </div>

                      {/* Impact Badge */}
                      <div className="mt-3 flex items-center gap-2">
                        {correlation.impact === 'positive' && (
                          <>
                            <Check className="w-4 h-4 text-green-600" />
                            <span className="text-sm text-green-700 font-semibold">
                              {correlation.impactAr}
                            </span>
                          </>
                        )}
                        {correlation.impact === 'negative' && (
                          <>
                            <AlertCircle className="w-4 h-4 text-red-600" />
                            <span className="text-sm text-red-700 font-semibold">
                              {correlation.impactAr}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Correlation Summary */}
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Info className="w-5 h-5 text-blue-600" />
                  ملخص التحليل
                </h4>
                <p className="text-sm text-gray-700">
                  تُظهر البيانات أن{' '}
                  <strong>
                    {selectedField.correlations.find((c) => c.correlation === Math.max(...selectedField.correlations.map((x) => x.correlation)))?.factorAr}
                  </strong>{' '}
                  لديها أقوى ارتباط إيجابي مع إنتاجية المحصول. التركيز على تحسين هذا العامل سيحقق أكبر
                  تأثير على زيادة الإنتاجية.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Management Actions Summary */}
        <div className="mt-8 bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-8 rounded-xl border-2 border-green-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            ملخص إجراءات الإدارة الموصى بها
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white p-6 rounded-xl shadow-sm text-center">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <p className="text-sm text-gray-600 mb-1">توصيات عالية الأولوية</p>
              <p className="text-3xl font-bold text-red-600">
                {selectedField.recommendations.filter((r) => r.priority === 'high').length}
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <p className="text-sm text-gray-600 mb-1">زيادة إنتاج محتملة</p>
              <p className="text-3xl font-bold text-green-600">
                {selectedField.recommendations
                  .reduce((sum, r) => sum + r.expectedYieldIncrease, 0)
                  .toFixed(0)}
                %
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <p className="text-sm text-gray-600 mb-1">متوسط عائد الاستثمار</p>
              <p className="text-3xl font-bold text-blue-600">
                {(
                  selectedField.recommendations.reduce((sum, r) => sum + r.roi, 0) /
                  selectedField.recommendations.length
                ).toFixed(0)}
                %
              </p>
            </div>
          </div>

          <div className="bg-white bg-opacity-70 p-4 rounded-lg text-center">
            <p className="text-sm text-gray-700">
              تطبيق هذه التوصيات يمكن أن يزيد من إجمالي الإنتاج بمقدار{' '}
              <strong className="text-green-700">
                {(selectedField.statistics.potentialYieldIncrease / 1000).toFixed(1)} طن
              </strong>
              ، مما يحقق إيرادات إضافية تقدر بـ{' '}
              <strong className="text-blue-700">
                {selectedField.statistics.estimatedAdditionalRevenue.toLocaleString('ar-SA')} ريال
              </strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YieldVariabilityMap;
