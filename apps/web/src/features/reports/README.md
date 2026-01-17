# Reports Feature (ميزة التقارير)

A comprehensive report generation system with Arabic RTL support for the SAHOOL agricultural platform.

## Features

- **Field Reports** - Detailed performance analysis for individual fields
- **Season Reports** - Complete seasonal summaries with yield and cost analysis
- **Arabic RTL Support** - Full right-to-left layout support for Arabic PDF generation
- **Multiple Formats** - Export to PDF, Excel, CSV
- **Bilingual** - Support for Arabic, English, or both languages
- **Real-time Status** - Live status updates during report generation
- **History & Management** - View, download, share, and delete past reports

## Directory Structure

```
/apps/web/src/features/reports/
├── api/
│   └── reports-api.ts          # API client for report operations
├── components/
│   ├── ReportGenerator.tsx      # Report configuration & generation UI
│   ├── ReportPreview.tsx        # Report preview with download/share
│   ├── FieldReportTemplate.tsx  # Field report layout template
│   └── ReportHistory.tsx        # Past reports list with filters
├── hooks/
│   └── useReports.ts            # React Query hooks
├── types/
│   └── reports.ts               # TypeScript type definitions
├── utils/
│   └── pdf-generator.ts         # PDF generation utilities
└── index.ts                     # Main exports
```

## Usage Examples

### 1. Generate a Field Report

```tsx
import { ReportGenerator } from "@/features/reports";

function MyFieldPage({ fieldId }) {
  const handleReportGenerated = (reportId: string) => {
    console.log("Report generated:", reportId);
    // Navigate to preview or show success message
  };

  return (
    <ReportGenerator
      fieldId={fieldId}
      fieldName="North Field"
      fieldNameAr="الحقل الشمالي"
      onReportGenerated={handleReportGenerated}
    />
  );
}
```

### 2. View Report History

```tsx
import { ReportHistory } from "@/features/reports";

function MyReportsPage() {
  const handleViewReport = (reportId: string) => {
    // Navigate to report preview
    router.push(`/reports/${reportId}`);
  };

  const handleShareReport = (reportId: string) => {
    // Open share modal
  };

  return (
    <ReportHistory
      onViewReport={handleViewReport}
      onShareReport={handleShareReport}
      showFilters={true}
    />
  );
}
```

### 3. Preview a Report

```tsx
import { ReportPreview } from "@/features/reports";

function ReportPreviewPage({ reportId }) {
  return (
    <div className="container mx-auto py-8">
      <ReportPreview reportId={reportId} showNavigation={true} />
    </div>
  );
}
```

### 4. Custom Report Template

```tsx
import { FieldReportTemplate, useFieldReportData } from "@/features/reports";

function CustomReportView({ fieldId, startDate, endDate }) {
  const { data, isLoading } = useFieldReportData(fieldId, startDate, endDate);

  if (isLoading) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;

  return (
    <FieldReportTemplate
      data={data}
      sections={["field_info", "ndvi_trend", "recommendations"]}
      language="both"
      startDate={startDate}
      endDate={endDate}
      title="Custom Field Report"
      titleAr="تقرير حقل مخصص"
    />
  );
}
```

### 5. Using Hooks Directly

