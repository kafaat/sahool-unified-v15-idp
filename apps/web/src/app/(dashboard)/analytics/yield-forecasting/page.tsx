'use client';

import { useState } from 'react';
import {
  Brain,
  TrendingUp,
  Target,
  AlertCircle,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Sparkles,
  Clock,
  Percent,
} from 'lucide-react';

const statsCards = [
  {
    title: 'دقة التنبؤ',
    value: '89.2%',
    change: '+2.4%',
    trend: 'up' as const,
    icon: Target,
    color: 'bg-indigo-500',
  },
  {
    title: 'الإنتاج المتوقع',
    value: '210 طن',
    change: '+12%',
    trend: 'up' as const,
    icon: TrendingUp,
    color: 'bg-green-500',
  },
  {
    title: 'نماذج AI النشطة',
    value: '4',
    change: '+1',
    trend: 'up' as const,
    icon: Brain,
    color: 'bg-purple-500',
  },
  {
    title: 'تنبيهات المخاطر',
    value: '3',
    change: '-2',
    trend: 'down' as const,
    icon: AlertCircle,
    color: 'bg-orange-500',
  },
];

const forecastData = [
  { field: 'حقل القمح - شمال', crop: 'قمح', currentStage: 'التفريع', harvestDate: '2026-05-20', predictedYield: '5.3 طن/هكتار', confidence: 91, riskLevel: 'منخفض', model: 'LSTM-v3', factors: 'NDVI, SM, ET' },
  { field: 'حقل القمح - جنوب', crop: 'قمح', currentStage: 'الإزهار', harvestDate: '2026-05-15', predictedYield: '4.8 طن/هكتار', confidence: 87, riskLevel: 'منخفض', model: 'LSTM-v3', factors: 'NDVI, SM, درجة حرارة' },
  { field: 'حقل الشعير', crop: 'شعير', currentStage: 'التسنبل', harvestDate: '2026-05-08', predictedYield: '4.1 طن/هكتار', confidence: 84, riskLevel: 'متوسط', model: 'XGBoost-v2', factors: 'SM, ET, أمطار' },
  { field: 'حقل الطماطم', crop: 'طماطم', currentStage: 'الإثمار', harvestDate: '2026-06-10', predictedYield: '30.2 طن/هكتار', confidence: 92, riskLevel: 'منخفض', model: 'CropGPT-v1', factors: 'NDVI, حرارة, رطوبة' },
  { field: 'حقل البرسيم', crop: 'برسيم', currentStage: 'حشة 4', harvestDate: '2026-04-25', predictedYield: '13.5 طن/هكتار', confidence: 78, riskLevel: 'متوسط', model: 'RF-v4', factors: 'SM, N, حرارة' },
  { field: 'حقل النخيل', crop: 'نخيل', currentStage: 'الكمري', harvestDate: '2026-09-15', predictedYield: '8.5 طن/هكتار', confidence: 72, riskLevel: 'مرتفع', model: 'LSTM-v3', factors: 'حرارة, رطوبة, RPW' },
];

const riskColor: Record<string, string> = {
  'منخفض': 'bg-green-100 text-green-800',
  'متوسط': 'bg-yellow-100 text-yellow-800',
  'مرتفع': 'bg-red-100 text-red-800',
};

function getConfidenceColor(value: number) {
  if (value >= 85) return 'text-green-600';
  if (value >= 75) return 'text-yellow-600';
  return 'text-red-600';
}

export default function YieldForecastingPage() {
  const [dateRange, setDateRange] = useState('season');
  const [modelFilter, setModelFilter] = useState('all');

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التنبؤ بالإنتاجية</h1>
          <p className="text-gray-500 mt-1">تنبؤات الإنتاجية المبنية على الذكاء الاصطناعي وتحليل المخاطر المحتملة</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={modelFilter}
            onChange={(e) => setModelFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="all">جميع النماذج</option>
            <option value="lstm">LSTM-v3</option>
            <option value="xgboost">XGBoost-v2</option>
            <option value="cropgpt">CropGPT-v1</option>
            <option value="rf">RF-v4</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="season">الموسم الحالي</option>
            <option value="next">الموسم القادم</option>
            <option value="year">السنة الكاملة</option>
          </select>
          <button className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <Sparkles className="h-4 w-4" />
            تحديث التنبؤات
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

      {/* Chart Placeholder */}
      <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900">منحنى التنبؤ مع فترة الثقة</h2>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Clock className="h-3.5 w-3.5" />
            <span>آخر تحديث: منذ 3 ساعات</span>
          </div>
        </div>
        <div className="flex items-center justify-center h-64 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <Brain className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط التنبؤ بالإنتاجية (AI) - قريبا</p>
            <p className="text-gray-300 text-xs mt-1">LSTM / XGBoost / CropGPT</p>
          </div>
        </div>
      </div>

      {/* Forecast Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">تفاصيل التنبؤات</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-3 text-right font-medium">الحقل</th>
                <th className="px-4 py-3 text-right font-medium">المحصول</th>
                <th className="px-4 py-3 text-right font-medium">المرحلة</th>
                <th className="px-4 py-3 text-right font-medium">موعد الحصاد</th>
                <th className="px-4 py-3 text-right font-medium">الإنتاجية المتوقعة</th>
                <th className="px-4 py-3 text-right font-medium">الثقة</th>
                <th className="px-4 py-3 text-right font-medium">المخاطر</th>
                <th className="px-4 py-3 text-right font-medium">النموذج</th>
                <th className="px-4 py-3 text-right font-medium">العوامل</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {forecastData.map((row) => (
                <tr key={row.field} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">{row.field}</td>
                  <td className="px-4 py-3 text-gray-600">{row.crop}</td>
                  <td className="px-4 py-3 text-gray-600">{row.currentStage}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{row.harvestDate}</td>
                  <td className="px-4 py-3 text-gray-900 font-bold">{row.predictedYield}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <Percent className="h-3 w-3 text-gray-400" />
                      <span className={`font-medium ${getConfidenceColor(row.confidence)}`}>{row.confidence}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${riskColor[row.riskLevel]}`}>
                      {row.riskLevel}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{row.model}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{row.factors}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
