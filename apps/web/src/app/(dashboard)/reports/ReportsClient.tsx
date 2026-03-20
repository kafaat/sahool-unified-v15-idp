"use client";

import React, { useState } from "react";
import {
  FileBarChart, Download, TrendingUp, Droplets,
  Sprout, DollarSign, BarChart3, PieChart, Loader2, AlertTriangle,
} from "lucide-react";
import { useReports, useGenerateReport } from "@/features/reports";
import type { Report } from "@/features/reports";
import { useToast } from "@/components/ui/toast";

type ReportCardType = "yield" | "irrigation" | "financial" | "crop-health" | "inventory" | "weather";
type ReportPeriod = "weekly" | "monthly" | "quarterly" | "annual";

interface ReportCard {
  type: ReportCardType;
  apiType: string;
  titleAr: string;
  title: string;
  descriptionAr: string;
  icon: React.ElementType;
  iconColor: string;
  bgColor: string;
}

const reportCards: ReportCard[] = [
  {
    type: "yield",
    apiType: "yield_analysis",
    titleAr: "تقرير الإنتاجية",
    title: "Yield Report",
    descriptionAr: "تحليل شامل لإنتاجية المحاصيل والمقارنة بالمواسم السابقة",
    icon: TrendingUp,
    iconColor: "text-green-600",
    bgColor: "bg-green-100",
  },
  {
    type: "irrigation",
    apiType: "irrigation",
    titleAr: "تقرير الري",
    title: "Irrigation Report",
    descriptionAr: "استهلاك المياه وكفاءة الري وتوصيات التحسين",
    icon: Droplets,
    iconColor: "text-blue-600",
    bgColor: "bg-blue-100",
  },
  {
    type: "financial",
    apiType: "financial",
    titleAr: "التقرير المالي",
    title: "Financial Report",
    descriptionAr: "الإيرادات والمصروفات والعائد على الاستثمار لكل موسم",
    icon: DollarSign,
    iconColor: "text-purple-600",
    bgColor: "bg-purple-100",
  },
  {
    type: "crop-health",
    apiType: "ndvi_summary",
    titleAr: "تقرير صحة المحاصيل",
    title: "Crop Health Report",
    descriptionAr: "مؤشرات NDVI وتحليل الأمراض وحالة النمو",
    icon: Sprout,
    iconColor: "text-sahool-green-600",
    bgColor: "bg-sahool-green-100",
  },
  {
    type: "inventory",
    apiType: "custom",
    titleAr: "تقرير المخزون",
    title: "Inventory Report",
    descriptionAr: "حركة المخزون والاستهلاك والتنبيهات",
    icon: BarChart3,
    iconColor: "text-orange-600",
    bgColor: "bg-orange-100",
  },
  {
    type: "weather",
    apiType: "weather",
    titleAr: "تقرير الطقس",
    title: "Weather Report",
    descriptionAr: "تحليل بيانات الطقس وتأثيرها على المحاصيل",
    icon: PieChart,
    iconColor: "text-cyan-600",
    bgColor: "bg-cyan-100",
  },
];

const periodMap: Record<ReportPeriod, string> = {
  weekly: "weekly",
  monthly: "monthly",
  quarterly: "quarterly",
  annual: "yearly",
};

const periodOptions: Array<{ value: ReportPeriod; labelAr: string }> = [
  { value: "weekly", labelAr: "أسبوعي" },
  { value: "monthly", labelAr: "شهري" },
  { value: "quarterly", labelAr: "ربع سنوي" },
  { value: "annual", labelAr: "سنوي" },
];

export default function ReportsClient() {
  const [selectedPeriod, setSelectedPeriod] = useState<ReportPeriod>("monthly");
  const { data: reports = [], isLoading, error } = useReports();
  const generateReport = useGenerateReport();
  const { showToast } = useToast();

  const handleGenerate = async (card: ReportCard) => {
    try {
      await generateReport.mutateAsync({
        type: card.apiType as Report["type"],
        format: "pdf",
        period: periodMap[selectedPeriod] as Report["period"],
      });
      showToast({ type: "success", message: "Report generation started", messageAr: "بدأ إنشاء التقرير" });
    } catch {
      showToast({ type: "error", message: "Failed to generate report", messageAr: "فشل في إنشاء التقرير" });
    }
  };

  const handleDownload = (report: Report) => {
    if (report.downloadUrl) {
      window.open(report.downloadUrl, "_blank");
    } else {
      showToast({ type: "info", message: "Download URL not available yet", messageAr: "رابط التحميل غير متاح بعد" });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل التقارير</p>
          <p className="text-gray-500 text-sm">Failed to load reports</p>
        </div>
      </div>
    );
  }

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
              <option key={p.value} value={p.value}>{p.labelAr}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Report Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reportCards.map((card) => {
          const Icon = card.icon;
          const isGenerating = generateReport.isPending;
          return (
            <div key={card.type} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4 mb-4">
                <div className={`w-12 h-12 ${card.bgColor} rounded-lg flex items-center justify-center`}>
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
                    ? "bg-gray-100 text-gray-400 cursor-wait"
                    : "bg-sahool-green-50 text-sahool-green-700 hover:bg-sahool-green-100"
                }`}
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
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
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">التقرير</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">النوع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">التاريخ</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحجم</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">إجراء</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reports.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                      لا توجد تقارير بعد
                    </td>
                  </tr>
                ) : (
                  reports.map((report: Report) => (
                    <tr key={report.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <FileBarChart className="w-5 h-5 text-gray-400" />
                          <span className="font-medium text-gray-900">{report.nameAr || report.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {reportCards.find((c) => c.apiType === report.type)?.titleAr ?? report.type}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(report.createdAt).toLocaleDateString("ar-SA")}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {report.fileSize ? `${(report.fileSize / (1024 * 1024)).toFixed(1)} MB` : "—"}
                      </td>
                      <td className="px-4 py-3">
                        {report.status === "ready" ? (
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            جاهز
                          </span>
                        ) : report.status === "generating" || report.status === "pending" ? (
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            قيد الإنشاء
                          </span>
                        ) : (
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            فشل
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {report.status === "ready" ? (
                          <button
                            onClick={() => handleDownload(report)}
                            className="inline-flex items-center gap-1 text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                          >
                            <Download className="w-4 h-4" />
                            تحميل
                          </button>
                        ) : report.status === "generating" || report.status === "pending" ? (
                          <span className="text-xs text-gray-400 flex items-center gap-1">
                            <Loader2 className="w-3 h-3 animate-spin" />
                            انتظر...
                          </span>
                        ) : (
                          <span className="text-xs text-red-400">خطأ</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
