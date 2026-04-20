/**
 * Screen Component Tests — Web Dashboard Pages
 * اختبارات مكونات الشاشات — صفحات لوحة التحكم
 *
 * Validates page structure, metadata exports, client component imports,
 * Arabic content, and module contracts for all dashboard pages.
 * Uses filesystem checks (following the admin app pattern) to avoid
 * server-side module resolution issues with 'use client' components.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

const DASHBOARD_DIR = path.resolve(__dirname, '..');

/** Prevent path traversal. */
function safePath(base: string, relative: string): string {
  const resolved = path.resolve(base, relative);
  if (!resolved.startsWith(base + path.sep) && resolved !== base) {
    throw new Error(`Path traversal detected: ${relative}`);
  }
  return resolved;
}

/** Read a page file, returning null when not found. */
function readPageFile(relativePath: string): { content: string; filePath: string } | null {
  const tsxPath = safePath(DASHBOARD_DIR, relativePath + '.tsx');
  const tsPath = safePath(DASHBOARD_DIR, relativePath + '.ts');
  const filePath = fs.existsSync(tsxPath) ? tsxPath : fs.existsSync(tsPath) ? tsPath : null;
  if (!filePath) return null;
  return { content: fs.readFileSync(filePath, 'utf-8'), filePath };
}

// ═══════════════════════════════════════════════════════════════════════════
// Server Component Pages (with metadata) — comprehensive tests
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Each entry: [route, exportedFunctionName, metadataTitleSubstring, clientComponentName, arabicLabel]
 */
