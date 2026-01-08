# Reports Feature - Quick Start Guide

## 🚀 5-Minute Integration

### Step 1: Import Components

```tsx
import {
  ReportGenerator,
  ReportPreview,
  ReportHistory,
} from '@/features/reports';
```

### Step 2: Add to Your Page

```tsx
'use client';

import { useState } from 'react';
import { ReportGenerator, ReportHistory } from '@/features/reports';

export default function FieldReportsPage({ fieldId }: { fieldId: string }) {
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate');

  return (
    <div className="p-8" dir="rtl">
      {/* Tab Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab('generate')}
          className={`px-6 py-3 rounded-lg ${
            activeTab === 'generate' ? 'bg-green-500 text-white' : 'bg-gray-200'
          }`}
        >
          إنشاء تقرير جديد
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-6 py-3 rounded-lg ${
            activeTab === 'history' ? 'bg-green-500 text-white' : 'bg-gray-200'
          }`}
        >
          سجل التقارير
        </button>
      </div>

      {/* Content */}
      {activeTab === 'generate' ? (
        <ReportGenerator
          fieldId={fieldId}
          fieldName="My Field"
          fieldNameAr="حقلي"
          onReportGenerated={(reportId) => {
            console.log('Report generated:', reportId);
            setActiveTab('history');
          }}
        />
      ) : (
        <ReportHistory
          fieldId={fieldId}
          onViewReport={(reportId) => {
            console.log('View report:', reportId);
          }}
          showFilters={true}
        />
      )}
    </div>
  );
}
```

### Step 3: That's It! 🎉

Your reports feature is now working with:
- ✅ Report generation UI
- ✅ Field/Season report types
- ✅ Arabic/English/Both language options
- ✅ PDF/Excel/CSV export formats
- ✅ Report history with search & filters
- ✅ Download & share functionality
- ✅ Full RTL support

## 📱 Common Use Cases

### Use Case 1: Simple Report Button

```tsx
import { useGenerateFieldReport } from '@/features/reports';

function FieldCard({ fieldId }: { fieldId: string }) {
  const generateReport = useGenerateFieldReport();

  const handleGenerateReport = async () => {
    const report = await generateReport.mutateAsync({
      fieldId,
      sections: ['field_info', 'ndvi_trend', 'recommendations'],
      options: {
        format: 'pdf',
        language: 'both',
        includeCharts: true,
      },
    });

    // Report is generating, show the ID
    alert(`تم إنشاء التقرير: ${report.id}`);
  };

  return (
    <button
      onClick={handleGenerateReport}
      disabled={generateReport.isPending}
      className="px-4 py-2 bg-green-500 text-white rounded-lg"
    >
      {generateReport.isPending ? 'جاري الإنشاء...' : 'إنشاء تقرير'}
    </button>
  );
}
```

### Use Case 2: Modal with Report Generator

```tsx
import { useState } from 'react';
import { ReportGenerator } from '@/features/reports';

function FieldPage({ fieldId }: { fieldId: string }) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <button onClick={() => setShowModal(true)}>
        إنشاء تقرير
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">إنشاء تقرير جديد</h2>
              <button onClick={() => setShowModal(false)}>✕</button>
            </div>
            <ReportGenerator
              fieldId={fieldId}
              onReportGenerated={(reportId) => {
                setShowModal(false);
                // Navigate to report preview
              }}
            />
          </div>
        </div>
      )}
    </>
  );
}
```

### Use Case 3: Standalone Preview Page

```tsx
import { ReportPreview } from '@/features/reports';

export default function ReportPage({ params }: { params: { id: string } }) {
  return (
    <div className="container mx-auto py-8">
      <ReportPreview reportId={params.id} showNavigation={true} />
    </div>
  );
}
```

### Use Case 4: Dashboard Widget

```tsx
import { useReportHistory } from '@/features/reports';
import { FileText } from 'lucide-react';

function RecentReportsWidget() {
  const { data: reports, isLoading } = useReportHistory({
    status: 'ready',
  });

  if (isLoading) return <div>Loading...</div>;

  const recentReports = reports?.slice(0, 5) || [];

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-bold mb-4">التقارير الأخيرة</h3>
      <div className="space-y-3">
        {recentReports.map((report) => (
          <div
            key={report.id}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-green-500" />
              <div>
                <div className="font-medium">{report.titleAr}</div>
                <div className="text-sm text-gray-600">
                  {new Date(report.createdAt).toLocaleDateString('ar-SA')}
                </div>
              </div>
            </div>
            <button className="text-green-500 hover:text-green-600">
              عرض
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 🎨 Customization

### Custom Report Sections

```tsx
<ReportGenerator
  fieldId={fieldId}
  // ... other props
/>
```

The user can select from these sections:
- `field_info` - Field information (required)
- `ndvi_trend` - NDVI analysis
- `health_zones` - Health zones map
- `tasks_summary` - Recent tasks
- `weather_summary` - Weather data
- `recommendations` - AI recommendations
- `crop_stages` - Growth stages (season reports)
- `yield_estimate` - Yield prediction (season reports)
- `cost_analysis` - Cost breakdown (season reports)

### Custom Filters

```tsx
<ReportHistory
  fieldId={fieldId}
  // Pre-filter to specific type
  filters={{ type: 'field', status: 'ready' }}
  showFilters={false}
  compact={true}
/>
```

## 🔧 Hooks API

### Generate Reports

```tsx
const generate = useGenerateFieldReport();

generate.mutate({
  fieldId: 'field-123',
  sections: ['field_info', 'ndvi_trend'],
  options: {
    format: 'pdf',
    language: 'both',
    includeCharts: true,
    includeMaps: true,
  },
});
```

### Get Report History

```tsx
const { data, isLoading, error } = useReportHistory({
  fieldId: 'field-123',
  type: 'field',
  status: 'ready',
  search: 'query',
});
```

### Download Report

```tsx
const download = useDownloadReport();

download.mutate(reportId); // Opens in new tab
```

### Share Report

```tsx
const share = useShareReport();

const result = await share.mutateAsync({
  reportId: 'report-123',
  method: 'link', // 'link' | 'email' | 'whatsapp'
});

console.log(result.shareUrl); // Copy this URL
```

### Delete Report

```tsx
const deleteReport = useDeleteFieldReport();

deleteReport.mutate(reportId);
```

## 🌐 Language Support

All components support three language modes:

```tsx
language="ar"    // Arabic only
language="en"    // English only
language="both"  // Bilingual (default)
```

RTL is automatically applied for Arabic mode.

## 📦 What's Included

- ✅ React components (4 components)
- ✅ React Query hooks (10+ hooks)
- ✅ TypeScript types (30+ types)
- ✅ API client (11 endpoints)
- ✅ PDF utilities (15+ functions)
- ✅ Arabic RTL support
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling
- ✅ Mock data for development

## 🐛 Troubleshooting

### Reports not generating?

Check if `NEXT_PUBLIC_API_URL` is set in your `.env`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### Download not working?

The download feature opens a new tab. Check browser popup settings.

### RTL not working?

Make sure the parent container has `dir="rtl"`:
```tsx
<div dir="rtl">
  <ReportGenerator ... />
</div>
```

## 📞 Support

For issues or questions:
1. Check the full [README.md](./README.md)
2. Review the [examples](./examples/ReportsPageExample.tsx)
3. See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for details

## 🎯 Next Steps

1. ✅ Use the components in your pages
2. ✅ Customize the sections and options
3. ✅ Integrate with your backend API
4. ⏭️ Add chart rendering
5. ⏭️ Add map visualization
6. ⏭️ Implement email delivery

Happy reporting! 🎉
