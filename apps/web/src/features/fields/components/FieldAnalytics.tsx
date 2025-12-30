'use client';

/**
 * SAHOOL Field Analytics Component
 * مكون تحليلات الحقل
 *
 * Advanced field analytics inspired by Farmonaut and Climate FieldView
 * - NDVI (Normalized Difference Vegetation Index)
 * - NDWI (Normalized Difference Water Index)
 * - EVI (Enhanced Vegetation Index)
 * - SAVI (Soil Adjusted Vegetation Index)
 * - Time series analysis
 * - Health score trends
 * - Historical comparisons
 * - Alert thresholds
 * - Full Arabic/RTL support
 */

import React, { useState, useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  BarChart,
  Leaf,
  Droplets,
  AlertCircle,
  Check,
  Calendar,
  RefreshCw,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
// ==================== TYPES ====================

interface VegetationIndex {
  date: string;
  value: number;
}

interface FieldAnalyticsProps {
  fieldId: string;
  fieldName?: string;
  ndviHistory?: VegetationIndex[];
  currentNdvi?: number;
  currentNdwi?: number;
  currentEvi?: number;
}

interface IndexCardProps {
  title: string;
  titleAr: string;
  value: number;
  threshold: number;
  icon: React.ReactNode;
  color: string;
  description: string;
  descriptionAr: string;
}

interface TimeSeriesData {
  date: string;
  dateAr: string;
  ndvi: number;
  ndwi: number;
  evi: number;
  savi: number;
}

// ==================== CONSTANTS ====================

const THRESHOLDS = {
  ndvi: {
    excellent: 0.7,
    good: 0.5,
    moderate: 0.3,
    poor: 0,
  },
  ndwi: {
    excellent: 0.5,
    good: 0.3,
    moderate: 0.1,
    poor: -0.2,
  },
  evi: {
    excellent: 0.6,
    good: 0.4,
    moderate: 0.2,
    poor: 0,
  },
  savi: {
    excellent: 0.6,
    good: 0.4,
    moderate: 0.2,
    poor: 0,
  },
};

// ==================== MOCK DATA ====================

const generateMockData = (currentNdvi?: number): TimeSeriesData[] => {
  const data: TimeSeriesData[] = [];
  const today = new Date();

  for (let i = 30; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    // Generate realistic values with seasonal trends
    const seasonalFactor = Math.sin((i / 30) * Math.PI) * 0.15;
    const randomNoise = (Math.random() - 0.5) * 0.1;

    const baseNdvi = currentNdvi ?? 0.65;
    const ndvi = Math.max(0, Math.min(1, baseNdvi + seasonalFactor + randomNoise));
    const ndwi = Math.max(-1, Math.min(1, 0.3 + seasonalFactor * 0.5 + randomNoise * 0.8));
    const evi = Math.max(0, Math.min(1, ndvi * 0.9 + randomNoise * 0.05));
    const savi = Math.max(0, Math.min(1, ndvi * 0.85 + randomNoise * 0.05));

    data.push({
      date: date.toISOString().split('T')[0] ?? '',
      dateAr: date.toLocaleDateString('ar-EG', { month: 'short', day: 'numeric' }),
      ndvi: Number(ndvi.toFixed(3)),
      ndwi: Number(ndwi.toFixed(3)),
      evi: Number(evi.toFixed(3)),
      savi: Number(savi.toFixed(3)),
    });
  }

  return data;
};

// ==================== HELPER FUNCTIONS ====================

const getHealthStatus = (value: number, thresholds: typeof THRESHOLDS.ndvi) => {
  if (value >= thresholds.excellent) return { status: 'excellent', color: 'green', labelAr: 'ممتاز' };
  if (value >= thresholds.good) return { status: 'good', color: 'lime', labelAr: 'جيد' };
  if (value >= thresholds.moderate) return { status: 'moderate', color: 'yellow', labelAr: 'متوسط' };
  return { status: 'poor', color: 'red', labelAr: 'ضعيف' };
};

const calculateTrend = (data: VegetationIndex[]): { direction: 'up' | 'down' | 'stable'; percentage: number } => {
  if (data.length < 2) return { direction: 'stable', percentage: 0 };

  const recent = data.slice(-7);
  const older = data.slice(-14, -7);

  const recentAvg = recent.reduce((sum, d) => sum + d.value, 0) / recent.length;
  const olderAvg = older.reduce((sum, d) => sum + d.value, 0) / (older.length || 1);

  const change = ((recentAvg - olderAvg) / olderAvg) * 100;

  if (Math.abs(change) < 2) return { direction: 'stable', percentage: 0 };
  return {
    direction: change > 0 ? 'up' : 'down',
    percentage: Math.abs(change),
  };
};

const _formatDate = (dateStr: string, locale: 'ar' | 'en' = 'ar'): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString(locale === 'ar' ? 'ar-EG' : 'en-US', {
    month: 'short',
    day: 'numeric',
  });
};
void _formatDate; // Reserved for future locale-based date formatting

