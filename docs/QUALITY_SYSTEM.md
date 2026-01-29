# SAHOOL Quality System - نظام الجودة

## Overview | نظرة عامة

The SAHOOL Quality System is a comprehensive, automated code quality management framework that integrates AI agents, dynamic tools, and full audit capabilities.

نظام الجودة في سهول هو إطار عمل شامل وآلي لإدارة جودة الكود يدمج وكلاء الذكاء الاصطناعي والأدوات الديناميكية وقدرات التدقيق الكاملة.

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SAHOOL Quality System                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────┐    ┌───────────────────┐    ┌────────────────┐  │
│  │  Code Fix Agent   │    │  Code Review Agent │    │ Quality Gates  │  │
│  │  وكيل إصلاح الكود │    │  وكيل مراجعة الكود │    │ بوابات الجودة  │  │
│  └─────────┬─────────┘    └─────────┬─────────┘    └───────┬────────┘  │
│            │                        │                       │           │
│            └────────────────────────┼───────────────────────┘           │
│                                     │                                   │
│  ┌──────────────────────────────────┴──────────────────────────────┐   │
│  │                   Quality Orchestrator                           │   │
│  │                   منسق الجودة                                    │   │
│  │  - Automatic tool selection                                      │   │
│  │  - Parallel execution                                            │   │
│  │  - Auto-audit with traceability                                  │   │
│  │  - Quality gates enforcement                                     │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│  ┌──────────────────────────────────┴──────────────────────────────┐   │
│  │                   Tool Registry                                  │   │
│  │                   سجل الأدوات                                    │   │
│  │  - Dynamic tool discovery                                        │   │
│  │  - Configuration-based selection                                 │   │
│  │  - Circuit breaker for resilience                                │   │
│  │  - Performance metrics tracking                                  │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│  ┌────────┬────────┬────────┬───────┴───┬────────┬────────┬────────┐  │
│  │  Ruff  │  Mypy  │ Bandit │  ESLint   │  TSC   │  Dart  │ Semgrep│  │
│  │ Python │ Types  │Security│TypeScript │ Types  │ Flutter│Security│  │
│  └────────┴────────┴────────┴───────────┴────────┴────────┴────────┘  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                       Auto-Audit System                                 │
│                       نظام التدقيق التلقائي                            │
│  - Full traceability                                                    │
│  - JSON/CSV export                                                      │
│  - Compliance reporting                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components | المكونات

### 1. Tool Registry (سجل الأدوات)

**Location**: `shared/ai/tool_registry.py`

Dynamic tool management for AI agents:

```python
from shared.ai.tool_registry import get_tool_registry, Language

# Get global registry
registry = get_tool_registry()

# Get tools for Python
python_tools = registry.get_tools_for_language(Language.PYTHON)

# Run a specific tool
result = await registry.run_tool("ruff", "apps/services/", auto_fix=True)

# Get metrics
metrics = registry.get_metrics()
```

**Supported Tools**:

| Tool | Language | Category | Capabilities |
|------|----------|----------|--------------|
| Ruff | Python | Linter | Auto-fix, JSON output, Config file |
| Mypy | Python | Type Checker | Incremental, Caching |
| Bandit | Python | Security | JSON output, Custom rules |
| Pylint | Python | Linter | JSON output, Custom rules |
| ESLint | TypeScript/JS | Linter | Auto-fix, JSON output |
| TSC | TypeScript | Type Checker | Incremental, Watch mode |
| Prettier | TS/JS | Formatter | Auto-fix |
| Dart Analyze | Dart | Linter | Config file |
| Dart Format | Dart | Formatter | Auto-fix |
| Import Sorter | Dart | Formatter | Auto-fix |
| Semgrep | Multi | Security | SARIF output, Parallel |
| Gitleaks | Multi | Security | Secret detection |

### 2. Quality Orchestrator (منسق الجودة)

**Location**: `shared/ai/quality_orchestrator.py`

Automated quality analysis with audit:

```python
from shared.ai.quality_orchestrator import (
    QualityOrchestrator,
    run_quality_check,
    generate_quality_report_markdown,
)

# Quick check
report = await run_quality_check("apps/services/")

# Full orchestration
orchestrator = QualityOrchestrator()
report = await orchestrator.analyze(
    paths=["apps/services/", "shared/"],
    languages=["python", "typescript"],
    fix=True,
    audit=True,
)

# Generate markdown report
markdown = generate_quality_report_markdown(report)
```

**Features**:
- Automatic tool selection based on file types
- Parallel execution for performance
- Auto-audit with full traceability
- Quality gates enforcement
- SARIF output for GitHub integration
- Bilingual reports (Arabic/English)

