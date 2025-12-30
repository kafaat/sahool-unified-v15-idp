'use client';

/**
 * Disease Risk Forecast Component
 * مكون توقعات مخاطر الأمراض
 *
 * Provides 7-14 day disease outbreak probability forecasts based on weather conditions,
 * similar to John Deere and Farmonaut disease prediction systems.
 */

import React, { useState, useMemo } from 'react';
import {
  AlertCircle,
  Calendar,
  Cloud,
  Droplets,
  Thermometer,
  TrendingUp,
  TrendingDown,
  Shield,
  Leaf,
  RefreshCw,
} from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

export interface WeatherFactors {
  temperature: number; // °C
  humidity: number; // %
  rainfall: number; // mm
  windSpeed?: number; // km/h
  cloudCover?: number; // %
}

export interface CropStage {
  id: string;
  name: string;
  nameAr: string;
  vulnerabilityMultiplier: number; // 0.5 - 2.0
}

export type RiskLevel = 'low' | 'moderate' | 'high' | 'critical';

export interface DiseaseRisk {
  disease: {
    id: string;
    name: string;
    nameAr: string;
    type: string;
    typeAr: string;
  };
  probability: number; // 0-100%
  riskLevel: RiskLevel;
  contributingFactors: {
    temperature: number; // impact score 0-100
    humidity: number; // impact score 0-100
    rainfall: number; // impact score 0-100
  };
}

export interface RiskForecast {
  date: string;
  dayNumber: number;
  weather: WeatherFactors;
  overallRiskLevel: RiskLevel;
  riskScore: number; // 0-100
  diseases: DiseaseRisk[];
  recommendations: {
    action: string;
    actionAr: string;
    priority: 'low' | 'medium' | 'high';
  }[];
}

export interface DiseaseRiskForecastProps {
  fieldId?: string;
  cropType?: string;
  cropTypeAr?: string;
  cropStage?: CropStage;
  forecastDays?: 7 | 14;
  lat?: number;
  lon?: number;
  onRefresh?: () => void;
  isLoading?: boolean;
  error?: string | null;
}

// ============================================================================
// Risk Calculation Utilities
// ============================================================================

