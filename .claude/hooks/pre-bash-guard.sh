#!/usr/bin/env bash
# PreToolUse hook for Bash. Blocks commands that could cause data loss or
# violate SAHOOL's security posture (see CLAUDE.md → "Security Considerations"
# and "Executing actions with care").
#
# Exit codes:
#   0  = allow
#   2  = block with a message (Claude reads stderr)
#
# CLAUDE_TOOL_INPUT contains the JSON payload of the Bash call; we grep it for
# high-risk patterns rather than parsing JSON (keeps the hook dependency-free).

set -u

payload="${CLAUDE_TOOL_INPUT:-}"
if [[ -z "$payload" ]]; then
  exit 0
fi

block() {
  echo "🚨 SAHOOL pre-bash-guard blocked this command:" >&2
  echo "    reason: $1" >&2
  echo "    If this is intentional, run it outside Claude Code or disable the guard in .claude/settings.local.json." >&2
  exit 2
}

# --- Git destructive operations ------------------------------------------------
echo "$payload" | grep -qE 'git[[:space:]]+push[[:space:]]+.*--force|git[[:space:]]+push[[:space:]]+.*-f([[:space:]]|$)' \
  && block "git push --force is not allowed (use a PR)"

echo "$payload" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard' \
  && block "git reset --hard can destroy uncommitted work — confirm with the user first"

echo "$payload" | grep -qE 'git[[:space:]]+clean[[:space:]]+-[a-zA-Z]*f' \
  && block "git clean -f can delete untracked files — confirm with the user first"

echo "$payload" | grep -qE 'git[[:space:]]+commit[[:space:]].*--no-verify' \
  && block "--no-verify skips git hooks and is forbidden in SAHOOL (see CLAUDE.md → Security)"

echo "$payload" | grep -qE 'git[[:space:]]+rebase[[:space:]].*--no-edit' \
  && block "--no-edit is not a valid rebase flag in SAHOOL workflow"

echo "$payload" | grep -qE 'git[[:space:]]+branch[[:space:]]+.*-D' \
  && block "force-deleting a branch can lose work — confirm with the user first"

# --- Filesystem destructive operations ----------------------------------------
echo "$payload" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+/($|[[:space:]])' \
  && block "rm -rf / detected"

echo "$payload" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+\*' \
  && block "rm -rf * is too broad"

echo "$payload" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+(apps|shared|packages|governance|docs|infrastructure)' \
  && block "refusing to delete top-level SAHOOL directories"

# --- Docker destructive operations --------------------------------------------
echo "$payload" | grep -qE 'docker[[:space:]]+(system|volume)[[:space:]]+prune[[:space:]]+.*-.*a' \
  && block "docker prune -a can wipe local volumes — confirm first"

echo "$payload" | grep -qE 'docker[[:space:]]+compose[[:space:]]+down[[:space:]]+.*(-v|--volumes)' \
  && block "docker compose down -v will delete SAHOOL database volumes — confirm first"

# --- Database destructive operations ------------------------------------------
echo "$payload" | grep -qiE '(drop[[:space:]]+database|truncate[[:space:]]+table|drop[[:space:]]+table)' \
  && block "destructive SQL detected — confirm with the user first"

echo "$payload" | grep -qE 'make[[:space:]]+db-reset' \
  && block "make db-reset deletes all data — confirm first"

# --- Secrets exfiltration smell tests -----------------------------------------
echo "$payload" | grep -qE '\.env[^.a-zA-Z0-9]' | grep -qiE '(curl|wget|nc|netcat).*(-d|--data)' \
  && block "possible .env exfiltration"

# Allow everything else.
exit 0
