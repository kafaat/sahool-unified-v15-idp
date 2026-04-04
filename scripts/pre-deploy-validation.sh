#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Pre-Deploy Validation Script
# سكريبت التحقق قبل النشر
#
# Fails the deployment if any CHANGE_ME_BEFORE_DEPLOY placeholders remain
# in production-critical configuration files.
#
# Usage:
#   ./scripts/pre-deploy-validation.sh          # check all known files
#   ./scripts/pre-deploy-validation.sh --strict  # also scan entire repo
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXIT_CODE=0

# ─────────────────────────────────────────────────────────────────────────────
# Known production-critical files that must NOT contain placeholders
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: Files using ${VAR:-CHANGE_ME_BEFORE_DEPLOY} shell substitution are safe
# (the placeholder is only a fallback when the env var is unset).
# Template files (*.template.*) and Helm templates with {{ .Values }} are also
# excluded since their placeholders are replaced at deploy/install time.
CRITICAL_FILES=(
  "infrastructure/core/vault/vault-production.hcl"
  "infrastructure/core/vault/docker-compose.vault.yml"
  "infrastructure/core/postgres/ha-replication/docker-compose.ha.yml"
  # NOTE: helm/infra/templates/secrets.yaml uses CHANGE_ME as Helm-time defaults
  # that MUST be overridden via --set or values files during helm install.
  # governance/credentials.template.yaml is a template file by design.
)

# Patterns that indicate unfilled placeholders
PLACEHOLDER_PATTERNS=(
  "CHANGE_ME_BEFORE_DEPLOY"
  "CHANGE_ME"
  "REPLACE_ME"
  "TODO_BEFORE_DEPLOY"
  "INSERT_SECRET_HERE"
)

echo "═══════════════════════════════════════════════════════════════"
echo " SAHOOL Pre-Deploy Validation — التحقق قبل النشر"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Check critical files for placeholder patterns
# ─────────────────────────────────────────────────────────────────────────────
echo "Checking critical configuration files..."
echo ""

for file in "${CRITICAL_FILES[@]}"; do
  filepath="${REPO_ROOT}/${file}"
  if [[ ! -f "$filepath" ]]; then
    echo -e "  ${YELLOW}SKIP${NC} ${file} (file not found)"
    continue
  fi

  file_clean=true
  for pattern in "${PLACEHOLDER_PATTERNS[@]}"; do
    # Search uncommented lines only (ignore lines starting with # or //)
    # Also ignore shell/Helm variable defaults like ${VAR:-CHANGE_ME_BEFORE_DEPLOY}
    # — these are safe fallback patterns that only activate when the env var is unset.
    matches=$(grep -n "${pattern}" "$filepath" 2>/dev/null \
      | grep -v '^\s*#' \
      | grep -v '^\s*//' \
      | grep -v ':-CHANGE_ME' \
      | grep -v '\${.*CHANGE_ME' \
      | grep -v '\.template\.' \
      || true)
    if [[ -n "$matches" ]]; then
      echo -e "  ${RED}FAIL${NC} ${file}"
      echo "$matches" | while IFS= read -r line; do
        echo -e "        ${RED}→${NC} $line"
      done
      file_clean=false
      EXIT_CODE=1
    fi
  done

  if [[ "$file_clean" == true ]]; then
    echo -e "  ${GREEN}PASS${NC} ${file}"
  fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Strict mode: scan entire repository (excluding known-safe files)
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--strict" ]]; then
  echo "Strict mode: scanning entire repository for CHANGE_ME_BEFORE_DEPLOY..."
  echo ""

  # Exclude example/template files, docs, and test fixtures via grep options below
  hits=$(grep -rn "CHANGE_ME_BEFORE_DEPLOY" "${REPO_ROOT}" \
    --exclude="*.example" \
    --exclude=".env.example" \
    --exclude="env.example" \
    --exclude="*.template.*" \
    --exclude="credentials.template.yaml" \
    --exclude="*.md" \
    --exclude="*.yml.bak" \
    --exclude="pre-deploy-validation.sh" \
    --exclude="pre-deploy-validation.yml" \
    --exclude="*.k8s.example.yaml" \
    --exclude-dir="node_modules" \
    --exclude-dir=".git" \
    --exclude-dir="archive" \
    --exclude-dir="tests" \
    --exclude-dir="helm" \
    2>/dev/null \
    | grep -v '^\s*#' \
    | grep -v '^\s*//' \
    | grep -v ':-CHANGE_ME' \
    | grep -v '\${.*CHANGE_ME' \
    || true)

  if [[ -n "$hits" ]]; then
    echo -e "  ${RED}FAIL${NC} Found CHANGE_ME_BEFORE_DEPLOY in repository:"
    echo "$hits" | head -20
    EXIT_CODE=1
  else
    echo -e "  ${GREEN}PASS${NC} No CHANGE_ME_BEFORE_DEPLOY found in repository"
  fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [[ "$EXIT_CODE" -eq 0 ]]; then
  echo -e " ${GREEN}✅ All pre-deploy validations passed${NC}"
else
  echo -e " ${RED}❌ Pre-deploy validation FAILED — fix placeholders before deploying${NC}"
fi
echo "═══════════════════════════════════════════════════════════════"

exit $EXIT_CODE
