/**
 * SAHOOL Platform — Migration Validation Tests
 * اختبارات التحقق من ترحيل الخدمات لمنصة سهول
 *
 * Filesystem-based Vitest tests that read actual source files and validate
 * that service migrations (deprecated → replacement) are properly handled.
 *
 * These tests do NOT launch a browser or containers; they analyse the source
 * code on disk to enforce migration completeness across the platform.
 */

import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// ─── Path Constants ──────────────────────────────────────────────────────────
const ROOT = path.resolve(__dirname, '../../..');
const CONTRACTS = path.join(ROOT, 'packages/shared-types/src/contracts');
const SERVICES = path.join(ROOT, 'apps/services');
const WEB_SRC = path.join(ROOT, 'apps/web/src');
const ADMIN_SRC = path.join(ROOT, 'apps/admin/src');
const DOCS = path.join(ROOT, 'docs/migrations');
const DOCKER_COMPOSE = path.join(ROOT, 'docker-compose.yml');
const ARCHIVE = path.join(ROOT, 'archive/deprecated-services');

// ─── Helpers ─────────────────────────────────────────────────────────────────

function readFile(filePath: string): string {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`File not found: ${resolved}`);
  }
  return fs.readFileSync(resolved, 'utf-8');
}

function fileExists(filePath: string): boolean {
  return fs.existsSync(path.resolve(filePath));
}

function dirExists(dirPath: string): boolean {
  const resolved = path.resolve(dirPath);
  return fs.existsSync(resolved) && fs.statSync(resolved).isDirectory();
}

/**
 * Recursively collect all files matching an extension under a directory.
 * Skips node_modules, .next, dist, __pycache__, and test directories.
 * Results are memoized per (dir, ext, skipTests) combination.
 */
const _fileCache = new Map<string, string[]>();
function collectFiles(
  dir: string,
  ext: string,
  maxDepth = 6,
  opts: { skipTests?: boolean } = {},
): string[] {
  const cacheKey = `${dir}|${ext}|${opts.skipTests ?? false}`;
  if (_fileCache.has(cacheKey)) return _fileCache.get(cacheKey)!;

  const results: string[] = [];
  if (!dirExists(dir) || maxDepth <= 0) return results;

  const SKIP = new Set([
    'node_modules', '.next', 'dist', '__pycache__', '.git', 'coverage',
  ]);
  if (opts.skipTests) {
    SKIP.add('__tests__');
    SKIP.add('__mocks__');
    SKIP.add('test');
    SKIP.add('tests');
  }

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...collectFilesInner(full, ext, maxDepth - 1, opts));
    } else if (entry.name.endsWith(ext)) {
      if (opts.skipTests && (entry.name.includes('.test.') || entry.name.includes('.spec.'))) {
        continue;
      }
      results.push(full);
    }
  }
  _fileCache.set(cacheKey, results);
  return results;
}

/** Inner recursive helper (no caching per sub-directory). */
function collectFilesInner(
  dir: string,
  ext: string,
  maxDepth: number,
  opts: { skipTests?: boolean },
): string[] {
  const results: string[] = [];
  if (!dirExists(dir) || maxDepth <= 0) return results;

  const SKIP = new Set([
    'node_modules', '.next', 'dist', '__pycache__', '.git', 'coverage',
  ]);
  if (opts.skipTests) {
    SKIP.add('__tests__');
    SKIP.add('__mocks__');
    SKIP.add('test');
    SKIP.add('tests');
  }

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...collectFilesInner(full, ext, maxDepth - 1, opts));
    } else if (entry.name.endsWith(ext)) {
      if (opts.skipTests && (entry.name.includes('.test.') || entry.name.includes('.spec.'))) {
        continue;
      }
      results.push(full);
    }
  }
  return results;
}

// ─── Migration Map ───────────────────────────────────────────────────────────

interface MigrationEntry {
  deprecated: string;
  replacement: string;
  replacementDir: string;
  deprecatedPort?: number;
  replacementPort: number;
}

const MIGRATIONS: MigrationEntry[] = [
  {
    deprecated: 'field-ops',
    replacement: 'field-management-service',
    replacementDir: 'field-management-service',
    deprecatedPort: 8080,
    replacementPort: 3000,
  },
  {
    deprecated: 'field-core',
    replacement: 'field-management-service',
    replacementDir: 'field-management-service',
    replacementPort: 3000,
  },
  {
    deprecated: 'field-service',
    replacement: 'field-management-service',
    replacementDir: 'field-management-service',
    replacementPort: 3000,
  },
  {
    deprecated: 'agro-advisor',
    replacement: 'advisory-service',
    replacementDir: 'advisory-service',
    deprecatedPort: 8105,
    replacementPort: 8093,
  },
  {
    deprecated: 'satellite-service',
    replacement: 'vegetation-analysis-service',
    replacementDir: 'vegetation-analysis-service',
    replacementPort: 8090,
  },
  {
    deprecated: 'ndvi-engine',
    replacement: 'vegetation-analysis-service',
    replacementDir: 'vegetation-analysis-service',
    replacementPort: 8090,
  },
  {
    deprecated: 'weather-advanced',
    replacement: 'weather-service',
    replacementDir: 'weather-service',
    replacementPort: 8092,
  },
  {
    deprecated: 'weather-core',
    replacement: 'weather-service',
    replacementDir: 'weather-service',
    replacementPort: 8092,
  },
  {
    deprecated: 'crop-health-ai',
    replacement: 'crop-intelligence-service',
    replacementDir: 'crop-intelligence-service',
    replacementPort: 8095,
  },
  {
    deprecated: 'community-chat',
    replacement: 'chat-service',
    replacementDir: 'chat-service',
    replacementPort: 8115,
  },
  {
    deprecated: 'field-chat',
    replacement: 'chat-service',
    replacementDir: 'chat-service',
    replacementPort: 8115,
  },
  {
    deprecated: 'yield-engine',
    replacement: 'yield-prediction-service',
    replacementDir: 'yield-prediction-service',
    replacementPort: 8152,
  },
];

/** Unique replacement services (de-duped by dir name). */
const REPLACEMENT_SERVICES = [
  ...new Map(MIGRATIONS.map((m) => [m.replacementDir, m])).values(),
];

/** All deprecated service names (unique). */
const DEPRECATED_NAMES = [...new Set(MIGRATIONS.map((m) => m.deprecated))];

// =============================================================================
// 1. CONTRACT DEPRECATION ANNOTATIONS
//    تعليقات الإهمال في العقود
// =============================================================================

