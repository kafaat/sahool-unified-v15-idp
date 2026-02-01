#!/bin/bash
# SAHOOL FixOps CLI Runner
# سكربت تشغيل FixOps لسهول
#
# Usage:
#   ./scripts/fixops.sh [options]
#
# Examples:
#   ./scripts/fixops.sh                    # Preview mode
#   ./scripts/fixops.sh --no-dry-run       # Apply fixes
#   ./scripts/fixops.sh -s comprehensive   # All fixes
#   ./scripts/fixops.sh --help             # Show help

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to repo root
cd "$REPO_ROOT"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required | خطأ: Python 3 مطلوب"
    exit 1
fi

# Run FixOps CLI
python3 -m tools.fixops.cli "$@"
