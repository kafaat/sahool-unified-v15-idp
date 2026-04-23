/**
 * Screen Component Tests — Admin Dashboard Pages
 * اختبارات مكونات الشاشات — صفحات لوحة تحكم المدير
 *
 * Validates page structure, directives, exports, Arabic content,
 * import patterns, and security checks for all admin pages.
 * Uses filesystem checks (matching the established admin test pattern)
 * to avoid complex client-side module resolution issues.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

const APP_DIR = path.resolve(__dirname, '..');

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
  const tsxPath = safePath(APP_DIR, relativePath + '.tsx');
  const tsPath = safePath(APP_DIR, relativePath + '.ts');
  const filePath = fs.existsSync(tsxPath) ? tsxPath : fs.existsSync(tsPath) ? tsPath : null;
  if (!filePath) return null;
  return { content: fs.readFileSync(filePath, 'utf-8'), filePath };
}

// ═══════════════════════════════════════════════════════════════════════════
// Admin 'use client' Pages — Structure Tests
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Each entry: [route, arabicComment, hasDefaultExport]
 * All admin pages are 'use client' components.
 */
const ADMIN_CLIENT_PAGES: [string, string][] = [
  ['dashboard/page', 'لوحة تحكم'],
  ['alerts/page', 'التنبيهات'],
  ['crop-health/page', 'صحة المحاصيل'],
  ['crop-planning/page', 'تخطيط'],
  ['crop-protection/page', 'حماية المحاصيل'],
  ['diseases/page', 'الأمراض'],
  ['drone/page', 'الطائرات'],
  ['equipment/page', 'المعدات'],
  ['farms/page', 'المزارع'],
  ['inventory/page', 'المخزون'],
  ['marketplace/page', 'السوق'],
  ['tasks/page', 'المهام'],
  ['terrain/page', 'التضاريس'],
  ['vision/page', 'الرؤية'],
  ['edge-devices/page', 'الحافة'],
  ['sensors/page', 'المستشعرات'],
  ['scouting/page', 'الاستكشاف'],
  ['seeds/page', 'البذور'],
  ['cooperatives/page', 'التعاونيات'],
  ['compliance/page', 'الامتثال'],
  ['community/page', 'المجتمع'],
  ['users/page', 'المستخدمين'],
  ['settings/page', 'الإعدادات'],
  ['irrigation/page', 'الري'],
  ['weather/page', 'الطقس'],
  ['yield/page', 'الإنتاجية'],
  ['soil-map/page', 'التربة'],
  ['logistics/page', 'اللوجستيات'],
  ['traceability/page', 'تتبع'],
  ['research/page', 'الأبحاث'],
  ['support/page', 'الدعم'],
  ['lab/page', 'useState'],
  ['field-comparison/page', 'مقارنة'],
  ['field-prep/page', 'تحضير'],
  ['field-zones/page', 'مناطق'],
  ['insurance/page', 'التأمين'],
  ['market-prices/page', 'أسعار'],
  ['virtual-sensors/page', 'المستشعرات'],
  ['reports/page', 'التقارير'],
  ['disasters/page', 'الكوارث'],
  ['epidemic/page', 'الأوبئة'],
  ['audit/page', 'التدقيق'],
  ['copilot/page', 'المساعد'],
  ['code-review/page', 'المراجعة'],
  ['seasons/page', 'المواسم'],
];

