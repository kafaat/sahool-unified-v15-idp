#!/usr/bin/env bash
# PostToolUse hook for Edit|Write|MultiEdit on the SAHOOL monorepo.
#
# Auto-formats/lints the file that was just edited, using the right tool for
# its extension. Failures are non-blocking (exit 0 always) because this hook is
# for ergonomics, not gating.
#
# CLAUDE_FILE_PATHS is the standard env var that Claude Code sets for file
# tool hooks (space-separated list of absolute paths).

set -u

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT" || exit 0

# Fall back: if the env var is not set, do nothing.
if [[ -z "${CLAUDE_FILE_PATHS:-}" ]]; then
  exit 0
fi

# Skip hook on vendored / generated / archived paths.
skip_path() {
  local f="$1"
  case "$f" in
    */node_modules/*|*/.venv/*|*/.next/*|*/dist/*|*/build/*) return 0 ;;
    */archive/deprecated-services/*) return 0 ;;
    */idp/templates/*) return 0 ;;
    */legacy/*) return 0 ;;
    */apps/mobile/lib/core/contracts/*) return 0 ;;  # generated Dart
  esac
  return 1
}

format_python() {
  local f="$1"
  command -v ruff >/dev/null 2>&1 || return 0
  ruff check --fix --exit-zero --quiet "$f" >/dev/null 2>&1 || true
  ruff format --quiet "$f" >/dev/null 2>&1 || true
}

format_js_ts() {
  local f="$1"
  # Prefer per-package prettier if available, else npx.
  if command -v npx >/dev/null 2>&1; then
    npx --no-install prettier --write --log-level=silent "$f" >/dev/null 2>&1 || true
  fi
}

format_dart() {
  local f="$1"
  command -v dart >/dev/null 2>&1 || return 0
  dart format --output=write "$f" >/dev/null 2>&1 || true
}

format_json() {
  local f="$1"
  if command -v npx >/dev/null 2>&1; then
    npx --no-install prettier --write --log-level=silent "$f" >/dev/null 2>&1 || true
  fi
}

# Iterate over every file the tool touched.
for f in $CLAUDE_FILE_PATHS; do
  [[ -f "$f" ]] || continue
  skip_path "$f" && continue

  case "$f" in
    *.py)               format_python "$f" ;;
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs) format_js_ts "$f" ;;
    *.dart)             format_dart "$f" ;;
    *.json|*.jsonc)     format_json "$f" ;;
  esac
done

exit 0
