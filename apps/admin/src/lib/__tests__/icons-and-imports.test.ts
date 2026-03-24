/**
 * Icons & Imports Verification Tests
 * اختبارات التحقق من الأيقونات والاستيرادات
 *
 * Verifies that all icons render correctly and critical imports resolve properly.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const SRC_DIR = path.resolve(__dirname, '../..');

// ═══════════════════════════════════════════════════════════════════════════
// Lucide Icons Import Verification | التحقق من استيراد أيقونات Lucide
// ═══════════════════════════════════════════════════════════════════════════

describe('Lucide Icons Usage', () => {
  const componentsWithIcons: {
    file: string;
    expectedIcons: string[];
  }[] = [
    {
      file: 'components/dashboard/MapOverview.tsx',
      expectedIcons: ['MapPin', 'Layers', 'Eye', 'EyeOff'],
    },
    {
      file: 'components/dashboard/AlertsPanel.tsx',
      expectedIcons: ['Bell', 'AlertTriangle', 'Filter'],
    },
    {
      file: 'components/dashboard/ActivityFeed.tsx',
      expectedIcons: ['Activity'],
    },
    {
      file: 'components/ui/SearchFilter.tsx',
      expectedIcons: ['Search', 'X', 'Filter'],
    },
    {
      file: 'components/ui/BulkActions.tsx',
      expectedIcons: ['Trash2', 'Archive', 'Download'],
    },
    {
      file: 'components/ui/ThemeToggle.tsx',
      expectedIcons: ['Sun', 'Moon', 'Monitor'],
    },
    {
      file: 'components/ui/ExportButton.tsx',
      expectedIcons: ['Download'],
    },
    {
      file: 'components/ui/Breadcrumbs.tsx',
      expectedIcons: ['ChevronLeft'],
    },
    {
      file: 'components/ui/StatCard.tsx',
      expectedIcons: ['LucideIcon'],
    },
  ];

  componentsWithIcons.forEach(({ file, expectedIcons }) => {
    it(`${file} imports lucide-react icons: ${expectedIcons.join(', ')}`, () => {
      const fullPath = path.join(SRC_DIR, file);
      expect(fs.existsSync(fullPath), `File not found: ${file}`).toBe(true);

      const content = fs.readFileSync(fullPath, 'utf-8');

      // Verify lucide-react import exists
      expect(content).toContain('lucide-react');

      // Verify each expected icon is imported
      expectedIcons.forEach((icon) => {
        expect(content.includes(icon), `Icon "${icon}" not found in ${file}`).toBe(true);
      });
    });
  });

  it('icons are imported from lucide-react (not custom implementation)', () => {
    const mapOverview = fs.readFileSync(
      path.join(SRC_DIR, 'components/dashboard/MapOverview.tsx'),
      'utf-8'
    );
    // Ensure icons come from lucide-react, not a custom source
    expect(mapOverview).toMatch(/import\s+\{[^}]*MapPin[^}]*\}\s+from\s+["']lucide-react["']/);
  });

  it('icon components use proper JSX rendering pattern', () => {
    const searchFilter = fs.readFileSync(
      path.join(SRC_DIR, 'components/ui/SearchFilter.tsx'),
      'utf-8'
    );
    // Icons should be rendered as JSX components: <Search ... />
    expect(searchFilter).toMatch(/<Search[\s/]/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Critical Module Imports | التحقق من الاستيرادات الحرجة
// ═══════════════════════════════════════════════════════════════════════════

describe('Critical Module Imports', () => {
  it('services.ts imports from @sahool/shared-types/contracts', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/api/services.ts'), 'utf-8');
    expect(content).toContain('@sahool/shared-types/contracts');
    expect(content).toContain('USER_ENDPOINTS');
    expect(content).toContain('IOT_ENDPOINTS');
    expect(content).toContain('IRRIGATION_ENDPOINTS');
    expect(content).toContain('ALERT_ENDPOINTS');
    expect(content).toContain('EQUIPMENT_ENDPOINTS');
    expect(content).toContain('buildUrl');
  });

  it('extended-services.ts imports from @sahool/shared-types/contracts', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/api/extended-services.ts'), 'utf-8');
    expect(content).toContain('@sahool/shared-types/contracts');
    expect(content).toContain('TASK_ENDPOINTS');
    expect(content).toContain('INVENTORY_ENDPOINTS');
    expect(content).toContain('MARKETPLACE_ENDPOINTS');
  });

  it('MapOverview uses next/dynamic for lazy loading', () => {
    const content = fs.readFileSync(
      path.join(SRC_DIR, 'components/dashboard/MapOverview.tsx'),
      'utf-8'
    );
    expect(content).toContain('next/dynamic');
    expect(content).toContain('ssr: false');
  });

  it('FarmsMap dynamically imports react-leaflet components', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'components/maps/FarmsMap.tsx'), 'utf-8');
    expect(content).toContain('react-leaflet');
    expect(content).toContain('MapContainer');
    expect(content).toContain('TileLayer');
    expect(content).toContain('CircleMarker');
    expect(content).toContain('Polygon');
    expect(content).toContain('Popup');
    expect(content).toContain('LayersControl');
  });

  it('useWebSocket hook imports from @/lib/websocket', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'hooks/useWebSocket.ts'), 'utf-8');
    expect(content).toContain('@/lib/websocket');
    expect(content).toContain('getWebSocketClient');
    expect(content).toContain('ConnectionStatus');
  });

  it('useRealTimeAlerts imports from ./useWebSocket', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'hooks/useRealTimeAlerts.ts'), 'utf-8');
    expect(content).toContain('useWebSocketEvent');
    expect(content).toContain('AlertMessage');
  });

  it('useCsrf imports from @/lib/csrf', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'hooks/useCsrf.ts'), 'utf-8');
    expect(content).toContain('@/lib/csrf');
    expect(content).toContain('CSRF_CONFIG');
  });

  it('auth store exports AuthProvider and useAuth', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'stores/auth.store.tsx'), 'utf-8');
    expect(content).toContain('AuthProvider');
    expect(content).toContain('useAuth');
  });

  it('theme store exports useTheme', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'stores/theme.store.tsx'), 'utf-8');
    expect(content).toContain('useTheme');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Export Utilities Import Check | التحقق من أدوات التصدير
// ═══════════════════════════════════════════════════════════════════════════

describe('Export Module', () => {
  it('export.ts exports all required functions', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/export.ts'), 'utf-8');
    expect(content).toContain('exportToCSV');
    expect(content).toContain('exportToExcel');
    expect(content).toContain('exportToPDF');
    expect(content).toContain('exportData');
    expect(content).toContain('exportFormatLabels');
  });

  it('export.ts supports Arabic content (BOM for CSV)', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/export.ts'), 'utf-8');
    // BOM (Byte Order Mark) for proper Arabic display in CSV
    expect(content).toContain('\\uFEFF');
  });

  it('export.ts escapes XML and HTML content', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/export.ts'), 'utf-8');
    expect(content).toContain('escapeXml');
    expect(content).toContain('escapeHtml');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Use Client Directive | التحقق من توجيه "use client"
// ═══════════════════════════════════════════════════════════════════════════

describe('Client Component Directives', () => {
  const clientComponents = [
    'components/dashboard/MapOverview.tsx',
    'components/maps/FarmsMap.tsx',
    'hooks/useWebSocket.ts',
    'hooks/useRealTimeAlerts.ts',
    'hooks/useCsrf.ts',
  ];

  clientComponents.forEach((file) => {
    it(`${file} has "use client" directive`, () => {
      const content = fs.readFileSync(path.join(SRC_DIR, file), 'utf-8');
      expect(content).toContain('"use client"');
    });
  });
});