// ==================== COMPONENTS ====================

const IndexCard: React.FC<IndexCardProps> = ({
  title: _title,
  titleAr,
  value,
  threshold,
  icon,
  color,
  description: _description,
  descriptionAr,
}) => {
  void _title; void _description; // Reserved for future i18n support
  const healthStatus = getHealthStatus(value, THRESHOLDS.ndvi);
  const isHealthy = value >= threshold;

  return (
    <div
      className={`
        bg-white rounded-xl border-2 p-5 transition-all duration-200
        ${isHealthy ? 'border-green-200 hover:border-green-300' : 'border-red-200 hover:border-red-300'}
        hover:shadow-lg
      `}
      dir="rtl"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-gray-600 mb-1">{titleAr}</h3>
          <p className="text-3xl font-bold text-gray-900">{value.toFixed(3)}</p>
        </div>
        <div className={`p-3 rounded-lg bg-${color}-50`}>
          {icon}
        </div>
      </div>

      <div className="flex items-center gap-2 mb-2">
        {isHealthy ? (
          <Check className="w-4 h-4 text-green-600" />
        ) : (
          <AlertCircle className="w-4 h-4 text-red-600" />
        )}
        <span className={`text-sm font-medium ${isHealthy ? 'text-green-700' : 'text-red-700'}`}>
          {healthStatus.labelAr}
        </span>
      </div>

      <p className="text-xs text-gray-500">{descriptionAr}</p>

      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">الحد الأدنى</span>
          <span className="font-medium text-gray-700">{threshold.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

const TrendIndicator: React.FC<{ trend: ReturnType<typeof calculateTrend> }> = ({ trend }) => {
  if (trend.direction === 'stable') {
    return (
      <div className="flex items-center gap-2 text-gray-600">
        <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
          <div className="w-3 h-0.5 bg-gray-400" />
        </div>
        <span className="text-sm font-medium">مستقر</span>
      </div>
    );
  }

  const isPositive = trend.direction === 'up';

  return (
    <div className={`flex items-center gap-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${isPositive ? 'bg-green-50' : 'bg-red-50'}`}>
        {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
      </div>
      <span className="text-sm font-medium">
        {isPositive ? 'تحسن' : 'تراجع'} {trend.percentage.toFixed(1)}%
      </span>
    </div>
  );
};

// ==================== MAIN COMPONENT ====================

export const FieldAnalytics: React.FC<FieldAnalyticsProps> = ({
  fieldId: _fieldId,
  fieldName,
  ndviHistory,
  currentNdvi = 0.68,
  currentNdwi = 0.35,
  currentEvi = 0.62,
}) => {
  void _fieldId; // Reserved for API calls
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'season'>('month');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Generate or use provided data
  const timeSeriesData = useMemo(() => {
    return generateMockData(currentNdvi);
  }, [currentNdvi]);

  // Calculate SAVI from NDVI (simplified calculation)
  const currentSavi = currentNdvi * 0.85;

  // Convert NDVI history to VegetationIndex format
  const ndviData: VegetationIndex[] = useMemo(() => {
    if (ndviHistory) return ndviHistory;
    return timeSeriesData.map(d => ({ date: d.date, value: d.ndvi }));
  }, [ndviHistory, timeSeriesData]);

  // Calculate trends
  const ndviTrend = calculateTrend(ndviData);

  // Filter data based on selected period
  const filteredData = useMemo(() => {
    const days = selectedPeriod === 'week' ? 7 : selectedPeriod === 'month' ? 30 : 90;
    return timeSeriesData.slice(-days);
  }, [timeSeriesData, selectedPeriod]);

  // Handle refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsRefreshing(false);
  };

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload) return null;

    return (
      <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200" dir="rtl">
        <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4 text-xs">
            <span style={{ color: entry.color }}>{entry.name}</span>
            <span className="font-bold" style={{ color: entry.color }}>
              {entry.value.toFixed(3)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">تحليلات الحقل</h2>
          {fieldName && <p className="text-gray-600 mt-1">{fieldName}</p>}
        </div>

        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg
            bg-green-600 text-white font-medium
            hover:bg-green-700 active:bg-green-800
            transition-colors duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>تحديث</span>
        </button>
      </div>

      {/* Index Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndexCard
          title="NDVI"
          titleAr="مؤشر NDVI"
          value={currentNdvi}
          threshold={THRESHOLDS.ndvi.good}
          icon={<Leaf className="w-6 h-6 text-green-600" />}
          color="green"
          description="Vegetation Health Index"
          descriptionAr="مؤشر صحة الغطاء النباتي"
        />

        <IndexCard
          title="NDWI"
          titleAr="مؤشر NDWI"
          value={currentNdwi}
          threshold={THRESHOLDS.ndwi.good}
          icon={<Droplets className="w-6 h-6 text-blue-600" />}
          color="blue"
          description="Water Content Index"
          descriptionAr="مؤشر المحتوى المائي"
        />

        <IndexCard
          title="EVI"
          titleAr="مؤشر EVI"
          value={currentEvi}
          threshold={THRESHOLDS.evi.good}
          icon={<BarChart className="w-6 h-6 text-emerald-600" />}
          color="emerald"
          description="Enhanced Vegetation Index"
          descriptionAr="مؤشر الغطاء النباتي المحسن"
        />

        <IndexCard
          title="SAVI"
          titleAr="مؤشر SAVI"
          value={currentSavi}
          threshold={THRESHOLDS.savi.good}
          icon={<Leaf className="w-6 h-6 text-lime-600" />}
          color="lime"
          description="Soil Adjusted Vegetation Index"
          descriptionAr="مؤشر الغطاء النباتي المعدل للتربة"
        />
      </div>

      {/* Trend Analysis */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-bold text-gray-900">اتجاه صحة الحقل</h3>
          </div>
          <TrendIndicator trend={ndviTrend} />
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <button
            onClick={() => setSelectedPeriod('week')}
            className={`
              px-4 py-2 rounded-lg font-medium transition-colors
              ${selectedPeriod === 'week'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            أسبوع
          </button>
          <button
            onClick={() => setSelectedPeriod('month')}
            className={`
              px-4 py-2 rounded-lg font-medium transition-colors
              ${selectedPeriod === 'month'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            شهر
          </button>
          <button
            onClick={() => setSelectedPeriod('season')}
            className={`
              px-4 py-2 rounded-lg font-medium transition-colors
              ${selectedPeriod === 'season'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            موسم
          </button>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="colorNdvi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="dateAr"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              stroke="#9ca3af"
            />
            <YAxis
              domain={[0, 1]}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              stroke="#9ca3af"
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={THRESHOLDS.ndvi.good}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              label={{ value: 'الحد الأدنى', position: 'insideTopRight', fill: '#f59e0b' }}
            />
            <ReferenceLine
              y={THRESHOLDS.ndvi.excellent}
              stroke="#10b981"
              strokeDasharray="5 5"
              label={{ value: 'ممتاز', position: 'insideTopRight', fill: '#10b981' }}
            />
            <Area
              type="monotone"
              dataKey="ndvi"
              stroke="#10b981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorNdvi)"
              name="NDVI"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Multi-Index Comparison */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <BarChart className="w-6 h-6 text-green-600" />
          <h3 className="text-lg font-bold text-gray-900">مقارنة المؤشرات</h3>
        </div>

        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="dateAr"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              stroke="#9ca3af"
            />
            <YAxis
              domain={[-0.2, 1]}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              stroke="#9ca3af"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '14px', paddingTop: '20px' }}
              iconType="line"
            />
            <Line
              type="monotone"
              dataKey="ndvi"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              name="NDVI"
            />
            <Line
              type="monotone"
              dataKey="ndwi"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              name="NDWI"
            />
            <Line
              type="monotone"
              dataKey="evi"
              stroke="#059669"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              name="EVI"
            />
            <Line
              type="monotone"
              dataKey="savi"
              stroke="#84cc16"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              name="SAVI"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Health Alerts */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="w-6 h-6 text-amber-600" />
          <h3 className="text-lg font-bold text-gray-900">التنبيهات والملاحظات</h3>
        </div>

        <div className="space-y-3">
          {currentNdvi < THRESHOLDS.ndvi.good && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">مؤشر NDVI منخفض</p>
                <p className="text-sm text-red-700 mt-1">
                  صحة النبات أقل من المعدل الطبيعي. يُنصح بفحص الري والتسميد.
                </p>
              </div>
            </div>
          )}

          {currentNdwi < THRESHOLDS.ndwi.moderate && (
            <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-amber-900">محتوى مائي منخفض</p>
                <p className="text-sm text-amber-700 mt-1">
                  يُنصح بزيادة معدل الري للحفاظ على المحتوى المائي الأمثل.
                </p>
              </div>
            </div>
          )}

          {currentNdvi >= THRESHOLDS.ndvi.excellent && currentEvi >= THRESHOLDS.evi.excellent && (
            <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">صحة ممتازة</p>
                <p className="text-sm text-green-700 mt-1">
                  جميع المؤشرات في المعدل الممتاز. استمر على نفس نظام الإدارة.
                </p>
              </div>
            </div>
          )}

          {ndviTrend.direction === 'down' && ndviTrend.percentage > 5 && (
            <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <TrendingDown className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-amber-900">اتجاه تنازلي</p>
                <p className="text-sm text-amber-700 mt-1">
                  انخفاض في صحة النبات بنسبة {ndviTrend.percentage.toFixed(1)}% خلال الأسبوع الماضي.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border-2 border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-700">متوسط NDVI</span>
            <Calendar className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-900">
            {(filteredData.reduce((sum, d) => sum + d.ndvi, 0) / filteredData.length).toFixed(3)}
          </p>
          <p className="text-xs text-green-600 mt-1">آخر {selectedPeriod === 'week' ? '7' : selectedPeriod === 'month' ? '30' : '90'} يوم</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-700">متوسط NDWI</span>
            <Droplets className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-900">
            {(filteredData.reduce((sum, d) => sum + d.ndwi, 0) / filteredData.length).toFixed(3)}
          </p>
          <p className="text-xs text-blue-600 mt-1">آخر {selectedPeriod === 'week' ? '7' : selectedPeriod === 'month' ? '30' : '90'} يوم</p>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-6 border-2 border-emerald-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-emerald-700">متوسط EVI</span>
            <Leaf className="w-5 h-5 text-emerald-600" />
          </div>
          <p className="text-3xl font-bold text-emerald-900">
            {(filteredData.reduce((sum, d) => sum + d.evi, 0) / filteredData.length).toFixed(3)}
          </p>
          <p className="text-xs text-emerald-600 mt-1">آخر {selectedPeriod === 'week' ? '7' : selectedPeriod === 'month' ? '30' : '90'} يوم</p>
        </div>
      </div>
    </div>
  );
};

export default FieldAnalytics;
