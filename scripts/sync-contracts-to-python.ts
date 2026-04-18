#!/usr/bin/env tsx
/**
 * SAHOOL TS → Python Contracts Sync
 * =================================
 *
 * Regenerates `shared/contracts_py/service_ports.py` from the
 * TypeScript source of truth at
 * `packages/shared-types/src/contracts/service-ports.ts`.
 *
 * Approach: lightweight regex-based parse (no TS compiler dependency).
 *   1. Read TS file
 *   2. Strip block/line comments
 *   3. Locate `SERVICE_PORTS = { ... } as const`
 *   4. Extract `KEY: <number>` pairs
 *   5. Emit a frozen dataclass Python module
 *
 * Usage:
 *   npx tsx scripts/sync-contracts-to-python.ts
 *   npx tsx scripts/sync-contracts-to-python.ts --out /tmp/check.py
 *
 * Exit 0 on success, 1 on parse errors.
 */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, "..");

const TS_SOURCE = resolve(
  REPO_ROOT,
  "packages/shared-types/src/contracts/service-ports.ts",
);
const DEFAULT_PY_OUT = resolve(REPO_ROOT, "shared/contracts_py/service_ports.py");
const TS_REL = "packages/shared-types/src/contracts/service-ports.ts";

interface ParsedEntry {
  key: string;
  port: number;
  deprecated: boolean;
}

/** Strip /* ... *\/ and // ... comments while preserving line structure. */
function stripComments(src: string): string {
  // Remove block comments (non-greedy, multi-line).
  let out = src.replace(/\/\*[\s\S]*?\*\//g, (m) =>
    m.replace(/[^\n]/g, " "),
  );
  // Remove line comments.
  out = out.replace(/\/\/[^\n]*/g, "");
  return out;
}