const calculateDiseaseRisk = (
  weather: WeatherFactors,
  cropStage: CropStage
): DiseaseRisk[] => {
  const { temperature, humidity, rainfall } = weather;

  // Late Blight (Phytophthora infestans) - High risk: 15-25°C, 90%+ humidity, rainfall
  const lateBlightTemp = temperature >= 15 && temperature <= 25 ? 100 : Math.max(0, 100 - Math.abs(temperature - 20) * 5);
  const lateBlightHumidity = humidity >= 90 ? 100 : humidity * 1.1;
  const lateBlightRain = rainfall > 5 ? 100 : rainfall * 15;
  const lateBlightProb = Math.min(100, ((lateBlightTemp + lateBlightHumidity + lateBlightRain) / 3) * cropStage.vulnerabilityMultiplier);

  // Powdery Mildew - High risk: 20-30°C, 50-70% humidity, low rainfall
  const powderyMildewTemp = temperature >= 20 && temperature <= 30 ? 100 : Math.max(0, 100 - Math.abs(temperature - 25) * 4);
  const powderyMildewHumidity = humidity >= 50 && humidity <= 70 ? 100 : Math.max(0, 100 - Math.abs(humidity - 60) * 2);
  const powderyMildewRain = rainfall < 2 ? 80 : Math.max(0, 80 - rainfall * 10);
  const powderyMildewProb = Math.min(100, ((powderyMildewTemp + powderyMildewHumidity + powderyMildewRain) / 3) * cropStage.vulnerabilityMultiplier);

  // Downy Mildew - High risk: 15-22°C, 80%+ humidity, moderate rainfall
  const downyMildewTemp = temperature >= 15 && temperature <= 22 ? 100 : Math.max(0, 100 - Math.abs(temperature - 18) * 5);
  const downyMildewHumidity = humidity >= 80 ? 100 : humidity * 1.2;
  const downyMildewRain = rainfall >= 2 && rainfall <= 8 ? 90 : Math.max(0, 90 - Math.abs(rainfall - 5) * 10);
  const downyMildewProb = Math.min(100, ((downyMildewTemp + downyMildewHumidity + downyMildewRain) / 3) * cropStage.vulnerabilityMultiplier);

  // Anthracnose - High risk: 22-28°C, 90%+ humidity, high rainfall
  const anthracnoseTemp = temperature >= 22 && temperature <= 28 ? 100 : Math.max(0, 100 - Math.abs(temperature - 25) * 4);
  const anthracnoseHumidity = humidity >= 90 ? 100 : humidity * 1.1;
  const anthracnoseRain = rainfall > 8 ? 100 : rainfall * 10;
  const anthracnoseProb = Math.min(100, ((anthracnoseTemp + anthracnoseHumidity + anthracnoseRain) / 3) * cropStage.vulnerabilityMultiplier);

  const getRiskLevel = (prob: number): RiskLevel => {
    if (prob >= 75) return 'critical';
    if (prob >= 50) return 'high';
    if (prob >= 25) return 'moderate';
    return 'low';
  };

  return [
    {
      disease: {
        id: 'late-blight',
        name: 'Late Blight',
        nameAr: 'اللفحة المتأخرة',
        type: 'Fungal',
        typeAr: 'فطري',
      },
      probability: Math.round(lateBlightProb),
      riskLevel: getRiskLevel(lateBlightProb),
      contributingFactors: {
        temperature: Math.round(lateBlightTemp),
        humidity: Math.round(lateBlightHumidity),
        rainfall: Math.round(lateBlightRain),
      },
    },
    {
      disease: {
        id: 'powdery-mildew',
        name: 'Powdery Mildew',
        nameAr: 'البياض الدقيقي',
        type: 'Fungal',
        typeAr: 'فطري',
      },
      probability: Math.round(powderyMildewProb),
      riskLevel: getRiskLevel(powderyMildewProb),
      contributingFactors: {
        temperature: Math.round(powderyMildewTemp),
        humidity: Math.round(powderyMildewHumidity),
        rainfall: Math.round(powderyMildewRain),
      },
    },
    {
      disease: {
        id: 'downy-mildew',
        name: 'Downy Mildew',
        nameAr: 'البياض الزغبي',
        type: 'Fungal',
        typeAr: 'فطري',
      },
      probability: Math.round(downyMildewProb),
      riskLevel: getRiskLevel(downyMildewProb),
      contributingFactors: {
        temperature: Math.round(downyMildewTemp),
        humidity: Math.round(downyMildewHumidity),
        rainfall: Math.round(downyMildewRain),
      },
    },
    {
      disease: {
        id: 'anthracnose',
        name: 'Anthracnose',
        nameAr: 'أنثراكنوز',
        type: 'Fungal',
        typeAr: 'فطري',
      },
      probability: Math.round(anthracnoseProb),
      riskLevel: getRiskLevel(anthracnoseProb),
      contributingFactors: {
        temperature: Math.round(anthracnoseTemp),
        humidity: Math.round(anthracnoseHumidity),
        rainfall: Math.round(anthracnoseRain),
      },
    },
  ].sort((a, b) => b.probability - a.probability);
};

