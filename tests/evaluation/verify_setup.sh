#!/bin/bash
# Verification script for Agent Evaluation Pipeline
# سكريبت التحقق من خط أنابيب تقييم الوكلاء

set -e

echo "🔍 Verifying Agent Evaluation Pipeline Setup..."
echo ""

# Check directory structure
echo "📁 Checking directory structure..."
for dir in datasets baselines scripts; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/ exists"
    else
        echo "  ❌ $dir/ missing"
        exit 1
    fi
done

# Check required files
echo ""
echo "📄 Checking required files..."
files=(
    "__init__.py"
    "conftest.py"
    "evaluator.py"
    "test_agent_behavior.py"
    "pytest.ini"
    "README.md"
    "SETUP.md"
    "datasets/golden_dataset.json"
    "scripts/__init__.py"
    "scripts/create_golden_dataset.py"
    "scripts/validate_dataset.py"
    "scripts/calculate_scores.py"
    "scripts/generate_report.py"
    "scripts/compare_with_baseline.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file missing"
        exit 1
    fi
done

# Check GitHub workflow
echo ""
echo "🔧 Checking GitHub workflow..."
if [ -f "../../.github/workflows/agent-evaluation.yml" ]; then
    echo "  ✅ agent-evaluation.yml exists"
else
    echo "  ❌ agent-evaluation.yml missing"
    exit 1
fi

# Validate golden dataset
echo ""
echo "🧪 Validating golden dataset..."
python scripts/validate_dataset.py
if [ $? -eq 0 ]; then
    echo "  ✅ Golden dataset is valid"
else
    echo "  ❌ Golden dataset validation failed"
    exit 1
fi

# Check Python syntax
echo ""
echo "🐍 Checking Python syntax..."
for pyfile in *.py scripts/*.py; do
    if [ -f "$pyfile" ]; then
        python -m py_compile "$pyfile" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ $pyfile"
        else
            echo "  ❌ $pyfile has syntax errors"
            exit 1
        fi
    fi
done

# Summary
echo ""
echo "════════════════════════════════════════════════"
echo "✅ Agent Evaluation Pipeline Setup Verified!"
echo "════════════════════════════════════════════════"
echo ""
echo "📊 Statistics:"
echo "  - Total Python files: $(find . -name '*.py' | wc -l)"
echo "  - Total lines of code: $(find . -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}')"
echo "  - Golden dataset tests: $(cat datasets/golden_dataset.json | grep -c '\"id\"')"
echo ""
echo "🚀 Next Steps:"
echo "  1. Review README.md for usage instructions"
echo "  2. Review SETUP.md for detailed setup guide"
echo "  3. Run: pytest -v (to test evaluation locally)"
echo "  4. Create a PR to trigger CI/CD evaluation"
echo ""
