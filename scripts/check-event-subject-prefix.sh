#!/usr/bin/env bash
# scripts/check-event-subject-prefix.sh
#
# Fail the build if any NATS publish/subscribe call uses a subject that
# doesn't start with `sahool.`.
#
# SAHOOL platform convention (see apps/services/NATS_AUDIT.md §3 Bug #1):
# every NATS subject MUST be `sahool.<domain>.<entity>.<action>` so
# TypeScript publishers and Python subscribers can interop. Without the
# `sahool.` prefix events are silently dropped at the broker — there are
# no subscribers for bare `field.created` because everyone listens on
# `sahool.field.*`.
#
# This script greps the code for publishes/subscribes that violate the
# rule and exits non-zero if any are found. Meant to be called from
# CI (see .github/workflows/event-contracts-guard.yml).
#
# False-positives: the regex deliberately also flags raw string literals
# passed to nats.js `publish()` / `subscribe()` / `subscribePattern()`.
# If a call is a legitimate non-SAHOOL subject (e.g. internal test
# fixtures, bridging to an external system) annotate the call with
# `// nats-subject-ignore` on the same line to silence this check.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Directories to scan — include service source and shared packages.
SCAN_PATHS=(
  "apps/services"
  "apps/web/src"
  "apps/admin/src"
  "packages/shared-events/src"
  "packages"
  "shared"
)

# Subjects in these files are known exceptions and must keep a non-SAHOOL
# form (e.g. upstream-protocol compatibility). Paths are anchored to
# REPO_ROOT and matched as substrings.
EXCEPTIONS=(
  # `.publish()` on MQTT clients has nothing to do with NATS
  "mqtt"
  # Generated Prisma client ships mocked calls
  "generated/client"
  # Build output
  "dist/"
  "node_modules/"
  # Test fixtures using abstract names like 'test.event'
  "__tests__/"
  ".spec.ts"
  ".test.ts"
  "/tests/"
  "/test/"
  # Legacy NATS tests in the Node redis-cluster pipeline
  "archive/"
  # Python subjects.py defines the prefix ITSELF so of course it has
  # lines like `"sahool.field.created"` — no risk of drift here.
  "shared/events/subjects.py"
  # Event-bus package itself defines the prefix
  "packages/shared-events/src/events.ts"
  # Event models only ship docstring examples, no runtime publish
  "shared/events/models.py"
  # Redis Pub/Sub (not NATS) — uses similar publish() verb
  "shared/cache/"
  # Usage examples / developer docs
  "/examples/"
  "examples.py"
  # JSON schemas in governance/ describe events that are already correct
  "governance/"
)

# Build an `rg`-style negative-path pattern.
IS_EXCEPTION() {
  local file="$1"
  for ex in "${EXCEPTIONS[@]}"; do
    case "$file" in
      *"$ex"*) return 0 ;;
    esac
  done
  return 1
}

# Patterns that indicate a NATS publish/subscribe with a string literal
# first argument. Two forms:
#   .publish('subject', …)
#   .subscribe('subject', …)
#   publishEvent('subject', …)
#   subscribePattern('subject', …)
#   subscribe('subject', …)
PATTERN='\b(publish|subscribe|subscribePattern|publishEvent)\s*\(\s*['"'"'"]'

echo "→ Scanning for NATS subjects without \`sahool.\` prefix..."

violations=0

# Use grep to collect candidate lines, then filter.
while IFS=: read -r file line content; do
  # Skip exceptions
  if IS_EXCEPTION "$file"; then
    continue
  fi

  # Skip lines with an explicit ignore annotation
  if echo "$content" | grep -q "nats-subject-ignore"; then
    continue
  fi

  # Skip comment-only lines. JSDoc/TSDoc lines start with `*`, Python
  # docstring example lines typically start with `>>>` or are indented
  # inside a triple-quoted block but appear to `grep -n` as plain
  # content. We do a best-effort match on a leading `*`, `//`, or `#`
  # (after optional whitespace).
  trimmed=$(echo "$content" | sed 's/^[[:space:]]*//')
  case "$trimmed" in
    \*\ *|\*|\/\/*|\#*) continue ;;
    # Python doctest line inside a docstring: `    >>> bus.publish(...)`
    '>>>'*) continue ;;
  esac

  # Extract the first string-literal argument: capture the content
  # between the first pair of matching quotes after `(`.
  subject=$(echo "$content" | sed -n "s/.*\b\(publish\|subscribe\|subscribePattern\|publishEvent\)\s*(\s*['\"]\\([^'\"]*\\)['\"].*/\\2/p" | head -1)

  if [[ -z "$subject" ]]; then
    continue
  fi

  # Allowed: starts with `sahool.`  OR is a wildcard fan-in like `>`.
  if [[ "$subject" == sahool.* ]] || [[ "$subject" == ">" ]]; then
    continue
  fi

  # Allowed: an internal NATS helper subject (rare, non-routing)
  case "$subject" in
    _INBOX.*|\$SYS.*) continue ;;
  esac

  echo "::error file=$file,line=$line::NATS subject '$subject' is missing the 'sahool.' prefix"
  echo "   $file:$line  → $subject"
  violations=$((violations + 1))
done < <(grep -rnE --include='*.ts' --include='*.tsx' --include='*.js' --include='*.py' \
           "$PATTERN" "${SCAN_PATHS[@]}" 2>/dev/null || true)

echo
if [[ $violations -gt 0 ]]; then
  echo "✗ Found $violations NATS publish/subscribe call(s) without the 'sahool.' prefix"
  echo "  See apps/services/NATS_AUDIT.md for context."
  echo "  If a call is intentional (e.g. external-protocol bridge), annotate"
  echo "  it with '// nats-subject-ignore' on the same line."
  exit 1
fi

echo "✓ All NATS subjects use the 'sahool.' prefix"