const SERVER_PAGES: [string, string, string, string, string][] = [
  ['dashboard/page', 'DashboardPage', 'Dashboard', 'DashboardClient', 'لوحة التحكم'],
  ['alerts/page', 'AlertsPage', 'Alerts', 'AlertsClient', 'التنبيهات'],
  ['analytics/page', 'AnalyticsPage', 'Analytics', 'AnalyticsDashboard', 'التحليلات'],
  ['crops/page', 'CropsPage', 'Crop Management', 'CropsClient', 'المحاصيل'],
  ['crop-health/page', 'CropHealthPage', 'Crop Health', 'CropHealthClient', 'صحة المحصول'],
  ['crop-planning/page', 'CropPlanningPage', 'Crop Planning', 'CropPlanningClient', 'تخطيط'],
  ['crop-protection/page', 'CropProtectionPage', 'Crop Protection', 'CropProtectionClient', 'حماية المحاصيل'],
  ['crop-insurance/page', 'CropInsurancePage', 'Crop Insurance', 'CropInsuranceClient', 'التأمين الزراعي'],
  ['diseases/page', 'DiseasesPage', 'Diseases', 'DiseasesClient', 'الأمراض'],
  ['drone/page', 'DronePage', 'Drone', 'DroneClient', 'الطائرات بدون طيار'],
  ['equipment/page', 'EquipmentPage', 'Equipment', 'EquipmentClient', 'المعدات'],
  ['farms/page', 'FarmsPage', 'Farm', 'FarmsClient', 'المزارع'],
  ['harvest-quality/page', 'HarvestQualityPage', 'Harvest Quality', 'HarvestQualityClient', 'جودة الحصاد'],
  ['inventory/page', 'InventoryPage', 'Inventory', 'InventoryClient', 'المخزون'],
  ['iot/page', 'IoTPage', 'IoT', 'IoTClient', 'إنترنت الأشياء'],
  ['marketplace/page', 'MarketplacePage', 'Marketplace', 'MarketplaceClient', 'السوق'],
  ['notifications/page', 'NotificationsPage', 'Notifications', 'NotificationsClient', 'الإشعارات'],
  ['tasks/page', 'TasksPage', 'Tasks', 'TasksClient', 'المهام'],
  ['terrain/page', 'TerrainPage', 'Terrain', 'TerrainClient', 'التضاريس'],
  ['seeds/page', 'SeedsPage', 'Seed', 'SeedsClient', 'البذور'],
  ['sensors/page', 'SensorsPage', 'Sensors', 'SensorsClient', 'الحساسات'],
  ['yield/page', 'YieldPage', 'Yield', 'YieldClient', 'المحصول'],
  ['soil-analysis/page', 'SoilAnalysisPage', 'Soil Analysis', 'SoilAnalysisClient', 'التربة'],
  ['compliance/page', 'CompliancePage', 'الامتثال', 'ComplianceClient', 'الامتثال'],
  ['cooperatives/page', 'CooperativesPage', 'Cooperatives', 'CooperativesClient', 'التعاونيات'],
  ['scouting/page', 'ScoutingPage', 'Scouting', 'ScoutingClient', 'الاستكشاف'],
  ['community/page', 'CommunityPage', 'Community', 'Feed', 'مجتمع'],
  ['audit/page', 'AuditPage', 'Audit', 'AuditClient', 'سجل التدقيق'],
  ['documents/page', 'DocumentsPage', 'Documents', 'DocumentsClient', 'الوثائق'],
  ['edge-devices/page', 'EdgeDevicesPage', 'Edge Devices', 'EdgeDevicesClient', 'الحوسبة الطرفية'],
  ['epidemic/page', 'EpidemicPage', 'Epidemic', 'EpidemicClient', 'الأوبئة'],
  ['vision/page', 'VisionPage', 'Vision', 'VisionClient', 'الكشف البصري'],
  ['market-prices/page', 'MarketPricesPage', 'Market', 'MarketPricesClient', 'أسعار'],
  ['logistics/page', 'LogisticsPage', 'اللوجستيات', 'LogisticsClient', 'اللوجستيات'],
  ['soil-map/page', 'SoilMapPage', 'Soil', 'SoilMapClient', 'التربة'],
  ['field-prep/page', 'FieldPrepPage', 'Field', 'FieldPrepClient', 'تحضير الحقل'],
  ['field-zones/page', 'FieldZonesPage', 'Field', 'FieldZonesClient', 'مناطق الحقل'],
  ['field-comparison/page', 'FieldComparisonPage', 'Field', 'FieldComparisonClient', 'مقارنة'],
  ['satellite/page', 'SatellitePage', 'Satellite', 'SatelliteClient', 'الأقمار الصناعية'],
  ['satellite-monitor/page', 'SatelliteMonitorPage', 'Satellite', 'SatelliteMonitorClient', 'الأقمار الصناعية'],
  ['settings/page', 'Settings', 'Settings', 'SettingsPage', 'الإعدادات'],
  ['support/page', 'SupportPage', 'Support', 'SupportClient', 'الدعم'],
  ['users/page', 'UsersPage', 'User Management', 'UsersClient', 'المستخدمين'],
  ['virtual-sensors/page', 'VirtualSensorsPage', 'Virtual', 'VirtualSensorsClient', 'المستشعرات الافتراضية'],
  ['wallet/page', 'WalletPage', 'Wallet', 'WalletClient', 'المحفظة'],
  ['pivot-irrigation/page', 'PivotIrrigationPage', 'Pivot', 'PivotIrrigationClient', 'الري المحوري'],
  ['reports/page', 'ReportsPage', 'Reports', 'ReportsClient', 'التقارير'],
  ['disaster-assessment/page', 'DisasterAssessmentPage', 'الكوارث', 'DisasterAssessmentClient', 'الكوارث'],
];

