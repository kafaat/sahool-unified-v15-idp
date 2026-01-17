/**
 * Report Preview Component
 * مكون معاينة التقرير
 */

"use client";

import React, { useState } from "react";
import {
  Download,
  Share2,
  ChevronLeft,
  ChevronRight,
  Mail,
  Link2,
  Eye,
  FileText,
  Loader2,
} from "lucide-react";
import {
  useReport,
  useDownloadReport,
  useShareReport,
  useReportStatus,
} from "../hooks/useReports";
import type { ShareMethod } from "../types/reports";
import { generateEmailShareContent } from "../utils/pdf-generator";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ReportPreviewProps {
  reportId: string;
  showNavigation?: boolean;
  onClose?: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const ReportPreview: React.FC<ReportPreviewProps> = ({
  reportId,
  showNavigation = true,
  onClose: _onClose,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [showShareMenu, setShowShareMenu] = useState(false);

  const { data: report, isLoading, error } = useReport(reportId);
  const { data: statusData } = useReportStatus(
    reportId,
    report?.status === "generating" || report?.status === "pending",
  );
  const downloadMutation = useDownloadReport();
  const shareMutation = useShareReport();

  // Use status data if available, otherwise use report data
  const activeReport = statusData || report;

  const totalPages = activeReport?.pageCount || 1;

  // Helper to safely access properties (handles both Report and GeneratedReport types)
  const r = (activeReport as unknown as Record<string, unknown>) || {};

  const getReportName = () => {
    return (
      (r.titleAr as string) ||
      (r.nameAr as string) ||
      (r.title as string) ||
      (r.name as string) ||
      "SAHOOL Report"
    );
  };

  const getReportNameEn = () => {
    return (r.title as string) || (r.name as string) || "SAHOOL Report";
  };

  const getFieldName = () => {
    return (r.fieldNameAr as string) || (r.fieldName as string) || "";
  };

  const getSections = () => {
    return (r.sections as string[]) || [];
  };

  const getLanguage = () => {
    return (r.language as string) || "ar";
  };

  const handlePreviousPage = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1));
  };

  const handleDownload = async () => {
    try {
      await downloadMutation.mutateAsync(reportId);
    } catch (error) {
      logger.error("Failed to download report:", error);
    }
  };

  const handleShare = async (method: ShareMethod) => {
    try {
      if (method === "download") {
        await handleDownload();
        return;
      }

      const shareResult = await shareMutation.mutateAsync({
        reportId,
        method,
      });

      if (method === "link" && shareResult.shareUrl) {
        // Copy to clipboard
        await navigator.clipboard.writeText(shareResult.shareUrl);
        alert("تم نسخ الرابط إلى الحافظة!\nLink copied to clipboard!");
      } else if (method === "email" && shareResult.shareUrl) {
        const emailContent = generateEmailShareContent(
          getReportNameEn(),
          shareResult.shareUrl,
          "ar",
        );
        window.location.href = `mailto:?subject=${encodeURIComponent(emailContent.subject)}&body=${encodeURIComponent(emailContent.body)}`;
      }

      setShowShareMenu(false);
    } catch (error) {
      logger.error("Failed to share report:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">جاري تحميل التقرير...</p>
          <p className="text-sm text-gray-500">Loading report...</p>
        </div>
      </div>
    );
  }

  if (error || !activeReport) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <FileText className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-900 font-medium">فشل في تحميل التقرير</p>
          <p className="text-sm text-gray-500 mt-1">Failed to load report</p>
        </div>
      </div>
    );
  }

  // Show generating status
  if (
    activeReport.status === "generating" ||
    activeReport.status === "pending"
  ) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-900 font-medium">جاري إنشاء التقرير...</p>
          <p className="text-sm text-gray-500 mt-1">
            Generating report... This may take a few moments
          </p>
          <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto">
            <p className="text-sm text-green-800">
              سيتم تحديث الصفحة تلقائياً عند اكتمال التقرير
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show error status
  if (activeReport.status === "failed") {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <FileText className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-900 font-medium">فشل في إنشاء التقرير</p>
          <p className="text-sm text-gray-500 mt-1">Report generation failed</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {getReportName()}
            </h2>
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <FileText className="w-4 h-4" />
                <span>
                  {activeReport.type === "field" ? "تقرير حقل" : "تقرير موسم"}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                <span>{totalPages} صفحة</span>
              </div>
              {activeReport.fileSize && (
                <div>
                  <span>
                    {(activeReport.fileSize / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Download Button */}
            <button
              onClick={handleDownload}
              disabled={downloadMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 transition-colors"
            >
              {downloadMutation.isPending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Download className="w-5 h-5" />
              )}
              <span>تنزيل</span>
            </button>

            {/* Share Button */}
            <div className="relative">
              <button
                onClick={() => setShowShareMenu(!showShareMenu)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <Share2 className="w-5 h-5" />
                <span>مشاركة</span>
              </button>

              {/* Share Menu */}
              {showShareMenu && (
                <div className="absolute left-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-10">
                  <button
                    onClick={() => handleShare("link")}
                    className="w-full px-4 py-2 text-right hover:bg-gray-50 flex items-center gap-2 transition-colors"
                  >
                    <Link2 className="w-4 h-4" />
                    <span>نسخ الرابط</span>
                  </button>
                  <button
                    onClick={() => handleShare("email")}
                    className="w-full px-4 py-2 text-right hover:bg-gray-50 flex items-center gap-2 transition-colors"
                  >
                    <Mail className="w-4 h-4" />
                    <span>إرسال بالبريد</span>
                  </button>
                  <button
                    onClick={() => handleShare("download")}
                    className="w-full px-4 py-2 text-right hover:bg-gray-50 flex items-center gap-2 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>تنزيل PDF</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Preview Panel */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Preview Content */}
        <div className="p-8 min-h-[600px] bg-gray-50">
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
            {/* This is where the actual report content would be rendered */}
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">
                معاينة التقرير - الصفحة {currentPage} من {totalPages}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Report Preview - Page {currentPage} of {totalPages}
              </p>
              <div className="mt-6 text-left">
                <h3 className="font-bold text-lg mb-2">{getReportName()}</h3>
                <p className="text-sm text-gray-600">
                  {getFieldName()} • {activeReport.format.toUpperCase()}
                </p>
                <div className="mt-4 space-y-2">
                  {getSections().map((section) => (
                    <div key={section} className="text-sm text-gray-700">
                      ✓ {section}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        {showNavigation && totalPages > 1 && (
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex items-center justify-between max-w-4xl mx-auto">
              <button
                onClick={handlePreviousPage}
                disabled={currentPage === 1}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
                <span>السابق</span>
              </button>

              <div className="text-sm text-gray-600">
                صفحة {currentPage} من {totalPages}
              </div>

              <button
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span>التالي</span>
                <ChevronLeft className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Report Info */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <span className="font-medium">تاريخ الإنشاء:</span>{" "}
            {new Date(activeReport.createdAt).toLocaleDateString("ar-SA")}
          </div>
          {activeReport.expiresAt && (
            <div>
              <span className="font-medium">تاريخ انتهاء الصلاحية:</span>{" "}
              {new Date(activeReport.expiresAt).toLocaleDateString("ar-SA")}
            </div>
          )}
          <div>
            <span className="font-medium">اللغة:</span>{" "}
            {getLanguage() === "both"
              ? "عربي + English"
              : getLanguage() === "ar"
                ? "عربي"
                : "English"}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportPreview;
