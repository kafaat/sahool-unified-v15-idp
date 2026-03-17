/**
 * Export Utilities
 * أدوات التصدير - PDF, Excel, CSV
 */

export type ExportFormat = "csv" | "excel" | "pdf";

export interface ExportColumn {
  key: string;
  header: string;
  headerAr?: string;
  width?: number;
  format?: (value: unknown) => string;
}

export interface ExportOptions {
  filename: string;
  title?: string;
  titleAr?: string;
  columns: ExportColumn[];
  data: Record<string, unknown>[];
  format: ExportFormat;
  // PDF specific options
  orientation?: "portrait" | "landscape";
  pageSize?: "A4" | "A3" | "Letter";
  // Additional metadata
  createdBy?: string;
  createdAt?: Date;
  includeHeader?: boolean;
  includeFooter?: boolean;
  footerText?: string;
  footerTextAr?: string;
}

/**
 * Export data to CSV format
 */
export function exportToCSV(options: Omit<ExportOptions, "format">): void {
  const { filename, columns, data, includeHeader = true } = options;

  const rows: string[][] = [];

  // Add header row
  if (includeHeader) {
    rows.push(columns.map((col) => col.headerAr || col.header));
  }

  // Add data rows
  data.forEach((item) => {
    const row = columns.map((col) => {
      const value = item[col.key];
      if (col.format) {
        return col.format(value);
      }
      if (value === null || value === undefined) {
        return "";
      }
      if (typeof value === "object") {
        return JSON.stringify(value);
      }
      return String(value);
    });
    rows.push(row);
  });

  // Convert to CSV string with proper escaping
  const csvContent = rows
    .map((row) =>
      row
        .map((cell) => {
          // Escape quotes and wrap in quotes if contains comma, newline, or quote
          if (cell.includes(",") || cell.includes("\n") || cell.includes('"')) {
            return `"${cell.replace(/"/g, '""')}"`;
          }
          return cell;
        })
        .join(",")
    )
    .join("\n");

  // Add BOM for proper Arabic character display
  const bom = "\uFEFF";
  const blob = new Blob([bom + csvContent], { type: "text/csv;charset=utf-8" });

  downloadBlob(blob, `${filename}.csv`);
}

/**
 * Export data to Excel format (simplified XLSX)
 * Uses simple XML-based format for compatibility
 */
