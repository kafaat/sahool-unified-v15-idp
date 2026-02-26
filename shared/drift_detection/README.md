# shared/drift_detection - Drift Detection Framework

إطار كشف الانحراف

Comprehensive drift detection and auto-remediation system for the SAHOOL platform. Monitors six categories of drift (config, schema, API, event, data, security), generates structured reports with bilingual descriptions, and can automatically remediate common failure patterns. Uses lazy imports to prevent circular dependency issues.

## File Structure

```
shared/drift_detection/
├── __init__.py           # Package exports with lazy loading
├── models.py             # Core data models (DriftResult, DriftReport, etc.)
├── engine.py             # DriftDetectionEngine orchestrator
├── quality_gates.py      # QualityGatesEngine - CI/CD gates
├── remediation.py        # AutoRemediationEngine
└── detectors/
    ├── __init__.py
    ├── base.py           # BaseDriftDetector ABC
    ├── config_drift.py   # GitOps / env / compose / helm drift
    ├── schema_drift.py   # Database migration drift
    ├── api_drift.py      # API contract drift
    ├── event_drift.py    # NATS event schema drift
    ├── data_drift.py     # ML/NDVI distribution drift, sensor anomalies
    └── security_drift.py # Policy, secret rotation, compliance
```

## Drift Categories

| Category | Class | What It Checks |
|----------|-------|---------------|
| `CONFIG` | `ConfigDriftDetector` | GitOps desired state vs actual, env vars, Docker Compose, Helm values |
| `SCHEMA` | `SchemaDriftDetector` | DB migrations applied vs expected, column type changes |
| `API` | `APIDriftDetector` | OpenAPI contract tests against staging/production |
| `EVENT` | `EventDriftDetector` | NATS schema registry version vs deployed schemas |
| `DATA` | `DataDriftDetector` | ML model input distribution shift, NDVI sensor anomalies |
| `SECURITY` | `SecurityDriftDetector` | Policy violations, secret rotation status, compliance gaps |

## Key Models (`models.py`)

### Enums

**`DriftSeverity`** with priority thresholds:
- `CRITICAL` - Immediate action required (<6h)
- `HIGH` - Action within 24h
- `MEDIUM` - Action within 48h
- `LOW` - Informational
- `INFO` - No action needed

**`RemediationStrategy`**:
- `AUTO_FIX` - Apply fix automatically
- `AUTO_ROLLBACK` - Roll back to known good state
- `AUTO_RESTART` - Restart the affected service
- `PAUSE_AND_DLQ` - Pause consumer, route to Dead Letter Queue
- `BLOCK_PR` - Block pull request merge
- `ALERT_ONLY` - Notify humans only
- `CREATE_ISSUE` - Open a GitHub issue automatically

### Data Classes

**`DriftResult`** - Single detection finding:
- `category`, `severity`, `source`, `expected`, `actual`
- `description` / `description_ar` (bilingual)
- `file_path`, `service_name`, `tenant_id`
- `auto_fixable: bool`, `remediation_hint` / `remediation_hint_ar`

**`DriftReport`** - Aggregated results:
- List of `DriftResult` findings
- Summary counts by category and severity
- `baseline_hash` for comparison against known-good state

**`RemediationAction`** - Planned fix:
- `strategy`, `target`, `command`, `expected_outcome`, `risk_level`

**`RemediationResult`** - Outcome of applying a fix:
- `success: bool`, `action_taken`, `duration_ms`, `rollback_available`

## Key Classes

**`DriftDetectionEngine`** - Main orchestrator:
- `run_all_detectors()` → `DriftReport`
- `run_detector(category)` → `DriftReport` for a single category
- `create_baseline()` → Snapshot current state as known-good
- `compare_with_baseline(baseline)` → Delta report

**`AutoRemediationEngine`** - Applies fixes:
- `remediate(report)` → List of `RemediationResult`
- Only attempts fixes marked `auto_fixable=True`
- Respects risk thresholds (skips HIGH risk without explicit approval)

**`QualityGatesEngine`** - CI/CD integration:
- `evaluate(report)` → `pass | fail` with reasons
- Configurable thresholds per severity level
- Returns structured gate results for GitHub Actions

## Utility Functions

```python
from shared.drift_detection import create_baseline, load_baseline, compare_with_baseline

# Save current state as known-good
baseline = await create_baseline(engine)

# Load stored baseline
baseline = await load_baseline(path="/var/sahool/drift_baseline.json")

# Compare current state against baseline
delta_report = await compare_with_baseline(engine, baseline)
```

## Usage Example

```python
from shared.drift_detection import (
    DriftDetectionEngine, AutoRemediationEngine, QualityGatesEngine,
    DriftCategory, DriftSeverity,
)

# Initialize
engine = DriftDetectionEngine(config_path="/app/config")

# Run all detectors
report = await engine.run_all_detectors()

print(f"Findings: {len(report.findings)}")
for finding in report.findings:
    if finding.severity in (DriftSeverity.CRITICAL, DriftSeverity.HIGH):
        print(f"[{finding.severity}] {finding.category}: {finding.description}")
        print(f"  AR: {finding.description_ar}")
        if finding.auto_fixable:
            print(f"  Fix: {finding.remediation_hint}")

# Auto-remediate fixable issues
remediation = AutoRemediationEngine()
results = await remediation.remediate(report)

# CI/CD quality gate
gates = QualityGatesEngine(max_critical=0, max_high=2)
gate_result = gates.evaluate(report)
if not gate_result.passed:
    raise SystemExit(f"Quality gate failed: {gate_result.reasons}")
```

## Notes

- The module uses lazy imports (`__getattr__`) to defer loading `engine`, `quality_gates`, and `remediation` modules. This prevents `RuntimeWarning` when the module is imported as part of a larger application.
- Only three modules are whitelisted for lazy loading (hardcoded `_ALLOWED_MODULES`) to prevent arbitrary code loading (Semgrep security requirement).
- Used by the `fixops` Make target (`make fixops`, `make fixops-run`) and GitHub workflow `api-contracts-guard.yml`.
- Works alongside `shared/stability/drift_detector.py` which provides a lighter-weight, service-embedded detector.