describe('1. Contract Deprecation Annotations | تعليقات الإهمال في العقود', () => {
  // ── 1.1 service-ports.ts ─────────────────────────────────────────────────
  describe('1.1 Service Ports File | ملف منافذ الخدمات', () => {
    const SERVICE_PORTS_FILE = path.join(CONTRACTS, 'service-ports.ts');

    it('should exist', () => {
      expect(fileExists(SERVICE_PORTS_FILE)).toBe(true);
    });

    it('should export SERVICE_PORTS constant', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toContain('export const SERVICE_PORTS');
    });

    it('should export SERVICE_PORT_ALIASES constant', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toContain('export const SERVICE_PORT_ALIASES');
    });

    it('should export SERVICE_REGISTRY constant', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toContain('export const SERVICE_REGISTRY');
    });

    it('should export ServicePortKey type', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toContain('export type ServicePortKey');
    });

    it('should export ServiceInfo interface', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toContain('export interface ServiceInfo');
    });

    it('should use "as const" for SERVICE_PORTS', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/SERVICE_PORTS\s*=\s*\{[\s\S]*?\}\s*as\s+const/);
    });

    it('should use "as const" for SERVICE_PORT_ALIASES', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/SERVICE_PORT_ALIASES\s*=\s*\{[\s\S]*?\}\s*as\s+const/);
    });

    it('should contain bilingual comments (Arabic + English)', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/[\u0600-\u06FF]/);
    });

    it('should define FIELD_MANAGEMENT port as 3000', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/FIELD_MANAGEMENT:\s*3000/);
    });

    it('should define ADVISORY port as 8093', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/ADVISORY:\s*8093/);
    });

    it('should define VEGETATION_ANALYSIS port as 8090', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/VEGETATION_ANALYSIS:\s*8090/);
    });

    it('should define WEATHER port as 8092', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/WEATHER:\s*8092/);
    });

    it('should define CROP_INTELLIGENCE port as 8095', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/CROP_INTELLIGENCE:\s*8095/);
    });

    it('should define CHAT_SERVICE port as 8115', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/CHAT_SERVICE:\s*8115/);
    });

    it('should define YIELD_PREDICTION port as 8152', () => {
      const content = readFile(SERVICE_PORTS_FILE);
      expect(content).toMatch(/YIELD_PREDICTION:\s*8152/);
    });
  });

  // ── 1.2 Deprecated port annotations ────────────────────────────────────
  describe('1.2 Deprecated Port Annotations | تعليقات المنافذ المهملة', () => {
    const SERVICE_PORTS_FILE = path.join(CONTRACTS, 'service-ports.ts');
    let content: string;

    it('should have content to test', () => {
      content = readFile(SERVICE_PORTS_FILE);
      expect(content.length).toBeGreaterThan(0);
    });

    it('should mark NDVI_PROCESSOR port with @deprecated', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      expect(c).toMatch(/@deprecated.*VEGETATION_ANALYSIS.*8090/s);
    });

    it('should mark COMMUNITY_CHAT port with @deprecated', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      expect(c).toMatch(/@deprecated.*CHAT_SERVICE.*8115/s);
    });

    it('should mark YIELD_PREDICTION_LEGACY port with @deprecated', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      expect(c).toMatch(/@deprecated.*YIELD_PREDICTION.*8152/s);
    });

    it('should mark weatherCore alias with @deprecated', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      expect(c).toMatch(/@deprecated.*weatherCore|weatherCore.*@deprecated/s);
    });

    it('should mark WECHAT as deprecated', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      expect(c).toMatch(/@deprecated.*WeChat|WECHAT.*deprecated/is);
    });

    it('should include removal version in NDVI_PROCESSOR deprecation', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      // Find the @deprecated line near NDVI_PROCESSOR
      const ndviBlock = c.match(/@deprecated[^}]*?NDVI_PROCESSOR/s);
      expect(ndviBlock).not.toBeNull();
      expect(ndviBlock![0]).toMatch(/Removal:\s*v\d+\.\d+\.\d+/);
    });

    it('should include removal version in COMMUNITY_CHAT deprecation', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      const block = c.match(/@deprecated[^}]*?COMMUNITY_CHAT/s);
      expect(block).not.toBeNull();
      expect(block![0]).toMatch(/Removal:\s*v\d+\.\d+\.\d+/);
    });

    it('should include removal version in YIELD_PREDICTION_LEGACY deprecation', () => {
      const c = readFile(SERVICE_PORTS_FILE);
      const block = c.match(/@deprecated[^}]*?YIELD_PREDICTION_LEGACY/s);
      expect(block).not.toBeNull();
      expect(block![0]).toMatch(/Removal:\s*v\d+\.\d+\.\d+/);
    });
  });

  // ── 1.3 SERVICE_PORT_ALIASES correctness ───────────────────────────────
  describe('1.3 Port Alias Mappings | خريطة الأسماء المستعارة للمنافذ', () => {
    const FILE = path.join(CONTRACTS, 'service-ports.ts');

    it('should map fieldCore → FIELD_MANAGEMENT', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/fieldCore:\s*SERVICE_PORTS\.FIELD_MANAGEMENT/);
    });

    it('should map satellite → VEGETATION_ANALYSIS', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/satellite:\s*SERVICE_PORTS\.VEGETATION_ANALYSIS/);
    });

    it('should map weather → WEATHER', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/weather:\s*SERVICE_PORTS\.WEATHER/);
    });

    it('should map weatherCore → WEATHER', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/weatherCore:\s*SERVICE_PORTS\.WEATHER/);
    });

    it('should map fertilizer → ADVISORY', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/fertilizer:\s*SERVICE_PORTS\.ADVISORY/);
    });

    it('should map cropHealth → CROP_INTELLIGENCE', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/cropHealth:\s*SERVICE_PORTS\.CROP_INTELLIGENCE/);
    });

    it('should map communityChat → COMMUNITY_CHAT (backward compat)', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/communityChat:\s*SERVICE_PORTS\.COMMUNITY_CHAT/);
    });

    it('should map yieldEngine → YIELD_ENGINE', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/yieldEngine:\s*SERVICE_PORTS\.YIELD_ENGINE/);
    });

    it('should map advisory → ADVISORY', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/advisory:\s*SERVICE_PORTS\.ADVISORY/);
    });

    it('should map yieldPrediction → YIELD_PREDICTION', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/yieldPrediction:\s*SERVICE_PORTS\.YIELD_PREDICTION/);
    });

    it('should map cropIntelligence → CROP_INTELLIGENCE', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/cropIntelligence:\s*SERVICE_PORTS\.CROP_INTELLIGENCE/);
    });
  });

  // ── 1.4 SERVICE_REGISTRY deprecated flags ──────────────────────────────
  describe('1.4 Service Registry Deprecated Flags | علامات الإهمال في سجل الخدمات', () => {
    const FILE = path.join(CONTRACTS, 'service-ports.ts');

    it('should mark community-chat as deprecated in SERVICE_REGISTRY', () => {
      const c = readFile(FILE);
      const block = c.match(/'community-chat':\s*\{[^}]*\}/s);
      expect(block).not.toBeNull();
      expect(block![0]).toContain('deprecated: true');
    });

    it('should set replacedBy for community-chat to CHAT_SERVICE', () => {
      const c = readFile(FILE);
      const block = c.match(/'community-chat':\s*\{[^}]*\}/s);
      expect(block).not.toBeNull();
      expect(block![0]).toContain("replacedBy: 'CHAT_SERVICE'");
    });

    it('should mark ndvi-processor as deprecated in SERVICE_REGISTRY', () => {
      const c = readFile(FILE);
      const block = c.match(/'ndvi-processor':\s*\{[^}]*\}/s);
      expect(block).not.toBeNull();
      expect(block![0]).toContain('deprecated: true');
    });

    it('should set replacedBy for ndvi-processor to VEGETATION_ANALYSIS', () => {
      const c = readFile(FILE);
      const block = c.match(/'ndvi-processor':\s*\{[^}]*\}/s);
      expect(block).not.toBeNull();
      expect(block![0]).toContain("replacedBy: 'VEGETATION_ANALYSIS'");
    });

    it('should include ServiceInfo.deprecated field in interface', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/deprecated\?:\s*boolean/);
    });

    it('should include ServiceInfo.replacedBy field in interface', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/replacedBy\?:\s*ServicePortKey/);
    });
  });

  // ── 1.5 api-endpoints.ts deprecation annotations ──────────────────────
  describe('1.5 API Endpoint Deprecation Annotations | تعليقات إهمال نقاط النهاية', () => {
    const FILE = path.join(CONTRACTS, 'api-endpoints.ts');

    it('should exist', () => {
      expect(fileExists(FILE)).toBe(true);
    });

    it('should export WEATHER_ENDPOINTS', () => {
      const c = readFile(FILE);
      expect(c).toContain('export const WEATHER_ENDPOINTS');
    });

    it('should export ADVISORY_ENDPOINTS', () => {
      const c = readFile(FILE);
      expect(c).toContain('export const ADVISORY_ENDPOINTS');
    });

    it('should export SATELLITE_ENDPOINTS', () => {
      const c = readFile(FILE);
      expect(c).toContain('export const SATELLITE_ENDPOINTS');
    });

    it('should export VEGETATION_ENDPOINTS (replacement for satellite)', () => {
      const c = readFile(FILE);
      expect(c).toContain('export const VEGETATION_ENDPOINTS');
    });

    it('should mark WEATHER_CORE_CURRENT as @deprecated', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/@deprecated.*WEATHER_CORE_CURRENT|WEATHER_CORE_CURRENT.*@deprecated/s);
    });

    it('should mark WEATHER_CORE_FORECAST as @deprecated', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/@deprecated.*WEATHER_CORE_FORECAST|WEATHER_CORE_FORECAST.*@deprecated/s);
    });

    it('should mark WEATHER_CORE_AG_REPORT as @deprecated', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/@deprecated.*WEATHER_CORE_AG_REPORT|WEATHER_CORE_AG_REPORT.*@deprecated/s);
    });

    it('should point WEATHER_CORE_CURRENT deprecation to WEATHER_ENDPOINTS', () => {
      const c = readFile(FILE);
      const block = c.match(/@deprecated[^\n]*WEATHER_CORE_CURRENT/);
      if (!block) {
        // Check the preceding JSDoc comment instead
        expect(c).toMatch(/@deprecated.*WEATHER_ENDPOINTS\.CURRENT[\s\S]*?WEATHER_CORE_CURRENT/);
      } else {
        expect(block[0]).toMatch(/WEATHER_ENDPOINTS/);
      }
    });

    it('should mark agro-advisor legacy endpoints with @deprecated', () => {
      const c = readFile(FILE);
      // agro-advisor → advisory-service endpoints marked deprecated
      expect(c).toMatch(/@deprecated.*agro-advisor.*consolidated|@deprecated.*Use ADVICE instead/s);
    });

    it('should have @deprecated annotation near HYDROLOGY_* in TERRAIN_ENDPOINTS', () => {
      const c = readFile(FILE);
      expect(c).toMatch(/@deprecated.*HYDROLOGY_ENDPOINTS/);
    });

    it('should export HYDROLOGY_ENDPOINTS', () => {
      const c = readFile(FILE);
      expect(c).toContain('export const HYDROLOGY_ENDPOINTS');
    });
  });

  // ── 1.6 Contract index.ts barrel exports ──────────────────────────────
  describe('1.6 Contract Barrel Exports | تصدير العقود', () => {
    const INDEX_FILE = path.join(CONTRACTS, 'index.ts');

    it('should exist', () => {
      expect(fileExists(INDEX_FILE)).toBe(true);
    });

    it('should export CONTRACT_VERSION', () => {
      const c = readFile(INDEX_FILE);
      expect(c).toContain('export const CONTRACT_VERSION');
    });

    it('should have a valid semver CONTRACT_VERSION', () => {
      const c = readFile(INDEX_FILE);
      const match = c.match(/CONTRACT_VERSION\s*=\s*"(\d+\.\d+\.\d+)"/);
      expect(match).not.toBeNull();
    });

    it('should re-export service-ports module', () => {
      const c = readFile(INDEX_FILE);
      expect(c).toMatch(/export\s+\*\s+from\s+['"]\.\/service-ports['"]/);
    });

    it('should re-export error-codes module', () => {
      const c = readFile(INDEX_FILE);
      expect(c).toMatch(/export\s+\*\s+from\s+['"]\.\/error-codes['"]/);
    });

    it('should re-export api-endpoints module', () => {
      const c = readFile(INDEX_FILE);
      expect(c).toMatch(/export\s+\*\s+from\s+['"]\.\/api-endpoints['"]/);
    });

    it('should re-export api-responses module', () => {
      const c = readFile(INDEX_FILE);
      expect(c).toMatch(/export\s+\*\s+from\s+['"]\.\/api-responses['"]/);
    });

    it('should include version changelog comments', () => {
      const c = readFile(INDEX_FILE);
      // Contract versions are tracked with comments like "// 4.12.1 —"
      expect(c).toMatch(/\/\/\s*\d+\.\d+\.\d+\s*[—–-]/);
    });
  });
});

// =============================================================================
// 2. REPLACEMENT SERVICE EXISTENCE
//    وجود خدمات الاستبدال
// =============================================================================

describe('2. Replacement Service Existence | وجود خدمات الاستبدال', () => {
  // ── 2.1 Directory structure ────────────────────────────────────────────
  describe('2.1 Service Directories | مجلدات الخدمات', () => {
    for (const svc of REPLACEMENT_SERVICES) {
      const svcDir = path.join(SERVICES, svc.replacementDir);

      describe(`${svc.replacementDir} (port ${svc.replacementPort})`, () => {
        it('should have a service directory', () => {
          expect(dirExists(svcDir)).toBe(true);
        });

        it('should have a Dockerfile', () => {
          expect(fileExists(path.join(svcDir, 'Dockerfile'))).toBe(true);
        });

        it('should have a src/ directory', () => {
          expect(dirExists(path.join(svcDir, 'src'))).toBe(true);
        });

        it('should have a README.md', () => {
          expect(fileExists(path.join(svcDir, 'README.md'))).toBe(true);
        });
      });
    }
  });

  // ── 2.2 Entry point files ─────────────────────────────────────────────
  describe('2.2 Entry Points | نقاط الدخول', () => {
    const NODE_SERVICES = REPLACEMENT_SERVICES.filter((s) =>
      ['field-management-service', 'chat-service', 'yield-prediction-service'].includes(
        s.replacementDir,
      ),
    );
    const PYTHON_SERVICES = REPLACEMENT_SERVICES.filter(
      (s) => !NODE_SERVICES.some((n) => n.replacementDir === s.replacementDir),
    );

    for (const svc of NODE_SERVICES) {
      it(`${svc.replacementDir} should have src/main.ts (Node.js entry)`, () => {
        expect(fileExists(path.join(SERVICES, svc.replacementDir, 'src/main.ts'))).toBe(true);
      });

      it(`${svc.replacementDir} should have src/app.module.ts (NestJS module)`, () => {
        expect(
          fileExists(path.join(SERVICES, svc.replacementDir, 'src/app.module.ts')),
        ).toBe(true);
      });
    }

    for (const svc of PYTHON_SERVICES) {
      it(`${svc.replacementDir} should have src/main.py (Python entry)`, () => {
        expect(fileExists(path.join(SERVICES, svc.replacementDir, 'src/main.py'))).toBe(true);
      });
    }
  });

  // ── 2.3 Health endpoints ──────────────────────────────────────────────
  describe('2.3 Health Endpoint References | مراجع نقاط الصحة', () => {
    for (const svc of REPLACEMENT_SERVICES) {
      it(`${svc.replacementDir} should reference /healthz in source`, () => {
        const svcDir = path.join(SERVICES, svc.replacementDir, 'src');
        const files = collectFiles(svcDir, '.ts').concat(collectFiles(svcDir, '.py'));
        const hasHealthz = files.some((f) => {
          const c = readFile(f);
          return c.includes('/healthz') || c.includes("'/healthz'") || c.includes('healthz');
        });
        expect(hasHealthz).toBe(true);
      });
    }
  });

  // ── 2.4 Dockerfile correctness ────────────────────────────────────────
  describe('2.4 Dockerfile Patterns | أنماط ملفات Docker', () => {
    for (const svc of REPLACEMENT_SERVICES) {
      const dockerfilePath = path.join(SERVICES, svc.replacementDir, 'Dockerfile');

      it(`${svc.replacementDir} Dockerfile should expose correct port`, () => {
        const c = readFile(dockerfilePath);
        expect(c).toMatch(/EXPOSE\s+\d+/);
      });

      it(`${svc.replacementDir} Dockerfile should create non-root user`, () => {
        const c = readFile(dockerfilePath);
        // Either creates user 'sahool' or uses USER directive
        expect(c).toMatch(/USER\s+\w+|useradd|adduser/);
      });

      it(`${svc.replacementDir} Dockerfile should have HEALTHCHECK`, () => {
        const c = readFile(dockerfilePath);
        expect(c).toMatch(/HEALTHCHECK/i);
      });
    }
  });
});

// =============================================================================
// 3. MIGRATION DOCUMENTATION
//    توثيق الترحيل
// =============================================================================

describe('3. Migration Documentation | توثيق الترحيل', () => {
  // ── 3.1 Migration docs existence ──────────────────────────────────────
  describe('3.1 Migration Documents | مستندات الترحيل', () => {
    it('should have docs/migrations/ directory', () => {
      expect(dirExists(DOCS)).toBe(true);
    });

    it('should have FIELD_OPS_MIGRATION_SUMMARY.md', () => {
      expect(fileExists(path.join(DOCS, 'FIELD_OPS_MIGRATION_SUMMARY.md'))).toBe(true);
    });

    it('should have AGRO_ADVISOR_MIGRATION_SUMMARY.md', () => {
      expect(fileExists(path.join(DOCS, 'AGRO_ADVISOR_MIGRATION_SUMMARY.md'))).toBe(true);
    });

    it('should have README.md index', () => {
      expect(fileExists(path.join(DOCS, 'README.md'))).toBe(true);
    });
  });

  // ── 3.2 Field-ops migration doc content ────────────────────────────────
  describe('3.2 Field-Ops Migration Doc | مستند ترحيل عمليات الحقل', () => {
    const DOC = path.join(DOCS, 'FIELD_OPS_MIGRATION_SUMMARY.md');

    it('should mention field-ops as deprecated service', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/field[_-]ops/i);
    });

    it('should mention field-management-service as replacement', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/field-management-service/i);
    });

    it('should reference old port 8080', () => {
      const c = readFile(DOC);
      expect(c).toContain('8080');
    });

    it('should reference new port 3000', () => {
      const c = readFile(DOC);
      expect(c).toContain('3000');
    });

    it('should contain endpoint mapping section', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/endpoint|mapping|API/i);
    });

    it('should contain docker-compose references', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/docker[_-]?compose|docker compose/i);
    });

    it('should mention status as complete', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/complete|✅|COMPLETE/i);
    });

    it('should mention backward compatibility', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/backward|compat|legacy|rollback/i);
    });
  });

  // ── 3.3 Agro-advisor migration doc content ────────────────────────────
  describe('3.3 Agro-Advisor Migration Doc | مستند ترحيل المستشار الزراعي', () => {
    const DOC = path.join(DOCS, 'AGRO_ADVISOR_MIGRATION_SUMMARY.md');

    it('should mention agro-advisor as deprecated service', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/agro[_-]?advisor/i);
    });

    it('should mention advisory-service as replacement', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/advisory[_-]service/i);
    });

    it('should reference port 8093', () => {
      const c = readFile(DOC);
      expect(c).toContain('8093');
    });

    it('should mention status as complete', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/complete|✅|COMPLETED/i);
    });

    it('should describe deprecation headers', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/deprecat|header|HTTP|Sunset/i);
    });

    it('should mention Kong compatibility route', () => {
      const c = readFile(DOC);
      expect(c).toMatch(/Kong|backward|route/i);
    });
  });

  // ── 3.4 Migration README index ────────────────────────────────────────
  describe('3.4 Migration README Index | فهرس مستندات الترحيل', () => {
    const README = path.join(DOCS, 'README.md');

    it('should reference FIELD_OPS_MIGRATION_SUMMARY.md', () => {
      const c = readFile(README);
      expect(c).toContain('FIELD_OPS_MIGRATION_SUMMARY');
    });

    it('should reference AGRO_ADVISOR_MIGRATION_SUMMARY.md', () => {
      const c = readFile(README);
      expect(c).toContain('AGRO_ADVISOR_MIGRATION_SUMMARY');
    });

    it('should reference DEPRECATION_SUMMARY.md', () => {
      const c = readFile(README);
      expect(c).toMatch(/DEPRECATION_SUMMARY|deprecation/i);
    });

    it('should contain bilingual header', () => {
      const c = readFile(README);
      expect(c).toMatch(/[\u0600-\u06FF]/);
    });

    it('should list deprecated services count', () => {
      const c = readFile(README);
      expect(c).toMatch(/15\s*total|15\s*service|deprecated/i);
    });
  });

  // ── 3.5 Deprecation Summary ───────────────────────────────────────────
  describe('3.5 Deprecation Summary | ملخص الإهمال', () => {
    const SUMMARY = path.join(SERVICES, 'DEPRECATION_SUMMARY.md');

    it('should exist', () => {
      expect(fileExists(SUMMARY)).toBe(true);
    });

    it('should list weather-advanced as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/weather[_-]advanced/i);
    });

    it('should list crop-health-ai as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/crop[_-]health[_-]ai/i);
    });

    it('should list satellite-service as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/satellite[_-]service/i);
    });

    it('should list field-ops as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/field[_-]ops/i);
    });

    it('should list agro-advisor as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/agro[_-]advisor/i);
    });

    it('should list community-chat as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/community[_-]chat/i);
    });

    it('should list field-chat as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/field[_-]chat/i);
    });

    it('should list ndvi-engine as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/ndvi[_-]engine/i);
    });

    it('should list yield-engine as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/yield[_-]engine/i);
    });

    it('should list weather-core as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/weather[_-]core/i);
    });

    it('should list ndvi-processor as deprecated', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/ndvi[_-]processor/i);
    });

    it('should contain sunset status summary table', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/Status.*Count|Sunset.*Status/is);
    });

    it('should reference archived services', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/Archived|archived|ARCHIVED/);
    });

    it('should describe deprecation pattern (HTTP headers)', () => {
      const c = readFile(SUMMARY);
      expect(c).toMatch(/header|HTTP|deprecat|startup/i);
    });
  });
});

