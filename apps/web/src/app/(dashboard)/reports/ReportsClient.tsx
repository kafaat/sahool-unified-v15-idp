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
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import { useReports, useGenerateReport } from '@/features/reports/hooks/useReports';
import type { Report } from '@/features/reports/api';

type ReportType = 'yield' | 'irrigation' | 'financial' | 'crop-health' | 'inventory' | 'weather';
type ReportPeriod = 'weekly' | 'monthly' | 'quarterly' | 'annual';

interface ReportCard {
  type: ReportType;
  apiType: string; // maps to the API's ReportType
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
    apiType: 'yield_analysis',
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
    apiType: 'irrigation',
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
    apiType: 'financial',
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
    apiType: 'disease',
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
    apiType: 'custom',
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
    apiType: 'weather',
    titleAr: 'تقرير الطقس',
    title: 'Weather Report',
    descriptionAr: 'تحليل بيانات الطقس وتأثيرها على المحاصيل',
    icon: PieChart,
    iconColor: 'text-cyan-600',
    bgColor: 'bg-cyan-100',
    available: true,
  },
];

const periodOptions: Array<{ value: ReportPeriod; labelAr: string; apiValue: string }> = [
  { value: 'weekly', labelAr: 'أسبوعي', apiValue: 'weekly' },
  { value: 'monthly', labelAr: 'شهري', apiValue: 'monthly' },
  { value: 'quarterly', labelAr: 'ربع سنوي', apiValue: 'quarterly' },
  { value: 'annual', labelAr: 'سنوي', apiValue: 'yearly' },
];

export default function ReportsClient() {
  const [selectedPeriod, setSelectedPeriod] = useState<ReportPeriod>('monthly');
  const [generatingReport, setGeneratingReport] = useState<string | null>(null);

  // Fetch recent reports from API
  const {
    data: recentReports,
    isLoading,
    isError,
    refetch,
  } = useReports();

  // Mutation for generating reports
  const generateMutation = useGenerateReport();

  const handleGenerate = (card: ReportCard) => {
    setGeneratingReport(card.type);
    const periodApiMap: Record<ReportPeriod, string> = {
      weekly: 'weekly',
      monthly: 'monthly',
      quarterly: 'quarterly',
      annual: 'yearly',
    };

    generateMutation.mutate(
      {
        type: card.apiType as Report['type'],
        format: 'pdf',
        period: periodApiMap[selectedPeriod] as Report['period'],
      },
      {
        onSettled: () => {
          setGeneratingReport(null);
        },
      },
    );
  };

  // Only open URLs with safe schemes (http/https/same-origin). This blocks
  // javascript:/data:/vbscript: URLs smuggled via a compromised or misbehaving
  // backend. noopener is set to drop the opener reference on new window.
  const isSafeDownloadUrl = (url: string): boolean => {
    try {
      // Allow relative URLs (resolved against current origin)
      if (url.startsWith('/')) return true;
      const parsed = new URL(url, window.location.origin);
      return parsed.protocol === 'https:' || parsed.protocol === 'http:';
    } catch {
      return false;
    }
  };

  const handleDownload = (report: Report) => {
    if (report.downloadUrl && isSafeDownloadUrl(report.downloadUrl)) {
      window.open(report.downloadUrl, '_blank', 'noopener,noreferrer');
    }
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
                onClick={() => handleGenerate(card)}
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

      {/* Generation success/error feedback */}
      {generateMutation.isSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700 text-sm">
          تم إنشاء التقرير بنجاح
        </div>
      )}
      {generateMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
          فشل في إنشاء التقرير. يرجى المحاولة مرة أخرى.
        </div>
      )}

      {/* Recent Reports */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">التقارير الأخيرة</h2>

        {/* Loading */}
        {isLoading && (
          <div className="bg-white rounded-lg border overflow-hidden p-6">
            <div className="space-y-4 animate-pulse">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="w-5 h-5 bg-gray-200 rounded" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/3" />
                    <div className="h-3 bg-gray-200 rounded w-1/4" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {isError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-red-700 font-medium mb-3">
              فشل في تحميل التقارير. يرجى المحاولة مرة أخرى.
            </p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              إعادة المحاولة
            </button>
          </div>
        )}

        {/* Table */}
        {!isLoading && !isError && (
          <div className="bg-white rounded-lg border overflow-hidden">
            {(!recentReports || recentReports.length === 0) ? (
              <div className="p-8 text-center text-gray-500">
                لا توجد تقارير سابقة
              </div>
            ) : (
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
                            <span className="font-medium text-gray-900">
                              {report.nameAr || report.name}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {reportCards.find((c) => c.apiType === report.type)?.titleAr ?? report.type}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {new Date(report.createdAt).toLocaleDateString('ar-SA')}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {report.fileSize
                            ? `${(report.fileSize / (1024 * 1024)).toFixed(1)} MB`
                            : '—'}
                        </td>
                        <td className="px-4 py-3">
                          {report.status === 'ready' ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              جاهز
                            </span>
                          ) : report.status === 'generating' || report.status === 'pending' ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              قيد الإنشاء
                            </span>
                          ) : report.status === 'failed' ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              فشل
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              {report.status}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {report.status === 'ready' ? (
                            <button
                              onClick={() => handleDownload(report)}
                              className="inline-flex items-center gap-1 text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                            >
                              <Download className="w-4 h-4" />
                              تحميل
                            </button>
                          ) : report.status === 'generating' || report.status === 'pending' ? (
                            <span className="text-xs text-gray-400">انتظر...</span>
                          ) : (
                            <span className="text-xs text-gray-400">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
