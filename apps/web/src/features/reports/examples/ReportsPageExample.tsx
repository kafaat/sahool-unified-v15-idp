/**
 * Reports Page Example
 * مثال على صفحة التقارير
 *
 * This is a complete example showing how to use all report components together
 */

'use client';

import React, { useState } from 'react';
import { FileText, History, Eye } from 'lucide-react';
import {
  ReportGenerator,
  ReportPreview,
  ReportHistory,
  FieldReportTemplate,
} from '../components';
import { useFieldReportData } from '../hooks/useReports';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

type ViewMode = 'generate' | 'history' | 'preview' | 'template';

interface ReportsPageExampleProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════════════════

export const ReportsPageExample: React.FC<ReportsPageExampleProps> = ({
  fieldId,
  fieldName = 'Field Name',
  fieldNameAr = 'اسم الحقل',
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('generate');
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  // Handle report generation success
  const handleReportGenerated = (reportId: string) => {
    setSelectedReportId(reportId);
    setViewMode('preview');
  };

  // Handle view report from history
  const handleViewReport = (reportId: string) => {
    setSelectedReportId(reportId);
    setViewMode('preview');
  };

  // Handle share report
  const handleShareReport = (reportId: string) => {
    // In a real app, you might open a share modal
    console.log('Share report:', reportId);
  };

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                التقارير
              </h1>
              <p className="text-gray-600">
                {fieldNameAr} • {fieldName}
              </p>
            </div>
            <FileText className="w-12 h-12 text-green-500" />
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2 mb-6">
          <div className="flex gap-2">
            <TabButton
              icon={<FileText className="w-5 h-5" />}
              label="إنشاء تقرير"
              labelEn="Generate Report"
              active={viewMode === 'generate'}
              onClick={() => setViewMode('generate')}
            />
            <TabButton
              icon={<History className="w-5 h-5" />}
              label="سجل التقارير"
              labelEn="Report History"
              active={viewMode === 'history'}
              onClick={() => setViewMode('history')}
            />
            {selectedReportId && (
              <TabButton
                icon={<Eye className="w-5 h-5" />}
                label="معاينة التقرير"
                labelEn="Preview Report"
                active={viewMode === 'preview'}
                onClick={() => setViewMode('preview')}
              />
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="space-y-6">
          {viewMode === 'generate' && (
            <ReportGenerator
              fieldId={fieldId}
              fieldName={fieldName}
              fieldNameAr={fieldNameAr}
              onReportGenerated={handleReportGenerated}
            />
          )}

          {viewMode === 'history' && (
            <ReportHistory
              fieldId={fieldId}
              onViewReport={handleViewReport}
              onShareReport={handleShareReport}
              showFilters={true}
            />
          )}

          {viewMode === 'preview' && selectedReportId && (
            <ReportPreview
              reportId={selectedReportId}
              showNavigation={true}
            />
          )}

          {viewMode === 'template' && (
            <TemplatePreview fieldId={fieldId} />
          )}
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 rounded-xl border border-blue-200 p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            كيفية استخدام التقارير
          </h3>
          <ul className="space-y-2 text-blue-800">
            <li className="flex items-start gap-2">
              <span className="font-bold">1.</span>
              <span>اختر نوع التقرير (حقل أو موسم)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">2.</span>
              <span>حدد الفترة الزمنية المطلوبة</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">3.</span>
              <span>اختر الأقسام التي تريد تضمينها</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">4.</span>
              <span>اضغط على "إنشاء التقرير" وانتظر حتى يكتمل الإنشاء</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">5.</span>
              <span>شاهد، نزّل، أو شارك التقرير</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Helper Components
// ═══════════════════════════════════════════════════════════════════════════

interface TabButtonProps {
  icon: React.ReactNode;
  label: string;
  labelEn: string;
  active: boolean;
  onClick: () => void;
}

const TabButton: React.FC<TabButtonProps> = ({ icon, label, labelEn, active, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
        active
          ? 'bg-green-500 text-white shadow-md'
          : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
      }`}
    >
      {icon}
      <div className="text-right">
        <div className="text-sm">{label}</div>
        <div className="text-xs opacity-75">{labelEn}</div>
      </div>
    </button>
  );
};

// Template Preview Component
const TemplatePreview: React.FC<{ fieldId: string }> = ({ fieldId }) => {
  const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  const endDate = new Date().toISOString();

  const { data, isLoading } = useFieldReportData(fieldId, startDate, endDate);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
        <p className="text-gray-600">جاري تحميل البيانات...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <p className="text-gray-600">لا توجد بيانات متاحة</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <FieldReportTemplate
        data={data}
        sections={['field_info', 'ndvi_trend', 'health_zones', 'recommendations']}
        language="both"
        startDate={startDate}
        endDate={endDate}
        title="Field Performance Report"
        titleAr="تقرير أداء الحقل"
      />
    </div>
  );
};

export default ReportsPageExample;
