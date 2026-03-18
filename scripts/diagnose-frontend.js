#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SAHOOL Platform - Frontend & Mobile Diagnostic Tool
 * أداة تشخيص الواجهات والتطبيق المحمول لمنصة سهول
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Usage:
 *   node scripts/diagnose-frontend.js           # Full diagnostic
 *   node scripts/diagnose-frontend.js --fix     # Fix auto-fixable issues
 *   node scripts/diagnose-frontend.js --web     # Web apps only
 *   node scripts/diagnose-frontend.js --mobile  # Mobile app only
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
};

const log = {
  info: (msg) => console.log(`${colors.cyan}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✅${colors.reset} ${msg}`),
  warn: (msg) => console.log(`${colors.yellow}⚠️${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}❌${colors.reset} ${msg}`),
  header: (msg) => console.log(`\n${colors.bright}${colors.blue}═══ ${msg} ═══${colors.reset}\n`),
  subheader: (msg) => console.log(`${colors.magenta}▶ ${msg}${colors.reset}`),
};

// Parse arguments
const args = process.argv.slice(2);
const options = {
  fix: args.includes('--fix'),
  webOnly: args.includes('--web'),
  mobileOnly: args.includes('--mobile'),
  all: !args.includes('--web') && !args.includes('--mobile'),
};

// Run command helper
function runCommand(cmd, description, cwd = '.', ignoreError = true) {
  log.subheader(description);
  try {
    // nosemgrep: javascript.lang.security.detect-child-process.detect-child-process  -- internal CLI tool, no user input
    const output = execSync(cmd, {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: cwd,
      maxBuffer: 50 * 1024 * 1024,
    });
    if (output.trim()) {
      console.log(output);
    }
    log.success(`${description} - تم بنجاح`);
    return { success: true, output };
  } catch (error) {
    if (ignoreError) {
      if (error.stdout) console.log(error.stdout);
      if (error.stderr) console.log(error.stderr);
      log.warn(`${description} - يوجد مشاكل`);
      return { success: false, output: error.stdout || error.stderr };
    }
    log.error(`${description} - فشل`);
    return { success: false, output: error.message };
  }
}

// Check if directory exists
function dirExists(dir) {
  return fs.existsSync(path.join(process.cwd(), dir));
}

