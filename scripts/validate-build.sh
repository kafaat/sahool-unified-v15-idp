#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Build Validation Script
# سكريبت التحقق من جاهزية البناء
# ═══════════════════════════════════════════════════════════════════════════════

# Don't use set -e as arithmetic operations return 1 when result is 0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICES_DIR="$ROOT_DIR/apps/services"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0
warnings=0

echo "═══════════════════════════════════════════════════════════════════"
echo "  SAHOOL Build Validation - التحقق من جاهزية البناء"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 1. Validate docker-compose.yml
# ─────────────────────────────────────────────────────────────────────────────
echo "📋 [1/6] Validating docker-compose.yml..."
if command -v docker &> /dev/null; then
    if docker compose config --quiet 2>/dev/null; then
        echo -e "   ${GREEN}✓ docker-compose.yml is valid${NC}"
    else
        echo -e "   ${RED}✗ docker-compose.yml has errors${NC}"
        ((errors++))
    fi
else
    # Fallback to Python YAML check
    if python3 -c "import yaml; yaml.safe_load(open('$ROOT_DIR/docker-compose.yml'))" 2>/dev/null; then
        echo -e "   ${GREEN}✓ docker-compose.yml YAML syntax valid${NC}"
    else
        echo -e "   ${RED}✗ docker-compose.yml YAML syntax error${NC}"
        ((errors++))
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. Check all build contexts exist
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "📁 [2/6] Checking build contexts..."
missing_contexts=0
# Skip shared/common directories that don't need Dockerfiles
SKIP_DIRS="shared common lib libs utils"
for dir in "$SERVICES_DIR"/*/; do
    service_name=$(basename "$dir")

    # Skip shared directories
    if echo "$SKIP_DIRS" | grep -qw "$service_name"; then
        continue
    fi

    if [ -f "$dir/Dockerfile" ]; then
        echo -e "   ${GREEN}✓${NC} $service_name"
    else
        echo -e "   ${RED}✗ $service_name - Missing Dockerfile${NC}"
        ((missing_contexts++))
    fi
done
if [ $missing_contexts -eq 0 ]; then
    echo -e "   ${GREEN}All build contexts valid${NC}"
else
    ((errors += missing_contexts))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. Validate Node.js package-lock.json files
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "📦 [3/6] Validating Node.js package-lock.json files..."
node_errors=0
for dir in "$SERVICES_DIR"/*/; do
    if [ -f "$dir/package.json" ]; then
        service_name=$(basename "$dir")

        # Check if package-lock.json exists
        if [ ! -f "$dir/package-lock.json" ]; then
            echo -e "   ${RED}✗ $service_name - Missing package-lock.json${NC}"
            ((node_errors++))
            continue
        fi

        # Check if all dependencies in package.json are in package-lock.json
        cd "$dir"
        deps=$(node -e "const p=require('./package.json'); const d=p.dependencies||{}; console.log(Object.keys(d).join(' '))" 2>/dev/null || echo "")

        missing_deps=""
        for dep in $deps; do
            if ! grep -q "\"$dep\"" package-lock.json 2>/dev/null; then
                missing_deps="$missing_deps $dep"
            fi
        done

        if [ -n "$missing_deps" ]; then
            echo -e "   ${RED}✗ $service_name - Missing in lock:$missing_deps${NC}"
            ((node_errors++))
        else
            echo -e "   ${GREEN}✓${NC} $service_name"
        fi
        cd - > /dev/null
    fi
done
if [ $node_errors -gt 0 ]; then
    echo -e "   ${YELLOW}Run 'npm install --package-lock-only' to fix${NC}"
    ((errors += node_errors))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. Validate Python requirements.txt files
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "🐍 [4/6] Validating Python requirements.txt files..."
python_errors=0
for dir in "$SERVICES_DIR"/*/; do
    if [ -f "$dir/requirements.txt" ] && [ ! -f "$dir/package.json" ]; then
        service_name=$(basename "$dir")

        # Check for syntax errors in requirements.txt
        if python3 -c "
import sys
try:
    with open('$dir/requirements.txt') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Basic syntax check
                if '==' not in line and '>=' not in line and '<=' not in line and '~=' not in line and line.count('=') == 0 and '[' not in line:
                    if not line.replace('-','').replace('_','').replace('.','').isalnum():
                        print(f'Invalid: {line}', file=sys.stderr)
                        sys.exit(1)
    sys.exit(0)
except Exception as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
            echo -e "   ${GREEN}✓${NC} $service_name"
        else
            echo -e "   ${RED}✗ $service_name - Invalid requirements.txt${NC}"
            ((python_errors++))
        fi
    fi
done
errors=$((errors + python_errors))

# ─────────────────────────────────────────────────────────────────────────────
# 5. Check for port conflicts in Dockerfiles
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "🔌 [5/6] Checking for port conflicts..."
declare -A ports
port_conflicts=0
for dir in "$SERVICES_DIR"/*/; do
    if [ -f "$dir/Dockerfile" ]; then
        service_name=$(basename "$dir")
        exposed_port=$(grep -E "^EXPOSE" "$dir/Dockerfile" 2>/dev/null | awk '{print $2}' | head -1)

        if [ -n "$exposed_port" ]; then
            if [ -n "${ports[$exposed_port]}" ]; then
                echo -e "   ${YELLOW}⚠ Port $exposed_port: $service_name conflicts with ${ports[$exposed_port]}${NC}"
                ((port_conflicts++))
            else
                ports[$exposed_port]=$service_name
            fi
        fi
    fi
done
if [ $port_conflicts -eq 0 ]; then
    echo -e "   ${GREEN}✓ No port conflicts in Dockerfiles${NC}"
else
    echo -e "   ${YELLOW}Note: docker-compose.yml may override these ports${NC}"
    ((warnings += port_conflicts))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. Check required directories and files
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "📂 [6/6] Checking required directories..."
required_dirs=(
    "models"
    "infra/kong"
    "infra/postgres/init"
    "infra/mqtt"
    "observability/prometheus"
    "observability/grafana/provisioning"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$ROOT_DIR/$dir" ]; then
        echo -e "   ${GREEN}✓${NC} $dir"
    else
        echo -e "   ${RED}✗ $dir - Missing directory${NC}"
        ((errors++))
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════"
if [ $errors -eq 0 ]; then
    echo -e "  ${GREEN}✓ BUILD VALIDATION PASSED${NC}"
    echo "  Ready for: docker compose build --no-cache"
else
    echo -e "  ${RED}✗ BUILD VALIDATION FAILED${NC}"
    echo "  Errors: $errors | Warnings: $warnings"
fi
echo "═══════════════════════════════════════════════════════════════════"

exit $errors
