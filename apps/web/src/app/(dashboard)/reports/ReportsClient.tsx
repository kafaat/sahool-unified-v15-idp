'use client';

import React, { useState } from 'react';
import {
  FileBarChart,
  Download,
  TrendingUp,
  Droplets,
  Sprout,
  DollarSign,
  BarChart3,
  PieChart,
} from 'lucide-react';

type ReportType = 'yield' | 'irrigation' | 'financial' | 'crop-health' | 'inventory' | 'weather';
type ReportPeriod = 'weekly' | 'monthly' | 'quarterly' | 'annual';

interface ReportCard {
  type: ReportType;
  titleAr: string;
  title: string;
  descriptionAr: string;
  icon: React.ElementType;
  iconColor: string;
  bgColor: string;
  available: boolean;
}

const reportCards: ReportCard[] = [
  {
    type: 'yield',
    titleAr: 'تقرير الإنتاجية',
    title: 'Yield Report',
    descriptionAr: 'تحليل شامل لإنتاجية المحاصيل والمقارنة بالمواسم السابقة',
    icon: TrendingUp,
    iconColor: 'text-green-600',
    bgColor: 'bg-green-100',
    available: true,
  },
  {
    type: 'irrigation',
    titleAr: 'تقرير الري',
    title: 'Irrigation Report',
    descriptionAr: 'استهلاك المياه وكفاءة الري وتوصيات التحسين',
    icon: Droplets,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-100',
    available: true,
  },
  {
    type: 'financial',
    titleAr: 'التقرير المالي',
    title: 'Financial Report',
    descriptionAr: 'الإيرادات والمصروفات والعائد على الاستثمار لكل موسم',
    icon: DollarSign,
    iconColor: 'text-purple-600',
    bgColor: 'bg-purple-100',
    available: true,
  },
  {
    type: 'crop-health',
    titleAr: 'تقرير صحة المحاصيل',
    title: 'Crop Health Report',
    descriptionAr: 'مؤشرات NDVI وتحليل الأمراض وحالة النمو',
    icon: Sprout,
    iconColor: 'text-sahool-green-600',
    bgColor: 'bg-sahool-green-100',
    available: true,
  },
  {
    type: 'inventory',
    titleAr: 'تقرير المخزون',
    title: 'Inventory Report',
    descriptionAr: 'حركة المخزون والاستهلاك والتنبيهات',
    icon: BarChart3,
    iconColor: 'text-orange-600',
    bgColor: 'bg-orange-100',
    available: true,
  },
  {
    type: 'weather',
    titleAr: 'تقرير الطقس',
    title: 'Weather Report',
    descriptionAr: 'تحليل بيانات الطقس وتأثيرها على المحاصيل',
    icon: PieChart,
    iconColor: 'text-cyan-600',
    bgColor: 'bg-cyan-100',
    available: true,
  },
];

const periodOptions: Array<{ value: ReportPeriod; labelAr: string }> = [
  { value: 'weekly', labelAr: 'أسبوعي' },
  { value: 'monthly', labelAr: 'شهري' },
  { value: 'quarterly', labelAr: 'ربع سنوي' },
  { value: 'annual', labelAr: 'سنوي' },
];

// Mock recent reports
const recentReports = [
  {
    id: 'r-001',
    titleAr: 'تقرير إنتاجية القمح - يناير 2026',
    type: 'yield' as ReportType,
    date: '2026-02-01',
    sizeMb: 2.4,
    status: 'ready',
  },
  {
    id: 'r-002',
    titleAr: 'تقرير الري الشهري - يناير 2026',
    type: 'irrigation' as ReportType,
    date: '2026-02-03',
    sizeMb: 1.8,
    status: 'ready',
  },
  {
    id: 'r-003',
    titleAr: 'التقرير المالي - الربع الرابع 2025',
    type: 'financial' as ReportType,
    date: '2026-01-15',
    sizeMb: 3.1,
    status: 'ready',
  },
  {
    id: 'r-004',
    titleAr: 'تقرير صحة المحاصيل - فبراير 2026',
    type: 'crop-health' as ReportType,
    date: '2026-02-15',
    sizeMb: 0,
    status: 'generating',
  },
];

export default function ReportsClient() {
  const [selectedPeriod, setSelectedPeriod] = useState<ReportPeriod>('monthly');
  const [generatingReport, setGeneratingReport] = useState<string | null>(null);

  const handleGenerate = (type: ReportType) => {
    setGeneratingReport(type);
    // Simulate report generation
    setTimeout(() => setGeneratingReport(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التقارير</h1>
          <p className="text-gray-500 mt-1">Reports & Analytics</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as ReportPeriod)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          >
            {periodOptions.map((p) => (
              <option key={p.value} value={p.value}>
                {p.labelAr}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Report Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reportCards.map((card) => {
          const Icon = card.icon;
          const isGenerating = generatingReport === card.type;
          return (
            <div
              key={card.type}
              className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4 mb-4">
                <div
                  className={`w-12 h-12 ${card.bgColor} rounded-lg flex items-center justify-center`}
                >
                  <Icon className={`w-6 h-6 ${card.iconColor}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{card.titleAr}</h3>
                  <p className="text-sm text-gray-500 mt-1">{card.descriptionAr}</p>
                </div>
              </div>
              <button
                onClick={() => handleGenerate(card.type)}
                disabled={isGenerating}
                className={`w-full py-2 rounded-lg text-sm font-medium transition-colors ${
                  isGenerating
                    ? 'bg-gray-100 text-gray-400 cursor-wait'
                    : 'bg-sahool-green-50 text-sahool-green-700 hover:bg-sahool-green-100'
                }`}
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-sahool-green-600" />
                    جاري الإنشاء...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <FileBarChart className="w-4 h-4" />
                    إنشاء التقرير
                  </span>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Recent Reports */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">التقارير الأخيرة</h2>
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                    التقرير
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">النوع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                    التاريخ
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحجم</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">إجراء</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {recentReports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <FileBarChart className="w-5 h-5 text-gray-400" />
                        <span className="font-medium text-gray-900">{report.titleAr}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {reportCards.find((c) => c.type === report.type)?.titleAr ?? report.type}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(report.date).toLocaleDateString('ar-SA')}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {report.sizeMb > 0 ? `${report.sizeMb} MB` : '—'}
                    </td>
                    <td className="px-4 py-3">
                      {report.status === 'ready' ? (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          جاهز
                        </span>
                      ) : (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          قيد الإنشاء
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {report.status === 'ready' ? (
                        <button className="inline-flex items-center gap-1 text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium">
                          <Download className="w-4 h-4" />
                          تحميل
                        </button>
                      ) : (
                        <span className="text-xs text-gray-400">انتظر...</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
