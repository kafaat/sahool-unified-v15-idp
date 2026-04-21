#!/usr/bin/env npx tsx
/**
 * SAHOOL Kong ↔ OpenAPI Validation Script
 * سكريبت التحقق من تطابق Kong مع مواصفات OpenAPI
 *
 * Validates that Kong declarative routes match the OpenAPI specifications
 * and the unified TypeScript contracts.
 *
 * Usage:
 *   npx tsx scripts/validate-kong-vs-openapi.ts          # Full validation
 *   npx tsx scripts/validate-kong-vs-openapi.ts --ci      # CI mode (exit 1 on errors)
 *   npx tsx scripts/validate-kong-vs-openapi.ts --report  # Generate JSON report
 *
 * @version 16.0.0
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { resolve, join } from "path";

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

interface KongService {
  name: string;
  host?: string;
  port?: number;
  url?: string;
  routes?: KongRoute[];
  plugins?: KongPlugin[];
}

interface KongRoute {
  name?: string;
  paths?: string[];
  methods?: string[];
  strip_path?: boolean;
  tags?: string[];
}

interface KongPlugin {
  name: string;
  config?: Record<string, unknown>;
}

interface KongConfig {
  _format_version: string;
  services?: KongService[];
  plugins?: KongPlugin[];
}

interface OpenAPISpec {
  openapi: string;
  info: { title: string; version: string };
  paths: Record<string, Record<string, unknown>>;
  servers?: Array<{ url: string; description?: string }>;
}

interface ValidationResult {
  errors: string[];
  warnings: string[];
  info: string[];
  kongRoutes: number;
  openapiPaths: number;
  contractEndpoints: number;
  matchedRoutes: number;
  unmatchedKongRoutes: string[];
  unmatchedOpenAPIPaths: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const ROOT = resolve(__dirname, "..");
const KONG_CONFIG = join(ROOT, "infrastructure/gateway/kong/kong.yml");
const OPENAPI_DIR = join(ROOT, "docs/api/openapi");
const CONTRACTS_DIR = join(
  ROOT,
  "packages/shared-types/src/contracts"
);

// Routes that Kong has but are infrastructure-level (not in OpenAPI)
const INFRASTRUCTURE_ROUTES = new Set([
  "/health",
  "/healthz",
  "/readyz",
  "/ping",
  "/metrics",
  "/monitoring",
]);

// Kong route patterns that are broad catch-alls
const BROAD_KONG_PATTERNS = [
  /^\/api\/v1\/[a-z-]+$/,  // e.g., /api/v1/fields
  /^\/api\/v2\/[a-z-]+$/,  // e.g., /api/v2/fields
];

// ═══════════════════════════════════════════════════════════════════════════════
// YAML Parser (simplified - handles Kong's declarative YAML)
// ═══════════════════════════════════════════════════════════════════════════════

function parseYAML(content: string): unknown {
  // Use a simple line-by-line parser for Kong YAML structure
  // For production use, install js-yaml: npm install js-yaml
  try {
    // Try dynamic import of js-yaml if available
    const jsYaml = require("js-yaml");
    return jsYaml.load(content);
  } catch {
    // Fallback: extract service names and route paths with regex
    return extractKongRoutesRegex(content);
  }
}

function extractKongRoutesRegex(content: string): KongConfig {
  const services: KongService[] = [];
  let currentService: KongService | null = null;
  let currentRoute: KongRoute | null = null;
  let inServices = false;
  let inRoutes = false;
  let inPaths = false;

  const lines = content.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();
    const indent = line.length - line.trimStart().length;

    if (/^services:\s*$/.test(trimmed)) {
      inServices = true;
      inRoutes = false;
      inPaths = false;
      currentRoute = null;
      continue;
    }

    if (!inServices) continue;

    if (indent <= 1 && /^[_a-zA-Z][\w-]*:\s*/.test(trimmed) && !/^services:\s*$/.test(trimmed)) {
      inServices = false;
      inRoutes = false;
      inPaths = false;
      currentRoute = null;
      continue;
    }

    // Detect service name
    const serviceNameMatch = trimmed.match(/^- name:\s*(.+)/);
    if (serviceNameMatch && indent <= 2) {
      if (currentService) {
        services.push(currentService);
      }
      currentService = {
        name: serviceNameMatch[1].trim(),
        routes: [],
      };
      inRoutes = false;
      inPaths = false;
      currentRoute = null;
      continue;
    }

    // Detect routes section
    if (trimmed === "routes:" && currentService) {
      inRoutes = true;
      continue;
    }

    // Detect route entry
    if (inRoutes && !inPaths && /^- /.test(trimmed) && indent >= 4) {
      currentRoute = { paths: [] };
      currentService?.routes?.push(currentRoute);
      inPaths = false;
      continue;
    }

    // Detect paths within route
    if (inRoutes && trimmed === "paths:") {
      inPaths = true;
      continue;
    }

    // Extract path
    if (inPaths && currentRoute) {
      const pathMatch = trimmed.match(/^- (\/.+)/);
      if (pathMatch) {
        currentRoute.paths?.push(pathMatch[1].trim());
      } else if (!/^[-\s]/.test(trimmed) || /^(methods|protocols|strip_path|name):/.test(trimmed)) {
        inPaths = false;
      }
    }

    // Detect host/port
    if (currentService) {
      const hostMatch = trimmed.match(/^host:\s*(.+)/);
      if (hostMatch) currentService.host = hostMatch[1].trim();

      const portMatch = trimmed.match(/^port:\s*(\d+)/);
      if (portMatch) currentService.port = parseInt(portMatch[1]);

      const urlMatch = trimmed.match(/^url:\s*(.+)/);
      if (urlMatch) currentService.url = urlMatch[1].trim();
    }
  }

  if (currentService) services.push(currentService);

  return { _format_version: "3.0", services };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Extract Routes from Kong Config
