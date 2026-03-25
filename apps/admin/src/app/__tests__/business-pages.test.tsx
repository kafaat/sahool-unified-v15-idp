import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const APP_DIR = path.resolve(__dirname, '..');

// ─── Helper ──────────────────────────────────────────────────────────────────

function readPage(relativePath: string): string {
  const filePath = path.join(APP_DIR, relativePath);
  return fs.readFileSync(filePath, 'utf-8');
}

function hasUseClientDirective(source: string): boolean {
  // Accept both single and double quotes
  return /['"]use client['"]/.test(source);
}

function hasDefaultExport(source: string): boolean {
  return /export\s+default\s+function\s+\w+/.test(source);
}

function hasArabicText(source: string): boolean {
  return /[\u0600-\u06FF]/.test(source);
}

// ─── Crop Health Page ────────────────────────────────────────────────────────

describe('Crop Health Page (crop-health/page.tsx)', () => {
  const pagePath = 'crop-health/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports CropHealthPage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+CropHealthPage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('صحة المحاصيل');
    expect(source).toContain('ممتاز');
    expect(source).toContain('حرج');
    expect(source).toContain('إجمالي الحقول');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('Leaf');
    expect(source).toContain('Search');
    expect(source).toContain('RefreshCw');
    expect(source).toContain('Activity');
    expect(source).toContain('AlertTriangle');
    expect(source).toContain('CheckCircle');
  });

  it('imports Header and DataTable components', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/import\s+Header\s+from/);
    expect(source).toMatch(/import\s+DataTable\s+from/);
  });

  it('has search input', () => {
    const source = readPage(pagePath);
    expect(source).toContain('searchQuery');
    expect(source).toContain('بحث بالمزرعة أو المحصول');
  });

  it('has status filter with options', () => {
    const source = readPage(pagePath);
    expect(source).toContain('statusFilter');
    expect(source).toContain('كل الحالات');
  });

  it('uses DataTable for rendering records', () => {
    const source = readPage(pagePath);
    expect(source).toContain('<DataTable');
    expect(source).toContain('columns={columns}');
    expect(source).toContain('keyExtractor');
  });

  it('has NDVI display column', () => {
    const source = readPage(pagePath);
    expect(source).toContain('NDVI');
    expect(source).toContain('ndvi');
    expect(source).toContain('متوسط NDVI');
  });

  it('has stats summary section', () => {
    const source = readPage(pagePath);
    expect(source).toContain('stats.total');
    expect(source).toContain('stats.excellent');
    expect(source).toContain('stats.issues');
    expect(source).toContain('stats.critical');
    expect(source).toContain('stats.avgNdvi');
  });
});

// ─── Diseases Page ───────────────────────────────────────────────────────────

describe('Diseases Page (diseases/page.tsx)', () => {
  const pagePath = 'diseases/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports DiseasesPage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+DiseasesPage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('إدارة الأمراض');
    expect(source).toContain('إجمالي التشخيصات');
    expect(source).toContain('قيد المراجعة');
    expect(source).toContain('حالات حرجة');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('Bug');
    expect(source).toContain('Search');
    expect(source).toContain('Check');
    expect(source).toContain('Pill');
    expect(source).toContain('MapPin');
    expect(source).toContain('Calendar');
    expect(source).toContain('Loader2');
  });

  it('imports Header, AlertBadge, and StatusBadge components', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/import\s+Header\s+from/);
    expect(source).toMatch(/import\s+AlertBadge\s+from/);
    expect(source).toMatch(/import\s+StatusBadge\s+from/);
  });

  it('imports API functions for data fetching', () => {
    const source = readPage(pagePath);
    expect(source).toContain('fetchDiagnoses');
    expect(source).toContain('updateDiagnosisStatus');
  });

  it('has search input and severity/status filters', () => {
    const source = readPage(pagePath);
    expect(source).toContain('searchQuery');
    expect(source).toContain('severityFilter');
    expect(source).toContain('statusFilter');
    expect(source).toContain('بحث بالمرض أو المزرعة');
  });

  it('has severity filter options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('كل الخطورات');
    expect(source).toContain('منخفض');
    expect(source).toContain('متوسط');
    expect(source).toContain('مرتفع');
  });

  it('has pagination controls', () => {
    const source = readPage(pagePath);
    expect(source).toContain('currentPage');
    expect(source).toContain('totalPages');
    expect(source).toContain('itemsPerPage');
    expect(source).toContain('ChevronLeft');
    expect(source).toContain('ChevronRight');
  });

  it('has a detail modal for diagnosis', () => {
    const source = readPage(pagePath);
    expect(source).toContain('isModalOpen');
    expect(source).toContain('selectedDiagnosis');
    expect(source).toContain('دقة التشخيص');
    expect(source).toContain('توصية العلاج');
  });

  it('wraps content in Suspense', () => {
    const source = readPage(pagePath);
    expect(source).toContain('Suspense');
    expect(source).toContain('DiseasesContent');
  });

  it('has stats summary section', () => {
    const source = readPage(pagePath);
    expect(source).toContain('stats.total');
    expect(source).toContain('stats.pending');
    expect(source).toContain('stats.critical');
    expect(source).toContain('stats.thisWeek');
  });
});