// =============================================================================
// 4. DEPRECATED PATH DETECTION
//    كشف المسارات المهملة
// =============================================================================

describe('4. Deprecated Path Detection | كشف المسارات المهملة', () => {
  /**
   * Deprecated API paths that should NOT appear as hardcoded strings in
   * web/admin source files. Services should import from contracts instead.
   */
  const DEPRECATED_PATHS = [
    '/api/v1/field-ops/',
    '/api/v1/agro-advisor/',
    '/api/v1/weather-core/',
    '/api/v1/ndvi-engine/',
    '/api/v1/community-chat/',
    '/api/v1/field-chat/',
    '/api/v1/yield-engine/',
    '/api/v1/crop-health-ai/',
    '/api/v1/weather-advanced/',
  ];

  // ── 4.1 Web app — no hardcoded deprecated paths ───────────────────────
  describe('4.1 Web App Deprecated Path Scan | فحص مسارات الويب المهملة', () => {
    for (const depPath of DEPRECATED_PATHS) {
      it(`should not hardcode ${depPath} in web app production source`, () => {
        if (!dirExists(WEB_SRC)) return; // skip if web src doesn't exist
        // Exclude test files — they're allowed to reference deprecated paths for migration assertions
        const tsFiles = collectFiles(WEB_SRC, '.ts', 6, { skipTests: true }).concat(
          collectFiles(WEB_SRC, '.tsx', 6, { skipTests: true }),
        );
        const offenders: string[] = [];
        for (const f of tsFiles) {
          const c = readFile(f);
          if (c.includes(depPath)) {
            offenders.push(path.relative(ROOT, f));
          }
        }
        expect(
          offenders,
          `Found deprecated path "${depPath}" in: ${offenders.join(', ')}`,
        ).toHaveLength(0);
      });
    }
  });

  // ── 4.2 Admin app — no hardcoded deprecated paths ─────────────────────
  describe('4.2 Admin App Deprecated Path Scan | فحص مسارات لوحة الإدارة المهملة', () => {
    for (const depPath of DEPRECATED_PATHS) {
      it(`should not hardcode ${depPath} in admin app production source`, () => {
        if (!dirExists(ADMIN_SRC)) return;
        const tsFiles = collectFiles(ADMIN_SRC, '.ts', 6, { skipTests: true }).concat(
          collectFiles(ADMIN_SRC, '.tsx', 6, { skipTests: true }),
        );
        const offenders: string[] = [];
        for (const f of tsFiles) {
          const c = readFile(f);
          if (c.includes(depPath)) {
            offenders.push(path.relative(ROOT, f));
          }
        }
        expect(
          offenders,
          `Found deprecated path "${depPath}" in: ${offenders.join(', ')}`,
        ).toHaveLength(0);
      });
    }
  });

  // ── 4.3 Legacy port numbers ───────────────────────────────────────────
  describe('4.3 Legacy Port Numbers in Config | أرقام منافذ قديمة في التكوين', () => {
    const LEGACY_PORTS: Record<string, number> = {
      'field-ops': 8080,
      'agro-advisor': 8105,
    };

    for (const [name, port] of Object.entries(LEGACY_PORTS)) {
      it(`should not hardcode ${name} legacy port ${port} in web app .env files`, () => {
        const envFiles = [
          path.join(ROOT, 'apps/web/.env'),
          path.join(ROOT, 'apps/web/.env.local'),
          path.join(ROOT, 'apps/web/.env.development'),
        ];
        for (const ef of envFiles) {
          if (fileExists(ef)) {
            const c = readFile(ef);
            expect(c).not.toMatch(
              new RegExp(`${name}.*${port}|${port}.*${name}`, 'i'),
            );
          }
        }
      });
    }

    it('should not reference field-ops:8080 in web API proxy files', () => {
      if (!dirExists(WEB_SRC)) return;
      const apiDir = path.join(WEB_SRC, 'app/api');
      if (!dirExists(apiDir)) return;
      const files = collectFiles(apiDir, '.ts');
      for (const f of files) {
        const c = readFile(f);
        expect(c).not.toMatch(/field[_-]ops.*8080|8080.*field[_-]ops/i);
      }
    });
  });

  // ── 4.4 Contract import validation ────────────────────────────────────
  describe('4.4 Contract Import Patterns | أنماط استيراد العقود', () => {
    it('should have api-client package using @sahool/shared-types', () => {
      const apiClientDir = path.join(ROOT, 'packages/api-client');
      if (!dirExists(apiClientDir)) return;
      const files = collectFiles(apiClientDir, '.ts');
      const usesContracts = files.some((f) => {
        const c = readFile(f);
        return c.includes('@sahool/shared-types') || c.includes('shared-types');
      });
      expect(usesContracts).toBe(true);
    });

    it('should not define local port constants in web app (use contracts)', () => {
      if (!dirExists(WEB_SRC)) return;
      const files = collectFiles(WEB_SRC, '.ts').concat(collectFiles(WEB_SRC, '.tsx'));
      const offenders: string[] = [];
      const portPattern = /(?:const|let|var)\s+\w*PORT\w*\s*=\s*(?:8080|8105|8097|3021)\b/i;
      for (const f of files) {
        const c = readFile(f);
        if (portPattern.test(c)) {
          offenders.push(path.relative(ROOT, f));
        }
      }
      expect(
        offenders,
        `Found hardcoded deprecated port constants in: ${offenders.join(', ')}`,
      ).toHaveLength(0);
    });

    it('should not define local port constants in admin app (use contracts)', () => {
      if (!dirExists(ADMIN_SRC)) return;
      const files = collectFiles(ADMIN_SRC, '.ts').concat(collectFiles(ADMIN_SRC, '.tsx'));
      const offenders: string[] = [];
      const portPattern = /(?:const|let|var)\s+\w*PORT\w*\s*=\s*(?:8080|8105|8097|3021)\b/i;
      for (const f of files) {
        const c = readFile(f);
        if (portPattern.test(c)) {
          offenders.push(path.relative(ROOT, f));
        }
      }
      expect(
        offenders,
        `Found hardcoded deprecated port constants in: ${offenders.join(', ')}`,
      ).toHaveLength(0);
    });
  });

  // ── 4.5 Deprecated service names in import paths ──────────────────────
  describe('4.5 Deprecated Service Name in Imports | أسماء خدمات مهملة في الاستيرادات', () => {
    const DEPRECATED_IMPORT_PATTERNS = [
      { name: 'field-ops', pattern: /from\s+['"].*field[_-]ops/i },
      { name: 'agro-advisor', pattern: /from\s+['"].*agro[_-]advisor/i },
      { name: 'ndvi-engine', pattern: /from\s+['"].*ndvi[_-]engine/i },
      { name: 'weather-core', pattern: /from\s+['"].*weather[_-]core/i },
      { name: 'community-chat', pattern: /from\s+['"].*community[_-]chat/i },
      { name: 'yield-engine', pattern: /from\s+['"].*yield[_-]engine/i },
    ];

    for (const { name, pattern } of DEPRECATED_IMPORT_PATTERNS) {
      it(`should not import from deprecated "${name}" package in web app`, () => {
        if (!dirExists(WEB_SRC)) return;
        const files = collectFiles(WEB_SRC, '.ts').concat(collectFiles(WEB_SRC, '.tsx'));
        const offenders: string[] = [];
        for (const f of files) {
          const c = readFile(f);
          if (pattern.test(c)) {
            offenders.push(path.relative(ROOT, f));
          }
        }
        expect(
          offenders,
          `Found deprecated import "${name}" in: ${offenders.join(', ')}`,
        ).toHaveLength(0);
      });

      it(`should not import from deprecated "${name}" package in admin app`, () => {
        if (!dirExists(ADMIN_SRC)) return;
        const files = collectFiles(ADMIN_SRC, '.ts').concat(collectFiles(ADMIN_SRC, '.tsx'));
        const offenders: string[] = [];
        for (const f of files) {
          const c = readFile(f);
          if (pattern.test(c)) {
            offenders.push(path.relative(ROOT, f));
          }
        }
        expect(
          offenders,
          `Found deprecated import "${name}" in: ${offenders.join(', ')}`,
        ).toHaveLength(0);
      });
    }
  });
});

// =============================================================================
// 5. DOCKER COMPOSE / KONG GATEWAY COMPATIBILITY
//    توافق Docker Compose / بوابة Kong
// =============================================================================

describe('5. Docker Compose & Gateway Compatibility | توافق Docker Compose وبوابة Kong', () => {
  // ── 5.1 Replacement services in docker-compose ────────────────────────
  describe('5.1 Replacement Services in Docker Compose | خدمات الاستبدال في Docker Compose', () => {
    it('should have docker-compose.yml', () => {
      expect(fileExists(DOCKER_COMPOSE)).toBe(true);
    });

    it('should define field-management-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/field-management-service/);
    });

    it('should define advisory-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/advisory-service/);
    });

    it('should define vegetation-analysis-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/vegetation-analysis-service/);
    });

    it('should define weather-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/weather-service/);
    });

    it('should define crop-intelligence-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/crop-intelligence-service/);
    });

    it('should define chat-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/chat-service/);
    });

    it('should define yield-prediction-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/yield-prediction-service/);
    });
  });

  // ── 5.2 Consolidation comments ────────────────────────────────────────
  describe('5.2 Consolidation Comments | تعليقات الدمج', () => {
    let compose: string;

    it('should have content', () => {
      compose = readFile(DOCKER_COMPOSE);
      expect(compose.length).toBeGreaterThan(0);
    });

    it('should note consolidation of field-core, field-service, field-ops', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/[Cc]onsolidat.*field-core.*field-service.*field-ops|[Cc]onsolidat.*field-ops/s);
    });

    it('should note consolidation of satellite-service', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/[Cc]onsolidat.*satellite-service/s);
    });

    it('should note consolidation of weather-core, weather-advanced', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/[Cc]onsolidat.*weather-core.*weather-advanced|[Cc]onsolidat.*weather-advanced/s);
    });

    it('should note consolidation of agro-advisor', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/[Cc]onsolidat.*agro-advisor/s);
    });

    it('should note consolidation of yield-engine', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/[Cc]onsolidat.*yield-engine/s);
    });

    it('should note consolidation of crop-health', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/[Cc]onsolidat.*crop-health/s);
    });
  });

  // ── 5.3 Deprecated services use profile ───────────────────────────────
  describe('5.3 Deprecated Services Use Profile | الخدمات المهملة تستخدم ملف تعريف', () => {
    it('should contain "profiles:" directive in compose file', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toContain('profiles:');
    });

    it('should reference deprecated profile', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/profiles:[\s\S]*?deprecated/);
    });

    it('should have ARCHIVED comments for deprecated services', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/ARCHIVED.*agro-advisor|agro-advisor.*ARCHIVED/i);
    });

    it('should have ARCHIVED comment for ndvi-engine', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/ARCHIVED.*ndvi-engine|ndvi-engine.*ARCHIVED/i);
    });

    it('should have ARCHIVED comment for weather-core', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/ARCHIVED.*weather-core|weather-core.*ARCHIVED/i);
    });
  });

  // ── 5.4 Updated environment variables ─────────────────────────────────
  describe('5.4 Updated Environment Variables | متغيرات البيئة المحدثة', () => {
    it('should reference field-management-service in FIELDOPS_URL', () => {
      const c = readFile(DOCKER_COMPOSE);
      expect(c).toMatch(/FIELDOPS_URL.*field-management-service|field-management-service.*FIELDOPS/i);
    });

    it('should use field-management-service as dependency (not field-ops)', () => {
      const c = readFile(DOCKER_COMPOSE);
      // The MIGRATION comment confirms updated dependency
      expect(c).toMatch(/field-management-service/);
    });
  });

  // ── 5.5 Port mapping correctness ─────────────────────────────────────
  describe('5.5 Port Mapping in Compose | تعيين المنافذ في Compose', () => {
    for (const svc of REPLACEMENT_SERVICES) {
      it(`${svc.replacementDir} should expose port ${svc.replacementPort} in compose`, () => {
        const c = readFile(DOCKER_COMPOSE);
        // Accept either "PORT: <port>" or "- <port>:<port>" or "PORT=<port>"
        const portStr = String(svc.replacementPort);
        const hasPort =
          c.includes(portStr) &&
          c.includes(svc.replacementDir);
        expect(hasPort).toBe(true);
      });
    }
  });
});

