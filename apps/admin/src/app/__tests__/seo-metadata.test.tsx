/**
 * SEO & Metadata Tests
 * اختبارات تحسين محركات البحث والبيانات الوصفية
 *
 * Verifies SEO metadata, layout structure, and accessibility attributes.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const APP_DIR = path.resolve(__dirname, '..');

/**
 * Validate that a resolved path stays within the base directory.
 * Prevents path traversal (e.g., via "../" segments).
 */
function safePath(base: string, relative: string): string {
  const resolved = path.resolve(base, relative);
  if (!resolved.startsWith(base + path.sep) && resolved !== base) {
    throw new Error(`Path traversal detected: ${relative}`);
  }
  return resolved;
}

/**
 * Helper: Read and return file content
 */
function readFile(relativePath: string): string {
  const fullPath = safePath(APP_DIR, relativePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`File not found: ${fullPath}`);
  }
  return fs.readFileSync(fullPath, 'utf-8');
}

// ═══════════════════════════════════════════════════════════════════════════
// Root Layout SEO Tests | اختبارات SEO للتخطيط الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

describe('Root Layout SEO', () => {
  const layoutContent = readFile('layout.tsx');

  it('exports metadata with bilingual title', () => {
    expect(layoutContent).toContain('لوحة تحكم سهول');
    expect(layoutContent).toContain('Sahool Admin Dashboard');
  });

  it('exports metadata with Arabic description', () => {
    expect(layoutContent).toContain('لوحة تحكم المشرفين لمنصة سهول الزراعية الذكية');
  });

  it('includes bilingual keywords', () => {
    expect(layoutContent).toContain('سهول');
    expect(layoutContent).toContain('زراعة');
    expect(layoutContent).toContain('sahool');
    expect(layoutContent).toContain('agriculture');
    expect(layoutContent).toContain('yemen');
    expect(layoutContent).toContain('اليمن');
  });

  it('configures favicon icons', () => {
    expect(layoutContent).toContain('favicon.ico');
    expect(layoutContent).toContain('icon-192.png');
    expect(layoutContent).toContain('icon-512.png');
  });

  it('configures apple touch icon', () => {
    expect(layoutContent).toContain('apple');
    expect(layoutContent).toContain('icon-192.png');
  });

  it('sets RTL direction', () => {
    expect(layoutContent).toMatch(/dir[={"]+/);
    expect(layoutContent).toContain('getDirection');
  });

  it('sets Arabic language', () => {
    expect(layoutContent).toMatch(/lang[={"]+/);
    expect(layoutContent).toContain('getLocale');
  });

  it('uses Tajawal Arabic font', () => {
    // Tajawal is referenced in layout via CSS variable
    expect(layoutContent).toContain('Tajawal');
    // Font loaded via globals.css @import with arabic+latin subsets and weights
    const cssContent = readFile('globals.css');
    expect(cssContent).toContain('Tajawal');
  });

  it('includes font weights 400, 500, 700', () => {
    // Font weights are specified in self-hosted @font-face declarations in globals.css
    const cssContent = readFile('globals.css');
    expect(cssContent).toContain('font-weight: 400');
    expect(cssContent).toContain('font-weight: 500');
    expect(cssContent).toContain('font-weight: 700');
  });

  it('sets font display to swap', () => {
    // font-display: swap is set in self-hosted @font-face declarations in globals.css
    const cssContent = readFile('globals.css');
    expect(cssContent).toContain('font-display: swap');
  });

  it('has CSP nonce support', () => {
    expect(layoutContent).toContain('X-Nonce');
    expect(layoutContent).toContain('nonce');
  });

  it('loads Leaflet CSS with integrity', () => {
    expect(layoutContent).toContain('leaflet');
    expect(layoutContent).toContain('integrity');
    expect(layoutContent).toContain('crossOrigin');
  });

  it('has noscript fallback for Leaflet CSS', () => {
    expect(layoutContent).toContain('<noscript>');
    expect(layoutContent).toContain('leaflet');
  });

  it('uses force-dynamic rendering', () => {
    expect(layoutContent).toContain('export const dynamic = "force-dynamic"');
  });

  it('wraps children with Providers', () => {
    expect(layoutContent).toContain('<Providers>');
    expect(layoutContent).toContain('</Providers>');
  });

  it('suppresses hydration warning on html element', () => {
    expect(layoutContent).toContain('suppressHydrationWarning');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Global CSS & Styling Tests | اختبارات التنسيق العام
// ═══════════════════════════════════════════════════════════════════════════

describe('Global Styles', () => {
  it('has globals.css file', () => {
    const cssPath = safePath(APP_DIR, 'globals.css');
    expect(fs.existsSync(cssPath)).toBe(true);
  });

  it('globals.css imports tailwind', () => {
    const cssContent = readFile('globals.css');
    expect(cssContent).toContain('tailwind');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Auth Layout Tests | اختبارات تخطيط المصادقة
// ═══════════════════════════════════════════════════════════════════════════

describe('Auth Layout', () => {
  it('has auth layout file', () => {
    const authLayoutPath = safePath(APP_DIR, path.join('(auth)', 'layout.tsx'));
    expect(fs.existsSync(authLayoutPath)).toBe(true);
  });

  it('auth layout exports default component', () => {
    const content = readFile('(auth)/layout.tsx');
    expect(content).toMatch(/export\s+default\s+/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Providers Tests | اختبارات مزودات السياق
// ═══════════════════════════════════════════════════════════════════════════

describe('Providers', () => {
  it('has providers file', () => {
    const providersPath = safePath(APP_DIR, 'providers.tsx');
    expect(fs.existsSync(providersPath)).toBe(true);
  });

  it('exports Providers component', () => {
    const content = readFile('providers.tsx');
    expect(content).toContain('Providers');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Component File Existence - Smoke Tests | اختبارات وجود ملفات المكونات
// ═══════════════════════════════════════════════════════════════════════════

describe('Component File Existence', () => {
  const SRC_DIR = path.resolve(APP_DIR, '..');
  const COMPONENTS_DIR = path.join(SRC_DIR, 'components');

  it('has dashboard components directory', () => {
    expect(fs.existsSync(safePath(COMPONENTS_DIR, 'dashboard'))).toBe(true);
  });

  it('has ui components directory', () => {
    expect(fs.existsSync(safePath(COMPONENTS_DIR, 'ui'))).toBe(true);
  });

  it('has layout components directory', () => {
    expect(fs.existsSync(safePath(COMPONENTS_DIR, 'layout'))).toBe(true);
  });

  it('has auth components directory', () => {
    expect(fs.existsSync(safePath(COMPONENTS_DIR, 'auth'))).toBe(true);
  });

  const uiComponents = [
    'StatCard.tsx',
    'StatusBadge.tsx',
    'AlertBadge.tsx',
    'Breadcrumbs.tsx',
    'DataTable.tsx',
    'EnhancedDataTable.tsx',
    'SearchFilter.tsx',
    'BulkActions.tsx',
    'ExportButton.tsx',
    'ThemeToggle.tsx',
    'TablePageSkeleton.tsx',
  ];

  uiComponents.forEach((component) => {
    it(`has UI component: ${component}`, () => {
      const componentPath = safePath(COMPONENTS_DIR, path.join('ui', component));
      expect(fs.existsSync(componentPath), `Missing UI component: ${component}`).toBe(true);
    });
  });

  const dashboardComponents = [
    'MetricsGrid.tsx',
    'AlertsPanel.tsx',
    'ActivityFeed.tsx',
    'MapOverview.tsx',
  ];

  dashboardComponents.forEach((component) => {
    it(`has dashboard component: ${component}`, () => {
      const componentPath = safePath(COMPONENTS_DIR, path.join('dashboard', component));
      expect(fs.existsSync(componentPath), `Missing dashboard component: ${component}`).toBe(true);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Store File Existence Tests | اختبارات وجود ملفات المخازن
// ═══════════════════════════════════════════════════════════════════════════

describe('Store Files', () => {
  const SRC_DIR = path.resolve(APP_DIR, '..');
  const STORES_DIR = path.join(SRC_DIR, 'stores');

  it('has auth store', () => {
    expect(fs.existsSync(safePath(STORES_DIR, 'auth.store.tsx'))).toBe(true);
  });

  it('has theme store', () => {
    expect(fs.existsSync(safePath(STORES_DIR, 'theme.store.tsx'))).toBe(true);
  });

  it('auth store exports AuthProvider and useAuth', () => {
    const content = fs.readFileSync(safePath(STORES_DIR, 'auth.store.tsx'), 'utf-8');
    expect(content).toContain('AuthProvider');
    expect(content).toContain('useAuth');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Hooks File Existence Tests | اختبارات وجود ملفات الخطافات
// ═══════════════════════════════════════════════════════════════════════════

describe('Custom Hooks', () => {
  const SRC_DIR = path.resolve(APP_DIR, '..');
  const HOOKS_DIR = path.join(SRC_DIR, 'hooks');

  it('has useWebSocket hook', () => {
    expect(fs.existsSync(safePath(HOOKS_DIR, 'useWebSocket.ts'))).toBe(true);
  });

  it('has useRealTimeAlerts hook', () => {
    expect(fs.existsSync(safePath(HOOKS_DIR, 'useRealTimeAlerts.ts'))).toBe(true);
  });

  it('has useCsrf hook', () => {
    expect(fs.existsSync(safePath(HOOKS_DIR, 'useCsrf.ts'))).toBe(true);
  });
});