### 3. Quality Configuration (إعدادات الجودة)

**Location**: `.sahool-quality.yaml`

Project-level configuration:

```yaml
# Global Settings
fail_on_warning: false
auto_fix: true
parallel: true

# Python Tools
python:
  tools:
    - ruff
    - mypy
    - bandit

# TypeScript Tools
typescript:
  tools:
    - eslint
    - tsc

# Dart/Flutter Tools
dart:
  tools:
    - dart_analyze
    - dart_format
    - import_sorter

# Quality Gates
ci:
  quality_gates:
    min_coverage: 60
    max_critical_issues: 0
    max_high_issues: 5
```

### 4. Auto-Audit System (نظام التدقيق التلقائي)

**Location**: `shared/ai/quality_orchestrator.py` (AutoAudit class)

Full audit trail for compliance:

```python
from shared.ai.quality_orchestrator import AutoAudit, AuditAction

audit = AutoAudit(
    session_id="session-123",
    user_id="user-456",
    agent_id="code-fix-agent",
)

# Log actions
audit.log(
    AuditAction.ANALYSIS_STARTED,
    {"paths": ["apps/"], "fix": True}
)

# Export for compliance
json_export = audit.export("json")
csv_export = audit.export("csv")
```

**Audit Actions**:
- `ANALYSIS_STARTED` - Analysis session started
- `ANALYSIS_COMPLETED` - Analysis completed
- `TOOL_EXECUTED` - Tool was executed
- `ISSUE_FOUND` - Quality issue found
- `ISSUE_FIXED` - Issue was auto-fixed
- `QUALITY_GATE_CHECK` - Gate check performed
- `QUALITY_GATE_PASSED` - Gate check passed
- `QUALITY_GATE_FAILED` - Gate check failed
- `NOTIFICATION_SENT` - Notification sent
- `ERROR_OCCURRED` - Error occurred

### 5. Code Fix Agent Integration

**Location**: `apps/services/code-fix-agent/src/agent/code_fix_agent.py`

The Code Fix Agent now includes quality orchestration:

```python
agent = CodeFixAgent()

# Run comprehensive quality analysis
result = await agent.run_quality_analysis(
    paths=["apps/services/"],
    languages=["python", "typescript"],
    fix=True,
    audit=True,
)

# Get available tools
tools = await agent.get_available_tools(language="python")

# Run specific tool
result = await agent.run_tool("ruff", "apps/services/", auto_fix=True)
```

## Usage | الاستخدام

### CLI Commands

```bash
# Run quality belt
./scripts/quality-belt.sh           # All checks
./scripts/quality-belt.sh python    # Python only
./scripts/quality-belt.sh typescript # TypeScript only
./scripts/quality-belt.sh flutter   # Flutter only
./scripts/quality-belt.sh quick     # Quick checks

# Makefile targets
make quality          # Full quality check
make quality-quick    # Quick check
make quality-python   # Python only
make quality-ts       # TypeScript only
make quality-flutter  # Flutter only
make security-check   # Security checks
```

### Flutter/Melos Commands

```bash
# Initialize Melos
make melos-bootstrap

# Run quality checks
melos run analyze       # Static analysis
melos run format        # Format check
melos run test          # Unit tests
melos run quality       # Full pipeline
melos run imports:sort  # Sort imports
melos run ci            # CI pipeline
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Quality Gates | بوابات الجودة

Quality gates are enforced during analysis:

| Gate | Default Threshold | Description |
|------|-------------------|-------------|
| max_critical_issues | 0 | No critical issues allowed |
| max_high_issues | 5 | Maximum 5 high severity issues |
| max_warnings | 50 | Maximum 50 warnings |
| min_coverage | 60% | Minimum code coverage |

## Reports | التقارير

### Quality Report Structure

```json
{
  "id": "report-uuid",
  "session_id": "session-uuid",
  "status": "completed",
  "quality_score": 85.5,
  "quality_level": "good",
  "total_issues": 15,
  "critical_issues": 0,
  "high_issues": 2,
  "medium_issues": 8,
  "low_issues": 5,
  "fixed_count": 12,
  "gates_passed": true,
  "tools_executed": ["ruff", "mypy", "bandit"],
  "duration_ms": 1250.5,
  "files_analyzed": 45
}
```

### SARIF Output

For GitHub integration, reports can be exported in SARIF format:

```python
sarif = report.to_sarif()
# Upload to GitHub Code Scanning
```

## Configuration Reference | مرجع الإعدادات

### Full .sahool-quality.yaml Example

```yaml
version: "1.0.0"
fail_on_warning: false
auto_fix: true
parallel: true
max_parallel_tools: 4

cache:
  enabled: true
  ttl: 300