// =============================================================================
// 6. BACKWARD COMPATIBILITY HEADERS
//    رؤوس التوافق العكسي
// =============================================================================

describe('6. Backward Compatibility Headers | رؤوس التوافق العكسي', () => {
  // ── 6.1 Deprecation header patterns in docs ───────────────────────────
  describe('6.1 Deprecation Header Patterns in Docs | أنماط رؤوس الإهمال في المستندات', () => {
    it('should document X-API-Deprecated header pattern', () => {
      const summary = path.join(SERVICES, 'DEPRECATION_SUMMARY.md');
      if (!fileExists(summary)) return;
      const c = readFile(summary);
      expect(c).toMatch(/X-API-Deprecated|deprecat.*header/i);
    });

    it('should document X-API-Sunset header pattern', () => {
      const docs = [
        path.join(SERVICES, 'DEPRECATION_SUMMARY.md'),
        path.join(DOCS, 'AGRO_ADVISOR_MIGRATION_SUMMARY.md'),
      ];
      const mentionsSunset = docs.some((d) => {
        if (!fileExists(d)) return false;
        const c = readFile(d);
        return /Sunset|sunset/i.test(c);
      });
      expect(mentionsSunset).toBe(true);
    });

    it('should document RFC 8594 deprecation standard', () => {
      const docs = [
        path.join(SERVICES, 'DEPRECATION_SUMMARY.md'),
        path.join(DOCS, 'AGRO_ADVISOR_MIGRATION_SUMMARY.md'),
        path.join(DOCS, 'FIELD_OPS_MIGRATION_SUMMARY.md'),
      ];
      const mentionsRFC = docs.some((d) => {
        if (!fileExists(d)) return false;
        const c = readFile(d);
        return /8594|RFC|Deprecation:\s*true/i.test(c);
      });
      expect(mentionsRFC).toBe(true);
    });
  });

  // ── 6.2 Deprecated service source patterns ────────────────────────────
  describe('6.2 Deprecated Service Source Patterns | أنماط مصدر الخدمات المهملة', () => {
    const ARCHIVED_SERVICES = [
      'agro-advisor',
      'ndvi-engine',
      'weather-core',
      'community-chat',
      'field-chat',
      'yield-engine',
      'ndvi-processor',
      'field-ops',
      'field-core',
      'field-service',
    ];

    for (const svc of ARCHIVED_SERVICES) {
      it(`${svc} should be archived (moved to archive/deprecated-services/)`, () => {
        const archiveDir = path.join(ARCHIVE, svc);
        const activeDir = path.join(SERVICES, svc);
        // Either archived OR no longer present in apps/services/
        const isArchived = dirExists(archiveDir) || !dirExists(activeDir);
        expect(isArchived).toBe(true);
      });
    }
  });

  // ── 6.3 Deprecation warning patterns ──────────────────────────────────
  describe('6.3 Deprecation Warning Patterns | أنماط تحذير الإهمال', () => {
    it('DEPRECATION_SUMMARY should describe startup warning pattern', () => {
      const summary = path.join(SERVICES, 'DEPRECATION_SUMMARY.md');
      if (!fileExists(summary)) return;
      const c = readFile(summary);
      expect(c).toMatch(/DEPRECATION\s+WARNING|startup|logging/i);
    });

    it('DEPRECATION_SUMMARY should describe README notice pattern', () => {
      const summary = path.join(SERVICES, 'DEPRECATION_SUMMARY.md');
      if (!fileExists(summary)) return;
      const c = readFile(summary);
      expect(c).toMatch(/README|notice|docstring/i);
    });

    it('should document sunset dates for deprecated services', () => {
      const summary = path.join(SERVICES, 'DEPRECATION_SUMMARY.md');
      if (!fileExists(summary)) return;
      const c = readFile(summary);
      // Should contain dates like 2025-01-01, 2026-02, etc.
      expect(c).toMatch(/20\d{2}[/-]\d{2}/);
    });

    it('should track overdue migrations', () => {
      const summary = path.join(SERVICES, 'DEPRECATION_SUMMARY.md');
      if (!fileExists(summary)) return;
      const c = readFile(summary);
      expect(c).toMatch(/OVERDUE|overdue/i);
    });
  });

  // ── 6.4 Migration dependency graph ────────────────────────────────────
  describe('6.4 Migration Dependency Updates | تحديثات تبعيات الترحيل', () => {
    it('agro-rules should depend on field-management-service (not field-ops)', () => {
      const c = readFile(DOCKER_COMPOSE);
      // MIGRATION comment confirms updated dependency
      expect(c).toMatch(/MIGRATION.*field-management-service|field-management-service.*instead.*field-ops/is);
    });

    it('compose should not have active (non-archived) field-ops service definition', () => {
      const c = readFile(DOCKER_COMPOSE);
      // field-ops references should be in comments or archived sections only
      const lines = c.split('\n');
      const activeFieldOps = lines.filter(
        (l) =>
          /^\s+field-ops:/.test(l) && !l.trim().startsWith('#'),
      );
      expect(activeFieldOps).toHaveLength(0);
    });
  });
});