// ─── Marketplace Page ────────────────────────────────────────────────────────

describe('Marketplace Page (marketplace/page.tsx)', () => {
  const pagePath = 'marketplace/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports MarketplacePage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+MarketplacePage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('إدارة السوق');
    expect(source).toContain('إجمالي المنتجات');
    expect(source).toContain('نشط');
    expect(source).toContain('قيد المراجعة');
    expect(source).toContain('إجمالي الطلبات');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('Search');
    expect(source).toContain('Package');
    expect(source).toContain('CheckCircle');
    expect(source).toContain('XCircle');
    expect(source).toContain('TrendingUp');
    expect(source).toContain('Filter');
  });

  it('imports Header and DataTable components', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/import\s+Header\s+from/);
    expect(source).toMatch(/import\s+DataTable\s+from/);
  });

  it('has search input and category/status filters', () => {
    const source = readPage(pagePath);
    expect(source).toContain('searchQuery');
    expect(source).toContain('categoryFilter');
    expect(source).toContain('statusFilter');
    expect(source).toContain('بحث بالاسم أو البائع');
  });

  it('has category filter options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('كل الفئات');
    expect(source).toContain('بذور');
    expect(source).toContain('أسمدة');
    expect(source).toContain('مبيدات');
    expect(source).toContain('معدات');
  });

  it('has product status labels in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('نشط');
    expect(source).toContain('مرفوض');
    expect(source).toContain('نفذ');
  });

  it('uses DataTable for rendering products', () => {
    const source = readPage(pagePath);
    expect(source).toContain('<DataTable');
    expect(source).toContain('columns={columns}');
    expect(source).toContain('filteredProducts');
  });

  it('has stats summary section', () => {
    const source = readPage(pagePath);
    expect(source).toContain('stats.total');
    expect(source).toContain('stats.active');
    expect(source).toContain('stats.pending');
    expect(source).toContain('stats.totalOrders');
  });
});

// ─── Community Page ──────────────────────────────────────────────────────────

describe('Community Page (community/page.tsx)', () => {
  const pagePath = 'community/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports CommunityPage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+CommunityPage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('إدارة المجتمع');
    expect(source).toContain('إجمالي المنشورات');
    expect(source).toContain('مُبلغ عنه');
    expect(source).toContain('قيد المراجعة');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('MessageSquare');
    expect(source).toContain('Search');
    expect(source).toContain('Flag');
    expect(source).toContain('ThumbsUp');
    expect(source).toContain('Trash2');
    expect(source).toContain('AlertTriangle');
  });

  it('imports Header and DataTable components', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/import\s+Header\s+from/);
    expect(source).toMatch(/import\s+DataTable\s+from/);
  });

  it('has search input and category/status filters', () => {
    const source = readPage(pagePath);
    expect(source).toContain('searchQuery');
    expect(source).toContain('categoryFilter');
    expect(source).toContain('statusFilter');
    expect(source).toContain('بحث في المنشورات');
  });

  it('has community category options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('نصائح');
    expect(source).toContain('تعليم');
    expect(source).toContain('أسئلة');
  });

  it('has post status labels in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('نشط');
    expect(source).toContain('مُبلغ عنه');
    expect(source).toContain('مخفي');
  });

  it('uses DataTable for rendering posts', () => {
    const source = readPage(pagePath);
    expect(source).toContain('<DataTable');
    expect(source).toContain('filteredPosts');
  });

  it('has stats summary section', () => {
    const source = readPage(pagePath);
    expect(source).toContain('stats.total');
    expect(source).toContain('stats.active');
    expect(source).toContain('stats.flagged');
    expect(source).toContain('stats.pending');
  });
});

// ─── Compliance Page ─────────────────────────────────────────────────────────

