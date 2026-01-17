# SAHOOL Platform Tools

## أدوات منصة سهول

**Version:** 15.5.0
**Last Updated:** 2024-12-22

---

## Overview | نظرة عامة

This document describes the development and operations tools available for the SAHOOL platform:

| Tool                  | Purpose                         | Location                                       |
| --------------------- | ------------------------------- | ---------------------------------------------- |
| **Complete Analyzer** | Dependency & conflict detection | `tools/complete-analyzer.py`                   |
| **Pre-commit Hook**   | Quality checks before commit    | `tools/scripts/pre-commit`                     |
| **Verify Fixes**      | Validate infrastructure setup   | `tools/scripts/verify-fixes.py`                |
| **Memory Manager**    | Flutter memory optimization     | `apps/mobile/lib/services/memory_manager.dart` |

---

## 1. Complete Analyzer | المحلل الشامل

### Purpose

Analyzes the entire SAHOOL platform for:

- Dependency version conflicts
- PostGIS slow query patterns
- Kong configuration issues
- Docker optimization opportunities

### Usage

```bash
# Full analysis
python3 tools/complete-analyzer.py

# Quick check (for pre-commit)
python3 tools/complete-analyzer.py --quick-check

# JSON output
python3 tools/complete-analyzer.py --json

# Custom project root
python3 tools/complete-analyzer.py --root /path/to/project
```

### Output

```
============================================================
📊 SAHOOL Platform Analysis Report
============================================================
📈 Risk Level: 🟢 LOW
🔴 Critical Issues: 0
🟠 Warnings: 3
💡 Optimizations: 5

💰 Estimated Savings:
  - docker: 83% faster
  - database: 75% cost reduction
  - mobile: 60% reduction
  - api_gateway: 99.9% uptime

📄 Full report saved: analysis-report.json
```

### Checks Performed

| Check                | Description                                             |
| -------------------- | ------------------------------------------------------- |
| Python Dependencies  | Scans all `requirements.txt` for version conflicts      |
| Flutter Dependencies | Scans all `pubspec.yaml` for version conflicts          |
| Node.js Dependencies | Scans all `package.json` for version conflicts          |
| PostGIS Queries      | Detects slow query patterns (SELECT \*, geometry casts) |
| Kong Configuration   | Validates health checks, rate limiting                  |
| Docker Files         | Checks for multi-stage builds, caching issues           |

---

## 2. Pre-commit Hook | خُطاف ما قبل الـCommit

### Purpose

Runs quality checks before allowing git commits to prevent issues from entering the codebase.

### Installation

```bash
# Copy hook to git directory
cp tools/scripts/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# Or use symlink
ln -sf ../../tools/scripts/pre-commit .git/hooks/pre-commit
```

### Checks Performed

1. **Dependency Conflicts** - Runs complete-analyzer quick check
2. **YAML Syntax** - Validates all .yml/.yaml files
3. **Secret Detection** - Scans for passwords, API keys, tokens
4. **Python Linting** - Runs ruff on Python files (if installed)
5. **File Size** - Blocks files larger than 1MB
6. **Critical TODOs** - Warns about TODOs in critical paths

### Output Example

```
🔧 Running SAHOOL pre-commit checks...

1. Checking dependencies...
✓ Dependencies OK

2. Checking YAML files...
✓ kong.yml
✓ docker-compose.yml

3. Checking for secrets...
✓ No secrets detected

4. Checking Python files...
✓ Python linting passed

5. Checking file sizes...
✓ All files are under size limit

6. Checking for unresolved TODOs in critical paths...
✓ No critical TODOs found

==================================================
✅ All pre-commit checks passed
```

### Bypass (Emergency Only)

```bash
# Skip hooks (not recommended)
git commit --no-verify -m "emergency fix"
```

---

## 3. Verify Fixes | التحقق من الإصلاحات

### Purpose

Validates that all infrastructure components are properly configured after running the Engineering Recovery Plan.

### Usage

```bash
python3 tools/scripts/verify-fixes.py
```

### Checks Performed

| Component         | Validation                             |
| ----------------- | -------------------------------------- |
| Kong HA           | Config files exist, services defined   |
| Circuit Breaker   | Classes and methods present            |
| PostGIS Migration | GIST, partitioning, materialized views |
| Memory Manager    | LRU cache, pagination support          |
| Platform Analyzer | Analysis functions present             |
| Pre-commit Hook   | Quality checks configured              |
| Pubspec Fixes     | mockito version, analyzer override     |

### Output Example

```
============================================================
  SAHOOL Platform Fix Verification
============================================================
  ✅ Kong HA Configuration - 3 config files, 9 services
  ✅ Circuit Breaker - CircuitBreaker with fallback support
  ✅ PostGIS Migration - GIST, Partitioning, Materialized View, pg_cron
  ✅ Memory Manager - LRU cache with pagination support
  ✅ Platform Analyzer - Full platform analyzer
  ✅ Pre-commit Hook - 4 quality checks
  ✅ Pubspec Fixes - mockito 5.4.5, analyzer override applied

============================================================
  Summary
============================================================
  Passed: 7/7

  🎉 All fixes verified! Platform ready for production.
```

---

## 4. Memory Manager (Flutter) | مدير الذاكرة

### Purpose

Provides intelligent memory management for the Flutter mobile app:

- LRU cache eviction
- Pagination support
- Stale data cleanup
- Memory threshold monitoring

### Usage

```dart
import 'package:sahool_field_app/services/memory_manager.dart';

// Initialize (in main.dart)
void main() {
  MemoryManager().initialize();
  runApp(MyApp());
}

// Store data
MemoryManager().put('fields:user:123', fieldsList);

// Retrieve data
final fields = MemoryManager().get<List<Field>>('fields:user:123');

// Paginated fetch with caching
final page1 = await MemoryManager().getPaginated(
  cacheKey: 'fields',
  page: 0,
  pageSize: 20,
  fetcher: (page, size) => api.getFields(page: page, size: size),
);

// Get stats
print(MemoryManager().getStats());
// {cacheSize: 45, maxSize: 50, utilizationPercent: "90.0", ...}

// Manual eviction
await MemoryManager().autoEvict();

// Invalidate by pattern
MemoryManager().invalidateByPattern(r'^fields:.*');
```

### Configuration

| Parameter         | Default | Description               |
| ----------------- | ------- | ------------------------- |
| `maxCacheSize`    | 50      | Maximum cached items      |
| `maxCacheAgeDays` | 7       | Days before auto-eviction |
| `memoryThreshold` | 0.8     | Trigger eviction at 80%   |

### Best Practices

1. **Initialize early** - Call `initialize()` in main.dart
2. **Use pagination** - For lists > 20 items
3. **Invalidate on logout** - Clear user-specific cache
4. **Check stats** - Monitor utilization in debug builds

---

## Creating New Tools | إنشاء أدوات جديدة

### Python Tool Template

```python
#!/usr/bin/env python3
"""
Tool description here.
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("--option", help="Option description")
    args = parser.parse_args()

    # Tool logic here

    return 0  # Success

if __name__ == "__main__":
    sys.exit(main())
```

### Shell Script Template

```bash
#!/bin/bash
# Tool description

set -e

PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT"

# Tool logic here

echo "✅ Done"
```

---

**Related Documents:**

- [Engineering Recovery Plan](../engineering/ENGINEERING_RECOVERY_PLAN.md)
- [Development Guidelines](../development/GUIDELINES.md)
