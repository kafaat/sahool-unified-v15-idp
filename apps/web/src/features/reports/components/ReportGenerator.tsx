/**
 * Report Generator Component
 * مكون إنشاء التقارير
 */

"use client";

import React, { useState } from "react";
import { FileText, Calendar, CheckCircle, Settings } from "lucide-react";
import {
  useGenerateFieldReport,
  useGenerateSeasonReport,
} from "../hooks/useReports";
import type {
  ReportSection,
  ReportFormat,
  GenerateFieldReportRequest,
  GenerateSeasonReportRequest,
} from "../types/reports";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ReportGeneratorProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  onReportGenerated?: (reportId: string) => void;
}

interface ReportConfig {
  type: "field" | "season";
  startDate: string;
  endDate: string;
  season?: string;
  sections: ReportSection[];
  format: ReportFormat;
  language: "ar" | "en" | "both";
  includeCharts: boolean;
  includeMaps: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Section Configurations
// ═══════════════════════════════════════════════════════════════════════════

const FIELD_SECTIONS: Array<{
  section: ReportSection;
  label: string;
  labelAr: string;
  description: string;
  required: boolean;
}> = [
  {
    section: "field_info",
    label: "Field Information",
    labelAr: "معلومات الحقل",
    description: "Basic field details and crop information",
    required: true,
  },
  {
    section: "ndvi_trend",
    label: "NDVI Trend",
    labelAr: "اتجاه NDVI",
    description: "Vegetation health trends over time",
    required: false,
  },
  {
    section: "health_zones",
    label: "Health Zones",
    labelAr: "مناطق الصحة",
    description: "Spatial distribution of crop health",
    required: false,
  },
  {
    section: "tasks_summary",
    label: "Tasks Summary",
    labelAr: "ملخص المهام",
    description: "Recent farming activities",
    required: false,
  },
  {
    section: "weather_summary",
    label: "Weather Summary",
    labelAr: "ملخص الطقس",
    description: "Weather conditions during period",
    required: false,
  },
  {
    section: "recommendations",
    label: "Recommendations",
    labelAr: "التوصيات",
    description: "AI-powered recommendations",
    required: false,
  },
];

const SEASON_SECTIONS: Array<{
  section: ReportSection;
  label: string;
  labelAr: string;
  description: string;
  required: boolean;
}> = [
  {
    section: "field_info",
    label: "Field Information",
    labelAr: "معلومات الحقل",
    description: "Basic field and crop information",
    required: true,
  },
  {
    section: "crop_stages",
    label: "Crop Stages",
    labelAr: "مراحل المحصول",
    description: "Growth stages timeline",
    required: false,
  },
  {
    section: "yield_estimate",
    label: "Yield Estimate",
    labelAr: "تقدير المحصول",
    description: "Predicted and actual yield",
    required: false,
  },
  {
    section: "input_summary",
    label: "Input Summary",
    labelAr: "ملخص المدخلات",
    description: "Water, fertilizer, and pesticides",
    required: false,
  },
  {
    section: "cost_analysis",
    label: "Cost Analysis",
    labelAr: "تحليل التكاليف",
    description: "Cost breakdown and ROI",
    required: false,
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  fieldId,
  fieldName,
  fieldNameAr,
  onReportGenerated,
}) => {
  const [config, setConfig] = useState<ReportConfig>({
    type: "field",
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0]!,
    endDate: new Date().toISOString().split("T")[0]!,
    sections: FIELD_SECTIONS.filter((s) => s.required).map((s) => s.section),
    format: "pdf",
    language: "both",
    includeCharts: true,
    includeMaps: true,
  });

  const generateFieldReport = useGenerateFieldReport();
  const generateSeasonReport = useGenerateSeasonReport();

  const currentSections =
    config.type === "field" ? FIELD_SECTIONS : SEASON_SECTIONS;

  const toggleSection = (section: ReportSection) => {
    const sectionConfig = currentSections.find((s) => s.section === section);
    if (sectionConfig?.required) return; // Don't toggle required sections

    setConfig((prev) => ({
      ...prev,
      sections: prev.sections.includes(section)
        ? prev.sections.filter((s) => s !== section)
        : [...prev.sections, section],
    }));
  };

  const handleTypeChange = (type: "field" | "season") => {
    const newSections =
      type === "field"
        ? FIELD_SECTIONS.filter((s) => s.required).map((s) => s.section)
        : SEASON_SECTIONS.filter((s) => s.required).map((s) => s.section);

    setConfig((prev) => ({
      ...prev,
      type,
      sections: newSections,
    }));
  };

  const handleGenerate = async () => {
    try {
      if (config.type === "field") {
        const request: GenerateFieldReportRequest = {
          fieldId,
          startDate: config.startDate,
          endDate: config.endDate,
          sections: config.sections,
          options: {
            includeCharts: config.includeCharts,
            includeMaps: config.includeMaps,
            format: config.format,
            language: config.language,
            titleAr: fieldNameAr ? `تقرير حقل - ${fieldNameAr}` : "تقرير الحقل",
            title: fieldName ? `Field Report - ${fieldName}` : "Field Report",
          },
        };

        const result = await generateFieldReport.mutateAsync(request);
        onReportGenerated?.(result.id);
      } else {
        const request: GenerateSeasonReportRequest = {
          fieldId,
          season: config.season,
          startDate: config.startDate,
          endDate: config.endDate,
          sections: config.sections,
          options: {
            includeCharts: config.includeCharts,
            format: config.format,
            language: config.language,
            titleAr: fieldNameAr
              ? `تقرير موسم - ${fieldNameAr}`
              : "تقرير الموسم",
            title: fieldName ? `Season Report - ${fieldName}` : "Season Report",
          },
        };

        const result = await generateSeasonReport.mutateAsync(request);
        onReportGenerated?.(result.id);
      }
    } catch (error) {
      logger.error("Failed to generate report:", error);
    }
  };

