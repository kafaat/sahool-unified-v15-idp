#!/usr/bin/env npx tsx
/**
 * SAHOOL Dart Hardcoded Path Scanner
 * فحص المسارات المضمّنة في الجوال
 *
 * Scans the Flutter mobile codebase for Dart files that construct API
 * URLs using interpolation of `baseUrl` with hardcoded path suffixes
 * (e.g. `'$_baseUrl/fields'` or `'$apiUrl/api/v1/weather'`). All API
 * paths must come from `apps/mobile/lib/core/contracts/api_endpoints.dart`.
 *
 * Usage:
 *   npx tsx scripts/check-dart-hardcoded-paths.ts            # Report
 *   npx tsx scripts/check-dart-hardcoded-paths.ts --strict   # Exit 1 on violations
 *
 * @version 1.0.0
 */

import { readFileSync, readdirSync, statSync, existsSync } from "fs";
import { resolve, join, dirname, relative } from "path";

const ROOT = resolve(dirname(new URL(import.meta.url).pathname), "..");
const MOBILE_ROOTS = [
  resolve(ROOT, "apps/mobile/lib"),
  resolve(ROOT, "apps/mobile/sahool_field_app/lib"),
  resolve(ROOT, "apps/mobile/sahol_atmosphere/lib"),
];
const CONTRACTS_FILE = resolve(
  ROOT,
  "apps/mobile/lib/core/contracts/api_endpoints.dart",
);

const STRICT = process.argv.includes("--strict");

/**
 * Files that are intentionally exempt (contract file itself, tests, config).
 */
const EXEMPT_FILE_PATTERNS = [
  /\/contracts\/api_endpoints\.dart$/,
  /\/contracts\/service_ports\.dart$/,
  /\/contracts\/error_codes\.dart$/,
  /\/test\//,
  /_test\.dart$/,
  /\.g\.dart$/,
  /\.freezed\.dart$/,
  /\/generated\//,
  /\/config\/api_config\.dart$/,   // baseUrl config file
  /\/config\/environment\.dart$/,
];

/**
 * Patterns that indicate a hardcoded API path literal.
 * Match cases:
 *   '$_baseUrl/fields'
 *   '$baseUrl/api/v1/something'
 *   "/api/v1/fields" (anywhere)
 *   `${apiBase}/weather/current`
 */
const HARDCODED_PATTERNS: Array<{ re: RegExp; label: string }> = [
  {
    re: /['"`]\$[a-zA-Z_][a-zA-Z0-9_]*\/(api\/v1\/|[a-z][a-z-]+(?:\/|['"`]))/g,
    label: "Interpolated baseUrl with hardcoded path segment",
  },
  {
    re: /['"`]\/api\/v1\/[^'"`]+['"`]/g,
    label: "Literal /api/v1/ path string",
  },
];

interface Violation {
  file: string;
  line: number;
  col: number;
  snippet: string;
  pattern: string;
}

function walk(dir: string, exts: string[] = [".dart"]): string[] {
  const out: string[] = [];
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    if (/^(node_modules|\.dart_tool|build|\.git|ios|android|macos|linux|windows)$/.test(name))
      continue;
    const full = join(dir, name);
    try {
      const st = statSync(full);
      if (st.isDirectory()) out.push(...walk(full, exts));
      else if (exts.some((e) => name.endsWith(e))) out.push(full);
    } catch {
      // skip
    }
  }
  return out;
}

function isExempt(file: string): boolean {
  return EXEMPT_FILE_PATTERNS.some((re) => re.test(file));
}

function stripComments(src: string): string {
  // Blank out // line comments and /* block */ comments to avoid false positives
  return src
    .replace(/\/\*[\s\S]*?\*\//g, (m) => " ".repeat(m.length))
    .replace(/^\s*\/\/.*$/gm, (m) => " ".repeat(m.length));
}

function scanFile(file: string): Violation[] {
  let src: string;
  try {
    src = readFileSync(file, "utf-8");
  } catch {
    return [];
  }
  const cleaned = stripComments(src);
  const violations: Violation[] = [];

  for (const { re, label } of HARDCODED_PATTERNS) {
    re.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(cleaned))) {
      // Find line/col
      const upto = cleaned.slice(0, m.index);
      const line = upto.split(/\r?\n/).length;
      const lastNl = upto.lastIndexOf("\n");
      const col = m.index - (lastNl + 1) + 1;
      violations.push({
        file,
        line,
        col,
        snippet: m[0].length > 120 ? m[0].slice(0, 117) + "..." : m[0],
        pattern: label,
      });
    }
  }

  return violations;
}

function main() {
  if (!existsSync(CONTRACTS_FILE)) {
    console.error(
      `❌ Contract file not found: ${relative(ROOT, CONTRACTS_FILE)}`,
    );
    console.error("   Run: npx tsx scripts/sync-contracts-to-dart.ts");
    process.exit(1);
  }

  const files = MOBILE_ROOTS.flatMap((r) => walk(r)).filter((f) => !isExempt(f));

  const allViolations: Violation[] = [];
  for (const file of files) {
    allViolations.push(...scanFile(file));
  }

  console.log(
    `🔍 Scanned ${files.length} Dart files for hardcoded API paths\n`,
  );

  if (allViolations.length === 0) {
    console.log("✅ No hardcoded API paths detected.");
    return;
  }

  // Group by file for readability
  const byFile = new Map<string, Violation[]>();
  for (const v of allViolations) {
    const arr = byFile.get(v.file) ?? [];
    arr.push(v);
    byFile.set(v.file, arr);
  }

  for (const [file, vs] of byFile) {
    console.log(`\n${relative(ROOT, file)}`);
    for (const v of vs.slice(0, 5)) {
      console.log(`  ${v.line}:${v.col}  ${v.pattern}`);
      console.log(`       ${v.snippet}`);
    }
    if (vs.length > 5) {
      console.log(`  … and ${vs.length - 5} more in this file`);
    }
  }

  console.log(
    `\n❌ Found ${allViolations.length} hardcoded path literal(s) in ${byFile.size} file(s).`,
  );
  console.log(
    "   Import the endpoint from 'package:.../core/contracts/api_endpoints.dart'",
  );
  console.log(
    "   (AuthEndpoints, FieldEndpoints, WeatherEndpoints, ...) instead.",
  );

  if (STRICT) {
    process.exit(1);
  }
}

main();