python:
  enabled: true
  paths:
    - apps/services/
    - shared/
  tools:
    - ruff
    - mypy
    - bandit

  ruff:
    select: [E, F, W, I, UP, B, C4, S]
    ignore: [E501]
    line-length: 120

  mypy:
    ignore_missing_imports: true
    strict_optional: true

  bandit:
    severity: medium
    exclude: [tests/]

typescript:
  enabled: true
  paths:
    - apps/web/
    - apps/admin/
  tools:
    - eslint
    - tsc

  eslint:
    max_warnings: 50
    fix: true

dart:
  enabled: true
  paths:
    - apps/mobile/
  tools:
    - dart_analyze
    - dart_format
    - import_sorter

security:
  enabled: true
  tools:
    - gitleaks
    - detect_secrets

testing:
  enabled: true
  tools:
    python: [pytest]
    typescript: [vitest, playwright]
    dart: [flutter_test]

  pytest:
    coverage: true
    min_coverage: 60

ai_agents:
  enabled: true
  code_fix_agent:
    enabled: true
    auto_run: true
    fix_strategy: safe

ci:
  github_actions:
    enabled: true
    fail_on_quality_issues: true
    create_annotations: true

  quality_gates:
    min_coverage: 60
    max_critical_issues: 0
    max_high_issues: 5
    max_warnings: 50

exclude:
  - "**/node_modules/**"
  - "**/build/**"
  - "**/*.g.dart"
  - "**/*.freezed.dart"
```

## Best Practices | أفضل الممارسات

### 1. Enable Auto-Fix
Always enable auto-fix to automatically resolve simple issues:
```yaml
auto_fix: true
```

### 2. Use Parallel Execution
Enable parallel execution for faster analysis:
```yaml
parallel: true
max_parallel_tools: 4
```

### 3. Configure Quality Gates
Set appropriate thresholds for your project:
```yaml
quality_gates:
  max_critical_issues: 0  # Zero tolerance for critical
  max_high_issues: 5      # Allow some high issues during development
```

### 4. Enable Audit for Compliance
Enable audit logging for compliance requirements:
```python
report = await orchestrator.analyze(
    paths=["apps/"],
    audit=True,
)
```

### 5. Use Pre-commit Hooks
Install pre-commit hooks to catch issues early:
```bash
pre-commit install
```

## Troubleshooting | استكشاف الأخطاء

### Tool Not Available

If a tool is not available:
```python
availability = await registry.check_availability()
print(availability)  # {'ruff': True, 'mypy': False, ...}
```

Install missing tools:
```bash
pip install ruff mypy bandit
npm install -g eslint
```

### Circuit Breaker Open

If a tool keeps failing, the circuit breaker will open:
```python
# Reset circuit breakers
registry.reset_circuit_breakers()
```

### Cache Issues

Clear the cache if results seem stale:
```python
registry.clear_cache()  # Clear all
registry.clear_cache("ruff")  # Clear specific tool
```

## API Reference | مرجع API

### Tool Registry

```python
class ToolRegistry:
    def register(tool: ToolInfo) -> None
    def unregister(tool_id: str) -> None
    def get_tool(tool_id: str) -> ToolInfo | None
    def get_all_tools() -> list[ToolInfo]
    def get_tools_for_language(language: Language) -> list[ToolInfo]
    def get_enabled_tools(language: Language) -> list[ToolInfo]
    async def check_availability(tool_id: str | None) -> dict[str, bool]
    async def run_tool(tool_id: str, target: str, ...) -> ToolResult
    async def run_tools(target: str, tools: list[str] | None, ...) -> list[ToolResult]
    def get_metrics(tool_id: str | None) -> dict[str, ToolMetrics]
    def add_hook(event: str, callback: Callable) -> None
    def clear_cache(tool_id: str | None) -> None
    def reset_circuit_breakers() -> None
```

### Quality Orchestrator

```python
class QualityOrchestrator:
    async def analyze(
        paths: list[str] | None,
        languages: list[str] | None,
        tools: list[str] | None,
        fix: bool,
        audit: bool,
        check_gates: bool,
        parallel: bool,
    ) -> QualityReport

class QualityReport:
    def to_dict() -> dict[str, Any]
    def to_json(indent: int) -> str
    def to_sarif() -> dict[str, Any]
```

### Auto-Audit

```python
class AutoAudit:
    def log(action: AuditAction, details: dict, metadata: dict | None) -> AuditEntry
    def get_entries(action: AuditAction | None, since: datetime | None) -> list[AuditEntry]
    def export(format: str) -> str  # "json" or "csv"
```

---

*Last Updated: January 2026*
*Version: 1.0.0*
