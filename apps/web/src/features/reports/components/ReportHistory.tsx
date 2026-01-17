/**
 * Report History Component
 * مكون سجل التقارير
 *
 * Displays a list of previously generated reports with filtering and actions
 */

"use client";

import React, { useState } from "react";
import {
  FileText,
  Download,
  Share2,
  Trash2,
  Eye,
  Filter,
  Search,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  AlertCircle,
} from "lucide-react";
import {
  useReportHistory,
  useDeleteFieldReport,
  useDownloadReport,
} from "../hooks/useReports";
import type {
  ReportHistoryFilters,
  ReportType,
  ReportStatus,
} from "../types/reports";
import { formatDateForPDF } from "../utils/pdf-generator";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ReportHistoryProps {
  fieldId?: string;
  onViewReport?: (reportId: string) => void;
  onShareReport?: (reportId: string) => void;
  showFilters?: boolean;
  compact?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const ReportHistory: React.FC<ReportHistoryProps> = ({
  fieldId,
  onViewReport,
  onShareReport,
  showFilters = true,
  compact = false,
}) => {
  const [filters, setFilters] = useState<ReportHistoryFilters>({
    fieldId,
    type: undefined,
    status: undefined,
    search: "",
  });
  const [showFilterPanel, setShowFilterPanel] = useState(false);

  const { data: reports, isLoading, error } = useReportHistory(filters);
  const deleteMutation = useDeleteFieldReport();
  const downloadMutation = useDownloadReport();

  const handleSearch = (search: string) => {
    setFilters((prev) => ({ ...prev, search }));
  };

  const handleFilterChange = (key: keyof ReportHistoryFilters, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleDelete = async (reportId: string, reportTitle: string) => {
    if (
      window.confirm(
        `هل تريد حذف التقرير "${reportTitle}"؟\nAre you sure you want to delete "${reportTitle}"?`,
      )
    ) {
      try {
        await deleteMutation.mutateAsync(reportId);
      } catch (error) {
        logger.error("Failed to delete report:", error);
      }
    }
  };

  const handleDownload = async (reportId: string) => {
    try {
      await downloadMutation.mutateAsync(reportId);
    } catch (error) {
      logger.error("Failed to download report:", error);
    }
  };

  const clearFilters = () => {
    setFilters({
      fieldId,
      type: undefined,
      status: undefined,
      search: "",
      startDate: undefined,
      endDate: undefined,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">جاري تحميل التقارير...</p>
          <p className="text-sm text-gray-500">Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-900 font-medium">فشل في تحميل التقارير</p>
          <p className="text-sm text-gray-500 mt-1">Failed to load reports</p>
        </div>
      </div>
    );
  }

  const reportsList = reports || [];
  const hasActiveFilters =
    filters.type ||
    filters.status ||
    filters.search ||
    filters.startDate ||
    filters.endDate;

  return (
    <div className="space-y-6">
      {/* Header with Search and Filters */}
      {showFilters && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-500" />
              سجل التقارير
            </h3>
            <button
              onClick={() => setShowFilterPanel(!showFilterPanel)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                showFilterPanel || hasActiveFilters
                  ? "bg-green-500 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Filter className="w-4 h-4" />
              <span>الفلاتر</span>
              {hasActiveFilters && (
                <span className="bg-white text-green-500 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                  !
                </span>
              )}
            </button>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={filters.search || ""}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="ابحث في التقارير... Search reports..."
              className="w-full pr-10 pl-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              dir="rtl"
            />
          </div>

          {/* Filter Panel */}
          {showFilterPanel && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Report Type Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    نوع التقرير
                  </label>
                  <select
                    value={filters.type || ""}
                    onChange={(e) =>
                      handleFilterChange("type", e.target.value || undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="">الكل</option>
                    <option value="field">تقرير حقل</option>
                    <option value="season">تقرير موسم</option>
                    <option value="scouting">تقرير استكشاف</option>
                    <option value="comprehensive">تقرير شامل</option>
                  </select>
                </div>

                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    الحالة
                  </label>
                  <select
                    value={filters.status || ""}
                    onChange={(e) =>
                      handleFilterChange("status", e.target.value || undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="">الكل</option>
                    <option value="ready">جاهز</option>
                    <option value="generating">قيد الإنشاء</option>
                    <option value="pending">معلق</option>
                    <option value="failed">فشل</option>
                    <option value="expired">منتهي الصلاحية</option>
                  </select>
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    من تاريخ
                  </label>
                  <input
                    type="date"
                    value={filters.startDate || ""}
                    onChange={(e) =>
                      handleFilterChange(
                        "startDate",
                        e.target.value || undefined,
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>
              </div>

              {hasActiveFilters && (
                <div className="flex justify-end">
                  <button
                    onClick={clearFilters}
                    className="text-sm text-gray-600 hover:text-gray-900 underline"
                  >
                    مسح جميع الفلاتر
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Reports List */}
      <div className="space-y-4">
        {reportsList.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">لا توجد تقارير</p>
            <p className="text-sm text-gray-500 mt-2">No reports found</p>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="mt-4 text-green-500 hover:text-green-600 underline text-sm"
              >
                مسح الفلاتر
              </button>
            )}
          </div>
        ) : (
          reportsList.map((report) => (
            <ReportCard
              key={report.id}
              report={report}
              compact={compact}
              onView={onViewReport}
              onShare={onShareReport}
              onDownload={handleDownload}
              onDelete={handleDelete}
              isDeleting={deleteMutation.isPending}
              isDownloading={downloadMutation.isPending}
            />
          ))
        )}
      </div>

      {/* Stats Footer */}
      {reportsList.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
          <div className="flex items-center justify-between">
            <span>
              إجمالي التقارير:{" "}
              <span className="font-bold text-gray-900">
                {reportsList.length}
              </span>
            </span>
            <span>
              Total Reports:{" "}
              <span className="font-bold text-gray-900">
                {reportsList.length}
              </span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Report Card Component
// ═══════════════════════════════════════════════════════════════════════════

interface ReportCardProps {
  report: any; // ReportHistoryItem
  compact?: boolean;
  onView?: (reportId: string) => void;
  onShare?: (reportId: string) => void;
  onDownload: (reportId: string) => void;
  onDelete: (reportId: string, title: string) => void;
  isDeleting?: boolean;
  isDownloading?: boolean;
}

const ReportCard: React.FC<ReportCardProps> = ({
  report,
  compact = false,
  onView,
  onShare,
  onDownload,
  onDelete,
  isDeleting,
  isDownloading,
}) => {
  const getStatusIcon = (status: ReportStatus) => {
    switch (status) {
      case "ready":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "generating":
      case "pending":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "expired":
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <FileText className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusLabel = (status: ReportStatus) => {
    const labels = {
      ready: { ar: "جاهز", en: "Ready" },
      generating: { ar: "قيد الإنشاء", en: "Generating" },
      pending: { ar: "معلق", en: "Pending" },
      failed: { ar: "فشل", en: "Failed" },
      expired: { ar: "منتهي", en: "Expired" },
    };
    return labels[status] || { ar: status, en: status };
  };

  const getTypeLabel = (type: ReportType) => {
    const labels = {
      field: { ar: "تقرير حقل", en: "Field Report" },
      season: { ar: "تقرير موسم", en: "Season Report" },
      scouting: { ar: "تقرير استكشاف", en: "Scouting Report" },
      tasks: { ar: "تقرير مهام", en: "Tasks Report" },
      ndvi: { ar: "تقرير NDVI", en: "NDVI Report" },
      weather: { ar: "تقرير طقس", en: "Weather Report" },
      comprehensive: { ar: "تقرير شامل", en: "Comprehensive Report" },
    };
    return labels[type] || { ar: type, en: type };
  };

  const statusLabel = getStatusLabel(report.status);
  const typeLabel = getTypeLabel(report.type);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        {/* Report Info */}
        <div className="flex-1">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-1">
              {getStatusIcon(report.status)}
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-gray-900 mb-1">
                {report.titleAr}
              </h4>
              <p className="text-sm text-gray-600 mb-3">{report.title}</p>

              {/* Meta Info */}
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <FileText className="w-4 h-4" />
                  <span>{typeLabel.ar}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>{formatDateForPDF(report.createdAt, "ar")}</span>
                </div>
                {report.pageCount && (
                  <div className="flex items-center gap-1">
                    <FileText className="w-4 h-4" />
                    <span>{report.pageCount} صفحة</span>
                  </div>
                )}
                {report.downloadCount !== undefined && (
                  <div className="flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    <span>{report.downloadCount} تنزيل</span>
                  </div>
                )}
              </div>

              {!compact && (
                <div className="mt-3 flex items-center gap-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      report.status === "ready"
                        ? "bg-green-100 text-green-700"
                        : report.status === "generating" ||
                            report.status === "pending"
                          ? "bg-blue-100 text-blue-700"
                          : report.status === "failed"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {statusLabel.ar} • {statusLabel.en}
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                    {report.format.toUpperCase()}
                  </span>
                  {report.language && (
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                      {report.language === "both"
                        ? "عربي + EN"
                        : report.language === "ar"
                          ? "عربي"
                          : "English"}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        {report.status === "ready" && (
          <div className="flex items-center gap-2">
            {onView && (
              <button
                onClick={() => onView(report.id)}
                className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                title="View Report / عرض التقرير"
              >
                <Eye className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={() => onDownload(report.id)}
              disabled={isDownloading}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
              title="Download / تنزيل"
            >
              {isDownloading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Download className="w-5 h-5" />
              )}
            </button>
            {onShare && (
              <button
                onClick={() => onShare(report.id)}
                className="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                title="Share / مشاركة"
              >
                <Share2 className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={() => onDelete(report.id, report.titleAr)}
              disabled={isDeleting}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              title="Delete / حذف"
            >
              {isDeleting ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Trash2 className="w-5 h-5" />
              )}
            </button>
          </div>
        )}
      </div>

      {/* Field Name Tag */}
      {report.fieldName && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <span className="text-sm text-gray-600">
            <span className="font-medium">{report.fieldNameAr}</span>
            {" • "}
            <span className="text-gray-500">{report.fieldName}</span>
          </span>
        </div>
      )}
    </div>
  );
};

export default ReportHistory;
