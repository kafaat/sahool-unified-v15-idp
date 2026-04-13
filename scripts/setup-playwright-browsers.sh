#!/usr/bin/env bash
# scripts/setup-playwright-browsers.sh
#
# Idempotent helper that prepares Playwright's chromium browser for E2E tests.
#
# - In a normal environment with internet access, this script is a no-op:
#   running developers should just use `npx playwright install chromium`.
# - In sandboxed CI environments where the Playwright CDN is blocked
#   (e.g. Claude Code on the web) but a Chrome for Testing build is
#   pre-installed under PLAYWRIGHT_BROWSERS_PATH at a *different* version,
#   this script symlinks the pre-installed binaries under the version path
#   that Playwright is currently expecting, so launches succeed without
#   a network download.
#
# Usage:
#   ./scripts/setup-playwright-browsers.sh
#
# Environment overrides:
#   PLAYWRIGHT_BROWSERS_PATH  default: /opt/pw-browsers (sandbox) or ~/.cache/ms-playwright
#
# Exit codes:
#   0  ready (either online install or symlinks created)
#   1  no compatible browser found and CDN unreachable

set -euo pipefail

PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
export PLAYWRIGHT_BROWSERS_PATH

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "→ Playwright browsers path: $PLAYWRIGHT_BROWSERS_PATH"

# 1. Determine which chromium build Playwright wants
WANTED_LINE=$(npx playwright install --dry-run chromium 2>&1 | grep -E "Install location:.*chromium-[0-9]+$" | head -1 || true)
if [[ -z "$WANTED_LINE" ]]; then
  echo "✗ Could not determine wanted chromium version (is @playwright/test installed?)" >&2
  exit 1
fi
WANTED_DIR=$(echo "$WANTED_LINE" | awk '{print $NF}')
WANTED_VERSION=$(basename "$WANTED_DIR" | sed 's/chromium-//')
echo "→ Playwright expects: chromium-${WANTED_VERSION} at ${WANTED_DIR}"

# 2. If the wanted dir already has a usable binary, we're done
if [[ -x "${WANTED_DIR}/chrome-linux64/chrome" ]] || [[ -x "${WANTED_DIR}/chrome-linux/chrome" ]]; then
  echo "✓ chromium-${WANTED_VERSION} already present"
  exit 0
fi

# 3. Try the standard online install first
if npx playwright install chromium >/dev/null 2>&1; then
  echo "✓ chromium installed via npx playwright install"
  exit 0
fi

echo "⚠ Online install failed (CDN blocked?). Looking for a pre-installed fallback..."

# 4. Find another chromium-XXXX directory with a real binary
FALLBACK_DIR=$(find "$PLAYWRIGHT_BROWSERS_PATH" -maxdepth 1 -type d -name 'chromium-*' 2>/dev/null | sort -V | tail -1 || true)
FALLBACK_SHELL_DIR=$(find "$PLAYWRIGHT_BROWSERS_PATH" -maxdepth 1 -type d -name 'chromium_headless_shell-*' 2>/dev/null | sort -V | tail -1 || true)

if [[ -z "$FALLBACK_DIR" ]] || [[ ! -x "${FALLBACK_DIR}/chrome-linux/chrome" ]]; then
  echo "✗ No fallback chromium found under ${PLAYWRIGHT_BROWSERS_PATH}" >&2
  echo "  Hint: install chromium with full network access first, or place a" >&2
  echo "        Chrome for Testing build under ${PLAYWRIGHT_BROWSERS_PATH}/chromium-XXXX/" >&2
  exit 1
fi

FALLBACK_VERSION=$(basename "$FALLBACK_DIR" | sed 's/chromium-//')
echo "→ Found fallback: chromium-${FALLBACK_VERSION} at ${FALLBACK_DIR}"

# 5. Create the layout Playwright expects, symlinking to the fallback binaries.
#    Newer Playwright uses chrome-linux64/chrome and chrome-headless-shell-linux64/chrome-headless-shell.
#    Older Chromium for Testing uses chrome-linux/chrome and chrome-linux/headless_shell.
mkdir -p "${WANTED_DIR}"
ln -sfn "${FALLBACK_DIR}/chrome-linux" "${WANTED_DIR}/chrome-linux64"
touch "${WANTED_DIR}/INSTALLATION_COMPLETE" "${WANTED_DIR}/DEPENDENCIES_VALIDATED"

WANTED_SHELL_DIR="${PLAYWRIGHT_BROWSERS_PATH}/chromium_headless_shell-${WANTED_VERSION}"
WANTED_SHELL_BIN_DIR="${WANTED_SHELL_DIR}/chrome-headless-shell-linux64"
mkdir -p "${WANTED_SHELL_BIN_DIR}"

if [[ -n "$FALLBACK_SHELL_DIR" ]] && [[ -x "${FALLBACK_SHELL_DIR}/chrome-linux/headless_shell" ]]; then
  ln -sfn "${FALLBACK_SHELL_DIR}/chrome-linux/headless_shell" \
          "${WANTED_SHELL_BIN_DIR}/chrome-headless-shell"
  touch "${WANTED_SHELL_DIR}/INSTALLATION_COMPLETE" "${WANTED_SHELL_DIR}/DEPENDENCIES_VALIDATED"
fi

echo "✓ Symlinked chromium-${FALLBACK_VERSION} → chromium-${WANTED_VERSION}"

# 6. Smoke-test
node -e "
const { chromium } = require('${REPO_ROOT}/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setContent('<h1>ok</h1>');
  await browser.close();
})().then(
  () => console.log('✓ Browser launches successfully'),
  e  => { console.error('✗ Browser smoke test failed:', e.message); process.exit(1); }
);
"