// ═══════════════════════════════════════════════════════════════════════════════

function extractKongRoutes(kongConfig: KongConfig): Map<string, string> {
  const routes = new Map<string, string>(); // path → service name

  if (!kongConfig.services) return routes;

  for (const service of kongConfig.services) {
    if (!service.routes) continue;
    for (const route of service.routes) {
      if (!route.paths) continue;
      for (const path of route.paths) {
        routes.set(path, service.name);
      }
    }
  }

  return routes;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Extract Paths from OpenAPI Specs
// ═══════════════════════════════════════════════════════════════════════════════

function extractOpenAPIPaths(openapiDir: string): Map<string, string> {
  const paths = new Map<string, string>(); // path → spec file

  if (!existsSync(openapiDir)) {
    console.warn(`⚠️  OpenAPI directory not found: ${openapiDir}`);
    return paths;
  }

  const { readdirSync } = require("fs");
  const files: string[] = readdirSync(openapiDir).filter(
    (f: string) => (f.endsWith(".yaml") || f.endsWith(".yml")) && !f.includes("..") && !f.includes("/")
  );

  for (const file of files) {
    const content = readFileSync(join(openapiDir, file), "utf-8");

    // Extract paths from OpenAPI YAML
    const pathMatches = content.matchAll(
      /^  (\/[^\s:]+):/gm
    );
    for (const match of pathMatches) {
      const path = match[1];
      // Skip component references like /components/schemas/...
      if (!path.startsWith("/components") && !path.startsWith("/#")) {
        paths.set(path, file);
      }
    }
  }

  return paths;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Extract Endpoints from TypeScript Contracts
// ═══════════════════════════════════════════════════════════════════════════════

function extractContractEndpoints(contractsDir: string): Map<string, string> {
  const endpoints = new Map<string, string>(); // path → constant name

  const apiEndpointsFile = join(contractsDir, "api-endpoints.ts");
  if (!existsSync(apiEndpointsFile)) {
    console.warn(`⚠️  Contracts file not found: ${apiEndpointsFile}`);
    return endpoints;
  }

  const content = readFileSync(apiEndpointsFile, "utf-8");

  // Extract endpoint paths from TypeScript constants
  // Pattern: KEY: `/api/v1/...`  or  KEY: `${API_PREFIX}/...`
  const matches = content.matchAll(
    /(\w+):\s*`\$\{API_PREFIX\}(\/[^`]+)`/g
  );
  for (const match of matches) {
    const name = match[1];
    const path = `/api/v1${match[2]}`;
    endpoints.set(path, name);
  }

  return endpoints;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Normalize path for comparison (remove param placeholders)
// ═══════════════════════════════════════════════════════════════════════════════

function normalizePath(path: string): string {
  return path
    .replace(/\{[^}]+\}/g, "*")   // {fieldId} → *
    .replace(/:path\*/g, "**")     // :path* → **
    .replace(/:(\w+)/g, "*")       // :id → *
    .replace(/\/+$/, "");           // trailing slash
}

function pathsMatch(kongPath: string, openapiPath: string): boolean {
  const nKong = normalizePath(kongPath);
  const nOpenAPI = normalizePath(openapiPath);

  // Exact match
  if (nKong === nOpenAPI) return true;

  // Kong uses prefix matching, so /api/v1/fields matches /api/v1/fields/{id}
  if (nOpenAPI.startsWith(nKong)) return true;

  return false;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Main Validation
// ═══════════════════════════════════════════════════════════════════════════════

function validate(): ValidationResult {
  const result: ValidationResult = {
    errors: [],
    warnings: [],
    info: [],
    kongRoutes: 0,
    openapiPaths: 0,
    contractEndpoints: 0,
    matchedRoutes: 0,
    unmatchedKongRoutes: [],
    unmatchedOpenAPIPaths: [],
  };

  // 1. Load Kong config
  if (!existsSync(KONG_CONFIG)) {
    result.errors.push(`Kong config not found: ${KONG_CONFIG}`);
    return result;
  }

  const kongContent = readFileSync(KONG_CONFIG, "utf-8");
  const kongConfig = parseYAML(kongContent) as KongConfig;
  const kongRoutes = extractKongRoutes(kongConfig);
  result.kongRoutes = kongRoutes.size;
  result.info.push(`Found ${kongRoutes.size} Kong routes`);
  if (kongRoutes.size === 0 && kongContent.includes("services:")) {
    result.errors.push("No Kong routes were parsed from kong.yml; check YAML parser/dependencies");
    return result;
  }

  // 2. Load OpenAPI specs
  const openapiPaths = extractOpenAPIPaths(OPENAPI_DIR);
  result.openapiPaths = openapiPaths.size;
  result.info.push(
    `Found ${openapiPaths.size} OpenAPI paths across ${new Set(openapiPaths.values()).size} spec files`
  );

  // 3. Load contract endpoints
  const contractEndpoints = extractContractEndpoints(CONTRACTS_DIR);
  result.contractEndpoints = contractEndpoints.size;
  result.info.push(
    `Found ${contractEndpoints.size} contract endpoints`
  );

  // 4. Validate: Kong routes should have matching OpenAPI paths
  for (const [kongPath, serviceName] of kongRoutes) {
    if (INFRASTRUCTURE_ROUTES.has(kongPath)) continue;

    let matched = false;
    for (const [openapiPath] of openapiPaths) {
      if (pathsMatch(kongPath, openapiPath)) {
        matched = true;
        result.matchedRoutes++;
        break;
      }
    }

    if (!matched) {
      // Check if it matches a broad pattern (Kong catch-all)
      const isBroad = BROAD_KONG_PATTERNS.some((p) => p.test(kongPath));
      if (isBroad) {
        result.info.push(
          `Kong broad route ${kongPath} (${serviceName}) - OK (catch-all pattern)`
        );
      } else {
        result.warnings.push(
          `Kong route ${kongPath} (${serviceName}) has no matching OpenAPI path`
        );
        result.unmatchedKongRoutes.push(kongPath);
      }
    }
  }

  // 5. Validate: Contract endpoints should exist in Kong
  for (const [contractPath, constName] of contractEndpoints) {
    // Normalize: replace {param} placeholders for matching
    const normalizedContract = normalizePath(contractPath);
    let matched = false;

    for (const [kongPath] of kongRoutes) {
      if (pathsMatch(kongPath, contractPath)) {
        matched = true;
        break;
      }
    }

    if (!matched) {
      result.warnings.push(
        `Contract endpoint ${constName} (${contractPath}) may not be routed through Kong`
      );
    }
  }

  // 6. Check for localhost in OpenAPI specs
  for (const [, specFile] of openapiPaths) {
    // Guard against path traversal (specFile comes from readdirSync but validate anyway)
    if (specFile.includes("..") || specFile.includes("/")) continue;
    const specContent = readFileSync(
      join(OPENAPI_DIR, specFile),
      "utf-8"
    );
    const localhostServers = specContent.match(
      /url:\s*http:\/\/localhost:\d+/g
    );
    if (localhostServers) {
      // Only warn if localhost is the ONLY server (not just dev fallback)
      const hasProductionServer = specContent.includes("api.sahool");
      if (!hasProductionServer) {
        result.warnings.push(
          `${specFile}: Only has localhost servers - add production server URL`
        );
      }
    }
  }

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Output
// ═══════════════════════════════════════════════════════════════════════════════

function printResult(result: ValidationResult): void {
  console.log("\n═══════════════════════════════════════════════════════");
  console.log("  SAHOOL Kong ↔ OpenAPI Validation Report");
  console.log("  تقرير التحقق من تطابق Kong مع OpenAPI");
  console.log("═══════════════════════════════════════════════════════\n");

  console.log(`📊 Summary:`);
  console.log(`   Kong routes:        ${result.kongRoutes}`);
  console.log(`   OpenAPI paths:      ${result.openapiPaths}`);
  console.log(`   Contract endpoints: ${result.contractEndpoints}`);
  console.log(`   Matched routes:     ${result.matchedRoutes}`);
  console.log();

  if (result.info.length > 0) {
    console.log("ℹ️  Info:");
    result.info.forEach((msg) => console.log(`   ${msg}`));
    console.log();
  }

  if (result.warnings.length > 0) {
    console.log(`⚠️  Warnings (${result.warnings.length}):`);
    result.warnings.forEach((msg) => console.log(`   ${msg}`));
    console.log();
  }

  if (result.errors.length > 0) {
    console.log(`❌ Errors (${result.errors.length}):`);
    result.errors.forEach((msg) => console.log(`   ${msg}`));
    console.log();
  }

  if (result.errors.length === 0 && result.warnings.length === 0) {
    console.log("✅ All validations passed!\n");
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Main
// ═══════════════════════════════════════════════════════════════════════════════

const args = process.argv.slice(2);
const isCI = args.includes("--ci");
const isReport = args.includes("--report");

const result = validate();
printResult(result);

if (isReport) {
  const reportPath = join(ROOT, "api/validation-report.json");
  writeFileSync(reportPath, JSON.stringify(result, null, 2));
  console.log(`📄 Report saved to: ${reportPath}\n`);
}

if (isCI && result.errors.length > 0) {
  console.log("::error::Kong ↔ OpenAPI validation failed");
  process.exit(1);
}

if (isCI && result.warnings.length > 10) {
  console.log(
    `::warning::${result.warnings.length} validation warnings - consider fixing`
  );
}
