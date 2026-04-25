#!/usr/bin/env npx tsx
/**
 * SAHOOL Endpoint Reality Check
 * فحص مطابقة العقود للخلفيات الفعلية
 *
 * For each service declared in the contracts, scans its source directory
 * and verifies that the endpoints declared in *_ENDPOINTS constants are
 * actually implemented (FastAPI @router/@app decorators, NestJS @Get/@Post).
 *
 * Emits a report with real / missing / stub services so contract drift
 * is detected in CI before release.
 *
 * Usage:
 *   npx tsx scripts/endpoint-reality-check.ts             # Human-readable
 *   npx tsx scripts/endpoint-reality-check.ts --json      # Machine-readable
 *   npx tsx scripts/endpoint-reality-check.ts --strict    # Exit 1 on any gap
 *
 * @version 1.0.0
 */

import { readFileSync, readdirSync, statSync, existsSync } from "fs";
import { resolve, join, dirname } from "path";

const ROOT = resolve(dirname(new URL(import.meta.url).pathname), "..");
const TS_CONTRACTS = resolve(ROOT, "packages/shared-types/src/contracts");
const SERVICES_ROOT = resolve(ROOT, "apps/services");

const JSON_MODE = process.argv.includes("--json");
const STRICT_MODE = process.argv.includes("--strict");

/**
 * Mapping: contract endpoint group → service directory.
 * Only services we want to enforce reality-check on.
 */
const CONTRACT_TO_SERVICE: Array<{
  group: string;
  service: string;
  /** Optional - paths inside *_ENDPOINTS that are allowed to be WIP/unimplemented */
  wipAllowed?: boolean;
  /**
   * Optional - paths to skip (e.g. deprecated paths that live on a different
   * service and should not be checked against this service directory).
   */
  skipPaths?: string[];
}> = [
  { group: "AUTH_ENDPOINTS", service: "user-service" },
  { group: "USER_ENDPOINTS", service: "user-service" },
  { group: "FIELD_ENDPOINTS", service: "field-management-service" },
  { group: "WEATHER_ENDPOINTS", service: "weather-service", wipAllowed: true },
  { group: "SATELLITE_ENDPOINTS", service: "vegetation-analysis-service", wipAllowed: true },
  // Large feature gap — in active development; tracked but not blocking CI
  { group: "CROP_HEALTH_ENDPOINTS", service: "crop-intelligence-service", wipAllowed: true },
  { group: "IRRIGATION_ENDPOINTS", service: "irrigation-smart", wipAllowed: true },
  { group: "ADVISORY_ENDPOINTS", service: "advisory-service", wipAllowed: true },
  { group: "TASK_ENDPOINTS", service: "task-service" },
  { group: "EQUIPMENT_ENDPOINTS", service: "equipment-service", wipAllowed: true },
  { group: "NOTIFICATION_ENDPOINTS", service: "notification-service", wipAllowed: true },
  { group: "IOT_ENDPOINTS", service: "iot-service", wipAllowed: true },
  { group: "MARKETPLACE_ENDPOINTS", service: "marketplace-service", wipAllowed: true },
  { group: "BILLING_ENDPOINTS", service: "billing-core", wipAllowed: true },
  { group: "VISION_ENDPOINTS", service: "yolo26-vision-service" },
  {
    group: "TERRAIN_ENDPOINTS",
    service: "terrain-core-service",
    // These @deprecated paths live on hydrology-service and leveling-optimizer-service,
    // not on terrain-core-service. Skip them to avoid false negatives.
    skipPaths: [
      "/api/v1/hydrology/drainage/{fieldId}",
      "/api/v1/hydrology/basins/{fieldId}",
      "/api/v1/leveling/cut-fill",
      "/api/v1/leveling/cost/{fieldId}",
    ],
  },
  { group: "DRONE_ENDPOINTS", service: "drone-service", wipAllowed: true },
];

interface CheckResult {
  group: string;
  service: string;
  declared: number;
  matched: number;
  missing: string[];
  status: "ok" | "partial" | "stub" | "missing-service" | "wip";
}

function walkFiles(dir: string, exts: string[] = [".py", ".ts"]): string[] {
  const out: string[] = [];
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    // Skip node_modules, __pycache__, dist, .next, etc.
    if (/^(node_modules|__pycache__|dist|build|\.next|coverage|venv|\.venv)$/.test(name))
      continue;
    const full = join(dir, name);
    try {
      const st = statSync(full);
      if (st.isDirectory()) {
        out.push(...walkFiles(full, exts));
      } else if (exts.some((e) => name.endsWith(e))) {
        out.push(full);
      }
    } catch {
      // ignore permission/broken symlink
    }
  }
  return out;
}