describe.each(SERVER_PAGES)(
  'Page: %s',
  (route, exportedFn, titleSubstr, clientComp, arabicLabel) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it('is NOT a client component (should be server component)', () => {
      if (!page) return;
      // Server component pages should NOT have 'use client'
      expect(page.content).not.toMatch(/^['"]use client['"]/m);
    });

    it(`exports default function ${exportedFn}`, () => {
      if (!page) return;
      expect(page.content).toMatch(
        new RegExp(`export\\s+default\\s+(async\\s+)?function\\s+${exportedFn}`)
      );
    });

    it('exports Next.js Metadata', () => {
      if (!page) return;
      expect(page.content).toContain('export const metadata');
      expect(page.content).toContain("Metadata");
    });

    it(`metadata title contains "${titleSubstr}"`, () => {
      if (!page) return;
      // Extract title from metadata object
      const titleMatch = page.content.match(/title:\s*['"]([^'"]+)['"]/);
      if (titleMatch) {
        expect(titleMatch[1]).toContain(titleSubstr);
      }
    });

    it(`imports ${clientComp} client component`, () => {
      if (!page) return;
      expect(page.content).toContain(clientComp);
    });

    it(`renders <${clientComp} /> in JSX`, () => {
      if (!page) return;
      expect(page.content).toMatch(new RegExp(`<${clientComp}\\s*/>`));
    });

    it(`has Arabic content "${arabicLabel}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicLabel);
    });

    it('has SEO description', () => {
      if (!page) return;
      expect(page.content).toContain('description');
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Client Component Pages ('use client') — structure tests
// ═══════════════════════════════════════════════════════════════════════════

const CLIENT_PAGES: [string, string][] = [
  ['analytics/field-compare/page', 'الحقول'],
  ['analytics/gap-analysis/page', 'الفجوات'],
  ['analytics/profitability/page', 'الربحية'],
  ['analytics/satellite/page', 'القمر الصناعي'],
  ['analytics/soil/page', 'التربة'],
  ['analytics/yield-forecasting/page', 'تنبؤ'],
  ['analytics/yield/page', 'الإنتاجية'],
  ['copilot/page', 'المساعد'],
  ['reports/seasonal/page', 'الموسم'],
];

describe.each(CLIENT_PAGES)(
  'Client Page: %s',
  (route, arabicContent) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it('has "use client" directive', () => {
      if (!page) return;
      expect(page.content).toMatch(/['"]use client['"]/);
    });

    it('exports a default function', () => {
      if (!page) return;
      expect(page.content).toMatch(/export\s+default\s+function/);
    });

    it('imports React hooks (useState or useEffect)', () => {
      if (!page) return;
      const hasHooks = page.content.includes('useState') || page.content.includes('useEffect');
      expect(hasHooks).toBe(true);
    });

    it(`contains Arabic content "${arabicContent}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicContent);
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Dynamic route pages — [id] pattern tests
// ═══════════════════════════════════════════════════════════════════════════

const DYNAMIC_PAGES: [string, string, string][] = [
  ['fields/[id]/page', 'FieldDetailsPage', 'الحقل'],
  ['equipment/[id]/page', 'EquipmentDetailPage', 'المعدات'],
  ['satellite-monitor/field/[id]/page', 'FieldDetailPage', 'الأقمار'],
];

describe.each(DYNAMIC_PAGES)(
  'Dynamic Page: %s',
  (route, exportedFn, arabicLabel) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it(`exports default function`, () => {
      if (!page) return;
      expect(page.content).toMatch(/export\s+default\s+(async\s+)?function/);
    });

    it('has metadata or page params', () => {
      if (!page) return;
      const hasMetadata = page.content.includes('metadata');
      const hasParams = page.content.includes('params');
      expect(hasMetadata || hasParams).toBe(true);
    });

    it(`has Arabic content "${arabicLabel}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicLabel);
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Precision Agriculture Sub-pages
// ═══════════════════════════════════════════════════════════════════════════

const PA_PAGES: [string, string, string][] = [
  ['precision-agriculture/page', 'PrecisionAgriculturePage', 'الزراعة الدقيقة'],
  ['precision-agriculture/fertilizer/page', 'FertilizerPage', 'الأسمدة'],
  ['precision-agriculture/gdd/page', 'GDDPage', 'درجات النمو'],
  ['precision-agriculture/spray/page', 'SprayPage', 'الرش'],
  ['precision-agriculture/vra/page', 'VRAPage', 'التطبيق المتغير'],
];

describe.each(PA_PAGES)(
  'Precision Agriculture: %s',
  (route, exportedFn, arabicLabel) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it('exports a default function', () => {
      if (!page) return;
      expect(page.content).toMatch(/export\s+default\s+function/);
    });

    it('has metadata with SAHOOL branding', () => {
      if (!page) return;
      expect(page.content).toContain('SAHOOL');
    });

    it(`has Arabic label "${arabicLabel}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicLabel);
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Cross-cutting Quality Checks
// ═══════════════════════════════════════════════════════════════════════════

describe('Cross-cutting Page Quality', () => {
  const allPageFiles = fs.readdirSync(DASHBOARD_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);

  it('should have at least 50 dashboard routes', () => {
    expect(allPageFiles.length).toBeGreaterThanOrEqual(50);
  });

  it('all server pages should import from next Metadata', () => {
    let serverPageCount = 0;
    let withMetadata = 0;

    for (const dir of allPageFiles) {
      const pagePath = path.join(DASHBOARD_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      if (content.match(/^['"]use client['"]/m)) continue;
      serverPageCount++;
      if (content.includes('Metadata')) withMetadata++;
    }

    expect(serverPageCount).toBeGreaterThan(0);
    expect(withMetadata).toBe(serverPageCount);
  });

  it('no page should import database/ORM directly (client boundary)', () => {
    for (const dir of allPageFiles) {
      const pagePath = path.join(DASHBOARD_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      expect(content).not.toContain('prisma');
      expect(content).not.toContain('asyncpg');
      expect(content).not.toContain('pg-pool');
    }
  });

  it('no page should expose API keys or secrets', () => {
    for (const dir of allPageFiles) {
      const pagePath = path.join(DASHBOARD_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      expect(content).not.toMatch(/API_KEY\s*=\s*['"]/);
      expect(content).not.toMatch(/SECRET\s*=\s*['"]/);
      expect(content).not.toMatch(/password\s*[:=]\s*['"]/i);
    }
  });

  it('all pages with metadata should have description for SEO', () => {
    let withMetadata = 0;
    let withDescription = 0;

    for (const dir of allPageFiles) {
      const pagePath = path.join(DASHBOARD_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      if (!content.includes('export const metadata')) continue;
      withMetadata++;
      if (content.includes('description')) withDescription++;
    }

    expect(withMetadata).toBeGreaterThan(0);
    expect(withDescription).toBe(withMetadata);
  });

  it('all pages with metadata should include SAHOOL branding', () => {
    for (const dir of allPageFiles) {
      const pagePath = path.join(DASHBOARD_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      if (!content.includes('export const metadata')) continue;
      expect(content).toContain('SAHOOL');
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Auth Pages — Structure Tests
// ═══════════════════════════════════════════════════════════════════════════

const AUTH_DIR = path.resolve(__dirname, '..', '..', '(auth)');

const AUTH_PAGES: [string, string][] = [
  ['login/page', 'تسجيل الدخول'],
  ['register/page', 'إنشاء حساب'],
  ['forgot-password/page', 'كلمة المرور'],
  ['reset-password/page', 'كلمة المرور'],
  ['verify-otp/page', 'التحقق'],
];

describe.each(AUTH_PAGES)(
  'Auth Page: %s',
  (route, arabicLabel) => {
    const tsxPath = path.join(AUTH_DIR, route + '.tsx');
    const exists = fs.existsSync(tsxPath);

    it('file exists', () => {
      expect(exists, `Auth page ${route}.tsx not found`).toBe(true);
    });

    it('exports a default function', () => {
      if (!exists) return;
      const content = fs.readFileSync(tsxPath, 'utf-8');
      expect(content).toMatch(/export\s+default\s+function/);
    });

    it(`has Arabic content "${arabicLabel}"`, () => {
      if (!exists) return;
      const content = fs.readFileSync(tsxPath, 'utf-8');
      expect(content).toContain(arabicLabel);
    });

    it('does not expose demo credentials', () => {
      if (!exists) return;
      const content = fs.readFileSync(tsxPath, 'utf-8');
      expect(content).not.toMatch(/demo@|admin@.*password|test.*password/i);
    });
  }
);
