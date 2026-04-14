#!/usr/bin/env npx tsx
/**
 * SAHOOL Contract Sync: TypeScript → Dart
 * مزامنة العقود: TypeScript → Dart
 *
 * Generates Dart contract files from TypeScript source of truth.
 *
 * Auto-generated:
 *   - apps/mobile/lib/core/contracts/service_ports.dart
 *   - apps/mobile/lib/core/contracts/error_codes.dart
 *
 * Drift-checked (hand-curated, see header of each file):
 *   - apps/mobile/lib/core/contracts/api_endpoints.dart
 *     Every `*_ENDPOINTS.*` URL declared in TypeScript is expected to appear
 *     (as a Dart-interpolated fragment) somewhere in the Dart file. Missing
 *     URLs are reported as warnings in both generate and check modes. Pass
 *     `--strict-endpoints` to treat them as failures (useful for per-PR
 *     enforcement once the pre-existing backlog is closed).
 *
 * Usage:
 *   npx tsx scripts/sync-contracts-to-dart.ts                    # Generate + warn on api_endpoints drift
 *   npx tsx scripts/sync-contracts-to-dart.ts --check            # CI: fail on service_ports/error_codes drift; warn on api_endpoints
 *   npx tsx scripts/sync-contracts-to-dart.ts --check --strict-endpoints   # CI: fail on api_endpoints drift too
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
// sahool_field_app is its own Flutter package and cannot import from
// `apps/mobile`; its contracts/ directory is a vendored copy kept in sync
// with the canonical one. We check both for api_endpoints drift.
const DART_CONTRACTS_FIELD_APP = resolve(
  ROOT,
  "apps/mobile/sahool_field_app/lib/core/contracts",
);

const CHECK_MODE = process.argv.includes("--check");
/**
 * Strict mode also treats api_endpoints.dart drift as a failure.
 * Off by default because api_endpoints.dart has ~300 pre-existing gaps
 * (it was hand-curated before this drift check existed). Flip via
 * `--strict-endpoints` once the backlog is closed — or on a per-PR basis
 * to enforce that new TS endpoints ship with a matching Dart entry.
 */
