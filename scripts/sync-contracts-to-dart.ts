#!/usr/bin/env npx tsx
/**
 * SAHOOL Contract Sync: TypeScript → Dart
 * مزامنة العقود: TypeScript → Dart
 *
 * Generates Dart contract files from TypeScript source of truth.
 * Usage:
 *   npx tsx scripts/sync-contracts-to-dart.ts          # Generate Dart files
 *   npx tsx scripts/sync-contracts-to-dart.ts --check   # Check if Dart is in sync (CI mode)
 *
 * @version 16.0.0
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

const ROOT = resolve(dirname(new URL(import.meta.url).pathname), "..");
const TS_CONTRACTS = resolve(ROOT, "packages/shared-types/src/contracts");
const DART_CONTRACTS = resolve(ROOT, "apps/mobile/lib/core/contracts");

const CHECK_MODE = process.argv.includes("--check");

// ─────────────────────────────────────────────────────────────────────────────
// Import TypeScript contracts dynamically
// ─────────────────────────────────────────────────────────────────────────────

async function main() {
  const { SERVICE_PORTS } = await import(
    resolve(TS_CONTRACTS, "service-ports.ts")
  );
  const { ERROR_CODES, ERROR_MESSAGES } = await import(
    resolve(TS_CONTRACTS, "error-codes.ts")
  );
  const endpointsModule = await import(
    resolve(TS_CONTRACTS, "api-endpoints.ts")
  );
  const { CONTRACT_VERSION } = await import(resolve(TS_CONTRACTS, "index.ts"));

  // ─────────────────────────────────────────────────────────────────────────
  // Generate service_ports.dart
  // ─────────────────────────────────────────────────────────────────────────

  const portLines = Object.entries(SERVICE_PORTS as Record<string, number>)
    .map(([name, port]) => {
      const dartName = toCamelCase(name);
      return `  static const int ${dartName} = ${port};`;
    })
    .join("\n");

  const servicePortsDart = `/// SAHOOL Unified Service Ports (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/service-ports.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: ${CONTRACT_VERSION}
library;

/// Single source of truth for all microservice ports.
abstract final class ServicePorts {
${portLines}
}

/// Get service URL from port and host.
String getServiceUrl(int port, {String host = 'http://localhost'}) =>
    '\$host:\$port';
`;

  // ─────────────────────────────────────────────────────────────────────────
  // Generate error_codes.dart
  // ─────────────────────────────────────────────────────────────────────────

  const errorCodeLines = Object.entries(ERROR_CODES as Record<string, string>)
    .filter(([, code]) => !code.startsWith("E")) // Skip vision E-codes for main file
    .map(([name, code]) => {
      const dartName = toCamelCase(name);
      return `  static const String ${dartName} = '${code}';`;
    })
    .join("\n");

  // Vision error codes
  const visionCodeLines = Object.entries(ERROR_CODES as Record<string, string>)
    .filter(([, code]) => code.startsWith("E"))
    .map(([name, code]) => {
      const dartName = toCamelCase(name);
      return `  static const String ${dartName} = '${code}';`;
    })
    .join("\n");

  const errorMessageEntries = Object.entries(
    ERROR_MESSAGES as Record<
      string,
      {
        code: string;
        httpStatus: number;
        en: string;
        ar: string;
        retryable: boolean;
      }
    >,
  )
    .filter(([key]) => !(ERROR_CODES as Record<string, string>)[key]?.startsWith?.("E"))
    .map(([key, msg]) => {
      const escaped = (s: string) => s.replace(/'/g, "\\'");
      return `  '${key}': ErrorMessage(
    code: '${msg.code}',
    httpStatus: ${msg.httpStatus},
    en: '${escaped(msg.en)}',
    ar: '${escaped(msg.ar)}',
    retryable: ${msg.retryable},
  ),`;
    })
    .join("\n");

  const errorCodesDart = `/// SAHOOL Unified Error Codes (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/error-codes.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: ${CONTRACT_VERSION}
library;

/// Unified error codes used across all SAHOOL clients and services.
abstract final class ErrorCodes {
${errorCodeLines}

  // Vision Service (E-codes)
${visionCodeLines}
}

/// Bilingual error message.
class ErrorMessage {
  final String code;
  final int httpStatus;
  final String en;
  final String ar;
  final bool retryable;

  const ErrorMessage({
    required this.code,
    required this.httpStatus,
    required this.en,
    required this.ar,
    required this.retryable,
  });
}

/// Unified error messages (en + ar).
const Map<String, ErrorMessage> errorMessages = {
${errorMessageEntries}
};

/// Get error message by code, with fallback to UNKNOWN.
ErrorMessage getErrorMessage(String code) =>
    errorMessages[code] ?? errorMessages[ErrorCodes.unknown]!;

/// Get localized error string.
String getLocalizedError(String code, {String locale = 'ar'}) {
  final msg = getErrorMessage(code);
  return locale == 'ar' ? msg.ar : msg.en;
}

/// Map HTTP status to error code.
String httpStatusToErrorCode(int status) => switch (status) {
      401 => ErrorCodes.unauthorized,
      403 => ErrorCodes.forbidden,
      404 => ErrorCodes.notFound,
      409 => ErrorCodes.conflict,
      429 => ErrorCodes.rateLimited,
      400 => ErrorCodes.badRequest,
      502 => ErrorCodes.invalidResponse,
      503 => ErrorCodes.serviceUnavailable,
      504 => ErrorCodes.gatewayTimeout,
      >= 500 => ErrorCodes.serverError,
      _ => ErrorCodes.unknown,
    };

/// Check if an error code is retryable.
bool isRetryable(String code) => getErrorMessage(code).retryable;
`;

  // ─────────────────────────────────────────────────────────────────────────
  // Generate api_endpoints.dart
  // ─────────────────────────────────────────────────────────────────────────

  // Auto-discover all *_ENDPOINTS exports from the TypeScript module so the
  // generator stays in sync as new endpoint groups are added (no manual list
  // to keep aligned). HEALTH_ENDPOINTS first for stability.
  //
  // Filter out non-object exports (e.g. PUBLIC_ENDPOINTS which is a string[]
  // of path literals, not a Record<name, path>) — those would produce invalid
  // Dart class members with numeric names.
  const isEndpointRecord = (v: unknown): boolean =>
    typeof v === "object" &&
    v !== null &&
    !Array.isArray(v) &&
    Object.keys(v as object).every((k) => /^[A-Z_][A-Z0-9_]*$/.test(k));

  const allKeys = Object.keys(endpointsModule).filter(
    (k) => /^[A-Z][A-Z0-9_]*_ENDPOINTS$/.test(k) && isEndpointRecord(endpointsModule[k]),
  );
  const orderedKeys = [
    "HEALTH_ENDPOINTS",
    "SERVICE_HEALTH_ENDPOINTS",
    "AUTH_ENDPOINTS",
    ...allKeys
      .filter((k) => !["HEALTH_ENDPOINTS", "SERVICE_HEALTH_ENDPOINTS", "AUTH_ENDPOINTS"].includes(k))
      .sort(),
  ].filter((k, i, a) => a.indexOf(k) === i && k in endpointsModule);

  const ENDPOINT_GROUPS = orderedKeys.map((tsName) => {
    // CROP_HEALTH_ENDPOINTS → CropHealthEndpoints
    // VIRTUAL_SENSOR_ENDPOINTS → VirtualSensorEndpoints
    const dartClass =
      tsName
        .replace(/_ENDPOINTS$/, "")
        .split("_")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
        .join("") + "Endpoints";
    const label = tsName.replace(/_ENDPOINTS$/, "").toLowerCase().replace(/_/g, " ");
    return { tsName, dartClass, label };
  });

  const endpointsClassBlocks: string[] = [];
  for (const { tsName, dartClass, label } of ENDPOINT_GROUPS) {
    const obj = endpointsModule[tsName] as Record<string, string> | undefined;
    if (!obj) continue;
    endpointsClassBlocks.push(renderDartEndpointClass(label, dartClass, obj));
  }

  const apiEndpointsDart = `/// SAHOOL Unified API Endpoint Paths (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/api-endpoints.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: ${CONTRACT_VERSION}
library;

/// API version prefix
const String apiVersion = 'v1';
const String apiPrefix = '/api/\$apiVersion';

${endpointsClassBlocks.join("\n\n")}
`;

  // ─────────────────────────────────────────────────────────────────────────
  // Write or Check
  // ─────────────────────────────────────────────────────────────────────────

  const files: Array<{ path: string; content: string; name: string }> = [
    {
      path: resolve(DART_CONTRACTS, "service_ports.dart"),
      content: servicePortsDart,
      name: "service_ports.dart",
    },
    {
      path: resolve(DART_CONTRACTS, "error_codes.dart"),
      content: errorCodesDart,
      name: "error_codes.dart",
    },
    {
      path: resolve(DART_CONTRACTS, "api_endpoints.dart"),
      content: apiEndpointsDart,
      name: "api_endpoints.dart",
    },
  ];

  if (CHECK_MODE) {
    console.log("🔍 Checking Dart contract synchronization...\n");
    let outOfSync = 0;

    for (const file of files) {
      if (!existsSync(file.path)) {
        console.error(`  ❌ ${file.name}: file does not exist`);
        outOfSync++;
        continue;
      }

      const existing = readFileSync(file.path, "utf-8");
      if (existing.trim() !== file.content.trim()) {
        console.error(`  ❌ ${file.name}: OUT OF SYNC`);
        outOfSync++;
      } else {
        console.log(`  ✅ ${file.name}: in sync`);
      }
    }

    if (outOfSync > 0) {
      console.error(
        `\n❌ ${outOfSync} Dart contract file(s) out of sync.`,
      );
      console.error(
        "   Run: npx tsx scripts/sync-contracts-to-dart.ts",
      );
      process.exit(1);
    }

    console.log("\n✅ All Dart contracts are in sync with TypeScript.");
  } else {
    console.log("📝 Generating Dart contracts from TypeScript...\n");

    for (const file of files) {
      writeFileSync(file.path, file.content, "utf-8");
      console.log(`  ✅ Generated ${file.name}`);
    }

    console.log(
      `\n✅ Dart contracts generated (version ${CONTRACT_VERSION}).`,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function toCamelCase(screaming: string): string {
  return screaming
    .toLowerCase()
    .replace(/_([a-z0-9])/g, (_, c: string) => c.toUpperCase());
}

/**
 * Convert a {paramName} template placeholder to Dart string interpolation.
 * - If no placeholders: emit `static const String name = 'path';`
 * - If placeholders: emit `static String name(String p1, String p2) => 'path/$p1/$p2';`
 */