describe('Compliance Page (compliance/page.tsx)', () => {
  const pagePath = 'compliance/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports CompliancePage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+CompliancePage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('تقارير الامتثال');
    expect(source).toContain('إجمالي السجلات');
    expect(source).toContain('متوافق');
    expect(source).toContain('جزئي');
    expect(source).toContain('منتهي');
    expect(source).toContain('متوسط النتيجة');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('Search');
    expect(source).toContain('RefreshCw');
    expect(source).toContain('Download');
    expect(source).toContain('FileText');
    expect(source).toContain('Award');
    expect(source).toContain('Clock');
    expect(source).toContain('CheckCircle');
    expect(source).toContain('AlertTriangle');
  });

  it('imports Header and DataTable components', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/import\s+Header\s+from/);
    expect(source).toMatch(/import\s+DataTable\s+from/);
  });

  it('has search input and standard/status filters', () => {
    const source = readPage(pagePath);
    expect(source).toContain('searchQuery');
    expect(source).toContain('standardFilter');
    expect(source).toContain('statusFilter');
    expect(source).toContain('بحث بالمزرعة');
  });

  it('has compliance standard options', () => {
    const source = readPage(pagePath);
    expect(source).toContain('كل المعايير');
    expect(source).toContain('GlobalGAP');
    expect(source).toContain('عضوي');
    expect(source).toContain('ISO 22000');
    expect(source).toContain('HACCP');
  });

  it('has compliance status labels in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('متوافق');
    expect(source).toContain('غير متوافق');
    expect(source).toContain('قيد التدقيق');
  });

  it('uses DataTable for rendering records', () => {
    const source = readPage(pagePath);
    expect(source).toContain('<DataTable');
    expect(source).toContain('filteredRecords');
  });

  it('has stats summary section', () => {
    const source = readPage(pagePath);
    expect(source).toContain('stats.total');
    expect(source).toContain('stats.compliant');
    expect(source).toContain('stats.partial');
    expect(source).toContain('stats.expired');
    expect(source).toContain('stats.avgScore');
  });
});

// ─── Traceability Page ───────────────────────────────────────────────────────

describe('Traceability Page (traceability/page.tsx)', () => {
  const pagePath = 'traceability/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports TraceabilityPage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+TraceabilityPage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('تتبع المنتجات وسلسلة التوريد');
    expect(source).toContain('إجمالي الدفعات');
    expect(source).toContain('دفعات نشطة');
    expect(source).toContain('تم التسليم');
    expect(source).toContain('سجل الأحداث');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('Package');
    expect(source).toContain('QrCode');
    expect(source).toContain('MapPin');
    expect(source).toContain('Search');
    expect(source).toContain('Truck');
    expect(source).toContain('Warehouse');
    expect(source).toContain('Leaf');
    expect(source).toContain('ShieldCheck');
    expect(source).toContain('Clock');
  });

  it('imports apiClient and API_URLS', () => {
    const source = readPage(pagePath);
    expect(source).toContain('apiClient');
    expect(source).toContain('API_URLS');
    expect(source).toContain('API_PATHS');
  });

  it('has search input and status filter', () => {
    const source = readPage(pagePath);
    expect(source).toContain('searchQuery');
    expect(source).toContain('statusFilter');
    expect(source).toContain('بحث بكود الدفعة أو اسم المنتج أو المزرعة');
  });

  it('has status filter options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('كل الحالات');
    expect(source).toContain('تم الحصاد');
    expect(source).toContain('مُخزّن');
    expect(source).toContain('قيد النقل');
    expect(source).toContain('تم البيع');
  });

  it('defines TraceabilityBatch and TraceabilityEvent types', () => {
    const source = readPage(pagePath);
    expect(source).toContain('interface TraceabilityBatch');
    expect(source).toContain('interface TraceabilityEvent');
    expect(source).toContain('interface TraceabilityStats');
  });

  it('has event timeline panel', () => {
    const source = readPage(pagePath);
    expect(source).toContain('selectedBatchEvents');
    expect(source).toContain('سجل الأحداث');
    expect(source).toContain('اختر دفعة لعرض سجل الأحداث');
  });

  it('has mock data for batches and events', () => {
    const source = readPage(pagePath);
    expect(source).toContain('MOCK_BATCHES');
    expect(source).toContain('MOCK_EVENTS');
    expect(source).toContain('MOCK_STATS');
  });

  it('has quality grade display', () => {
    const source = readPage(pagePath);
    expect(source).toContain('quality_grade');
    expect(source).toContain('getGradeColor');
  });

  it('has stats summary with 6 stat cards', () => {
    const source = readPage(pagePath);
    expect(source).toContain('الكمية الكلية');
    expect(source).toContain('متوسط الجودة');
    expect(source).toContain('نسبة المعتمد');
  });
});

// ─── Audit Page ──────────────────────────────────────────────────────────────

