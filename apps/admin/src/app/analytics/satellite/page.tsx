'use client';

// Satellite Data Analytics
// تحليلات البيانات الفضائية

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import AlertBadge from '@/components/ui/AlertBadge';
import { fetchSatelliteData, fetchNDVITrends } from '@/lib/api/analytics';
import {
  Satellite,
  TrendingUp,
  AlertTriangle,
  MapPin,
  Calendar,
  Download,
  Eye,
  Activity
} from 'lucide-react';
import { formatDate } from '@/lib/utils';
import {
import { logger } from '../../../lib/logger';
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';

// Dynamic map import
const SatelliteMap = dynamic(() => import('@/components/maps/SatelliteMap'), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] bg-gray-100 animate-pulse rounded-xl flex items-center justify-center">
      <p className="text-gray-500">جاري تحميل الخريطة...</p>
    </div>
  ),
});

interface SatelliteData {
  summary: {
    totalFields: number;
    lastUpdate: string;
    coverage: number;
    dataUsage: number;
  };
  fields: Array<{
    id: string;
    farmId: string;
    farmName: string;
    fieldName: string;
    area: number;
    location: { lat: number; lng: number };
    ndvi: {
      current: number;
      average: number;
      trend: 'up' | 'down' | 'stable';
      change: number;
    };
    lastImageDate: string;
    alerts: Array<{
      type: 'anomaly' | 'stress' | 'disease' | 'pest';
      severity: 'low' | 'medium' | 'high' | 'critical';
      message: string;
      messageAr: string;
      detectedAt: string;
    }>;
  }>;
  ndviTrends: Array<{
    date: string;
    ndvi: number;
    fieldId: string;
    fieldName: string;
  }>;
}

const CHART_COLORS = {
  primary: '#2E7D32',
  secondary: '#4CAF50',
  accent: '#81C784',
  warning: '#FF9800',
  danger: '#F44336',
  info: '#2196F3',
};

const getNDVIColor = (ndvi: number) => {
  if (ndvi >= 0.7) return 'text-green-600';
  if (ndvi >= 0.5) return 'text-lime-600';
  if (ndvi >= 0.3) return 'text-yellow-600';
  return 'text-red-600';
};

const getNDVILabel = (ndvi: number) => {
  if (ndvi >= 0.7) return 'ممتاز';
  if (ndvi >= 0.5) return 'جيد';
  if (ndvi >= 0.3) return 'متوسط';
  return 'ضعيف';
};

