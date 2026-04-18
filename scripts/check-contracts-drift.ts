#!/usr/bin/env tsx
/**
 * SAHOOL Contracts Drift Check
 * ============================
 *
 * Regenerates the Python service-ports module to a temp file and diffs
 * it against the committed `shared/contracts_py/service_ports.py`. Any
 * meaningful difference (ignoring the `Generated:` timestamp line) fails
 * with exit 1 and a helpful message.
 *
 * Usage:
 *   npx tsx scripts/check-contracts-drift.ts
 */

import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, "..");
const COMMITTED = resolve(REPO_ROOT, "shared/contracts_py/service_ports.py");
const GENERATOR = resolve(__dirname, "sync-contracts-to-python.ts");

/** Remove generator-timestamp lines so only semantic drift counts. */
function normalize(src: string): string {
  return src
    .split("\n")
    .filter((line) => !/^Generated:\s/.test(line.trim()))
    .join("\n")
    .trimEnd();
}

function main(): void {
  if (!existsSync(COMMITTED)) {
    console.error(
      `[check-drift] Committed Python file not found: ${COMMITTED}\n` +
        `Run: npx tsx scripts/sync-contracts-to-python.ts`,
    );
    process.exit(1);
  }

  const tmpDir = mkdtempSync(join(tmpdir(), "sahool-contracts-"));
  const tmpOut = join(tmpDir, "service_ports.py");

  const result = spawnSync(
    "npx",
    ["tsx", GENERATOR, "--out", tmpOut],
    { stdio: "inherit" },
  );
  if (result.status !== 0) {
    console.error("[check-drift] Generator failed — see above.");
    process.exit(1);
  }

  const generated = normalize(readFileSync(tmpOut, "utf8"));
  const committed = normalize(readFileSync(COMMITTED, "utf8"));

  if (generated === committed) {
    console.log("[check-drift] OK — Python contracts are in sync with TS source.");
    process.exit(0);
  }

  console.error("[check-drift] DRIFT DETECTED");
  console.error(
    "  The committed shared/contracts_py/service_ports.py is out of sync with",
  );
  console.error("  packages/shared-types/src/contracts/service-ports.ts.");
  console.error("");
  console.error("  To fix, run:");
  console.error("    npx tsx scripts/sync-contracts-to-python.ts");
  console.error("  then commit the regenerated file.");

  // Emit a minimal unified-diff-ish hint: first differing block.
  const gLines = generated.split("\n");
  const cLines = committed.split("\n");
  const max = Math.max(gLines.length, cLines.length);
  let shown = 0;
  for (let i = 0; i < max && shown < 10; i++) {
    if (gLines[i] !== cLines[i]) {
      console.error(`  line ${i + 1}:`);
      console.error(`    - committed: ${cLines[i] ?? "<missing>"}`);
      console.error(`    + generated: ${gLines[i] ?? "<missing>"}`);
      shown++;
    }
  }
  process.exit(1);
}

main();