// ═══════════════════════════════════════════════════════════════════════════════
// Web Frontend Diagnostics
// ═══════════════════════════════════════════════════════════════════════════════
const webDiagnostics = {
  // Web Dashboard (Next.js/React)
  web: () => {
    if (!dirExists('apps/web')) {
      log.warn('apps/web غير موجود');
      return;
    }
    log.header('🌐 Web Dashboard | لوحة القيادة');

    const fixFlag = options.fix ? '--fix' : '';

    // ESLint
    runCommand(`npm run lint ${fixFlag}`.trim(), 'ESLint - فحص الكود', 'apps/web');

    // TypeScript
    runCommand('npx tsc --noEmit', 'TypeScript - فحص الأنواع', 'apps/web');

    // Biome (if available)
    if (fs.existsSync('biome.json')) {
      const biomeFlag = options.fix ? '--apply' : '';
      runCommand(`npx biome check ${biomeFlag} src/`.trim(), 'Biome - فحص وتنسيق', 'apps/web');
    }
  },

  // Admin Portal (React)
  admin: () => {
    if (!dirExists('apps/admin')) {
      log.warn('apps/admin غير موجود');
      return;
    }
    log.header('👤 Admin Portal | بوابة الإدارة');

    const fixFlag = options.fix ? '--fix' : '';

    // ESLint
    runCommand(`npm run lint ${fixFlag}`.trim(), 'ESLint - فحص الكود', 'apps/admin');

    // TypeScript
    runCommand('npx tsc --noEmit', 'TypeScript - فحص الأنواع', 'apps/admin');
  },

  // Shared Packages
  packages: () => {
    if (!dirExists('packages')) {
      log.warn('packages غير موجود');
      return;
    }
    log.header('📦 Shared Packages | الحزم المشتركة');

    const packages = [
      'shared-ui',
      'shared-utils',
      'shared-types',
      'shared-hooks',
      'api-client',
      'design-system',
    ];

    for (const pkg of packages) {
      const pkgPath = `packages/${pkg}`;
      if (dirExists(pkgPath)) {
        runCommand('npm run lint --if-present', `${pkg} - فحص`, pkgPath);
      }
    }
  },

  // Run tests
  tests: () => {
    log.header('🧪 Frontend Tests | اختبارات الواجهات');
    runCommand('npm run test --workspaces --if-present', 'Vitest - الاختبارات');
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Mobile App Diagnostics (Flutter)
// ═══════════════════════════════════════════════════════════════════════════════
const mobileDiagnostics = {
  // Flutter Analysis
  analyze: () => {
    if (!dirExists('apps/mobile')) {
      log.warn('apps/mobile غير موجود');
      return;
    }
    log.header('📱 Mobile App Analysis | تحليل التطبيق المحمول');

    // Dart Analyzer
    runCommand('flutter analyze', 'Dart Analyzer - تحليل الكود', 'apps/mobile');
  },

  // Flutter Format
  format: () => {
    if (!dirExists('apps/mobile')) return;

    log.header('🎨 Mobile Code Formatting | تنسيق الكود');

    if (options.fix) {
      runCommand('dart format .', 'Dart Format - تنسيق', 'apps/mobile');
    } else {
      runCommand('dart format --set-exit-if-changed .', 'Dart Format - فحص التنسيق', 'apps/mobile');
    }
  },

  // Flutter Fix
  fix: () => {
    if (!dirExists('apps/mobile') || !options.fix) return;

    log.header('🔧 Mobile Auto-Fix | الإصلاح التلقائي');
    runCommand('dart fix --apply', 'Dart Fix - إصلاح تلقائي', 'apps/mobile');
  },

  // Flutter Tests
  tests: () => {
    if (!dirExists('apps/mobile')) return;

    log.header('🧪 Mobile Tests | اختبارات التطبيق');
    runCommand('flutter test', 'Flutter Test - الاختبارات', 'apps/mobile');
  },

  // Dependency Check
  dependencies: () => {
    if (!dirExists('apps/mobile')) return;

    log.header('📋 Mobile Dependencies | التبعيات');
    runCommand('flutter pub outdated', 'Outdated Packages - الحزم القديمة', 'apps/mobile');
  },

  // Build Check
  buildCheck: () => {
    if (!dirExists('apps/mobile')) return;

    log.header('🏗️ Build Check | فحص البناء');
    runCommand('flutter build apk --debug --analyze-size', 'APK Build Check', 'apps/mobile');
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Main Execution
// ═══════════════════════════════════════════════════════════════════════════════
async function main() {
  console.log(`
${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${colors.reset}
${colors.bright}   🔍 SAHOOL Frontend & Mobile Diagnostic Suite${colors.reset}
${colors.bright}   أداة تشخيص الواجهات والتطبيق المحمول${colors.reset}
${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${colors.reset}
`);

  const startTime = Date.now();

  // Web Diagnostics
  if (options.all || options.webOnly) {
    webDiagnostics.web();
    webDiagnostics.admin();
    webDiagnostics.packages();
    webDiagnostics.tests();
  }

  // Mobile Diagnostics
  if (options.all || options.mobileOnly) {
    mobileDiagnostics.analyze();
    mobileDiagnostics.format();
    mobileDiagnostics.fix();
    mobileDiagnostics.tests();
    mobileDiagnostics.dependencies();
  }

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);

  console.log(`
${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${colors.reset}
${colors.bright}   ✅ Diagnostic Complete | اكتمل التشخيص${colors.reset}
${colors.cyan}   ⏱️  Duration: ${duration}s | المدة: ${duration} ثانية${colors.reset}
${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${colors.reset}
`);

  if (options.fix) {
    log.info('تم تطبيق الإصلاحات التلقائية. راجع التغييرات قبل الـ commit.');
  }
}

main().catch(console.error);