// Dart reserved words / built-in identifiers that cannot safely be used
// as static member names. Escape by suffixing the class context.
const DART_RESERVED_MEMBER_NAMES = new Set([
  "assert", "break", "case", "catch", "class", "const", "continue", "default",
  "do", "else", "enum", "extends", "false", "final", "finally", "for", "if",
  "in", "is", "new", "null", "rethrow", "return", "super", "switch", "this",
  "throw", "true", "try", "var", "void", "while", "with",
  // Context-sensitive / built-in identifiers that are problematic as method names
  "get", "set", "yield", "async", "await", "sync", "operator", "abstract",
  "dynamic", "export", "extension", "external", "factory", "implements",
  "import", "interface", "library", "mixin", "of", "on", "part", "show",
  "static", "typedef", "hide", "as",
]);

function safeDartMember(name: string, classSuffix: string): string {
  if (DART_RESERVED_MEMBER_NAMES.has(name)) {
    return `${name}${classSuffix}`;
  }
  return name;
}

function renderDartEndpointClass(
  label: string,
  dartClass: string,
  entries: Record<string, string>,
): string {
  // Derive a suffix from the class name to disambiguate reserved words
  const suffix = dartClass.replace(/Endpoints$/, "");
  const lines: string[] = [];
  for (const [rawKey, template] of Object.entries(entries)) {
    // Skip empty / non-string values defensively
    if (typeof template !== "string") continue;
    const dartName = safeDartMember(toCamelCase(rawKey), suffix);
    const params = [...template.matchAll(/\{([a-zA-Z][a-zA-Z0-9]*)\}/g)].map(
      (m) => m[1],
    );
    // Replace /api/v1 with $apiPrefix for consistency with existing convention.
    const pathExpr = template.replace(/^\/api\/v1/, "\\$apiPrefix");

    if (params.length === 0) {
      // Plain constant
      lines.push(`  static const String ${dartName} = '${pathExpr}';`);
    } else {
      // Function with required params → interpolation
      const uniqueParams = Array.from(new Set(params));
      const paramSig = uniqueParams.map((p) => `String ${p}`).join(", ");
      let interpolated = pathExpr;
      for (const p of uniqueParams) {
        interpolated = interpolated.split(`{${p}}`).join(`\$${p}`);
      }
      lines.push(
        `  static String ${dartName}(${paramSig}) => '${interpolated}';`,
      );
    }
  }
  return `/// ${label}
abstract final class ${dartClass} {
${lines.join("\n")}
}`;
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
