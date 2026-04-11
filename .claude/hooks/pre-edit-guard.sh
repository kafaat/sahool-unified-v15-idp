#!/usr/bin/env bash
# PreToolUse hook for Edit|Write|MultiEdit. Blocks edits that would violate
# SAHOOL platform invariants (deprecated services, generated files, secrets).
#
# Exit codes:
#   0 = allow
#   2 = block with message on stderr

set -u

payload="${CLAUDE_TOOL_INPUT:-}"
paths="${CLAUDE_FILE_PATHS:-}"

# Fall back to scraping the JSON payload if CLAUDE_FILE_PATHS isn't set.
if [[ -z "$paths" && -n "$payload" ]]; then
  paths=$(echo "$payload" | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]+"' \
    | sed -E 's/.*"file_path"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
fi

[[ -z "$paths" ]] && exit 0

block() {
  echo "🚨 SAHOOL pre-edit-guard blocked this edit:" >&2
  echo "    file:   $1" >&2
  echo "    reason: $2" >&2
  echo "    If this is intentional, override in .claude/settings.local.json." >&2
  exit 2
}

for f in $paths; do
  case "$f" in
    */archive/deprecated-services/*)
      block "$f" "deprecated service archive is frozen" ;;
    */legacy/*)
      block "$f" "legacy/ is preserved for compatibility — do not edit" ;;
    */apps/mobile/lib/core/contracts/*)
      block "$f" "Dart contracts are generated; edit packages/shared-types/src/contracts/ and run sync-dart-contracts" ;;
    *.env|*.env.production|*.env.staging|*credentials*.json|*.pem|*.key)
      block "$f" "refusing to edit secret/credential file" ;;
    */config/certs/*.key|*/config/certs/*.pem)
      block "$f" "TLS key/cert files must not be edited through Claude" ;;
    */node_modules/*|*/.venv/*|*/.next/*|*/dist/*|*/build/*)
      block "$f" "refusing to edit vendored/build output" ;;
  esac
done

exit 0