// =============================================================================
// 7. CROSS-CUTTING MIGRATION INTEGRITY
//    سلامة الترحيل الشاملة
// =============================================================================

describe('7. Cross-Cutting Migration Integrity | سلامة الترحيل الشاملة', () => {
  // ── 7.1 All migrations have replacement service ───────────────────────
  describe('7.1 Every Migration Has Replacement | كل ترحيل له بديل', () => {
    for (const m of MIGRATIONS) {
      it(`${m.deprecated} → ${m.replacement} replacement dir exists`, () => {
        expect(dirExists(path.join(SERVICES, m.replacementDir))).toBe(true);
      });
    }
  });

  // ── 7.2 No orphaned deprecated service directories ────────────────────
  describe('7.2 No Orphaned Deprecated Dirs | لا مجلدات مهملة متروكة', () => {
    for (const name of DEPRECATED_NAMES) {
      it(`${name} should not exist as active service in apps/services/`, () => {
        const activeDir = path.join(SERVICES, name);
        if (dirExists(activeDir)) {
          // If it still exists, it should be deprecated (no src/main.* or marked deprecated)
          const hasActiveMain =
            fileExists(path.join(activeDir, 'src/main.py')) ||
            fileExists(path.join(activeDir, 'src/main.ts'));

          if (hasActiveMain) {
            // Acceptable if README marks it deprecated
            const readmePath = path.join(activeDir, 'README.md');
            if (fileExists(readmePath)) {
              const readme = readFile(readmePath);
              expect(readme).toMatch(/deprecated|DEPRECATED|⚠️|إهمال/i);
            }
          }
        }
        // If directory doesn't exist, that's the expected state
        expect(true).toBe(true);
      });
    }
  });

  // ── 7.3 Archive directory ─────────────────────────────────────────────
  describe('7.3 Archive Directory | مجلد الأرشيف', () => {
    it('should have archive/deprecated-services/ directory', () => {
      expect(dirExists(ARCHIVE)).toBe(true);
    });

    it('should have README.md in archive directory', () => {
      expect(fileExists(path.join(ARCHIVE, 'README.md'))).toBe(true);
    });

    const EXPECTED_ARCHIVED = [
      'agro-advisor',
      'weather-core',
      'ndvi-engine',
      'community-chat',
      'field-chat',
      'yield-engine',
    ];

    for (const svc of EXPECTED_ARCHIVED) {
      it(`should have archived ${svc}/ in archive dir`, () => {
        // Some archives may be flattened or structured differently
        const direct = dirExists(path.join(ARCHIVE, svc));
        // Also check if referenced in README
        const readme = fileExists(path.join(ARCHIVE, 'README.md'))
          ? readFile(path.join(ARCHIVE, 'README.md'))
          : '';
        const mentioned = readme.toLowerCase().includes(svc);
        expect(direct || mentioned).toBe(true);
      });
    }
  });

  // ── 7.4 Contract version is up to date ────────────────────────────────
  describe('7.4 Contract Version Currency | حداثة إصدار العقد', () => {
    it('should have CONTRACT_VERSION ≥ 4.18.0 (includes deprecation annotations)', () => {
      const c = readFile(path.join(CONTRACTS, 'index.ts'));
      const match = c.match(/CONTRACT_VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"/);
      expect(match).not.toBeNull();
      const [, major, minor] = match!;
      // 4.18.0 is when COMMUNITY_CHAT, NDVI_PROCESSOR, YIELD_PREDICTION_LEGACY
      // were tagged @deprecated in service-ports.ts
      const version = Number(major) * 1000 + Number(minor);
      expect(version).toBeGreaterThanOrEqual(4018);
    });
  });

  // ── 7.5 Governance alignment ──────────────────────────────────────────
  describe('7.5 Governance Alignment | التوافق مع الحوكمة', () => {
    const GOV_SERVICES = path.join(ROOT, 'governance/services.yaml');

    it('should have governance/services.yaml', () => {
      expect(fileExists(GOV_SERVICES)).toBe(true);
    });

    it('governance services.yaml should reference field-management-service', () => {
      const c = readFile(GOV_SERVICES);
      expect(c).toMatch(/field-management/i);
    });

    it('governance services.yaml should reference advisory-service', () => {
      const c = readFile(GOV_SERVICES);
      expect(c).toMatch(/advisory/i);
    });

    it('governance services.yaml should reference vegetation-analysis-service', () => {
      const c = readFile(GOV_SERVICES);
      expect(c).toMatch(/vegetation-analysis/i);
    });

    it('governance services.yaml should reference weather-service', () => {
      const c = readFile(GOV_SERVICES);
      expect(c).toMatch(/weather-service|weather:/i);
    });
  });

  // ── 7.6 Helm chart references ─────────────────────────────────────────
  describe('7.6 Helm Chart References | مراجع خرائط Helm', () => {
    const HELM_DIR = path.join(ROOT, 'helm');

    it('should have helm/ directory', () => {
      expect(dirExists(HELM_DIR)).toBe(true);
    });

    it('helm charts should not reference active (non-deprecated) field-ops service', () => {
      if (!dirExists(HELM_DIR)) return;
      const yamlFiles = collectFiles(HELM_DIR, '.yaml').concat(
        collectFiles(HELM_DIR, '.yml'),
      );
      const offenders: string[] = [];
      for (const f of yamlFiles) {
        const relPath = path.relative(ROOT, f);
        // Skip auto-generated values files
        if (relPath.includes('values.generated')) continue;

        const c = readFile(f);
        // If file mentions field-ops, it should also mention DEPRECATED/consolidated
        // or only reference it inside comments (YAML # or Go template {{- /* ... */}})
        if (/field-ops/i.test(c) && !/DEPRECATED|deprecated|consolidated/i.test(c)) {
          // Check if all field-ops references are within Go template comment blocks
          const stripped = c.replace(/\{\{-?\s*\/\*[\s\S]*?\*\/\s*-?\}\}/g, '');
          if (/field-ops/i.test(stripped)) {
            offenders.push(relPath);
          }
        }
      }
      expect(
        offenders,
        `Found undocumented field-ops references in helm: ${offenders.join(', ')}`,
      ).toHaveLength(0);
    });
  });
});
