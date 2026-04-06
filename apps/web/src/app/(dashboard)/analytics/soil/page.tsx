'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Mountain,
  Droplets,
  Zap,
  Thermometer,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  FlaskConical,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { analyticsApi } from '@/features/analytics/api';
import { ApiError } from '@/lib/api/safe-fetch';

const statsCards = [
  {
    title: 'متوسط pH التربة',
    value: '7.2',
    change: '-0.1',
    trend: 'down' as const,
    icon: FlaskConical,
    color: 'bg-amber-500',
  },
  {
    title: 'رطوبة التربة',
    value: '42%',
    change: '+5%',
    trend: 'up' as const,
    icon: Droplets,
    color: 'bg-blue-500',
  },
  {
    title: 'التوصيل الكهربائي',
    value: '2.8 dS/m',
    change: '-0.3',
    trend: 'down' as const,
    icon: Zap,
    color: 'bg-yellow-500',
  },
  {
    title: 'درجة حرارة التربة',
    value: '22.5 C',
    change: '+1.8',
    trend: 'up' as const,
    icon: Thermometer,
    color: 'bg-red-500',
  },
];

const soilData = [
  { field: 'حقل القمح - شمال', ph: 7.1, nitrogen: 24, phosphorus: 18, potassium: 165, organic: '2.1%', ec: 2.4, moisture: 45, texture: 'طينية لومية', lastTest: '2026-03-28' },
  { field: 'حقل القمح - جنوب', ph: 7.3, nitrogen: 19, phosphorus: 22, potassium: 148, organic: '1.8%', ec: 2.6, moisture: 40, texture: 'لومية', lastTest: '2026-03-25' },
  { field: 'حقل الشعير', ph: 7.0, nitrogen: 21, phosphorus: 16, potassium: 172, organic: '2.3%', ec: 3.1, moisture: 38, texture: 'رملية لومية', lastTest: '2026-03-20' },
  { field: 'حقل الطماطم', ph: 6.8, nitrogen: 32, phosphorus: 28, potassium: 195, organic: '2.8%', ec: 1.9, moisture: 52, texture: 'طينية', lastTest: '2026-04-01' },
  { field: 'حقل النخيل', ph: 7.6, nitrogen: 15, phosphorus: 12, potassium: 130, organic: '1.2%', ec: 5.8, moisture: 30, texture: 'رملية', lastTest: '2026-03-15' },
  { field: 'حقل البرسيم', ph: 7.2, nitrogen: 28, phosphorus: 20, potassium: 158, organic: '2.5%', ec: 2.2, moisture: 48, texture: 'لومية طينية', lastTest: '2026-03-30' },
];

function getNutrientStatus(value: number, thresholds: { low: number; high: number }) {
  if (value < thresholds.low) return { label: 'منخفض', color: 'text-red-600' };
  if (value > thresholds.high) return { label: 'مرتفع', color: 'text-blue-600' };
  return { label: 'مناسب', color: 'text-green-600' };
}

export default function SoilAnalyticsPage() {
  const [dateRange, setDateRange] = useState('quarter');
  const [fieldFilter, setFieldFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiSoilData, setApiSoilData] = useState<typeof soilData | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resources = await analyticsApi.getResourceUsage({ period: dateRange });
      if (resources && Array.isArray(resources) && resources.length > 0) {
        // Map resource data to soil format if API provides it
        setApiSoilData(null); // API will populate when backend returns soil data
      } else {
        setApiSoilData(null);
      }
    } catch (err) {
      const message = err instanceof ApiError ? err.messageAr : 'فشل في جلب بيانات التربة';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const displayData = apiSoilData ?? soilData;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-500">جاري تحميل بيانات التربة...</p>
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
          <h1 className="text-2xl font-bold text-gray-900">تحليلات التربة</h1>
          <p className="text-gray-500 mt-1">تحليل شامل لخصائص التربة والعناصر الغذائية لتحسين خصوبة الحقول</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={fieldFilter}
            onChange={(e) => setFieldFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="all">جميع الحقول</option>
            <option value="wheat">حقول القمح</option>
            <option value="palm">حقل النخيل</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="month">آخر شهر</option>
            <option value="quarter">آخر 3 أشهر</option>
            <option value="year">آخر سنة</option>
          </select>
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

      {/* Chart Placeholder */}
      <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-5 w-5 text-amber-600" />
          <h2 className="text-lg font-semibold text-gray-900">مخطط العناصر الغذائية NPK</h2>
        </div>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <Mountain className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط تحليل التربة - قريبا</p>
          </div>
        </div>
      </div>

      {/* Soil Data Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">نتائج تحليل التربة</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-3 text-right font-medium">الحقل</th>
                <th className="px-4 py-3 text-right font-medium">pH</th>
                <th className="px-4 py-3 text-right font-medium">N (جزء/م)</th>
                <th className="px-4 py-3 text-right font-medium">P (جزء/م)</th>
                <th className="px-4 py-3 text-right font-medium">K (جزء/م)</th>
                <th className="px-4 py-3 text-right font-medium">المادة العضوية</th>
                <th className="px-4 py-3 text-right font-medium">EC (dS/m)</th>
                <th className="px-4 py-3 text-right font-medium">الرطوبة</th>
                <th className="px-4 py-3 text-right font-medium">القوام</th>
                <th className="px-4 py-3 text-right font-medium">آخر فحص</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {displayData.map((row) => {
                const nStatus = getNutrientStatus(row.nitrogen, { low: 20, high: 30 });
                const pStatus = getNutrientStatus(row.phosphorus, { low: 15, high: 25 });
                const kStatus = getNutrientStatus(row.potassium, { low: 140, high: 180 });
                return (
                  <tr key={row.field} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-gray-900">{row.field}</td>
                    <td className="px-4 py-3 text-gray-600">{row.ph}</td>
                    <td className={`px-4 py-3 font-medium ${nStatus.color}`}>{row.nitrogen}</td>
                    <td className={`px-4 py-3 font-medium ${pStatus.color}`}>{row.phosphorus}</td>
                    <td className={`px-4 py-3 font-medium ${kStatus.color}`}>{row.potassium}</td>
                    <td className="px-4 py-3 text-gray-600">{row.organic}</td>
                    <td className={`px-4 py-3 ${row.ec > 4 ? 'text-red-600 font-medium' : 'text-gray-600'}`}>{row.ec}</td>
                    <td className="px-4 py-3 text-gray-600">{row.moisture}%</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{row.texture}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{row.lastTest}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