const STRICT_ENDPOINTS = process.argv.includes("--strict-endpoints");

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
  const { CONTRACT_VERSION } = await import(resolve(TS_CONTRACTS, "index.ts"));
  const apiEndpointsModule = await import(
    resolve(TS_CONTRACTS, "api-endpoints.ts")
  );

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
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Drift check for api_endpoints.dart
  // ─────────────────────────────────────────────────────────────────────────
  //
  // `api_endpoints.dart` (both the canonical mirror and the vendored
  // sahool_field_app copy) is MANUALLY maintained because it uses
  // hand-curated typed Dart helpers (e.g. `static String get(String fieldId)
  // => '$apiPrefix/fields/$fieldId';`) that cannot be mechanically derived
  // from the TypeScript declarations with 100% fidelity.
  //
  // But we still want CI to catch the common drift failure mode: a developer
  // adds a new URL to `*_ENDPOINTS` in TypeScript and forgets to mirror it
  // in Dart. This check scans every TS `*_ENDPOINTS` constant's URL
  // templates, normalises the placeholders to Dart's `$var` syntax, and
  // verifies the resulting path fragment appears somewhere in the Dart file.
  // Missing URLs are reported (warning in generate mode, fatal in --check).

  const apiEndpointsTargets: Array<{ label: string; path: string }> = [
    {
      label: "apps/mobile/lib/core/contracts/api_endpoints.dart",
      path: resolve(DART_CONTRACTS, "api_endpoints.dart"),
    },
    {
      label:
        "apps/mobile/sahool_field_app/lib/core/contracts/api_endpoints.dart",
      path: resolve(DART_CONTRACTS_FIELD_APP, "api_endpoints.dart"),
    },
  ];

  const tsEndpointUrls = collectTsEndpointUrls(apiEndpointsModule);

  type Drift = {
    label: string;
    missing: TsEndpointUrl[];
  };
  const driftReports: Drift[] = apiEndpointsTargets
    .filter(({ path }) => existsSync(path))
    .map(({ label, path }) => {
      const content = readFileSync(path, "utf-8");
      return {
        label,
        missing: tsEndpointUrls.filter(
          ({ dartFragment }) => !content.includes(dartFragment),
        ),
      };
    });

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

    // Drift check for the hand-maintained api_endpoints.dart files.
    for (const { label, missing } of driftReports) {
      if (missing.length === 0) {
        console.log(
          `  ✅ ${label}: all ${tsEndpointUrls.length} TypeScript endpoint URLs mirrored`,
        );
        continue;
      }
      const header = STRICT_ENDPOINTS ? "❌" : "⚠️ ";
      const mode = STRICT_ENDPOINTS ? "STRICT" : "warn-only";
      console.log(
        `  ${header} ${label}: ${missing.length} TypeScript endpoint URL(s) not mirrored (${mode})`,
      );
      // Preview — full list is printed in generate mode only.
      const preview = missing.slice(0, 10);
      for (const { group, member, dartFragment } of preview) {
        console.log(`     • ${group}.${member}  (expected fragment: ${dartFragment})`);
      }
      if (missing.length > preview.length) {
        console.log(
          `     …and ${missing.length - preview.length} more. ` +
            `Run without --check to see the full list.`,
        );
      }
      if (STRICT_ENDPOINTS) {
        outOfSync++;
      }
    }

    if (outOfSync > 0) {
      console.error(
        `\n❌ ${outOfSync} Dart contract file(s) out of sync.`,
      );
      console.error(
        "   Run: npx tsx scripts/sync-contracts-to-dart.ts",
      );
      console.error(
        "   For api_endpoints.dart drift, add the missing URLs manually",
      );
      console.error(
        "   (the file is hand-curated; see its header for the reason).",
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
    const totalMissing = driftReports.reduce(
      (sum, d) => sum + d.missing.length,
      0,
    );
    if (totalMissing > 0) {
      console.log(
        "\n⚠️  api_endpoints.dart files are out of sync with TypeScript:",
      );
      console.log(
        "   (These files are hand-curated because typed Dart helpers like",
      );
      console.log(
        "   `static String get(String fieldId) => ...` do not round-trip",
      );
      console.log(
        "   cleanly from TypeScript constants. Add the missing entries",
      );
      console.log(
        "   manually to keep the mobile app in sync.)",
      );
      for (const { label, missing } of driftReports) {
        if (missing.length === 0) {
          console.log(`\n   ✅ ${label}: all ${tsEndpointUrls.length} URLs mirrored`);
          continue;
        }
        console.log(`\n   ⚠️  ${label}: ${missing.length} missing`);
        const preview = missing.slice(0, 30);
        for (const { group, member, dartFragment } of preview) {
          console.log(`       • ${group}.${member}  → ${dartFragment}`);
        }
        if (missing.length > preview.length) {
          console.log(`       …and ${missing.length - preview.length} more.`);
        }
      }
    } else if (driftReports.length > 0) {
      console.log(
        `   api_endpoints.dart (×${driftReports.length}) mirrors all ${tsEndpointUrls.length} TypeScript endpoint URLs.`,
      );
    }
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
 * Collect every endpoint URL declared in TypeScript `*_ENDPOINTS` constants,
 * normalise placeholders to Dart-interpolation syntax, and return the
 * fragments that should appear (as literal strings) inside
 * `api_endpoints.dart`.
 *
 * A TypeScript path like `/api/v1/fields/{fieldId}` becomes the Dart
 * fragment `/fields/$fieldId` (leading `/api/v1` is stripped because Dart
 * builds those via the `apiPrefix` constant). Matching on fragments rather
 * than full paths keeps the check tolerant of how the Dart side chooses to
 * compose its strings (template interpolation vs. concatenation).
 */
interface TsEndpointUrl {
  group: string;
  member: string;
  tsPath: string;
  dartFragment: string;
}

function collectTsEndpointUrls(
  apiEndpointsModule: Record<string, unknown>,
): TsEndpointUrl[] {
  const out: TsEndpointUrl[] = [];

  for (const [groupName, value] of Object.entries(apiEndpointsModule)) {
    if (!groupName.endsWith("_ENDPOINTS")) continue;
    if (!value || typeof value !== "object") continue;
    // Skip PUBLIC_ENDPOINTS (readonly string[]) which is an array of URLs
    // already covered by their owning groups.
    if (Array.isArray(value)) continue;

    for (const [memberName, rawPath] of Object.entries(
      value as Record<string, unknown>,
    )) {
      if (typeof rawPath !== "string") continue;
      if (!rawPath.startsWith("/api/")) continue;

      // Strip the `/api/vN` prefix so the fragment is agnostic to how Dart
      // composes it (apiPrefix vs literal).
      const withoutPrefix = rawPath.replace(/^\/api\/v\d+/, "");

      // Convert `{placeholder}` to Dart `$placeholder` interpolation.
      // Replacement `$$$1` = literal `$` (from `$$`) + capture group 1.
      const dartFragment = withoutPrefix.replace(
        /\{([a-zA-Z_][a-zA-Z0-9_]*)\}/g,
        "$$$1",
      );

      out.push({
        group: groupName,
        member: memberName,
        tsPath: rawPath,
        dartFragment,
      });
    }
  }

  return out;
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