const getRecommendations = (riskLevel: RiskLevel) => {
  const recommendations: { action: string; actionAr: string; priority: 'low' | 'medium' | 'high' }[] = [];

  if (riskLevel === 'critical') {
    recommendations.push(
      {
        action: 'Apply preventive fungicide immediately',
        actionAr: 'رش المبيدات الفطرية الوقائية فوراً',
        priority: 'high',
      },
      {
        action: 'Increase field monitoring to twice daily',
        actionAr: 'زيادة مراقبة الحقل إلى مرتين يومياً',
        priority: 'high',
      },
      {
        action: 'Improve drainage to prevent waterlogging',
        actionAr: 'تحسين الصرف لمنع تراكم المياه',
        priority: 'high',
      }
    );
  } else if (riskLevel === 'high') {
    recommendations.push(
      {
        action: 'Prepare fungicide application',
        actionAr: 'تجهيز رش المبيدات الفطرية',
        priority: 'high',
      },
      {
        action: 'Monitor for early disease symptoms',
        actionAr: 'مراقبة ظهور أعراض الأمراض المبكرة',
        priority: 'medium',
      },
      {
        action: 'Ensure proper air circulation',
        actionAr: 'ضمان التهوية الجيدة',
        priority: 'medium',
      }
    );
  } else if (riskLevel === 'moderate') {
    recommendations.push(
      {
        action: 'Regular field inspections',
        actionAr: 'الفحص المنتظم للحقل',
        priority: 'medium',
      },
      {
        action: 'Maintain optimal irrigation schedule',
        actionAr: 'الحفاظ على جدول الري المثالي',
        priority: 'medium',
      },
      {
        action: 'Monitor weather forecasts',
        actionAr: 'متابعة توقعات الطقس',
        priority: 'low',
      }
    );
  } else {
    recommendations.push(
      {
        action: 'Continue routine monitoring',
        actionAr: 'الاستمرار في المراقبة الروتينية',
        priority: 'low',
      },
      {
        action: 'Maintain good agricultural practices',
        actionAr: 'الحفاظ على الممارسات الزراعية الجيدة',
        priority: 'low',
      }
    );
  }

  return recommendations;
};

// ============================================================================
// Mock Data Generator
// ============================================================================

const generateMockForecast = (days: number, cropStage: CropStage): RiskForecast[] => {
  const forecast: RiskForecast[] = [];
  const today = new Date();

  for (let i = 0; i < days; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() + i);

    // Generate realistic weather variations
    const baseTemp = 25 + Math.sin(i * 0.5) * 5;
    const baseHumidity = 70 + Math.sin(i * 0.3) * 15;
    const baseRainfall = Math.max(0, Math.sin(i * 0.7) * 8 + Math.random() * 3);

    const weather: WeatherFactors = {
      temperature: Math.round(baseTemp * 10) / 10,
      humidity: Math.round(baseHumidity),
      rainfall: Math.round(baseRainfall * 10) / 10,
      windSpeed: Math.round((10 + Math.random() * 10) * 10) / 10,
      cloudCover: Math.round(40 + Math.random() * 40),
    };

    const diseases = calculateDiseaseRisk(weather, cropStage);
    const topDiseases = diseases.slice(0, 3);

    // Calculate overall risk score
    const riskScore = Math.round(
      topDiseases.reduce((sum, d) => sum + d.probability, 0) / topDiseases.length
    );

    const overallRiskLevel: RiskLevel =
      riskScore >= 75 ? 'critical' :
      riskScore >= 50 ? 'high' :
      riskScore >= 25 ? 'moderate' : 'low';

    forecast.push({
      date: date.toISOString(),
      dayNumber: i + 1,
      weather,
      overallRiskLevel,
      riskScore,
      diseases,
      recommendations: getRecommendations(overallRiskLevel),
    });
  }

  return forecast;
};

// ============================================================================
// Default Crop Stages
// ============================================================================

const DEFAULT_CROP_STAGES: CropStage[] = [
  {
    id: 'seedling',
    name: 'Seedling',
    nameAr: 'الشتلة',
    vulnerabilityMultiplier: 1.5,
  },
  {
    id: 'vegetative',
    name: 'Vegetative Growth',
    nameAr: 'النمو الخضري',
    vulnerabilityMultiplier: 1.2,
  },
  {
    id: 'flowering',
    name: 'Flowering',
    nameAr: 'الإزهار',
    vulnerabilityMultiplier: 1.8,
  },
  {
    id: 'fruiting',
    name: 'Fruiting',
    nameAr: 'الإثمار',
    vulnerabilityMultiplier: 1.4,
  },
  {
    id: 'maturity',
    name: 'Maturity',
    nameAr: 'النضج',
    vulnerabilityMultiplier: 1.0,
  },
];

// ============================================================================
// Risk Level Configuration
// ============================================================================