describe.each(ADMIN_CLIENT_PAGES)(
  'Admin Page: %s',
  (route, arabicContent) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it('has "use client" directive', () => {
      if (!page) return;
      expect(page.content).toMatch(/['"]use client['"]/);
    });

    it('exports a default function or component', () => {
      if (!page) return;
      const hasDefaultExport =
        page.content.includes('export default function') ||
        page.content.includes('export default ');
      expect(hasDefaultExport).toBe(true);
    });

    it(`contains Arabic content or identifier "${arabicContent}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicContent);
    });

    it('does not expose credentials or secrets', () => {
      if (!page) return;
      expect(page.content).not.toMatch(/API_KEY\s*=\s*['"]/);
      expect(page.content).not.toMatch(/SECRET\s*=\s*['"]/);
      expect(page.content).not.toMatch(/password\s*[:=]\s*['"][^'"]+['"]/i);
    });

    it('does not import database/ORM directly', () => {
      if (!page) return;
      expect(page.content).not.toContain('from \'prisma\'');
      expect(page.content).not.toContain('from \'asyncpg\'');
      expect(page.content).not.toContain('from \'pg\'');
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Admin Auth Pages — Structure Tests
// ═══════════════════════════════════════════════════════════════════════════

const ADMIN_AUTH_PAGES: [string, string][] = [
  ['(auth)/login/page', 'تسجيل الدخول'],
  ['(auth)/register/page', 'إنشاء'],
  ['(auth)/forgot-password/page', 'كلمة المرور'],
  ['(auth)/reset-password/page', 'كلمة المرور'],
  ['(auth)/verify-otp/page', 'التحقق'],
];

describe.each(ADMIN_AUTH_PAGES)(
  'Admin Auth Page: %s',
  (route, arabicLabel) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `Auth page ${route}.tsx not found`).not.toBeNull();
    });

    it('exports a default function', () => {
      if (!page) return;
      expect(page.content).toMatch(/export\s+default\s+(async\s+)?function/);
    });

    it(`has Arabic content "${arabicLabel}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicLabel);
    });

    it('does not expose demo credentials', () => {
      if (!page) return;
      expect(page.content).not.toMatch(/demo@|admin@.*password/i);
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Admin Sub-routes — Nested Pages
// ═══════════════════════════════════════════════════════════════════════════

const ADMIN_SUB_PAGES: [string, string][] = [
  ['analytics/profitability/page', 'الربحية'],
  ['analytics/satellite/page', 'الفضائية'],
  ['analytics/yield/page', 'الغلة'],
  ['analytics/soil/page', 'التربة'],
  ['analytics/gap-analysis/page', 'الفجوات'],
  ['analytics/yield-forecasting/page', 'تنبؤ'],
  ['analytics/field-compare/page', 'مقارنة'],
  ['equipment/fleet-tracking/page', 'الأسطول'],
  ['reports/seasonal/page', 'الموسم'],
  ['(dashboard)/settings/sessions/page', 'الجلسات'],
];

describe.each(ADMIN_SUB_PAGES)(
  'Admin Sub-page: %s',
  (route, arabicLabel) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it('has "use client" directive', () => {
      if (!page) return;
      expect(page.content).toMatch(/['"]use client['"]/);
    });

    it(`contains Arabic content "${arabicLabel}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicLabel);
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Admin Dynamic Route Pages
// ═══════════════════════════════════════════════════════════════════════════

const ADMIN_DYNAMIC_PAGES: [string, string][] = [
  ['farms/[id]/page', 'الحقل'],
  ['audit/fields/[fieldId]/page', 'تدقيق الحقل'],
];

describe.each(ADMIN_DYNAMIC_PAGES)(
  'Admin Dynamic Page: %s',
  (route, arabicLabel) => {
    const page = readPageFile(route);

    it('file exists', () => {
      expect(page, `${route}.tsx not found`).not.toBeNull();
    });

    it(`contains Arabic content "${arabicLabel}"`, () => {
      if (!page) return;
      expect(page.content).toContain(arabicLabel);
    });
  }
);

// ═══════════════════════════════════════════════════════════════════════════
// Admin Page Import Pattern Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Admin Page Import Patterns', () => {
  const pageFiles = fs.readdirSync(APP_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('__') && !d.name.startsWith('('))
    .map(d => d.name);

  it('should have at least 40 admin routes', () => {
    expect(pageFiles.length).toBeGreaterThanOrEqual(40);
  });

  it('all client pages import React hooks', () => {
    let withHooks = 0;
    let total = 0;

    for (const dir of pageFiles) {
      const pagePath = path.join(APP_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      if (!content.match(/['"]use client['"]/)) continue;
      total++;
      if (content.includes('useState') || content.includes('useEffect') || content.includes('useCallback')) {
        withHooks++;
      }
    }

    expect(total).toBeGreaterThan(0);
    // Most client pages should use React hooks
    expect(withHooks / total).toBeGreaterThan(0.8);
  });

  it('no page uses eval() or Function constructor', () => {
    for (const dir of pageFiles) {
      const pagePath = path.join(APP_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      expect(content).not.toMatch(/\beval\s*\(/);
      expect(content).not.toMatch(/new\s+Function\s*\(/);
    }
  });

  it('no page has dangerouslySetInnerHTML without sanitization', () => {
    for (const dir of pageFiles) {
      const pagePath = path.join(APP_DIR, dir, 'page.tsx');
      if (!fs.existsSync(pagePath)) continue;
      const content = fs.readFileSync(pagePath, 'utf-8');
      if (content.includes('dangerouslySetInnerHTML')) {
        // If used, should have sanitization nearby
        const hasSanitize = content.includes('DOMPurify') ||
          content.includes('sanitize') ||
          content.includes('xss');
        expect(hasSanitize).toBe(true);
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Admin Page Completeness Check
// ═══════════════════════════════════════════════════════════════════════════

describe('Admin Page Completeness', () => {
  const expectedRoutes = [
    'dashboard', 'alerts', 'crop-health', 'crop-planning', 'crop-protection',
    'diseases', 'drone', 'equipment', 'farms', 'inventory', 'marketplace',
    'tasks', 'terrain', 'vision', 'edge-devices', 'sensors', 'scouting',
    'seeds', 'cooperatives', 'compliance', 'community', 'users', 'settings',
    'irrigation', 'weather', 'yield', 'soil-map', 'logistics', 'traceability',
    'research', 'support', 'lab', 'reports', 'disasters', 'epidemic',
    'audit', 'copilot', 'code-review', 'seasons', 'field-comparison',
    'field-prep', 'field-zones', 'insurance', 'market-prices', 'virtual-sensors',
  ];

  it.each(expectedRoutes)('route %s has a page.tsx file', (route) => {
    const pagePath = path.join(APP_DIR, route, 'page.tsx');
    expect(fs.existsSync(pagePath), `${route}/page.tsx missing`).toBe(true);
  });

  it('should have all expected admin routes', () => {
    const actual = fs.readdirSync(APP_DIR, { withFileTypes: true })
      .filter(d => d.isDirectory() && !d.name.startsWith('__') && !d.name.startsWith('('))
      .map(d => d.name);

    for (const route of expectedRoutes) {
      expect(actual).toContain(route);
    }
  });
});
