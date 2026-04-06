'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Satellite,
  Leaf,
  Sun,
  Thermometer,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Eye,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { analyticsApi } from '@/features/analytics/api';
import type { AnalyticsFilters } from '@/features/analytics/types';
import { ApiError } from '@/lib/api/safe-fetch';

const statsCards = [
  {
    title: 'متوسط NDVI',
    value: '0.68',
    change: '+0.04',
    trend: 'up' as const,
    icon: Leaf,
    color: 'bg-green-500',
  },
  {
    title: 'تغطية القمر الصناعي',
    value: '94%',
    change: '+2%',
    trend: 'up' as const,
    icon: Satellite,
    color: 'bg-blue-500',
  },
  {
    title: 'مؤشر الحرارة السطحية',
    value: '32.4 C',
    change: '+1.2',
    trend: 'up' as const,
    icon: Thermometer,
    color: 'bg-orange-500',
  },
  {
    title: 'مؤشر الإشعاع الشمسي',
    value: '6.8 kWh/m2',
    change: '+0.3',
    trend: 'up' as const,
    icon: Sun,
    color: 'bg-yellow-500',
  },
];

const satelliteData = [
  { field: 'حقل القمح - شمال', lastCapture: '2026-04-02', ndvi: 0.74, lai: 3.2, evi: 0.42, cloudCover: '5%', healthStatus: 'صحي', source: 'Sentinel-2' },
  { field: 'حقل القمح - جنوب', lastCapture: '2026-04-02', ndvi: 0.68, lai: 2.8, evi: 0.38, cloudCover: '5%', healthStatus: 'صحي', source: 'Sentinel-2' },
  { field: 'حقل الشعير', lastCapture: '2026-04-01', ndvi: 0.65, lai: 2.5, evi: 0.35, cloudCover: '12%', healthStatus: 'معتدل', source: 'Sentinel-2' },
  { field: 'حقل الطماطم', lastCapture: '2026-04-02', ndvi: 0.78, lai: 3.8, evi: 0.48, cloudCover: '3%', healthStatus: 'صحي', source: 'Landsat-9' },
  { field: 'حقل النخيل', lastCapture: '2026-03-30', ndvi: 0.55, lai: 2.1, evi: 0.28, cloudCover: '18%', healthStatus: 'مجهد', source: 'Sentinel-2' },
  { field: 'حقل البرسيم', lastCapture: '2026-04-01', ndvi: 0.71, lai: 3.0, evi: 0.40, cloudCover: '8%', healthStatus: 'صحي', source: 'Sentinel-2' },
];

const healthColor: Record<string, string> = {
  'صحي': 'bg-green-100 text-green-800',
  'معتدل': 'bg-yellow-100 text-yellow-800',
  'مجهد': 'bg-orange-100 text-orange-800',
  'حرج': 'bg-red-100 text-red-800',
};

export default function SatelliteAnalyticsPage() {
  const [dateRange, setDateRange] = useState<AnalyticsPeriod>('month');
  const [indexType, setIndexType] = useState('ndvi');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiSatelliteData, setApiSatelliteData] = useState<typeof satelliteData | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await analyticsApi.getSummary({ period: dateRange });
      if (summary && Array.isArray((summary as any).satelliteFields)) {
        setApiSatelliteData((summary as any).satelliteFields);
      } else {
        setApiSatelliteData(null);
      }
    } catch (err) {
      const message = err instanceof ApiError ? err.messageAr : 'فشل في جلب بيانات الأقمار الصناعية';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const displayData = apiSatelliteData ?? satelliteData;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-500">جاري تحميل بيانات الأقمار الصناعية...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">خطأ في تحميل البيانات</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <button onClick={fetchData} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تحليلات الأقمار الصناعية</h1>
          <p className="text-gray-500 mt-1">تحليل صور الأقمار الصناعية ومؤشرات الغطاء النباتي لمراقبة صحة المحاصيل</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={indexType}
            onChange={(e) => setIndexType(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="ndvi">NDVI - مؤشر الغطاء النباتي</option>
            <option value="lai">LAI - مؤشر مساحة الورقة</option>
            <option value="evi">EVI - مؤشر الغطاء المحسّن</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="week">آخر أسبوع</option>
            <option value="month">آخر شهر</option>
            <option value="quarter">آخر 3 أشهر</option>
            <option value="season">الموسم</option>
          </select>
          <button className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <RefreshCw className="h-4 w-4" />
            تحديث
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 transition-colors">
            <Download className="h-4 w-4" />
            تصدير
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((card) => (
          <div key={card.title} className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div className={`rounded-lg ${card.color} p-2.5`}>
                <card.icon className="h-5 w-5 text-white" />
              </div>
              <span className={`flex items-center text-sm font-medium ${card.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {card.change}
                {card.trend === 'up' ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              </span>
            </div>
            <p className="mt-3 text-2xl font-bold text-gray-900">{card.value}</p>
            <p className="text-sm text-gray-500">{card.title}</p>
          </div>
        ))}
      </div>

      {/* Map / Chart Placeholder */}
      <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">خريطة NDVI الحقول</h2>
          </div>
          <span className="text-xs text-gray-400">آخر تحديث: 2026-04-02</span>
        </div>
        <div className="flex items-center justify-center h-72 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <Satellite className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">خريطة الأقمار الصناعية التفاعلية - قريبا</p>
            <p className="text-gray-300 text-xs mt-1">Sentinel-2 / Landsat-9</p>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">بيانات الاستشعار عن بعد</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-3 text-right font-medium">الحقل</th>
                <th className="px-4 py-3 text-right font-medium">آخر التقاط</th>
                <th className="px-4 py-3 text-right font-medium">NDVI</th>
                <th className="px-4 py-3 text-right font-medium">LAI</th>
                <th className="px-4 py-3 text-right font-medium">EVI</th>
                <th className="px-4 py-3 text-right font-medium">السحب</th>
                <th className="px-4 py-3 text-right font-medium">الحالة</th>
                <th className="px-4 py-3 text-right font-medium">المصدر</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {displayData.map((row) => (
                <tr key={row.field} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">{row.field}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{row.lastCapture}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-12 rounded-full bg-gray-200">
                        <div className="h-2 rounded-full bg-green-500" style={{ width: `${row.ndvi * 100}%` }} />
                      </div>
                      <span className="text-gray-700 font-medium">{row.ndvi}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{row.lai}</td>
                  <td className="px-4 py-3 text-gray-600">{row.evi}</td>
                  <td className="px-4 py-3 text-gray-500">{row.cloudCover}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${healthColor[row.healthStatus]}`}>
                      {row.healthStatus}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{row.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