  const isGenerating =
    generateFieldReport.isPending || generateSeasonReport.isPending;
  const hasError = generateFieldReport.isError || generateSeasonReport.isError;

  return (
    <div className="space-y-6">
      {/* Report Type Selector */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-green-500" />
          نوع التقرير
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => handleTypeChange("field")}
            className={`p-4 rounded-lg border-2 transition-all text-right ${
              config.type === "field"
                ? "bg-green-50 border-green-500"
                : "bg-gray-50 border-gray-200 hover:border-gray-300"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">تقرير الحقل</h4>
                <p className="text-sm text-gray-600 mt-1">
                  تحليل شامل لأداء الحقل الحالي
                </p>
              </div>
              {config.type === "field" && (
                <CheckCircle className="w-6 h-6 text-green-500" />
              )}
            </div>
          </button>

          <button
            onClick={() => handleTypeChange("season")}
            className={`p-4 rounded-lg border-2 transition-all text-right ${
              config.type === "season"
                ? "bg-green-50 border-green-500"
                : "bg-gray-50 border-gray-200 hover:border-gray-300"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">تقرير الموسم</h4>
                <p className="text-sm text-gray-600 mt-1">
                  ملخص كامل للموسم الزراعي
                </p>
              </div>
              {config.type === "season" && (
                <CheckCircle className="w-6 h-6 text-green-500" />
              )}
            </div>
          </button>
        </div>
      </div>

      {/* Date Range Picker */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-green-500" />
          الفترة الزمنية
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              من تاريخ
            </label>
            <input
              type="date"
              value={config.startDate}
              onChange={(e) =>
                setConfig((prev) => ({ ...prev, startDate: e.target.value }))
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
              value={config.endDate}
              onChange={(e) =>
                setConfig((prev) => ({ ...prev, endDate: e.target.value }))
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {config.type === "season" && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الموسم (اختياري)
            </label>
            <input
              type="text"
              value={config.season || ""}
              onChange={(e) =>
                setConfig((prev) => ({ ...prev, season: e.target.value }))
              }
              placeholder="مثال: ربيع 2024"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              dir="rtl"
            />
          </div>
        )}
      </div>

      {/* Report Sections */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          أقسام التقرير
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentSections.map((section) => {
            const isSelected = config.sections.includes(section.section);
            const isRequired = section.required;

            return (
              <button
                key={section.section}
                onClick={() => toggleSection(section.section)}
                disabled={isRequired}
                className={`p-4 rounded-lg border-2 transition-all text-right ${
                  isSelected
                    ? "bg-green-50 border-green-500"
                    : "bg-gray-50 border-gray-200 hover:border-gray-300"
                } ${isRequired ? "opacity-75 cursor-not-allowed" : "cursor-pointer"}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-gray-900">
                        {section.labelAr}
                      </h4>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                      {isRequired && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          مطلوب
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {section.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Options */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-green-500" />
          إعدادات التقرير
        </h3>

        <div className="space-y-4">
          {/* Format and Language */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                صيغة التقرير
              </label>
              <select
                value={config.format}
                onChange={(e) =>
                  setConfig((prev) => ({
                    ...prev,
                    format: e.target.value as ReportFormat,
                  }))
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
                  setConfig((prev) => ({
                    ...prev,
                    language: e.target.value as "ar" | "en" | "both",
                  }))
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="ar">العربية</option>
                <option value="en">English</option>
                <option value="both">كلاهما</option>
              </select>
            </div>
          </div>

          {/* Checkboxes */}
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.includeCharts}
                onChange={(e) =>
                  setConfig((prev) => ({
                    ...prev,
                    includeCharts: e.target.checked,
                  }))
                }
                className="w-5 h-5 text-green-500 rounded focus:ring-green-500"
              />
              <span className="text-sm font-medium text-gray-700">
                تضمين الرسوم البيانية
              </span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.includeMaps}
                onChange={(e) =>
                  setConfig((prev) => ({
                    ...prev,
                    includeMaps: e.target.checked,
                  }))
                }
                className="w-5 h-5 text-green-500 rounded focus:ring-green-500"
              />
              <span className="text-sm font-medium text-gray-700">
                تضمين الخرائط
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex items-center justify-center">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || config.sections.length === 0}
          className="flex items-center gap-3 px-8 py-4 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-lg"
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>جاري إنشاء التقرير...</span>
            </>
          ) : (
            <>
              <FileText className="w-6 h-6" />
              <span>إنشاء التقرير</span>
            </>
          )}
        </button>
      </div>

      {/* Success Message */}
      {(generateFieldReport.isSuccess || generateSeasonReport.isSuccess) && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <p className="text-green-800 font-medium">تم إنشاء التقرير بنجاح!</p>
          <p className="text-sm text-green-600 mt-1">
            Report generated successfully!
          </p>
        </div>
      )}

      {/* Error Message */}
      {hasError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-800 font-medium">فشل في إنشاء التقرير</p>
          <p className="text-sm text-red-600 mt-1">
            Failed to generate report. Please try again.
          </p>
        </div>
      )}
    </div>
  );
};

export default ReportGenerator;
