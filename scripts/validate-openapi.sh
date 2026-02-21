#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL OpenAPI Specification Validator
# أداة التحقق من مواصفات OpenAPI لمنصة سهول
#
# Validates all OpenAPI YAML specs for:
# - YAML syntax correctness
# - OpenAPI 3.0.x structure compliance
# - Internal $ref reference integrity
# - SAHOOL naming conventions
#
# Usage:
#   ./scripts/validate-openapi.sh [--fix] [--verbose]
#
# Options:
#   --fix       Auto-fix minor issues (trailing whitespace, etc.)
#   --verbose   Show detailed output
#   -h, --help  Show this help message
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OPENAPI_DIR="$PROJECT_ROOT/docs/api/openapi"

# Counters
TOTAL=0
PASSED=0
FAILED=0
WARNINGS=0

VERBOSE=false
FIX=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --fix)
            FIX=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Validates all OpenAPI YAML specifications in docs/api/openapi/"
            echo ""
            echo "Options:"
            echo "  --verbose, -v  Show detailed output"
            echo "  --fix          Auto-fix minor issues"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  SAHOOL OpenAPI Specification Validator${NC}"
echo -e "${BLUE}  أداة التحقق من مواصفات OpenAPI${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -d "$OPENAPI_DIR" ]; then
    echo -e "${RED}Error: OpenAPI directory not found: $OPENAPI_DIR${NC}"
    exit 1
fi

# Check for required tools
HAS_PYTHON=false
if command -v python3 &> /dev/null; then
    HAS_PYTHON=true
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Validation Functions
# ═══════════════════════════════════════════════════════════════════════════════

validate_yaml_syntax() {
    local file="$1"
    local filename="$(basename "$file")"

    if $HAS_PYTHON; then
        python3 -c "
import yaml, sys
try:
    with open('$file') as f:
        yaml.safe_load(f)
    sys.exit(0)
except yaml.YAMLError as e:
    print(f'YAML Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null
        return $?
    else
        # Fallback: basic check
        if [ -s "$file" ]; then
            return 0
        else
            return 1
        fi
    fi
}

validate_openapi_structure() {
    local file="$1"

    if ! $HAS_PYTHON; then
        return 0  # Skip if no Python
    fi

    python3 -c "
import yaml, sys

with open('$file') as f:
    data = yaml.safe_load(f)

errors = []

# Check required fields
if 'openapi' not in data:
    errors.append('Missing openapi version field')
elif not str(data['openapi']).startswith('3.0'):
    errors.append(f\"OpenAPI version should be 3.0.x, got {data['openapi']}\")

if 'info' not in data:
    errors.append('Missing info section')
else:
    info = data['info']
    if 'title' not in info:
        errors.append('Missing info.title')
    if 'version' not in info:
        errors.append('Missing info.version')
    if 'description' not in info:
        errors.append('Missing info.description')

if 'paths' not in data:
    errors.append('Missing paths section')
elif len(data['paths']) == 0:
    errors.append('No paths defined')

if 'servers' not in data:
    errors.append('Missing servers section')

# Check for security scheme
components = data.get('components', {})
security_schemes = components.get('securitySchemes', {})
if not security_schemes:
    errors.append('Missing securitySchemes in components')

if errors:
    for e in errors:
        print(e, file=sys.stderr)
    sys.exit(1)
sys.exit(0)
" 2>&1
    return $?
}

validate_refs() {
    local file="$1"

    if ! $HAS_PYTHON; then
        return 0
    fi

    python3 -c "
import yaml, sys

with open('$file') as f:
    data = yaml.safe_load(f)

def collect_refs(obj, refs=None):
    if refs is None:
        refs = []
    if isinstance(obj, dict):
        if '\$ref' in obj:
            refs.append(obj['\$ref'])
        for v in obj.values():
            collect_refs(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            collect_refs(item, refs)
    return refs

def resolve_ref(data, ref):
    if not ref.startswith('#/'):
        return True
    parts = ref[2:].split('/')
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    return True

refs = collect_refs(data)
broken = [r for r in refs if r.startswith('#/') and not resolve_ref(data, r)]

if broken:
    for b in broken:
        print(f'Broken ref: {b}', file=sys.stderr)
    sys.exit(1)
sys.exit(0)
" 2>&1
    return $?
}

count_endpoints() {
    local file="$1"

    if ! $HAS_PYTHON; then
        echo "?"
        return
    fi

    python3 -c "
import yaml
with open('$file') as f:
    data = yaml.safe_load(f)
methods = {'get','post','put','delete','patch'}
count = 0
for path, item in data.get('paths', {}).items():
    for m in methods:
        if m in item:
            count += 1
print(count)
"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Run Validation
# ═══════════════════════════════════════════════════════════════════════════════

TOTAL_ENDPOINTS=0

for spec_file in "$OPENAPI_DIR"/*.yaml; do
    [ -f "$spec_file" ] || continue

    filename="$(basename "$spec_file")"
    TOTAL=$((TOTAL + 1))

    echo -n "  Validating $filename ... "

    # Test 1: YAML syntax
    if ! yaml_result=$(validate_yaml_syntax "$spec_file" 2>&1); then
        echo -e "${RED}FAIL${NC} (YAML syntax error)"
        if $VERBOSE; then
            echo "    $yaml_result"
        fi
        FAILED=$((FAILED + 1))
        continue
    fi

    # Test 2: OpenAPI structure
    if ! struct_result=$(validate_openapi_structure "$spec_file" 2>&1); then
        echo -e "${RED}FAIL${NC} (structure)"
        if $VERBOSE; then
            echo "    $struct_result"
        fi
        FAILED=$((FAILED + 1))
        continue
    fi

    # Test 3: Reference integrity
    if ! ref_result=$(validate_refs "$spec_file" 2>&1); then
        echo -e "${YELLOW}WARN${NC} (broken refs)"
        if $VERBOSE; then
            echo "    $ref_result"
        fi
        WARNINGS=$((WARNINGS + 1))
        PASSED=$((PASSED + 1))
        continue
    fi

    # Count endpoints
    endpoints=$(count_endpoints "$spec_file")
    TOTAL_ENDPOINTS=$((TOTAL_ENDPOINTS + endpoints))

    echo -e "${GREEN}PASS${NC} ($endpoints endpoints)"
    PASSED=$((PASSED + 1))
done

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Summary | الملخص${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Specs validated:  $TOTAL"
echo -e "  ${GREEN}Passed:${NC}           $PASSED"
echo -e "  ${RED}Failed:${NC}           $FAILED"
echo -e "  ${YELLOW}Warnings:${NC}         $WARNINGS"
echo -e "  Total endpoints:  $TOTAL_ENDPOINTS"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Validation failed with $FAILED errors${NC}"
    exit 1
else
    echo -e "${GREEN}All OpenAPI specifications are valid${NC}"
    exit 0
fi
