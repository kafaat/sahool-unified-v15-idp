# Audit Trail Module - وحدة مسار التدقيق

Comprehensive audit trail management for the SAHOOL platform. Provides tamper-evident action logging, automatic change diffing, GlobalGAP IFA v6 compliance support (5-year retention), multi-format export, and configurable retention policies.

**Version**: 16.0.0 | **Python**: 3.11+

## File Structure

```
shared/audit_trail/
├── __init__.py      # Public API, version, and re-exports
├── models.py        # AuditEntry, AuditReport, RetentionPolicy, enums, SHA-256 hash chain
├── logger.py        # AuditTrailLogger, log_action(), log_change(), log_globalgap_event()
├── reporter.py      # AuditReportGenerator, export to JSON/CSV/Excel/XML
└── retention.py     # RetentionManager, expiry detection, archival, dry-run support
```

## Key Components

### `AuditEntry`
The core data structure for every auditable event. Each entry includes:
- Actor identity (`actor_id`, `actor_type`, `actor_name`)
- Action classification (`AuditActionType`, `AuditCategory`, `AuditSeverity`)
- Resource context (`resource_type`, `resource_id`)
- Field-level change tracking (`FieldChange` list with before/after values)
- Tamper detection via SHA-256 hash chain (`prev_hash`, `entry_hash`)
- Retention metadata (`retention_period`, `expires_at`)
- GlobalGAP context (`ggn`, `audit_session_id`, `control_point_id`)

### Action Types (`AuditActionType`)
Covers CRUD operations, authentication events (LOGIN, LOGOUT, LOGIN_FAILED, TWOFA_ENABLED), authorization changes (PERMISSION_GRANTED, ROLE_ASSIGNED), field operations (IRRIGATION, FERTILIZER_APPLICATION, PESTICIDE_APPLICATION, HARVEST), GlobalGAP lifecycle (AUDIT_STARTED, FINDING_RECORDED, NC_RAISED, NC_CLOSED, CERTIFICATE_ISSUED), and data operations (EXPORT, IMPORT, ARCHIVE, PURGE).

### Retention Periods

| Period | Days | Use Case |
|--------|------|----------|
| `SHORT` | 90 | Debug / transient data |
| `MEDIUM` | 365 | General operational records |
| `LONG` | 1095 (3 yr) | Business records |
| `GLOBALGAP` | 1825 (5 yr) | **Default** - IFA v6 requirement |
| `PERMANENT` | Never | Legal / compliance hold |

### Export Formats (`ExportFormat`)
`JSON`, `CSV`, `EXCEL`, `XML`, `PDF`

## Usage Examples

### Basic Logging

```python
from shared.audit_trail import log_action, log_change, log_login, AuditActionType

# Log a simple action
entry = log_action(
    action=AuditActionType.CREATE,
    resource_type="field",
    resource_id="FIELD-123",
    actor_id="user-456",
    tenant_id="farm_001",
)

# Log with automatic field-level diff
entry = log_change(
    action=AuditActionType.UPDATE,
    resource_type="field",
    resource_id="FIELD-123",
    before={"name": "Old Name", "area_ha": 5.0},
    after={"name": "New Name", "area_ha": 5.2},
    actor_id="user-456",
    tenant_id="farm_001",
)
# entry.changes contains FieldChange entries with old_value / new_value

# Log a login event
entry = log_login(actor_id="user-456", tenant_id="farm_001", success=True, ip_address="10.0.0.1")
```

### GlobalGAP Compliance Logging

```python
from shared.audit_trail import log_globalgap_event, AuditActionType

entry = log_globalgap_event(
    action=AuditActionType.FINDING_RECORDED,
    resource_type="control_point",
    resource_id="AF.1.1.1",
    ggn="4012345678901",
    audit_session_id="audit-2024-001",
    tenant_id="farm_001",
    actor_id="auditor-789",
)
```

### Report Generation and Export

```python
from shared.audit_trail import (
    get_audit_logger,
    AuditReportGenerator,
    generate_globalgap_report,
    ExportFormat,
)
from datetime import datetime

logger = get_audit_logger("farm_001")
entries = logger.get_entries()

generator = AuditReportGenerator(entries, language="ar")

# GlobalGAP compliance report
report = generator.generate_globalgap_report(
    ggn="4012345678901",
    period_start=datetime(2025, 1, 1),
    period_end=datetime(2025, 12, 31),
)
print(f"Compliance score: {report.compliance_score:.0%}")
print(f"Major musts compliant: {report.major_musts_compliant}")

# Export to Excel
excel_bytes = generator.export_to_excel(report=report)

# Export raw entries to CSV
csv_text = generator.export(entries, format=ExportFormat.CSV)
```

### Retention Management

```python
from shared.audit_trail import get_retention_manager, run_retention

manager = get_retention_manager()

# Preview what would be deleted/archived (safe dry-run)
job = await manager.run_retention(dry_run=True)
print(f"Would archive: {job.entries_archived}, delete: {job.entries_deleted}")

# Entries expiring within 30 days
expiring = manager.get_entries_expiring_soon(days=30)

# Apply retention for real
job = await manager.run_retention(dry_run=False)
```

## Integration Notes

- Audit entries default to `RetentionPeriod.GLOBALGAP` (5 years) to satisfy IFA v6.
- Hash chain (`prev_hash` -> `entry_hash`) enables tamper detection; entries are immutable once written.
- Bilingual labels for actions, categories, and severities are available via `get_action_label()`, `get_category_label()`, `get_severity_label()`.
- The `AuditTrailLogger` holds entries in memory; in production, persist entries to PostgreSQL via the `audit-service` (port 8114).
- `AuditQueryFilter` supports filtering by actor, action, category, severity, resource, time range, GlobalGAP session, correlation ID, and tags.