export default function SatellitePage() {
  const [data, setData] = useState<SatelliteData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<'week' | 'month' | 'season'>('month');

  useEffect(() => {
    loadData();
  }, [dateRange]);

  async function loadData() {
    setIsLoading(true);
    try {
      const satelliteData = await fetchSatelliteData({ range: dateRange });
      setData(satelliteData);
      if (satelliteData.fields.length > 0 && !selectedField) {
        setSelectedField(satelliteData.fields[0].id);
      }
    } catch (error) {
      logger.error('Failed to load satellite data:', error);
    } finally {
      setIsLoading(false);
    }
  }

  if (isLoading || !data) {
    return (
      <div className="p-6">
        <Header
          title="تحليلات البيانات الفضائية"
          subtitle="Satellite Data Analytics - مراقبة صحة المحاصيل عبر الأقمار الصناعية"
        />
        <div className="mt-6 flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-sahool-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  const criticalAlerts = data.fields.reduce(
    (sum, field) => sum + field.alerts.filter(a => a.severity === 'critical').length,
    0
  );

  const avgNDVI =
    data.fields.reduce((sum, field) => sum + field.ndvi.current, 0) / data.fields.length;

  const selectedFieldData = data.fields.find(f => f.id === selectedField);
  const selectedFieldTrends = data.ndviTrends.filter(t => t.fieldId === selectedField);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        <Header
          title="تحليلات البيانات الفضائية"
          subtitle="Satellite Data Analytics - مراقبة صحة المحاصيل عبر الأقمار الصناعية"
        />
        <div className="flex items-center gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as 'week' | 'month' | 'season')}
            className="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="week">أسبوع</option>
            <option value="month">شهر</option>
            <option value="season">موسم</option>
          </select>
          <button className="px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm font-medium hover:bg-sahool-700 transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" />
            تصدير البيانات
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="إجمالي الحقول"
          value={data.summary.totalFields}
          icon={MapPin}
          iconColor="text-blue-600"
        />
        <StatCard
          title="التغطية"
          value={`${data.summary.coverage.toFixed(0)}%`}
          icon={Satellite}
          iconColor="text-green-600"
        />
        <StatCard
          title="متوسط NDVI"
          value={avgNDVI.toFixed(2)}
          icon={Activity}
          iconColor="text-purple-600"
        />
        <StatCard
          title="تنبيهات حرجة"
          value={criticalAlerts}
          icon={AlertTriangle}
          iconColor="text-red-600"
        />
      </div>

      {/* Satellite Map */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-bold text-gray-900">خريطة التغطية الفضائية</h2>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Calendar className="w-4 h-4" />
            <span>آخر تحديث: {formatDate(data.summary.lastUpdate)}</span>
          </div>
        </div>
        <div className="h-[500px]">
          <SatelliteMap
            fields={data.fields}
            selectedFieldId={selectedField}
            onFieldClick={(fieldId) => setSelectedField(fieldId)}
          />
        </div>
      </div>

      {/* NDVI Trends and Field Details */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* NDVI Trend Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">اتجاه NDVI</h3>
            {selectedFieldData && (
              <select
                value={selectedField || ''}
                onChange={(e) => setSelectedField(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
              >
                {data.fields.map(field => (
                  <option key={field.id} value={field.id}>
                    {field.farmName} - {field.fieldName}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={selectedFieldTrends}>
                <defs>
                  <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ar-YE', { month: 'short', day: 'numeric' })}
                />
                <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    direction: 'rtl',
                  }}
                  labelFormatter={(value) => formatDate(value)}
                />
                <Area
                  type="monotone"
                  dataKey="ndvi"
                  stroke={CHART_COLORS.primary}
                  fill="url(#ndviGradient)"
                  strokeWidth={2}
                  name="NDVI"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Selected Field Details */}
        {selectedFieldData && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="font-bold text-gray-900 mb-4">تفاصيل الحقل</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">المزرعة / الحقل</p>
                <p className="font-medium text-gray-900">{selectedFieldData.farmName}</p>
                <p className="text-sm text-gray-600">{selectedFieldData.fieldName}</p>
              </div>

              <div className="border-t border-gray-100 pt-4">
                <p className="text-sm text-gray-500 mb-2">NDVI الحالي</p>
                <div className="flex items-end gap-2 mb-1">
                  <span className={`text-3xl font-bold ${getNDVIColor(selectedFieldData.ndvi.current)}`}>
                    {selectedFieldData.ndvi.current.toFixed(2)}
                  </span>
                  <span className="text-sm text-gray-500 mb-1">
                    ({getNDVILabel(selectedFieldData.ndvi.current)})
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp className={`w-4 h-4 ${selectedFieldData.ndvi.trend === 'up' ? 'text-green-600' : selectedFieldData.ndvi.trend === 'down' ? 'text-red-600 rotate-180' : 'text-gray-400'}`} />
                  <span className={selectedFieldData.ndvi.trend === 'up' ? 'text-green-600' : selectedFieldData.ndvi.trend === 'down' ? 'text-red-600' : 'text-gray-600'}>
                    {selectedFieldData.ndvi.change >= 0 ? '+' : ''}{(selectedFieldData.ndvi.change * 100).toFixed(1)}%
                  </span>
                  <span className="text-gray-500">عن المتوسط</span>
                </div>
              </div>

              <div className="border-t border-gray-100 pt-4">
                <p className="text-sm text-gray-500 mb-1">المساحة</p>
                <p className="font-medium text-gray-900">{selectedFieldData.area.toFixed(1)} هكتار</p>
              </div>

              <div className="border-t border-gray-100 pt-4">
                <p className="text-sm text-gray-500 mb-1">آخر صورة</p>
                <p className="font-medium text-gray-900">{formatDate(selectedFieldData.lastImageDate)}</p>
              </div>

              {selectedFieldData.alerts.length > 0 && (
                <div className="border-t border-gray-100 pt-4">
                  <p className="text-sm font-medium text-gray-900 mb-2">التنبيهات</p>
                  <div className="space-y-2">
                    {selectedFieldData.alerts.map((alert, index) => (
                      <div
                        key={index}
                        className={`p-2 rounded-lg text-xs ${
                          alert.severity === 'critical'
                            ? 'bg-red-50 text-red-700'
                            : alert.severity === 'high'
                            ? 'bg-orange-50 text-orange-700'
                            : alert.severity === 'medium'
                            ? 'bg-yellow-50 text-yellow-700'
                            : 'bg-blue-50 text-blue-700'
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="font-medium">{alert.messageAr}</p>
                            <p className="text-xs opacity-75 mt-1">{formatDate(alert.detectedAt)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Fields List with NDVI */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h3 className="font-bold text-gray-900">جميع الحقول</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المزرعة / الحقل</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المساحة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">NDVI الحالي</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المتوسط</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الاتجاه</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التنبيهات</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">آخر صورة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">إجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.fields.map((field) => (
                <tr
                  key={field.id}
                  className={`hover:bg-gray-50 transition-colors ${selectedField === field.id ? 'bg-sahool-50' : ''}`}
                  onClick={() => setSelectedField(field.id)}
                >
                  <td className="px-6 py-4 cursor-pointer">
                    <div>
                      <p className="font-medium text-gray-900">{field.farmName}</p>
                      <p className="text-sm text-gray-500">{field.fieldName}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{field.area.toFixed(1)} هكتار</td>
                  <td className="px-6 py-4">
                    <span className={`text-sm font-bold ${getNDVIColor(field.ndvi.current)}`}>
                      {field.ndvi.current.toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{field.ndvi.average.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1">
                      <TrendingUp
                        className={`w-4 h-4 ${
                          field.ndvi.trend === 'up'
                            ? 'text-green-600'
                            : field.ndvi.trend === 'down'
                            ? 'text-red-600 rotate-180'
                            : 'text-gray-400'
                        }`}
                      />
                      <span className={`text-sm ${field.ndvi.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {field.ndvi.change >= 0 ? '+' : ''}{(field.ndvi.change * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {field.alerts.length > 0 ? (
                      <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
                        {field.alerts.length}
                      </span>
                    ) : (
                      <span className="text-sm text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(field.lastImageDate)}</td>
                  <td className="px-6 py-4">
                    <button
                      className="p-1 text-sahool-600 hover:bg-sahool-50 rounded transition-colors"
                      title="عرض التفاصيل"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Usage Stats */}
      <div className="mt-6 bg-gradient-to-br from-sahool-600 to-sahool-700 p-6 rounded-xl shadow-sm text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold mb-2">استخدام البيانات الفضائية</h3>
            <p className="text-sm opacity-80">
              تم استخدام {data.summary.dataUsage.toFixed(1)} GB من بيانات الأقمار الصناعية هذا الشهر
            </p>
          </div>
          <Satellite className="w-12 h-12 opacity-20" />
        </div>
        <div className="mt-4 h-2 bg-white/20 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full"
            style={{ width: `${Math.min((data.summary.dataUsage / 100) * 100, 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
