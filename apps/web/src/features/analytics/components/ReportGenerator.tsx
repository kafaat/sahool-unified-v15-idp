/**
 * Report Generator Component
 * مكون إنشاء التقارير
 */

'use client';

import React, { useState } from 'react';
import { FileText, Download, CheckCircle } from 'lucide-react';
import { useGenerateReport, useDownloadReport } from '../hooks/useAnalytics';
import type { AnalyticsFilters, ReportConfig, ReportSectionType } from '../types';

interface ReportGeneratorProps {
  filters?: AnalyticsFilters;
}

const reportSections: Array<{
  type: ReportSectionType;
  label: string;
  labelAr: string;
  description: string;
}> = [
  {
    type: 'summary',
    label: 'Summary',
    labelAr: 'الملخص',
    description: 'Overview of key metrics and statistics',
  },
  {
    type: 'yield_analysis',
    label: 'Yield Analysis',
    labelAr: 'تحليل المحصول',
    description: 'Detailed yield analysis with charts',
  },
  {
    type: 'cost_analysis',
    label: 'Cost Analysis',
    labelAr: 'تحليل التكاليف',
    description: 'Cost breakdown and analysis',
  },
  {
    type: 'revenue_analysis',
    label: 'Revenue Analysis',
    labelAr: 'تحليل الإيرادات',
    description: 'Revenue and profit analysis',
  },
  {
    type: 'comparison',
    label: 'Comparison',
    labelAr: 'المقارنة',
    description: 'Field and season comparisons',
  },
  {
    type: 'recommendations',
    label: 'Recommendations',
    labelAr: 'التوصيات',
    description: 'AI-powered recommendations',
  },
];

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({ }) => {
  const [config, setConfig] = useState<ReportConfig>({
    title: 'تقرير التحليلات الزراعية',
    titleAr: 'تقرير التحليلات الزراعية',
    period: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]!,
      end: new Date().toISOString().split('T')[0]!,
    },
    sections: reportSections.map((section) => ({
      type: section.type,
      enabled: true,
    })),
    includeCharts: true,
    includeTables: true,
    format: 'pdf',
    language: 'ar',
  });

  const generateMutation = useGenerateReport();
  const downloadMutation = useDownloadReport();

  const toggleSection = (sectionType: ReportSectionType) => {
    setConfig({
      ...config,
      sections: config.sections.map((section) =>
        section.type === sectionType ? { ...section, enabled: !section.enabled } : section
      ),
    });
  };

  const handleGenerate = async () => {
    try {
      const result = await generateMutation.mutateAsync(config);

      // Auto-download after generation
      const blob = await downloadMutation.mutateAsync(result.reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sahool-report-${result.reportId}.${config.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Report Configuration */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          إعدادات التقرير
        </h3>

        <div className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              عنوان التقرير
            </label>
            <input
              type="text"
              value={config.titleAr}
              onChange={(e) => setConfig({ ...config, titleAr: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              dir="rtl"
            />
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                من تاريخ
              </label>
              <input
                type="date"
                value={config.period.start}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    period: { ...config.period, start: e.target.value },
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                إلى تاريخ
              </label>
              <input
                type="date"
                value={config.period.end}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    period: { ...config.period, end: e.target.value },
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Format and Language */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                صيغة التقرير
              </label>
              <select
                value={config.format}
                onChange={(e) =>
                  setConfig({ ...config, format: e.target.value as ReportConfig['format'] })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="csv">CSV</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                اللغة
              </label>
              <select
                value={config.language}
                onChange={(e) =>
                  setConfig({ ...config, language: e.target.value as ReportConfig['language'] })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="ar">العربية</option>
                <option value="en">English</option>
                <option value="both">كلاهما</option>
              </select>
            </div>
            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.includeCharts}
                  onChange={(e) =>
                    setConfig({ ...config, includeCharts: e.target.checked })
                  }
                  className="w-5 h-5 text-green-500 rounded focus:ring-green-500"
                />
                <span className="text-sm font-medium text-gray-700">تضمين الرسوم البيانية</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Sections Selection */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          أقسام التقرير
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="report-sections-grid">
          {reportSections.map((section) => {
            const enabled = config.sections.find((s) => s.type === section.type)?.enabled || false;
            return (
              <div
                key={section.type}
                data-testid={`report-section-${section.type}`}
                onClick={() => toggleSection(section.type)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  enabled
                    ? 'bg-green-50 border-green-500'
                    : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-gray-900">{section.labelAr}</h4>
                      {enabled && <CheckCircle className="w-5 h-5 text-green-500" />}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{section.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex items-center justify-center">
        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending || downloadMutation.isPending}
          className="flex items-center gap-3 px-8 py-4 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-lg"
        >
          {generateMutation.isPending || downloadMutation.isPending ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>جاري إنشاء التقرير...</span>
            </>
          ) : (
            <>
              <FileText className="w-6 h-6" />
              <span>إنشاء التقرير</span>
              <Download className="w-5 h-5" />
            </>
          )}
        </button>
      </div>

      {/* Success Message */}
      {generateMutation.isSuccess && !downloadMutation.isPending && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <p className="text-green-800 font-medium">
            تم إنشاء التقرير بنجاح!
          </p>
          <p className="text-sm text-green-600 mt-1">
            Report generated successfully!
          </p>
        </div>
      )}

      {/* Error Message */}
      {(generateMutation.isError || downloadMutation.isError) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-800 font-medium">
            فشل في إنشاء التقرير
          </p>
          <p className="text-sm text-red-600 mt-1">
            Failed to generate report
          </p>
        </div>
      )}
    </div>
  );
};

export default ReportGenerator;