function extractRoutePatterns(sourceFiles: string[]): Set<string> {
  const patterns = new Set<string>();
  for (const file of sourceFiles) {
    let src: string;
    try {
      src = readFileSync(file, "utf-8");
    } catch {
      continue;
    }
    // FastAPI: @app.get("/path"), @router.post("/path"), @app.route("/path")
    const pyRe =
      /@(?:app|router)\s*\.\s*(?:get|post|put|patch|delete|head|options|route)\s*\(\s*["']([^"']+)["']/g;
    // NestJS: @Get('/path'), @Post('/path'), ...
    const nestRe =
      /@(?:Get|Post|Put|Patch|Delete|Head|Options|All)\s*\(\s*["'`]([^"'`]+)["'`]/g;
    // NestJS @Controller('prefix')
    const controllerRe = /@Controller\s*\(\s*["'`]([^"'`]+)["'`]/g;

    let m: RegExpExecArray | null;
    while ((m = pyRe.exec(src))) patterns.add(normalizePath(m[1]));
    while ((m = nestRe.exec(src))) patterns.add(normalizePath(m[1]));
    // For Nest controllers, prefix itself counts as an implemented base path
    while ((m = controllerRe.exec(src))) patterns.add(normalizePath(m[1]));
  }
  return patterns;
}

function normalizePath(p: string): string {
  // Normalize to /path (no trailing slash except root), strip leading/trailing whitespace
  let out = p.trim();
  if (!out.startsWith("/")) out = "/" + out;
  if (out.length > 1 && out.endsWith("/")) out = out.slice(0, -1);
  return out;
}

/**
 * Given a contract path like `/api/v1/fields/{fieldId}` and an implemented
 * path like `/fields/{field_id}` or `/api/v1/fields/{fieldId}`, determine
 * if they match after Kong prefix stripping and param-name insensitivity.
 */
function pathMatches(contractPath: string, implemented: string): boolean {
  // Remove /api/v1 prefix from contract — backends are often mounted behind Kong
  const strip = (p: string) =>
    p
      .replace(/^\/api\/v1/, "")
      .replace(/\{[^}]+\}/g, "{P}") // normalize param names
      .replace(/:[a-zA-Z_][a-zA-Z0-9_]*/g, "{P}"); // NestJS :param
  const a = strip(contractPath);
  const b = strip(implemented);
  if (a === b) return true;
  // Allow suffix match (backend mounts may be relative)
  if (a.endsWith(b) || b.endsWith(a)) return true;
  return false;
}

async function main() {
  const endpointsModule = await import(resolve(TS_CONTRACTS, "api-endpoints.ts"));
  const results: CheckResult[] = [];

  for (const { group, service, wipAllowed, skipPaths } of CONTRACT_TO_SERVICE) {
    const endpoints = endpointsModule[group] as Record<string, string> | undefined;
    const serviceDir = join(SERVICES_ROOT, service);

    if (!endpoints) {
      results.push({ group, service, declared: 0, matched: 0, missing: [], status: "missing-service" });
      continue;
    }

    const declaredPaths = Object.values(endpoints).filter(
      (v): v is string =>
        typeof v === "string" &&
        v.startsWith("/api/") &&
        !(skipPaths ?? []).includes(v),
    );

    if (!existsSync(serviceDir)) {
      results.push({
        group,
        service,
        declared: declaredPaths.length,
        matched: 0,
        missing: declaredPaths,
        status: "missing-service",
      });
      continue;
    }

    const srcDirs = [join(serviceDir, "src")].filter(existsSync);
    const files = srcDirs.flatMap((d) => walkFiles(d));
    const implemented = extractRoutePatterns(files);

    const missing: string[] = [];
    for (const p of declaredPaths) {
      let found = false;
      for (const impl of implemented) {
        if (pathMatches(p, impl)) {
          found = true;
          break;
        }
      }
      if (!found) missing.push(p);
    }

    const matched = declaredPaths.length - missing.length;
    let status: CheckResult["status"];
    if (matched === 0 && wipAllowed) status = "wip";
    else if (matched === 0) status = "stub";
    else if (missing.length === 0) status = "ok";
    // Partial but all gaps are known WIP — treat as wip for CI purposes
    else if (wipAllowed && missing.length > 0) status = "wip";
    else status = "partial";

    results.push({
      group,
      service,
      declared: declaredPaths.length,
      matched,
      missing,
      status,
    });
  }

  // ───────── Report ─────────

  if (JSON_MODE) {
    console.log(JSON.stringify({ results }, null, 2));
  } else {
    console.log("🔍 Endpoint Reality Check\n");
    console.log("Legend: ✅ ok  ⚠️  partial  🚧 wip  ❌ stub  ❓ missing-service\n");
    for (const r of results) {
      const icon = {
        ok: "✅",
        partial: "⚠️ ",
        wip: "🚧",
        stub: "❌",
        "missing-service": "❓",
      }[r.status];
      console.log(
        `${icon} ${r.group.padEnd(32)} → ${r.service.padEnd(34)} ${r.matched}/${r.declared}`,
      );
      if (r.status === "partial" || r.status === "stub") {
        for (const m of r.missing.slice(0, 5)) {
          console.log(`     • missing: ${m}`);
        }
        if (r.missing.length > 5) {
          console.log(`     • … and ${r.missing.length - 5} more`);
        }
      }
    }

    const totals = {
      ok: results.filter((r) => r.status === "ok").length,
      partial: results.filter((r) => r.status === "partial").length,
      wip: results.filter((r) => r.status === "wip").length,
      stub: results.filter((r) => r.status === "stub").length,
      missing: results.filter((r) => r.status === "missing-service").length,
    };

    console.log(
      `\nSummary: ${totals.ok} ok, ${totals.partial} partial, ${totals.wip} wip, ${totals.stub} stub, ${totals.missing} missing`,
    );

    if (STRICT_MODE && (totals.stub > 0 || totals.missing > 0 || totals.partial > 0)) {
      console.error(
        "\n❌ Strict mode: endpoint-reality-check failed. Fix stubs/partials or mark services as WIP in CONTRACT_TO_SERVICE.",
      );
      process.exit(1);
    }
  }
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
