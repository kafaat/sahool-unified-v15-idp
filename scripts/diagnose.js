#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SAHOOL Platform - Comprehensive Diagnostic Tool
 * أداة التشخيص الشاملة لمنصة سهول
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Usage:
 *   npm run diagnose           # Full diagnostic
 *   npm run diagnose -- --fix  # Fix auto-fixable issues
 *   npm run diagnose -- --py   # Python only
 *   npm run diagnose -- --js   # JavaScript/TypeScript only
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors for terminal output
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

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
  fix: args.includes('--fix'),
  pyOnly: args.includes('--py'),
  jsOnly: args.includes('--js'),
  security: args.includes('--security'),
  all: !args.includes('--py') && !args.includes('--js') && !args.includes('--security'),
};

// Allowlist of safe commands for diagnostic purposes
const ALLOWED_COMMANDS = new Set([
  'ruff', 'pyright', 'bandit', 'vulture', 'safety',
  'npx', 'npm', 'docker', 'which', 'where'
]);

// Validate command against allowlist
function isAllowedCommand(cmd) {
  const baseCommand = cmd.split(/\s+/)[0];
  return ALLOWED_COMMANDS.has(baseCommand) || baseCommand === 'npx' || baseCommand === 'npm' || baseCommand === 'docker';
}

// Run a command and return result (with allowlist validation)
function runCommand(cmd, description, ignoreError = false) {
  log.subheader(description);

  // Security: validate command against allowlist
  if (!isAllowedCommand(cmd)) {
    log.error(`Command not in allowlist: ${cmd.split(/\s+/)[0]}`);
    return { success: false, output: 'Command not allowed' };
  }

  try {
    // nosemgrep: javascript.lang.security.detect-child-process.detect-child-process  -- internal CLI tool, cmd from allowlist
    const output = execSync(cmd, {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
      maxBuffer: 50 * 1024 * 1024 // 50MB buffer
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
    if (error.stdout) console.log(error.stdout);
    if (error.stderr) console.log(error.stderr);
    return { success: false, output: error.message };
  }
}

// Check if a command exists (only for allowed commands)
function commandExists(cmd) {
  // Security: only check for commands in our allowlist
  if (!ALLOWED_COMMANDS.has(cmd)) {
    return false;
  }
  try {
    // Use platform-specific command lookup
    const checkCmd = process.platform === 'win32' ? `where ${cmd}` : `which ${cmd}`;
    execSync(checkCmd, { stdio: 'pipe' }); // nosemgrep: javascript.lang.security.detect-child-process.detect-child-process
    return true;
  } catch {
    return false;
  }
}

// Main diagnostic functions
const diagnostics = {
  // Python diagnostics
  python: {
    ruff: () => {
      if (!commandExists('ruff')) {
        log.warn('ruff غير مثبت - pip install ruff');
        return;
      }
      const fixFlag = options.fix ? '--fix --unsafe-fixes' : '';
      runCommand(`ruff check ${fixFlag} apps/ shared/`, 'فحص Python بـ Ruff', true);
      if (options.fix) {
        runCommand('ruff format apps/ shared/', 'تنسيق Python', true);
      }
    },

    pyright: () => {
      if (!commandExists('pyright')) {
        log.warn('pyright غير مثبت - pip install pyright');
        return;
      }
      runCommand('pyright shared/ai/', 'فحص الأنواع بـ Pyright', true);
    },

    bandit: () => {
      if (!commandExists('bandit')) {
        log.warn('bandit غير مثبت - pip install bandit');
        return;
      }
      runCommand('bandit -r shared/ apps/services/ -ll -q', 'فحص أمني بـ Bandit', true);
    },

    vulture: () => {
      if (!commandExists('vulture')) {
        log.warn('vulture غير مثبت - pip install vulture');
        return;
      }
      runCommand('vulture shared/ apps/kernel/ --min-confidence 90', 'كشف الكود الميت', true);
    },
  },

  // JavaScript/TypeScript diagnostics
  javascript: {
    oxlint: () => {
      runCommand('npx oxlint .', 'فحص JS/TS بـ oxlint', true);
    },

    biome: () => {
      const fixFlag = options.fix ? '--apply' : '';
      runCommand(`npx biome check ${fixFlag} .`, 'فحص بـ Biome', true);
    },

    typescript: () => {
      runCommand('npx tsc --noEmit', 'فحص TypeScript', true);
    },

    knip: () => {
      runCommand('npx knip', 'كشف الكود والتبعيات الميتة', true);
    },

    depcheck: () => {
      runCommand('npx depcheck', 'فحص التبعيات غير المستخدمة', true);
    },
  },

  // Security diagnostics
  security: {
    npmAudit: () => {
      runCommand('npm audit --audit-level=moderate', 'فحص أمني npm', true);
    },

    safety: () => {
      if (!commandExists('safety')) {
        log.warn('safety غير مثبت - pip install safety');
        return;
      }
      runCommand('safety check', 'فحص أمني Python', true);
    },
  },

  // Infrastructure diagnostics
  infrastructure: {
    docker: () => {
      runCommand('docker compose config --quiet', 'فحص Docker Compose', true);
    },

    containers: () => {
      runCommand('docker compose ps', 'حالة الحاويات', true);
    },
  },
};

// Main execution
async function main() {
  console.log(`
${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${colors.reset}
${colors.bright}   🔍 SAHOOL Platform Diagnostic Suite | أداة تشخيص منصة سهول${colors.reset}
${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${colors.reset}
`);

  const startTime = Date.now();
  const results = { passed: 0, failed: 0, warnings: 0 };

  // Python diagnostics
  if (options.all || options.pyOnly) {
    log.header('🐍 Python Diagnostics | تشخيص Python');
    diagnostics.python.ruff();
    diagnostics.python.pyright();
    diagnostics.python.bandit();
    diagnostics.python.vulture();
  }

  // JavaScript/TypeScript diagnostics
  if (options.all || options.jsOnly) {
    log.header('📦 JavaScript/TypeScript Diagnostics | تشخيص JS/TS');
    diagnostics.javascript.oxlint();
    diagnostics.javascript.typescript();
    diagnostics.javascript.knip();
  }

  // Security diagnostics
  if (options.all || options.security) {
    log.header('🔐 Security Diagnostics | التشخيص الأمني');
    diagnostics.security.npmAudit();
    diagnostics.security.safety();
  }

  // Infrastructure diagnostics
  if (options.all) {
    log.header('🐳 Infrastructure Diagnostics | تشخيص البنية التحتية');
    diagnostics.infrastructure.docker();
    diagnostics.infrastructure.containers();
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