describe('Audit Page (audit/page.tsx)', () => {
  const pagePath = 'audit/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports AuditPage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+AuditPage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('سجل التدقيق');
    expect(source).toContain('إجمالي الأحداث');
    expect(source).toContain('أحداث اليوم');
    expect(source).toContain('أحداث حرجة');
    expect(source).toContain('مستخدمون نشطون');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('Shield');
    expect(source).toContain('FileText');
    expect(source).toContain('AlertTriangle');
    expect(source).toContain('Users');
    expect(source).toContain('ClipboardList');
  });

  it('imports Header component', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/import\s+Header\s+from/);
  });

  it('has stats cards with hardcoded values', () => {
    const source = readPage(pagePath);
    expect(source).toContain('12,847');
    expect(source).toContain('324');
    expect(source).toContain('7');
    expect(source).toContain('48');
  });

  it('has placeholder content section', () => {
    const source = readPage(pagePath);
    expect(source).toContain('سيتم عرض سجل أحداث التدقيق هنا');
  });
});

// ─── Yield Page ──────────────────────────────────────────────────────────────

describe('Yield Page (yield/page.tsx)', () => {
  const pagePath = 'yield/page.tsx';

  it('file exists', () => {
    const fullPath = path.join(APP_DIR, pagePath);
    expect(fs.existsSync(fullPath)).toBe(true);
  });

  it('has "use client" directive', () => {
    const source = readPage(pagePath);
    expect(hasUseClientDirective(source)).toBe(true);
  });

  it('has a default export', () => {
    const source = readPage(pagePath);
    expect(hasDefaultExport(source)).toBe(true);
  });

  it('exports YieldPage', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/export\s+default\s+function\s+YieldPage/);
  });

  it('contains Arabic labels', () => {
    const source = readPage(pagePath);
    expect(hasArabicText(source)).toBe(true);
    expect(source).toContain('حاسبة التنبؤ بالإنتاجية');
    expect(source).toContain('بيانات الحقل');
    expect(source).toContain('نوع المحصول');
    expect(source).toContain('جودة التربة');
    expect(source).toContain('نوع الري');
    expect(source).toContain('احسب الإنتاجية المتوقعة');
  });

  it('imports lucide-react icons', () => {
    const source = readPage(pagePath);
    expect(source).toMatch(/from\s+['"]lucide-react['"]/);
    expect(source).toContain('TrendingUp');
    expect(source).toContain('Loader2');
    expect(source).toContain('DollarSign');
    expect(source).toContain('Scale');
    expect(source).toContain('Droplets');
    expect(source).toContain('Thermometer');
  });

  it('imports apiClient and API_URLS', () => {
    const source = readPage(pagePath);
    expect(source).toContain('apiClient');
    expect(source).toContain('API_URLS');
  });

  it('has crop options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('قمح');
    expect(source).toContain('ذرة');
    expect(source).toContain('طماطم');
    expect(source).toContain('بطاطس');
    expect(source).toContain('بن يمني');
    expect(source).toContain('نخيل (تمر)');
  });

  it('has soil quality options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('ضعيفة');
    expect(source).toContain('متوسطة');
    expect(source).toContain('ممتازة');
  });

  it('has irrigation type options in Arabic', () => {
    const source = readPage(pagePath);
    expect(source).toContain('اعتماد على الأمطار');
    expect(source).toContain('ري غمر');
    expect(source).toContain('ري رشاش');
    expect(source).toContain('ري بالتنقيط');
    expect(source).toContain('ري ذكي');
  });

  it('defines YieldPrediction interface', () => {
    const source = readPage(pagePath);
    expect(source).toContain('interface YieldPrediction');
    expect(source).toContain('predicted_yield_tons');
    expect(source).toContain('confidence_percent');
    expect(source).toContain('estimated_revenue_usd');
    expect(source).toContain('estimated_revenue_yer');
  });

  it('has form submission handler', () => {
    const source = readPage(pagePath);
    expect(source).toContain('handleSubmit');
    expect(source).toContain('onSubmit={handleSubmit}');
    expect(source).toContain('type="submit"');
  });

  it('has prediction result display', () => {
    const source = readPage(pagePath);
    expect(source).toContain('الإنتاج المتوقع');
    expect(source).toContain('العائد بالدولار');
    expect(source).toContain('العائد بالريال');
    expect(source).toContain('نسبة الثقة');
  });

  it('has factors and recommendations sections', () => {
    const source = readPage(pagePath);
    expect(source).toContain('العوامل المؤثرة');
    expect(source).toContain('التوصيات');
    expect(source).toContain('factors_applied');
    expect(source).toContain('recommendations');
  });

  it('has empty state prompt', () => {
    const source = readPage(pagePath);
    expect(source).toContain('أدخل بيانات الحقل');
    expect(source).toContain('ستظهر نتائج التنبؤ هنا بعد إدخال البيانات');
  });
});