export function exportToExcel(options: Omit<ExportOptions, "format">): void {
  const {
    filename,
    title,
    titleAr,
    columns,
    data,
    includeHeader = true,
  } = options;

  // Create Excel XML
  let excelContent = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
  xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">
    <Title>${escapeXml(titleAr || title || filename)}</Title>
    <Created>${new Date().toISOString()}</Created>
  </DocumentProperties>
  <Styles>
    <Style ss:ID="Default">
      <Font ss:FontName="Tajawal" ss:Size="11"/>
      <Alignment ss:Horizontal="Right" ss:Vertical="Center" ss:ReadingOrder="RightToLeft"/>
    </Style>
    <Style ss:ID="Header">
      <Font ss:FontName="Tajawal" ss:Size="12" ss:Bold="1"/>
      <Interior ss:Color="#10B981" ss:Pattern="Solid"/>
      <Font ss:Color="#FFFFFF"/>
      <Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:ReadingOrder="RightToLeft"/>
    </Style>
    <Style ss:ID="Title">
      <Font ss:FontName="Tajawal" ss:Size="16" ss:Bold="1"/>
      <Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:ReadingOrder="RightToLeft"/>
    </Style>
    <Style ss:ID="Alt">
      <Interior ss:Color="#F3F4F6" ss:Pattern="Solid"/>
      <Font ss:FontName="Tajawal" ss:Size="11"/>
      <Alignment ss:Horizontal="Right" ss:Vertical="Center" ss:ReadingOrder="RightToLeft"/>
    </Style>
  </Styles>
  <Worksheet ss:Name="${escapeXml(titleAr || title || "Data")}">
    <Table>`;

  // Add column widths
  columns.forEach((col) => {
    excelContent += `\n      <Column ss:Width="${col.width || 100}"/>`;
  });

  // Add title row if provided
  if (title || titleAr) {
    excelContent += `\n      <Row ss:Height="30">
        <Cell ss:StyleID="Title" ss:MergeAcross="${columns.length - 1}">
          <Data ss:Type="String">${escapeXml(titleAr || title || "")}</Data>
        </Cell>
      </Row>`;
  }

  // Add header row
  if (includeHeader) {
    excelContent += `\n      <Row>`;
    columns.forEach((col) => {
      excelContent += `\n        <Cell ss:StyleID="Header">
          <Data ss:Type="String">${escapeXml(col.headerAr || col.header)}</Data>
        </Cell>`;
    });
    excelContent += `\n      </Row>`;
  }

  // Add data rows
  data.forEach((item, index) => {
    const styleId = index % 2 === 1 ? "Alt" : "Default";
    excelContent += `\n      <Row>`;

    columns.forEach((col) => {
      const value = item[col.key];
      const formattedValue = col.format
        ? col.format(value)
        : value?.toString() || "";
      const dataType =
        typeof value === "number" ? "Number" : "String";

      excelContent += `\n        <Cell ss:StyleID="${styleId}">
          <Data ss:Type="${dataType}">${escapeXml(formattedValue)}</Data>
        </Cell>`;
    });

    excelContent += `\n      </Row>`;
  });

  excelContent += `\n    </Table>
  </Worksheet>
</Workbook>`;

  const blob = new Blob([excelContent], {
    type: "application/vnd.ms-excel;charset=utf-8",
  });

  downloadBlob(blob, `${filename}.xls`);
}

/**
 * Export data to PDF format
 * Creates a simple HTML-based PDF using print
 */
export function exportToPDF(options: Omit<ExportOptions, "format">): void {
  const {
    title,
    titleAr,
    columns,
    data,
    orientation = "portrait",
    footerText,
    footerTextAr,
  } = options;

  // Create print-friendly HTML
  const htmlContent = `
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>${escapeXml(titleAr || title || "Export")}</title>
  <style>
    /* Tajawal font - self-hosted, no CDN dependency */
    @font-face {
      font-family: 'Tajawal';
      font-style: normal;
      font-weight: 400;
      src: url('/fonts/Tajawal-Regular.woff2') format('woff2');
    }
    @font-face {
      font-family: 'Tajawal';
      font-style: normal;
      font-weight: 500;
      src: url('/fonts/Tajawal-Medium.woff2') format('woff2');
    }
    @font-face {
      font-family: 'Tajawal';
      font-style: normal;
      font-weight: 700;
      src: url('/fonts/Tajawal-Bold.woff2') format('woff2');
    }
    @page {
      size: A4 ${orientation};
      margin: 2cm;
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: 'Tajawal', Arial, sans-serif;
      font-size: 12px;
      line-height: 1.5;
      color: #1f2937;
      direction: rtl;
      margin: 0;
      padding: 20px;
    }

    .header {
      text-align: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 2px solid #10b981;
    }

    .header h1 {
      font-size: 24px;
      font-weight: 700;
      color: #10b981;
      margin: 0 0 10px 0;
    }

    .header .date {
      font-size: 12px;
      color: #6b7280;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 30px;
    }

    th {
      background-color: #10b981;
      color: white;
      font-weight: 700;
      text-align: right;
      padding: 12px 8px;
      font-size: 11px;
    }

    td {
      padding: 10px 8px;
      border-bottom: 1px solid #e5e7eb;
      text-align: right;
    }

    tr:nth-child(even) {
      background-color: #f9fafb;
    }

    tr:hover {
      background-color: #f3f4f6;
    }

    .footer {
      text-align: center;
      font-size: 10px;
      color: #9ca3af;
      padding-top: 20px;
      border-top: 1px solid #e5e7eb;
    }

    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      margin-bottom: 10px;
    }

    .logo-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 20px;
    }

    @media print {
      body {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">
      <div class="logo-icon">س</div>
      <span style="font-size: 24px; font-weight: bold; color: #10b981;">سهول</span>
    </div>
    <h1>${escapeXml(titleAr || title || "تقرير البيانات")}</h1>
    <div class="date">تاريخ التصدير: ${new Date().toLocaleDateString("ar-YE", { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" })}</div>
  </div>

  <table>
    <thead>
      <tr>
        ${columns.map((col) => `<th>${col.headerAr || col.header}</th>`).join("")}
      </tr>
    </thead>
    <tbody>
      ${data
        .map(
          (item) => `
        <tr>
          ${columns
            .map((col) => {
              const value = item[col.key];
              const formattedValue = col.format
                ? col.format(value)
                : value?.toString() || "-";
              return `<td>${escapeHtml(formattedValue)}</td>`;
            })
            .join("")}
        </tr>
      `
        )
        .join("")}
    </tbody>
  </table>

  <div class="footer">
    <p>${footerTextAr || footerText || "تم إنشاء هذا التقرير بواسطة منصة سهول الزراعية"}</p>
    <p>SAHOOL Agricultural Platform - ${new Date().getFullYear()}</p>
  </div>
</body>
</html>
  `;

  // Open print dialog
  const printWindow = window.open("", "_blank");
  if (printWindow) {
    printWindow.document.write(htmlContent);
    printWindow.document.close();

    // Wait for fonts to load then print
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print();
      }, 500);
    };
  }
}

/**
 * Main export function that handles all formats
 */
export function exportData(options: ExportOptions): void {
  const { format, ...rest } = options;

  switch (format) {
    case "csv":
      exportToCSV(rest);
      break;
    case "excel":
      exportToExcel(rest);
      break;
    case "pdf":
      exportToPDF(rest);
      break;
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

// Helper functions
function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Export format labels
export const exportFormatLabels = {
  csv: { en: "CSV", ar: "CSV" },
  excel: { en: "Excel", ar: "Excel" },
  pdf: { en: "PDF", ar: "PDF" },
};