/** Extract the SERVICE_PORTS object body using balanced-brace scanning. */
function extractObjectBody(src: string, identifier: string): string {
  // Validate identifier shape so no regex metachars can sneak in.
  if (!/^[A-Z][A-Z0-9_]*$/.test(identifier)) {
    throw new Error(`Invalid identifier (must be UPPER_SNAKE_CASE): ${identifier}`);
  }
  // Locate `export const <IDENTIFIER>` via plain indexOf, then verify the
  // surrounding context with literal regexes. Avoids `new RegExp(dynamic)`
  // so Semgrep's detect-non-literal-regexp rule is satisfied and there is
  // no ReDoS surface even if `identifier` were ever attacker-controlled.
  const needle = `export const ${identifier}`;
  let searchFrom = 0;
  while (searchFrom < src.length) {
    const found = src.indexOf(needle, searchFrom);
    if (found === -1) break;
    // Require a word-boundary after the identifier so `SERVICE_PORTS`
    // doesn't match `SERVICE_PORTS_ALIASES`.
    const afterIdent = src.charCodeAt(found + needle.length);
    const isWordChar =
      (afterIdent >= 48 && afterIdent <= 57) || // 0-9
      (afterIdent >= 65 && afterIdent <= 90) || // A-Z
      (afterIdent >= 97 && afterIdent <= 122) || // a-z
      afterIdent === 95; // _
    if (isWordChar) {
      searchFrom = found + 1;
      continue;
    }
    // After the identifier we expect `<whitespace>=<whitespace>{`.
    const tail = src.slice(found + needle.length);
    const tailMatch = /^\s*=\s*\{/.exec(tail);
    if (!tailMatch) {
      searchFrom = found + 1;
      continue;
    }
    const openIdx = found + needle.length + tailMatch[0].length - 1;
    let depth = 0;
    for (let i = openIdx; i < src.length; i++) {
      const ch = src[i];
      if (ch === "{") depth++;
      else if (ch === "}") {
        depth--;
        if (depth === 0) return src.slice(openIdx + 1, i);
      }
    }
    throw new Error(`Unbalanced braces while parsing ${identifier}`);
  }
  throw new Error(`Could not locate "export const ${identifier} = {" in TS source`);
}

/** Return the index of `<KEY>: <digit>` in `src`, or -1.
 *
 * Word boundary: preceding char must NOT be an identifier character.
 * Uses literal regexes + indexOf walking so no dynamic RegExp is built
 * from the caller-supplied key (Semgrep detect-non-literal-regexp).
 */
function _findKeyDeclaration(src: string, key: string): number {
  let searchFrom = 0;
  while (searchFrom < src.length) {
    const found = src.indexOf(key, searchFrom);
    if (found === -1) return -1;
    // Preceding char must not be an identifier continuation.
    if (found > 0) {
      const prev = src.charCodeAt(found - 1);
      const isIdentChar =
        (prev >= 48 && prev <= 57) || // 0-9
        (prev >= 65 && prev <= 90) || // A-Z
        (prev >= 97 && prev <= 122) || // a-z
        prev === 95; // _
      if (isIdentChar) {
        searchFrom = found + 1;
        continue;
      }
    }
    const tail = src.slice(found + key.length);
    if (/^\s*:\s*\d/.test(tail)) return found;
    searchFrom = found + 1;
  }
  return -1;
}

function parseEntries(body: string, originalSrc: string): ParsedEntry[] {
  const entries: ParsedEntry[] = [];
  // Match `KEY: 1234,` allowing whitespace and optional trailing comma/newline.
  const re = /([A-Z][A-Z0-9_]*)\s*:\s*(\d+)\s*,?/g;
  let m: RegExpExecArray | null;
  const seen = new Set<string>();
  while ((m = re.exec(body)) !== null) {
    const key = m[1];
    const port = Number.parseInt(m[2], 10);
    if (seen.has(key)) {
      throw new Error(`Duplicate key in SERVICE_PORTS: ${key}`);
    }
    seen.add(key);
    // Detect @deprecated by looking at the ORIGINAL source's JSDoc immediately
    // above this key declaration. Find `KEY: <digits>` in originalSrc, walk
    // backward to the nearest `*/` closing a JSDoc block, and check that block.
    //
    // `key` was just captured by the outer regex which matches
    // /[A-Z][A-Z0-9_]*/ — so it cannot contain regex metacharacters and the
    // interpolation below is safe. Extra guard anyway.
    if (!/^[A-Z][A-Z0-9_]*$/.test(key)) {
      throw new Error(`Malformed key: ${key}`);
    }
    // Locate `<KEY>: <digit>` in the original source without building a
    // dynamic RegExp. Walk indexOf matches and verify the boundary +
    // suffix with literal regexes — avoids Semgrep's
    // detect-non-literal-regexp finding and removes the ReDoS surface.
    const declMatch = _findKeyDeclaration(originalSrc, key);
    let deprecated = false;
    if (declMatch !== -1) {
      const before = originalSrc.slice(0, declMatch);
      const lastClose = before.lastIndexOf("*/");
      if (lastClose !== -1) {
        const afterClose = before.slice(lastClose + 2);
        // Only count the JSDoc if nothing but whitespace/comma/newline separates
        // it from the key declaration (i.e., it is THIS key's JSDoc).
        if (/^[\s,]*$/.test(afterClose)) {
          const blockStart = before.lastIndexOf("/**", lastClose);
          if (blockStart !== -1) {
            const block = before.slice(blockStart, lastClose);
            if (/@deprecated/.test(block)) deprecated = true;
          }
        }
      }
    }
    entries.push({ key, port, deprecated });
  }
  if (entries.length === 0) {
    throw new Error("Parsed zero entries from SERVICE_PORTS — parser likely broken");
  }
  return entries;
}

function renderPython(entries: ParsedEntry[]): string {
  const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const lines: string[] = [];
  lines.push('"""');
  lines.push("SAHOOL Unified Service Ports Registry (Python mirror).");
  lines.push("");
  lines.push("AUTO-GENERATED — DO NOT EDIT BY HAND.");
  lines.push(`Source: ${TS_REL}`);
  lines.push(`Generated: ${timestamp}`);
  lines.push("Regenerate via: npx tsx scripts/sync-contracts-to-python.ts");
  lines.push('"""');
  lines.push("");
  lines.push("from __future__ import annotations");
  lines.push("");
  lines.push("from dataclasses import dataclass");
  lines.push("");
  lines.push("");
  lines.push("@dataclass(frozen=True)");
  lines.push("class ServicePorts:");
  lines.push('    """Frozen dataclass mirroring the TS ``SERVICE_PORTS`` record."""');
  lines.push("");
  for (const e of entries) {
    const suffix = e.deprecated ? "  # deprecated" : "";
    lines.push(`    ${e.key}: int = ${e.port}${suffix}`);
  }
  lines.push("");
  lines.push("");
  lines.push("#: Module-level singleton for convenient imports.");
  lines.push("SERVICE_PORTS: ServicePorts = ServicePorts()");
  lines.push("");
  return lines.join("\n");
}

function main(): void {
  const args = process.argv.slice(2);
  let outPath = DEFAULT_PY_OUT;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--out" && args[i + 1]) {
      outPath = resolve(args[i + 1]);
      i++;
    }
  }

  let src: string;
  try {
    src = readFileSync(TS_SOURCE, "utf8");
  } catch (err) {
    console.error(`[sync-contracts] Failed to read TS source: ${String(err)}`);
    process.exit(1);
  }

  try {
    const stripped = stripComments(src);
    const body = extractObjectBody(stripped, "SERVICE_PORTS");
    const entries = parseEntries(body, src);
    const py = renderPython(entries);
    mkdirSync(dirname(outPath), { recursive: true });
    writeFileSync(outPath, py, "utf8");
    console.log(
      `[sync-contracts] Wrote ${entries.length} entries to ${outPath}`,
    );
  } catch (err) {
    console.error(`[sync-contracts] Parse/generate failed: ${String(err)}`);
    process.exit(1);
  }
}

main();