const RISK_CONFIG = {
  low: {
    label: 'منخفض',
    labelEn: 'Low',
    color: 'text-green-700',
    bg: 'bg-green-50',
    border: 'border-green-300',
    bgDark: 'bg-green-500',
    icon: Shield,
    iconColor: 'text-green-600',
  },
  moderate: {
    label: 'متوسط',
    labelEn: 'Moderate',
    color: 'text-yellow-700',
    bg: 'bg-yellow-50',
    border: 'border-yellow-300',
    bgDark: 'bg-yellow-500',
    icon: AlertCircle,
    iconColor: 'text-yellow-600',
  },
  high: {
    label: 'عالي',
    labelEn: 'High',
    color: 'text-orange-700',
    bg: 'bg-orange-50',
    border: 'border-orange-300',
    bgDark: 'bg-orange-500',
    icon: TrendingUp,
    iconColor: 'text-orange-600',
  },
  critical: {
    label: 'حرج',
    labelEn: 'Critical',
    color: 'text-red-700',
    bg: 'bg-red-50',
    border: 'border-red-300',
    bgDark: 'bg-red-500',
    icon: AlertCircle,
    iconColor: 'text-red-600',
  },
};

// ============================================================================
// Main Component
// ============================================================================

export const DiseaseRiskForecast: React.FC<DiseaseRiskForecastProps> = ({
  fieldId: _fieldId, // Prefix with _ to indicate intentionally unused
  cropType = 'Tomato',
  cropTypeAr = 'طماطم',
  cropStage: providedCropStage,
  forecastDays = 7,
  lat: _lat, // Reserved for future weather API integration
  lon: _lon, // Reserved for future weather API integration
  onRefresh,
  isLoading: externalLoading = false,
  error: externalError = null,
}) => {
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [internalLoading, setInternalLoading] = useState(false);

  const isLoading = externalLoading || internalLoading;
  const error = externalError;

  // Use provided crop stage or default to flowering (guaranteed to be defined)
  const cropStage: CropStage = providedCropStage ?? DEFAULT_CROP_STAGES[2]!;

  // Generate forecast data
  const forecast = useMemo(() => {
    return generateMockForecast(forecastDays, cropStage);
  }, [forecastDays, cropStage]);

  const selectedForecast = selectedDay !== null ? forecast[selectedDay] : null;

  // Handle refresh
  const handleRefresh = async () => {
    setInternalLoading(true);
    if (onRefresh) {
      await onRefresh();
    }
    // Simulate API call
    setTimeout(() => {
      setInternalLoading(false);
    }, 1000);
  };

  // Calculate summary statistics
  const summary = useMemo(() => {
    const criticalDays = forecast.filter(f => f.overallRiskLevel === 'critical').length;
    const highDays = forecast.filter(f => f.overallRiskLevel === 'high').length;
    const avgRisk = Math.round(forecast.reduce((sum, f) => sum + f.riskScore, 0) / forecast.length);

    return { criticalDays, highDays, avgRisk };
  }, [forecast]);

  // ============================================================================
  // Render: Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="disease-risk-loading">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Leaf className="w-6 h-6 text-green-500 animate-pulse" />
            <h2 className="text-2xl font-bold text-gray-900">توقعات مخاطر الأمراض</h2>
          </div>
        </div>
        <div className="space-y-4">
          <div className="h-32 bg-gray-100 rounded-lg animate-pulse" />
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
          <div className="h-48 bg-gray-100 rounded-lg animate-pulse" />
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Error State
  // ============================================================================

  if (error) {
    return (
      <div className="bg-white rounded-xl border-2 border-red-200 p-6" data-testid="disease-risk-error">
        <div className="text-center py-8">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">خطأ في تحميل البيانات</h3>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          {onRefresh && (
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              إعادة المحاولة
            </button>
          )}
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Main Content
  // ============================================================================

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="disease-risk-forecast" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3">
            <Leaf className="w-6 h-6 text-green-500" />
            <h2 className="text-2xl font-bold text-gray-900">توقعات مخاطر الأمراض</h2>
          </div>
          <p className="text-sm text-gray-600 mt-1">Disease Risk Forecast ({forecastDays} Days)</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isLoading}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          data-testid="refresh-button"
          title="تحديث"
        >
          <RefreshCw className={`w-5 h-5 text-gray-600 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Crop Info */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">المحصول</p>
            <p className="text-lg font-semibold text-gray-900">
              {cropTypeAr} <span className="text-sm text-gray-600">({cropType})</span>
            </p>
          </div>
          <div className="text-left">
            <p className="text-sm text-gray-600">مرحلة النمو</p>
            <div className="flex items-center gap-2">
              <p className="text-lg font-semibold text-gray-900">{cropStage.nameAr}</p>
              <div
                className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium"
                title="Vulnerability Multiplier"
              >
                ×{cropStage.vulnerabilityMultiplier}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4 border-2 border-gray-200">
          <p className="text-sm text-gray-600 mb-1">متوسط المخاطر</p>
          <div className="flex items-center gap-2">
            <p className="text-2xl font-bold text-gray-900">{summary.avgRisk}%</p>
            {summary.avgRisk >= 50 ? (
              <TrendingUp className="w-5 h-5 text-red-500" />
            ) : (
              <TrendingDown className="w-5 h-5 text-green-500" />
            )}
          </div>
        </div>
        <div className="bg-orange-50 rounded-lg p-4 border-2 border-orange-200">
          <p className="text-sm text-orange-700 mb-1">أيام مخاطر عالية</p>
          <p className="text-2xl font-bold text-orange-700">{summary.highDays}</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
          <p className="text-sm text-red-700 mb-1">أيام حرجة</p>
          <p className="text-2xl font-bold text-red-700">{summary.criticalDays}</p>
        </div>
      </div>

      {/* Risk Timeline */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          الجدول الزمني للمخاطر
        </h3>
        <div className={`grid gap-2 ${forecastDays === 14 ? 'grid-cols-7' : 'grid-cols-7'}`}>
          {forecast.map((day, index) => {
            const config = RISK_CONFIG[day.overallRiskLevel];
            const Icon = config.icon;
            const isSelected = selectedDay === index;

            return (
              <button
                key={index}
                onClick={() => setSelectedDay(isSelected ? null : index)}
                className={`
                  p-3 rounded-lg border-2 transition-all
                  ${isSelected ? 'ring-4 ring-blue-200 scale-105' : ''}
                  ${config.bg} ${config.border}
                  hover:shadow-md
                `}
                data-testid={`timeline-day-${index}`}
              >
                <div className="text-center">
                  <p className="text-xs text-gray-600 mb-1">
                    {new Date(day.date).toLocaleDateString('ar-EG', { weekday: 'short' })}
                  </p>
                  <Icon className={`w-6 h-6 mx-auto mb-1 ${config.iconColor}`} />
                  <p className={`text-xs font-semibold ${config.color}`}>
                    {day.riskScore}%
                  </p>
                  <p className={`text-xs ${config.color} mt-1`}>
                    {config.label}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Day Details */}
      {selectedForecast && (
        <div className="mb-6 bg-gray-50 rounded-lg p-5 border-2 border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              تفاصيل اليوم {selectedForecast.dayNumber}
            </h3>
            <p className="text-sm text-gray-600">
              {new Date(selectedForecast.date).toLocaleDateString('ar-EG', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>

          {/* Weather Conditions */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <Thermometer className="w-4 h-4 text-red-500" />
                <p className="text-xs text-gray-600">درجة الحرارة</p>
              </div>
              <p className="text-lg font-bold text-gray-900">{selectedForecast.weather.temperature}°C</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <Droplets className="w-4 h-4 text-blue-500" />
                <p className="text-xs text-gray-600">الرطوبة</p>
              </div>
              <p className="text-lg font-bold text-gray-900">{selectedForecast.weather.humidity}%</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <Cloud className="w-4 h-4 text-gray-500" />
                <p className="text-xs text-gray-600">الأمطار</p>
              </div>
              <p className="text-lg font-bold text-gray-900">{selectedForecast.weather.rainfall} mm</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <Cloud className="w-4 h-4 text-gray-400" />
                <p className="text-xs text-gray-600">الغطاء السحابي</p>
              </div>
              <p className="text-lg font-bold text-gray-900">{selectedForecast.weather.cloudCover}%</p>
            </div>
          </div>

          {/* Top Disease Risks */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">أبرز الأمراض المتوقعة</h4>
            <div className="space-y-2">
              {selectedForecast.diseases.slice(0, 3).map((disease) => {
                const diseaseConfig = RISK_CONFIG[disease.riskLevel];
                return (
                  <div
                    key={disease.disease.id}
                    className={`p-3 rounded-lg border-2 ${diseaseConfig.bg} ${diseaseConfig.border}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-semibold text-gray-900">{disease.disease.nameAr}</p>
                        <p className="text-xs text-gray-600">{disease.disease.name}</p>
                      </div>
                      <div className="text-left">
                        <p className={`text-xl font-bold ${diseaseConfig.color}`}>
                          {disease.probability}%
                        </p>
                        <p className={`text-xs ${diseaseConfig.color}`}>{diseaseConfig.label}</p>
                      </div>
                    </div>

                    {/* Contributing Factors */}
                    <div className="grid grid-cols-3 gap-2 mt-2">
                      <div className="bg-white bg-opacity-50 rounded p-2">
                        <div className="flex items-center gap-1 mb-1">
                          <Thermometer className="w-3 h-3 text-red-500" />
                          <p className="text-xs text-gray-600">حرارة</p>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full bg-red-500"
                            style={{ width: `${disease.contributingFactors.temperature}%` }}
                          />
                        </div>
                      </div>
                      <div className="bg-white bg-opacity-50 rounded p-2">
                        <div className="flex items-center gap-1 mb-1">
                          <Droplets className="w-3 h-3 text-blue-500" />
                          <p className="text-xs text-gray-600">رطوبة</p>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full bg-blue-500"
                            style={{ width: `${disease.contributingFactors.humidity}%` }}
                          />
                        </div>
                      </div>
                      <div className="bg-white bg-opacity-50 rounded p-2">
                        <div className="flex items-center gap-1 mb-1">
                          <Cloud className="w-3 h-3 text-gray-500" />
                          <p className="text-xs text-gray-600">أمطار</p>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full bg-gray-500"
                            style={{ width: `${disease.contributingFactors.rainfall}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Shield className="w-4 h-4" />
              التوصيات الوقائية
            </h4>
            <div className="space-y-2">
              {selectedForecast.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border ${
                    rec.priority === 'high'
                      ? 'bg-red-50 border-red-200'
                      : rec.priority === 'medium'
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-green-50 border-green-200'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <div
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        rec.priority === 'high'
                          ? 'bg-red-200 text-red-800'
                          : rec.priority === 'medium'
                          ? 'bg-yellow-200 text-yellow-800'
                          : 'bg-green-200 text-green-800'
                      }`}
                    >
                      {rec.priority === 'high' ? 'عالي' : rec.priority === 'medium' ? 'متوسط' : 'منخفض'}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{rec.actionAr}</p>
                      <p className="text-xs text-gray-600 mt-0.5">{rec.action}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="pt-4 border-t-2 border-gray-100">
        <p className="text-xs text-gray-600 mb-2 text-center">مستويات المخاطر / Risk Levels</p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          {(Object.keys(RISK_CONFIG) as RiskLevel[]).map((level) => {
            const config = RISK_CONFIG[level];
            const Icon = config.icon;
            return (
              <div key={level} className="flex items-center gap-1.5">
                <Icon className={`w-4 h-4 ${config.iconColor}`} />
                <span className="text-xs text-gray-700">
                  {config.label} ({config.labelEn})
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer Note */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-center">
        <p className="text-xs text-gray-500">
          💡 التوقعات مبنية على نماذج الطقس وخصائص الأمراض. يُنصح بمراقبة الحقل بانتظام.
        </p>
        <p className="text-xs text-gray-400 mt-1" dir="ltr">
          Forecasts based on weather models and disease characteristics. Regular field monitoring recommended.
        </p>
      </div>
    </div>
  );
};

export default DiseaseRiskForecast;
