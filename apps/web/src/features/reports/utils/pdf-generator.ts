/**
 * PDF Generation Utilities
 * أدوات إنشاء ملفات PDF
 *
 * Note: This provides utilities for PDF generation.
 * For actual PDF rendering, consider adding @react-pdf/renderer or jspdf to package.json
 */

import type {
  PDFGenerationOptions,
  PDFChartConfig,
  FieldReportData,
  SeasonReportData,
  ReportSection,
} from "../types/reports";

// ═══════════════════════════════════════════════════════════════════════════
// Default PDF Options
// ═══════════════════════════════════════════════════════════════════════════

export const DEFAULT_PDF_OPTIONS: PDFGenerationOptions = {
  language: "both",
  includeCharts: true,
  includeMaps: true,
  pageSize: "A4",
  orientation: "portrait",
  margins: {
    top: 40,
    bottom: 40,
    left: 40,
    right: 40,
  },
  footer: {
    includePageNumbers: true,
    includeDate: true,
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Arabic Text Support
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if text contains Arabic characters
 * التحقق من احتواء النص على أحرف عربية
 */
export function containsArabic(text: string): boolean {
  const arabicPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/;
  return arabicPattern.test(text);
}

/**
 * Format text for RTL display in PDF
 * تنسيق النص للعرض من اليمين إلى اليسار في PDF
 */
export function formatRTLText(text: string): string {
  if (containsArabic(text)) {
    // Reverse the text order for proper RTL rendering
    // Note: For production, use a proper RTL library like 'rtl-detect'
    return text;
  }
  return text;
}

/**
 * Get text direction based on content
 * الحصول على اتجاه النص بناءً على المحتوى
 */
export function getTextDirection(text: string): "ltr" | "rtl" {
  return containsArabic(text) ? "rtl" : "ltr";
}

// ═══════════════════════════════════════════════════════════════════════════
// Chart Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Convert chart data to base64 image for PDF embedding
 * تحويل بيانات الرسم البياني إلى صورة base64 للتضمين في PDF
 */
export async function chartToBase64(
  chartElement: HTMLCanvasElement | HTMLElement,
  format: "png" | "jpeg" = "png",
): Promise<string> {
  try {
    if (chartElement instanceof HTMLCanvasElement) {
      return chartElement.toDataURL(`image/${format}`);
    }

    // For non-canvas elements, use html2canvas if available
    // Note: Add html2canvas to package.json for this functionality
    if (typeof window !== "undefined" && (window as any).html2canvas) {
      const canvas = await (window as any).html2canvas(chartElement);
      return canvas.toDataURL(`image/${format}`);
    }

    throw new Error("Chart conversion not supported for this element type");
  } catch (error) {
    console.error("Failed to convert chart to base64:", error);
    return "";
  }
}

/**
 * Generate chart configuration for PDF
 * إنشاء إعدادات الرسم البياني لـ PDF
 */
export function generateChartConfig(
  type: PDFChartConfig["type"],
  labels: string[],
  data: number[],
  label: string,
  options?: PDFChartConfig["options"],
): PDFChartConfig {
  const colors = {
    green: "#22c55e",
    blue: "#3b82f6",
    yellow: "#eab308",
    red: "#ef4444",
    gray: "#6b7280",
  };

  return {
    type,
    data: {
      labels,
      datasets: [
        {
          label,
          data,
          backgroundColor:
            type === "pie"
              ? [
                  colors.green,
                  colors.blue,
                  colors.yellow,
                  colors.red,
                  colors.gray,
                ]
              : colors.green,
          borderColor: colors.green,
        },
      ],
    },
    options: {
      width: 800,
      height: 400,
      ...options,
    },
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Data Formatting Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Format date for PDF display
 * تنسيق التاريخ للعرض في PDF
 */
export function formatDateForPDF(
  date: string | Date,
  language: "ar" | "en" = "en",
): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;

  if (language === "ar") {
    return dateObj.toLocaleDateString("ar-SA", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  return dateObj.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Format number with locale
 * تنسيق الرقم مع اللغة
 */
export function formatNumberForPDF(
  num: number,
  language: "ar" | "en" = "en",
  decimals = 2,
): string {
  const locale = language === "ar" ? "ar-SA" : "en-US";
  return num.toLocaleString(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format currency for PDF
 * تنسيق العملة للعرض في PDF
 */
export function formatCurrencyForPDF(
  amount: number,
  currency = "SAR",
  language: "ar" | "en" = "en",
): string {
  const locale = language === "ar" ? "ar-SA" : "en-US";
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(amount);
}

/**
 * Format area measurement
 * تنسيق قياس المساحة
 */
export function formatArea(
  area: number,
  unit: "hectare" | "acre" | "sqm" = "hectare",
  language: "ar" | "en" = "en",
): string {
  const unitLabels = {
    hectare: { en: "ha", ar: "هكتار" },
    acre: { en: "acre", ar: "فدان" },
    sqm: { en: "m²", ar: "م²" },
  };

  const formattedNumber = formatNumberForPDF(area, language);
  return `${formattedNumber} ${unitLabels[unit][language]}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Section Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get section title in specified language
 * الحصول على عنوان القسم باللغة المحددة
 */
export function getSectionTitle(
  section: ReportSection,
  language: "ar" | "en",
): string {
  const titles: Record<ReportSection, { en: string; ar: string }> = {
    field_info: { en: "Field Information", ar: "معلومات الحقل" },
    ndvi_trend: { en: "NDVI Trend Analysis", ar: "تحليل اتجاه NDVI" },
    health_zones: { en: "Health Zones Map", ar: "خريطة مناطق الصحة" },
    tasks_summary: { en: "Tasks Summary", ar: "ملخص المهام" },
    weather_summary: { en: "Weather Summary", ar: "ملخص الطقس" },
    recommendations: { en: "Recommendations", ar: "التوصيات" },
    crop_stages: { en: "Crop Growth Stages", ar: "مراحل نمو المحصول" },
    yield_estimate: { en: "Yield Estimate", ar: "تقدير المحصول" },
    input_summary: { en: "Input Summary", ar: "ملخص المدخلات" },
    cost_analysis: { en: "Cost Analysis", ar: "تحليل التكاليف" },
    pest_disease: { en: "Pest & Disease Report", ar: "تقرير الآفات والأمراض" },
    soil_analysis: { en: "Soil Analysis", ar: "تحليل التربة" },
  };

  return titles[section][language];
}

/**
 * Order sections for PDF generation
 * ترتيب الأقسام لإنشاء PDF
 */
export function orderSections(
  sections: ReportSection[],
  type: "field" | "season",
): ReportSection[] {
  const fieldOrder: ReportSection[] = [
    "field_info",
    "ndvi_trend",
    "health_zones",
    "soil_analysis",
    "weather_summary",
    "tasks_summary",
    "pest_disease",
    "recommendations",
  ];

  const seasonOrder: ReportSection[] = [
    "field_info",
    "crop_stages",
    "ndvi_trend",
    "yield_estimate",
    "input_summary",
    "cost_analysis",
    "recommendations",
  ];

  const orderArray = type === "field" ? fieldOrder : seasonOrder;

  return sections.sort((a, b) => {
    const indexA = orderArray.indexOf(a);
    const indexB = orderArray.indexOf(b);
    return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// HTML to PDF Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generate HTML template for field report
 * إنشاء قالب HTML لتقرير الحقل
 */
export function generateFieldReportHTML(
  data: FieldReportData,
  sections: ReportSection[],
  language: "ar" | "en" | "both",
): string {
  const orderedSections = orderSections(sections, "field");
  const isRTL = language === "ar";
  const dir = isRTL ? "rtl" : "ltr";

  let html = `
    <!DOCTYPE html>
    <html dir="${dir}" lang="${language === "ar" ? "ar" : "en"}">
    <head>
      <meta charset="UTF-8">
      <style>
        body {
          font-family: ${isRTL ? "'Tajawal', 'Noto Sans Arabic'" : "'Inter', 'Arial'"}, sans-serif;
          direction: ${dir};
          padding: 40px;
          color: #1f2937;
        }
        .header {
          text-align: center;
          border-bottom: 3px solid #22c55e;
          padding-bottom: 20px;
          margin-bottom: 30px;
        }
        .section {
          margin-bottom: 30px;
          page-break-inside: avoid;
        }
        .section-title {
          font-size: 20px;
          font-weight: bold;
          color: #22c55e;
          margin-bottom: 15px;
          border-bottom: 2px solid #e5e7eb;
          padding-bottom: 10px;
        }
        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
        }
        .info-item {
          padding: 10px;
          background: #f9fafb;
          border-radius: 8px;
        }
        .info-label {
          font-weight: bold;
          color: #6b7280;
          font-size: 14px;
        }
        .info-value {
          font-size: 16px;
          margin-top: 5px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 15px;
        }
        th, td {
          padding: 12px;
          text-align: ${isRTL ? "right" : "left"};
          border-bottom: 1px solid #e5e7eb;
        }
        th {
          background: #f3f4f6;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>${isRTL ? data.field.nameAr : data.field.name}</h1>
        <p>${isRTL ? "تقرير أداء الحقل" : "Field Performance Report"}</p>
      </div>
  `;

  // Add sections based on selected sections
  orderedSections.forEach((section) => {
    const title = getSectionTitle(section, language === "ar" ? "ar" : "en");
    html += `<div class="section"><h2 class="section-title">${title}</h2>`;

    // Add section-specific content
    // This is a simplified version - expand based on actual data structure
    html += `<p>Section content for ${section}</p>`;

    html += `</div>`;
  });

  html += `
    </body>
    </html>
  `;

  return html;
}

/**
 * Generate HTML template for season report
 * إنشاء قالب HTML لتقرير الموسم
 */
export function generateSeasonReportHTML(
  data: SeasonReportData,
  sections: ReportSection[],
  language: "ar" | "en" | "both",
): string {
  const orderedSections = orderSections(sections, "season");
  const isRTL = language === "ar";
  const dir = isRTL ? "rtl" : "ltr";

  let html = `
    <!DOCTYPE html>
    <html dir="${dir}" lang="${language === "ar" ? "ar" : "en"}">
    <head>
      <meta charset="UTF-8">
      <style>
        /* Similar styles as field report */
        body {
          font-family: ${isRTL ? "'Tajawal', 'Noto Sans Arabic'" : "'Inter', 'Arial'"}, sans-serif;
          direction: ${dir};
          padding: 40px;
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>${isRTL ? data.season.nameAr : data.season.name}</h1>
        <p>${isRTL ? "تقرير ملخص الموسم" : "Season Summary Report"}</p>
      </div>
  `;

  orderedSections.forEach((section) => {
    const title = getSectionTitle(section, language === "ar" ? "ar" : "en");
    html += `<div class="section"><h2 class="section-title">${title}</h2>`;
    html += `<p>Section content for ${section}</p>`;
    html += `</div>`;
  });

  html += `</body></html>`;
  return html;
}

// ═══════════════════════════════════════════════════════════════════════════
// Export Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Download PDF blob
 * تنزيل ملف PDF
 */
export function downloadPDF(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename.endsWith(".pdf") ? filename : `${filename}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Generate share link for report
 * إنشاء رابط مشاركة للتقرير
 */
export function generateShareLink(reportId: string, baseUrl?: string): string {
  const base =
    baseUrl ||
    (typeof window !== "undefined"
      ? window.location.origin
      : "https://sahool.app");
  return `${base}/reports/shared/${reportId}`;
}

/**
 * Generate email share content
 * إنشاء محتوى مشاركة البريد الإلكتروني
 */
export function generateEmailShareContent(
  reportTitle: string,
  shareLink: string,
  language: "ar" | "en",
): { subject: string; body: string } {
  if (language === "ar") {
    return {
      subject: `تقرير SAHOOL: ${reportTitle}`,
      body: `مرحباً،\n\nيسعدني مشاركة تقرير SAHOOL معك:\n${reportTitle}\n\nيمكنك عرض التقرير على الرابط التالي:\n${shareLink}\n\nمع تحياتي،\nمنصة SAHOOL الزراعية`,
    };
  }

  return {
    subject: `SAHOOL Report: ${reportTitle}`,
    body: `Hello,\n\nI'd like to share a SAHOOL report with you:\n${reportTitle}\n\nYou can view the report at:\n${shareLink}\n\nBest regards,\nSAHOOL Agricultural Platform`,
  };
}

export default {
  DEFAULT_PDF_OPTIONS,
  containsArabic,
  formatRTLText,
  getTextDirection,
  chartToBase64,
  generateChartConfig,
  formatDateForPDF,
  formatNumberForPDF,
  formatCurrencyForPDF,
  formatArea,
  getSectionTitle,
  orderSections,
  generateFieldReportHTML,
  generateSeasonReportHTML,
  downloadPDF,
  generateShareLink,
  generateEmailShareContent,
};