```tsx
import {
  useGenerateFieldReport,
  useReportHistory,
  useDownloadReport,
  useShareReport,
} from "@/features/reports";

function ReportsManager() {
  // Generate a report
  const generateReport = useGenerateFieldReport();

  // Get report history
  const { data: reports } = useReportHistory({
    type: "field",
    status: "ready",
  });

  // Download a report
  const downloadReport = useDownloadReport();

  // Share a report
  const shareReport = useShareReport();

  const handleGenerate = async () => {
    const result = await generateReport.mutateAsync({
      fieldId: "field-123",
      sections: ["field_info", "ndvi_trend", "recommendations"],
      options: {
        format: "pdf",
        language: "both",
        includeCharts: true,
        includeMaps: true,
      },
    });
    console.log("Report ID:", result.id);
  };

  const handleDownload = async (reportId: string) => {
    await downloadReport.mutateAsync(reportId);
  };

  const handleShare = async (reportId: string) => {
    const result = await shareReport.mutateAsync({
      reportId,
      method: "link",
    });
    console.log("Share URL:", result.shareUrl);
  };

  return (
    <div>
      <button onClick={handleGenerate}>Generate Report</button>
      {reports?.map((report) => (
        <div key={report.id}>
          <h3>{report.titleAr}</h3>
          <button onClick={() => handleDownload(report.id)}>Download</button>
          <button onClick={() => handleShare(report.id)}>Share</button>
        </div>
      ))}
    </div>
  );
}
```

## Report Sections

### Field Report Sections

- `field_info` - Basic field information (required)
- `ndvi_trend` - NDVI trend analysis
- `health_zones` - Health zones distribution map
- `tasks_summary` - Recent farming tasks
- `weather_summary` - Weather conditions
- `recommendations` - AI-powered recommendations

### Season Report Sections

- `field_info` - Field and crop information (required)
- `crop_stages` - Growth stages timeline
- `yield_estimate` - Yield predictions
- `input_summary` - Water, fertilizer, pesticides
- `cost_analysis` - Cost breakdown and ROI

## API Endpoints

The feature expects the following backend endpoints:

```
POST   /api/v1/reports/field/generate      - Generate field report
POST   /api/v1/reports/season/generate     - Generate season report
GET    /api/v1/reports/history              - Get report history
GET    /api/v1/reports/{id}                 - Get specific report
GET    /api/v1/reports/{id}/download        - Download report
POST   /api/v1/reports/{id}/share           - Share report
DELETE /api/v1/reports/{id}                 - Delete report
GET    /api/v1/reports/field/data           - Get field report data
GET    /api/v1/reports/season/data          - Get season report data
GET    /api/v1/reports/templates            - Get report templates
GET    /api/v1/reports/{id}/status          - Check generation status
```

## Arabic RTL Support

The feature includes comprehensive RTL support:

- **PDF Generation** - Proper Arabic text rendering with RTL layout
- **UI Components** - All components support `dir="rtl"` for Arabic
- **Bilingual Mode** - Display both Arabic and English side-by-side
- **Date Formatting** - Proper Arabic date formatting
- **Number Formatting** - Arabic numeral formatting
- **Font Support** - Arabic fonts (Tajawal, Noto Sans Arabic)

## Type Definitions

All types are exported from `types/reports.ts`:

```typescript
import type {
  ReportType,
  ReportFormat,
  ReportStatus,
  ReportSection,
  FieldReportData,
  GenerateFieldReportRequest,
  GeneratedReport,
  // ... and more
} from "@/features/reports";
```

## Utilities

PDF generation utilities are available:

```typescript
import {
  formatDateForPDF,
  formatNumberForPDF,
  formatCurrencyForPDF,
  formatArea,
  getSectionTitle,
  generateFieldReportHTML,
  downloadPDF,
  generateShareLink,
} from "@/features/reports";
```

## Development Notes

- Mock data is used in development mode when API calls fail
- Reports auto-refresh during generation (polling every 3-5 seconds)
- Downloads open in new tab for better UX
- Share links are copied to clipboard automatically
- All error messages are bilingual (Arabic/English)

## Dependencies

- **React Query** - Data fetching and caching
- **Lucide React** - Icons
- **Axios** - HTTP client
- **js-cookie** - Cookie management

## Future Enhancements

- [ ] Chart rendering in PDF exports
- [ ] Map embedding in reports
- [ ] Email report delivery
- [ ] WhatsApp sharing integration
- [ ] Scheduled report generation
- [ ] Report templates customization
- [ ] Bulk report generation
- [ ] Report comparison views
