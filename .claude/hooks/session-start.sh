#!/usr/bin/env bash
# SessionStart hook. Prints a short SAHOOL-specific orientation to stdout so
# Claude has fresh context about the repo state when a session begins.
#
# Intentionally cheap — no network calls, no docker, no make.

set -u

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT" || exit 0

echo "=== SAHOOL session start ==="
echo "repo:       $(basename "$REPO_ROOT")"
echo "branch:     $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
echo "head:       $(git log -1 --pretty='%h %s' 2>/dev/null || echo '?')"

# Only show short status; avoid -uall on a large monorepo.
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "dirty files: $dirty"

if [[ "$dirty" -gt 0 && "$dirty" -lt 30 ]]; then
  echo "--- short status ---"
  git status --short 2>/dev/null
fi

# Warn on protected branches.
cur_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')
case "$cur_branch" in
  main|master|develop|release/*)
    echo "⚠️  You are on a protected branch ($cur_branch). Most edits should happen on a feature branch."
    ;;
esac

echo "=== end SAHOOL session start ==="
exit 0
